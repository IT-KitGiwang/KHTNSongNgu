# 🎓 Ứng dụng Học tập KHTN Song ngữ với AI

Ứng dụng hỗ trợ học sinh học tập các môn Khoa học Tự nhiên (Toán, Lý, Hóa, Sinh) bằng tiếng Việt và tiếng Anh với sự hỗ trợ của AI Gemma-3-12B-IT.

## ✨ Tính năng

- 🤖 **AI Tutor chuyên môn**: Giáo viên AI riêng cho từng môn học
  - Toán học (Mathematics)
  - Vật lý (Physics)
  - Hóa học (Chemistry)
  - Sinh học (Biology)

- 🎮 **Trò chơi Scratch tương tác**: 21 trò chơi giáo dục
  - 5 trò chơi Toán học
  - 5 trò chơi Vật lý
  - 5 trò chơi Hóa học
  - 6 trò chơi Sinh học

- 🌐 **Song ngữ Việt - Anh**: Mọi giải thích đều có cả tiếng Việt và tiếng Anh

- 📊 **Đánh giá năng lực**: Hệ thống tự động đánh giá trình độ học sinh

- 📚 **RAG (Retrieval-Augmented Generation)**: Tìm kiếm thông tin từ tài liệu PDF

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd AI-Hoc-Tap-KHTN-Song-Ngu
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường

Sao chép file `.env.example` thành `.env` và điền thông tin:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
GEMINI_API_KEY=your_actual_api_key_here
FLASK_SECRET_KEY=your_generated_secret_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/khtn_db
```

#### Lấy Gemini API Key:
1. Truy cập: https://aistudio.google.com/app/apikey
2. Đăng nhập với Google Account
3. Tạo API key mới
4. Copy và paste vào file `.env`

#### Tạo Flask Secret Key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Thiết lập Database

Tạo database PostgreSQL:

```bash
createdb khtn_db
```

Hoặc sử dụng pgAdmin để tạo database mới.

### 5. Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

## 📁 Cấu trúc thư mục

```
AI-Hoc-Tap-KHTN-Song-Ngu/
├── app.py                 # Flask application chính
├── requirements.txt       # Python dependencies
├── .env                   # Biến môi trường (không commit)
├── .env.example          # Template cho .env
├── Procfile              # Cấu hình deploy
├── static/               # Thư mục chứa PDF cho RAG
├── templates/            # HTML templates
│   ├── home.html         # Trang chủ
│   ├── math_tutor.html   # AI Toán học
│   ├── physics_tutor.html # AI Vật lý
│   ├── chemistry_tutor.html # AI Hóa học
│   ├── biology_tutor.html # AI Sinh học
│   ├── games.html        # Trang chọn trò chơi
│   ├── math_games.html   # Trò chơi Toán
│   ├── physics_games.html # Trò chơi Vật lý
│   ├── chemistry_games.html # Trò chơi Hóa học
│   ├── biology_games.html # Trò chơi Sinh học
│   ├── login.html        # Đăng nhập
│   ├── register.html     # Đăng ký
│   ├── admin.html        # Quản trị
│   └── admin_login.html  # Đăng nhập admin
└── flask_session/        # Session storage
```

## 🎨 Công nghệ sử dụng

- **Backend**: Flask (Python)
- **AI Model**: Google Gemma-3-12B-IT
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS (Vanilla), JavaScript
- **Math Rendering**: MathJax
- **Games**: Scratch (embedded iframes)

## 👨‍🏫 Tác giả

**Giáo viên Lê Quang Phúc**  
Trường THCS Trung Thành – Linh Hồ – Tuyên Quang  
📧 lequangphuctq81@gmail.com

## 📝 License

© 2024-2026 Trường THCS Trung Thành – Linh Hồ – Tuyên Quang
