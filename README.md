# KHTN SONG NGỮ - HỆ THỐNG GIA SƯ AI THÔNG MINH (AI EDUCATION PLATFORM)

**Dự án tham dự:** Cuộc Thi Sáng Tạo Với AI Trong Giáo Dục – Năm học 2025 - 2026  
**Đơn vị:** Trường THCS Trung Thành – Linh Hồ, Tuyên Quang  
**Tác giả:** Nhóm phát triển KHTN Song Ngữ (Lê Quang Phúc - Trưởng nhóm)

---

## 1. GIỚI THIỆU TỔNG QUAN (EXECUTIVE SUMMARY)

Trong kỷ nguyên chuyển đổi số, việc ứng dụng trí tuệ nhân tạo (AI) vào giáo dục không chỉ là xu thế mà còn là giải pháp đột phá để cá nhân hóa việc học. Dự án **"KHTN Song Ngữ"** là một nền tảng học tập tiên tiến, tích hợp mô hình ngôn ngữ lớn (LLM) để hỗ trợ học sinh học tập các môn Khoa học Tự nhiên (Toán, Lý, Hóa, Sinh) bằng cả hai ngôn ngữ Việt - Anh. Hệ thống đóng vai trò như một gia sư ảo 24/7, giúp xóa tan rào cản ngôn ngữ và kiến thức khoa học khó nhằn.

## 2. NHỮNG ĐIỂM ĐỘT PHÁ (INNOVATIVE FEATURES)

### 🚀 Cá Nhân Hóa Với RAG (Retrieval-Augmented Generation)
Hệ thống không chỉ trả lời dựa trên tri thức có sẵn của AI mà còn được "nạp" thêm kiến thức từ kho học liệu chính thống (PDF) do giáo viên cung cấp. Điều này đảm bảo:
- Thông tin chính xác, bám sát chương trình học.
- Trả lời có dẫn nguồn tài liệu cụ thể.

### 🧠 Đánh Giá Năng Lực Tự Động
Hệ thống tự động phân tích 10 câu hỏi gần nhất của học sinh để đánh giá trình độ (Giỏi - Khá - Trung bình - Yếu). Qua đó, AI sẽ:
- Điều chỉnh cách dùng thuật ngữ và độ khó câu trả lời.
- Cung cấp báo cáo chi tiết cho giáo viên quản lý về tiến độ của từng học sinh.

### 🇻🇳🇬🇧 Tư Duy Song Ngữ (Bilingual Literacy)
Mỗi tương tác của AI đều được cấu trúc 3 phần:
1. **Tiếng Việt:** Giải thích chi tiết khái niệm.
2. **English Version:** Phiên bản tiếng Anh học thuật tương đương.
3. **Key Vocabulary:** Hệ thống hóa các thuật ngữ khoa học song ngữ.

### 🎮 Gamification (Vừa học vừa chơi)
Tích hợp kho trò chơi Scratch tương tác theo từng môn học, giúp học sinh củng cố kiến thức một cách thú vị, tránh gây áp lực học tập.

---

## 3. CÔNG NGHỆ SỬ DỤNG (TECHNICAL STACK)

- **AI Model:** `Gemma-3-12B-IT` (Mô hình ngôn ngữ lớn tối ưu cho giáo dục).
- **Embeddings:** `Text-embedding-004` (Xử lý truy xuất ngữ cảnh chính xác).
- **Backend:** Flask (Python) - Xử lý logic và hệ thống RAG.
- **Database:** SQLAlchemy - Quản lý tài khoản và lịch sử học tập.
- **Frontend:** HTML5, Tailwind CSS, Font Awesome - Giao diện hiện đại, responsive.
- **Math Engine:** MathJax (Hiển thị công thức toán học/hóa học chuẩn xác).

---

## 4. Ý NGHĨA GIÁO DỤC (EDUCATIONAL IMPACT)

1. **Hỗ trợ tự học:** Học sinh có thể chủ động tìm hiểu kiến thức mọi lúc mọi nơi.
2. **Phát triển ngoại ngữ:** Giúp học sinh làm quen với thuật ngữ khoa học bằng tiếng Anh, chuẩn bị hành trang hội nhập quốc tế.
3. **Số hóa học liệu:** Giúp giáo viên quản lý và phân tích năng lực học sinh qua dữ liệu trực quan từ Admin Panel.
4. **Công bằng giáo dục:** Tiếp cận gia sư chất lượng cao cho mọi học sinh, không phân biệt vùng miền.

---

## 5. HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### Cài đặt môi trường
1. Clone dự án về máy.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
3. Cấu hình file `.env` với `GEMINI_API_KEY` của bạn.

### Khởi chạy
```bash
python app.py
```
Truy cập: `http://127.0.0.1:5000`

---

## 6. ĐỘI NGŨ THỰC HIỆN

- **Lê Quang Phúc:** Trưởng nhóm - Kiến trúc hệ thống & AI logic.
- **Phùng Văn Hạnh:** Xây dựng cơ sở dữ liệu & Nội dung học liệu.
- **Hoàng Thị Nha:** Thiết kế giao diện (UI/UX) & Trò chơi Scratch.
- **Nguyễn Thị Thương:** Biên tập nội dung song ngữ & Kiểm thử.

---
**© 2026 KHTN Song Ngữ** - *Phát triển vì một nền giáo dục thông minh và toàn cầu.*
