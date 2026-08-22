"""PW1 Scoring Engine — MCDA 6 trụ cột chuẩn hóa Sigmoid.

Bám sát phương pháp luận: document/01_PHUONG_PHAP_LUAN_TOAN_HOC_VA_CHAM_DIEM.md
S(x) = Σ w_k · S_k(x), Σ w_k = 1.0

Mỗi trụ cột trả về: điểm, các sub-score thành phần, evidence và công thức giải tích.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


STRATEGY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "VIRAL_TREND": {"demand": 0.35, "gap": 0.15, "margin": 0.15, "supply": 0.10, "safety": 0.10, "virality": 0.15},
    "HIGH_MARGIN": {"demand": 0.20, "gap": 0.15, "margin": 0.40, "supply": 0.10, "safety": 0.10, "virality": 0.05},
    "SAFE_EVERGREEN": {"demand": 0.15, "gap": 0.20, "margin": 0.20, "supply": 0.20, "safety": 0.20, "virality": 0.05},
    "LOW_COMPETITION": {"demand": 0.20, "gap": 0.40, "margin": 0.15, "supply": 0.10, "safety": 0.10, "virality": 0.05},
}

PILLAR_LABELS = {
    "demand": ("Nhu Cầu", "Demand"),
    "gap": ("Khoảng Trống", "Market Gap"),
    "margin": ("Biên Lãi", "Profit Margin"),
    "supply": ("Chuỗi Cung", "Supply Chain"),
    "safety": ("Bản Quyền", "IP Safety"),
    "virality": ("Viral TikTok", "TikTok Virality"),
}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(min(x, 15.0), -15.0)))


def _z(score: float, mean: float, std: float) -> float:
    return (score - mean) / max(std, 1e-6)


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(min(high, max(low, value)), 1)


# ─────────────────────────────────────────────────────────────────────────
# 1. S_Demand — Z-Score đa biến + Sigmoid + hệ số ý định mua
# ─────────────────────────────────────────────────────────────────────────
def _pillar_demand(sig: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    dm = sig.get("demand_metrics", {}) or {}
    raw = sig.get("raw_csv_row", {}) or {}

    growth = float(dm.get("tiktok_shop_sales_growth_pct") or raw.get("growth") or 50.0)
    trends = float(dm.get("google_trends_score") or raw.get("trend") or 50.0)
    demand_idx = float(
        dm.get("amazon_monthly_search_vol") or raw.get("demand") or 50.0
    )
    # Khối lượng tìm kiếm Amazon chuyển về thang 0-100 (log-scale)
    if demand_idx > 100:
        demand_idx = min(100.0, 30.0 + math.log10(max(demand_idx, 10.0)) * 15.0)
    velocity = float(dm.get("tiktok_views_growth_pct") or raw.get("trend") or 50.0)
    intent = str(raw.get("buyer_intent") or dm.get("buyer_intent") or "MEDIUM")

    z_growth = _z(growth, 50.0, 40.0)
    z_trends = _z(trends, 50.0, 25.0)
    z_demand = _z(demand_idx, 50.0, 25.0)
    z_velocity = _z(velocity, 50.0, 25.0)

    composite = 0.40 * z_growth + 0.25 * z_trends + 0.20 * z_demand + 0.15 * z_velocity
    base = _sigmoid(composite) * 100.0
    intent_upper = intent.upper()
    mult = 1.10 if intent_upper in ("HIGH", "STRONG", "PURCHASE", "GIFT") else (0.90 if intent_upper in ("LOW", "WEAK") else 1.0)

    score = _clamp(base * mult, 20.0, 100.0)
    sub_scores = [
        {
            "label_vi": f"Tăng trưởng TikTok (z = {z_growth:+.2f})",
            "label_en": f"TikTok growth (z = {z_growth:+.2f})",
            "score": _clamp(40.0 + z_growth * 20.0),
            "evidence": f"+{growth:g}% sales growth",
        },
        {
            "label_vi": f"Google Trends (z = {z_trends:+.2f})",
            "label_en": f"Google Trends (z = {z_trends:+.2f})",
            "score": _clamp(40.0 + z_trends * 20.0),
            "evidence": f"{trends:g}/100 trends",
        },
        {
            "label_vi": f"Nhu cầu tìm kiếm (z = {z_demand:+.2f})",
            "label_en": f"Search demand (z = {z_demand:+.2f})",
            "score": _clamp(40.0 + z_demand * 20.0),
            "evidence": f"demand index {demand_idx:g}/100",
        },
        {
            "label_vi": f"Vận tốc viral (z = {z_velocity:+.2f})",
            "label_en": f"Viral velocity (z = {z_velocity:+.2f})",
            "score": _clamp(40.0 + z_velocity * 20.0),
            "evidence": f"views velocity {velocity:g}",
        },
        {
            "label_vi": f"Hệ số ý định mua ×{mult}",
            "label_en": f"Buyer intent ×{mult}",
            "score": mult * 50.0,
            "evidence": f"buyer_intent = {intent_upper}",
        },
    ]
    return score, sub_scores


# ─────────────────────────────────────────────────────────────────────────
# 2. S_Gap — CDI (Customer Disappointment Index) + độ bão hòa ngách
# ─────────────────────────────────────────────────────────────────────────
def _pillar_gap(sig: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    comp = sig.get("competitor_analysis", {}) or {}
    raw = sig.get("raw_csv_row", {}) or {}

    competition_index = float(raw.get("competition") or (comp.get("competitor_count", 20) * 2.0) or 40.0)
    opportunity_index = float(raw.get("opportunity") or 70.0)
    negative_reviews = comp.get("top_negative_reviews", []) or []
    pain_desc = comp.get("market_gap_description", "") or ""

    comp_component = max(0.0, 100.0 - competition_index)
    opp_component = min(100.0, max(0.0, opportunity_index))
    pain_component = min(30.0, len(negative_reviews) * 10.0)
    pain_bonus = 15.0 if pain_desc else 0.0

    score = _clamp(0.35 * comp_component + 0.35 * opp_component + pain_component + pain_bonus, 15.0)
    sub_scores = [
        {
            "label_vi": "Điểm ít cạnh tranh (100 − Competition)",
            "label_en": "Inverse competition (100 − Competition)",
            "score": _clamp(comp_component),
            "evidence": f"competition index = {competition_index:g}",
        },
        {
            "label_vi": "Chỉ số cơ hội ngách",
            "label_en": "Niche opportunity index",
            "score": _clamp(opp_component),
            "evidence": f"opportunity = {opportunity_index:g}/100",
        },
        {
            "label_vi": f"Nỗi đau review (min 30): {len(negative_reviews)} review 1-3★",
            "label_en": f"Review pain (cap 30): {len(negative_reviews)} negative reviews",
            "score": pain_component,
            "evidence": f"{len(negative_reviews)} pain reviews mined",
        },
        {
            "label_vi": "Khớp giải pháp phôi Printway (+15)",
            "label_en": "Printway blank match bonus (+15)",
            "score": float(pain_bonus),
            "evidence": "SKU solves competitor flaws",
        },
    ]
    return score, sub_scores


# ─────────────────────────────────────────────────────────────────────────
# 3. S_Margin — Lợi nhuận kép (% margin + đệm tiền lãi $)
# ─────────────────────────────────────────────────────────────────────────
def _pillar_margin(
    profit_margin_pct: float, profit_per_unit: float, min_margin_pct: float
) -> Tuple[float, List[Dict[str, Any]]]:
    if profit_margin_pct < min_margin_pct:
        return 0.0, [
            {
                "label_vi": "Dưới ngưỡng biên lãi → 0đ",
                "label_en": "Below margin threshold → 0",
                "score": 0.0,
                "evidence": f"{profit_margin_pct:.1f}% < {min_margin_pct:g}%",
            }
        ]

    score_pct = min(100.0, ((profit_margin_pct - min_margin_pct) / max(1.0, 75.0 - min_margin_pct)) * 100.0)
    score_dollar = min(100.0, (profit_per_unit / 20.0) * 100.0)
    combined = 0.60 * score_pct + 0.40 * score_dollar

    sub_scores = [
        {
            "label_vi": "Tỷ suất biên lãi (60%)",
            "label_en": "Margin % score (60%)",
            "score": round(score_pct, 1),
            "evidence": f"{profit_margin_pct:.1f}% gross margin",
        },
        {
            "label_vi": "Đệm tiền lãi tuyệt đối (40%)",
            "label_en": "Dollar cushion (40%)",
            "score": round(score_dollar, 1),
            "evidence": f"${profit_per_unit:.2f} profit/unit (max $20)",
        },
    ]
    return _clamp(combined), sub_scores


# ─────────────────────────────────────────────────────────────────────────
# 4. S_Supply — Vận tải + kỹ thuật gia công + SLA
# ─────────────────────────────────────────────────────────────────────────
def _pillar_supply(
    warehouse_match: bool,
    technique_match: bool,
    production_days: int,
    warehouse_label: str,
    techniques: List[str],
) -> Tuple[float, List[Dict[str, Any]]]:
    geo_score = 100.0 if warehouse_match else 70.0
    tech_score = 100.0 if technique_match else 50.0
    sla_score = max(0.0, 100.0 - max(0, production_days - 2) * 15.0)

    score = _clamp(0.45 * geo_score + 0.30 * tech_score + 0.25 * sla_score, 20.0)
    sub_scores = [
        {
            "label_vi": f"Vị trí kho (45%) — {warehouse_label}",
            "label_en": f"Warehouse location (45%) — {warehouse_label}",
            "score": geo_score,
            "evidence": "Kho nội địa ship 2-5 ngày" if warehouse_match else "Kho VN/Global",
        },
        {
            "label_vi": f"Kỹ thuật gia công (30%) — {', '.join(techniques) or 'N/A'}",
            "label_en": f"Craft technique (30%) — {', '.join(techniques) or 'N/A'}",
            "score": tech_score,
            "evidence": "Xưởng đáp ứng kỹ thuật chọn" if technique_match else "Kỹ thuật không khớp",
        },
        {
            "label_vi": f"SLA sản xuất (25%) — {production_days} ngày",
            "label_en": f"Production SLA (25%) — {production_days} days",
            "score": sla_score,
            "evidence": "≤2 ngày = 100đ, mỗi ngày trễ −15đ",
        },
    ]
    return score, sub_scores


# ─────────────────────────────────────────────────────────────────────────
# 5. S_Safety — Ma trận rủi ro IP 3 tầng
# ─────────────────────────────────────────────────────────────────────────
TRADEMARK_FLAGS = [
    "martha stewart", "pottery barn", "target", "asda", "tk maxx", "snoopy",
    "emma bridgewater", "phasmophobia", "hobby lobby", "michaels",
    "disney", "marvel", "nfl", "nba", "pokemon", "stanley", "yeti", "nike",
]
CELEBRITY_FLAGS = ["taylor swift", "harry potter", "star wars", "barbie", "hello kitty"]


def _pillar_safety(sig: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]], Dict[str, Any]]:
    ip = sig.get("ip_safety", {}) or {}
    topic = (sig.get("topic", "") or "").lower()
    status = (ip.get("status") or "").upper()
    raw_score = float(ip.get("safety_score") or 96.0)

    is_trademark = "TRADEMARK" in status or any(flag in topic for flag in TRADEMARK_FLAGS)
    is_celebrity = any(flag in topic for flag in CELEBRITY_FLAGS)

    if is_trademark:
        tier, tier_label_vi, tier_label_en, score = 1, "Vi phạm nhãn hiệu USPTO", "USPTO trademark violation", 35.0
        verdict_vi = "DỪNG — rủi ro nhãn hiệu độc quyền"
        verdict_en = "STOP — registered trademark risk"
    elif is_celebrity:
        tier, tier_label_vi, tier_label_en, score = 2, "Rủi ro trung bình (giải trí/nhân vật)", "Medium risk (entertainment/characters)", 60.0
        verdict_vi = "THẬN TRỌNG — dính tên phim/nhân vật"
        verdict_en = "CAUTION — movie/character names"
    else:
        tier, tier_label_vi, tier_label_en, score = 3, "An toàn sạch 100% (từ khóa generic)", "100% clean (generic keywords)", _clamp(raw_score, 96.0)
        verdict_vi = "GO — không vi phạm bản quyền"
        verdict_en = "GO — no IP infringement"

    ip_check = {
        "tier": tier,
        "tier_label_vi": tier_label_vi,
        "tier_label_en": tier_label_en,
        "score": round(score, 1),
        "status": ip.get("status") or ("TRADEMARK_ALERT" if is_trademark else "CLEAN_IP"),
        "verdict_vi": verdict_vi,
        "verdict_en": verdict_en,
        "notes": ip.get("notes", ""),
    }
    sub_scores = [
        {
            "label_vi": "Quét nhãn hiệu đăng ký (USPTO)",
            "label_en": "Registered trademark scan (USPTO)",
            "score": 100.0 if not is_trademark else 0.0,
            "evidence": "Phát hiện nhãn hiệu độc quyền" if is_trademark else "Không trùng nhãn hiệu đăng ký",
        },
        {
            "label_vi": "Quét tên phim/nhân vật giải trí",
            "label_en": "Movie/character name scan",
            "score": 100.0 if not is_celebrity else 0.0,
            "evidence": "Dính tên giải trí" if is_celebrity else "Không dính tên giải trí",
        },
        {
            "label_vi": "Điểm từ khóa generic POD",
            "label_en": "Generic POD keyword score",
            "score": round(raw_score, 1),
            "evidence": ip.get("notes", "Từ khóa generic, an toàn cho POD"),
        },
    ]
    return round(score, 1), sub_scores, ip_check


# ─────────────────────────────────────────────────────────────────────────
# 6. S_Virality — Visual Hook Index
# ─────────────────────────────────────────────────────────────────────────
def _pillar_virality(sig: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    vm = sig.get("virality_metrics", {}) or {}
    topic = (sig.get("topic", "") or "").lower()
    keywords = " ".join(sig.get("keywords", []) or []).lower()

    is_personalized = any(k in (topic + " " + keywords) for k in ["custom", "personalized", "personal", "name", "monogram", "engraved"])
    is_visual = float(vm.get("virality_score") or 70.0) >= 80.0 or any(
        k in (topic + " " + keywords) for k in ["light", "glow", "led", "laser", "mirror", "glitter"]
    )
    is_aesthetic = "genz" in keywords or True  # gu thẩm mỹ Gen Z 2026 mặc định bật

    score = 50.0
    if is_personalized:
        score += 20.0
    if is_visual:
        score += 18.0
    if is_aesthetic:
        score += 12.0
    score = _clamp(score, 30.0)

    sub_scores = [
        {
            "label_vi": "Cá nhân hóa (khắc tên/ảnh) +20",
            "label_en": "Personalization (name/photo) +20",
            "score": 20.0 if is_personalized else 0.0,
            "evidence": "Tăng retention rate video" if is_personalized else "Chưa có yếu tố cá nhân hóa",
        },
        {
            "label_vi": "Hiệu ứng thị giác LED/Laser +18",
            "label_en": "LED/Laser visual wow +18",
            "score": 18.0 if is_visual else 0.0,
            "evidence": vm.get("visual_wow_factor", "Hiệu ứng đổi màu/đèn LED"),
        },
        {
            "label_vi": "Gu thẩm mỹ Gen Z 2026 +12",
            "label_en": "Gen Z 2026 aesthetic +12",
            "score": 12.0 if is_aesthetic else 0.0,
            "evidence": f"hook_potential = {vm.get('hook_potential', 'MEDIUM')}",
        },
    ]
    return score, sub_scores


# ─────────────────────────────────────────────────────────────────────────
# Tổng hợp — Opportunity Score + chi tiết chấm điểm hoàn chỉnh
# ─────────────────────────────────────────────────────────────────────────
def calculate_opportunity_score(
    sig: Dict[str, Any],
    profit_margin_pct: float,
    profit_per_unit: float,
    min_margin_pct: float,
    warehouse_match: bool,
    technique_match: bool,
    production_days: int,
    warehouse_label: str,
    techniques: List[str],
    strategy: str = "VIRAL_TREND",
) -> Tuple[float, Dict[str, Any]]:
    """Trả về (total_score, scoring_detail) theo chuẩn PW1."""
    weights = STRATEGY_WEIGHTS.get(strategy, STRATEGY_WEIGHTS["VIRAL_TREND"])

    s_demand, sub_demand = _pillar_demand(sig)
    s_gap, sub_gap = _pillar_gap(sig)
    s_margin, sub_margin = _pillar_margin(profit_margin_pct, profit_per_unit, min_margin_pct)
    s_supply, sub_supply = _pillar_supply(warehouse_match, technique_match, production_days, warehouse_label, techniques)
    s_safety, sub_safety, ip_check = _pillar_safety(sig)
    s_virality, sub_virality = _pillar_virality(sig)

    scores = {
        "demand": s_demand, "gap": s_gap, "margin": s_margin,
        "supply": s_supply, "safety": s_safety, "virality": s_virality,
    }
    subs = {
        "demand": sub_demand, "gap": sub_gap, "margin": sub_margin,
        "supply": sub_supply, "safety": sub_safety, "virality": sub_virality,
    }
    formulas = {
        "demand": ("S = 100·σ(0.40z_g + 0.25z_T + 0.20z_D + 0.15z_V) × M_intent", "S = 100·σ(0.40z_g + 0.25z_T + 0.20z_D + 0.15z_V) × M_intent"),
        "gap": ("S = 0.35·(100−Competition) + 0.35·Opportunity + min(30, N_reviews·10) + Δ_PainMatch", "S = 0.35·(100−Competition) + 0.35·Opportunity + min(30, N_reviews·10) + Δ_PainMatch"),
        "margin": ("S = 0.60·Score_Margin% + 0.40·min(100, Profit$/20·100)", "S = 0.60·Score_Margin% + 0.40·min(100, Profit$/20·100)"),
        "supply": ("S = 0.45·S_Warehouse + 0.30·S_Technique + 0.25·S_SLA", "S = 0.45·S_Warehouse + 0.30·S_Technique + 0.25·S_SLA"),
        "safety": ("Ma trận 3 tầng: Trademark→35 | Celebrity/Movie→60 | Generic→96-100", "3-tier matrix: Trademark→35 | Celebrity/Movie→60 | Generic→96-100"),
        "virality": ("S = 50 + 20·I(Personalized) + 18·I(LED/Laser) + 12·I(GenZ)", "S = 50 + 20·I(Personalized) + 18·I(LED/Laser) + 12·I(GenZ)"),
    }

    total = 0.0
    pillars_detail = []
    for key in ["demand", "gap", "margin", "supply", "safety", "virality"]:
        weight = weights[key]
        contribution = round(scores[key] * weight, 1)
        total += contribution
        label_vi, label_en = PILLAR_LABELS[key]
        pillars_detail.append({
            "key": key,
            "label_vi": label_vi,
            "label_en": label_en,
            "score": round(scores[key], 1),
            "weight": weight,
            "contribution": contribution,
            "formula_vi": formulas[key][0],
            "formula_en": formulas[key][1],
            "sub_scores": subs[key],
        })

    total = round(total, 1)

    # 4.3 Verdict cuối cùng
    if total >= 75.0 and ip_check["tier"] == 3:
        verdict_result, verdict_vi, verdict_en = "GO", "GO — Triển khai ngay", "GO — Launch now"
        reasons_vi = ["Điểm tổng ≥ 75", "Bản quyền sạch 100%", "Biên lãi đủ đệm chi phí quảng cáo"]
        reasons_en = ["Total score ≥ 75", "100% clean IP", "Margin covers ad spend"]
    elif total >= 55.0 and ip_check["tier"] >= 2:
        verdict_result, verdict_vi, verdict_en = "CAUTION", "CAUTION — Thận trọng, cần kiểm tra thêm", "CAUTION — Proceed with checks"
        reasons_vi = ["Điểm tổng ở mức trung bình", "Cần rà soát thêm yếu tố bản quyền/giá"]
        reasons_en = ["Mid-range total score", "Re-check IP/pricing factors"]
    else:
        verdict_result, verdict_vi, verdict_en = "STOP", "STOP — Loại khỏi danh mục", "STOP — Exclude from pipeline"
        reasons_vi = ["Điểm tổng dưới ngưỡng", "Hoặc rủi ro bản quyền cao"]
        reasons_en = ["Total score below threshold", "Or high IP risk"]

    detail = {
        "weights": weights,
        "strategy_preset": strategy,
        "formula_total": "S = Σ w_k · S_k,  Σ w_k = 1.0",
        "pillars": pillars_detail,
        "ip_check": ip_check,
        "verdict": {
            "result": verdict_result,
            "label_vi": verdict_vi,
            "label_en": verdict_en,
            "reasons_vi": reasons_vi,
            "reasons_en": reasons_en,
        },
    }
    return total, detail
