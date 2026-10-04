"""Blueprint khu quản trị — Bước 5: tổng quan, kho sách (CRUD), danh mục, thống kê."""
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from functools import wraps
from sqlalchemy import or_

from extensions import db
from models import (
    ACTIVE_BORROW_STATUSES,
    AuditLog,
    Book,
    BorrowRequest,
    Category,
    record_audit,
)

admin_bp = Blueprint('admin', __name__)

BORROW_DAYS = 14


def admin_required(view):
    """Chỉ cho phép quản trị viên truy cập; người khác nhận 403."""
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapper


@admin_bp.route('/')
@admin_required
def dashboard():
    now_dt = datetime.now()

    total_books = Book.query.count()
    total_copies = db.session.query(db.func.sum(Book.quantity)).scalar() or 0
    active_borrows = BorrowRequest.query.filter(
        BorrowRequest.status.in_(ACTIVE_BORROW_STATUSES)
    ).count()
    pending_count = BorrowRequest.query.filter_by(status='pending').count()

    # Lượt mượn theo tháng (6 tháng gần nhất, dựa trên thời điểm duyệt)
    counts_by_ym = {
        ym: cnt
        for ym, cnt in (
            db.session.query(
                db.func.strftime('%Y-%m', BorrowRequest.decided_at).label('ym'),
                db.func.count(BorrowRequest.id),
            )
            .filter(
                BorrowRequest.status.in_(['approved', 'return_pending', 'returned']),
                BorrowRequest.decided_at.isnot(None),
            )
            .group_by('ym')
            .all()
        )
    }
    monthly, max_month = [], 0
    for i in range(5, -1, -1):
        y, m = now_dt.year, now_dt.month - i
        while m <= 0:
            m += 12
            y -= 1
        count = counts_by_ym.get(f'{y}-{m:02d}', 0)
        max_month = max(max_month, count)
        monthly.append({'label': f'Th{m}/{str(y)[-2:]}', 'count': count})
    for item in monthly:
        item['pct'] = round(item['count'] / max_month * 100) if max_month else 0

    # Top 5 sách được mượn nhiều nhất
    top_rows = (
        db.session.query(BorrowRequest.book_id, db.func.count(BorrowRequest.id).label('cnt'))
        .filter(BorrowRequest.status.in_(['approved', 'return_pending', 'returned']))
        .group_by(BorrowRequest.book_id)
        .order_by(db.desc('cnt'))
        .limit(5)
        .all()
    )
    top_books = []
    for book_id, cnt in top_rows:
        book = db.session.get(Book, book_id)
        if book is not None:
            top_books.append({'book': book, 'count': cnt})
    max_top = top_books[0]['count'] if top_books else 0

    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_books=total_books,
        total_copies=total_copies,
        active_borrows=active_borrows,
        pending_count=pending_count,
        monthly=monthly,
        top_books=top_books,
        max_top=max_top,
        recent_logs=recent_logs,
    )


@admin_bp.route('/books')
@admin_required
def books():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    query = Book.query
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))
    if category_id:
        query = query.filter(Book.category_id == category_id)
    book_list = query.order_by(Book.title).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template(
        'admin/books.html',
        books=book_list,
        categories=categories,
        q=q,
        category_id=category_id,
    )


def _parse_book_form():
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    description = request.form.get('description', '').strip()
    try:
        quantity = int(request.form.get('quantity', 0))
    except (TypeError, ValueError):
        quantity = 0
    category_id = request.form.get('category_id', type=int) or None
    cover_url = request.form.get('cover_url', '').strip()
    return title, author, description, max(quantity, 0), category_id, cover_url


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def book_add():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        title, author, description, quantity, category_id, cover_url = _parse_book_form()
        if not title or not author:
            flash('Vui lòng nhập tên sách và tác giả.', 'danger')
            return render_template(
                'admin/book_form.html', book=None, categories=categories, form=request.form
            )
        book = Book(
            title=title,
            author=author,
            description=description or 'Chưa có mô tả.',
            quantity=quantity,
            category_id=category_id,
            cover_url=cover_url or None,
            created_at=datetime.now(),
        )
        db.session.add(book)
        record_audit(
            'Thêm sách',
            f"Thêm sách '{title}' (tác giả: {author}, số lượng: {quantity})",
            current_user.id,
        )
        db.session.commit()
        flash(f'Đã thêm sách “{title}” vào kho.', 'success')
        return redirect(url_for('admin.books'))
    return render_template('admin/book_form.html', book=None, categories=categories, form=None)


@admin_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def book_edit(book_id):
    book = db.get_or_404(Book, book_id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        title, author, description, quantity, category_id, cover_url = _parse_book_form()
        if not title or not author:
            flash('Vui lòng nhập tên sách và tác giả.', 'danger')
            return render_template(
                'admin/book_form.html', book=book, categories=categories, form=request.form
            )
        old_qty = book.quantity
        book.title = title
        book.author = author
        book.description = description or 'Chưa có mô tả.'
        book.quantity = quantity
        book.category_id = category_id
        book.cover_url = cover_url or None
        record_audit(
            'Sửa sách',
            f"Sửa sách '{title}' (tác giả: {author}"
            + (f', số lượng {old_qty} → {quantity})' if old_qty != quantity else ')'),
            current_user.id,
        )
        db.session.commit()
        flash(f'Đã cập nhật sách “{title}”.', 'success')
        return redirect(url_for('admin.books'))
    return render_template('admin/book_form.html', book=book, categories=categories, form=None)


@admin_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def book_delete(book_id):
    book = db.get_or_404(Book, book_id)
    active_count = book.borrow_requests.filter(
        BorrowRequest.status.in_(['pending'] + list(ACTIVE_BORROW_STATUSES))
    ).count()
    if active_count:
        flash(
            f'Không thể xóa “{book.title}” vì còn {active_count} phiếu mượn đang lưu hành.',
            'danger',
        )
    else:
        title = book.title
        db.session.delete(book)
        record_audit('Xóa sách', f"Xóa sách '{title}'", current_user.id)
        db.session.commit()
        flash(f'Đã xóa sách “{title}” khỏi kho.', 'success')
    return redirect(url_for('admin.books'))


@admin_bp.route('/books/<int:book_id>/quantity', methods=['POST'])
@admin_required
def book_set_quantity(book_id):
    book = db.get_or_404(Book, book_id)
    try:
        new_qty = int(request.form.get('quantity', book.quantity))
    except (TypeError, ValueError):
        new_qty = book.quantity
    new_qty = max(new_qty, 0)
    borrowed = book.borrowed_count
    if new_qty < borrowed:
        flash(
            f'Không thể giảm xuống dưới {borrowed} (số bản đang cho mượn của “{book.title}”).',
            'danger',
        )
    else:
        old_qty = book.quantity
        book.quantity = new_qty
        record_audit(
            'Cập nhật tồn kho',
            f"Sách '{book.title}': số lượng {old_qty} → {new_qty}",
            current_user.id,
        )
        db.session.commit()
        flash(f'Đã cập nhật số lượng “{book.title}” thành {new_qty}.', 'success')
    return redirect(url_for('admin.books'))


@admin_bp.route('/categories')
@admin_required
def categories():
    rows = (
        db.session.query(Category, db.func.count(Book.id))
        .outerjoin(Book, Book.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name)
        .all()
    )
    items = [{'category': cat, 'count': cnt} for cat, cnt in rows]
    return render_template('admin/categories.html', items=items)


@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def category_add():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Vui lòng nhập tên danh mục.', 'warning')
    elif Category.query.filter_by(name=name).first() is not None:
        flash(f'Danh mục “{name}” đã tồn tại.', 'warning')
    else:
        db.session.add(Category(name=name))
        record_audit('Thêm danh mục', f"Thêm danh mục '{name}'", current_user.id)
        db.session.commit()
        flash(f'Đã thêm danh mục “{name}”.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/<int:cat_id>/rename', methods=['POST'])
@admin_required
def category_rename(cat_id):
    cat = db.get_or_404(Category, cat_id)
    name = request.form.get('name', '').strip()
    old_name = cat.name
    if not name:
        flash('Tên danh mục không được để trống.', 'warning')
    elif name != old_name and Category.query.filter_by(name=name).first() is not None:
        flash(f'Danh mục “{name}” đã tồn tại.', 'warning')
    else:
        cat.name = name
        record_audit(
            'Đổi tên danh mục',
            f"Danh mục '{old_name}' → '{name}'",
            current_user.id,
        )
        db.session.commit()
        flash('Đã đổi tên danh mục.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@admin_required
def category_delete(cat_id):
    cat = db.get_or_404(Category, cat_id)
    if cat.books:
        flash(f'Không thể xóa “{cat.name}” vì còn {len(cat.books)} sách đang phân loại.', 'danger')
    else:
        name = cat.name
        db.session.delete(cat)
        record_audit('Xóa danh mục', f"Xóa danh mục '{name}'", current_user.id)
        db.session.commit()
        flash(f'Đã xóa danh mục “{name}”.', 'success')
    return redirect(url_for('admin.categories'))
