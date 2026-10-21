# DATA DICTIONARY

> File này được tự động sinh ra từ `src/01_data_understanding.py` dựa trên dữ liệu thực tế.

## Customers (`olist_customers_dataset.csv`)

- **Purpose:** Lưu trữ thông tin định danh và địa chỉ của khách hàng.
- **Business Meaning / Grain:** Mỗi dòng là một customer_id duy nhất. Lưu ý: một người (unique_id) có thể có nhiều customer_id nếu dùng nhiều tài khoản/địa chỉ.
- **Total Rows:** 99,441
- **Total Columns:** 5
- **Primary Key Candidate(s):** customer_id

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| customer_id | str | 0 | 0.00% |
| customer_unique_id | str | 0 | 0.00% |
| customer_zip_code_prefix | int64 | 0 | 0.00% |
| customer_city | str | 0 | 0.00% |
| customer_state | str | 0 | 0.00% |

---

## Geolocation (`olist_geolocation_dataset.csv`)

- **Purpose:** Ánh xạ zip code prefix với tọa độ địa lý (lat/lng) và thành phố.
- **Business Meaning / Grain:** Grain: KHÔNG PHẢI 1 zip code = 1 dòng. Một zip code có thể có nhiều điểm tọa độ (nhiều dòng). Bảng này rất nặng và dễ gây nhân dòng khi join.
- **Total Rows:** 1,000,163
- **Total Columns:** 5
- **Primary Key Candidate(s):** None (Composite key or no unique ID)

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| geolocation_zip_code_prefix | int64 | 0 | 0.00% |
| geolocation_lat | float64 | 0 | 0.00% |
| geolocation_lng | float64 | 0 | 0.00% |
| geolocation_city | str | 0 | 0.00% |
| geolocation_state | str | 0 | 0.00% |

---

## Orders (`olist_orders_dataset.csv`)

- **Purpose:** Lưu trữ thông tin chính của đơn hàng, trạng thái và các mốc thời gian.
- **Business Meaning / Grain:** Mỗi dòng đại diện cho một đơn hàng (order) được đặt trên platform.
- **Total Rows:** 99,441
- **Total Columns:** 8
- **Primary Key Candidate(s):** order_id, customer_id

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| order_id | str | 0 | 0.00% |
| customer_id | str | 0 | 0.00% |
| order_status | str | 0 | 0.00% |
| order_purchase_timestamp | str | 0 | 0.00% |
| order_approved_at | str | 160 | 0.16% |
| order_delivered_carrier_date | str | 1,783 | 1.79% |
| order_delivered_customer_date | str | 2,965 | 2.98% |
| order_estimated_delivery_date | str | 0 | 0.00% |

---

## Order Items (`olist_order_items_dataset.csv`)

- **Purpose:** Lưu trữ chi tiết từng sản phẩm trong đơn hàng, giá bán và phí vận chuyển.
- **Business Meaning / Grain:** Grain: 1 dòng = 1 sản phẩm (item) trong 1 đơn hàng. Một order có thể có nhiều dòng.
- **Total Rows:** 112,650
- **Total Columns:** 7
- **Primary Key Candidate(s):** None (Composite key or no unique ID)

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| order_id | str | 0 | 0.00% |
| order_item_id | int64 | 0 | 0.00% |
| product_id | str | 0 | 0.00% |
| seller_id | str | 0 | 0.00% |
| shipping_limit_date | str | 0 | 0.00% |
| price | float64 | 0 | 0.00% |
| freight_value | float64 | 0 | 0.00% |

---

## Order Payments (`olist_order_payments_dataset.csv`)

- **Purpose:** Lưu trữ thông tin thanh toán của đơn hàng.
- **Business Meaning / Grain:** Grain: 1 dòng = 1 phương thức thanh toán cho 1 đơn hàng. Một order có thể trả nhiều lần (installments) hoặc dùng nhiều phương thức.
- **Total Rows:** 103,886
- **Total Columns:** 5
- **Primary Key Candidate(s):** None (Composite key or no unique ID)

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| order_id | str | 0 | 0.00% |
| payment_sequential | int64 | 0 | 0.00% |
| payment_type | str | 0 | 0.00% |
| payment_installments | int64 | 0 | 0.00% |
| payment_value | float64 | 0 | 0.00% |

---

## Order Reviews (`olist_order_reviews_dataset.csv`)

- **Purpose:** Lưu trữ đánh giá và phản hồi của khách hàng sau khi nhận hàng.
- **Business Meaning / Grain:** Grain: 1 dòng = 1 đánh giá cho 1 đơn hàng. Không phải order nào cũng có review.
- **Total Rows:** 99,224
- **Total Columns:** 7
- **Primary Key Candidate(s):** None (Composite key or no unique ID)

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| review_id | str | 0 | 0.00% |
| order_id | str | 0 | 0.00% |
| review_score | int64 | 0 | 0.00% |
| review_comment_title | str | 87,656 | 88.34% |
| review_comment_message | str | 58,247 | 58.70% |
| review_creation_date | str | 0 | 0.00% |
| review_answer_timestamp | str | 0 | 0.00% |

---

## Products (`olist_products_dataset.csv`)

- **Purpose:** Lưu trữ thông tin chi tiết về sản phẩm (kích thước, trọng lượng, category).
- **Business Meaning / Grain:** Mỗi dòng là một product_id duy nhất.
- **Total Rows:** 32,951
- **Total Columns:** 9
- **Primary Key Candidate(s):** product_id

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| product_id | str | 0 | 0.00% |
| product_category_name | str | 610 | 1.85% |
| product_name_lenght | float64 | 610 | 1.85% |
| product_description_lenght | float64 | 610 | 1.85% |
| product_photos_qty | float64 | 610 | 1.85% |
| product_weight_g | float64 | 2 | 0.01% |
| product_length_cm | float64 | 2 | 0.01% |
| product_height_cm | float64 | 2 | 0.01% |
| product_width_cm | float64 | 2 | 0.01% |

---

## Sellers (`olist_sellers_dataset.csv`)

- **Purpose:** Lưu trữ thông tin định danh và địa chỉ của người bán.
- **Business Meaning / Grain:** Mỗi dòng là một seller_id duy nhất.
- **Total Rows:** 3,095
- **Total Columns:** 4
- **Primary Key Candidate(s):** seller_id

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| seller_id | str | 0 | 0.00% |
| seller_zip_code_prefix | int64 | 0 | 0.00% |
| seller_city | str | 0 | 0.00% |
| seller_state | str | 0 | 0.00% |

---

## Product Category Translation (`product_category_name_translation.csv`)

- **Purpose:** Dịch tên category từ tiếng Bồ Đào Nha sang tiếng Anh.
- **Business Meaning / Grain:** Bảng mapping 1-1 giữa category gốc và category tiếng Anh.
- **Total Rows:** 71
- **Total Columns:** 2
- **Primary Key Candidate(s):** product_category_name, product_category_name_english

### Columns & Data Types

| Column Name | Data Type | Missing Values | % Missing |
| :--- | :--- | :--- | :--- |
| product_category_name | str | 0 | 0.00% |
| product_category_name_english | str | 0 | 0.00% |

---

