from urllib.parse import (
    quote,
    urlencode,
)
from lxml import html
import random
import re
import os
import time
from searx.utils import (
    eval_xpath_getindex,
    eval_xpath_list,
    extract_text,
)
from searx.network import get


about = {
    "website": 'https://weixin.sogou.com/weixin',
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}
categories = ['general', 'web']
paging = False
time_range_support = False


def request(query, params):
    base_url = 'https://weixin.sogou.com/weixin'
    args = urlencode(
        {
            'query': query,
            'page': 1,
            'type': 2,
        }
    )
    params['url'] = base_url + '?' + args

    # UA 池与请求头（降低反爬拦截）
    UA_POOL = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    ]
    ua = random.choice(UA_POOL)
    params['headers'] = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://weixin.sogou.com/',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive',
    }

    # 可选代理（环境变量 WECHAT_PROXY，格式 http://host:port）
    proxy = os.environ.get('WECHAT_PROXY')
    if proxy:
        params['proxies'] = {
            'http': proxy,
            'https': proxy,
        }


def parse_url(url_string):
    try:
        if not url_string:
            return None
        url = 'https://weixin.sogou.com' + url_string
        b = random.randint(0, 99)
        if 'url=' not in url:
            return url
        a = url.index('url=')
        if a + 31 + b >= len(url):
            return url
        a = url[a + 30 + b:a + 31 + b:]
        url += '&k=' + str(b) + '&h=' + a
        return url
    except Exception:
        return None


def parse_url2(url_string):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Cookie': 'ssuid=9651828800; SUID=A2FECF7C1AA7A20B000000006694AD27; cuid=AAHHUGJrTQAAAAuipikTpgEANgg=;'
                  'SUV=1721019689438419; ABTEST=0|1721019689|v1; SNUID=D18DBB0874756E366C36BF0B7401396F; SMYUV=1721022241781501;'
                  'IPLOC=CN1100; ariaDefaultTheme=undefined',
    }
    try:
        # 带重试和退避
        backoff = 0.5
        for _ in range(3):
            resp = get(url_string, headers=headers)
            parsed_url_list = re.findall(r"url \\+= '(.+)'", resp.text)
            parsed_url = ''.join(parsed_url_list)
            parsed_url = re.sub(r'@', r'', parsed_url)
            if parsed_url:
                return parsed_url
            time.sleep(backoff)
            backoff *= 2
        return url_string
    except Exception:
        # 如果获取失败，返回原始 URL
        return url_string


def response(resp):
    results = []
    try:
        dom = html.fromstring(resp.text)
    except Exception:
        return results

    # parse results
    for result in eval_xpath_list(dom, '//div[contains(@class,"txt-box")]'):
        try:
            url = eval_xpath_getindex(result, './/h3/a/@href', 0, default=None)
            if url is None:
                continue
            
            # 处理URL
            url = parse_url(url)
            if not url:
                continue
            url = parse_url2(url)
            if not url:
                continue
            
            # 处理标题
            title1 = eval_xpath_getindex(result, './/h3//a/text()', 0, default='')
            title2 = eval_xpath_getindex(result, './/h3//a/text()', 1, default='')
            title_em1 = eval_xpath_getindex(result, './/h3//a/em/text()', 0, default='')
            title_em2 = eval_xpath_getindex(result, './/h3//a/em/text()', 1, default='')
            
            if title2 == '':
                title = extract_text(title_em1 + title1) if (title_em1 + title1) else '无标题'
            else:
                title = extract_text(title1 + title_em1 + title2 + title_em2) if (title1 + title_em1 + title2 + title_em2) else '无标题'
            
            # 处理内容
            content = eval_xpath_getindex(result, './/p[contains(@class, "txt-info")]', 0, default='')
            content = extract_text(content, allow_none=True) if content else ''
            
            # 确保所有必需字段都有值
            if url and title:
                results.append({
                    'url': url,
                    'title': title,
                    'content': content or ''
                })
        except Exception:
            # 跳过有问题的结果
            continue
    
    return results 