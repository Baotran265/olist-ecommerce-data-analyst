# BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS REPORT

> **Dự án:** Phân tích Dữ liệu Nền tảng Thương mại Điện tử Olist (Brazil)  
> **Tác giả:** Data Analyst Portfolio Project  
> **Đối tượng báo cáo:** Ban Giám đốc Vận hành (Head of Operations), Đội ngũ Quản lý Đối tác Bán hàng (Seller Management), Đội ngũ Logistics.  
> **Nguồn dữ liệu:** `data/processed/olist_master_analytical_dataset.csv` (112,650 dòng, 99,441 đơn hàng).  

---

## Executive Summary (Tóm tắt điều hành)

Phân tích trên **96,478 đơn hàng đã giao thành công** và **96,096 khách hàng duy nhất** trên nền tảng Olist (2016 - 2018) đã làm sáng tỏ 5 điểm then chốt chi phối sức khỏe vận hành và trải nghiệm khách hàng:

1. **"Điểm gãy chịu đựng" (Tolerance Cliff) ở mốc 3 ngày trễ:** Khách hàng chấp nhận sự trễ hẹn nhẹ từ 1-3 ngày (điểm hài lòng chỉ giảm nhẹ từ 4.29 ★ xuống 3.76 ★). Tuy nhiên, **từ ngày trễ thứ 4 trở đi, sự hài lòng sụp đổ hoàn toàn xuống 2.32 ★ (4-7 ngày) và 1.73 ★ (>7 ngày)**, với hơn 50% - 67% khách hàng để lại đánh giá 1 sao.
2. **Nghẽn cổ chai logistics tại vùng Đông Bắc (Northeast):** Các bang Đông Bắc như **Alagoas (AL: 23.9% trễ)**, **Maranhão (MA: 19.7% trễ)** có tỷ lệ trễ hẹn cao gấp 4 lần so với thủ phủ kinh tế São Paulo (SP: 5.9% trễ). Giao hàng liên bang (`is_interstate = 1`) mất trung bình 15.1 ngày, gấp đôi so với nội bang (7.9 ngày).
3. **21 Seller thuộc nhóm "Rủi ro cao" (High Revenue - Low Satisfaction):** Có 21 nhà bán hàng tạo ra doanh thu trên 15,000 R$ nhưng điểm đánh giá trung bình dưới 3.8 ★ (thậm chí có seller đạt doanh thu khủng nhưng tỷ lệ trễ lên tới 21.2%). Đây là những đối tượng gây tổn hại thương hiệu nghiêm trọng nhất.
4. **Tỷ lệ khách hàng quay lại (Repeat Purchase Rate) cực kỳ thấp (3.12%):** Trong 96,096 khách hàng, chỉ có 2,997 người mua hàng từ lần thứ 2 trở lên.
5. **Đòn bẩy trải nghiệm đơn đầu tiên:** Khách hàng có đơn hàng đầu tiên bị giao trễ có tỷ lệ quay lại mua hàng **sụt giảm gần 19%** (từ 3.13% xuống 2.54%) so với khách hàng được giao đúng hẹn.

---

## Phân tích Chi tiết 5 Câu hỏi Kinh doanh Trọng tâm

### Câu hỏi 1: Giao hàng trễ tác động thế nào đến Điểm đánh giá (Review Score)?

| Nhóm thời gian giao hàng (Delay Bucket) | Số đơn hàng | Điểm đánh giá TB | Trung vị | % Đánh giá 1 ★ | % Đánh giá 5 ★ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On Time / Early)** | 88,650 (91.9%) | **4.29 ★** | 5.0 | 6.55% | **62.10%** |
| **Trễ 1 - 3 ngày (1-3 Days Late)** | 2,660 (2.8%) | **3.76 ★** | 4.0 | 13.72% | 42.78% |
| **Trễ 4 - 7 ngày (4-7 Days Late)** | 1,819 (1.9%) | **2.32 ★** | 1.0 | **51.68%** | 17.59% |
| **Trễ > 7 ngày (> 7 Days Late)** | 3,341 (3.5%) | **1.73 ★** | 1.0 | **66.90%** | 7.24% |

![Fig 1: Delivery Delay vs Review Score](../outputs/figures/fig1_delivery_delay_vs_review_score.png)

* **Insight then chốt:** Khách hàng mua sắm online có một "vùng đệm tâm lý" khoảng 72 giờ. Khi vượt qua 3 ngày trễ, đơn hàng bước vào "vùng báo động đỏ" khi tỷ lệ 1 sao chiếm đa số tuyệt đối.
* **Hành động đề xuất:** Thiết lập hệ thống cảnh báo tự động (Automated Proactive Alert). Ngay khi một đơn hàng có nguy cơ trễ chạm mốc **ngày thứ 2**, hệ thống phải chủ động gửi email/SMS xin lỗi kèm voucher đền bù (5-10% cho lần mua kế tiếp) **trước khi** khách hàng nhận hàng và viết review.

---

### Câu hỏi 2: Nghẽn cổ chai địa lý (Geographic Bottlenecks) nằm ở đâu?

| Vùng / Bang | Số đơn hàng | Tỷ lệ trễ hẹn (%) | Thời gian giao TB (ngày) | Điểm đánh giá TB |
| :--- | :---: | :---: | :---: | :---: |
| **Alagoas (AL)** | 397 | **23.93%** | 24.5 ngày | 3.85 ★ |
| **Maranhão (MA)** | 717 | **19.67%** | 21.6 ngày | 3.83 ★ |
| **Piauí (PI)** | 476 | **15.97%** | 19.5 ngày | 3.99 ★ |
| **Ceará (CE)** | 1,279 | **15.32%** | 21.3 ngày | 3.94 ★ |
| **Sergipe (SE)** | 335 | **15.22%** | 21.5 ngày | 3.91 ★ |
| *Toàn quốc (Benchmark)* | *96,478* | *7.90%* | *12.5 ngày* | *4.16 ★* |
| **São Paulo (SP)** | 40,501 | **5.89%** | 8.8 ngày | 4.25 ★ |
| **Paraná (PR)** | 4,923 | **5.00%** | 12.0 ngày | 4.24 ★ |

![Fig 2: State Delivery Performance](../outputs/figures/fig2_state_delivery_performance.png)

* **Insight then chốt:** Các bang Đông Bắc (AL, MA, PI, CE, SE) có tỷ lệ giao trễ trên 15% (cứ 5 đơn thì có 1 đơn trễ). Nguyên nhân chính là do **90% người bán tập trung ở vùng Đông Nam (SP, RJ, MG, PR)** trong khi hạ tầng giao thông liên bang kết nối đến Đông Bắc còn nhiều hạn chế.
* **Hành động đề xuất:** 
  1. Cân nhắc điều chỉnh lại thuật toán dự báo ngày giao (`order_estimated_delivery_date`) cho khu vực Đông Bắc cộng thêm 3-5 ngày đệm (Buffer Days) để quản trị kỳ vọng khách hàng.
  2. Khuyến khích hoặc chiêu mộ thêm các Seller đặt kho hàng (Fulfillment Hub) tại khu vực Đông Bắc.

---

### Câu hỏi 3: Ma trận Rủi ro Người bán (Seller Risk Matrix)

Bằng cách phân loại người bán dựa trên **Tổng Doanh thu (Trục X)** và **Điểm Đánh giá Trung bình (Trục Y)** với ngưỡng 15,000 R$ và 3.8 ★:

![Fig 3: Seller Risk Matrix](../outputs/figures/fig3_seller_risk_matrix.png)

* **Phát hiện 21 High-Risk Sellers:**
  - Seller tiêu biểu `712e6ed8aa4aa1fa65dab41fed5737e4`: Tạo ra hơn 50,000 R$ doanh thu nhưng **tỷ lệ trễ hẹn lên tới 21.18%** và điểm đánh giá chỉ đạt **3.65 ★**.
  - Seller `2eb70248d66e0e3ef83659f71b244378`: Tỷ lệ trễ 14.21%, điểm đánh giá 3.63 ★.
* **Hành động đề xuất:**
  1. Áp dụng chính sách **SLA Dispatching**: Buộc các seller nhóm này phải bàn giao hàng cho carrier trong vòng 48h (`seller_dispatch_days <= 2`).
  2. Nếu không cải thiện trong 30 ngày, tạm thời giảm độ hiển thị (Deprioritize in search/ranking) trên sàn.

---

### Câu hỏi 4: Hiệu suất Nhóm Sản phẩm (Product Category Matrix)

![Fig 4: Category Performance Matrix](../outputs/figures/fig4_category_performance_matrix.png)

* **Nhóm dẫn đầu Doanh thu & Hài lòng cao:**
  - `Health & Beauty`: Doanh thu > 1.25 triệu R$, Điểm đánh giá TB **4.19 ★**, Tỷ lệ trễ thấp (7.1%).
  - `Watches & Gifts`: Doanh thu > 1.20 triệu R$, Điểm đánh giá TB **4.05 ★**.
  - `Bed, Bath & Table`: Nhóm bán chạy nhất về số lượng (11,115 items), doanh thu > 1.03 triệu R$, Điểm đánh giá **3.93 ★** (tỷ lệ trễ 8.5%).
* **Nhóm rủi ro chi phí vận chuyển cao:**
  - Các mặt hàng nội thất cồng kềnh (`furniture_decor`, `office_furniture`) có tỷ trọng phí ship chiếm tới 25-35% giá trị món hàng, thời gian vận chuyển kéo dài và tỷ lệ phàn nàn về trầy xước/hư hỏng cao hơn.

---

### Câu hỏi 5: Tỷ lệ Khách hàng Quay lại (Customer Retention) & Tác động của Đơn hàng Đầu tiên

| Trạng thái giao hàng Đơn đầu tiên | Tổng số khách hàng | Tỷ lệ quay lại mua tiếp (%) | Mức độ sụt giảm tương đối |
| :--- | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On-Time)** | 85,669 | **3.13%** | — |
| **Bị giao trễ (Delayed)** | 7,584 | **2.54%** | **-18.7% (Sụt giảm nghiêm trọng)** |

![Fig 5: Customer Retention & First Order Impact](../outputs/figures/fig5_customer_retention_and_first_order_impact.png)

* **Insight then chốt:** Trên các sàn Marketplace, tỷ lệ giữ chân khách hàng tự nhiên vốn đã rất thử thách (~3.1%). Việc để khách hàng mới gặp trải nghiệm giao hàng trễ ngay ở đơn đầu tiên sẽ **làm mất đi gần 1/5 cơ hội giữ chân họ quay lại**.
* **Hành động đề xuất:** Gắn cờ ưu tiên (Flag `is_first_time_buyer = 1`) trong hệ thống fulfillment để các đối tác vận chuyển ưu tiên tuyến đường và giao đúng hẹn cho các đơn hàng đầu tiên của khách mới.

---

## 🚀 4 Đề xuất Chiến lược cho Ban Giám đốc Olist (Actionable Plan)

1. **Triển khai "Early Warning & Compensation Bot" (Chống trễ trên 3 ngày):**
   - Tập trung mọi nỗ lực vận hành để không để đơn hàng vượt qua mốc **3 ngày trễ** (nơi điểm số lao dốc từ 3.76 ★ xuống 2.32 ★).
   - Tự động phát voucher 10% ngay ngày trễ thứ 2.
2. **Cơ chế kiểm soát 21 Top-Revenue High-Risk Sellers:**
   - Đặt KPI thời gian chuẩn bị hàng (`seller_dispatch_days` <= 2 ngày). Phạt phí dịch vụ hoặc giảm traffic hiển thị nếu tái phạm.
3. **Hiệu chỉnh thời gian dự kiến (Dynamic Estimated Delivery Date) theo Vùng:**
   - Tăng thời gian ước tính cho các đơn hàng đi các bang Đông Bắc (AL, MA, PI, CE) thêm 3-4 ngày để giảm tỷ lệ "bị coi là trễ", giúp giảm tỷ lệ đánh giá 1 sao.
4. **Chương trình "First Order VIP Protection":**
   - Đơn hàng của khách mới phải được kiểm tra tracking chủ động mỗi ngày. Nếu phát sinh trục trặc, CSKH chủ động liên hệ trước khi khách hàng phàn nàn.

---
*Báo cáo được tổng hợp dựa trên kết quả tính toán định lượng chính xác từ mã nguồn [src/04_exploratory_data_analysis.py](../src/04_exploratory_data_analysis.py).*
