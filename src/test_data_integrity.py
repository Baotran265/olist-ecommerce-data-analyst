"""
TEST DATA INTEGRITY & KPI RECONCILIATION
========================================
Kiểm tra tự động tính toàn vẹn của mô hình Star Schema và đối chiếu số liệu KPI.

Các truy vấn KPI được lấy TRỰC TIẾP từ `sql/02_kpi_business_queries.sql` (không viết lại SQL riêng),
chạy trên SQLite, rồi đối chiếu với kết quả tính độc lập bằng pandas từ master dataset.
"""

import os
import re
import sqlite3
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'olist_star_schema.db')
MASTER_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'olist_master_analytical_dataset.csv')
SQL_PATH = os.path.join(BASE_DIR, 'sql', '02_kpi_business_queries.sql')

TOL = 0.01 + 1e-9  # sai số cho các giá trị đã làm tròn 2 chữ số

# Bảng chuỗi thời gian chuẩn (order-level, theo ngày mua) — đối chiếu với Query 6
EXPECTED_MONTHLY = {
    # tháng: (số đơn, doanh thu R$, % trễ, review)
    '2017-01': (750, 111798, 2.93, 4.20),
    '2017-05': (3545, 489159, 2.99, 4.24),
    '2017-08': (4193, 554700, 2.91, 4.31),
    '2017-11': (7288, 987648, 12.40, 3.99),
    '2017-12': (5513, 726033, 7.46, 4.09),
    '2018-02': (6555, 826437, 14.13, 3.88),
    '2018-03': (7003, 953356, 18.96, 3.81),
    '2018-04': (6798, 973534, 4.50, 4.21),
    '2018-06': (6096, 855592, 1.16, 4.31),
    '2018-08': (6351, 838577, 6.19, 4.31),
}


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def load_sql_queries():
    """Đọc file .sql thật, bỏ comment, tách thành các câu truy vấn theo dấu ';'."""
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        lines = [ln.split('--', 1)[0] for ln in f.read().splitlines()]
    statements = [s.strip() for s in "\n".join(lines).split(';') if s.strip()]
    assert len(statements) == 6, f"LỖI: Kỳ vọng 6 truy vấn trong {SQL_PATH}, tìm thấy {len(statements)}"
    return statements


def load_python_orders():
    """Tính độc lập ở cấp order từ master dataset (cohort: delivered + valid delivery delay)."""
    df = pd.read_csv(MASTER_PATH)
    df = df[(df['order_status'] == 'delivered') & (df['is_valid_delivery_delay'] == 1)]
    orders = df.groupby('order_id', as_index=False).agg(
        customer_unique_id=('customer_unique_id', 'first'),
        order_purchase_timestamp=('order_purchase_timestamp', 'first'),
        revenue=('price', 'sum'),
        is_delayed=('is_delayed', 'max'),
        review_score=('review_score', 'max'),
        delay_bucket=('delay_bucket', 'first'),
    )
    orders['year_month'] = orders['order_purchase_timestamp'].astype(str).str[:7]
    return orders


def close(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


# ------------------------------------------------------------------
# 1. Primary keys
# ------------------------------------------------------------------
def test_primary_keys(conn):
    print("\n[1/6] Kiểm tra Khóa chính (Primary Keys) của 5 bảng trong Star Schema...")
    tables = {
        'dim_date': ['date_key'],
        'dim_customers': ['customer_id'],
        'dim_sellers': ['seller_id'],
        'dim_products': ['product_id'],
        'fact_order_items': ['order_id', 'order_item_id']
    }

    for table, pks in tables.items():
        cols = ", ".join(pks)
        query = f"SELECT {cols}, COUNT(*) FROM {table} GROUP BY {cols} HAVING COUNT(*) > 1;"
        duplicates = pd.read_sql_query(query, conn)
        assert len(duplicates) == 0, f"LỖI: Bảng {table} bị trùng lặp khóa chính: {duplicates}"

        for col in pks:
            null_count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table} WHERE {col} IS NULL;", conn)['cnt'].iloc[0]
            assert null_count == 0, f"LỖI: Khóa chính {col} trong {table} có chứa giá trị NULL!"

        total_rows = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table};", conn)['cnt'].iloc[0]
        print(f"  -> {table}: {total_rows:,} dòng, Khóa chính ({cols}) chuẩn 100% (No Nulls, No Duplicates).")


# ------------------------------------------------------------------
# 2. Foreign keys
# ------------------------------------------------------------------
def test_foreign_keys(conn):
    print("\n[2/6] Kiểm tra Khóa ngoại (Foreign Keys Integrity)...")
    fk_checks = [
        ("customer_id", "fact_order_items", "dim_customers"),
        ("seller_id", "fact_order_items", "dim_sellers"),
        ("product_id", "fact_order_items", "dim_products"),
        ("order_date_key", "fact_order_items", "dim_date", "date_key")
    ]

    for item in fk_checks:
        fk_col, child_tbl, parent_tbl = item[0], item[1], item[2]
        parent_pk = item[3] if len(item) > 3 else fk_col

        query = f"""
        SELECT COUNT(f.{fk_col}) AS orphan_count
        FROM {child_tbl} f
        LEFT JOIN {parent_tbl} p ON f.{fk_col} = p.{parent_pk}
        WHERE p.{parent_pk} IS NULL;
        """
        orphan_count = pd.read_sql_query(query, conn)['orphan_count'].iloc[0]
        assert orphan_count == 0, f"LỖI: Có {orphan_count} khóa ngoại mồ côi (orphans) {fk_col} từ {child_tbl} đến {parent_tbl}!"
        print(f"  -> FK {child_tbl}.{fk_col} -> {parent_tbl}.{parent_pk}: 0 khóa ngoại mồ côi (100% khớp).")


# ------------------------------------------------------------------
# 3. Tất cả truy vấn trong file .sql chạy được
# ------------------------------------------------------------------
def test_all_queries_execute(conn, queries):
    print("\n[3/6] Chạy toàn bộ 6 truy vấn từ sql/02_kpi_business_queries.sql...")
    for i, q in enumerate(queries, start=1):
        res = pd.read_sql_query(q, conn)
        assert len(res) > 0, f"LỖI: Query {i} không trả về dòng nào"
        print(f"  -> Query {i}: {len(res)} dòng.")
    q2 = pd.read_sql_query(queries[1], conn)
    assert len(q2) <= 10, "LỖI: Query 2 phải giới hạn tối đa 10 bang"


# ------------------------------------------------------------------
# 4. Query 1: delay bucket vs review
# ------------------------------------------------------------------
def test_query1_delay_vs_review(conn, queries, orders):
    print("\n[4/6] Đối chiếu Query 1 (độ trễ vs điểm đánh giá) với pandas...")
    sql = pd.read_sql_query(queries[0], conn).set_index('delay_bucket')

    assert int(sql['total_orders'].sum()) == 96470, \
        f"LỖI: Tổng đơn delivered hợp lệ (SQL Q1) = {sql['total_orders'].sum()}, kỳ vọng 96,470"
    assert len(orders) == 96470, f"LỖI: Python tính được {len(orders)} đơn, kỳ vọng 96,470"

    delay_rate = round(orders['is_delayed'].mean() * 100.0, 2)
    avg_review = round(orders['review_score'].mean(), 2)
    assert delay_rate == 6.77, f"LỖI: Tỷ lệ trễ hẹn = {delay_rate}%, kỳ vọng 6.77%"
    assert avg_review == 4.16, f"LỖI: Điểm review delivered = {avg_review}, kỳ vọng 4.16"

    py = orders.groupby('delay_bucket').agg(
        total_orders=('order_id', 'count'),
        valid_reviews=('review_score', 'count'),
        mean_review=('review_score', 'mean'),
        pct_1_star=('review_score', lambda s: (s == 1).sum() * 100.0 / max(s.count(), 1)),
    )
    for bucket, row in py.iterrows():
        assert bucket in sql.index, f"LỖI: SQL Q1 thiếu bucket '{bucket}'"
        s = sql.loc[bucket]
        assert int(s['total_orders']) == int(row['total_orders']), f"LỖI: total_orders lệch ở '{bucket}'"
        assert int(s['valid_reviews_count']) == int(row['valid_reviews']), f"LỖI: valid_reviews lệch ở '{bucket}'"
        assert close(s['mean_review'], row['mean_review']), f"LỖI: mean_review lệch ở '{bucket}'"
        assert close(s['pct_1_star'], row['pct_1_star']), f"LỖI: pct_1_star lệch ở '{bucket}'"
    print(f"  -> {len(orders):,} đơn, trễ {delay_rate}%, review TB {avg_review}★; {len(py)} nhóm trễ khớp SQL vs pandas.")


# ------------------------------------------------------------------
# 5. Query 5: retention + chi-square
# ------------------------------------------------------------------
def test_query5_retention(conn, queries, orders):
    print("\n[5/6] Đối chiếu Query 5 (tỷ lệ mua lại) và kiểm định Chi-Square...")
    sql = pd.read_sql_query(queries[4], conn)

    # Tính độc lập bằng pandas — khóa sort có order_id làm tiêu chí phụ (giống SQL)
    cust_counts = orders.groupby('customer_unique_id')['order_id'].nunique()
    total_cust = len(cust_counts)
    repeat_cust = int((cust_counts > 1).sum())
    repeat_rate = repeat_cust / total_cust * 100.0

    assert total_cust == 93350, f"LỖI: Số khách delivered là {total_cust}, kỳ vọng 93,350"
    assert repeat_cust == 2801, f"LỖI: Số khách repeat là {repeat_cust}, kỳ vọng 2,801"
    assert round(repeat_rate, 2) == 3.00, f"LỖI: Tỷ lệ repeat là {repeat_rate:.2f}%, kỳ vọng 3.00%"

    sorted_orders = orders.sort_values(by=['customer_unique_id', 'order_purchase_timestamp', 'order_id'])
    first = sorted_orders.drop_duplicates(subset=['customer_unique_id'], keep='first').copy()
    repeat_ids = set(cust_counts[cust_counts > 1].index)
    first['is_repeat'] = first['customer_unique_id'].isin(repeat_ids).astype(int)

    py = first.groupby('is_delayed').agg(total_customers=('is_repeat', 'size'), repeat_customers=('is_repeat', 'sum'))
    py['rate'] = py['repeat_customers'] * 100.0 / py['total_customers']

    # SQL tổng
    assert int(sql['total_customers'].sum()) == 93350, "LỖI: Tổng khách trong SQL Q5 khác 93,350"
    assert int(sql['repeat_customers'].sum()) == 2801, "LỖI: Tổng khách repeat trong SQL Q5 khác 2,801"

    # SQL từng nhóm trạng thái đơn đầu
    label_map = {0: 'First Eligible Order On-Time', 1: 'First Eligible Order Late'}
    sql_idx = sql.set_index('first_order_delivery_status')
    for flag, label in label_map.items():
        s = sql_idx.loc[label]
        assert int(s['total_customers']) == int(py.loc[flag, 'total_customers']), f"LỖI: total_customers lệch ({label})"
        assert int(s['repeat_customers']) == int(py.loc[flag, 'repeat_customers']), f"LỖI: repeat_customers lệch ({label})"
        assert close(s['repeat_purchase_rate_pct'], py.loc[flag, 'rate']), f"LỖI: repeat rate lệch ({label})"

    on_time = float(sql_idx.loc[label_map[0], 'repeat_purchase_rate_pct'])
    late = float(sql_idx.loc[label_map[1], 'repeat_purchase_rate_pct'])
    assert on_time == 3.04, f"LỖI: Tỷ lệ mua lại nhóm đơn đầu đúng hạn = {on_time}%, kỳ vọng 3.04%"
    assert late == 2.52, f"LỖI: Tỷ lệ mua lại nhóm đơn đầu trễ = {late}%, kỳ vọng 2.52%"

    ct = pd.crosstab(first['is_delayed'], first['is_repeat'])
    chi2, p_val, _, _ = chi2_contingency(ct)
    assert round(chi2, 2) == 5.29, f"LỖI: Chi2 = {chi2}, kỳ vọng ~5.29"
    assert round(p_val, 4) == 0.0215, f"LỖI: p-value = {p_val}, kỳ vọng ~0.0215"
    print(f"  -> Repeat: {repeat_cust:,}/{total_cust:,} ({repeat_rate:.2f}%); đơn đầu đúng hạn {on_time}% vs trễ {late}%.")
    print(f"  -> Chi-Square: chi2 = {chi2:.4f}, p-value = {p_val:.4f} (Khớp).")


# ------------------------------------------------------------------
# 6. Query 6: monthly time series
# ------------------------------------------------------------------
def test_query6_monthly(conn, queries, orders):
    print("\n[6/6] Đối chiếu Query 6 (chuỗi thời gian order-level) với pandas và bảng chuẩn...")
    sql = pd.read_sql_query(queries[5], conn).set_index('year_month')

    py = orders.groupby('year_month').agg(
        total_orders=('order_id', 'count'),
        total_revenue=('revenue', 'sum'),
        delay_rate=('is_delayed', lambda s: s.mean() * 100.0),
        mean_review=('review_score', 'mean'),
    )
    assert set(sql.index) == set(py.index), "LỖI: Tập tháng giữa SQL Q6 và pandas khác nhau"
    for month, row in py.iterrows():
        s = sql.loc[month]
        assert int(s['total_orders']) == int(row['total_orders']), f"LỖI: total_orders lệch tháng {month}"
        assert close(s['total_revenue'], row['total_revenue'], tol=1.0), f"LỖI: doanh thu lệch tháng {month}"
        assert close(s['delay_rate_pct'], row['delay_rate']), f"LỖI: delay rate lệch tháng {month}"
        assert close(s['mean_review'], row['mean_review']), f"LỖI: review lệch tháng {month}"

    for month, (n, rev, delay, review) in EXPECTED_MONTHLY.items():
        s = sql.loc[month]
        assert int(s['total_orders']) == n, f"LỖI: {month} đơn = {s['total_orders']}, kỳ vọng {n}"
        assert close(s['total_revenue'], rev, tol=1.0), f"LỖI: {month} doanh thu = {s['total_revenue']}, kỳ vọng {rev}"
        assert close(s['delay_rate_pct'], delay), f"LỖI: {month} % trễ = {s['delay_rate_pct']}, kỳ vọng {delay}"
        assert close(s['mean_review'], review), f"LỖI: {month} review = {s['mean_review']}, kỳ vọng {review}"
    print(f"  -> {len(py)} tháng khớp SQL vs pandas; {len(EXPECTED_MONTHLY)} tháng mốc khớp bảng chuẩn.")


# ------------------------------------------------------------------
def main():
    print("=" * 65)
    print("BẮT ĐẦU CHẠY BỘ KIỂM THỬ TỰ ĐỘNG (DATA INTEGRITY & RECONCILIATION)")
    print("=" * 65)

    assert os.path.exists(DB_PATH), f"Không tìm thấy database tại {DB_PATH}"
    assert os.path.exists(SQL_PATH), f"Không tìm thấy file SQL tại {SQL_PATH}"
    conn = sqlite3.connect(DB_PATH)

    try:
        queries = load_sql_queries()
        orders = load_python_orders()
        test_primary_keys(conn)
        test_foreign_keys(conn)
        test_all_queries_execute(conn, queries)
        test_query1_delay_vs_review(conn, queries, orders)
        test_query5_retention(conn, queries, orders)
        test_query6_monthly(conn, queries, orders)
        print("\n" + "=" * 65)
        print("TẤT CẢ CÁC BÀI KIỂM THỬ ĐÃ VƯỢT QUA THÀNH CÔNG (100% PASSED)!")
        print("=" * 65)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
