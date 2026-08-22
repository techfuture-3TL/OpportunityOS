"""Crawl services - marketplace data extraction."""
from app.services.crawl.service import CrawlService
from app.services.crawl.kalodata import KalodataCrawler
from app.services.crawl.ebay import EbayCrawler
from app.services.crawl.amazon import AmazonCrawler
from app.services.crawl.etsy import EtsyCrawler
from app.services.crawl.shopee import ShopeeCrawler
from app.services.crawl.lazada import LazadaCrawler

__all__ = ["CrawlService", "KalodataCrawler", "EbayCrawler", "AmazonCrawler", "EtsyCrawler", "ShopeeCrawler", "LazadaCrawler"]


