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

# Bộ màu (đầu, cuối) cho ảnh bìa SVG — tông trầm, giống bìa sách in thực tế
PALETTES = [
    ('#243447', '#3d5670'),  # 1 - xanh thép
    ('#5e2a22', '#8a4a3d'),  # 2 - oxblood
    ('#2f3a3a', '#556565'),  # 3 - xám than
    ('#275245', '#41795f'),  # 4 - xanh rừng
    ('#7a4a1f', '#a86f35'),  # 5 - hổ phách đậm
    ('#43305e', '#6a4f8b'),  # 6 - tím than
    ('#1f4e5f', '#357084'),  # 7 - xanh biển sẫm
    ('#26282b', '#5a5f66'),  # 8 - đen chì
    ('#1e4d43', '#397f68'),  # 9 - xanh ngọc trầm
    ('#4a3324', '#7a5c41'),  # 10 - nâu cà phê
    ('#16233f', '#2c4470'),  # 11 - xanh đêm
    ('#5a2333', '#8a4055'),  # 12 - rượu vang
]

COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'covers')

# ---------------------------------------------------------------------------
# Dữ liệu "xúc giác" & nhân văn cho từng cuốn (Editorial & Tactile Design)
# Khóa mood: healing (chữa lành) | night (đọc hết trong một đêm) | morning (cà phê T7)
# ---------------------------------------------------------------------------
BOOK_EXTRAS = {
    'Introduction to Algorithms': {
        'mood': 'night', 'pages': 1312, 'times_borrowed': 47,
        'spine_color': '#2f4858',
        'condition_note': 'Gáy hơi lỏng ở trang 812 — đã dán lại bằng băng keo trong. Vài dòng gạch chân bút chì ở chương Dynamic Programming.',
        'librarian_note': 'Chương 3 là xương sống. Hiểu recursion ở đây thì cả cuốn nhẹ như lông hồng.',
        'librarian_note_by': 'Thủ thư Nam',
    },
    'Clean Code': {
        'mood': 'night', 'pages': 464, 'times_borrowed': 89,
        'spine_color': '#33684f',
        'condition_note': 'Góc bìa trước quăn nhẹ. Một trang ở chương 3 có vết cà phê phai — ai đó đã đọc khi thức khuya.',
        'librarian_note': 'Đừng đọc từ đầu đến cuối. Mở một chương, viết lại code của mình, rồi mới lật trang.',
        'librarian_note_by': 'Thủ thư Hà',
    },
    'The Art of Computer Programming': {
        'mood': 'night', 'pages': 650, 'times_borrowed': 15,
        'spine_color': '#4a3b5c',
        'condition_note': 'Cuốn này nặng và dày, gáy đã sờn đúng giữa. Đọc nhanh không được — đây là sách để mở ra tra.',
        'librarian_note': 'Sách này không phải để đọc, là để chiêm nghiệm. Mang theo một tách cà phê thật đậm.',
        'librarian_note_by': 'Thủ thư Nam',
    },
    'A First Course in Probability': {
        'mood': 'morning', 'pages': 640, 'times_borrowed': 34,
        'spine_color': '#7a4a1f',
        'condition_note': 'Trang 156 có công thức được chép lại bằng bút chì dự phòng. Bìa sau hơi bong keo.',
        'librarian_note': 'Bài tập cuối chương dễ mắc bẫy. Làm xong nhớ soát lại đáp án, đừng tự tin quá.',
        'librarian_note_by': 'Thủ thư Hà',
    },
    'Nhà Giả Kim': {
        'mood': 'healing', 'pages': 192, 'times_borrowed': 126,
        'spine_color': '#b5651d',
        'condition_note': 'Góc bìa trên quẹn nhẹ, gáy ngả màu thời gian. Cuốn này đã qua tay rất nhiều người.',
        'librarian_note': 'Chương 4 cuốn này sẽ làm bạn khóc. Nên đọc vào một chiều mưa.',
        'librarian_note_by': 'Thủ thư Nam',
    },
    'Sapiens: Lược sử loài người': {
        'mood': 'morning', 'pages': 443, 'times_borrowed': 98,
        'spine_color': '#8a4a3d',
        'condition_note': 'Một trang giữa được gấp mép đánh dấu. Bìa trong còn thơm mùi giấy mới.',
        'librarian_note': 'Đọc chương “Cách mạng nhận thức” khi đầu óc tỉnh táo nhất. Thay đổi góc nhìn hẳn.',
        'librarian_note_by': 'Thủ thư Hà',
    },
    'Đắc Nhân Tâm': {
        'mood': 'healing', 'pages': 300, 'times_borrowed': 154,
        'spine_color': '#1f4e5f',
        'condition_note': 'Gáy đã nhuốm màu dầu tay của trăm đôi tay cầm. Mực ở trang 40 hơi nhòe.',
        'librarian_note': 'Mẹ mình từng tặng mình cuốn này. Vết mực ở trang 40 là của bà ấy.',
        'librarian_note_by': 'Thủ thư Nam',
    },
    'Tư duy nhanh và chậm': {
        'mood': 'morning', 'pages': 512, 'times_borrowed': 76,
        'spine_color': '#26282b',
        'condition_note': 'Cuốn này dày nên hay bị ngốn bìa. Trang 201 có dòng gạch chân “đừng tin vào trực giác”.',
        'librarian_note': 'Hệ thống 1 sẽ muốn bạn lướt nhanh. Hãy ép Hệ thống 2 chạy thêm chút nữa.',
        'librarian_note_by': 'Thủ thư Hà',
    },
    'Kafka bên bờ biển': {
        'mood': 'healing', 'pages': 500, 'times_borrowed': 63,
        'spine_color': '#5a2333',
        'condition_note': 'Có một nhành lá ép khô còn sót lại ở trang 300 — giữ lại cho vui.',
        'librarian_note': 'Đừng cố hiểu hết. Cứ để Murakami dẫn bạn đi, đến cuối cùng tự khắc rõ.',
        'librarian_note_by': 'Thủ thư Nam',
    },
    'Tội ác và hình phạt': {
        'mood': 'night', 'pages': 671, 'times_borrowed': 41,
        'spine_color': '#43305e',
        'condition_note': 'Gáy nứt ở trang 199. Đọc cuốn này nhớ đánh dấu chỗ dừng, khó dứt ra lắm.',
        'librarian_note': 'Đọc chương một lúc nửa đêm sẽ ám ảnh bạn cả tuần. Chưa cảnh báo trước đấy nhé.',
        'librarian_note_by': 'Thủ thư Hà',
    },
    'Vũ trụ': {
        'mood': 'morning', 'pages': 400, 'times_borrowed': 57,
        'spine_color': '#16233f',
        'condition_note': 'Ảnh minh họa trang 42 đã hơi bong mép vì được lật đi lật lại nhiều lần.',
        'librarian_note': 'Carl Sagan viết để bạn ngước lên nhìn trời đêm. Làm ơn hãy ngước lên.',
        'librarian_note_by': 'Thủ thư Nam',
    },
    'Thiên tài bên trái, kẻ điên bên phải': {
        'mood': 'healing', 'pages': 336, 'times_borrowed': 72,
        'spine_color': '#1e4d43',
        'condition_note': 'Bìa sau có vài vết bút bi loang. Cuốn này từng nằm trên bàn làm việc của một sinh viên tâm lý.',
        'librarian_note': 'Cuốn này dễ hơn tên nó tưởng. Đọc xong bạn sẽ dịu dàng hơn với người khác.',
        'librarian_note_by': 'Thủ thư Hà',
    },
}



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
    """Vẽ một tấm ảnh bìa SVG 400x560 kiểu bìa sách in (chữ serif, khung mảnh)."""
    c1, c2 = palette
    title_lines = _wrap(book['title'], width=14)
    line_h = 40
    start_y = 268 - (len(title_lines) - 1) * (line_h // 2)
    title = '\n'.join(
        '  <text x="200" y="{y}" text-anchor="middle" '
        'font-family="Georgia, \'Times New Roman\', serif" font-size="32" font-weight="700" '
        'fill="#f5f2ea">{line}</text>'.format(y=start_y + i * line_h, line=_esc(line))
        for i, line in enumerate(title_lines)
    )
    author_y = start_y + len(title_lines) * line_h + 34
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
        '  <rect x="14" y="14" width="372" height="532" fill="none" '
        'stroke="#f5f2ea" stroke-opacity="0.35" stroke-width="1.5"/>\n'
        f'  <text x="200" y="70" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" '
        'font-size="12" letter-spacing="4" fill="#f5f2ea" fill-opacity="0.72">'
        f'{_esc(book["category"].upper())}</text>\n'
        f'{title}\n'
        f'  <line x1="158" y1="{author_y - 18}" x2="242" y2="{author_y - 18}" '
        'stroke="#f5f2ea" stroke-opacity="0.55" stroke-width="1.5"/>\n'
        f'  <text x="200" y="{author_y}" text-anchor="middle" '
        'font-family="Georgia, \'Times New Roman\', serif" font-size="18" font-style="italic" '
        f'fill="#f5f2ea" fill-opacity="0.95">{_esc(book["author"])}</text>\n'
        '  <text x="200" y="524" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" '
        'font-size="10" letter-spacing="3" fill="#f5f2ea" fill-opacity="0.45">THƯ VIỆN SỐ</text>\n'
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


def enrich_books():
    """Nạp dữ liệu xúc giác (mood, tình trạng, ghi chú viết tay, màu gáy) cho sách
    đã có trong CSDL. Chỉ ghi đè khi ô còn trống — an toàn khi chạy lại."""
    updated = 0
    for title, extra in BOOK_EXTRAS.items():
        book = Book.query.filter_by(title=title).first()
        if book is None:
            continue
        changed = False
        for field, value in extra.items():
            current = getattr(book, field, None)
            # Ghi đè khi ô trống; riêng số (pages, times_borrowed) cũng ghi khi = 0
            if current in (None, '', 0):
                setattr(book, field, value)
                changed = True
        if book.spine_color in (None, ''):
            book.spine_color = extra.get('spine_color', '')
        if changed:
            updated += 1
    if updated:
        db.session.commit()
    return updated


def ensure_default_accounts():
    """Đảm bảo 2 tài khoản mặc định (admin & user) luôn luôn tồn tại trong hệ thống."""
    # 1. Tài khoản Quản trị viên: admin / admin123
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@thuvien.local',
            role='admin',
            is_active=True,
        )
        admin.set_password('admin123')
        db.session.add(admin)
    else:
        admin.role = 'admin'
        admin.is_active = True
        if not admin.check_password('admin123'):
            admin.set_password('admin123')

    # 2. Tài khoản Độc giả: user / user123
    member = User.query.filter_by(username='user').first()
    if not member:
        member = User(
            username='user',
            email='user@thuvien.local',
            role='user',
            is_active=True,
        )
        member.set_password('user123')
        db.session.add(member)
    else:
        member.role = 'user'
        member.is_active = True
        if not member.check_password('user123'):
            member.set_password('user123')

    db.session.commit()
    return admin, member


def seed_if_empty():
    """Seed dữ liệu mẫu khi CSDL trống. Đảm bảo ảnh bìa và tài khoản mặc định."""
    ensure_default_accounts()

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
        extra = BOOK_EXTRAS.get(data['title'], {})
        for field in ('mood', 'pages', 'condition_note', 'times_borrowed',
                      'librarian_note', 'librarian_note_by', 'spine_color'):
            if field in extra:
                setattr(book, field, extra[field])
        db.session.add(book)

    db.session.commit()
    print(
        f'[Seed] Đã tạo {len(SEED_BOOKS)} cuốn sách, '
        f'{len(categories)} danh mục, và 2 tài khoản mặc định (admin, user).'
    )
    return True

