import os
import pandas as pd
import numpy as np
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Tự động lấy đường dẫn tuyệt đối đến thư mục gốc của project (thư mục cha của 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')

EXPECTED_FILES = [
    'olist_customers_dataset.csv',
    'olist_geolocation_dataset.csv',
    'olist_order_items_dataset.csv',
    'olist_order_payments_dataset.csv',
    'olist_order_reviews_dataset.csv',
    'olist_orders_dataset.csv',
    'olist_products_dataset.csv',
    'olist_sellers_dataset.csv',
    'product_category_name_translation.csv'
]

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def check_file_existence(directory, files):
    print("="*60)
    print("STEP 1: CHECKING FILE EXISTENCE")
    print("="*60)
    print(f"Checking directory: {directory}\n")
    
    missing_files = []
    for file in files:
        path = os.path.join(directory, file)
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"[OK] {file} ({size_mb:.2f} MB)")
        else:
            print(f"[MISSING] {file}")
            missing_files.append(file)
    
    if missing_files:
        raise FileNotFoundError(f"Missing files: {missing_files}")
    print("\nAll required raw files are present.\n")

def audit_dataframe(filepath, filename):
    """Đọc file và trả về thông tin audit cơ bản."""
    df = pd.read_csv(filepath)
    
    # Kiểm tra duplicates dựa trên toàn bộ row
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_values = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    return {
        'file_name': filename,
        'rows': total_rows,
        'columns': total_cols,
        'missing_values': missing_values,
        'duplicate_rows': duplicate_rows,
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024**2)
    }

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Check files
    check_file_existence(RAW_DATA_DIR, EXPECTED_FILES)
    
    # Step 2: Audit each dataframe
    print("="*60)
    print("STEP 2: AUDITING DATAFRAMES")
    print("="*60)
    
    audit_results = []
    
    for file in EXPECTED_FILES:
        filepath = os.path.join(RAW_DATA_DIR, file)
        print(f"Processing: {file}...")
        
        try:
            result = audit_dataframe(filepath, file)
            audit_results.append(result)
            print(f"  -> Rows: {result['rows']:,} | Cols: {result['columns']} | Missing: {result['missing_values']:,} | Duplicates: {result['duplicate_rows']:,}")
        except Exception as e:
            print(f"  -> ERROR reading {file}: {e}")
            
    # Step 3: Save audit summary
    audit_df = pd.DataFrame(audit_results)
    summary_path = os.path.join(OUTPUT_DIR, 'audit_summary.csv')
    audit_df.to_csv(summary_path, index=False)
    print(f"\nAudit summary saved to: {summary_path}")
    
    print("\n" + "="*60)
    print("PHASE 0 AUDIT COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    main()