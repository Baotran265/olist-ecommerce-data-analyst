import os
import sys
import sqlite3
import pandas as pd
import numpy as np

# Cấu hình UTF-8 an toàn
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)

PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
STAR_SCHEMA_DIR = os.path.join(PROCESSED_DATA_DIR, 'star_schema')
DB_PATH = os.path.join(BASE_DIR, 'data', 'olist_star_schema.db')

os.makedirs(STAR_SCHEMA_DIR, exist_ok=True)

# ==========================================
# 2. BUILD DIMENSIONS
# ==========================================

def build_dim_date():
    print("--- [1/5] Building Dim Date (Calendar Table) ---")
    start_date = '2016-01-01'
    end_date = '2018-12-31'
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    df_date = pd.DataFrame({'date': dates})
    df_date['date_key'] = df_date['date'].dt.strftime('%Y%m%d').astype(int)
    df_date['date'] = df_date['date'].dt.strftime('%Y-%m-%d')
    df_date['year'] = pd.to_datetime(df_date['date']).dt.year
    df_date['quarter'] = 'Q' + pd.to_datetime(df_date['date']).dt.quarter.astype(str)
    df_date['year_quarter'] = df_date['year'].astype(str) + '-' + df_date['quarter']
    df_date['month'] = pd.to_datetime(df_date['date']).dt.month
    df_date['month_name'] = pd.to_datetime(df_date['date']).dt.strftime('%B')
    df_date['year_month'] = pd.to_datetime(df_date['date']).dt.strftime('%Y-%m')
    df_date['day_of_month'] = pd.to_datetime(df_date['date']).dt.day
    df_date['day_of_week'] = pd.to_datetime(df_date['date']).dt.dayofweek + 1  # 1 = Monday, 7 = Sunday
    df_date['day_name'] = pd.to_datetime(df_date['date']).dt.strftime('%A')
    df_date['is_weekend'] = df_date['day_of_week'].isin([6, 7]).astype(int)


    out_csv = os.path.join(STAR_SCHEMA_DIR, 'dim_date.csv')
    df_date.to_csv(out_csv, index=False)
    print(f"  -> Saved dim_date to: {out_csv} ({len(df_date):,} days)")
    return df_date


def build_dim_customers_and_sellers():
    print("--- [2/5] Building Dim Customers & Dim Sellers (Enriched with Geolocation) ---")
    df_cust = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_customers_cleaned.csv'))
    df_sellers = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_sellers_cleaned.csv'))
    df_geo = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_geolocation_cleaned.csv'))

    # Merge tọa độ địa lý (1-1 qua zip_code_prefix)
    dim_cust = df_cust.merge(
        df_geo[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']],
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    ).drop(columns=['geolocation_zip_code_prefix'])

    dim_sellers = df_sellers.merge(
        df_geo[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']],
        left_on='seller_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    ).drop(columns=['geolocation_zip_code_prefix'])

    out_cust = os.path.join(STAR_SCHEMA_DIR, 'dim_customers.csv')
    out_sellers = os.path.join(STAR_SCHEMA_DIR, 'dim_sellers.csv')

    dim_cust.to_csv(out_cust, index=False)
    dim_sellers.to_csv(out_sellers, index=False)
    print(f"  -> Saved dim_customers to: {out_cust} ({len(dim_cust):,} rows)")
    print(f"  -> Saved dim_sellers to: {out_sellers} ({len(dim_sellers):,} rows)")
    return dim_cust, dim_sellers


def build_dim_products():
    print("--- [3/5] Building Dim Products ---")
    df_prods = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_products_cleaned.csv'))

    dim_products = df_prods[[
        'product_id',
        'product_category_formatted',
        'product_category_name_english',
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm',
        'product_photos_qty'
    ]].copy()

    out_prods = os.path.join(STAR_SCHEMA_DIR, 'dim_products.csv')
    dim_products.to_csv(out_prods, index=False)
    print(f"  -> Saved dim_products to: {out_prods} ({len(dim_products):,} rows)")
    return dim_products


# ==========================================
# 3. BUILD FACT TABLE
# ==========================================

def build_fact_order_items():
    print("--- [4/5] Building Fact Order Items (Grain: 1 row = 1 order item) ---")
    df_master = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_master_analytical_dataset.csv'))

    # Sinh surrogate date key từ order_purchase_timestamp (YYYYMMDD)
    df_master['order_date_key'] = pd.to_datetime(df_master['order_purchase_timestamp']).dt.strftime('%Y%m%d').astype(int)

    fact = df_master[[
        'order_id',
        'order_item_id',
        'customer_id',
        'seller_id',
        'product_id',
        'order_date_key',
        'order_purchase_timestamp',
        'order_status',
        'price',
        'freight_value',
        'item_total_value',
        'actual_delivery_days',
        'estimated_delivery_days',
        'delivery_delay_days',
        'is_delayed',
        'is_valid_delivered',
        'delay_bucket',
        'seller_dispatch_days',
        'carrier_delivery_days',
        'review_score',
        'satisfaction_tier',
        'has_comment',
        'is_interstate'
    ]].copy()

    # has_comment là cờ nhị phân (1/0), nếu đơn không có review thì gán 0
    fact['has_comment'] = fact['has_comment'].fillna(0).astype(int)

    out_fact = os.path.join(STAR_SCHEMA_DIR, 'fact_order_items.csv')
    fact.to_csv(out_fact, index=False)
    print(f"  -> Saved fact_order_items to: {out_fact} ({len(fact):,} rows, {len(fact.columns)} columns)")
    return fact


# ==========================================
# 4. LOAD INTO SQLITE DATABASE
# ==========================================

def load_into_sqlite(dim_date, dim_cust, dim_sellers, dim_products, fact_items):
    print("--- [5/5] Loading Star Schema into SQLite Database with Strict DDL Constraints ---")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Thực thi DDL Schema từ sql/01_create_star_schema.sql (Tạo bảng có Primary Key & Foreign Keys)
    ddl_path = os.path.join(BASE_DIR, 'sql', '01_create_star_schema.sql')
    with open(ddl_path, 'r', encoding='utf-8') as f:
        ddl_sql = f.read()
    cursor.executescript(ddl_sql)
    print("  -> Applied DDL schema (Tables, Primary Keys, Foreign Keys, Indexes) with PRAGMA foreign_keys = ON")

    # 2. Nạp dữ liệu vào bảng (if_exists='append' để giữ nguyên DDL constraints)
    dim_date.to_sql('dim_date', conn, if_exists='append', index=False)
    dim_cust.to_sql('dim_customers', conn, if_exists='append', index=False)
    dim_sellers.to_sql('dim_sellers', conn, if_exists='append', index=False)
    dim_products.to_sql('dim_products', conn, if_exists='append', index=False)
    fact_items.to_sql('fact_order_items', conn, if_exists='append', index=False)

    # 3. Commit và hoàn tất (Các indexes đã được khởi tạo chuẩn xác trong DDL script)
    conn.commit()

    print(f"  -> Star Schema successfully loaded into SQLite: {DB_PATH}")
    conn.close()


# ==========================================
# 5. MAIN PIPELINE
# ==========================================

def main():
    print("="*60)
    print("STARTING PHASE 6: DIMENSIONAL MODELING (STAR SCHEMA)")
    print("="*60)

    dim_date = build_dim_date()
    dim_cust, dim_sellers = build_dim_customers_and_sellers()
    dim_products = build_dim_products()
    fact_items = build_fact_order_items()

    load_into_sqlite(dim_date, dim_cust, dim_sellers, dim_products, fact_items)

    print("\n" + "="*60)
    print("PHASE 6 STAR SCHEMA CREATED SUCCESSFULLY!")
    print(f"Output files in: {STAR_SCHEMA_DIR}")
    print(f"SQLite DB: {DB_PATH}")
    print("="*60)

if __name__ == "__main__":
    main()
