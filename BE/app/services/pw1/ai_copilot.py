"""PW1 AI Copilot — sinh Product Brief bằng DeepSeek, fallback template chuẩn."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings
from app.services.pw1.catalog_matcher import get_printway_catalog, get_seed_market_signals
from app.services.pw1.database_service import CSVDatabaseService


def call_deepseek_llm(system_prompt: str, user_prompt: str) -> Optional[str]:
    if not settings.DEEPSEEK_API_KEY:
        return None
    url = f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
    }
    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        print(f"[DeepSeek Error] HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"[DeepSeek Connection Error]: {e}")
    return None


def _find_signal(opportunity_id: str) -> Optional[Dict[str, Any]]:
    for sig in get_seed_market_signals():
        if sig.get("signal_id") == opportunity_id:
            return sig
    for sig in CSVDatabaseService.load_database_records():
        if sig.get("signal_id") == opportunity_id:
            return sig
    return None


def generate_product_brief(opportunity_id: str, custom_notes: Optional[str] = None) -> Dict[str, Any]:
    signals = get_seed_market_signals() + CSVDatabaseService.load_database_records()
    catalog_map = {item["sku"]: item for item in get_printway_catalog()}

    target_sig = _find_signal(opportunity_id) or (signals[0] if signals else {})
    sku_info = catalog_map.get(target_sig.get("best_fit_sku", ""), {})
    base_cost = float(sku_info.get("base_cost", 8.0))
    suggested_price = float((target_sig.get("competitor_analysis", {}) or {}).get("avg_market_price", 28.99))
    profit = round(suggested_price - base_cost, 2)
    margin = round((profit / suggested_price) * 100.0, 1) if suggested_price else 65.0
    title = target_sig.get("topic", "Winning Product Opportunity")

    system_prompt = (
        "Bạn là Lead E-commerce Product Strategist & R&D AI Copilot cho Printway "
        "(nền tảng Print-on-Demand & Fulfillment toàn cầu). Từ tín hiệu thị trường và phôi xưởng Printway, "
        "hãy tạo một Product Opportunity Brief hành động được. "
        "Trả VỀ DUY NHẤT một JSON hợp lệ (không markdown, không backticks) với các khóa: "
        "executive_summary (string), target_buyer_persona (string), "
        "ai_design_prompts (list 2-3 prompt Midjourney/Flux vector), "
        "tiktok_marketing_plan (list 3-4 giai đoạn), "
        "tiktok_hooks (list 3 hook video), launch_checklist (list 5 bước)."
    )

    user_prompt = (
        f"Product Topic: {title}\nCategory: {target_sig.get('category')}\nNiche: {target_sig.get('target_niche')}\n"
        f"Printway SKU: {sku_info.get('sku')} ({sku_info.get('name')})\n"
        f"COGS: ${base_cost}\nGiá bán lẻ đề xuất: ${suggested_price}\nBiên lãi: {margin}%\n"
        f"Review tiêu cực đối thủ: {json.dumps((target_sig.get('competitor_analysis', {}) or {}).get('top_negative_reviews', []))}\n"
        f"Market Gap: {(target_sig.get('competitor_analysis', {}) or {}).get('market_gap_description')}\n"
        f"Ghi chú R&D: {custom_notes or 'Không có'}"
    )

    ai_response = call_deepseek_llm(system_prompt, user_prompt)
    parsed: Dict[str, Any] = {}
    if ai_response:
        try:
            parsed = json.loads(ai_response)
        except Exception as e:
            print(f"[DeepSeek JSON Parse Error]: {e}")

    return {
        "opportunity_id": opportunity_id,
        "title": f"Actionable Product Brief: {title}",
        "executive_summary": parsed.get("executive_summary") or (
            f"Dựa trên dữ liệu thị trường thời gian thực từ TikTok Shop & Amazon, '{title}' là sản phẩm tiềm năng "
            f"chiến thắng. Dùng phôi {sku_info.get('name', 'Printway')} ({sku_info.get('sku', '')}) để khắc phục lỗi đối thủ "
            f"và đạt biên lãi {margin}%."
        ),
        "target_buyer_persona": parsed.get("target_buyer_persona") or (
            f"{target_sig.get('target_niche', 'Khách TMĐT')} có thu nhập khả dụng cao, thích quà tặng và cá nhân hóa thẩm mỹ."
        ),
        "product_specifications": {
            "Printway SKU": sku_info.get("sku", "PW-SKU"),
            "Product Name": sku_info.get("name", "Custom Printway Product"),
            "Material": sku_info.get("description", "Chất liệu cao cấp"),
            "Craft Technique": ", ".join(sku_info.get("techniques", ["UV_PRINT"])),
            "Production SLA": f"{sku_info.get('production_days', 2)} ngày làm việc",
            "Warehouse Fulfillment": ", ".join(sku_info.get("warehouses", ["US"])),
        },
        "financial_model": {
            "base_cost_cogs": base_cost,
            "suggested_retail_price": suggested_price,
            "gross_profit_per_unit": profit,
            "profit_margin_percentage": margin,
            "projected_break_even_units": round(1000.0 / max(profit, 1.0), 1),
        },
        "ai_design_prompts": parsed.get("ai_design_prompts") or [
            f"Masterpiece vector artwork cho {title}, trending aesthetic Etsy 2026, typography sạch 'EST. [NĂM]' hoặc '[TÊN KHÁCH]', tương phản cao phù hợp {', '.join(sku_info.get('techniques', []))} --ar 1:1",
            f"Minimalist vintage emblem illustration cho {title}, monochrome laser engraving, đen trên nền trắng tinh, svg quality --v 6.0",
        ],
        "tiktok_marketing_plan": parsed.get("tiktok_marketing_plan") or [
            "Giai đoạn 1 (Ngày 1-3): Seed 15 mẫu cho micro-creator kèm khắc tên riêng.",
            "Giai đoạn 2 (Ngày 4-7): Chạy 3 UGC hooks tập trung điểm đau đối thủ ('Vì sao bản khác hỏng, bản mình bền').",
            "Giai đoạn 3 (Ngày 8-14): Scale TikTok Shop Spark Ads trên video creator tốt nhất.",
        ],
        "tiktok_hooks": parsed.get("tiktok_hooks") or [
            f"Nếu bạn đang tìm {title.lower()} xịn, đừng mua bản đại trà rẻ tiền…",
            f"Chúng tôi sửa đúng lỗi #1 khách phàn nàn về {target_sig.get('keywords', ['sản phẩm này'])[0]}!",
            f"Bí mật khiến chiếc {sku_info.get('name', 'sản phẩm')} tùy chỉnh này viral toàn TikTok Shop.",
        ],
        "launch_checklist": parsed.get("launch_checklist") or [
            f"Kết nối SKU {sku_info.get('sku')} vào TikTok Shop & Shopify.",
            "Bật trường cá nhân hóa động (Tên / Năm / Text).",
            "Sinh artwork mẫu bằng prompt Midjourney/Flux đã cho.",
            "Đặt 1 mẫu vật lý từ kho US Printway để quay video.",
            f"Ra mắt với giá bán tối thiểu ${suggested_price}.",
        ],
    }
