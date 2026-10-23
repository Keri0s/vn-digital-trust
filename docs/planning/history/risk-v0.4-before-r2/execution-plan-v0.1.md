# VN Digital Trust — Kế hoạch thực hiện v0.1

**Cập nhật:** 2026-10-11

**Trạng thái:** Bước 01 COMPLETE về phạm vi thiết kế; bước 02 IN_PROGRESS — RM-01 v0.4 đã cập nhật theo sửa đổi được người dùng đồng ý ngày 2026-10-10. Bước 03–06 NOT_STARTED. Chưa triển khai hoặc kiểm chứng lab. Mục 13–15 là lịch sử; trạng thái hiện hành và việc còn thiếu ở mục 16.

## 1. Nơi theo dõi tiến độ chung

Bản làm việc chính: D:/Projects/vn-digital-trust/docs/planning/execution-plan-v0.1.md.

Mỗi chat đọc file này và docs/README.md trước khi tiếp tục. Mỗi lần bàn giao ghi: đầu ra đã có, kiểm tra đã thực hiện, quyết định, giả định chưa xác minh và việc tiếp theo. Các chat có lịch sử riêng; không dựa vào việc mọi chat tự nhớ toàn bộ trao đổi.

Chỉ một bước được IN_PROGRESS tại một thời điểm. Chỉ chuyển bước khi điều kiện hoàn thành có bằng chứng trong đầu ra. Câu hỏi về bước sau được ghi vào mục chờ, không tự khởi động bước đó. Nếu phát hiện thiếu sót ở bước trước, mở lại bước đó và ghi ảnh hưởng. Người dùng có thể đổi thứ tự một cách rõ ràng; phải ghi lý do và cập nhật kế hoạch.

## 2. Phạm vi được giữ

- Kỹ thuật, inventory, asset và risk management trước; đánh giá nghĩa vụ pháp lý để giai đoạn sau.
- Một SME trên một deployment; nhiều tài khoản với RBAC; tài khoản do admin quản lý, không tự đăng ký công khai.
- SME self-assessment là luồng chính; consultant reviewer tùy chọn.
- Kết quả theo quy tắc xác định, có version và rationale; likelihood/impact cần đầu vào có căn cứ, không tự suy ra từ ATT&CK.
- Đánh giá dựa trên evidence: thiếu evidence khác control thất bại; UNKNOWN không tự thành LOW.
- Không chứng nhận tuân thủ pháp luật; chưa dùng AI làm người quyết định kết quả.
- Đề xuất demo local/VM, dữ liệu giả lập, ABC Trading và CRM làm bối cảnh. Topology cụ thể cần chốt ở bước 01.
- Atomic Red Team và Caldera là công cụ kiểm chứng bên ngoài sản phẩm. Không mở rộng v0.1 thành SOC/SIEM hoặc nền tảng tự động tấn công.

## 3. Sáu bước và điều kiện hoàn thành

| Bước | Trạng thái | Đầu ra cần có | Điều kiện hoàn thành |
| --- | --- | --- | --- |
| 01 — Kịch bản demo và phạm vi triển khai | COMPLETE — thiết kế | Hồ sơ SME giả lập; system/assets/data liên quan; topology dự kiến; vai trò; mô tả kịch bản và ranh giới | Một kịch bản chính có tiền điều kiện, sự kiện, hậu quả, phạm vi; một ca exfiltration để kiểm tra mô hình; xác định rõ giả định và điều chưa biết. Đối chiếu hoàn thành tại mục 12. |
| 02 — Phương pháp risk và control/evidence mẫu | IN_PROGRESS — review RM-01 v0.4 | Rubric likelihood/impact và quy tắc có version; bộ control nhỏ; tiêu chí và evidence mẫu | Có nguồn tham khảo, giới hạn, ví dụ tính nhất quán; phân biệt thiếu evidence/control thất bại; UNKNOWN và override có quy tắc. Kỳ vọng test được xác định trước khi chạy. Bản mới và việc cần review ở mục 16; chưa bàn giao sang bước 03. |
| 03 — Luồng xử lý chi tiết | NOT_STARTED | Use case được tinh chỉnh, activity/sequence cho assessment → gap → treatment → retest | Truy vết được từ yêu cầu đến luồng; có đường thành công, thiếu evidence, lỗi nhập, thiếu quyền và retest giữ lịch sử. Sơ đồ được render/đọc kiểm tra. |
| 04 — Kiến trúc v0.1 | NOT_STARTED | Thành phần, luồng dữ liệu, deployment, lưu evidence, auth/RBAC; ranh giới lab | Mỗi thành phần có trách nhiệm rõ; mô tả nguồn evidence, kiểm soát quyền, snapshot/version và lỗi; khả thi trong tài nguyên đồ án. |
| 05 — Công nghệ, database và API | NOT_STARTED | Quyết định công nghệ có lý do; ERD; API contract; thiết kế lưu file và version | Thiết kế đáp ứng luồng/kiến trúc; constraints, quyền, trạng thái và lỗi có chỗ xử lý; không chọn công nghệ chỉ vì phổ biến. |
| 06 — Prototype và kiểm chứng | NOT_STARTED | Luồng chạy được inventory → scenario → evaluation → control/evidence → gap → treatment → retest/report; bộ kiểm thử và báo cáo lab | Chứng minh RBAC, tính lặp lại, thiếu evidence khác failed control, lỗi test không bị kết luận sai, lịch sử bất biến; ghi rõ giới hạn và những gì chưa kiểm chứng. |

Không bắt buộc có Caldera để hoàn thành bước 06. Việc tích hợp hoặc chạy công cụ mô phỏng chỉ thực hiện sau khi có môi trường, tiêu chí và mục đích kiểm chứng cụ thể.

## 4. Initial access và exfiltration

Initial Access và Exfiltration là các tactic (mục tiêu của hành vi) trong ATT&CK, không phải bản thân một bản mô tả rủi ro đầy đủ. Kịch bản rủi ro phải gắn với tài sản/dữ liệu, điều kiện, sự kiện và hậu quả trong bối cảnh cụ thể.

Đề xuất giữ hai trường hợp để thiết kế, chưa xem là kịch bản đã được kiểm chứng:

| Trường hợp | Câu chuyện mẫu | Cần làm rõ ở bước 01–02 |
| --- | --- | --- |
| SC-01 — Truy cập trái phép | Người không được phép dùng tài khoản CRM bị lộ để có quyền truy cập dữ liệu khách hàng giả lập | CRM nào, tài khoản/quyền nào, đường truy cập, điều kiện MFA/phiên đăng nhập, hậu quả; control và evidence phù hợp với mô hình xác thực thực tế. |
| SC-02 — Đưa dữ liệu ra ngoài trái phép | Một tài khoản đã có quyền đọc chuyển tập dữ liệu khách hàng giả lập đến nơi nhận thử nghiệm nằm ngoài ranh giới tin cậy của CRM | Dữ liệu nào, nguồn/đích, quyền xuất dữ liệu, luồng truyền, ranh giới mạng, log quan sát, biện pháp kiểm soát; nơi nhận vẫn thuộc lab do mình kiểm soát. |

SC-02 có thể bắt đầu với tiền điều kiện đã có quyền đọc. Không cần tự động dựng toàn bộ chuỗi initial access để kiểm tra exfiltration. Khi so sánh các đánh giá, phải giữ và ghi rõ tiền điều kiện này.

Domain hiện tại có RiskScenario, DataAsset, RiskControlLink, EvidenceRevision và ControlAssessment nên có nền tảng khái niệm dùng cho cả hai. Chưa có prototype chạy để khẳng định tương thích thực tế.

Các điểm cần kiểm tra khi hoàn thiện mô hình, không triển khai schema lúc này:

- Không hardcode mọi scenario vào initial access hoặc MFA. ATT&CK mapping nếu cần là metadata tùy chọn, có version; một scenario có thể liên quan nhiều tactic/technique.
- Bổ sung cách biểu diễn nguồn/đích dữ liệu, tiền điều kiện và ranh giới tin cậy; bước 01 mô tả bằng văn bản, bước 03–05 quyết định cấu trúc nếu luồng yêu cầu.
- Chọn control theo mục tiêu cụ thể. MFA không tự chứng minh dữ liệu được bảo vệ khi phiên/tài khoản đã bị kiểm soát.
- Evidence cho đăng nhập không tự chứng minh hoạt động xuất/chuyển dữ liệu được chặn hoặc phát hiện.
- Không cộng điểm hoặc tính likelihood theo số technique được mô phỏng. Kết quả kỹ thuật chỉ là một phần căn cứ đánh giá rủi ro.

## 5. Atomic Red Team và Caldera nằm ở đâu

**Bây giờ (bước 01):** ghi mục đích và giới hạn mô phỏng; chọn câu chuyện cần kiểm chứng. Chưa cài/chạy công cụ.

**Bước 02:** đặt tiêu chí control và evidence cần thu. Có thể ghi ứng viên test; cần kiểm tra test thực sự đo được mục tiêu và phù hợp OS/ứng dụng. Một atomic mô phỏng hành vi đơn lẻ không mặc nhiên chứng minh toàn bộ initial access hoặc toàn bộ quy trình CRM.

**Bước 03–05:** thiết kế cách nhận và truy vết evidence từ lab. Ưu tiên file/reference do người dùng nhập cho v0.1; chưa bắt buộc kết nối trực tiếp API của công cụ.

**Bước 06:** sau khi luồng cơ bản và lab sẵn sàng, bắt đầu bằng một vài Atomic phù hợp. Chỉ xem xét Caldera khi cần kiểm chứng chuỗi nhiều bước và việc thu evidence đã ổn định. Nếu nguồn lực không đủ hoặc không đem lại thêm tiêu chí kiểm chứng, để Caldera cho v0.2+.

Lab sử dụng tài sản được phép kiểm thử, dữ liệu giả lập, nơi nhận kiểm soát được và khả năng khôi phục trạng thái. Không dùng dữ liệu khách hàng thật để minh họa exfiltration.

Mỗi lần mô phỏng cần lưu tối thiểu: scenario/asset, công cụ và version/test ID, môi trường/tiền điều kiện, thời điểm, mục tiêu control, kết quả mong đợi, kết quả quan sát, trạng thái thực thi, log/evidence references, giới hạn và người xác minh.

Phân biệt bốn câu hỏi:

1. Test có thực sự chạy đúng và tạo hành vi mong muốn không?
2. Telemetry/log cần thiết có được thu đầy đủ không?
3. Control được đánh giá là phòng ngừa, phát hiện hay phản ứng; kết quả có đáp ứng tiêu chí của control đó không?
4. Căn cứ mới ảnh hưởng likelihood/impact như thế nào theo phương pháp đã chọn?

Test lỗi không tự nghĩa là hệ thống đã chặn. Không có alert không tự nghĩa là không có hành vi. Công cụ báo thành công không tự nghĩa là control thất bại. Kết quả không đủ xác minh phải giữ trạng thái chưa đủ evidence; không tự đặt risk LOW hoặc HIGH.

## 6. Tổ chức chat và bàn giao

Nhóm thanh bên: **VN Digital Trust · 6 bước**. Chat hiện tại là bước 01, năm chat mới dành cho bước 02–06. Đây là tổ chức giao diện; năm chat mới là local projectless, chưa phải năm chat thuộc project ChatGPT gốc hoặc năm checkout của repository.

Các chat dùng chung đường dẫn tài liệu D:/Projects/vn-digital-trust. Khả năng đọc/ghi vẫn theo quyền của từng chat. File trong sources/ của project mirror là tham chiếu chỉ đọc. Không ghi đè tài liệu research lịch sử bằng baseline kỹ thuật.

Danh sách ID chat được ghi ở phần cuối sau khi khởi tạo. Các chat bước sau chỉ xác nhận chờ trong lượt đầu; không tự chạy bước đó. Không có automation hoặc chuyển bước tự động.

### Mẫu bàn giao khi hoàn thành một bước

- Bước / ngày / trạng thái:
- File đầu ra và phiên bản:
- Điều kiện hoàn thành đã kiểm tra + bằng chứng:
- Quyết định và lý do:
- Giả định / điều còn chưa xác minh:
- Việc chờ giai đoạn sau:
- Bước tiếp theo được phép bắt đầu:

## 7. Đầu vào lịch sử cho bước 02

Hồ sơ [phạm vi lab và dữ liệu giả lập](../../lab-scope-and-fixtures-v0.1.md) đã mô tả ABC Trading/CRM, hai chi nhánh, topology logic LAN/VPN, assets, tài khoản/role, dữ liệu, SC-01 và SC-02. [JSON fixture](../../lab-fixtures-v0.1.json) là dữ liệu thiết kế, chưa tạo tài khoản thật. Người dùng đã chọn mật khẩu + WebAuthn; đầu vào này đã được bước 02 tiếp nhận và xử lý tại mục 13.

Đã chọn nhóm control quản lý quyền truy cập để làm trước; control đầu tiên là yêu cầu MFA cho đăng nhập tương tác của tài khoản người dùng CRM trong phạm vi demo (xem mục 10). Risk matrix v0.1 là bản lịch sử tại mục 13; phương pháp v0.4 đang review tại mục 16. Tiêu chí control và test ID được giữ làm đầu vào thiết kế. Topology triển khai chi tiết, các control mở rộng, công nghệ, DB/API chưa chốt. Chưa chạy Atomic hoặc Caldera; chưa có xác nhận nhu cầu từ SME/consultant. Những hạn chế này phải được giữ trong báo cáo đồ án.

## 8. Nguồn tham khảo

- [MITRE ATT&CK — Initial Access](https://attack.mitre.org/tactics/TA0001/).
- [MITRE ATT&CK — Exfiltration](https://attack.mitre.org/tactics/TA0010/).
- [Atomic Red Team — repository chính thức](https://github.com/redcanaryco/atomic-red-team).
- [MITRE Caldera — tài liệu chính thức](https://caldera.readthedocs.io/en/stable/).
- [OpenAI — Projects and chats](https://learn.chatgpt.com/docs/projects).

Các nguồn trên hỗ trợ khái niệm và khả năng công cụ. Thứ tự thực hiện và phạm vi demo là quyết định thiết kế cho đồ án này, không phải yêu cầu bắt buộc của MITRE hay OpenAI.

## 9. Chỉ mục chat

| Bước | Chat ID |
| --- | --- |
| 01 | 01a0ee1d-1428-76f3-88d1-36162069ef32 |
| 02 | 01a11017-50a3-7160-adb8-33610b115257 |
| 03 | 01a11017-5d2d-7f61-9eca-72ad4a73d759 |
| 04 | 01a11017-6a8a-7dd3-ae84-92ec9c17c946 |
| 05 | 01a11017-7725-7c80-84fe-349ae18b455f |
| 06 | 01a11017-843c-75d0-9988-79baf7614ceb |

## 10. Quyết định chọn nhóm control đầu tiên — 2026-10-06

**Yêu cầu người dùng:** Làm quản lý quyền truy cập / initial access trước.

**Nhóm được chọn:** Access Control Management — quản lý việc cấp, sử dụng và thu hồi quyền truy cập. Initial Access là mục tiêu tấn công được xét trong scenario đầu, không phải tên một control và không đồng nghĩa toàn bộ quản lý quyền truy cập.

**Control đầu tiên để đặc tả:** AC-DEMO-01 — Yêu cầu MFA cho đăng nhập tương tác của tài khoản người dùng CRM nằm trong phạm vi demo. Đây là mã nội bộ đồ án, không phải mã CIS hoặc MITRE.

### Kịch bản SC-01 được thu hẹp

- Bối cảnh thiết kế: CRM của SME giả lập ABC Trading; dữ liệu khách hàng giả lập.
- Tiền điều kiện: người thử nghiệm truy cập được trang đăng nhập trong lab và biết username/password của một tài khoản demo đang hoạt động; chưa có yếu tố xác thực bổ sung hoặc phiên đăng nhập hợp lệ. 
- Sự kiện cần xem xét: sử dụng thông tin đăng nhập bị lộ để đăng nhập CRM và truy cập dữ liệu theo quyền tài khoản đó.
- Mục tiêu control đầu: chỉ biết username/password chưa đủ để hoàn tất đăng nhập mới trong phạm vi đã chọn; người dùng hợp lệ vẫn có luồng đăng nhập hoạt động.
- Hậu quả nếu truy cập được: có thể đọc hoặc thay đổi dữ liệu trong quyền của tài khoản bị lộ; chưa khẳng định đã có exfiltration.
- Phạm vi đầu: đăng nhập mới bằng tài khoản người dùng. Loại MFA, tài khoản mẫu, đường đăng nhập/khôi phục, ngoại lệ và cách xử lý phiên phải được ghi rõ khi chốt lab/tiêu chí. Không suy rộng kết quả sang API token, service account, phiên bị đánh cắp hoặc mọi kỹ thuật initial access.

### Thứ tự control trong nhóm

1. **MFA cho đăng nhập CRM:** làm đầu tiên để có một control cụ thể đi xuyên suốt luồng evidence → assessment → gap → treatment → retest.
2. **Cấp và thu hồi truy cập:** xét tiếp tài khoản có người chịu trách nhiệm, được cấp đúng nhu cầu và bị thu hồi khi không còn được phép truy cập; cần tách kiểm tra đăng nhập mới và phiên đang tồn tại.
3. **Quyền theo vai trò/đặc quyền tối thiểu:** xét tiếp các thao tác được phép sau đăng nhập. Control này giới hạn phạm vi hành động; không tự ngăn người có mật khẩu bị lộ đăng nhập.

Các mục 2–3 là hướng mở rộng trong nhóm đã chọn, chưa phải yêu cầu phải triển khai đồng thời. Không mở rộng ngay sang tất cả tactic của ATT&CK.

### Ranh giới sản phẩm và hệ thống được đánh giá

VN Digital Trust ghi nhận CRM, control, evidence, đánh giá và việc khắc phục. CRM/lớp xác thực của CRM là nơi thực thi MFA và quyền truy cập. Tài khoản/RBAC của chính VN Digital Trust phục vụ bảo vệ ứng dụng đánh giá; không dùng việc đăng nhập VN Digital Trust làm bằng chứng mặc định rằng CRM đã được bảo vệ.

### Đầu vào chuyển sang bước 02 khi bước 01 hoàn thành

- Evidence dự kiến: cấu hình áp dụng MFA cùng phạm vi tài khoản, trạng thái đăng ký, kết quả kiểm thử đăng nhập hợp lệ và chỉ có mật khẩu, log tương ứng; ghi nguồn/thời điểm và xác minh. Ảnh một tùy chọn MFA chưa đủ chứng minh enforcement trên mọi đường đăng nhập.
- Tiêu chí chi tiết và dữ liệu kiểm thử sẽ chốt ở bước 02. Ví dụ định hướng: đủ evidence xác minh cho đúng phạm vi mới kết luận SATISFIED; evidence xác minh cho thấy vi phạm tiêu chí mới kết luận NOT_SATISFIED; thiếu evidence hoặc lỗi môi trường chưa đủ giải thích thì INSUFFICIENT_EVIDENCE.
- Atomic Red Team chỉ chọn nếu test phù hợp control/CRM thực tế. Kiểm thử đăng nhập có kiểm soát có thể phù hợp hơn một atomic có sẵn; chưa bắt buộc dùng Atomic/Caldera cho control này.

**Trạng thái lịch sử tại quyết định ngày 2026-10-06:** Bước 01 IN_PROGRESS; bước 02–06 NOT_STARTED. Trạng thái hiện hành xem mục 16.

### Căn cứ tham khảo

- [CIS Control 6 — Access Control Management](https://www.cisecurity.org/controls/access-control-management): căn cứ cho nhóm quản lý cấp, quản lý và thu hồi truy cập.
- [MITRE ATT&CK T1078 — Valid Accounts](https://attack.mitre.org/techniques/T1078/): căn cứ mô tả lạm dụng tài khoản hợp lệ để giành quyền truy cập; ánh xạ mang tính bối cảnh, chưa chọn sub-technique khi chưa biết loại tài khoản.
- [MITRE ATT&CK M1032 — Multi-factor Authentication](https://attack.mitre.org/mitigations/M1032/): căn cứ kỹ thuật cho lựa chọn MFA.

Phạm vi, thứ tự và mã AC-DEMO-01 là quyết định thiết kế của đồ án; không phải chứng nhận đáp ứng toàn bộ CIS hay ATT&CK.

## 11. Cập nhật phạm vi và fixture — 2026-10-09

- Người dùng xác nhận giữ một công ty ở v0.1, có nhiều chi nhánh và consultant được mời; nhiều công ty để sau.
- Ghi mô hình web nội bộ qua VPN trong hồ sơ lab; các vùng mạng là thiết kế logic, chưa cấu hình sản phẩm/VM hay công bố lên Internet.
- Đã tạo 12 tài khoản giả lập, 8 vai trò, 7 tài sản logic và 6 hồ sơ khách hàng; tách quyền VN Digital Trust với CRM, có trạng thái pending/disabled/expired và phạm vi chi nhánh/bản ghi.
- Ban đầu đề xuất WebAuthn/FIDO2 và TOTP để đối chiếu; sau đó người dùng chọn mật khẩu + WebAuthn (mục 12). Chưa xác định khóa AWS của người dùng nằm trong phần cứng; baseline không thêm TOTP làm fallback.
- Định hướng ISO/IEC 27005 cho risk, ISO/IEC 27002 cho control và ATT&CK cho hành vi. Chưa kiểm tra toàn văn ISO, chưa ánh xạ điều khoản chi tiết và không tuyên bố chứng nhận.
- Trạng thái tại lần tạo fixture: bước 01 IN_PROGRESS; bước 02–06 NOT_STARTED. Lần bàn giao hoàn thành bước 01 được ghi tiếp tại mục 12.

## 12. Chốt mật khẩu + WebAuthn và bàn giao bước 01 — 2026-10-09

**Quyết định người dùng:** Dùng mật khẩu + WebAuthn cho đăng nhập CRM. AUTH-CRM-01 trong JSON ghi lựa chọn; trạng thái triển khai vẫn NOT_IMPLEMENTED. Control được đánh giá là AC-DEMO-01.

### Đối chiếu điều kiện hoàn thành bước 01

| Điều kiện | Đầu ra đã có |
| --- | --- |
| SME, hệ thống và phạm vi organization | Hồ sơ lab mục 1–2: ABC Trading, một công ty, hai chi nhánh và consultant được mời. |
| Tài sản, tài khoản, vai trò và dữ liệu | Hồ sơ lab mục 5–6 cùng JSON: 12 user, 8 role, 7 asset, 6 khách hàng giả lập; có owner và scope. |
| Ranh giới triển khai | Hồ sơ lab mục 3: LAN/VPN, HTTPS, các vùng logic, đường truy cập và tiền điều kiện đã vào VPN. |
| Scenario chính có điều kiện/sự kiện/hậu quả | Hồ sơ lab mục 7: SC-01 lạm dụng mật khẩu U102 để truy cập CRM, chưa có WebAuthn hoặc phiên hợp lệ. |
| Scenario ngoài initial access | Hồ sơ lab mục 7: SC-02 chuyển dữ liệu giả lập đến AST-RECEIVER trong lab, có nguồn/đích và giới hạn. |
| Phương thức MFA đầu tiên | Người dùng chốt mật khẩu + WebAuthn; hồ sơ lab mục 4 và AUTH-CRM-01 phản ánh cùng quyết định. |
| Giả định và điều chưa kiểm chứng | Hồ sơ lab mục 4, 7–9: chưa xác nhận thiết bị/CRM, chưa chạy lab, chưa có risk score/evidence hoặc mapping ISO đầy đủ. |

**Kiểm tra bàn giao:** đối chiếu tài liệu với JSON; JSON đọc được, tham chiếu user/role/branch/asset nhất quán, cấu hình xác thực là dữ liệu thiết kế và evidence vẫn rỗng. Đây là kiểm tra tài liệu/dữ liệu, không phải kiểm thử bảo mật.

**Kết luận:** bước 01 COMPLETE về phạm vi thiết kế. Bước 02–06 giữ NOT_STARTED; chỉ bước 02 được tiếp tục theo thứ tự.

### Đầu vào và việc cần làm ở bước 02

- Xác định rubric likelihood/impact, quy tắc có version và rationale; không suy điểm từ số technique hay việc test chạy thành công.
- Đặc tả tiêu chí/evidence cho mật khẩu + WebAuthn: người hợp lệ, chỉ có mật khẩu, chưa đăng ký, credential không hợp lệ/bị thu hồi, challenge hết hạn/dùng lại, xác minh người dùng, hủy xác thực và ranh giới origin/RP ID.
- Định nghĩa đăng ký/khôi phục đủ kiểm soát; người chỉ có mật khẩu bị lộ không được tự đăng ký khóa để vượt control. Chốt ngưỡng thời gian/số lần thử dựa trên tiêu chí thay vì đoán trước.
- Thay các ca OTP không còn phù hợp trong danh sách minh họa 20 tình huống. Các ca vòng đời tài khoản và quyền sau đăng nhập vẫn là đầu vào; không tự coi mọi ca đều kiểm tra MFA.
- Phân biệt thiếu evidence với control thất bại, giữ revision/snapshot và lý do kết luận.
- Loại authenticator cụ thể, sản phẩm CRM/identity provider, hostname/RP ID thực tế và thư viện thuộc bước 04–05; triển khai/kiểm chứng thuộc bước 06.

## 13. Bàn giao bước 02 — 2026-10-09 (lịch sử; đã mở lại tại mục 14)

**Tiếp nhận:** Chat bước 02 nhận bàn giao từ chat bước 01 ngày 2026-10-09. Bước 01 giữ COMPLETE. Trong lúc soạn các tài liệu dưới đây, bước 02 là bước duy nhất IN_PROGRESS; sau đối chiếu này, bước 02 COMPLETE về **thiết kế**. Bước 03–06 vẫn NOT_STARTED.

| Điều kiện hoàn thành bước 02 | Bằng chứng thiết kế |
| --- | --- |
| Nguồn tham khảo và giới hạn | [RM-01 v0.1](../risk-v0.1/risk-method-v0.1.md) giải thích vai trò ISO/IEC 27005/27002 và ATT&CK; [CE-01 v0.1](../../control-evidence-v0.1.md) dẫn W3C/OWASP/MITRE. Không tuyên bố ISO đưa ra ma trận nội bộ. |
| Rubric và quy tắc có version | RM-01 v0.1: thang L/I 1–5, UNKNOWN, ma trận, input bắt buộc, inherent/current, rationale, confidence và snapshot. |
| Ví dụ tính nhất quán | RM-01 v0.1 có ví dụ 3×2=6 MODERATE, 4×4=16 HIGH và ca current thiếu evidence → NEEDS_REVIEW. Đây là ví dụ giả định, không phải điểm thực nghiệm. |
| Bộ control nhỏ và evidence | CE-01 v0.1 có AC-DEMO-01 chi tiết, AC-DEMO-02/03 và EX-DEMO-01 ở mức catalog; C01–C08 xác định phạm vi, đăng nhập, registration/recovery, verification và evidence. |
| Thiếu evidence khác thất bại | CE-01 v0.1 định nghĩa INSUFFICIENT_EVIDENCE/EVIDENCE_GAP tách NOT_SATISFIED/CONTROL_GAP; test lỗi → INCONCLUSIVE. |
| UNKNOWN và override | RM-01 v0.1 giữ NEEDS_REVIEW; override lưu old/new, quyền, reason, actor/time, không che thiếu dữ liệu. CE-01 v0.1 giữ assessment/evidence revision bất biến. |
| Kỳ vọng test trước khi chạy | [TC-01 v0.1](../../control-test-cases-v0.1.md) có 24 ca với expected results, gồm challenge replay/expiry, origin/RP ID, UV, enrollment, recovery, vòng đời tài khoản và quyền riêng. Chưa chạy lab. |

**Kiểm tra tài liệu:** đối chiếu AUTH-CRM-01, SC-01/SC-02, U101–U108 và quyền/branch với fixture bước 01; kiểm tra liên kết tài liệu và các status. Không có account thật, evidence revision hay risk score thực nghiệm. Mã control và threshold risk là quyết định thiết kế, chưa kiểm tra toàn văn ISO hoặc nhu cầu thực tế của SME.

**Quyết định và giới hạn:** Giữ password + WebAuthn với UV required; không TOTP fallback/passwordless. Người chỉ có mật khẩu không tự đăng ký khóa; recovery cần xác minh/phê duyệt độc lập. Giá trị TTL, giới hạn thử, chính sách phiên, CRM/IdP, hostname/RP ID, loại authenticator và tính bảo vệ phần cứng chưa chốt/kiểm chứng. Bộ catalog ngoài AC-DEMO-01 chưa có tiêu chí chi tiết hay assessment; SC-02 chưa chạy. Ví dụ risk chỉ minh họa tính toán; nếu đánh giá current dựa vào control chưa có evidence thì NEEDS_REVIEW.

**Dự kiến bàn giao tại thời điểm 2026-10-09; hiệu lực chuyển bước đã tạm dừng tại mục 14:** Bước 03 — tinh chỉnh luồng assessment → gap → treatment → retest theo RM-01/CE-01/TC-01, gồm đường thiếu evidence, lỗi test, thiếu quyền và lịch sử. Không tự bắt đầu kiến trúc, chọn stack hoặc triển khai lab từ bàn giao này.

**Làm rõ sau bàn giao:** Theo câu hỏi của người dùng, RM-01 v0.1 mục 5 đã đối chiếu công thức risk score của IBM Security Verify Access. Điểm IBM đánh giá một yêu cầu đăng nhập qua device fingerprint để ra quyết định truy cập; RM-01 đánh giá scenario và hậu quả ở mức SME. Có thể bổ sung điểm IBM như tín hiệu riêng khi có dữ liệu/thiết bị và policy phù hợp, nhưng không dùng thay impact hoặc bỏ WebAuthn bắt buộc. Chưa chọn triển khai phương án mở rộng này.

## 14. Mở lại phương pháp risk nhiều yếu tố — 2026-10-10 (lịch sử; bản hiện hành ở mục 16)

**Yêu cầu người dùng:** sửa theo mô hình nhiều yếu tố, xem công thức và nhận link control/evidence, ca kiểm thử và kế hoạch. Chưa xác nhận công thức/trọng số cụ thể. Bước 01 COMPLETE; bước 02 IN_PROGRESS; bước 03–06 NOT_STARTED. Việc ghi COMPLETE ở mục 13 không còn là trạng thái hiện hành.

**Đầu ra:** [RM-01 v0.2](../risk-v0.2/risk-method-v0.2.md) và [fixture tính toán v0.2](../risk-v0.2/risk-method-fixtures-v0.2.json). Giữ v0.1 làm lịch sử; [CE-01](../../control-evidence-v0.1.md) và [TC-01](../../control-test-cases-v0.1.md) tiếp tục là tài liệu thiết kế control, không phải test report.

**Công thức đề xuất:** P=0.40E+0.60F; L=1+(P−1)×G/5; I=max(C,T,A,B); R=L×I. E là cơ hội, F là mức dễ thực hiện, G là mức yếu control; C/T/A/B là các chiều hậu quả. G điều chỉnh khả thi bằng phép nhân; impact lấy mức lớn nhất để không che hậu quả nghiêm trọng. UNKNOWN chặn tính điểm; control failure vẫn được giữ riêng. Các hệ số do dự án đề xuất, không gán cho ISO/NIST/IBM.

**Phạm vi mới được làm rõ:** CONDITIONAL theo tiền điều kiện SC-01/SC-02, không suy xác suất năm từ điểm lab. Dùng chung profile nhiều tactic, không cộng điểm tactic/chuỗi. Lưu yếu tố, rationale, evidence revision và version để hỗ trợ review/AI sau này; chưa triển khai AI.

**Kiểm tra đã thực hiện:** đối chiếu phép tính ví dụ/fixture, biên phân mức, input thiếu/ngoài thang, tính đơn điệu và miền 1–25. Đây là kiểm tra tính nhất quán quy tắc, không phải hiệu chuẩn trọng số hay kiểm chứng CRM. Fixture tính toán không chứa evidence thật và không thay lab-fixtures-v0.1.json.

**Còn thiếu trước khi đóng bước 02:** người dùng review công thức 40/60, cách G điều chỉnh và cách lấy max impact; kiểm tra thứ tự ưu tiên của các ví dụ có phù hợp mong muốn; thống nhất rubric/ngưỡng và ghi nhận chấp thuận hoặc sửa version. Chưa có ý kiến SME hay risk score thực nghiệm. TTL, chính sách phiên, enrollment/recovery chi tiết và môi trường vẫn phải chốt trước các test liên quan, như giới hạn CE-01/TC-01 đã ghi.

**Việc tiếp theo duy nhất:** xem xét RM-01 v0.2 ngay trong bước 02; chưa mở bước 03.

## 15. Sửa theo năm phản hồi — RM-01 v0.3 — 2026-10-10 (lịch sử; bản hiện hành ở mục 16)

**Tại lần cập nhật v0.3:** bước 02 IN_PROGRESS. [Phương pháp v0.3](../risk-v0.3/risk-method-v0.3.md), [fixture](../risk-v0.3/risk-method-fixtures-v0.3.json) và [review/độ nhạy](../risk-v0.3/risk-method-review-v0.3.md) thay v0.2 cho review; các bản cũ giữ lịch sử. Control/evidence CE-01 và ca kiểm thử control TC-01 tiếp tục là thiết kế chưa chạy lab.

**Điều đã sửa:** R chủ yếu so sánh trước/sau cùng scenario/tiền điều kiện; độ khả dĩ tiền điều kiện có nhãn/horizon riêng, không nhân vào R. Thêm cổng I=1 LOW và I=2 tối đa MODERATE; giữ raw score. F giả định bỏ đúng control đang chấm ở G; G tách coverage và sức cản từng đường, mapping ControlAssessment chỉ là gợi ý để reviewer xác nhận. UNKNOWN cho score_range/level_range khi context đủ; trường hợp impact max=5 xác định được vẫn giữ review và gap. Hiển thị R xấp xỉ, không ngụ ý độ chính xác đo lường. Template E/F và lý do/source dùng lại giảm công nhập SME.

**Nguồn:** đã kiểm tra NIST SP 800-30 Rev.1 final Task 2-4 và Phụ lục G: khởi phát và hậu quả sau khởi phát được phân biệt rồi tổ hợp; không coi công thức 40/60/G của đồ án là NIST. Đã đọc abstract Cox (2008) trên PubMed, ghi rõ chưa rà soát toàn văn; thêm giới hạn thứ bậc, thứ hạng và max impact.

**Kiểm tra hoàn tất:** 16 fixture, cổng impact và biên raw; cận UNKNOWN đối chiếu tổ hợp hợp lệ; độ nhạy ±1 mọi yếu tố trên toàn fixture với boundary/UNKNOWN/context-invalid ghi rõ. Báo cáo cho thấy MF-03 nhạy theo G±1 (±2.24) và C±1 (±3.24), lớn hơn trọng số ±10 điểm phần trăm (±0.64). Đây chỉ là kiểm tra phương pháp, chưa là hiệu chuẩn SME.

**Việc còn thiếu:** cặp MF-03/MF-04 PENDING_USER_REVIEW về ưu tiên khi hậu quả có độ rộng khác nhau; chính sách cổng và hiển thị cũng cần người dùng xem. Đã chuẩn bị [phiếu G-A](../risk-v0.3/risk-g-rating-a-v0.3.md) và [phiếu G-B](../risk-v0.3/risk-g-rating-b-v0.3.md) với 6 case tổng hợp; **NOT_RUN**, chưa có người chấm độc lập hoặc số liệu độ lệch. Cần thu điểm thật, báo mẫu số/UNKNOWN, phân xử lệch lớn hoặc khác nhãn và giữ lịch sử. Không đánh dấu COMPLETE chỉ vì đã có phiếu trống và kiểm tra số học.

**Việc tiếp theo:** review v0.3 trong bước 02, thực hiện/chốt phạm vi kiểm tra người chấm; chưa chuyển bước 03. Chưa có evidence lab hoặc risk score thực nghiệm; không triển khai AI, architecture, stack hay lab ở lần cập nhật này.

**Chỉnh thuật ngữ trong v0.3 — 2026-10-10:** Theo yêu cầu người dùng, dùng Integrity (I_integrity) — tính toàn vẹn thuộc CIA; Impact tổng hợp ký hiệu I_total. Đồng bộ công thức, ví dụ UNKNOWN, báo cáo độ nhạy và fixture v0.3; giữ điểm số/hệ số/ngưỡng. Mục 5 phân biệt rõ B là hậu quả nghiệp vụ bổ sung, không thuộc CIA. Các phiên bản lịch sử giữ nguyên.

## 16. Thống nhất UNKNOWN và tính chính xác — RM-01 v0.4 — 2026-10-10

**Hiện hành:** bước 01 COMPLETE; bước 02 IN_PROGRESS; bước 03–06 NOT_STARTED. Người dùng đã đồng ý áp dụng các sửa đổi sau khi review phản biện. [RM-01 v0.4](risk-method-v0.4.md), [fixture v0.4](../../verification/risk-method-fixtures-v0.4.json), [báo cáo kiểm tra v0.4](risk-method-review-v0.4.md) thay v0.3 cho công việc tiếp theo. Giữ các phiên bản cũ làm lịch sử; trạng thái phương pháp vẫn DRAFT_REVIEW.

**Quyết định đã áp dụng:** giữ P=0.40E+0.60F; L=1+(P−1)G/5; I_total=max(C,I_integrity,A,B); R=L×I_total. Dùng số nguyên R25=I_total×[25+(2E+3F−5)G] làm căn cứ lưu/so sánh/phân mức. Giá trị và cận của từng yếu tố đầu vào là số nguyên 1–5. Hệ số, cổng và ngưỡng không đổi, chưa hiệu chuẩn. Chấp nhận hệ quả G=1 ⇒ R≤9 như chỉ số rủi ro còn lại có điều kiện, có mức sàn dương; G=1 chỉ xác minh trong scope/thời điểm đã ghi. CRITICAL cần I_total≥4; P=1 khiến điểm không phụ thuộc G. Các hệ quả này không tự chấp nhận risk hoặc xóa gap.

**UNKNOWN thống nhất:** tính max của các cận thành phần cho cả G và impact, không luôn đặt cận trên 5. Aggregate có hai cận bằng nhau thì đã xác định, đặc biệt một đường bypass g=5 cộng đường UNKNOWN vẫn cho G=5. Hai cận R25 bằng nhau thì điền cả điểm và nhãn, kể cả MF-12/MF-13; còn UNKNOWN/việc xác nhận thì NEEDS_REVIEW. Thiếu context hoặc input/miền không hợp lệ không có điểm/range. Template chưa xác nhận không biến thành evidence. Gaps và control failures vẫn giữ riêng.

**Hiển thị:** cắt điểm xuống một chữ số thập phân; range làm tròn ra ngoài; nhãn từ R25 chính xác và cổng impact. Giữ CIA gồm C/I_integrity/A và B nghiệp vụ bổ sung, không đổi nghĩa Integrity. MF-03 hiển thị 12.9 HIGH; MF-04 12.3 HIGH; thứ tự ưu tiên vẫn cần lý do của reviewer.

**Kiểm tra:** kết quả kiểm tra tự động chi tiết ghi trong [báo cáo v0.4](risk-method-review-v0.4.md): đối chiếu công thức nguyên, các bất biến/biên/cận, fixture hồi quy và bổ sung, độ nhạy ±1 từng yếu tố. Đây là kiểm tra số học và quy tắc, chưa là hiệu chuẩn SME hoặc kiểm thử CRM. [CE-01](../../control-evidence-v0.1.md) và [TC-01](../../control-test-cases-v0.1.md) giữ nguyên tiêu chí; 24 ca control chưa chạy.

**Còn thiếu sau review ngày 2026-10-11:** [phiếu G-A v0.4](../../review-forms/risk-g-rating-a-v0.4.md) và [phiếu G-B v0.4](../../review-forms/risk-g-rating-b-v0.4.md) vẫn trống, kiểm tra hai người NOT_RUN. Cần thực hiện hoặc chốt phạm vi kiểm tra người chấm, không coi phiếu trống là kết quả. Chưa có evidence lab/risk score thực nghiệm. Các giá trị TTL, chính sách phiên và môi trường vẫn TO_SET_BEFORE_LAB theo CE-01/TC-01.

**Việc tiếp theo:** tiếp tục review các mục còn thiếu trong bước 02. Sửa đổi v0.4 đã được cho phép, không yêu cầu phê duyệt lại các thay đổi này; chưa chuyển bước 03, kiến trúc, công nghệ hoặc triển khai.

### Review cặp MF-03/MF-04 theo yêu cầu người dùng — 2026-10-11

Người dùng yêu cầu trợ lý tự đánh giá hai ca. **DESIGN_REVIEW_COMPLETED**, người review: trợ lý Codex; không yêu cầu người dùng tự chấm fixture. Điểm giữ MF-03=12.96 HIGH và MF-04=12.32 HIGH. Cả hai cùng nhóm HIGH. Đề xuất MF-04 trước trong ví dụ khi giả định độ khả dĩ tiền điều kiện tương đương và reviewer ưu tiên hậu quả rộng hơn, do vector (4,4,3,4) không thấp hơn (4,1,1,3) ở mọi chiều. E/F khác nhau nên đây là nhận xét có điều kiện, không là thứ tự bắt buộc từ công thức. Độ khả dĩ thực tế vẫn UNKNOWN, ưu tiên thực tế NOT_DETERMINED; không ghi thành phê duyệt của SME.

Đã cập nhật RM-01 v0.4 mục 5 và 9, báo cáo review mục 4–5 và README. Công thức, ngưỡng, fixture số học và phiếu G-A/G-B không đổi. Kiểm tra đồng bộ bản đọc và bảo toàn fixture; không cần chạy lại phép tính vì thay đổi chỉ là kết luận review. Bước 02 vẫn IN_PROGRESS; phần cần hoàn tất/chốt phạm vi còn lại là kiểm tra G độc lập. Review của trợ lý không được tính thành hai người chấm độc lập, không tự mở bước 03.
