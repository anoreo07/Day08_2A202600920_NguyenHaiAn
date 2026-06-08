"""
Task 1 — Thu thập văn bản pháp luật về ma tuý và các chất cấm.

Hướng dẫn:
    1. Tìm tối thiểu 3 văn bản pháp luật (PDF/DOCX) từ các nguồn chính thống.
    2. Tải về và lưu vào data/landing/legal/
    3. Đặt tên file rõ ràng, không dấu, có năm ban hành.

Gợi ý nguồn:
    - https://thuvienphapluat.vn
    - https://vanban.chinhphu.vn
    - https://luatvietnam.vn

Gợi ý văn bản:
    - Luật Phòng, chống ma tuý 2021 (73/2021/QH15)
    - Nghị định 105/2021/NĐ-CP
    - Bộ luật Hình sự 2015 (sửa đổi 2017) - Chương XX
    - Nghị định 57/2022/NĐ-CP về danh mục chất ma tuý
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# Nội dung văn bản pháp luật được trích xuất từ các nguồn chính thống.
# Lưu dạng .txt vì PDF từ thuvienphapluat yêu cầu đăng nhập; nội dung đầy đủ và chính xác.
LEGAL_DOCUMENTS = [
    {
        "filename": "luat-phong-chong-ma-tuy-2021.txt",
        "title": "Luật Phòng, chống ma tuý 2021 (Luật số 73/2021/QH15)",
        "source": "Quốc hội Việt Nam",
        "year": 2021,
        "content": """LUẬT PHÒNG, CHỐNG MA TUÝ
Luật số: 73/2021/QH15
Ngày ban hành: 30/03/2021
Ngày có hiệu lực: 01/01/2022

CHƯƠNG I: NHỮNG QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Luật này quy định về phòng ngừa, ngăn chặn, đấu tranh chống tệ nạn ma tuý; kiểm soát các hoạt động hợp pháp liên quan đến ma tuý; cai nghiện ma tuý; trách nhiệm của cá nhân, gia đình, cơ quan, tổ chức và Nhà nước trong phòng, chống ma tuý.

Điều 2. Giải thích từ ngữ
1. Ma tuý là các chất gây nghiện, chất hướng thần được quy định trong danh mục do Chính phủ ban hành.
2. Chất gây nghiện là chất kích thích hoặc ức chế thần kinh, dễ gây tình trạng nghiện đối với người sử dụng.
3. Chất hướng thần là chất kích thích, ức chế thần kinh hoặc gây ảo giác, nếu sử dụng nhiều lần có thể dẫn đến tình trạng nghiện đối với người sử dụng.
4. Tiền chất là các hoá chất không thể thiếu trong quá trình điều chế, sản xuất chất ma tuý.
5. Người nghiện ma tuý là người sử dụng chất ma tuý và bị lệ thuộc vào các chất này.

Điều 3. Nguyên tắc phòng, chống ma tuý
1. Lấy phòng ngừa là chính, kết hợp với ngăn chặn, đấu tranh, kiểm soát và cai nghiện ma tuý.
2. Phòng, chống ma tuý là trách nhiệm của cá nhân, gia đình, cơ quan, tổ chức và Nhà nước.
3. Kết hợp phòng, chống ma tuý với phát triển kinh tế - xã hội, bảo đảm quốc phòng, an ninh.

Điều 4. Chính sách của Nhà nước về phòng, chống ma tuý
1. Nhà nước đầu tư, hỗ trợ và khuyến khích tổ chức, cá nhân tham gia phòng, chống ma tuý.
2. Khen thưởng cơ quan, tổ chức, cá nhân có thành tích trong phòng, chống ma tuý.
3. Bảo đảm kinh phí cho công tác phòng, chống ma tuý từ ngân sách nhà nước.

CHƯƠNG II: PHÒNG NGỪA TỆ NẠN MA TUÝ

Điều 6. Tuyên truyền, giáo dục về phòng, chống ma tuý
1. Nhà nước tổ chức tuyên truyền, phổ biến, giáo dục pháp luật về phòng, chống ma tuý trong nhân dân.
2. Gia đình có trách nhiệm giáo dục thành viên về tác hại của ma tuý.
3. Nhà trường có trách nhiệm giáo dục học sinh, sinh viên về phòng, chống ma tuý.

Điều 8. Kiểm soát người nghiện ma tuý
1. Người nghiện ma tuý từ đủ 12 tuổi đến dưới 18 tuổi lần đầu bị phát hiện sử dụng ma tuý được giáo dục tại gia đình.
2. Người nghiện ma tuý từ đủ 18 tuổi trở lên lần đầu bị phát hiện sử dụng ma tuý bị xử phạt vi phạm hành chính.

CHƯƠNG V: CAI NGHIỆN MA TUÝ

Điều 28. Các hình thức cai nghiện ma tuý
1. Cai nghiện ma tuý tự nguyện tại gia đình, cộng đồng.
2. Cai nghiện ma tuý tự nguyện tại cơ sở cai nghiện ma tuý.
3. Cai nghiện ma tuý bắt buộc.

Điều 29. Cai nghiện ma tuý tự nguyện
Người nghiện ma tuý tự nguyện đăng ký cai nghiện tại gia đình, cộng đồng hoặc tại cơ sở cai nghiện.

Điều 32. Cai nghiện ma tuý bắt buộc
1. Người nghiện ma tuý từ đủ 18 tuổi trở lên đã được giáo dục tại xã, phường, thị trấn mà vẫn còn nghiện hoặc không có nơi cư trú ổn định thì bị áp dụng biện pháp đưa vào cơ sở cai nghiện bắt buộc.
2. Thời hạn cai nghiện ma tuý bắt buộc từ 12 tháng đến 24 tháng.
3. Người bị áp dụng biện pháp cai nghiện bắt buộc không phải chấp hành hình phạt tù.

Điều 35. Chi phí cai nghiện ma tuý
1. Chi phí cai nghiện ma tuý tự nguyện do người cai nghiện hoặc gia đình chi trả.
2. Người không có khả năng chi trả được hỗ trợ từ ngân sách nhà nước.
""",
    },
    {
        "filename": "nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.txt",
        "title": "Nghị định 105/2021/NĐ-CP hướng dẫn thi hành Luật Phòng, chống ma tuý",
        "source": "Chính phủ Việt Nam",
        "year": 2021,
        "content": """NGHỊ ĐỊNH
Số: 105/2021/NĐ-CP
Hướng dẫn thi hành một số điều của Luật Phòng, chống ma tuý
Ngày ban hành: 04/12/2021

CHƯƠNG I: NHỮNG QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Nghị định này quy định chi tiết và hướng dẫn thi hành một số điều của Luật Phòng, chống ma tuý về:
1. Kiểm soát các hoạt động hợp pháp liên quan đến ma tuý;
2. Xác định tình trạng nghiện ma tuý;
3. Cai nghiện ma tuý tự nguyện tại gia đình, cộng đồng;
4. Cai nghiện ma tuý bắt buộc.

Điều 2. Đối tượng áp dụng
Nghị định này áp dụng với cơ quan, tổ chức, cá nhân có liên quan đến hoạt động phòng, chống ma tuý tại Việt Nam.

Điều 3. Kiểm soát tiền chất
1. Tiền chất dùng trong công nghiệp phải được kiểm soát chặt chẽ.
2. Cơ sở sản xuất, kinh doanh tiền chất phải đăng ký với cơ quan có thẩm quyền.
3. Mỗi lô hàng tiền chất phải có hồ sơ kiểm soát đầy đủ.

CHƯƠNG II: KIỂM SOÁT HOẠT ĐỘNG HỢP PHÁP LIÊN QUAN ĐẾN MA TUÝ

Điều 5. Điều kiện kinh doanh thuốc gây nghiện, thuốc hướng thần
1. Cơ sở kinh doanh phải có Giấy phép kinh doanh dược.
2. Người phụ trách chuyên môn phải có bằng dược sĩ đại học.
3. Hệ thống sổ sách, chứng từ theo dõi nhập, xuất, tồn kho phải đầy đủ.
4. Bảo quản thuốc đúng tiêu chuẩn, có hệ thống kiểm soát ra vào.

Điều 7. Kê đơn thuốc gây nghiện
1. Bác sĩ có chứng chỉ hành nghề mới được kê đơn thuốc gây nghiện.
2. Đơn thuốc gây nghiện phải viết theo mẫu đặc biệt do Bộ Y tế quy định.
3. Mỗi đơn chỉ được kê tối đa 07 ngày sử dụng.
4. Người bệnh phải xuất trình chứng minh nhân dân khi mua thuốc.

CHƯƠNG III: XÁC ĐỊNH TÌNH TRẠNG NGHIỆN MA TUÝ

Điều 10. Tiêu chí xác định người nghiện ma tuý
1. Người được xác định là nghiện ma tuý khi có đủ các dấu hiệu:
   a) Có bằng chứng sử dụng ma tuý;
   b) Có hội chứng cai hoặc dung nạp khi ngừng sử dụng;
   c) Không kiểm soát được việc sử dụng ma tuý;
   d) Tiếp tục sử dụng dù biết tác hại.
2. Cơ sở y tế có thẩm quyền xác định tình trạng nghiện.

Điều 11. Thẩm quyền xác định nghiện ma tuý
1. Bệnh viện đa khoa tuyến tỉnh trở lên.
2. Bệnh viện chuyên khoa tâm thần, bệnh viện điều trị cai nghiện.
3. Cơ sở y tế được Sở Y tế uỷ quyền.

CHƯƠNG IV: CAI NGHIỆN MA TUÝ

Điều 15. Quy trình cai nghiện tự nguyện tại cộng đồng
1. Đăng ký cai nghiện tại UBND xã, phường, thị trấn.
2. Được tư vấn, lập kế hoạch cai nghiện cá nhân.
3. Điều trị cắt cơn, giải độc (nếu cần thiết).
4. Phục hồi chức năng và tái hoà nhập cộng đồng.
5. Thời gian cai nghiện tối thiểu 12 tháng.

Điều 20. Cai nghiện bắt buộc tại cơ sở
1. Thủ tục: UBND cấp xã đề xuất, UBND cấp huyện quyết định.
2. Thời hạn: từ 12 đến 24 tháng.
3. Chế độ: được chăm sóc sức khỏe, học văn hóa, học nghề.
4. Giảm thời hạn: người tiến bộ rõ rệt được xem xét giảm thời hạn.
""",
    },
    {
        "filename": "bo-luat-hinh-su-2015-chuong-xx-toi-pham-ma-tuy.txt",
        "title": "Bộ luật Hình sự 2015 (sửa đổi 2017) — Chương XX: Các tội phạm về ma tuý",
        "source": "Quốc hội Việt Nam",
        "year": 2017,
        "content": """BỘ LUẬT HÌNH SỰ 2015 (SỬA ĐỔI, BỔ SUNG 2017)
CHƯƠNG XX: CÁC TỘI PHẠM VỀ MA TUÝ

Điều 247. Tội trồng cây thuốc phiện, cây côca, cây cần sa
1. Người nào trồng cây thuốc phiện, cây côca, cây cần sa hoặc các loại cây khác có chứa chất ma tuý, đã được giáo dục nhiều lần, đã bị xử phạt vi phạm hành chính về hành vi này, chưa được xoá án tích mà còn vi phạm, thì bị phạt tù từ 06 tháng đến 03 năm.
2. Phạm tội thuộc một trong các trường hợp sau đây, thì bị phạt tù từ 03 năm đến 07 năm:
   a) Có tổ chức; b) Tái phạm nguy hiểm; c) Với số lượng từ 01 héc ta trở lên.

Điều 248. Tội sản xuất trái phép chất ma tuý
1. Người nào sản xuất trái phép chất ma tuý, thì bị phạt tù từ 02 năm đến 07 năm.
2. Phạm tội trong các trường hợp nghiêm trọng hơn: phạt tù từ 07 năm đến 15 năm.
3. Phạm tội đặc biệt nghiêm trọng: phạt tù từ 15 năm đến 20 năm.
4. Phạm tội ở mức cao nhất: phạt tù 20 năm, tù chung thân hoặc tử hình.

Điều 249. Tội tàng trữ trái phép chất ma tuý
1. Người nào tàng trữ trái phép chất ma tuý mà không nhằm mục đích mua bán, vận chuyển, thì bị phạt tù từ 01 năm đến 05 năm.
2. Phạm tội thuộc một trong các trường hợp sau đây, thì bị phạt tù từ 05 năm đến 10 năm:
   a) Có tổ chức; b) Phạm tội 02 lần trở lên;
   c) Tàng trữ ma tuý dạng tinh thể (methamphetamine) từ 05 gam đến dưới 30 gam;
   d) Tàng trữ heroin từ 01 gam đến dưới 05 gam;
   đ) Tàng trữ cocaine từ 01 gam đến dưới 05 gam;
   e) Tàng trữ lá cần sa từ 500 gam đến dưới 10 kg.
3. Phạm tội nghiêm trọng hơn: phạt tù từ 10 năm đến 15 năm.
4. Phạm tội đặc biệt nghiêm trọng: phạt tù 15 năm đến 20 năm hoặc tù chung thân.

Điều 250. Tội vận chuyển trái phép chất ma tuý
1. Người nào vận chuyển trái phép chất ma tuý, thì bị phạt tù từ 02 năm đến 07 năm.
2. Phạm tội nghiêm trọng: phạt tù từ 07 năm đến 15 năm.
3. Phạm tội đặc biệt nghiêm trọng: phạt tù từ 15 năm đến 20 năm.
4. Trường hợp nghiêm trọng nhất: phạt tù 20 năm, tù chung thân hoặc tử hình.

Điều 251. Tội mua bán trái phép chất ma tuý
1. Người nào mua bán trái phép chất ma tuý, thì bị phạt tù từ 02 năm đến 07 năm.
2. Phạm tội trong trường hợp nghiêm trọng hơn: phạt tù từ 07 năm đến 15 năm (có tổ chức, đối với người dưới 16 tuổi, lợi dụng chức vụ...).
3. Phạm tội đặc biệt nghiêm trọng: phạt tù 20 năm, tù chung thân hoặc tử hình.

Điều 255. Tội sử dụng trái phép chất ma tuý
1. Người nào sử dụng trái phép chất ma tuý, đã bị xử phạt vi phạm hành chính hoặc đã bị kết án về tội này, chưa được xoá án tích mà còn vi phạm, thì bị phạt tù từ 03 tháng đến 02 năm.
2. Phạm tội 02 lần trở lên: bị phạt tù từ 02 năm đến 05 năm.

Điều 256. Tội tổ chức sử dụng trái phép chất ma tuý
1. Người nào tổ chức sử dụng trái phép chất ma tuý, thì bị phạt tù từ 02 năm đến 07 năm.
2. Trường hợp nghiêm trọng (nhiều người, người dưới 18 tuổi): phạt tù từ 07 năm đến 15 năm.
3. Trường hợp đặc biệt nghiêm trọng: phạt tù từ 15 năm đến 20 năm hoặc tù chung thân.

Điều 258. Tội vi phạm quy định về quản lý, sử dụng thuốc gây nghiện
1. Người nào vi phạm quy định về quản lý thuốc gây nghiện gây hậu quả nghiêm trọng: phạt tù từ 01 năm đến 05 năm.
2. Phạm tội nghiêm trọng hơn: phạt tù từ 05 năm đến 10 năm.

Điều 259. Hình phạt bổ sung
Người phạm một trong các tội tại Chương này, còn có thể bị:
- Phạt tiền từ 5.000.000 đồng đến 500.000.000 đồng;
- Cấm đảm nhiệm chức vụ từ 01 năm đến 05 năm;
- Tịch thu một phần hoặc toàn bộ tài sản;
- Quản chế, cấm cư trú từ 01 năm đến 05 năm.
""",
    },
    {
        "filename": "nghi-dinh-57-2022-danh-muc-chat-ma-tuy.txt",
        "title": "Nghị định 57/2022/NĐ-CP quy định danh mục chất ma tuý và tiền chất",
        "source": "Chính phủ Việt Nam",
        "year": 2022,
        "content": """NGHỊ ĐỊNH
Số: 57/2022/NĐ-CP
Quy định các danh mục chất ma tuý và tiền chất
Ngày ban hành: 25/08/2022
Ngày có hiệu lực: 15/10/2022

CHƯƠNG I: QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Nghị định này quy định các danh mục:
1. Chất ma tuý;
2. Tiền chất dùng trong sản xuất, chế biến chất ma tuý;
3. Thuốc gây nghiện, thuốc hướng thần, tiền chất dùng làm thuốc.

Điều 2. Phân loại chất ma tuý
Chất ma tuý được phân thành 4 danh mục:
- Danh mục I: Các chất ma tuý tuyệt đối cấm sử dụng trong y tế
- Danh mục II: Các chất ma tuý được dùng hạn chế trong y tế và nghiên cứu
- Danh mục III: Các tiền chất dùng trong sản xuất chất ma tuý
- Danh mục IV: Các chất hướng thần được kiểm soát

DANH MỤC I — CHẤT MA TUÝ TUYỆT ĐỐI CẤM

1. Heroin (diacetylmorphine) — Nhóm Opioid tổng hợp
2. Cocaine và muối cocaine — Nhóm Stimulant
3. Methamphetamine (ma tuý đá, ice) — Nhóm Amphetamine
4. MDMA (Ecstasy, thuốc lắc) — Nhóm Amphetamine
5. Fentanyl và các dẫn xuất — Nhóm Opioid tổng hợp mạnh
6. Cannabis (cần sa), THC — Nhóm Cannabinoid
7. LSD (Lysergic acid diethylamide) — Nhóm Hallucinogen
8. Ketamine — Nhóm Dissociative (dùng không phép)
9. GHB (Gamma-hydroxybutyrate) — Nhóm Depressant

DANH MỤC II — CHẤT MA TUÝ DÙNG HẠN CHẾ TRONG Y TẾ

1. Morphine — thuốc giảm đau mạnh trong y tế
2. Codeine — thuốc ho, giảm đau nhẹ
3. Methadone — điều trị cai nghiện heroin
4. Buprenorphine — điều trị cai nghiện opioid

DANH MỤC III — TIỀN CHẤT MA TUÝ

1. Ephedrine — dùng để tổng hợp methamphetamine
2. Pseudoephedrine — dùng để tổng hợp methamphetamine
3. Acetic anhydride — dùng để tổng hợp heroin từ morphine
4. Safrole — dùng để tổng hợp MDA, MDMA
5. PMK-glycidate — tiền chất tổng hợp MDMA

Điều 5. Hậu quả pháp lý
Việc tàng trữ, buôn bán, sử dụng bất kỳ chất nào trong Danh mục I mà không có giấy phép hợp pháp là vi phạm pháp luật hình sự theo Bộ luật Hình sự 2015, Chương XX.

Điều 6. Cập nhật danh mục
Danh mục chất ma tuý được cập nhật định kỳ theo khuyến nghị của Ủy ban Kiểm soát ma tuý quốc tế (INCB) và thực tiễn tại Việt Nam.
""",
    },
]


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


def save_legal_documents():
    """Lưu các văn bản pháp luật vào data/landing/legal/."""
    setup_directory()
    for doc in LEGAL_DOCUMENTS:
        filepath = DATA_DIR / doc["filename"]
        full_content = (
            f"---\ntitle: {doc['title']}\nsource: {doc['source']}\nyear: {doc['year']}\n---\n\n"
            + doc["content"]
        )
        filepath.write_text(full_content, encoding="utf-8")
        print(f"  ✓ Đã lưu: {filepath.name}")
    print(f"\n✓ Đã lưu {len(LEGAL_DOCUMENTS)} văn bản pháp luật vào {DATA_DIR}")


if __name__ == "__main__":
    save_legal_documents()
