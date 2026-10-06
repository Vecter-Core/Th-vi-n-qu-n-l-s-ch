# 📚 Thư viện Số — Hệ thống quản lý thư viện

Ứng dụng web quản lý thư viện số chạy local, xây dựng bằng **Python (Flask) + SQLite (SQLAlchemy) + Bootstrap 5**.

## ✨ Tính năng

### Khu người dùng (`/`)

| Tính năng                 | Mô tả                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------- |
| Trang chủ & khám phá sách | Hiển thị sách nổi bật, chia theo danh mục, kèm ảnh bìa trực quan                       |
| Tìm kiếm & bộ lọc         | Tìm theo tên sách / tác giả, lọc theo thể loại và trạng thái còn/hết sách              |
| Chi tiết sách             | Thông tin đầy đủ, số lượng còn, điểm đánh giá trung bình, danh sách bình luận          |
| Giỏ mượn                  | Chọn tối đa **3 cuốn**, gửi yêu cầu mượn tới quản trị viên                             |
| Tủ sách cá nhân           | Xem sách đang mượn, hạn trả (báo quá hạn), trạng thái duyệt, lịch sử, yêu cầu trả sách |
| Đánh giá & bình luận      | Chấm 1–5 sao, viết nhận xét; mỗi người đánh giá 1 lần/sách (sửa được)                  |

### Khu quản trị (`/admin`)

| Tính năng           | Mô tả                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------- |
| Tổng quan & báo cáo | Số đầu sách, tổng số bản, lượt mượn đang lưu hành; biểu đồ lượt mượn 6 tháng; top 5 sách được mượn nhiều nhất |
| Quản lý kho sách    | Thêm (có URL ảnh bìa), sửa, xóa, cập nhật nhanh số lượng tồn kho                                              |
| Yêu cầu mượn/trả    | Duyệt (hạn trả +14 ngày) / từ chối đơn mượn; xác nhận khi người dùng trả sách                                 |
| Thành viên          | Xem danh sách, khóa / mở khóa tài khoản (chống tự khóa & chống khóa admin cuối)                               |
| Danh mục            | Thêm, đổi tên, xóa thể loại (chặn xóa khi còn sách)                                                           |
| Nhật ký hệ thống    | Theo dõi 100 sự kiện quản trị gần nhất (CRUD sách, duyệt/trả, khóa tài khoản...)                              |

### Luồng mượn sách

```
Người dùng:  Giỏ (≤3) → Gửi yêu cầu  →  Chờ duyệt
Admin:       Duyệt (hạn trả +14 ngày) / Từ chối
Người dùng:  Đang mượn → "Yêu cầu trả sách"
Admin:       "Xác nhận trả sách" → Hoàn tất (tồn kho tự động khôi phục)
```

Tồn kho khả dụng được **tính toán** từ các phiếu `approved`/`return_pending` → không bao giờ lệch số.

## 🚀 Chạy ứng dụng

Yêu cầu: **Python 3.10+** (khuyến nghị 3.12).

```bash
# 1. Tạo môi trường ảo
python -m venv venv

# 2. Kích hoạt
#   Windows:
venv\Scripts\activate
#   macOS/Linux:
source venv/bin/activate

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Chạy ứng dụng
python app.py
```

Mở trình duyệt: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

> ⚡ CSDL `library.db` được tạo và **tự động seed 12 đầu sách + 9 danh mục + ảnh bìa**
> vào lần chạy đầu tiên (nếu CSDL trống).

### Tài khoản mặc định

| Vai trò       | Tên đăng nhập             | Mật khẩu   |
| ------------- | ------------------------- | ---------- |
| Quản trị viên | `admin`                   | `admin123` |
| Thành viên    | đăng ký tại trang Đăng ký | —          |

## 🗂 Cấu trúc thư mục

```
├── app.py                  # Ứng dụng Flask: config, blueprint, error handlers
├── extensions.py           # db (SQLAlchemy) & login_manager
├── models.py               # User, Category, Book, BorrowRequest, Review, AuditLog
├── seed.py                 # Dữ liệu mẫu: 12 cuốn sách, danh mục, admin, ảnh bìa SVG
├── auth.py                 # Đăng nhập / đăng ký / đăng xuất
├── user.py                 # Khu người dùng: trang chủ, tìm kiếm, giỏ, dashboard
├── admin.py                # Khu quản trị: kho sách, duyệt mượn, thành viên, nhật ký
├── requirements.txt
├── library.db              # SQLite (tự tạo & seed lần đầu)
├── templates/
│   ├── base.html           # Layout chung (navbar, flash messages, footer)
│   ├── auth/               # login, register
│   ├── user/               # index, book_detail, cart, dashboard
│   ├── admin/              # dashboard, books, book_form, requests, users, categories, audit
│   ├── partials/           # book_card (thẻ sách dùng chung)
│   └── errors/             # 403, 404, 500
└── static/
    ├── css/style.css
    ├── js/main.js
    └── covers/             # 13 ảnh bìa SVG (12 sách + 1 bìa dự phòng)
```

## 📋 Các route chính

| Route                                                           | Mô tả                                                               |
| --------------------------------------------------------------- | ------------------------------------------------------------------- |
| `GET /`                                                         | Trang chủ + tìm kiếm & lọc (`?q=`, `?category=`, `?status=in\|out`) |
| `GET /sach/<id>`                                                | Chi tiết sách + đánh giá                                            |
| `POST /sach/<id>/review`                                        | Viết / cập nhật đánh giá                                            |
| `POST /gio/them/<id>`                                           | Thêm sách vào giỏ (tối đa 3)                                        |
| `GET /gio` · `POST /gio/ghi`                                    | Xem giỏ · gửi yêu cầu mượn                                          |
| `GET /tu-sach` · `POST /tu-sach/tra/<id>`                       | Tủ sách cá nhân · yêu cầu trả                                       |
| `GET /auth/login` · `POST /auth/register`                       | Đăng nhập · đăng ký                                                 |
| `GET /admin/`                                                   | Tổng quan & báo cáo                                                 |
| `GET /admin/books` · `add` · `edit` · `delete` · `quantity`     | Kho sách (CRUD)                                                     |
| `GET /admin/requests` · `approve` · `reject` · `confirm-return` | Duyệt & xử lý phiếu mượn                                            |
| `GET /admin/users` · `toggle`                                   | Quản lý thành viên                                                  |
| `GET /admin/categories` · `add` · `rename` · `delete`           | Quản lý danh mục                                                    |
| `GET /admin/audit`                                              | Nhật ký hệ thống                                                    |

## 🧪 Ghi chú kỹ thuật

- **Bảo mật mật khẩu**: băm bằng `werkzeug.security` (pbkdf2).
- **Quyền**: `flask-login` + decorator `admin_required` (403 cho người thường).
- **Kiểm soát tồn kho**: không thể duyệt mượn khi hết bản; không thể giảm tồn kho dưới số bản đang cho mượn; không thể xóa sách/danh mục đang dùng.
- **Nhật ký**: mọi thao tác quản trị đều ghi vào bảng `audit_logs`.
- Ảnh bìa: dùng URL bất kỳ (nếu admin nhập) hoặc SVG minh họa tự sinh trong `static/covers/`.
- Bootstrap 5 & Bootstrap Icons nạp qua CDN — cần kết nối mạng lần đầu để tải CSS/JS.
