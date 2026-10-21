# BUSINESS PROBLEM VALIDATION

> Tài liệu này xác định phạm vi, mục tiêu và giới hạn của dự án phân tích dữ liệu Olist, dựa trên khả năng thực tế của dataset.

## 1. Business Context
Olist là nền tảng marketplace kết nối các doanh nghiệp nhỏ (small businesses) tại Brazil với người tiêu dùng. Trong mô hình này, Olist không trực tiếp nắm giữ hàng tồn kho mà chịu trách nhiệm về trải nghiệm tổng thể của đơn hàng, bao gồm: kết nối người mua - người bán, xử lý thanh toán và theo dõi logistics. Do đó, **Delivery Performance** (Hiệu suất giao hàng) và **Customer Satisfaction** (Sự hài lòng của khách hàng, đo bằng Review Score) là hai yếu tố sống còn quyết định tỷ lệ giữ chân khách hàng (Retention) và doanh thu bền vững.

## 2. Initial Business Problem
"Ban giám đốc vận hành của Olist Marketplace muốn hiểu các yếu tố ảnh hưởng đến trải nghiệm khách hàng, đặc biệt là delivery performance và customer satisfaction, đồng thời xác định những khu vực (geography), seller hoặc product category cần được ưu tiên cải thiện để bảo vệ hiệu quả kinh doanh."

## 3. Dataset Capability Assessment
Dựa trên việc kiểm tra schema và dữ liệu thực tế (Phase 1), khả năng trả lời của dataset được phân loại như sau:

| Business Question | Capability | Lý do / Giới hạn dữ liệu |
| :--- | :--- | :--- |
| **Mối tương quan giữa thời gian giao hàng trễ và điểm đánh giá (Review Score)?** | ✅ ANSWERABLE | Có đầy đủ `order_purchase_timestamp`, `order_estimated_delivery_date`, `order_delivered_customer_date` và `review_score`. |
| **Khu vực (State/City) hoặc Seller nào đang có hiệu suất giao hàng và sự hài lòng thấp nhất?** | ✅ ANSWERABLE | Có thể join `orders` với `customers` (lấy state) và `order_items` (lấy `seller_id`) một cách an toàn nếu aggregate đúng grain. |
| **Tỷ lệ khách hàng quay lại mua hàng (Repeat Purchase Rate) là bao nhiêu?** | ✅ ANSWERABLE | Có thể tính toán bằng cách group by `customer_unique_id` (96,096 unique customers trong 99,441 orders). |
| **Nguyên nhân gốc rễ (Root Cause) của việc giao hàng trễ là do đâu?** | ⚠️ PARTIALLY ANSWERABLE | Dataset chỉ cho biết *khi nào* và *ở đâu* bị trễ. Không có thông tin về tên đơn vị vận chuyển cụ thể (carrier name), điều kiện thời tiết, hoặc lý do hủy hàng chi tiết. |
| **Biên lợi nhuận (Profit Margin) của từng đơn hàng/seller?** | ❌ NOT ANSWERABLE | Dataset chỉ có `price` (giá bán) và `freight_value` (phí ship). Không có dữ liệu về Giá vốn hàng bán (COGS) hoặc chi phí vận hành của Olist. |
| **Phân tích nhân khẩu học khách hàng (Độ tuổi, Thu nhập, Giới tính)?** | ❌ NOT ANSWERABLE | Bảng `customers` chỉ chứa `customer_id`, `customer_unique_id`, `zip_code`, `city`, `state`. Không có dữ liệu cá nhân. |

## 4. Final Business Problem (Đã điều chỉnh)
"Dựa trên dữ liệu lịch sử giao dịch, dự án sẽ phân tích tác động của **Delivery Delay** (Số ngày giao hàng trễ so với dự kiến) đến **Customer Satisfaction** (Review Score). Đồng thời, dự án sẽ xác định các **Seller** và **Product Categories** có doanh thu cao nhưng điểm hài lòng thấp (High Risk), cũng như đánh giá **Repeat Purchase Rate** để đề xuất các hành động ưu tiên nhằm tối ưu hóa trải nghiệm khách hàng và giảm thiểu rủi ro kinh doanh."

## 5. Business Objective
1. Đo lường mức độ ảnh hưởng của việc giao hàng trễ đến điểm đánh giá của khách hàng.
2. Xác định top 3 bang (states) và top 5 sellers có tỷ lệ giao hàng trễ cao nhất kèm theo khối lượng đơn hàng đáng kể (để tránh kết luận từ sample size quá nhỏ).
3. Tính toán và phân tích Repeat Purchase Rate dựa trên `customer_unique_id`.
4. Đề xuất 3-5 hành động cụ thể, khả thi cho đội ngũ vận hành và quản lý seller.

## 6. Stakeholders
- **Primary:** Ban giám đốc vận hành (Head of Operations), Đội ngũ quản lý Seller (Seller Management Team).
- **Secondary:** Đội ngũ Logistics, Đội ngũ Chăm sóc khách hàng (Customer Support).

## 7. Key Business Questions
1. **Delivery & Satisfaction:** Những đơn hàng bị giao trễ (delay > 0 ngày) có điểm review score trung bình thấp hơn bao nhiêu so với đơn hàng giao đúng hạn?
2. **Geographic Bottlenecks:** Bang (state) nào có tỷ lệ đơn hàng trễ (On-time Delivery Rate) thấp nhất, và điều này có tương quan với review score thấp của bang đó không?
3. **Seller Risk Matrix:** Những seller nào nằm trong nhóm "High Revenue - Low Satisfaction" (Doanh thu cao nhưng review thấp), cần được can thiệp ngay lập tức?
4. **Category Performance:** Nhóm sản phẩm (product category) nào có tỷ lệ hủy hàng (canceled/unavailable) hoặc tỷ lệ missing items cao bất thường?
5. **Customer Retention:** Trong số 96,096 khách hàng duy nhất, bao nhiêu phần trăm đã mua hàng từ 2 lần trở lên? Liệu trải nghiệm giao hàng ở đơn đầu tiên có ảnh hưởng đến việc họ quay lại không?

## 8. Scope
- **In Scope:** Phân tích dữ liệu từ `olist_orders_dataset`, `olist_order_items_dataset`, `olist_order_reviews_dataset`, `olist_customers_dataset`, `olist_sellers_dataset`, `olist_products_dataset`, và `product_category_name_translation`.
- **Out of Scope:** Phân tích văn bản chi tiết (NLP) trên `review_comment_message` (do giới hạn công cụ và scope project), phân tích dữ liệu `olist_geolocation_dataset` ở cấp độ tọa độ (chỉ sử dụng ở cấp độ mapping zip_code nếu cần, tránh row multiplication).

## 9. Assumptions
- `order_status` = 'delivered' được coi là đơn hàng thành công. Các đơn hàng 'canceled' hoặc 'unavailable' sẽ được phân tích riêng như một chỉ số rủi ro, không tính vào doanh thu thực tế.
- `review_score` từ 1-5 là thước đo hợp lý và duy nhất cho "Customer Satisfaction" trong dataset này.
- Có 775 đơn hàng là Parent records không có Child items (tồn tại trong bảng `orders` nhưng không có chi tiết trong bảng `order_items`). Đây không phải là lỗi toàn vẹn tham chiếu (Referential Integrity) của database, mà chủ yếu là các đơn hàng bị hủy (`canceled`) hoặc không khả dụng (`unavailable`) trước khi hệ thống kịp tạo chi tiết sản phẩm. Các đơn hàng này sẽ được gắn cờ (flag) và loại trừ khỏi các metric tính toán doanh thu (Revenue/GMV)

## 10. Limitations
- **Historical Data:** Dữ liệu chỉ phản ánh giai đoạn từ 2016-2018. Các đề xuất có thể không còn hoàn toàn chính xác với thị trường hiện tại.
- **No Causality:** Phân tích chỉ chỉ ra mối tương quan (correlation) giữa delivery delay và review score, không chứng minh được quan hệ nhân quả (causation) tuyệt đối.
- **Missing Translations Strategy:** 2 danh mục sản phẩm (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) thiếu bản dịch tiếng Anh. **Chiến lược xử lý:** Ở Phase 4 (Data Cleaning), sẽ kiểm tra volume doanh thu của 2 category này. Nếu khối lượng đáng kể, sẽ dịch thủ công chuẩn xác thành "PC Gamer" và "Kitchen & Food Processors". Nếu không đáng kể (dưới 1%), sẽ gán nhãn "Others" để giảm nhiễu cho Dashboard.
- **Review Bias:** Chỉ những khách hàng chủ động để lại đánh giá mới được tính vào Review Score, có thể dẫn đến thiên lệch nếu nhóm khách hàng im lặng có trải nghiệm quá tệ hoặc quá tốt