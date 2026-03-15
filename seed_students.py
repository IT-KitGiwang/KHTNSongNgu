"""
Seed script to populate data/users.json with sample student data.
Run: python seed_students.py
"""
import json_db
import random
from werkzeug.security import generate_password_hash

# Dữ liệu giả lập
ho_list = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
ten_dem_nam = ['Văn', 'Hữu', 'Đức', 'Công', 'Minh', 'Quang', 'Hải', 'Thành', 'Trung', 'Tiến', 'Tuấn', 'Việt', 'Bảo', 'Gia']
ten_nam = ['Anh', 'Bình', 'Cường', 'Dũng', 'Đạt', 'Huy', 'Khoa', 'Long', 'Nam', 'Phong', 'Quân', 'Sơn', 'Tài', 'Tâm', 'Thắng', 'Trí', 'Tú', 'Vinh']
ten_dem_nu = ['Thị', 'Ngọc', 'Thu', 'Phương', 'Hồng', 'Thanh', 'Kiều', 'Bích', 'Trúc', 'Diễm', 'Tuyết', 'Mai', 'Lan', 'Kim']
ten_nu = ['An', 'Chi', 'Dung', 'Hà', 'Hiền', 'Hoa', 'Hương', 'Linh', 'Ly', 'My', 'Nhi', 'Nhung', 'Oanh', 'Quyên', 'Trang', 'Trinh', 'Uyên', 'Vy']
lop_list = ['6A', '6B', '6C', '7A', '7B', '7C', '8A', '8B', '8C', '9A', '9B', '9C']

def generate_name():
    if random.choice([True, False]):
        return f'{random.choice(ho_list)} {random.choice(ten_dem_nam)} {random.choice(ten_nam)}'
    else:
        return f'{random.choice(ho_list)} {random.choice(ten_dem_nu)} {random.choice(ten_nu)}'

levels = ['Giỏi', 'Khá', 'TB', 'Yếu']
weights = [0.15, 0.35, 0.40, 0.10]

lydo_mau = {
    'Toán': {
        'Giỏi': 'Học sinh có tư duy phản biện xuất sắc, đưa ra cách giải nhanh và tối ưu cho bài phương trình bậc hai.',
        'Khá': 'Nắm chắc kiến thức căn bản về biến đổi đại số, giải toán chính xác.',
        'TB': 'Có khả năng giải toán ở mức độ hiểu bài mẫu, hay mắc lỗi dấu khi chuyển vế.',
        'Yếu': 'Học sinh thường xuyên nhầm lẫn giữa công thức tính diện tích và chu vi.'
    },
    'Lý': {
        'Giỏi': 'Khả năng liên hệ thực tiễn cao, liên tục đặt câu hỏi mở rộng.',
        'Khá': 'Hiểu bản chất của định luật bảo toàn năng lượng.',
        'TB': 'Chỉ thuộc lòng công thức chứ chưa hiểu sâu về ý nghĩa vật lý.',
        'Yếu': 'Sự tự học còn hạn chế, nhầm lẫn khái niệm trọng lượng và khối lượng.'
    },
    'Hóa': {
        'Giỏi': 'Sử dụng chuẩn xác tên gọi danh pháp tiếng Anh.',
        'Khá': 'Viết đúng phương trình hóa học và biết cân bằng số nguyên tử.',
        'TB': 'Đọc hiểu tên nguyên tố cơ bản tốt nhưng còn lúng túng khi viết công thức muối.',
        'Yếu': 'Không phân biệt được hiện tượng vật lý và hiện tượng hóa học.'
    },
    'Sinh': {
        'Giỏi': 'Câu hỏi tìm tòi sâu rộng về lĩnh vực di truyền học.',
        'Khá': 'Nhận diện đúng cấu tạo tế bào động vật và thực vật.',
        'TB': 'Hiểu được nguyên lý tuần hoàn máu nhưng chưa làm rõ chức năng từng thành phần.',
        'Yếu': 'Các kiến thức nền tảng như sinh thái học, chuỗi thức ăn còn hổng.'
    }
}

try:
    # Keep admin users, remove students
    admin_users = ['lequangphuc', 'phungvanhanh', 'hoangthinha', 'nguyenthithuong']
    users = json_db.load_users()
    users = [u for u in users if u['tendangnhap'] in admin_users]
    json_db.save_users(users)
    print("Done: cleaned old student data.")

    # Tạo 40 học sinh có data đầy đủ
    for i in range(1, 41):
        ho_ten = generate_name()
        ten_dn = f"hs{i:03d}"
        mat_khau_hash = generate_password_hash("123456")
        lop = random.choice(lop_list)
        
        user = json_db.create_user(ten_dn, mat_khau_hash, f"{ho_ten} ({lop})")

        updates = {}
        for mon, k_nangluc, k_lydo, k_socau in [
            ('Toán', 'nangluctoan', 'lydotoan', 'socautoan'),
            ('Lý', 'nanglucly', 'lydoly', 'socauly'),
            ('Hóa', 'nangluchoa', 'lydohoa', 'socauhoa'),
            ('Sinh', 'nanglucsinh', 'lydosinh', 'socausinh')
        ]:
            if random.random() < 0.8:
                nl = random.choices(levels, weights)[0]
                updates[k_nangluc] = "Gioi" if nl == "Giỏi" else ("Kha" if nl == "Khá" else ("Yeu" if nl == "Yếu" else "TB"))
                updates[k_lydo] = lydo_mau[mon][nl]
                updates[k_socau] = random.randint(10, 85)

        if updates:
            json_db.update_user(user['id'], updates)

    # 10 HS mới đăng ký chưa có đánh giá
    for i in range(41, 51):
        ho_ten = generate_name()
        ten_dn = f"hs{i:03d}"
        mat_khau_hash = generate_password_hash("123456")
        lop = random.choice(lop_list)
        json_db.create_user(ten_dn, mat_khau_hash, f"{ho_ten} ({lop})")

    print("Done: seeded 50 students into data/users.json!")

except Exception as e:
    print(f"Error: {e}")
