"""Scrapy spiders for all 7 marketplace search pages.

Each spider fetches the marketplace search page and yields the RAW HTML -
parsers stay in app/services/crawlers (single source of truth). Scrapy
adds auto-throttle, retry middleware, UA rotation, and polite delay.

Run:  python scripts/crawl_scrapy.py <site> "<query>"
"""
from __future__ import annotations

import re
from urllib.parse import quote_plus

import scrapy

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

SITES = {
    "ebay": "https://www.ebay.com/sch/i.html?_nkw={q}&_ipg=60",
    "amazon": "https://www.amazon.com/s?k={q}",
    "etsy": "https://www.etsy.com/search?q={q}",
    "walmart": "https://www.walmart.com/search?q={q}",
    "redbubble": "https://www.redbubble.com/shop/?query={q}",
    "shopee": "https://shopee.vn/search?keyword={q}",
    "aliexpress": "https://www.aliexpress.com/w/wholesale-{q}.html",
}


class Pw1SearchSpider(scrapy.Spider):
    name = "pw1_search"
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "DOWNLOAD_DELAY": 0.6,
        "CONCURRENT_REQUESTS": 1,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [403, 429, 500, 502, 503],
        "USER_AGENT": _USER_AGENTS[0],
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "ROBOTSTXT_OBEY": False,
    }

    def __init__(self, site: str = "ebay", query: str = "", **kwargs):
        super().__init__(**kwargs)
        self.site = site
        self.query = query
        template = SITES.get(site)
        if not template:
            raise ValueError(f"unknown site {site}")
        self.start_urls = [template.format(q=quote_plus(query))]
        self._ua_idx = 0

    def start_requests(self):
        for url in self.start_urls:
            self._ua_idx = (self._ua_idx + 1) % len(_USER_AGENTS)
            yield scrapy.Request(
                url,
                headers={"User-Agent": _USER_AGENTS[self._ua_idx],
                         "Referer": re.sub(r"/[^/]*$", "/", url)},
                callback=self.parse)

    def parse(self, response):
        yield {"site": self.site, "query": self.query, "url": str(response.url),
               "html": response.text}
