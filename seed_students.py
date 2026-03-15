# -*- coding: utf-8 -*-
"""
Seed script - Tạo 50 học sinh giả lập với đánh giá 5 tiêu chí đa dạng.
Mỗi đánh giá được ghép ngẫu nhiên từ ngân hàng câu → không trùng lặp.
Run: python seed_students.py
"""
import json_db
import random
from werkzeug.security import generate_password_hash

# ========== TÊN HỌC SINH ==========
ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
dem_nam = ['Văn', 'Hữu', 'Đức', 'Công', 'Minh', 'Quang', 'Hải', 'Thành', 'Trung', 'Tiến', 'Tuấn', 'Việt', 'Bảo', 'Gia']
ten_nam = ['Anh', 'Bình', 'Cường', 'Dũng', 'Đạt', 'Huy', 'Khoa', 'Long', 'Nam', 'Phong', 'Quân', 'Sơn', 'Tài', 'Tâm', 'Thắng', 'Trí', 'Tú', 'Vinh']
dem_nu = ['Thị', 'Ngọc', 'Thu', 'Phương', 'Hồng', 'Thanh', 'Kiều', 'Bích', 'Trúc', 'Diễm', 'Tuyết', 'Mai', 'Lan', 'Kim']
ten_nu = ['An', 'Chi', 'Dung', 'Hà', 'Hiền', 'Hoa', 'Hương', 'Linh', 'Ly', 'My', 'Nhi', 'Nhung', 'Oanh', 'Quyên', 'Trang', 'Trinh', 'Uyên', 'Vy']
lop_list = ['6A', '6B', '7A', '7B', '8A', '8B', '9A', '9B']

def gen_name():
    if random.choice([True, False]):
        return f'{random.choice(ho)} {random.choice(dem_nam)} {random.choice(ten_nam)}'
    return f'{random.choice(ho)} {random.choice(dem_nu)} {random.choice(ten_nu)}'

levels = ['Gioi', 'Kha', 'TB', 'Yeu']
weights = [0.15, 0.35, 0.40, 0.10]

# ==================================================================
# NGÂN HÀNG CÂU ĐÁNH GIÁ — mỗi tiêu chí nhiều biến thể
# Sẽ ghép ngẫu nhiên 5 tiêu chí → mỗi HS có đánh giá khác nhau
# ==================================================================

# Cấu trúc: bank[môn][level][tiêu_chí] = [danh sách các câu]

bank = {
  'Toán': {
    'Gioi': {
      'kienthuc': [
        "Học sinh nắm vững kiến thức ở mức vận dụng cao: giải thành thạo phương trình bậc hai, hệ phương trình và bất đẳng thức. Tự giải thích được bản chất các khái niệm trừu tượng.",
        "Kiến thức toán học rất sâu — hiểu được mối liên hệ giữa đại số và hình học, vận dụng linh hoạt trong nhiều dạng bài khác nhau. Có khả năng chứng minh định lý bằng nhiều cách.",
        "Nắm chắc kiến thức vượt chương trình THCS: tiếp cận được đề thi HSG cấp huyện/thành phố. Giải quyết bài toán đa bước phức tạp một cách tự tin.",
      ],
      'logic': [
        "Lập luận chặt chẽ, chia nhỏ bài toán phức tạp thành các bước rõ ràng. Biết suy luận ngược từ kết quả để kiểm chứng đáp án.",
        "Tư duy phản biện xuất sắc — đưa ra nhiều phương pháp giải cho cùng một bài toán, so sánh và chọn cách tối ưu nhất.",
        "Phân tích bài toán logic, xây dựng lời giải từ giả thiết đến kết luận mạch lạc. Tự đặt câu hỏi 'Nếu thay đổi điều kiện thì kết quả sẽ ra sao?'",
      ],
      'songngu': [
        "Sử dụng đúng thuật ngữ toán học tiếng Anh (equation, inequality, variable, coefficient). Tự tin diễn đạt lời giải bằng tiếng Anh.",
        "Đọc hiểu đề bài và tài liệu toán tiếng Anh tốt. Sử dụng thuật ngữ chính xác: perpendicular, congruent, quadratic.",
        "Năng lực song ngữ tốt — chuyển đổi linh hoạt giữa tiếng Việt và tiếng Anh khi giải toán. Viết lời giải song ngữ mạch lạc.",
      ],
      'tuhoc': [
        "Rất chủ động — tự tìm thêm bài tập ngoài sách giáo khoa, đặt câu hỏi mở rộng vượt chương trình.",
        "Ham học hỏi, liên tục hỏi 'Vì sao?' và 'Có cách nào khác không?'. Tự tìm hiểu các phương pháp giải sáng tạo.",
        "Chủ động nghiên cứu thêm về ứng dụng toán trong thực tế, thích khám phá các bài toán thách thức.",
      ],
      'dexuat': [
        "Đề xuất: Cho tham gia bồi dưỡng HSG Toán, tiếp cận đề Olympic và bài tập tư duy sáng tạo.",
        "Đề xuất: Giới thiệu sách toán nâng cao, cho nghiên cứu các vấn đề mở. Khuyến khích thi Toán cấp thành phố.",
        "Đề xuất: Tạo nhóm học tập nâng cao, cho tiếp cận tài liệu tiếng Anh về toán tổ hợp và số học.",
      ],
    },
    'Kha': {
      'kienthuc': [
        "Thông hiểu tốt — nắm được các công thức đại số cơ bản, áp dụng đúng vào bài tập mẫu. Khi gặp bài biến thể thì cần thêm thời gian suy nghĩ.",
        "Giải tốt các bài tập về số học, phân số, phương trình bậc nhất. Biết công thức tính diện tích, chu vi hình cơ bản nhưng đôi khi áp dụng nhầm.",
        "Nắm kiến thức ở mức thông hiểu: hiểu bài giảng và làm bài tập tương tự, nhưng gặp khó khi đề thay đổi cách diễn đạt.",
      ],
      'logic': [
        "Trình bày lời giải có cấu trúc nhưng đôi khi nhảy bước, bỏ qua giải thích trung gian. Chưa có thói quen kiểm tra lại kết quả.",
        "Biết chia bài toán thành bước nhưng khi gặp bài 3-4 bước thì mất phương hướng. Cần rèn thêm kỹ năng suy luận đa bước.",
        "Tư duy logic khá — lập luận đúng hướng nhưng chưa chặt chẽ ở bước kết luận. Cần luyện thêm cách trình bày lời giải hoàn chỉnh.",
      ],
      'songngu': [
        "Nhận diện thuật ngữ toán tiếng Anh cơ bản (addition, multiplication, fraction) nhưng chưa tự tin viết lời giải bằng tiếng Anh.",
        "Đọc được đề tiếng Anh đơn giản nhưng cần thời gian dịch. Biết vài thuật ngữ như triangle, circle, area.",
        "Năng lực song ngữ khá — nhận diện từ khóa tiếng Anh trong đề bài, nhưng chưa tự diễn đạt ý tưởng bằng tiếng Anh.",
      ],
      'tuhoc': [
        "Có chủ động hỏi thêm nhưng chủ yếu theo hướng dẫn của giáo viên, chưa tự đặt vấn đề mới.",
        "Chăm chỉ làm bài tập về nhà, có hỏi câu hỏi mở rộng khi được khuyến khích.",
        "Tự học ở mức khá — làm thêm bài tập nhưng chủ yếu giống dạng đã học, chưa thử thách bản thân.",
      ],
      'dexuat': [
        "Đề xuất: Tăng bài tập vận dụng đa dạng, rèn kỹ năng kiểm tra ngược và trình bày chi tiết.",
        "Đề xuất: Cho bài tập từ cơ bản lên nâng cao dần, luyện giải bài có nhiều bước.",
        "Đề xuất: Khuyến khích tự đặt câu hỏi 'Tại sao?', cho thêm bài liên hệ thực tế.",
      ],
    },
    'TB': {
      'kienthuc': [
        "Nhận biết — biết công thức nhưng chỉ áp dụng được khi bài giống mẫu. Gặp khó khi đề thay đổi cách diễn đạt.",
        "Nắm kiến thức cơ bản nhưng chưa liên kết giữa các chủ đề: biết công thức nhưng không hiểu khi nào dùng.",
        "Mức nhận biết: thuộc bài nhưng chưa hiểu bản chất. Ví dụ: biết a² + b² = c² nhưng không nhận ra bài nào cần dùng.",
      ],
      'logic': [
        "Cần hướng dẫn từng bước, chưa tự chia nhỏ bài toán. Hay bỏ sót bước trung gian.",
        "Trình bày lời giải rời rạc, cần giáo viên nhắc nhở từng bước. Chưa biết cách kiểm tra kết quả.",
        "Tư duy theo khuôn mẫu — chỉ giải được bài giống mẫu, không biến đổi khi đề thay đổi.",
      ],
      'songngu': [
        "Hạn chế — chỉ biết vài thuật ngữ cơ bản (number, plus, minus), khó đọc hiểu đề tiếng Anh.",
        "Chỉ nhận diện số và phép tính bằng tiếng Anh. Chưa biết thuật ngữ hình học tiếng Anh.",
        "Năng lực song ngữ cơ bản — cần hỗ trợ dịch khi gặp thuật ngữ toán tiếng Anh.",
      ],
      'tuhoc': [
        "Thường xin đáp án trước rồi mới hiểu ngược lại, ít chủ động đặt câu hỏi.",
        "Cần hướng dẫn rõ ràng, ít tự tìm hiểu thêm ngoài bài tập được giao.",
        "Tự học ở mức thấp — chờ thầy cô giải thích, không tự tìm cách giải.",
      ],
      'dexuat': [
        "Đề xuất: Ôn lại kiến thức nền tảng, làm bài tập mẫu kèm hướng dẫn chi tiết từng bước.",
        "Đề xuất: Cho bài tập dạng 'Bước 1... Bước 2...' tăng dần độ khó. Dùng ví dụ thực tế.",
        "Đề xuất: Kiểm tra lại kiến thức lớp dưới, chú trọng rèn quy tắc cơ bản trước khi nâng cao.",
      ],
    },
    'Yeu': {
      'kienthuc': [
        "Chưa nắm vững kiến thức nền tảng — nhầm diện tích và chu vi, chưa thành thạo bốn phép tính với số âm.",
        "Lỗ hổng kiến thức nghiêm trọng từ lớp dưới: chưa thuộc bảng cửu chương, nhầm lẫn quy tắc dấu.",
        "Kiến thức rất hạn chế — không phân biệt được biểu thức và phương trình, chưa biết khái niệm ẩn số.",
      ],
      'logic': [
        "Khó theo dõi bài giải nhiều bước, thường bỏ cuộc giữa chừng khi gặp bài khó.",
        "Chưa hình thành tư duy giải toán — không biết bắt đầu từ đâu khi nhìn đề bài.",
        "Tư duy logic rất yếu — không phân biệt được cho/tìm trong bài toán, cần cầm tay chỉ việc.",
      ],
      'songngu': [
        "Rất hạn chế — chưa nhận diện thuật ngữ toán tiếng Anh cơ bản.",
        "Chưa có nền tảng tiếng Anh để học thuật ngữ toán. Cần bắt đầu từ con số.",
      ],
      'tuhoc': [
        "Phụ thuộc hoàn toàn vào hướng dẫn, chỉ hỏi lại đáp án, chưa cố gắng tự giải.",
        "Không có thói quen tự học, cần động viên khích lệ liên tục để duy trì hứng thú.",
      ],
      'dexuat': [
        "Đề xuất: Ôn lại kiến thức nền tảng lớp 5-6, dùng bài tập trắc nghiệm đơn giản, xây lại tự tin.",
        "Đề xuất: Học kèm 1:1, dùng trò chơi toán học để tăng hứng thú. Không giao bài quá khó.",
        "Đề xuất: Bắt đầu từ bài cực kỳ đơn giản, khen ngợi mọi tiến bộ nhỏ. Gia đình cần hỗ trợ thêm.",
      ],
    },
  },
}

# Tạo bank cho Lý, Hóa, Sinh tương tự
bank['Lý'] = {
  'Gioi': {
    'kienthuc': [
      "Vận dụng cao — hiểu sâu bản chất định luật Newton, giải thích được tại sao vật rơi tự do có gia tốc không đổi. Liên hệ xuất sắc giữa lý thuyết và thực nghiệm.",
      "Nắm vững kiến thức từ cơ học đến điện học, giải bài tập phức tạp nhiều bước. Hiểu ý nghĩa vật lý của mỗi đại lượng.",
      "Kiến thức rộng và sâu — tự tìm hiểu thêm về vật lý hiện đại, hiểu nguyên lý bảo toàn năng lượng ở mức nâng cao.",
    ],
    'logic': [
      "Phân tích bài toán lực phức tạp, vẽ giản đồ lực chính xác, suy luận từ giả thiết đến kết luận chặt chẽ.",
      "Tư duy logic xuất sắc — biết đặt giả thuyết, kiểm chứng bằng tính toán và liên hệ thực tế.",
      "Biết phân tích định tính trước khi tính toán: dự đoán kết quả rồi kiểm tra, phát hiện lỗi sai nhanh.",
    ],
    'songngu': [
      "Sử dụng đúng thuật ngữ: force, acceleration, velocity, momentum. Đọc hiểu tài liệu vật lý tiếng Anh.",
      "Năng lực song ngữ tốt — viết được mô tả thí nghiệm bằng tiếng Anh, dùng thuật ngữ chính xác.",
    ],
    'tuhoc': [
      "Rất chủ động — liên tục hỏi 'Tại sao lại như vậy?', tự đọc thêm về vật lý vũ trụ.",
      "Ham tìm hiểu — tự làm thí nghiệm đơn giản ở nhà, ghi chép quan sát.",
    ],
    'dexuat': [
      "Đề xuất: Cho tham gia CLB Vật lý, làm thí nghiệm nâng cao, giới thiệu tài liệu tiếng Anh.",
      "Đề xuất: Hướng dẫn viết báo cáo khoa học, cho tiếp cận đề thi HSG Lý.",
    ],
  },
  'Kha': {
    'kienthuc': [
      "Thông hiểu — nắm được công thức vận tốc, gia tốc, lực. Biết áp dụng nhưng đôi khi quên đổi đơn vị trước khi tính.",
      "Hiểu bản chất của các định luật cơ bản nhưng khi gặp bài tổng hợp nhiều kiến thức thì lúng túng.",
    ],
    'logic': [
      "Biết vẽ sơ đồ phân tích lực nhưng chưa kiểm tra tính hợp lý của kết quả sau khi tính.",
      "Tư duy logic khá — phân tích đúng hướng nhưng đôi khi bỏ sót một lực tác dụng.",
    ],
    'songngu': [
      "Nhận diện thuật ngữ cơ bản (speed, energy, heat) nhưng chưa tự tin giải thích bằng tiếng Anh.",
      "Đọc được đề tiếng Anh đơn giản nhưng cần thời gian dịch thuật ngữ chuyên ngành.",
    ],
    'tuhoc': [
      "Có đặt câu hỏi liên hệ thực tế ('Tại sao máy bay bay được?') nhưng chưa tự tìm câu trả lời.",
      "Chăm chỉ nhưng chủ yếu theo giáo trình, chưa tự mở rộng tìm hiểu thêm.",
    ],
    'dexuat': [
      "Đề xuất: Nhấn mạnh bước đổi đơn vị trước khi tính, cho thêm bài tập liên hệ thực tế.",
      "Đề xuất: Rèn phân tích đề bài kỹ hơn, cho xem video thí nghiệm trước mỗi chủ đề mới.",
    ],
  },
  'TB': {
    'kienthuc': [
      "Thuộc công thức nhưng chưa hiểu ý nghĩa vật lý. Ví dụ: biết v = s/t nhưng không giải thích được chuyển động đều.",
      "Nắm kiến thức ở mức nhận biết — ghi nhớ được công thức nhưng thay số máy móc, không hiểu bản chất.",
    ],
    'logic': ["Thay số vào công thức được nhưng không biết phân tích bài toán trước khi giải.", "Tư duy theo khuôn mẫu — chỉ làm được bài giống mẫu."],
    'songngu': ["Hạn chế — chỉ biết vài từ cơ bản: light, water, hot, cold.", "Chưa nhận diện thuật ngữ vật lý tiếng Anh."],
    'tuhoc': ["Ít chủ động, thường chờ giáo viên hướng dẫn rồi mới làm.", "Cần được giao bài cụ thể, không tự tìm bài tập thêm."],
    'dexuat': [
      "Đề xuất: Sử dụng thí nghiệm trực quan, video minh họa, liên hệ hiện tượng đời sống.",
      "Đề xuất: Giảm lượng công thức, tập trung hiểu bản chất trước, sau đó mới luyện tính toán.",
    ],
  },
  'Yeu': {
    'kienthuc': ["Nhầm lẫn khái niệm khối lượng và trọng lượng, chưa phân biệt được lực và năng lượng.", "Kiến thức rất hạn chế — không nhớ đơn vị đo lường cơ bản (m, kg, s, N)."],
    'logic': ["Không biết sắp xếp các bước giải, thường chỉ chép đáp án mà không hiểu.", "Tư duy rất yếu — không biết đọc đề, xác định cho/tìm."],
    'songngu': ["Rất hạn chế — chưa nhận biết thuật ngữ tiếng Anh cơ bản."],
    'tuhoc': ["Phụ thuộc hoàn toàn, không đặt câu hỏi. Cần động viên rất nhiều.", "Mất hứng thú học, cần phương pháp tiếp cận hoàn toàn mới."],
    'dexuat': [
      "Đề xuất: Dùng video thí nghiệm, hình ảnh sinh động. Bài tập cực đơn giản kèm hình minh họa.",
      "Đề xuất: Học kèm 1:1, bắt đầu từ hiện tượng thực tế quen thuộc (ném bóng, nấu nước sôi).",
    ],
  },
}

bank['Hóa'] = {
  'Gioi': {
    'kienthuc': ["Vận dụng cao — hiểu sâu cấu tạo nguyên tử, liên kết hóa học, phản ứng oxi hóa khử. Viết và cân bằng phương trình phức tạp thành thạo.", "Kiến thức rộng — nắm vững hóa vô cơ lẫn hữu cơ, tự dự đoán sản phẩm phản ứng chưa học."],
    'logic': ["Giải thích cơ chế phản ứng ở cấp độ phân tử, dự đoán sản phẩm dựa trên quy luật.", "Tư duy hệ thống — liên kết kiến thức hóa học với thực tế một cách logic."],
    'songngu': ["Sử dụng đúng danh pháp IUPAC tiếng Anh (sodium chloride, sulfuric acid, ethanol).", "Đọc hiểu tài liệu hóa tiếng Anh tốt, viết được công thức và tên gọi song ngữ."],
    'tuhoc': ["Rất chủ động — hỏi về ứng dụng hóa học trong đời sống, tự tìm hiểu hóa hữu cơ.", "Ham tìm hiểu — tự nghiên cứu phản ứng mới, thích làm thí nghiệm."],
    'dexuat': ["Đề xuất: Cho làm thí nghiệm nâng cao, tiếp cận đề thi HSG Hóa.", "Đề xuất: Hướng dẫn viết phương trình phức tạp, giới thiệu hóa hữu cơ nâng cao."],
  },
  'Kha': {
    'kienthuc': ["Viết đúng phương trình hóa học cơ bản, biết cân bằng. Phân biệt được axit, bazơ, muối.", "Nắm kiến thức thông hiểu — hiểu quy luật sắp xếp trong bảng tuần hoàn cơ bản."],
    'logic': ["Trình bày bước giải rõ ràng nhưng khi gặp phản ứng phức tạp cần gợi ý.", "Tư duy khá — biết cân bằng phương trình đơn giản nhưng lúng túng với phản ứng oxi hóa khử."],
    'songngu': ["Đọc tên nguyên tố tiếng Anh đúng nhưng chưa thuộc hết danh pháp IUPAC.", "Nhận diện thuật ngữ cơ bản: atom, molecule, reaction, acid, base."],
    'tuhoc': ["Có hỏi thêm về hiện tượng hóa học trong đời sống, biểu hiện quan tâm.", "Chăm chỉ học bài nhưng chủ yếu theo sách giáo khoa."],
    'dexuat': ["Đề xuất: Tăng bài tập viết phương trình, mô tả hiện tượng kèm giải thích.", "Đề xuất: Cho xem video thí nghiệm trước mỗi bài, rèn cân bằng phương trình."],
  },
  'TB': {
    'kienthuc': ["Đọc tên nguyên tố cơ bản nhưng lúng túng khi viết công thức hóa học phức tạp. Chưa phân biệt rõ hiện tượng vật lý và hóa học.", "Nhận biết — thuộc ký hiệu nguyên tố nhưng chưa biết viết công thức hợp chất. Nhầm lẫn hóa trị."],
    'logic': ["Cần hướng dẫn cách đọc và viết phương trình từng bước.", "Tư duy trung bình — viết được phương trình đơn giản nếu có mẫu, nhưng không tự lập."],
    'songngu': ["Chỉ biết tên tiếng Anh của vài nguyên tố phổ biến (oxygen, hydrogen, carbon).", "Năng lực song ngữ hạn chế — cần hỗ trợ dịch khi gặp thuật ngữ."],
    'tuhoc': ["Ít chủ động, thường chỉ hỏi đáp án mà không cố hiểu.", "Cần giáo viên giải thích nhiều lần, chưa có thói quen ôn bài."],
    'dexuat': ["Đề xuất: Dùng bảng tuần hoàn có màu sắc, thí nghiệm trực quan tăng hứng thú.", "Đề xuất: Cho học thuộc 20 nguyên tố đầu, rèn viết công thức hóa học từ đơn giản."],
  },
  'Yeu': {
    'kienthuc': ["Không phân biệt được nguyên tử, phân tử, ion. Chưa biết cách viết ký hiệu hóa học.", "Kiến thức rất yếu — không nhớ ký hiệu nguyên tố cơ bản, nhầm lẫn chất và hỗn hợp."],
    'logic': ["Không thể tự cân bằng phương trình đơn giản nhất.", "Tư duy rất yếu — không hiểu khái niệm 'phản ứng hóa học' là gì."],
    'songngu': ["Rất hạn chế — chưa nhận diện thuật ngữ tiếng Anh."],
    'tuhoc': ["Phụ thuộc hoàn toàn vào hướng dẫn, cần động viên liên tục.", "Mất hứng thú với môn Hóa, cần phương pháp tiếp cận mới."],
    'dexuat': ["Đề xuất: Bắt đầu lại từ khái niệm nguyên tử, dùng mô hình 3D và video trực quan.", "Đề xuất: Cho xem thí nghiệm thực tế (pha màu, tạo bong bóng) để kích thích tò mò."],
  },
}

bank['Sinh'] = {
  'Gioi': {
    'kienthuc': ["Vận dụng cao — hiểu sâu cơ chế di truyền, quá trình phân bào, vai trò ADN/ARN. Hỏi về đột biến gen và tiến hóa.", "Kiến thức rộng — nắm vững từ tế bào đến hệ sinh thái, hiểu mối quan hệ giữa các bậc phân loại."],
    'logic': ["Phân tích mối quan hệ nhân quả trong hệ sinh thái xuất sắc, lập sơ đồ tư duy rõ ràng.", "Tư duy hệ thống — liên kết kiến thức từ tế bào đến cơ thể đến quần thể một cách logic."],
    'songngu': ["Sử dụng chính xác thuật ngữ: DNA, mitosis, ecosystem, photosynthesis, chromosome.", "Đọc hiểu tài liệu sinh học tiếng Anh, dùng thuật ngữ tự tin."],
    'tuhoc': ["Rất chủ động — tự tìm hiểu công nghệ sinh học, đặt câu hỏi vượt chương trình.", "Ham khám phá — tự quan sát thiên nhiên, ghi chép và đặt giả thuyết."],
    'dexuat': ["Đề xuất: Cho nghiên cứu mini project về di truyền, tiếp cận tài liệu tiếng Anh.", "Đề xuất: Khuyến khích tham gia CLB Sinh học, hướng dẫn làm tiêu bản."],
  },
  'Kha': {
    'kienthuc': ["Nhận diện đúng cấu tạo tế bào động vật và thực vật, phân biệt quang hợp và hô hấp.", "Nắm kiến thức thông hiểu — hiểu chu trình sống của thực vật, phân loại động vật cơ bản."],
    'logic': ["Trình bày quá trình sinh học theo trình tự nhưng đôi khi nhầm lẫn thứ tự các giai đoạn.", "Tư duy khá — vẽ được sơ đồ tế bào cơ bản nhưng chưa giải thích chức năng chi tiết."],
    'songngu': ["Nhận diện thuật ngữ cơ bản (cell, nucleus, membrane, photosynthesis).", "Đọc được tên khoa học của sinh vật nhưng chưa tự tin giải thích bằng tiếng Anh."],
    'tuhoc': ["Có hỏi câu hỏi mở rộng về hệ sinh thái, quan tâm bảo vệ môi trường.", "Chăm chỉ nhưng chủ yếu học theo sách, chưa tự tìm thêm tài liệu."],
    'dexuat': ["Đề xuất: Tăng bài tập sơ đồ tư duy, so sánh các quá trình sinh học.", "Đề xuất: Cho xem phim tài liệu, tổ chức quan sát thực địa."],
  },
  'TB': {
    'kienthuc': ["Hiểu nguyên lý tuần hoàn máu nhưng chưa rõ chức năng từng thành phần. Biết cấu trúc tế bào nhưng chưa phân biệt bào quan.", "Nắm kiến thức ở mức nhận biết — biết tên các cơ quan nhưng chưa hiểu chức năng chi tiết."],
    'logic': ["Cần hướng dẫn từng bước khi mô tả quá trình sinh học.", "Tư duy trung bình — mô tả hiện tượng được nhưng chưa giải thích nguyên nhân."],
    'songngu': ["Chỉ biết vài thuật ngữ cơ bản: heart, blood, plant, animal.", "Năng lực song ngữ hạn chế — cần giáo viên hỗ trợ dịch thuật ngữ."],
    'tuhoc': ["Ít chủ động, thường chờ giáo viên giải thích.", "Cần được nhắc nhở ôn bài, chưa có phương pháp tự học hiệu quả."],
    'dexuat': ["Đề xuất: Sử dụng hình ảnh, video minh họa. Dùng so sánh đời thường (ti thể = nhà máy điện).", "Đề xuất: Cho quan sát mẫu vật thật, vẽ sơ đồ đơn giản để ghi nhớ."],
  },
  'Yeu': {
    'kienthuc': ["Kiến thức hệ sinh thái, chuỗi thức ăn hổng. Không phân biệt tế bào nhân sơ và nhân thực.", "Rất yếu — không nhớ chức năng các cơ quan cơ bản trong cơ thể."],
    'logic': ["Mô tả rời rạc, thiếu logic nhân quả.", "Không biết sắp xếp thông tin theo trình tự."],
    'songngu': ["Rất hạn chế — chưa nhận biết thuật ngữ tiếng Anh."],
    'tuhoc': ["Phụ thuộc hoàn toàn, cần động viên liên tục.", "Mất hứng thú học, cần tiếp cận bằng trò chơi hoặc phim ảnh."],
    'dexuat': ["Đề xuất: Dùng phim tài liệu, hình ảnh trực quan. Bắt đầu từ khái niệm đơn giản nhất.", "Đề xuất: Cho chơi game sinh học, sử dụng flashcard có hình ảnh. Không ép học thuộc."],
  },
}

def build_evaluation(mon, level):
    """Ghép ngẫu nhiên 5 tiêu chí → đánh giá duy nhất cho mỗi HS"""
    b = bank[mon][level]
    parts = [
        f"1. Độ sâu kiến thức: {random.choice(b['kienthuc'])}",
        f"2. Tư duy logic: {random.choice(b['logic'])}",
        f"3. Năng lực song ngữ: {random.choice(b['songngu'])}",
        f"4. Tự học và tư duy phản biện: {random.choice(b['tuhoc'])}",
        f"5. {random.choice(b['dexuat'])}",
    ]
    return "\n".join(parts)

# ========== CHẠY SEED ==========
try:
    admin_users = ['lequangphuc', 'phungvanhanh', 'hoangthinha', 'nguyenthithuong']
    users = json_db.load_users()
    users = [u for u in users if u['tendangnhap'] in admin_users]
    json_db.save_users(users)

    for i in range(1, 41):
        name = gen_name()
        uname = f"hs{i:03d}"
        pw = generate_password_hash("123456")
        lop = random.choice(lop_list)
        user = json_db.create_user(uname, pw, f"{name} ({lop})")

        updates = {}
        for mon, k_nl, k_ld, k_sc in [
            ('Toán', 'nangluctoan', 'lydotoan', 'socautoan'),
            ('Lý', 'nanglucly', 'lydoly', 'socauly'),
            ('Hóa', 'nangluchoa', 'lydohoa', 'socauhoa'),
            ('Sinh', 'nanglucsinh', 'lydosinh', 'socausinh'),
        ]:
            if random.random() < 0.85:
                nl = random.choices(levels, weights)[0]
                updates[k_nl] = nl
                updates[k_ld] = build_evaluation(mon, nl)
                updates[k_sc] = random.randint(5, 95)

        if updates:
            json_db.update_user(user['id'], updates)

    for i in range(41, 51):
        name = gen_name()
        uname = f"hs{i:03d}"
        pw = generate_password_hash("123456")
        lop = random.choice(lop_list)
        json_db.create_user(uname, pw, f"{name} ({lop})")

    total = len(json_db.get_all_users())
    print(f"[OK] Tao 50 hoc sinh thanh cong (tong {total} users)")
    print("Mo ta: moi danh gia co 5 tieu chi, ghep ngau nhien tu ngan hang cau")
    print("Mat khau mac dinh: 123456")

except Exception as e:
    print(f"Loi: {e}")
    import traceback
    traceback.print_exc()
