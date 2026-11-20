# BÁO CÁO KIỂM TOÁN CHẤT LƯỢNG DỮ LIỆU (DATA QUALITY REPORT)

> Báo cáo này ghi nhận và đánh giá mức độ ảnh hưởng của các vấn đề chất lượng dữ liệu phát hiện trong Phase 3 (`src/02_data_quality_assessment.py`). Quy trình tuân thủ nguyên tắc: PHÁT HIỆN (Detect) + ĐÁNH GIÁ (Assess) + LƯU HỒ SƠ (Document).

| Tên bảng | Tên cột | Vấn đề chất lượng phát hiện | Số dòng ảnh hưởng | Tỷ lệ (%) | Mức độ nghiêm trọng | Phương án xử lý đề xuất | Căn cứ nghiệp vụ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| olist_geolocation_dataset.csv | Toàn bộ các cột | Dòng trùng lặp 100% | 261,831 | 26.18% | Cao (High) | Lọc bỏ trùng lặp ở Phase 4 | Tránh nhân dòng khi liên kết dữ liệu địa lý |
| olist_orders_dataset.csv | order_approved_at | Khuyết dữ liệu (Missing) | 160 | 0.16% | Trung bình | Giữ NaT, kiểm soát qua cờ hợp lệ ở Phase 4 | Dữ liệu khuyết có thể làm méo mó phép gom nhóm |
| olist_orders_dataset.csv | order_delivered_carrier_date | Khuyết dữ liệu (Missing) | 1,783 | 1.79% | Trung bình | Giữ NaT, kiểm soát qua cờ hợp lệ ở Phase 4 | Cần thiết để tính thời gian bàn giao của seller |
| olist_orders_dataset.csv | order_delivered_customer_date | Khuyết dữ liệu (Missing) | 2,965 | 2.98% | Trung bình | Lọc đơn chưa giao ở phân tích SLA | Không thể tính thời gian giao cho đơn chưa hoàn tất |
| olist_order_payments_dataset.csv | payment_value | Giá trị thanh toán bằng 0 | 9 | 0.0087% | Thấp | Điều tra đơn giảm giá / đơn thử nghiệm | Đơn giá trị 0 ảnh hưởng đến tính toán AOV |
| olist_order_reviews_dataset.csv | review_comment_title | Khuyết dữ liệu (Missing) | 87,656 | 88.34% | Cao (High) | Giữ nguyên, phân tích flag has_comment | Khách hàng thường chỉ chấm sao mà không viết tiêu đề |
| olist_products_dataset.csv | product_category_name | Khuyết dữ liệu (Missing) | 610 | 1.85% | Trung bình | Điền nhãn 'Unknown' ở Phase 4 | Tránh mất dòng sản phẩm khi phân tích |
| olist_products_dataset.csv | product_name_lenght | Khuyết dữ liệu (Missing) | 610 | 1.85% | Thấp | Điền giá trị trung vị (median) | Bổ trợ thuộc tính sản phẩm |
| olist_products_dataset.csv | product_description_lenght | Khuyết dữ liệu (Missing) | 610 | 1.85% | Thấp | Điền giá trị trung vị (median) | Bổ trợ thuộc tính sản phẩm |
| olist_products_dataset.csv | product_photos_qty | Khuyết dữ liệu (Missing) | 610 | 1.85% | Thấp | Điền giá trị 0 | Sản phẩm không có ảnh hiển thị |
| olist_products_dataset.csv | product_weight_g | Khuyết dữ liệu (Missing) | 2 | 0.01% | Thấp | Điền giá trị trung vị (median) | Cần thiết để tính toán logistics |
| olist_products_dataset.csv | product_length_cm | Khuyết dữ liệu (Missing) | 2 | 0.01% | Thấp | Điền giá trị trung vị (median) | Cần thiết để tính toán logistics |
| olist_products_dataset.csv | product_height_cm | Khuyết dữ liệu (Missing) | 2 | 0.01% | Thấp | Điền giá trị trung vị (median) | Cần thiết để tính toán logistics |
| olist_products_dataset.csv | product_width_cm | Khuyết dữ liệu (Missing) | 2 | 0.01% | Thấp | Điền giá trị trung vị (median) | Cần thiết để tính toán logistics |
| olist_orders_dataset.csv | delivery_days | Ngoại lai thời gian giao (> 90 ngày) | 76 | 0.08% | Trung bình | Giữ nguyên và dùng trung vị/phân đoạn | Phản ánh các sự cố giao hàng thực tế |
| olist_orders_dataset.csv | order_id | Đơn hàng không có sản phẩm (775 đơn) | 775 | 0.78% | Cao (High) | Loại trừ khỏi phân tích doanh thu sản phẩm | Đơn bị hủy trước khi tạo item record |
| olist_products_dataset.csv | product_category_name | Thiếu bản dịch tiếng Anh (2 / 73 danh mục) | 2 | 2.74% (trên danh mục) | Trung bình | Bổ sung dịch thủ công ở Phase 4 | Đảm bảo Dashboard hiển thị chuẩn tiếng Anh |
