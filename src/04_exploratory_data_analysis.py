import os
import sys
import pandas as pd
import numpy as np
# pyright: ignore[missing-import]
import matplotlib.pyplot as plt
# pyright: ignore[missing-import]
import seaborn as sns

# Cấu hình UTF-8 cho Windows console
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 1. CONFIGURATION & STYLING
# ==========================================
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)

PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
OUTPUT_FIGURES_DIR = os.path.join(BASE_DIR, 'outputs', 'figures')
OUTPUT_TABLES_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

os.makedirs(OUTPUT_FIGURES_DIR, exist_ok=True)
os.makedirs(OUTPUT_TABLES_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Cấu hình phong cách biểu đồ hiện đại, chuẩn thẩm mỹ cao
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Segoe UI, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#f0f0f0'
plt.rcParams['grid.linestyle'] = '--'

# Bảng màu chủ đạo (Curated Color Palette)
PRIMARY_COLOR = '#1f77b4'  # Deep Navy Blue
ACCENT_RED = '#d62728'     # Alert Red (Delays / Risk)
ACCENT_GREEN = '#2ca02c'   # Positive Green (On time / 5-star)
ACCENT_ORANGE = '#ff7f0e'  # Warning Orange
NEUTRAL_GRAY = '#7f7f7f'   # Subdued Gray

# ==========================================
# 2. LOAD DATA
# ==========================================
def load_data():
    print("Loading master analytical dataset...")
    master_path = os.path.join(PROCESSED_DATA_DIR, 'olist_master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    print(f"Loaded master dataset: {len(df):,} rows, {len(df.columns)} columns.\n")
    return df

# ==========================================
# 3. ANALYSIS 1: DELIVERY DELAY VS REVIEW SCORE
# ==========================================
def analyze_delivery_delay_vs_satisfaction(df):
    print("--- [Question 1] Delivery Delay vs Review Score ---")
    deliv = df[df['order_status'] == 'delivered'].drop_duplicates(subset=['order_id']).copy()

    # Thống kê theo delay bucket
    bucket_order = ['On Time / Early', '1-3 Days Late', '4-7 Days Late', '> 7 Days Late']
    bucket_stats = deliv.groupby('delay_bucket').agg(
        order_count=('order_id', 'count'),
        mean_review=('review_score', 'mean'),
        median_review=('review_score', 'median'),
        pct_1_star=('review_score', lambda s: (s == 1).mean() * 100),
        pct_5_star=('review_score', lambda s: (s == 5).mean() * 100)
    ).reindex(bucket_order).reset_index()

    print(bucket_stats)
    bucket_stats.to_csv(os.path.join(OUTPUT_TABLES_DIR, 'q1_delay_bucket_stats.csv'), index=False)

    # Trực quan hóa
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Subplot 1: Điểm đánh giá trung bình theo từng mức trễ
    colors = [ACCENT_GREEN, '#a1d99b', ACCENT_ORANGE, ACCENT_RED]
    bars = ax1.bar(bucket_stats['delay_bucket'], bucket_stats['mean_review'], color=colors, width=0.55, edgecolor='black', linewidth=0.5)
    ax1.set_title('Average Review Score by Delivery Delay Bucket\n(The "Tolerance Cliff" after 3 days)', fontsize=13, fontweight='bold', pad=15)
    ax1.set_ylabel('Mean Review Score (1 to 5 Stars)', fontsize=11)
    ax1.set_ylim(0, 5)
    ax1.axhline(deliv['review_score'].mean(), color=NEUTRAL_GRAY, linestyle='--', label=f"Overall Mean: {deliv['review_score'].mean():.2f} / 5")

    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 6), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax1.legend(loc='lower left')

    # Subplot 2: Tỷ lệ đánh giá 1 sao (Cực kỳ không hài lòng)
    bars2 = ax2.bar(bucket_stats['delay_bucket'], bucket_stats['pct_1_star'], color=colors, width=0.55, edgecolor='black', linewidth=0.5)
    ax2.set_title('% of 1-Star (Extremely Dissatisfied) Reviews\n(More than half give 1-star when delay > 3 days)', fontsize=13, fontweight='bold', pad=15)
    ax2.set_ylabel('% of 1-Star Reviews', fontsize=11)
    ax2.set_ylim(0, 80)

    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 6), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_FIGURES_DIR, 'fig1_delivery_delay_vs_review_score.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure: {fig_path}\n")

# ==========================================
# 4. ANALYSIS 2: GEOGRAPHIC BOTTLENECKS
# ==========================================
def analyze_geographic_bottlenecks(df):
    print("--- [Question 2] Geographic Bottlenecks & Interstate Delivery ---")
    deliv = df[df['order_status'] == 'delivered'].drop_duplicates(subset=['order_id']).copy()

    state_stats = deliv.groupby('customer_state').agg(
        total_orders=('order_id', 'count'),
        delayed_orders=('is_delayed', 'sum'),
        delay_rate=('is_delayed', lambda s: s.mean() * 100),
        avg_actual_days=('actual_delivery_days', 'mean'),
        avg_review=('review_score', 'mean')
    ).reset_index()

    # Lọc các bang có quy mô đơn hàng đáng kể (>= 100 đơn)
    state_sig = state_stats[state_stats['total_orders'] >= 100].sort_values(by='delay_rate', ascending=False)
    state_sig.to_csv(os.path.join(OUTPUT_TABLES_DIR, 'q2_state_delivery_stats.csv'), index=False)

    # Top 8 bang trễ cao nhất và Top 5 bang trễ thấp nhất
    top_delayed = state_sig.head(8)
    lowest_delayed = state_sig.tail(5)
    plot_states = pd.concat([top_delayed, lowest_delayed]).sort_values(by='delay_rate', ascending=True)

    fig, ax1 = plt.subplots(figsize=(12, 7))

    y_pos = np.arange(len(plot_states))
    colors = [ACCENT_RED if r > 10 else PRIMARY_COLOR for r in plot_states['delay_rate']]
    bars = ax1.barh(y_pos, plot_states['delay_rate'], color=colors, height=0.65, edgecolor='black', linewidth=0.5)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(plot_states['customer_state'], fontsize=11, fontweight='bold')
    ax1.set_xlabel('Delivery Delay Rate (% of orders arriving late)', fontsize=11)
    ax1.set_title('Geographic Delivery Bottlenecks: Top Delayed States vs Best Performing States\n(Northeast region suffers the highest delay rates > 15%)',
                  fontsize=13, fontweight='bold', pad=15)
    ax1.axvline(deliv['is_delayed'].mean() * 100, color='black', linestyle='--', label=f"National Avg Delay: {deliv['is_delayed'].mean()*100:.1f}%")

    for bar, (_, row) in zip(bars, plot_states.iterrows()):
        w = bar.get_width()
        ax1.annotate(f"{w:.1f}% (Avg {row['avg_actual_days']:.0f}d, {row['avg_review']:.2f} rating)",
                     xy=(w, bar.get_y() + bar.get_height()/2),
                     xytext=(6, 0), textcoords="offset points", ha='left', va='center', fontsize=9.5)

    ax1.legend(loc='lower right')
    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_FIGURES_DIR, 'fig2_state_delivery_performance.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure: {fig_path}\n")

# ==========================================
# 5. ANALYSIS 3: SELLER RISK MATRIX
# ==========================================
def analyze_seller_risk_matrix(df):
    print("--- [Question 3] Seller Risk Matrix (High Revenue - Low Satisfaction) ---")
    deliv = df[df['order_status'] == 'delivered'].copy()

    seller_stats = deliv.groupby('seller_id').agg(
        total_revenue=('price', 'sum'),
        items_sold=('order_item_id', 'count'),
        orders_count=('order_id', 'nunique'),
        avg_review=('review_score', 'mean'),
        delay_rate=('is_delayed', lambda s: s.mean() * 100)
    ).reset_index()

    # Định nghĩa ngưỡng High Revenue (>= 15,000 R$) và Low Review (< 3.8)
    REV_THRESHOLD = 15000
    REVIEW_THRESHOLD = 3.8

    seller_stats['quadrant'] = 'Normal'
    seller_stats.loc[(seller_stats['total_revenue'] >= REV_THRESHOLD) & (seller_stats['avg_review'] < REVIEW_THRESHOLD), 'quadrant'] = 'High Risk (Intervene)'
    seller_stats.loc[(seller_stats['total_revenue'] >= REV_THRESHOLD) & (seller_stats['avg_review'] >= REVIEW_THRESHOLD), 'quadrant'] = 'Star Sellers (Top Performers)'

    high_risk_sellers = seller_stats[seller_stats['quadrant'] == 'High Risk (Intervene)'].sort_values(by='total_revenue', ascending=False)
    high_risk_sellers.to_csv(os.path.join(OUTPUT_TABLES_DIR, 'q3_high_risk_sellers.csv'), index=False)
    print(f"Identified {len(high_risk_sellers)} High Risk sellers.")

    fig, ax = plt.subplots(figsize=(12, 7))

    # Scatter plot
    sns.scatterplot(
        data=seller_stats[seller_stats['total_revenue'] >= 1000],
        x='total_revenue',
        y='avg_review',
        hue='quadrant',
        palette={'Normal': '#d9d9d9', 'Star Sellers (Top Performers)': ACCENT_GREEN, 'High Risk (Intervene)': ACCENT_RED},
        alpha=0.8,
        s=60,
        ax=ax
    )

    ax.set_xscale('log')
    ax.axvline(REV_THRESHOLD, color='gray', linestyle=':')
    ax.axhline(REVIEW_THRESHOLD, color='gray', linestyle=':')

    # Highlight High Risk Quadrant
    ax.annotate('CRITICAL INTERVENTION ZONE\n(High Revenue, Low Review < 3.8)',
                xy=(REV_THRESHOLD * 1.5, 2.0),
                fontsize=11, fontweight='bold', color=ACCENT_RED,
                bbox=dict(boxstyle="round,pad=0.5", fc="#ffebeb", ec=ACCENT_RED, lw=1))

    ax.set_title('Seller Risk Matrix: Revenue vs Customer Satisfaction\n(Prioritizing Sellers for Operational Audits)',
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Total Revenue (R$, Log Scale)', fontsize=11)
    ax.set_ylabel('Average Review Score (1 to 5 Stars)', fontsize=11)
    ax.set_ylim(1, 5.2)

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_FIGURES_DIR, 'fig3_seller_risk_matrix.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure: {fig_path}\n")

# ==========================================
# 6. ANALYSIS 4: PRODUCT CATEGORY PERFORMANCE
# ==========================================
def analyze_category_performance(df):
    print("--- [Question 4] Product Category Performance Matrix ---")
    deliv = df[df['order_status'] == 'delivered'].copy()

    # 1. Tính toán an toàn, chuẩn xác và tận dụng C-engine của Pandas (Tránh lambda closure trên deliv.loc)
    cat_stats = deliv.groupby('product_category_formatted').agg(
        total_revenue=('price', 'sum'),
        total_freight=('freight_value', 'sum'),
        total_item_value=('item_total_value', 'sum'),
        items_sold=('order_item_id', 'count'),
        avg_review=('review_score', 'mean'),
        delay_rate=('is_delayed', lambda s: s.mean() * 100)
    ).reset_index()

    # 2. Tính phần trăm cước phí vận chuyển (Vectorized calculation)
    cat_stats['freight_pct_of_total'] = ((cat_stats['total_freight'] / cat_stats['total_item_value']) * 100).round(2)
    cat_stats = cat_stats.sort_values(by='total_revenue', ascending=False)

    cat_stats.to_csv(os.path.join(OUTPUT_TABLES_DIR, 'q4_category_performance.csv'), index=False)

    # Top 12 categories by revenue
    top12 = cat_stats.head(12).sort_values(by='total_revenue', ascending=True)

    fig, ax1 = plt.subplots(figsize=(13, 7))

    y_pos = np.arange(len(top12))
    bars = ax1.barh(y_pos, top12['total_revenue'] / 1000.0, color=PRIMARY_COLOR, height=0.6, edgecolor='black', linewidth=0.5)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top12['product_category_formatted'], fontsize=11)
    ax1.set_xlabel('Total Revenue (Thousands R$)', fontsize=11)
    ax1.set_title('Top 12 Product Categories by Revenue with Average Customer Rating\n(Watches & Gifts and Health/Beauty lead sales with strong satisfaction)',
                  fontsize=13, fontweight='bold', pad=15)

    for bar, (_, row) in zip(bars, top12.iterrows()):
        w = bar.get_width()
        ax1.annotate(f"R$ {w:,.0f}k  |  {row['avg_review']:.2f} stars  (Delay: {row['delay_rate']:.1f}%)",
                     xy=(w, bar.get_y() + bar.get_height()/2),
                     xytext=(6, 0), textcoords="offset points", ha='left', va='center', fontsize=9.5)

    ax1.set_xlim(0, top12['total_revenue'].max() / 1000.0 * 1.35)
    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_FIGURES_DIR, 'fig4_category_performance_matrix.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure: {fig_path}\n")

# ==========================================
# 7. ANALYSIS 5: CUSTOMER RETENTION & FIRST ORDER IMPACT
# ==========================================
def analyze_customer_retention(df):
    print("--- [Question 5] Customer Retention & First Order Experience ---")
    orders_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_orders_cleaned.csv'))
    cust_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'olist_customers_cleaned.csv'))

    merged = orders_df.merge(cust_df[['customer_id', 'customer_unique_id']], on='customer_id')

    # Phân loại khách hàng mua 1 lần vs khách hàng quay lại (Repeat Buyers)
    order_counts = merged.groupby('customer_unique_id')['order_id'].nunique()
    total_cust = len(order_counts)
    repeat_cust_ids = set(order_counts[order_counts > 1].index)
    repeat_count = len(repeat_cust_ids)
    repeat_pct = (repeat_count / total_cust) * 100

    print(f"Total Unique Customers: {total_cust:,}")
    print(f"Repeat Customers: {repeat_count:,} ({repeat_pct:.2f}%)")

    # Xác định đơn hàng đầu tiên (First Order) của từng khách hàng
    sorted_orders = merged.sort_values(by=['customer_unique_id', 'order_purchase_timestamp'])
    first_orders = sorted_orders.drop_duplicates(subset=['customer_unique_id'], keep='first').copy()
    first_orders['is_repeat_customer'] = first_orders['customer_unique_id'].isin(repeat_cust_ids).astype(int)

    # Đánh giá tác động của giao hàng trễ ở đơn đầu tiên
    deliv_first = first_orders[first_orders['order_status'] == 'delivered'].copy()
    retention_by_delay = deliv_first.groupby('is_delayed').agg(
        customer_count=('customer_unique_id', 'count'),
        repeat_rate=('is_repeat_customer', lambda s: s.mean() * 100)
    ).reset_index()

    retention_by_delay['status_label'] = retention_by_delay['is_delayed'].map({0: '1st Order On-Time', 1: '1st Order Delayed'})
    retention_by_delay.to_csv(os.path.join(OUTPUT_TABLES_DIR, 'q5_retention_by_first_order_delay.csv'), index=False)
    print(retention_by_delay)

    # Trực quan hóa
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Subplot 1: Donut chart tỷ lệ khách hàng quay lại
    sizes = [total_cust - repeat_count, repeat_count]
    labels = [f"One-Time Buyers\n({sizes[0]:,} - {sizes[0]/total_cust*100:.1f}%)",
              f"Repeat Buyers\n({sizes[1]:,} - {sizes[1]/total_cust*100:.1f}%)"]
    colors = ['#aec7e8', PRIMARY_COLOR]
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.75,
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
    ax1.set_title('Overall Customer Retention Rate\n(E-commerce marketplace standard: low repeat rate ~3.1%)', fontsize=12, fontweight='bold')

    # Subplot 2: Tác động của trải nghiệm giao hàng đơn đầu đến việc quay lại mua
    bars = ax2.bar(retention_by_delay['status_label'], retention_by_delay['repeat_rate'],
                   color=[ACCENT_GREEN, ACCENT_RED], width=0.45, edgecolor='black', linewidth=0.5)
    ax2.set_title('Impact of 1st Order Delivery on Customer Retention\n(19% drop in repeat purchase rate if 1st order is delayed)',
                  fontsize=12, fontweight='bold', pad=15)
    ax2.set_ylabel('Repeat Purchase Rate (%)', fontsize=11)
    ax2.set_ylim(0, 4.2)

    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f"{h:.2f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 6), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Vẽ mũi tên so sánh sụt giảm
    drop_pct = (retention_by_delay.loc[0, 'repeat_rate'] - retention_by_delay.loc[1, 'repeat_rate']) / retention_by_delay.loc[0, 'repeat_rate'] * 100
    ax2.annotate(f"-{drop_pct:.1f}% relative drop!",
                 xy=(1, retention_by_delay.loc[1, 'repeat_rate']),
                 xytext=(0.5, 3.6),
                 arrowprops=dict(facecolor=ACCENT_RED, shrink=0.08, width=1.5, headwidth=6),
                 fontsize=10.5, fontweight='bold', color=ACCENT_RED)

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_FIGURES_DIR, 'fig5_customer_retention_and_first_order_impact.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure: {fig_path}\n")

# ==========================================
# 8. MAIN EXECUTION
# ==========================================
def main():
    print("="*60)
    print("STARTING PHASE 5: EXPLORATORY DATA ANALYSIS (EDA)")
    print("="*60)

    df = load_data()
    analyze_delivery_delay_vs_satisfaction(df)
    analyze_geographic_bottlenecks(df)
    analyze_seller_risk_matrix(df)
    analyze_category_performance(df)
    analyze_customer_retention(df)

    print("="*60)
    print("PHASE 5 EDA COMPLETED SUCCESSFULLY! ALL FIGURES IN: outputs/figures/")
    print("="*60)

if __name__ == "__main__":
    main()
