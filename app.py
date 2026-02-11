from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import PyPDF2
import re
from dotenv import load_dotenv
load_dotenv()
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import text
import pandas as pd
from io import BytesIO
from werkzeug.utils import secure_filename
# ================== CẤU HÌNH & KHỞI TẠO ==================
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ Không tìm thấy GEMINI_API_KEY trong biến môi trường!")

genai.configure(api_key=api_key)

GENERATION_MODEL = 'gemma-3-4b-it'
EMBEDDING_MODEL = 'text-embedding-004'

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session(app)
# Cấu hình upload folder cho PDF
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class NguoiDung(db.Model):
    __tablename__ = 'taikhoanhocsinh'
    id = db.Column(db.Integer, primary_key=True)
    tendangnhap = db.Column(db.String(80), unique=True, nullable=False)
    matkhau = db.Column(db.String(255), nullable=False)
    tenhocsinh = db.Column(db.Text, default='')
    
    # Legacy columns (kept for backward compatibility)
    nangluc = db.Column(db.String(20), default='TB')
    lichsu = db.Column(db.Text, default='')
    lydo = db.Column(db.Text, default='')
    
    # Subject-specific chat lichsu
    lichsutoan = db.Column(db.Text, default='')
    lichsuly = db.Column(db.Text, default='')
    lichsuhoa = db.Column(db.Text, default='')
    lichsusinh = db.Column(db.Text, default='')
    
    # Subject-specific proficiency levels
    nangluctoan = db.Column(db.String(20), default='TB')
    nanglucly = db.Column(db.String(20), default='TB')
    nangluchoa = db.Column(db.String(20), default='TB')
    nanglucsinh = db.Column(db.String(20), default='TB')
    
    # Subject-specific assessment reasons
    lydotoan = db.Column(db.Text, default='')
    lydoly = db.Column(db.Text, default='')
    lydohoa = db.Column(db.Text, default='')
    lydosinh = db.Column(db.Text, default='')
    
    # Question counters for tracking when to assess
    socautoan = db.Column(db.Integer, default=0)
    socauly = db.Column(db.Integer, default=0)
    socauhoa = db.Column(db.Integer, default=0)
    socausinh = db.Column(db.Integer, default=0)

with app.app_context():
    # Đảm bảo schema public tồn tại
    db.session.execute(text('CREATE SCHEMA IF NOT EXISTS public;'))
    db.create_all()
    print("✅ Đã kiểm tra/tạo bảng taikhoanhocsinh trong schema public")

# Biến toàn cục cho RAG
RAG_DATA = {
    "chunks": [],
    "embeddings": np.array([]),
    "is_ready": False
}

# ================== ĐỌC & CHIA CHUNKS ==================
def extract_pdf_text(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"⚠️ Lỗi khi đọc PDF {pdf_path}: {e}")
    return text

def create_chunks_from_directory(directory='./static', chunk_size=400):
    all_chunks = []
    if not os.path.exists(directory):
        print(f"Thư mục {directory} không tồn tại.")
        return []
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    print(f"🔍 Tìm thấy {len(pdf_files)} tệp PDF trong {directory}...")
    for filename in pdf_files:
        pdf_path = os.path.join(directory, filename)
        content = extract_pdf_text(pdf_path)
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size].strip()
            if chunk:
                all_chunks.append(f"[Nguồn: {filename}] {chunk}")
    print(f"✅ Đã tạo tổng cộng {len(all_chunks)} đoạn văn (chunks).")
    return all_chunks

def embed_with_retry(texts, model_name, max_retries=5):
    all_embeddings = []
    for text in texts:
        for attempt in range(max_retries):
            try:
                result = genai.embed_content(model=model_name, content=text)
                all_embeddings.append(result["embedding"])
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Thử lại lần {attempt+1}: {e}")
                    time.sleep(2 ** attempt)
                else:
                    print(f"💥 Thất bại sau {max_retries} lần: {e}")
                    raise
    return np.array(all_embeddings)

def initialize_rag_data():
    global RAG_DATA
    print("⏳ Đang khởi tạo dữ liệu RAG...")
    chunks = create_chunks_from_directory()
    if not chunks:
        print("Không có dữ liệu để nhúng.")
        return
    try:
        embeddings = embed_with_retry(chunks, EMBEDDING_MODEL)
        RAG_DATA.update({
            "chunks": chunks,
            "embeddings": embeddings,
            "is_ready": True
        })
        print("🎉 Khởi tạo RAG hoàn tất!")
    except Exception as e:
        print(f"❌ KHÔNG THỂ KHỞI TẠO RAG: {e}")
        RAG_DATA["is_ready"] = False

initialize_rag_data()

# ================== TRUY XUẤT NGỮ CẢNH ==================
def retrieve_context(query, top_k=3):
    if not RAG_DATA["is_ready"]:
        return "Không có tài liệu RAG nào được tải."
    try:
        query_vec = embed_with_retry([query], EMBEDDING_MODEL)[0].reshape(1, -1)
        sims = cosine_similarity(query_vec, RAG_DATA["embeddings"])[0]
        top_idxs = np.argsort(sims)[-top_k:][::-1]
        return "\n\n---\n\n".join([RAG_DATA["chunks"][i] for i in top_idxs])
    except Exception as e:
        print(f"❌ Lỗi RAG: {e}")
        return "Lỗi khi tìm kiếm ngữ cảnh."

# ================== ĐÁNH GIÁ NĂNG LỰC ==================
def evaluate_student_level(history):
    recent_questions = "\n".join([msg for msg in history[-10:] if msg.startswith("👧 Học sinh:")])
    prompt = f"""
    Bạn là một **Giáo viên Khoa học Tự nhiên Song ngữ (Anh – Việt)**, có nhiệm vụ **đánh giá năng lực học tập và khả năng tự học của học sinh** dựa trên lịch sử câu hỏi gần đây.

    Dưới đây là **10 câu hỏi gần nhất của học sinh**:
    {recent_questions}

    ### 🎯 Yêu cầu:
    1. Đọc kỹ nội dung các câu hỏi, xác định:
    - Mức độ hiểu biết của học sinh về các môn **Toán, Lý, Hóa, Sinh**.
    - Khả năng **diễn đạt logic**, **sử dụng thuật ngữ khoa học**, **tự tìm hiểu**.
    - Mức độ sử dụng **song ngữ Anh – Việt**: đúng, sai, hoặc thiếu tự nhiên.
    2. Phân loại năng lực học tập tổng quát thành **một trong 4 cấp độ**:
    - **Giỏi (Gioi)** → hỏi các vấn đề nâng cao, diễn đạt logic, dùng tiếng Anh đúng ngữ cảnh học thuật, thể hiện tư duy phản biện.
    - **Khá (Kha)** → hỏi ở mức khá, hiểu khái niệm cơ bản, có thể sai nhẹ nhưng diễn đạt tốt.
    - **Trung bình (TB)** → hỏi những kiến thức cơ bản, còn sai sót khi dùng thuật ngữ hoặc câu hỏi chưa rõ.
    - **Yếu (Yeu)** → hỏi lặp lại, diễn đạt kém, không nắm chắc khái niệm, chưa tự giải thích được vấn đề.
    3. Nếu học sinh xen kẽ nhiều môn khác nhau (VD: Toán và Sinh), hãy **đánh giá trung bình tổng hợp**, không thiên lệch một môn.
    4. Viết kết quả ngắn gọn, có lý do súc tích.

    ### 📋 Định dạng đầu ra:
    Cấp độ: [Gioi / Kha / TB / Yeu]  
    Lý do: [Giải thích lý do rõ ràng, phân tích định hướng cho giáo viên hỗ trợ, tối đa 150–200 từ.]
    """

    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        # Extract level and reason from response
        level_match = re.search(r'Cấp độ: (Gioi|Kha|TB|Yeu)', response_text)
        lydo_match = re.search(r'Lý do: (.+)', response_text, re.DOTALL)
        
        level = level_match.group(1) if level_match else "TB"
        lydo = lydo_match.group(1).strip() if lydo_match else "Không có lý do cụ thể."
        
        if level not in ['Gioi', 'Kha', 'TB', 'Yeu']:
            level = 'TB'
        return level, lydo
    except Exception as e:
        print(f"❌ Lỗi đánh giá: {e}")
        return 'TB', 'Đánh giá không thành công do lỗi hệ thống.'


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


# ================== ROUTES ==================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        tendangnhap = request.form.get('tendangnhap')
        matkhau = request.form.get('matkhau')
        tenhocsinh = request.form.get('tenhocsinh', '').strip()  # LẤY TÊN HỌC SINH
        if not tendangnhap or not matkhau:
            flash('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.', 'error')
            return redirect(url_for('register'))
        if not tenhocsinh:
            flash('Vui lòng nhập tên học sinh.', 'error')
            return redirect(url_for('register'))

        if NguoiDung.query.filter_by(tendangnhap=tendangnhap).first():
            flash('Tên đăng nhập đã tồn tại.', 'error')
            return redirect(url_for('register'))

        try:
            hashed_password = generate_password_hash(matkhau, method='pbkdf2:sha256')
            user = NguoiDung(
                tendangnhap=tendangnhap, 
                matkhau=hashed_password, 
                tenhocsinh=tenhocsinh,
                # Legacy columns
                nangluc='TB',
                lichsu='',
                lydo='',
                # Subject-specific lichsu
                lichsutoan='',
                lichsuly='',
                lichsuhoa='',
                lichsusinh='',
                # Subject-specific levels
                nangluctoan='TB',
                nanglucly='TB',
                nangluchoa='TB',
                nanglucsinh='TB',
                # Subject-specific reasons
                lydotoan='',
                lydoly='',
                lydohoa='',
                lydosinh='',
                # Question counters
                socautoan=0,
                socauly=0,
                socauhoa=0,
                socausinh=0
            )
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
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
        user = NguoiDung.query.filter_by(tendangnhap=tendangnhap).first()
        if user and check_password_hash(user.matkhau, matkhau):
            session['user_id'] = user.id
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

    # Get user from database
    user = db.session.get(NguoiDung, session['user_id'])
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
    current_history_str = getattr(user, subject_data['history_col']) or ''
    current_history = current_history_str.split('\n') if current_history_str else []
    
    # Add new question to history
    current_history.append(f"👧 Học sinh: {user_message}")
    
    # 🔍 Retrieve RAG context
    related_context = retrieve_context(user_message)
    recent_history = "\n".join(current_history[-10:])

    # Get subject-specific level
    student_level = getattr(user, subject_data['level_col'])

    # Subject-specific information with Enhanced Personas
    subject_info = {
        'math': {
            'name': 'Toán học',
            'name_en': 'Mathematics',
            'focus': 'Đại số, Hình học, Số học, Phương trình, Hàm số, và các phép tính toán học',
            'persona_instruction': """
            - **Tư duy Logic:** Hãy giải thích mọi bước biến đổi phương trình/biểu thức thật rõ ràng (từ dòng này sang dòng kia đã làm gì).
            - **Cấu trúc:** Sử dụng các gạch đầu dòng để tách biệt các bước giải.
            - **Visualization:** Nếu là bài hình học, hãy mô tả hình vẽ thật chi tiết để học sinh hình dung được.
            """
        },
        'physics': {
            'name': 'Vật lý',
            'name_en': 'Physics',
            'focus': 'Cơ học, Điện học, Nhiệt học, Quang học, Lực, Năng lượng, và các định luật vật lý',
            'persona_instruction': """
            - **Hiện tượng thực tế:** Luôn bắt đầu bằng việc liên hệ vấn đề với hiện tượng thực tế xung quanh (ví dụ: tại sao xe dừng lại khi phanh).
            - **Đơn vị:** Nhấn mạnh việc đổi đơn vị trước khi tính toán.
            - **Bản chất:** Giải thích bản chất vật lý (tại sao lực tác dụng lại gây ra gia tốc) thay vì chỉ thay số vào công thức.
            """
        },
        'chemistry': {
            'name': 'Hóa học',
            'name_en': 'Chemistry',
            'focus': 'Nguyên tử, Phân tử, Phản ứng hóa học, Dung dịch, Axit-Bazơ-Muối, và Hóa học hữu cơ',
            'persona_instruction': """
            - **Cơ chế:** Mô tả quá trình phản ứng xảy ra ở cấp độ phân tử (nguyên tử nào tách ra, nguyên tử nào kết hợp).
            - **Phương trình:** Luôn luôn cân bằng phương trình hóa học và ghi rõ trạng thái chất (rắn, lỏng, khí, dung dịch) nếu cần.
            - **Màu sắc/Hiện tượng:** Mô tả màu sắc dung dịch, khí bay ra, hay kết tủa để học sinh dễ nhớ.
            """
        },
        'biology': {
            'name': 'Sinh học',
            'name_en': 'Biology',
            'focus': 'Tế bào, Di truyền, Sinh thái, Cơ thể người, Thực vật, Động vật, và Hệ sinh thái',
            'persona_instruction': """
            - **Hệ thống:** Giải thích sinh học như một hệ thống liên kết (tế bào -> mô -> cơ quan -> hệ cơ quan -> cơ thể).
            - **So sánh:** Sử dụng phép so sánh đời sống (ví dụ: Ti thể giống như nhà máy điện của tế bào).
            - **Quá trình:** Mô tả các quá trình sinh học theo trình tự thời gian hoặc nhân-quả rõ ràng.
            """
        },
        'general': {
            'name': 'Khoa học Tự nhiên',
            'name_en': 'Natural Sciences',
            'focus': 'Toán, Lý, Hóa, Sinh',
            'persona_instruction': "- Hãy hướng dẫn học sinh xác định vấn đề thuộc môn học nào trước."
        }
    }

    current_subject = subject_info.get(subject, subject_info['general'])
    
    prompt = f"""
    Bạn là **Thầy giáo Song ngữ Việt – Anh**, chuyên dạy môn **{current_subject['name']} ({current_subject['name_en']})**.  
    Model: **Gemma-3-4B-IT** (Instruction Tuned for Education).
    Giọng điệu: Thân thiện, khích lệ, chuyên nghiệp (Professional & Encouraging).
    Xưng hô: **"thầy – con"**.
    
    **Chuyên môn:** {current_subject['focus']}

    ---

    ### 🧠 **Thông tin ngữ cảnh (Context):**
    - 📚 **RAG (Tài liệu):** {related_context}
    - 💬 **Lịch sử trò chuyện:** {recent_history}
    - 👨‍🎓 **Trình độ học sinh:** {student_level} (Hãy điều chỉnh độ khó từ vựng và khái niệm cho phù hợp).
    - ❓ **Câu hỏi hiện tại:** {user_message}

    ---

    ### 💎 **Hướng dẫn sư phạm đặc biệt ({current_subject['name']}):**
    {current_subject['persona_instruction']}

    ---

    ### 🎯 **Cấu trúc câu trả lời bắt buộc:**

    1.  **Phần Tiếng Việt (Vietnamese Explanation):**
        -   Giải thích chi tiết, dễ hiểu, chia nhỏ vấn đề.
        -   Sử dụng **Markdown chuẩn**: `**bold**`, `*italic*`, danh sách có dấu đầu dòng `-`, danh sách số `1.`
        -   Sử dụng LaTeX cho công thức Toán/Lý/Hóa:
            - Công thức trong dòng: `$x^2 + y^2 = z^2$`
            - Công thức riêng dòng: `$$\\int_0^1 x^2 dx$$`
        -   **QUAN TRỌNG:** Chỉ dùng Markdown thuần túy, KHÔNG dùng HTML tags.

    2.  **Phần Tiếng Anh (English Translation - Learning Corner):**
        -   Bắt đầu bằng tiêu đề: `### 👉 English Version`
        -   Dịch nội dung chính sang tiếng Anh chuẩn học thuật.
        -   Giữ nguyên công thức LaTeX.

    3.  **Từ vựng quan trọng (Key Vocabulary):**
        -   Liệt kê 3-5 từ khóa khoa học theo format:
        -   `**Từ tiếng Việt** - English Term`

    ---
    
    ### 📝 **Nguyên tắc định dạng:**
    - Sử dụng Markdown thuần túy, KHÔNG dùng HTML
    - Công thức toán: dùng `$...$` (inline) hoặc `$$...$$` (display)
    - Xuống dòng: để trống một dòng giữa các đoạn
    - Nhấn mạnh: `**bold**` hoặc `*italic*`
    - Code/thuật ngữ: dùng backticks `như thế này`
    """

    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        ai_text = response.text

        # Add AI response to history
        current_history.append(f"🧑‍🏫 Thầy/Cô: {ai_text}")
        
        # Save updated history to database
        setattr(user, subject_data['history_col'], '\n'.join(current_history))
        
        # Increment question counter for this subject
        current_count = getattr(user, subject_data['counter_col']) or 0
        new_count = current_count + 1
        setattr(user, subject_data['counter_col'], new_count)
        
        # Check if we need to assess this subject (every 10 questions)
        if new_count % 10 == 0:
            # Assess THIS subject only
            new_level, lydo = evaluate_student_level(current_history)
            setattr(user, subject_data['level_col'], new_level)
            setattr(user, subject_data['lydo_col'], lydo)
            print(f"✅ User {user.tendangnhap} - {subject.upper()} level updated to {new_level} after {new_count} questions")
            print(f"   Reason: {lydo[:100]}...")
        
        # Commit all changes to database
        db.session.commit()

        return jsonify({'response': ai_text})

    except Exception as e:
        print(f"❌ Lỗi Gemini: {e}")
        return jsonify({'response': "Thầy Gemini hơi mệt, con thử lại sau nhé!"})
# QUẢN LÝ HỌC SINH
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_session' not in session:
        if request.method == 'POST':
            tendangnhap = request.form.get('tendangnhap')
            matkhau = request.form.get('matkhau')
            if tendangnhap == 'lequangphuc':
                user = NguoiDung.query.filter_by(tendangnhap=tendangnhap).first()
                if user and check_password_hash(user.matkhau, matkhau):
                    session['admin_session'] = True
                    flash('Đăng nhập admin thành công!', 'success')
                    return redirect(url_for('admin'))
                else:
                    flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
            else:
                flash('Tên đăng nhập admin không đúng.', 'error')
        return render_template('admin_login.html')
    
    # Lấy dữ liệu năng lực học sinh theo từng môn
    danhsachhocsinh = NguoiDung.query.all()
    user_data = []
    for user in danhsachhocsinh:
        # Skip admin users
        if user.tendangnhap == 'lequangphuc':
            continue
        user_data.append({
            'id': user.id,
            'tendangnhap': user.tendangnhap,
            'tenhocsinh': user.tenhocsinh or "Chưa đặt tên",
            # Subject-specific levels
            'nangluctoan': user.nangluctoan or 'TB',
            'nanglucly': user.nanglucly or 'TB',
            'nangluchoa': user.nangluchoa or 'TB',
            'nanglucsinh': user.nanglucsinh or 'TB',
            # Question counts
            'socautoan': user.socautoan or 0,
            'socauly': user.socauly or 0,
            'socauhoa': user.socauhoa or 0,
            'socausinh': user.socausinh or 0,
            # Total questions
            'tongsocau': (user.socautoan or 0) + (user.socauly or 0) + 
                              (user.socauhoa or 0) + (user.socausinh or 0),
            # Reasons (for detail view)
            'lydotoan': user.lydotoan or '',
            'lydoly': user.lydoly or '',
            'lydohoa': user.lydohoa or '',
            'lydosinh': user.lydosinh or ''
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
    
    user = db.session.get(NguoiDung, student_id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'id': user.id,
        'tendangnhap': user.tendangnhap,
        'tenhocsinh': user.tenhocsinh or 'Chưa đặt tên',
        'nangluctoan': user.nangluctoan or 'TB',
        'nanglucly': user.nanglucly or 'TB',
        'nangluchoa': user.nangluchoa or 'TB',
        'nanglucsinh': user.nanglucsinh or 'TB',
        'socautoan': user.socautoan or 0,
        'socauly': user.socauly or 0,
        'socauhoa': user.socauhoa or 0,
        'socausinh': user.socausinh or 0,
        'lydotoan': user.lydotoan or 'Chưa có đánh giá',
        'lydoly': user.lydoly or 'Chưa có đánh giá',
        'lydohoa': user.lydohoa or 'Chưa có đánh giá',
        'lydosinh': user.lydosinh or 'Chưa có đánh giá'
    })

# API: Xóa học sinh
@app.route('/admin/api/student/<int:student_id>/delete', methods=['POST'])
def admin_delete_student(student_id):
    if 'admin_session' not in session or not session.get('admin_session'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = db.session.get(NguoiDung, student_id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    
    if user.tendangnhap == 'lequangphuc':
        return jsonify({'error': 'Cannot delete admin account'}), 403
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Đã xóa học sinh {user.tenhocsinh}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Reset dữ liệu học sinh
@app.route('/admin/api/student/<int:student_id>/reset', methods=['POST'])
def admin_reset_student(student_id):
    if 'admin_session' not in session or not session.get('admin_session'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = db.session.get(NguoiDung, student_id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    
    try:
        # Reset subject-specific data
        user.lichsutoan = ''
        user.lichsuly = ''
        user.lichsuhoa = ''
        user.lichsusinh = ''
        user.nangluctoan = 'TB'
        user.nanglucly = 'TB'
        user.nangluchoa = 'TB'
        user.nanglucsinh = 'TB'
        user.lydotoan = ''
        user.lydoly = ''
        user.lydohoa = ''
        user.lydosinh = ''
        user.socautoan = 0
        user.socauly = 0
        user.socauhoa = 0
        user.socausinh = 0
        # Reset legacy columns
        user.nangluc = 'TB'
        user.lichsu = ''
        user.lydo = ''
        db.session.commit()
        return jsonify({'success': True, 'message': f'Đã reset dữ liệu học sinh {user.tenhocsinh}'})
    except Exception as e:
        db.session.rollback()
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
    
    danhsachhocsinh = NguoiDung.query.all()
    user_data = []
    for user in danhsachhocsinh:
        if user.tendangnhap == 'lequangphuc':
            continue
        user_data.append({
            'ID': user.id,
            'Tên đăng nhập': user.tendangnhap,
            'Tên học sinh': user.tenhocsinh or 'Chưa đặt tên',
            'Năng lực Toán': user.nangluctoan or 'TB',
            'Số câu Toán': user.socautoan or 0,
            'Lý do Toán': user.lydotoan or '',
            'Năng lực Lý': user.nanglucly or 'TB',
            'Số câu Lý': user.socauly or 0,
            'Lý do Lý': user.lydoly or '',
            'Năng lực Hóa': user.nangluchoa or 'TB',
            'Số câu Hóa': user.socauhoa or 0,
            'Lý do Hóa': user.lydohoa or '',
            'Năng lực Sinh': user.nanglucsinh or 'TB',
            'Số câu Sinh': user.socausinh or 0,
            'Lý do Sinh': user.lydosinh or '',
            'Tổng số câu': (user.socautoan or 0) + (user.socauly or 0) + (user.socauhoa or 0) + (user.socausinh or 0)
        })
    
    df = pd.DataFrame(user_data)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return send_file(
        output,
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