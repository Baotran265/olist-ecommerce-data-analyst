import os
import pandas as pd
import numpy as np

# ==========================================
# 1. CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

os.makedirs(DOCS_DIR, exist_ok=True)

# Danh sách các bảng và thông tin ngữ nghĩa business (Business Context)
TABLE_INFO = {
    'olist_orders_dataset.csv': {
        'name': 'Orders',
        'purpose': 'Lưu trữ thông tin chính của đơn hàng, trạng thái và các mốc thời gian.',
        'business_meaning': 'Mỗi dòng đại diện cho một đơn hàng (order) được đặt trên platform.'
    },
    'olist_customers_dataset.csv': {
        'name': 'Customers',
        'purpose': 'Lưu trữ thông tin định danh và địa chỉ của khách hàng.',
        'business_meaning': 'Mỗi dòng là một customer_id duy nhất. Lưu ý: một người (unique_id) có thể có nhiều customer_id nếu dùng nhiều tài khoản/địa chỉ.'
    },
    'olist_sellers_dataset.csv': {
        'name': 'Sellers',
        'purpose': 'Lưu trữ thông tin định danh và địa chỉ của người bán.',
        'business_meaning': 'Mỗi dòng là một seller_id duy nhất.'
    },
    'olist_products_dataset.csv': {
        'name': 'Products',
        'purpose': 'Lưu trữ thông tin chi tiết về sản phẩm (kích thước, trọng lượng, category).',
        'business_meaning': 'Mỗi dòng là một product_id duy nhất.'
    },
    'olist_order_items_dataset.csv': {
        'name': 'Order Items',
        'purpose': 'Lưu trữ chi tiết từng sản phẩm trong đơn hàng, giá bán và phí vận chuyển.',
        'business_meaning': 'Grain: 1 dòng = 1 sản phẩm (item) trong 1 đơn hàng. Một order có thể có nhiều dòng.'
    },
    'olist_order_payments_dataset.csv': {
        'name': 'Order Payments',
        'purpose': 'Lưu trữ thông tin thanh toán của đơn hàng.',
        'business_meaning': 'Grain: 1 dòng = 1 phương thức thanh toán cho 1 đơn hàng. Một order có thể trả nhiều lần (installments) hoặc dùng nhiều phương thức.'
    },
    'olist_order_reviews_dataset.csv': {
        'name': 'Order Reviews',
        'purpose': 'Lưu trữ đánh giá và phản hồi của khách hàng sau khi nhận hàng.',
        'business_meaning': 'Grain: 1 dòng = 1 đánh giá cho 1 đơn hàng. Không phải order nào cũng có review.'
    },
    'olist_geolocation_dataset.csv': {
        'name': 'Geolocation',
        'purpose': 'Ánh xạ zip code prefix với tọa độ địa lý (lat/lng) và thành phố.',
        'business_meaning': 'Grain: KHÔNG PHẢI 1 zip code = 1 dòng. Một zip code có thể có nhiều điểm tọa độ (nhiều dòng). Bảng này rất nặng và dễ gây nhân dòng khi join.'
    },
    'product_category_name_translation.csv': {
        'name': 'Product Category Translation',
        'purpose': 'Dịch tên category từ tiếng Bồ Đào Nha sang tiếng Anh.',
        'business_meaning': 'Bảng mapping 1-1 giữa category gốc và category tiếng Anh.'
    }
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_table_stats(df):
    """Tính toán các thống kê cơ bản của DataFrame."""
    total_rows = len(df)
    total_cols = len(df.columns)
    missing = df.isnull().sum().to_dict()
    
    # Tìm candidate Primary Key (cột có số unique = total_rows và không có missing)
    pk_candidates = []
    for col in df.columns:
        unique_count = df[col].nunique()
        missing_count = df[col].isnull().sum()
        if unique_count == total_rows and missing_count == 0:
            pk_candidates.append(col)
            
    return {
        'rows': total_rows,
        'cols': total_cols,
        'missing': missing,
        'pk_candidates': pk_candidates,
        'dtypes': df.dtypes.astype(str).to_dict()
    }

def check_referential_integrity(df_source, col_source, df_target, col_target):
    """
    Kiểm tra xem các khóa ở bảng nguồn (Foreign Key - Bảng con) 
    có tồn tại ở bảng đích (Primary Key - Bảng cha) không.
    """
    source_values = set(df_source[col_source].dropna().unique())
    target_values = set(df_target[col_target].dropna().unique())
    
    missing_in_target = source_values - target_values
    return {
        'total_source_keys': len(source_values),
        'missing_in_target': len(missing_in_target),
        'is_valid': len(missing_in_target) == 0
    }

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    print("Starting Phase 1: Data Understanding...")
    
    # Load all dataframes
    dfs = {}
    for file in os.listdir(RAW_DATA_DIR):
        if file.endswith('.csv'):
            dfs[file] = pd.read_csv(os.path.join(RAW_DATA_DIR, file))
            
    # --- GENERATE 01_data_dictionary.md ---
    md_content = "# DATA DICTIONARY\n\n"
    md_content += "> File này được tự động sinh ra từ `src/01_data_understanding.py` dựa trên dữ liệu thực tế.\n\n"
    
    for file, df in dfs.items():
        info = TABLE_INFO.get(file, {'name': file.replace('.csv', ''), 'purpose': 'N/A', 'business_meaning': 'N/A'})
        stats = get_table_stats(df)
        
        md_content += f"## {info['name']} (`{file}`)\n\n"
        md_content += f"- **Purpose:** {info['purpose']}\n"
        md_content += f"- **Business Meaning / Grain:** {info['business_meaning']}\n"
        md_content += f"- **Total Rows:** {stats['rows']:,}\n"
        md_content += f"- **Total Columns:** {stats['cols']}\n"
        md_content += f"- **Primary Key Candidate(s):** {', '.join(stats['pk_candidates']) if stats['pk_candidates'] else 'None (Composite key or no unique ID)'}\n\n"
        
        md_content += "### Columns & Data Types\n\n"
        md_content += "| Column Name | Data Type | Missing Values | % Missing |\n"
        md_content += "| :--- | :--- | :--- | :--- |\n"
        for col in df.columns:
            miss = stats['missing'][col]
            pct = (miss / stats['rows']) * 100 if stats['rows'] > 0 else 0
            md_content += f"| {col} | {stats['dtypes'][col]} | {miss:,} | {pct:.2f}% |\n"
        md_content += "\n---\n\n"

    with open(os.path.join(DOCS_DIR, '01_data_dictionary.md'), 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("Created: docs/01_data_dictionary.md")

    # --- GENERATE 02_data_relationships.md ---
    md_rel = "# DATA RELATIONSHIPS & INTEGRITY CHECK\n\n"
    md_rel += "> Kết quả kiểm tra Referential Integrity giữa các bảng.\n\n"
    
    # Define relationships to check (Child/Source -> Parent/Target)
    relationships = [
        ('olist_order_items_dataset.csv', 'order_id', 'olist_orders_dataset.csv', 'order_id'),
        ('olist_order_payments_dataset.csv', 'order_id', 'olist_orders_dataset.csv', 'order_id'),
        ('olist_order_reviews_dataset.csv', 'order_id', 'olist_orders_dataset.csv', 'order_id'),
        ('olist_orders_dataset.csv', 'customer_id', 'olist_customers_dataset.csv', 'customer_id'),
        ('olist_order_items_dataset.csv', 'seller_id', 'olist_sellers_dataset.csv', 'seller_id'),
        ('olist_order_items_dataset.csv', 'product_id', 'olist_products_dataset.csv', 'product_id'),
        ('olist_products_dataset.csv', 'product_category_name', 'product_category_name_translation.csv', 'product_category_name')
    ]
    
    md_rel += "## Referential Integrity Checks\n\n"
    md_rel += "| Child Table (Source) | Foreign Key | Parent Table (Target) | Primary Key | Total Child Keys | Missing in Parent | Status |\n"
    md_rel += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for child_file, child_col, parent_file, parent_col in relationships:
        if child_file in dfs and parent_file in dfs:
            # GỌI HÀM VÀ LẤY KEY ĐÚNG: total_source_keys và missing_in_target
            res = check_referential_integrity(dfs[child_file], child_col, dfs[parent_file], parent_col)
            status = "✅ VALID" if res['is_valid'] else "⚠️ ORPHAN RECORDS FOUND"
            md_rel += f"| {child_file} | {child_col} | {parent_file} | {parent_col} | {res['total_source_keys']:,} | {res['missing_in_target']:,} | {status} |\n"
            
    md_rel += "\n## Critical Grain Warnings\n\n"
    md_rel += "1. **Geolocation Table:** Bảng `olist_geolocation_dataset` có grain là **1 dòng = 1 điểm tọa độ**. Một `geolocation_zip_code_prefix` có thể xuất hiện **nhiều lần** (nhiều lat/lng khác nhau cho cùng 1 zip code). \n"
    md_rel += "   - **Rủi ro:** Nếu join trực tiếp bảng này với `customers` hoặc `sellers` qua zip code, sẽ gây ra **ROW MULTIPLICATION** (nhân dòng) làm sai lệch hoàn toàn số liệu.\n"
    md_rel += "   - **Giải pháp:** Chỉ sử dụng bảng này để lấy thông tin city/state nếu cần, hoặc phải group by zip code trước khi join.\n\n"
    md_rel += "2. **Order Items / Payments / Reviews:** Các bảng này có grain nhỏ hơn bảng `orders` (1 order có nhiều items, nhiều payments, hoặc không có review).\n"
    md_rel += "   - **Rủi ro:** Join cả 3 bảng này lại với nhau sẽ gây ra **CROSS JOIN / ROW MULTIPLICATION** nghiêm trọng.\n"
    md_rel += "   - **Giải pháp:** Luôn aggregate (group by order_id) các bảng con này về grain của `orders` trước khi join, hoặc xây dựng Fact table riêng biệt.\n"

    with open(os.path.join(DOCS_DIR, '02_data_relationships.md'), 'w', encoding='utf-8') as f:
        f.write(md_rel)
    print("Created: docs/02_data_relationships.md")
    
    print("\nPHASE 1 COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    main()