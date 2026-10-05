"""Các model cơ sở dữ liệu của Thư viện Số."""
from datetime import datetime

from flask import has_request_context, url_for
from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

# Các trạng thái coi cuốn sách là "đang lưu hành" (chiếm một bản tồn kho)
ACTIVE_BORROW_STATUSES = ('approved', 'return_pending')


def now():
    return datetime.now()


class User(db.Model, UserMixin):
    """Tài khoản người dùng / quản trị viên."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=now, nullable=False)

    borrow_requests = db.relationship('BorrowRequest', back_populates='user', lazy='dynamic')
    reviews = db.relationship('Review', back_populates='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Category(db.Model):
    """Danh mục / thể loại sách."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    books = db.relationship('Book', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'


class Book(db.Model):
    """Đầu sách trong kho."""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default='')
    quantity = db.Column(db.Integer, nullable=False, default=0)
    cover_url = db.Column(db.String(300), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=now, nullable=False)

    # --- Thông tin "xúc giác" & nhân văn (Editorial & Tactile Design) ---
    # Tâm trạng đọc sách (Reading Mood Matcher) — khóa kỹ thuật: healing / overnight / saturday / deep
    mood = db.Column(db.String(30), nullable=True, index=True)
    # Số trang — dùng cho bộ lọc "đọc hết trong một đêm"
    pages = db.Column(db.Integer, nullable=True, default=0)
    # Tình trạng vật lý của cuốn sách (vết sẹo, góc bìa quăn...)
    condition_note = db.Column(db.String(300), nullable=True, default='')
    # Số người từng mượn cuốn này (lịch sử truyền tay)
    times_borrowed = db.Column(db.Integer, nullable=False, default=0)
    # Ghi chú tay của thủ thư (Sticky Note viết tay)
    librarian_note = db.Column(db.String(400), nullable=True, default='')
    librarian_note_by = db.Column(db.String(80), nullable=True, default='')
    # Màu gáy sách cho Kệ sách gỗ 3D (Wood Shelf View)
    spine_color = db.Column(db.String(9), nullable=True, default='')

    category = db.relationship('Category', back_populates='books')
    borrow_requests = db.relationship('BorrowRequest', backref='book', lazy='dynamic')
    reviews = db.relationship('Review', backref='book', lazy='dynamic')

    @property
    def borrowed_count(self):
        """Số bản đang lưu hành (đã duyệt hoặc chờ xác nhận trả)."""
        return BorrowRequest.query.filter(
            BorrowRequest.book_id == self.id,
            BorrowRequest.status.in_(ACTIVE_BORROW_STATUSES),
        ).count()

    @property
    def available(self):
        """Số bản hiện có thể cho mượn."""
        return max(0, self.quantity - self.borrowed_count)

    @property
    def in_stock(self):
        return self.available > 0

    @property
    def average_rating(self):
        """Trả về (điểm trung bình, số lượng đánh giá)."""
        row = (
            db.session.query(func.avg(Review.rating), func.count(Review.id))
            .filter(Review.book_id == self.id)
            .one()
        )
        avg = round(float(row[0]), 1) if row[0] is not None else 0.0
        return avg, int(row[1] or 0)

    @property
    def cover(self):
        """URL ảnh bìa (kèm ảnh mặc định khi chưa có)."""
        if self.cover_url:
            return self.cover_url
        if has_request_context():
            return url_for('static', filename='covers/default.svg')
        return '/static/covers/default.svg'

    def __repr__(self):
        return f'<Book {self.title}>'


class BorrowRequest(db.Model):
    """Phiếu yêu cầu mượn / trả sách.

    Luồng trạng thái:
        pending -> approved -> return_pending -> returned
                    \\-> rejected
    """
    __tablename__ = 'borrow_requests'

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    RETURN_PENDING = 'return_pending'
    RETURNED = 'returned'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=PENDING)
    requested_at = db.Column(db.DateTime, default=now, nullable=False)
    decided_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    returned_at = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.String(300), nullable=True)

    user = db.relationship('User', back_populates='borrow_requests')

    @property
    def is_active(self):
        """True nếu phiếu đang chiếm bản sách (chưa hoàn thành)."""
        return self.status in ACTIVE_BORROW_STATUSES

    def __repr__(self):
        return f'<BorrowRequest {self.id} ({self.status})>'


class Review(db.Model):
    """Đánh giá / bình luận của độc giả cho một cuốn sách."""
    __tablename__ = 'reviews'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='uq_review_user_book'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False, default=5)
    comment = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, default=now, nullable=False)

    author = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id} (★{self.rating})>'


class AuditLog(db.Model):
    """Nhật ký hệ thống — thao tác của quản trị viên & sự kiện quan trọng."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=now, nullable=False, index=True)

    actor = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.action}>'


def record_audit(action, details='', actor_id=None):
    """Thêm một bản ghi nhật ký vào session (người gọi tự commit)."""
    db.session.add(
        AuditLog(action=action, details=details, actor_id=actor_id, created_at=now())
    )


def migrate_schema():
    """Tự thêm cột mới vào bảng `books` nếu chạy trên CSDL cũ (SQLite).
    An toàn — chỉ ALTER khi cột chưa tồn tại. Chạy trong app_context."""
    engine = db.engine
    # Thuật toán xếp hạng & tính khả dụng đã có sẵn trong Python — không cần cột mới
    required = {
        'mood': 'VARCHAR(30)',
        'pages': 'INTEGER DEFAULT 0',
        'condition_note': 'VARCHAR(300)',
        'times_borrowed': 'INTEGER NOT NULL DEFAULT 0',
        'librarian_note': 'VARCHAR(400)',
        'librarian_note_by': 'VARCHAR(80)',
        'spine_color': 'VARCHAR(9)',
    }
    with engine.connect() as conn:
        existing = {
            row[1] for row in conn.execute(db.text('PRAGMA table_info(books)'))
        }
        for col, ddl in required.items():
            if col not in existing:
                conn.execute(db.text(f'ALTER TABLE books ADD COLUMN {col} {ddl}'))
                conn.commit()
