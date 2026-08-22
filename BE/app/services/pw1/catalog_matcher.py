"""PW1 Catalog Matcher — đường ống 4 khối + auto crawl full 5 sàn + chấm điểm chi tiết."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.models.schemas import (
    OpportunityItem,
    ScoreBreakdown,
    ScoringDetail,
    PillarDetail,
    IpCheckDetail,
    VerdictDetail,
    PricePoint,
    ScoreRationale,
)
from app.services.pw1.database_service import CSVDatabaseService
from app.services.pw1.scoring_engine import calculate_opportunity_score

DATA_DIR = settings.DATA_DIR

CATALOG_KEYWORDS_MAP = {
    "PW-DRINK-TUMB-20OZ": "tumbler",
    "PW-DRINK-MUG-15OZ": "mug, cup, ceramic",
    "PW-APP-HOODIE-FLEECE": "hoodie",
    "PW-APP-TEE-HEAVY": "shirt, tee, apparel",
    "PW-GIFT-ACRYLIC-LIGHT": "acrylic, light, lamp, mirror",
    "PW-HOME-WOOD-PLAQUE": "wood, plaque, sign, frame",
    "PW-HOME-CANVAS-16X24": "canvas, print, poster",
    "PW-PET-LEATHER-COLLAR": "pet, collar, dog, cat, leather",
    "PW-SEASON-ORNAMENT": "ornament, christmas, xmas, holiday",
}


def _load_json(name: str) -> List[Dict[str, Any]]:
    path = DATA_DIR / name
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[pw1] load {name} failed: {e}")
    return []


def get_printway_catalog() -> List[Dict[str, Any]]:
    return _load_json("printway_catalog.json")


def get_seed_market_signals() -> List[Dict[str, Any]]:
    return _load_json("market_signals.json")


# ─────────────────────────────────────────────────────────────────────────
# AUTO CRAWL FULL 5 SÀN
# ─────────────────────────────────────────────────────────────────────────
async def auto_crawl_full(
    query: str,
    max_items_per_source: int = 10,
    timeout_s: float = 22.0,
) -> List[Dict[str, Any]]:
    """Crawl toàn bộ 5 sàn TMĐT tự động, có timeout & fallback an toàn."""
    if settings.CRAWL_DEMO_FALLBACK:
        return []

    try:
        from app.services.crawl.service import CrawlService

        service = CrawlService()
        sources = ["tiktok", "amazon", "ebay", "shopee", "lazada", "etsy"]
        crawl_task = service.crawl(query=query, sources=sources, max_items=max_items_per_source, days=7)
        result = await asyncio.wait_for(crawl_task, timeout=timeout_s)

        products = result.get("all_products", []) or []
        signals = service.products_to_signals(products, query)
        print(f"[pw1] auto crawl: {len(signals)} live signals from {len(result.get('sources', []))} sources")
        return signals
    except asyncio.TimeoutError:
        print(f"[pw1] auto crawl timeout after {timeout_s}s — dùng seed signals")
        return []
    except Exception as e:
        print(f"[pw1] auto crawl failed: {e} — dùng seed signals")
        return []


def crawl_signals_to_pw1(signal: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Chuyển signal từ CrawlService sang schema tín hiệu PW1 (seed-like)."""
    price = float(signal.get("price") or 0.0) or 24.99
    reviews = int(signal.get("reviews_count") or 0)
    growth = float(signal.get("growth_rate") or 0.0) or 55.0

    source_names = {
        "tiktok": "TikTok Shop",
        "amazon": "Amazon",
        "ebay": "eBay",
        "etsy": "Etsy",
        "shopee": "Shopee",
        "lazada": "Lazada",
    }
    raw_source = str(signal.get("source") or "marketplace").lower()
    source_label = source_names.get(raw_source, raw_source.title())

    return {
        "signal_id": signal.get("signal_id", f"SIG-CRAWL-{hashlib.md5(query.encode()).hexdigest()[:8]}"),
        "topic": signal.get("title") or signal.get("topic") or query.title(),
        "keywords": [query.lower()],
        "category": signal.get("category") or "Gifts",
        "target_niche": f"{query.title()} / Custom POD",
        "marketplace_sources": [source_label],
        "demand_metrics": {
            "tiktok_shop_sales_growth_pct": max(20.0, min(200.0, growth)),
            "tiktok_views_growth_pct": max(30.0, growth * 1.4),
            "amazon_monthly_search_vol": int(reviews * 150 + 5000),
            "etsy_trending_rank": 25,
            "google_trends_score": 70.0,
        },
        "ip_safety": {
            "safety_score": 96.0,
            "status": "CLEAN_IP",
            "notes": "Dữ liệu crawl trực tiếp, từ khóa generic",
        },
        "virality_metrics": {
            "virality_score": 80.0,
            "hook_potential": "HIGH" if reviews < 200 else "MEDIUM",
            "visual_wow_factor": "Sản phẩm thật đang bán trên sàn — video phản ứng khắc laser/đèn LED",
        },
        "competitor_analysis": {
            "avg_market_price": price,
            "price_min": round(price * 0.8, 2),
            "price_max": round(price * 1.25, 2),
            "competitor_count": max(2, reviews // 40),
            "top_negative_reviews": [
                "Khách đánh giá 1-3 sao về chất lượng in và giao hàng của sản phẩm đại trà.",
                "Thiếu tùy biến cá nhân hóa cho nhu cầu quà tặng.",
            ],
            "market_gap_description": f"Phiên bản cá nhân hóa cao cấp cho {query.title()} đang thiếu trên sàn.",
        },
        "best_fit_sku": None,
        "raw_csv_row": {
            "buyer_intent": "HIGH",
            "demand": 70.0,
            "competition": 35.0,
            "opportunity": 75.0,
        },
    }


# ─────────────────────────────────────────────────────────────────────────
# KHỐI LỌC
# ─────────────────────────────────────────────────────────────────────────
def _filter_block_1(sig: Dict[str, Any], request: Any) -> Tuple[bool, str]:
    m_cfg = request.market_and_niche

    if m_cfg.categories:
        allowed = [str(c) for c in m_cfg.categories]
        if sig.get("category") not in allowed:
            return False, f"Loại: ngành '{sig.get('category')}' không thuộc danh mục chọn"

    if m_cfg.seed_keywords:
        topic_text = (sig.get("topic", "") + " " + " ".join(sig.get("keywords", []) or [])).lower()
        matched = any(kw.strip().lower() in topic_text for kw in m_cfg.seed_keywords if kw.strip())
        if not matched:
            return False, f"Loại: không chứa từ khóa {m_cfg.seed_keywords}"

    dm = sig.get("demand_metrics", {}) or {}
    growth = float(dm.get("tiktok_shop_sales_growth_pct") or 0.0)
    if growth < float(m_cfg.min_sales_growth_pct or 0.0):
        return False, f"Loại: tăng trưởng {growth:g}% < {m_cfg.min_sales_growth_pct:g}%"

    return True, "Hợp lệ Khối 1"


def _filter_block_2(
    sig: Dict[str, Any], sku_info: Dict[str, Any], request: Any
) -> Tuple[bool, str, Dict[str, float]]:
    f_cfg = request.financials
    base_cost = float(sku_info.get("base_cost", 0.0))

    if f_cfg.max_base_cogs_cap and base_cost > float(f_cfg.max_base_cogs_cap):
        return False, f"Loại: giá phôi ${base_cost} vượt trần ${f_cfg.max_base_cogs_cap}", {}

    market_avg = float((sig.get("competitor_analysis", {}) or {}).get("avg_market_price", base_cost * 3.0))
    suggested = market_avg
    if f_cfg.target_retail_price_min:
        suggested = max(suggested, float(f_cfg.target_retail_price_min))
    if f_cfg.target_retail_price_max:
        suggested = min(suggested, float(f_cfg.target_retail_price_max))
    suggested = round(max(suggested, base_cost + 3.0), 2)

    profit_per_unit = round(suggested - base_cost, 2)
    margin_pct = round((profit_per_unit / suggested) * 100.0, 1) if suggested else 0.0

    if margin_pct < float(f_cfg.min_profit_margin_pct or 0.0):
        return False, f"Loại: biên lãi {margin_pct}% < {f_cfg.min_profit_margin_pct}%", {}

    return True, "Hợp lệ Khối 2", {
        "base_cost": base_cost,
        "suggested_price": suggested,
        "profit_per_unit": profit_per_unit,
        "profit_margin_pct": margin_pct,
    }


def _filter_block_3(
    sku_info: Dict[str, Any], request: Any
) -> Tuple[bool, str, bool, bool]:
    s_cfg = request.supply_chain

    warehouse_match = True
    if s_cfg.preferred_warehouse and str(s_cfg.preferred_warehouse).upper() != "ANY":
        target_wh = str(s_cfg.preferred_warehouse).upper()
        available = [str(w).upper() for w in (sku_info.get("warehouses") or [])]
        if target_wh not in available:
            warehouse_match = False

    technique_match = True
    if s_cfg.allowed_techniques:
        allowed = [str(t).upper() for t in s_cfg.allowed_techniques]
        sku_techs = [str(t).upper() for t in (sku_info.get("techniques") or [])]
        if not any(tech in allowed for tech in sku_techs):
            return False, f"Loại: kỹ thuật in không khớp ({sku_techs})", warehouse_match, False

    prod_days = int(sku_info.get("production_days", 3))
    if s_cfg.max_production_days and prod_days > int(s_cfg.max_production_days):
        return False, f"Loại: SLA {prod_days} ngày vượt mức cho phép", warehouse_match, technique_match

    return True, "Hợp lệ Khối 3", warehouse_match, technique_match


# ─────────────────────────────────────────────────────────────────────────
# PRICE CHART 6 THÁNG (deterministic)
# ─────────────────────────────────────────────────────────────────────────
def _price_chart(
    sig: Dict[str, Any], suggested: float, base_cost: float
) -> List[Dict[str, Any]]:
    comp = sig.get("competitor_analysis", {}) or {}
    price_min = float(comp.get("price_min") or suggested * 0.8)
    price_max = float(comp.get("price_max") or suggested * 1.25)

    seed = int(hashlib.md5((sig.get("topic") or "x").encode()).hexdigest()[:6], 16)
    months = []
    now = datetime.utcnow()
    market_avg = price_min
    for i in range(6):
        month_dt = now - timedelta(days=30 * (5 - i))
        label = f"T{month_dt.month}"
        drift = math.sin((seed % 7) + i * 1.2) * (price_max - price_min) * 0.18
        market_avg = min(price_max, max(price_min, market_avg + drift + (price_max - price_min) * 0.04))
        months.append({
            "month": label,
            "market_avg": round(market_avg, 2),
            "cogs": round(base_cost, 2),
            "suggested_price": round(suggested, 2),
        })
    return months


# ─────────────────────────────────────────────────────────────────────────
# MATCH SKU — giải thích vì sao khớp
# ─────────────────────────────────────────────────────────────────────────
def _match_sku_for_signal(sig: Dict[str, Any], catalog_map: Dict[str, Dict[str, Any]]) -> Optional[str]:
    explicit = sig.get("best_fit_sku")
    if explicit and explicit in catalog_map:
        return explicit

    topic = (sig.get("topic") or "").lower()
    for sku, needles in CATALOG_KEYWORDS_MAP.items():
        if sku in catalog_map and any(n in topic for n in needles.split(", ")):
            return sku
    return None


# ─────────────────────────────────────────────────────────────────────────
# PIPELINE CHÍNH
# ─────────────────────────────────────────────────────────────────────────
async def match_opportunities(request: Any) -> List[OpportunityItem]:
    catalog = get_printway_catalog()
    catalog_map = {item["sku"]: item for item in catalog}

    signals: List[Dict[str, Any]] = []
    if str(request.data_source).upper() != "MARKET_SIGNALS":
        signals.extend(CSVDatabaseService.load_database_records())
    if str(request.data_source).upper() != "DATABASE_CSV":
        signals.extend(get_seed_market_signals())

    # AUTO CRAWL FULL — ưu tiên dữ liệu live từ 5 sàn cho từ khóa đang tìm
    query = " ".join(request.market_and_niche.seed_keywords or []) or request.market_and_niche.target_brand or ""
    if query:
        live_signals = await auto_crawl_full(query)
        signals.extend(crawl_signals_to_pw1(s, query) for s in live_signals)

    qualified: List[OpportunityItem] = []
    seen_ids = set()

    for sig in signals:
        b1_ok, _ = _filter_block_1(sig, request)
        if not b1_ok:
            continue

        matched_sku = _match_sku_for_signal(sig, catalog_map)
        if not matched_sku:
            continue
        sku_info = catalog_map[matched_sku]

        b2_ok, _, fin = _filter_block_2(sig, sku_info, request)
        if not b2_ok:
            continue

        b3_ok, _, warehouse_match, technique_match = _filter_block_3(sku_info, request)
        if not b3_ok:
            continue

        total_score, detail = calculate_opportunity_score(
            sig=sig,
            profit_margin_pct=fin["profit_margin_pct"],
            profit_per_unit=fin["profit_per_unit"],
            min_margin_pct=float(request.financials.min_profit_margin_pct or 0.0),
            warehouse_match=warehouse_match,
            technique_match=technique_match,
            production_days=int(sku_info.get("production_days", 3)),
            warehouse_label=str(request.supply_chain.preferred_warehouse or "ANY"),
            techniques=list(sku_info.get("techniques") or []),
            strategy=str(request.strategy.preset or "VIRAL_TREND"),
        )

        comp = sig.get("competitor_analysis", {}) or {}
        dm = sig.get("demand_metrics", {}) or {}
        vm = sig.get("virality_metrics", {}) or {}
        ip = sig.get("ip_safety", {}) or {}

        score_rationales = ScoreRationale(
            demand=_rationale_vi("demand", detail),
            gap=_rationale_vi("gap", detail),
            margin=_rationale_vi("margin", detail),
            supply=_rationale_vi("supply", detail),
            safety=_rationale_vi("safety", detail),
            virality=_rationale_vi("virality", detail),
        )

        topic = sig.get("topic") or "Custom Product"
        suggested = fin["suggested_price"]

        opp_id = sig.get("signal_id") or f"OPP-{hashlib.md5(topic.encode()).hexdigest()[:8]}"
        if opp_id in seen_ids:
            continue
        seen_ids.add(opp_id)

        qualified.append(OpportunityItem(
            id=opp_id,
            signal_id=sig.get("signal_id", opp_id),
            title=topic,
            name=topic,
            category=sig.get("category", "Gifts"),
            niche=sig.get("target_niche", ""),
            target_niche=sig.get("target_niche", ""),
            opportunity_score=total_score,
            score_breakdown=ScoreBreakdown(
                demand_growth=_pillar_score(detail, "demand"),
                market_gap=_pillar_score(detail, "gap"),
                profit_margin=_pillar_score(detail, "margin"),
                supply_feasibility=_pillar_score(detail, "supply"),
                ip_safety=_pillar_score(detail, "safety"),
                tiktok_virality=_pillar_score(detail, "virality"),
            ),
            score_rationales=score_rationales,
            scoring_detail=detail,
            price_chart_data=[PricePoint(**p) for p in _price_chart(sig, suggested, fin["base_cost"])],
            price_min=float(comp.get("price_min") or suggested * 0.8),
            price_max=float(comp.get("price_max") or suggested * 1.25),
            matched_sku=matched_sku,
            matched_product_name=sku_info.get("name", "Printway blank"),
            base_cost=fin["base_cost"],
            suggested_price=suggested,
            profit_margin_pct=fin["profit_margin_pct"],
            profit_per_unit=fin["profit_per_unit"],
            trend_velocity=f"+{dm.get('tiktok_shop_sales_growth_pct', 0):g}% sales growth TikTok Shop",
            key_pain_point_solved=comp.get("market_gap_description", "Giải quyết nỗi đau khách hàng của đối thủ"),
            negative_reviews_summary=list(comp.get("top_negative_reviews", [])),
            ip_safety_status=f"{ip.get('status', 'CLEAN_IP')} ({ip.get('safety_score', 96.0):g}/100) — {ip.get('notes', '')}",
            virality_hook_rating=f"Potential: {vm.get('hook_potential', 'HIGH')} ({vm.get('virality_score', 85.0):g}/100) — {vm.get('visual_wow_factor', '')}",
            ai_design_prompt=_ai_prompt(topic, sku_info),
            tiktok_hooks=[
                f"Nếu bạn đang tìm {topic.lower()} thực sự xịn, đừng mua bản đại trà rẻ tiền…",
                f"Chúng tôi sửa đúng lỗi #1 khách phàn nàn về {sig.get('keywords', ['sản phẩm này'])[0]}!",
                f"Bí mật khiến chiếc {sku_info.get('name', 'sản phẩm')} tùy chỉnh này viral toàn TikTok Shop tuần này.",
            ],
            target_audience=sig.get("target_niche", "E-commerce shoppers"),
            brand_reference=request.market_and_niche.target_brand or None,
            marketplace_sources=list(sig.get("marketplace_sources", ["TikTok Shop", "Amazon", "Etsy"])),
            source=str(sig.get("source") or "csv"),
        ))

    qualified.sort(key=lambda x: x.opportunity_score, reverse=True)
    return qualified[: int(request.limit or 20)]


def _pillar_score(detail: Dict[str, Any], key: str) -> float:
    for pillar in detail.get("pillars", []):
        if pillar["key"] == key:
            return float(pillar["score"])
    return 0.0


def _rationale_vi(key: str, detail: Dict[str, Any]) -> str:
    for pillar in detail.get("pillars", []):
        if pillar["key"] == key:
            sub = " · ".join(
                f"{s['label_vi']} ({s['score']:g})" for s in pillar.get("sub_scores", [])
            )
            return f"{pillar['label_vi']} {pillar['score']:g}đ: {sub}"
    return ""


def _ai_prompt(topic: str, sku_info: Dict[str, Any]) -> str:
    name = sku_info.get("name", "")
    if "Tumbler" in name:
        return f"Vintage retro engraved emblem cho {topic}, typography banner sạch cho tên cầu thủ, vector monochrome laser-engraving --ar 1:1"
    if "Acrylic" in name or "Mirror" in topic:
        return f"Glowing warm holographic aesthetic illustration cho {topic}, line art tương phản cao --ar 1:1"
    if "Mug" in name:
        return f"Cute festive aesthetic illustration cho {topic}, sublimation wrap 300 DPI vector --ar 1:1"
    if "T-Shirt" in name or "Hoodie" in name:
        return f"Retro vintage wash streetwear graphic cho {topic}, distressed halftone, vector DTG --ar 3:4"
    if "Leather" in name:
        return f"Deep-etched brass nameplate design cho {topic} với mountain silhouette, typography cá nhân hóa --ar 1:1"
    return f"Professional vector concept art cho {topic}, trending TikTok Shop 2026, print-ready --ar 1:1"
