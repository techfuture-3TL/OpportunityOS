from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BE_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, BE_DIR)

import asyncio
from app.models.schemas import (
    OpportunityAnalysisRequest,
    MarketAndNicheInputs,
    FinancialConstraintsInputs,
    SupplyChainConstraintInputs,
    ScoringStrategyInputs,
    ProductCategory,
    TargetCountry,
    CraftingTechnique,
    WarehouseLocation,
    StrategyPreset,
    DataSourceSelection,
    GenerateBriefRequest
)
from app.api.routes import (
    health_check,
    list_catalog,
    list_strategies,
    database_statistics,
    database_sample_keywords,
    analyze_opportunities,
    get_opportunity_detail,
    generate_brief
)


async def _test_full_pipeline():
    print("=" * 80)
    print("🚀 BẮT ĐẦU TEST TOÀN BỘ BACKEND VỚI NGUỒN DỮ LIỆU CỨNG (2092 BẢN GHI CSV)")
    print("=" * 80)

    # 1. Health
    health = await health_check()
    assert health["status"] == "healthy"
    print("✅ 1. GET /api/v1/health: PASS")

    # 2. Database stats
    db_stats = await database_statistics()
    assert db_stats["total_records"] > 0
    print(f"✅ 2. GET /api/v1/database/stats: PASS -> {db_stats['total_records']} bản ghi")

    # 3. Database sample
    db_sample = await database_sample_keywords(limit=3)
    assert len(db_sample["sample"]) == 3
    print("✅ 3. GET /api/v1/database/sample: PASS")

    # 4. Catalog
    cat = await list_catalog()
    assert cat["total_skus"] > 0
    print(f"✅ 4. GET /api/v1/catalog: PASS -> {cat['total_skus']} SKUs")

    # 5. Analyze on CSV DB
    req_db = OpportunityAnalysisRequest(
        search_mode="DISCOVERY",
        data_source=DataSourceSelection.DATABASE_CSV,
        limit=10,
        strategy=ScoringStrategyInputs(preset=StrategyPreset.VIRAL_TREND)
    )
    res_db = await analyze_opportunities(req_db)
    assert res_db.total_opportunities > 0
    print(f"✅ 5. POST /api/v1/opportunities/analyze: PASS -> "
          f"{res_db.total_opportunities} cơ hội trong {res_db.execution_time_ms}ms")
    top = res_db.opportunities[0]
    print(f"   #1 [{top.id}] {top.name} score={top.opportunity_score}")
    print(f"      pain_points={len(top.pain_points)} trademark_alert={top.trademark_alert}")

    # 6. Guided filter
    req_hw = OpportunityAnalysisRequest(
        search_mode="GUIDED",
        data_source=DataSourceSelection.DATABASE_CSV,
        market_and_niche=MarketAndNicheInputs(
            categories=[ProductCategory.DRINKWARE],
            seed_keywords=["Halloween"]
        ),
        financials=FinancialConstraintsInputs(min_profit_margin_pct=50.0),
        limit=5
    )
    res_hw = await analyze_opportunities(req_hw)
    print(f"✅ 6. Lọc Drinkware + Halloween: {len(res_hw.opportunities)} cơ hội khớp")

    # 7. Detail by id
    detail = await get_opportunity_detail(top.id)
    assert detail.id == top.id
    print(f"✅ 7. GET /api/v1/opportunities/{top.id}: PASS")

    # 8. Brief (LLM primary + fallback; may take time if DeepSeek is live)
    brief = await generate_brief(GenerateBriefRequest(opportunity_id=top.id))
    assert brief.title
    print(f"✅ 8. POST /api/v1/opportunities/generate-brief: PASS -> {brief.title}")
    print(f"   break_even: {brief.financial_model.get('projected_break_even_units')} units")

    print("\n" + "=" * 80)
    print("🎉 TOÀN BỘ DATABASE VÀ API BACKEND ĐÃ KẾT NỐI VÀ CHẠY HOÀN HẢO 100%!")
    print("=" * 80)


def test_full_pipeline_with_database():
    asyncio.run(_test_full_pipeline())


if __name__ == "__main__":
    test_full_pipeline_with_database()
