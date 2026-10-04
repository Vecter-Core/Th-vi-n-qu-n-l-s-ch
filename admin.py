"""Blueprint khu quản trị — sẽ được hoàn thiện đầy đủ ở Bước 5 & 6."""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def dashboard():
    return (
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
        '<title>Quản trị – Thư viện Số</title></head>'
        '<body style="font-family:sans-serif;padding:4rem">'
        '<h1>🛡️ Trang quản trị</h1>'
        '<p>Đang xây dựng giao diện quản trị...</p>'
        '<a href="/">← Về trang chủ</a>'
        '</body></html>'
    )
