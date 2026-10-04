"""Khởi tạo dữ liệu mẫu: 12 đầu sách thực tế, danh mục, tài khoản admin & ảnh bìa."""
import os
from datetime import datetime

from extensions import db
from models import Book, Category, User

SEED_BOOKS = [
    {
        'title': 'Introduction to Algorithms',
        'author': 'Thomas H. Cormen',
        'category': 'Khoa học máy tính',
        'quantity': 5,
        'description': 'Kinh thánh về giải thuật cho kỹ sư phần mềm.',
    },
    {
        'title': 'Clean Code',
        'author': 'Robert C. Martin',
        'category': 'Lập trình',
        'quantity': 8,
        'description': 'Nghệ thuật viết mã nguồn sạch và dễ bảo trì.',
    },
    {
        'title': 'The Art of Computer Programming',
        'author': 'Donald Knuth',
        'category': 'Khoa học máy tính',
        'quantity': 3,
        'description': 'Công trình vĩ đại về nền tảng khoa học máy tính.',
    },
    {
        'title': 'A First Course in Probability',
        'author': 'Sheldon Ross',
        'category': 'Toán học',
        'quantity': 6,
        'description': 'Sách gối đầu giường về xác suất thống kê.',
    },
    {
        'title': 'Nhà Giả Kim',
        'author': 'Paulo Coelho',
        'category': 'Văn học',
        'quantity': 10,
        'description': 'Hành trình theo đuổi vận mệnh của chàng chăn cừu.',
    },
    {
        'title': 'Sapiens: Lược sử loài người',
        'author': 'Yuval Noah Harari',
        'category': 'Lịch sử',
        'quantity': 7,
        'description': 'Hành trình tiến hóa của loài người qua các thời kỳ.',
    },
    {
        'title': 'Đắc Nhân Tâm',
        'author': 'Dale Carnegie',
        'category': 'Kỹ năng sống',
        'quantity': 12,
        'description': 'Nghệ thuật thu phục lòng người và giao tiếp đỉnh cao.',
    },
    {
        'title': 'Tư duy nhanh và chậm',
        'author': 'Daniel Kahneman',
        'category': 'Tâm lý học',
        'quantity': 5,
        'description': 'Khám phá hai hệ thống tư duy chi phối quyết định.',
    },
    {
        'title': 'Kafka bên bờ biển',
        'author': 'Haruki Murakami',
        'category': 'Văn học',
        'quantity': 4,
        'description': 'Kiệt tác văn học đậm chất hiện thực huyền ảo Nhật Bản.',
    },
    {
        'title': 'Tội ác và hình phạt',
        'author': 'Fyodor Dostoevsky',
        'category': 'Văn học kinh điển',
        'quantity': 3,
        'description': 'Đằng xé nội tâm sâu sắc về đạo đức và tội lỗi.',
    },
    {
        'title': 'Vũ trụ',
        'author': 'Carl Sagan',
        'category': 'Khoa học vũ trụ',
        'quantity': 6,
        'description': 'Khám phá không gian bao la và lịch sử khoa học.',
    },
    {
        'title': 'Thiên tài bên trái, kẻ điên bên phải',
        'author': 'Cao Minh',
        'category': 'Tâm lý học',
        'quantity': 8,
        'description': 'Góc nhìn độc đáo từ các bệnh nhân tâm thần viện.',
    },
]

# Bộ màu (đầu, cuối) cho ảnh bìa SVG của từng cuốn sách
PALETTES = [
    ('#1a237e', '#3949ab'),  # 1 - xanh chàm
    ('#c62828', '#ef5350'),  # 2 - đỏ
    ('#263238', '#546e7a'),  # 3 - xám than
    ('#00695c', '#26a69a'),  # 4 - xanh rêu
    ('#e65100', '#ffb74d'),  # 5 - cam hổ phách
    ('#4a148c', '#8e24aa'),  # 6 - tím
    ('#01579b', '#4fc3f7'),  # 7 - xanh dương
    ('#212121', '#757575'),  # 8 - đen - xám
    ('#004d40', '#00897b'),  # 9 - xanh nước biển thẫm
    ('#1b1b1b', '#5d4037'),  # 10 - nâu đen
    ('#0a0e33', '#1a2980'),  # 11 - xanh đêm
    ('#880e4f', '#d81b60'),  # 12 - hồng cánh sen
]

COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'covers')


def _esc(text):
    """Escape các ký tự XML đặc biệt."""
    return (
        text.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


def _wrap(text, width=16):
    """Tách tiêu đề thành các dòng ngắn để đặt lên ảnh bìa."""
    words = text.split()
    lines, current = [], ''
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f'{current} {word}'.strip()
    if current:
        lines.append(current)
    return lines


def make_cover_svg(index, book, palette, out_path):
    """Vẽ một tấm ảnh bìa SVG 400x560 và lưu vào out_path."""
    c1, c2 = palette
    title_lines = _wrap(book['title'])
    line_h = 42
    start_y = 250 - (len(title_lines) - 1) * (line_h // 2)
    title = '\n'.join(
        '  <text x="200" y="{y}" text-anchor="middle" '
        'font-family="Segoe UI, Arial, sans-serif" font-size="30" font-weight="700" '
        'fill="#ffffff">{line}</text>'.format(y=start_y + i * line_h, line=_esc(line))
        for i, line in enumerate(title_lines)
    )
    author_y = start_y + len(title_lines) * line_h + 26
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560">\n'
        '  <defs>\n'
        '    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">\n'
        f'      <stop offset="0%" stop-color="{c1}"/>\n'
        f'      <stop offset="100%" stop-color="{c2}"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="400" height="560" fill="url(#bg)"/>\n'
        '  <circle cx="340" cy="80" r="140" fill="#ffffff" opacity="0.07"/>\n'
        '  <circle cx="40" cy="500" r="160" fill="#000000" opacity="0.10"/>\n'
        '  <rect x="18" y="18" width="364" height="524" rx="12" fill="none" '
        'stroke="#ffffff" stroke-opacity="0.4" stroke-width="2"/>\n'
        '  <text x="200" y="64" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" '
        'font-size="15" letter-spacing="6" fill="#ffffff" fill-opacity="0.8">THƯ VIỆN SỐ</text>\n'
        f'{title}\n'
        f'  <line x1="150" y1="{author_y - 14}" x2="250" y2="{author_y - 14}" '
        'stroke="#ffffff" stroke-opacity="0.6" stroke-width="2"/>\n'
        f'  <text x="200" y="{author_y}" text-anchor="middle" '
        'font-family="Segoe UI, Arial, sans-serif" font-size="20" '
        f'fill="#ffffff" fill-opacity="0.95">{_esc(book["author"])}</text>\n'
        '  <text x="200" y="512" text-anchor="middle" '
        'font-family="Segoe UI, Arial, sans-serif" font-size="14" '
        f'fill="#ffffff" fill-opacity="0.75">{_esc(book["category"])}</text>\n'
        '</svg>\n'
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(svg)


def generate_all_covers():
    """Tạo ảnh bìa cho 12 cuốn sách + 1 ảnh bìa mặc định."""
    make_cover_svg(
        0,
        {'title': 'Thư viện Số', 'author': 'Ảnh minh họa', 'category': 'Bìa dự phòng'},
        ('#37474f', '#607d8b'),
        os.path.join(COVERS_DIR, 'default.svg'),
    )
    for idx, book in enumerate(SEED_BOOKS, start=1):
        make_cover_svg(
            idx,
            book,
            PALETTES[idx - 1],
            os.path.join(COVERS_DIR, f'book_{idx}.svg'),
        )


def seed_if_empty():
    """Seed dữ liệu mẫu khi CSDL trống. Trả về True nếu đã tạo mới."""
    if Book.query.count() > 0:
        return False

    generate_all_covers()

    categories = {}
    for idx, data in enumerate(SEED_BOOKS, start=1):
        cat_name = data['category']
        if cat_name not in categories:
            cat = Category(name=cat_name)
            db.session.add(cat)
            db.session.flush()
            categories[cat_name] = cat

        book = Book(
            title=data['title'],
            author=data['author'],
            description=data['description'],
            quantity=data['quantity'],
            category=categories[cat_name],
            cover_url=f'/static/covers/book_{idx}.svg',
            created_at=datetime.now(),
        )
        db.session.add(book)

    admin = User(username='admin', email='admin@thuvien.local', role='admin', is_active=True)
    admin.set_password('admin123')
    db.session.add(admin)

    db.session.commit()
    print(
        f'[Seed] Đã tạo {len(SEED_BOOKS)} cuốn sách, '
        f'{len(categories)} danh mục, tài khoản admin.'
    )
    return True
