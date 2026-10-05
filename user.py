"""Blueprint khu người dùng — Bước 3: trang chủ, tìm kiếm, lọc, chi tiết sách, đánh giá."""
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
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


# Bộ lọc theo tâm trạng đọc sách (Reading Mood Matcher)
MOODS = {
    'healing': {
        'label': 'Cần chữa lành',
        'desc': 'Sách nhẹ nhàng, tản văn cho ngày dài mệt mỏi.',
        'icon': 'bi-heart',
        'phrase': 'Cần chữa lành sau một ngày mệt mỏi',
    },
    'night': {
        'label': 'Đọc hết trong đêm',
        'desc': 'Sách mỏng, trinh thám dồn dập — đọc một mạch tới sáng.',
        'icon': 'bi-moon-stars',
        'phrase': 'Đọc hết trong một đêm',
    },
    'morning': {
        'label': 'Cà phê sáng T7',
        'desc': 'Sách tư duy, nghệ thuật nhâm nhi cuối tuần.',
        'icon': 'bi-cup-hot',
        'phrase': 'Uống cà phê sáng thứ Bảy',
    },
}


@user_bp.route('/')
def home():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    status = request.args.get('status', '')
    if status not in ('in', 'out'):
        status = ''
    mood = request.args.get('mood', '').strip()
    if mood not in MOODS:
        mood = ''
    view = request.args.get('view', '').strip()
    if view not in ('shelf', 'grid'):
        view = 'grid'

    query = Book.query
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if mood:
        query = query.filter(Book.mood == mood)

    books = query.order_by(Book.title).all()
    if status == 'in':
        books = [b for b in books if b.in_stock]
    elif status == 'out':
        books = [b for b in books if not b.in_stock]

    categories = Category.query.order_by(Category.name).all()
    filtering = bool(q or category_id or status or mood)

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

    # Trạng thái yêu cầu của user hiện tại theo từng cuốn (1 query cho cả trang)
    # Dùng trong book_card để nút Mượn / Xếp hàng phản ánh đúng trạng thái thật.
    active_statuses = {}
    if current_user.is_authenticated:
        active_statuses = dict(
            db.session.query(BorrowRequest.book_id, BorrowRequest.status)
            .filter(
                BorrowRequest.user_id == current_user.id,
                BorrowRequest.status.in_(['pending', 'approved', 'return_pending']),
            )
            .all()
        )

    return render_template(
        'user/index.html',
        books=books,
        grouped=grouped,
        categories=categories,
        q=q,
        category_id=category_id,
        status=status,
        mood=mood,
        moods=MOODS,
        view=view,
        active_statuses=active_statuses,
        filtering=filtering,
        stats=stats,
    )


def _human_queue(book):
    """Thông tin hàng chờ 'người thật' cho một cuốn sách: ai đang giữ,
    còn bao nhiêu ngày trả, và có bao nhiêu người đang xếp hàng chờ."""
    holder = (
        BorrowRequest.query.filter(
            BorrowRequest.book_id == book.id,
            BorrowRequest.status.in_(['approved', 'return_pending']),
        )
        .order_by(BorrowRequest.requested_at)
        .first()
    )
    waiting = BorrowRequest.query.filter(
        BorrowRequest.book_id == book.id,
        BorrowRequest.status == 'pending',
    ).count()

    holder_name, days_left = None, None
    if holder is not None:
        holder_name = holder.user.username
        if holder.due_date:
            days_left = (holder.due_date.date() - datetime.now().date()).days
        else:
            days_left = BORROW_DAYS
    return {'holder': holder_name, 'days_left': days_left, 'waiting': waiting}


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
        queue=_human_queue(book),
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


BORROW_DAYS = 14


@user_bp.route('/cho/<int:book_id>', methods=['POST'])
@login_required
def join_waitlist(book_id):
    """Xếp hàng chờ mượn sách khi hết bản — Human Queue.
    Tạo phiếu 'pending'; thủ thư sẽ duyệt theo thứ tự khi có bản trả về kho."""
    book = db.get_or_404(Book, book_id)
    next_url = request.args.get('next') or request.referrer or url_for(
        'user.book_detail', book_id=book.id
    )

    if book.in_stock:
        flash(f'“{book.title}” hiện còn bản trên kệ — hãy bấm Mượn ngay.', 'info')
        return redirect(next_url)

    if _active_request(current_user, book_id):
        flash(f'Bạn đã có yêu cầu cho “{book.title}” đang trong tiến trình xử lý.', 'info')
    else:
        db.session.add(
            BorrowRequest(
                user_id=current_user.id,
                book_id=book.id,
                status=BorrowRequest.PENDING,
                requested_at=datetime.now(),
                note='Xếp hàng chờ (sách đang hết bản)',
            )
        )
        db.session.commit()
        position = BorrowRequest.query.filter_by(
            book_id=book.id, status=BorrowRequest.PENDING
        ).count()
        flash(
            f'Đã xếp hàng chờ “{book.title}”. Bạn đứng thứ {position} trong hàng chờ — '
            'khi có bản trả về, thủ thư sẽ duyệt theo thứ tự.',
            'success',
        )
    return redirect(next_url)


@user_bp.route('/gio')
def cart():
    books = [b for b in (db.session.get(Book, i) for i in _cart()) if b is not None]
    return render_template('user/cart.html', books=books, max_items=MAX_CART_ITEMS)


@user_bp.route('/gio/gia/<int:book_id>', methods=['POST'])
@login_required
def remove_from_cart(book_id):
    _save_cart([i for i in _cart() if i != book_id])
    flash('Đã loại sách khỏi giỏ mượn.', 'info')
    return redirect(request.referrer or url_for('user.cart'))


@user_bp.route('/gio/ghi', methods=['POST'])
@login_required
def submit_borrow():
    ids = _cart()
    if not ids:
        flash('Giỏ mượn đang trống, bạn không thể gửi yêu cầu.', 'warning')
        return redirect(url_for('user.cart'))

    created, skipped = 0, []
    for book_id in ids:
        book = db.session.get(Book, book_id)
        if book is None:
            continue
        if not book.in_stock:
            skipped.append(f'“{book.title}” đã hết bản khả dụng.')
            continue
        if _active_request(current_user, book_id):
            skipped.append(f'“{book.title}” đã có yêu cầu đang xử lý.')
            continue
        db.session.add(
            BorrowRequest(
                user_id=current_user.id,
                book_id=book_id,
                status=BorrowRequest.PENDING,
                requested_at=datetime.now(),
            )
        )
        created += 1

    if created:
        _save_cart([])
        db.session.commit()
        flash(f'Đã gửi {created} yêu cầu mượn. Quản trị viên sẽ xem xét sớm!', 'success')
    else:
        db.session.rollback()
        flash('Không thể gửi yêu cầu: các cuốn trong giỏ hiện không khả dụng.', 'danger')
    for msg in skipped:
        flash(msg, 'warning')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/tu-sach')
@login_required
def dashboard():
    active = (
        BorrowRequest.query.filter(
            BorrowRequest.user_id == current_user.id,
            BorrowRequest.status.in_(['pending', 'approved', 'return_pending']),
        ).order_by(BorrowRequest.requested_at.desc()).all()
    )
    history = (
        BorrowRequest.query.filter(
            BorrowRequest.user_id == current_user.id,
            BorrowRequest.status.in_(['returned', 'rejected']),
        )
        .order_by(
            db.func.coalesce(
                BorrowRequest.returned_at, BorrowRequest.decided_at
            ).desc()
        )
        .all()
    )
    counts = {
        'borrowing': sum(1 for r in active if r.status in ('approved', 'return_pending')),
        'pending': sum(1 for r in active if r.status == 'pending'),
        'returned': BorrowRequest.query.filter(
            BorrowRequest.user_id == current_user.id,
            BorrowRequest.status == 'returned',
        ).count(),
    }
    return render_template(
        'user/dashboard.html', active=active, history=history, counts=counts
    )


@user_bp.route('/tu-sach/tra/<int:req_id>', methods=['POST'])
@login_required
def request_return(req_id):
    req = db.session.get(BorrowRequest, req_id)
    if req is None or req.user_id != current_user.id:
        abort(404)
    if req.status != 'approved':
        flash('Chỉ có thể yêu cầu trả sách khi đang được duyệt mượn.', 'warning')
    else:
        req.status = 'return_pending'
        db.session.commit()
        flash(
            f'Đã ghi nhận yêu cầu trả “{req.book.title}”. '
            'Quản trị viên sẽ xác nhận khi nhận được sách.',
            'success',
        )
    return redirect(url_for('user.dashboard'))
