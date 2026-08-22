# 🔬 BÁO CÁO 01: PHƯƠNG PHÁP LUẬN TOÁN HỌC & CÔNG THỨC CHẤM ĐIỂM (NÂNG CẤP ĐA BIẾN)
## Dự án: PW1 - Product Opportunity Hub (Printway R&D AI Copilot)

---

## 1. Cơ Sở Lý Thuyết Ra Quyết Định Đa Tiêu Chuẩn (MCDA / MADM)

Hệ thống sử dụng mô hình **Multi-Criteria Decision Analysis (MCDA)** kết hợp chuẩn hóa phi tuyến **Sigmoid Activation**:

\[
S(x_i) = \sum_{k=1}^{6} w_k \cdot S_k(x_i), \quad \text{với } \sum_{k=1}^{6} w_k = 1.0
\]

---

## 2. Công Thức Giải Tích Nâng Cấp 6 Trụ Cột Thành Phần ($S_1 \to S_6$)

### 2.1. Trụ cột 1: $S_{\text{Demand}}$ — Mô Hình Z-Score Đa Biến & Sigmoid
Kết hợp 4 tham số dữ liệu thực tế: `growth` ($g$), `trend` ($T$), `demand` ($D$) và `buyer_intent` ($M_{\text{intent}}$):
\[
Z_{\text{composite}} = 0.40 \left(\frac{g - 50}{40}\right) + 0.25 \left(\frac{T - 50}{25}\right) + 0.20 \left(\frac{D - 50}{25}\right) + 0.15 \left(\frac{V - 50}{25}\right)
\]
\[
S_{\text{Demand}} = 100 \times \frac{1}{1 + e^{-Z_{\text{composite}}}} \times M_{\text{intent}}
\]
* Ý định mua hàng cao (`buyer_intent == "HIGH"`) $\implies M_{\text{intent}} = 1.10$.

---

### 2.2. Trụ cột 2: $S_{\text{Gap}}$ — Chỉ Số Thất Vọng Khách Hàng (CDI) & Bão Hòa Ngách
\[
S_{\text{Gap}} = 0.35 \cdot \max(0, 100 - \text{Competition}) + 0.35 \cdot \text{Opportunity} + \min(30, N_{\text{reviews}} \times 10) + \Delta_{\text{PainMatch}}
\]
* Khắc phục trực tiếp lỗi đối thủ bằng phôi xưởng Printway: $\Delta_{\text{PainMatch}} = +15.0$.

---

### 2.3. Trụ cột 3: $S_{\text{Margin}}$ — Mô Hình Lợi Nhuận Kép (% Margin + Đệm Tiền Lãi $)
\[
S_{\text{Margin}} = 0.60 \cdot \text{Score}_{\text{Margin}\%} + 0.40 \cdot \min\left(100, \frac{\text{Profit}_{\$}}{20.0} \times 100\right)
\]
* Đảm bảo Seller vừa có % lãi gộp cao ($> 70\%$) vừa có số tiền lãi tuyệt đối ($> \$15 - \$20$) để chịu được chi phí chạy TikTok Ads (\$8 - \$10 CPA).

---

### 2.4. Trụ cột 4: $S_{\text{Supply}}$ — Mô Hình Đáp Ứng Vận Tải & Khả Năng Gia Công
\[
S_{\text{Supply}} = 0.45 \cdot S_{\text{Warehouse}} + 0.30 \cdot S_{\text{Technique}} + 0.25 \cdot \max(0, 100 - \max(0, \text{SLA} - 2) \times 15)
\]
* Kho US nội địa (ship 2-5 ngày) = $100$ điểm; Kho VN/Global = $70$ điểm.

---

### 2.5. Trụ cột 5: $S_{\text{Safety}}$ — Ma Trận Đánh Giá Rủi Ro Bản Quyền Đa Tầng
* **Tier 1 (Vi phạm nhãn hiệu USPTO):** Tên thương hiệu đăng ký (Disney, Snoopy, Martha Stewart...) $\implies S_{\text{Safety}} = 35.0$.
* **Tier 2 (Rủi ro trung bình):** Tên phim, nhân vật giải trí $\implies S_{\text{Safety}} = 60.0$.
* **Tier 3 (An toàn sạch 100%):** Từ khóa generic POD $\implies S_{\text{Safety}} = 96.0 - 100.0$.

---

### 2.6. Trụ cột 6: $S_{\text{Virality}}$ — Chỉ Số Tác Động Thị Giác (Visual Hook Index)
\[
S_{\text{Virality}} = 50.0 + 20.0 \cdot I(\text{Personalized}) + 18.0 \cdot I(\text{LED/Laser/Glow}) + 12.0 \cdot I(\text{GenZ Aesthetic})
\]
