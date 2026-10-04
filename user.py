"""Blueprint khu người dùng — Bước 3: trang chủ, tìm kiếm, lọc, chi tiết sách, đánh giá."""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from extensions import db
from models import Book, BorrowRequest, Category, Review

user_bp = Blueprint('user', __name__)

MAX_CART_ITEMS = 3


def _cart():
    return [int(i) for i in session.get('cart', [])]


def _save_cart(ids):
    if ids:
        session['cart'] = ids
    else:
        session.pop('cart', None)


def _active_request(user, book_id):
    """Yêu cầu mượn đang trong tiến trình (pending / approved / return_pending)."""
    return (
        BorrowRequest.query.filter(
            BorrowRequest.user_id == user.id,
            BorrowRequest.book_id == book_id,
            BorrowRequest.status.in_(['pending', 'approved', 'return_pending']),
        ).first()
    )


@user_bp.route('/')
def home():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    status = request.args.get('status', '')
    if status not in ('in', 'out'):
        status = ''

    query = Book.query
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))
    if category_id:
        query = query.filter(Book.category_id == category_id)

    books = query.order_by(Book.title).all()
    if status == 'in':
        books = [b for b in books if b.in_stock]
    elif status == 'out':
        books = [b for b in books if not b.in_stock]

    categories = Category.query.order_by(Category.name).all()
    filtering = bool(q or category_id or status)

    grouped = None
    if not filtering:
        buckets = {}
        for book in books:
            key = book.category.name if book.category else 'Chưa phân loại'
            buckets.setdefault(key, []).append(book)
        grouped = sorted(buckets.items(), key=lambda kv: len(kv[1]), reverse=True)

    stats = {
        'total_books': Book.query.count(),
        'total_copies': db.session.query(db.func.sum(Book.quantity)).scalar() or 0,
        'total_categories': len(categories),
    }

    return render_template(
        'user/index.html',
        books=books,
        grouped=grouped,
        categories=categories,
        q=q,
        category_id=category_id,
        status=status,
        filtering=filtering,
        stats=stats,
    )


@user_bp.route('/sach/<int:book_id>')
def book_detail(book_id):
    book = db.get_or_404(Book, book_id)
    reviews = book.reviews.order_by(Review.created_at.desc()).all()
    avg, count = book.average_rating
    active_request = (
        _active_request(current_user, book_id)
        if current_user.is_authenticated
        else None
    )
    my_review = (
        Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if current_user.is_authenticated
        else None
    )
    return render_template(
        'user/book_detail.html',
        book=book,
        reviews=reviews,
        avg=avg,
        count=count,
        active_request=active_request,
        my_review=my_review,
    )


@user_bp.route('/sach/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    book = db.get_or_404(Book, book_id)
    try:
        rating = int(request.form.get('rating', 0))
    except (TypeError, ValueError):
        rating = 0
    comment = request.form.get('comment', '').strip()

    if not (1 <= rating <= 5):
        flash('Vui lòng chọn số sao từ 1 đến 5.', 'warning')
        return redirect(url_for('user.book_detail', book_id=book_id))
    if len(comment) < 5:
        flash('Vui lòng viết nhận xét ngắn (tối thiểu 5 ký tự).', 'warning')
        return redirect(url_for('user.book_detail', book_id=book_id))

    review = Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if review:
        review.rating = rating
        review.comment = comment
        review.created_at = datetime.now()
        flash('Đã cập nhật đánh giá của bạn.', 'success')
    else:
        db.session.add(
            Review(user_id=current_user.id, book_id=book_id, rating=rating, comment=comment)
        )
        flash('Cảm ơn bạn đã chia sẻ đánh giá!', 'success')
    db.session.commit()
    return redirect(url_for('user.book_detail', book_id=book_id))


@user_bp.route('/gio/them/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = db.get_or_404(Book, book_id)

    if not book.in_stock:
        flash(f'“{book.title}” hiện đã hết bản cho mượn.', 'warning')
    elif book.id in _cart():
        flash(f'“{book.title}” đã có sẵn trong giỏ mượn.', 'info')
    elif _active_request(current_user, book_id):
        flash(f'Bạn đã có yêu cầu mượn “{book.title}” đang trong tiến trình xử lý.', 'info')
    elif len(_cart()) >= MAX_CART_ITEMS:
        flash(f'Giỏ mượn chỉ chứa tối đa {MAX_CART_ITEMS} cuốn. '
              'Hãy gửi yêu cầu hoặc loại bớt trước khi thêm.', 'warning')
    else:
        _save_cart(_cart() + [book.id])
        flash(f'Đã thêm “{book.title}” vào giỏ mượn.', 'success')

    next_url = request.args.get('next')
    return redirect(next_url or request.referrer or url_for('user.home'))
