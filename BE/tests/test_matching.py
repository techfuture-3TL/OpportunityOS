from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BE_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, BE_DIR)

from app.models.schemas import (
    OpportunityAnalysisRequest,
    MarketAndNicheInputs,
    FinancialConstraintsInputs,
    SupplyChainConstraintInputs,
    ProductCategory,
    TargetCountry,
    CraftingTechnique,
    WarehouseLocation,
    DataSourceSelection
)
from app.services.catalog_matcher import match_opportunities

def test_matching_logic():
    print("=" * 60)
    print("🧪 TEST UNIT: 3 KHỐI LỌC VÀ SO KHỚP KHO PHÔI PRINTWAY")
    print("=" * 60)

    # Test 1: Lọc Ngành Drinkware
    req1 = OpportunityAnalysisRequest(
        data_source=DataSourceSelection.ALL,
        market_and_niche=MarketAndNicheInputs(
            categories=[ProductCategory.DRINKWARE]
        ),
        limit=5
    )
    res1 = match_opportunities(req1)
    assert len(res1) > 0
    print(f"✅ 1. Lọc theo ngành Drinkware: Tìm thấy {len(res1)} cơ hội (Mã SKU: {[r.matched_sku for r in res1]})")

    # Test 2: Lọc Tài chính biên lãi tối thiểu >= 70%
    req2 = OpportunityAnalysisRequest(
        financials=FinancialConstraintsInputs(min_profit_margin_pct=70.0),
        limit=5
    )
    res2 = match_opportunities(req2)
    assert len(res2) > 0
    for r in res2:
        assert r.profit_margin_pct >= 70.0
    print(f"✅ 2. Lọc tài chính Margin ≥ 70%: Tất cả {len(res2)} cơ hội đều đạt chuẩn lãi gộp cao.")

    # Test 3: Lọc kỹ thuật Khắc Laser và Kho US
    req3 = OpportunityAnalysisRequest(
        supply_chain=SupplyChainConstraintInputs(
            preferred_warehouse=WarehouseLocation.US_DOMESTIC,
            allowed_techniques=[CraftingTechnique.LASER_ENGRAVING]
        ),
        limit=5
    )
    res3 = match_opportunities(req3)
    assert len(res3) > 0
    print(f"✅ 3. Lọc kho US + Khắc Laser: Tìm thấy {len(res3)} cơ hội phù hợp năng lực xưởng.")

    print("\n" + "=" * 60)
    print("🎉 TOÀN BỘ TEST MATCHING ĐÃ HOÀN THÀNH XUẤT SẮC!")
    print("=" * 60)

if __name__ == "__main__":
    test_matching_logic()
