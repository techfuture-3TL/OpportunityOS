"""Marketplace search-index fallback tests."""
from __future__ import annotations

import urllib.parse
from typing import Optional

import pytest

from app.services.crawl.search_index import parse_indexed_results


def _result(title: str, target: str, snippet: str = "") -> str:
    wrapped = "//duckduckgo.com/l/?uddg=" + urllib.parse.quote(target, safe="")
    return (
        '<div class="result">'
        f'<a class="result__a" href="{wrapped}">{title}</a>'
        f'<a class="result__snippet">{snippet}</a>'
        "</div>"
    )


@pytest.mark.parametrize(
    ("source", "target", "expected_id"),
    [
        ("ebay", "https://www.ebay.com/itm/184158974024", "184158974024"),
        ("etsy", "https://www.etsy.com/listing/4550987987/insulated-tumbler", "4550987987"),
        ("lazada", "https://www.lazada.vn/products/insulated-tumbler-i3022050983.html", None),
    ],
)
def test_parse_real_marketplace_listing(source: str, target: str, expected_id: Optional[str]):
    html = _result("Insulated Tumbler - Marketplace", target, "Popular listing US $24.99")
    products = parse_indexed_results(html, source, "insulated tumbler", limit=5)

    assert len(products) == 1
    product = products[0]
    assert product["url"] == target
    assert product["price"] == 24.99
    assert product["data_mode"] == "search_index"
    assert product["is_synthetic"] is False
    assert "quantity_sold" in product["estimated_fields"]
    if expected_id:
        assert expected_id in product["product_id"]


def test_filters_ads_and_wrong_marketplace():
    html = _result(
        "Sponsored tumbler",
        "https://duckduckgo.com/y.js?ad_domain=ebay.com",
    ) + _result(
        "Wrong marketplace",
        "https://www.amazon.com/dp/B012345",
    )

    assert parse_indexed_results(html, "etsy", "tumbler") == []


def test_filters_irrelevant_listing_from_matching_marketplace():
    html = _result(
        "2026 Declaration of Independence Quarter Coin",
        "https://www.ebay.com/itm/123456789",
        "Rare collectible coin",
    )

    assert parse_indexed_results(html, "ebay", "bình giữ nhiệt") == []
