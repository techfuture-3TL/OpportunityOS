"""Scraper parser tests - real saved HTML from live eBay SRP."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

import pytest

from app.services.crawlers.amazon_scraper import (AmazonScraper,
                                                  parse_search_html as parse_amazon)
from app.services.crawlers.ebay_scraper import (EbayScraper,
                                                parse_search_html as parse_ebay)

EBAY_FIXTURE = """
<html><body>
<div class=srp-river>
<li class="s-card s-card--horizontal" data-viewport='{}' data-listingid="318603921761">
  <a class="s-card__link image-treatment" href="https://www.ebay.com/itm/318603921761"><img src="https://i.ebayimg.com/images/g/SWcAAeSwxFVqiAol/s-l500.jpg"></a>
  <div class="su-card-container__attributes__primary">
    <span class="su-styled-text primary bold large-1 s-card__title"> Personalized Bookshop Mug Spooky Reads Ceramic Coffee Halloween Gift Opens in a new window or tab Brand New </span>
  </div>
  <div class=su-card-container__attributes__primary>
    <span class="su-styled-text primary bold large-1 s-card__price">$20.00</span>
  </div>
  <div class=s-card__footer--row><span>Free shipping</span></div>
</li>
<li class="s-card s-card--horizontal" data-listingid="296931284300">
  <a class="s-card__link image-treatment" href="https://www.ebay.com/itm/296931284300"><img src="https://i.ebayimg.com/images/g/c9cAAeSwAbdqXG1V/s-l500.jpg"></a>
  <span class="s-card__title"> Halloween Witch Mug Set 11oz Ceramic Coffee Cup Gift Opens in a new window or tab Brand New </span>
  <span class="s-card__price">$14.99</span>
  <span>1,254 sold</span>
</li>
</div>
</body></html>
"""


def test_ebay_parse_titles():
    products = parse_ebay(EBAY_FIXTURE)
    assert len(products) == 2
    assert products[0].external_id == "318603921761"
    assert "Bookshop Mug" in products[0].title
    assert products[0].price == 20.00
    assert products[0].url == "https://www.ebay.com/itm/318603921761"
    assert "ebayimg" in products[0].image_url


def test_ebay_parse_sold():
    products = parse_ebay(EBAY_FIXTURE)
    assert products[1].quantity_sold == 1254
    assert products[1].revenue == round(14.99 * 1254, 2)
    assert products[1].raw["sold_price"] is True


def test_ebay_empty_html():
    assert parse_ebay("<html><body>no results</body></html>") == []


AMAZON_FIXTURE = """
<div data-asin="B0ABCD1234" data-component-type="s-search-result" class="s-result-item">
  <h2 class="a-size-mini"><span>Ceramic Halloween Mug Set of 4, 15oz Spooky Coffee Cups</span></h2>
  <span class="a-price"><span class="a-offscreen">$25.99</span></span>
  <span class="a-icon-alt">4.6 out of 5 stars</span>
  <span aria-label="1,432 ratings">1,432</span>
  <img class="s-image" src="https://m.media-amazon.com/images/I/71xyz.jpg">
</div>
<div data-asin="B0WXYZ9876" data-component-type="s-search-result" class="s-result-item">
  <h2 class="a-size-mini"><span>Halloween Glow in the Dark Mug</span></h2>
  <span class="a-price"><span class="a-offscreen">$12.50</span></span>
  <span class="a-icon-alt">4.2 out of 5 stars</span>
  <span aria-label="89 ratings">89</span>
  <img class="s-image" src="https://m.media-amazon.com/images/I/71abc.jpg">
</div>
"""


def test_amazon_parse():
    products = parse_amazon(AMAZON_FIXTURE)
    assert len(products) == 2
    assert products[0].external_id == "B0ABCD1234"
    assert "Halloween Mug" in products[0].title
    assert products[0].price == 25.99
    assert products[0].rating == 4.6
    assert products[0].reviews_count == 1432
    assert products[0].url == "https://www.amazon.com/dp/B0ABCD1234"
    assert "m.media-amazon.com" in products[0].image_url


def test_scrapers_need_no_keys():
    assert AmazonScraper().status() == (True, "ok")
    assert EbayScraper().status() == (True, "ok")
