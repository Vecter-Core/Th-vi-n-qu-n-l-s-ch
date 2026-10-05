"""
Thư viện Số — Ứng dụng quản lý thư viện số (Flask + SQLite/SQLAlchemy + Bootstrap 5)

Chạy ứng dụng:   python app.py
Truy cập:        http://127.0.0.1:5000
Quản trị viên:   admin / admin123   (đăng nhập vào khu quản trị /admin)
Thành viên:      user  / user123    (đăng nhập vào giao diện người dùng)
"""
import os
import sys
from datetime import datetime


def _force_utf8_stdio():
    """Mặc định, console Windows dùng mã cp1252 khiến việc in chữ tiếng Việt
    gây UnicodeEncodeError. Ép stdout/stderr ra UTF-8 (kiểu thay thế ký tự lạ)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError, OSError):
            pass


_force_utf8_stdio()

from flask import (  # noqa: E402
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)
from flask_login import current_user, logout_user

from extensions import db, login_manager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nhãn & màu (Bootstrap) cho các trạng thái phiếu mượn — dùng chung trong template
STATUS_LABELS = {
    'pending': 'Chờ duyệt',
    'approved': 'Đang mượn',
    'rejected': 'Đã từ chối',
    'return_pending': 'Chờ xác nhận trả',
    'returned': 'Đã trả',
}
STATUS_COLORS = {
    'pending': 'warning',
    'approved': 'primary',
    'rejected': 'secondary',
    'return_pending': 'info',
    'returned': 'success',
}


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'thu-vien-so-2026-mat-kha-bi-mat')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'library.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để sử dụng tính năng này.'
    login_manager.login_message_category = 'info'

    # Đăng ký blueprint (import bên trong hàm để tránh import tuần hoàn)
    from auth import auth_bp
    from user import user_bp
    from admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models import User
        except ImportError:
            # Bước khởi tạo đầu tiên: models.py chưa có
            return None
        return db.session.get(User, int(user_id))

    @app.before_request
    def invalidate_locked_accounts():
        """Tự động đăng xuất khi tài khoản trong phiên đã bị khóa."""
        if current_user.is_authenticated and not getattr(current_user, 'is_active', True):
            logout_user()
            flash('Tài khoản của bạn đã bị khóa hoặc vô hiệu hóa.', 'danger')
            return redirect(url_for('auth.login'))

    @app.context_processor
    def inject_globals():
        def _has_endpoint(endpoint):
            return endpoint in current_app.view_functions

        return {
            'cart_count': len(session.get('cart', [])),
            'status_labels': STATUS_LABELS,
            'status_colors': STATUS_COLORS,
            'now': lambda: datetime.now(),
            'has_endpoint': _has_endpoint,
        }

    @app.template_filter('fmt_date')
    def fmt_date(value):
        return value.strftime('%d/%m/%Y') if value else '—'

    @app.template_filter('fmt_datetime')
    def fmt_datetime(value):
        return value.strftime('%d/%m/%Y %H:%M') if value else '—'

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from seed import ensure_default_accounts, seed_if_empty
        seed_if_empty()
        ensure_default_accounts()
    app.run(host='127.0.0.1', port=5000, debug=True)

