import os
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. Lùi 1 cấp ra khỏi thư mục src để về thư mục gốc dự án
FILE_DIR = os.path.dirname(os.path.abspath(__file__))  # Thư mục src
BASE_DIR = os.path.dirname(FILE_DIR)                  # Thư mục gốc dự án

ITEMS_PATH = os.path.join(BASE_DIR, "data", "raw", "olist_order_items_dataset.csv")
PAYMENTS_PATH = os.path.join(BASE_DIR, "data", "raw", "olist_order_payments_dataset.csv")

# 2. Đọc dữ liệu
df_order_items = pd.read_csv(ITEMS_PATH)
df_order_payments = pd.read_csv(PAYMENTS_PATH)

# 3. Hàm kiểm tra Composite Primary Key
def check_composite_pk(df, col_list, table_name):
    has_nulls = df[col_list].isnull().any().any()
    duplicate_count = df.duplicated(subset=col_list).sum()
    
    print(f"\n=== KIỂM TRA BẢNG: {table_name} ===")
    print(f"Cụm cột kiểm tra: {col_list}")
    print(f"- Có ô Null không?: {has_nulls}")
    print(f"- Số dòng trùng lặp: {duplicate_count}")
    
    if not has_nulls and duplicate_count == 0:
        print("=> KẾT LUẬN: Cụm cột này LÀ Khóa chính ghép (Composite PK) chuẩn 100%!\n")
    else:
        print("=> KẾT LUẬN: KHÔNG thể làm Khóa chính ghép.\n")

# 4. Thực thi kiểm tra
check_composite_pk(df_order_items, ['order_id', 'order_item_id'], "Order Items")
check_composite_pk(df_order_payments, ['order_id', 'payment_sequential'], "Order Payments")