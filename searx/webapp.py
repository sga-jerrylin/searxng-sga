#!/usr/bin/env python
# SPDX-License-Identifier: AGPL-3.0-or-later
"""WebbApp

"""
# pylint: disable=use-dict-literal
from __future__ import annotations

import inspect
import json
import os
import sys
import base64

from timeit import default_timer
import re
import threading
import time
from html import escape
from io import StringIO
import typing

import urllib
import urllib.parse
from urllib.parse import urlencode, urlparse, unquote

import warnings
import httpx

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter  # pylint: disable=no-name-in-module

from werkzeug.serving import is_running_from_reloader

import flask

from flask import (
    Flask,
    render_template,
    url_for,
    make_response,
    redirect,
    send_from_directory,
)
from flask.wrappers import Response
from flask.json import jsonify

from flask_babel import (
    Babel,
    gettext,
    format_decimal,
)

import searx
from searx.extended_types import sxng_request
from searx import (
    logger,
    get_setting,
    settings,
)

from searx import infopage
from searx import limiter
from searx.botdetection import link_token

from searx.data import ENGINE_DESCRIPTIONS
from searx.result_types import Answer
from searx.settings_defaults import OUTPUT_FORMATS
from searx.settings_loader import DEFAULT_SETTINGS_FILE
from searx.exceptions import SearxParameterException
from searx.engines import (
    DEFAULT_CATEGORY,
    categories,
    engines,
    engine_shortcuts,
)

from searx import webutils
from searx.webutils import (
    highlight_content,
    get_static_files,
    get_result_templates,
    get_themes,
    exception_classname_to_text,
    new_hmac,
    is_hmac_of,
    group_engines_in_tab,
)
from searx.webadapter import (
    get_search_query_from_webapp,
    get_selected_categories,
    parse_lang,
)
from searx.utils import gen_useragent, dict_subset
from searx.version import VERSION_STRING, GIT_URL, GIT_BRANCH
from searx.query import RawTextQuery
from searx.plugins.oa_doi_rewrite import get_doi_resolver
from searx.preferences import (
    Preferences,
    ClientPref,
    ValidationException,
)
import searx.answerers
import searx.plugins


from searx.metrics import get_engines_stats, get_engine_errors, get_reliabilities, histogram, counter, openmetrics
from searx.flaskfix import patch_application

from searx.locales import (
    LOCALE_BEST_MATCH,
    LOCALE_NAMES,
    RTL_LOCALES,
    localeselector,
    locales_initialize,
    match_locale,
)

# renaming names from searx imports ...
from searx.autocomplete import search_autocomplete, backends as autocomplete_backends
from searx import favicons

from searx.redisdb import initialize as redis_initialize
from searx.sxng_locales import sxng_locales
import searx.search
from searx.network import stream as http_stream, set_context_network_name
from searx.search.checker import get_result as checker_get_result


logger = logger.getChild('webapp')


def _sort_results_by_time(result_container):
    """按时间对搜索结果进行排序（从最新到最旧）
    
    Args:
        result_container: 搜索结果容器
    """
    import datetime
    
    # 获取当前时间
    current_time = datetime.datetime.now()
    logger.info(f"开始时间排序，当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_sort_key(result):
        """获取排序键值"""
        # 尝试获取发布时间
        published_date = None
        
        if hasattr(result, 'publishedDate') and result.publishedDate:
            published_date = result.publishedDate
        elif isinstance(result, dict) and result.get('publishedDate'):
            published_date = result['publishedDate']
        
        # 如果有发布时间，使用发布时间；否则使用当前时间（排到最后）
        if published_date:
            if isinstance(published_date, str):
                try:
                    # 尝试解析字符串格式的时间
                    published_date = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                except:
                    try:
                        # 尝试其他常见格式
                        published_date = datetime.datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        published_date = None
            
            if published_date:
                # 返回负的时间戳，这样最新的时间会排在前面
                return -published_date.timestamp()
        
        # 没有时间信息的结果排到最后
        return 0
    
    # 对结果进行排序
    if hasattr(result_container, 'results') and result_container.results:
        try:
            # 统计有时间信息的结果数量
            results_with_time = 0
            for result in result_container.results:
                if hasattr(result, 'publishedDate') and result.publishedDate:
                    results_with_time += 1
                elif isinstance(result, dict) and result.get('publishedDate'):
                    results_with_time += 1
            
            result_container.results.sort(key=get_sort_key)
            logger.info(f"按时间排序完成: 总结果数 {len(result_container.results)}, 有时间信息的结果数 {results_with_time}")
        except Exception as e:
            logger.warning(f"时间排序失败: {e}")
    
    return result_container


def _get_field(result, field_name: str):
    try:
        if isinstance(result, dict):
            return result.get(field_name)
        return getattr(result, field_name, None)
    except Exception:
        return None


def _compute_simple_relevance_score(query_text: str, title: str, content: str) -> float:
    if not query_text:
        return 0.0
    q = str(query_text).strip().lower()
    if not q:
        return 0.0
    t = (title or "").lower()
    c = (content or "").lower()

    score = 0.0
    # 标题强匹配权重较高
    if q in t:
        score += 1.0
        # 标题前缀/整词强化（简单启发）
        if t.startswith(q):
            score += 0.3
    # 摘要匹配
    if q in c:
        score += 0.4

    # 覆盖率（非常轻量，避免过重开销）
    # 使用分词开销较大，这里采用按空白切分的近似（对中文退化为子串匹配已上面覆盖）
    tokens = [tok for tok in q.split() if tok]
    if tokens:
        covered = sum(1 for tok in tokens if tok in t or tok in c)
        score += 0.1 * (covered / max(1, len(tokens)))
    return score


def _re_rank_results(query_text: str, result_container, keep_time_bias: bool = True, include_score: bool = False):
    # 为每条结果附加 relevance 分数，并与时间分数做简易融合
    # 时间分数：若存在发布时间，则给一个小幅加成，保持“越新越好”的微弱偏好
    ranked = []
    for item in getattr(result_container, 'results', []) or []:
        title = _get_field(item, 'title')
        content = _get_field(item, 'content')
        rel = _compute_simple_relevance_score(query_text, title or '', content or '')

        time_bonus = 0.0
        if keep_time_bias:
            published_date = _get_field(item, 'publishedDate')
            if published_date:
                try:
                    import datetime
                    if isinstance(published_date, str):
                        try:
                            published_date_dt = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                        except Exception:
                            published_date_dt = datetime.datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
                    else:
                        published_date_dt = published_date
                    # 最近 7 天内的结果给额外加成，线性衰减
                    delta_days = (datetime.datetime.now(datetime.timezone.utc) - published_date_dt.replace(tzinfo=datetime.timezone.utc)).days if published_date_dt.tzinfo else (datetime.datetime.now() - published_date_dt).days
                    if delta_days <= 7:
                        time_bonus = max(0.0, 0.3 * (1 - delta_days / 7.0))
                except Exception:
                    time_bonus = 0.0

        total_score = rel + time_bonus
        if include_score:
            try:
                if isinstance(item, dict):
                    item['score'] = round(total_score, 4)
            except Exception:
                pass
        ranked.append((total_score, item))

    ranked.sort(key=lambda x: x[0], reverse=True)
    if ranked:
        result_container.results = [it for _, it in ranked]
    return result_container


def _sort_results_list_by_time(items):
    import datetime
    def parse_dt(val):
        if not val:
            return None
        if isinstance(val, str):
            try:
                return datetime.datetime.fromisoformat(val.replace('Z', '+00:00'))
            except Exception:
                try:
                    return datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                except Exception:
                    return None
        return val
    def key_func(it):
        dt = _get_field(it, 'publishedDate')
        dt = parse_dt(dt)
        if not dt:
            return 0
        try:
            return dt.timestamp()
        except Exception:
            return 0
    try:
        items.sort(key=key_func, reverse=True)
    except Exception:
        pass
    return items


def _is_textual_template(template_name: str) -> bool:
    if not template_name:
        return True
    name = template_name.lower()
    excluded = ['image', 'images', 'video', 'videos', 'map', 'torrent', 'file', 'files', 'music', 'audio']
    return not any(x in name for x in excluded)


def _re_rank_results_for_web(query_text: str, result_container, keep_time_bias: bool = True, include_score: bool = False):
    # 仅在同一模板组内重排，避免打散前端不同结果模板的分组
    items = getattr(result_container, 'results', []) or []
    if not items:
        return result_container
    # 分组：template -> indices
    groups = {}
    for idx, item in enumerate(items):
        tpl = getattr(item, 'template', '') or ''
        groups.setdefault(tpl, []).append(idx)

    for tpl, indices in groups.items():
        if not _is_textual_template(tpl):
            continue
        # 组内计算分数并排序
        scored = []
        for i in indices:
            it = items[i]
            title = _get_field(it, 'title') or ''
            content = _get_field(it, 'content') or ''
            rel = _compute_simple_relevance_score(query_text, title, content)
            time_bonus = 0.0
            if keep_time_bias:
                published_date = _get_field(it, 'publishedDate')
                if published_date:
                    try:
                        import datetime
                        if isinstance(published_date, str):
                            try:
                                dt = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                            except Exception:
                                dt = datetime.datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
                        else:
                            dt = published_date
                        delta_days = (datetime.datetime.now(datetime.timezone.utc) - dt.replace(tzinfo=datetime.timezone.utc)).days if dt.tzinfo else (datetime.datetime.now() - dt).days
                        if delta_days <= 7:
                            time_bonus = max(0.0, 0.3 * (1 - delta_days / 7.0))
                    except Exception:
                        pass
            total = rel + time_bonus
            if include_score and isinstance(it, dict):
                try:
                    it['score'] = round(total, 4)
                except Exception:
                    pass
            scored.append((total, i))
        scored.sort(key=lambda x: x[0], reverse=True)
        # 组内重排
        ordered_indices = [i for _, i in scored]
        # 将此模板组的 items 重新按分数顺序放回
        items_slice = [items[i] for i in ordered_indices]
        for j, idx in enumerate(indices):
            items[idx] = items_slice[j]
    result_container.results = items
    return result_container


def _re_rank_results_for_web_list(query_text: str, items: list, keep_time_bias: bool = True):
    if not items:
        return items
    groups = {}
    for idx, item in enumerate(items):
        tpl = getattr(item, 'template', '') or ''
        groups.setdefault(tpl, []).append(idx)

    for tpl, indices in groups.items():
        if not _is_textual_template(tpl):
            continue
        scored = []
        for i in indices:
            it = items[i]
            title = _get_field(it, 'title') or ''
            content = _get_field(it, 'content') or ''
            rel = _compute_simple_relevance_score(query_text, title, content)
            time_bonus = 0.0
            if keep_time_bias:
                published_date = _get_field(it, 'publishedDate')
                if published_date:
                    try:
                        import datetime
                        if isinstance(published_date, str):
                            try:
                                dt = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                            except Exception:
                                dt = datetime.datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
                        else:
                            dt = published_date
                        delta_days = (datetime.datetime.now(datetime.timezone.utc) - dt.replace(tzinfo=datetime.timezone.utc)).days if dt.tzinfo else (datetime.datetime.now() - dt).days
                        if delta_days <= 7:
                            time_bonus = max(0.0, 0.3 * (1 - delta_days / 7.0))
                    except Exception:
                        pass
            scored.append((rel + time_bonus, i))
        scored.sort(key=lambda x: x[0], reverse=True)
        ordered_indices = [i for _, i in scored]
        group_items = [items[i] for i in ordered_indices]
        for j, idx in enumerate(indices):
            items[idx] = group_items[j]
    return items


def _calc_item_relevance(query_text: str, item) -> float:
    title = _get_field(item, 'title') or ''
    content = _get_field(item, 'content') or ''
    rel = _compute_simple_relevance_score(query_text, title, content)
    time_bonus = 0.0
    published_date = _get_field(item, 'publishedDate')
    if published_date:
        try:
            import datetime
            if isinstance(published_date, str):
                try:
                    dt = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                except Exception:
                    dt = datetime.datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
            else:
                dt = published_date
            delta_days = (datetime.datetime.now(datetime.timezone.utc) - dt.replace(tzinfo=datetime.timezone.utc)).days if dt.tzinfo else (datetime.datetime.now() - dt).days
            if delta_days <= 7:
                time_bonus = max(0.0, 0.3 * (1 - delta_days / 7.0))
        except Exception:
            pass
    return rel + time_bonus


def _filter_low_relevance_for_web(query_text: str, items: list, min_score: float) -> list:
    if not items:
        return items
    # 从查询中提取必须命中的关键片段
    alnum_tokens = re.findall(r"[A-Za-z0-9]{2,}", query_text or "")
    cjk_tokens = re.findall(r"[\u4e00-\u9fff]{2,}", query_text or "")
    must_tokens = set([t.lower() for t in alnum_tokens + cjk_tokens])
    AGG_HOSTS = {
        'baidu.com', 'www.baidu.com', 'm.baidu.com',
        'weixin.sogou.com', 'sogou.com', 'www.sogou.com',
        '360kuai.com', 'www.360kuai.com', 'so.com', 'www.so.com',
        '360doc.com', 'www.360doc.com',
    }

    filtered = []
    for it in items:
        tpl = getattr(it, 'template', '') or ''
        if _is_textual_template(tpl):
            score = _calc_item_relevance(query_text, it)
            title = (_get_field(it, 'title') or '').lower()
            content = (_get_field(it, 'content') or '').lower()
            text_blob = title + ' ' + content
            must_ok = True
            if must_tokens:
                must_ok = any(tok in text_blob for tok in must_tokens)
            host = ''
            try:
                u = _normalize_url_for_fingerprint(_get_field(it, 'url') or '')
                host = urllib.parse.urlparse(u).netloc.lower()
            except Exception:
                host = ''
            is_agg = host in AGG_HOSTS
            # 聚合/跳转站点更严格
            if (score >= min_score and must_ok) or (not is_agg and score >= (min_score - 0.15) and must_ok):
                filtered.append(it)
        else:
            filtered.append(it)
    return filtered


# -------------------------
# 结果去重 / 规范化 / 清洗
# -------------------------
_TRACKING_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'spm', 'from', 'source', 'referer', 'ref', 'ncid', 'mkt', 'cid'
}


def _normalize_url_for_fingerprint(url: str) -> str:
    try:
        if not url:
            return ''
        parsed = urllib.parse.urlparse(url)
        scheme = (parsed.scheme or 'http').lower()
        netloc = (parsed.netloc or '').lower()
        path = parsed.path or '/'
        # 过滤常见追踪参数，并排序
        query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
        filtered = [(k, v) for (k, v) in query_pairs if k not in _TRACKING_PARAMS]
        filtered.sort()
        query = urllib.parse.urlencode(filtered)
        return urllib.parse.urlunparse((scheme, netloc, path, '', query, ''))
    except Exception:
        return url or ''


def _clean_text_noise(text: typing.Optional[str]) -> str:
    if not text:
        return ''
    try:
        # 去零宽字符/多空白/首尾空白
        t = str(text)
        t = t.replace('\u200b', '').replace('\ufeff', '')
        t = re.sub(r'[\s\u00A0\u3000]+', ' ', t)
        t = t.strip()
        # 去常见噪声标记
        t = re.sub(r'[\[\]（）()【】<>「」『』]+', ' ', t)
        t = re.sub(r'\s{2,}', ' ', t)
        return t
    except Exception:
        return str(text)


def _dedupe_and_clean_results(result_container):
    seen = set()
    deduped = []
    for item in getattr(result_container, 'results', []) or []:
        try:
            if isinstance(item, dict):
                url_val = item.get('url')
                title_val = item.get('title')
            else:
                url_val = getattr(item, 'url', None)
                title_val = getattr(item, 'title', None)

            fp_url = _normalize_url_for_fingerprint(url_val or '')
            fp_title = (_clean_text_noise(title_val or '')).lower()
            fingerprint = fp_url or fp_title
            if fingerprint in seen:
                continue
            seen.add(fingerprint)

            # 清洗文本字段
            cleaned_title = _clean_text_noise(title_val)
            content_val = item.get('content') if isinstance(item, dict) else getattr(item, 'content', '')
            cleaned_content = _clean_text_noise(content_val)
            if isinstance(item, dict):
                item['title'] = cleaned_title
                item['content'] = cleaned_content
                item['url'] = fp_url or (url_val or '')
            else:
                try:
                    setattr(item, 'title', cleaned_title)
                    setattr(item, 'content', cleaned_content)
                    setattr(item, 'url', fp_url or (url_val or ''))
                except Exception:
                    pass

            deduped.append(item)
        except Exception:
            deduped.append(item)

    if deduped:
        result_container.results = deduped
    return result_container


# -------------------------
# 简易内存缓存（TTL + 容量限制）
# -------------------------
_API_CACHE: dict[str, tuple[float, str]] = {}
_API_CACHE_LOCK = threading.Lock()
_API_CACHE_TTL_SEC = 60.0
_API_CACHE_MAX_ENTRIES = 512


def _cache_get(cache_key: str) -> typing.Optional[str]:
    now = time.time()
    with _API_CACHE_LOCK:
        hit = _API_CACHE.get(cache_key)
        if not hit:
            return None
        ts, val = hit
        if now - ts > _API_CACHE_TTL_SEC:
            _API_CACHE.pop(cache_key, None)
            return None
        return val


def _cache_set(cache_key: str, value: str) -> None:
    now = time.time()
    with _API_CACHE_LOCK:
        if len(_API_CACHE) >= _API_CACHE_MAX_ENTRIES:
            # 简单清理：删除最早插入的 10%（无序 dict 近似，足够简单）
            to_remove = int(max(1, _API_CACHE_MAX_ENTRIES * 0.1))
            for k in list(_API_CACHE.keys())[:to_remove]:
                _API_CACHE.pop(k, None)
        _API_CACHE[cache_key] = (now, value)


def _dedupe_list_for_web(results_list):
    """网页端列表级去重：
    - 规则1：规范化 URL 指纹完全相同 => 去重
    - 规则2：标题近似（相似度>=0.92 或包含关系）也视为重复；在这种情况下优先保留“更优主域”的结果
    """
    import difflib
    HOST_PRIORITY = {
        # 优先保留（数值越小越优先）
        'mp.weixin.qq.com': 0,
        '36kr.com': 1,
        'www.huxiu.com': 1,
        'www.cnbeta.com': 2,
        # 明显聚合/跳转域名（尽量丢弃）
        'weixin.sogou.com': 9,
        'www.sogou.com': 9,
        'sogou.com': 9,
        '360kuai.com': 9,
        'www.360kuai.com': 9,
        'baidu.com': 9,
        'www.baidu.com': 9,
    }

    def host_priority(url: str) -> int:
        try:
            host = urllib.parse.urlparse(url or '').netloc.lower()
            # 去掉常见 www 前缀统一判定
            if host.startswith('www.'):
                host_key = host
            else:
                host_key = host
            return HOST_PRIORITY.get(host_key, 5)
        except Exception:
            return 5

    kept = []
    fingerprints = []  # 与 kept 对齐，存(规范化URL, 规范化标题)
    for item in results_list or []:
        try:
            url_val = getattr(item, 'url', None) or (item.get('url') if isinstance(item, dict) else None)
            title_val = getattr(item, 'title', None) or (item.get('title') if isinstance(item, dict) else None)

            norm_url = _normalize_url_for_fingerprint(url_val or '')
            norm_title = (_clean_text_noise(title_val or '')).lower()

            # 规则1：URL 指纹完全一样 => 重复
            is_duplicate = False
            duplicate_index = -1
            for idx, (k_url, k_title) in enumerate(fingerprints):
                if norm_url and k_url and norm_url == k_url:
                    is_duplicate = True
                    duplicate_index = idx
                    break
            if not is_duplicate and norm_title:
                # 规则2：标题近似
                for idx, (k_url, k_title) in enumerate(fingerprints):
                    if not k_title:
                        continue
                    ratio = difflib.SequenceMatcher(None, norm_title, k_title).ratio()
                    if ratio >= 0.92 or norm_title in k_title or k_title in norm_title:
                        is_duplicate = True
                        duplicate_index = idx
                        break

            if not is_duplicate:
                kept.append(item)
                fingerprints.append((norm_url, norm_title))
            else:
                # 发生冲突：按主域优先级选择保留谁
                try:
                    current_priority = host_priority(norm_url or url_val or '')
                    exist_item = kept[duplicate_index]
                    exist_url = getattr(exist_item, 'url', None) or (exist_item.get('url') if isinstance(exist_item, dict) else None)
                    exist_priority = host_priority(_normalize_url_for_fingerprint(exist_url or '') or exist_url or '')
                    if current_priority < exist_priority:
                        kept[duplicate_index] = item
                        fingerprints[duplicate_index] = (norm_url, norm_title)
                except Exception:
                    pass
        except Exception:
            kept.append(item)
            fingerprints.append(('', ''))
    return kept

warnings.simplefilter("always")

# about static
logger.debug('static directory is %s', settings['ui']['static_path'])
static_files = get_static_files(settings['ui']['static_path'])

# about templates
logger.debug('templates directory is %s', settings['ui']['templates_path'])
default_theme = settings['ui']['default_theme']
templates_path = settings['ui']['templates_path']
themes = get_themes(templates_path)
result_templates = get_result_templates(templates_path)

STATS_SORT_PARAMETERS = {
    'name': (False, 'name', ''),
    'score': (True, 'score_per_result', 0),
    'result_count': (True, 'result_count', 0),
    'time': (False, 'total', 0),
    'reliability': (False, 'reliability', 100),
}

# Flask app
app = Flask(__name__, static_folder=settings['ui']['static_path'], template_folder=templates_path)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.add_extension('jinja2.ext.loopcontrols')  # pylint: disable=no-member
app.jinja_env.filters['group_engines_in_tab'] = group_engines_in_tab  # pylint: disable=no-member
app.secret_key = settings['server']['secret_key']


def get_locale():
    locale = localeselector()
    logger.debug("%s uses locale `%s`", urllib.parse.quote(sxng_request.url), locale)
    return locale


babel = Babel(app, locale_selector=get_locale)


def _get_browser_language(req, lang_list):
    client = ClientPref.from_http_request(req)
    locale = match_locale(client.locale_tag, lang_list, fallback='en')
    return locale


def _get_locale_rfc5646(locale):
    """Get locale name for <html lang="...">
    Chrom* browsers don't detect the language when there is a subtag (ie a territory).
    For example "zh-TW" is detected but not "zh-Hant-TW".
    This function returns a locale without the subtag.
    """
    parts = locale.split('-')
    return parts[0].lower() + '-' + parts[-1].upper()


# code-highlighter
@app.template_filter('code_highlighter')
def code_highlighter(codelines, language=None):
    if not language:
        language = 'text'

    try:
        # find lexer by programming language
        lexer = get_lexer_by_name(language, stripall=True)

    except Exception as e:  # pylint: disable=broad-except
        logger.warning("pygments lexer: %s " % e)
        # if lexer is not found, using default one
        lexer = get_lexer_by_name('text', stripall=True)

    html_code = ''
    tmp_code = ''
    last_line = None
    line_code_start = None

    # parse lines
    for line, code in codelines:
        if not last_line:
            line_code_start = line

        # new codeblock is detected
        if last_line is not None and last_line + 1 != line:

            # highlight last codepart
            formatter = HtmlFormatter(linenos='inline', linenostart=line_code_start, cssclass="code-highlight")
            html_code = html_code + highlight(tmp_code, lexer, formatter)

            # reset conditions for next codepart
            tmp_code = ''
            line_code_start = line

        # add codepart
        tmp_code += code + '\n'

        # update line
        last_line = line

    # highlight last codepart
    formatter = HtmlFormatter(linenos='inline', linenostart=line_code_start, cssclass="code-highlight")
    html_code = html_code + highlight(tmp_code, lexer, formatter)

    return html_code


def get_result_template(theme_name: str, template_name: str):
    themed_path = theme_name + '/result_templates/' + template_name
    if themed_path in result_templates:
        return themed_path
    return 'result_templates/' + template_name


def custom_url_for(endpoint: str, **values):
    suffix = ""
    if endpoint == 'static' and values.get('filename'):
        file_hash = static_files.get(values['filename'])
        if not file_hash:
            # try file in the current theme
            theme_name = sxng_request.preferences.get_value('theme')
            filename_with_theme = "themes/{}/{}".format(theme_name, values['filename'])
            file_hash = static_files.get(filename_with_theme)
            if file_hash:
                values['filename'] = filename_with_theme
        if get_setting('ui.static_use_hash') and file_hash:
            suffix = "?" + file_hash
    if endpoint == 'info' and 'locale' not in values:
        locale = sxng_request.preferences.get_value('locale')
        if infopage.INFO_PAGES.get_page(values['pagename'], locale) is None:
            locale = infopage.INFO_PAGES.locale_default
        values['locale'] = locale
    return url_for(endpoint, **values) + suffix


def image_proxify(url: str):
    if not url:
        return url

    if url.startswith('//'):
        url = 'https:' + url

    if not sxng_request.preferences.get_value('image_proxy'):
        return url

    if url.startswith('data:image/'):
        # 50 is an arbitrary number to get only the beginning of the image.
        partial_base64 = url[len('data:image/') : 50].split(';')
        if (
            len(partial_base64) == 2
            and partial_base64[0] in ['gif', 'png', 'jpeg', 'pjpeg', 'webp', 'tiff', 'bmp']
            and partial_base64[1].startswith('base64,')
        ):
            return url
        return None

    h = new_hmac(settings['server']['secret_key'], url.encode())

    return '{0}?{1}'.format(url_for('image_proxy'), urlencode(dict(url=url.encode(), h=h)))


def get_translations():
    return {
        # when there is autocompletion
        'no_item_found': gettext('No item found'),
        # /preferences: the source of the engine description (wikipedata, wikidata, website)
        'Source': gettext('Source'),
        # infinite scroll
        'error_loading_next_page': gettext('Error loading the next page'),
    }


def get_enabled_categories(category_names: typing.Iterable[str]):
    """The categories in ``category_names```for which there is no active engine
    are filtered out and a reduced list is returned."""

    enabled_engines = [item[0] for item in sxng_request.preferences.engines.get_enabled()]
    enabled_categories = set()
    for engine_name in enabled_engines:
        enabled_categories.update(engines[engine_name].categories)
    return [x for x in category_names if x in enabled_categories]


def get_pretty_url(parsed_url: urllib.parse.ParseResult):
    url_formatting_pref = sxng_request.preferences.get_value('url_formatting')

    if url_formatting_pref == 'full':
        return [parsed_url.geturl()]

    if url_formatting_pref == 'host':
        return [parsed_url.netloc]

    path = parsed_url.path
    path = path[:-1] if len(path) > 0 and path[-1] == '/' else path
    path = unquote(path.replace("/", " › "))
    return [parsed_url.scheme + "://" + parsed_url.netloc, path]


def get_client_settings():
    req_pref = sxng_request.preferences
    return {
        'autocomplete': req_pref.get_value('autocomplete'),
        'autocomplete_min': get_setting('search.autocomplete_min'),
        'method': req_pref.get_value('method'),
        'infinite_scroll': req_pref.get_value('infinite_scroll'),
        'translations': get_translations(),
        'search_on_category_select': req_pref.get_value('search_on_category_select'),
        'hotkeys': req_pref.get_value('hotkeys'),
        'url_formatting': req_pref.get_value('url_formatting'),
        'theme_static_path': custom_url_for('static', filename='themes/simple'),
        'results_on_new_tab': req_pref.get_value('results_on_new_tab'),
        'favicon_resolver': req_pref.get_value('favicon_resolver'),
        'advanced_search': req_pref.get_value('advanced_search'),
        'query_in_title': req_pref.get_value('query_in_title'),
        'safesearch': str(req_pref.get_value('safesearch')),
        'theme': req_pref.get_value('theme'),
        'doi_resolver': get_doi_resolver(),
    }


def render(template_name: str, **kwargs):
    # values from the preferences
    # pylint: disable=too-many-statements
    client_settings = get_client_settings()
    kwargs['client_settings'] = str(
        base64.b64encode(
            bytes(
                json.dumps(client_settings),
                encoding='utf-8',
            )
        ),
        encoding='utf-8',
    )
    kwargs['preferences'] = sxng_request.preferences
    kwargs.update(client_settings)

    # values from the HTTP requests
    kwargs['endpoint'] = 'results' if 'q' in kwargs else sxng_request.endpoint
    kwargs['cookies'] = sxng_request.cookies
    kwargs['errors'] = sxng_request.errors
    kwargs['link_token'] = link_token.get_token()

    kwargs['categories_as_tabs'] = list(settings['categories_as_tabs'].keys())
    kwargs['categories'] = get_enabled_categories(settings['categories_as_tabs'].keys())
    kwargs['DEFAULT_CATEGORY'] = DEFAULT_CATEGORY

    # i18n
    kwargs['sxng_locales'] = [l for l in sxng_locales if l[0] in settings['search']['languages']]

    locale = sxng_request.preferences.get_value('locale')
    kwargs['locale_rfc5646'] = _get_locale_rfc5646(locale)

    if locale in RTL_LOCALES and 'rtl' not in kwargs:
        kwargs['rtl'] = True

    if 'current_language' not in kwargs:
        kwargs['current_language'] = parse_lang(sxng_request.preferences, {}, RawTextQuery('', []))

    # values from settings
    kwargs['search_formats'] = [x for x in settings['search']['formats'] if x != 'html']
    kwargs['instance_name'] = get_setting('general.instance_name')
    kwargs['searx_version'] = VERSION_STRING
    kwargs['searx_git_url'] = GIT_URL
    kwargs['enable_metrics'] = get_setting('general.enable_metrics')
    kwargs['get_setting'] = get_setting
    kwargs['get_pretty_url'] = get_pretty_url

    # values from settings: donation_url
    donation_url = get_setting('general.donation_url')
    if donation_url is True:
        donation_url = custom_url_for('info', pagename='donate')
    kwargs['donation_url'] = donation_url

    # helpers to create links to other pages
    kwargs['url_for'] = custom_url_for  # override url_for function in templates
    kwargs['image_proxify'] = image_proxify
    kwargs['favicon_url'] = favicons.favicon_url
    kwargs['cache_url'] = settings['ui']['cache_url']
    kwargs['get_result_template'] = get_result_template
    kwargs['opensearch_url'] = (
        url_for('opensearch')
        + '?'
        + urlencode(
            {
                'method': sxng_request.preferences.get_value('method'),
                'autocomplete': sxng_request.preferences.get_value('autocomplete'),
            }
        )
    )
    kwargs['urlparse'] = urlparse

    start_time = default_timer()
    result = render_template('{}/{}'.format(kwargs['theme'], template_name), **kwargs)
    sxng_request.render_time += default_timer() - start_time  # pylint: disable=assigning-non-slot

    return result


@app.before_request
def pre_request():
    sxng_request.start_time = default_timer()  # pylint: disable=assigning-non-slot
    sxng_request.render_time = 0  # pylint: disable=assigning-non-slot
    sxng_request.timings = []  # pylint: disable=assigning-non-slot
    sxng_request.errors = []  # pylint: disable=assigning-non-slot

    client_pref = ClientPref.from_http_request(sxng_request)
    # pylint: disable=redefined-outer-name
    preferences = Preferences(themes, list(categories.keys()), engines, searx.plugins.STORAGE, client_pref)

    user_agent = sxng_request.headers.get('User-Agent', '').lower()
    if 'webkit' in user_agent and 'android' in user_agent:
        preferences.key_value_settings['method'].value = 'GET'
    sxng_request.preferences = preferences  # pylint: disable=assigning-non-slot

    try:
        preferences.parse_dict(sxng_request.cookies)

    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e, exc_info=True)
        sxng_request.errors.append(gettext('Invalid settings, please edit your preferences'))

    # merge GET, POST vars
    # HINT request.form is of type werkzeug.datastructures.ImmutableMultiDict
    sxng_request.form = dict(sxng_request.form.items())  # type: ignore
    for k, v in sxng_request.args.items():
        if k not in sxng_request.form:
            sxng_request.form[k] = v

    if sxng_request.form.get('preferences'):
        preferences.parse_encoded_data(sxng_request.form['preferences'])
    else:
        try:
            preferences.parse_dict(sxng_request.form)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e, exc_info=True)
            sxng_request.errors.append(gettext('Invalid settings'))

    # language is defined neither in settings nor in preferences
    # use browser headers
    if not preferences.get_value("language"):
        language = _get_browser_language(sxng_request, settings['search']['languages'])
        preferences.parse_dict({"language": language})
        logger.debug('set language %s (from browser)', preferences.get_value("language"))

    # UI locale is defined neither in settings nor in preferences
    # use browser headers
    if not preferences.get_value("locale"):
        locale = _get_browser_language(sxng_request, LOCALE_NAMES.keys())
        preferences.parse_dict({"locale": locale})
        logger.debug('set locale %s (from browser)', preferences.get_value("locale"))

    # request.user_plugins
    sxng_request.user_plugins = []  # pylint: disable=assigning-non-slot
    allowed_plugins = preferences.plugins.get_enabled()
    disabled_plugins = preferences.plugins.get_disabled()
    for plugin in searx.plugins.STORAGE:
        if (plugin.id not in disabled_plugins) or plugin.id in allowed_plugins:
            sxng_request.user_plugins.append(plugin.id)


@app.after_request
def add_default_headers(response: flask.Response):
    # set default http headers
    for header, value in settings['server']['default_http_headers'].items():
        if header in response.headers:
            continue
        response.headers[header] = value
    return response


@app.after_request
def post_request(response: flask.Response):
    total_time = default_timer() - sxng_request.start_time
    timings_all = [
        'total;dur=' + str(round(total_time * 1000, 3)),
        'render;dur=' + str(round(sxng_request.render_time * 1000, 3)),
    ]
    if len(sxng_request.timings) > 0:
        timings = sorted(sxng_request.timings, key=lambda t: t.total)
        timings_total = [
            'total_' + str(i) + '_' + t.engine + ';dur=' + str(round(t.total * 1000, 3)) for i, t in enumerate(timings)
        ]
        timings_load = [
            'load_' + str(i) + '_' + t.engine + ';dur=' + str(round(t.load * 1000, 3))
            for i, t in enumerate(timings)
            if t.load
        ]
        timings_all = timings_all + timings_total + timings_load
    response.headers.add('Server-Timing', ', '.join(timings_all))
    return response


def index_error(output_format: str, error_message: str):
    if output_format == 'json':
        return Response(json.dumps({'error': error_message}), mimetype='application/json')
    if output_format == 'csv':
        response = Response('', mimetype='application/csv')
        cont_disp = 'attachment;Filename=searx.csv'
        response.headers.add('Content-Disposition', cont_disp)
        return response

    if output_format == 'rss':
        response_rss = render(
            'opensearch_response_rss.xml',
            results=[],
            q=sxng_request.form['q'] if 'q' in sxng_request.form else '',
            number_of_results=0,
            error_message=error_message,
        )
        return Response(response_rss, mimetype='text/xml')

    # html
    sxng_request.errors.append(gettext('search error'))
    return render(
        # fmt: off
        'index.html',
        selected_categories=get_selected_categories(sxng_request.preferences, sxng_request.form),
        # fmt: on
    )


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render index page."""

    # redirect to search if there's a query in the request
    if sxng_request.form.get('q'):
        query = ('?' + sxng_request.query_string.decode()) if sxng_request.query_string else ''
        return redirect(url_for('search') + query, 308)

    return render(
        # fmt: off
        'index.html',
        selected_categories=get_selected_categories(sxng_request.preferences, sxng_request.form),
        current_locale = sxng_request.preferences.get_value("locale"),
        # fmt: on
    )


@app.route('/healthz', methods=['GET'])
def health():
    return Response('OK', mimetype='text/plain')


@app.route('/client<token>.css', methods=['GET', 'POST'])
def client_token(token=None):
    link_token.ping(sxng_request, token)
    return Response('', mimetype='text/css', headers={"Cache-Control": "no-store, max-age=0"})


@app.route('/rss.xsl', methods=['GET', 'POST'])
def rss_xsl():
    return render_template(
        f"{sxng_request.preferences.get_value('theme')}/rss.xsl",
        url_for=custom_url_for,
    )


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search query in q and return results.

    Supported outputs: html, json, csv, rss.
    """
    # pylint: disable=too-many-locals, too-many-return-statements, too-many-branches
    # pylint: disable=too-many-statements

    # output_format
    output_format = sxng_request.form.get('format', 'html')
    if output_format not in OUTPUT_FORMATS:
        output_format = 'html'

    if output_format not in settings['search']['formats']:
        flask.abort(403)

    # check if there is query (not None and not an empty string)
    if not sxng_request.form.get('q'):
        if output_format == 'html':
            return render(
                # fmt: off
                'index.html',
                selected_categories=get_selected_categories(sxng_request.preferences, sxng_request.form),
                # fmt: on
            )
        return index_error(output_format, 'No query'), 400

    # search
    search_query = None
    raw_text_query = None
    result_container = None
    try:
        search_query, raw_text_query, _, _, selected_locale = get_search_query_from_webapp(
            sxng_request.preferences, sxng_request.form
        )
        search_obj = searx.search.SearchWithPlugins(search_query, sxng_request, sxng_request.user_plugins)
        result_container = search_obj.search()

    except SearxParameterException as e:
        logger.exception('search error: SearxParameterException')
        return index_error(output_format, e.message), 400
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e, exc_info=True)
        return index_error(output_format, gettext('search error')), 500

    # 1. check if the result is a redirect for an external bang
    if result_container.redirect_url:
        return redirect(result_container.redirect_url)

    # 2. add Server-Timing header for measuring performance characteristics of
    # web applications
    sxng_request.timings = result_container.get_timings()  # pylint: disable=assigning-non-slot

    # 3. formats without a template

    if output_format == 'json':

        response = webutils.get_json_response(search_query, result_container)
        return Response(response, mimetype='application/json')

    if output_format == 'csv':

        csv = webutils.CSVWriter(StringIO())
        webutils.write_csv_response(csv, result_container)
        csv.stream.seek(0)

        response = Response(csv.stream.read(), mimetype='application/csv')
        cont_disp = 'attachment;Filename=searx_-_{0}.csv'.format(search_query.query)
        response.headers.add('Content-Disposition', cont_disp)
        return response

    # 4. formats rendered by a template / RSS & HTML

    current_template = None
    previous_result = None

    results = result_container.get_ordered_results()
    # 列表级去重（标题/URL）+ 过滤低相关 + 时间优先排序 + 组内相关性（文本模板）
    results = _dedupe_list_for_web(results)
    results = _filter_low_relevance_for_web(search_query.query, results, min_score=0.8)
    results = _sort_results_list_by_time(results)
    results = _re_rank_results_for_web_list(search_query.query, results, keep_time_bias=True)
    # 网页端：清洗文本噪声，提升可读性
    for result in results:
        if output_format == 'html':
            if 'content' in result and result['content']:
                result['content'] = _clean_text_noise(result['content'])
                result['content'] = highlight_content(escape(result['content'][:1024]), search_query.query)
            if 'title' in result and result['title']:
                result['title'] = _clean_text_noise(result['title'])
                result['title'] = highlight_content(escape(result['title'] or ''), search_query.query)

    if search_query.redirect_to_first_result and results:
        return redirect(results[0]['url'], 302)

    # 在分组标记之前：对组内进行相关性重排（仅文本模板），避免跨模板分组被打散
    _re_rank_results_for_web(search_query.query, result_container, keep_time_bias=True, include_score=False)
    results = result_container.get_ordered_results()
    results = _dedupe_list_for_web(results)
    results = _filter_low_relevance_for_web(search_query.query, results, min_score=0.8)
    results = _sort_results_list_by_time(results)
    results = _re_rank_results_for_web_list(search_query.query, results, keep_time_bias=True)

    for result in results:
        if output_format == 'html':
            if 'content' in result and result['content']:
                result['content'] = highlight_content(escape(result['content'][:1024]), search_query.query)
            if 'title' in result and result['title']:
                result['title'] = highlight_content(escape(result['title'] or ''), search_query.query)

        # set result['open_group'] = True when the template changes from the previous result
        # set result['close_group'] = True when the template changes on the next result
        if current_template != result.template:
            result.open_group = True
            if previous_result:
                previous_result.close_group = True  # pylint: disable=unsupported-assignment-operation
        current_template = result.template
        previous_result = result

    if previous_result:
        previous_result.close_group = True

    # 4.a RSS

    if output_format == 'rss':
        response_rss = render(
            'opensearch_response_rss.xml',
            results=results,
            q=sxng_request.form['q'],
            number_of_results=result_container.number_of_results,
        )
        return Response(response_rss, mimetype='text/xml')

    # 4.b HTML

    # suggestions: use RawTextQuery to get the suggestion URLs with the same bang
    suggestion_urls = list(
        map(
            lambda suggestion: {'url': raw_text_query.changeQuery(suggestion).getFullQuery(), 'title': suggestion},
            result_container.suggestions,
        )
    )

    correction_urls = list(
        map(
            lambda correction: {'url': raw_text_query.changeQuery(correction).getFullQuery(), 'title': correction},
            result_container.corrections,
        )
    )

    # engine_timings: get engine response times sorted from slowest to fastest
    engine_timings = sorted(result_container.get_timings(), reverse=True, key=lambda e: e.total)
    max_response_time = engine_timings[0].total if engine_timings else None
    engine_timings_pairs = [(timing.engine, timing.total) for timing in engine_timings]

    # search_query.lang contains the user choice (all, auto, en, ...)
    # when the user choice is "auto", search.search_query.lang contains the detected language
    # otherwise it is equals to search_query.lang
    return render(
        # fmt: off
        'results.html',
        results = results,
        q=sxng_request.form['q'],
        selected_categories = search_query.categories,
        pageno = search_query.pageno,
        time_range = search_query.time_range or '',
        number_of_results = format_decimal(result_container.number_of_results),
        suggestions = suggestion_urls,
        answers = result_container.answers,
        corrections = correction_urls,
        infoboxes = result_container.infoboxes,
        engine_data = result_container.engine_data,
        paging = result_container.paging,
        unresponsive_engines = webutils.get_translated_errors(
            result_container.unresponsive_engines
        ),
        current_locale = sxng_request.preferences.get_value("locale"),
        current_language = selected_locale,
        search_language = match_locale(
            search_obj.search_query.lang,
            settings['search']['languages'],
            fallback=sxng_request.preferences.get_value("language")
        ),
        timeout_limit = sxng_request.form.get('timeout_limit', None),
        timings = engine_timings_pairs,
        max_response_time = max_response_time
        # fmt: on
    )


@app.route('/wechat_search', methods=['GET', 'POST'])
def wechat_search():
    """专门的微信公众号搜索API
    
    只使用微信相关的搜索引擎进行搜索
    支持的输出格式: json
    
    参数:
    - q: 搜索关键词 (必需)
    - limit: 返回结果数量限制 (可选，默认10，最大100)
    - sort_by_time: 是否按时间排序 (可选，默认true)
    """
    # 强制使用JSON格式
    output_format = 'json'
    
    # 检查是否有查询参数
    query = sxng_request.form.get('q') or sxng_request.args.get('q')
    if not query:
        return jsonify({
            'error': 'No query provided',
            'message': '请提供搜索关键词'
        }), 400

    # 获取返回条数限制
    limit = sxng_request.form.get('limit') or sxng_request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
            # 限制范围在1-100之间
            limit = max(1, min(100, limit))
        except ValueError:
            limit = 10
    else:
        limit = 10

    # 获取排序参数
    sort_by_time = sxng_request.form.get('sort_by_time') or sxng_request.args.get('sort_by_time')
    sort_by_time = sort_by_time and sort_by_time.lower() in ['true', '1', 'yes']

    try:
        # 创建一个包含查询参数的form对象
        from werkzeug.datastructures import MultiDict
        form_data = MultiDict()
        form_data['q'] = query
        form_data['format'] = 'json'
        if limit:
            form_data['pageno'] = '1'
        
        # 获取搜索查询对象
        search_query, raw_text_query, _, _, selected_locale = get_search_query_from_webapp(
            sxng_request.preferences, form_data
        )
        
        # 设置返回条数
        search_query.pageno = 1
        # 注意：results_per_page不是SearchQuery的属性，而是在各个引擎中定义的
        
        # 重写engineref_list，只包含微信相关引擎
        from searx.search.models import EngineRef
        wechat_engines = []
        
        # 添加微信相关的搜索引擎
        for engine_name in ['wechat', 'sogou wechat']:
            if engine_name in engines:
                wechat_engines.append(EngineRef(engine_name, 'general'))
        
        # 如果没有可用的微信引擎，返回错误
        if not wechat_engines:
            return jsonify({
                'error': 'No WeChat engines available',
                'message': '微信搜索引擎不可用'
            }), 503
        
        # 替换搜索引擎列表
        search_query.engineref_list = wechat_engines
        
        # 缓存键
        cache_key = f"wechat::{query}::p1::limit={limit}::debug={debug_score}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return Response(cached, mimetype='application/json')

        # 执行搜索
        search_obj = searx.search.SearchWithPlugins(search_query, sxng_request, sxng_request.user_plugins)
        result_container = search_obj.search()

        # 去重与清洗
        _dedupe_and_clean_results(result_container)
        # 相关性重排（轻量级）+ 时间微偏好 + 可选透出分数（API默认仍保留新鲜度）
        debug_score = sxng_request.form.get('debug_score') or sxng_request.args.get('debug_score')
        debug_score = bool(debug_score and str(debug_score).lower() in ['true', '1', 'yes'])
        _re_rank_results(query, result_container, keep_time_bias=True, include_score=debug_score)

        # 返回JSON响应
        response = webutils.get_json_response(search_query, result_container)
        _cache_set(cache_key, response)
        return Response(response, mimetype='application/json')

    except SearxParameterException as e:
        logger.exception('wechat search error: SearxParameterException')
        return jsonify({
            'error': 'Search parameter error',
            'message': str(e.message)
        }), 400
    except Exception as e:  # pylint: disable=broad-except
        logger.exception('wechat search error', exc_info=True)
        return jsonify({
            'error': 'Internal search error',
            'message': '搜索过程中发生错误'
        }), 500


@app.route('/chinese_search', methods=['GET', 'POST'])
def chinese_search():
    """专门的中文搜索API
    
    使用您指定的中文搜索引擎：sogou, baidu, 360search, wechat
    支持的输出格式: json
    
    参数:
    - q: 搜索关键词 (必需)
    - limit: 返回结果数量限制 (可选，默认10，最大100)
    - engines: 指定搜索引擎 (可选，默认使用所有中文引擎)
    - sort_by_time: 是否按时间排序 (可选，默认true)
    """
    # 强制使用JSON格式
    output_format = 'json'
    
    # 检查是否有查询参数
    query = sxng_request.form.get('q') or sxng_request.args.get('q')
    if not query:
        return jsonify({
            'error': 'No query provided',
            'message': '请提供搜索关键词'
        }), 400

    # 获取返回条数限制
    limit = sxng_request.form.get('limit') or sxng_request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
            # 限制范围在1-100之间
            limit = max(1, min(100, limit))
        except ValueError:
            limit = 10
    else:
        limit = 10

    # 获取指定的搜索引擎
    specified_engines = sxng_request.form.get('engines') or sxng_request.args.get('engines')
    if specified_engines:
        specified_engines = [e.strip() for e in specified_engines.split(',')]
    else:
        specified_engines = ['sogou', 'baidu', '360search', 'wechat']

    # 获取排序参数
    sort_by_time = sxng_request.form.get('sort_by_time') or sxng_request.args.get('sort_by_time')
    sort_by_time = sort_by_time and sort_by_time.lower() in ['true', '1', 'yes']

    try:
        # 创建一个包含查询参数的form对象
        from werkzeug.datastructures import MultiDict
        form_data = MultiDict()
        form_data['q'] = query
        form_data['format'] = 'json'
        if limit:
            form_data['pageno'] = '1'
        
        # 获取搜索查询对象
        search_query, raw_text_query, _, _, selected_locale = get_search_query_from_webapp(
            sxng_request.preferences, form_data
        )
        
        # 设置返回条数
        search_query.pageno = 1
        # 注意：results_per_page不是SearchQuery的属性，而是在各个引擎中定义的
        
        # 重写engineref_list，只包含您指定的中文搜索引擎
        from searx.search.models import EngineRef
        chinese_engines = []
        
        # 添加您指定的中文搜索引擎（按优先级排序）
        for engine_name in specified_engines:
            if engine_name in engines:
                chinese_engines.append(EngineRef(engine_name, 'general'))
        
        # 如果没有可用的中文引擎，返回错误
        if not chinese_engines:
            return jsonify({
                'error': 'No Chinese engines available',
                'message': '中文搜索引擎不可用',
                'available_engines': list(engines.keys())
            }), 503
        
        # 替换搜索引擎列表
        search_query.engineref_list = chinese_engines
        
        # 缓存键（包含引擎列表）
        cache_key = f"chinese::{query}::p1::{'-'.join(specified_engines)}::limit={limit}::debug={debug_score}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return Response(cached, mimetype='application/json')

        # 执行搜索
        search_obj = searx.search.SearchWithPlugins(search_query, sxng_request, sxng_request.user_plugins)
        result_container = search_obj.search()

        # 去重与清洗
        _dedupe_and_clean_results(result_container)
        # 相关性重排（轻量级）+ 时间微偏好 + 可选透出分数（API默认仍保留新鲜度）
        debug_score = sxng_request.form.get('debug_score') or sxng_request.args.get('debug_score')
        debug_score = bool(debug_score and str(debug_score).lower() in ['true', '1', 'yes'])
        _re_rank_results(query, result_container, keep_time_bias=True, include_score=debug_score)

        # 返回JSON响应
        response = webutils.get_json_response(search_query, result_container)
        _cache_set(cache_key, response)
        return Response(response, mimetype='application/json')

    except SearxParameterException as e:
        logger.exception('chinese search error: SearxParameterException')
        return jsonify({
            'error': 'Search parameter error',
            'message': str(e.message)
        }), 400
    except Exception as e:  # pylint: disable=broad-except
        logger.exception('chinese search error', exc_info=True)
        return jsonify({
            'error': 'Internal search error',
            'message': '搜索过程中发生错误'
        }), 500


@app.route('/about', methods=['GET'])
def about():
    """Redirect to about page"""
    # custom_url_for is going to add the locale
    return redirect(custom_url_for('info', pagename='about'))


@app.route('/info/<locale>/<pagename>', methods=['GET'])
def info(pagename, locale):
    """Render page of online user documentation"""
    page = infopage.INFO_PAGES.get_page(pagename, locale)
    if page is None:
        flask.abort(404)

    user_locale = sxng_request.preferences.get_value('locale')
    return render(
        'info.html',
        all_pages=infopage.INFO_PAGES.iter_pages(user_locale, fallback_to_default=True),
        active_page=page,
        active_pagename=pagename,
    )


@app.route('/autocompleter', methods=['GET', 'POST'])
def autocompleter():
    """Return autocompleter results"""

    # run autocompleter
    results = []

    # set blocked engines
    disabled_engines = sxng_request.preferences.engines.get_disabled()

    # parse query
    raw_text_query = RawTextQuery(sxng_request.form.get('q', ''), disabled_engines)
    sug_prefix = raw_text_query.getQuery()

    for obj in searx.answerers.STORAGE.ask(sug_prefix):
        if isinstance(obj, Answer):
            results.append(obj.answer)

    # normal autocompletion results only appear if no inner results returned
    # and there is a query part
    if len(raw_text_query.autocomplete_list) == 0 and len(sug_prefix) > 0:

        # get SearXNG's locale and autocomplete backend from cookie
        sxng_locale = sxng_request.preferences.get_value('language')
        backend_name = sxng_request.preferences.get_value('autocomplete')

        for result in search_autocomplete(backend_name, sug_prefix, sxng_locale):
            # attention: this loop will change raw_text_query object and this is
            # the reason why the sug_prefix was stored before (see above)
            if result != sug_prefix:
                results.append(raw_text_query.changeQuery(result).getFullQuery())

    if len(raw_text_query.autocomplete_list) > 0:
        for autocomplete_text in raw_text_query.autocomplete_list:
            results.append(raw_text_query.get_autocomplete_full_query(autocomplete_text))

    if sxng_request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # the suggestion request comes from the searx search form
        suggestions = json.dumps(results)
        mimetype = 'application/json'
    else:
        # the suggestion request comes from browser's URL bar
        suggestions = json.dumps([sug_prefix, results])
        mimetype = 'application/x-suggestions+json'

    suggestions = escape(suggestions, False)
    return Response(suggestions, mimetype=mimetype)


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """Render preferences page && save user preferences"""

    # pylint: disable=too-many-locals, too-many-return-statements, too-many-branches
    # pylint: disable=too-many-statements

    # save preferences using the link the /preferences?preferences=...
    if sxng_request.args.get('preferences') or sxng_request.form.get('preferences'):
        resp = make_response(redirect(url_for('index', _external=True)))
        return sxng_request.preferences.save(resp)

    # save preferences
    if sxng_request.method == 'POST':
        resp = make_response(redirect(url_for('index', _external=True)))
        try:
            sxng_request.preferences.parse_form(sxng_request.form)
        except ValidationException:
            sxng_request.errors.append(gettext('Invalid settings, please edit your preferences'))
            return resp
        return sxng_request.preferences.save(resp)

    # render preferences
    image_proxy = sxng_request.preferences.get_value('image_proxy')  # pylint: disable=redefined-outer-name
    disabled_engines = sxng_request.preferences.engines.get_disabled()
    allowed_plugins = sxng_request.preferences.plugins.get_enabled()

    # stats for preferences page
    filtered_engines = dict(filter(lambda kv: sxng_request.preferences.validate_token(kv[1]), engines.items()))

    engines_by_category = {}

    for c in categories:  # pylint: disable=consider-using-dict-items
        engines_by_category[c] = [e for e in categories[c] if e.name in filtered_engines]
        # sort the engines alphabetically since the order in settings.yml is meaningless.
        list.sort(engines_by_category[c], key=lambda e: e.name)

    # get first element [0], the engine time,
    # and then the second element [1] : the time (the first one is the label)
    stats = {}  # pylint: disable=redefined-outer-name
    max_rate95 = 0
    for _, e in filtered_engines.items():
        h = histogram('engine', e.name, 'time', 'total')
        median = round(h.percentage(50), 1) if h.count > 0 else None
        rate80 = round(h.percentage(80), 1) if h.count > 0 else None
        rate95 = round(h.percentage(95), 1) if h.count > 0 else None

        max_rate95 = max(max_rate95, rate95 or 0)

        result_count_sum = histogram('engine', e.name, 'result', 'count').sum
        successful_count = counter('engine', e.name, 'search', 'count', 'successful')
        result_count = int(result_count_sum / float(successful_count)) if successful_count else 0

        stats[e.name] = {
            'time': median,
            'rate80': rate80,
            'rate95': rate95,
            'warn_timeout': e.timeout > settings['outgoing']['request_timeout'],
            'supports_selected_language': e.traits.is_locale_supported(
                str(sxng_request.preferences.get_value('language') or 'all')
            ),
            'result_count': result_count,
        }
    # end of stats

    # reliabilities
    reliabilities = {}
    engine_errors = get_engine_errors(filtered_engines)
    checker_results = checker_get_result()
    checker_results = (
        checker_results['engines'] if checker_results['status'] == 'ok' and 'engines' in checker_results else {}
    )
    for _, e in filtered_engines.items():
        checker_result = checker_results.get(e.name, {})
        checker_success = checker_result.get('success', True)
        errors = engine_errors.get(e.name) or []
        if counter('engine', e.name, 'search', 'count', 'sent') == 0:
            # no request
            reliability = None
        elif checker_success and not errors:
            reliability = 100
        elif 'simple' in checker_result.get('errors', {}):
            # the basic (simple) test doesn't work: the engine is broken according to the checker
            # even if there is no exception
            reliability = 0
        else:
            # pylint: disable=consider-using-generator
            reliability = 100 - sum([error['percentage'] for error in errors if not error.get('secondary')])

        reliabilities[e.name] = {
            'reliability': reliability,
            'errors': [],
            'checker': checker_results.get(e.name, {}).get('errors', {}).keys(),
        }
        # keep the order of the list checker_results[e.name]['errors'] and deduplicate.
        # the first element has the highest percentage rate.
        reliabilities_errors = []
        for error in errors:
            error_user_text = None
            if error.get('secondary') or 'exception_classname' not in error:
                continue
            error_user_text = exception_classname_to_text.get(error.get('exception_classname'))
            if not error:
                error_user_text = exception_classname_to_text[None]
            if error_user_text not in reliabilities_errors:
                reliabilities_errors.append(error_user_text)
        reliabilities[e.name]['errors'] = reliabilities_errors

    # supports
    supports = {}
    for _, e in filtered_engines.items():
        supports_selected_language = e.traits.is_locale_supported(
            str(sxng_request.preferences.get_value('language') or 'all')
        )
        safesearch = e.safesearch
        time_range_support = e.time_range_support
        for checker_test_name in checker_results.get(e.name, {}).get('errors', {}):
            if supports_selected_language and checker_test_name.startswith('lang_'):
                supports_selected_language = '?'
            elif safesearch and checker_test_name == 'safesearch':
                safesearch = '?'
            elif time_range_support and checker_test_name == 'time_range':
                time_range_support = '?'
        supports[e.name] = {
            'supports_selected_language': supports_selected_language,
            'safesearch': safesearch,
            'time_range_support': time_range_support,
        }

    return render(
        # fmt: off
        'preferences.html',
        preferences = True,
        selected_categories = get_selected_categories(sxng_request.preferences, sxng_request.form),
        locales = LOCALE_NAMES,
        current_locale = sxng_request.preferences.get_value("locale"),
        image_proxy = image_proxy,
        engines_by_category = engines_by_category,
        stats = stats,
        max_rate95 = max_rate95,
        reliabilities = reliabilities,
        supports = supports,
        answer_storage = searx.answerers.STORAGE.info,
        disabled_engines = disabled_engines,
        autocomplete_backends = autocomplete_backends,
        favicon_resolver_names = favicons.proxy.CFG.resolver_map.keys(),
        shortcuts = {y: x for x, y in engine_shortcuts.items()},
        themes = themes,
        plugins_storage = searx.plugins.STORAGE.info,
        current_doi_resolver = get_doi_resolver(),
        allowed_plugins = allowed_plugins,
        preferences_url_params = sxng_request.preferences.get_as_url_params(),
        locked_preferences = get_setting("preferences.lock", []),
        doi_resolvers = get_setting("doi_resolvers", {}),
        # fmt: on
    )


app.add_url_rule('/favicon_proxy', methods=['GET'], endpoint="favicon_proxy", view_func=favicons.favicon_proxy)


@app.route('/image_proxy', methods=['GET'])
def image_proxy():
    # pylint: disable=too-many-return-statements, too-many-branches

    url = sxng_request.args.get('url')
    if not url:
        return '', 400

    if not is_hmac_of(settings['server']['secret_key'], url.encode(), sxng_request.args.get('h', '')):
        return '', 400

    maximum_size = 5 * 1024 * 1024
    forward_resp = False
    resp = None
    try:
        request_headers = {
            'User-Agent': gen_useragent(),
            'Accept': 'image/webp,*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Sec-GPC': '1',
            'DNT': '1',
        }
        set_context_network_name('image_proxy')
        resp, stream = http_stream(method='GET', url=url, headers=request_headers, allow_redirects=True)
        content_length = resp.headers.get('Content-Length')
        if content_length and content_length.isdigit() and int(content_length) > maximum_size:
            return 'Max size', 400

        if resp.status_code != 200:
            logger.debug('image-proxy: wrong response code: %i', resp.status_code)
            if resp.status_code >= 400:
                return '', resp.status_code
            return '', 400

        if not resp.headers.get('Content-Type', '').startswith('image/') and not resp.headers.get(
            'Content-Type', ''
        ).startswith('binary/octet-stream'):
            logger.debug('image-proxy: wrong content-type: %s', resp.headers.get('Content-Type', ''))
            return '', 400

        forward_resp = True
    except httpx.HTTPError:
        logger.exception('HTTP error')
        return '', 400
    finally:
        if resp and not forward_resp:
            # the code is about to return an HTTP 400 error to the browser
            # we make sure to close the response between searxng and the HTTP server
            try:
                resp.close()
            except httpx.HTTPError:
                logger.exception('HTTP error on closing')

    def close_stream():
        nonlocal resp, stream
        try:
            if resp:
                resp.close()
            del resp
            del stream
        except httpx.HTTPError as e:
            logger.debug('Exception while closing response', e)

    try:
        headers = dict_subset(resp.headers, {'Content-Type', 'Content-Encoding', 'Content-Length', 'Length'})
        response = Response(stream, mimetype=resp.headers['Content-Type'], headers=headers, direct_passthrough=True)
        response.call_on_close(close_stream)
        return response
    except httpx.HTTPError:
        close_stream()
        return '', 400


@app.route('/engine_descriptions.json', methods=['GET'])
def engine_descriptions():
    sxng_ui_lang_tag = get_locale().replace("_", "-")
    sxng_ui_lang_tag = LOCALE_BEST_MATCH.get(sxng_ui_lang_tag, sxng_ui_lang_tag)

    result = ENGINE_DESCRIPTIONS['en'].copy()
    if sxng_ui_lang_tag != 'en':
        for engine, description in ENGINE_DESCRIPTIONS.get(sxng_ui_lang_tag, {}).items():
            result[engine] = description
    for engine, description in result.items():
        if len(description) == 2 and description[1] == 'ref':
            ref_engine, ref_lang = description[0].split(':')
            description = ENGINE_DESCRIPTIONS[ref_lang][ref_engine]
        if isinstance(description, str):
            description = [description, 'wikipedia']
        result[engine] = description

    # overwrite by about:description (from settings)
    for engine_name, engine_mod in engines.items():
        descr = getattr(engine_mod, 'about', {}).get('description', None)
        if descr is not None:
            result[engine_name] = [descr, "SearXNG config"]

    return jsonify(result)


@app.route('/stats', methods=['GET'])
def stats():
    """Render engine statistics page."""
    sort_order = sxng_request.args.get('sort', default='name', type=str)
    selected_engine_name = sxng_request.args.get('engine', default=None, type=str)

    filtered_engines = dict(filter(lambda kv: sxng_request.preferences.validate_token(kv[1]), engines.items()))
    if selected_engine_name:
        if selected_engine_name not in filtered_engines:
            selected_engine_name = None
        else:
            filtered_engines = [selected_engine_name]

    checker_results = checker_get_result()
    checker_results = (
        checker_results['engines'] if checker_results['status'] == 'ok' and 'engines' in checker_results else {}
    )

    engine_stats = get_engines_stats(filtered_engines)
    engine_reliabilities = get_reliabilities(filtered_engines, checker_results)

    if sort_order not in STATS_SORT_PARAMETERS:
        sort_order = 'name'

    reverse, key_name, default_value = STATS_SORT_PARAMETERS[sort_order]

    def get_key(engine_stat):
        reliability = engine_reliabilities.get(engine_stat['name'], {}).get('reliability', 0)
        reliability_order = 0 if reliability else 1
        if key_name == 'reliability':
            key = reliability
            reliability_order = 0
        else:
            key = engine_stat.get(key_name) or default_value
            if reverse:
                reliability_order = 1 - reliability_order
        return (reliability_order, key, engine_stat['name'])

    technical_report = []
    for error in engine_reliabilities.get(selected_engine_name, {}).get('errors', []):
        technical_report.append(
            f"\
            Error: {error['exception_classname'] or error['log_message']} \
            Parameters: {error['log_parameters']} \
            File name: {error['filename'] }:{ error['line_no'] } \
            Error Function: {error['function']} \
            Code: {error['code']} \
            ".replace(
                ' ' * 12, ''
            ).strip()
        )
    technical_report = ' '.join(technical_report)

    engine_stats['time'] = sorted(engine_stats['time'], reverse=reverse, key=get_key)
    return render(
        # fmt: off
        'stats.html',
        sort_order = sort_order,
        engine_stats = engine_stats,
        engine_reliabilities = engine_reliabilities,
        selected_engine_name = selected_engine_name,
        searx_git_branch = GIT_BRANCH,
        technical_report = technical_report,
        # fmt: on
    )


@app.route('/stats/errors', methods=['GET'])
def stats_errors():
    filtered_engines = dict(filter(lambda kv: sxng_request.preferences.validate_token(kv[1]), engines.items()))
    result = get_engine_errors(filtered_engines)
    return jsonify(result)


@app.route('/stats/checker', methods=['GET'])
def stats_checker():
    result = checker_get_result()
    return jsonify(result)


@app.route('/metrics')
def stats_open_metrics():
    password = settings['general'].get("open_metrics")

    if not (settings['general'].get("enable_metrics") and password):
        return Response('open metrics is disabled', status=404, mimetype='text/plain')

    if not sxng_request.authorization or sxng_request.authorization.password != password:
        return Response('access forbidden', status=401, mimetype='text/plain')

    filtered_engines = dict(filter(lambda kv: sxng_request.preferences.validate_token(kv[1]), engines.items()))

    checker_results = checker_get_result()
    checker_results = (
        checker_results['engines'] if checker_results['status'] == 'ok' and 'engines' in checker_results else {}
    )

    engine_stats = get_engines_stats(filtered_engines)
    engine_reliabilities = get_reliabilities(filtered_engines, checker_results)
    metrics_text = openmetrics(engine_stats, engine_reliabilities)

    return Response(metrics_text, mimetype='text/plain')


@app.route('/robots.txt', methods=['GET'])
def robots():
    return Response(
        """User-agent: *
Allow: /info/en/about
Disallow: /stats
Disallow: /image_proxy
Disallow: /preferences
Disallow: /*?*q=*
""",
        mimetype='text/plain',
    )


@app.route('/opensearch.xml', methods=['GET'])
def opensearch():
    method = sxng_request.preferences.get_value('method')
    autocomplete = sxng_request.preferences.get_value('autocomplete')

    # chrome/chromium only supports HTTP GET....
    if sxng_request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'GET'

    if method not in ('POST', 'GET'):
        method = 'POST'

    ret = render('opensearch.xml', opensearch_method=method, autocomplete=autocomplete)
    resp = Response(response=ret, status=200, mimetype="application/opensearchdescription+xml")
    return resp


@app.route('/favicon.ico')
def favicon():
    theme = sxng_request.preferences.get_value("theme")
    return send_from_directory(
        os.path.join(app.root_path, settings['ui']['static_path'], 'themes', theme, 'img'),  # type: ignore
        'favicon.png',
        mimetype='image/vnd.microsoft.icon',
    )


@app.route('/clear_cookies')
def clear_cookies():
    resp = make_response(redirect(url_for('index', _external=True)))
    for cookie_name in sxng_request.cookies:
        resp.delete_cookie(cookie_name)
    return resp


@app.route('/config')
def config():
    """Return configuration in JSON format."""
    _engines = []
    for name, engine in engines.items():
        if not sxng_request.preferences.validate_token(engine):
            continue

        _languages = engine.traits.languages.keys()
        _engines.append(
            {
                'name': name,
                'categories': engine.categories,
                'shortcut': engine.shortcut,
                'enabled': not engine.disabled,
                'paging': engine.paging,
                'language_support': engine.language_support,
                'languages': list(_languages),
                'regions': list(engine.traits.regions.keys()),
                'safesearch': engine.safesearch,
                'time_range_support': engine.time_range_support,
                'timeout': engine.timeout,
            }
        )

    _plugins = []
    for _ in searx.plugins.STORAGE:
        _plugins.append({'name': _.id, 'enabled': _.active})

    _limiter_cfg = limiter.get_cfg()

    return jsonify(
        {
            'categories': list(categories.keys()),
            'engines': _engines,
            'plugins': _plugins,
            'instance_name': settings['general']['instance_name'],
            'locales': LOCALE_NAMES,
            'default_locale': settings['ui']['default_locale'],
            'autocomplete': settings['search']['autocomplete'],
            'safe_search': settings['search']['safe_search'],
            'default_theme': settings['ui']['default_theme'],
            'version': VERSION_STRING,
            'brand': {
                'PRIVACYPOLICY_URL': get_setting('general.privacypolicy_url'),
                'CONTACT_URL': get_setting('general.contact_url'),
                'GIT_URL': GIT_URL,
                'GIT_BRANCH': GIT_BRANCH,
                'DOCS_URL': get_setting('brand.docs_url'),
            },
            'limiter': {
                'enabled': limiter.is_installed(),
                'botdetection.ip_limit.link_token': _limiter_cfg.get('botdetection.ip_limit.link_token'),
                'botdetection.ip_lists.pass_searxng_org': _limiter_cfg.get('botdetection.ip_lists.pass_searxng_org'),
            },
            'doi_resolvers': list(settings['doi_resolvers'].keys()),
            'default_doi_resolver': settings['default_doi_resolver'],
            'public_instance': settings['server']['public_instance'],
        }
    )


@app.errorhandler(404)
def page_not_found(_e):
    return render('404.html'), 404


def run():
    """Runs the application on a local development server.

    This run method is only called when SearXNG is started via ``__main__``::

        python -m searx.webapp

    Do not use :ref:`run() <flask.Flask.run>` in a production setting.  It is
    not intended to meet security and performance requirements for a production
    server.

    It is not recommended to use this function for development with automatic
    reloading as this is badly supported.  Instead you should be using the flask
    command line script's run support::

        flask --app searx.webapp run --debug --reload --host 127.0.0.1 --port 8888

    .. _Flask.run: https://flask.palletsprojects.com/en/stable/api/#flask.Flask.run
    """

    host: str = get_setting("server.bind_address")  # type: ignore
    port: int = get_setting("server.port")  # type: ignore

    if searx.sxng_debug:
        logger.debug("run local development server (DEBUG) on %s:%s", host, port)
        app.run(
            debug=True,
            port=port,
            host=host,
            threaded=True,
            extra_files=[DEFAULT_SETTINGS_FILE],
        )
    else:
        logger.debug("run local development server on %s:%s", host, port)
        app.run(port=port, host=host, threaded=True)


def is_werkzeug_reload_active() -> bool:
    """Returns ``True`` if server is is launched by :ref:`werkzeug.serving` and
    the ``use_reload`` argument was set to ``True``.  If this is the case, it
    should be avoided that the server is initialized twice (:py:obj:`init`,
    :py:obj:`run`).

    .. _werkzeug.serving:
       https://werkzeug.palletsprojects.com/en/stable/serving/#werkzeug.serving.run_simple
    """

    if "uwsgi" in sys.argv:
        # server was launched by uWSGI
        return False

    # https://github.com/searxng/searxng/pull/1656#issuecomment-1214198941
    # https://github.com/searxng/searxng/pull/1616#issuecomment-1206137468

    frames = inspect.stack()

    if len(frames) > 1 and frames[-2].filename.endswith('flask/cli.py'):
        # server was launched by "flask run", is argument "--reload" set?
        if "--reload" in sys.argv or "--debug" in sys.argv:
            return True

    elif frames[0].filename.endswith('searx/webapp.py'):
        # server was launched by "python -m searx.webapp" / see run()
        if searx.sxng_debug:
            return True

    return False


def init():

    if searx.sxng_debug or app.debug:
        app.debug = True
        searx.sxng_debug = True

    # check secret_key in production

    if not app.debug and get_setting("server.secret_key") == 'ultrasecretkey':
        logger.error("server.secret_key is not changed. Please use something else instead of ultrasecretkey.")
        sys.exit(1)

    # When automatic reloading is activated stop Flask from initialising twice.
    # - https://github.com/pallets/flask/issues/5307#issuecomment-1774646119
    # - https://stackoverflow.com/a/25504196

    reloader_active = is_werkzeug_reload_active()
    werkzeug_run_main = is_running_from_reloader()

    if reloader_active and not werkzeug_run_main:
        logger.info("in reloading mode and not in main loop, cancel the initialization")
        return

    locales_initialize()
    redis_initialize()
    searx.plugins.initialize(app)

    metrics: bool = get_setting("general.enable_metrics")  # type: ignore
    searx.search.initialize(enable_checker=True, check_network=True, enable_metrics=metrics)

    limiter.initialize(app, settings)
    favicons.init()


application = app
patch_application(app)
init()

if __name__ == "__main__":
    run()
