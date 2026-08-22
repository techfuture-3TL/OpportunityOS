"""Headless browser crawler with proxy support."""
from __future__ import annotations

import asyncio
import random
import re
from typing import Any, Dict, List, Optional

from app.core.config import settings


# Proxy configuration - VN datacenter proxies
PROXIES = [
    "http://a1ff22d521c34db8a6fbe0e4d7a028e1-cc-VN-s-l2w9z3nu-ttl-60:1fd5f6634cd11018828fab9a1f39ed83@resi.maskify.su:80",
]

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
]


def _get_proxy() -> str:
    """Get random proxy."""
    return random.choice(PROXIES)


def _get_headers() -> Dict[str, str]:
    """Get random headers."""
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }


async def _init_browser():
    """Initialize playwright browser with proxy."""
    try:
        from playwright.async_api import async_playwright

        proxy = _get_proxy()
        proxy_info = {
            "server": proxy.split("@")[1] if "@" in proxy else proxy,
            "username": proxy.split("@")[0].split(":")[0] if "@" in proxy else None,
            "password": proxy.split("@")[0].split(":")[1] if "@" in proxy and ":" in proxy.split("@")[0] else None,
        }

        # Remove None values
        proxy_info = {k: v for k, v in proxy_info.items() if v}

        pw = await async_playwright().start()
        browser = await pw.chromium.launch(
            headless=True,
            proxy=proxy_info if proxy_info.get("server") else None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        )
        return browser, pw
    except Exception as e:
        print(f"[browser] Init error: {e}")
        return None, None


async def _close_browser(browser, pw):
    """Close browser."""
    if browser:
        await browser.close()
    if pw:
        await pw.stop()


class BrowserCrawler:
    """Base class for browser-based crawlers."""

    name = "browser"
    label = "Browser Crawler"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Override in subclass."""
        raise NotImplementedError


class AmazonBrowserCrawler(BrowserCrawler):
    """Amazon crawler using headless browser."""

    name = "amazon"
    label = "Amazon (Browser)"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Crawl Amazon with headless browser."""
        print(f"[amazon-browser] Searching: {query}")

        browser, pw = await _init_browser()
        if not browser:
            return {"source": "amazon", "success": False, "error": "Browser init failed", "products": []}

        products = []
        context = None

        try:
            context = await browser.new_context(
                user_agent=random.choice(_USER_AGENTS),
                locale="en-US",
            )
            page = await context.new_page()

            # Navigate to Amazon search
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            await page.goto(search_url, wait_until="networkidle", timeout=30000)

            # Wait for results
            await page.wait_for_selector("[data-component-type='s-search-result']", timeout=10000)

            # Extract products
            items = await page.query_selector_all("[data-component-type='s-search-result']")

            for item in items[:limit]:
                try:
                    # Title
                    title_el = await item.query_selector("h2 a span")
                    title = await title_el.inner_text() if title_el else ""

                    # Price
                    price_el = await item.query_selector(".a-price-whole")
                    price_frac_el = await item.query_selector(".a-price-fraction")
                    price = 0.0
                    if price_el:
                        whole = await price_el.inner_text()
                        frac = await price_frac_el.inner_text() if price_frac_el else "00"
                        price = float(f"{whole}.{frac}".replace(",", ""))

                    # Rating
                    rating_el = await item.query_selector(".a-icon-alt")
                    rating = 0.0
                    if rating_el:
                        rating_text = await rating_el.inner_text()
                        rating_match = re.search(r"([\d.]+)", rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))

                    # Reviews
                    reviews_el = await item.query_selector("span.a-size-base-plus")
                    reviews = 0
                    if reviews_el:
                        reviews_text = await reviews_el.inner_text()
                        reviews_match = re.search(r"([\d,]+)", reviews_text.replace(",", ""))
                        if reviews_match:
                            reviews = int(reviews_match.group(1).replace(",", ""))

                    # URL
                    url_el = await item.query_selector("h2 a")
                    url = ""
                    if url_el:
                        url = await url_el.get_attribute("href")
                        url = f"https://www.amazon.com{url}" if url else ""

                    # Estimate sales (1:20 ratio)
                    est_sales = reviews * 20 if reviews > 0 else 0
                    revenue = price * est_sales

                    if title and len(title) > 5:
                        products.append({
                            "source": "amazon",
                            "product_id": url.split("/dp/")[1][:10] if "/dp/" in url else url[-10:],
                            "title": title[:400],
                            "price": round(price, 2),
                            "currency": "USD",
                            "revenue": round(revenue, 2),
                            "quantity_sold": est_sales,
                            "growth_rate": min(200, reviews / 10) if reviews > 0 else 50,
                            "rating": rating,
                            "reviews_count": reviews,
                            "url": url,
                        })

                except Exception as e:
                    continue

            print(f"[amazon-browser] Got {len(products)} products")
            return {"source": "amazon", "success": True, "products": products}

        except Exception as e:
            print(f"[amazon-browser] Error: {e}")
            return {"source": "amazon", "success": False, "error": str(e), "products": products}

        finally:
            if context:
                await context.close()
            await _close_browser(browser, pw)


class EbayBrowserCrawler(BrowserCrawler):
    """eBay crawler using headless browser."""

    name = "ebay"
    label = "eBay (Browser)"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Crawl eBay with headless browser."""
        print(f"[ebay-browser] Searching: {query}")

        browser, pw = await _init_browser()
        if not browser:
            return {"source": "ebay", "success": False, "error": "Browser init failed", "products": []}

        products = []
        context = None

        try:
            context = await browser.new_context(
                user_agent=random.choice(_USER_AGENTS),
                locale="en-US",
            )
            page = await context.new_page()

            # Navigate to eBay sold search
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
            await page.goto(search_url, wait_until="networkidle", timeout=30000)

            # Wait for results
            await page.wait_for_selector(".s-item", timeout=10000)

            # Extract products
            items = await page.query_selector_all(".s-item")

            for item in items[:limit]:
                try:
                    # Title
                    title_el = await item.query_selector(".s-item__title")
                    title = await title_el.inner_text() if title_el else ""

                    # Price
                    price_el = await item.query_selector(".s-item__price")
                    price = 0.0
                    if price_el:
                        price_text = await price_el.inner_text()
                        price_match = re.search(r"[\d,.]+", price_text.replace(",", ""))
                        if price_match:
                            price = float(price_match.group())

                    # Sold count
                    sold_el = await item.query_selector(".s-item__quantitySold")
                    sold = 0
                    if sold_el:
                        sold_text = await sold_el.inner_text()
                        sold_match = re.search(r"([\d,]+)", sold_text.replace(",", ""))
                        if sold_match:
                            sold = int(sold_match.group().replace(",", ""))

                    # URL
                    url_el = await item.query_selector(".s-item__link")
                    url = ""
                    if url_el:
                        url = await url_el.get_attribute("href")

                    revenue = price * sold if sold > 0 else 0

                    if title and len(title) > 5 and "shop on" not in title.lower():
                        products.append({
                            "source": "ebay",
                            "product_id": url.split("/itm/")[1][:10] if "/itm/" in url else url[-10:],
                            "title": title[:400],
                            "price": round(price, 2),
                            "currency": "USD",
                            "revenue": round(revenue, 2),
                            "quantity_sold": sold,
                            "growth_rate": min(200, sold / 5) if sold > 0 else 50,
                            "url": url,
                        })

                except Exception as e:
                    continue

            print(f"[ebay-browser] Got {len(products)} products")
            return {"source": "ebay", "success": True, "products": products}

        except Exception as e:
            print(f"[ebay-browser] Error: {e}")
            return {"source": "ebay", "success": False, "error": str(e), "products": products}

        finally:
            if context:
                await context.close()
            await _close_browser(browser, pw)
