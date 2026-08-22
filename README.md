# ⚡ OpportunityOS — Next-Gen AI Opportunity Engine for Print-On-Demand (POD)

<div align="center">

![OpportunityOS Banner](https://img.shields.io/badge/OpportunityOS-Printway%20Hackathon%202026-dc2626?style=for-the-badge&logo=rocket)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)

**Hệ điều hành AI Agent tự động phát hiện cơ hội, thẩm định bản quyền Clean IP 3 tầng, tính toán mô hình định lượng đa tiêu chí MCDA 6 trụ cột và khớp lệnh phôi xưởng Printway chuẩn SLA 48h chỉ trong 30 giây.**

[Trải nghiệm Trực tiếp](#-cài-đặt--triển-khai-nhanh) • [Mô hình AI & Toán học](#-chi-tiết-mô-hình-toán-học--ai-engine) • [Thuật toán Matching Printway](#-thuật-toán-matching-phôi-xưởng-printway) • [Tài liệu API](#-api-endpoints)

</div>

---

## 📌 1. Bối Cảnh & Vấn Đề (Problem Statement)

Ngành **Print-On-Demand (POD)** toàn cầu đang đối mặt với 4 "nút thắt cổ chai" chí mạng:

1. **Thử & Sai Tốn Kém (High Trial & Error Costs)**: Seller mất từ **$500 – $2,000** tiền chạy ads thử nghiệm cho mỗi sản phẩm mới chỉ để kiểm tra dung lượng thị trường.
2. **Rủi Ro "Chết Store" Do Bản Quyền (IP & Trademark Bans)**: Hơn **40%** tài khoản Etsy/Amazon/TikTok Shop bị khóa vĩnh viễn do dính nhãn hiệu đã đăng ký (USPTO/WIPO).
3. **Phân Mảnh Dữ Liệu Sàn (Marketplace Fragmentation)**: Dữ liệu bị phân mảnh trên nhiều sàn (Amazon, TikTok Shop, Shopee, Lazada, Etsy, eBay) mà không có công cụ hợp nhất.
4. **Lệch Pha Chuỗi Cung Ứng & Phôi Xưởng (Supply Chain Mismatch)**: Sản phẩm tìm thấy trên mạng không có phôi phù hợp, SLA sản xuất quá dài (>7 ngày) dẫn đến tỉ lệ hủy đơn cao.

---

## 🧠 2. Chi Tiết Mô Hình Toán Học & AI Engine

OpportunityOS vận hành trên nền tảng **Hệ thống Ra Quyết Định Đa Tiêu Chí (Multi-Criteria Decision Analysis - MCDA)** kết hợp mô hình học máy và phân tích ngữ nghĩa đa tầng.

### 2.1. Công thức Tổng quát Điểm Cơ Hội ($S_{opp}$)

$$\text{Opportunity Score } (S_{opp}) = \sum_{i=1}^{6} w_i \cdot P_i \quad \text{với } \sum w_i = 1.0$$

Trong đó, $P_i \in [0, 100]$ là điểm chuẩn hóa của từng trụ cột và $w_i$ là trọng số chiến lược:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MÔ HÌNH ĐỊNH LƯỢNG MCDA 6 TRỤ CỘT                     │
├────────────────────────────────┬────────┬───────────────────────────────────┤
│ Trụ cột (Pillar)               │Trọng số│ Phương pháp tính toán & Định lượng│
├────────────────────────────────┼────────┼───────────────────────────────────┤
│ 1. Nhu cầu & Tăng trưởng (D&G) │  25%   │ Volume tìm kiếm, Tốc độ tăng sales│
│ 2. Biên lãi & Đệm lợi nhuận    │  20%   │ Margin %, Gross Profit, Khung CPA │
│ 3. Khả thi Chuỗi cung (Printway)│ 15%   │ Độ khớp SKU phôi xưởng, SLA 48h   │
│ 4. Mức độ Cạnh tranh (Comp)    │  15%   │ Mật độ đối thủ trực tiếp & Review │
│ 5. An toàn Bản quyền (Clean IP)│  15%   │ Quét nhãn hiệu USPTO/WIPO 3 tầng  │
│ 6. Tiềm năng Viral TikTok      │  10%   │ Chỉ số visual hooks & viral video │
└────────────────────────────────┴────────┴───────────────────────────────────┘
```

---

### 2.2. Chi Tiết 6 Trụ Cột Đánh Giá

#### 1. Trụ Cột Nhu Cầu & Tăng Trưởng ($P_1$ - Trọng số: 25%)
* **Định nghĩa**: Đo lường sức mua thực tế và độ nóng của từ khóa trên cả 6 sàn TMĐT.
* **Công thức**:
  $$P_1 = \min\left(100, \, 30 \cdot \log_{10}(V_{\text{search}} + 1) + 0.4 \cdot \Delta S_{\text{growth}} + 0.3 \cdot Q_{\text{sold}}\right)$$
* **Ý nghĩa thực chiến**: Đảm bảo sản phẩm có dòng người mua thực tế, không bị "đu đỉnh trend ảo".

#### 2. Trụ Cột Biên Lãi & Đệm Lợi Nhuận Gộp ($P_2$ - Trọng số: 20%)
* **Định nghĩa**: Tính toán đệm lợi nhuận để seller có đủ biên độ chi trả chi phí quảng cáo (Facebook Ads, TikTok Ads, Etsy Ads).
* **Công thức**:
  $$\text{Margin} = \frac{P_{\text{retail}} - \text{COGS}_{\text{Printway}} - \text{Fee}_{\text{platform}}}{P_{\text{retail}}} \times 100$$

  $$P_2 = \begin{cases} 95 + \text{Bonus} & \text{khi Margin } \ge 65\% \text{ và Net Profit } \ge 12\text{ USD} \\ 75 \to 90 & \text{khi Margin } 50\% - 64\% \\ 30 \to 50 & \text{khi Margin } < 40\% \end{cases}$$

#### 3. Trụ Cột Khả Thi Chuỗi Cung Printway ($P_3$ - Trọng số: 15%)
* **Định nghĩa**: Kiểm tra độ sẵn sàng của phôi xưởng Printway, vật liệu gia công và cam kết **SLA 48h**.
* **Công thức**:
  $$P_3 = \text{MatchScore}(\text{Catalog}_{\text{Printway}}) \times 0.6 + \text{SLAScore}(48\text{h}) \times 0.4$$
* **Tiêu chuẩn**: SLA sản xuất tiêu chuẩn **48 giờ** giúp seller đạt chỉ số vận chuyển xuất sắc trên TikTok Shop & Amazon.

#### 4. Trụ Cột Mức Độ Cạnh Tranh ($P_4$ - Trọng số: 15%)
* **Định nghĩa**: Đánh giá số lượng đối thủ cạnh tranh trực tiếp cùng ngách và điểm xếp hạng trung bình.
* **Công thức**:
  $$P_4 = 100 - \min(70, \, N_{\text{competitors}} \times 3.5) + \text{ReviewPenalty}$$

#### 5. Trụ Cột Lá Chắn Bản Quyền Clean IP ($P_5$ - Trọng số: 15%)
* **Định nghĩa**: Kiểm tra đối soát 3 tầng đối với từ khóa thương hiệu, danh mục nhãn hiệu đăng ký (USPTO Class 025, 021, 028) và WIPO.
* **Cơ chế Penalty**: Nếu phát hiện Trademark vi phạm $\to P_5 = 0$, lập tức đánh cờ cảnh báo đỏ `Flagged: Trademark Risk`.

#### 6. Trụ Cột Tiềm Năng Viral TikTok ($P_6$ - Trọng số: 10%)
* **Định nghĩa**: Đánh giá tính trực quan (visual appeal), khả năng cá nhân hóa (Personalization) và tính cảm xúc (Emotional Gift) phù hợp với video ngắn.

---

## 🏭 3. Thuật Toán Matching Phôi Xưởng Printway (SLA 48h)

Hệ thống sử dụng pipeline **Semantic Entity Extraction & Jaccard-Cosine Hybrid Distance** để bóc tách thông số sản phẩm cào từ sàn và khớp trực tiếp với catalog phôi xưởng Printway:

```
[Sản phẩm cào từ Sàn TMĐT]
    │
    ├── 1. Phân tích Ngữ nghĩa (NLP Tokenizer & Attribute Parser)
    │      └── Trích xuất: Title, Category, Keywords, Material, Print Type
    │
    ├── 2. Khớp Fuzzy & Cosine Similarity với Catalog Phôi Printway
    │      ├── Inox 304, Vacuum Insulated ──> PW-DRINK-TUMB-20OZ
    │      ├── Acrylic, 3D Night Lamp    ──> PW-GIFT-ACRYLIC-LIGHT
    │      ├── Ceramic, Hanging Ribbon   ──> PW-ORNAMENT-CERAMIC
    │      └── Heavy Cotton 250gsm       ──> PW-APP-TEE-HEAVY
    │
    ├── 3. Ràng buộc Chi Phí Gốc (COGS) & SLA Xưởng Chuẩn 48h
    │      └── Tự động gán Base Cost, Kỹ thuật in UV / DTG / Khắc Laser
    │
    └── 4. Tính toán Đệm Lợi Nhuận Gộp & Đồ thị Biến động Giá 6 Tháng
```

### 📋 Bảng Quy Chuẩn Phôi Xưởng Printway (Standard SLA 48h):

| Ngách Sản Phẩm | Mã Phôi Printway Chuẩn | Chất Liệu & Kỹ Thuật In | COGS Xưởng | Giá Bán Thị Trường | Lãi Ròng / SP | SLA Xưởng |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Bình giữ nhiệt 20oz/40oz** | `PW-DRINK-TUMB-20OZ` | Inox 304 hai lớp chân không · In UV / Khắc Laser | **$8.50** | $29.99 | **+$16.99 (68%)** | **48h** |
| **Đèn ngủ Mica 3D Led** | `PW-GIFT-ACRYLIC-LIGHT` | Mica quang học cao cấp · Đế gỗ sồi tự nhiên | **$6.80** | $24.99 | **+$14.44 (65%)** | **48h** |
| **Đồ trang trí Giáng Sinh** | `PW-ORNAMENT-CERAMIC` | Gốm sứ tráng men 2 mặt · Dây treo ruy băng | **$3.20** | $16.99 | **+$11.24 (73%)** | **48h** |
| **Áo thun Streetwear 250gsm** | `PW-APP-TEE-HEAVY` | 100% Cotton định lượng cao · In kỹ thuật số DTG | **$7.50** | $27.99 | **+$16.09 (63%)** | **48h** |
| **Áo Hoodie Nỉ Bông** | `PW-APP-HOODIE-FLEECE` | Nỉ bông 320gsm co giãn · Thêu vi tính / In lụa | **$14.00** | $44.99 | **+$23.24 (59%)** | **48h** |

---

## 🗂️ 4. Cấu Trúc Dự Án (Project Structure)

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

## 🚀 5. Cài Đặt & Triển Khai Nhanh

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

## 🔐 6. Cấu Hình Biến Môi Trường (Environment Variables)

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

## 📡 7. API Endpoints

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

## 👥 8. Đội Ngũ Phát Triển (Team 3TL - TechFuture)

Dự án được xây dựng và tối ưu trong khuôn khổ cuộc thi **Printway Hackathon 2026**.

* 🏆 **Định hướng sản phẩm**: AI Agent Driven E-Commerce Intelligence.
* 🌐 **Mã nguồn**: [https://github.com/techfuture-3TL/OpportunityOS](https://github.com/techfuture-3TL/OpportunityOS)
* 📄 **Bản quyền**: Phát hành theo giấy phép [MIT License](LICENSE).
