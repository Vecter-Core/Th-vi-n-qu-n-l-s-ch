"""Blueprint xác thực — sẽ được hoàn thiện đầy đủ ở Bước 2."""
from flask import Blueprint, redirect, url_for

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    return (
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
        '<title>Đăng nhập – Thư viện Số</title></head>'
        '<body style="font-family:sans-serif;padding:4rem">'
        '<h1>📚 Thư viện Số</h1>'
        '<p>Chức năng đăng nhập sẽ được xây dựng ở Bước 2.</p>'
        '<a href="/">← Về trang chủ</a>'
        '</body></html>'
    )


@auth_bp.route('/register')
def register():
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    return redirect(url_for('user.home'))
