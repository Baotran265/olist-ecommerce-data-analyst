import os
import pandas as pd
import numpy as np
import sys
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

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def load_data():
    """Load tất cả các file CSV vào một dictionary."""
    dfs = {}
    for file in os.listdir(RAW_DATA_DIR):
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
            report_data.append({
                'Table': table_name,
                'Column': col,
                'Issue': 'Missing Values',
                'Affected Rows': int(missing),
                'Percentage': f"{pct * 100:.2f}%",
                'Severity': 'High' if pct > 0.05 else 'Medium',
                'Proposed Treatment': 'Investigate in Phase 4 (Fillna / Flag)',
                'Reason': 'Missing attribute data can distort group-by aggregations.'
            })

    # Full row duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        report_data.append({
            'Table': table_name,
            'Column': 'All Columns',
            'Issue': 'Duplicate Rows',
            'Affected Rows': int(dupes),
            'Percentage': f"{(dupes / total_rows) * 100:.2f}%",
            'Severity': 'High',
            'Proposed Treatment': 'Drop duplicates in Phase 4',
            'Reason': 'Duplicate rows cause double counting in analysis.'
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
            'Issue': 'Impossible Dates (Delivered < Purchased)',
            'Affected Rows': len(impossible_dates),
            'Percentage': f"{(len(impossible_dates) / len(delivered)) * 100:.4f}%",
            'Severity': 'Critical',
            'Proposed Treatment': 'Flag or Filter Out in Phase 4',
            'Reason': 'Violates basic chronological logic.'
        })
        
    # 2. Extreme Delivery Delays (> 90 days)
    delivered['delivery_days'] = (delivered['order_delivered_customer_date'] - delivered['order_purchase_timestamp']).dt.days
    extreme_delays = delivered[delivered['delivery_days'] > 90]
    if len(extreme_delays) > 0:
        report_data.append({
            'Table': 'olist_orders_dataset.csv',
            'Column': 'delivery_days',
            'Issue': 'Extreme Delivery Outlier (> 90 Days)',
            'Affected Rows': len(extreme_delays),
            'Percentage': f"{(len(extreme_delays) / len(delivered)) * 100:.2f}%",
            'Severity': 'Medium',
            'Proposed Treatment': 'Flag and analyze separately in Phase 6',
            'Reason': 'Extreme outliers skew mean delivery time metrics.'
        })

def check_monetary_values(table_name, df, report_data):
    """Kiểm tra giá trị âm và số 0 bất thường trong tiền tệ."""
    monetary_cols = ['price', 'freight_value', 'payment_value']
    for col in monetary_cols:
        if col in df.columns:
            # Giá trị âm
            negative_vals = df[df[col] < 0]
            if len(negative_vals) > 0:
                report_data.append({
                    'Table': table_name,
                    'Column': col,
                    'Issue': 'Negative Monetary Value',
                    'Affected Rows': len(negative_vals),
                    'Percentage': f"{(len(negative_vals) / len(df)) * 100:.2f}%",
                    'Severity': 'Critical',
                    'Proposed Treatment': 'Investigate & Filter in Phase 4',
                    'Reason': 'Negative revenue/payment is logically invalid.'
                })
            
            # Giá trị bằng 0 (Loại trừ freight_value vì Free Shipping là chính sách business hợp lệ)
            if col in ['price', 'payment_value']:
                zero_vals = df[df[col] == 0]
                if len(zero_vals) > 0:
                    report_data.append({
                        'Table': table_name,
                        'Column': col,
                        'Issue': f'Zero {col.capitalize()} Value',
                        'Affected Rows': len(zero_vals),
                        'Percentage': f"{(len(zero_vals) / len(df)) * 100:.4f}%",
                        'Severity': 'Medium',
                        'Proposed Treatment': 'Investigate potential discounts / test orders',
                        'Reason': 'Zero monetary values distort Average Order Value (AOV).'
                    })

def check_review_score(df, report_data):
    """Kiểm tra review score có nằm trong khoảng 1-5 không."""
    if 'review_score' in df.columns:
        invalid_scores = df[(df['review_score'] < 1) | (df['review_score'] > 5)]
        if len(invalid_scores) > 0:
            report_data.append({
                'Table': 'olist_order_reviews_dataset.csv',
                'Column': 'review_score',
                'Issue': 'Invalid Review Score (Not 1-5)',
                'Affected Rows': len(invalid_scores),
                'Percentage': f"{(len(invalid_scores) / len(df)) * 100:.2f}%",
                'Severity': 'Critical',
                'Proposed Treatment': 'Exclude or investigate in Phase 4',
                'Reason': 'Review score must strictly be bounded between 1 and 5.'
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
                'Issue': 'Orphan Orders (No Items)',
                'Affected Rows': len(orphan_orders),
                'Percentage': f"{(len(orphan_orders) / len(orders_set)) * 100:.2f}%",
                'Severity': 'High',
                'Proposed Treatment': 'Exclude from Revenue analysis / Keep for Order Conversion',
                'Reason': 'Cannot calculate product revenue without order item details.'
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
                'Issue': 'Unmapped English Category Translation',
                'Affected Rows': len(unmapped_cats),
                'Percentage': f"{(len(unmapped_cats) / len(prod_cats)) * 100:.2f}%",
                'Severity': 'Medium',
                'Proposed Treatment': 'Translate manually or assign "Others" based on volume in Phase 4',
                'Reason': 'Missing translation breaks English dashboard categories.'
            })

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    print("=== STARTING PHASE 3: DATA QUALITY ASSESSMENT ===")
    dfs = load_data()
    report_data = []

    # 1. Loop per table
    for file, df in dfs.items():
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
    df_report.to_csv(csv_out_path, index=False)
    print(f"\n=> Data Quality CSV saved to: {csv_out_path}")

    # 4. Generate Markdown Report for GitHub / Hiring Manager
    md_content = "# DATA QUALITY REPORT\n\n"
    md_content += "> Báo cáo này được tự động sinh ra từ `src/02_data_quality_assessment.py`. "
    md_content += "Chỉ ghi nhận và đánh giá mức độ ảnh hưởng của các vấn đề dữ liệu (DETECT + ASSESS + DOCUMENT).\n\n"
    
    if not report_data:
        md_content += "✅ **No major data quality issues found.**\n"
    else:
        md_content += "| Table | Column | Issue | Affected Rows | Percentage | Severity | Proposed Treatment | Reason |\n"
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