"""Auto-crawl service tests (demo source + mocked remote crawlers)."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

import asyncio
import pytest

from app.services import crawl_service
from app.services.crawlers.base import CrawlResult, RawProduct
from app.services.crawlers.registry import resolve_sources, source_status


@pytest.mark.asyncio
async def test_resolve_sources():
    auto = resolve_sources("auto")
    assert "demo" not in auto, "auto = REAL sources only (demo là fallback riêng)"
    assert "ebay" in auto and "amazon" in auto
    assert resolve_sources("demo") == ["demo"]
    with pytest.raises(ValueError):
        resolve_sources("not-a-source")


def test_source_status_shape():
    statuses = source_status()
    assert len(statuses) >= 5
    assert all({"name", "enabled", "official", "reason"} <= set(s.keys()) for s in statuses)


@pytest.mark.asyncio
async def test_crawl_demo_source(monkeypatch, tmp_path):
    from app.services import signals_service

    monkeypatch.setattr(crawl_service, "merge_crawled_signals",
                        _isolated_merge(tmp_path))
    entry = await crawl_service.crawl("halloween decor", sources=["demo"],
                                      max_items=10, days=30)
    assert entry["products_found"] > 0
    assert entry["signals_added"] > 0
    logs = {r["source"]: r for r in entry["results"]}
    assert logs["demo"]["status"] == "ok"


@pytest.mark.asyncio
async def test_crawl_skips_unconfigured_sources(monkeypatch):
    class FakeNoKey:
        name = "fakenokey"
        def __init__(self):
            pass
        def status(self):
            return False, "missing credentials: X"
        async def run(self, query, max_items=30, days=30):
            return CrawlResult(source="fakenokey", status="skipped", error="missing credentials: X")

    async def fake_crawl(query, sources=None, max_items=30, days=30, persist=True):
        return {"run_id": "x", "query": query, "sources": sources or [],
                "products_found": 0, "signals_added": 0,
                "results": [{"source": "fakenokey", "status": "skipped",
                             "products": 0, "error": "missing credentials: X", "meta": {}}]}

    monkeypatch.setattr(crawl_service, "crawl", fake_crawl)
    entry = await crawl_service.crawl("x", sources=["fakenokey"])
    assert entry["results"][0]["status"] == "skipped"


def test_product_to_signal_shape():
    p = RawProduct(
        source="demo", external_id="x1", title="Personalized Dog Collar",
        price=12.99, currency="USD", quantity_sold=120, revenue=1558.8,
        reviews_count=45, rating=4.6, category="Pet_Accessories",
        growth_pct=180.0,
        reviews=["Cheap buckle broke in a week.", "No custom name option."],
        estimated_fields=["quantity_sold", "revenue"],
    )
    sig = crawl_service.product_to_signal(p, "dog collar", 0)
    assert sig["source"] == "crawl_demo"
    assert sig["demand_metrics"]["tiktok_shop_sales_growth_pct"] == 180.0
    assert sig["competitor_analysis"]["avg_market_price"] == 12.99
    assert len(sig["competitor_analysis"]["top_negative_reviews"]) == 2
    assert sig["best_fit_sku"] == "PW-PET-LEATHER-COLLAR"
    assert sig["crawl_raw"]["estimated_fields"] == ["quantity_sold", "revenue"]


@pytest.mark.asyncio
async def test_crawled_signals_flow_into_analysis(monkeypatch, tmp_path):
    from app.services import signals_service

    monkeypatch.setattr(crawl_service, "merge_crawled_signals",
                        _isolated_merge(tmp_path))
    signals_service._live_signals.clear()
    await crawl_service.crawl("personalized tumbler", sources=["demo"],
                              max_items=8, days=30)
    from app.models.schemas import DataSourceSelection, OpportunityAnalysisRequest
    from app.services.catalog_matcher import match_opportunities

    req = OpportunityAnalysisRequest(data_source=DataSourceSelection.MARKET_SIGNALS, limit=20)
    opps = match_opportunities(req)
    crawled = [o for o in opps if o.data_source.startswith("crawl_")]
    assert crawled, "crawled signals must appear in analysis results"
    top = crawled[0]
    assert top.opportunity_score > 0
    assert top.unit_economics is not None
    print(f"[crawl->analyze] {len(crawled)} crawled opportunities, "
          f"top={top.name[:40]} score={top.opportunity_score}")


def _isolated_merge(tmp_path):
    from app.services import signals_service

    def _merge(signals):
        signals_service._live_signals.clear()
        signals_service._live_signals.extend(signals)
        return len(signals)

    return _merge
