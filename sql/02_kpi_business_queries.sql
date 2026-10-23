-- ====================================================================
-- OLIST E-COMMERCE: ANALYTICAL & BUSINESS KPI SQL QUERIES
-- Executed against: Star Schema (fact_order_items + dimension tables)
-- Demonstrates: CTEs, Window Functions, Aggregate Ratios, Case When
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: DELIVERY DELAY VS CUSTOMER SATISFACTION (The Tolerance Cliff)
-- Business Goal: Measure average rating and 1-star percentage across delay buckets.
-- --------------------------------------------------------------------
WITH order_level AS (
    -- Deduplicate to order level to prevent multi-item orders from skewing review score
    SELECT 
        order_id,
        delay_bucket,
        review_score,
        is_delayed
    FROM fact_order_items f
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivered = 1
      AND f.review_score IS NOT NULL
    GROUP BY f.order_id, f.delay_bucket, f.review_score, f.is_delayed
)
SELECT 
    delay_bucket,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1.0 ELSE 0 END) * 100.0 / COUNT(order_id), 2) AS pct_1_star_reviews,
    ROUND(SUM(CASE WHEN review_score = 5 THEN 1.0 ELSE 0 END) * 100.0 / COUNT(order_id), 2) AS pct_5_star_reviews
FROM order_level
GROUP BY delay_bucket
ORDER BY 
    CASE delay_bucket
        WHEN 'On Time / Early' THEN 1
        WHEN '1-3 Days Late'   THEN 2
        WHEN '4-7 Days Late'   THEN 3
        WHEN '> 7 Days Late'   THEN 4
        ELSE 5
    END;


-- --------------------------------------------------------------------
-- QUERY 2: GEOGRAPHIC BOTTLENECKS (Top Delayed States & Regional Delay Rates)
-- Business Goal: Identify states with highest delay rates (min 100 orders).
-- Grain-Safe: Deduplicate to order level first to prevent multi-item orders from skewing averages.
-- --------------------------------------------------------------------
WITH order_level_state AS (
    -- Deduplicate to order level per customer state
    SELECT 
        f.order_id,
        c.customer_state,
        f.is_delayed,
        f.actual_delivery_days,
        f.review_score
    FROM fact_order_items f
    JOIN dim_customers c ON f.customer_id = c.customer_id
    WHERE f.order_status = 'delivered' AND f.is_valid_delivered = 1
    GROUP BY f.order_id, c.customer_state, f.is_delayed, f.actual_delivery_days, f.review_score
),
state_summary AS (
    SELECT 
        customer_state,
        COUNT(order_id) AS total_orders,
        SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_orders,
        ROUND(AVG(actual_delivery_days), 1) AS avg_delivery_days,
        ROUND(AVG(review_score), 2) AS avg_review_score
    FROM order_level_state
    GROUP BY customer_state
)
SELECT 
    customer_state,
    total_orders,
    delayed_orders,
    ROUND(delayed_orders * 100.0 / total_orders, 2) AS delay_rate_pct,
    avg_delivery_days,
    avg_review_score,
    RANK() OVER (ORDER BY (delayed_orders * 100.0 / total_orders) DESC) AS delay_rank
FROM state_summary
WHERE total_orders >= 100
ORDER BY delay_rate_pct DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 3: SELLER RISK MATRIX (High Revenue, Low Satisfaction Sellers)
-- Business Goal: Flag top revenue sellers with average review < 3.8 for operational audit.
-- Methodology Note: Review scores and delays are order-level attributes.
-- Deduplicating to (seller_id, order_id) ensures order-level weighting (yielding 16 High-Risk sellers).
-- Direct aggregation on fact_order_items yields item-level weighting (21 sellers).
-- --------------------------------------------------------------------
WITH seller_orders AS (
    -- Bước 1: Tổng hợp ở cấp độ (seller, order) để bảo toàn grain của review_score và is_delayed
    SELECT 
        f.seller_id,
        f.order_id,
        SUM(f.price) AS order_revenue,
        COUNT(f.order_item_id) AS items_in_order,
        AVG(f.review_score) AS order_review_score,
        MAX(f.is_delayed) AS is_order_delayed,
        AVG(f.seller_dispatch_days) AS avg_dispatch_days
    FROM fact_order_items f
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivered = 1
    GROUP BY f.seller_id, f.order_id
),
seller_summary AS (
    -- Bước 2: Tổng hợp lên cấp độ người bán (Seller Level)
    -- Lưu ý: Giữ raw_avg_review (chưa làm tròn) để so ngưỡng chính xác, tránh lệch với DAX
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        SUM(so.order_revenue) AS raw_total_revenue,
        ROUND(SUM(so.order_revenue), 2) AS total_revenue,
        COUNT(so.order_id) AS total_orders,
        SUM(so.items_in_order) AS items_sold,
        AVG(so.order_review_score) AS raw_avg_review,
        ROUND(AVG(so.order_review_score), 2) AS avg_review_score,
        ROUND(AVG(so.is_order_delayed) * 100.0, 2) AS order_delay_rate_pct,
        ROUND(AVG(so.avg_dispatch_days), 1) AS avg_dispatch_days
    FROM seller_orders so
    JOIN dim_sellers s ON so.seller_id = s.seller_id
    GROUP BY s.seller_id, s.seller_city, s.seller_state
)
SELECT 
    seller_id,
    seller_city,
    seller_state,
    total_revenue,
    total_orders,
    items_sold,
    avg_review_score,
    order_delay_rate_pct,
    avg_dispatch_days,
    CASE 
        WHEN raw_total_revenue >= 15000 AND raw_avg_review < 3.8 THEN 'CRITICAL RISK - AUDIT REQUIRED'
        WHEN raw_total_revenue >= 15000 AND raw_avg_review >= 4.2 THEN 'STAR SELLER'
        WHEN raw_total_revenue >= 15000 THEN 'STANDARD HIGH-VOLUME'
        ELSE 'STANDARD'
    END AS operational_status
FROM seller_summary
WHERE raw_total_revenue >= 15000 AND raw_avg_review < 3.8
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 4: PRODUCT CATEGORY PERFORMANCE & FREIGHT BURDEN
-- Business Goal: Evaluate Revenue, Freight % of Gross Order Value, and ratings by category.
-- Methodology Note: Categories are item-level attributes. Financial metrics (Revenue, Freight, GOV)
-- are aggregated at item level. Customer metrics (Avg Review Score, Delay Rate %) are calculated
-- at Order-Level (deduplicated by order_id, category) to match DAX Measure #16 and Python EDA.
-- Naming: Revenue = SUM(price), Gross Order Value = price + freight, Freight Ratio = freight / GOV
-- --------------------------------------------------------------------
WITH category_financials AS (
    SELECT 
        p.product_category_formatted AS category_name,
        COUNT(f.order_item_id) AS items_sold,
        SUM(f.price) AS total_revenue,
        SUM(f.freight_value) AS total_freight,
        SUM(f.item_total_value) AS gross_order_value
    FROM fact_order_items f
    JOIN dim_products p ON f.product_id = p.product_id
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivered = 1
    GROUP BY p.product_category_formatted
),
category_orders AS (
    -- Deduplicate về cấp (order_id, category) để tính avg_review và delay_rate ở order level (đồng bộ 100% với DAX & Python)
    SELECT 
        p.product_category_formatted AS category_name,
        f.order_id,
        f.review_score,
        f.is_delayed
    FROM fact_order_items f
    JOIN dim_products p ON f.product_id = p.product_id
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivered = 1
    GROUP BY p.product_category_formatted, f.order_id, f.review_score, f.is_delayed
),
category_order_kpis AS (
    SELECT 
        category_name,
        COUNT(order_id) AS total_orders,
        AVG(review_score) AS avg_review_score,
        AVG(is_delayed) * 100.0 AS delay_rate_pct
    FROM category_orders
    GROUP BY category_name
)
SELECT 
    cf.category_name,
    cf.items_sold,
    ROUND(cf.total_revenue, 2) AS total_revenue,
    ROUND(cf.total_freight, 2) AS total_freight,
    ROUND(cf.gross_order_value, 2) AS gross_order_value,
    ROUND(cf.total_freight * 100.0 / cf.gross_order_value, 2) AS freight_pct_of_gov,
    ROUND(co.avg_review_score, 2) AS avg_review_score,
    ROUND(co.delay_rate_pct, 2) AS delay_rate_pct
FROM category_financials cf
JOIN category_order_kpis co ON cf.category_name = co.category_name
ORDER BY cf.total_revenue DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 5: CUSTOMER RETENTION & FIRST ORDER EXPERIENCE (Completed Purchases)
-- Business Goal: Quantify the drop in completed repeat purchases caused by a delayed first order.
-- Methodological Notes:
-- 1. Repeat Completed Buyer is defined as a customer with >= 2 delivered orders.
-- 2. First order must be 'delivered' and have valid delivery date (is_valid_delivered = 1).
-- 3. SQL vs Python Sequence Alignment: Fact table includes order_purchase_timestamp, allowing
--    exact second-grain chronological ordering partitioned by customer_unique_id with tie-break f.order_id ASC.
--    This achieves 100% exact numerical match with Python:
--    On-time first order retention = 3.04% (2,641 / 86,995), Delayed first order retention = 2.52% (160 / 6,355),
--    representing a statistically significant 17.1% relative drop (Chi-Square with Yates correction: chi2 = 5.286, p = 0.0215).
-- 4. Limitation (Right-Censoring): Olist dataset spans 2016-2018. Customers acquired
--    near the end of the window had less opportunity to repeat purchase.
-- --------------------------------------------------------------------
WITH customer_orders AS (
    -- Group by customer_unique_id and order_id on delivered orders only
    SELECT 
        c.customer_unique_id,
        f.order_id,
        f.order_purchase_timestamp,
        f.is_delayed,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY f.order_purchase_timestamp ASC, f.order_id ASC
        ) AS order_sequence,
        COUNT(f.order_id) OVER (
            PARTITION BY c.customer_unique_id
        ) AS total_completed_orders
    FROM fact_order_items f
    JOIN dim_customers c ON f.customer_id = c.customer_id
    WHERE f.order_status = 'delivered' AND f.is_valid_delivered = 1
    GROUP BY c.customer_unique_id, f.order_id, f.order_purchase_timestamp, f.is_delayed
),
first_orders AS (
    -- Lọc riêng đơn hàng đầu tiên (First Order) giao thành công hợp lệ
    SELECT 
        customer_unique_id,
        is_delayed,
        CASE WHEN total_completed_orders > 1 THEN 1 ELSE 0 END AS is_repeat_buyer
    FROM customer_orders
    WHERE order_sequence = 1
)
SELECT 
    CASE is_delayed 
        WHEN 0 THEN 'First Order Delivered On-Time'
        WHEN 1 THEN 'First Order Delivered LATE'
    END AS first_order_delivery_status,
    COUNT(customer_unique_id) AS total_customers,
    SUM(is_repeat_buyer) AS repeat_customers,
    ROUND(SUM(is_repeat_buyer) * 100.0 / COUNT(customer_unique_id), 2) AS repeat_purchase_rate_pct
FROM first_orders
GROUP BY is_delayed;
