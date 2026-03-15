from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq
import re
from dotenv import load_dotenv
load_dotenv()
import os
import json
import csv

from io import StringIO

# JSON Database module
import json_db

# ================== CAU HINH & KHOI TAO ==================
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# Model routing - phan bo mo hinh theo task
CHAT_MODEL = os.getenv('CHAT_MODEL', 'qwen/qwen3-32b')          # Chat tutoring - chat luong tot
EVAL_MODEL = os.getenv('EVAL_MODEL', 'llama-3.1-8b-instant')    # Danh gia - nhanh, nhe
FALLBACK_MODEL = os.getenv('FALLBACK_MODEL', 'llama-3.3-70b-versatile')

print(f"[CONFIG] Chat: {CHAT_MODEL} | Eval: {EVAL_MODEL} | Fallback: {FALLBACK_MODEL}")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")

# Flask's built-in cookie sessions are used (no server-side session needed)

# ================== LEVEL-BASED PEDAGOGY ==================
def get_level_instruction(level):
    """Trả về hướng dẫn sư phạm tùy chỉnh theo trình độ học sinh"""
    instructions = {
        'Gioi': """
    [TRÌNH ĐỘ: GIỎI — Học sinh giỏi, tư duy tốt]
    - Giao tiếp như hai người cùng nghiên cứu: "Con đã nắm tốt rồi, hãy cùng đi sâu hơn nhé!"
    - Đặt câu hỏi ngược để thách thức tư duy: "Vậy nếu thay đổi điều kiện này thì sao?"
    - Giới thiệu kiến thức mở rộng, liên môn, ứng dụng thực tế nâng cao
    - Sử dụng thuật ngữ song ngữ tự nhiên, không cần dịch từng từ
    - Gợi ý bài tập tự luận, Olympic, hoặc vấn đề mở để học sinh tự khám phá
    - Độ khó từ vựng tiếng Anh: tương đương IELTS 5.0–6.0""",
        'Kha': """
    [TRÌNH ĐỘ: KHÁ — Học sinh khá, cần phát triển thêm]
    - Giảng dạy có cấu trúc: giải thích khái niệm → ví dụ minh họa → bài vận dụng
    - Khích lệ: "Con làm tốt lắm! Hãy thử thêm bài này nhé"
    - Đưa ra 1–2 câu hỏi mở rộng sau mỗi giải thích
    - Song ngữ: Giải thích bằng tiếng Việt trước, thêm thuật ngữ tiếng Anh kèm theo
    - Độ khó từ vựng tiếng Anh: tương đương IELTS 4.0–5.0""",
        'TB': """
    [TRÌNH ĐỘ: TRUNG BÌNH — Cần hướng dẫn từng bước]
    - Chia nhỏ vấn đề thành các bước nhỏ, dễ hiểu
    - Sử dụng ví dụ đơn giản, gần gũi đời sống hàng ngày
    - Dẫn dắt từ từ: "Bước 1: ...", "Bước 2: ..."
    - Nhắc lại kiến thức nền tảng trước khi giải bài mới
    - Song ngữ: Tiếng Việt là chính, chỉ thêm từ khóa tiếng Anh quan trọng
    - Độ khó từ vựng tiếng Anh: cơ bản, đơn giản""",
        'Yeu': """
    [TRÌNH ĐỘ: YẾU — Cần hỗ trợ đặc biệt]
    - Giảng giải cực kỳ đơn giản, như nói chuyện với trẻ nhỏ
    - Mỗi bước chỉ nêu 1 ý, kèm ví dụ cụ thể ngay
    - Sử dụng so sánh đời thường (VD: phản ứng hóa học giống như nấu ăn)
    - Không dùng thuật ngữ phức tạp, giải thích bằng ngôn ngữ bình dân
    - Động viên thường xuyên: "Đừng lo, thầy sẽ giúp con hiểu từng bước một!"
    - Song ngữ: Chỉ dùng tiếng Việt, thêm 1–2 từ tiếng Anh cơ bản nhất
    - Luôn kiểm tra lại: Con hiểu chưa? Thầy giải thích lại nhé!"""
    }
    return instructions.get(level, instructions['TB'])

# ================== DANH GIA NANG LUC ==================
def evaluate_student_level(history, subject='general'):
    recent_exchanges = "\n".join(history[-10:])
    recent_questions = "\n".join([msg for msg in history[-10:] if msg.startswith("\U0001f467")])

    subject_names = {
        'math': 'Toán học', 'physics': 'Vật lý',
        'chemistry': 'Hóa học', 'biology': 'Sinh học',
        'general': 'Khoa học Tự nhiên'
    }
    subject_name = subject_names.get(subject, 'Khoa học Tự nhiên')

    prompt = f"""Bạn là chuyên gia đánh giá năng lực học sinh THCS môn {subject_name}.

=== DỮ LIỆU PHÂN TÍCH ===
Lịch sử hỏi đáp gần nhất (bao gồm câu hỏi của học sinh và phản hồi của giáo viên):
{recent_exchanges}

Các câu hỏi riêng của học sinh:
{recent_questions}

=== ĐÁNH GIÁ THEO 5 TIÊU CHÍ ===

1. **Độ sâu kiến thức**: Học sinh hỏi ở mức nào? (nhận biết / thông hiểu / vận dụng / vận dụng cao). Có tự giải thích được khái niệm không?

2. **Tư duy logic**: Cách đặt câu hỏi có logic không? Có biết chia nhỏ vấn đề, suy luận từ tiên đề đến kết luận không?

3. **Năng lực song ngữ**: Sử dụng thuật ngữ khoa học tiếng Anh đúng/sai? Có tự tin hỏi bằng tiếng Anh không?

4. **Tự học và tư duy phản biện**: Học sinh có chủ động tìm hiểu sâu hơn, đặt câu hỏi mở rộng, hay chỉ xin đáp án?

5. **Điểm yếu và lỗi thường gặp**: Sai sót lặp lại (tính toán, khái niệm, đơn vị)? Lỗ hổng kiến thức nền tảng? Có cải thiện qua các lần hỏi không?

=== PHÂN LOẠI ===
- Gioi: Vận dụng cao, tư duy phản biện, song ngữ tốt, chủ động khám phá
- Kha: Thông hiểu tốt, có tư duy nhưng chưa sâu, song ngữ khá
- TB: Nhận biết kiến thức cơ bản, cần hướng dẫn từng bước, song ngữ hạn chế
- Yeu: Chưa nắm kiến thức nền tảng, hỏi lặp lại, khó diễn đạt

=== ĐỊNH DẠNG ĐẦU RA (BẮT BUỘC TUÂN THỦ) ===
Cap do: [Gioi/Kha/TB/Yeu]
Ly do: [200–300 từ. Phân tích cụ thể theo 5 tiêu chí trên. Nêu rõ điểm mạnh, điểm yếu, và 2–3 đề xuất cụ thể để giáo viên hỗ trợ học sinh tiến bộ.]
"""

    try:
        response = groq_client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        response_text = response.choices[0].message.content.strip()

        level_match = re.search(r'Cap do:\s*(Gioi|Kha|TB|Yeu)', response_text)
        if not level_match:
            level_match = re.search(r'\b(Gioi|Kha|TB|Yeu)\b', response_text)

        lydo_match = re.search(r'Ly do:\s*(.+)', response_text, re.DOTALL)

        level = level_match.group(1) if level_match else "TB"
        lydo = lydo_match.group(1).strip() if lydo_match else response_text[:500]

        if level not in ['Gioi', 'Kha', 'TB', 'Yeu']:
            level = 'TB'
        return level, lydo
    except Exception as e:
        print(f"[ERROR] Evaluation failed: {e}")
        return 'TB', 'Danh gia khong thanh cong do loi he thong.'


# ================== ĐỊNH DẠNG TRẢ LỜI ==================
def format_response(response):
    # Bảo vệ cú pháp LaTeX bằng cách tạm thời thay thế
    latex_matches = []
    def store_latex(match):
        latex_matches.append(match.group(0))
        return f"__LATEX_{len(latex_matches)-1}__"
    
    # Thay thế các đoạn LaTeX độc lập ($$...$$) và nội dòng ($...$)
    # Quan trọng: Phải thay thế $$ trước $ để tránh nhầm lẫn
    response = re.sub(r'\$\$(.+?)\$\$', store_latex, response, flags=re.DOTALL)
    response = re.sub(r'\$([^\$\n]+?)\$', store_latex, response)

    # Áp dụng định dạng Markdown
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight:700;">\1</strong>', response)
    formatted = re.sub(r'(?<!\n)\*(?!\s)(.*?)(?<!\s)\*(?!\*)', r'<em style="font-style:italic;">\1</em>', formatted)
    formatted = re.sub(r'(?m)^\s*\*\s+(.*)', r'• <span style="line-height:1.6;">\1</span>', formatted)
    
    # Khôi phục cú pháp LaTeX TRƯỚC KHI thay thế newline
    for i, latex in enumerate(latex_matches):
        formatted = formatted.replace(f"__LATEX_{i}__", latex)
    
    # Thay thế newline SAU KHI đã khôi phục LaTeX
    formatted = formatted.replace('\n', '<br>')

    # Áp dụng highlight_terms cho các từ khóa toán học
    # Chú ý: Không highlight nếu nằm trong LaTeX
    for term, color in highlight_terms.items():
        # Chỉ highlight nếu không nằm trong $ hoặc $$
        formatted = re.sub(
            r'(?<!\$)' + re.escape(term) + r'(?!\$)',
            f'<span style="line-height:1.6; background:{color}; color:white; font-weight:bold; padding:2px 4px; border-radius:4px;">{term}</span>',
            formatted
        )

    return formatted

# FORMAT TRẢ LỜI
highlight_terms = {
    # 🧮 TOÁN HỌC
    "Số tự nhiên": "#59C059",
    "Số nguyên": "#59C059",
    "Số hữu tỉ": "#59C059",
    "Số thập phân": "#59C059",
    "Phân số": "#59C059",
    "Tỉ số – Tỉ lệ": "#59C059",
    "Tỉ lệ thuận – Tỉ lệ nghịch": "#59C059",
    "Biểu thức đại số": "#59C059",
    "Hằng đẳng thức đáng nhớ": "#59C059",
    "Nhân, chia đa thức": "#59C059",
    "Phân tích đa thức thành nhân tử": "#59C059",
    "Căn bậc hai, căn bậc ba": "#59C059",
    "Lũy thừa – Căn thức": "#59C059",
    "Giải phương trình": "#59C059",
    "Phương trình bậc nhất một ẩn": "#59C059",
    "Hệ phương trình bậc nhất hai ẩn": "#59C059",
    "Bất phương trình": "#59C059",
    "Hàm số – Đồ thị hàm số": "#59C059",
    "Hàm số bậc nhất": "#59C059",
    "Tọa độ trong mặt phẳng": "#59C059",
    "Định lý Pythagoras": "#59C059",
    "Chu vi – Diện tích – Thể tích": "#59C059",
    "Tam giác": "#59C059",
    "Hình tròn – Hình cầu": "#59C059",

    # ⚡ VẬT LÝ
    "Vận tốc": "#E8B33F",
    "Quãng đường": "#E8B33F",
    "Thời gian": "#E8B33F",
    "Lực": "#E8B33F",
    "Trọng lực": "#E8B33F",
    "Khối lượng": "#E8B33F",
    "Trọng lượng": "#E8B33F",
    "Áp suất": "#E8B33F",
    "Công cơ học": "#E8B33F",
    "Nhiệt năng": "#E8B33F",
    "Công suất": "#E8B33F",
    "Nhiệt lượng": "#E8B33F",
    "Dẫn nhiệt": "#E8B33F",
    "Đối lưu": "#E8B33F",
    "Bức xạ nhiệt": "#E8B33F",
    "Điện tích": "#E8B33F",
    "Cường độ dòng điện": "#E8B33F",
    "Hiệu điện thế": "#E8B33F",
    "Điện trở": "#E8B33F",
    "Định luật Ôm": "#E8B33F",
    "Công của dòng điện": "#E8B33F",
    "Công suất điện": "#E8B33F",
    "Từ trường": "#E8B33F",
    "Nam châm": "#E8B33F",
    "Thấu kính hội tụ": "#E8B33F",
    "Ảnh thật – Ảnh ảo": "#E8B33F",
    "Phản xạ ánh sáng": "#E8B33F",
    "Khúc xạ ánh sáng": "#E8B33F",
    "Dòng điện – Mạch điện": "#E8B33F",
    "Nhiệt học": "#E8B33F",
    "Cơ học": "#E8B33F",
    "Điện học": "#E8B33F",
    "Quang học": "#E8B33F",

    # ⚗️ HÓA HỌC
    "Nguyên tử": "#D46A6A",
    "Phân tử": "#D46A6A",
    "Nguyên tố hóa học": "#D46A6A",
    "Kí hiệu hóa học": "#D46A6A",
    "Công thức hóa học": "#D46A6A",
    "Phản ứng hóa học": "#D46A6A",
    "Phương trình hóa học": "#D46A6A",
    "Hóa trị": "#D46A6A",
    "Khối lượng mol": "#D46A6A",
    "Thể tích mol": "#D46A6A",
    "Định luật bảo toàn khối lượng": "#D46A6A",
    "Định luật Avogadro": "#D46A6A",
    "Chất tinh khiết – Hỗn hợp": "#D46A6A",
    "Dung dịch": "#D46A6A",
    "Nồng độ phần trăm": "#D46A6A",
    "Nồng độ mol": "#D46A6A",
    "Chất oxi hóa – Chất khử": "#D46A6A",
    "Phản ứng oxi hóa – khử": "#D46A6A",
    "Axit – Bazơ – Muối": "#D46A6A",
    "pH – Độ axit": "#D46A6A",
    "Kim loại – Phi kim": "#D46A6A",
    "Oxit – Axit – Bazơ – Muối": "#D46A6A",
    "Hóa học vô cơ": "#D46A6A",
    "Hóa học hữu cơ": "#D46A6A",
    "Hiđrocacbon": "#D46A6A",
    "Rượu – Axit cacboxylic": "#D46A6A",
    "Este – Chất béo": "#D46A6A",
    "Gluxit – Protein": "#D46A6A",

    # 🌿 SINH HỌC
    "Tế bào": "#4FA3A5",
    "Mô – Cơ quan – Hệ cơ quan": "#4FA3A5",
    "Cơ thể sống": "#4FA3A5",
    "Hô hấp": "#4FA3A5",
    "Tuần hoàn": "#4FA3A5",
    "Tiêu hóa": "#4FA3A5",
    "Bài tiết": "#4FA3A5",
    "Thần kinh": "#4FA3A5",
    "Cảm giác – Giác quan": "#4FA3A5",
    "Sinh sản": "#4FA3A5",
    "Di truyền": "#4FA3A5",
    "Biến dị": "#4FA3A5",
    "Gen – Nhiễm sắc thể": "#4FA3A5",
    "Quang hợp": "#4FA3A5",
    "Hô hấp thực vật": "#4FA3A5",
    "Thực vật – Động vật": "#4FA3A5",
    "Chuỗi thức ăn – Lưới thức ăn": "#4FA3A5",
    "Sinh thái học": "#4FA3A5",
    "Môi trường – Hệ sinh thái": "#4FA3A5",
    "Vi sinh vật": "#4FA3A5",
    "Cấu tạo tế bào": "#4FA3A5",
    "Diễn biến sự sống": "#4FA3A5",
    "Tiến hóa": "#4FA3A5"
}


# ================== INJECT USER INFO ==================
@app.context_processor
def inject_user():
    """Inject current user info into all templates."""
    user_info = None
    if 'user_id' in session:
        user = json_db.get_user_by_id(session['user_id'])
        if user:
            user_info = {
                'id': user['id'],
                'tendangnhap': user['tendangnhap'],
                'tenhocsinh': user.get('tenhocsinh') or user['tendangnhap'],
                'nangluctoan': user.get('nangluctoan', 'TB'),
                'nanglucly': user.get('nanglucly', 'TB'),
                'nangluchoa': user.get('nangluchoa', 'TB'),
                'nanglucsinh': user.get('nanglucsinh', 'TB'),
            }
    return dict(current_user=user_info)

# ================== ROUTES ==================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        tendangnhap = request.form.get('tendangnhap')
        matkhau = request.form.get('matkhau')
        tenhocsinh = request.form.get('tenhocsinh', '').strip()
        if not tendangnhap or not matkhau:
            flash('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.', 'error')
            return redirect(url_for('register'))
        if not tenhocsinh:
            flash('Vui lòng nhập tên học sinh.', 'error')
            return redirect(url_for('register'))

        if json_db.get_user_by_username(tendangnhap):
            flash('Tên đăng nhập đã tồn tại.', 'error')
            return redirect(url_for('register'))

        try:
            hashed_password = generate_password_hash(matkhau, method='pbkdf2:sha256')
            json_db.create_user(tendangnhap, hashed_password, tenhocsinh)
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during registration: {str(e)}")
            flash(f'Lỗi khi đăng ký: {str(e)}', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tendangnhap = request.form.get('tendangnhap')
        matkhau = request.form.get('matkhau')
        if not tendangnhap or not matkhau:
            flash('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.', 'error')
            return redirect(url_for('login'))
        user = json_db.get_user_by_username(tendangnhap)
        if user and check_password_hash(user['matkhau'], matkhau):
            session['user_id'] = user['id']
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('home.html')

# Subject-specific tutor routes
@app.route('/tutor/math')
def math_tutor():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('math_tutor.html')

@app.route('/tutor/physics')
def physics_tutor():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('physics_tutor.html')

@app.route('/tutor/chemistry')
def chemistry_tutor():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('chemistry_tutor.html')

@app.route('/tutor/biology')
def biology_tutor():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('biology_tutor.html')

# Games routes
@app.route('/games')
def games():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('games.html')

@app.route('/games/math')
def math_games():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('math_games.html')

@app.route('/games/physics')
def physics_games():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('physics_games.html')

@app.route('/games/chemistry')
def chemistry_games():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('chemistry_games.html')

@app.route('/games/biology')
def biology_games():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('biology_games.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Vui lòng đăng nhập'}), 401

    user_message = request.json.get('message', '')
    subject = request.json.get('subject', 'general')
    if not user_message:
        return jsonify({'response': format_response('Con hãy nhập câu hỏi nhé!')})

    # Get user from JSON database
    user = json_db.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 401

    # Subject mapping to database columns
    subject_mapping = {
        'math': {
            'history_col': 'lichsutoan',
            'level_col': 'nangluctoan',
            'lydo_col': 'lydotoan',
            'counter_col': 'socautoan'
        },
        'physics': {
            'history_col': 'lichsuly',
            'level_col': 'nanglucly',
            'lydo_col': 'lydoly',
            'counter_col': 'socauly'
        },
        'chemistry': {
            'history_col': 'lichsuhoa',
            'level_col': 'nangluchoa',
            'lydo_col': 'lydohoa',
            'counter_col': 'socauhoa'
        },
        'biology': {
            'history_col': 'lichsusinh',
            'level_col': 'nanglucsinh',
            'lydo_col': 'lydosinh',
            'counter_col': 'socausinh'
        }
    }

    # Get subject-specific data or use general if subject not recognized
    if subject not in subject_mapping:
        subject = 'math'  # Default to math if subject not recognized
    
    subject_data = subject_mapping[subject]
    
    # Get current history for this subject
    current_history_str = user.get(subject_data['history_col'], '') or ''
    current_history = current_history_str.split('\n') if current_history_str else []
    
    # Add new question to history
    current_history.append(f"Học sinh: {user_message}")
    
    recent_history = "\n".join(current_history[-6:])

    # Get subject-specific level and adaptive instruction
    student_level = user.get(subject_data['level_col'], 'TB')
    level_instruction = get_level_instruction(student_level)

    # Thông tin môn học và hướng dẫn chuyên môn
    subject_info = {
        'math': {
            'name': 'Toán học',
            'name_en': 'Mathematics',
            'focus': 'Đại số, Hình học, Số học, Phương trình, Hàm số, và các phép tính toán học',
            'persona_instruction': """
            - **Tư duy Logic:** Giải thích mọi bước biến đổi phương trình/biểu thức thật rõ ràng.
            - **Cấu trúc:** Sử dụng gạch đầu dòng để tách biệt các bước giải.
            - **Hình học:** Nếu là bài hình học, hãy mô tả hình vẽ thật chi tiết để học sinh hình dung."""
        },
        'physics': {
            'name': 'Vật lý',
            'name_en': 'Physics',
            'focus': 'Cơ học, Điện học, Nhiệt học, Quang học, Lực, Năng lượng, và các định luật vật lý',
            'persona_instruction': """
            - **Hiện tượng thực tế:** Luôn liên hệ vấn đề với hiện tượng thực tế xung quanh.
            - **Đơn vị:** Nhấn mạnh việc đổi đơn vị trước khi tính toán.
            - **Bản chất:** Giải thích bản chất vật lý thay vì chỉ thay số vào công thức."""
        },
        'chemistry': {
            'name': 'Hóa học',
            'name_en': 'Chemistry',
            'focus': 'Nguyên tử, Phân tử, Phản ứng hóa học, Dung dịch, Axit-Bazơ-Muối, và Hóa học hữu cơ',
            'persona_instruction': """
            - **Cơ chế:** Mô tả quá trình phản ứng ở cấp độ phân tử.
            - **Phương trình:** Luôn cân bằng phương trình hóa học và ghi rõ trạng thái chất.
            - **Hiện tượng:** Mô tả màu sắc dung dịch, khí bay ra, hay kết tủa để học sinh dễ nhớ."""
        },
        'biology': {
            'name': 'Sinh học',
            'name_en': 'Biology',
            'focus': 'Tế bào, Di truyền, Sinh thái, Cơ thể người, Thực vật, Động vật, và Hệ sinh thái',
            'persona_instruction': """
            - **Hệ thống:** Giải thích sinh học như hệ thống liên kết (tế bào → mô → cơ quan → cơ thể).
            - **So sánh:** Sử dụng so sánh đời sống (VD: Ti thể giống nhà máy điện của tế bào).
            - **Quá trình:** Mô tả các quá trình sinh học theo trình tự thời gian hoặc nhân-quả rõ ràng."""
        },
        'general': {
            'name': 'Khoa học Tự nhiên',
            'name_en': 'Natural Sciences',
            'focus': 'Toan, Ly, Hoa, Sinh',
            'persona_instruction': '- Hãy hướng dẫn học sinh xác định vấn đề thuộc môn học nào trước.'
        }
    }

    current_subject = subject_info.get(subject, subject_info['general'])
    
    prompt = f"""Bạn là **Thầy giáo Song ngữ Việt – Anh**, chuyên dạy môn **{current_subject['name']} ({current_subject['name_en']})**.
    Giọng điệu: Thân thiện, khích lệ, chuyên nghiệp (Professional & Encouraging).
    Xưng hô: **"thầy – con"**.
    
    **Chuyên môn:** {current_subject['focus']}

    ---

    ### 🧠 Thông tin học sinh:
    - 💬 **Lịch sử trò chuyện gần đây:** {recent_history}
    - 🎓 **Trình độ học sinh hiện tại:** **{student_level}**
    - ❓ **Câu hỏi hiện tại:** {user_message}

    ---

    ### 🎯 HƯỚNG DẪN SƯ PHẠM THEO TRÌNH ĐỘ (RẤT QUAN TRỌNG — PHẢI TUÂN THỦ NGHIÊM NGẶT):
    {level_instruction}

    ### 💎 Hướng dẫn chuyên môn ({current_subject['name']}):
    {current_subject['persona_instruction']}

    ---

    ### 📋 CẤU TRÚC CÂU TRẢ LỜI BẮT BUỘC:

    1.  **Phần Tiếng Việt (Vietnamese Explanation):**
        -   Giải thích chi tiết, dễ hiểu, chia nhỏ vấn đề.
        -   Sử dụng **Markdown chuẩn**: `**bold**`, `*italic*`, danh sách `-`, số `1.`
        -   Công thức toán/lý/hóa dùng LaTeX:
            - Inline: `$x^2 + y^2 = z^2$`
            - Display: `$$\\int_0^1 x^2 dx$$`
        -   **QUAN TRỌNG:** Chỉ dùng Markdown thuần túy, KHÔNG dùng HTML tags.

    2.  **Phần Tiếng Anh (English Version):**
        -   Bắt đầu bằng: `### 👉 English Version`
        -   Dịch nội dung chính sang tiếng Anh chuẩn học thuật.
        -   Giữ nguyên công thức LaTeX.
        -   **ĐỘ KHÓ TIẾNG ANH PHẢI PHÙ HỢP VỚI TRÌNH ĐỘ ({student_level}).**

    3.  **Từ vựng quan trọng (Key Vocabulary):**
        -   Liệt kê 3–5 từ khóa khoa học: `**Từ tiếng Việt** — English Term`

    ---
    
    ### 📝 Nguyên tắc định dạng:
    - Sử dụng Markdown thuần túy, KHÔNG dùng HTML
    - Công thức toán: dùng `$...$` (inline) hoặc `$$...$$` (display)
    - Xuống dòng: để trống một dòng giữa các đoạn
    """
    # Detect if running on Vercel (serverless - no SSE support)
    is_vercel = os.getenv('VERCEL', '') != ''

    if is_vercel:
        # NON-STREAMING mode for Vercel serverless
        try:
            response = groq_client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4096,
                stream=False
            )
            raw_text = response.choices[0].message.content or ""
            # Strip <think>...</think> blocks
            clean_text = re.sub(r'<think>[\s\S]*?</think>', '', raw_text).strip()

            # Save to history
            current_history.append(f"Thầy/Cô: {clean_text}")
            updates = {}
            updates[subject_data['history_col']] = '\n'.join(current_history)
            current_count = user.get(subject_data['counter_col'], 0) or 0
            new_count = current_count + 1
            updates[subject_data['counter_col']] = new_count
            if new_count % 5 == 0:
                new_level, lydo = evaluate_student_level(current_history, subject)
                updates[subject_data['level_col']] = new_level
                updates[subject_data['lydo_col']] = lydo
            json_db.update_user(session['user_id'], updates)

            return jsonify({'response': clean_text})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # STREAMING mode for local development
    _user_id = session['user_id']
    _subject = subject
    _subject_data = subject_data
    _current_history = current_history
    _user = user
    _prompt = prompt

    def generate_stream():
        try:
            stream = groq_client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[{"role": "user", "content": _prompt}],
                temperature=0.7,
                max_tokens=4096,
                stream=True
            )
            full_raw = ""
            full_text = ""
            in_think = False

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    token = delta.content
                    full_raw += token

                    if '<think>' in full_raw and not in_think:
                        in_think = True
                        continue

                    if in_think:
                        if '</think>' in full_raw:
                            in_think = False
                            after_think = full_raw.split('</think>', 1)[-1]
                            new_text = after_think[len(full_text):]
                            if new_text.strip():
                                full_text = after_think
                                chunk_data = json.dumps({'chunk': new_text}, ensure_ascii=False)
                                yield f"data: {chunk_data}\n\n"
                        continue

                    full_text += token
                    chunk_data = json.dumps({'chunk': token}, ensure_ascii=False)
                    yield f"data: {chunk_data}\n\n"

            clean_text = re.sub(r'<think>[\s\S]*?</think>', '', full_raw).strip()

            done_data = json.dumps({'done': True, 'full_text': clean_text}, ensure_ascii=False)
            yield f"data: {done_data}\n\n"

            _current_history.append(f"Thầy/Cô: {clean_text}")
            updates = {}
            updates[_subject_data['history_col']] = '\n'.join(_current_history)
            current_count = _user.get(_subject_data['counter_col'], 0) or 0
            new_count = current_count + 1
            updates[_subject_data['counter_col']] = new_count

            if new_count % 5 == 0:
                new_level, lydo = evaluate_student_level(_current_history, _subject)
                updates[_subject_data['level_col']] = new_level
                updates[_subject_data['lydo_col']] = lydo

            json_db.update_user(_user_id, updates)

        except Exception as e:
            error_data = json.dumps({'error': str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return Response(generate_stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
# QUẢN LÝ HỌC SINH
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_session' not in session:
        if request.method == 'POST':
            tendangnhap = request.form.get('tendangnhap')
            matkhau = request.form.get('matkhau')
            if tendangnhap == 'lequangphuc':
                user = json_db.get_user_by_username(tendangnhap)
                if user and check_password_hash(user['matkhau'], matkhau):
                    session['admin_session'] = True
                    flash('Đăng nhập admin thành công!', 'success')
                    return redirect(url_for('admin'))
                else:
                    flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
            else:
                flash('Tên đăng nhập admin không đúng.', 'error')
        return render_template('admin_login.html')
    
    # Lấy dữ liệu năng lực học sinh theo từng môn
    danhsachhocsinh = json_db.get_all_users()
    user_data = []
    for user in danhsachhocsinh:
        # Skip admin users
        if user['tendangnhap'] == 'lequangphuc':
            continue
        user_data.append({
            'id': user['id'],
            'tendangnhap': user['tendangnhap'],
            'tenhocsinh': user.get('tenhocsinh') or "Chưa đặt tên",
            'nangluctoan': user.get('nangluctoan', 'TB'),
            'nanglucly': user.get('nanglucly', 'TB'),
            'nangluchoa': user.get('nangluchoa', 'TB'),
            'nanglucsinh': user.get('nanglucsinh', 'TB'),
            'socautoan': user.get('socautoan', 0),
            'socauly': user.get('socauly', 0),
            'socauhoa': user.get('socauhoa', 0),
            'socausinh': user.get('socausinh', 0),
            'tongsocau': (user.get('socautoan', 0) or 0) + (user.get('socauly', 0) or 0) + 
                              (user.get('socauhoa', 0) or 0) + (user.get('socausinh', 0) or 0),
            'lydotoan': user.get('lydotoan', ''),
            'lydoly': user.get('lydoly', ''),
            'lydohoa': user.get('lydohoa', ''),
            'lydosinh': user.get('lydosinh', '')
        })
    
    # Statistics
    all_levels = []
    for u in user_data:
        all_levels.extend([u['nangluctoan'], u['nanglucly'], u['nangluchoa'], u['nanglucsinh']])
    
    stats = {
        'total_students': len(user_data),
        'gioi_count': sum(1 for u in user_data if u['nangluctoan'] == 'Gioi' or u['nanglucly'] == 'Gioi' or u['nangluchoa'] == 'Gioi' or u['nanglucsinh'] == 'Gioi'),
        'kha_count': sum(1 for u in user_data if 'Kha' in [u['nangluctoan'], u['nanglucly'], u['nangluchoa'], u['nanglucsinh']]),
        'tb_count': sum(1 for u in user_data if 'TB' in [u['nangluctoan'], u['nanglucly'], u['nangluchoa'], u['nanglucsinh']]),
        'yeu_count': sum(1 for u in user_data if 'Yeu' in [u['nangluctoan'], u['nanglucly'], u['nangluchoa'], u['nanglucsinh']]),
        'total_questions': sum(u['tongsocau'] for u in user_data),
        # Subject-specific stats
        'toan_gioi': sum(1 for u in user_data if u['nangluctoan'] == 'Gioi'),
        'toan_kha': sum(1 for u in user_data if u['nangluctoan'] == 'Kha'),
        'toan_tb': sum(1 for u in user_data if u['nangluctoan'] == 'TB'),
        'toan_yeu': sum(1 for u in user_data if u['nangluctoan'] == 'Yeu'),
        'ly_gioi': sum(1 for u in user_data if u['nanglucly'] == 'Gioi'),
        'ly_kha': sum(1 for u in user_data if u['nanglucly'] == 'Kha'),
        'ly_tb': sum(1 for u in user_data if u['nanglucly'] == 'TB'),
        'ly_yeu': sum(1 for u in user_data if u['nanglucly'] == 'Yeu'),
        'hoa_gioi': sum(1 for u in user_data if u['nangluchoa'] == 'Gioi'),
        'hoa_kha': sum(1 for u in user_data if u['nangluchoa'] == 'Kha'),
        'hoa_tb': sum(1 for u in user_data if u['nangluchoa'] == 'TB'),
        'hoa_yeu': sum(1 for u in user_data if u['nangluchoa'] == 'Yeu'),
        'sinh_gioi': sum(1 for u in user_data if u['nanglucsinh'] == 'Gioi'),
        'sinh_kha': sum(1 for u in user_data if u['nanglucsinh'] == 'Kha'),
        'sinh_tb': sum(1 for u in user_data if u['nanglucsinh'] == 'TB'),
        'sinh_yeu': sum(1 for u in user_data if u['nanglucsinh'] == 'Yeu'),
        # Total questions per subject
        'total_toan': sum(u['socautoan'] for u in user_data),
        'total_ly': sum(u['socauly'] for u in user_data),
        'total_hoa': sum(u['socauhoa'] for u in user_data),
        'total_sinh': sum(u['socausinh'] for u in user_data),
    }
    
    # Pre-render table body in Python with enhanced UI classes
    table_rows = []
    for s in user_data:
        avatar_char = s['tenhocsinh'][0].upper() if s['tenhocsinh'] else "?"
        # Determine strict level class
        def get_lvl_class(lvl):
            return f"badge-{lvl.lower()}" if lvl else "badge-tb"
            
        row = f"""
        <tr class="table-row">
            <td>
                <div class="student-info">
                    <div class="avatar">{avatar_char}</div>
                    <div class="info-text">
                        <div class="name">{s['tenhocsinh']}</div>
                        <div class="username">@{s['tendangnhap']}</div>
                    </div>
                </div>
            </td>
            <td>
                <div class="subject-cell">
                    <span class="badge {get_lvl_class(s['nangluctoan'])}">{s['nangluctoan']}</span>
                    <span class="sub-text">{s['socautoan']} câu</span>
                </div>
            </td>
            <td>
                <div class="subject-cell">
                    <span class="badge {get_lvl_class(s['nanglucly'])}">{s['nanglucly']}</span>
                    <span class="sub-text">{s['socauly']} câu</span>
                </div>
            </td>
            <td>
                <div class="subject-cell">
                    <span class="badge {get_lvl_class(s['nangluchoa'])}">{s['nangluchoa']}</span>
                    <span class="sub-text">{s['socauhoa']} câu</span>
                </div>
            </td>
            <td>
                <div class="subject-cell">
                    <span class="badge {get_lvl_class(s['nanglucsinh'])}">{s['nanglucsinh']}</span>
                    <span class="sub-text">{s['socausinh']} câu</span>
                </div>
            </td>
            <td><span class="total-questions">{s['tongsocau']}</span></td>
            <td>
                <button class="btn-view-detail" onclick="showStudentDetails({s['id']})">
                    <i class="fa-solid fa-eye"></i> Xem & Đánh giá
                </button>
            </td>
        </tr>
        """
        table_rows.append(row)
    table_html = "".join(table_rows)
    
    # Get PDF files list
    pdf_files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if f.endswith('.pdf'):
                fpath = os.path.join(upload_dir, f)
                fsize = os.path.getsize(fpath)
                pdf_files.append({
                    'name': f,
                    'size': round(fsize / 1024, 1)  # KB
                })
    
    return render_template('admin.html', user_data=user_data, stats=stats, pdf_files=pdf_files, table_html=table_html)

# API: Chi tiết học sinh
@app.route('/admin/api/student/<int:student_id>')
def admin_student_detail(student_id):
    if 'admin_session' not in session or not session.get('admin_session'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = json_db.get_user_by_id(student_id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'id': user['id'],
        'tendangnhap': user['tendangnhap'],
        'tenhocsinh': user.get('tenhocsinh') or 'Chưa đặt tên',
        'nangluctoan': user.get('nangluctoan', 'TB'),
        'nanglucly': user.get('nanglucly', 'TB'),
        'nangluchoa': user.get('nangluchoa', 'TB'),
        'nanglucsinh': user.get('nanglucsinh', 'TB'),
        'socautoan': user.get('socautoan', 0),
        'socauly': user.get('socauly', 0),
        'socauhoa': user.get('socauhoa', 0),
        'socausinh': user.get('socausinh', 0),
        'lydotoan': user.get('lydotoan') or 'Chưa có đánh giá',
        'lydoly': user.get('lydoly') or 'Chưa có đánh giá',
        'lydohoa': user.get('lydohoa') or 'Chưa có đánh giá',
        'lydosinh': user.get('lydosinh') or 'Chưa có đánh giá'
    })

# API: Xóa học sinh
@app.route('/admin/api/student/<int:student_id>/delete', methods=['POST'])
def admin_delete_student(student_id):
    if 'admin_session' not in session or not session.get('admin_session'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = json_db.get_user_by_id(student_id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    
    if user['tendangnhap'] == 'lequangphuc':
        return jsonify({'error': 'Cannot delete admin account'}), 403
    
    try:
        json_db.delete_user(student_id)
        return jsonify({'success': True, 'message': f"Đã xóa học sinh {user.get('tenhocsinh', '')}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Reset dữ liệu học sinh
@app.route('/admin/api/student/<int:student_id>/reset', methods=['POST'])
def admin_reset_student(student_id):
    if 'admin_session' not in session or not session.get('admin_session'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = json_db.get_user_by_id(student_id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    
    try:
        json_db.reset_user_data(student_id)
        return jsonify({'success': True, 'message': f"Đã reset dữ liệu học sinh {user.get('tenhocsinh', '')}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Upload PDF
@app.route('/admin/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'admin_session' not in session or not session.get('admin_session'):
        flash('Bạn không có quyền truy cập.', 'error')
        return redirect(url_for('admin'))
    
    if 'pdf_file' not in request.files:
        flash('Không tìm thấy file PDF.', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['pdf_file']
    if file.filename == '':
        flash('Chưa chọn file.', 'error')
        return redirect(url_for('admin'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'Upload file {filename} thành công! Đang cập nhật RAG...', 'success')
        initialize_rag_data()  # Re-init RAG after upload
    else:
        flash('Chỉ cho phép upload file PDF.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete_pdf/<filename>', methods=['POST'])
def delete_pdf(filename):
    if 'admin_session' not in session or not session['admin_session']:
        flash('Bạn không có quyền truy cập.', 'error')
        return redirect(url_for('admin'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'Xóa file {filename} thành công! Đã cập nhật RAG.', 'success')
            initialize_rag_data()  # Re-init RAG sau khi xóa
        except Exception as e:
            flash(f'Lỗi khi xóa file {filename}: {str(e)}', 'error')
    else:
        flash(f'File {filename} không tồn tại.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/export_csv')
def export_csv():
    if 'admin_session' not in session or not session['admin_session']:
        flash('Bạn không có quyền truy cập.', 'error')
        return redirect(url_for('admin'))
    
    danhsachhocsinh = json_db.get_all_users()
    
    output = StringIO()
    fieldnames = ['ID', 'Tên đăng nhập', 'Tên học sinh', 'Năng lực Toán', 'Số câu Toán', 'Lý do Toán',
                  'Năng lực Lý', 'Số câu Lý', 'Lý do Lý', 'Năng lực Hóa', 'Số câu Hóa', 'Lý do Hóa',
                  'Năng lực Sinh', 'Số câu Sinh', 'Lý do Sinh', 'Tổng số câu']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for user in danhsachhocsinh:
        if user['tendangnhap'] == 'lequangphuc':
            continue
        writer.writerow({
            'ID': user['id'],
            'Tên đăng nhập': user['tendangnhap'],
            'Tên học sinh': user.get('tenhocsinh') or 'Chưa đặt tên',
            'Năng lực Toán': user.get('nangluctoan', 'TB'),
            'Số câu Toán': user.get('socautoan', 0),
            'Lý do Toán': user.get('lydotoan', ''),
            'Năng lực Lý': user.get('nanglucly', 'TB'),
            'Số câu Lý': user.get('socauly', 0),
            'Lý do Lý': user.get('lydoly', ''),
            'Năng lực Hóa': user.get('nangluchoa', 'TB'),
            'Số câu Hóa': user.get('socauhoa', 0),
            'Lý do Hóa': user.get('lydohoa', ''),
            'Năng lực Sinh': user.get('nanglucsinh', 'TB'),
            'Số câu Sinh': user.get('socausinh', 0),
            'Lý do Sinh': user.get('lydosinh', ''),
            'Tổng số câu': (user.get('socautoan', 0) or 0) + (user.get('socauly', 0) or 0) + 
                           (user.get('socauhoa', 0) or 0) + (user.get('socausinh', 0) or 0)
        })
    
    # Convert to bytes with BOM for Excel compatibility
    bytes_output = BytesIO()
    bytes_output.write(b'\xef\xbb\xbf')  # UTF-8 BOM
    bytes_output.write(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='ket_qua_hoc_tap.csv'
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_session', None)
    flash('Đã đăng xuất admin.', 'success')
    return redirect(url_for('admin'))

# ================== CHẠY APP ==================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)