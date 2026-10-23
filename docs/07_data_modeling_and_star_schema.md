# DATA MODELING & STAR SCHEMA SPECIFICATION

> **Dự án:** Olist Brazilian E-Commerce Analytics  
> **Kiến trúc:** Dimensional Modeling (Star Schema - Kimball Methodology)  
> **Tệp mô hình vật lý:** `data/processed/star_schema/`  
> **Cơ sở dữ liệu:** `data/olist_star_schema.db` (SQLite) / `sql/01_create_star_schema.sql` (PostgreSQL/DuckDB/SQLite DDL)  

---

## 🏛️ 1. Kiến trúc Mô hình Dữ liệu (Dimensional Modeling)

Trong môi trường phân tích dữ liệu hiện đại (Modern Analytics Stack) và Business Intelligence (Power BI / Tableau / Metabase), việc thiết kế mô hình dữ liệu đóng vai trò quyết định tới **tính chính xác của phép tính (Measure Correctness)** và **tốc độ phản hồi của Dashboard (Query Performance)**.

### So sánh các phương án thiết kế dữ liệu:

| Tiêu chí | 3NF (Chuẩn hóa giao dịch) | Flat Table (1 Bảng dẹt duy nhất) | **Star Schema (Kimball Methodology - LỰA CHỌN)** |
| :--- | :--- | :--- | :--- |
| **Mục đích thiết kế** | Tối ưu ghi (OLTP), tránh trùng lặp dữ liệu khi insert/update | Nhanh, tiện lợi cho phân tích sơ bộ một lần | **Tối ưu đọc & phân tích (OLAP/BI), chuẩn mực ngành** |
| **Số lượng bảng** | 9 bảng liên kết phức tạp (Snowflake) | 1 bảng duy nhất 34 cột | **1 Fact Table + 4 Dimension Tables** |
| **Rủi ro nhân dòng** | Rất cao khi join qua lại các bảng 1-N | Đã denormalize nhưng nặng bộ nhớ khi lọc | **Triệt tiêu hoàn toàn (Grain được phân tách rõ ràng)** |
| **Hiệu năng Power BI** | Chậm (Nhiều quan hệ bắc cầu, quan hệ 2 chiều) | Tốn RAM, khó viết DAX Time Intelligence | **Tối ưu tuyệt đối với VertiPaq Engine, DAX đơn giản** |

---

## 📊 2. Sơ đồ Thực thể Liên kết (Entity Relationship Diagram - ERD)

```mermaid
erDiagram
    dim_date ||--o{ fact_order_items : "order_date_key"
    dim_customers ||--o{ fact_order_items : "customer_id"
    dim_sellers ||--o{ fact_order_items : "seller_id"
    dim_products ||--o{ fact_order_items : "product_id"

    dim_date {
        int date_key PK
        date date
        int year
        string quarter
        string year_quarter
        int month
        string month_name
        string year_month
        int day_of_month
        int day_of_week
        string day_name
        int is_weekend
    }

    dim_customers {
        string customer_id PK
        string customer_unique_id
        int customer_zip_code_prefix
        string customer_city
        string customer_state
        float geolocation_lat
        float geolocation_lng
    }

    dim_sellers {
        string seller_id PK
        int seller_zip_code_prefix
        string seller_city
        string seller_state
        float geolocation_lat
        float geolocation_lng
    }

    dim_products {
        string product_id PK
        string product_category_formatted
        string product_category_name_english
        float product_weight_g
        float product_length_cm
        float product_height_cm
        float product_width_cm
        float product_photos_qty
    }

    fact_order_items {
        string order_id PK
        int order_item_id PK
        string customer_id FK
        string seller_id FK
        string product_id FK
        int order_date_key FK
        string order_purchase_timestamp
        string order_status
        decimal price
        decimal freight_value
        decimal item_total_value
        float actual_delivery_days
        float estimated_delivery_days
        float delivery_delay_days
        int is_delayed
        int is_valid_delivered
        string delay_bucket
        float seller_dispatch_days
        float carrier_delivery_days
        float review_score
        string satisfaction_tier
        int has_comment
        int is_interstate
    }
```

---

## 🔍 3. Đặc tả Chi tiết các Bảng trong Star Schema

### 3.1. Bảng Fact: `fact_order_items`
* **Grain:** **1 dòng = 1 sản phẩm (item) trong 1 đơn hàng.**
* **Số dòng:** 112,650 dòng, 23 cột.
* **Khóa chính ghép (Composite Primary Key):** `(order_id, order_item_id)`.
* **Khóa ngoại (Foreign Keys):**
  - `customer_id` -> `dim_customers.customer_id`
  - `seller_id` -> `dim_sellers.seller_id`
  - `product_id` -> `dim_products.product_id`
  - `order_date_key` -> `dim_date.date_key`
* **Metrics & Chỉ số vận hành:**
  - `price`, `freight_value`, `item_total_value` (Doanh thu & cước phí).
  - `actual_delivery_days`, `delivery_delay_days`, `is_delayed` (Chỉ số thời gian giao hàng).
  - `review_score`, `satisfaction_tier` (Chỉ số điểm hài lòng).
  - `is_interstate` (Cờ giao hàng liên bang).

### 3.2. Bảng Chiều: `dim_customers`
* **Grain:** 1 dòng = 1 tài khoản mua hàng (`customer_id`).
* **Số dòng:** 99,441 dòng.
* **Tọa độ địa lý:** Tích hợp tọa độ địa lý `geolocation_lat` và `geolocation_lng` (trung vị) từ bảng Geolocation sạch. *(Lưu ý: có 279 dòng mang giá trị NULL do tiền tố zip code không tồn tại trong danh mục bưu chính sau khi lọc ngoại lai).*

### 3.3. Bảng Chiều: `dim_sellers`
* **Grain:** 1 dòng = 1 người bán (`seller_id`).
* **Số dòng:** 3,095 dòng.
* **Tọa độ địa lý:** Tích hợp tọa độ người bán *(có 7 dòng NULL do thiếu mã zip code trong bảng geo)*.

### 3.4. Bảng Chiều: `dim_products`
* **Grain:** 1 dòng = 1 sản phẩm duy nhất (`product_id`).
* **Số dòng:** 32,951 dòng.
* **Tên danh mục:** Tên danh mục tiếng Anh chuẩn hóa (`product_category_formatted`), đã bổ sung đầy đủ bản dịch cho các category thiếu và xử lý chính tả.

### 3.5. Bảng Chiều: `dim_date`
* **Grain:** 1 dòng = 1 ngày theo lịch (Calendar Day) từ `2016-01-01` đến `2018-12-31`.
* **Số dòng:** 1,096 ngày.
* **Khóa ngày:** `date_key` dạng số nguyên `YYYYMMDD` (ví dụ: `20170115`), kèm cột `year_quarter` (`2017-Q1`).

### 3.6. ⚠️ Lưu ý về Grain Mismatch: `review_score` & `satisfaction_tier`

> **Vấn đề:** Bảng `fact_order_items` có grain là **1 dòng = 1 sản phẩm (item)** trong đơn hàng. Tuy nhiên, `review_score` và `satisfaction_tier` là thông tin **ở cấp độ Đơn hàng (Order-level)**, vì trong dataset gốc Olist, mỗi đơn hàng (`order_id`) chỉ có **1 lượt đánh giá duy nhất** từ khách hàng, bất kể đơn đó chứa bao nhiêu sản phẩm.

**Hệ quả:** Nếu một đơn hàng có 3 items và review_score = 5, thì cả 3 dòng trong `fact_order_items` đều mang giá trị `review_score = 5`. Khi tính `AVERAGE(review_score)` trực tiếp trên bảng Fact, đơn hàng này sẽ được tính 3 lần thay vì 1 lần → **Kết quả bị thiên lệch (bias) về phía các đơn hàng có nhiều items.**

**Giải pháp trong DAX (Power BI):**

```dax
-- SAI: Tính trung bình trên toàn bộ dòng fact (bị nhân dòng)
Avg Review Score (WRONG) = AVERAGE(fact_order_items[review_score])

-- ĐÚNG: Deduplicate về cấp order trước khi tính trung bình (đồng thời lọc đơn giao thành công hợp lệ)
Avg Review Score Delivered = 
AVERAGEX(
    FILTER(
        SUMMARIZE(
            fact_order_items, 
            fact_order_items[order_id], 
            fact_order_items[order_status],
            fact_order_items[is_valid_delivered],
            fact_order_items[review_score]
        ),
        fact_order_items[order_status] = "delivered" && 
        fact_order_items[is_valid_delivered] = 1 &&
        NOT(ISBLANK(fact_order_items[review_score]))
    ),
    fact_order_items[review_score]
)
```

**Giải pháp trong SQL:**

```sql
-- Deduplicate về order-level trước khi tính average
SELECT AVG(review_score)
FROM (
    SELECT order_id, review_score
    FROM fact_order_items
    WHERE order_status = 'delivered' AND is_valid_delivered = 1 AND review_score IS NOT NULL
    GROUP BY order_id, review_score
) AS order_level;
```

> **⚠️ Lưu ý mở rộng cho Power BI DAX:** Quy tắc deduplicate này áp dụng cho tất cả các trường order-level khác đang nằm trong fact table: `actual_delivery_days`, `estimated_delivery_days`, `delivery_delay_days`. Toàn bộ các DAX Measures tính trung bình cho các trường này đều sử dụng cấu trúc Grain-Safe `AVERAGEX(SUMMARIZE(...))`. Xem chi tiết trong [powerbi/dax_measures_and_model_guide.md](../powerbi/dax_measures_and_model_guide.md) — Nhóm 2 (Measures #13–15) và Nhóm 3 (Measure #16).

---

## ⚡ 4. Tối ưu Hóa Hiệu Năng Truy Vấn (Performance & Indexing)

Trong cơ sở dữ liệu `data/olist_star_schema.db`, toàn bộ 7 Performance Indexes đã được khởi tạo:

```sql
CREATE INDEX idx_fact_order ON fact_order_items(order_id);
CREATE INDEX idx_fact_cust ON fact_order_items(customer_id);
CREATE INDEX idx_fact_seller ON fact_order_items(seller_id);
CREATE INDEX idx_fact_prod ON fact_order_items(product_id);
CREATE INDEX idx_fact_date ON fact_order_items(order_date_key);
CREATE INDEX idx_fact_status ON fact_order_items(order_status);
CREATE INDEX idx_fact_delayed ON fact_order_items(is_delayed);
```

Nhờ cấu trúc chỉ mục B-Tree này, 5 câu truy vấn phân tích nghiệp vụ trong [sql/02_kpi_business_queries.sql](../sql/02_kpi_business_queries.sql) (bao gồm CTE, Window Functions, Partition By) đều thực thi nhanh chóng (khoảng 100 – 600 ms trên SQLite tùy cấu hình phần cứng).

---
*Tài liệu này được biên soạn cho Phase 6 của dự án Olist Data Analyst Portfolio.*
