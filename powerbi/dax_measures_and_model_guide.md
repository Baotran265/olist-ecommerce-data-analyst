# POWER BI DATA MODEL & DAX MEASURES GUIDE

> **Dự án:** Olist Brazilian E-Commerce Analytics  
> **Thư mục dữ liệu kết nối:** `data/processed/star_schema/`  
> **Mục tiêu:** Hướng dẫn kết nối dữ liệu vào Power BI Desktop, thiết lập quan hệ Star Schema chuẩn 1-N (Single Direction), và cung cấp 22 công thức DAX Measures cốt lõi.

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

## 📐 2. Bảng Công thức DAX Measures Cốt lõi (Core DAX Measures)

Tạo một bảng rỗng chuyên chứa Measure đặt tên là `_Measures` để quản lý chuyên nghiệp.

### Nhóm 1: Sales & Revenue Metrics (Doanh thu & Đơn hàng)

```dax
-- 1. Tổng số đơn hàng (Distinct Order Count)
Total Orders = 
DISTINCTCOUNT(fact_order_items[order_id])

-- 2. Số lượng sản phẩm bán ra (Items Sold)
Total Items Sold = 
COUNTROWS(fact_order_items)

-- 3. Tổng Doanh thu sản phẩm (Revenue = SUM(price), tất cả trạng thái)
Total Revenue = 
SUM(fact_order_items[price])

-- 4. Tổng Phí vận chuyển (Total Freight Cost)
Total Freight = 
SUM(fact_order_items[freight_value])

-- 5. Tổng giá trị đơn hàng (Gross Order Value = price + freight)
Gross Order Value = 
SUM(fact_order_items[item_total_value])

-- 6. Tỷ trọng Phí ship trên Tổng giá trị đơn hàng (Freight / Gross Order Value)
--    ⚠️ Tên measure phải đồng nhất với SQL Q4 (freight_pct_of_gov).
--    Revenue = SUM(price), GOV = price + freight. Freight Ratio = freight / GOV.
Freight Ratio % of GOV = 
DIVIDE([Total Freight], [Gross Order Value], 0)

-- 7. Doanh thu chỉ tính đơn giao thành công hợp lệ (Delivered Revenue)
--    ⚠️ Dùng cho các measure Seller Risk (#20, #21) để đồng nhất với Python & SQL
Delivered Revenue = 
CALCULATE(
    SUM(fact_order_items[price]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivered] = 1
)

-- 8. Giá trị đơn hàng trung bình (Average Order Value - AOV)
AOV = 
DIVIDE([Gross Order Value], [Total Orders], 0)
```

---

### Nhóm 2: Delivery & Logistics Performance (Hiệu suất Vận chuyển)

```dax
-- 9. Số đơn hàng đã giao thành công hợp lệ (có ngày giao thực tế)
Delivered Orders = 
CALCULATE(
    DISTINCTCOUNT(fact_order_items[order_id]),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivered] = 1
)

-- 10. Số đơn hàng bị giao trễ hẹn (Delivered Late)
Delayed Orders = 
CALCULATE(
    [Delivered Orders],
    fact_order_items[is_delayed] = 1
)

-- 11. Tỷ lệ giao hàng trễ (% Delay Rate)
Delay Rate % = 
DIVIDE([Delayed Orders], [Delivered Orders])

-- 12. Tỷ lệ giao hàng đúng hạn (% On-Time Delivery Rate)
--     ⚠️ Không truyền tham số thứ 3 cho DIVIDE → trả về BLANK khi empty context
--     (thay vì hiện "1" trên visual khi không có dữ liệu)
On-Time Delivery Rate % = 
DIVIDE([Delivered Orders] - [Delayed Orders], [Delivered Orders])

-- 13. Thời gian giao hàng thực tế trung bình (Grain-Safe)
--     ⚠️ Delivery days là order-level → phải deduplicate về order_id
Avg Delivery Days = 
AVERAGEX(
    VALUES(fact_order_items[order_id]),
    CALCULATE(AVERAGE(fact_order_items[actual_delivery_days]))
)

-- 14. Thời gian giao hàng dự kiến trung bình (Grain-Safe)
Avg Estimated Days = 
AVERAGEX(
    VALUES(fact_order_items[order_id]),
    CALCULATE(AVERAGE(fact_order_items[estimated_delivery_days]))
)

-- 15. Số ngày trễ trung bình đối với các đơn bị trễ (Grain-Safe)
Avg Days Delayed = 
CALCULATE(
    AVERAGEX(
        VALUES(fact_order_items[order_id]),
        CALCULATE(AVERAGE(fact_order_items[delivery_delay_days]))
    ),
    fact_order_items[is_delayed] = 1
)
```

---

### Nhóm 3: Customer Satisfaction & Review Metrics (Đánh giá Khách hàng)

```dax
-- 16. Điểm đánh giá trung bình (Average Review Score - Delivered Orders, Grain-Safe)
--     ⚠️ Phải deduplicate về order-level vì review_score là order-grain.
--     Đồng thời lọc đơn giao thành công hợp lệ để đồng bộ với Python & Benchmark.
Avg Review Score = 
CALCULATE(
    AVERAGEX(
        SUMMARIZE(fact_order_items, fact_order_items[order_id], fact_order_items[review_score]),
        fact_order_items[review_score]
    ),
    fact_order_items[order_status] = "delivered",
    fact_order_items[is_valid_delivered] = 1
)

-- 17. Tổng số đơn có đánh giá hợp lệ (Valid Reviews Count)
Valid Reviews Count = 
CALCULATE(
    [Delivered Orders],
    NOT(ISBLANK(fact_order_items[review_score]))
)

-- 18. Số lượt đánh giá 1 sao (1-Star Count)
1-Star Reviews = 
CALCULATE(
    [Delivered Orders],
    fact_order_items[review_score] = 1
)

-- 19. Tỷ lệ đánh giá 1 sao (% 1-Star Ratio trên tập có đánh giá)
1-Star Rate % = 
DIVIDE([1-Star Reviews], [Valid Reviews Count], 0)
```

---

### Nhóm 4: Customer Retention & Risk Management (Giữ chân & Rủi ro)

```dax
-- 20. Số khách hàng duy nhất (Unique Customers)
--     ⚠️ Sử dụng CALCULATE + DISTINCTCOUNT trên fact table để phản ứng
--     đúng khi slicer lọc theo ngành hàng, tháng, hoặc trạng thái đơn.
--     Nếu dùng trực tiếp DISTINCTCOUNT(dim_customers[customer_unique_id]),
--     kết quả luôn là tổng 96,096 khách bất kể slicer nào.
Total Unique Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_customers[customer_unique_id]),
    fact_order_items
)

-- 21. Trạng thái rủi ro của Seller (Seller Risk Tier)
--     ⚠️ Measure này trả về TEXT, chỉ hoạt động đúng khi có context của seller_id
--     Dùng trong Table/Matrix Visual (không dùng trong Card tổng quát)
--     ⚠️ Sử dụng [Delivered Revenue] để đồng nhất với Python & SQL Q3
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
--     ⚠️ Sử dụng [Delivered Revenue] thay vì [Total Revenue] để đồng bộ 100%
--     với Python & SQL (ra đúng 16 sellers)
High Risk Sellers Count = 
COUNTROWS(
    FILTER(
        ADDCOLUMNS(
            VALUES(fact_order_items[seller_id]),
            "Rev", CALCULATE(
                SUM(fact_order_items[price]),
                fact_order_items[order_status] = "delivered",
                fact_order_items[is_valid_delivered] = 1
            ),
            "Review", [Avg Review Score]
        ),
        [Rev] >= 15000 && [Review] < 3.8
    )
)

-- 23. Tỷ lệ khách hàng mua lại hoàn tất (Repeat Purchase Rate - Delivered Orders Only)
--     Khách hàng có >= 2 đơn hàng giao thành công / Tổng khách hàng có đơn giao thành công
--     Lưu ý kỹ thuật DAX: Sử dụng cấu trúc tường minh để không phụ thuộc vào hướng quan hệ 2 chiều (Bidirectional)
Repeat Purchase Rate % = 
VAR CustomerOrderSummary = 
    ADDCOLUMNS(
        VALUES(dim_customers[customer_unique_id]),
        "CompletedOrders", 
        CALCULATE(
            DISTINCTCOUNT(fact_order_items[order_id]),
            fact_order_items[order_status] = "delivered"
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

## 🖥️ 3. Thiết kế Cấu trúc Dashboard (3-Page Layout Recommendation)

### Trang 1: Executive Overview (Tổng quan Điều hành)
- **Hàng KPI Cards (Top):** Total Revenue | Total Orders | On-Time Delivery Rate (%) | Avg Review Score | Repeat Customer Rate (%).
- **Biểu đồ 1 (Line & Clustered Bar):** Doanh thu & Tỷ lệ giao trễ theo từng tháng (Year-Month Trend).
- **Biểu đồ 2 (Bar Chart):** Review Score & Tỷ lệ 1★ theo từng nhóm thời gian trễ (Delay Buckets: On-Time, 1-3d, 4-7d, >7d).
- **Slicers (Bộ lọc):** Năm/Tháng, Bang Khách hàng, Trạng thái đơn hàng.

### Trang 2: Logistics & Geographic Drill-down (Hiệu suất Vận chuyển theo Vùng)
- **Bản đồ trực quan (Shape Map / Filled Map):** Tỷ lệ giao hàng trễ theo từng bang của Brazil (Tô màu đậm các bang Đông Bắc: AL, MA, PI, CE).
- **Biểu đồ so sánh:** Giao hàng nội bang (Intrastate) vs Giao hàng liên bang (Interstate) về thời gian và chi phí cước ship.
- **Bảng phân tích (Matrix):** Bang | Số đơn | Thời gian giao TB | Tỷ lệ trễ | Review Score.

### Trang 3: Seller Management & Product Category Matrix (Quản lý Đối tác & Ngành hàng)
- **Scatter Plot (Ma trận Rủi ro Seller):** Trục X = Doanh thu (Log), Trục Y = Review Score, Bubble Size = Số đơn hàng. Làm nổi bật góc dưới bên phải (High Revenue, Low Review).
- **Top 10 Categories Bar Chart:** Doanh thu và % Cước phí vận chuyển trên tổng giá trị.
- **Bảng chi tiết Seller cần can thiệp:** Seller ID, Thành phố, Doanh thu, Tỷ lệ trễ, Review TB, Thời gian chuẩn bị hàng (`seller_dispatch_days`).
