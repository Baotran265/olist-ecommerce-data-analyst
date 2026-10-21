-- ====================================================================
-- OLIST E-COMMERCE: STAR SCHEMA DDL DEFINITION
-- Architecture: Kimball Dimensional Model (Star Schema)
-- Engine Compatibility: PostgreSQL, SQLite, DuckDB, BigQuery
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. DIMENSION: DATE (Calendar Table)
-- Grain: 1 row = 1 calendar day
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,              -- Format: YYYYMMDD (e.g., 20170101)
    date DATE NOT NULL,                    -- Standard ISO date
    year INT NOT NULL,
    quarter VARCHAR(2) NOT NULL,           -- Q1, Q2, Q3, Q4
    year_quarter VARCHAR(7) NOT NULL,      -- 2017-Q1
    month INT NOT NULL,                    -- 1 to 12
    month_name VARCHAR(15) NOT NULL,       -- January, February...
    year_month VARCHAR(7) NOT NULL,        -- 2017-01
    day_of_month INT NOT NULL,             -- 1 to 31
    day_of_week INT NOT NULL,              -- 1 (Monday) to 7 (Sunday)
    day_name VARCHAR(15) NOT NULL,         -- Monday, Tuesday...
    is_weekend INT NOT NULL                -- 1 = Weekend, 0 = Weekday
);

-- --------------------------------------------------------------------
-- 2. DIMENSION: CUSTOMERS
-- Grain: 1 row = 1 customer_id (Transaction customer account)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32) NOT NULL, -- Real person identifier
    customer_zip_code_prefix INT NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state VARCHAR(2) NOT NULL,      -- 2-letter Brazilian state code
    geolocation_lat FLOAT,                   -- Median latitude from geolocation
    geolocation_lng FLOAT                    -- Median longitude from geolocation
);

-- --------------------------------------------------------------------
-- 3. DIMENSION: SELLERS
-- Grain: 1 row = 1 seller_id
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_sellers (
    seller_id VARCHAR(32) PRIMARY KEY,
    seller_zip_code_prefix INT NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state VARCHAR(2) NOT NULL,        -- 2-letter Brazilian state code
    geolocation_lat FLOAT,
    geolocation_lng FLOAT
);

-- --------------------------------------------------------------------
-- 4. DIMENSION: PRODUCTS
-- Grain: 1 row = 1 product_id
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_category_formatted VARCHAR(100) NOT NULL,    -- Title Case English Category
    product_category_name_english VARCHAR(100) NOT NULL, -- Lowercase English Category
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT,
    product_photos_qty FLOAT
);

-- --------------------------------------------------------------------
-- 5. FACT TABLE: ORDER ITEMS
-- Grain: 1 row = 1 item in an order
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INT NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    order_date_key INT NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    
    -- Financial Measures
    price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    item_total_value DECIMAL(10, 2) NOT NULL, -- price + freight_value
    
    -- Operational Delivery Metrics (in days)
    actual_delivery_days FLOAT,               -- Customer delivered - Purchased
    estimated_delivery_days FLOAT,            -- Estimated - Purchased
    delivery_delay_days FLOAT,                -- Customer delivered - Estimated (>0 = late)
    is_delayed INT NOT NULL,                  -- 1 if delivery_delay_days > 0 else 0
    is_valid_delivered INT NOT NULL,          -- 1 if status = 'delivered' and delivered_date is not null
    delay_bucket VARCHAR(30) NOT NULL,        -- 'On Time / Early', '1-3 Days Late', etc.
    seller_dispatch_days FLOAT,               -- Carrier date - Purchased
    carrier_delivery_days FLOAT,              -- Customer delivered - Carrier date
    
    -- Customer Satisfaction Metrics
    review_score FLOAT,                       -- 1 to 5 stars
    satisfaction_tier VARCHAR(15),            -- 'Positive', 'Neutral', 'Negative'
    has_comment INT NOT NULL,                 -- 1 if review has text message
    is_interstate INT NOT NULL,               -- 1 if customer_state != seller_state
    
    -- Primary & Foreign Keys
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (seller_id) REFERENCES dim_sellers(seller_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key)
);

-- --------------------------------------------------------------------
-- 6. PERFORMANCE INDEXES
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_cust ON fact_order_items(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_seller ON fact_order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_fact_prod ON fact_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_order_items(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_status ON fact_order_items(order_status);
CREATE INDEX IF NOT EXISTS idx_fact_delayed ON fact_order_items(is_delayed);
