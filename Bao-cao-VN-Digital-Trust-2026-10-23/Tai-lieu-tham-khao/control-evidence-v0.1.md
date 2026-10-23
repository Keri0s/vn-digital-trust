# Bộ control và evidence thiết kế CE-01 v0.1

**Ngày:** 2026-10-09. **Trạng thái:** tiêu chí trước kiểm thử; chưa có evidence CRM thực tế. Áp dụng cho ABC Trading giả lập, một deployment và hai chi nhánh. Mã control/criteria là mã nội bộ đồ án.

## 1. Catalog nhỏ

| Control/version | Mục tiêu và phạm vi | Giới hạn |
| --- | --- | --- |
| AC-DEMO-01 v0.1 | Mật khẩu **và** WebAuthn có user verification cho mọi đăng nhập tương tác tài khoản người dùng CRM trong scope, trước khi cấp quyền nghiệp vụ. Gắn AUTH-CRM-01 và SC-01. | Không chứng minh an toàn VPN, phiên bị đánh cắp, API/service account, hoặc quyền sau đăng nhập. Không TOTP fallback/passwordless. |
| AC-DEMO-02 v0.1 | Cấp, vô hiệu, hết hạn và thu hồi tài khoản/quyền CRM theo người chịu trách nhiệm; kiểm tra đăng nhập mới và phiên cũ riêng. | Catalog thiết kế; không tự nhận CRM đã triển khai. |
| AC-DEMO-03 v0.1 | Role và phạm vi chi nhánh/bản ghi giới hạn thao tác CRM sau đăng nhập; admin không mặc nhiên đọc/xuất dữ liệu. | Catalog thiết kế; không thay thế MFA. |
| EX-DEMO-01 v0.1 | Ứng viên cho SC-02: chỉ tài khoản/phạm vi được duyệt mới xuất dữ liệu đến đích được phép. | Cần chốt chính sách đích và đường truyền trước khi test; chưa có kết luận. |

AC-DEMO-01 là control chi tiết đầu tiên. AC-DEMO-02/03 và EX-DEMO-01 là mục tiêu thiết kế để giữ ranh giới và xây ca kiểm thử, chưa có assessment. [ISO/IEC 27002:2022](https://www.iso.org/standard/75652.html) là nguồn định hướng chọn control, [MITRE M1032](https://attack.mitre.org/mitigations/M1032/) là tham chiếu mitigation, [OWASP MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) và [W3C WebAuthn](https://www.w3.org/TR/webauthn-2/) hỗ trợ tiêu chí kỹ thuật. Tập tiêu chí bên dưới là quyết định thiết kế; chưa gán điều khoản ISO cụ thể hoặc tuyên bố tuân thủ.

## 2. AC-DEMO-01 v0.1 — tiêu chí bắt buộc

| ID | Điều phải chứng minh trên **mọi đường đăng nhập tương tác thuộc scope** | Evidence tối thiểu mong đợi |
| --- | --- | --- |
| C01 | Danh sách tài khoản/role, đường đăng nhập, hostname/origin/RP ID và ngoại lệ được owner phê duyệt; đường thay thế không bỏ qua MFA. VPN không được tính là yếu tố thứ hai của CRM. | Snapshot cấu hình và scope, danh sách đường đăng nhập, xác nhận owner; test từng đường. |
| C02 | U102 hợp lệ: mật khẩu đúng + WebAuthn credential đã đăng ký đúng user, challenge còn hiệu lực, origin/RP ID đúng, chữ ký hợp lệ và UV flag được kiểm tra → cấp phiên nghiệp vụ; trước đó chỉ có trạng thái chờ xác thực, không đọc CRM/API nghiệp vụ. | Cấu hình verifier, trace request/response đã che dữ liệu nhạy cảm, log server và thử truy cập trước/sau. |
| C03 | Chỉ mật khẩu, WebAuthn sai/hủy/hết hạn, challenge đã dùng hoặc credential thu hồi → không cấp phiên nghiệp vụ; phản hồi không tiết lộ bí mật. | Test âm và log máy chủ đối chiếu ID yêu cầu, trạng thái phiên/quyền. |
| C04 | Registration đầu tiên/thêm credential cần bootstrap danh tính hoặc phiên đã hoàn tất MFA và phê duyệt phù hợp. Người chỉ có mật khẩu U102 bị lộ không thể tự đăng ký credential để vượt control; tài khoản U105 chưa đăng ký không được vào CRM trước bootstrap. | Quy trình/phê duyệt, cấu hình enrollment, test âm với password-only và test bootstrap hợp lệ. |
| C05 | Recovery/mất thiết bị: khóa cũ được thu hồi, xác minh danh tính và người phê duyệt độc lập với password-only, thao tác có audit; không có đường khôi phục yếu hơn cho phép vào CRM. Phiên hiện hữu và đăng ký mới được xem xét riêng. | Quy trình, hồ sơ phê duyệt giả lập, log revoke/recovery, test khóa cũ và credential mới. |
| C06 | Credential được ràng buộc với tài khoản và RP ID; server xác minh challenge một lần, origin, RP ID hash, chữ ký và UV. `userVerification=required` ở yêu cầu và UV được xác minh tại server; thao tác chạm thiết bị đơn thuần không đủ. | Cấu hình verifier/trace đã biên tập, test wrong origin/RP ID/UV off/replay. |
| C07 | TLS/HTTPS tin cậy, origin ổn định; thay đổi hostname/RP ID được quản lý như migration, không coi credential lab dùng được ở domain mới. | Cấu hình môi trường và kiểm tra máy khách; biên bản thay đổi nếu có. |
| C08 | Phạm vi, phiên bản cấu hình, thời điểm, người thực hiện và log xác minh cho mỗi test được giữ; test phải chạy đúng tiền điều kiện. | Manifest evidence, log/ảnh/config revision, test run và xác nhận reviewer. |

Tiêu chí thời gian sống challenge, giới hạn thử, timeout phiên và chính sách thông báo/recovery cần được **đặt giá trị theo môi trường và ghi vào cấu hình/test trước khi chạy**, thay vì tuyên bố một số chưa được chọn là chuẩn. C01–C08 là cổng đánh giá; các cấu hình chưa biết ở bước 02 được ghi `TO_SET_BEFORE_LAB`, không được coi là đã đạt.

## 3. Evidence và kết luận

Mỗi EvidenceRevision ghi ID/version, control implementation và scope, nguồn, owner, collected_at, valid_until, verification status, file/reference và hash nếu là file, thông tin môi trường/CRM version, người xác minh, thời điểm, redaction và test ID. Không lưu mật khẩu, private key, recovery code, toàn bộ assertion hoặc dữ liệu thật. Giữ bản đã dùng trong assessment bất biến; thay cấu hình hoặc evidence tạo revision và assessment mới. Evidence cho CRM không dùng mặc định để chứng minh VN Digital Trust auth, và ngược lại.

| Kết quả | Quy tắc CE-01 v0.1 |
| --- | --- |
| SATISFIED | C01–C08 trong phạm vi đánh giá có evidence phù hợp, còn hiệu lực, được xác minh; test dương/âm thành công theo expected result và không có vi phạm đã xác minh. |
| PARTIALLY_SATISFIED | Có evidence xác minh một phần phạm vi/tiêu chí đạt, phần còn lại **được xác minh là không đạt** nhưng control còn tác dụng ở phần khác; ghi chính xác scope. Không dùng trạng thái này để che phần chưa có evidence. |
| NOT_SATISFIED | Evidence đã xác minh chứng minh ít nhất một tiêu chí bắt buộc bị vi phạm trong scope (ví dụ password-only vào được CRM, UV không kiểm tra, bypass enrollment). Ghi tiêu chí và phạm vi thất bại. |
| INSUFFICIENT_EVIDENCE | Thiếu, hết hạn, chưa xác minh, sai scope hoặc test lỗi/không quan sát được ở tiêu chí cần thiết; chưa đủ căn cứ kết luận đạt/không đạt. Tạo EVIDENCE_GAP. |
| NOT_ASSESSED | Chưa bắt đầu assessment. |

Nếu có vi phạm xác minh và phần khác thiếu evidence, ghi NOT_SATISFIED cho scope vi phạm **và** EVIDENCE_GAP cho phần chưa biết; không tuyên bố toàn bộ scope đã được kiểm hết. EVIDENCE_GAP khác CONTROL_GAP. Test lỗi, timeout không rõ nguyên nhân, hoặc không thấy alert không chứng minh đã chặn. Kết quả công cụ chỉ là observation; reviewer kiểm tra tiền điều kiện, đường thực thi và log trước khi kết luận. Assessment giữ criteria version, evidence revision IDs, raw observations, reasoning, actor/time, snapshot và review decision nếu override; override cần quyền và không sửa kết quả gốc.

## 4. Trạng thái đầu vào hiện tại

Fixture `AUTH-CRM-01` là quyết định cấu hình, `implementation_status=NOT_IMPLEMENTED`; `ENROLLED_SIMULATED` chỉ là tiền điều kiện giả lập. Hiện chưa có EvidenceRevision hay test run. Vì vậy **chưa tạo ControlAssessment thực tế** và không gán SATISFIED/NOT_SATISFIED cho CRM. Nếu tạo assessment từ hồ sơ hiện có, kết quả đúng là INSUFFICIENT_EVIDENCE, không phải control thất bại. Kết quả risk current cũng NEEDS_REVIEW nếu phụ thuộc hiệu lực control này.
