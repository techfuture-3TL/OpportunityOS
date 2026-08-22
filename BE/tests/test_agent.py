"""AI Agent + report exporter tests."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

import pytest

from app.models.agent_schemas import AgentAnalysisRequest
from app.services.agent import (filter_by_window, forecast_from_signals,
                                keyword_stats, load_raw_signals, product_stats)
from app.services.report_exporter import (export_json, export_markdown,
                                          export_pdf, export_xlsx)


@pytest.mark.asyncio
async def test_agent_reads_raw_data():
    req = AgentAnalysisRequest(query="tumbler", window="30d",
                               data_source="MARKET_SIGNALS", deep=False)
    from app.services.agent import analyze_with_agent

    report = await analyze_with_agent(req, [])
    assert report.raw_records_read > 0, "agent must read raw crawled records"
    assert report.top_keywords, "agent must produce top keywords"
    assert all(0 <= k.demand <= 100 for k in report.top_keywords)
    assert report.top_products_revenue or report.top_products_quantity
    assert report.key_insights
    assert report.forecast is not None
    assert len(report.forecast.daily) == 30
    assert report.rd_recommendations
    assert report.agent_trace, "agent trace must show what the agent did"
    print(f"[agent] read {report.raw_records_read} raw records, "
          f"{len(report.top_keywords)} keywords, "
          f"{len(report.rd_recommendations)} R&D recs")


def test_keyword_stats_deterministic():
    signals = [
        {"keywords": ["christmas ornament"], "category": "Home_Decor",
         "demand_metrics": {"tiktok_shop_sales_growth_pct": 200, "google_trends_score": 90},
         "source": "ebay"},
        {"keywords": ["christmas ornament"], "category": "Home_Decor",
         "demand_metrics": {"tiktok_shop_sales_growth_pct": 100, "google_trends_score": 80},
         "source": "etsy"},
    ]
    stats = keyword_stats(signals, "30d")
    assert stats[0]["keyword"] == "christmas ornament"
    assert stats[0]["n_sources"] == 2
    assert 0 <= stats[0]["demand"] <= 100


def test_product_stats_windows():
    import time
    signals = [
        {"crawl_raw": {"source": "ebay", "revenue": 500, "quantity_sold": 20,
                       "price": 25, "url": "u"}, "crawled_at": time.time() - 20 * 86400,
         "topic": "old product"},
        {"crawl_raw": {"source": "amazon", "revenue": 800, "quantity_sold": 40,
                       "price": 20, "url": "u"}, "crawled_at": time.time(),
         "topic": "fresh product"},
    ]
    w7 = product_stats(filter_by_window(signals, "7d"), "7d", "revenue")
    assert len(w7) == 1 and w7[0]["title"] == "fresh product"
    w1y = product_stats(filter_by_window(signals, "1y"), "1y", "revenue")
    assert len(w1y) == 2


def test_forecast_shape():
    signals = [{"demand_metrics": {"tiktok_shop_sales_growth_pct": 120}}]
    fc = forecast_from_signals(signals)
    assert fc["horizon_days"] == 30
    assert len(fc["daily"]) == 30
    assert fc["projected_total_demand"] > 0
    for d in fc["daily"]:
        assert d["low"] <= d["demand"] <= d["high"]


def test_report_exports(tmp_path):
    from app.models.agent_schemas import (AgentReport, ForecastDay, ForecastReport,
                                          InsightReport, KeywordReport,
                                          ProductReport, RecommendationReport)
    report = AgentReport(
        query="christmas ornament",
        generated_at="2026-08-21T00:00:00",
        raw_records_read=100,
        sources_used=["ebay", "amazon"],
        top_keywords=[KeywordReport(keyword="christmas ornament", demand=80,
                                    growth=60, collection="Home_Decor",
                                    recommended_product="ornament set",
                                    price_range="$15-$30", reason="high demand")],
        top_products_revenue=[ProductReport(rank=1, title="Ornament set", source="ebay",
                                            revenue=1000, quantity=50, price=20)],
        key_insights=[InsightReport(title="t", finding="f", evidence=["e"])],
        forecast=ForecastReport(method="holt", confidence="medium",
                                projected_total_demand=3000, avg_daily=100,
                                daily=[ForecastDay(day="2026-08-22", demand=100,
                                                   low=80, high=120)],
                                narrative="up trend"),
        rd_recommendations=[RecommendationReport(rank=1, product="X",
                                                 opportunity_score=85,
                                                 rationale="r")],
    )
    x = export_xlsx(report, tmp_path / "r.xlsx")
    j = export_json(report, tmp_path / "r.json")
    m = export_markdown(report, tmp_path / "r.md")
    p = export_pdf(report, tmp_path / "r.pdf")
    assert x.exists() and j.exists() and m.exists() and p.exists()
    assert p.stat().st_size > 1000
