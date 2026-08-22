# 🧠 BÁO CÁO 02: BÓC TÁCH REVIEW NỖI ĐAU & BẢO VỆ BẢN QUYỀN
## Dự án: PW1 - Product Opportunity Hub (Printway R&D AI Copilot)

---

## 1. Phương Pháp Khai Phá Nỗi Đau Khách Hàng (Aspect-Based Review Mining)

Khi khách hàng mua sản phẩm POD trên Amazon/TikTok Shop và để lại đánh giá 1-3 sao, họ phàn nàn về các khía cạnh cụ thể (Aspects). Hệ thống bóc tách các khía cạnh tiêu cực này và tự động đối soát với phôi xưởng Printway:

```
┌──────────────────────────────────────────────┐
│ Review 1-3★ của Đối Thủ:                     │
│ "The printed design peeled off after 2 washes│
│ in the dishwasher. Mug feels cheap & thin."  │
└──────────────────────┬───────────────────────┘
                       │
         [ ASPECT EXTRACTION (ABSA) ]
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[Aspect 1: ĐỘ BỀN HÌNH IN]     [Aspect 2: CHẤT LIỆU PHÔI]
• Vấn đề: Tróc sơn sau khi rửa • Vấn đề: Mỏng, dễ vỡ
• Cường độ tiêu cực: -0.92     • Cường độ tiêu cực: -0.85
       │                               │
       └───────────────┬───────────────┘
                       │
         [ PAIN-TO-FEATURE MATCHING ]
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ GIẢI PHÁP PHÔI PRINTWAY:                     │
│ • Thay bằng Inox 304 hai lớp cách nhiệt      │
│ • Khắc Laser chìm vĩnh viễn (Laser Engraving)│
│ ➔ 100% không bao giờ tróc sơn khi rửa        │
└──────────────────────────────────────────────┘
```

---

## 2. Ma Trận So Khớp "Nỗi Đau Đối Thủ ➔ Tính Năng Phôi Printway"

| Nỗi Đau Phổ Biến Của Đối Thủ (Review Mining) | Mã Phôi Printway Khắc Phục | Kỹ Thuật Gia Công Giải Quyết | Hiệu Quả Cải Tiến |
| :--- | :--- | :--- | :--- |
| **"Hình in dán đề can bị bong tróc, phai màu"** | `PW-DRINK-TUMB-20OZ` | **Khắc Laser vĩnh viễn (Laser Engraving)** | Khắc chìm vào kim loại Inox 304, rửa máy tiệt trùng không bao giờ phai. |
| **"Cốc sứ mỏng, nứt vỡ khi rót nước sôi"** | `PW-DRINK-MUG-15OZ` | **Gốm sứ tráng men cao cấp (Sublimation)** | Gốm sứ dày 4mm chịu nhiệt cao, cầm đầm tay. |
| **"Áo thun mỏng dính, giặt bị co rút và xù lông"** | `PW-APP-TEE-HEAVY` | **100% Ring-spun Cotton 240 GSM (DTG)** | Vải cotton dệt dày dặn, đứng form chuẩn Streetwear Mỹ. |
| **"Đèn mica dễ trầy xước, ánh sáng chói mắt"** | `PW-GIFT-ACRYLIC-LIGHT` | **Mica Acrylic quang học 5mm + LED Đế Gỗ** | Acrylic đúc nguyên khối chống xước, ánh sáng vàng ấm 3000K bảo vệ mắt. |
| **"Vòng cổ thú cưng bằng vải dù dễ đứt, cọ xát đau cổ"** | `PW-PET-LEATHER-COLLAR` | **Da bò thật cao cấp + Bảng tên đồng khắc laser** | Da thuộc mềm êm ái, khóa hợp kim chịu lực kéo 50kg. |

---

## 3. Thuật Toán Kiểm Duyệt Bản Quyền & Nhãn Hiệu (IP & Trademark Guard)

### 3.1. Cơ Chế Phát Hiện Vi Phạm 2 Lớp:
1. **Đối soát từ điển nhãn hiệu TMĐT (Dictionary Matching):**  
   Đối soát tức thời với kho từ điển nhãn hiệu (*Disney, Marvel, Snoopy, Martha Stewart, Pottery Barn, Target, Starbucks, Nike, Lego...*).
2. **Khoảng cách chỉnh sửa Levenshtein Distance:**  
   Bắt các biến thể cố tình viết sai chính tả để lách luật (e.g. *Snooppy, Disnney, Starbuckss*):
   \[
   \text{Sim}(s_1, s_2) = 1.0 - \frac{\text{Levenshtein}(s_1, s_2)}{\max(|s_1|, |s_2|)}
   \]
   Nếu $\text{Sim} \ge 0.85 \implies$ Cảnh báo `TRADEMARK_ALERT`.

### 3.2. Bảng Phân Loại Trạng Thái Bản Quyền:
* 🟢 **`CLEAN_IP` (Điểm an toàn $95 - 100$):** Từ khóa thuần túy mô tả sản phẩm ngách (VD: *Personalized Pickleball Tumbler, Ghost Acrylic Mirror, Teacher Appreciation Mug*). Được phép đưa vào sản xuất ngay.
* 🔴 **`TRADEMARK_ALERT` (Điểm an toàn $\le 45$):** Chứa thương hiệu độc quyền hoặc tên nhân vật được bảo hộ $\rightarrow$ Hệ thống tự động cảnh báo Seller không nên chọn.
