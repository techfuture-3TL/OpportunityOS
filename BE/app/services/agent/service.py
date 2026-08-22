"""PW1 AI Agent - Market Intelligence Engine.

Flow: Query -> Crawl Realtime -> In-memory Signals -> Score -> Report
NO PERSISTENCE - Data flows through memory only.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.models.schemas import (
    AgentReport,
    DataSource,
    ForecastDay,
    ForecastReport,
    InsightReport,
    KeywordReport,
    ProductReport,
    RecommendationReport,
    TimeWindow,
)
from app.services.crawl.service import CrawlService
from app.services.scoring.service import ScoringService


class AgentService:
    """
    PW1 Market Intelligence Agent.

    NO FILE STORAGE, NO DATABASE PERSISTENCE.
    All data flows through memory only.
    Job metadata goes to Supabase.
    """

    def __init__(self):
        self.crawl_service = CrawlService()
        self.scoring_service = ScoringService()

    async def analyze(
        self,
        query: str,
        window: TimeWindow = TimeWindow.DAY_30,
        data_source: DataSource = DataSource.ALL,
        limit: int = 10,
        sources: Optional[List[str]] = None,
        deep: bool = True,
    ) -> AgentReport:
        """
        Analyze query: Crawl -> Score -> Report.
        All in memory, no persistence.
        """
        trace = []
        start_time = time.time()
        trace.append(f"[{_iso_now()}] Starting: {query}")

        # Map window to days
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365, "all": 365}
        days = days_map.get(window.value, 30)

        # Determine sources
        if data_source == DataSource.TIKTOK_SHOP:
            sources = ["tiktok"]
        elif sources:
            pass
        else:
            sources = ["tiktok"] if settings.has_kalodata_key else ["amazon", "ebay"]

        trace.append(f"[{_iso_now()}] Sources: {sources}, window: {days}d")

        # 1. CRAWL REALTIME - data stays in memory
        crawl_result = await self.crawl_service.crawl(
            query=query,
            sources=sources,
            max_items=limit,
            days=days,
        )

        # Convert products to signals IN MEMORY with LLM classification
        products = crawl_result.get("all_products", [])
        
        # LLM Relevance & Category Filtering
        from app.services.agent.classifier import filter_and_classify_products_with_llm
        classified_products = await filter_and_classify_products_with_llm(query, products)
        if classified_products:
            products = classified_products

        signals = self.crawl_service.products_to_signals(products, query)

        trace.append(f"[{_iso_now()}] {len(signals)} relevant signals classified")

        # 2. SCORE OPPORTUNITIES
        opportunities = self.scoring_service.get_top_opportunities(
            signals, limit=limit, min_score=35.0
        )
        trace.append(f"[{_iso_now()}] {len(opportunities)} scored with 6-pillar rationales")

        # 3. GENERATE REPORT
        keywords = self._extract_keywords(signals, query)
        product_reports = self._extract_products(signals)
        insights = self._generate_insights(signals, opportunities)
        forecast = self._generate_forecast(signals, days)
        recommendations = self._generate_recommendations(opportunities)
        summary = self._build_summary(query, opportunities, insights, forecast)

        elapsed = time.time() - start_time
        trace.append(f"[{_iso_now()}] Done in {elapsed:.2f}s")

        return AgentReport(
            query=query,
            generated_at=_iso_now(),
            window=window.value,
            sources_used=sources,
            raw_records_read=len(signals),
            top_keywords=keywords,
            top_products_revenue=product_reports[:limit],
            top_products_quantity=self._sort_by_quantity(product_reports)[:limit],
            key_insights=insights,
            forecast=forecast,
            rd_recommendations=recommendations,
            opportunity_summary=summary,
            opportunities=opportunities,
            agent_trace=trace,
            human_review_required=any(o.opportunity_score > 85 for o in opportunities[:3]),
        )

    def _extract_keywords(self, signals: List[Dict], query: str) -> List[KeywordReport]:
        """Extract keywords from signals."""
        q_lower = query.lower()
        query_cat = "General"
        if any(k in q_lower for k in ["tumbler", "bình", "binh", "ly", "cốc", "coc", "flask", "cup", "bottle"]):
            query_cat = "Drinkware"
        elif any(k in q_lower for k in ["giày", "giay", "sneaker", "shoes", "shoe", "boot"]):
            query_cat = "Footwear"
        elif any(k in q_lower for k in ["áo", "ao", "shirt", "tee", "hoodie"]):
            query_cat = "Apparel"
        elif any(k in q_lower for k in ["đèn", "den", "light", "lamp", "mirror"]):
            query_cat = "Home Decor"
        elif any(k in q_lower for k in ["noel", "christmas", "ornament"]):
            query_cat = "Seasonal"
        elif any(k in q_lower for k in ["chó", "mèo", "pet", "dog", "cat"]):
            query_cat = "Pet"

        cat_data: Dict[str, Dict] = {}

        for sig in signals:
            raw_cat = sig.get("category", "General")
            cat = query_cat if (raw_cat in ["General", "Other"] and query_cat != "General") else raw_cat
            if cat not in cat_data:
                cat_data[cat] = {"demand": 0.0, "growth": 0.0, "count": 0}

            revenue = sig.get("revenue", 0)
            growth = sig.get("growth_rate", 0)

            cat_data[cat]["demand"] += min(100, revenue / 50000 * 50)
            cat_data[cat]["growth"] += growth
            cat_data[cat]["count"] += 1

        keywords = []
        for cat, data in sorted(cat_data.items(), key=lambda x: x[1]["demand"], reverse=True):
            count = data["count"]
            avg_demand = max(0, data["demand"] / count) if count else 0
            avg_growth = max(0, min(100, data["growth"] / count)) if count else 0

            keywords.append(KeywordReport(
                keyword=f"{query} + {cat}".lower(),
                demand=min(100, round(avg_demand, 1)),
                growth=round(avg_growth, 1),
                collection=cat,
                volume=count * 500,
                sources_count=count,
                recommended_product=self._suggest_pod(cat, query),
                price_range=self._price_range(cat),
                reason=f"Trending in {cat} with {count} products detected",
                evidence=[f"Analysis of {count} signals"],
            ))

        return keywords[:10]

    def _extract_products(self, signals: List[Dict]) -> List[ProductReport]:
        """Extract top products by revenue."""
        products = []

        for sig in signals:
            products.append(ProductReport(
                rank=0,
                title=sig.get("title", "")[:200],
                source=sig.get("source", "unknown"),
                revenue=sig.get("revenue", 0),
                quantity=sig.get("quantity_sold", 0),
                price=sig.get("price", 0),
                currency=sig.get("currency", "USD"),
                window="30d",
                url=sig.get("url", ""),
                growth_rate=sig.get("growth_rate", 0),
                rating=sig.get("rating", 0),
                estimated=sig.get("is_synthetic", False),
            ))

        products.sort(key=lambda x: x.revenue, reverse=True)
        for i, p in enumerate(products):
            p.rank = i + 1

        return products[:20]

    def _sort_by_quantity(self, products: List[ProductReport]) -> List[ProductReport]:
        """Sort products by quantity sold."""
        sorted_prods = sorted(products, key=lambda x: x.quantity, reverse=True)
        for i, p in enumerate(sorted_prods):
            p.rank = i + 1
        return sorted_prods

    def _generate_insights(self, signals: List[Dict], opportunities: List) -> List[InsightReport]:
        """Generate insights from signals."""
        if not signals:
            return [InsightReport(
                title="No Data",
                finding="Could not retrieve market data. Check API configuration.",
                confidence="low",
            )]

        insights = []
        total_revenue = sum(s.get("revenue", 0) for s in signals)
        total_products = len(signals)

        insights.append(InsightReport(
            title="Market Size",
            finding=f"Found {total_products} products with ${total_revenue:,.2f} combined revenue",
            evidence=[f"Based on {len(signals)} signals"],
            confidence="high",
        ))

        # Top category
        cat_rev: Dict[str, float] = {}
        for s in signals:
            cat = s.get("category", "Other")
            cat_rev[cat] = cat_rev.get(cat, 0) + s.get("revenue", 0)

        if cat_rev:
            top_cat = max(cat_rev.items(), key=lambda x: x[1])
            insights.append(InsightReport(
                title="Top Category",
                finding=f"{top_cat[0]} leads with ${top_cat[1]:,.2f} revenue",
                evidence=[f"Category breakdown: {', '.join(cat_rev.keys())}"],
                confidence="medium",
            ))

        # Top opportunity
        if opportunities:
            top = opportunities[0]
            insights.append(InsightReport(
                title="Top Opportunity",
                finding=f"'{top.title[:50]}' scores {top.opportunity_score}/100",
                evidence=[f"demand={top.score_breakdown.demand_growth}, margin={top.score_breakdown.profit_margin}"],
                confidence="medium",
            ))

        # TikTok virality
        tiktok = [s for s in signals if s.get("source") == "tiktok"]
        if tiktok:
            views = sum(s.get("views", 0) for s in tiktok)
            insights.append(InsightReport(
                title="TikTok Demand",
                finding=f"TikTok driving {views:,} views for this niche",
                evidence=[f"{len(tiktok)} TikTok signals"],
                confidence="high",
            ))

        return insights[:5]

    def _generate_forecast(self, signals: List[Dict], days: int) -> Optional[ForecastReport]:
        """Generate 30-day demand forecast."""
        if not signals:
            return None

        avg_growth = sum(s.get("growth_rate", 0) for s in signals) / len(signals)
        avg_demand = sum(s.get("revenue", 0) for s in signals) / max(1, len(signals))

        daily = []
        today = datetime.now(timezone.utc).date()

        for i in range(1, 31):
            projected = avg_demand * (1 + (avg_growth / 100) * (i / 30))
            daily.append(ForecastDay(
                day=(today.fromordinal(today.toordinal() + i)).isoformat(),
                demand=round(projected, 2),
                low=round(projected * 0.8, 2),
                high=round(projected * 1.2, 2),
            ))

        trend = round(avg_growth, 1)
        total = sum(d.demand for d in daily)

        return ForecastReport(
            method="linear_projection",
            horizon_days=30,
            confidence="medium" if abs(trend) < 50 else "low",
            projected_total_demand=round(total, 2),
            avg_daily=round(total / 30, 2),
            trend=trend,
            daily=daily,
            narrative=f"Based on {trend}% growth rate, demand is expected to {'increase' if trend > 0 else 'decrease'} over 30 days.",
        )

    def _generate_recommendations(self, opportunities: List) -> List[RecommendationReport]:
        """Generate R&D recommendations."""
        recs = []

        for i, opp in enumerate(opportunities[:5]):
            risk = "high" if opp.score_breakdown.ip_safety < 40 else "medium" if opp.score_breakdown.ip_safety < 70 else "low"

            recs.append(RecommendationReport(
                rank=i + 1,
                product=opp.title[:200],
                opportunity_score=round(opp.opportunity_score, 1),
                price_range=f"${opp.base_cost:.2f} - ${opp.suggested_price:.2f}",
                rationale=f"Score {opp.opportunity_score}/100 driven by demand ({opp.score_breakdown.demand_growth}) and virality ({opp.score_breakdown.tiktok_virality})",
                evidence=[
                    f"Revenue potential: ${opp.suggested_price * 100:,}",
                    f"Margin: {opp.profit_margin_pct}%",
                    f"SKU: {opp.best_fit_sku}",
                ],
                risk=risk,
            ))

        return recs

    def _build_summary(self, query: str, opportunities: List, insights: List[InsightReport], forecast: Optional[ForecastReport]) -> str:
        """Build executive summary."""
        if not opportunities:
            return f"No significant opportunities for '{query}'. Try different keywords."

        top = opportunities[0]
        parts = [
            f"Analysis of '{query}' identified {len(opportunities)} opportunities.",
            f"Top: {top.title[:50]} (score {top.opportunity_score}/100).",
            f"Margin: {top.profit_margin_pct}% at ${top.suggested_price:.2f}.",
        ]

        if forecast and forecast.trend != 0:
            direction = "up" if forecast.trend > 0 else "down"
            parts.append(f"30-day trend: {direction} {abs(forecast.trend)}%.")

        if insights:
            parts.append(f"Key: {insights[0].finding}")

        return " ".join(parts)

    def _suggest_pod(self, category: str, query: str = "") -> str:
        """Suggest POD product for category."""
        q_lower = query.lower()
        if any(k in q_lower for k in ["tumbler", "bình", "binh", "ly", "cốc", "coc", "flask", "cup", "bottle"]):
            return "20oz Stainless Steel Tumbler"
        if any(k in q_lower for k in ["giày", "giay", "sneaker", "shoes", "shoe"]):
            return "Custom Sneaker Shoes"

        mapping = {
            "Drinkware": "20oz Stainless Steel Tumbler",
            "Footwear": "Custom Sneaker Shoes",
            "Apparel": "Heavyweight Cotton T-Shirt",
            "Home Decor": "Acrylic LED Night Light",
            "Pet": "Personalized Pet Collar",
            "Seasonal": "Custom Christmas Ornament",
            "General": "20oz Stainless Steel Tumbler" if any(k in q_lower for k in ["bình", "tumbler", "ly"]) else "Custom Keychain",
        }
        return mapping.get(category, "Custom Print Product")

    def _price_range(self, category: str) -> str:
        """Get typical price range."""
        mapping = {
            "Drinkware": "$18-28",
            "Apparel": "$22-35",
            "Home Decor": "$25-45",
            "Pet": "$15-25",
            "Seasonal": "$12-22",
            "General": "$20-30",
        }
        return mapping.get(category, "$20-30")


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()
