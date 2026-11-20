# XÁC ĐỊNH & ĐÁNH GIÁ BÀI TOÁN KINH DOANH (BUSINESS PROBLEM VALIDATION)

> Tài liệu này xác định phạm vi, mục tiêu và giới hạn của dự án phân tích dữ liệu Olist, dựa trên khả năng thực tế của tập dữ liệu.

---

## 1. Bối cảnh Kinh doanh (Business Context)

Olist là nền tảng thương mại điện tử (Marketplace) kết nối các doanh nghiệp vừa và nhỏ (SMBs) tại Brazil với người tiêu dùng trên toàn quốc. Trong mô hình này, Olist không trực tiếp sở hữu kho hàng hay đội xe vận chuyển mà giữ vai trò quản lý trải nghiệm tổng thể: kết nối người mua - người bán, xử lý thanh toán và giám sát mạng lưới đối tác logistics. 

Do đó, **Hiệu suất Giao hàng (Delivery Performance)** và **Mức độ Hài lòng Khách hàng (Customer Satisfaction - đo bằng Review Score)** là hai yếu tố sống còn quyết định tỷ lệ giữ chân khách hàng (Retention) và sự tăng trưởng doanh thu bền vững của sàn.

---

## 2. Bài toán Nghiệp vụ Ban đầu (Initial Business Problem)

> *"Ban giám đốc vận hành của Olist Marketplace muốn hiểu rõ các yếu tố ảnh hưởng đến trải nghiệm khách hàng, đặc biệt là hiệu suất vận chuyển và mức độ hài lòng, đồng thời xác định các khu vực địa lý, đối tác bán hàng (sellers) hoặc danh mục sản phẩm cần được ưu tiên cải thiện để bảo vệ uy tín thương hiệu và hiệu quả kinh doanh."*

---

## 3. Đánh giá Khả năng Đáp ứng của Tập Dữ liệu (Dataset Capability Assessment)

Dựa trên việc kiểm tra cấu trúc dữ liệu và thực tế dữ liệu (Phase 1), khả năng trả lời các câu hỏi nghiệp vụ được phân loại chi tiết:

| Câu hỏi Nghiệp vụ | Khả năng Đáp ứng | Phân tích Khả thi & Giới hạn Thực tế |
| :--- | :--- | :--- |
| **Mối liên hệ giữa thời gian giao hàng trễ và điểm đánh giá (Review Score)?** | ✅ ĐÁP ỨNG TỐT | Đầy đủ dữ liệu mốc thời gian `order_purchase_timestamp`, `order_estimated_delivery_date`, `order_delivered_customer_date` và `review_score`. |
| **Khu vực (Bang/Tuyến đường) hoặc Seller nào có tỷ lệ trễ cao và điểm hài lòng thấp?** | ✅ ĐÁP ỨNG TỐT | Có thể liên kết `orders` với `customers` (bang nhận hàng) và `order_items` (`seller_id`) một cách an toàn khi tổng hợp đúng cấp độ grain (tránh lặp dòng). |
| **Tỷ lệ khách hàng quay lại mua hàng (Repeat Purchase Rate) là bao nhiêu?** | ✅ ĐÁP ỨNG TỐT | Xác định được qua mã định danh thực `customer_unique_id`. *(Lưu ý: Có **96,096 khách hàng duy nhất** trên toàn bộ 99,441 đơn hàng phát sinh, và **93,350 khách hàng duy nhất** có ít nhất 1 đơn giao thành công hợp lệ)*. |
| **Tỷ lệ hủy đơn và hiệu suất theo danh mục sản phẩm (Category Performance)?** | ⚠️ ĐIỀU CHỈNH PHẠM VI | Trong 99,441 đơn hàng, có 775 đơn hàng không có dòng sản phẩm trong `order_items` (gồm 603 đơn không có hàng `unavailable`, 164 đơn bị hủy `canceled`, và 8 đơn thuộc trạng thái khác: 5 `created`, 2 `invoiced`, 1 `shipped`). Đối với các đơn có sản phẩm, tỷ lệ hủy rất thấp: dưới 0.8% trong nhóm danh mục doanh thu cao nhất; với các danh mục từ 500 đơn trở lên, tỷ lệ này dao động 0.08–1.37%. Do đó, phân tích danh mục được điều chỉnh tập trung vào: **Doanh thu, Tỷ trọng cước phí vận chuyển (Freight Ratio), Tỷ lệ giao trễ và Điểm đánh giá** ở cấp Order-Category. |
| **Nguyên nhân gốc rễ (Root Cause) của việc giao hàng trễ từ phía nhà xe?** | ⚠️ MỘT PHẦN | Dữ liệu cho biết *khi nào* và *ở đâu* bị trễ, thời gian seller bàn giao (`dispatch_days`) và thời gian vận chuyển (`carrier_days`). Không có tên hãng vận chuyển cụ thể (Correios vs nhà xe tư nhân) hay dữ liệu thời tiết. |
| **Biên lợi nhuận ròng (Profit Margin) của từng đơn hàng/seller?** | ❌ KHÔNG KHẢ THI | Dữ liệu chỉ ghi nhận giá bán (`price`) và phí ship (`freight_value`), không có Giá vốn hàng bán (COGS) hay chi phí vận hành sàn. |
| **Phân tích nhân khẩu học khách hàng (Tuổi, Giới tính, Thu nhập)?** | ❌ KHÔNG KHẢ THI | Bảng `customers` tuân thủ ẩn danh, chỉ có vị trí địa lý (`zip_code`, `city`, `state`). |

---

## 4. Bài toán Nghiệp vụ Sau khi Tinh chỉnh (Final Business Problem)

> *"Khai thác dữ liệu giao dịch lịch sử 2016–2018, dự án phân tích tác động của **Độ trễ Giao hàng (Delivery Delay)** đối với **Mức độ Hài lòng Khách hàng (Review Score)** và **Tỷ lệ Mua lại (Repeat Purchases)**. Đồng thời, nhận diện các **Điểm nghẽn Logistics theo Địa lý**, sàng lọc danh sách **Seller ứng viên rủi ro cao (High Revenue - Low Satisfaction)**, và phân tích **Hiệu suất Danh mục Sản phẩm** nhằm cung cấp cơ sở định lượng cho các thử nghiệm vận hành tối ưu hóa trải nghiệm khách hàng."*

---

## 5. Mục tiêu Phân tích Cụ thể (Business Objectives)

1. **Đo lường định lượng** mức độ sụt giảm của điểm đánh giá theo các mức độ trễ giao hàng (Delay Buckets).
2. **Nhận diện điểm nóng logistics:** Xác định các bang có tỷ lệ giao trễ cao nhất và đo lường khoảng cách vận chuyển, chi phí giữa giao hàng liên bang (Interstate) so với nội bang (Intrastate).
3. **Phân tích xu hướng thời gian & tính mùa vụ:** Đánh giá biến động doanh thu, sản lượng đơn, tỷ lệ giao trễ và điểm đánh giá theo tháng (đặc biệt là tháng 11/2017 – Black Friday, và giai đoạn tháng 2–3/2018 có tỷ lệ trễ cao). Dữ liệu chỉ cho thấy các tháng trễ cao đi kèm review thấp; không có thông tin xác định nguyên nhân (đình công, quá tải, v.v.) nên không suy diễn quan hệ nhân quả.
4. **Sàng lọc Seller rủi ro:** Áp dụng chuẩn khử trùng lặp cấp đơn hàng để định vị nhóm đối tác bán hàng có doanh thu lớn nhưng điểm đánh giá kém, phân tách rõ nhóm đủ cỡ mẫu (≥ 30 đơn) và nhóm cỡ mẫu nhỏ.
5. **Đánh giá hiệu suất ngành hàng:** Phân tích doanh thu và gánh nặng tỷ trọng cước phí vận chuyển trên giá trị đơn hàng theo từng danh mục sản phẩm.
6. **Đo lường tỷ lệ giữ chân:** Đánh giá mối liên hệ giữa trạng thái giao hàng ở đơn đầu tiên đối với xác suất mua lại lần 2.

---

## 6. Các Bên Liên quan (Stakeholders)

* **Ban Giám đốc Vận hành (Head of Operations):** Cần bức tranh tổng thể về sức khỏe vận hành, điểm nghẽn địa lý và tác động của độ trễ đến thương hiệu.
* **Đội ngũ Quản lý Đối tác Bán hàng (Seller Management):** Cần danh sách sàng lọc đối tác có vấn đề vận hành để rà soát quy trình bàn giao hàng (SLA dispatching).
* **Đội ngũ Logistics:** Cần dữ liệu tuyến vận chuyển liên bang và các bang trọng điểm để đàm phán hợp đồng hoặc hiệu chỉnh ngày giao dự kiến.
* **Đội ngũ Chăm sóc Khách hàng (Customer Support):** Cần thông tin dự báo về rủi ro đánh giá 1 sao khi đơn trễ để chủ động chăm sóc.

---

## 7. 5 Câu hỏi Kinh doanh Trọng tâm

1. **Giao trễ và Mức độ Hài lòng:** Những đơn hàng bị giao trễ có điểm review trung bình thấp hơn bao nhiêu so với đơn đúng hạn? Ở mốc thời gian trễ nào thì tỷ lệ đánh giá 1 sao gia tăng đột biến?
2. **Điểm nghẽn Địa lý & Vận chuyển Liên bang:** Bang nào có tỷ lệ giao trễ cao nhất so với São Paulo? Tuyến vận chuyển liên bang làm tăng thời gian và chi phí cước ship bao nhiêu so với nội bang?
3. **Ma trận Rủi ro Người bán:** Những seller nào thuộc nhóm doanh thu cao (≥ 15,000 R$) nhưng điểm đánh giá kém (< 3.8 ★)? Nhóm nào đủ cỡ mẫu để ưu tiên can thiệp vận hành?
4. **Hiệu suất Danh mục Sản phẩm:** Ngành hàng nào dẫn đầu về doanh thu? Những ngành hàng cồng kềnh có tỷ trọng cước phí cao và điểm đánh giá ra sao?
5. **Hành vi Khách hàng Quay lại:** Tỷ lệ khách hàng mua lại hoàn tất là bao nhiêu? Trải nghiệm giao hàng ở đơn đầu tiên (đúng hạn vs trễ) có mối liên hệ như thế nào với tỷ lệ quay lại mua tiếp?

---

## 8. Chú thích Quy chuẩn Tập Mẫu số Khách hàng (96,096 vs 93,350)

> 📌 **Phân biệt hai khái niệm khách hàng trong dự án:**
> - **96,096 khách hàng duy nhất (Total Unique Customers):** Tính trên toàn bộ **99,441 đơn hàng phát sinh** ở mọi trạng thái (`created`, `approved`, `shipped`, `delivered`, `canceled`, `unavailable`). Tỷ lệ khách hàng từng đặt đơn từ lần thứ 2 trở lên trên toàn sàn là **3.12%** (2,997 / 96,096 khách hàng).
> - **93,350 khách hàng duy nhất có đơn giao thành công (Delivered Unique Customers):** Tính trên tập **96,470 đơn hàng đã giao thành công hợp lệ** (`is_valid_delivery_delay = 1`). Đây là mẫu số quy chuẩn được dùng trên Power BI Dashboard, Báo cáo Insights và Mô hình Star Schema để tính **Tỷ lệ Mua lại Hoàn tất (Repeat Completed Purchases: 2,801 / 93,350 = 3.00%)**, đảm bảo phản ánh chính xác khách hàng đã thực sự trải nghiệm chu trình giao hàng trọn vẹn.

---

## 9. Giả định & Giới hạn Phân tích

1. **Chuẩn hóa ngày lịch cho chỉ số giao trễ:** Do trường ngày dự kiến (`order_estimated_delivery_date`) trong dữ liệu gốc luôn mang mốc giờ mặc định `00:00:00`, việc tính toán độ trễ được chuẩn hóa về cấp ngày (`dt.normalize()`). Đơn giao trong ngày dự kiến được tính là đúng hạn.
2. **Quan sát tĩnh & Giới hạn Right-Censoring:** Dữ liệu phản ánh giai đoạn 2016–2018. Khách hàng gia nhập vào cuối giai đoạn quan sát có ít thời gian để quay lại mua đơn thứ hai hơn. Tỷ lệ 3.00% là tỷ lệ tích lũy tĩnh, không tương đương tỷ lệ retention trong một khoảng thời gian cố định (như 60 ngày).
3. **Mối liên hệ tương quan (Correlation vs Causation):** Các phân tích chỉ ra mối liên hệ thống kê giữa độ trễ, điểm đánh giá và tỷ lệ mua lại trong tập dữ liệu quan sát, không phải bằng chứng khẳng định quan hệ nhân quả duy nhất. Các đề xuất vận hành được định vị là giả thuyết cần kiểm chứng qua thử nghiệm có đối chứng (A/B Testing).
