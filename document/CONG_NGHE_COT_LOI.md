# ⚙️ CÔNG NGHỆ CỐT LÕI
## Dự án: PW1 - Product Opportunity Hub (Printway R&D AI Copilot)
### HN AI Hackathon 2026

---

## 📐 MÔ HÌNH TỔNG: MCDA ĐA BIẾN

$$S_{\text{Total}} = \sum_{k=1}^{6} w_k \cdot S_k \in [0, 100], \quad \sum_{k=1}^{6} w_k = 1.0$$

---

## 1️⃣ $S_{\text{Demand}}$ — Nhu Cầu Thị Trường (Z-Score + Sigmoid)

$$Z = 0.40 \cdot \frac{g_{\text{sales}} - 50}{40} + 0.25 \cdot \frac{T_{\text{Google}} - 50}{25} + 0.20 \cdot \frac{D_{\text{volume}} - 50}{25} + 0.15 \cdot \frac{V_{\text{velocity}} - 50}{25}$$

$$S_{\text{Demand}} = 100 \cdot \sigma(Z) \cdot M_{\text{intent}}, \quad \sigma(Z) = \frac{1}{1 + e^{-Z}}$$

* $M_{\text{intent}} = 1.10$ nếu `buyer_intent = HIGH` | $= 0.90$ nếu `LOW` | $= 1.00$ nếu `MEDIUM`
* Hàm **Sigmoid** đảm bảo điểm không bao giờ chạm 0 hay 100 do một biến ngoại lai gây ra.

---

## 2️⃣ $S_{\text{Gap}}$ — Khoảng Trống Thị Trường (CDI - Customer Disappointment Index)

$$S_{\text{Gap}} = 0.35 \cdot (100 - C_{\text{comp}}) + 0.35 \cdot O_{\text{index}} + \min(30,\ N_{\text{reviews}} \times 10) + \Delta_{\text{PainMatch}}$$

* $C_{\text{comp}}$: Chỉ số cạnh tranh lấy trực tiếp từ cột `competition` trong CSV.
* $O_{\text{index}}$: Chỉ số cơ hội lấy từ cột `opportunity` trong CSV.
* $N_{\text{reviews}}$: Số cụm nỗi đau được bóc tách từ review 1-3 sao của đối thủ.
* $\Delta_{\text{PainMatch}} = +15$ điểm nếu phôi xưởng Printway giải quyết đúng nỗi đau đó.

---

## 3️⃣ $S_{\text{Margin}}$ — Lợi Nhuận Kép (% Margin + Đệm Tiền Lãi $)

$$\text{Margin\%} = \frac{P_{\text{retail}} - \text{COGS}}{P_{\text{retail}}} \times 100\%$$

$$\text{Score}_{\text{Margin\%}} = \frac{\text{Margin\%} - 50}{75 - 50} \times 100$$

$$S_{\text{Margin}} = 0.60 \cdot \text{Score}_{\text{Margin\%}} + 0.40 \cdot \min\!\left(100,\ \frac{\text{Profit}_{\$}}{20} \times 100\right)$$

* Nếu $\text{Margin\%} < 50\% \Rightarrow S_{\text{Margin}} = 0$ (loại ngay từ Lớp 1).
* Yêu cầu tiền lãi tuyệt đối $\ge \$15 - \$20$ để đủ sức gánh chi phí quảng cáo TikTok Ads (\$8 - \$10 CPA).

---

## 4️⃣ $S_{\text{Supply}}$ — Chuỗi Cung Ứng Xưởng Printway

$$S_{\text{Supply}} = 0.45 \cdot S_{\text{Kho}} + 0.30 \cdot S_{\text{KyThuat}} + 0.25 \cdot \max\!\left(0,\ 100 - \max(0,\ \text{SLA} - 2) \times 15\right)$$

| Thành Phần | Điểm Tối Đa | Điều Kiện |
| :--- | :---: | :--- |
| $S_{\text{Kho}}$ (Vị trí kho) | 100 | Kho US Domestic (ship 2-5 ngày) = 100 \| Kho VN/Global = 70 |
| $S_{\text{KyThuat}}$ (Kỹ thuật in) | 100 | Khớp Laser / UV / DTG = 100 \| Không khớp = 50 |
| SLA Sản Xuất | 100 | $\le 2$ ngày = 100 \| Mỗi ngày vượt quá bị trừ 15 điểm |

---

## 5️⃣ $S_{\text{Safety}}$ — Bảo Vệ Bản Quyền (3 Cấp Rủi Ro Pháp Lý)

$$S_{\text{Safety}} = \begin{cases} 35.0 & \text{Tier 1: Vi phạm nhãn hiệu lớn USPTO (Disney, Nike, Snoopy, Martha Stewart...)} \\ 60.0 & \text{Tier 2: Rủi ro trung bình (tên phim, nhân vật giải trí)} \\ 96.0 - 100.0 & \text{Tier 3: Sạch hoàn toàn — Generic POD Keyword} \end{cases}$$

**Thuật toán phát hiện biến thể cố ý viết sai (Levenshtein Guard):**

$$\text{Sim}(s_1, s_2) = 1 - \frac{\text{Levenshtein}(s_1, s_2)}{\max(|s_1|, |s_2|)} \ge 0.85 \Rightarrow \text{TRADEMARK\_ALERT}$$

Ví dụ bắt được: *Snooppy, Disnney, Starbuckss, Nikee* → Cờ cảnh báo đỏ 🔴

---

## 6️⃣ $S_{\text{Virality}}$ — Ăn Hình TikTok (Visual Hook Index - VHI)

$$S_{\text{Virality}} = 50 + 20 \cdot I_{\text{Personalized}} + 18 \cdot I_{\text{LED/Laser/Glow}} + 12 \cdot I_{\text{GenZ\_Aesthetic}}$$

| Yếu Tố Thị Giác | Điểm Cộng | Lý Do |
| :--- | :---: | :--- |
| Cá nhân hóa tên riêng / năm sinh | +20 | Tăng thời gian giữ chân xem video (Watch Time) |
| Hiệu ứng Laser đổi màu / LED phát sáng | +18 | "Wow moment" → Tăng tỷ lệ Shares & Comments |
| Gu thẩm mỹ Gen Z 2026 đang trending | +12 | Tăng tỷ lệ For You Page (FYP) xuất hiện tự nhiên |

---

## ⚡ MA TRẬN TRỌNG SỐ 5 CHIẾN LƯỢC R&D

| Chiến Lược | $w_{\text{Demand}}$ | $w_{\text{Gap}}$ | $w_{\text{Margin}}$ | $w_{\text{Supply}}$ | $w_{\text{Safety}}$ | $w_{\text{Virality}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `VIRAL_TREND` — Bắt Hot Trend TikTok | **0.35** | 0.15 | 0.15 | 0.10 | 0.10 | **0.15** |
| `HIGH_MARGIN` — Lợi Nhuận Gộp Dày | 0.20 | 0.15 | **0.40** | 0.10 | 0.10 | 0.05 |
| `SAFE_EVERGREEN` — Ổn Định & An Toàn | 0.15 | 0.20 | 0.20 | **0.20** | **0.20** | 0.05 |
| `LOW_COMPETITION` — Khai Thác Ngách | 0.20 | **0.40** | 0.15 | 0.10 | 0.10 | 0.05 |
| `CUSTOM_WEIGHTS` — Tùy Chỉnh Seller | $w_1$ | $w_2$ | $w_3$ | $w_4$ | $w_5$ | $w_6$ |

---

## 💰 KINH TẾ ĐƠN VỊ & ĐIỂM HÒA VỐN

**Phương trình dòng tiền đơn vị:**

$$\Pi_{\text{unit}} = P_{\text{retail}} - \text{COGS} - \text{Fee}_{\text{Platform}} - \text{CPA}_{\text{Ads}} - \text{Shipping}$$

**Điểm hòa vốn chạy Ads:**

$$Q_{\text{Hòa Vốn}} = \frac{B_{\text{Ads}}}{\Pi_{\text{unit}}}$$

**Ví dụ thực tế — Personalized Pickleball Tumbler (Top 1 Winner):**

| Chỉ Số | Giá Trị | Ghi Chú |
| :--- | :---: | :--- |
| Giá phôi Printway (`COGS`) | \$7.80 | Inox 304 Laser Engraving |
| Giá bán đề xuất ($P_{\text{retail}}$) | \$29.99 | TikTok Shop US |
| Tiền lãi gộp ($\Pi_{\text{unit}}$) | **+\$22.19** | Biên lãi **74.0%** |
| Ngân sách thử Ads ($B_{\text{Ads}}$) | \$1,000 | TikTok Spark Ads |
| Số sản phẩm cần bán để hòa vốn | **46 chiếc** | $1000 \div 22.19 = 45.07$ |

---

## 🏗️ KIẾN TRÚC LUỒNG XỬ LÝ 3 LỚP (TRI-LAYER HYBRID FUSION)

```
2,092 DÒNG DỮ LIỆU TỪ KHÓA PRINTWAY
              │
              ▼
┌─────────────────────────────────────────────────┐
│ LỚP 1: BỘ LỌC CỨNG                              │
│ ⚡ Tốc độ: < 2 mili-giây   │   Chi phí: $0.00   │
│ Loại: COGS > giới hạn, Margin < min,            │
│        Kỹ thuật in không khớp, Trademark Alert  │
└─────────────────────┬───────────────────────────┘
                      │ ~50 - 100 sản phẩm còn lại
                      ▼
┌─────────────────────────────────────────────────┐
│ LỚP 2: MA TRẬN CHẤM ĐIỂM 6 TRỤ CỘT             │
│ 📊 Tốc độ: < 1 mili-giây  │  Chi phí: $0.00    │
│ Tính S_Total, Sắp xếp Top Cơ Hội Vàng           │
└─────────────────────┬───────────────────────────┘
                      │ Top 1 - 5 Cơ Hội Vàng
                      ▼
┌─────────────────────────────────────────────────┐
│ LỚP 3: TỔNG HỢP AI DEEPSEEK (deepseek-v4-flash) │
│ 🤖 Tốc độ: ~1.5 giây   │  Lazy Invocation       │
│ Sinh Prompt Midjourney + Kịch bản TikTok Ads     │
└─────────────────────────────────────────────────┘
```

**Tiết kiệm token: 99.8%** — Chỉ gọi AI khi Seller bấm xem chi tiết sản phẩm Top.
