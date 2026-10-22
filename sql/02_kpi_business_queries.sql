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
    FROM fact_order_items
    WHERE order_status = 'delivered'
      AND review_score IS NOT NULL
    GROUP BY order_id, delay_bucket, review_score, is_delayed
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
    WHERE f.order_status = 'delivered'
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
-- --------------------------------------------------------------------
WITH seller_kpis AS (
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        ROUND(SUM(f.price), 2) AS total_revenue,
        COUNT(f.order_item_id) AS items_sold,
        COUNT(DISTINCT f.order_id) AS total_orders,
        ROUND(AVG(f.review_score), 2) AS avg_review_score,
        ROUND(AVG(f.is_delayed) * 100.0, 2) AS item_delay_rate_pct,
        ROUND(AVG(f.seller_dispatch_days), 1) AS avg_dispatch_days
    FROM fact_order_items f
    JOIN dim_sellers s ON f.seller_id = s.seller_id
    WHERE f.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_city, s.seller_state
)
SELECT 
    seller_id,
    seller_state,
    total_revenue,
    total_orders,
    avg_review_score,
    item_delay_rate_pct,
    avg_dispatch_days,
    CASE 
        WHEN total_revenue >= 15000 AND avg_review_score < 3.8 THEN 'CRITICAL RISK - AUDIT REQUIRED'
        WHEN total_revenue >= 15000 AND avg_review_score >= 4.2 THEN 'STAR SELLER'
        ELSE 'STANDARD'
    END AS operational_status
FROM seller_kpis
WHERE total_revenue >= 15000 AND avg_review_score < 3.8
ORDER BY total_revenue DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 4: PRODUCT CATEGORY PERFORMANCE & FREIGHT BURDEN
-- Business Goal: Evaluate GMV, Freight % of GMV, and ratings by category.
-- --------------------------------------------------------------------
SELECT 
    p.product_category_formatted AS category_name,
    COUNT(f.order_item_id) AS items_sold,
    ROUND(SUM(f.price), 2) AS total_revenue,
    ROUND(SUM(f.freight_value), 2) AS total_freight,
    ROUND(SUM(f.freight_value) * 100.0 / SUM(f.item_total_value), 2) AS freight_pct_of_total,
    ROUND(AVG(f.review_score), 2) AS avg_review_score,
    ROUND(AVG(f.is_delayed) * 100.0, 2) AS delay_rate_pct
FROM fact_order_items f
JOIN dim_products p ON f.product_id = p.product_id
WHERE f.order_status = 'delivered'
GROUP BY p.product_category_formatted
ORDER BY total_revenue DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 5: CUSTOMER RETENTION & FIRST ORDER EXPERIENCE
-- Business Goal: Quantify the drop in repeat purchase rate caused by a delayed first order.
-- Methodological Note:
-- 1. Repeat Buyer is defined as a customer with >= 2 distinct lifetime orders.
-- 2. First order must be 'delivered' to establish whether it arrived on-time or delayed.
-- 3. Limitation (Right-Censoring): Olist dataset spans 2016-2018. Customers acquired
--    near the end of the window (e.g., Aug 2018) had less opportunity to repeat purchase
--    than customers acquired in 2017.
-- --------------------------------------------------------------------
WITH customer_orders AS (
    -- Group by customer_unique_id and order_id to get 1 row per unique order
    SELECT 
        c.customer_unique_id,
        f.order_id,
        f.order_date_key,
        f.is_delayed,
        f.order_status,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY f.order_date_key ASC, f.order_id ASC
        ) AS order_sequence,
        COUNT(f.order_id) OVER (
            PARTITION BY c.customer_unique_id
        ) AS total_lifetime_orders
    FROM fact_order_items f
    JOIN dim_customers c ON f.customer_id = c.customer_id
    GROUP BY c.customer_unique_id, f.order_id, f.order_date_key, f.is_delayed, f.order_status
),
first_orders AS (
    -- Lọc riêng đơn hàng đầu tiên (First Order) đã giao thành công
    SELECT 
        customer_unique_id,
        is_delayed,
        CASE WHEN total_lifetime_orders > 1 THEN 1 ELSE 0 END AS is_repeat_buyer
    FROM customer_orders
    WHERE order_sequence = 1
      AND order_status = 'delivered'
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
