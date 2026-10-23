# BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS REPORT

> **Dự án:** Phân tích Dữ liệu Nền tảng Thương mại Điện tử Olist (Brazil)  
> **Tác giả:** Data Analyst Portfolio Project  
> **Đối tượng báo cáo:** Ban Giám đốc Vận hành (Head of Operations), Đội ngũ Quản lý Đối tác Bán hàng (Seller Management), Đội ngũ Logistics.  
> **Nguồn dữ liệu:** `data/processed/olist_master_analytical_dataset.csv` (112,650 dòng sản phẩm, 98,666 đơn hàng có sản phẩm, 96,470 đơn giao thành công hợp lệ).  

---

## Executive Summary (Tóm tắt điều hành)

Phân tích trên **96,470 đơn hàng đã giao thành công hợp lệ** (loại bỏ 8 đơn delivered thiếu ngày giao thực tế) và **93,350 khách hàng duy nhất có đơn giao thành công** (96,096 khách hàng trên toàn sàn) trong giai đoạn 2016 – 2018 đã làm sáng tỏ 5 phát hiện cốt lõi chi phối sức khỏe vận hành và trải nghiệm khách hàng:

1. **"Điểm gãy chịu đựng" (Tolerance Cliff) ở mốc 3 ngày trễ:** Khách hàng chấp nhận sự trễ hẹn nhẹ từ 1–3 ngày (điểm hài lòng đạt 3.29 ★). Tuy nhiên, **từ ngày trễ thứ 4 trở đi, sự hài lòng sụp đổ hoàn toàn xuống 2.10 ★ (4–7 ngày) và 1.70 ★ (>7 ngày)**, với 58.58% – 69.83% khách hàng để lại đánh giá 1 sao.
2. **Nghẽn cổ chai logistics tại vùng Đông Bắc (Northeast) và bang Rio de Janeiro:** Các bang Đông Bắc như **Alagoas (AL: 21.41% trễ)**, **Maranhão (MA: 17.43% trễ)**, **Sergipe (SE: 15.22% trễ)** có tỷ lệ trễ hẹn cao gấp 4–5 lần so với São Paulo (SP: 4.49%) hay Paraná (PR: 4.04%). Bang Rio de Janeiro (RJ) thuộc vùng Đông Nam cũng ghi nhận tỷ lệ trễ cao (12.11% trên 12,350 đơn). Giao hàng liên bang (`is_interstate = 1`) mất trung bình 15.1 ngày (cước bình quân 26.94 R$), gần gấp đôi so với nội bang (7.9 ngày, 15.35 R$, chênh lệch +75.5% cước phí).
3. **16 Seller rủi ro cao theo chuẩn Order-Deduplicated:** Các nhà bán hàng này tạo ra doanh thu trên 15,000 R$ nhưng điểm đánh giá trung bình dưới 3.8 ★ (trong đó 11 seller có quy mô lớn $\ge 30$ đơn và 5 seller thuộc nhóm giá trị cao nhưng mẫu nhỏ $< 30$ đơn). Nhóm 16 seller này có tỷ lệ trễ bình quân trọng số là 9.47% (trung bình đơn giản 14.11%, cá biệt có seller trễ 20.78% – 64.29%) và thời gian bàn giao hàng cho carrier (`avg_dispatch_days`) bình quân 7.0 ngày (cá biệt lên tới 11.9 – 15.7 ngày).
4. **Tỷ lệ khách hàng quay lại (Repeat Purchase Rate) trên sàn ở mức 3.00% – 3.12%:** Xét trên tập khách hàng có đơn giao thành công, tỷ lệ mua lại là **3.00%** (2,801 / 93,350 khách hàng). Nếu tính trên toàn bộ đơn hàng phát sinh ở mọi trạng thái (kể cả 775 đơn mồ côi không có sản phẩm), tỷ lệ là **3.12%** (2,997 / 96,096 khách hàng).
5. **Đòn bẩy trải nghiệm đơn đầu tiên:** Khách hàng có đơn hàng đầu tiên bị giao trễ có tỷ lệ quay lại mua hàng **sụt giảm 17.1%** (từ 3.04% xuống 2.52%, kiểm định Chi-square $\chi^2 = 5.29, p = 0.0219 < 0.05$) so với khách hàng được giao đúng hẹn.

---

## Phân tích Chi tiết 5 Câu hỏi Kinh doanh Trọng tâm

### Câu hỏi 1: Giao hàng trễ tác động thế nào đến Điểm đánh giá (Review Score)?

| Nhóm thời gian giao hàng (Delay Bucket) | Số đơn hàng (Total Orders) | Số đơn có Review hợp lệ | Điểm đánh giá TB | Trung vị | % Đánh giá 1 ★ | % Đánh giá 5 ★ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On Time / Early)** | 89,936 (93.2%) | 89,443 | **4.29 ★** | 5.0 | 6.62% | **62.27%** |
| **Trễ 1 - 3 ngày (1-3 Days Late)** | 1,870 (1.9%) | 1,852 | **3.29 ★** | 4.0 | 25.11% | 33.15% |
| **Trễ 4 - 7 ngày (4-7 Days Late)** | 1,802 (1.9%) | 1,748 | **2.10 ★** | 1.0 | **58.58%** | 14.07% |
| **Trễ > 7 ngày (> 7 Days Late)** | 2,862 (3.0%) | 2,781 | **1.70 ★** | 1.0 | **69.83%** | 7.01% |

![Fig 1: Delivery Delay vs Review Score](../outputs/figures/fig1_delivery_delay_vs_review_score.png)

* **Insight then chốt:** Khách hàng có sự kiên nhẫn nhất định trong 72 giờ đầu tiên sau hẹn. Khi vượt qua 3 ngày trễ, đơn hàng bước vào "vùng sụp đổ" khi tỷ lệ đánh giá 1 sao chiếm đa số tuyệt đối (>58%), và tiếp tục rơi xuống đáy 1.70 ★ khi trễ trên 1 tuần (gần 70% đánh giá 1 sao).
* **Hành động đề xuất:** Thiết lập hệ thống cảnh báo tự động (Automated Proactive Alert). Ngay khi một đơn hàng có nguy cơ trễ chạm mốc **ngày thứ 2**, hệ thống phải chủ động gửi thông báo xin lỗi kèm voucher đền bù (5-10% cho lần mua kế tiếp) **trước khi** khách hàng nhận hàng và viết review.

---

### Câu hỏi 2: Nghẽn cổ chai địa lý (Geographic Bottlenecks) nằm ở đâu?

| Vùng / Bang | Số đơn hàng | Tỷ lệ trễ hẹn (%) | Thời gian giao TB (ngày) | Điểm đánh giá TB |
| :--- | :---: | :---: | :---: | :---: |
| **Alagoas (AL)** | 397 | **21.41%** | 24.5 ngày | 3.85 ★ |
| **Maranhão (MA)** | 717 | **17.43%** | 21.6 ngày | 3.83 ★ |
| **Sergipe (SE)** | 335 | **15.22%** | 21.5 ngày | 3.91 ★ |
| **Piauí (PI)** | 476 | **13.87%** | 19.5 ngày | 3.99 ★ |
| **Ceará (CE)** | 1,279 | **13.76%** | 21.3 ngày | 3.94 ★ |
| **Bahia (BA)** | 3,256 | **12.16%** | 19.3 ngày | 3.93 ★ |
| **Rio de Janeiro (RJ)** | 12,350 | **12.11%** | 15.3 ngày | 3.97 ★ |
| *Toàn quốc (Benchmark)* | *96,470* | *6.77%* | *12.6 ngày* | *4.16 ★* |
| **São Paulo (SP)** | 40,494 | **4.49%** | 8.8 ngày | 4.25 ★ |
| **Paraná (PR)** | 4,923 | **4.04%** | 12.0 ngày | 4.24 ★ |

> 💡 **Lưu ý về Grain (Độ chi tiết dữ liệu):** Tỷ lệ giao trễ toàn quốc ở cấp độ **Đơn hàng (Order-level)** là **6.77%** (6,534 / 96,470 đơn). Nếu tính ở cấp độ **Sản phẩm (Item-level trên 110,189 dòng delivered hợp lệ)**, tỷ lệ trễ là **6.59%** (7,264 / 110,189) do các đơn hàng giỏ lớn (nhiều items) có tỷ lệ trễ thấp hơn. Toàn bộ báo cáo và Power BI thống nhất chuẩn Order-level (6.77% trễ, tương ứng **93.23% đúng hạn**).

![Fig 2: State Delivery Performance](../outputs/figures/fig2_state_delivery_performance.png)

* **Insight then chốt:** Các bang Đông Bắc (AL, MA, SE, PI, CE) có tỷ lệ giao trễ cao nhất toàn quốc (13.8% – 21.4%). Ngoài ra, bang Rio de Janeiro (RJ) dù ở Đông Nam cũng có tỷ lệ trễ 12.11% trên 12,350 đơn. Nguyên nhân cốt lõi là sự tập trung bất đối xứng: **84.4% nhà bán hàng và 91.1% dòng sản phẩm tập trung ở 4 bang SP, RJ, MG, PR** (trong đó PR thuộc vùng Nam, 3 bang còn lại thuộc Đông Nam).
* **Hành động đề xuất:** 
  1. Thử nghiệm A/B Testing điều chỉnh thuật toán dự báo ngày giao (`order_estimated_delivery_date`) cho các tuyến Đông Bắc cộng thêm 3–4 ngày đệm (Buffer Days) để quản trị kỳ vọng khách hàng.
  2. Khuyến khích hoặc chiêu mộ các Seller đặt kho hàng (Fulfillment Hub) tại khu vực Đông Bắc.

---

### Câu hỏi 3: Ma trận Rủi ro Người bán (Seller Risk Matrix)

Bằng cách phân loại người bán dựa trên **Tổng Doanh thu (Trục X)** và **Điểm Đánh giá Trung bình (Trục Y)** với ngưỡng 15,000 R$ và 3.8 ★:

![Fig 3: Seller Risk Matrix](../outputs/figures/fig3_seller_risk_matrix.png)

* **Phát hiện 16 High-Risk Sellers (Order-Deduplicated Standard):**
  - **11 Seller có quy mô đơn hàng đáng kể ($\ge 30$ đơn):**
    - Seller dẫn đầu doanh thu nhóm rủi ro `7c67e1448b00f6e969d365cea6b010ab`: Doanh thu **186,570 R$** (973 đơn), nhưng điểm đánh giá chỉ **3.50 ★** và thời gian bàn giao hàng trung bình cho vận chuyển lên tới **11.9 ngày** (`avg_dispatch_days`).
    - Seller `712e6ed8aa4aa1fa65dab41fed5737e4`: Doanh thu 39,385 R$ (77 đơn), tỷ lệ trễ hẹn **20.78%** và điểm đánh giá chỉ đạt **3.39 ★**.
    - Seller `88460e8ebdecbfecb5f9601833981930`: Doanh thu 31,320 R$ (246 đơn), tỷ lệ trễ **17.07%**, điểm đánh giá **3.43 ★**, dispatch trung bình 7.8 ngày.
  - **5 Seller thuộc nhóm giá trị đơn lớn nhưng cỡ mẫu nhỏ ($< 30$ đơn):**
    - Seller `b1b3948701c5c72445495bd161b83a4c`: Doanh thu 21,520 R$ (14 đơn), điểm đánh giá **1.93 ★**, tỷ lệ trễ 64.29% (9/14 đơn trễ), thời gian dispatch 15.7 ngày. Cần gắn cờ kiểm toán riêng tránh ngộ nhận cỡ mẫu.
    - Seller `b37c4c02bda3161a7546a4e6d222d5b2`: Doanh thu 24,075 R$ nhưng chỉ có 4 đơn hàng (review 2.25 ★, 0 đơn trễ nhưng điểm thấp do chất lượng sản phẩm).
* **Hành động đề xuất (Chương trình Pilot):**
  1. Thử nghiệm áp dụng chính sách **SLA Dispatching**: Yêu cầu nhóm seller có quy mô lớn cam kết bàn giao hàng cho carrier trong vòng 48h (`seller_dispatch_days <= 2`).
  2. Nếu không cải thiện sau 30 ngày thử nghiệm, tạm thời giảm thứ hạng hiển thị (Deprioritize in search/ranking).

---

### Câu hỏi 4: Hiệu suất Nhóm Sản phẩm (Product Category Matrix)

![Fig 4: Category Performance Matrix](../outputs/figures/fig4_category_performance_matrix.png)

* **Nhóm dẫn đầu Doanh thu & Hài lòng cao:**
  - `Health Beauty`: Doanh thu **1,233,132 R$**, 9,465 sản phẩm, Điểm đánh giá TB **4.19 ★**, Tỷ lệ trễ 7.56%, Cước phí chiếm 12.67% tổng giá trị đơn hàng (GOV).
  - `Watches Gifts`: Doanh thu **1,165,899 R$**, 5,857 sản phẩm, Điểm đánh giá TB **4.07 ★**, Tỷ lệ trễ 7.21%, Cước phí chỉ chiếm 7.76% GOV.
  - `Bed Bath Table`: Bán chạy nhất về số lượng (**10,953 sản phẩm**), doanh thu **1,023,435 R$**, Điểm đánh giá **3.92 ★**, Tỷ lệ trễ 7.03%, Cước phí chiếm 16.47% GOV.
* **Nhóm chịu gánh nặng chi phí vận chuyển cao:**
  - Các mặt hàng nội thất (`Furniture Decor`, `Office Furniture`, `Furniture Living Room`): Tỷ trọng cước phí vận chuyển chiếm tới **19.1% – 20.8% tổng giá trị đơn hàng (GOV)** (và cá biệt `Furniture Mattress And Upholstery` lên tới 26.78%). Đây là nhóm có chi phí logistics trên mỗi đơn hàng cao nhất sàn.

---

### Câu hỏi 5: Tỷ lệ Khách hàng Quay lại (Customer Retention) & Tác động của Đơn hàng Đầu tiên

| Trạng thái giao hàng Đơn đầu tiên | Tổng số khách hàng | Tỷ lệ quay lại mua tiếp (%) | Mức độ sụt giảm tương đối |
| :--- | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On-Time)** | 86,995 | **3.04%** | — |
| **Bị giao trễ (Delayed)** | 6,355 | **2.52%** | **-17.1% ($\chi^2 = 5.29, p = 0.0219$)** |

![Fig 5: Customer Retention & First Order Impact](../outputs/figures/fig5_customer_retention_and_first_order_impact.png)

* **Insight then chốt:** Trên sàn thương mại điện tử Olist, tỷ lệ khách hàng mua lại đo lường trên tập đơn giao thành công hợp lệ là **3.00%** (2,801 / 93,350 khách hàng). Trải nghiệm tiêu cực ở đơn hàng đầu tiên làm sụt giảm **17.1% cơ hội giữ chân khách hàng** (từ 3.04% xuống 2.52%, chênh lệch có ý nghĩa thống kê ở mức ý nghĩa 5% với $p = 0.0219$).
* **Hành động đề xuất:** Gắn cờ ưu tiên (Flag `is_first_time_buyer = 1`) trong hệ thống fulfillment để các đối tác vận chuyển ưu tiên tuyến đường và giao đúng hẹn cho các đơn hàng đầu tiên của khách mới.

---

## 🚀 4 Giả thuyết Chiến lược Đề xuất Kiểm chứng (Actionable Hypotheses for Testing)

1. **Giả thuyết 1: "Early Compensation Voucher Bot" (Chống trễ trên 3 ngày)**
   * *Giả thuyết:* Khi đơn hàng chạm mốc trễ ngày thứ 2, việc chủ động gửi thông báo xin lỗi kèm mã giảm giá 10% cho đơn tiếp theo sẽ ngăn chặn điểm đánh giá sụt giảm sâu xuống dưới 2.0 ★ và giảm tỷ lệ đánh giá 1 sao.
   * *Cách kiểm chứng:* Chia 50/50 nhóm khách hàng có đơn trễ ngày thứ 2 để đo lường Review Score và Chi phí đền bù (Voucher Cost vs LTV).
2. **Giả thuyết 2: "Buffer Days" cho Khu vực Đông Bắc**
   * *Giả thuyết:* Tăng thời gian ước tính (`estimated_delivery_days`) thêm 3–4 ngày cho các bang AL, MA, SE, PI, CE sẽ kéo giảm tỷ lệ "bị tính là trễ" trên hệ thống, từ đó giảm áp lực tâm lý của người mua và cải thiện điểm hài lòng trung bình thêm ít nhất 0.2 ★.
3. **Giả thuyết 3: "SLA Dispatching" cho Nhóm Seller Rủi ro Cao**
   * *Giả thuyết:* Áp dụng cam kết bàn giao hàng cho carrier $\le 48h$ đối với 11 seller rủi ro cao có quy mô đơn lớn sẽ giúp rút ngắn thời gian dispatch bình quân từ 7.0 ngày xuống $\le 2.0$ ngày, qua đó kéo giảm tỷ lệ trễ bình quân trọng số của nhóm từ **9.47% xuống dưới 6.0%**.
4. **Giả thuyết 4: "First-Order VIP Route"**
   * *Giả thuyết:* Ưu tiên xử lý đơn hàng đầu tiên của khách hàng mới sẽ bảo vệ tỷ lệ Retention không bị sụt giảm 17.1%.

---

## 🔍 5. Giới Hạn Phân Tích & Phân Biệt Tương Quan vs Nhân Quả (Methodological Limitations)

1. **Tương quan (Correlation) vs Nhân quả (Causation):**
   * Dữ liệu quan sát (Observational Data) cho thấy sự sụt giảm mạnh về điểm review khi thời gian trễ tăng. Tuy nhiên, thời gian giao trễ chưa hẳn là nguyên nhân duy nhất; các yếu tố ngoại lai như đóng gói, bể vỡ trong quá trình vận chuyển cũng có thể cùng xảy ra.
2. **Thiên lệch Cửa sổ Quan sát trong Phân tích Retention (Right-Censoring Bias):**
   * Tỷ lệ mua lại 3.00% (2,801 / 93,350 khách hàng có đơn delivered) đo lường trên toàn bộ tập dữ liệu tĩnh Olist (2016–2018).
   * Khách hàng mua đơn đầu tiên vào tháng 08/2018 chỉ có khoảng 1–3 tuần để phát sinh đơn mua lại trước khi tập dữ liệu kết thúc. Trong môi trường sản xuất thực tế, chỉ số này nên được chuẩn hóa theo cửa sổ thời gian cố định như **60-day Retention Rate** hoặc **90-day Retention Rate**.
3. **Định nghĩa Đơn hàng Mua lại (Repeat Orders):**
   * Báo cáo này chuẩn hóa định nghĩa chính là **Repeat Completed Purchases** (2,801 khách hàng có $\ge 2$ đơn giao thành công hợp lệ trên tổng số 93,350 khách hàng, đạt 3.00%). Nếu tính trên toàn bộ đơn hàng ở mọi trạng thái (kể cả 775 đơn mồ côi không có sản phẩm trong raw orders), con số là 3.12% (2,997 / 96,096).

---
*Báo cáo được tổng hợp dựa trên kết quả tính toán định lượng chính xác từ mã nguồn [src/04_exploratory_data_analysis.py](../src/04_exploratory_data_analysis.py) và cơ sở dữ liệu Star Schema [data/olist_star_schema.db](../data/olist_star_schema.db).*
