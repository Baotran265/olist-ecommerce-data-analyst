-- ====================================================================
-- OLIST E-COMMERCE: ANALYTICAL & BUSINESS KPI SQL QUERIES
-- Executed against: Star Schema (fact_order_items + dimension tables)
-- Grain: One row per order item in fact_order_items
-- ====================================================================


-- --------------------------------------------------------------------
-- QUERY 1: DELIVERY DELAY VS CUSTOMER SATISFACTION
-- Business Goal:
-- Compare average review and 1-star rate across delivery-delay buckets.
-- Cohort: Delivered orders with valid delivery-delay information.
-- Grain: One row per order.
-- --------------------------------------------------------------------

WITH order_level AS (
    SELECT
        f.order_id,
        MAX(f.delay_bucket) AS delay_bucket,
        MAX(f.review_score) AS review_score,
        MAX(f.is_delayed) AS is_delayed
    FROM fact_order_items AS f
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY f.order_id
)
SELECT
    delay_bucket,
    COUNT(*) AS total_orders,
    COUNT(review_score) AS valid_reviews_count,
    ROUND(AVG(review_score), 2) AS mean_review,
    ROUND(
        SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(review_score), 0),
        2
    ) AS pct_1_star
FROM order_level
GROUP BY delay_bucket
ORDER BY
    CASE delay_bucket
        WHEN 'On Time / Early' THEN 1
        WHEN '1-3 Days Late' THEN 2
        WHEN '4-7 Days Late' THEN 3
        WHEN '> 7 Days Late' THEN 4
        ELSE 5
    END;


-- --------------------------------------------------------------------
-- QUERY 2: GEOGRAPHIC BOTTLENECKS
-- Business Goal:
-- Identify states with the highest delivery-delay rates.
-- Minimum sample: 100 valid delivery-delay orders per state.
-- Grain: One row per order.
-- --------------------------------------------------------------------

WITH order_level_state AS (
    SELECT
        f.order_id,
        c.customer_state,
        MAX(f.is_delayed) AS is_delayed,
        MAX(f.actual_delivery_days) AS actual_delivery_days,
        MAX(f.review_score) AS review_score
    FROM fact_order_items AS f
    JOIN dim_customers AS c
        ON f.customer_id = c.customer_id
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY
        f.order_id,
        c.customer_state
),
state_summary AS (
    SELECT
        customer_state,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END)
            AS delayed_orders,
        ROUND(AVG(actual_delivery_days), 1)
            AS avg_delivery_days,
        ROUND(AVG(review_score), 2)
            AS avg_review_score
    FROM order_level_state
    GROUP BY customer_state
)
SELECT
    customer_state,
    total_orders,
    delayed_orders,
    ROUND(
        delayed_orders * 100.0 / NULLIF(total_orders, 0),
        2
    ) AS delay_rate_pct,
    avg_delivery_days,
    avg_review_score,
    RANK() OVER (
        ORDER BY
            delayed_orders * 100.0 / NULLIF(total_orders, 0) DESC
    ) AS delay_rank
FROM state_summary
WHERE total_orders >= 100
ORDER BY delay_rate_pct DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 3: SELLER RISK MATRIX
-- Business Goal:
-- Identify high-revenue sellers with average review below 3.8.
-- Cohort: Delivered orders with valid delivery-delay information.
-- Grain: Seller-order, then seller.
-- Note: Revenue here is product price, excluding freight.
-- --------------------------------------------------------------------

WITH seller_orders AS (
    SELECT
        f.seller_id,
        f.order_id,
        SUM(f.price) AS order_revenue,
        COUNT(f.order_item_id) AS items_in_order,
        AVG(f.review_score) AS order_review_score,
        MAX(f.is_delayed) AS is_order_delayed,
        AVG(f.seller_dispatch_days) AS avg_dispatch_days
    FROM fact_order_items AS f
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY
        f.seller_id,
        f.order_id
),
seller_summary AS (
    SELECT
        so.seller_id,
        s.seller_city,
        s.seller_state,
        SUM(so.order_revenue) AS raw_total_revenue,
        ROUND(SUM(so.order_revenue), 2) AS total_revenue,
        COUNT(*) AS total_orders,
        SUM(so.items_in_order) AS items_sold,
        AVG(so.order_review_score) AS raw_avg_review,
        ROUND(AVG(so.order_review_score), 2) AS avg_review_score,
        ROUND(AVG(so.is_order_delayed) * 100.0, 2)
            AS order_delay_rate_pct,
        ROUND(AVG(so.avg_dispatch_days), 1)
            AS avg_dispatch_days
    FROM seller_orders AS so
    JOIN dim_sellers AS s
        ON so.seller_id = s.seller_id
    GROUP BY
        so.seller_id,
        s.seller_city,
        s.seller_state
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
    -- WHERE bên dưới đã lọc raw_avg_review < 3.8 nên chỉ cần phân nhóm theo cỡ mẫu
    CASE
        WHEN total_orders >= 30
            THEN 'High Risk - Intervene'
        ELSE 'Potential Risk - Monitor (Low Sample)'
    END AS operational_status
FROM seller_summary
WHERE raw_total_revenue >= 15000
  AND raw_avg_review < 3.8
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 4: PRODUCT CATEGORY PERFORMANCE & FREIGHT BURDEN
-- Business Goal:
-- Compare revenue, freight burden, ratings and delay rates by category.
-- Financial grain: Item.
-- Experience grain: One row per order-category.
-- Cohort: Delivered orders with valid delivery-delay information.
-- Revenue = SUM(price)
-- GOV = SUM(price + freight)
-- Freight % of GOV = freight / GOV * 100
-- --------------------------------------------------------------------

WITH category_financials AS (
    SELECT
        p.product_category_formatted AS category_name,
        COUNT(f.order_item_id) AS items_sold,
        SUM(f.price) AS total_revenue,
        SUM(f.freight_value) AS total_freight,
        SUM(f.item_total_value) AS gross_order_value
    FROM fact_order_items AS f
    JOIN dim_products AS p
        ON f.product_id = p.product_id
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY p.product_category_formatted
),
category_orders AS (
    SELECT
        p.product_category_formatted AS category_name,
        f.order_id,
        MAX(f.review_score) AS review_score,
        MAX(f.is_delayed) AS is_delayed
    FROM fact_order_items AS f
    JOIN dim_products AS p
        ON f.product_id = p.product_id
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY
        p.product_category_formatted,
        f.order_id
),
category_order_kpis AS (
    SELECT
        category_name,
        COUNT(*) AS total_orders,
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
    ROUND(
        cf.total_freight * 100.0
        / NULLIF(cf.gross_order_value, 0),
        2
    ) AS freight_pct_of_gov,
    ROUND(co.avg_review_score, 2) AS avg_review_score,
    ROUND(co.delay_rate_pct, 2) AS delay_rate_pct
FROM category_financials AS cf
JOIN category_order_kpis AS co
    ON cf.category_name = co.category_name
ORDER BY cf.total_revenue DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 5: CUSTOMER RETENTION & FIRST VALID DELIVERY EXPERIENCE
-- Business Goal:
-- Compare repeat-purchase rates by the first eligible order's delay status.
-- Repeat buyer: Customer with at least 2 eligible delivered orders.
-- Eligible order: Delivered with valid delivery-delay information.
-- First order: Earliest eligible order in the observation window.
-- Limitation: This is not necessarily the customer's first order ever.
-- --------------------------------------------------------------------

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        f.order_id,
        f.order_purchase_timestamp,
        MAX(f.is_delayed) AS is_delayed
    FROM fact_order_items AS f
    JOIN dim_customers AS c
        ON f.customer_id = c.customer_id
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY
        c.customer_unique_id,
        f.order_id,
        f.order_purchase_timestamp
),
sequenced_orders AS (
    SELECT
        customer_unique_id,
        order_id,
        order_purchase_timestamp,
        is_delayed,
        ROW_NUMBER() OVER (
            PARTITION BY customer_unique_id
            ORDER BY order_purchase_timestamp ASC, order_id ASC
        ) AS order_sequence,
        COUNT(*) OVER (
            PARTITION BY customer_unique_id
        ) AS total_completed_orders
    FROM customer_orders
),
first_orders AS (
    SELECT
        customer_unique_id,
        is_delayed,
        CASE
            WHEN total_completed_orders > 1 THEN 1
            ELSE 0
        END AS is_repeat_buyer
    FROM sequenced_orders
    WHERE order_sequence = 1
)
SELECT
    CASE
        WHEN is_delayed = 0 THEN 'First Eligible Order On-Time'
        WHEN is_delayed = 1 THEN 'First Eligible Order Late'
        ELSE 'Unknown'
    END AS first_order_delivery_status,
    COUNT(*) AS total_customers,
    SUM(is_repeat_buyer) AS repeat_customers,
    ROUND(
        SUM(is_repeat_buyer) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_purchase_rate_pct
FROM first_orders
GROUP BY is_delayed
ORDER BY is_delayed;


-- --------------------------------------------------------------------
-- QUERY 6: MONTHLY TIME SERIES (ORDER-LEVEL)
-- Business Goal:
-- Track orders, revenue, delay rate and review score by purchase month.
-- Cohort: Delivered orders with valid delivery-delay information.
-- Grain: One row per order, then month. (All metrics are order-level,
-- so delay rate and review are not biased by multi-item orders.)
-- Revenue = SUM(price) per order, excluding freight.
-- Note: Co-occurrence of high-delay and low-review months is
-- descriptive only; it does not identify the cause of the delays.
-- --------------------------------------------------------------------

WITH order_level AS (
    SELECT
        f.order_id,
        SUBSTR(MAX(f.order_purchase_timestamp), 1, 7) AS year_month,
        SUM(f.price) AS order_revenue,
        MAX(f.is_delayed) AS is_delayed,
        MAX(f.review_score) AS review_score
    FROM fact_order_items AS f
    WHERE f.order_status = 'delivered'
      AND f.is_valid_delivery_delay = 1
    GROUP BY f.order_id
)
SELECT
    year_month,
    COUNT(*) AS total_orders,
    ROUND(SUM(order_revenue), 0) AS total_revenue,
    ROUND(AVG(is_delayed) * 100.0, 2) AS delay_rate_pct,
    COUNT(review_score) AS valid_reviews_count,
    ROUND(AVG(review_score), 2) AS mean_review
FROM order_level
GROUP BY year_month
ORDER BY year_month;
