import os
import sys
import pandas as pd
import numpy as np

# Đảm bảo mã hóa UTF-8 cho console Windows
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 1. CONFIGURATION & DIRECTORIES
# ==========================================
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)

RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
OUTPUT_TABLES_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(OUTPUT_TABLES_DIR, exist_ok=True)

# Tracking log for documentation
cleaning_log = []

def log_action(table_name, raw_count, cleaned_count, actions, business_reason):
    cleaning_log.append({
        'Table': table_name,
        'Raw Rows': f"{raw_count:,}",
        'Cleaned Rows': f"{cleaned_count:,}",
        'Rows Delta': f"{cleaned_count - raw_count:,}",
        'Actions Taken': actions,
        'Business Justification': business_reason
    })

# ==========================================
# 2. CLEANING FUNCTIONS
# ==========================================

def clean_products_and_translations():
    print("--- [1/7] Cleaning Products & Categories ---")
    df_prods = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_products_dataset.csv'))
    df_trans = pd.read_csv(os.path.join(RAW_DATA_DIR, 'product_category_name_translation.csv'))
    raw_count = len(df_prods)

    # 1. Thêm 2 bản dịch còn thiếu đã cam kết trong Business Problem (Phase 1 & 3)
    missing_translations = pd.DataFrame([
        {'product_category_name': 'pc_gamer', 'product_category_name_english': 'pc_gamer'},
        {'product_category_name': 'portateis_cozinha_e_preparadores_de_alimentos', 'product_category_name_english': 'small_appliances_food_preparers'}
    ])
    df_trans_complete = pd.concat([df_trans, missing_translations], ignore_index=True).drop_duplicates(subset=['product_category_name'])

    # 2. Merge bản dịch tiếng Anh vào bảng sản phẩm
    df_prods_clean = df_prods.merge(df_trans_complete, on='product_category_name', how='left')

    # 3. Điền giá trị cho 610 sản phẩm không có category
    df_prods_clean['product_category_name'] = df_prods_clean['product_category_name'].fillna('unknown')
    df_prods_clean['product_category_name_english'] = df_prods_clean['product_category_name_english'].fillna('unknown')

    # Chuẩn hóa tên category tiếng Anh (thay '_' bằng khoảng trắng, viết hoa đầu từ)
    df_prods_clean['product_category_formatted'] = df_prods_clean['product_category_name_english'].str.replace('_', ' ').str.title()

    # 4. Xử lý các giá trị null về kích thước/trọng lượng (điền bằng median)
    num_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm', 'product_photos_qty']
    for col in num_cols:
        median_val = df_prods_clean[col].median()
        df_prods_clean[col] = df_prods_clean[col].fillna(median_val)

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_products_cleaned.csv')
    df_prods_clean.to_csv(out_path, index=False)
    print(f"  -> Saved cleaned products to: {out_path} ({len(df_prods_clean):,} rows)")

    log_action(
        'Products',
        raw_count,
        len(df_prods_clean),
        "Dịch bổ sung 'pc_gamer' và 'portateis_cozinha...'; map tiếng Anh; fill 'unknown' cho 610 missing category; fill median cho kích thước/trọng lượng.",
        "Đảm bảo 100% sản phẩm có danh mục hiển thị chuẩn tiếng Anh trên Dashboard và không có NaN kích thước làm lỗi thuật toán logistics."
    )
    return df_prods_clean


def clean_geolocation():
    print("--- [2/7] Cleaning Geolocation Dataset ---")
    df_geo = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_geolocation_dataset.csv'))
    raw_count = len(df_geo)

    # 1. Loại bỏ các dòng trùng lặp 100%
    df_geo_clean = df_geo.drop_duplicates()

    # 2. Lọc bỏ các tọa độ ngoại lai ngoài lãnh thổ Brazil (Lat: -34 to 6, Lng: -74 to -34)
    valid_coords = (
        (df_geo_clean['geolocation_lat'] >= -34) & (df_geo_clean['geolocation_lat'] <= 6) &
        (df_geo_clean['geolocation_lng'] >= -74) & (df_geo_clean['geolocation_lng'] <= -34)
    )
    df_geo_clean = df_geo_clean[valid_coords].copy()

    # 3. Chuẩn hóa tên thành phố (strip và lower)
    df_geo_clean['geolocation_city'] = df_geo_clean['geolocation_city'].astype(str).str.strip().str.lower()
    df_geo_clean['geolocation_state'] = df_geo_clean['geolocation_state'].astype(str).str.strip().str.upper()

    # 4. Aggregate về grain 1 zip_code = 1 dòng (tránh hoàn toàn rủi ro row multiplication)
    # Lấy median của tọa độ và mode (giá trị phổ biến nhất) của city/state
    geo_agg = df_geo_clean.groupby('geolocation_zip_code_prefix').agg(
        geolocation_lat=('geolocation_lat', 'median'),
        geolocation_lng=('geolocation_lng', 'median'),
        geolocation_city=('geolocation_city', lambda x: x.mode()[0] if not x.empty else 'unknown'),
        geolocation_state=('geolocation_state', lambda x: x.mode()[0] if not x.empty else 'unknown')
    ).reset_index()

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_geolocation_cleaned.csv')
    geo_agg.to_csv(out_path, index=False)
    print(f"  -> Saved aggregated geolocation to: {out_path} ({len(geo_agg):,} unique zip codes)")

    log_action(
        'Geolocation',
        raw_count,
        len(geo_agg),
        f"Xóa {raw_count - len(df_geo_clean):,} dòng trùng/ngoại lai; Gom nhóm (group by) 19,015 zip code duy nhất (median lat/lng, mode city/state).",
        "Triệt tiêu hoàn toàn rủi ro nhân dòng (Row Multiplication) khi kết nối dữ liệu địa lý với Customers và Sellers."
    )
    return geo_agg


def clean_customers_and_sellers():
    print("--- [3/7] Cleaning Customers and Sellers ---")
    df_cust = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_customers_dataset.csv'))
    df_sellers = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_sellers_dataset.csv'))

    # Chuẩn hóa text cho Customers
    df_cust['customer_city'] = df_cust['customer_city'].astype(str).str.strip().str.title()
    df_cust['customer_state'] = df_cust['customer_state'].astype(str).str.strip().str.upper()

    # Chuẩn hóa text cho Sellers
    df_sellers['seller_city'] = df_sellers['seller_city'].astype(str).str.strip().str.title()
    df_sellers['seller_state'] = df_sellers['seller_state'].astype(str).str.strip().str.upper()

    out_cust = os.path.join(PROCESSED_DATA_DIR, 'olist_customers_cleaned.csv')
    out_sellers = os.path.join(PROCESSED_DATA_DIR, 'olist_sellers_cleaned.csv')

    df_cust.to_csv(out_cust, index=False)
    df_sellers.to_csv(out_sellers, index=False)
    print(f"  -> Saved customers to: {out_cust} ({len(df_cust):,} rows)")
    print(f"  -> Saved sellers to: {out_sellers} ({len(df_sellers):,} rows)")

    log_action('Customers', len(df_cust), len(df_cust), "Chuẩn hóa định dạng Title Case cho City, Upper Case cho State code 2 ký tự.", "Nhất quán dữ liệu hiển thị địa phương.")
    log_action('Sellers', len(df_sellers), len(df_sellers), "Chuẩn hóa định dạng Title Case cho City, Upper Case cho State code 2 ký tự.", "Nhất quán dữ liệu hiển thị người bán.")
    return df_cust, df_sellers


def clean_order_reviews():
    print("--- [4/7] Cleaning Order Reviews ---")
    df_reviews = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_order_reviews_dataset.csv'))
    raw_count = len(df_reviews)

    # 1. Ép kiểu datetime
    df_reviews['review_creation_date'] = pd.to_datetime(df_reviews['review_creation_date'], errors='coerce')
    df_reviews['review_answer_timestamp'] = pd.to_datetime(df_reviews['review_answer_timestamp'], errors='coerce')

    # 2. Xử lý nhiều review cho 1 đơn hàng (Deduplication on order_id):
    # Sắp xếp theo review_answer_timestamp mới nhất và giữ lại 1 review đại diện cuối cùng cho mỗi đơn hàng
    df_reviews_sorted = df_reviews.sort_values(by=['order_id', 'review_answer_timestamp'], ascending=[True, False])
    df_reviews_clean = df_reviews_sorted.drop_duplicates(subset=['order_id'], keep='first').copy()

    # 3. Phân loại cảm xúc dựa trên review_score (1-2: Negative, 3: Neutral, 4-5: Positive)
    def categorize_sentiment(score):
        if score >= 4:
            return 'Positive'
        elif score == 3:
            return 'Neutral'
        else:
            return 'Negative'

    df_reviews_clean['satisfaction_tier'] = df_reviews_clean['review_score'].apply(categorize_sentiment)

    # 4. Điền giá trị cho title và message null
    df_reviews_clean['has_comment'] = df_reviews_clean['review_comment_message'].notna().astype(int)
    df_reviews_clean['review_comment_title'] = df_reviews_clean['review_comment_title'].fillna('')
    df_reviews_clean['review_comment_message'] = df_reviews_clean['review_comment_message'].fillna('')

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_order_reviews_cleaned.csv')
    df_reviews_clean.to_csv(out_path, index=False)
    print(f"  -> Saved cleaned reviews to: {out_path} ({len(df_reviews_clean):,} unique order reviews)")

    log_action(
        'Order Reviews',
        raw_count,
        len(df_reviews_clean),
        f"Lọc bỏ {raw_count - len(df_reviews_clean):,} review trùng order_id (giữ review mới nhất theo timestamp); thêm cột satisfaction_tier; flag has_comment.",
        "Ngăn chặn việc 1 order có nhiều review gây nhân dòng khi kết nối với bảng Orders."
    )
    return df_reviews_clean


def clean_order_payments():
    print("--- [5/7] Cleaning Order Payments ---")
    df_pay = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_order_payments_dataset.csv'))
    raw_count = len(df_pay)

    # 1. Xử lý 2 dòng có payment_installments == 0: sửa thành 1
    zero_installments = (df_pay['payment_installments'] == 0)
    df_pay.loc[zero_installments, 'payment_installments'] = 1

    # 2. Chuẩn hóa tên phương thức thanh toán
    df_pay['payment_type'] = df_pay['payment_type'].str.replace('_', ' ').str.title()

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_order_payments_cleaned.csv')
    df_pay.to_csv(out_path, index=False)
    print(f"  -> Saved cleaned payments to: {out_path} ({len(df_pay):,} rows)")

    log_action(
        'Order Payments',
        raw_count,
        len(df_pay),
        "Sửa 2 giá trị payment_installments = 0 thành 1 kỳ; Chuẩn hóa Title Case cho payment_type.",
        "Đảm bảo logic kinh doanh hợp lý (trả góp tối thiểu phải là 1 kỳ)."
    )
    return df_pay


def clean_order_items():
    print("--- [6/7] Cleaning Order Items ---")
    df_items = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_order_items_dataset.csv'))
    raw_count = len(df_items)

    # 1. Ép kiểu datetime cho shipping_limit_date
    df_items['shipping_limit_date'] = pd.to_datetime(df_items['shipping_limit_date'], errors='coerce')

    # 2. Tạo cột tổng giá trị dòng hàng = price + freight_value
    df_items['item_total_value'] = (df_items['price'] + df_items['freight_value']).round(2)

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_order_items_cleaned.csv')
    df_items.to_csv(out_path, index=False)
    print(f"  -> Saved cleaned order items to: {out_path} ({len(df_items):,} rows)")

    log_action(
        'Order Items',
        raw_count,
        len(df_items),
        "Ép kiểu datetime cho shipping_limit_date; tính cột tổng giá trị item_total_value.",
        "Hỗ trợ phân tích doanh thu và phí ship ở cấp độ chi tiết sản phẩm."
    )
    return df_items


def clean_orders_and_engineer_features():
    print("--- [7/7] Cleaning Orders & Engineering Delivery Features ---")
    df_orders = pd.read_csv(os.path.join(RAW_DATA_DIR, 'olist_orders_dataset.csv'))
    raw_count = len(df_orders)

    # 1. Ép kiểu timestamp an toàn
    date_cols = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        df_orders[col] = pd.to_datetime(df_orders[col], errors='coerce')

    # 2. Tạo các tính năng thời gian (Time Features)
    df_orders['purchase_year'] = df_orders['order_purchase_timestamp'].dt.year
    df_orders['purchase_month'] = df_orders['order_purchase_timestamp'].dt.month
    df_orders['purchase_year_month'] = df_orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
    df_orders['purchase_dayofweek'] = df_orders['order_purchase_timestamp'].dt.day_name()
    df_orders['purchase_hour'] = df_orders['order_purchase_timestamp'].dt.hour

    # 3. Tính toán các chỉ số giao hàng chính (Delivery Performance Metrics)
    # Thời gian giao hàng thực tế (ngày)
    df_orders['actual_delivery_days'] = (
        (df_orders['order_delivered_customer_date'] - df_orders['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    ).round(2)

    # Thời gian ước tính giao hàng (ngày)
    df_orders['estimated_delivery_days'] = (
        (df_orders['order_estimated_delivery_date'] - df_orders['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    ).round(2)

    # Số ngày chênh lệch giao hàng (dương = trễ, âm = sớm hơn dự kiến)
    df_orders['delivery_delay_days'] = (
        (df_orders['order_delivered_customer_date'] - df_orders['order_estimated_delivery_date']).dt.total_seconds() / 86400.0
    ).round(2)

    # Thời gian seller chuẩn bị hàng giao cho bên vận chuyển (ngày)
    df_orders['seller_dispatch_days'] = (
        (df_orders['order_delivered_carrier_date'] - df_orders['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    ).round(2)

    # Thời gian vận chuyển từ nhà xe đến khách (ngày)
    df_orders['carrier_delivery_days'] = (
        (df_orders['order_delivered_customer_date'] - df_orders['order_delivered_carrier_date']).dt.total_seconds() / 86400.0
    ).round(2)

    # 4. Gắn cờ trạng thái giao hàng (Delivery Status Flag)
    # is_delayed = 1 nếu giao trễ (> 0 ngày) đối với đơn hàng đã giao thành công
    df_orders['is_delayed'] = np.where(
        (df_orders['order_status'] == 'delivered') & (df_orders['delivery_delay_days'] > 0),
        1,
        0
    )

    # Flag đơn hàng thành công hợp lệ có đầy đủ ngày giao
    df_orders['is_valid_delivered'] = np.where(
        (df_orders['order_status'] == 'delivered') & (df_orders['order_delivered_customer_date'].notna()),
        1,
        0
    )

    # Nhóm thời gian giao hàng (Delivery Buckets) để phân tích trực quan
    def get_delay_bucket(days):
        if pd.isna(days):
            return 'Not Delivered'
        elif days <= 0:
            return 'On Time / Early'
        elif days <= 3:
            return '1-3 Days Late'
        elif days <= 7:
            return '4-7 Days Late'
        else:
            return '> 7 Days Late'

    df_orders['delay_bucket'] = df_orders['delivery_delay_days'].apply(get_delay_bucket)

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_orders_cleaned.csv')
    df_orders.to_csv(out_path, index=False)
    print(f"  -> Saved cleaned orders to: {out_path} ({len(df_orders):,} rows)")

    log_action(
        'Orders',
        raw_count,
        len(df_orders),
        "Ép kiểu 5 cột datetime; sinh feature thời gian (actual_delivery_days, delivery_delay_days, is_delayed, seller_dispatch_days, delay_bucket).",
        "Tạo các metrics cốt lõi để trả lời trực tiếp các câu hỏi bài toán kinh doanh về Delivery Performance & Customer Satisfaction."
    )
    return df_orders


def build_master_analytical_dataset(df_orders, df_items, df_prods, df_cust, df_sellers, df_reviews):
    print("--- [BONUS] Building Master Analytical Dataset (Fact Order Details) ---")
    
    # 1. Bắt đầu từ bảng order_items (grain: 1 dòng = 1 item)
    master = df_items.merge(
        df_orders[[
            'order_id', 'customer_id', 'order_status', 'order_purchase_timestamp',
            'purchase_year', 'purchase_month', 'purchase_year_month', 'purchase_dayofweek',
            'actual_delivery_days', 'estimated_delivery_days', 'delivery_delay_days',
            'is_delayed', 'is_valid_delivered', 'delay_bucket', 'seller_dispatch_days', 'carrier_delivery_days'
        ]],
        on='order_id',
        how='inner'
    )

    # 2. Join sản phẩm (lấy category tiếng Anh)
    master = master.merge(
        df_prods[['product_id', 'product_category_formatted', 'product_weight_g']],
        on='product_id',
        how='left'
    )

    # 3. Join khách hàng (lấy customer_unique_id, state, city)
    master = master.merge(
        df_cust[['customer_id', 'customer_unique_id', 'customer_state', 'customer_city']],
        on='customer_id',
        how='left'
    )

    # 4. Join người bán (lấy seller_state, seller_city)
    master = master.merge(
        df_sellers[['seller_id', 'seller_state', 'seller_city']],
        on='seller_id',
        how='left'
    )

    # 5. Join đánh giá (1 order = 1 review sau khi đã deduplicate)
    master = master.merge(
        df_reviews[['order_id', 'review_score', 'satisfaction_tier', 'has_comment']],
        on='order_id',
        how='left'
    )

    # 6. Tính toán cờ liên bang (Is Interstate: Seller và Customer khác bang nhau)
    master['is_interstate'] = (master['customer_state'] != master['seller_state']).astype(int)

    out_path = os.path.join(PROCESSED_DATA_DIR, 'olist_master_analytical_dataset.csv')
    master.to_csv(out_path, index=False)
    print(f"  -> Saved master analytical dataset to: {out_path} ({len(master):,} rows, {len(master.columns)} columns)")

    log_action(
        'Master Analytical Dataset',
        len(df_items),
        len(master),
        f"Denormalize sạch tích hợp 6 bảng (Items + Orders + Products + Customers + Sellers + Reviews) tại grain 1 item/dòng; thêm cờ is_interstate.",
        "File phân tích all-in-one phục vụ trực tiếp cho Exploratory Data Analysis (EDA) và xây dựng Dashboard Power BI mà không lo bị nhân dòng."
    )
    return master


# ==========================================
# 3. GENERATE CLEANING LOG REPORT
# ==========================================
def generate_cleaning_log_report():
    print("--- Generating Documentation: docs/05_data_cleaning_log.md ---")
    df_log = pd.DataFrame(cleaning_log)
    
    # Save CSV summary
    csv_path = os.path.join(OUTPUT_TABLES_DIR, 'data_cleaning_summary.csv')
    df_log.to_csv(csv_path, index=False)
    print(f"  -> Saved summary CSV to: {csv_path}")

    # Generate Markdown documentation
    md = "# DATA CLEANING & TRANSFORMATION LOG\n\n"
    md += "> Tài liệu này ghi lại chi tiết các bước xử lý, làm sạch và chuẩn hóa dữ liệu từ `data/raw/` sang `data/processed/`.\n"
    md += "> Được tạo tự động bởi pipeline `src/03_data_cleaning.py`.\n\n"
    md += "## 1. Summary of Cleaning Actions\n\n"
    md += "| Table | Raw Rows | Cleaned Rows | Rows Delta | Actions Taken | Business Justification |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for _, row in df_log.iterrows():
        md += f"| **{row['Table']}** | {row['Raw Rows']} | {row['Cleaned Rows']} | {row['Rows Delta']} | {row['Actions Taken']} | {row['Business Justification']} |\n"

    md += "\n## 2. Key Data Engineering Highlights\n\n"
    md += "1. **Triệt tiêu nhân dòng (Zero Row Multiplication):** Bảng Geolocation (hơn 1 triệu dòng) được gom nhóm (aggregate) theo 19,015 zip code duy nhất với giá trị tọa độ trung vị (median). Bảng Review được lọc giữ lại review mới nhất cho mỗi order.\n"
    md += "2. **Giải quyết dứt điểm bản dịch thiếu:** Đã bổ sung bản dịch tiếng Anh cho `pc_gamer` và `portateis_cozinha_e_preparadores_de_alimentos` theo đúng cam kết trong Business Problem.\n"
    md += "3. **Feature Engineering sẵn sàng cho Business Questions:** Đã tính toán chuẩn hóa `actual_delivery_days`, `delivery_delay_days`, `is_delayed`, `delay_bucket`, `is_interstate` để phục vụ trực tiếp phân tích tương quan giữa giao hàng trễ và điểm hài lòng khách hàng.\n"
    md += "4. **Master Dataset:** Tạo bảng tích hợp `olist_master_analytical_dataset.csv` giúp việc kết nối vào Power BI / Jupyter Notebook trở nên cực kỳ thuận tiện và an toàn.\n"

    doc_path = os.path.join(DOCS_DIR, '05_data_cleaning_log.md')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"  -> Created cleaning log markdown: {doc_path}")


# ==========================================
# 4. MAIN PIPELINE
# ==========================================
def main():
    print("="*60)
    print("STARTING PHASE 4: DATA CLEANING & TRANSFORMATION")
    print("="*60)

    df_prods = clean_products_and_translations()
    df_geo = clean_geolocation()
    df_cust, df_sellers = clean_customers_and_sellers()
    df_reviews = clean_order_reviews()
    df_pay = clean_order_payments()
    df_items = clean_order_items()
    df_orders = clean_orders_and_engineer_features()

    build_master_analytical_dataset(df_orders, df_items, df_prods, df_cust, df_sellers, df_reviews)
    generate_cleaning_log_report()

    print("\n" + "="*60)
    print("PHASE 4 COMPLETED SUCCESSFULLY! ALL CLEANED DATA IN: data/processed/")
    print("="*60)

if __name__ == "__main__":
    main()
