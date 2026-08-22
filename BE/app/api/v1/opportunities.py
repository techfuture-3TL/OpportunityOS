"""PW1 Product Opportunity Hub — API endpoints (frontend contract)."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from app.core.responses import ApiResponse
from app.models.schemas import (
    OpportunityAnalysisRequestPW1,
    OpportunityAnalysisResponsePW1,
    GenerateBriefRequestPW1,
    StrategyPreset,
)
from app.services.pw1.ai_copilot import generate_product_brief
from app.services.pw1.catalog_matcher import (
    auto_crawl_full,
    get_printway_catalog,
    get_seed_market_signals,
    match_opportunities,
)
from app.services.pw1.database_service import CSVDatabaseService

router = APIRouter(prefix="/api/v1", tags=["pw1"])

STRATEGY_LABELS = {
    "VIRAL_TREND": ("Bắt Trend TikTok Nóng", "Ưu tiên tối đa tốc độ tăng trưởng doanh số và độ ăn hình video TikTok."),
    "HIGH_MARGIN": ("Lợi Nhuận Siêu Dày", "Ưu tiên các sản phẩm có biên lợi nhuận gộp cao nhất (> 70%)."),
    "SAFE_EVERGREEN": ("Ăn Chắc Mặc Bền", "Ưu tiên sản phẩm an toàn bản quyền 100% và chuỗi cung ứng ổn định quanh năm."),
    "LOW_COMPETITION": ("Đánh Vào Ngách Trống", "Ưu tiên ngách nhiều review chê đối thủ nhưng ít gian hàng lớn độc quyền."),
}


@router.get("/catalog")
def list_catalog() -> Dict[str, Any]:
    items = get_printway_catalog()
    catalog = [
        {
            "sku": item.get("sku"),
            "name": item.get("name"),
            "category": item.get("category"),
            "base_cost": item.get("base_cost"),
            "suggested_min_price": item.get("suggested_min_price"),
            "suggested_max_price": item.get("suggested_max_price"),
            "warehouses": item.get("warehouses", []),
            "techniques": item.get("techniques", []),
            "production_days": item.get("production_days", 2),
            "description": item.get("description", ""),
        }
        for item in items
    ]
    return {"total_skus": len(catalog), "catalog": catalog}


@router.get("/database/stats")
def database_statistics() -> Dict[str, Any]:
    return CSVDatabaseService.get_database_stats()


@router.get("/database/sample")
def database_sample_keywords(limit: int = Query(default=10, ge=1, le=100)) -> Dict[str, Any]:
    records = CSVDatabaseService.load_database_records()
    return {"total_records": len(records), "sample": records[:limit]}


@router.get("/strategies")
def list_strategies() -> List[Dict[str, Any]]:
    weights = {
        "VIRAL_TREND": {"demand": 0.35, "gap": 0.15, "margin": 0.15, "supply": 0.10, "safety": 0.10, "virality": 0.15},
        "HIGH_MARGIN": {"demand": 0.20, "gap": 0.15, "margin": 0.40, "supply": 0.10, "safety": 0.10, "virality": 0.05},
        "SAFE_EVERGREEN": {"demand": 0.15, "gap": 0.20, "margin": 0.20, "supply": 0.20, "safety": 0.20, "virality": 0.05},
        "LOW_COMPETITION": {"demand": 0.20, "gap": 0.40, "margin": 0.15, "supply": 0.10, "safety": 0.10, "virality": 0.05},
    }
    return [
        {
            "id": preset,
            "name": STRATEGY_LABELS.get(preset, (preset, ""))[0],
            "description": STRATEGY_LABELS.get(preset, (preset, ""))[1],
            "weights": weights.get(preset, weights["VIRAL_TREND"]),
        }
        for preset in ["VIRAL_TREND", "HIGH_MARGIN", "SAFE_EVERGREEN", "LOW_COMPETITION", "CUSTOM_WEIGHTS"]
    ]


@router.get("/marketplace/stats")
def marketplace_statistics() -> Dict[str, Any]:
    csv_count = len(CSVDatabaseService.load_database_records())
    seed_count = len(get_seed_market_signals())
    return {
        "status": "live",
        "marketplace_live_signals_count": seed_count,
        "csv_database_records_count": csv_count,
        "total_combined_signals": csv_count + seed_count,
        "crawler_status": {
            "tiktok": "ready",
            "amazon": "ready",
            "ebay": "ready",
            "shopee": "ready",
            "lazada": "ready",
            "etsy": "ready",
        },
    }


@router.post("/opportunities/analyze", response_model=OpportunityAnalysisResponsePW1)
async def analyze_opportunities(request: OpportunityAnalysisRequestPW1) -> OpportunityAnalysisResponsePW1:
    """
    ENDPOINT CHÍNH PW1:
    - Auto crawl full 5 sàn TMĐT (ưu tiên dữ liệu live, có timeout an toàn)
    - Đối soát 2,091 dòng CSV + seed signals
    - Bộ lọc 3 khối → chấm điểm MCDA 6 trụ cột chi tiết (sub-scores, weights, contributions)
    - Trả kèm IP check 3 tầng + verdict GO/CAUTION/STOP
    """
    start_time = time.time()
    results = await match_opportunities(request)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    strategy_name = str(request.strategy.preset or "VIRAL_TREND")
    source_name = str(request.data_source or "ALL")

    return OpportunityAnalysisResponsePW1(
        total_opportunities=len(results),
        execution_time_ms=elapsed_ms,
        applied_strategy=strategy_name,
        data_source_used=source_name,
        crawl_summary={"auto_crawl_full": True, "marketplaces": ["tiktok", "amazon", "ebay", "shopee", "lazada", "etsy"]},
        opportunities=results,
    )


@router.get("/opportunities/{opportunity_id}")
async def get_opportunity_detail(opportunity_id: str = Path(...)) -> ApiResponse:
    default_req = OpportunityAnalysisRequestPW1(limit=100)
    all_opps = await match_opportunities(default_req)
    for opp in all_opps:
        if opp.id == opportunity_id:
            return ApiResponse.ok(opp.model_dump(), "Opportunity found")
    raise HTTPException(status_code=404, detail=f"Không tìm thấy cơ hội với ID: {opportunity_id}")


@router.post("/opportunities/generate-brief")
def generate_brief(request: GenerateBriefRequestPW1) -> Dict[str, Any]:
    """DeepSeek AI sinh Product Brief: executive summary, 3 prompt in, kế hoạch TikTok 14 ngày, checklist."""
    return generate_product_brief(
        opportunity_id=request.opportunity_id,
        custom_notes=request.custom_notes,
    )
