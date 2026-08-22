"""KaloData OpenAPI crawler tests (mocked HTTP)."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

import pytest

from app.services.crawlers.kalodata import KaloDataCrawler

FAKE_RANK = {
    "success": True,
    "data": [
        {"product_id": "1729508370969629931",
         "product_name": "Wireless Bluetooth Headphones",
         "revenue": 8500.5, "commission_rate": 15,
         "revenue_growth_rate": 25.8, "sales_volumn": 340,
         "unit_price": 25, "live_revenue": 1200, "video_revenue": 800,
         "launch_date": "2024-01-15",
         "master_image_url": "https://img.example.com/1.jpg",
         "seller_name": "TechStore", "sku_count": "2"},
        {"product_id": "1729508370969629932",
         "product_name": "Smart Watch Pro",
         "revenue": 6200.0, "revenue_growth_rate": 10.2,
         "sales_volumn": 120, "unit_price": 51.6,
         "master_image_url": ""},
    ],
    "message": "ok", "code": "0",
}


def test_to_product_conversion():
    c = KaloDataCrawler()
    p = c._to_product(FAKE_RANK["data"][0], 0)
    assert p.source == "tiktok"
    assert p.external_id == "1729508370969629931"
    assert p.revenue == 8500.5
    assert p.quantity_sold == 340
    assert p.price == 25.0
    assert p.growth_pct == 25.8
    assert p.image_url.startswith("https://img.example.com")
    assert p.raw["tiktok_shop"] is True
    assert p.raw["seller_name"] == "TechStore"


@pytest.mark.asyncio
async def test_crawl_mocked(monkeypatch):
    c = KaloDataCrawler()

    async def fake_rank(endpoint, payload):
        assert endpoint == "product/rank"
        assert payload["keyword"] == "christmas ornament"
        assert payload["sort_field"] == {"field": "revenue", "type": "DESC"}
        assert payload["region"] == "US"
        return FAKE_RANK["data"]

    monkeypatch.setattr(c, "_rank", fake_rank)
    res = await c.crawl("christmas ornament", max_items=10, days=7)
    assert res.status == "ok"
    assert len(res.products) == 2
    assert res.products[0].quantity_sold == 340
    assert res.meta["tiktok_shop"] is True


@pytest.mark.asyncio
async def test_crawl_auth_error_surfaced(monkeypatch):
    c = KaloDataCrawler()

    async def fake_rank(endpoint, payload):
        raise RuntimeError("kalodata error: invalid api key")

    monkeypatch.setattr(c, "_rank", fake_rank)
    res = await c.crawl("x", max_items=5, days=7)
    assert res.status == "failed"
    assert "invalid api key" in res.error


def test_requires_key():
    c = KaloDataCrawler()
    ok, reason = c.status()
    assert ok is False
    assert "KALODATA_API_KEY" in reason
