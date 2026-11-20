# POWER BI DATA MODEL & DAX MEASURES GUIDE

> **Dự án:** Olist Brazilian E-Commerce Analytics  
> **Thư mục dữ liệu kết nối:** `data/processed/star_schema/`  
> **Mục tiêu:** Hướng dẫn kết nối dữ liệu vào Power BI Desktop, thiết lập quan hệ Star Schema chuẩn 1-N (Single Direction), và cung cấp 24 công thức DAX Measures cốt lõi.

---

## 🏗️ 1. Hướng dẫn thiết lập Mô hình Star Schema trong Power BI

### Bước 1: Get Data
1. Mở **Power BI Desktop**.
2. Chọn **Get Data** -> **Text/CSV** (hoặc **Folder** trỏ vào `data/processed/star_schema/`).
3. Load 5 bảng:
   - `fact_order_items.csv`
   - `dim_customers.csv`
   - `dim_sellers.csv`
   - `dim_products.csv`
   - `dim_date.csv`

### Bước 2: Thiết lập Quan hệ (Model View)
Trong tab **Model View**, kéo thả tạo các mối quan hệ (Relationships) như sau:

| Bảng 1 (Dimension - 1) | Khóa (PK) | Bảng 2 (Fact - Many) | Khóa (FK) | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `dim_customers` | `customer_id` | `fact_order_items` | `customer_id` | 1 to Many (1:*) | **Single** |
| `dim_sellers` | `seller_id` | `fact_order_items` | `seller_id` | 1 to Many (1:*) | **Single** |
| `dim_products` | `product_id` | `fact_order_items` | `product_id` | 1 to Many (1:*) | **Single** |
| `dim_date` | `date_key` | `fact_order_items` | `order_date_key` | 1 to Many (1:*) | **Single** |

> ⚠️ **Quy tắc vàng trong Power BI:** Luôn để **Cross Filter Direction = Single** từ Dimension sang Fact để tối ưu hiệu năng VertiPaq Engine và tránh ambiguous filter context. Đánh dấu bảng `dim_date` là Date Table (Mark as Date Table).

---

## 📐 2. Bảng Công thức DAX Measures Cốt lõi (24 Core DAX Measures)

Tạo một bảng rỗng chuyên chứa Measure đặt tên là `_Measures` để quản lý chuyên nghiệp.

### Nhóm 1: Sales & Revenue Metrics (Doanh thu & Đơn hàng)

```dax
-- 1. Tổng số đơn hàng (Distinct Order Count)
--    KPI tổng quát dashboard, đếm tất cả đơn hàng bất kể trạng thái
Total Orders = 
DISTINCTCOUNT(fact_order_items[order_id])

-- 2. Số lượng sản phẩm bán ra (Items Sold)
--    KPI tổng quát dashboard
Total Items Sold = 
COUNTROWS(fact_order_items)

-- 3. Tổng Doanh thu sản phẩm (Revenue = SUM(price), tất cả trạng thái)
--    KPI tổng quát dashboard
Total Revenue = 
SUM(fact_order_items[price])

-- 4. Tổng Phí vận chuyển (Total Freight Cost)
--    KPI tổng quát dashboard
Total Freight = 
SUM(fact_order_items[freight_value])

-- 5. Tổng giá trị đơn hàng (Gross Order Value = price + freight)
--    KPI tổng quát dashboard
--    ⚠️ Chỉ đúng nếu item_total_value = price + freight_value trong data processing
Gross Order Value = 
SUM(fact_order_items[item_total_value])

-- 6. Tỷ trọng Phí ship trên Tổng giá trị đơn hàng (Freight / Gross Order Value)
--    KPI tổng quát dashboard, đồng nhất với SQL Q4 (freight_pct_of_gov)
Freight Ratio % of GOV = 
DIVIDE([Total Freight], [Gross Order Value], 0)

-- 7. Doanh thu chỉ tính đơn giao thành công hợp lệ (Delivered Revenue)
--    ⚠️ Dùng is_valid_delivery_delay để đồng bộ với Python EDA & SQL Q3 (Seller Risk)
--    Mẫu số: các đơn có thể xác định độ trễ (có ngày giao thực tế và ngày dự kiến)
Delivered Revenue = 
CALCULATE(
    SUM(fact_order_items[price]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivery_delay] = 1
)

-- 8. Giá trị đơn hàng trung bình (Average Order Value - AOV)
--    KPI tổng quát dashboard
AOV = 
DIVIDE([Gross Order Value], [Total Orders], 0)
```

---

### Nhóm 2: Delivery & Logistics Performance (Hiệu suất Vận chuyển)

```dax
-- 9. Số đơn hàng đã giao thành công hợp lệ (có ngày giao thực tế)
--    KPI tổng quát dashboard, dùng is_valid_delivered (đơn có ngày giao thực tế)
Delivered Orders = 
CALCULATE(
    DISTINCTCOUNT(fact_order_items[order_id]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivered] = 1
)

-- 9b. Số đơn hàng có dữ liệu độ trễ hợp lệ (Valid Delivery Orders)
--     ⚠️ Measure mới: Dùng làm mẫu số cho Delay Rate % và On-Time Delivery Rate %
--     Đồng bộ với Python EDA: chỉ tính các đơn có thể xác định độ trễ
Valid Delivery Orders = 
CALCULATE(
    DISTINCTCOUNT(fact_order_items[order_id]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivery_delay] = 1
)

-- 10. Số đơn hàng bị giao trễ hẹn (Delivered Late)
--     KPI tổng quát dashboard, dùng is_valid_delivered (đơn có ngày giao thực tế)
--     ⚠️ KHÔNG dùng measure này làm tử số của Delay Rate %
--     Delay Rate % dùng tử số riêng với filter is_valid_delivery_delay = 1 (xem Measure 11)
Delayed Orders = 
CALCULATE(
    [Delivered Orders],
    fact_order_items[is_delayed] = 1
)

-- 11. Tỷ lệ giao hàng trễ (% Delay Rate)
--     ⚠️ Dùng để tái tạo Q1, Q2 Python EDA
--     Mẫu số: Valid Delivery Orders (is_valid_delivery_delay = 1)
--     Tử số: Đếm trực tiếp DISTINCTCOUNT với filter is_delayed = 1
--     Đồng bộ với Python: delay_rate = delayed / valid_delay_orders
Delay Rate % = 
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(fact_order_items[order_id]),
        fact_order_items[order_status] = "delivered",
        fact_order_items[is_valid_delivery_delay] = 1,
        fact_order_items[is_delayed] = 1
    ),
    [Valid Delivery Orders]
)

-- 12. Tỷ lệ giao hàng đúng hạn (% On-Time Delivery Rate)
--     ⚠️ Dùng để tái tạo Q1, Q2 Python EDA
--     Mẫu số: Valid Delivery Orders (is_valid_delivery_delay = 1)
--     Tử số: Đếm trực tiếp DISTINCTCOUNT với filter is_delayed = 0
--     Không truyền tham số thứ 3 cho DIVIDE → trả về BLANK khi empty context
On-Time Delivery Rate % = 
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(fact_order_items[order_id]),
        fact_order_items[order_status] = "delivered",
        fact_order_items[is_valid_delivery_delay] = 1,
        fact_order_items[is_delayed] = 0
    ),
    [Valid Delivery Orders]
)

-- 13. Thời gian giao hàng thực tế trung bình (Grain-Safe, lọc đơn delivered hợp lệ)
--     KPI tổng quát dashboard, dùng is_valid_delivered
--     AVERAGEX(VALUES(order_id)) đảm bảo mỗi đơn đóng góp một lần
Avg Delivery Days = 
CALCULATE(
    AVERAGEX(
        VALUES(fact_order_items[order_id]),
        CALCULATE(AVERAGE(fact_order_items[actual_delivery_days]))
    ),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivered] = 1
)

-- 14. Thời gian giao hàng dự kiến trung bình (Grain-Safe)
--     KPI tổng quát dashboard, dùng is_valid_delivered
Avg Estimated Days = 
CALCULATE(
    AVERAGEX(
        VALUES(fact_order_items[order_id]),
        CALCULATE(AVERAGE(fact_order_items[estimated_delivery_days]))
    ),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivered] = 1
)

-- 15. Số ngày trễ trung bình đối với các đơn bị trễ (Grain-Safe)
--     Dùng để tái tạo Q1 Python EDA
--     Chỉ xét các đơn có dữ liệu độ trễ hợp lệ (is_valid_delivery_delay = 1) và thực sự bị trễ
Avg Days Delayed = 
CALCULATE(
    AVERAGEX(
        VALUES(fact_order_items[order_id]),
        CALCULATE(AVERAGE(fact_order_items[delivery_delay_days]))
    ),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivery_delay] = 1,
    fact_order_items[is_delayed] = 1
)
```

---

### Nhóm 3: Customer Satisfaction & Review Metrics (Đánh giá Khách hàng)

```dax
-- 16. Điểm đánh giá trung bình (Average Review Score - Delivered Orders, Grain-Safe)
--     ⚠️ Dùng để tái tạo Q1 Python EDA
--     Deduplicate về order-level vì review_score là order-grain
--     Dùng MAX(review_score) để lấy một giá trị đại diện sau khi xác minh tính nhất quán
--     Lọc cùng tập đơn hợp lệ với Python: is_valid_delivery_delay = 1
Avg Review Score = 
CALCULATE(
    AVERAGEX(
        VALUES(fact_order_items[order_id]),
        CALCULATE(MAX(fact_order_items[review_score]))
    ),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivery_delay] = 1
)

-- 17. Tổng số đơn giao thành công có đánh giá hợp lệ (Delivered Orders With Review)
--     ⚠️ Dùng để tái tạo Q1 Python EDA
--     Đếm trực tiếp DISTINCTCOUNT(order_id) thay vì gọi [Delivered Orders]
--     Lọc cùng tập đơn hợp lệ với Python: is_valid_delivery_delay = 1
Valid Reviews Count = 
CALCULATE(
    DISTINCTCOUNT(fact_order_items[order_id]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivery_delay] = 1,
    NOT(ISBLANK(fact_order_items[review_score]))
)

-- 18. Số đơn giao thành công nhận đánh giá 1 sao (1-Star Count)
--     ⚠️ Dùng để tái tạo Q1 Python EDA
--     Đếm trực tiếp DISTINCTCOUNT(order_id) thay vì gọi [Delivered Orders]
--     Lọc cùng tập đơn hợp lệ với Python: is_valid_delivery_delay = 1
1-Star Reviews = 
CALCULATE(
    DISTINCTCOUNT(fact_order_items[order_id]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivery_delay] = 1,
    fact_order_items[review_score] = 1
)

-- 19. Tỷ lệ đánh giá 1 sao (% 1-Star Ratio trên tập có đánh giá)
--     Dùng để tái tạo Q1 Python EDA
--     Mẫu số: Valid Reviews Count (đã dùng is_valid_delivery_delay = 1)
1-Star Rate % = 
DIVIDE([1-Star Reviews], [Valid Reviews Count], 0)
```

---

### Nhóm 4: Customer Retention & Risk Management (Giữ chân & Rủi ro)

```dax
-- 20. Số khách hàng duy nhất (Unique Customers)
--     KPI tổng quát dashboard
--     ⚠️ Đếm khách hàng có đơn trong ngữ cảnh lọc hiện tại (không phải tất cả khách hàng)
Total Unique Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_customers[customer_unique_id]),
    fact_order_items
)

-- 21. Trạng thái rủi ro của Seller (Seller Risk Tier)
--     ⚠️ Measure trả về TEXT, hoạt động trong context của seller_id (Table/Matrix Visual)
--     ⚠️ Dùng để tái tạo Q3 Python EDA & SQL Q3
--     Sử dụng [Delivered Revenue] và [Avg Review Score] (đã dùng is_valid_delivery_delay)
Seller Risk Flag = 
IF(
    [Delivered Revenue] >= 15000 && [Avg Review Score] < 3.8,
    "High Risk - Audit Required",
    IF(
        [Delivered Revenue] >= 15000 && [Avg Review Score] >= 4.2,
        "Star Seller",
        IF(
            [Delivered Revenue] >= 15000,
            "Standard High-Volume",
            "Standard"
        )
    )
)

-- 22. Số lượng Seller rủi ro cao (Dùng cho KPI Card tổng quát)
--     ⚠️ Dùng để tái tạo Q3 Python EDA & SQL Q3
--     Sử dụng [Delivered Revenue] (đã dùng is_valid_delivery_delay)
--     Sử dụng [Valid Delivery Orders] thay vì [Delivered Orders] để đồng bộ tập đơn
--     Điều kiện [Orders] >= 30 để tách 11 seller đủ mẫu (Intervene) khỏi 5 seller ít mẫu (Monitor)
High Risk Sellers Count (Intervene) = 
COUNTROWS(
    FILTER(
        ADDCOLUMNS(
            VALUES(fact_order_items[seller_id]),
            "Rev", [Delivered Revenue],
            "Review", [Avg Review Score],
            "Orders", [Valid Delivery Orders]
        ),
        [Rev] >= 15000 && [Review] < 3.8 && [Orders] >= 30
    )
)

-- 23. Tỷ lệ khách hàng mua lại hoàn tất (Repeat Purchase Rate - Delivered Orders Only)
--     ⚠️ Dùng để tái tạo Q5 Python EDA
--     Khách hàng có >= 2 đơn hàng giao thành công hợp lệ / Tổng khách hàng có đơn giao thành công hợp lệ
--     Lọc cùng tập đơn hợp lệ với Python: is_valid_delivery_delay = 1
Repeat Purchase Rate % = 
VAR CustomerOrderSummary = 
    ADDCOLUMNS(
        VALUES(dim_customers[customer_unique_id]),
        "CompletedOrders", 
        CALCULATE(
            DISTINCTCOUNT(fact_order_items[order_id]),
            fact_order_items[order_status] = "delivered",
            fact_order_items[is_valid_delivery_delay] = 1
        )
    )
VAR RepeatCustomers = 
    COUNTROWS(
        FILTER(CustomerOrderSummary, [CompletedOrders] > 1)
    )
VAR TotalCompletedCustomers = 
    COUNTROWS(
        FILTER(CustomerOrderSummary, [CompletedOrders] >= 1)
    )
RETURN
    DIVIDE(RepeatCustomers, TotalCompletedCustomers, 0)
```

---

## 📊 3. Phân loại Measure theo Mục đích Sử dụng

### KPI Tổng quát Dashboard (giữ nguyên `is_valid_delivered`)
Các measure này đo lường số đơn đã giao thành công hoặc thời gian giao thực tế, không nhất thiết phải đổi cờ:

| # | Measure | Mục đích |
| :---: | :--- | :--- |
| 1 | Total Orders | Đếm tất cả đơn hàng |
| 2 | Total Items Sold | Đếm số dòng sản phẩm |
| 3 | Total Revenue | Doanh thu tất cả trạng thái |
| 4 | Total Freight | Tổng phí vận chuyển |
| 5 | Gross Order Value | Tổng giá trị đơn hàng |
| 6 | Freight Ratio % of GOV | Tỷ trọng cước phí |
| 8 | AOV | Giá trị đơn hàng trung bình |
| 9 | Delivered Orders | Số đơn giao thành công (có ngày giao thực tế) |
| 10 | Delayed Orders | Số đơn trễ (phụ thuộc Delivered Orders) |
| 13 | Avg Delivery Days | Thời gian giao trung bình |
| 14 | Avg Estimated Days | Thời gian dự kiến trung bình |
| 20 | Total Unique Customers | Số khách hàng duy nhất |

### Measure tái tạo Q1-Q5 Python EDA (dùng `is_valid_delivery_delay`)
Các measure này cần dùng cùng bộ lọc hợp lệ như Python để đối chiếu kết quả:

| # | Measure | Câu hỏi | Lý do |
| :---: | :--- | :--- | :--- |
| 7 | Delivered Revenue | Q3 (Seller Risk) | Đồng bộ với Python & SQL Q3 |
| 9b | Valid Delivery Orders | Q1, Q2, Q3 | Mẫu số chung cho các tỷ lệ |
| 11 | Delay Rate % | Q1, Q2 | Mẫu số: đơn có thể xác định độ trễ |
| 12 | On-Time Delivery Rate % | Q1, Q2 | Mẫu số: đơn có thể xác định độ trễ |
| 15 | Avg Days Delayed | Q1 | Chỉ xét đơn có dữ liệu độ trễ hợp lệ và bị trễ |
| 16 | Avg Review Score | Q1 | Lọc cùng tập đơn hợp lệ với Python |
| 17 | Valid Reviews Count | Q1 | Lọc cùng tập đơn hợp lệ với Python |
| 18 | 1-Star Reviews | Q1 | Lọc cùng tập đơn hợp lệ với Python |
| 19 | 1-Star Rate % | Q1 | Mẫu số: đơn có đánh giá trong tập hợp lệ |
| 21 | Seller Risk Flag | Q3 | Dùng Delivered Revenue (đã dùng is_valid_delivery_delay) |
| 22 | High Risk Sellers Count | Q3 | Dùng Delivered Revenue + Valid Delivery Orders |
| 23 | Repeat Purchase Rate % | Q5 | Lọc cùng tập đơn hợp lệ với Python |

---

## 🖥️ 4. Thiết kế Cấu trúc Dashboard (3-Page Layout Recommendation)

### Trang 1: Executive Overview (Tổng quan Điều hành)
- **Hàng KPI Cards (Top):** Gross Order Value (R$ 15.42M) / Delivered Revenue (R$ 13.22M) | Delivered Orders (96.5K) | On-Time Delivery Rate (93.2%) | Avg Review Score (4.16 ★) | Repeat Purchase Rate (3.00%).
- **Biểu đồ 1 (Line & Clustered Bar):** Doanh thu & Tỷ lệ giao trễ theo từng tháng (Year-Month Trend).
- **Biểu đồ 2 (Bar Chart):** Review Score & Tỷ lệ 1★ theo 4 nhóm thời gian trễ (On-Time, 1-3d, 4-7d, >7d).
- **Slicers (Bộ lọc):** Năm/Tháng, Bang Khách hàng, Trạng thái đơn hàng (mặc định chọn `delivered`).

### Trang 2: Geographic Delivery Bottlenecks (Hiệu suất Vận chuyển theo Vùng)
- **Bản đồ trực quan (Brazil Choropleth Map):**
  - *Lưu ý cấu hình để tránh hiển thị nhầm bản đồ Mỹ:* Trong tab Data, chọn cột `customer_state` trong bảng `dim_customers`, vào tab **Column tools** -> đặt **Data category = State or Province**. Tạo một calculated column `Country = "Brazil"` và kéo vào ô Location cùng với State, hoặc sử dụng visual **Shape Map** với file TopoJSON các bang của Brazil (`brazil_geo.json`).
- **Biểu đồ so sánh:** Giao hàng nội bang (Intrastate: 7.9 ngày, 15.35 R$) vs Giao hàng liên bang (Interstate: 15.1 ngày, 26.94 R$).
- **Bảng phân tích (Matrix):** Bang | Số đơn | Thời gian giao TB | Tỷ lệ trễ | Review Score.

### Trang 3: Seller Performance & Category Matrix (Quản trị Đối tác & Ngành hàng)
- **Scatter Plot (Ma trận Rủi ro Seller):** Trục X = Doanh thu người bán `[Delivered Revenue]` (Log scale), Trục Y = Điểm đánh giá trung bình `[Avg Review Score]`, Bubble Size = Số đơn hàng.
- **Top Ngành hàng:** Trục danh mục `product_category_formatted` xếp hạng theo Doanh thu kèm theo đường cước phí `[Freight Ratio % of GOV]`.
- **Bảng chi tiết Seller cần can thiệp (Seller Action Table):** Kéo `dim_sellers[seller_id]`, `dim_sellers[seller_city]`, `dim_sellers[seller_state]`, `[Delivered Revenue]`, `[Avg Review Score]`, `[Delay Rate %]`, `[Seller Risk Flag]` vào bảng để hiển thị danh sách đối tác rủi ro.
  - *Lưu ý:* Measure `[Seller Risk Flag]` phân loại 16 seller candidate (doanh thu ≥ 15,000 R$ và review < 3.8 ★), trong đó 11 seller đủ mẫu (≥ 30 đơn) được ưu tiên can thiệp và 5 seller ít mẫu cần theo dõi riêng. Measure `[High Risk Sellers Count (Intervene)]` chỉ đếm 11 seller đủ mẫu.

---
*Tài liệu này được biên soạn cho Power BI Desktop kết nối trực tiếp với Olist Kimball Star Schema.*
