"""CLI runner: scrapy spider -> JSON line with raw HTML on stdout.

Usage: python scripts/crawl_scrapy.py <site> <query>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BE_DIR))
sys.path.insert(0, str(BE_DIR / "scripts" / "spiders"))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings  # noqa

from pw1_spiders import Pw1SearchSpider


def main() -> None:
    site = sys.argv[1] if len(sys.argv) > 1 else "ebay"
    query = sys.argv[2] if len(sys.argv) > 2 else ""

    results = []

    class Collector:
        def __init__(self):
            pass

    def item_scraped(item, response, spider):
        results.append(dict(item))

    from scrapy import signals

    settings = {
        "LOG_LEVEL": "ERROR",
        "TELNETCONSOLE_ENABLED": False,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "CONCURRENT_REQUESTS": 1,
        "RETRY_TIMES": 3,
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_TIMEOUT": 30,
    }
    process = CrawlerProcess(settings=settings)
    crawler = process.create_crawler(Pw1SearchSpider)
    crawler.signals.connect(item_scraped, signal=signals.item_scraped)
    process.crawl(crawler, site=site, query=query)
    process.start()  # blocks until done

    if results:
        print(json.dumps(results[0], ensure_ascii=False))
    else:
        print(json.dumps({"site": site, "query": query, "html": None}))


if __name__ == "__main__":
    main()
