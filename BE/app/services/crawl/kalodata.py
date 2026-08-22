"""Kalodata TikTok Shop API crawler - REAL data source for PW1."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


BASE_URL = "https://www.kalodata.com/openapi/v1/tiktok"

# Rate limiting: 10 requests per 10 seconds
_SEMAPHORE = asyncio.Semaphore(1)
_WINDOW_SEC = 1.1
_last_call = 0.0


async def _rate_limit():
    """Enforce 10 req/10s rate limit."""
    global _last_call
    async with _SEMAPHORE:
        elapsed = time.time() - _last_call
        if elapsed < _WINDOW_SEC:
            await asyncio.sleep(_WINDOW_SEC - elapsed)
        _last_call = time.time()


async def _post(payload: Dict[str, Any], endpoint: str) -> Optional[Dict]:
    """Make authenticated POST request to Kalodata API."""
    await _rate_limit()

    api_key = settings.KALODATA_API_KEY
    if not api_key:
        return None

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "Authorization": f"Bearer {api_key}",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{BASE_URL}/{endpoint}", json=payload, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            print(f"[kalodata] HTTP {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"[kalodata] Error: {e}")
    return None


def _map_date_range(days: int) -> str:
    """Map days to Kalodata date_range string."""
    mapping = {
        1: "lastDay", 7: "last7Day", 30: "last30Day",
        60: "last60Day", 90: "last90Day", 180: "last180Day", 365: "last365Day",
    }
    return mapping.get(days, "last7Day")


def _map_region(region: str) -> str:
    """Map region name to Kalodata region code."""
    mapping = {
        "VN": "VN", "VI": "VN", "Vietnam": "VN",
        "US": "US", "USA": "US",
        "UK": "GB", "GB": "GB",
        "ID": "ID", "TH": "TH", "MY": "MY", "PH": "PH", "SG": "SG",
        "BR": "BR", "MX": "MX",
        "DE": "DE", "FR": "FR", "ES": "ES", "IT": "IT",
        "JP": "JP",
    }
    return mapping.get(region.upper(), "US")


class KalodataCrawler:
    """TikTok Shop data crawler using Kalodata API."""

    name = "tiktok"
    label = "TikTok Shop (Kalodata)"

    @classmethod
    async def crawl(
        cls,
        query: str,
        region: str = "US",
        days: int = 7,
        limit: int = 30,
    ) -> Dict[str, Any]:
        """
        Crawl TikTok Shop products via Kalodata API.

        Returns:
            Dict with products, categories, videos, and meta
        """
        region_code = _map_region(region)
        date_range = _map_date_range(days)

        print(f"[kalodata] Crawling: query='{query}', region={region_code}, days={days}")

        result = {
            "source": "tiktok",
            "region": region_code,
            "date_range": date_range,
            "query": query,
            "products": [],
            "categories": [],
            "videos": [],
            "shops": [],
            "success": False,
        }

        # 1. Fetch product rankings (MAIN DATA)
        products_payload = {
            "region": region_code,
            "language": "en-US",
            "currency": "USD",
            "date_range": date_range,
            "sort_field": {"field": "revenue", "type": "DESC"},
            "page_size": min(limit, 100),
            "page_number": 1,
            "keyword": query,
            "need_image": 1,
            "need_extra": True,
        }

        resp = await _post(products_payload, "product/rank")
        if resp and resp.get("success"):
            items = resp.get("data") or []
            result["products"] = [cls._parse_product(p) for p in items]
            result["success"] = True
            print(f"[kalodata] Got {len(result['products'])} products")
        else:
            print(f"[kalodata] Product rank failed: {resp}")
            return result

        # 2. Fetch category rankings
        cat_payload = {
            "region": region_code,
            "language": "en-US",
            "currency": "USD",
            "date_range": date_range,
            "sort_field": {"field": "revenue", "type": "DESC"},
            "page_size": 20,
            "page_number": 1,
            "category_level": 2,
        }

        resp = await _post(cat_payload, "category/rank")
        if resp and resp.get("success"):
            cats = resp.get("data") or []
            result["categories"] = [
                {
                    "id": c.get("category_id"),
                    "name": c.get("category_name"),
                    "revenue": c.get("revenue"),
                    "growth": c.get("revenue_growth_rate"),
                    "rank": c.get("rank"),
                }
                for c in cats
            ]

        # 3. Fetch video rankings (demand signals)
        video_payload = {
            "region": region_code,
            "language": "en-US",
            "currency": "USD",
            "date_range": date_range,
            "sort_field": {"field": "revenue", "type": "DESC"},
            "page_size": 10,
            "page_number": 1,
            "keyword": query,
        }

        resp = await _post(video_payload, "video/rank")
        if resp and resp.get("success"):
            videos = resp.get("data") or []
            result["videos"] = [
                {
                    "id": v.get("video_id"),
                    "title": v.get("video_title"),
                    "views": v.get("views"),
                    "revenue": v.get("revenue"),
                    "growth": v.get("revenue_growth_rate"),
                    "creator": v.get("belonged_creator_handle"),
                }
                for v in videos
            ]

        return result

    @classmethod
    def _parse_product(cls, p: Dict) -> Dict:
        """Parse Kalodata product to standard format."""
        price = float(p.get("unit_price") or 0)
        qty = int(p.get("sales_volumn") or 0)
        revenue = float(p.get("revenue") or 0)
        growth = float(p.get("revenue_growth_rate") or 0)

        cat_list = p.get("category_list") or []
        cat_name = cat_list[0] if isinstance(cat_list, list) and cat_list else ""

        return {
            "source": "tiktok",
            "product_id": str(p.get("product_id", "")),
            "title": (p.get("product_name") or "")[:400],
            "price": round(price, 2),
            "currency": "USD",
            "revenue": round(revenue, 2),
            "quantity_sold": qty,
            "growth_rate": round(growth, 1),
            "rating": float(p.get("commission_rate") or 0),
            "reviews_count": int(p.get("product_review_count") or 0),
            "category": cat_name,
            "image_url": p.get("master_image_url") or "",
            "seller_id": p.get("seller_id"),
            "seller_name": p.get("seller_name"),
            "launch_date": p.get("launch_date"),
            "commission_rate": p.get("commission_rate"),
            "video_revenue": p.get("video_revenue", 0),
            "live_revenue": p.get("live_revenue", 0),
            "url": f"https://shop.tiktok.com/product/{p.get('product_id', '')}",
        }


# Standalone convenience functions
async def crawl_tiktok(query: str, region: str = "US", days: int = 7, limit: int = 30) -> Dict:
    """Convenience function to crawl TikTok Shop data."""
    return await KalodataCrawler.crawl(query, region, days, limit)


async def get_tiktok_products(query: str, region: str = "US", days: int = 7, limit: int = 30) -> List[Dict]:
    """Get just the products from TikTok Shop."""
    result = await crawl_tiktok(query, region, days, limit)
    return result.get("products", [])
