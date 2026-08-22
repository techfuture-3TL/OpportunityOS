# PW1 RAG Architecture Specification

## Overview

**PRINTWAY MARKET INTELLIGENCE PLATFORM (PW1)**

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   API        │────▶│  Crawlers    │────▶│  IN-MEMORY  │
│   Request    │     │  (Realtime)  │     │  Signals     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Report     │◀────│  Scoring     │◀────│  Agent       │
│   Response   │     │  MCDA        │     │  Pipeline    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
                                         ┌──────────────┐
                                         │  Supabase    │
                                         │  (Job Meta)  │
                                         └──────────────┘
```

## CRITICAL: NO PERSISTENCE

- **NO file storage** (signals.json, .csv, etc.)
- **NO database data storage** 
- **ALL data in-memory only** during request lifecycle
- **Supabase** = Job metadata only (id, status, timestamps)

---

## Data Flow

### 1. Request Flow
```
User Request → API → Crawl (Realtime) → In-Memory Products → Agent Pipeline → Report → Response
```

### 2. Supabase Only Stores
```sql
-- Job metadata ONLY
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  job_id TEXT UNIQUE,
  job_type TEXT,        -- 'analyze', 'crawl', 'score'
  query TEXT,
  status TEXT,          -- 'pending', 'running', 'completed', 'failed'
  sources TEXT[],
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  result_summary JSONB, -- lightweight summary only
  error TEXT
);
```

---

## INPUT Schema

### POST /api/v1/analyze

```json
{
  "query": "christmas ornament",
  "window": "30d",
  "data_source": "ALL",
  "limit": 10,
  "sources": ["tiktok"],
  "deep": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | ✅ | - | Research keyword (2-200 chars) |
| window | string | ❌ | "30d" | Time: 7d, 30d, 90d, 1y |
| data_source | string | ❌ | "ALL" | Source: ALL, LIVE_ONLY, TIKTOK_SHOP |
| limit | int | ❌ | 10 | Max items (1-50) |
| sources | string[] | ❌ | auto | ["tiktok"], ["amazon"], etc. |
| deep | bool | ❌ | true | Enable LLM enhancement |

### POST /api/v1/crawl

```json
{
  "query": "halloween decor",
  "sources": ["tiktok", "ebay", "amazon"],
  "max_items": 30,
  "days": 7
}
```

---

## OUTPUT Schema

### POST /api/v1/analyze Response

```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {
    "query": "christmas ornament",
    "generated_at": "2025-08-21T10:30:00Z",
    "window": "30d",
    "sources_used": ["tiktok"],
    "raw_records_read": 25,

    "top_keywords": [
      {
        "keyword": "christmas ornament + Seasonal",
        "demand": 78.5,
        "growth": 45.2,
        "collection": "Seasonal",
        "recommended_product": "Custom Christmas Ornament",
        "price_range": "$12-22",
        "reason": "Trending in Seasonal with 8 products detected",
        "evidence": ["Analysis of 8 signals"]
      }
    ],

    "top_products_revenue": [
      {
        "rank": 1,
        "title": "Personalized Christmas Ornament 2025",
        "source": "tiktok",
        "revenue": 45678.90,
        "quantity": 2400,
        "price": 19.03,
        "currency": "USD",
        "window": "30d",
        "url": "https://shop.tiktok.com/product/xxx",
        "growth_rate": 35.5,
        "rating": 4.8,
        "estimated": false
      }
    ],

    "top_products_quantity": [
      { /* sorted by quantity sold */ }
    ],

    "key_insights": [
      {
        "title": "Market Size",
        "finding": "Found 25 products with $245,000 combined revenue",
        "evidence": ["Based on 25 signals"],
        "confidence": "high"
      }
    ],

    "forecast": {
      "method": "linear_projection",
      "horizon_days": 30,
      "confidence": "medium",
      "projected_total_demand": 125000.00,
      "avg_daily": 4166.67,
      "trend": 25.5,
      "daily": [
        {"day": "2025-08-22", "demand": 3800.00, "low": 3040.00, "high": 4560.00}
      ],
      "narrative": "Based on 25.5% growth rate, demand expected to increase over 30 days."
    },

    "rd_recommendations": [
      {
        "rank": 1,
        "product": "Custom Engraved Christmas Ornament",
        "opportunity_score": 82.5,
        "price_range": "$5.00 - $18.99",
        "rationale": "Score 82.5/100 driven by demand (75) and virality (88)",
        "evidence": ["Revenue potential: $1,899", "Margin: 74%", "SKU: PW-SEASON-ORNAMENT"],
        "risk": "low"
      }
    ],

    "opportunity_summary": "Analysis of 'christmas ornament' identified 8 opportunities...",

    "agent_trace": [
      "[2025-08-21T10:30:00Z] Starting: christmas ornament",
      "[2025-08-21T10:30:03Z] 25 signals in memory",
      "[2025-08-21T10:30:03Z] 8 opportunities scored"
    ],

    "human_review_required": false
  }
}
```

---

## Crawler Data Format (Internal)

Products from crawlers are converted to in-memory signals:

```python
signal = {
    "signal_id": "SIG-tiktok-abc123",  # generated UUID
    "source": "tiktok",                  # tiktok, ebay, amazon
    "crawled_at": 1724212345.678,       # timestamp
    
    # Product
    "product_id": "1729587769570529799",
    "title": "HydroJug Traveler Tumbler",
    "url": "https://shop.tiktok.com/product/xxx",
    "image_url": "https://...",
    
    # Pricing
    "price": 25.49,
    "currency": "USD",
    "revenue": 85697.38,       # price × quantity_sold
    "quantity_sold": 3362,
    
    # Demand
    "reviews_count": 1250,
    "rating": 4.8,
    "growth_rate": 35.5,       # % growth
    
    # Category
    "category": "Drinkware",
    "niche": "personalized tumbler",
    "keywords": ["personalized tumbler"],
    
    # TikTok-specific
    "video_revenue": 8500.25,
    "live_revenue": 6500.50,
    "views": 250000,
    
    # Technical
    "is_synthetic": False,
    "estimated_fields": [],
}
```

---

## Scoring Strategy

### MCDA 6-Pillar Weights

| Preset | demand | gap | margin | supply | safety | virality |
|--------|--------|-----|--------|--------|--------|----------|
| VIRAL_TREND | 0.35 | 0.15 | 0.15 | 0.10 | 0.10 | 0.15 |
| HIGH_MARGIN | 0.20 | 0.15 | 0.40 | 0.10 | 0.10 | 0.05 |
| SAFE_EVERGREEN | 0.15 | 0.20 | 0.20 | 0.20 | 0.20 | 0.05 |
| LOW_COMPETITION | 0.20 | 0.40 | 0.15 | 0.10 | 0.10 | 0.05 |

---

## SKU Catalog

| Category | SKU | Base Cost | Suggested Price |
|----------|-----|-----------|----------------|
| Drinkware | PW-DRINK-TUMB-20OZ | $8.50 | $24.99 |
| Drinkware | PW-DRINK-MUG-15OZ | $7.50 | $22.99 |
| Apparel | PW-APP-HOODIE-FLEECE | $14.00 | $39.99 |
| Apparel | PW-APP-TEE-HEAVY | $9.00 | $27.99 |
| Home Decor | PW-GIFT-ACRYLIC-LIGHT | $12.00 | $34.99 |
| Home Decor | PW-HOME-WOOD-PLAQUE | $10.00 | $29.99 |
| Seasonal | PW-SEASON-ORNAMENT | $5.00 | $18.99 |
| Pet | PW-PET-LEATHER-COLLAR | $7.00 | $19.99 |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/crawl | Realtime crawl, no persistence |
| POST | /api/v1/analyze | Full AI analysis, no persistence |
| POST | /api/v1/score | Score signals in memory |
| GET | /api/v1/health | Health check |

---

## Environment Variables

```env
# Server
PORT=8001
HOST=0.0.0.0
ENVIRONMENT=development

# Kalodata (TikTok Shop)
KALODATA_API_KEY=your_api_key
KALODATA_REGION=US

# Supabase (Job metadata only)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# Crawl Settings
CRAWL_SOURCES=tiktok,ebay,amazon
CRAWL_WATCHLIST=personalized tumbler,halloween decor,christmas ornament,mug
```
