# SPDX-License-Identifier: AGPL-3.0-or-later
"""Sogou-WeChat search engine for retrieving WeChat Article from Sogou"""

from urllib.parse import urlencode
import random
from datetime import datetime
import re
from lxml import html

from searx.utils import extract_text

# Metadata
about = {
    "website": "https://weixin.sogou.com/",
    "use_official_api": False,
    "require_api_key": False,
    "results": "HTML",
    "language": "zh",
}

# Engine Configuration
categories = ["news"]
paging = True

# Base URL
base_url = "https://weixin.sogou.com"


def request(query, params):
    query_params = {
        "query": query,
        "page": params["pageno"],
        "type": 2,
    }

    params["url"] = f"{base_url}/weixin?{urlencode(query_params)}"
    # 设置请求头，贴近真实浏览器，提升成功率（UA 轮换）
    UA_POOL = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    ]
    ua = random.choice(UA_POOL)
    params["headers"] = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://weixin.sogou.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    }
    return params


def response(resp):
    dom = html.fromstring(resp.text)
    results = []

    for item in dom.xpath('//li[contains(@id, "sogou_vr_")]'):
        title = extract_text(item.xpath('.//h3/a'))
        url = extract_text(item.xpath('.//h3/a/@href'))

        if url.startswith("/link?url="):
            url = f"{base_url}{url}"

        content = extract_text(item.xpath('.//p[@class="txt-info"]'))
        if not content:
            content = extract_text(item.xpath('.//p[contains(@class, "txt-info")]'))

        thumbnail = extract_text(item.xpath('.//div[@class="img-box"]/a/img/@src'))
        if thumbnail and thumbnail.startswith("//"):
            thumbnail = f"https:{thumbnail}"

        published_date = None
        timestamp = extract_text(item.xpath('.//script[contains(text(), "timeConvert")]'))
        if timestamp:
            match = re.search(r"timeConvert\('(\d+)'\)", timestamp)
            if match:
                published_date = datetime.fromtimestamp(int(match.group(1)))

        if title and url:
            results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content,
                    'thumbnail': thumbnail,
                    "publishedDate": published_date,
                }
            )

    return results
