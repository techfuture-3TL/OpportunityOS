"""Signals service + KaloPilot client tests (mocked HTTP - no live token needed)."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

import asyncio
import pytest

from app.services import kalopilot_client as kalo


def json_text():
    import json
    return json.dumps([
        {"product_name": "Custom Pet Collar", "revenue_usd": 45000,
         "sales_volume": 3200, "growth_rate_pct": 210, "unit_price_usd": 12.99,
         "shop_name": "PawStyle"},
        {"product_name": "LED Dog Collar", "revenue_usd": 30000,
         "sales_volume": 2800, "growth_rate_pct": 95, "unit_price_usd": 9.99,
         "shop_name": "GlowPets"},
    ])


FAKE_COMPLETED = {
    "task_id": "t-123",
    "status": "completed",
    "text": json_text(),
    "report": None,
    "credits_consumed": 10,
    "report_url": None,
}


def test_build_products_query():
    q = kalo.build_products_query("US", "Pet_Accessories", 7, 10, 10, 50)
    assert "Pet Supplies" in q
    assert "top 10 products" in q
    assert "$10-$50" in q
    assert "JSON array" in q


def test_parse_products_to_signals():
    signals = kalo.parse_products_to_signals(FAKE_COMPLETED, "US", "Pet_Accessories", 7)
    assert len(signals) == 2
    s0 = signals[0]
    assert s0["signal_id"].startswith("KALO-US-PET")
    assert s0["demand_metrics"]["tiktok_shop_sales_growth_pct"] == 210
    assert s0["competitor_analysis"]["avg_market_price"] == 12.99
    assert s0["source"] == "kalopilot_live"


def test_parse_products_json_fallback_from_markdown():
    text = "Here are the results:\n```json\n" + json_text() + "\n```\nHope this helps"
    result = dict(FAKE_COMPLETED, text=text)
    signals = kalo.parse_products_to_signals(result, "US", "Pet_Accessories", 7)
    assert len(signals) == 2


@pytest.mark.asyncio
async def test_run_query_mocked(monkeypatch):
    async def fake_submit(query, task_id=None, client=None):
        return {"task_id": "t-abc", "status": "submitted"}

    async def fake_poll(task_id, client=None):
        return dict(FAKE_COMPLETED, task_id=task_id)

    monkeypatch.setattr(kalo, "submit_query", fake_submit)
    monkeypatch.setattr(kalo, "poll_result", fake_poll)
    data = await kalo.run_query("test", first_poll_s=0.0, poll_interval_s=0.01)
    assert data["status"] == "completed"
    assert data["credits_consumed"] == 10


@pytest.mark.asyncio
async def test_run_query_error_surfaced(monkeypatch):
    async def fake_submit(query, task_id=None, client=None):
        return {"task_id": "t-err"}

    async def fake_poll(task_id, client=None):
        return {"task_id": task_id, "status": "error", "error": {"message": "boom"}}

    monkeypatch.setattr(kalo, "submit_query", fake_submit)
    monkeypatch.setattr(kalo, "poll_result", fake_poll)
    with pytest.raises(kalo.KaloPilotError):
        await kalo.run_query("test", first_poll_s=0.0, poll_interval_s=0.01)


@pytest.mark.asyncio
async def test_start_fetch_job_completes(monkeypatch, tmp_path):
    from app.services import signals_service as svc

    # isolate from the persistent live store so tests never touch real data
    monkeypatch.setattr(svc, "LIVE_SIGNALS_FILE", tmp_path / "live_test.json")
    svc._live_signals.clear()

    async def fake_run(query, **kwargs):
        return dict(FAKE_COMPLETED)

    monkeypatch.setattr(svc.kalo, "run_query", fake_run)
    job = svc.start_fetch("US", "Pet_Accessories", 7, 5)
    assert job["status"] == "submitted"
    for _ in range(100):
        await asyncio.sleep(0.02)
        if svc.get_job(job["job_id"])["status"] == "completed":
            break
    done = svc.get_job(job["job_id"])
    assert done["status"] == "completed"
    assert done["signals_count"] == 2
    signals = svc.list_signals()
    assert any(s.get("source") == "kalopilot_live" for s in signals)
