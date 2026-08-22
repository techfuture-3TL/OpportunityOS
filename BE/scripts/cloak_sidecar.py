"""CloakBrowser sidecar - human-like stealth browser service on the HOST.

Anti-detection layers:
  1. CloakBrowser patched Chromium (source-level fingerprint stealth)
  2. humanize=True - human mouse curves / keyboard timing / scroll patterns
  3. Persistent per-domain sessions (cookies survive between fetches -
     cold sessions look like bots; returning sessions look human)
  4. Warm-up visit: homepage first, randomized pacing, slow scroll
  5. Residential proxy (CRAWL_PROXY) - sticky sessions

Run on the host:
    CRAWL_PROXY=http://user:pass@host:port python scripts/cloak_sidecar.py
"""
from __future__ import annotations

import asyncio
import os
import random
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Query  # noqa: E402
from pydantic import BaseModel  # noqa: E402

app = FastAPI(title="CloakBrowser Sidecar", version="2.0.0")

_PROXY = os.getenv("CRAWL_PROXY", "")
_PROXY_VN = os.getenv("CRAWL_PROXY_VN", "")
# Domains routed to the VN proxy / direct VN path (VN sites geo-block foreign IPs)
_DIRECT_DOMAINS = {"shopee.vn", "shopee.sg", "shopee.com.my", "shopee.co.id",
                   "shopee.co.th", "shopee.ph", "shopee.tw", "shopee.com.br",
                   "tiktok.com", "google.com", "google.com.vn"}
_browser = None
_vn_browser = None
_lock = asyncio.Lock()
# per-domain persistent contexts (cookie jars survive between requests)
_contexts: dict = {}
_warmed: set = set()
_ctx_lock = asyncio.Lock()


async def _get_browser():
    global _browser, _vn_browser
    async with _lock:
        from cloakbrowser import launch_async

        if _vn_browser is None:
            if _PROXY_VN:
                _vn_browser = await launch_async(headless=True, humanize=True,
                                                 proxy=_PROXY_VN)
            else:
                # direct = host's own VN residential IP (for VN-geo sites)
                _vn_browser = await launch_async(headless=True, humanize=True)
        if _browser is None:
            if _PROXY:
                _browser = await launch_async(headless=True, humanize=True,
                                              proxy=_PROXY)
            else:
                _browser = _vn_browser
        return _browser


async def _browser_for(url: str):
    host = urlparse(url).netloc.lower()
    if any(host == d or host.endswith("." + d) for d in _DIRECT_DOMAINS):
        global _vn_browser
        if _vn_browser is None:
            from cloakbrowser import launch_async

            kwargs = {"headless": True, "humanize": True}
            if _PROXY_VN:
                kwargs["proxy"] = _PROXY_VN
            _vn_browser = await launch_async(**kwargs)
        return _vn_browser
    return await _get_browser()


# real Chrome 151 client hints cloned from a HAR capture (defeats CF checks)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.services.browser.fingerprints import get_profile as _get_profile  # noqa: E402
from app.services.browser.stealth import STEALTH_JS as _STEALTH_JS  # noqa: E402

_CH151 = _get_profile("chrome151_mac")


async def _make_context(browser, host: str):
    """Context with the real Chrome-151 fingerprint (headers + viewport)."""
    ctx = await browser.new_context(
        user_agent=_CH151["user_agent"],
        viewport=_CH151["viewport"],
        locale="en-US",
        timezone_id=_CH151["timezone_id"],
        extra_http_headers=_CH151.get("headers") or None,
    )
    await ctx.add_init_script(_STEALTH_JS)
    return ctx


async def _human_scroll(page, rounds: int = 3):
    """Human-like scrolling: varied distances, pauses, occasional micro-move."""
    for _ in range(rounds):
        dist = random.randint(400, 1400)
        await page.mouse.wheel(0, dist)
        await asyncio.sleep(random.uniform(0.4, 1.4))


async def _warm_up(page, url: str) -> None:
    """First visit to a domain: browse homepage like a human before the
    actual target page. Cold direct hits to search = bot signal."""
    host = urlparse(url).netloc
    base = f"{urlparse(url).scheme}://{host}/"
    try:
        await page.goto(base, timeout=60000)
        await asyncio.sleep(random.uniform(2.5, 5.5))
        await _human_scroll(page, rounds=2)
    except Exception:
        pass


async def _get_context(browser, url: str):
    host = urlparse(url).netloc
    async with _ctx_lock:
        ctx = _contexts.get(host)
        if ctx is None:
            ctx = await _make_context(browser, host)
            # inject account session cookies when provided (e.g. ETSY_COOKIE
            # from a bought account -> real logged-in session, no challenge)
            site_cookie = os.getenv(f"SIDECAR_COOKIE_{host.split('.')[0].upper()}", "")
            site_cookie = site_cookie or os.getenv("SIDECAR_COOKIES", "")
            if site_cookie:
                try:
                    import json as _json

                    pairs = _json.loads(site_cookie) if site_cookie.startswith("[") \
                        else [{"name": k.strip(), "value": v.strip(), "domain": f".{host}"}
                              for pair in site_cookie.split(";") if "=" in pair
                              for k, v in [pair.split("=", 1)]]
                    await ctx.add_cookies(pairs)
                except Exception:
                    pass
            _contexts[host] = ctx
        return ctx, host


class FetchResponse(BaseModel):
    ok: bool
    html: str = ""
    error: str = ""
    warmed: bool = False


class EvalResponse(BaseModel):
    ok: bool
    result: str = ""
    error: str = ""


@app.get("/eval", response_model=EvalResponse)
async def eval_page(url: str = Query(...), js: str = Query(...),
                    wait: int = Query(3000, ge=0, le=30000)):
    """Load a page then run fetch() INSIDE the page context (same-origin
    cookies + anti-bot tokens) - the trick for SPA APIs (Shopee/TikTok CC).

    Shopee rate-limits sessions (error 90309999): when detected, the domain
    session is dropped and the request retried once with a FRESH cookie jar."""
    import json as _json

    host = urlparse(url).netloc
    try:
        browser = await _browser_for(url)
        context, host = await _get_context(browser, url)
        page = await context.new_page()
        try:
            await page.goto(url, timeout=60000)
            await asyncio.sleep(wait / 1000.0)
            result = await page.evaluate(js)
            text = str(result)
            # shopee session ban -> fresh session + single retry
            if "90309999" in text or '"error"' in text[:300]:
                async with _ctx_lock:
                    _contexts.pop(host, None)
                    _warmed.discard(host)
                try:
                    await context.close()
                except Exception:
                    pass
                await asyncio.sleep(2)
                context, host = await _get_context(browser, url)
                page2 = await context.new_page()
                try:
                    await page2.goto(url, timeout=60000)
                    await asyncio.sleep(wait / 1000.0)
                    result = await page2.evaluate(js)
                    text = str(result)
                finally:
                    await page2.close()
            if isinstance(result, dict):
                text = _json.dumps(result)
            return EvalResponse(ok=True, result=text)
        finally:
            await page.close()
    except Exception as e:
        return EvalResponse(ok=False, error=str(e)[:300])


@app.get("/health")
async def health():
    return {"ok": True, "engine": "cloakbrowser", "sessions": len(_contexts)}


@app.get("/fetch", response_model=FetchResponse)
async def fetch(url: str = Query(...), wait: int = Query(4000, ge=0, le=30000),
                scroll: bool = Query(True)):
    try:
        browser = await _browser_for(url)
        context, host = await _get_context(browser, url)
        page = await context.new_page()
        try:
            warmed = False
            if host not in _warmed:
                await _warm_up(page, url)
                _warmed.add(host)
                warmed = True

            html = await _goto_with_reconnect(page, browser, url, wait, scroll)
            return FetchResponse(ok=True, html=html or "", warmed=warmed)
        finally:
            await page.close()
    except Exception as e:
        return FetchResponse(ok=False, error=str(e)[:300])


async def _goto_with_reconnect(page, browser, url, wait, scroll) -> str:
    """Residential proxies rotate sticky IPs (ttl) - a dead connection means
    the old IP died: relaunch the browser once and retry."""
    global _browser, _contexts, _warmed

    try:
        await page.goto(url, timeout=60000)
    except Exception as e:
        if "ERR_CONNECTION" not in str(e):
            raise
        try:
            await browser.close()
        except Exception:
            pass
        _browser = None
        _contexts.clear()
        _warmed.clear()
        browser = await _browser_for(url)
        context, host = await _get_context(browser, url)
        page = await context.new_page()
        await page.goto(url, timeout=60000)
    await asyncio.sleep((wait / 1000.0) * random.uniform(0.8, 1.3))
    if scroll:
        await _human_scroll(page)
    return await page.content()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("cloak_sidecar:app", host="0.0.0.0", port=8866)
