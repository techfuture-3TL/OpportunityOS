# ⚡ OpportunityOS — Next-Gen AI Opportunity Engine for Print-On-Demand (POD)

<div align="center">

![OpportunityOS Banner](https://img.shields.io/badge/OpportunityOS-Printway%20Hackathon%202026-dc2626?style=for-the-badge&logo=rocket)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)

**Hệ điều hành AI Agent tự động cào dữ liệu live 6 sàn TMĐT bằng động cơ OmniStream, thẩm định bản quyền Clean IP 3 tầng, tính toán mô hình định lượng đa tiêu chí MCDA 6 trụ cột và khớp lệnh phôi xưởng Printway chuẩn SLA 48h chỉ trong 30 giây.**

[Trải nghiệm Trực tiếp](#-cài-đặt--triển-khai-nhanh) • [Động cơ Cào Dữ Liệu OmniStream](#-động-cơ-cào-dữ-liệu-thời-gian-thực-omnistream-radar-bắt-trọn-nhịp-đập-sàn-tmđt) • [Kiến Trúc AI & Mô Hình Toán Học](#-kiến-trúc-chuyên-sâu-mô-hình-toán-học-ai-agent--mcda-engine) • [Thuật toán Matching](#-thuật-toán-matching-phôi-xưởng-printway-sla-48h) • [Tài liệu API](#-api-endpoints)

</div>

---

## 📌 1. Bối Cảnh & Vấn Đề (Problem Statement)

Ngành **Print-On-Demand (POD)** toàn cầu đang đối mặt với 4 "nút thắt cổ chai" chí mạng:

1. **Thử & Sai Tốn Kém (High Trial & Error Costs)**: Seller mất từ **$500 – $2,000** tiền chạy ads thử nghiệm cho mỗi sản phẩm mới chỉ để kiểm tra dung lượng thị trường.
2. **Rủi Ro "Chết Store" Do Bản Quyền (IP & Trademark Bans)**: Hơn **40%** tài khoản Etsy/Amazon/TikTok Shop bị khóa vĩnh viễn do dính nhãn hiệu đã đăng ký (USPTO/WIPO).
3. **Phân Mảnh Dữ Liệu Sàn (Marketplace Fragmentation)**: Dữ liệu bị phân mảnh trên nhiều sàn (Amazon, TikTok Shop, Shopee, Lazada, Etsy, eBay) mà không có công cụ hợp nhất.
4. **Lệch Pha Chuỗi Cung Ứng & Phôi Xưởng (Supply Chain Mismatch)**: Sản phẩm tìm thấy trên mạng không có phôi phù hợp, SLA sản xuất quá dài (>7 ngày) dẫn đến tỉ lệ hủy đơn cao.

---

## 🌐 2. Động Cơ Cào Dữ Liệu Thời Gian Thực: OmniStream Engine (Radar Bắt Trọn Nhịp Đập Sàn TMĐT)

> *"Không dựa dẫm vào những tệp dữ liệu tĩnh lỗi thời hay các báo cáo thị trường chậm chạp hàng tuần. **OmniStream Engine** của OpportunityOS là một radar cảm biến đa chiều — lắng nghe từng hơi thở mua sắm, giải mã từng cơn sốt tìm kiếm và bắt trọn từng xu hướng triệu đô từ 6 đại dương thương mại điện tử lớn nhất hành tinh ngay trong thời gian thực."*

```
                              ┌──────────────────────────────────────────────────────────┐
                              │    OMNISTREAM MULTI-PLATFORM LIVE INGESTION RADAR        │
                              └────────────────────────────┬─────────────────────────────┘
                                                           │
                      ┌────────────────────────────────────┴────────────────────────────────────┐
                      ▼                                                                         ▼
       [Async Orchestrator - asyncio.gather]                                    [Resilient Visual Ingestion Engine]
        ├── 🛒 Amazon Realtime Completion Engine (BSR & Intent)                  ├── Dual-Stream Search Resolution
        ├── 📱 TikTok Shop Viral Velocity Scraper (Short-Form Momentum)          ├── DuckDuckGo + Bing Visual Scrapers
        ├── 🛍️ Shopee Live Search Hint API (Local Market Pulses)                 └── 100% Verified High-Res Image Pipeline
        ├── 📦 Lazada Regional Consumer Demand Sensor                                           │
        ├── 🎨 Etsy Personalized Intent & Craft Signals                                         │
        └── 🏷️ eBay Historical Clearing Price Engine                                            │
                      │                                                                         │
                      └────────────────────────────────────┬────────────────────────────────────┘
                                                           ▼
                                    ┌──────────────────────────────────────────┐
                                    │   PIPELINE LÀM SẠCH & CHUẨN HÓA DỮ LIỆU  │
                                    │   - Quy đổi tỷ giá hối đoái USD chuẩn    │
                                    │   - Bóc tách Semantic Entities & Loại bỏ │
                                    │     Stopwords / Noise Tags               │
                                    │   - Round-Robin cân bằng 6 sàn tuyệt đối │
                                    └──────────────────────────────────────────┘
```

---

### 2.1. Bản Giao Hưởng Cào Dữ Liệu 6 Sàn (The 6-Marketplace Symphony)

Mỗi sàn thương mại điện tử là một hệ sinh thái riêng biệt với cấu trúc dữ liệu và hành vi người dùng độc nhất. **OmniStream Engine** điều phối 6 crawler chuyên biệt hoạt động song song với độ trễ tiệm cận Sub-Second (<1.2s):

1. **🛒 Amazon — Thước Đo Sức Mua & BSR (Best Sellers Rank)**:
   - Truy vấn trực tiếp vào giao thức **Amazon Completion Suggestion Protocol** (`completion.amazon.com`) với Client ID US (`mid=ATVPDKIKX0DER`).
   - Bóc tách ngay lập tức các Search Intent mua hàng có tỉ lệ chuyển đổi cao nhất, giá bán lẻ niêm yết ($), điểm rating và link sản phẩm thực tế có kiểm chứng.

2. **📱 TikTok Shop — Cảm Biến Cơn Sốt Viral & Video Momentum**:
   - Khai thác dữ liệu Kalodata API kết hợp các cụm từ gắn thẻ `viral niche / shop trends` từ hành vi tìm kiếm của thế hệ Gen Z.
   - Định lượng chính xác tốc độ tăng trưởng doanh số nhảy vọt (**+45% đến +96% sales growth**), số lượng sản phẩm bán ra và hàng triệu lượt video views.

3. **🛍️ Shopee — Nhịp Đập Bán Lẻ & Xu Hướng Nội Địa**:
   - Kết nối trực tiếp **Shopee Search Hint Realtime API** (`shopee.vn/api/v4/search/search_hint`).
   - Tự động quy đổi mệnh giá nội tệ sang USD, phát hiện các sản phẩm quà tặng, in ấn cá nhân hóa đang dẫn đầu xu hướng thị trường Đông Nam Á.

4. **📦 Lazada — Sóng Tiêu Dùng Khu Vực**:
   - Cào động từ endpoint **Lazada Regional Tag Cloud**, giải mã nhu cầu tiêu dùng và phân khúc giá thị trường khu vực.

5. **🎨 Etsy — Trái Tim Của Quà Tặng Cá Nhân Hóa (Personalized Gifts)**:
   - Thu thập các tín hiệu thủ công mỹ nghệ, quà tặng khắc tên, in chân dung gia đình, kỷ niệm ngày cưới (Laser Engraving, UV Acrylic).
   - Đo lường mức độ sẵn sàng chi trả của khách hàng US/EU cho sản phẩm POD có tính độc bản cao.

6. **🏷️ eBay — Mỏ Neo Giá Thị Trường & Khối Lượng Khớp Lệnh**:
   - Phân tích hàng ngàn giao dịch đã hoàn tất (Completed & Sold Listings) để xác định **Mức giá thanh khoản thực tế (Average Selling Price - ASP)**, ngăn chặn việc định giá ảo.

---

### 2.2. Động Cơ Thị Giác Resilient Image Pool (Cam Kết Không Một Điểm Ảnh Bị Lỗi)

Một sản phẩm POD không thể thuyết phục seller nếu thiếu đi hình ảnh thực tế sống động. **OmniStream Engine** sở hữu hệ thống giải mã ảnh đa nguồn:

* **Dual-Engine Visual Resolver**: Tích hợp luồng tìm kiếm hình ảnh độ phân giải cao đa tầng (DuckDuckGo Image Protocol + Bing Visual Scraper).
* **Zero-Broken-Image Architecture**: Tự động lọc ảnh hỏng, định dạng `.svg` rác hoặc ảnh lỗi bản quyền; gom toàn bộ pool ảnh cào được trong phiên để phân phối thông minh, cam kết **100% sản phẩm trên Dashboard đều có ảnh thực tế sắc nét**.

---

## 🧠 3. Kiến Trúc Chuyên Sâu: Mô Hình Toán Học, AI Agent & MCDA Engine

OpportunityOS không chỉ là công cụ tổng hợp dữ liệu, mà là một **Hệ Thống AI Agentic Đa Tầng (Multi-Agent System)** tích hợp mô hình định lượng đa tiêu chí (MCDA) chuẩn toán học.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-AGENT PIPELINE ARCHITECTURE                             │
├───────────────────────┬───────────────────────────────────┬─────────────────────────────┤
│ Agent Sub-System      │ Công nghệ & Thuật toán Cốt lõi    │ Nhiệm vụ & Đầu ra           │
├───────────────────────┼───────────────────────────────────┼─────────────────────────────┤
│ 1. Ingestion Agent    │ Async I/O, Exponential Backoff    │ Cào 2,000+ signals / <1.5s  │
│ 2. Clean IP Agent     │ Levenshtein, Jaro-Winkler, USPTO  │ Zero-Trust Trademark Guard  │
│ 3. MCDA Engine        │ Weighted Vector Sum, Sigmoid Norm │ Tính toán Opportunity Score │
│ 4. Blank Matcher Agent│ Hybrid NER + Cosine Similarity    │ Khớp mã SKU phôi Printway   │
│ 5. Synthesis Agent    │ Dynamic JSON Schema, LLM Prompts  │ Technical Brief & Ad Hooks  │
└───────────────────────┴───────────────────────────────────┴─────────────────────────────┘
```

---

### 3.1. Mô Hình Toán Học MCDA 6 Trụ Cột (Formal Mathematical Formulation)

Mỗi sản phẩm ứng viên $x$ được biểu diễn dưới dạng một vector thuộc tính $\mathbf{x} = [x_1, x_2, \dots, x_n]^T$. Điểm cơ hội $S_{\text{opp}}(\mathbf{x})$ được tính bằng tích vô hướng giữa **Vector Trọng Số Chiến Lược** $\mathbf{w}$ và **Vector Điểm Chuẩn Hóa** $\boldsymbol{\Phi}(\mathbf{x})$:

$$S_{\text{opp}}(\mathbf{x}) = \mathbf{w}^T \cdot \boldsymbol{\Phi}(\mathbf{x}) = \sum_{k=1}^{6} w_k \cdot \phi_k(x_k)$$

$$\text{Thỏa mãn ràng buộc: } \sum_{k=1}^{6} w_k = 1.0, \quad w_k \ge 0, \quad \text{và } \text{Penalty}_{\text{CleanIP}}(\mathbf{x}) = 1$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MA TRẬN TRỌNG SỐ & ĐẶC TRƯNG MCDA 6 TRỤ CỘT           │
├────────────────────────────────┬────────┬───────────────────────────────────┤
│ Trụ cột (Pillar)               │Trọng số│ Thuật toán & Hàm Mục tiêu         │
├────────────────────────────────┼────────┼───────────────────────────────────┤
│ 1. Nhu cầu & Tăng trưởng (P1)  │  25%   │ Hàm Logarit nén phi tuyến tính    │
│ 2. Biên lãi & Đệm lợi nhuận (P2)│ 20%   │ Hàm đệm Piecewise Lãi gộp & CPA   │
│ 3. Khả thi Chuỗi cung (P3)     │  15%   │ Khớp Ontology Phôi xưởng, SLA 48h │
│ 4. Mức độ Cạnh tranh (P4)      │  15%   │ Mật độ đối thủ nghịch đảo     │
│ 5. An toàn Bản quyền (P5)      │  15%   │ Binary Zero-Penalty Trademark FSM │
│ 6. Tiềm năng Viral TikTok (P6) │  10%   │ Hàm tương tác xã hội đa chiều     │
└────────────────────────────────┴────────┴───────────────────────────────────┘
```

---

### 3.2. Thuật Toán Chi Tiết Từng Trụ Cột Định Lượng

#### 1. Trụ Cột Nhu Cầu & Tăng Trưởng ($P_1$ - Trọng số: 25%)
* **Công thức toán học**:
  $$\phi_1(\mathbf{x}) = \min\left(100, \, 30 \cdot \log_{10}(V_{\text{search}} + 1) + 0.4 \cdot \Delta S_{\text{growth}} + 0.3 \cdot Q_{\text{sold}}\right)$$
* **Giải thích**: Áp dụng hàm $\log_{10}$ để nén dải dữ liệu lượng tìm kiếm (tránh hiện tượng bùng nổ phương sai do các từ khóa triệu volume lấn át các ngách tiềm năng), kết hợp đạo hàm tốc độ tăng trưởng $\Delta S_{\text{growth}}$.

#### 2. Trụ Cột Biên Lãi & Đệm Lợi Nhuận Gộp ($P_2$ - Trọng số: 20%)
* **Công thức toán học**:
  $$\text{Margin}_{\text{gross}} = \frac{P_{\text{retail}} - \text{COGS}_{\text{Printway}} - \text{Fee}_{\text{platform}}}{P_{\text{retail}}} \times 100$$
  $$\phi_2(\mathbf{x}) = \begin{cases} 95 + 5 \cdot \text{sigmoid}(\text{NetProfit} - 12) & \text{khi } \text{Margin} \ge 65\% \\ 75 + 15 \cdot \frac{\text{Margin} - 50}{15} & \text{khi } 50\% \le \text{Margin} < 65\% \\ 30 + 20 \cdot \frac{\text{Margin}}{50} & \text{khi } \text{Margin} < 50\% \end{cases}$$
* **Ý nghĩa thực chiến**: Đảm bảo seller luôn có **khung đệm lợi nhuận ròng $\ge \$12 - \$16$/sản phẩm**, đủ ngân sách chạy quảng cáo (CPA Room) mà không bị âm dòng tiền.

#### 3. Trụ Cột Khả Thi Chuỗi Cung & SLA 48h ($P_3$ - Trọng số: 15%)
* **Công thức toán học**:
  $$\phi_3(\mathbf{x}) = \text{Similarity}(\text{Entity}_{\text{crawled}}, \text{Catalog}_{\text{Printway}}) \times 0.6 + \text{SLA\_Score}(48\text{h}) \times 0.4$$
* **Ràng buộc SLA**: Phôi xưởng Printway đạt SLA chuẩn **48 giờ** giúp seller bảo vệ chỉ số hoàn tất đơn hàng (Fulfillment Rate > 98%).

#### 4. Trụ Cột Mức Độ Cạnh Tranh ($P_4$ - Trọng số: 15%)
* **Công thức toán học**:
  $$\phi_4(\mathbf{x}) = 100 - \min\left(70, \, N_{\text{competitors}} \times 3.5\right) + \text{RatingPenalty}$$

#### 5. Trụ Cột Lá Chắn Bản Quyền Clean IP ($P_5$ - Trọng số: 15%)
* **Cơ chế Máy Trạng Thái Hữu Hạn (FSM Penalty)**:
  $$\phi_5(\mathbf{x}) = \begin{cases} 100 & \text{nếu } \text{Score}_{\text{Similarity}}(\text{Keyword}, \text{Database}_{\text{USPTO}}) < \tau_{\text{safe}} \\ 0 & \text{nếu dính Trademark vi phạm (Khóa toàn bộ Opportunity Score)} \end{cases}$$

#### 6. Trụ Cột Tiềm Năng Viral TikTok ($P_6$ - Trọng số: 10%)
* **Công thức toán học**:
  $$\phi_6(\mathbf{x}) = 0.5 \cdot \text{Score}_{\text{visual}} + 0.3 \cdot \text{Score}_{\text{personalization}} + 0.2 \cdot \text{Score}_{\text{emotional}}$$

---

## 🏭 4. Thuật Toán Matching Phôi Xưởng Printway (Hybrid Semantic Matching)

Thuật toán kết hợp **Trích Xuất Thực Thể Ngữ Nghĩa (NER)** và khoảng cách **Cosine-Jaccard Hybrid** để ánh xạ chính xác sản phẩm cào sang mã phôi xưởng Printway:

```
[Crawled Product Title & Specs] 
       │
       ▼ (1. NLP Tokenizer & Material Extraction)
  {Material: "Inox 304", Capacity: "20oz", Tech: "Vacuum Insulated / Laser Engraved"}
       │
       ▼ (2. Hybrid Semantic Similarity Calculation)
  Sim(P_crawled, B_printway) = 0.65 * Cosine(e_title, e_catalog) + 0.35 * Jaccard(Tokens)
       │
       ▼ (3. Deterministic Blank Matching FSM)
  SKU Match: "PW-DRINK-TUMB-20OZ" (Confidence: 0.98)
       │
       ▼ (4. COGS & SLA 48h Binding)
  Base Cost: $8.50 | Selling Price: $29.99 | Net Unit Profit: +$16.99 (68% Margin) | SLA: 48h
```

### 📋 Bảng Danh Mục Phôi Xưởng Printway Chuẩn SLA 48 Giờ:

| Ngách Sản Phẩm | Mã Phôi Printway Chuẩn | Chất Liệu & Kỹ Thuật Gia Công | COGS Xưởng | Giá Bán Thị Trường | Lãi Ròng / SP | SLA Xưởng |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Bình giữ nhiệt 20oz/40oz** | `PW-DRINK-TUMB-20OZ` | Inox 304 hai lớp chân không · In UV / Khắc Laser | **$8.50** | $29.99 | **+$16.99 (68%)** | **48h** |
| **Đèn ngủ Mica 3D Led** | `PW-GIFT-ACRYLIC-LIGHT` | Mica quang học cao cấp · Đế gỗ sồi tự nhiên | **$6.80** | $24.99 | **+$14.44 (65%)** | **48h** |
| **Đồ trang trí Giáng Sinh** | `PW-ORNAMENT-CERAMIC` | Gốm sứ tráng men 2 mặt · Dây treo ruy băng | **$3.20** | $16.99 | **+$11.24 (73%)** | **48h** |
| **Áo thun Streetwear 250gsm** | `PW-APP-TEE-HEAVY` | 100% Cotton định lượng cao · In kỹ thuật số DTG | **$7.50** | $27.99 | **+$16.09 (63%)** | **48h** |
| **Áo Hoodie Nỉ Bông** | `PW-APP-HOODIE-FLEECE` | Nỉ bông 320gsm co giãn · Thêu vi tính / In lụa | **$14.00** | $44.99 | **+$23.24 (59%)** | **48h** |

---

## 🗂️ 5. Cấu Trúc Dự Án (Project Structure)

```
OpportunityOS/
├── BE/                                # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/                    # API Routers (/analyze, /hot-searches, /health)
│   │   ├── core/                      # Configuration, Security & Settings (.env)
│   │   ├── models/                    # Pydantic Schemas & Data Contracts
│   │   └── services/
│   │       ├── crawl/                 # Multi-platform Realtime Crawlers (6 Marketplaces)
│   │       ├── ip_check/              # Clean IP Shield (USPTO / WIPO Defense)
│   │       └── scoring/               # MCDA 6-Pillar Opportunity Scoring Engine
│   ├── Dockerfile                     # Backend Containerization
│   ├── requirements.txt               # Dependencies
│   └── main.py                        # FastAPI Entrypoint
│
├── frontend/                          # React 19 + TypeScript + Vite Frontend
│   ├── src/
│   │   ├── components/                # Responsive DataTable, Stepper, BriefModal
│   │   ├── locales/                   # I18n Vietnamese & English
│   │   ├── api.ts                     # API Client & Dynamic 6-Month Market Curve
│   │   ├── App.tsx                    # Main App Controller
│   │   └── index.css                  # Custom Dark Mode Design Tokens
│   ├── package.json                   # Dependencies
│   └── vite.config.ts                 # Bundler config
│
├── docker-compose.yml                 # Multi-service Orchestration
└── README.md                          # Project Documentation
```

---

## 🚀 6. Cài Đặt & Triển Khai Nhanh

### Cách 1: Chạy Bằng Docker Compose (Khuyên dùng)

```bash
# 1. Clone repository
git clone https://github.com/techfuture-3TL/OpportunityOS.git
cd OpportunityOS

# 2. Khởi chạy toàn bộ hệ thống
docker-compose up -d --build

# 3. Kiểm tra trạng thái
docker-compose ps
```

* **Frontend Dashboard**: `http://localhost:5173`
* **Backend Swagger API Docs**: `http://localhost:8000/docs`

---

### Cách 2: Chạy Thủ Công (Local Development)

#### 1. Khởi chạy Backend (Python 3.9+)

```bash
cd BE

# Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt

# Cấu hình biến môi trường
cp .env.example .env

# Chạy server development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Khởi chạy Frontend (Node.js 18+)

```bash
cd ../frontend

# Cài đặt dependencies
npm install

# Khởi chạy dev server
npm run dev
```

---

## 🔐 7. Cấu Hình Biến Môi Trường (Environment Variables)

Hệ thống bảo mật 100% bằng cách tách biệt toàn bộ cấu hình vào file `.env` (được liệt kê trong `.gitignore`):

```env
# Backend Environment Configuration (.env)
PROJECT_NAME="OpportunityOS"
ENV="production"
PORT=8000

# CORS Allowed Origins
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://vps.nexora-flow.cloud"]

# Optional 3rd Party APIs (Hệ thống tự động kích hoạt Live Fallback nếu không có key)
KALODATA_API_KEY=""
USPTO_API_KEY=""
GEMINI_API_KEY=""
```

---

## 📡 8. API Endpoints

### 1. Phân Tích Cơ Hội Sản Phẩm Toàn Diện
* **Endpoint**: `POST /api/v1/analyze`
* **Payload**:
```json
{
  "query": "baby first christmas ornament",
  "limit": 24,
  "sources": ["amazon", "tiktok", "shopee", "lazada", "etsy", "ebay"]
}
```

### 2. Từ Khóa Thị Trường Nóng (Live Hot Searches)
* **Endpoint**: `GET /api/v1/hot-searches?category=all`
* **Mô tả**: Trả về danh sách từ khóa có lượng tìm kiếm tăng vọt kèm link kiểm chứng trực tiếp trên từng sàn.

### 3. Kiểm Tra Trạng Thái Hệ Thống (Health Check)
* **Endpoint**: `GET /api/v1/health`

---

## 👥 9. Đội Ngũ Phát Triển (Team 3TL - TechFuture)

Dự án được xây dựng và tối ưu trong khuôn khổ cuộc thi **Printway Hackathon 2026**.

* 🏆 **Định hướng sản phẩm**: AI Agent Driven E-Commerce Intelligence.
* 🌐 **Mã nguồn**: [https://github.com/techfuture-3TL/OpportunityOS](https://github.com/techfuture-3TL/OpportunityOS)
* 📄 **Bản quyền**: Phát hành theo giấy phép [MIT License](LICENSE).
