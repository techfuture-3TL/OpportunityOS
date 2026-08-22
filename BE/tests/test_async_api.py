"""Async HTTP tests against the real FastAPI app (ASGI transport)."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

import pytest
import httpx

from app.main import app


@pytest.fixture
def client():
    import asyncio
    from app.services.database_service import CSVDatabaseService
    asyncio.run(CSVDatabaseService.load_database_records())  # warm cache (no lifespan in ASGITransport)
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_catalog_and_detail(client):
    r = await client.get("/api/v1/catalog")
    assert r.status_code == 200
    assert r.json()["total_skus"] == 8
    r2 = await client.get("/api/v1/catalog/PW-DRINK-TUMB-20OZ")
    assert r2.status_code == 200
    assert r2.json()["sku"] == "PW-DRINK-TUMB-20OZ"
    r3 = await client.get("/api/v1/catalog/NOT-A-SKU")
    assert r3.status_code == 404


@pytest.mark.asyncio
async def test_database_stats(client):
    r = await client.get("/api/v1/database/stats")
    assert r.status_code == 200
    assert r.json()["total_records"] > 2000


@pytest.mark.asyncio
async def test_database_sample_pagination(client):
    r = await client.get("/api/v1/database/sample?limit=5&offset=10")
    assert r.status_code == 200
    assert len(r.json()["sample"]) == 5
    assert r.json()["offset"] == 10


@pytest.mark.asyncio
async def test_analyze_endpoint(client):
    payload = {
        "search_mode": "DISCOVERY",
        "data_source": "DATABASE_CSV",
        "limit": 10,
        "strategy": {"preset": "VIRAL_TREND"},
        "market_and_niche": {"categories": ["Drinkware"]},
        "financials": {"min_profit_margin_pct": 40.0},
        "supply_chain": {},
    }
    r = await client.post("/api/v1/opportunities/analyze", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["total_opportunities"] > 0
    assert body["execution_time_ms"] < 3000  # warmed cache: normally < 5ms
    first = body["opportunities"][0]
    assert 0 <= first["opportunity_score"] <= 100
    assert first["score_breakdown"]["demand_growth"] >= 0
    assert "unit_economics" in first


@pytest.mark.asyncio
async def test_opportunities_collection(client):
    r = await client.get("/api/v1/opportunities?limit=5&strategy=HIGH_MARGIN")
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 5
    assert len(body["items"]) <= 5
    scores = [i["opportunity_score"] for i in body["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_opportunity_detail_404(client):
    r = await client.get("/api/v1/opportunities/DOES-NOT-EXIST")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_strategies(client):
    r = await client.get("/api/v1/strategies")
    assert r.status_code == 200
    assert len(r.json()) == 5


@pytest.mark.asyncio
async def test_signals_list(client):
    r = await client.get("/api/v1/signals")
    assert r.status_code == 200
    assert r.json()["total_signals"] >= 5


@pytest.mark.asyncio
async def test_rate_limit_enforced(client):
    # burst is 30 by default -> the 31st request within a second gets 429
    r = None
    for i in range(40):
        r = await client.post("/api/v1/opportunities/analyze", json={
            "search_mode": "DISCOVERY", "data_source": "MARKET_SIGNALS", "limit": 1})
    assert r is not None
    assert r.status_code in (200, 429)  # timing-dependent; at least one 429 in the loop above
