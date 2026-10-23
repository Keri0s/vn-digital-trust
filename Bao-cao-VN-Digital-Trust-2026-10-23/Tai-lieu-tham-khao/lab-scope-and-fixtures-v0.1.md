# VN Digital Trust — Phạm vi lab và dữ liệu giả lập v0.1

**Ngày:** 2026-10-09. **Trạng thái:** Hoàn thành phạm vi thiết kế bước 01; chưa triển khai hoặc kiểm chứng lab.

Tài liệu đi cùng dữ liệu JSON và kế hoạch 6 bước. Tên, tài khoản, khách hàng, chi nhánh và trạng thái xác thực đều là dữ liệu giả lập.

## 1. Quyết định và đề xuất

| Nội dung | Trạng thái |
| --- | --- |
| Một công ty/deployment ở v0.1; nhiều công ty để sau | Người dùng xác nhận ngày 2026-10-09. |
| Có thể có nhiều chi nhánh và consultant được mời trong một công ty | Trong phạm vi v0.1; dùng hai chi nhánh giả lập. |
| Lab web nội bộ LAN và đường truy cập qua VPN | Hướng triển khai người dùng đề xuất; mô hình logic bên dưới cụ thể hóa để thiết kế. |
| Control đầu là MFA cho đăng nhập CRM | Đã chọn; không thay thế bằng việc chỉ có MFA ở VPN. |
| Mật khẩu + WebAuthn cho đăng nhập CRM | Người dùng xác nhận ngày 2026-10-09. Yêu cầu xác minh người dùng trên authenticator; chưa chọn sản phẩm/thiết bị hoặc kiểm chứng tương thích. |
| ISO/IEC 27005 cho risk, ISO/IEC 27002 cho control, ATT&CK cho tactic/technique | Đề xuất cách tổ chức tham chiếu; chưa phải tuyên bố đáp ứng tiêu chuẩn. |

## 2. Bối cảnh SME giả lập

ABC Trading có trụ sở BR-HCM và chi nhánh BR-DN, cùng một pháp nhân giả lập và một deployment VN Digital Trust. CRM quản lý hồ sơ khách hàng được giao cho nhân viên/chi nhánh. VN Digital Trust quản lý inventory, risk, control, evidence, assessment và treatment của công ty này.

Tài sản được đánh giá chính là CRM và dữ liệu khách hàng; máy khách, cổng VPN và nơi lưu dữ liệu/evidence là tài sản liên quan. Những thành phần này là trách nhiệm logic, không bắt buộc mỗi thành phần chạy trên một VM riêng.

## 3. Phạm vi mạng và truy cập

Luồng thiết kế: máy khách trong vùng mạng thử nghiệm → kết nối VPN → truy cập HTTPS tới dịch vụ được cấp → đăng nhập ứng dụng → kiểm tra quyền.

- CLIENT_ZONE: máy khách mô phỏng nhân viên, chi nhánh hoặc consultant, nằm ngoài vùng dịch vụ được bảo vệ. Có thể mô phỏng bằng mạng ảo trên cùng máy vật lý; chưa cần Internet công cộng.
- GATEWAY_ZONE: điểm vào VPN. Chính sách mạng chỉ cho từng nhóm đi tới dịch vụ cần dùng.
- SERVICE_ZONE: CRM và VN Digital Trust; không cho máy khách thử nghiệm đi thẳng tới đây để bỏ qua VPN.
- DATA_ZONE: database và evidence store; không mở trực tiếp cho máy khách/VPN users.
- RECEIVER_ZONE: điểm nhận dùng riêng cho bài thử exfiltration, nằm ngoài ranh giới được phép nhận dữ liệu CRM nhưng vẫn thuộc lab kiểm soát. Chỉ bật đường thử khi thực hiện bài test được xác định.
- Máy khách consultant chỉ cần đến VN Digital Trust; không tự có đường đến CRM, database hoặc kho evidence thô.

Chính sách yêu cầu VPN trong lab phải được kiểm chứng bằng thử truy cập khi chưa kết nối VPN. Một trang lỗi hay timeout đơn lẻ chưa chứng minh chính sách đúng nếu không biết nguyên nhân.

VPN giải quyết quyền đi vào mạng; trạng thái VPN không thay thế danh tính, MFA, quyền chức năng và quyền đối với dữ liệu trong ứng dụng. Thiết kế xác thực VPN sẽ được mô tả ở bước 04–05; control CRM vẫn được đánh giá riêng.

Đối với SC-01, tiền điều kiện là máy khách đã có đường tới CRM qua VPN. Vì vậy bài test chỉ chứng minh bảo vệ tại lớp đăng nhập CRM, chưa chứng minh khả năng vượt VPN hoặc xâm nhập từ Internet.

## 4. Phương thức xác thực

### 4.1. WebAuthn/FIDO2 và passkey

Công nghệ người dùng mô tả có thể thuộc WebAuthn/FIDO2: trình duyệt chuyển yêu cầu xác thực cho authenticator, người dùng xác nhận bằng PIN/sinh trắc học/thao tác trên thiết bị, authenticator dùng khóa riêng để ký và máy chủ xác minh bằng khóa công khai. Chưa có bằng chứng xác định chính xác phương thức AWS người dùng đã sử dụng.

Passkey có thể gắn với thiết bị hoặc được đồng bộ qua nhà cung cấp. Việc có hộp thoại PIN/vân tay không tự chứng minh khóa nằm trong TPM, không xuất được hoặc là khóa chỉ có trên một máy. Nếu muốn đánh giá yêu cầu bảo vệ bằng phần cứng, phải thêm tiêu chí và evidence phù hợp ở bước 02; kiểm tra tổ hợp thiết bị/OS/trình duyệt ở bước 04–05.

Người dùng đã chốt SC-01 dùng mật khẩu + WebAuthn làm yếu tố bổ sung, yêu cầu xác minh người dùng trên authenticator (user verification required). Luồng đăng nhập mới cần hoàn tất cả hai bước trước khi được truy cập dữ liệu CRM. Trạng thái đã đúng mật khẩu nhưng đang chờ WebAuthn chỉ cho tiếp tục xác thực, chưa cấp phiên có quyền nghiệp vụ. Đăng ký thiết bị đầu tiên và khôi phục phải có xác minh phù hợp, không để người chỉ biết mật khẩu bị lộ tự đăng ký khóa rồi vào CRM; tiêu chí đã được định nghĩa tại [CE-01 v0.1, C04/C05](control-evidence-v0.1.md). Các ngưỡng vận hành và cấu hình theo môi trường vẫn TO_SET_BEFORE_LAB; trạng thái có tiêu chí không chứng minh đã triển khai hoặc đã chạy test.

Đây là cấu hình baseline cho demo. Nếu sau này chuyển sang passkey không mật khẩu, phải ghi quyết định thay đổi và sửa tiền điều kiện, luồng, test. Không dùng nguyên bộ ca mật khẩu + OTP để kết luận cho WebAuthn.

Lab WebAuthn cần HTTPS có chứng chỉ được máy khách tin cậy, tên truy cập ổn định và cấu hình origin/RP ID đúng. Ví dụ tên giả lập có thể là crm.abc.test và trust.abc.test; đây chưa phải tên đã cấu hình. Không dùng việc bỏ qua cảnh báo chứng chỉ làm tiêu chí thành công. Bước 04–05 quyết định xác thực ở từng ứng dụng hay qua dịch vụ danh tính chung và RP ID tương ứng.

Chuyển tên miền/RP ID khi triển khai Internet có thể cần đăng ký lại credential. Cần thiết kế migration; không hứa các passkey lab tự dùng được trên tên miền production khác.

### 4.2. TOTP

TOTP là mã dùng một lần theo thời gian; Google Authenticator là một ứng dụng có thể tạo mã dạng này. Trong cấu hình mật khẩu + TOTP, máy chủ cần xác minh mã dựa trên bí mật dùng chung và thời gian. TOTP không có đặc tính ràng buộc với website giống WebAuthn và vẫn có thể bị phishing.

TOTP được giữ làm thông tin tham khảo, không thuộc đường đăng nhập hoặc fallback của baseline đã chọn. Các ca hết hạn/sử dụng lại OTP chỉ áp dụng trực tiếp cho cấu hình OTP; [TC-01 v0.1](control-test-cases-v0.1.md) đã xác định các ca phù hợp WebAuthn: challenge hết hạn/dùng lại, credential không hợp lệ, sai origin/RP ID, người dùng hủy và thiết bị mất/thu hồi. Đây là thiết kế expected results, chưa có test run.

Mất thiết bị, thêm thiết bị và khôi phục quyền truy cập phải có quy trình xác minh; không lưu password, OTP seed, private key hoặc recovery code thật vào bộ fixture hay evidence công khai.

## 5. Tài khoản giả lập

Các tài khoản dưới đây chỉ là bản ghi thiết kế; chưa được tạo trong bất kỳ dịch vụ nào. ENROLLED_SIMULATED trong JSON nghĩa là tiền điều kiện giả lập, không phải MFA đã được xác minh hoạt động. Đồng hồ fixture cố định: 2026-10-09 09:00 UTC+07.

| ID | Username | Ứng dụng | Vai trò / phạm vi | Trạng thái mẫu |
| --- | --- | --- | --- | --- |
| U001 | vdt.admin | VN Digital Trust | Quản trị organization, user và role | ACTIVE |
| U002 | vdt.security | VN Digital Trust | Inventory, risk, control/evidence và treatment | ACTIVE |
| U003 | vdt.owner | VN Digital Trust | Duyệt tác động/xử lý, chấp nhận risk | ACTIVE |
| U004 | vdt.reviewer | VN Digital Trust | Consultant: chỉ assessment ASM-DEMO-01 và evidence được giao | ACTIVE; quyền hết hạn 2026-10-31 17:00 UTC+07 |
| U101 | crm.admin | CRM | Quản lý tài khoản, role, cấu hình xác thực | ACTIVE |
| U102 | crm.sales.hcm | CRM | Nhân viên HCM; chỉ khách hàng được giao | ACTIVE |
| U103 | crm.sales.dn | CRM | Nhân viên Đà Nẵng; chỉ khách hàng được giao | ACTIVE |
| U104 | crm.manager.hcm | CRM | Trưởng nhóm; dữ liệu BR-HCM; được yêu cầu export | ACTIVE |
| U105 | crm.new | CRM | Nhân viên mới; chưa đăng ký MFA | ACTIVE / UNENROLLED |
| U106 | crm.pending | CRM | Vai trò dự kiến Sales; chưa được sử dụng tài khoản | PENDING |
| U107 | crm.disabled | CRM | Nhân viên đã thu hồi truy cập | DISABLED |
| U108 | crm.temporary | CRM | Chỉ đọc bản ghi được giao; quyền đã hết hạn | EXPIRED từ 2026-10-08 17:00 UTC+07 |

Email có dạng username@abc-trading.example và không dùng để gửi thư. Một người ngoài đời có thể đảm nhiệm nhiều vai trò, nhưng fixture tách tài khoản để kiểm chứng rõ quyền của từng vai trò.

### Quy tắc quyền của fixture

- Vai trò quyết định loại thao tác; phạm vi chi nhánh/bản ghi được giao quyết định dữ liệu được thao tác. Không chỉ kiểm tra role rồi cho xem toàn bộ công ty.
- CRM_ADMIN quản lý cấu hình/tài khoản, không mặc định có quyền đọc/xuất mọi hồ sơ khách hàng. Nếu cần phải cấp thêm quyền rõ ràng và ghi audit.
- CRM_MANAGER chỉ được yêu cầu export, không mặc nhiên được chuyển dữ liệu đến bất kỳ đích nào.
- VDT_ADMIN không mặc định được chấp nhận rủi ro. Quyền đó thuộc VDT_RISK_OWNER.
- VDT_REVIEWER không quản lý user, không tự chấp nhận rủi ro, không sửa evidence gốc. Điều chỉnh kết quả cần reason và giữ giá trị trước đó theo baseline.
- Không vai trò nào bỏ qua trạng thái PENDING, DISABLED, EXPIRED hoặc yêu cầu MFA chưa hoàn thành.
- Khi cần test thu hồi quyền admin/phiên đang tồn tại, tạo biến thể có trạng thái trước/sau từ baseline; không sửa fixture lịch sử đã được assessment dùng.

## 6. Dữ liệu khách hàng mẫu

| ID | Nhãn | Chi nhánh | Người được giao | Phân loại nội bộ |
| --- | --- | --- | --- | --- |
| CUS-001 | Khách hàng giả lập 01 | BR-HCM | U102 | INTERNAL_DEMO |
| CUS-002 | Khách hàng giả lập 02 | BR-HCM | U102 | INTERNAL_DEMO |
| CUS-003 | Khách hàng giả lập 03 | BR-HCM | U102 | INTERNAL_DEMO |
| CUS-004 | Khách hàng giả lập 04 | BR-DN | U103 | INTERNAL_DEMO |
| CUS-005 | Khách hàng giả lập 05 | BR-DN | U103 | INTERNAL_DEMO |
| CUS-006 | Khách hàng giả lập 06 | BR-DN | U103 | INTERNAL_DEMO |

Mỗi bản ghi có email giả lập customerNN@customer.example. Không chứa số điện thoại, giấy tờ, địa chỉ hoặc dữ liệu người thật. Nhãn INTERNAL_DEMO là phân loại do đồ án đặt, không phải phân loại pháp lý/ISO.

Ví dụ kiểm tra quyền: U102 đọc CUS-001 được phép, đọc CUS-004 bị từ chối; U104 xem ba khách hàng BR-HCM được phép nhưng không xem BR-DN. U108 đã hết hạn nên không được truy cập dù được gán thêm một bản ghi trong biến thể test.

## 7. Cách dùng tiêu chuẩn và ATT&CK

| Nguồn | Vai trò trong đồ án | Giới hạn |
| --- | --- | --- |
| ISO/IEC 27005:2022 | Tham chiếu tổ chức quy trình quản lý rủi ro, bối cảnh, phân tích/đánh giá và xử lý | Không tự cung cấp một risk score đã đúng cho SME giả lập; [RM-01 v0.4-r3](risk-method-v0.4.md) là phương pháp thiết kế của dự án, chưa hiệu chuẩn. |
| ISO/IEC 27002:2022 | Tham chiếu lựa chọn control, ví dụ quản lý truy cập, xác thực, bảo vệ dữ liệu | Mapping điều khoản/control cụ thể cần kiểm tra theo bản tiêu chuẩn được truy cập hợp lệ; chưa khẳng định đáp ứng đầy đủ. |
| MITRE ATT&CK | Gọi tên mục tiêu/hành vi, Initial Access TA0001 và Exfiltration TA0010 | Không dùng làm risk matrix hoặc chứng nhận control. Technique chỉ gán sau khi biết hành vi thực tế. |

Chỉ dùng phần giới thiệu công khai của ISO cho định hướng này; chưa rà soát toàn văn tiêu chuẩn. Các trường mô tả scenario dưới đây là mẫu thiết kế của dự án, không phải trích nguyên mẫu bắt buộc của ISO.

### SC-01 — Dùng mật khẩu bị lộ để truy cập CRM

- Asset/data: AST-CRM và các bản ghi CUS-001..003 thuộc phạm vi U102.
- Owner rủi ro: U003; người phụ trách kỹ thuật/evidence: U002.
- Tiền điều kiện: đã đến được CRM qua VPN; có mật khẩu của U102; không có yếu tố bổ sung, không có phiên đã xác thực.
- Sự kiện: thử hoàn tất đăng nhập mới và đọc dữ liệu CRM.
- Điều kiện bảo vệ cần đánh giá: MFA bắt buộc được thực thi tại CRM/lớp danh tính của CRM trên đường đăng nhập thuộc phạm vi.
- Hậu quả nếu thất bại: đọc/sửa dữ liệu trong quyền U102 trái phép; chưa suy ra có exfiltration hoặc quyền admin.
- Tham chiếu: TA0001; T1078 là technique ứng viên, sub-technique chưa chọn.
- Control đầu: AC-DEMO-01. Evidence dự kiến: cấu hình/phạm vi, enrollment và kết quả đăng nhập hợp lệ/không có yếu tố bổ sung cùng log đã xác minh.

### SC-02 — Chuyển dữ liệu CRM đến nơi nhận không được phép

- Asset/data: AST-CRM, CUS-001..003 và điểm nhận AST-RECEIVER.
- Owner rủi ro: U003.
- Tiền điều kiện: một phiên U102 có quyền đọc ba bản ghi; không cần tái diễn SC-01. Điểm nhận ở vùng riêng, vẫn do nhóm lab kiểm soát.
- Sự kiện: đưa dữ liệu giả lập từ phạm vi CRM tới điểm nhận không được phép theo chính sách lab.
- Điều kiện/điểm yếu giả định cần kiểm tra: quyền xuất dữ liệu hoặc đường truyền chưa được kiểm soát phù hợp. Không mặc định điểm yếu đã tồn tại.
- Hậu quả: mất tính bí mật của dữ liệu trong phạm vi thử nghiệm; tác động thực tế phải mô tả theo bối cảnh SME, chưa gán mức HIGH/LOW.
- Tham chiếu: TA0010. Chưa chọn technique vì chưa xác định cơ chế truyền cụ thể.
- Control ứng viên: quyền xuất dữ liệu, giới hạn đích truyền và ghi nhận/phát hiện hoạt động chuyển dữ liệu. Đây là các mục tiêu khác nhau, không gộp thành một kết quả duy nhất.
- Evidence dự kiến: quyền tài khoản, hành vi tạo tại nguồn, kết quả tại điểm nhận, log mạng/ứng dụng, cấu hình control và thời điểm. Không có dữ liệu tại điểm nhận chưa đủ chứng minh control đã chặn nếu test không thực sự chạy.
- Phạm vi bước 01: dùng để kiểm tra domain có biểu diễn được scenario ngoài initial access. Chưa triển khai test exfiltration hoặc cài DLP/SIEM.

## 8. Mở rộng sau lab

1. Nhiều chi nhánh cùng công ty: thêm phạm vi chi nhánh và kết nối được kiểm soát; giữ một organization. Consultant có account riêng, quyền giới hạn và thời hạn.
2. Tiếp cận từ Internet cho cùng công ty: đánh giá lại bề mặt truy cập, hostname/TLS/RP ID, session, giới hạn yêu cầu, vận hành/backup/log, năng lực phục vụ. Có thể vẫn đi qua VPN; việc dùng Internet không tự biến hệ thống thành multi-tenant.
3. Nhiều công ty: giai đoạn riêng; có thể bắt đầu bằng deployment tách biệt. Nếu dùng chung dịch vụ thì cần thiết kế và kiểm chứng cô lập danh tính, dữ liệu, evidence, backup và quyền consultant giữa tenant. Chỉ thêm organization_id chưa chứng minh cô lập tenant.

Bước 04–05 giữ cấu hình môi trường/hostname tách khỏi code, trách nhiệm auth rõ ràng và scope quyền có thể kiểm tra. Không đưa multi-tenant SaaS hoặc tính năng giống toàn bộ AWS vào v0.1.

## 9. Bàn giao hoàn thành bước 01 — lịch sử ngày 2026-10-09

**Trạng thái hiện hành ngày 2026-10-12:** bước 01 và bước 02 COMPLETE về thiết kế, bước 03–06 NOT_STARTED; VALID-G-01 ở bước 06 còn NOT_RUN. Xem kế hoạch mục 19. Các đoạn dưới mô tả thời điểm bàn giao bước 01.

Đã có bối cảnh, topology logic LAN/VPN, hai chi nhánh, fixture tài khoản/dữ liệu, SC-01 và SC-02. JSON chưa có evidence/kết quả risk; không bịa kết quả kiểm chứng.

Ngày 2026-10-09, người dùng chốt mật khẩu + WebAuthn. Bước 01 COMPLETE ở mức phạm vi thiết kế; bước 02–06 chưa bắt đầu. Kế hoạch mục 12 ghi đối chiếu điều kiện hoàn thành và đầu vào cho bước tiếp theo.

Thiết bị/OS/trình duyệt, việc khóa có được bảo vệ bằng phần cứng hay không và khả năng CRM hỗ trợ vẫn chưa kiểm chứng; thực hiện ở bước 04–06. Bước 02 sẽ xác định phương pháp risk, tiêu chí AC-DEMO-01, evidence, đăng ký/khôi phục và ca kiểm thử WebAuthn. Hoàn thành bước 01 không đồng nghĩa lab hoặc control đã hoạt động.

## 10. Nguồn

- [AWS — Supported configurations for passkeys/security keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_fido_supported_configurations.html).
- [Microsoft — Passkeys in Windows](https://learn.microsoft.com/en-us/windows/security/identity-protection/passkeys/).
- [W3C — WebAuthn](https://www.w3.org/TR/webauthn-2/).
- [Google — Authenticator](https://support.google.com/accounts/answer/1066447?hl=en).
- [OWASP — MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html).
- [ISO/IEC 27005:2022](https://www.iso.org/standard/80585.html).
- [ISO/IEC 27002:2022](https://www.iso.org/standard/75652.html).
- [MITRE ATT&CK — Exfiltration](https://attack.mitre.org/tactics/TA0010/).
