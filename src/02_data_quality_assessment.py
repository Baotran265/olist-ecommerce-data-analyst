import os
import sys
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
OUTPUT_TABLES_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(OUTPUT_TABLES_DIR, exist_ok=True)

# Thứ tự bảng trong báo cáo (các bảng khác, nếu có, được xử lý sau)
TABLE_ORDER = [
    'olist_geolocation_dataset.csv',
    'olist_orders_dataset.csv',
    'olist_order_payments_dataset.csv',
    'olist_order_reviews_dataset.csv',
    'olist_products_dataset.csv',
]

# Quy tắc xử lý riêng cho từng cột khuyết: (mức độ, phương án xử lý, căn cứ nghiệp vụ)
MISSING_RULES = {
    ('olist_orders_dataset.csv', 'order_approved_at'):
        ('Trung bình', 'Giữ NaT, kiểm soát qua cờ hợp lệ ở Phase 4', 'Dữ liệu khuyết có thể làm méo mó phép gom nhóm'),
    ('olist_orders_dataset.csv', 'order_delivered_carrier_date'):
        ('Trung bình', 'Giữ NaT, kiểm soát qua cờ hợp lệ ở Phase 4', 'Cần thiết để tính thời gian bàn giao của seller'),
    ('olist_orders_dataset.csv', 'order_delivered_customer_date'):
        ('Trung bình', 'Lọc đơn chưa giao ở phân tích SLA', 'Không thể tính thời gian giao cho đơn chưa hoàn tất'),
    ('olist_order_reviews_dataset.csv', 'review_comment_title'):
        ('Cao (High)', 'Giữ nguyên, phân tích flag has_comment', 'Khách hàng thường chỉ chấm sao mà không viết tiêu đề'),
    ('olist_products_dataset.csv', 'product_category_name'):
        ('Trung bình', "Điền nhãn 'Unknown' ở Phase 4", 'Tránh mất dòng sản phẩm khi phân tích'),
    ('olist_products_dataset.csv', 'product_name_lenght'):
        ('Thấp', 'Giữ nguyên (cột không dùng trong phân tích, không đưa vào dim_products)', 'Bổ trợ thuộc tính sản phẩm'),
    ('olist_products_dataset.csv', 'product_description_lenght'):
        ('Thấp', 'Giữ nguyên (cột không dùng trong phân tích, không đưa vào dim_products)', 'Bổ trợ thuộc tính sản phẩm'),
    ('olist_products_dataset.csv', 'product_photos_qty'):
        ('Thấp', 'Điền giá trị trung vị (median)', 'Bổ trợ thuộc tính sản phẩm'),
    ('olist_products_dataset.csv', 'product_weight_g'):
        ('Thấp', 'Điền giá trị trung vị (median)', 'Cần thiết để tính toán logistics'),
    ('olist_products_dataset.csv', 'product_length_cm'):
        ('Thấp', 'Điền giá trị trung vị (median)', 'Cần thiết để tính toán logistics'),
    ('olist_products_dataset.csv', 'product_height_cm'):
        ('Thấp', 'Điền giá trị trung vị (median)', 'Cần thiết để tính toán logistics'),
    ('olist_products_dataset.csv', 'product_width_cm'):
        ('Thấp', 'Điền giá trị trung vị (median)', 'Cần thiết để tính toán logistics'),
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def load_data():
    """Load tất cả các file CSV vào một dictionary."""
    dfs = {}
    for file in sorted(os.listdir(RAW_DATA_DIR)):
        if file.endswith('.csv'):
            dfs[file] = pd.read_csv(os.path.join(RAW_DATA_DIR, file))
    return dfs

def check_missing_and_duplicates(df, table_name, report_data):
    """Kiểm tra missing values và duplicate rows toàn diện."""
    total_rows = len(df)

    # Missing values (Loại trừ review_comment_message vì không phải lỗi bắt buộc)
    for col in df.columns:
        if col == 'review_comment_message':
            continue
        missing = df[col].isnull().sum()
        if missing > 0:
            pct = missing / total_rows
            default_sev = 'Cao (High)' if pct > 0.05 else 'Trung bình'
            sev, treatment, reason = MISSING_RULES.get(
                (table_name, col),
                (default_sev, 'Điều tra ở Phase 4 (fillna / flag)',
                 'Dữ liệu khuyết có thể làm méo mó phép gom nhóm')
            )
            report_data.append({
                'Table': table_name,
                'Column': col,
                'Issue': 'Khuyết dữ liệu (Missing)',
                'Affected Rows': int(missing),
                'Percentage': f"{pct * 100:.2f}%",
                'Severity': sev,
                'Proposed Treatment': treatment,
                'Reason': reason
            })

    # Full row duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        is_geo = table_name == 'olist_geolocation_dataset.csv'
        report_data.append({
            'Table': table_name,
            'Column': 'Toàn bộ các cột',
            'Issue': 'Dòng trùng lặp 100%',
            'Affected Rows': int(dupes),
            'Percentage': f"{(dupes / total_rows) * 100:.2f}%",
            'Severity': 'Cao (High)',
            'Proposed Treatment': 'Lọc bỏ trùng lặp ở Phase 4',
            'Reason': 'Tránh nhân dòng khi liên kết dữ liệu địa lý' if is_geo
                      else 'Dòng trùng lặp gây đếm trùng khi phân tích'
        })

def check_date_logic(dfs, report_data):
    """Kiểm tra logic ngày tháng và các giá trị cực trị thời gian."""
    if 'olist_orders_dataset.csv' not in dfs:
        return

    df_orders = dfs['olist_orders_dataset.csv'].copy()
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    df_orders['order_delivered_customer_date'] = pd.to_datetime(df_orders['order_delivered_customer_date'])

    # 1. Ngày giao hàng < Ngày mua hàng
    delivered = df_orders[df_orders['order_status'] == 'delivered'].copy()
    impossible_dates = delivered[delivered['order_delivered_customer_date'] < delivered['order_purchase_timestamp']]

    if len(impossible_dates) > 0:
        report_data.append({
            'Table': 'olist_orders_dataset.csv',
            'Column': 'order_delivered_customer_date',
            'Issue': 'Ngày không hợp lệ (Giao hàng < Mua hàng)',
            'Affected Rows': len(impossible_dates),
            'Percentage': f"{(len(impossible_dates) / len(delivered)) * 100:.4f}%",
            'Severity': 'Nghiêm trọng (Critical)',
            'Proposed Treatment': 'Gắn cờ hoặc lọc bỏ ở Phase 4',
            'Reason': 'Vi phạm logic thứ tự thời gian cơ bản'
        })

    # 2. Extreme Delivery Delays (> 90 days)
    delivered['delivery_days'] = (delivered['order_delivered_customer_date'] - delivered['order_purchase_timestamp']).dt.days
    extreme_delays = delivered[delivered['delivery_days'] > 90]
    if len(extreme_delays) > 0:
        report_data.append({
            'Table': 'olist_orders_dataset.csv',
            'Column': 'delivery_days',
            'Issue': 'Ngoại lai thời gian giao (> 90 ngày)',
            'Affected Rows': len(extreme_delays),
            'Percentage': f"{(len(extreme_delays) / len(delivered)) * 100:.2f}%",
            'Severity': 'Trung bình',
            'Proposed Treatment': 'Giữ nguyên và dùng trung vị/phân đoạn',
            'Reason': 'Phản ánh các sự cố giao hàng thực tế'
        })

def check_monetary_values(table_name, df, report_data):
    """Kiểm tra giá trị âm và số 0 bất thường trong tiền tệ."""
    monetary_cols = ['price', 'freight_value', 'payment_value']
    zero_labels = {'price': 'Giá bán bằng 0', 'payment_value': 'Giá trị thanh toán bằng 0'}
    for col in monetary_cols:
        if col in df.columns:
            # Giá trị âm
            negative_vals = df[df[col] < 0]
            if len(negative_vals) > 0:
                report_data.append({
                    'Table': table_name,
                    'Column': col,
                    'Issue': 'Giá trị tiền tệ âm',
                    'Affected Rows': len(negative_vals),
                    'Percentage': f"{(len(negative_vals) / len(df)) * 100:.2f}%",
                    'Severity': 'Nghiêm trọng (Critical)',
                    'Proposed Treatment': 'Điều tra & lọc bỏ ở Phase 4',
                    'Reason': 'Doanh thu/thanh toán âm là vô lý về mặt logic'
                })

            # Giá trị bằng 0 (Loại trừ freight_value vì Free Shipping là chính sách business hợp lệ)
            if col in zero_labels:
                zero_vals = df[df[col] == 0]
                if len(zero_vals) > 0:
                    report_data.append({
                        'Table': table_name,
                        'Column': col,
                        'Issue': zero_labels[col],
                        'Affected Rows': len(zero_vals),
                        'Percentage': f"{(len(zero_vals) / len(df)) * 100:.4f}%",
                        'Severity': 'Thấp',
                        'Proposed Treatment': 'Điều tra đơn giảm giá / đơn thử nghiệm',
                        'Reason': 'Đơn giá trị 0 ảnh hưởng đến tính toán AOV'
                    })

def check_review_score(df, report_data):
    """Kiểm tra review score có nằm trong khoảng 1-5 không."""
    if 'review_score' in df.columns:
        invalid_scores = df[(df['review_score'] < 1) | (df['review_score'] > 5)]
        if len(invalid_scores) > 0:
            report_data.append({
                'Table': 'olist_order_reviews_dataset.csv',
                'Column': 'review_score',
                'Issue': 'Điểm đánh giá không hợp lệ (ngoài khoảng 1-5)',
                'Affected Rows': len(invalid_scores),
                'Percentage': f"{(len(invalid_scores) / len(df)) * 100:.2f}%",
                'Severity': 'Nghiêm trọng (Critical)',
                'Proposed Treatment': 'Loại trừ hoặc điều tra ở Phase 4',
                'Reason': 'Điểm đánh giá bắt buộc nằm trong khoảng 1 đến 5'
            })

def check_cross_table_integrity(dfs, report_data):
    """Kiểm tra tính toàn vẹn giữa các bảng (Orphan Records & Translation)."""
    if 'olist_orders_dataset.csv' in dfs and 'olist_order_items_dataset.csv' in dfs:
        orders_set = set(dfs['olist_orders_dataset.csv']['order_id'])
        items_orders_set = set(dfs['olist_order_items_dataset.csv']['order_id'])
        orphan_orders = orders_set - items_orders_set

        if len(orphan_orders) > 0:
            report_data.append({
                'Table': 'olist_orders_dataset.csv',
                'Column': 'order_id',
                'Issue': f'Đơn hàng không có sản phẩm ({len(orphan_orders):,} đơn)',
                'Affected Rows': len(orphan_orders),
                'Percentage': f"{(len(orphan_orders) / len(orders_set)) * 100:.2f}%",
                'Severity': 'Cao (High)',
                'Proposed Treatment': 'Loại trừ khỏi phân tích doanh thu sản phẩm',
                'Reason': 'Đơn bị hủy trước khi tạo item record'
            })

    # Kiểm tra thiếu bản dịch tiếng Anh
    if 'olist_products_dataset.csv' in dfs and 'product_category_name_translation.csv' in dfs:
        prod_cats = set(dfs['olist_products_dataset.csv']['product_category_name'].dropna())
        trans_cats = set(dfs['product_category_name_translation.csv']['product_category_name'])
        unmapped_cats = prod_cats - trans_cats

        if len(unmapped_cats) > 0:
            report_data.append({
                'Table': 'olist_products_dataset.csv',
                'Column': 'product_category_name',
                'Issue': f'Thiếu bản dịch tiếng Anh ({len(unmapped_cats)} / {len(prod_cats)} danh mục)',
                'Affected Rows': len(unmapped_cats),
                'Percentage': f"{(len(unmapped_cats) / len(prod_cats)) * 100:.2f}% (trên danh mục)",
                'Severity': 'Trung bình',
                'Proposed Treatment': 'Bổ sung dịch thủ công ở Phase 4',
                'Reason': 'Đảm bảo Dashboard hiển thị chuẩn tiếng Anh'
            })

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    print("=== STARTING PHASE 3: DATA QUALITY ASSESSMENT ===")
    dfs = load_data()
    report_data = []

    # 1. Loop per table (theo TABLE_ORDER, các bảng còn lại xử lý sau)
    ordered = [f for f in TABLE_ORDER if f in dfs] + [f for f in dfs if f not in TABLE_ORDER]
    for file in ordered:
        df = dfs[file]
        print(f"Assessing: {file}...")
        check_missing_and_duplicates(df, file, report_data)
        check_monetary_values(file, df, report_data)
        check_review_score(df, report_data)

    # 2. Logic & Cross-table checks
    check_date_logic(dfs, report_data)
    check_cross_table_integrity(dfs, report_data)

    # 3. Save Summary CSV for Data Pipeline
    df_report = pd.DataFrame(report_data)
    csv_out_path = os.path.join(OUTPUT_TABLES_DIR, "data_quality_summary.csv")
    df_report.to_csv(csv_out_path, index=False, encoding='utf-8-sig')
    print(f"\n=> Data Quality CSV saved to: {csv_out_path}")

    # 4. Generate Markdown Report
    md_content = "# BÁO CÁO KIỂM TOÁN CHẤT LƯỢNG DỮ LIỆU (DATA QUALITY REPORT)\n\n"
    md_content += "> Báo cáo này ghi nhận và đánh giá mức độ ảnh hưởng của các vấn đề chất lượng dữ liệu phát hiện trong Phase 3 (`src/02_data_quality_assessment.py`). "
    md_content += "Quy trình tuân thủ nguyên tắc: PHÁT HIỆN (Detect) + ĐÁNH GIÁ (Assess) + LƯU HỒ SƠ (Document).\n\n"

    if not report_data:
        md_content += "✅ **Không phát hiện vấn đề chất lượng dữ liệu đáng kể.**\n"
    else:
        md_content += "| Tên bảng | Tên cột | Vấn đề chất lượng phát hiện | Số dòng ảnh hưởng | Tỷ lệ (%) | Mức độ nghiêm trọng | Phương án xử lý đề xuất | Căn cứ nghiệp vụ |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for row in report_data:
            md_content += f"| {row['Table']} | {row['Column']} | {row['Issue']} | {row['Affected Rows']:,} | {row['Percentage']} | {row['Severity']} | {row['Proposed Treatment']} | {row['Reason']} |\n"

    md_out_path = os.path.join(DOCS_DIR, '04_data_quality_report.md')
    with open(md_out_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"=> Data Quality Report saved to: {md_out_path}")
    print("\n=== PHASE 3 COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
