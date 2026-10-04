"""Blueprint xác thực: đăng ký, đăng nhập, đăng xuất."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            error = 'Tên đăng nhập hoặc mật khẩu không chính xác.'
        elif not user.is_active:
            error = 'Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.'
        else:
            login_user(user)
            flash(f'Đăng nhập thành công! Xin chào, {user.username}.', 'success')
            next_url = request.args.get('next')
            if not next_url or not next_url.startswith('/'):
                next_url = (
                    url_for('admin.dashboard') if user.is_admin else url_for('user.home')
                )
            return redirect(next_url)

    return render_template('auth/login.html', error=error, next=request.args.get('next', ''))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not (3 <= len(username) <= 30):
            error = 'Tên đăng nhập phải từ 3 đến 30 ký tự.'
        elif email and '@' not in email:
            error = 'Vui lòng nhập email hợp lệ.'
        elif len(password) < 6:
            error = 'Mật khẩu phải có ít nhất 6 ký tự.'
        elif password != confirm:
            error = 'Xác nhận mật khẩu không khớp.'
        elif User.query.filter_by(username=username).first() is not None:
            error = 'Tên đăng nhập đã tồn tại.'
        elif email and User.query.filter_by(email=email).first() is not None:
            error = 'Email này đã được đăng ký.'
        else:
            user = User(username=username, email=email or None)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Tạo tài khoản thành công. Chào mừng {username} đến với thư viện!', 'success')
            return redirect(url_for('user.home'))

    return render_template('auth/register.html', error=error)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất khỏi hệ thống.', 'info')
    return redirect(url_for('user.home'))
