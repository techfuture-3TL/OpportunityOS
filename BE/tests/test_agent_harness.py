"""Comprehensive Test Suite for AI Agent Harness, RAG Retriever, and Deep Research Engine."""
from __future__ import annotations

import pytest
from app.models.agent_schemas import AgentAnalysisRequest
from app.services.rag.store import get_knowledge_store
from app.services.rag.retriever import hybrid_retrieve
from app.services.agent_harness.tools import AgentHarnessTools
from app.services.agent_harness.deep_research import DeepResearchAgent


def test_rag_store_initialization():
    store = get_knowledge_store()
    assert len(store.docs) >= 2091, "RAG Knowledge Store must index >= 2,091 documents"
    assert len(store.inverted_index) > 100, "BM25 Inverted index must be populated"
    types = {d.doc_type for d in store.docs}
    assert "market_signal" in types
    assert "printway_sku" in types
    assert "niche_playbook" in types


def test_rag_hybrid_retrieval():
    results = hybrid_retrieve("stainless tumbler", top_k=5)
    assert len(results) > 0, "Retriever must return relevant items"
    assert all(r.score > 0 for r in results), "Scores must be positive"
    titles = [r.title.lower() for r in results]
    assert any("tumbler" in t for t in titles), "Retrieved titles must match query"


def test_unit_economics_tool():
    res = AgentHarnessTools.execute_unit_economics(market_price=28.99, base_cost=8.50)
    assert res.success is True
    assert res.data["gross_profit_per_unit"] > 0
    assert res.data["profit_margin_pct"] > 50.0


@pytest.mark.asyncio
async def test_agent_harness_tools_rag_search():
    res = await AgentHarnessTools.execute_rag_search("pet collar", top_k=3)
    assert res.success is True
    assert len(res.data) > 0


@pytest.mark.asyncio
async def test_deep_research_agent_run():
    agent = DeepResearchAgent()
    req = AgentAnalysisRequest(
        query="holiday ornament",
        window="30d",
        data_source="MARKET_SIGNALS",
        limit=5,
        deep=True,
        live_scrape=False,
    )
    trace = []
    report = await agent.run(req, trace_callback=trace)

    assert report.query == "holiday ornament"
    assert report.raw_records_read > 0
    assert len(report.top_keywords) > 0
    assert len(report.rd_recommendations) > 0
    assert len(report.agent_trace) > 5, "Trace must reflect multi-stage agent execution"
    assert report.forecast is not None
    assert len(report.forecast.daily) == 30
