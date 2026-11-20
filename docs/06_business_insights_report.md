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

### 3️⃣ Xu hướng thời gian & Áp lực mùa vụ (Khai thác `dim_date` ở cấp độ đơn hàng)
Giai đoạn 2017–2018 ghi nhận sự tăng trưởng quy mô mạnh mẽ từ **111.8k R$** (tháng 1/2017) lên đỉnh điểm **987.6k R$** vào Black Friday (tháng 11/2017). Tuy nhiên, các đợt cao điểm mùa vụ và biến động vận tải đã cho thấy các giai đoạn tỷ lệ trễ tăng cao:
- **Black Friday (11/2017):** Sản lượng đơn tăng lên 7,288 đơn, tỷ lệ trễ ở mức **12,40%**, điểm đánh giá trung bình **3,99 ★**.
- **Giai đoạn tỷ lệ trễ cao đầu năm 2018:** Tỷ lệ giao hàng trễ ở cấp đơn hàng ghi nhận **14,13%** (tháng 2/2018, review **3,88 ★**) và **18,96%** (tháng 3/2018, review **3,81 ★**).
- **Giai đoạn tỷ lệ trễ thấp giữa năm 2018:** Khi tỷ lệ trễ hạ nhiệt về mức **1,16%** (tháng 6/2018), điểm đánh giá trung bình đạt **4,31 ★**.

### 4️⃣ Xác định 16 seller ứng viên cần rà soát theo quy tắc sàng lọc của dự án
Các seller này có **Delivered Revenue từ 15.000 R$ trở lên** và điểm đánh giá trung bình dưới **3,8 ★**. Trong đó:
- **11 seller** có ít nhất 30 đơn hàng hợp lệ (tổng 3,201 đơn, trễ 9.00%, thời gian chuẩn bị hàng bình quân 7.04 ngày) được đề xuất ưu tiên rà soát;
- **5 seller** còn lại có ít hơn 30 đơn và nên được theo dõi riêng do cỡ mẫu hạn chế.
> ⚠️ *Đây là danh sách sàng lọc, không phải kết luận rằng mọi seller trong nhóm đều đã được xác nhận là nguyên nhân gây ra vấn đề vận hành.*

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

- **Insight then chốt:** Điểm đánh giá trung bình giảm từ **4,29 ★** ở nhóm đúng hạn xuống **3,29 ★** ở nhóm trễ 1–3 ngày. Ở nhóm trễ 4–7 ngày, điểm trung bình giảm tiếp xuống **2,10 ★** và tỷ lệ đánh giá 1 sao đạt **58,58%**. Mối liên hệ này cho thấy thời gian giao trễ dài hơn đi kèm với mức độ hài lòng thấp hơn trong tập dữ liệu phân tích. Kết quả quan sát chưa đủ để kết luận độ trễ là yếu tố duy nhất quyết định điểm đánh giá.

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

- **Insight then chốt:** Trong nhóm bang được phân tích, các bang vùng Đông Bắc (`AL`, `MA`, `SE`, `PI`, `CE`) chịu tỷ lệ trễ từ 13,8% đến 21,4%, cao gấp **3,1–4,8 lần** so với **São Paulo** (**4,49%**). Đơn hàng vận chuyển liên bang mất trung bình 15.1 ngày (cước bình quân 26.94 R$), gần gấp đôi nội bang (7.9 ngày, 15.35 R$, chênh lệch cước +75.5%).

---

### Câu hỏi 3: Ma trận Rủi ro Người bán (Seller Risk Matrix)

Phân loại seller được sử dụng như một quy tắc sàng lọc nội bộ của dự án, dựa trên `Delivered Revenue`, điểm đánh giá trung bình và số đơn hàng hợp lệ. Ngưỡng doanh thu là **15.000 R$**, ngưỡng đánh giá thấp là dưới **3,8 sao** và ngưỡng cỡ mẫu tham khảo là **30 đơn**.

- **11 seller đủ cỡ mẫu (≥ 30 đơn):** Nhóm gồm 3.201 đơn hàng, tỷ lệ giao trễ **9,00%** và thời gian `dispatch` trung bình **7,04 ngày**. Đây là đối tượng ưu tiên rà soát quy trình vận hành và cam kết thời gian chuẩn bị hàng.
- **5 seller có cỡ mẫu nhỏ (< 30 đơn):** Được đưa vào danh sách theo dõi riêng, tránh kết luận vội vã do cỡ mẫu nhỏ.

---

### Câu hỏi 4: Hiệu suất Danh mục Sản phẩm & Làm rõ về Tỷ lệ Hủy đơn

*Lưu ý về grain dữ liệu và điều chỉnh phạm vi:*
1. **Làm rõ về Tỷ lệ Hủy đơn (Order Cancellation Analysis):** Trong 99,441 đơn hàng của sàn, có **775 đơn hàng không có dòng sản phẩm** trong bảng `order_items` (gồm 603 đơn không khả dụng `unavailable`, 164 đơn hủy `canceled`, và 8 đơn còn lại thuộc các trạng thái khác không có bản ghi trong `order_items`). Đối với các đơn hàng có sản phẩm, tỷ lệ hủy đơn rất thấp (chỉ dao động từ **0,19%** ở `Bed Bath Table` đến **0,80%** ở `Toys`). Do đó, phân tích danh mục được điều chỉnh tập trung vào các chỉ số vận hành và tài chính cốt lõi.
2. **Grain phân tích:** Doanh thu (`price`), tổng cước (`freight_value`) và sản lượng được tính từ dòng sản phẩm hợp lệ. Điểm đánh giá trung bình và tỷ lệ giao trễ được khử trùng lặp ở cấp **(order_id, category)** để phản ánh đúng trải nghiệm của khách hàng đối với đơn hàng chứa danh mục đó.

| Danh mục Sản phẩm (Top Revenue) | Doanh thu (Delivered R$) | Số sản phẩm bán | Điểm đánh giá TB | Tỷ lệ trễ hẹn (%) | Tỷ trọng cước (% GOV) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Health Beauty** | **1,233,132 R$** | 9,465 | **4.23 ★** | **7.51%** | 12.67% |
| **Watches Gifts** | **1,165,899 R$** | 5,857 | **4.12 ★** | **7.39%** | 7.76% |
| **Bed Bath Table** | **1,023,435 R$** | 10,953 | **4.00 ★** | **7.43%** | 16.47% |
| **Sports Leisure** | 959,101 R$ | 8,431 | 4.14 ★ | 7.15% | 15.11% |
| **Computers Accessories** | 896,876 R$ | 7,680 | 3.98 ★ | 8.85% | 13.91% |
| **Furniture Decor** | 711,540 R$ | 8,054 | 3.93 ★ | 8.87% | 20.89% |

---

### Câu hỏi 5: Tỷ lệ Khách hàng Quay lại & Đơn hàng Đầu tiên

| Trạng thái giao hàng Đơn đầu tiên | Tổng số khách hàng | Tỷ lệ quay lại mua tiếp (%) | Mức độ chênh lệch tương đối |
| :--- | :---: | :---: | :---: |
| **Đơn đầu tiên giao đúng hạn** | 86,995 | **3.04%** | — |
| **Đơn đầu tiên bị giao trễ** | 6,355 | **2.52%** | **-17.1% ($\chi^2 = 5.2856, p = 0.0215$)** |

- **Insight then chốt:** Khách hàng nhận đơn đầu tiên đúng hạn có tỷ lệ mua lại **3,04%**, so với **2,52%** ở nhóm nhận đơn đầu bị trễ (chênh lệch tương đối khoảng **17,1%**, kiểm định Chi-square cho thấy sự khác biệt có ý nghĩa thống kê ở mức $\alpha = 0.05$). Đây là **mối liên hệ quan sát được**, phản ánh tín hiệu quan trọng về ấn tượng ban đầu đối với lòng trung thành thương hiệu.

---

## 📈 3. Phân Tích Xu Hướng Thời Gian & Tính Mùa Vụ (Khai thác `dim_date` 2017–2018)

Bảng chiều ngày tháng (`dim_date`) được liên kết với `fact_order_items` qua khóa `order_date_key` cho phép bóc tách chu kỳ tăng trưởng và biến động chỉ số vận hành theo từng tháng ở cấp độ đơn hàng (đồng bộ với SQL Query 6 và bảng chuẩn `EXPECTED_MONTHLY`):

| Năm - Tháng | Số đơn hàng | Doanh thu sản phẩm (R$) | Tỷ lệ trễ (%) | Điểm Review TB | Ghi chú chuỗi thời gian (Order-level) |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **2017-01** | 750 | 111,798 R$ | 2.93% | 4.20 ★ | Khởi đầu giai đoạn mở rộng quy mô |
| **2017-05** | 3,545 | 489,159 R$ | 2.99% | 4.24 ★ | Tăng trưởng ổn định |
| **2017-08** | 4,193 | 554,700 R$ | 2.91% | **4.31 ★** | Mức review cao trong nhóm tháng mốc |
| **2017-11** | **7,288** | **987,648 R$** | **12.40%** | **3.99 ★** | **Cao điểm Black Friday: Doanh thu đỉnh, tỷ lệ trễ 12.40%** |
| **2017-12** | 5,513 | 726,033 R$ | 7.46% | 4.09 ★ | Mùa mua sắm cuối năm |
| **2018-02** | 6,555 | 826,437 R$ | **14.13%** | **3.88 ★** | Tỷ lệ trễ cao đầu năm 2018 |
| **2018-03** | 7,003 | 953,356 R$ | **18.96%** | **3.81 ★** | **Tỷ lệ trễ cao nhất trong nhóm tháng mốc, điểm review thấp nhất** |
| **2018-04** | 6,798 | 973,534 R$ | 4.50% | 4.21 ★ | Tỷ lệ trễ giảm về 4.50%, điểm review hồi phục |
| **2018-06** | 6,096 | 855,592 R$ | **1.16%** | **4.31 ★** | Tỷ lệ trễ thấp nhất trong nhóm tháng mốc, điểm review 4.31 ★ |
| **2018-08** | 6,351 | 838,577 R$ | 6.19% | **4.31 ★** | Duy trì điểm đánh giá trung bình 4.31 ★ |

> 💡 **Phát hiện quan trọng:** Ở cấp độ chuỗi thời gian tháng (order-level), các tháng ghi nhận tỷ lệ trễ cao đi kèm với điểm đánh giá trung bình thấp hơn (như `2017-11` với **12.40%** trễ và **3.99 ★**, `2018-02` với **14.13%** trễ và **3.88 ★**, `2018-03` với **18.96%** trễ và **3.81 ★**), trong khi tháng có tỷ lệ trễ thấp như `2018-06` (**1.16%** trễ) ghi nhận điểm đánh giá trung bình **4.31 ★**. Đây là sự cùng biến động mô tả theo tháng, không tự nó chứng minh nguyên nhân gây trễ.

---

## 🎯 4. Mô Phỏng Ước Lượng Tác Động Vận Hành (Scenario Modeling)

Để tránh các đề xuất định tính chung chung, dưới đây là mô phỏng định lượng tác động dựa trên dữ liệu thực nghiệm (lưu ý: các kịch bản dưới đây là giả định mô phỏng từ dữ liệu quan sát, không phải kết luận nhân quả tuyệt đối):

### 1. Kịch bản Tối ưu Tuyến Vận chuyển Bang Alagoas (AL)
- **Hiện trạng:** 397 đơn hàng, tỷ lệ trễ **21,41%**, điểm đánh giá trung bình **3,85 ★**. Trong đó, đơn đúng hạn đạt **4,30 ★**, đơn trễ chỉ đạt **2,13 ★**.
- **Mô phỏng can thiệp:** Nếu thiết lập trung tâm trung chuyển hoặc bổ sung ngày đệm dự báo (buffer days) hợp lý, đưa tỷ lệ trễ tại AL từ **21,41% về mức mục tiêu 10,00%** (chuyển đổi ~45 đơn trễ sang giao đúng hạn):
  $$\text{Review Dự kiến} = (0.90 \times 4.30) + (0.10 \times 2.13) = \mathbf{4.08 \ ★}$$
- **Tác động:** Điểm đánh giá trung bình toàn bang AL sẽ tăng **+0,23 ★** (từ 3.85 lên 4.08, vượt ngưỡng 4 sao), và tỷ lệ đơn nhận đánh giá 1 sao tại bang này ước tính giảm từ ~22% xuống còn ~11%.

### 2. Kịch bản Thiết lập Quy chế SLA 48h cho Nhóm 11 Seller Ứng viên Rủi ro
- **Hiện trạng:** 11 seller này tạo ra 3,201 đơn hàng với thời gian chuẩn bị hàng (`dispatch_days`) trung bình lên tới **7,04 ngày** (so với mức trung vị sàn là 3 ngày), tỷ lệ trễ đạt **9,00%** (288 đơn trễ).
- **Mô phỏng can thiệp:** Buộc bàn giao hàng trong vòng 48h (`dispatch_days <= 2`), đưa tỷ lệ trễ của nhóm về mức benchmark sàn (**4,5%**):
- **Tác động (ước tính giả định theo mô phỏng):** Khoảng **144 đơn hàng** được giả định chuyển từ trễ sang đúng hạn; nhân với giá trị đơn hàng trung bình của nhóm cho ước tính giả định hơn **22.000 R$** giá trị đơn hàng giảm nguy cơ khiếu nại/hủy đơn (đây là kết quả tính toán dựa trên giả định mô phỏng, không phải doanh thu chắc chắn thu về).

### 3. Kịch bản Bảo vệ Trải nghiệm Đơn hàng Đầu tiên (First Delivered Order Protection)
- **Hiện trạng:** Nhóm khách hàng có đơn đầu bị trễ (6,355 khách) có tỷ lệ mua lại thấp hơn 17.1% so với nhóm đúng hạn (2.52% vs 3.04%).
- **Mô phỏng can thiệp:** Áp dụng cơ chế theo dõi ưu tiên vận chuyển cho người mua lần đầu, giảm tỷ lệ trễ đơn đầu từ **6,77% xuống 3,50%** (chuyển ~3,000 khách hàng mới từ nhóm trễ sang đúng hạn):
- **Tác động:** Giữ chân thêm ước tính **~16 khách hàng trung thành** quay lại phát sinh đơn hàng lần 2, tạo ra doanh thu bổ sung ước tính từ 3,000 – 5,000 R$ mỗi chu kỳ mà không tốn thêm chi phí thu hút khách hàng mới (CAC).

---

## 🔒 5. Kiểm Chứng Dữ Liệu & Quy Chuẩn Tập Mẫu Số

1. **Phân biệt 96,096 vs 93,350 khách hàng:**
  - **96,096 khách hàng:** Tổng số khách hàng trên toàn sàn (99,441 đơn mọi trạng thái). Tỷ lệ đặt mua lần 2 là 3.12%.
  - **93,350 khách hàng:** Tập khách hàng có đơn giao thành công hợp lệ (96,470 đơn delivered). Tỷ lệ mua lại hoàn tất là 3.00% (2,801 khách hàng). Mẫu số này được dùng thống nhất trong báo cáo, dashboard và mô hình Kimball Star Schema.
2. **Chuẩn hóa ngày lịch (`dt.normalize()`):** Trường ngày dự kiến trong dữ liệu gốc luôn mang mốc giờ mặc định `00:00:00`. Pipeline đã chuẩn hóa cấp ngày lịch để đảm bảo đơn giao trong ngày dự kiến được tính đúng hạn (delay = 0), tránh lỗi lệch giờ làm tăng khống tỷ lệ trễ.
3. **Bộ kiểm thử tự động (`src/test_data_integrity.py`) và đối chiếu Notebook (143/143 checks):** Toàn bộ 5 bảng trong Star Schema, khóa chính ghép `(order_id, order_item_id)`, ràng buộc khóa ngoại (0 orphan records), 6 truy vấn SQL (`sql/02_kpi_business_queries.sql`) và các chỉ số thống kê (96,470 đơn, 93.23% đúng hạn, Chi-square $\chi^2 = 5.2856, p = 0.0215$, chuỗi thời gian tháng cấp order) đã được kiểm thử và đối chiếu đồng bộ giữa Python, Notebook và SQLite.

---
*Báo cáo được tổng hợp dựa trên kết quả tính toán định lượng chính xác từ mã nguồn Python (`src/04_exploratory_data_analysis.py`), notebook đối chiếu (`notebooks/01_eda_and_insights.ipynb`) và cơ sở dữ liệu Star Schema (`data/olist_star_schema.db`).*