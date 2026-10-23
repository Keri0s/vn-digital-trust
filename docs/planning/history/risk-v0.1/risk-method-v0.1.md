# Phương pháp đánh giá rủi ro kỹ thuật RM-01 v0.1

**Ngày:** 2026-10-09. **Trạng thái:** phương pháp thiết kế; chưa có điểm thực nghiệm. **Phạm vi:** một SME/deployment, scenario gắn tài sản và hậu quả cụ thể. Risk owner xác nhận tác động; người phụ trách kỹ thuật cung cấp điều kiện và bằng chứng.

## 1. Nguyên tắc

Đánh giá một **scenario trong một context snapshot**, không chấm tactic ATT&CK hay số lượng finding. Likelihood là nhận định về khả năng sự kiện và hậu quả mô tả xảy ra trong **12 tháng tới**, với tiền điều kiện của scenario và control hiện tại được nêu rõ. Impact là hậu quả hợp lý nếu sự kiện xảy ra, trước khi tính các hành động ứng cứu chưa được chứng minh. Cả hai là thang **thứ bậc**; phép nhân bên dưới chỉ là quy tắc xếp ưu tiên nội bộ, không phải xác suất hay thiệt hại tiền tệ.

Nguồn tham khảo định hướng: [ISO/IEC 27005:2022](https://www.iso.org/standard/80585.html) về quy trình quản lý rủi ro; [ISO/IEC 27002:2022](https://www.iso.org/standard/75652.html) về tập control; [MITRE ATT&CK](https://attack.mitre.org/) để mô tả hành vi. Rubric, chân trời 12 tháng, điểm và ngưỡng **do đồ án thiết kế**, không phải thang bắt buộc của ISO. Chưa rà soát toàn văn ISO, chưa ánh xạ điều khoản, chưa chứng nhận tuân thủ.

## 2. Đầu vào bắt buộc

Scenario ID, asset/data và owner, phạm vi/tài khoản/đường truy cập, tiền điều kiện, sự kiện, hậu quả; thời điểm và phiên bản context; căn cứ cho likelihood và impact; người đánh giá. Fact thiết yếu chưa rõ (ví dụ owner, phạm vi dữ liệu, hiệu lực control dùng để hạ likelihood) phải ghi UNKNOWN. Không biến UNKNOWN thành giả định control hoạt động. Mỗi mức chọn một mô tả khớp nhất và ghi lý do cùng bằng chứng/giả định; nếu hai mức đều có vẻ phù hợp, chọn mức cao hơn tạm thời và gắn `confidence=LOW` để review.

### Likelihood (L)

| Mức | Rubric 12 tháng, xét điều kiện tiếp cận và cản trở thực tế |
| --- | --- |
| 1 — Rất khó | Cần nhiều điều kiện độc lập ít khả thi; biện pháp cản trở liên quan đã được xác minh, không có dấu hiệu cùng loại trong phạm vi quan sát. |
| 2 — Khó | Có đường khả thi nhưng cần thêm điều kiện đáng kể hoặc control đã được xác minh làm giảm rõ khả năng hoàn tất. |
| 3 — Có thể | Đường thực hiện hợp lý và các điều kiện chính có thể xuất hiện; chưa có căn cứ mạnh để xếp thấp hoặc cao. |
| 4 — Dễ | Điều kiện chính sẵn có/lặp lại, hoặc control liên quan được xác minh không đạt; hành vi cần ít bước bổ sung. |
| 5 — Rất dễ | Đường thực hiện đang mở/rất thường xuyên và có bằng chứng lặp lại sát bối cảnh; cần xử lý ngay. |

Không suy L=1 chỉ vì chưa có sự cố; không suy L=5 chỉ từ một test công cụ. Nếu hiệu lực control là lý do quyết định để chọn L thấp mà evidence chưa đủ, L=UNKNOWN và NEEDS_REVIEW.

### Impact (I)

Đánh giá hậu quả lớn nhất **có căn cứ** trong ba chiều: bí mật/toàn vẹn, gián đoạn hoạt động, chi phí/phục hồi. Ghi chiều chi phối, số bản ghi/người dùng hoặc quy trình bị ảnh hưởng. Dữ liệu giả lập chỉ phục vụ test; impact mô tả tương tự trong nghiệp vụ SME giả định, không định giá tổn thất thực.

| Mức | Rubric hậu quả hợp lý |
| --- | --- |
| 1 — Không đáng kể | Một lỗi cục bộ, không lộ/sửa dữ liệu nghiệp vụ, xử lý thường lệ. |
| 2 — Nhỏ | Ít bản ghi hoặc một người dùng bị ảnh hưởng; khôi phục trong công việc thường ngày, không ngừng quy trình chính. |
| 3 — Vừa | Một nhóm/chi nhánh hoặc tập dữ liệu giới hạn; cần điều tra và khôi phục có kế hoạch. |
| 4 — Lớn | Nhiều nhóm/chi nhánh hoặc dữ liệu nhạy cảm đáng kể; quy trình chính gián đoạn hoặc khắc phục tốn nguồn lực lớn. |
| 5 — Nghiêm trọng | Phần lớn hoạt động hoặc tập dữ liệu trọng yếu bị ảnh hưởng kéo dài; khả năng phục hồi bị đe dọa. |

Thiếu phạm vi dữ liệu, owner xác nhận hậu quả, hoặc thiếu căn cứ phân biệt các mức → I=UNKNOWN.

## 3. Quy tắc RM-01 v0.1

Nếu L hoặc I là UNKNOWN, hoặc đầu vào thiết yếu thiếu, `status=NEEDS_REVIEW`, `risk_level=null`, không tự tính. Nếu đủ đầu vào: `score=L×I`; 1–4 LOW, 5–9 MODERATE, 10–16 HIGH, 17–25 CRITICAL. Ma trận theo L hàng/I cột:

| L \ I | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 L | 2 L | 3 L | 4 L | 5 M |
| 2 | 2 L | 4 L | 6 M | 8 M | 10 H |
| 3 | 3 L | 6 M | 9 M | 12 H | 15 H |
| 4 | 4 L | 8 M | 12 H | 16 H | 20 C |
| 5 | 5 M | 10 H | 15 H | 20 C | 25 C |

`L/M/H/C` lần lượt là LOW/MODERATE/HIGH/CRITICAL. Đây là ưu tiên thảo luận, không tự ra quyết định chấp nhận rủi ro. Control result và risk level là hai kết quả riêng. Nếu control chưa xác minh, không giảm L dựa trên control đó. Có thể đánh giá **inherent** bằng giả định không tính control, hoặc **current/residual** theo control đã xác minh; phải ghi rõ loại, không so sánh hai loại như cùng đầu vào.

Override của reviewer có quyền cần lưu kết quả tự động, kết quả mới, lý do, bằng chứng, actor/time, phạm vi và version. Không được override để che UNKNOWN/thiếu evidence thành kết quả đã xác minh; nếu cần đánh giá tạm, ghi `provisional` và review riêng. Sửa rubric/ngưỡng tạo RM-01 v0.2, không sửa bản đã dùng.

## 4. Ví dụ cố định, chưa phải kết quả lab

| Ví dụ | Đầu vào và rationale giả định | Kết quả |
| --- | --- | --- |
| EX-R1 / SC-01 inherent | L=3: đã có đường CRM qua VPN và mật khẩu U102, chưa giả định MFA hiệu lực; I=2: chỉ ba bản ghi giả lập thuộc U102 trong bối cảnh demo. Owner cần xác nhận tác động kinh doanh thực tế. | 3×2=6 MODERATE, `confidence=LOW`, minh họa. |
| EX-R2 / SC-01 current | Cùng scenario, nhưng muốn hạ L nhờ AC-DEMO-01; chưa có evidence thực thi CRM. | L=UNKNOWN, NEEDS_REVIEW; không chuyển EX-R1 thành LOW. |
| EX-R3 / SC-02 | Có phiên U102 đã hợp lệ; chưa rõ quyền xuất/đường truyền và hậu quả SME. | L=UNKNOWN, I=UNKNOWN, NEEDS_REVIEW. |
| EX-R4 / phép tính | L=4 và I=4 đã có căn cứ trong một snapshot giả định. | 16 HIGH; cùng input/RM-01 v0.1 luôn ra HIGH. |

Mỗi RiskEvaluation lưu scenario snapshot, loại inherent/current, giá trị và rationale L/I, source refs, confidence, RM-01 v0.1, actor/time, kết quả tự động và review. Retest tạo evaluation mới. Ví dụ EX-R1 không phải risk register chính thức của ABC Trading.

## 5. Đối chiếu cách tính của IBM Security Verify Access

[IBM — Risk score calculation](https://www.ibm.com/docs/en/sva/11.0.1?topic=overview-risk-score-calculation) mô tả **điểm rủi ro của một yêu cầu truy cập** bằng cách so device fingerprint hiện tại với các fingerprint đã đăng ký. Công thức IBM là `100 × tổng trọng số thuộc tính không khớp / tổng trọng số thuộc tính có thể xác định`; thuộc tính không xác định bị trừ khỏi mẫu số. Engine chọn điểm thấp nhất trong các fingerprint được so sánh, sau đó policy so với ngưỡng để permit, step-up hoặc deny. Ví dụ IBM có 1 thuộc tính không khớp trọng số 10 trong tổng 70 → khoảng 14 điểm. Trọng số, ngưỡng và thuộc tính phải được cấu hình theo môi trường; tài liệu IBM không cung cấp điểm likelihood/impact của SC-01 cho ABC Trading.

Do đó có thể dùng cách IBM làm **tín hiệu risk cho phiên đăng nhập** nếu sau này CRM/IdP thu được fingerprint và có cơ sở quản lý thiết bị. Lưu nó thành `login_request_score`, cùng policy/version, matched fingerprint, thuộc tính/trọng số, phần dữ liệu không xác định và quyết định; không ghi đè `RiskEvaluation` của scenario theo RM-01. Điểm thấp không được bỏ qua WebAuthn bắt buộc của AC-DEMO-01. Điểm cao có thể dẫn tới từ chối hoặc bước xác minh bổ sung theo policy đã chốt, nhưng không tự suy ra impact hay mức risk của SME. Thiếu nhiều thuộc tính có thể làm điểm tưởng thấp dù độ bao phủ kém; cần cổng dữ liệu tối thiểu/NEEDS_REVIEW trước khi dùng quyết định tự động. Đây là phương án mở rộng **chưa chọn triển khai**; cần quyết định chính sách và kiểm chứng quyền riêng tư, dữ liệu, độ ổn định fingerprint ở bước 04–06.
