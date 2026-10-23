# DATA CLEANING & TRANSFORMATION LOG

> Tài liệu này ghi lại chi tiết các bước xử lý, làm sạch và chuẩn hóa dữ liệu từ `data/raw/` sang `data/processed/`.
> Được tạo tự động bởi pipeline `src/03_data_cleaning.py`.

## 1. Summary of Cleaning Actions

| Table | Raw Rows | Cleaned Rows | Rows Delta | Actions Taken | Business Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Products** | 32,951 | 32,951 | 0 | Dịch bổ sung 'pc_gamer' và 'portateis_cozinha...'; map tiếng Anh; fill 'unknown' cho 610 missing category; fill median cho kích thước/trọng lượng. | Đảm bảo 100% sản phẩm có danh mục hiển thị chuẩn tiếng Anh trên Dashboard và không có NaN kích thước làm lỗi thuật toán logistics. |
| **Geolocation** | 1,000,163 | 19,010 | -981,153 | Xóa 261,831 dòng trùng lặp 100%; Xóa 33 tọa độ ngoại lai ngoài Brazil; Xóa 0 dòng thiếu zip code; Gom nhóm (group by) 19,010 zip code duy nhất (median lat/lng, mode city/state). | Triệt tiêu hoàn toàn rủi ro nhân dòng (Row Multiplication) khi kết nối dữ liệu địa lý với Customers và Sellers. |
| **Customers** | 99,441 | 99,441 | 0 | Chuẩn hóa định dạng Title Case cho City, Upper Case cho State code 2 ký tự. | Nhất quán dữ liệu hiển thị địa phương. |
| **Sellers** | 3,095 | 3,095 | 0 | Chuẩn hóa định dạng Title Case cho City, Upper Case cho State code 2 ký tự. | Nhất quán dữ liệu hiển thị người bán. |
| **Order Reviews** | 99,224 | 98,673 | -551 | Lọc bỏ 551 review trùng order_id (giữ review mới nhất theo timestamp); thêm cột satisfaction_tier; flag has_comment. | Ngăn chặn việc 1 order có nhiều review gây nhân dòng khi kết nối với bảng Orders. |
| **Order Payments** | 103,886 | 103,886 | 0 | Sửa 2 giá trị payment_installments = 0 thành 1 kỳ; Chuẩn hóa Title Case cho payment_type. | Đảm bảo logic kinh doanh hợp lý (trả góp tối thiểu phải là 1 kỳ). |
| **Order Items** | 112,650 | 112,650 | 0 | Ép kiểu datetime cho shipping_limit_date; tính cột tổng giá trị item_total_value. | Hỗ trợ phân tích doanh thu và phí ship ở cấp độ chi tiết sản phẩm. |
| **Orders** | 99,441 | 99,441 | 0 | Ép kiểu 5 cột datetime; sinh feature thời gian (actual_delivery_days, delivery_delay_days, is_delayed, seller_dispatch_days, delay_bucket). | Tạo các metrics cốt lõi để trả lời trực tiếp các câu hỏi bài toán kinh doanh về Delivery Performance & Customer Satisfaction. |
| **Master Analytical Dataset** | 112,650 | 112,650 | 0 | Denormalize sạch tích hợp 6 bảng (Items + Orders + Products + Customers + Sellers + Reviews) tại grain 1 item/dòng; thêm cờ is_interstate. | File phân tích all-in-one phục vụ trực tiếp cho Exploratory Data Analysis (EDA) và xây dựng Dashboard Power BI mà không lo bị nhân dòng. |

## 2. Key Data Engineering Highlights

1. **Triệt tiêu nhân dòng (Zero Row Multiplication):** Bảng Geolocation (hơn 1 triệu dòng) được gom nhóm (aggregate) theo 19,010 zip code duy nhất với giá trị tọa độ trung vị (median). Bảng Review được lọc giữ lại review mới nhất cho mỗi order.
2. **Giải quyết dứt điểm bản dịch thiếu:** Đã bổ sung bản dịch tiếng Anh cho `pc_gamer` và `portateis_cozinha_e_preparadores_de_alimentos` theo đúng cam kết trong Business Problem.
3. **Feature Engineering sẵn sàng cho Business Questions:** Đã tính toán chuẩn hóa `actual_delivery_days`, `delivery_delay_days`, `is_delayed`, `delay_bucket`, `is_interstate` để phục vụ trực tiếp phân tích tương quan giữa giao hàng trễ và điểm hài lòng khách hàng.
4. **Master Dataset:** Tạo bảng tích hợp `olist_master_analytical_dataset.csv` giúp việc kết nối vào Power BI / Jupyter Notebook trở nên cực kỳ thuận tiện và an toàn.
