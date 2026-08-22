"""API v1 routes - realtime crawl and analyze, NO PERSISTENCE."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.responses import ApiResponse
from app.models.schemas import DataSource, TimeWindow, StrategyPreset, ScoringStrategy
from app.services.agent.service import AgentService
from app.services.crawl.service import CrawlService
from app.services.scoring.service import ScoringService


router = APIRouter(prefix="/api/v1", tags=["v1"])


# ============================================================================
# Request Models
# ============================================================================

class AnalyzeRequestIn(BaseModel):
    query: str
    window: str = "30d"
    data_source: str = "ALL"
    limit: int = 10
    sources: Optional[List[str]] = None
    deep: bool = True


class CrawlRequestIn(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    platform: Optional[str] = None
    max_items: int = 30
    limit: Optional[int] = None
    days: int = 7


class AgentJobRequestIn(BaseModel):
    query: str
    window: str = "30d"
    data_source: str = "ALL"
    deep: bool = True
    sources: Optional[List[str]] = None


# ============================================================================
# POST /api/v1/crawl & POST /api/v1/crawlers/search - REALTIME CRAWL
# ============================================================================

@router.post("/crawl", response_model=ApiResponse)
@router.post("/crawlers/search", response_model=ApiResponse)
async def crawl_marketplace(request: CrawlRequestIn) -> ApiResponse:
    """
    Crawl marketplace data in realtime.

    NO PERSISTENCE - Returns data directly.
    Job metadata goes to Supabase.
    """
    service = CrawlService()

    # Normalize sources from platform / sources
    sources = request.sources
    if not sources and request.platform:
        if request.platform.lower() in ("all", "*"):
            sources = ["ebay", "amazon", "etsy", "tiktok", "shopee"]
        else:
            sources = [s.strip().lower() for s in request.platform.split(",") if s.strip()]

    max_items = request.limit or request.max_items or 30

    try:
        result = await service.crawl(
            query=request.query,
            sources=sources,
            max_items=max_items,
            days=request.days,
        )
        return ApiResponse.ok(result, f"Crawled {result['products_found']} products")
    except Exception as e:
        return ApiResponse.fail(str(e), "Crawl failed")



# ============================================================================
# POST /api/v1/analyze - REALTIME + AI
# ============================================================================

@router.post("/analyze", response_model=ApiResponse)
async def analyze_market(request: AnalyzeRequestIn) -> ApiResponse:
    """
    Run AI market analysis - REALTIME.

    NO PERSISTENCE - All processing in memory.
    Job metadata goes to Supabase.
    """
    window_map = {
        "7d": TimeWindow.DAY_7,
        "30d": TimeWindow.DAY_30,
        "90d": TimeWindow.DAY_90,
        "1y": TimeWindow.YEAR_1,
    }
    data_source_map = {
        "ALL": DataSource.ALL,
        "LIVE_ONLY": DataSource.LIVE_ONLY,
        "TIKTOK_SHOP": DataSource.TIKTOK_SHOP,
    }

    service = AgentService()

    try:
        report = await service.analyze(
            query=request.query,
            window=window_map.get(request.window, TimeWindow.DAY_30),
            data_source=data_source_map.get(request.data_source, DataSource.ALL),
            limit=request.limit,
            sources=request.sources,
            deep=request.deep,
        )
        return ApiResponse.ok(report, "Analysis complete")
    except Exception as e:
        return ApiResponse.fail(str(e), "Analysis failed")


# ============================================================================
# POST /api/v1/score - SCORE SIGNALS
# ============================================================================

@router.post("/score")
async def score_opportunities(
    signals: List[Dict[str, Any]],
    preset: str = "viral_trend",
) -> ApiResponse:
    """Score market signals for opportunities."""
    preset_map = {
        "viral_trend": StrategyPreset.VIRAL_TREND,
        "high_margin": StrategyPreset.HIGH_MARGIN,
        "safe_evergreen": StrategyPreset.SAFE_EVERGREEN,
        "low_competition": StrategyPreset.LOW_COMPETITION,
    }

    strategy = ScoringStrategy.with_preset(
        preset_map.get(preset, StrategyPreset.VIRAL_TREND)
    )
    service = ScoringService(strategy=strategy)

    try:
        opportunities = service.get_top_opportunities(signals, limit=20, min_score=40.0)
        return ApiResponse.ok(
            [o.model_dump() for o in opportunities],
            f"{len(opportunities)} opportunities"
        )
    except Exception as e:
        return ApiResponse.fail(str(e), "Scoring failed")


# ============================================================================
# POST /api/v1/agent/jobs & GET /api/v1/agent/jobs/{job_id} - DEEP RESEARCH AGENT
# ============================================================================

@router.post("/agent/jobs", response_model=ApiResponse)
async def create_agent_job(request: AgentJobRequestIn) -> ApiResponse:
    """Create and dispatch asynchronous Deep Research CoT job."""
    from app.services.agent.jobs import AgentJobStore, run_agent_job_background
    import uuid

    job_id = f"job-{uuid.uuid4().hex[:8]}"
    AgentJobStore.create_job(
        job_id=job_id,
        query=request.query,
        window=request.window,
        data_source=request.data_source,
        deep=request.deep,
    )
    run_agent_job_background(
        job_id=job_id,
        query=request.query,
        window=request.window,
        data_source=request.data_source,
        deep=request.deep,
        sources=request.sources,
    )
    job = AgentJobStore.get_job(job_id)
    return ApiResponse.ok(job.model_dump() if job else {"job_id": job_id}, "Agent research job dispatched")


@router.get("/agent/jobs/{job_id}", response_model=ApiResponse)
async def get_agent_job_status(job_id: str) -> ApiResponse:
    """Get status and report of Deep Research agent job."""
    from app.services.agent.jobs import AgentJobStore

    job = AgentJobStore.get_job(job_id)
    if not job:
        return ApiResponse.fail(f"Job {job_id} not found", "Not Found", code=404)
    return ApiResponse.ok(job.model_dump(), f"Job status: {job.status}")


# ============================================================================
# GET /api/v1/health - HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    from app.core.config import settings
    from app.services.database import supabase

    return {
        "status": "healthy",
        "kalodata_configured": settings.has_kalodata_key,
        "sources": settings.crawl_sources,
        "supabase_connected": supabase.is_connected(),
    }
