# BÁO CÁO PHÂN TÍCH CHUYÊN SÂU & ĐỀ XUẤT CHIẾN LƯỢC KINH DOANH
(BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS REPORT)
 
> **Dự án:** Phân tích Dữ liệu Nền tảng Thương mại Điện tử Olist (Brazil)  
> **Ngôn ngữ báo cáo:** Tiếng Việt (Thống nhất toàn bộ tài liệu dự án)  
> **Đối tượng báo cáo:** Ban Giám đốc Vận hành (Head of Operations), Đội ngũ Quản lý Đối tác Bán hàng (Seller Management), Đội ngũ Logistics.  
> **Nguồn dữ liệu:** `data/processed/olist_master_analytical_dataset.csv` (112,650 dòng sản phẩm, 96,470 đơn giao thành công hợp lệ).  
 
---
 
## 📋 1. Tóm Tắt Điều Hành (Executive Summary)
 
Dự án phân tích dữ liệu thương mại điện tử Olist tại Brazil trong giai đoạn **2016–2018**, tập trung giải quyết bài toán: **Mối liên hệ giữa hiệu suất giao hàng (logistics delay) đối với mức độ hài lòng khách hàng (review score), tỷ lệ giữ chân khách hàng (retention) và nhận diện các rủi ro vận hành trong mạng lưới đối tác bán hàng.**
 
Tập phân tích chính gồm **96.470 đơn hàng giao thành công hợp lệ** (đã chuẩn hóa cấp ngày lịch `dt.normalize()` và lọc bỏ các đơn thiếu mốc ngày thực tế hoặc ngày dự kiến), tương ứng với **93.350 khách hàng duy nhất có đơn giao thành công**.
 
---
 
### 1️⃣ Độ trễ giao hàng có mối liên hệ với điểm đánh giá thấp hơn
Điểm đánh giá trung bình giảm từ **4,29 ★** ở nhóm giao đúng hạn/sớm xuống **3,29 ★** ở nhóm trễ 1–3 ngày và giảm sâu xuống **2,10 ★** ở nhóm trễ 4–7 ngày. Trong nhóm trễ 4–7 ngày, **58,58%** đánh giá hợp lệ là 1 sao. Kết quả cho thấy trải nghiệm khách hàng kém hơn rõ rệt ở các nhóm giao trễ dài hơn trong tập dữ liệu phân tích.
 
### 2️⃣ Một số bang có tỷ lệ giao trễ cao hơn đáng kể so với São Paulo
Alagoas có tỷ lệ trễ **21,41%**, Maranhão **17,43%** và Sergipe **15,22%**, cao gấp **3,1–4,8 lần** so với **4,49%** tại São Paulo. Tuyến giao hàng liên bang (Interstate) mất trung bình **15,1 ngày**, gần gấp đôi nội bang (**7,9 ngày**) và cước phí cao hơn **75,5%** (26,94 R$ vs 15,35 R$).
 
### 3️⃣ Xu hướng thời gian & các tháng trễ cao (Khai thác `dim_date`)
Giai đoạn 2017–2018 ghi nhận quy mô tăng mạnh từ **111.8k R$** (tháng 1/2017) lên **987.6k R$** vào tháng 11/2017 (Black Friday). Các chỉ số dưới đây tính ở cấp **order** (theo ngày mua, đơn giao thành công hợp lệ). Tháng có tỷ lệ trễ cao đi kèm điểm đánh giá thấp hơn:
- **Tháng 11/2017:** tỷ lệ trễ **12,40%**, điểm đánh giá **3,99 ★**.
- **Tháng 2–3/2018:** tỷ lệ trễ **14,13%** (tháng 2) và **18,96%** (tháng 3), cao nhất trong các tháng được liệt kê; điểm đánh giá **3,88 ★** và **3,81 ★**. Dữ liệu không cho biết nguyên nhân của giai đoạn này.
- **Tháng 6/2018:** tỷ lệ trễ **1,16%**, điểm đánh giá **4,31 ★**.
Đây là mối liên hệ mô tả theo thời gian, không phải bằng chứng nhân quả.
 
---
 
### 4️⃣ Xác định 16 seller ứng viên cần rà soát theo quy tắc sàng lọc của dự án
Các seller này có **Delivered Revenue từ 15.000 R$ trở lên** và điểm đánh giá trung bình dưới **3,8 ★**. Trong đó:
- **11 seller** có ít nhất 30 đơn hàng hợp lệ (tổng 3,201 đơn, trễ 9.00%, thời gian chuẩn bị hàng bình quân 7.04 ngày) được đề xuất ưu tiên rà soát;
- **5 seller** còn lại có ít hơn 30 đơn và nên được theo dõi riêng do cỡ mẫu hạn chế.
> ⚠️ *Đây là danh sách sàng lọc, không phải kết luận rằng mọi seller trong nhóm đều đã được xác nhận là nguyên nhân duy nhất gây ra vấn đề vận hành.*
 
### 5️⃣ Tỷ lệ mua lại hoàn tất là 3,00% và sự khác biệt theo trạng thái đơn đầu tiên
- Tỷ lệ mua lại hoàn tất chung là **3,00%** (2.801 / 93.350 khách hàng có đơn delivered).
- Nhóm khách hàng có đơn đầu tiên giao đúng hạn đạt tỷ lệ mua lại **3,04%**, trong khi nhóm có đơn đầu bị trễ chỉ đạt **2,52%** (chênh lệch tương đối khoảng **17,1%**, kiểm định Chi-square $\chi^2 = 5,2856, p = 0,0215$). Đây là mối liên hệ quan sát được trong dữ liệu tĩnh, không phải bằng chứng khẳng định quan hệ nhân quả duy nhất.
---
 
## 🔍 2. Phân Tích Chi Tiết 5 Câu Hỏi Kinh Doanh Trọng Tâm
 
### Câu hỏi 1: Giao hàng trễ tác động thế nào đến Điểm đánh giá (Review Score)?
 
| Nhóm thời gian giao hàng (Delay Bucket) | Số đơn hàng (Total Orders) | Số đơn có Review hợp lệ | Điểm đánh giá TB | % Đánh giá 1 ★ | % Đánh giá 5 ★ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Giao đúng hạn / Sớm (On Time / Early)** | 89,936 (93.2%) | 89,443 | **4.29 ★** | 6.62% | **62.27%** |
| **Trễ 1 - 3 ngày (1-3 Days Late)** | 1,870 (1.9%) | 1,852 | **3.29 ★** | 25.11% | 33.15% |
| **Trễ 4 - 7 ngày (4-7 Days Late)** | 1,802 (1.9%) | 1,748 | **2.10 ★** | **58.58%** | 14.07% |
| **Trễ > 7 ngày (> 7 Days Late)** | 2,862 (3.0%) | 2,781 | **1.70 ★** | **69.83%** | 7.01% |
 
* **Insight then chốt:** Điểm đánh giá trung bình giảm từ **4,29 ★** ở nhóm đúng hạn xuống **3,29 ★** ở nhóm trễ 1–3 ngày. Ở nhóm trễ 4–7 ngày, điểm trung bình giảm tiếp xuống **2,10 ★** và tỷ lệ đánh giá 1 sao đạt **58,58%**. Mối liên hệ này cho thấy thời gian giao trễ dài hơn đi kèm với mức độ hài lòng thấp hơn trong tập dữ liệu phân tích. Kết quả quan sát chưa đủ để kết luận độ trễ là yếu tố duy nhất quyết định điểm đánh giá.
---
 
### Câu hỏi 2: Nghẽn cổ chai địa lý (Geographic Bottlenecks) nằm ở đâu?
 
| Vùng / Bang | Số đơn hàng | Tỷ lệ trễ hẹn (%) | Thời gian giao TB (ngày) | Điểm đánh giá TB | So với SP (4.49%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Alagoas (AL)** | 397 | **21.41%** | 24.5 ngày | 3.85 ★ | **Gấp 4.8 lần** |
| **Maranhão (MA)** | 717 | **17.43%** | 21.6 ngày | 3.83 ★ | **Gấp 3.9 lần** |
| **Sergipe (SE)** | 335 | **15.22%** | 21.5 ngày | 3.91 ★ | **Gấp 3.4 lần** |
| **Piauí (PI)** | 476 | **13.87%** | 19.5 ngày | 3.99 ★ | **Gấp 3.1 lần** |
| **Ceará (CE)** | 1,279 | **13.76%** | 21.3 ngày | 3.94 ★ | **Gấp 3.1 lần** |
| **Rio de Janeiro (RJ)** | 12,350 | **12.11%** | 15.3 ngày | 3.97 ★ | **Gấp 2.7 lần** |
| *Toàn quốc (Benchmark)* | *96,470* | *6.77%* | *12.6 ngày* | *4.16 ★* | *—* |
| **São Paulo (SP)** | 40,494 | **4.49%** | 8.8 ngày | 4.25 ★ | *Benchmark* |
 
* **Insight then chốt:** Trong nhóm bang được phân tích, các bang vùng Đông Bắc (`AL`, `MA`, `SE`, `PI`, `CE`) chịu tỷ lệ trễ từ 13,8% đến 21,4%, cao gấp **3,1–4,8 lần** so với **São Paulo** (**4,49%**). Đơn hàng vận chuyển liên bang mất trung bình 15.1 ngày (cước bình quân 26.94 R$), gần gấp đôi nội bang (7.9 ngày, 15.35 R$, chênh lệch cước +75.5%).
---
 
### Câu hỏi 3: Ma trận Rủi ro Người bán (Seller Risk Matrix)
 
Phân loại seller được sử dụng như một quy tắc sàng lọc nội bộ của dự án, dựa trên `Delivered Revenue`, điểm đánh giá trung bình và số đơn hàng hợp lệ. Ngưỡng doanh thu là **15.000 R$**, ngưỡng đánh giá thấp là dưới **3,8 sao** và ngưỡng cỡ mẫu tham khảo là **30 đơn**.
 
- **11 seller đủ cỡ mẫu (≥ 30 đơn):** Nhóm gồm 3.201 đơn hàng, tỷ lệ giao trễ **9,00%** và thời gian `dispatch` trung bình **7,04 ngày**. Đây là đối tượng ưu tiên rà soát quy trình vận hành và cam kết thời gian chuẩn bị hàng.
- **5 seller có cỡ mẫu nhỏ (< 30 đơn):** Được đưa vào danh sách theo dõi riêng, tránh kết luận vội vã do cỡ mẫu nhỏ.
---
 
### Câu hỏi 4: Hiệu suất Danh mục Sản phẩm & Làm rõ về Tỷ lệ Hủy đơn
 
*Lưu ý về grain dữ liệu và điều chỉnh phạm vi:*
1. **Làm rõ về Tỷ lệ Hủy đơn (Order Cancellation Analysis):** Trong 99,441 đơn hàng của sàn, có **775 đơn hàng không có dòng sản phẩm** trong bảng `order_items` (trong đó gồm 603 đơn không khả dụng `unavailable`, 164 đơn hủy `canceled`, và 8 đơn thuộc các trạng thái khác chưa phát sinh item: 5 đơn `created`, 2 đơn `invoiced`, 1 đơn `shipped`). Đối với các đơn hàng có sản phẩm, tỷ lệ hủy đơn rất thấp: trong nhóm danh mục doanh thu cao nhất chỉ dao động từ **0,19%** ở `Bed Bath Table` đến **0,80%** ở `Toys`; với các danh mục từ 500 đơn trở lên, khoảng **0,08–1,37%**. Do đó, phân tích danh mục được điều chỉnh tập trung vào các chỉ số vận hành và tài chính cốt lõi.
2. **Grain phân tích:** Doanh thu (`price`), tổng cước (`freight_value`) và sản lượng được tính từ dòng sản phẩm hợp lệ. Điểm đánh giá trung bình và tỷ lệ giao trễ được khử trùng lặp ở cấp **(order_id, category)** để phản ánh đúng trải nghiệm của khách hàng đối với đơn hàng chứa danh mục đó.
| Danh mục Sản phẩm (Top Revenue) | Doanh thu (Delivered R$) | Số sản phẩm bán | Điểm đánh giá TB | Tỷ lệ trễ hẹn (%) | Tỷ trọng cước (% GOV) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Health Beauty** | **1,233,132 R$** | 9,465 | **4.23 ★** | **7.51%** | 12.67% |
| **Watches Gifts** | **1,165,899 R$** | 5,857 | **4.12 ★** | **7.39%** | 7.76% |
| **Bed Bath Table** | **1,023,435 R$** | 10,953 | **4.00 ★** | **7.43%** | 16.47% |
| **Sports Leisure** | 954,674 R$ | 8,430 | 4.23 ★ | 6.57% | 14.61% |
| **Computers Accessories** | 888,614 R$ | 7,643 | 4.08 ★ | 6.39% | 13.94% |
| **Furniture Decor** | 711,928 R$ | 8,160 | 4.06 ★ | 7.12% | 19.13% |
 
---
 
### Câu hỏi 5: Tỷ lệ Khách hàng Quay lại & Đơn hàng Đầu tiên
 
| Trạng thái giao hàng Đơn đầu tiên | Tổng số khách hàng | Tỷ lệ quay lại mua tiếp (%) | Mức độ chênh lệch tương đối |
| :--- | :---: | :---: | :---: |
| **Đơn đầu tiên giao đúng hạn** | 86,995 | **3.04%** | — |
| **Đơn đầu tiên bị giao trễ** | 6,355 | **2.52%** | **-17.1% ($\chi^2 = 5.2856, p = 0.0215$)** |
 
* **Insight then chốt:** Khách hàng nhận đơn đầu tiên đúng hạn có tỷ lệ mua lại **3,04%**, so với **2,52%** ở nhóm nhận đơn đầu bị trễ (chênh lệch tương đối khoảng **17,1%**, kiểm định Chi-square cho thấy sự khác biệt có ý nghĩa thống kê ở mức $\alpha = 0.05$). Đây là **mối liên hệ quan sát được**, phản ánh tín hiệu quan trọng về ấn tượng ban đầu đối với lòng trung thành thương hiệu.
---
 
## 📈 3. Phân Tích Xu Hướng Thời Gian & Tính Mùa Vụ (Khai thác `dim_date` 2017–2018)
 
Bảng chiều ngày tháng (`dim_date`) được liên kết với `fact_order_items` qua khóa `order_date_key` cho phép bóc tách chu kỳ tăng trưởng và áp lực vận hành theo từng tháng. Mọi chỉ số ở cấp **order** (theo ngày mua, đơn giao thành công hợp lệ); doanh thu = tổng `price`, không gồm cước:
 
| Năm - Tháng | Số đơn hàng | Doanh thu sản phẩm (R$) | Tỷ lệ trễ (%) | Điểm Review TB | Sự kiện / Bối cảnh vận hành |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **2017-01** | 750 | 111,798 R$ | 2.93% | 4.20 ★ | Khởi đầu giai đoạn mở rộng quy mô |
| **2017-05** | 3,545 | 489,159 R$ | 2.99% | 4.24 ★ | Tăng trưởng ổn định |
| **2017-08** | 4,193 | 554,700 R$ | 2.91% | **4.31 ★** | Tỷ lệ trễ thấp trước mùa cao điểm |
| **2017-11** | **7,288** | **987,648 R$** | **12.40%** | **3.99 ★** | Tháng Black Friday: đơn tăng mạnh, tỷ lệ trễ tăng, review giảm |
| **2017-12** | 5,513 | 726,033 R$ | 7.46% | 4.09 ★ | Mùa mua sắm Giáng sinh |
| **2018-02** | 6,555 | 826,437 R$ | **14.13%** | **3.88 ★** | Tỷ lệ trễ cao, review thấp |
| **2018-03** | 7,003 | 953,356 R$ | **18.96%** | **3.81 ★** | Tỷ lệ trễ cao nhất và review thấp nhất trong các tháng liệt kê |
| **2018-04** | 6,798 | 973,534 R$ | 4.50% | 4.21 ★ | Tỷ lệ trễ giảm trở lại |
| **2018-06** | 6,096 | 855,592 R$ | **1.16%** | **4.31 ★** | Tỷ lệ trễ thấp nhất trong các tháng liệt kê |
| **2018-08** | 6,351 | 838,577 R$ | 6.19% | 4.31 ★ | Điểm hài lòng ở mức cao |
 
> 💡 **Quan sát:** Trong các tháng liệt kê, tháng có tỷ lệ trễ cao (11/2017: 12,40%; 2–3/2018: 14,13% và 18,96%) đi kèm điểm review thấp hơn (3,81–3,99 ★), còn tháng trễ thấp (6/2018: 1,16%) đi kèm 4,31 ★. Đây là mối liên hệ mô tả ở cấp tháng; dữ liệu không cho phép kết luận độ trễ là nguyên nhân, cũng không cho biết nguyên nhân của các tháng trễ cao. Bảng được sinh bằng SQL Query 6 (`sql/02_kpi_business_queries.sql`) và đối chiếu tự động trong `src/test_data_integrity.py`.
 
---
 
## 🎯 4. Mô Phỏng Ước Lượng Tác Động Vận Hành (Scenario Modeling)
 
Để tránh các đề xuất định tính chung chung, dưới đây là mô phỏng định lượng tác động dựa trên dữ liệu thực nghiệm:
 
### 1. Kịch bản Tối ưu Tuyến Vận chuyển Bang Alagoas (AL)
- **Hiện trạng:** 397 đơn hàng, tỷ lệ trễ **21,41%**, điểm đánh giá trung bình **3,85 ★**. Trong đó, đơn đúng hạn đạt **4,30 ★**, đơn trễ chỉ đạt **2,13 ★**. Tỷ lệ đánh giá 1 sao thực tế tại bang là **15,2%**.
- **Mô phỏng can thiệp:** Nếu thiết lập trung tâm trung chuyển hoặc bổ sung ngày đệm dự báo (buffer days) hợp lý, đưa tỷ lệ trễ tại AL từ **21,41% về mức mục tiêu 10,00%** (chuyển đổi ~45 đơn trễ sang giao đúng hạn):
  $$\text{Review Dự kiến} = (0.90 \times 4.30) + (0.10 \times 2.13) = \mathbf{4.08 \ ★}$$
- **Tác động:** Điểm đánh giá trung bình toàn bang AL ước tính tăng **+0,23 ★** (từ 3,85 lên 4,08 ★, vượt ngưỡng 4 sao) theo công thức mô phỏng trên. Lưu ý: Không đồng nhất tỷ lệ giao trễ thực tế (~21,4%) với tỷ lệ đánh giá 1 sao thực tế tại bang này (15,2%).

### 2. Kịch bản Thiết lập Quy chế SLA 48h cho Nhóm 11 Seller Ứng viên Rủi ro
- **Hiện trạng:** 11 seller này tạo ra 3.201 đơn hàng với thời gian chuẩn bị hàng (`dispatch_days`) trung vị đạt **4,90 ngày** (trung bình 7,04 ngày), cao hơn rõ rệt so với mức trung vị toàn sàn là **2,20 ngày** (trung bình toàn sàn 3,22 ngày); tỷ lệ trễ đạt **9,00%** (288 đơn trễ).
- **Mô phỏng can thiệp:** Buộc bàn giao hàng trong vòng 48h (`dispatch_days <= 2`), đưa tỷ lệ trễ của nhóm về mức benchmark sàn (**4,5%**):
- **Tác động (ước tính giả định theo mô phỏng):** Theo mô phỏng giả định, khoảng **144 đơn hàng** có thể chuyển từ trạng thái giao trễ sang đúng hạn. Với AOV toàn nhóm là 140,47 R$ và AOV của nhóm đơn trễ là 168,15 R$, giá trị đơn hàng tương ứng nằm trong khoảng **20.222 – 24.206 R$**. Đây là giá trị đơn hàng giả định được giảm mức độ phơi nhiễm với rủi ro giao trễ, không phải doanh thu chắc chắn được bảo vệ.

### 3. Kịch bản Bảo vệ Trải nghiệm Đơn hàng Đầu tiên (First Delivered Order Protection)
- **Hiện trạng:** Nhóm khách hàng có đơn delivered hợp lệ đầu tiên trong cửa sổ quan sát bị trễ (6.355 khách) có tỷ lệ mua lại thấp hơn 17,1% so với nhóm đúng hạn (2,52% vs 3,04%).
- **Mô phỏng can thiệp:** Áp dụng cơ chế theo dõi ưu tiên vận chuyển cho người mua có đơn đầu tiên, mô phỏng giảm tỷ lệ trễ đơn đầu từ **6,81% xuống 3,50%** (chuyển đổi giả định khoảng **~3.088 khách hàng** từ nhóm trễ sang đúng hạn):
- **Tác động (ước tính mô phỏng giả định):** Giữ chân thêm ước tính **~16 khách hàng** ($3.088 \times (3,04\% - 2,52\%)$) quay lại phát sinh đơn hàng lần 2. Với giá trị đơn hàng trung bình AOV 137,04 R$, doanh thu bổ sung ước tính khoảng **~2.192 R$** (đây là giá trị mô phỏng giả định theo dữ liệu quan sát, không phải cam kết doanh thu chắc chắn phát sinh).

---
 
## 🔒 5. Kiểm Chứng Dữ Liệu & Quy Chuẩn Tập Mẫu Số
 
1. **Phân biệt 96,096 vs 93,350 khách hàng:**
   - **96,096 khách hàng:** Tổng số khách hàng trên toàn sàn (99,441 đơn mọi trạng thái). Tỷ lệ đặt mua lần 2 là 3.12%.
   - **93,350 khách hàng:** Tập khách hàng có đơn giao thành công hợp lệ (96,470 đơn delivered). Tỷ lệ mua lại hoàn tất là 3.00% (2,801 khách hàng). Mẫu số này được dùng thống nhất trong báo cáo, dashboard và mô hình Kimball Star Schema.
2. **Chuẩn hóa ngày lịch (`dt.normalize()`):** Trường ngày dự kiến trong dữ liệu gốc luôn mang mốc giờ mặc định `00:00:00`. Pipeline đã chuẩn hóa cấp ngày lịch để đảm bảo đơn giao trong ngày dự kiến được tính đúng hạn (delay = 0), tránh lỗi lệch giờ làm tăng khống tỷ lệ trễ.
3. **Bộ kiểm thử tự động (`src/test_data_integrity.py`) và đối chiếu Notebook:** Toàn bộ 5 bảng trong Star Schema, khóa chính ghép `(order_id, order_item_id)`, ràng buộc khóa ngoại (0 orphan records), và 6 truy vấn SQL (`sql/02_kpi_business_queries.sql`) đều được kiểm tra thực thi thành công. Các chỉ số KPI cốt lõi (Query 1, Query 5, Query 6) được đối chiếu độc lập giữa SQLite và Pandas; Query 2, 3, 4 được đối chiếu trực tiếp giữa Notebook và các bảng kết quả xuất ra từ Python (143/143 checks PASS, Chi-square $\chi^2 = 5.29, p = 0.0215$). Bộ kiểm thử và notebook xác nhận tính nhất quán của số liệu đầu vào và các phép tính mô phỏng, không bảo đảm hiệu quả thực tế của các hành động đề xuất.

---
*Báo cáo được tổng hợp dựa trên kết quả tính toán định lượng chính xác từ mã nguồn Python (`src/04_exploratory_data_analysis.py`), notebook đối chiếu (`notebooks/01_eda_and_insights.ipynb`) và cơ sở dữ liệu Star Schema (`data/olist_star_schema.db`).*
 