"""Blueprint khu người dùng — sẽ được hoàn thiện đầy đủ ở Bước 3 & 4."""
from flask import Blueprint

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
def home():
    return (
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
        '<title>Thư viện Số</title></head>'
        '<body style="font-family:sans-serif;padding:4rem">'
        '<h1>📚 Thư viện Số</h1>'
        '<p>Đang xây dựng giao diện người dùng...</p>'
        '</body></html>'
    )
