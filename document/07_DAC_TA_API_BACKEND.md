# 🔗 BÁO CÁO 07: ĐẶC TẢ API BACKEND FASTAPI
## Dự án: PW1 - Product Opportunity Hub (Printway R&D AI Copilot)

Base URL: `http://localhost:8000/api/v1`  
Data Source: `C:\hackathon\BE\data\PW_Daily_Keyword_Research - Data.csv` (2,092 bản ghi)  
AI Model: `deepseek-v4-flash`

---

## 1. Danh Sách Endpoint Đầy Đủ

| Phương Thức | Endpoint | Chức Năng |
| :---: | :--- | :--- |
| `GET` | `/health` | Kiểm tra trạng thái máy chủ Backend. |
| `GET` | `/catalog` | Lấy danh sách 8 phôi sản phẩm sẵn có trong kho Printway. |
| `GET` | `/database/stats` | Thống kê số lượng 2,092 từ khóa và phân bổ ngành hàng. |
| `GET` | `/database/sample` | Xem trước các mẫu từ khóa trong database. |
| `GET` | `/strategies` | Lấy danh sách 5 chiến lược tính điểm (Viral Trend, High Margin...). |
| `POST` | `/opportunities/analyze` | **ENDPOINT CHÍNH:** Quét 2,092 dòng theo 13 tiêu chí lọc $\rightarrow$ Trả về Bảng Xếp Hạng. |
| `GET` | `/opportunities/{id}` | Lấy thông tin chi tiết của 1 cơ hội sản phẩm cụ thể. |
| `POST` | `/opportunities/generate-brief` | **DEEPSEEK AI:** Sinh bản Product Brief, 3 Midjourney Prompts và Kế hoạch TikTok Ads. |

---

## 2. Request Payload Mẫu (`POST /opportunities/analyze`)

```json
{
  "search_mode": "DISCOVERY",
  "data_source": "ALL",
  "limit": 20,
  "market_and_niche": {
    "target_country": "US",
    "categories": ["Drinkware", "Gifts", "Apparel", "Home_Decor"],
    "seasonality": "Evergreen",
    "seed_keywords": ["Halloween", "Teacher", "Tumbler"],
    "min_sales_growth_pct": 20.0
  },
  "financials": {
    "min_profit_margin_pct": 60.0,
    "target_retail_price_min": 20.0,
    "target_retail_price_max": 50.0,
    "max_base_cogs_cap": 15.0,
    "target_ad_budget": 1000.0
  },
  "supply_chain": {
    "preferred_warehouse": "US",
    "allowed_techniques": ["LASER_ENGRAVING", "UV_PRINT", "DTG"],
    "max_production_days": 3
  },
  "strategy": {
    "preset": "VIRAL_TREND"
  }
}
```
