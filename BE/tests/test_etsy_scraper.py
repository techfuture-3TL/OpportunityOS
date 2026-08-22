"""Etsy scraper parser tests."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

from app.services.crawlers.etsy_scraper import EtsyScraper, parse_etsy_search

FIXTURE = """
<html><body>
<div data-listing-card-listing-id="1635539031">
  <a href="/listing/1635539031/personalized-christmas-ornament-family-name">
    <h3 class="wt-text-caption v2-listing-card__title wt-text-truncate">Personalized Christmas Ornament Family Name Custom Gift</h3>
  </a>
  <p><span class="currency-symbol">$</span><span class="currency-value">15.99</span></p>
  <img src="https://i.etsystatic.com/27194230/r/il/abc123/456.jpeg">
  <span aria-label="(1,234) reviews">(1,234)</span>
  <input type="hidden" name="rating" value="4.8">
</div>
<div data-listing-card-listing-id="1635539032">
  <a href="/listing/1635539032/halloween-mug">
    <h3 class="wt-text-caption v2-listing-card__title wt-text-truncate">Spooky Halloween Mug Custom Name</h3>
  </a>
  <p><span class="currency-symbol">$</span><span class="currency-value">12.50</span></p>
  <span aria-label="(89) reviews">(89)</span>
</div>
</body></html>
"""


def test_parse_etsy_search_jsonld():
    import json as _json

    items = [
        {"@type": "ListItem", "position": 1, "item": {
            "@type": "Product",
            "name": "Personalized Christmas Ornament Family Name Custom Gift",
            "url": "https://www.etsy.com/listing/1635539031/personalized-christmas-ornament",
            "image": "https://i.etsystatic.com/27194230/r/il/abc123/456.jpeg",
            "brand": {"@type": "Brand", "name": "XmasShop"},
            "offers": {"@type": "Offer", "price": "405000", "priceCurrency": "VND"}}},
        {"@type": "ListItem", "position": 2, "item": {
            "@type": "Product",
            "name": "Spooky Halloween Mug Custom Name",
            "url": "https://www.etsy.com/listing/1635539032/halloween-mug",
            "offers": {"@type": "Offer", "price": "12.50", "priceCurrency": "USD"}}},
    ]
    html = ('<script type="application/ld+json">'
            + _json.dumps({"@context": "x", "@type": "ItemList",
                           "itemListElement": items})
            + "</script>")
    products = parse_etsy_search(html)
    assert len(products) == 2
    p0 = products[0]
    assert p0.external_id == "1635539031"
    assert "Personalized Christmas Ornament" in p0.title
    assert p0.price == round(405000 / 25400.0, 2)  # VND -> USD
    assert p0.url.endswith("/listing/1635539031/personalized-christmas-ornament")
    assert p0.image_url.startswith("https://i.etsystatic.com/")
    assert p0.raw["jsonld"] is True
    assert p0.raw["brand"] == "XmasShop"
    assert products[1].price == 12.50  # USD passthrough


def test_parse_etsy_card_fallback():
    html = ('<div data-listing-id="807920266">'
            '<a aria-label="Glass Chandelier. Murano Glass Lighting." '
            'href="https://www.etsy.com/listing/807920266/glass-chandelier"></a>'
            "</div>")
    products = parse_etsy_search(html)
    assert len(products) == 1
    assert products[0].external_id == "807920266"
    assert "Glass Chandelier" in products[0].title
    assert products[0].raw["card_fallback"] is True


def test_parse_empty():
    assert parse_etsy_search("<html><body>no listings</body></html>") == []


def test_etsy_scraper_no_keys():
    ok, reason = EtsyScraper().status()
    assert ok is True
    assert reason == "ok"
