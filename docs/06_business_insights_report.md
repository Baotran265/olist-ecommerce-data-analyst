# BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS REPORT

> **Dự án:** Phân tích Dữ liệu Nền tảng Thương mại Điện tử Olist (Brazil)  
> **Tác giả:** Data Analyst Portfolio Project  
> **Đối tượng báo cáo:** Ban Giám đốc Vận hành (Head of Operations), Đội ngũ Quản lý Đối tác Bán hàng (Seller Management), Đội ngũ Logistics.  
> **Nguồn dữ liệu:** `data/processed/olist_master_analytical_dataset.csv` (112,650 dòng sản phẩm, 96,470 đơn giao thành công hợp lệ).  

---

## Executive Summary (Tóm tắt điều hành)

Phân tích trên **96,470 đơn hàng đã giao thành công hợp lệ** (loại bỏ các đơn thiếu ngày giao thực tế hoặc ngày dự kiến) và **93,350 khách hàng duy nhất có đơn giao thành công** trong giai đoạn 2016 – 2018 đã làm sáng tỏ 5 phát hiện cốt lõi chi phối sức khỏe vận hành và trải nghiệm khách hàng:

1. **"Điểm gãy chịu đựng" (Tolerance Cliff) ở mốc 3 ngày trễ:** Khách hàng chấp nhận sự trễ hẹn nhẹ từ 1–3 ngày (điểm hài lòng đạt 3.29 ★). Tuy nhiên, **từ ngày trễ thứ 4 trở đi, sự hài lòng sụp đổ hoàn toàn xuống 2.10 ★ (4–7 ngày) và 1.70 ★ (>7 ngày)**, với 58.58% – 69.83% khách hàng để lại đánh giá 1 sao.
2. **Nghẽn cổ chai logistics tại vùng Đông Bắc (Northeast):** Các bang Đông Bắc như **Alagoas (AL: 21.41% trễ)**, **Maranhão (MA: 17.43% trễ)**, **Sergipe (SE: 15.22% trễ)** có tỷ lệ trễ hẹn cao gấp 4–5 lần so với São Paulo (SP: 4.49%). Giao hàng liên bang (`is_interstate = 1`) mất trung bình 15.1 ngày (cước bình quân 26.94 R$), gần gấp đôi so với nội bang (7.9 ngày, 15.35 R$, chênh lệch +75.5% cước phí).
3. **16 Seller rủi ro cao theo chuẩn Order-Deduplicated:** Các nhà bán hàng này tạo ra doanh thu trên 15,000 R$ từ các đơn giao thành công nhưng điểm đánh giá trung bình dưới 3.8 ★. Trong đó:
   - **11 Seller đủ cỡ mẫu ($\ge 30$ đơn) mang nhãn `High Risk - Intervene`:** Sở hữu tỷ lệ trễ bình quân trọng số là **9.00%** và thời gian bàn giao hàng cho carrier (`avg_dispatch_days`) bình quân 7.04 ngày (cá biệt có seller trễ >20% và dispatch lên tới 11.9 ngày).
   - **5 Seller giá trị cao nhưng cỡ mẫu nhỏ ($< 30$ đơn) mang nhãn `Potential Risk - Monitor (Low Sample)`:** Cần thiết lập kênh giám sát riêng thay vì can thiệp quy trình vận hành đại trà do độ tin cậy thống kê chưa cao.
4. **Tỷ lệ khách hàng quay lại hoàn tất (Repeat Completed Purchases) ở mức 3.00%:** Xét trên tập khách hàng có đơn giao thành công, tỷ lệ mua lại là **3.00%** (2,801 / 93,350 khách hàng). 
5. **Đòn bẩy trải nghiệm đơn đầu tiên giao thành công:** Khách hàng có đơn hàng đầu tiên *giao thành công* bị trễ có tỷ lệ quay lại mua hàng **sụt giảm 17.1%** (từ 3.04% xuống 2.52%, kiểm định Chi-square $\chi^2 \approx 5.29, p < 0.05$) so với khách hàng được giao đúng hẹn.

---

## Phân tích Chi tiết 5 Câu hỏi Kinh doanh Trọng tâm

### Câu hỏi 1: Giao hàng trễ tác động thế nào đến Điểm đánh giá (Review Score)?

| Nhóm thời gian giao hàng (Delay Bucket) | Số đơn hàng (Total Orders) | Số đơn có Review hợp lệ | Điểm đánh giá TB | % Đánh giá 1 ★ | % Đánh giá 5 ★ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On Time / Early)** | 89,936 (93.2%) | 89,443 | **4.29 ★** | 6.62% | **62.27%** |
| **Trễ 1 - 3 ngày (1-3 Days Late)** | 1,870 (1.9%) | 1,852 | **3.29 ★** | 25.11% | 33.15% |
| **Trễ 4 - 7 ngày (4-7 Days Late)** | 1,802 (1.9%) | 1,748 | **2.10 ★** | **58.58%** | 14.07% |
| **Trễ > 7 ngày (> 7 Days Late)** | 2,862 (3.0%) | 2,781 | **1.70 ★** | **69.83%** | 7.01% |

* **Insight then chốt:** Khách hàng có sự kiên nhẫn nhất định trong 72 giờ đầu tiên sau hẹn. Khi vượt qua 3 ngày trễ, đơn hàng bước vào "vùng sụp đổ" khi tỷ lệ đánh giá 1 sao chiếm đa số tuyệt đối (>58%).
* **Hành động đề xuất:** Thiết lập hệ thống cảnh báo tự động (Automated Proactive Alert). Ngay khi một đơn hàng có nguy cơ trễ chạm mốc **ngày thứ 2**, hệ thống phải chủ động gửi thông báo xin lỗi kèm voucher đền bù (5-10%) **trước khi** khách hàng nhận hàng và viết review.

---

### Câu hỏi 2: Nghẽn cổ chai địa lý (Geographic Bottlenecks) nằm ở đâu?

| Vùng / Bang | Số đơn hàng | Tỷ lệ trễ hẹn (%) | Thời gian giao TB (ngày) | Điểm đánh giá TB |
| :--- | :---: | :---: | :---: | :---: |
| **Alagoas (AL)** | 397 | **21.41%** | 24.5 ngày | 3.85 ★ |
| **Maranhão (MA)** | 717 | **17.43%** | 21.6 ngày | 3.83 ★ |
| **Sergipe (SE)** | 335 | **15.22%** | 21.5 ngày | 3.91 ★ |
| **Piauí (PI)** | 476 | **13.87%** | 19.5 ngày | 3.99 ★ |
| **Ceará (CE)** | 1,279 | **13.76%** | 21.3 ngày | 3.94 ★ |
| *Toàn quốc (Benchmark)* | *96,470* | *6.77%* | *12.6 ngày* | *4.16 ★* |
| **São Paulo (SP)** | 40,494 | **4.49%** | 8.8 ngày | 4.25 ★ |

* **Insight then chốt:** Các bang Đông Bắc có tỷ lệ giao trễ cao nhất toàn quốc (13.8% – 21.4%). Nguyên nhân cốt lõi là sự tập trung bất đối xứng: phần lớn nhà bán hàng và kho hàng tập trung ở vùng Đông Nam (SP, RJ, MG).
* **Hành động đề xuất:** Thử nghiệm A/B Testing điều chỉnh thuật toán dự báo ngày giao (`order_estimated_delivery_date`) cho các tuyến Đông Bắc cộng thêm 3–4 ngày đệm (Buffer Days) để quản trị kỳ vọng khách hàng.

---

### Câu hỏi 3: Ma trận Rủi ro Người bán (Seller Risk Matrix)

Phân loại người bán dựa trên **Tổng Doanh thu (Trục X)** và **Điểm Đánh giá Trung bình (Trục Y)** với ngưỡng 15,000 R$ và 3.8 ★ (chỉ tính trên đơn giao thành công hợp lệ):

* **Phân khúc 16 Candidate Sellers (Order-Deduplicated Standard):**
  - **11 Seller đủ cỡ mẫu ($\ge 30$ đơn) - Nhãn `High Risk - Intervene`:** 
    - Seller dẫn đầu nhóm rủi ro `7c67...`: Doanh thu **186,570 R$** (973 đơn), nhưng điểm đánh giá chỉ **3.50 ★** và thời gian bàn giao hàng trung bình cho vận chuyển lên tới **11.9 ngày**.
    - Seller `712e...`: Doanh thu 39,385 R$ (77 đơn), tỷ lệ trễ hẹn **20.78%** và điểm đánh giá chỉ đạt **3.39 ★**.
  - **5 Seller giá trị cao nhưng cỡ mẫu nhỏ ($< 30$ đơn) - Nhãn `Potential Risk - Monitor (Low Sample)`:**
    - Ví dụ: Seller `b1b3...` có doanh thu 21,520 R$ (14 đơn), điểm đánh giá **1.93 ★**, tỷ lệ trễ 64.29%. Nhóm này cần gắn cờ kiểm toán riêng, tránh ngộ nhận do cỡ mẫu quá nhỏ để kết luận xu hướng.
* **Hành động đề xuất (Chương trình Pilot):** Thử nghiệm áp dụng chính sách **SLA Dispatching**: Yêu cầu nhóm 11 seller đủ mẫu cam kết bàn giao hàng cho carrier trong vòng 48h. Nếu không cải thiện sau 30 ngày, tạm thời giảm thứ hạng hiển thị.

---

### Câu hỏi 4: Hiệu suất Nhóm Sản phẩm (Product Category Matrix)

* **Nhóm dẫn đầu Doanh thu & Hài lòng cao:**
  - `Health Beauty`: Doanh thu **1,233,132 R$**, Điểm đánh giá TB **4.23 ★**, Tỷ lệ trễ **7.51%**.
  - `Watches Gifts`: Doanh thu **1,165,899 R$**, Điểm đánh giá TB **4.12 ★**, Tỷ lệ trễ **7.39%**.
  - `Bed Bath Table`: Doanh thu **1,023,435 R$**, Điểm đánh giá **4.00 ★**, Tỷ lệ trễ **7.43%**.
* **Nhóm chịu gánh nặng chi phí vận chuyển cao:**
  - Các mặt hàng nội thất (`Furniture Decor`, `Office Furniture`): Tỷ trọng cước phí vận chuyển chiếm tới **19.1% – 20.0% tổng giá trị đơn hàng (GOV)**. Đây là nhóm có chi phí logistics trên mỗi đơn hàng cao nhất sàn.

---

### Câu hỏi 5: Tỷ lệ Khách hàng Quay lại & Tác động của Đơn hàng Đầu tiên

| Trạng thái giao hàng Đơn đầu tiên | Tổng số khách hàng | Tỷ lệ quay lại mua tiếp (%) | Mức độ sụt giảm tương đối |
| :--- | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On-Time)** | 86,995 | **3.04%** | — |
| **Bị giao trễ (Delayed)** | 6,355 | **2.52%** | **-17.1% ($p < 0.05$)** |

* **Insight then chốt:** Trải nghiệm tiêu cực ở đơn hàng đầu tiên *giao thành công* làm sụt giảm **17.1% cơ hội giữ chân khách hàng**. 
* **Hành động đề xuất:** Gắn cờ ưu tiên (Flag `is_first_time_buyer = 1`) trong hệ thống fulfillment để các đối tác vận chuyển ưu tiên tuyến đường và giao đúng hẹn cho các đơn hàng đầu tiên của khách mới.

---

## 🔍 Giới Hạn Phân Tích & Phân Biệt Tương Quan vs Nhân Quả

1. **Tương quan (Correlation) vs Nhân quả (Causation):** Dữ liệu quan sát cho thấy sự sụt giảm mạnh về điểm review khi thời gian trễ tăng. Tuy nhiên, thời gian giao trễ chưa hẳn là nguyên nhân duy nhất; các yếu tố ngoại lai như đóng gói, bể vỡ trong quá trình vận chuyển cũng có thể cùng xảy ra.
2. **Thiên lệch Cửa sổ Quan sát (Right-Censoring Bias):** Tỷ lệ mua lại 3.00% đo lường trên toàn bộ tập dữ liệu tĩnh Olist (2016–2018). Khách hàng mua đơn đầu tiên vào tháng 08/2018 chỉ có khoảng 1–3 tuần để phát sinh đơn mua lại. Trong môi trường sản xuất thực tế, chỉ số này nên được chuẩn hóa theo cửa sổ thời gian cố định (ví dụ: 60-day Retention Rate).
3. **Định nghĩa Đơn hàng Mua lại:** Báo cáo này chuẩn hóa định nghĩa chính là **Repeat Completed Purchases** (khách hàng có $\ge 2$ đơn giao thành công hợp lệ). 

---
*Báo cáo được tổng hợp dựa trên kết quả tính toán định lượng chính xác từ mã nguồn Python và cơ sở dữ liệu Star Schema.*