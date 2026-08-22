# Printway AI Agent & Market Intelligence Platform (Backend)

An enterprise-grade autonomous AI Agent platform for Print-on-Demand (POD) market intelligence, real-time multi-channel scraping, and Hybrid Vector RAG analytics.

---

## 🌟 Key Features

- **Autonomous Deep Research Agent**: Multi-hop planning, real-time scraping, unit economics evaluation, and Chain-of-Thought (`<thinking>`) reasoning.
- **Hybrid Vector & Lexical RAG**: Reciprocal Rank Fusion (RRF) combining BM25 lexical search and Dense Semantic Cosine Similarity across 2,100+ market signals and Printway SKU catalogs.
- **Multi-Channel Real-Time Scraping**: In-memory, zero-disk scraping across Etsy, Shopee, Amazon, eBay, and Redbubble with session token support.
- **Structured Instructor LLM Engine**: Resilient JSON schema validation, automatic heuristic repair, and multi-provider failover (DeepSeek / Gemini).
- **Standardized RESTful API**: Unified response envelopes (`ApiResponse[T]`), custom domain exceptions, and asynchronous job polling (`POST /api/v1/agent/jobs`).

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and enter directory
cd BE

# Install dependencies
make install
# or
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment
```bash
cp .env.example .env
# Ensure PORT=8001 (or desired port)
```

### 3. Launch Backend
```bash
# Using Makefile
make run

# or using script
./scripts/start.sh

# or using uvicorn directly
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

- **Swagger UI**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Health Check**: [http://localhost:8001/health](http://localhost:8001/health)

---

## 📁 System Architecture

```
BE/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── agent.py          # Deep Research Agent & Async Jobs
│   │   │   │   ├── crawlers.py       # Live Marketplace Scraping
│   │   │   │   ├── rag.py            # RAG Search & SKU Catalog
│   │   │   │   └── analytics.py      # Unit Economics & Forecasting
│   │   │   └── router.py             # Central v1 Router
│   │   └── routes.py                 # Core business routes
│   ├── core/
│   │   ├── config.py                 # Configuration & Environment
│   │   ├── exceptions.py             # Global Exception Handlers
│   │   └── responses.py              # Standardized ApiResponse[T] Envelope
│   ├── models/
│   │   ├── agent_schemas.py          # Agent & Report Pydantic Models
│   │   └── schemas.py                # Core Product & Signal Models
│   ├── services/
│   │   ├── agent/                    # Deep Research Agent & Job Queue
│   │   ├── crawlers/                 # Etsy, Shopee, Amazon, eBay, Redbubble
│   │   ├── llm/                      # Structured Instructor & Prompts
│   │   ├── rag/                      # In-memory BM25 + Dense RAG Engine
│   │   └── unit_economics.py         # Margin & ROAS Financial Engine
│   └── main.py                       # FastAPI Application Entrypoint
├── data/                             # Market datasets & session credentials
├── scripts/                          # Executable startup scripts
├── tests/                            # Automated Pytest Suite
├── Makefile                          # Development commands
└── requirements.txt                  # Python dependencies
```

---

## 📡 API Reference Overview

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/agent/jobs` | Submit asynchronous Deep Research job | `202 Accepted` |
| `GET` | `/api/v1/agent/jobs/{job_id}` | Poll job status, trace & final report | `200 OK` |
| `POST` | `/api/v1/agent/analyze` | Synchronous market analysis | `200 OK` |
| `POST` | `/api/v1/rag/search` | Query Hybrid RAG knowledge base | `200 OK` |
| `GET` | `/api/v1/rag/catalog` | Get Printway SKU catalog & economics | `200 OK` |
| `POST` | `/api/v1/crawlers/search` | Trigger live multi-source scraping | `200 OK` |
| `GET` | `/api/v1/crawlers/sources` | Check crawler operational statuses | `200 OK` |

---

## 🧪 Testing

Run the comprehensive automated test suite:
```bash
make test
# or
python3 -m pytest tests/ -v
```
