# 💰 BÁO CÁO 04: MÔ HÌNH TÀI CHÍNH & KINH TẾ ĐƠN VỊ
## Dự án: PW1 - Product Opportunity Hub (Printway R&D AI Copilot)

---

## 1. Phương Trình Dòng Tiền Đơn Vị Sản Phẩm (Unit Economics)

Để đảm bảo mỗi cơ hội được đề xuất mang lại lợi nhuận thực tế, hệ thống mô hình hóa phương trình dòng tiền trên từng đơn vị sản phẩm:

\[
\Pi_{\text{unit}} = P_{\text{retail}} - \text{COGS}_{\text{Printway}} - \text{Fee}_{\text{Platform}} - \text{CPA}_{\text{Ads}} - \text{Shipping}
\]

Trong đó:
* $P_{\text{retail}}$: Giá bán lẻ đề xuất trên thị trường (USD).
* $\text{COGS}_{\text{Printway}}$: Giá vốn phôi in từ hệ thống xưởng Printway (USD).
* $\text{Fee}_{\text{Platform}}$: Phí sàn thương mại điện tử (TikTok Shop $\approx 5\%$, Etsy $\approx 6.5\%$).
* $\text{CPA}_{\text{Ads}}$: Chi phí để có 1 đơn hàng qua TikTok Shop Spark Ads.
* $\text{Shipping}$: Phí vận chuyển nội địa US (qua kho US Printway chỉ \$3.99 - \$5.50).

---

## 2. Công Thức Tính Điểm Hòa Vốn (Break-Even Analysis)

Với ngân sách thử nghiệm ban đầu của Seller là $B_{\text{test}}$ (ví dụ: $\$1,000$ tiền chạy Ads):

Số lượng sản phẩm cần bán để hoàn vốn:
\[
Q_{\text{Break-Even}} = \frac{B_{\text{test}}}{P_{\text{retail}} - \text{COGS}_{\text{Printway}}}
\]

### Ví dụ Thực Tế:
* Sản phẩm: **Personalized Pickleball 20oz Tumbler (`PW-DRINK-TUMB-20OZ`)**
* $\text{COGS}_{\text{Printway}} = \$7.80$ | $P_{\text{retail}} = \$29.99$
* Lãi gộp trên từng đơn vị: $\text{Gross Profit} = \$29.99 - \$7.80 = \$22.19$ (Biên lãi: **$74.0\%$**)
* Với ngân sách chạy thử nghiệm $B_{\text{test}} = \$1,000$:
  \[
  Q_{\text{Break-Even}} = \frac{1000}{22.19} \approx 45.06 \text{ sản phẩm}
  \]
  $\implies$ Seller chỉ cần bán được **46 chiếc ly** là đã hoàn vốn toàn bộ chiến dịch quảng cáo!

---

## 3. Bảng Phân Tích Độ Nhạy Lợi Nhuận (Sensitivity Matrix)

| Giá Bán Lẻ ($P_{\text{retail}}$) | Giá Phôi Printway | CPA Ads: $5 | CPA Ads: $8 | CPA Ads: $12 | CPA Ads: $15 | Đánh Giá Tính Khả Thi |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$24.99** | $7.80 | +$12.19 | +$9.19 | +$5.19 | +$2.19 | Khả thi (Biên an toàn trung bình) |
| **$29.99** *(Đề xuất)* | $7.80 | **+$17.19** | **+$14.19** | **+$10.19** | **+$7.19** | **LÝ TƯỞNG (Biên an toàn cực dày)** |
| **$34.99** *(Khắc tên CLB)*| $7.80 | +$22.19 | +$19.19 | +$15.19 | +$12.19 | Siêu lợi nhuận cho sản phẩm ngách VIP |

---

## 4. Phân Bổ Ngân Sách Tiếp Thị 4 Giai Đoạn

```
┌────────────────────────────────────────────────────────────────────────┐
│ TỔNG NGÂN SÁCH THỬ NGHIỆM: $1,000 USD                                  │
├──────────────────┬─────────────────┬─────────────────┬─────────────────┤
│ PHASE 1: SEEDING │ PHASE 2: LAUNCH │ PHASE 3: UGC    │ PHASE 4: SCALE  │
│ 15% ($150)       │ 35% ($350)      │ 20% ($200)      │ 30% ($300)      │
│ • Gửi 15 mẫu phôi│ • Chạy 3 Video  │ • Hashtag video │ • Bật Spark Ads │
│   thật cho KOLs  │   Hooks TikTok  │   từ khách hàng │   scale ads win │
└──────────────────┴─────────────────┴─────────────────┴─────────────────┘
```
