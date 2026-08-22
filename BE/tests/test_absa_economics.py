"""ABSA review mining + unit economics tests (BÁO CÁO 02 + 04)."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

from app.services.review_miner import (extract_pain_points, match_pain_to_features,
                                       pain_weight_sum)
from app.services.unit_economics import (break_even_units, gross_profit,
                                         marketing_budget_plan, profit_margin_pct,
                                         sensitivity_matrix, unit_profit,
                                         unit_economics_report)


REVIEWS = [
    "The printed design peeled off after 2 washes in the dishwasher. Mug feels cheap & thin.",
    "No option to personalize with custom names. Shipping took forever.",
]


def test_extract_pain_points():
    pains = extract_pain_points(REVIEWS)
    aspects = {p["aspect"] for p in pains}
    assert "print_durability" in aspects
    assert "material_quality" in aspects
    assert "no_personalization" in aspects
    assert "slow_shipping" in aspects
    # severity weights per doc: durability/material 15, others 10
    sev = {p["aspect"]: p["severity"] for p in pains}
    assert sev["print_durability"] == 15.0
    assert sev["no_personalization"] == 10.0


def test_pain_weight_cap():
    assert pain_weight_sum(extract_pain_points(REVIEWS)) == 50.0
    assert pain_weight_sum([]) == 0.0


def test_pain_to_feature():
    sols = match_pain_to_features(extract_pain_points(REVIEWS))
    assert sols, "no solutions mapped"
    assert any(s["technique"] == "LASER_ENGRAVING" for s in sols)


def test_unit_profit_equation():
    # P - COGS - fee(5%) - CPA - shipping
    p = unit_profit(29.99, 7.80, platform="tiktok_shop", cpa_ads=5.0, shipping=4.5)
    assert abs(p - (29.99 - 7.80 - 29.99 * 0.05 - 5.0 - 4.5)) < 0.01


def test_doc_example_margin():
    # Doc 04: $29.99 retail, $7.80 COGS => 74.0% margin, +$22.19 gross
    assert abs(gross_profit(29.99, 7.80) - 22.19) < 0.01
    assert profit_margin_pct(29.99, 7.80) == 74.0


def test_doc_example_break_even():
    # Q = 1000 / 22.19 = 45.06 -> 46 units
    assert abs(break_even_units(1000.0, 29.99, 7.80) - 45.1) < 0.1


def test_sensitivity_matrix_shape():
    rows = sensitivity_matrix(7.80, [24.99, 29.99, 34.99])
    assert len(rows) == 3
    assert all("cpa_5" in r["cpa_profits"] for r in rows)
    best = rows[1]
    assert best["verdict"].startswith("LÝ TƯỞNG")


def test_budget_phases_sum_to_total():
    phases = marketing_budget_plan(1000.0)
    assert sum(p["amount"] for p in phases) == 1000.0
    assert [p["pct"] for p in phases] == [15, 35, 20, 30]


def test_economics_report_complete():
    rep = unit_economics_report(29.99, 7.80)
    assert rep["break_even_units"] > 0
    assert rep["sensitivity_matrix"]
    assert rep["marketing_budget_phases"]
