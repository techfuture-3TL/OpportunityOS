"""Advanced marketplace crawlers using HAR-based approach."""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List

import httpx

# Headers extracted from HAR files
EBAY_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}

AMAZON_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "viewport-width": "1920",
    "viewport-height": "1080",
}


class EbayAdvancedCrawler:
    """eBay crawler using direct HTTP with HAR-extracted headers."""

    name = "ebay"
    label = "eBay"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Crawl eBay search results."""
        print(f"[ebay-adv] Searching: {query}")

        products = []
        proxy = "http://a1ff22d521c34db8a6fbe0e4d7a028e1-cc-VN-s-l2w9z3nu-ttl-60:1fd5f6634cd11018828fab9a1f39ed83@resi.maskify.su:80"

        async with httpx.AsyncClient(
            headers=EBAY_HEADERS,
            timeout=30.0,
            follow_redirects=True,
            proxy=proxy,
        ) as client:
            try:
                # First get cookies from homepage
                await client.get("https://www.ebay.com/")
                await asyncio.sleep(1)

                # Then search with sold items
                search_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&_ipg=60"
                resp = await client.get(search_url)
                html = resp.text

                # Parse items from HTML
                products = cls._parse_items(html, limit)

            except Exception as e:
                print(f"[ebay-adv] Error: {e}")

        print(f"[ebay-adv] Got {len(products)} products")
        return {"source": "ebay", "success": len(products) > 0, "products": products}

    @classmethod
    def _parse_items(cls, html: str, limit: int) -> List[Dict]:
        """Parse eBay items from HTML."""
        products = []

        # Find item IDs and extract data
        item_ids = re.findall(r'ebay\.com/itm/(\d+)', html)
        item_ids = list(dict.fromkeys(item_ids))[:limit]  # Dedupe

        # Find prices
        price_pattern = re.findall(r'<span[^>]*class="[^"]*s-item__price[^"]*"[^>]*>([^<]+)</span>', html)
        # Find sold counts
        sold_pattern = re.findall(r'<span[^>]*>\s*([\d,]+)\s+sold\s*</span>', html, re.IGNORECASE)

        # Find titles using different patterns
        title_pattern = re.findall(r'class="[^"]*s-item__title[^"]*"[^>]*>([^<]+)</span>', html)
        if not title_pattern:
            title_pattern = re.findall(r'class="[^"]*x-item__title[^"]*"[^>]*>([^<]+)</span>', html)

        # Match items by index
        for i, item_id in enumerate(item_ids):
            # Try to find matching data by position
            title_idx = min(i, len(title_pattern) - 1) if title_pattern else 0
            price_idx = min(i, len(price_pattern) - 1) if price_pattern else 0
            sold_idx = min(i, len(sold_pattern) - 1) if sold_pattern else 0

            title = title_pattern[title_idx].strip() if title_pattern else f"eBay Item {item_id}"
            price_str = price_pattern[price_idx].replace('$', '').replace(',', '') if price_pattern else "0"
            sold_str = sold_pattern[sold_idx].replace(',', '') if sold_pattern else "0"

            try:
                price = float(price_str) if price_str.replace('.', '').isdigit() else 0
            except:
                price = 0

            try:
                sold = int(sold_str) if sold_str.isdigit() else 0
            except:
                sold = 0

            revenue = price * sold if sold > 0 else 0

            if title and "shop on ebay" not in title.lower():
                products.append({
                    "source": "ebay",
                    "product_id": item_id,
                    "title": title[:400],
                    "price": round(price, 2),
                    "currency": "USD",
                    "revenue": round(revenue, 2),
                    "quantity_sold": sold,
                    "growth_rate": min(200, sold / 5) if sold > 0 else 50,
                    "url": f"https://www.ebay.com/itm/{item_id}",
                })

        return products


class AmazonAdvancedCrawler:
    """Amazon crawler using internal API approach."""

    name = "amazon"
    label = "Amazon"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Crawl Amazon search results."""
        print(f"[amazon-adv] Searching: {query}")

        products = []
        proxy = "http://a1ff22d521c34db8a6fbe0e4d7a028e1-cc-VN-s-l2w9z3nu-ttl-60:1fd5f6634cd11018828fab9a1f39ed83@resi.maskify.su:80"

        async with httpx.AsyncClient(
            headers=AMAZON_HEADERS,
            timeout=30.0,
            follow_redirects=True,
            proxy=proxy,
        ) as client:
            try:
                # First get cookies
                await client.get("https://www.amazon.com/")
                await asyncio.sleep(1)

                # Try to get search page
                search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}&s=review-rank"
                resp = await client.get(search_url)
                html = resp.text

                products = cls._parse_items(html, limit)

            except Exception as e:
                print(f"[amazon-adv] Error: {e}")

        print(f"[amazon-adv] Got {len(products)} products")
        return {"source": "amazon", "success": len(products) > 0, "products": products}

    @classmethod
    def _parse_items(cls, html: str, limit: int) -> List[Dict]:
        """Parse Amazon items from HTML."""
        products = []

        # Find ASINs
        asins = re.findall(r'data-asin="([A-Z0-9]{10})"', html)
        asins = list(dict.fromkeys(asins))[:limit]

        # Find titles - multiple patterns
        title_patterns = [
            r'class="a-size-medium a-color-base a-text-normal"[^>]*>([^<]+)</span>',
            r'class="[^"]*a-text-normal[^"]*"[^>]*>([^<]+)</span>',
        ]

        titles = []
        for pattern in title_patterns:
            titles = re.findall(pattern, html)
            if titles:
                break

        # Find prices
        price_patterns = [
            r'<span class="a-price-whole">([^<]+)</span>',
            r'class="a-offscreen"[^>]*>\$([\d,.]+)',
        ]

        prices = []
        for pattern in price_patterns:
            prices = re.findall(pattern, html)
            if prices:
                break

        # Find ratings
        ratings = re.findall(r'class="a-icon-alt"[^>]*>([^<]+)</span>', html)

        # Find reviews count
        reviews = re.findall(r'(\d+[\d,]*) ratings?', html, re.IGNORECASE)

        for i, asin in enumerate(asins):
            title_idx = min(i, len(titles) - 1) if titles else 0
            price_idx = min(i, len(prices) - 1) if prices else 0
            rating_idx = min(i, len(ratings) - 1) if ratings else 0
            review_idx = min(i, len(reviews) - 1) if reviews else 0

            title = titles[title_idx].strip() if titles else f"Amazon {asin}"
            price_str = prices[price_idx].replace(',', '') if prices else "0"
            rating_str = ratings[rating_idx] if ratings else "0"
            review_str = reviews[review_idx].replace(',', '') if reviews else "0"

            try:
                price = float(price_str) if price_str.replace('.', '').isdigit() else 0
            except:
                price = 0

            try:
                rating = float(re.search(r'([\d.]+)', rating_str).group(1)) if rating_str else 0
            except:
                rating = 0

            try:
                review_count = int(review_str) if review_str.isdigit() else 0
            except:
                review_count = 0

            # Estimate sales: ~1:20 ratio of reviews to sales
            estimated_sales = review_count * 20
            revenue = price * estimated_sales

            products.append({
                "source": "amazon",
                "product_id": asin,
                "title": title[:400],
                "price": round(price, 2),
                "currency": "USD",
                "revenue": round(revenue, 2),
                "quantity_sold": estimated_sales,
                "growth_rate": min(200, review_count / 10) if review_count > 0 else 50,
                "rating": rating,
                "reviews_count": review_count,
                "url": f"https://www.amazon.com/dp/{asin}",
            })

        return products


class ShopeeCrawler:
    """Shopee crawler for SEA markets."""

    name = "shopee"
    label = "Shopee"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Crawl Shopee search results."""
        print(f"[shopee] Searching: {query}")

        products = []
        proxy = "http://a1ff22d521c34db8a6fbe0e4d7a028e1-cc-VN-s-l2w9z3nu-ttl-60:1fd5f6634cd11018828fab9a1f39ed83@resi.maskify.su:80"

        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            proxy=proxy,
        ) as client:
            try:
                # Shopee API endpoint
                url = f"https://shopee.vn/api/v4/search/search_items?keyword={query}&limit={limit}&newest=0"
                resp = await client.get(url)
                data = resp.json()

                if data.get("items"):
                    for item in data["items"][:limit]:
                        products.append({
                            "source": "shopee",
                            "product_id": str(item.get("itemid", "")),
                            "shopid": item.get("shopid", 0),
                            "title": item.get("title", ""),
                            "price": item.get("price", 0) / 100000,  # VND to USD approx
                            "currency": "VND",
                            "historical_sold": item.get("historical_sold", 0),
                            "stock": item.get("stock", 0),
                            "rating": item.get("rating_star", 0),
                            "image": item.get("image", ""),
                            "url": f"https://shopee.vn/product/-/{item.get('shopid', 0)}/{item.get('itemid', 0)}",
                        })

            except Exception as e:
                print(f"[shopee] Error: {e}")

        print(f"[shopee] Got {len(products)} products")
        return {"source": "shopee", "success": len(products) > 0, "products": products}


class LazadaCrawler:
    """Lazada crawler for SEA markets."""

    name = "lazada"
    label = "Lazada"

    @classmethod
    async def crawl(cls, query: str, limit: int = 30) -> Dict[str, Any]:
        """Crawl Lazada search results."""
        print(f"[lazada] Searching: {query}")

        products = []
        proxy = "http://a1ff22d521c34db8a6fbe0e4d7a028e1-cc-VN-s-l2w9z3nu-ttl-60:1fd5f6634cd11018828fab9a1f39ed83@resi.maskify.su:80"

        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "accept": "application/json",
        }

        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            proxy=proxy,
        ) as client:
            try:
                # Lazada API
                url = f"https://www.lazada.com.ph/catalog?q={query}&_keyori=ss&from=input&spm=a2o4l.searchlist.search.go.279249c3yB3qFL"
                resp = await client.get(url, follow_redirects=True)
                html = resp.text

                # Parse JSON from page
                json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
                if json_match:
                    import json as json_lib
                    data = json_lib.loads(json_match.group(1))
                    # Navigate to products
                    items = data.get("products", {}).get("items", [])
                    for item in items[:limit]:
                        products.append({
                            "source": "lazada",
                            "product_id": str(item.get("itemId", "")),
                            "title": item.get("name", ""),
                            "price": item.get("price", 0),
                            "original_price": item.get("originalPrice", 0),
                            "sales": item.get("sales", 0),
                            "rating": item.get("ratingScore", 0),
                            "url": item.get("productUrl", ""),
                        })

            except Exception as e:
                print(f"[lazada] Error: {e}")

        print(f"[lazada] Got {len(products)} products")
        return {"source": "lazada", "success": len(products) > 0, "products": products}
