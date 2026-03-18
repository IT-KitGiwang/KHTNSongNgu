# -*- coding: utf-8 -*-
"""
Seed script - Thêm 50 HSG (Học sinh Giỏi) và 20 HSK (Học sinh Khá)
với bộ nhận xét đa dạng mở rộng hơn seed_students.py cũ.
Run: python seed_hsg_hsk.py
"""
import json_db
import random
from werkzeug.security import generate_password_hash

# ========== TÊN HỌC SINH ==========
ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
      'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Trịnh', 'Cao', 'Mai']
dem_nam = ['Văn', 'Hữu', 'Đức', 'Công', 'Minh', 'Quang', 'Hải', 'Thành', 'Trung', 'Tiến',
           'Tuấn', 'Việt', 'Bảo', 'Gia', 'Nhật', 'Hoàng', 'Phúc', 'Khắc', 'Anh', 'Thế']
ten_nam = ['Anh', 'Bình', 'Cường', 'Dũng', 'Đạt', 'Huy', 'Khoa', 'Long', 'Nam', 'Phong',
           'Quân', 'Sơn', 'Tài', 'Tâm', 'Thắng', 'Trí', 'Tú', 'Vinh', 'Khải', 'Kiên',
           'Lâm', 'Luân', 'Nghĩa', 'Phát', 'Quý', 'Thịnh', 'Tín', 'Toàn', 'Vũ', 'Xuân']
dem_nu = ['Thị', 'Ngọc', 'Thu', 'Phương', 'Hồng', 'Thanh', 'Kiều', 'Bích', 'Trúc', 'Diễm',
          'Tuyết', 'Mai', 'Lan', 'Kim', 'Quỳnh', 'Mỹ', 'Thùy', 'Minh', 'Yến', 'Khánh']
ten_nu = ['An', 'Chi', 'Dung', 'Hà', 'Hiền', 'Hoa', 'Hương', 'Linh', 'Ly', 'My',
          'Nhi', 'Nhung', 'Oanh', 'Quyên', 'Trang', 'Trinh', 'Uyên', 'Vy', 'Yên', 'Châu',
          'Đan', 'Hạnh', 'Khanh', 'Lam', 'Ngân', 'Như', 'Phúc', 'Thảo', 'Vân', 'Xuân']
lop_list = ['6A', '6B', '7A', '7B', '8A', '8B', '9A', '9B']

_vn_map = str.maketrans(
    'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ'
    'ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ',
    'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
    'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
)
def no_dau(s):
    return s.translate(_vn_map).lower().replace(' ', '')

en_nicknames = ['alex', 'john', 'tommy', 'kevin', 'jack', 'henry', 'peter', 'tony',
                'jenny', 'amy', 'lily', 'emma', 'sunny', 'lucky', 'coco', 'david',
                'anna', 'rose', 'ben', 'max', 'sam', 'leo', 'luna', 'sky']

def gen_name():
    if random.choice([True, False]):
        h, d, t = random.choice(ho), random.choice(dem_nam), random.choice(ten_nam)
    else:
        h, d, t = random.choice(ho), random.choice(dem_nu), random.choice(ten_nu)
    return f'{h} {d} {t}', no_dau(h), no_dau(d), no_dau(t)

_used_unames = set(u['tendangnhap'] for u in json_db.load_users())

def gen_username(ho_nd, dem_nd, ten_nd, lop):
    lop_lower = lop.lower()
    birth_year = random.choice(['2011', '2012', '2013', '2k12', '2k13', '09', '10', '11'])
    num = random.choice(['', str(random.randint(1,99)), str(random.randint(100,999))])
    patterns = [
        lambda: f"{dem_nd}{ten_nd}{lop_lower}",
        lambda: f"{dem_nd}{ten_nd}{random.randint(10,999)}",
        lambda: f"{ten_nd}{dem_nd}{birth_year}",
        lambda: f"{ho_nd}{ten_nd}{lop_lower}",
        lambda: f"{ten_nd}{random.choice(['star','pro','vip','ace','top','hsg','gioi','smart'])}{num}",
        lambda: f"{random.choice(en_nicknames)}{ten_nd}{num}",
        lambda: f"{ten_nd}{birth_year}",
        lambda: f"{ho_nd}{dem_nd}{ten_nd}",
        lambda: f"{ten_nd}{ho_nd}{random.randint(1,99)}",
    ]
    for _ in range(50):
        uname = random.choice(patterns)()
        if uname not in _used_unames and len(uname) >= 5:
            _used_unames.add(uname)
            return uname
    fb = f"{ten_nd}{dem_nd}{random.randint(1000,9999)}"
    _used_unames.add(fb)
    return fb

# ========== NGÂN HÀNG NHẬN XÉT ĐA DẠNG ==========

# HSG - Học sinh Giỏi: nhận xét phong phú, cụ thể, có chiều sâu
bank_gioi_toan = [
    "Học sinh nắm vững kiến thức vận dụng cao: giải thành thạo phương trình bậc hai, chứng minh hình học phức tạp. Có khả năng chuyển đổi linh hoạt giữa đại số và hình học để tìm lời giải tối ưu.\n2. Tư duy logic: Phân tích bài toán theo nhiều hướng, biết chọn phương pháp hiệu quả nhất. Lập luận chặt chẽ từ giả thiết đến kết luận, không bỏ sót trường hợp đặc biệt.\n3. Năng lực song ngữ: Đọc và diễn giải bài toán tiếng Anh tốt. Dùng chính xác: quadratic equation, geometric proof, algebraic identity.\n4. Tự học: Chủ động làm thêm đề HSG cấp huyện, tự tìm phương pháp giải sáng tạo ngoài sách giáo khoa.\n5. Đề xuất: Tham gia bồi dưỡng HSG Toán cấp tỉnh; tiếp cận bài toán Olympic Toán quốc tế dạng nhập môn.",

    "Kiến thức vượt chương trình: tự nghiên cứu số học tổ hợp, hiểu sâu mối liên hệ pi–đường tròn–tích phân cơ bản. Giải bài toán tư duy vượt trội so với bạn cùng lớp.\n2. Tư duy logic: Biết đặt câu hỏi 'Điều kiện nào là cần, điều kiện nào là đủ?' khi giải bài. Phân tích trường hợp đầy đủ, không bỏ sót.\n3. Năng lực song ngữ: Viết lời giải song ngữ mạch lạc. Thuật ngữ chính xác: theorem, lemma, corollary, proof by contradiction.\n4. Tự học: Tự tìm hiểu lịch sử toán học, hứng thú với bài toán mở chưa có lời giải hoàn chỉnh.\n5. Đề xuất: Kết nối với CLB Toán học sinh giỏi; hướng dẫn viết báo cáo nghiên cứu mini.",

    "Nắm chắc toàn bộ chương trình THCS: áp dụng linh hoạt bất đẳng thức, hệ phương trình, hình học không gian. Tốc độ tính toán nhanh, ít sai số.\n2. Tư duy logic: Biết nhận dạng dạng bài ngay từ đầu đề, rút ngắn thời gian giải. Kiểm tra lại kết quả bằng phương pháp ngược chiều.\n3. Năng lực song ngữ: Tự tin đọc đề thi tiếng Anh; dùng đúng: variable, coefficient, root, domain, range.\n4. Tự học: Thường xuyên luyện đề thi AMC, SASMO; không nản khi gặp bài khó.\n5. Đề xuất: Cho tiếp cận tài liệu Art of Problem Solving; luyện kỹ năng trình bày thi tự luận.",

    "Hiểu sâu bản chất các định lý: không chỉ thuộc mà còn hiểu TẠI SAO định lý Pythagoras đúng, tại sao định lý Thales vận dụng được ở đây. Năng lực phân tích vượt trội.\n2. Tư duy logic: Tự giải thích được tại sao một cách giải sai khi người khác trình bày. Tư duy phản biện sắc bén.\n3. Năng lực song ngữ: Dịch bài toán Anh → Việt không cần từ điển. Biết thuật ngữ nâng cao: bijection, permutation, combination.\n4. Tự học: Tự đặt bài toán tương tự và giải; chia sẻ kiến thức với bạn trong lớp.\n5. Đề xuất: Bổ nhiệm làm trưởng nhóm học tập; giao vai trò hướng dẫn bạn yếu hơn.",

    "Thành thạo các kỹ thuật giải toán nâng cao: phân tích đa thức nhân tử, căn bậc hai có điều kiện, bất phương trình hệ. Giải chính xác cả bài toán có nhiều ẩn.\n2. Tư duy logic: Hệ thống hóa kiến thức bằng sơ đồ tư duy; biết phân nhánh các trường hợp một cách có cấu trúc.\n3. Năng lực song ngữ: Sử dụng ĐÚNG: simplify, factor, expand, evaluate, substitute trong bài giải tiếng Anh.\n4. Tự học: Chủ động ôn tập trước kỳ thi, lập kế hoạch học cá nhân; không cần giáo viên nhắc nhở.\n5. Đề xuất: Tham gia kỳ thi Toán Kangaroo; luyện trực tuyến trên Khan Academy nâng cao.",
]

bank_gioi_ly = [
    "Hiểu sâu bản chất vật lý: giải thích tại sao vật nổi trong chất lỏng theo áp suất Archimedes, không chỉ thay số vào công thức. Liên hệ xuất sắc lý thuyết với thực nghiệm.\n2. Tư duy logic: Phân tích bài toán lực phức tạp bằng giản đồ lực chi tiết; kiểm tra chiều và độ lớn từng lực trước khi tính.\n3. Năng lực song ngữ: Dùng chính xác: buoyancy, pressure, friction, equilibrium, torque. Đọc tài liệu vật lý tiếng Anh không cần dịch từng từ.\n4. Tự học: Tự thiết kế thí nghiệm đơn giản ở nhà để kiểm chứng định luật Hooke, Newton.\n5. Đề xuất: Cho làm thí nghiệm thực hành nâng cao; tham gia CLB Khoa học Tự nhiên.",

    "Nắm vững từ cơ học đến điện học, quang học: hiểu ý nghĩa vật lý sâu sắc của từng đại lượng. Giải bài tập phức hợp nhiều kiến thức một lúc.\n2. Tư duy logic: Biết dự đoán kết quả trước khi tính; phát hiện ngay khi đáp án vô lý về mặt vật lý.\n3. Năng lực song ngữ: Viết báo cáo thí nghiệm ngắn bằng tiếng Anh. Thuật ngữ tốt: wavelength, frequency, amplitude, electric field.\n4. Tự học: Xem video thí nghiệm MIT OpenCourseWare; hỏi thêm về vật lý thiên văn ngoài chương trình.\n5. Đề xuất: Hướng dẫn viết báo cáo khoa học ngắn; cho tiếp cận đề thi HSG Lý cấp tỉnh.",

    "Giải xuất sắc bài toán nhiệt học và điện học: tính nhiệt lượng trao đổi, phân tích mạch điện có nhiều nhánh phức tạp. Xử lý số liệu thực nghiệm tốt.\n2. Tư duy logic: Luôn phân tích bài toán định tính trước (dự đoán xu hướng) rồi mới tính định lượng.\n3. Năng lực song ngữ: Thuật ngữ điện học chính xác: resistance, voltage, current, parallel circuit, series circuit.\n4. Tự học: Tự tính nhẩm nhanh các đại lượng quen thuộc; hứng thú với vật lý lượng tử cơ bản.\n5. Đề xuất: Cho tham gia dự án STEM; kết nối với nhóm học sinh yêu thích khoa học.",

    "Kiến thức vật lý toàn diện: từ chuyển động thẳng đều đến dao động điều hòa; hiểu mối liên hệ năng lượng–công–công suất sâu sắc. Tự giải được đề thi HSG.\n2. Tư duy logic: Phân tích theo nguyên lý bảo toàn (năng lượng, động lượng) một cách hệ thống; ít sai sót do thiếu bước.\n3. Năng lực song ngữ: Đọc được đề thi quốc tế IPhO mức nhập môn; dùng notation khoa học chuẩn.\n4. Tự học: Theo dõi kênh Physics Girl, Veritasium bằng tiếng Anh; tự tóm tắt kiến thức sau mỗi video.\n5. Đề xuất: Bồi dưỡng HSG Vật lý; cho tiếp xúc thực hành phòng thí nghiệm trường THPT.",

    "Xuất sắc về quang học và điện từ: giải bài tập thấu kính, gương, mạch từ chính xác. Biết vận dụng nguyên lý chồng chất sóng, giao thoa ánh sáng cơ bản.\n2. Tư duy logic: Vẽ sơ đồ tia sáng chính xác; phân tích chiều truyền và góc khúc xạ chi tiết.\n3. Năng lực song ngữ: Thuật ngữ quang học: refraction, lens, focal length, magnification. Đọc bài báo khoa học phổ thông tiếng Anh.\n4. Tự học: Dùng PhET Simulations để tự thí nghiệm ảo; ghi chép quan sát nghiêm túc.\n5. Đề xuất: Cho xây dựng dự án kính thiên văn đơn giản; tham gia cuộc thi KHKT cấp trường.",
]

bank_gioi_hoa = [
    "Vận dụng cao: hiểu sâu cấu tạo nguyên tử, mô hình electron hóa trị, giải thích tính chất hóa học qua cấu trúc. Cân bằng thành thạo phương trình oxi hóa–khử phức tạp nhất chương trình.\n2. Tư duy logic: Dự đoán sản phẩm phản ứng dựa trên quy luật bảng tuần hoàn; kiểm tra bảo toàn nguyên tử và điện tích sau mỗi bước.\n3. Năng lực song ngữ: Danh pháp IUPAC thành thạo; đọc được nhãn sản phẩm hóa học tiếng Anh. Thuật ngữ: oxidation state, ionic compound, covalent bond.\n4. Tự học: Tự nghiên cứu hóa hữu cơ vượt chương trình; hứng thú với hóa sinh và phản ứng trong cơ thể.\n5. Đề xuất: Cho làm thí nghiệm tổng hợp chất đơn giản; tham gia HSG Hóa cấp thành phố.",

    "Nắm vững hóa vô cơ và bước đầu hóa hữu cơ: tự viết phản ứng este hóa, tráng gương, trùng hợp. Hiểu ý nghĩa thực tiễn từng loại phản ứng trong công nghiệp.\n2. Tư duy logic: Hệ thống hóa kiến thức theo nhóm nguyên tố; giải bài tính toán hóa học nhiều bước chính xác.\n3. Năng lực song ngữ: Đọc hiểu bảo an toàn hóa chất tiếng Anh; biết SDS (Safety Data Sheet). Thuật ngữ: reagent, catalyst, yield, solution.\n4. Tự học: Xem video thí nghiệm hóa học an toàn; ghi chép hiện tượng quan sát được tỉ mỉ.\n5. Đề xuất: Hướng dẫn làm báo cáo thí nghiệm chuẩn; giới thiệu hóa học xanh, hóa học bền vững.",

    "Kiến thức hóa học rộng và hệ thống: liên kết tốt từ nguyên tử → phân tử → phản ứng → ứng dụng thực tiễn. Không nhầm lẫn hóa trị, không sai công thức phân tử.\n2. Tư duy logic: Phân tích cơ chế phản ứng ở mức phân tử, giải thích tại sao axit HCl mạnh hơn CH3COOH.\n3. Năng lực song ngữ: Thuật ngữ chính xác: mole, molarity, titration, pH, electrolysis. Dịch được phương pháp thí nghiệm tiếng Anh.\n4. Tự học: Chủ động tìm hiểu hóa học trong nấu ăn, y tế, môi trường; kết nối kiến thức với đời sống.\n5. Đề xuất: Cho làm dự án nghiên cứu chất lượng nước; giới thiệu hóa phân tích cơ bản.",

    "Xuất sắc về phản ứng oxi hóa khử và điện phân: xác định chất oxi hóa, chất khử, chiều phản ứng chính xác tuyệt đối. Giải bài toán điện phân có màng ngăn.\n2. Tư duy logic: Lập bảng theo dõi số oxi hóa; cân bằng electron chặt chẽ, không sai sót.\n3. Năng lực song ngữ: Thuật ngữ điện hóa: anode, cathode, electrolyte, half-reaction, reduction potential.\n4. Tự học: Tự học hóa phân tích cơ bản; biết dùng phần mềm vẽ phân tử 3D (Avogadro, Jmol).\n5. Đề xuất: Cho tiếp cận đề thi IChO mức nhập môn; hướng dẫn viết phương trình ion rút gọn.",

    "Hiểu tường tận bảng tuần hoàn: giải thích xu hướng tính kim loại, phi kim, bán kính nguyên tử qua từng chu kỳ và nhóm. Nắm vững hóa học của các nguyên tố quan trọng.\n2. Tư duy logic: Từ cấu hình electron suy ra tính chất hóa học; dự đoán sản phẩm chính xác trước khi thực nghiệm.\n3. Năng lực song ngữ: Đọc được tài liệu hóa học Cambridge A-Level cơ bản; thuật ngữ: ionization energy, electronegativity.\n4. Tự học: Dùng Chemspider, PubChem để tra cứu tính chất chất; tự học ngoài giờ trên ChemLibreTexts.\n5. Đề xuất: Cho nghiên cứu cơ chế phản ứng hữu cơ; giới thiệu hóa lý và nhiệt động học cơ bản.",
]

bank_gioi_sinh = [
    "Vận dụng cao: hiểu sâu cơ chế di truyền Mendel và phi Mendel; giải thích được tại sao có ngoại lệ trong di truyền. Liên hệ kiến thức ADN → ARN → Protein thành thạo.\n2. Tư duy logic: Phân tích phả hệ, xác định kiểu gen cha mẹ chính xác; giải bài toán di truyền nhiều gen liên kết.\n3. Năng lực song ngữ: Thuật ngữ chính xác: genotype, phenotype, dominant, recessive, homozygous, heterozygous.\n4. Tự học: Tự đọc về công nghệ CRISPR-Cas9, PCR trong chẩn đoán bệnh; hứng thú với di truyền học phân tử.\n5. Đề xuất: Cho làm dự án phả hệ gia đình; giới thiệu sinh học phân tử, công nghệ sinh học hiện đại.",

    "Kiến thức sinh học toàn diện từ tế bào đến hệ sinh thái: hiểu mối quan hệ năng lượng trong chuỗi thức ăn, chu trình vật chất trong hệ sinh thái. Nắm vững sinh lý thực vật và động vật.\n2. Tư duy logic: Liên kết kiến thức theo mô hình hệ thống: from molecules to ecosystems. Phân tích nhân quả trong quần thể sinh vật.\n3. Năng lực song ngữ: Thuật ngữ tốt: ecosystem, biodiversity, photosynthesis, cellular respiration, homeostasis.\n4. Tự học: Xem BBC Earth, National Geographic bằng tiếng Anh; ghi chép quan sát thiên nhiên xung quanh.\n5. Đề xuất: Cho tham gia dự án nghiên cứu đa dạng sinh học địa phương; hướng dẫn làm tiêu bản hiển vi.",

    "Xuất sắc về di truyền và tiến hóa: giải bài tập di truyền nhiều tính trạng, viết sơ đồ lai chính xác. Hiểu cơ chế chọn lọc tự nhiên và bằng chứng tiến hóa.\n2. Tư duy logic: Phân tích từng bước: xác định tỉ lệ kiểu gen → kiểu hình → xác suất phân li độc lập.\n3. Năng lực song ngữ: Thuật ngữ di truyền và tiến hóa: mutation, natural selection, adaptation, speciation, gene pool.\n4. Tự học: Đọc sách 'The Selfish Gene' phiên bản đơn giản hóa; xem TED-Ed về sinh học tiến hóa.\n5. Đề xuất: Cho nghiên cứu case study bệnh di truyền (máu khó đông, bạch tạng); mở rộng sang sinh học tiến hóa phân tử.",

    "Giỏi cả lý thuyết lẫn thực hành: sử dụng kính hiển vi thành thạo, phân biệt chính xác tế bào nhân sơ và nhân thực, quan sát rõ các bào quan. Vẽ sơ đồ tế bào chi tiết.\n2. Tư duy logic: Phân tích quá trình phân bào: nguyên phân vs giảm phân, liên hệ với di truyền và sinh sản.\n3. Năng lực song ngữ: Thuật ngữ tế bào học: organelle, mitochondria, chloroplast, endoplasmic reticulum, Golgi apparatus.\n4. Tự học: Dùng Khan Academy Biology; xem animation phân bào trực tuyến và giải thích cho bạn bè.\n5. Đề xuất: Cho làm mô hình tế bào 3D; hướng dẫn kỹ thuật nhuộm tiêu bản và quan sát hiển vi.",

    "Hiểu sâu sinh lý người: giải thích cơ chế điều hòa huyết áp, điều hòa thân nhiệt, hệ miễn dịch. Liên kết kiến thức sinh học cơ thể với y học và sức khỏe.\n2. Tư duy logic: Phân tích theo mô hình feedback loop: kích thích → đáp ứng → điều chỉnh. Hệ thống hóa rõ ràng.\n3. Năng lực song ngữ: Thuật ngữ y sinh: immune system, antibody, hormone, homeostasis, nervous system, endocrine.\n4. Tự học: Đọc bài báo y khoa phổ thông tiếng Anh; hứng thú với sinh học thần kinh và tâm lý học.\n5. Đề xuất: Cho làm bài tập case study bệnh lý; giới thiệu giải phẫu cơ thể người và y học hiện đại.",
]

# HSK - Học sinh Khá: nhận xét chi tiết, cụ thể, tích cực nhưng chỉ ra điểm cần cải thiện
bank_kha_toan = [
    "Nắm tốt kiến thức đại số: giải được phương trình bậc hai, bất phương trình, hệ hai ẩn. Khi gặp bài hình học phức tạp cần thêm thời gian xây dựng hình vẽ phụ trợ.\n2. Tư duy logic: Trình bày lời giải có cấu trúc, đôi khi nhảy cóc bước trung gian làm giám khảo khó theo dõi. Nên tập trình bày rõ từng bước.\n3. Năng lực song ngữ: Đọc hiểu đề toán tiếng Anh cơ bản; biết thuật ngữ: equation, fraction, percentage, angle.\n4. Tự học: Chăm làm bài tập về nhà; chủ yếu theo hướng dẫn, chưa tự tìm bài bổ sung.\n5. Đề xuất: Luyện thêm bài hình học chứng minh; tập viết lời giải đầy đủ không bỏ bước.",

    "Kiến thức số học và đại số vững chắc: tính toán nhanh, ít sai số cơ bản. Phần hình học còn lúng túng khi bài cần nhiều bước phụ.\n2. Tư duy logic: Nhận dạng dạng bài tốt nhưng khi bài thay đổi cách hỏi dễ bị nhầm hướng. Cần luyện đọc đề kỹ hơn.\n3. Năng lực song ngữ: Nhận diện tốt ký hiệu toán học quốc tế; biết dùng thuật ngữ: perpendicular, parallel, similar.\n4. Tự học: Tích cực làm thêm bài; đôi khi bỏ qua các dạng bài khó vì ngại suy nghĩ lâu.\n5. Đề xuất: Tăng thời gian luyện bài hình học; tập không bỏ qua bài khó mà hỏi giáo viên sau khi cố gắng.",

    "Thông hiểu kiến thức cơ bản đến nâng cao bước đầu: hiểu hằng đẳng thức, phân tích nhân tử, căn bậc hai. Khi gặp bài tổng hợp nhiều kỹ năng thì chậm hơn.\n2. Tư duy logic: Có tư duy phân tích tốt; đôi khi thiếu kiên nhẫn kiểm tra lại đáp án trước khi nộp.\n3. Năng lực song ngữ: Đọc và dịch đề toán tiếng Anh cở 70% chính xác; cần cải thiện vốn từ thuật ngữ.\n4. Tự học: Chủ động hỏi khi không hiểu; thái độ học tập tích cực và cầu tiến.\n5. Đề xuất: Xây dựng thói quen kiểm tra lại; rèn thêm bài tổng hợp nhiều kiến thức cùng lúc.",

    "Giải tốt bài tập vận dụng mức độ thông hiểu; bắt đầu tiếp cận được bài vận dụng cao nếu có gợi ý ban đầu. Số học và đại số là thế mạnh.\n2. Tư duy logic: Biết phân tích bài toán 2-3 bước; khi đến bước 4 trở lên cần hướng dẫn thêm.\n3. Năng lực song ngữ: Biết đọc đề và trả lời câu hỏi trắc nghiệm tiếng Anh mức basic; vốn từ cần mở rộng.\n4. Tự học: Làm đầy đủ bài về nhà; hỏi bạn bè và giáo viên khi cần; thái độ học tập đáng khen.\n5. Đề xuất: Thêm bài tập vận dụng cao dần; hướng dẫn kỹ thuật giải toán nhiều bước phức tạp.",

    "Nắm chắc công thức và quy tắc; áp dụng đúng trong 85% bài tập. Phần hay sai là toán tỉ lệ và bài toán thực tế có ẩn nghĩa phức tạp.\n2. Tư duy logic: Biết lập phương trình từ bài toán thực tế; đôi khi chọn ẩn không tối ưu làm tính toán phức tạp hơn cần.\n3. Năng lực song ngữ: Đọc hiểu bài word problem tiếng Anh cơ bản; cần học thêm từ vựng toán thực tế.\n4. Tự học: Ôn bài thường xuyên; ghi chép cẩn thận; đôi khi thụ động chờ giáo viên giải đáp.\n5. Đề xuất: Hướng dẫn chọn ẩn hiệu quả; luyện đọc đề bài thực tế bằng tiếng Anh mỗi tuần.",
]

bank_kha_ly = [
    "Thông hiểu kiến thức cơ học và nhiệt học: áp dụng đúng công thức trong 80% bài. Phần điện học còn lúng túng khi mạch có nhiều nhánh.\n2. Tư duy logic: Biết phân tích lực tác dụng theo phương ngang-dọc; đôi khi quên lực ma sát hoặc lực đẩy Archimedes.\n3. Năng lực song ngữ: Biết thuật ngữ cơ bản: force, velocity, acceleration, mass, temperature. Đọc đề tiếng Anh cơ bản.\n4. Tự học: Xem video thí nghiệm; liên hệ kiến thức với hiện tượng xung quanh khá tốt.\n5. Đề xuất: Luyện thêm bài tập điện học; ôn lại đơn vị đo và cách đổi đơn vị trước khi tính.",

    "Kiến thức vật lý khá toàn diện: từ chuyển động đến ánh sáng đều nắm cơ bản. Điểm yếu là bài toán tổng hợp, phân tích nhiều định luật cùng lúc.\n2. Tư duy logic: Phân tích bài đúng hướng ban đầu; đôi khi tính toán sai do bỏ sót hệ số hoặc đổi đơn vị.\n3. Năng lực song ngữ: Nhận diện tốt ký hiệu vật lý quốc tế (v, a, F, P, E); đọc công thức tiếng Anh được.\n4. Tự học: Chăm chỉ, làm đủ bài tập; đôi khi cần thêm thời gian để nắm bài mới.\n5. Đề xuất: Luyện đề tổng hợp nhiều kiến thức; rèn thói quen kiểm tra đơn vị ở kết quả cuối.",

    "Nắm tốt quang học và điện học cơ bản: vẽ được đường truyền ánh sáng, phân tích mạch điện đơn giản đúng. Cơ học nâng cao còn hạn chế.\n2. Tư duy logic: Có khả năng liên hệ vật lý với hiện tượng thực tế tốt; đôi khi bài toán tính toán nhiều bước bị sai ở bước cuối.\n3. Năng lực song ngữ: Biết các thuật ngữ điện và quang: voltage, current, lens, focal point, reflection.\n4. Tự học: Hay đặt câu hỏi 'Tại sao?' khi học; thái độ tích cực khám phá kiến thức mới.\n5. Đề xuất: Tăng bài tập cơ học nhiều lực; luyện tính toán nhiều bước có kiểm tra từng bước.",

    "Hiểu tốt khái niệm năng lượng, công, công suất: áp dụng đúng định lý động năng-thế năng. Phần nhiệt học đổi nhiệt lượng đôi khi nhầm công thức Q = mc∆t.\n2. Tư duy logic: Phân tích đúng chiều biến đổi năng lượng; đôi khi thiếu nhận xét về dấu (+ hoặc -).\n3. Năng lực song ngữ: Biết thuật ngữ năng lượng: kinetic energy, potential energy, work, power, efficiency.\n4. Tự học: Chủ động tìm ứng dụng thực tế; hay chia sẻ tìm hiểu được với bạn cùng lớp.\n5. Đề xuất: Ôn lại các công thức nhiệt học; hướng dẫn phân tích dấu đại lượng kỹ hơn.",
]

bank_kha_hoa = [
    "Viết đúng và cân bằng phương trình hóa học cơ bản; tính toán mol chính xác trong bài toán một phản ứng. Bài có nhiều phản ứng nối tiếp còn cần nhiều thời gian.\n2. Tư duy logic: Hiểu quy trình giải bài hóa tính toán; đôi khi không kiểm tra lại bảo toàn khối lượng.\n3. Năng lực song ngữ: Biết thuật ngữ: atom, molecule, element, compound, reaction, product, reactant.\n4. Tự học: Hay xem video thí nghiệm hóa học; tò mò về hiện tượng hóa học trong đời sống.\n5. Đề xuất: Luyện bài toán tính toán nhiều phản ứng; tập kiểm tra bảo toàn khối lượng sau mỗi bài.",

    "Nắm tốt axit-bazơ-muối và tính chất hóa học cơ bản của từng nhóm. Hóa hữu cơ bắt đầu tiếp cận được ở mức nhận biết hiđrocacbon.\n2. Tư duy logic: Phân loại phản ứng đúng; đôi khi nhầm khi bài cần phân biệt nhiều loại oxit cùng lúc.\n3. Năng lực song ngữ: Biết tên nguyên tố và hợp chất thông dụng tiếng Anh; đọc nhãn chai hóa chất được.\n4. Tự học: Chăm học; ghi chép đầy đủ; thỉnh thoảng hỏi thêm về ứng dụng thực tiễn của phản ứng.\n5. Đề xuất: Tăng bài tập nhận biết chất; luyện chi tiết hơn về hóa hữu cơ cơ bản.",

    "Kiến thức hóa học tương đối tốt: biết cách lập công thức hóa học từ hóa trị, tính được khối lượng mol phân tử phức tạp. Phản ứng oxi hóa khử còn nhầm chiều.\n2. Tư duy logic: Biết phân tích bài toán hóa theo các bước: nhận diện chất → viết ptpư → tính toán mol.\n3. Năng lực song ngữ: Đọc bảng tuần hoàn tiếng Anh thành thạo; biết ký hiệu IUPAC cơ bản.\n4. Tự học: Luyện thêm qua app Periodic Table; xem video thí nghiệm hóa học trước khi học lý thuyết.\n5. Đề xuất: Ôn kỹ phản ứng oxi hóa–khử; hướng dẫn phân tích số oxi hóa có hệ thống.",

    "Hiểu tốt cấu tạo bảng tuần hoàn: nắm xu hướng biến đổi tính chất theo chu kỳ và nhóm. Bài thi đòi hỏi vận dụng cao còn thiếu ý tưởng sáng tạo.\n2. Tư duy logic: Phân loại bài đúng; trình bày rõ ràng; đôi khi cần thêm giải thích lý do chọn phương pháp.\n3. Năng lực song ngữ: Biết mô tả tính chất hóa học bằng tiếng Anh cơ bản; vốn từ cần mở rộng thêm.\n4. Tự học: Nghiêm túc ôn tập; ghi bài chi tiết; thiếu tính sáng tạo trong tìm phương pháp giải mới.\n5. Đề xuất: Bổ sung bài tập vận dụng sáng tạo; khuyến khích đặt câu hỏi phản biện trong học.",
]

bank_kha_sinh = [
    "Nhận diện và phân tích cấu trúc tế bào tốt: phân biệt tế bào ĐV–TV, nhân sơ–nhân thực. Phần di truyền còn lúng túng bài có nhiều tính trạng.\n2. Tư duy logic: Mô tả quá trình sinh học có trình tự; đôi khi thiếu giải thích cơ chế tại sao.\n3. Năng lực song ngữ: Biết thuật ngữ: cell, nucleus, chromosome, DNA, gene, protein, evolution.\n4. Tự học: Hay đặt câu hỏi liên hệ sinh học với y tế và môi trường; thái độ tích cực.\n5. Đề xuất: Luyện thêm bài di truyền nhiều tính trạng; hướng dẫn cách viết sơ đồ lai đầy đủ.",

    "Kiến thức sinh học khá toàn diện: từ quang hợp đến hệ sinh thái đều nắm được. Phần tiến hóa và bằng chứng tiến hóa còn chưa sắc bén.\n2. Tư duy logic: Phân tích mối quan hệ giữa sinh vật với môi trường tốt; đôi khi thiếu liên kết giữa các cấp độ tổ chức.\n3. Năng lực song ngữ: Đọc tên khoa học sinh vật đúng; biết thuật ngữ hệ sinh thái: food chain, biodiversity, habitat.\n4. Tự học: Xem phim khoa học tự nhiên thường xuyên; ghi chép quan sát thiên nhiên xung quanh.\n5. Đề xuất: Bổ sung kiến thức tiến hóa; cho làm dự án quan sát đa dạng sinh học địa phương.",

    "Nắm tốt sinh lý người: hiểu chức năng các cơ quan hô hấp, tiêu hóa, tuần hoàn. Phần thần kinh và nội tiết còn chưa sâu.\n2. Tư duy logic: Trình bày quá trình tiêu hóa, hấp thu theo trình tự đúng; đôi khi lẫn lộn enzym tiêu hóa.\n3. Năng lực song ngữ: Biết thuật ngữ giải phẫu cơ bản: heart, lung, kidney, liver, brain, stomach.\n4. Tự học: Quan tâm sức khỏe và y tế; hay hỏi thêm về bệnh tật liên quan đến cơ quan học.\n5. Đề xuất: Tăng bài tập hệ thần kinh và nội tiết; giới thiệu sách sinh lý người cho học sinh khá.",

    "Thông hiểu di truyền Mendel: giải được lai một tính, bước đầu lai hai tính. Phần di truyền liên kết và giới tính cần ôn thêm.\n2. Tư duy logic: Phân tích kiểu gen–kiểu hình đúng ở bài cơ bản; bài phức tạp cần thêm gợi ý.\n3. Năng lực song ngữ: Biết thuật ngữ di truyền: gene, allele, dominant, recessive, cross, offspring.\n4. Tự học: Dùng Punnett square thành thạo; chủ động tự làm thêm bài tập dạng lai.\n5. Đề xuất: Ôn kỹ di truyền liên kết và di truyền theo giới tính; hướng dẫn phân tích phả hệ phức tạp.",
]

def pick_eval(bank, level_bank, subject_name):
    """Chọn ngẫu nhiên 1 đánh giá từ bank tương ứng level."""
    text = random.choice(level_bank)
    return f"1. Độ sâu kiến thức: {text}"

def build_eval_gioi(subject):
    banks = {
        'Toán': bank_gioi_toan,
        'Lý': bank_gioi_ly,
        'Hóa': bank_gioi_hoa,
        'Sinh': bank_gioi_sinh,
    }
    return pick_eval(banks[subject], banks[subject], subject)

def build_eval_kha(subject):
    banks = {
        'Toán': bank_kha_toan,
        'Lý': bank_kha_ly,
        'Hóa': bank_kha_hoa,
        'Sinh': bank_kha_sinh,
    }
    return pick_eval(banks[subject], banks[subject], subject)

# ========== CHẠY SEED ==========
try:
    print("=== BẮT ĐẦU SEED HSG + HSK ===")

    # --- 50 HSG: tất cả đều có 4 môn Giỏi, đánh giá chi tiết đa dạng ---
    print("Đang tạo 50 HSG...")
    for i in range(50):
        name, ho_nd, dem_nd, ten_nd = gen_name()
        lop = random.choice(lop_list)
        uname = gen_username(ho_nd, dem_nd, ten_nd, lop)
        pw = generate_password_hash("123456")
        user = json_db.create_user(uname, pw, f"{name} ({lop})")

        updates = {}
        # Tất cả 4 môn đều Giỏi với đánh giá chi tiết
        for mon, k_nl, k_ld, k_sc in [
            ('Toán', 'nangluctoan', 'lydotoan', 'socautoan'),
            ('Lý',   'nanglucly',   'lydoly',   'socauly'),
            ('Hóa',  'nangluchoa',  'lydohoa',  'socauhoa'),
            ('Sinh', 'nanglucsinh', 'lydosinh', 'socausinh'),
        ]:
            updates[k_nl] = 'Gioi'
            updates[k_ld] = build_eval_gioi(mon)
            updates[k_sc] = random.randint(15, 120)

        json_db.update_user(user['id'], updates)

    print(f"✓ Tạo xong 50 HSG")

    # --- 20 HSK: tất cả đều có 4 môn Khá, đánh giá tích cực cụ thể ---
    print("Đang tạo 20 HSK...")
    for i in range(20):
        name, ho_nd, dem_nd, ten_nd = gen_name()
        lop = random.choice(lop_list)
        uname = gen_username(ho_nd, dem_nd, ten_nd, lop)
        pw = generate_password_hash("123456")
        user = json_db.create_user(uname, pw, f"{name} ({lop})")

        updates = {}
        for mon, k_nl, k_ld, k_sc in [
            ('Toán', 'nangluctoan', 'lydotoan', 'socautoan'),
            ('Lý',   'nanglucly',   'lydoly',   'socauly'),
            ('Hóa',  'nangluchoa',  'lydohoa',  'socauhoa'),
            ('Sinh', 'nanglucsinh', 'lydosinh', 'socausinh'),
        ]:
            updates[k_nl] = 'Kha'
            updates[k_ld] = build_eval_kha(mon)
            updates[k_sc] = random.randint(8, 80)

        json_db.update_user(user['id'], updates)

    print(f"✓ Tạo xong 20 HSK")

    total = len(json_db.get_all_users())
    print(f"\n[OK] Tổng cộng {total} users trong hệ thống")
    print("Mật khẩu mặc định: 123456")
    print("=== HOÀN THÀNH ===")

except Exception as e:
    print(f"Lỗi: {e}")
    import traceback
    traceback.print_exc()
