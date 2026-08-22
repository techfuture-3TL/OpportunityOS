"""Comprehensive test suite for deep quantitative 6-pillar opportunity scoring & financial metrics."""
import pytest
from app.models.schemas import ScoreBreakdown
from app.services.scoring.service import (
    ScoringService,
    _generate_pillar_rationales,
    _map_sku,
    INDUSTRY_BENCHMARKS,
)


def test_map_sku_catalog():
    """Verify SKU mapping for different product categories."""
    assert _map_sku("HydroJug Insulated Tumbler")[0] == "PW-DRINK-TUMB-20OZ"
    assert _map_sku("Bình giữ nhiệt inox 40oz")[0] == "PW-DRINK-TUMB-20OZ"
    assert _map_sku("Custom Nike Style Sneaker Shoes")[0] == "PW-FOOT-SNEAKER-CUSTOM"
    assert _map_sku("Christmas Acrylic LED Night Light")[0] == "PW-GIFT-ACRYLIC-LIGHT"
    assert _map_sku("Vintage Unisex Heavyweight T-Shirt")[0] == "PW-APP-TEE-HEAVY"


def test_financial_deductions_and_net_profit():
    """Verify exact net profit calculation after platform fees and payment processing."""
    sig = {
        "signal_id": "SIG-TEST-1",
        "title": "HydroJug Traveler 40oz Tumbler",
        "niche": "Tumbler POD",
        "price": 24.99,
        "quantity_sold": 660,
        "growth_rate": 109,
        "reviews_count": 45,
        "views": 150000,
        "source": "tiktok",
    }
    breakdown = ScoreBreakdown(
        demand_growth=100.0,
        market_gap=88.0,
        profit_margin=90.0,
        supply_feasibility=85.0,
        ip_safety=80.0,
        tiktok_virality=95.0,
    )
    
    rationales, explanations, breakdown_details, pain, kws, fin = _generate_pillar_rationales(
        sig=sig,
        breakdown=breakdown,
        margin_pct=66.0,
        base_cost=8.50,
        suggested_price=24.99,
    )
    
    # Financial verifications
    assert fin["revenue"] == round(24.99 * 660, 2)
    assert fin["platform_fee"] == round(24.99 * 0.15, 2)  # 15%
    assert fin["net_unit_profit"] > 0
    assert fin["net_total_profit"] == round(fin["net_unit_profit"] * 660, 2)
    
    # Pillar reason verifications
    assert "Doanh số kiếm được:" in rationales["demand_growth"]
    assert "người mua tại khu vực US/VN" in rationales["demand_growth"]
    assert "sản phẩm công năng tương tự" in rationales["ip_safety"]
    assert "Lãi ròng kiếm được trên mỗi sản phẩm:" in rationales["profit_margin"]
    assert "TỔNG TIỀN LÃI RÒNG THỰC TẾ KIẾM ĐƯỢC:" in rationales["profit_margin"]
    assert "Truy xuất TikTok Search API:" in rationales["tiktok_virality"]
    assert "lượt tìm kiếm từ khóa/tháng" in rationales["tiktok_virality"]


def test_scoring_service_end_to_end():
    """Verify full scoring service pipeline produces complete valid OpportunityItem."""
    service = ScoringService()
    signals = [
        {
            "signal_id": "SIG-TUMBLER-40OZ",
            "title": "40oz Stainless Steel Insulated Tumbler",
            "niche": "Drinkware",
            "price": 29.99,
            "quantity_sold": 1200,
            "growth_rate": 85,
            "reviews_count": 30,
            "views": 250000,
            "source": "tiktok",
        }
    ]
    
    opportunities = service.score(signals)
    assert len(opportunities) == 1
    opp = opportunities[0]
    
    assert opp.opportunity_score > 0
    assert opp.best_fit_sku == "PW-DRINK-TUMB-20OZ"
    assert opp.unit_economics["net_unit_profit"] > 0
    assert opp.unit_economics["net_total_profit"] > 0
    assert len(opp.keywords) > 0
    assert len(opp.score_rationales) >= 6
    assert len(opp.pillar_explanations) == 6
    
    # Check all 6 alias keys exist for frontend compatibility
    for key in ["demand", "gap", "margin", "supply", "safety", "virality"]:
        assert key in opp.score_rationales
        assert len(opp.score_rationales[key]) > 50


def test_competitor_price_does_not_undercut_printway_target():
    """A low marketplace benchmark must not become an unprofitable POD retail target."""
    opportunity = ScoringService().score([
        {
            "signal_id": "SIG-LAZADA-1",
            "title": "Bình giữ nhiệt Lazada",
            "price": 8.5,
            "quantity_sold": 100,
            "growth_rate": 40,
            "source": "lazada",
        }
    ])[0]

    assert opportunity.best_fit_sku == "PW-DRINK-TUMB-20OZ"
    assert opportunity.suggested_price == 24.99
    assert opportunity.profit_margin_pct >= 60


if __name__ == "__main__":
    pytest.main(["-v", __file__])
