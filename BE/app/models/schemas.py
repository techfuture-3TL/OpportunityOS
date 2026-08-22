"""Core Pydantic schemas for PW1 - Printway Market Intelligence Platform."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class DataSource(str, Enum):
    """Data source selection for analysis."""
    ALL = "ALL"
    LIVE_ONLY = "LIVE_ONLY"
    MARKET_SIGNALS = "MARKET_SIGNALS"
    TIKTOK_SHOP = "TIKTOK_SHOP"


class StrategyPreset(str, Enum):
    """Pre-configured scoring strategy presets."""
    VIRAL_TREND = "VIRAL_TREND"
    HIGH_MARGIN = "HIGH_MARGIN"
    SAFE_EVERGREEN = "SAFE_EVERGREEN"
    LOW_COMPETITION = "LOW_COMPETITION"
    CUSTOM = "CUSTOM"
    CUSTOM_WEIGHTS = "CUSTOM_WEIGHTS"


class TimeWindow(str, Enum):
    """Time window for data filtering."""
    DAY_7 = "7d"
    DAY_30 = "30d"
    DAY_90 = "90d"
    YEAR_1 = "1y"
    ALL = "all"


# =============================================================================
# MARKET SIGNAL (Raw Data from Crawlers)
# =============================================================================

class MarketSignal(BaseModel):
    """A single market signal from crawling - THE RAW DATA."""

    signal_id: str
    source: str  # "tiktok", "ebay", "amazon", "etsy", "shopee"

    # Identification
    product_id: Optional[str] = None
    title: str
    url: str = ""

    # Pricing & Revenue (ACTUAL DATA)
    price: float = 0.0
    currency: str = "USD"
    revenue: float = 0.0  # Total revenue (price × quantity_sold)
    quantity_sold: int = 0

    # Demand Signals
    reviews_count: int = 0
    rating: float = 0.0
    growth_rate: float = 0.0  # % growth

    # Categorization
    category: str = ""
    keywords: List[str] = []
    niche: str = ""

    # Metadata
    image_url: str = ""
    seller_name: str = ""
    seller_id: str = ""
    launch_date: Optional[str] = None
    commission_rate: float = 0.0

    # TikTok-specific
    video_revenue: float = 0.0
    live_revenue: float = 0.0
    views: int = 0

    # Technical
    crawled_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    estimated_fields: List[str] = []  # Fields that were estimated, not real
    is_synthetic: bool = False  # True if this is fake/demo data


# =============================================================================
# KEYWORD ANALYSIS
# =============================================================================

class KeywordStats(BaseModel):
    """Keyword-level aggregated statistics."""

    keyword: str
    demand: float = Field(0, ge=0, le=100, description="Demand score 0-100")
    growth: float = Field(0, ge=0, le=100, description="Growth score 0-100")
    collection: str = ""  # Product collection/category
    volume: int = 0  # Search volume estimate
    sources_count: int = 0  # Number of sources


class KeywordReport(BaseModel):
    """Final keyword analysis report item."""

    keyword: str
    demand: float = Field(0, ge=0, le=100)
    growth: float = Field(0, ge=0, le=100)
    collection: str = ""
    recommended_product: str = ""  # POD product suggestion
    price_range: str = ""
    reason: str = ""  # Why this keyword is an opportunity
    evidence: List[str] = []  # Source citations


# =============================================================================
# PRODUCT ANALYSIS
# =============================================================================

class ProductReport(BaseModel):
    """Top product ranking item."""

    rank: int = 1
    title: str
    source: str  # Which marketplace
    revenue: float
    quantity: int
    price: float = 0.0
    currency: str = "USD"
    window: str = "30d"
    url: str = ""
    growth_rate: float = 0.0
    rating: float = 0.0
    estimated: bool = False  # True if data was estimated


# =============================================================================
# INSIGHTS
# =============================================================================

class InsightReport(BaseModel):
    """Business insight from data analysis."""

    title: str
    finding: str  # What was found
    evidence: List[str] = []  # Source citations
    confidence: str = "medium"  # high | medium | low


# =============================================================================
# FORECAST
# =============================================================================

class ForecastDay(BaseModel):
    """Single day forecast."""

    day: str  # ISO date
    demand: float  # Projected demand score
    low: float  # Lower bound
    high: float  # Upper bound


class ForecastReport(BaseModel):
    """30-day demand forecast."""

    method: str  # "holt_growth" | "linear_regression" | "llm_estimate"
    horizon_days: int = 30
    confidence: str = "low"  # high | medium | low
    projected_total_demand: float = 0
    avg_daily: float = 0
    trend: float = 0  # % trend direction
    daily: List[ForecastDay] = []
    narrative: str = ""  # LLM-generated interpretation


# =============================================================================
# R&D RECOMMENDATIONS
# =============================================================================

class RecommendationReport(BaseModel):
    """R&D product recommendation."""

    rank: int = 1
    product: str  # Product name/idea
    opportunity_score: float = Field(0, ge=0, le=100)
    price_range: str = ""
    rationale: str = ""  # Business justification
    evidence: List[str] = []
    risk: str = "medium"  # low | medium | high


# =============================================================================
# FULL AGENT REPORT (FINAL OUTPUT)
# =============================================================================

class AgentReport(BaseModel):
    """Complete AI Agent analysis report - THE FINAL OUTPUT per PW1 spec."""

    query: str  # Research query
    generated_at: str  # ISO timestamp
    window: str = "30d"  # Time window used

    # Data sources used
    sources_used: List[str] = []
    raw_records_read: int = 0

    # PW1 Required Outputs:
    top_keywords: List[KeywordReport] = []  # ✅ Top Keywords with Demand/Growth
    top_products_revenue: List[ProductReport] = []  # ✅ Revenue ranking
    top_products_quantity: List[ProductReport] = []  # ✅ Volume ranking
    key_insights: List[InsightReport] = []  # ✅ Key Insights
    forecast: Optional[ForecastReport] = None  # ✅ 30 Days Forecast
    rd_recommendations: List[RecommendationReport] = []  # ✅ R&D Recommendation

    # Summary & Scored Opportunities
    opportunity_summary: str = ""
    opportunities: List[OpportunityItem] = []  # Scored opportunity cards with 6-pillar rationales

    # Debug
    agent_trace: List[str] = []
    human_review_required: bool = False


# =============================================================================
# API REQUESTS
# =============================================================================

class AnalyzeRequest(BaseModel):
    """Request to run AI agent analysis."""

    query: str = Field(..., min_length=2, max_length=200)
    window: TimeWindow = TimeWindow.DAY_30
    data_source: DataSource = DataSource.ALL
    limit: int = Field(10, ge=1, le=50)
    sources: Optional[List[str]] = None  # Specific crawlers
    deep: bool = True  # Enable deep research mode


class CrawlRequest(BaseModel):
    """Request to crawl marketplace data."""

    query: str = Field(..., min_length=2)
    sources: Optional[List[str]] = None  # ["tiktok", "ebay", "amazon"]
    max_items: int = Field(30, ge=1, le=100)
    days: int = Field(7, ge=1, le=365)
    persist: bool = True


class CrawlResponse(BaseModel):
    """Response from crawl operation."""

    run_id: str
    query: str
    sources: List[str]
    products_found: int
    signals_added: int
    raw_data_path: Optional[str] = None
    results: List[Dict[str, Any]] = []
    execution_time_sec: float = 0.0


# =============================================================================
# SCORING
# =============================================================================

class ScoreBreakdown(BaseModel):
    """MCDA score breakdown - 6 pillars."""

    demand_growth: float = 0
    market_gap: float = 0
    profit_margin: float = 0
    supply_feasibility: float = 0
    ip_safety: float = 0
    tiktok_virality: float = 0


class PillarExplanation(BaseModel):
    """Detailed rationale and score for an individual pillar."""

    pillar: str  # e.g. "demand_growth", "market_gap", "profit_margin", "supply_feasibility", "ip_safety", "tiktok_virality"
    label: str   # e.g. "Nhu cầu", "Khoảng trống", "Biên lãi", "Chuỗi cung", "Bản quyền", "Viral TikTok"
    score: float = 0
    reason: str = ""  # Clear explanation of the score in Vietnamese


class OpportunityItem(BaseModel):
    """Scored market opportunity with rich 6-pillar explanations."""

    id: str
    signal_id: str
    title: str
    category: str = ""
    niche: str = ""

    # Scores
    opportunity_score: float = 0
    score_breakdown: ScoreBreakdown = ScoreBreakdown()

    # 6 Pillar Rationales & Explanations (with formulas and keywords)
    score_rationales: Dict[str, str] = Field(default_factory=dict)
    rationales: Dict[str, str] = Field(default_factory=dict)
    reasons: Dict[str, str] = Field(default_factory=dict)
    explanations: Dict[str, str] = Field(default_factory=dict)
    pillar_explanations: List[PillarExplanation] = Field(default_factory=list)
    score_breakdown_details: Dict[str, Any] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    pain_point_solved: str = ""  # Nỗi đau khách hàng được giải quyết
    key_pain_point_solved: str = ""  # Frontend compatibility alias
    sales_growth_text: str = ""  # e.g. "+109% sales growth"

    # Financial & Unit Economics
    suggested_price: float = 0
    base_cost: float = 0
    profit_margin_pct: float = 0
    unit_economics: Dict[str, Any] = Field(default_factory=dict)

    # Metadata & Media
    source: str = ""
    best_fit_sku: str = ""
    image_url: str = ""
    img_url: str = ""
    thumbnail: str = ""
    agent_trace: List[str] = []


class ScoringStrategy(BaseModel):
    """Scoring strategy with custom weights."""

    preset: StrategyPreset = StrategyPreset.VIRAL_TREND
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "demand": 0.35, "gap": 0.15, "margin": 0.15,
        "supply": 0.10, "safety": 0.10, "virality": 0.15
    })

    @classmethod
    def with_preset(cls, preset: StrategyPreset) -> ScoringStrategy:
        presets = {
            StrategyPreset.VIRAL_TREND: {"demand": 0.35, "gap": 0.15, "margin": 0.15, "supply": 0.10, "safety": 0.10, "virality": 0.15},
            StrategyPreset.HIGH_MARGIN: {"demand": 0.20, "gap": 0.15, "margin": 0.40, "supply": 0.10, "safety": 0.10, "virality": 0.05},
            StrategyPreset.SAFE_EVERGREEN: {"demand": 0.15, "gap": 0.20, "margin": 0.20, "supply": 0.20, "safety": 0.20, "virality": 0.05},
            StrategyPreset.LOW_COMPETITION: {"demand": 0.20, "gap": 0.40, "margin": 0.15, "supply": 0.10, "safety": 0.10, "virality": 0.05},
        }
        return cls(preset=preset, weights=presets.get(preset, presets[StrategyPreset.VIRAL_TREND]))


# =============================================================================
# SKU CATALOG
# =============================================================================

class SKUCatalogItem(BaseModel):
    """Printway SKU catalog item."""

    sku: str
    name: str
    category: str
    base_cost: float
    suggested_retail_price: float
    production_days: str = "2-4"
    techniques: List[str] = []
    warehouses: List[str] = ["US"]
    description: str = ""


# =============================================================================
# PRODUCT BRIEF
# =============================================================================

class ProductBrief(BaseModel):
    """AI-generated product brief for R&D."""

    opportunity_id: str
    title: str
    executive_summary: str = ""
    target_buyer_persona: str = ""

    product_specifications: Dict[str, Any] = {}
    financial_model: Dict[str, Any] = {}

    ai_design_prompts: List[str] = []
    tiktok_marketing_plan: List[str] = []
    launch_checklist: List[str] = []


# =============================================================================
# ENUMS & INPUT CONSTRAINTS (For Matching & Legacy API Pipeline)
# =============================================================================

class ProductCategory(str, Enum):
    ALL = "ALL"
    DRINKWARE = "DRINKWARE"
    HOME_DECOR = "HOME_DECOR"
    APPAREL = "APPAREL"
    ACCESSORIES = "ACCESSORIES"
    SEASONAL = "SEASONAL"


class TargetCountry(str, Enum):
    US = "US"
    UK = "UK"
    VN = "VN"
    GLOBAL = "GLOBAL"


class CraftingTechnique(str, Enum):
    UV_PRINT = "UV_PRINT"
    SUBLIMATION = "SUBLIMATION"
    EMBROIDERY = "EMBROIDERY"
    LASER_ENGRAVING = "LASER_ENGRAVING"
    DIRECT_TO_GARMENT = "DIRECT_TO_GARMENT"


class WarehouseLocation(str, Enum):
    US = "US"
    VN = "VN"
    EU = "EU"
    CN = "CN"


class MarketAndNicheInputs(BaseModel):
    categories: List[ProductCategory] = Field(default_factory=list)
    target_countries: List[TargetCountry] = Field(default_factory=list)
    search_keyword: Optional[str] = None


class FinancialConstraintsInputs(BaseModel):
    min_profit_margin_pct: float = 0.0
    max_cogs_usd: Optional[float] = None
    target_retail_price: Optional[float] = None


class SupplyChainConstraintInputs(BaseModel):
    max_production_days: Optional[int] = None
    warehouse_locations: List[WarehouseLocation] = Field(default_factory=list)
    techniques: List[CraftingTechnique] = Field(default_factory=list)


DataSourceSelection = DataSource
ActionableProductBrief = ProductBrief


class OpportunityAnalysisRequest(BaseModel):
    data_source: DataSourceSelection = DataSourceSelection.ALL
    limit: int = 20
    market_and_niche: Optional[MarketAndNicheInputs] = None
    financials: Optional[FinancialConstraintsInputs] = None
    supply_chain: Optional[SupplyChainConstraintInputs] = None
    strategy: StrategyPreset = StrategyPreset.VIRAL_TREND


class OpportunityCollection(BaseModel):
    total: int = 0
    items: List[OpportunityItem] = Field(default_factory=list)


class OpportunityAnalysisResponse(BaseModel):
    success: bool = True
    opportunities: List[OpportunityItem] = Field(default_factory=list)
    total_found: int = 0
    execution_time_sec: float = 0.0


class GenerateBriefRequest(BaseModel):
    opportunity_id: str
    target_buyer_persona: Optional[str] = None


class BenchmarkResponse(BaseModel):
    latency_ms: float = 0.0
    throughput_rps: float = 0.0
    runs: int = 1
    details: Dict[str, Any] = Field(default_factory=dict)


class SignalFetchRequest(BaseModel):
    query: str
    sources: List[str] = Field(default_factory=lambda: ["tiktok", "ebay", "amazon"])
    limit: int = 30


class SignalJob(BaseModel):
    job_id: str
    status: str = "pending"
    query: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
