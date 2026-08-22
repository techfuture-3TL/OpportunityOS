"""Crawl orchestration - realtime only, no persistence."""
from __future__ import annotations

import asyncio
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings

DEFAULT_CRAWL_SOURCES = ("tiktok", "amazon", "ebay", "shopee", "lazada", "etsy")


class CrawlService:
    """
    Realtime crawl service - NO PERSISTENCE.
    - Crawls data in real-time from sources
    - Returns results directly
    - No file storage, no signal store
    - Job metadata goes to Supabase
    """

    def __init__(self):
        self.sources = settings.crawl_sources

    async def crawl(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_items: int = 30,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Crawl sources in realtime and return results DIRECTLY.
        NO persistence - data stays in memory.
        """
        run_id = f"crawl_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        # Determine which sources to crawl
        requested_sources = sources if sources else self.sources
        target_sources = list(
            dict.fromkeys(
                source.strip().lower()
                for source in requested_sources
                if source and source.strip()
            )
        )

        print(f"[crawl] Run {run_id}: query='{query}', sources={target_sources}")

        # Import dedicated marketplace crawlers
        from .kalodata import KalodataCrawler
        from .ebay import EbayCrawler
        from .amazon import AmazonCrawler
        from .etsy import EtsyCrawler
        from .shopee import ShopeeCrawler
        from .lazada import LazadaCrawler

        crawler_map = {
            "tiktok": KalodataCrawler,  # Kalodata TikTok Shop API
            "amazon": AmazonCrawler,  # Amazon Realtime Scraper
            "ebay": EbayCrawler,  # eBay Realtime Scraper
            "etsy": EtsyCrawler,  # Etsy Realtime Scraper
            "shopee": ShopeeCrawler,  # Shopee.vn Realtime Scraper
            "lazada": LazadaCrawler,  # Lazada.vn Realtime Scraper
        }

        # Run crawlers concurrently
        tasks = {}
        for src in target_sources:
            if src in crawler_map:
                crawler_cls = crawler_map[src]
                tasks[src] = asyncio.create_task(
                    self._run_crawler(crawler_cls, query, max_items, days)
                )

        # Wait for all to complete
        results = {}
        all_products = []

        for src, task in tasks.items():
            try:
                result = await task
                results[src] = result
                # Collect products directly - NO STORAGE
                all_products.extend(result.get("products", []))
            except Exception as e:
                print(f"[crawl] {src} failed: {e}")
                results[src] = {"source": src, "success": False, "error": str(e), "products": []}

        elapsed = time.time() - start_time
        products_count = sum(len(r.get("products", [])) for r in results.values())

        print(f"[crawl] {run_id}: {products_count} products in {elapsed:.2f}s")

        return {
            "run_id": run_id,
            "query": query,
            "sources": list(results.keys()),
            "products_found": products_count,
            "all_products": all_products,  # Return directly, no storage
            "by_source": results,
            "generated_at": datetime.utcnow().isoformat(),
            "execution_time_sec": round(elapsed, 3),
        }

    async def _run_crawler(self, crawler_cls, query: str, max_items: int, days: int) -> Dict:
        """Run a single crawler."""
        try:
            if hasattr(crawler_cls, "crawl"):
                return await crawler_cls.crawl(query, limit=max_items)
            return await crawler_cls(query, limit=max_items)
        except Exception as e:
            print(f"[crawl] {crawler_cls.name} error: {e}")
            return {"source": crawler_cls.name, "success": False, "error": str(e), "products": []}

    def products_to_signals(self, products: List[Dict], query: str) -> List[Dict]:
        """
        Convert products to signals (in-memory only).
        This is the ONLY way data moves through the system.
        """
        signals = []
        for p in products:
            signal = {
                "signal_id": f"SIG-{p.get('source', '?')}-{uuid.uuid4().hex[:8]}",
                "source": p.get("source", "unknown"),
                "crawled_at": time.time(),
                "topic": p.get("title", ""),
                "keywords": [query.lower()],
                "category": self._guess_category(p.get("title", "")),
                "niche": query.lower(),
                # Pricing
                "price": p.get("price", 0),
                "currency": p.get("currency", "USD"),
                "revenue": p.get("revenue", 0),
                "quantity_sold": p.get("quantity_sold", 0),
                # Demand
                "reviews_count": p.get("reviews_count", 0),
                "rating": p.get("rating", 0),
                "growth_rate": p.get("growth_rate", 0),
                # Metadata
                "product_id": p.get("product_id", ""),
                "title": p.get("title", ""),
                "url": p.get("url", ""),
                "image_url": p.get("image_url", ""),
                "seller_name": p.get("seller_name", ""),
                # TikTok-specific
                "video_revenue": p.get("video_revenue", 0),
                "live_revenue": p.get("live_revenue", 0),
                "views": p.get("views", 0),
                # Technical
                "is_synthetic": bool(p.get("is_synthetic", False)),
                "estimated_fields": list(p.get("estimated_fields", [])),
                "data_mode": p.get("data_mode", "marketplace_html"),
            }
            signals.append(signal)
        return signals

    def _guess_category(self, title: str) -> str:
        """Guess category from product title."""
        t = title.lower()
        if any(k in t for k in ["tumbler", "mug", "cup", "bottle", "water"]):
            return "Drinkware"
        if any(k in t for k in ["shirt", "tee", "hoodie", "jacket"]):
            return "Apparel"
        if any(k in t for k in ["light", "lamp", "mirror", "sign", "canvas", "plaque"]):
            return "Home Decor"
        if any(k in t for k in ["dog", "cat", "pet", "collar", "leash"]):
            return "Pet"
        if any(k in t for k in ["ornament", "christmas", "holiday", "gift"]):
            return "Seasonal"
        return "General"
