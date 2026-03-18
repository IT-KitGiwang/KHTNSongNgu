# Báo Cáo: Các Mô Hình AI (LLMs) Được Sử Dụng Trong Phiên Bản Hiện Tại

Hệ thống **KHTN Song Ngữ** ứng dụng kiến trúc đa mô hình (Multi-Model Architecture) thông qua API của Groq nhằm tối ưu hóa hiệu năng, độ trễ và chi phí. Dưới đây là phân tích chi tiết về các mô hình AI đang được sử dụng trong hệ thống:

## 1. Mô hình tương tác sư phạm chính (Chat Tutoring Model)
* **Model ID:** `qwen/qwen3-32b` (hoặc các phiên bản Qwen tương tự có kích thước vừa-lớn)
* **Vai trò:** Đóng vai trò là "Thầy giáo Song ngữ", chịu trách nhiệm sinh văn bản đầu ra cho tất cả các tương tác hỏi đáp của học sinh, giải thích kiến thức, và tạo lộ trình song ngữ.
* **Đặc điểm & Lý do lựa chọn:**
    * **Khả năng suy luận tốt:** Với khoảng 32 tỷ tham số, mô hình có khả năng phân tích logic tốt các bài toán Toán, Lý, Hóa, Sinh.
    * **Hỗ trợ đa ngôn ngữ xuất sắc:** Qwen được đánh giá rất cao về khả năng xử lý tiếng Việt kết hợp tiếng Anh thuật ngữ chuyên ngành một cách tự nhiên, không bị cứng nhắc.
    * **Tuân thủ Prompt sư phạm:** Có khả năng nhập vai tốt (chia theo trình độ Giỏi, Khá, Trung bình, Yếu) và tuân thủ chặt وتح chặt chẽ cấu trúc JSON/Markdown yêu cầu.

## 2. Mô hình phân tích và đánh giá (Evaluation Model)
* **Model ID:** `llama-3.1-8b-instant`
* **Vai trò:** Hệ thống chạy ngầm để đánh giá năng lực học sinh (tính sau mỗi 5 câu hỏi) và tự động xếp loại học sinh theo 4 mức độ: Giỏi, Khá, TB, Yếu.
* **Đặc điểm & Lý do lựa chọn:**
    * **Nhanh và nhẹ (Instant):** Hàm đánh giá cần chạy ngầm liên tục sau chu kỳ câu hỏi. Sử dụng Llama 3.1 8B (với tốc độ sinh token cực nhanh trên Groq, có thể lên tới 800-1000 tokens/s) giúp hệ thống không bị "nghẽn" (bottleneck).
    * **Tiết kiệm chi phí:** Phân tích logic từ lịch sử hội thoại chỉ cần mô hình nhỏ nhưng được huấn luyện tốt như Llama 3.1 8B. Nhiệm vụ chỉ là đọc hiểu văn bản tóm tắt và đưa ra quyết định xếp loại theo rubric 5 tiêu chí.

## 3. Mô hình dự phòng (Fallback Model)
* **Model ID:** `llama-3.3-70b-versatile`
* **Vai trò:** Mô hình xử lý dự phòng cho các trường hợp câu hỏi cực kỳ phức tạp hoặc hệ thống chính gặp lỗi.
* **Đặc điểm & Lý do lựa chọn:**
    * **Độ chính xác cao, đa năng (Versatile):** Với 70 tỷ tham số, khả năng giải quyết vấn đề toán học và lý luận của Llama 3.3 70B nằm trong nhóm xuất sắc nhất thị trường hiện nay (tiệm cận GPT-4).
    * Được dùng để xử lý các fallback khi mô hình chính không thể phân tích các bài toán Olympic hay khi cần một khả năng suy luận chuyên sâu vượt chuẩn.

---

## Tổng kết Lợi Ích của Kiến Trúc Đa Mô Hình Này:
1. **Trải nghiệm người dùng:** Việc tách biệt giữa **Task Chat** (dùng model lớn) và **Task Đánh giá ngầm** (dùng Llama-8B) giúp học sinh nhận được phản hồi chat gần như ngay lập tức, trong khi hệ thống admin vẫn lưu trữ trọn vẹn dữ liệu đánh giá chất lượng cao mà không bị quá tải.
2. **Chi phí và Scaling:** Việc không dùng một model 70B cho mọi hành động (đặc biệt là các vòng lặp ẩn) giúp tối ưu hóa chi phí API và dễ dàng mở rộng cho hàng nghìn học sinh dùng cùng lúc trên server.
