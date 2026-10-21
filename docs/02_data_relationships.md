# DATA RELATIONSHIPS & INTEGRITY CHECK

> Kết quả kiểm tra Referential Integrity giữa các bảng.

## Referential Integrity Checks

| Child Table (Source) | Foreign Key | Parent Table (Target) | Primary Key | Total Child Keys | Missing in Parent | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| olist_order_items_dataset.csv | order_id | olist_orders_dataset.csv | order_id | 98,666 | 0 | ✅ VALID |
| olist_order_payments_dataset.csv | order_id | olist_orders_dataset.csv | order_id | 99,440 | 0 | ✅ VALID |
| olist_order_reviews_dataset.csv | order_id | olist_orders_dataset.csv | order_id | 98,673 | 0 | ✅ VALID |
| olist_orders_dataset.csv | customer_id | olist_customers_dataset.csv | customer_id | 99,441 | 0 | ✅ VALID |
| olist_order_items_dataset.csv | seller_id | olist_sellers_dataset.csv | seller_id | 3,095 | 0 | ✅ VALID |
| olist_order_items_dataset.csv | product_id | olist_products_dataset.csv | product_id | 32,951 | 0 | ✅ VALID |
| olist_products_dataset.csv | product_category_name | product_category_name_translation.csv | product_category_name | 73 | 2 | ⚠️ ORPHAN RECORDS FOUND |

## Critical Grain Warnings

1. **Geolocation Table:** Bảng `olist_geolocation_dataset` có grain là **1 dòng = 1 điểm tọa độ**. Một `geolocation_zip_code_prefix` có thể xuất hiện **nhiều lần** (nhiều lat/lng khác nhau cho cùng 1 zip code). 
   - **Rủi ro:** Nếu join trực tiếp bảng này với `customers` hoặc `sellers` qua zip code, sẽ gây ra **ROW MULTIPLICATION** (nhân dòng) làm sai lệch hoàn toàn số liệu.
   - **Giải pháp:** Chỉ sử dụng bảng này để lấy thông tin city/state nếu cần, hoặc phải group by zip code trước khi join.

2. **Order Items / Payments / Reviews:** Các bảng này có grain nhỏ hơn bảng `orders` (1 order có nhiều items, nhiều payments, hoặc không có review).
   - **Rủi ro:** Join cả 3 bảng này lại với nhau sẽ gây ra **CROSS JOIN / ROW MULTIPLICATION** nghiêm trọng.
   - **Giải pháp:** Luôn aggregate (group by order_id) các bảng con này về grain của `orders` trước khi join, hoặc xây dựng Fact table riêng biệt.
