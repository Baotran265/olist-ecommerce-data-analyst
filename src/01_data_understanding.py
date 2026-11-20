import os
import sys
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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

    # Load all dataframes (sắp xếp tên file để thứ tự bảng trong tài liệu ổn định)
    dfs = {}
    for file in sorted(os.listdir(RAW_DATA_DIR)):
        if file.endswith('.csv'):
            dfs[file] = pd.read_csv(os.path.join(RAW_DATA_DIR, file))

    # --- GENERATE 01_data_dictionary.md ---
    md_content = "# TỪ ĐIỂN DỮ LIỆU DỰ ÁN (DATA DICTIONARY)\n\n"
    md_content += f"> Tài liệu này mô tả chi tiết từ điển dữ liệu, ý nghĩa nghiệp vụ, cấu trúc grain và kiểu dữ liệu của {len(dfs)} bảng dữ liệu Olist.\n"
    md_content += "> Được sinh ra từ quy trình khám phá dữ liệu `src/01_data_understanding.py`.\n\n"

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
    md_rel = "# QUAN HỆ DỮ LIỆU & KIỂM TOÁN TÍNH TOÀN VẸN (DATA RELATIONSHIPS & INTEGRITY CHECK)\n\n"
    md_rel += "> Kết quả kiểm tra tính toàn vẹn tham chiếu (Referential Integrity) giữa các bảng trong cơ sở dữ liệu.\n\n"

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

    md_rel += "## 1. Kiểm toán Toàn vẹn Tham chiếu (Referential Integrity Checks)\n\n"
    md_rel += "| Bảng con (Child Table) | Khóa ngoại (FK) | Bảng cha (Parent Table) | Khóa chính (PK) | Tổng số khóa con | Thiếu ở bảng cha | Trạng thái |\n"
    md_rel += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

    for child_file, child_col, parent_file, parent_col in relationships:
        if child_file in dfs and parent_file in dfs:
            res = check_referential_integrity(dfs[child_file], child_col, dfs[parent_file], parent_col)
            if res['is_valid']:
                status = "✅ HỢP LỆ (VALID)"
            elif parent_file == 'product_category_name_translation.csv':
                status = "⚠️ THIẾU BẢN DỊCH (Xử lý bổ sung ở Phase 4)"
            else:
                status = "⚠️ PHÁT HIỆN BẢN GHI MỒ CÔI (ORPHAN)"
            md_rel += f"| {child_file} | {child_col} | {parent_file} | {parent_col} | {res['total_source_keys']:,} | {res['missing_in_target']:,} | {status} |\n"

    md_rel += "\n## 2. Cảnh báo Nghiệp vụ về Grain & Rủi ro Nhân dòng (Critical Grain Warnings)\n\n"
    md_rel += "1. **Bảng Địa lý (Geolocation):** Bảng `olist_geolocation_dataset` có grain là **1 dòng = 1 điểm tọa độ**. Một `geolocation_zip_code_prefix` có thể xuất hiện **nhiều lần** (nhiều cặp lat/lng khác nhau cho cùng một mã zip code). \n"
    md_rel += "   - **Rủi ro:** Nếu liên kết trực tiếp bảng này với `customers` hoặc `sellers` qua zip code mà không khử trùng lặp, sẽ gây ra **LỖI NHÂN DÒNG (Row Multiplication)** làm sai lệch hoàn toàn số liệu doanh thu và sản lượng.\n"
    md_rel += "   - **Giải pháp:** Gom nhóm (aggregate) bảng Geolocation theo từng zip code duy nhất với giá trị tọa độ trung vị (median) ở Phase 4 trước khi tích hợp vào Dimension tables.\n\n"
    md_rel += "2. **Các bảng chi tiết (Order Items / Payments / Reviews):** Các bảng này có grain chi tiết hơn bảng `orders` (1 đơn hàng có thể chứa nhiều sản phẩm, nhiều kỳ thanh toán hoặc không có đánh giá).\n"
    md_rel += "   - **Rủi ro:** Thực hiện phép kết nối (JOIN) ngang giữa 3 bảng này sẽ dẫn đến tích đề-các (Cross Join) gây nhân dòng nghiêm trọng.\n"
    md_rel += "   - **Giải pháp:** Luôn tổng hợp dữ liệu về đúng grain trước khi liên kết, hoặc phân tách thành Fact Table (Items) và Dimension Tables trong mô hình Kimball Star Schema.\n"

    with open(os.path.join(DOCS_DIR, '02_data_relationships.md'), 'w', encoding='utf-8') as f:
        f.write(md_rel)
    print("Created: docs/02_data_relationships.md")

    print("\nPHASE 1 COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    main()
