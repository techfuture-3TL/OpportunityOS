# 🐳 BÁO CÁO 08: HƯỚNG DẪN ĐÓNG GÓI & KHỞI CHẠY DOCKER
## Dự án: PW1 - Product Opportunity Hub (Printway R&D AI Copilot)

---

## 🚀 1. Lệnh Khởi Chạy Nhanh (Chỉ 1 Câu Lệnh)

Mở Terminal tại thư mục `C:\hackathon\` và gõ:

```bash
docker compose up --build -d
```

Sau khi chạy:
* 🌐 **API Base URL:** `http://localhost:8000/api/v1`
* 📑 **Swagger API Docs trực quan:** `http://localhost:8000/docs`
* 💚 **Trạng thái Healthcheck:** `http://localhost:8000/api/v1/health`

---

## 🛠️ 2. Các Lệnh Quản Lý Container & Chạy Test

```bash
# Xem log hoạt động thời gian thực
docker compose logs -f

# Chạy test suite trực tiếp BÊN TRONG container Docker
docker compose exec pw1-backend python tests/test_api_pipeline.py

# Dừng container khi không dùng
docker compose down
```

---

## ⚙️ 3. Cấu Hình Biến Môi Trường Sẵn Sàng

```env
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```
