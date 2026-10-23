# Phương pháp risk nhiều yếu tố — RM-01 v0.2

**Ngày:** 2026-10-10. **Trạng thái:** DRAFT_REVIEW — người dùng chọn hướng nhiều yếu tố; công thức, trọng số và ngưỡng dưới đây là đề xuất để xem xét. Chưa có đánh giá thực nghiệm. Bước 02 IN_PROGRESS.

Tài liệu liên quan: [control/evidence](../../control-evidence-v0.1.md), [ca kiểm thử control](../../control-test-cases-v0.1.md), [kế hoạch chung](../../execution-plan-v0.1.md), [fixture tính toán](risk-method-fixtures-v0.2.json). [RM-01 v0.1](../risk-v0.1/risk-method-v0.1.md) được giữ làm lịch sử, không dùng cho đánh giá mới theo đề xuất này.

## 1. Mục đích và giới hạn

Đánh giá từng scenario gắn tài sản, tiền điều kiện, sự kiện và hậu quả. Tactic/technique ATT&CK là metadata có version; không phải biến cộng điểm. Một scenario có thể gắn nhiều tactic, nhưng vẫn chỉ tính một lần cho cùng hậu quả. Không cộng các điểm scenario để suy ra tổng risk doanh nghiệp hoặc xác suất của chuỗi tấn công.

V0.2 dùng chỉ số thứ bậc có trọng số, **không phải xác suất**, phần trăm control effectiveness hay thiệt hại tiền tệ kỳ vọng. Điểm 14 không có nghĩa rủi ro gấp đôi điểm 7. Các phép toán là quy ước hỗ trợ xếp ưu tiên và truy vết lý do.

Chế độ của bản này là `CONDITIONAL`: đánh giá tại context snapshot khi các tiền điều kiện scenario đã đúng. SC-01 đã qua VPN và biết mật khẩu; SC-02 đã có phiên đọc dữ liệu. Không dùng điểm này như khả năng sự cố xảy ra trong 12 tháng. Thay đổi này sửa sự mơ hồ về chân trời 12 tháng của v0.1; đánh giá theo thời gian cần mô hình tần suất/khởi phát riêng trước khi hỗ trợ. Chỉ so sánh điểm khi cùng method/profile, loại current/inherent, cách đặt tiền điều kiện và phạm vi hậu quả tương thích; nếu khác phải trình bày điều kiện cạnh nhau.

## 2. Công thức đề xuất

Mọi yếu tố nhận số nguyên 1–5 (càng cao càng bất lợi), hoặc UNKNOWN; không có số 0 thay cho thiếu dữ liệu.

```text
P = 0.40 × E + 0.60 × F
L = 1 + (P − 1) × (G / 5)
I = max(C, T, A, B)
R = L × I
```

| Ký hiệu | Ý nghĩa | Miền |
| --- | --- | --- |
| E | Cơ hội tiếp cận/thực hiện hành vi trong tiền điều kiện đã chọn | 1–5 |
| F | Mức dễ thực hiện hành vi đối với năng lực đối thủ mô tả trong scenario, chưa tính các control đưa vào G | 1–5 |
| P | Chỉ số khả thi ban đầu; trọng số E=40%, F=60% | 1–5 |
| G | Mức yếu của các control ngăn hậu quả trong đúng scope | 1–5 |
| L | Chỉ số likelihood có điều kiện sau khi xét control | 1–5 |
| C | Hậu quả mất bí mật | 1–5 |
| T | Hậu quả mất toàn vẹn/tính đúng đắn | 1–5 |
| A | Hậu quả mất sẵn sàng/gián đoạn hoạt động | 1–5 |
| B | Gánh nặng nghiệp vụ và phục hồi | 1–5 |
| I | Hậu quả lớn nhất có căn cứ trong bốn chiều | 1–5 |
| R | Chỉ số ưu tiên risk | 1–25 |

**Lý do thiết kế:** F được đề xuất 60% vì mức dễ thực hiện sau khi tiếp cận là trọng tâm của các scenario lab có điều kiện; E vẫn đóng góp 40%. G điều chỉnh phần điểm tăng trên mức nền 1 bằng phép nhân, để control đã xác minh có thể giảm L rõ ràng ngay cả khi đường truy cập đã có. G=1 giữ mức nền dương; G=5 không được giảm P. G/5 là hệ số tính nội bộ, **không có nghĩa đã đo control giảm 80% xác suất khi G=1**. Chọn max cho impact giúp một hậu quả bí mật nghiêm trọng không bị trung bình hóa bởi tính sẵn sàng ít bị ảnh hưởng.

40/60, phép điều chỉnh G và các ngưỡng đều chưa được hiệu chuẩn với dữ liệu SME. Đây không phải công thức của IBM, ISO hoặc NIST. Có trọng số ở phần khả thi, nhưng không bắt buộc mọi phần đều phải lấy trung bình có trọng số. Thay hệ số/công thức/rubric phải tạo version mới.

## 3. Rubric likelihood và ranh giới tránh tính trùng

| Điểm | E — cơ hội tiếp cận/thực hiện | F — mức dễ thực hiện, chưa tính control trong G |
| --- | --- | --- |
| 1 | Cần nhiều cơ hội hiếm, chưa sẵn trong điều kiện đã chốt | Cần năng lực/nguồn lực chuyên biệt vượt xa đối thủ giả định |
| 2 | Chỉ có cơ hội hạn chế, cần thêm sắp xếp đáng kể | Cần kỹ năng cao và nhiều điều kiện kỹ thuật độc lập |
| 3 | Có cơ hội khả thi nhưng không liên tục, có điều kiện bổ sung rõ | Cần kỹ năng trung bình, công cụ và vài bước chuẩn bị |
| 4 | Thường xuyên có cơ hội, ít điều kiện tiếp cận bổ sung | Có phương pháp sẵn, cần tùy chỉnh nhỏ |
| 5 | Có thể bắt đầu ngay, tiền điều kiện truy cập cần thiết đã sẵn | Hành động thường lệ/ít kỹ năng, các điều kiện kỹ thuật đã sẵn |

Nguồn cho E: sơ đồ đường truy cập, quyền/phiên và điều kiện đã xác minh hoặc giả định minh họa được gắn nhãn. Nguồn cho F: mô tả hành vi, năng lực đối thủ, điều kiện kỹ thuật và phân tích có căn cứ. Không suy F từ số technique, số alert hoặc chữ “success” của công cụ.

Trong SC-01 đã qua VPN, không giảm E nhờ VPN một lần nữa. Khó khăn vượt WebAuthn được xét trong G, không cộng lại trong F. Với SC-02 có phiên đọc hợp lệ, MFA đăng nhập không được dùng để giảm G cho việc xuất dữ liệu. Một evidence có thể hỗ trợ nhiều nhận định, nhưng cùng một tác dụng bảo vệ chỉ được tính ở một nơi trong phép tổng hợp.

| G | Rubric về mức yếu control trong phạm vi sự kiện/hậu quả |
| --- | --- |
| 1 | Evidence xác minh cho thấy các đường trọng yếu trong scope có kiểm soát hữu hiệu; tiêu chí bắt buộc đạt và không có bypass đã xác minh |
| 2 | Các đường trọng yếu được kiểm soát; còn hạn chế phụ đã xác định, không tạo đường trực tiếp đạt hậu quả |
| 3 | Control có tác dụng nhưng chỉ bao phủ một phần đường/nhóm đã xác định; phần còn lại còn cản trở đáng kể được chứng minh |
| 4 | Đường liên quan được xác minh bảo vệ yếu, chỉ còn cản trở nhỏ để đạt hậu quả |
| 5 | Có đường không được bảo vệ hoặc bypass control bắt buộc đã xác minh; hoặc đánh giá inherent giả định không tính control |

G đánh giá **tác dụng tổng thể đối với scenario**, không lấy trung bình số control đạt. Phải liệt kê các đường và tiêu chí trọng yếu trước khi chấm; chọn mức cao nhất của các đường có thể dẫn tới hậu quả. Chỉ dùng điểm số khi đủ căn cứ cho toàn scope. Nếu còn đường trọng yếu chưa biết thì G=UNKNOWN; giữ riêng các vi phạm đã xác minh và CONTROL_GAP, đồng thời ghi EVIDENCE_GAP cho phần chưa rõ. SATISFIED của một control đơn lẻ không tự suy G=1 nếu scenario còn đường khác. G=1 cần evidence phạm vi rộng hơn một test âm thành công.

Control phát hiện/phản ứng chỉ được dùng để giảm G khi có evidence nó ngăn được hậu quả đang xét; alert sau khi dữ liệu đã rời hệ thống không chứng minh đã ngăn exfiltration. Nếu tác dụng chỉ giảm hậu quả, xem xét trong dimension impact thích hợp với căn cứ, không tính giảm lần nữa ở G.

## 4. Rubric impact

Owner ghi hậu quả theo bối cảnh nghiệp vụ, không tự cho I thấp vì fixture chỉ có vài khách hàng giả. Nếu mô phỏng SME, ghi giả định hậu quả; nếu đánh giá thật, cần dữ liệu/owner xác nhận. Mỗi chiều không bị ảnh hưởng nhận 1 khi có lý do; chưa rõ nhận UNKNOWN.

| Điểm | C — bí mật | T — toàn vẹn | A — sẵn sàng | B — nghiệp vụ/phục hồi |
| --- | --- | --- | --- | --- |
| 1 | Không lộ thông tin nhạy cảm trong scope | Không sai dữ liệu/quyết định nghiệp vụ | Không gián đoạn đáng kể | Xử lý thường lệ, không thiệt hại đáng kể |
| 2 | Lộ tập nhỏ, độ nhạy cảm thấp | Sai ít bản ghi, đối chiếu/sửa đơn giản | Ảnh hưởng cục bộ một người/nhóm nhỏ | Khắc phục trong công việc thường ngày |
| 3 | Lộ dữ liệu nhạy cảm của một nhóm/phạm vi giới hạn | Sai dữ liệu ảnh hưởng một quy trình/chi nhánh | Một quy trình quan trọng bị gián đoạn, có cách làm tạm | Cần điều tra và khôi phục có kế hoạch |
| 4 | Lộ dữ liệu nhạy cảm đáng kể/nhiều nhóm | Sai dữ liệu trọng yếu hoặc quyết định của nhiều nhóm | Quy trình chính/nhiều chi nhánh ngừng đáng kể | Chi phí/nguồn lực lớn, ảnh hưởng đối tác/khách hàng đáng kể |
| 5 | Lộ dữ liệu cốt lõi hoặc đặc biệt nhạy cảm có hậu quả nghiêm trọng | Mất khả năng tin cậy dữ liệu cốt lõi, hậu quả khó đảo ngược | Hoạt động cốt lõi ngừng kéo dài, khả năng phục hồi bị đe dọa | Đe dọa khả năng tiếp tục hoạt động hoặc gây tổn thất nghiêm trọng |

“Nhỏ/lớn/kéo dài” cần owner giải thích bằng phạm vi bản ghi, quy trình, thời gian/chi phí dự kiến và khả năng chịu đựng của tổ chức. Mốc định lượng chưa được SME xác nhận; không giả vờ các mô tả đã đủ hiệu chuẩn. Ghi điều kiện còn mơ hồ để review. I=max giúp không cộng trùng cùng hậu quả vào nhiều chiều, nhưng không biểu diễn tổng thiệt hại tích lũy; giới hạn này phải được giữ trong báo cáo.

## 5. Cổng dữ liệu, mức risk và loại đánh giá

Đầu vào bắt buộc: scenario/asset/data/owner, tiền điều kiện, scope đường/hậu quả, actor/time, method/profile, loại đánh giá và rationale/source cho từng yếu tố. Thiếu đầu vào thiết yếu hoặc bất kỳ yếu tố E/F/G/C/T/A/B là UNKNOWN → `status=NEEDS_REVIEW`, `score=null`, `risk_level=null`. Không tự bỏ yếu tố thiếu rồi chia lại trọng số. Dữ liệu ngoài 1–5, trọng số không hợp lệ hoặc profile không hỗ trợ → lỗi đầu vào và NEEDS_REVIEW.

Đủ dữ liệu: tính P, L, I, R bằng số chưa làm tròn. Phân mức theo R gốc; chỉ hiển thị tối đa hai số thập phân. Các hệ số cố định cho phép lưu/tính chính xác theo số thập phân. Cùng input và version phải cho cùng output.

| R | Risk level |
| --- | --- |
| 1 ≤ R < 5 | LOW |
| 5 ≤ R < 10 | MODERATE |
| 10 ≤ R < 17 | HIGH |
| 17 ≤ R ≤ 25 | CRITICAL |

Đây là ngưỡng đề xuất nội bộ, không phải ngưỡng ISO/NIST. Chuyển từ thang nguyên v0.1 sang điểm liên tục cần dùng các khoảng đầy đủ này; không có khoảng trống 4–5, 9–10, 16–17. Điểm v0.1 và v0.2 không so sánh như cùng một phương pháp.

`CURRENT`: G cần evidence thực tế đúng scope. `INHERENT`: G=5 theo giả định loại bỏ các control được liệt kê; không có nghĩa control thực tế đã thất bại. `ILLUSTRATIVE`: ca tính toán giả định, đánh dấu mọi đầu vào mô phỏng; kết quả tính không được đưa vào risk register như assessment thực tế. Mỗi ví dụ ghi intended basis current/inherent. Không dùng trạng thái NOT_IMPLEMENTED trong fixture thiết kế làm evidence về môi trường chưa tồn tại.

G hoặc risk score không sửa ControlAssessment. Một vi phạm control bắt buộc vẫn là NOT_SATISFIED/CONTROL_GAP dù risk LOW. Test lỗi không phải bằng chứng chặn thành công. Risk acceptance là quyết định có quyền, scope và reason riêng; không sửa evidence/control result.

## 6. Ví dụ và ca kiểm tra phương pháp

Tất cả điểm số sau là **giả định minh họa**, không phải đánh giá hiện trạng CRM.

| ID / ví dụ | E,F,G | C,T,A,B | P | L | I | R / kết quả |
| --- | --- | --- | --- | --- | --- | --- |
| MF-01 / SC-01 giả định các yếu tố đã biết | 5,5,2 | 3,2,1,2 | 5 | 2.60 | 3 | 7.80 MODERATE |
| MF-02 / cùng scope, giả định bypass được xác minh | 5,5,5 | 3,2,1,2 | 5 | 5.00 | 3 | 15.00 HIGH |
| MF-03 / SC-02 minh họa đường chuyển cần chuẩn bị | 5,3,4 | 4,1,1,3 | 3.80 | 3.24 | 4 | 12.96 HIGH |
| MF-04 / scenario mở rộng giành đặc quyền, chỉ kiểm tra biểu diễn | 3,4,4 | 4,4,3,4 | 3.60 | 3.08 | 4 | 12.32 HIGH |
| MF-05 / SC-01 current với hồ sơ hiện tại | 5,5,UNKNOWN | UNKNOWN,UNKNOWN,UNKNOWN,UNKNOWN | — | — | — | NEEDS_REVIEW, không có điểm |
| MF-06 / mọi yếu tố ở mức 1 | 1,1,1 | 1,1,1,1 | 1 | 1 | 1 | 1 LOW |
| MF-07 / mọi yếu tố ở mức 5 | 5,5,5 | 5,5,5,5 | 5 | 5 | 5 | 25 CRITICAL |

MF-01: E=5 vì đã có đường và thông tin đăng nhập; F=5 vì nhập mật khẩu là hành động thường lệ; G=2 chỉ là giả định control hiệu lực với hạn chế phụ đã xác minh. C=3 giả định hậu quả dữ liệu nhạy cảm phạm vi giới hạn, cần owner xác nhận, không suy từ ba bản ghi fixture. MF-02 giữ E/F/impact để minh họa tác động của riêng G. MF-03: đã có phiên đọc (E=5), đường chuyển cần chuẩn bị (F=3), control giả định yếu (G=4), mất bí mật chi phối I=4. MF-04 có role ban đầu nhưng cơ hội tăng quyền còn điều kiện (E=3), hành vi giả định ít tùy chỉnh (F=4), cản trở nhỏ (G=4); đây không phải scenario mới được phép triển khai.

Ca phương pháp cần kiểm tra: biên R=5/10/17; UNKNOWN tại từng yếu tố; owner/rationale thiếu; input 0/6; giữ lịch sử version; tăng E/F/G hoặc một impact không làm R giảm; đổi G không sửa control result. JSON đi kèm có expected results và trạng thái minh họa; kiểm tra phép tính không phải chạy lab.

Độ nhạy đề xuất: MF-03 đổi trọng số E/F từ 40/60 sang 30/70 cho R=12.32, sang 50/50 cho R=13.60, vẫn HIGH. Đây là phân tích ngoài baseline để xem độ nhạy, không được tự đổi trọng số khi chấm từng case. Một ca sát ngưỡng có thể đổi mức do thay 1 điểm hoặc hệ số nhỏ; phải hiển thị yếu tố/rationale thay vì tin tuyệt đối vào nhãn. Trước khi chốt, người dùng xem các cặp case và xác nhận thứ tự ưu tiên có hợp lý; chưa có hiệu chuẩn với SME hay ước lượng xác suất.

## 7. Lưu lịch sử, reviewer và chuẩn bị cho AI

Mỗi lần đánh giá lưu context snapshot, scenario và ATT&CK version nếu có, method RM-01 v0.2, profile CONDITIONAL-BASE-v0.2, E/F/G/C/T/A/B cùng rationale/source và trạng thái evidence, weights, P/L/I/R trước làm tròn, result, actor/time và mức tin cậy. Confidence không nhân vào risk score để làm giảm risk khi thiếu dữ liệu. Chưa đủ căn cứ chọn mức → UNKNOWN; bất đồng reviewer giữ NEEDS_REVIEW cho đến khi có quyết định có lý do.

Reviewer có quyền ghi old/new, reason, nguồn, actor/time và target; không xóa kết quả tự động hoặc biến UNKNOWN thành đã xác minh. Thay facts/weights/rubric tạo assessment/method revision phù hợp, không ghi đè snapshot cũ. Đổi trọng số theo nhóm scenario cần profile mới, kiểm tra tính so sánh trước khi xếp chung; giai đoạn này dùng một profile.

AI sau này có thể đề xuất giá trị/mapping dựa trên evidence và chỉ rõ nguồn. Con người xác minh đầu vào; bộ tính xác định theo version thực hiện phép toán. Huấn luyện AI dự đoán/điều chỉnh trọng số cần dữ liệu/nhãn độc lập và kiểm chứng, không coi học lại các nhãn do công thức sinh ra là bằng chứng dự đoán tốt. Bước 02 chỉ chuẩn bị cấu trúc khái niệm, chưa chọn AI, schema, API hoặc stack.

## 8. Nguồn và phần do dự án thiết kế

- [ISO/IEC 27005:2022](https://www.iso.org/standard/80585.html): định hướng quản lý risk; mới tham khảo giới thiệu công khai, chưa rà soát toàn văn.
- [NIST SP 800-30 Rev.1](https://csrc.nist.gov/pubs/sp/800/30/r1/final): tham khảo hướng dẫn đánh giá risk, không gán công thức/hệ số của đồ án cho NIST.
- [MITRE ATT&CK — Tactics](https://attack.mitre.org/tactics/): mô tả mục tiêu hành vi để gắn metadata cho scenario.
- [IBM — Risk score calculation](https://www.ibm.com/docs/en/sva/11.0.1?topic=overview-risk-score-calculation): tham khảo ý tưởng trọng số trong đánh giá yêu cầu truy cập; mô hình này không dùng công thức fingerprint IBM. Chưa chọn tính năng adaptive authentication; WebAuthn CRM vẫn bắt buộc.

E/F/G/C/T/A/B, 40/60, phép điều chỉnh G, lấy max impact, ngưỡng và rules UNKNOWN là **quyết định thiết kế đề xuất của dự án**. RM-01 v0.2 không tuyên bố chứng nhận ISO, tuân thủ pháp luật hoặc khả năng dự báo đã kiểm chứng.
