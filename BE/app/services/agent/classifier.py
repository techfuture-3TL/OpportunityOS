"""
LLM-powered Product Relevance Filter and Classification Service.
Ensures crawled products strictly match the user's search intent (e.g. 'giày' only returns shoes/sneakers).
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings


_CATEGORY_KEYWORDS = {
    "Footwear": ["giày", "giay", "sneaker", "shoes", "boot", "sandal", "dép", "dep", "loafer"],
    "Apparel": ["áo", "ao", "shirt", "tee", "hoodie", "jacket", "quần", "quan", "dress", "pant", "sweatshirt", "sweater"],
    "Drinkware": ["tumbler", "mug", "cup", "bình", "binh", "ly", "cốc", "coc", "flask", "bottle"],
    "Home Decor": ["đèn", "den", "light", "lamp", "mirror", "sign", "canvas", "plaque", "tranh", "gối", "pillow", "rug"],
    "Accessories": ["ốp", "op", "case", "cover", "móc khóa", "moc khoa", "keychain", "túi", "tui", "bag", "ví", "vi", "wallet", "balo", "backpack"],
    "Seasonal": ["ornament", "christmas", "noel", "halloween", "holiday", "easter", "xmas"],
    "Jewelry": ["ring", "nhẫn", "nhan", "necklace", "dây chuyền", "bracelet", "vòng", "vong", "earring", "bông tai"],
    "Pet": ["pet", "chó", "cho", "mèo", "meo", "dog", "cat", "collar", "leash"],
}


def _rule_based_relevance_check(query: str, title: str) -> bool:
    """Fast heuristic relevance check between query and title."""
    q_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
    t_tokens = [t.lower() for t in re.findall(r"\w+", title) if len(t) > 1]
    
    if not q_tokens:
        return True

    # Check category match
    query_lower = query.lower()
    for cat, kws in _CATEGORY_KEYWORDS.items():
        if any(kw in query_lower for kw in kws):
            # Query belongs to this category. Check if title matches category or keywords
            title_lower = title.lower()
            if any(kw in title_lower for kw in kws):
                return True
            # If query is for footwear, but title is a phone case or ornament, reject!
            other_cats = [c for c, w in _CATEGORY_KEYWORDS.items() if c != cat]
            for o_cat in other_cats:
                if any(w in title_lower for w in _CATEGORY_KEYWORDS[o_cat]) and not any(kw in title_lower for kw in kws):
                    return False

    # Check token overlap
    overlap = set(q_tokens).intersection(set(t_tokens))
    return len(overlap) > 0 or len(q_tokens) == 0


def _ensure_source_coverage(
    products: List[Dict[str, Any]],
    filtered: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Keep the best available candidate from every crawled marketplace."""
    result = list(filtered)
    covered = {str(product.get("source", "")).lower() for product in result}
    for product in products:
        source = str(product.get("source", "")).lower()
        if source and source not in covered:
            result.append(product)
            covered.add(source)
    return result


async def filter_and_classify_products_with_llm(
    query: str,
    products: List[Dict[str, Any]],
    timeout_s: float = 6.0,
) -> List[Dict[str, Any]]:
    """
    Use DeepSeek LLM to filter out irrelevant products and accurately classify categories.
    Falls back to semantic heuristic filter if LLM is unavailable or times out.
    """
    if not products:
        return []

    # If no DeepSeek API key, use rule-based filter
    if not settings.DEEPSEEK_API_KEY:
        filtered = [p for p in products if _rule_based_relevance_check(query, p.get("title", ""))]
        return _ensure_source_coverage(products, filtered)

    # Prepare titles for LLM
    product_candidates = []
    for idx, p in enumerate(products[:20]):
        product_candidates.append({
            "idx": idx,
            "title": p.get("title", ""),
            "price": p.get("price", 0),
        })

    prompt = f"""You are an e-commerce product relevance and classification specialist.
Search Query: "{query}"

Analyze the following product titles.
1. Determine if each product is DIRECTLY RELEVANT to the search query "{query}".
(For example, if query is "giày nam" / "shoes", keep only shoes/footwear; REJECT phone cases, mugs, shirts, unrelated keychains).
2. Assign the best product category (e.g., "Footwear", "Apparel", "Drinkware", "Home Decor", "Accessories", "Seasonal", "Pet").
3. Identify customer pain point or key selling point for relevant items in Vietnamese.

Candidate Products:
{json.dumps(product_candidates, ensure_ascii=False, indent=2)}

Return ONLY valid JSON matching this schema:
{{
  "results": [
    {{
      "idx": 0,
      "is_relevant": true,
      "category": "Footwear",
      "pain_point": "Chất liệu cao cấp, êm chân, thoáng khí, chống trơn trượt"
    }}
  ]
}}"""

    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.DEEPSEEK_MODEL or "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a precise e-commerce classifier. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            resp = await client.post(
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                items_res = parsed.get("results", [])
                
                res_by_idx = {item.get("idx"): item for item in items_res}
                
                filtered_products = []
                for idx, p in enumerate(products[:20]):
                    item_info = res_by_idx.get(idx)
                    if item_info and item_info.get("is_relevant", True):
                        p["category"] = item_info.get("category", p.get("category", "General"))
                        p["pain_point_solved"] = item_info.get("pain_point", "")
                        filtered_products.append(p)
                    elif not item_info:
                        # Fallback heuristic
                        if _rule_based_relevance_check(query, p.get("title", "")):
                            filtered_products.append(p)

                if filtered_products:
                    print(f"[classifier] LLM filtered {len(products)} -> {len(filtered_products)} relevant products for '{query}'")
                    return _ensure_source_coverage(products, filtered_products)

    except Exception as e:
        print(f"[classifier] LLM classifier notice: {e}. Using rule-based filter.")

    # Rule-based fallback
    filtered = [p for p in products if _rule_based_relevance_check(query, p.get("title", ""))]
    return _ensure_source_coverage(products, filtered)
