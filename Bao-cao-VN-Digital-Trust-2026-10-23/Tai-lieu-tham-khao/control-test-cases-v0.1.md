# Ca kiểm thử thiết kế TC-01 v0.1

**Ngày:** 2026-10-09. **Trạng thái:** expected results trước khi chạy; không phải test report. Baseline: lab ABC Trading, CRM qua VPN/HTTPS, mật khẩu + WebAuthn với UV required, không TOTP fallback/passwordless. Dùng fixture U101–U108 và dữ liệu CUS-001..006; test thay đổi trạng thái dùng bản sao fixture, không sửa snapshot lịch sử.

Trước mỗi ca ghi test ID, criteria ID, build/cấu hình/hostname/RP ID, tài khoản và credential giả lập, tiền điều kiện, thời điểm, actor, expected result, observed result, execution status, log/reference và reviewer. `PASS` chỉ khi test thực sự chạy đúng và observation + log chứng minh expected result. `FAIL` là expected result bị vi phạm đã xác minh. `INCONCLUSIVE` khi chạy lỗi hoặc telemetry thiếu; không đổi thành PASS. Không ghi bí mật/khóa riêng vào evidence.

| ID | Tiêu chí | Tiền điều kiện và hành động | Expected result |
| --- | --- | --- | --- |
| T01 | C01,C02 | U102 ở đúng origin, mật khẩu đúng, credential đã đăng ký và UV thành công. | Phiên nghiệp vụ chỉ cấp sau xác minh WebAuthn; đọc CUS-001 được. |
| T02 | C02,C03 | U102 nhập đúng mật khẩu rồi gọi CRM/API nghiệp vụ trước WebAuthn. | Không có quyền nghiệp vụ; không đọc CUS-001. |
| T03 | C03 | U102 chỉ có mật khẩu, không đưa assertion. | Không cấp phiên nghiệp vụ. |
| T04 | C03 | Mật khẩu sai nhưng credential hợp lệ. | Không đi qua cổng mật khẩu; không cấp quyền. |
| T05 | C03,C06 | Assertion ký bởi credential khác user U102. | Từ chối, không gắn credential của user khác. |
| T06 | C03,C06 | Challenge hết hạn theo TTL cấu hình đã chốt. | Từ chối, không cấp quyền; log chỉ ra lý do kiểm tra. |
| T07 | C03,C06 | Gửi lại assertion/challenge đã dùng. | Từ chối replay. |
| T08 | C06 | Client data có origin ngoài allowlist. | Từ chối dù chữ ký hợp lệ. |
| T09 | C06 | RP ID hash không khớp RP ID đã cấu hình. | Từ chối. |
| T10 | C06 | Authenticator không thực hiện UV / UV flag không có. | Từ chối; thao tác chạm thiết bị không đủ. |
| T11 | C03 | Người dùng hủy prompt WebAuthn. | Không cấp phiên nghiệp vụ; trạng thái chờ được kết thúc/giới hạn. |
| T12 | C04 | U102 chỉ có mật khẩu bị lộ, thử tự đăng ký credential mới. | Không đăng ký được và không vào CRM. |
| T13 | C04 | U105 chưa đăng ký WebAuthn, thử đăng nhập rồi truy cập dữ liệu. | Không vào CRM; chỉ quy trình bootstrap được phê duyệt mới cho đăng ký. |
| T14 | C04 | Bootstrap U105 qua xác minh/phê duyệt đã chốt, đăng ký credential rồi login đủ hai bước. | Audit đầy đủ; đăng ký đúng user và chỉ sau hai bước mới có quyền. |
| T15 | C05 | Thu hồi credential U102, thử login bằng credential cũ. | Từ chối; quyết định với phiên cũ được ghi và kiểm tra riêng. |
| T16 | C05 | U102 mất thiết bị; chỉ biết mật khẩu, xin recovery. | Không tự thay factor hoặc lấy phiên; cần xác minh và phê duyệt độc lập. |
| T17 | C05 | Recovery hợp lệ rồi thử credential mới và cũ. | Credential mới dùng được sau quy trình; cũ bị từ chối; log/phê duyệt có thể truy vết. |
| T18 | C01,C07 | Thử đường login thay thế, origin khác, hoặc truy cập qua endpoint chưa liệt kê. | Không có đường bypass; origin/TLS không hợp lệ không cấp quyền. |
| T19 | AC-DEMO-02 | U106 PENDING, U107 DISABLED, U108 EXPIRED thử đăng nhập mới với yếu tố hợp lệ. | Không có quyền nghiệp vụ; từng trạng thái có log. Đây là control vòng đời, không phải bằng chứng MFA riêng. |
| T20 | AC-DEMO-02 | Thu hồi U102 khi đã có phiên, thử tiếp tục dùng phiên. | Kết quả theo chính sách thu hồi phiên được chốt trước test; nếu chưa chốt, INCONCLUSIVE/NEEDS_REVIEW. |
| T21 | AC-DEMO-03 | U102 đã login hợp lệ đọc CUS-001 và CUS-004. | CUS-001 cho phép, CUS-004 từ chối theo phạm vi bản ghi/chi nhánh. |
| T22 | AC-DEMO-03 | U101 admin đã login thử đọc/xuất mọi hồ sơ. | Không có quyền mặc định ngoài quyền đã cấp rõ và audit. |
| T23 | C08 | Thực thi một ca âm khi máy chủ CRM/log không khả dụng. | INCONCLUSIVE; không ghi PASS hoặc kết luận control đã chặn. |
| T24 | EX-DEMO-01 | SC-02: U102 có phiên và ba bản ghi, thử chuyển đến AST-RECEIVER. | Chỉ đánh giá sau khi chốt đường truyền/đích/chính sách; log nguồn, mạng và receiver phải đối chiếu. Hiện NOT_READY, không suy từ MFA. |

Không có danh sách 20 ca gốc trong hồ sơ. Đây là danh sách mới theo baseline WebAuthn; không giả định đã chạy ca OTP. T19–T22 kiểm tra vòng đời tài khoản và quyền sau đăng nhập như control riêng. T24 chỉ giữ khả năng mở rộng sang Exfiltration, không yêu cầu triển khai tấn công ở bước 02. TTL, giới hạn thử, chính sách thu hồi phiên, đường login và môi trường cần được chốt trước bước 06; test nào phụ thuộc biến chưa chốt phải giữ NOT_READY.
