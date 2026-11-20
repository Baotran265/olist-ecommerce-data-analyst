# QUAN HỆ DỮ LIỆU & KIỂM TOÁN TÍNH TOÀN VẸN (DATA RELATIONSHIPS & INTEGRITY CHECK)

> Kết quả kiểm tra tính toàn vẹn tham chiếu (Referential Integrity) giữa các bảng trong cơ sở dữ liệu.

## 1. Kiểm toán Toàn vẹn Tham chiếu (Referential Integrity Checks)

| Bảng con (Child Table) | Khóa ngoại (FK) | Bảng cha (Parent Table) | Khóa chính (PK) | Tổng số khóa con | Thiếu ở bảng cha | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| olist_order_items_dataset.csv | order_id | olist_orders_dataset.csv | order_id | 98,666 | 0 | ✅ HỢP LỆ (VALID) |
| olist_order_payments_dataset.csv | order_id | olist_orders_dataset.csv | order_id | 99,440 | 0 | ✅ HỢP LỆ (VALID) |
| olist_order_reviews_dataset.csv | order_id | olist_orders_dataset.csv | order_id | 98,673 | 0 | ✅ HỢP LỆ (VALID) |
| olist_orders_dataset.csv | customer_id | olist_customers_dataset.csv | customer_id | 99,441 | 0 | ✅ HỢP LỆ (VALID) |
| olist_order_items_dataset.csv | seller_id | olist_sellers_dataset.csv | seller_id | 3,095 | 0 | ✅ HỢP LỆ (VALID) |
| olist_order_items_dataset.csv | product_id | olist_products_dataset.csv | product_id | 32,951 | 0 | ✅ HỢP LỆ (VALID) |
| olist_products_dataset.csv | product_category_name | product_category_name_translation.csv | product_category_name | 73 | 2 | ⚠️ THIẾU BẢN DỊCH (Xử lý bổ sung ở Phase 4) |

## 2. Cảnh báo Nghiệp vụ về Grain & Rủi ro Nhân dòng (Critical Grain Warnings)

1. **Bảng Địa lý (Geolocation):** Bảng `olist_geolocation_dataset` có grain là **1 dòng = 1 điểm tọa độ**. Một `geolocation_zip_code_prefix` có thể xuất hiện **nhiều lần** (nhiều cặp lat/lng khác nhau cho cùng một mã zip code). 
   - **Rủi ro:** Nếu liên kết trực tiếp bảng này với `customers` hoặc `sellers` qua zip code mà không khử trùng lặp, sẽ gây ra **LỖI NHÂN DÒNG (Row Multiplication)** làm sai lệch hoàn toàn số liệu doanh thu và sản lượng.
   - **Giải pháp:** Gom nhóm (aggregate) bảng Geolocation theo từng zip code duy nhất với giá trị tọa độ trung vị (median) ở Phase 4 trước khi tích hợp vào Dimension tables.

2. **Các bảng chi tiết (Order Items / Payments / Reviews):** Các bảng này có grain chi tiết hơn bảng `orders` (1 đơn hàng có thể chứa nhiều sản phẩm, nhiều kỳ thanh toán hoặc không có đánh giá).
   - **Rủi ro:** Thực hiện phép kết nối (JOIN) ngang giữa 3 bảng này sẽ dẫn đến tích đề-các (Cross Join) gây nhân dòng nghiêm trọng.
   - **Giải pháp:** Luôn tổng hợp dữ liệu về đúng grain trước khi liên kết, hoặc phân tách thành Fact Table (Items) và Dimension Tables trong mô hình Kimball Star Schema.
