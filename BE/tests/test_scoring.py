from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BE_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, BE_DIR)

from app.services.scoring_engine import calculate_opportunity_score

def test_scoring_presets():
    print("=" * 60)
    print("🧪 TEST UNIT: THUẬT TOÁN CHẤM ĐIỂM OPPORTUNITY SCORE 6 TRỤ CỘT")
    print("=" * 60)

    # Kịch bản 1: Hot Trend TikTok
    score_viral, breakdown_viral = calculate_opportunity_score(
        demand_growth_pct=250.0,
        google_trends=95.0,
        competitor_count=15,
        negative_reviews_count=4,
        profit_margin_pct=72.0,
        production_days=2,
        warehouse_match=True,
        ip_safety_rating=98.0,
        virality_rating=95.0,
        strategy="VIRAL_TREND"
    )
    print(f"✅ 1. Test Preset VIRAL_TREND: Score = {score_viral}/100")
    assert score_viral >= 85.0
    print(f"     Breakdown: Demand={breakdown_viral.demand_growth}, Gap={breakdown_viral.market_gap}, Margin={breakdown_viral.profit_margin}")

    # Kịch bản 2: High Margin
    score_margin, breakdown_margin = calculate_opportunity_score(
        demand_growth_pct=80.0,
        google_trends=60.0,
        competitor_count=20,
        negative_reviews_count=2,
        profit_margin_pct=80.0,
        production_days=3,
        warehouse_match=True,
        strategy="HIGH_MARGIN"
    )
    print(f"\n✅ 2. Test Preset HIGH_MARGIN: Score = {score_margin}/100")
    assert score_margin >= 70.0

    # Kịch bản 3: Dính Trademark bản quyền (IP Safety thấp)
    score_unsafe, breakdown_unsafe = calculate_opportunity_score(
        demand_growth_pct=200.0,
        google_trends=90.0,
        competitor_count=50,
        negative_reviews_count=1,
        profit_margin_pct=60.0,
        production_days=2,
        warehouse_match=True,
        ip_safety_rating=40.0, # Dính trademark
        strategy="SAFE_EVERGREEN"
    )
    print(f"\n✅ 3. Test IP Trademark Alert: Score = {score_unsafe}/100 (IP Safety = {breakdown_unsafe.ip_safety})")
    assert breakdown_unsafe.ip_safety <= 45.0

    print("\n" + "=" * 60)
    print("🎉 TOÀN BỘ TEST SCORING ĐÃ HOÀN THÀNH XUẤT SẮC!")
    print("=" * 60)

if __name__ == "__main__":
    test_scoring_presets()
