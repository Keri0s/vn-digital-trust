# VN Digital Trust — Kế hoạch thực hiện v0.1

**Cập nhật:** 2026-10-23

**Trạng thái:** Bước 01 COMPLETE về phạm vi thiết kế; bước 02 COMPLETE — DESIGN_FROZEN, RM-01 v0.4-r3 ngày 2026-10-12, công thức/profile vẫn v0.4. Bước 03 COMPLETE về thiết kế luồng v0.2-r1; bước 04 COMPLETE về thiết kế kiến trúc v0.1 ngày 2026-10-18 (mục 25); bước 05 COMPLETE về thiết kế v0.1 ngày 2026-10-21 (mục 28); bước 06 IN_PROGRESS theo yêu cầu ngày 2026-10-23 (mục 29). Chưa triển khai hoặc kiểm chứng lab. Bàn giao bước 03 → 04 ở mục 24; kết quả bước 04 ở mục 25; bàn giao bước 04 → 05 và yêu cầu chờ của người dùng ở mục 26. Kiểm chứng hai người chấm G được theo dõi tại VALID-G-01, bước 06: NOT_RUN, độ tin cậy giữa người chấm chưa được kiểm chứng.

## 1. Nơi theo dõi tiến độ chung

Bản làm việc chính: D:/Projects/vn-digital-trust/docs/planning/execution-plan-v0.1.md.

Mỗi chat đọc file này và [docs/planning/README.md](README.md) trước khi tiếp tục. [docs/README.md](../README.md) là chỉ mục toàn bộ tài liệu dự án; đây là tệp khác, dẫn vào chỉ mục planning cho công việc sáu bước. Mỗi lần bàn giao ghi: đầu ra đã có, kiểm tra đã thực hiện, quyết định, giả định chưa xác minh và việc tiếp theo. Các chat có lịch sử riêng; không dựa vào việc mọi chat tự nhớ toàn bộ trao đổi.

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
| 02 — Phương pháp risk và control/evidence mẫu | COMPLETE — DESIGN_FROZEN | RM-01 v0.4-r3; CE-01/TC-01 v0.1; fixture và bộ kiểm tra tái lập | Có nguồn, giới hạn, rubric/version, UNKNOWN/override, phân biệt thiếu evidence/control thất bại và kỳ vọng trước test. Đối chiếu đóng thiết kế ở mục 19; kiểm chứng chấm G chuyển sang VALID-G-01 bước 06, chưa được coi là đã đạt. |
| 03 — Luồng xử lý chi tiết | COMPLETE — thiết kế v0.2-r1, mục 22 | Use case được tinh chỉnh, activity/sequence cho assessment → gap → treatment → retest | Truy vết được từ yêu cầu đến luồng; có đường thành công, thiếu evidence, lỗi nhập, thiếu quyền và retest giữ lịch sử. Sơ đồ được render/đọc kiểm tra. |
| 04 — Kiến trúc v0.1 | COMPLETE — thiết kế, mục 25 | Thành phần, luồng dữ liệu, deployment, lưu evidence, auth/RBAC; ranh giới lab | Mỗi thành phần có trách nhiệm rõ; mô tả nguồn evidence, kiểm soát quyền, snapshot/version và lỗi; khả thi trong tài nguyên đồ án. Đối chiếu ở mục 25. |
| 05 — Công nghệ, database và API | COMPLETE — thiết kế v0.1, mục 28 | Quyết định công nghệ có lý do; ERD; API contract; thiết kế lưu file và version | Thiết kế đáp ứng luồng/kiến trúc; constraints, quyền, trạng thái và lỗi có chỗ xử lý; không chọn công nghệ chỉ vì phổ biến. |
| 06 — Prototype và kiểm chứng | IN_PROGRESS — mục 29 | Luồng chạy được inventory → scenario → evaluation → control/evidence → gap → treatment → retest/report; bộ kiểm thử và báo cáo lab | Chứng minh RBAC, tính lặp lại, thiếu evidence khác failed control, lỗi test không bị kết luận sai, lịch sử bất biến; thực hiện VALID-G-01 hoặc ghi quyết định phạm vi chưa kiểm chứng có actor/thời điểm/lý do; không gọi rubric G đáng tin cậy khi thiếu kết quả. |

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

**Bước 01 — đã hoàn tất thiết kế:** ghi mục đích và giới hạn mô phỏng; chọn câu chuyện cần kiểm chứng. Chưa cài/chạy công cụ.

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

Nhóm thanh bên: **VN Digital Trust · 6 bước**. Chat bước 02 hoàn tất bàn giao sang chat bước 03 ngày 2026-10-13 theo yêu cầu người dùng; bước 01 và bước 02 đã hoàn tất thiết kế. Mỗi bước có chat riêng theo chỉ mục mục 9; đọc trạng thái công việc hiện hành tại mục 24; bàn giao bước 02 ở mục 20. Đây là tổ chức giao diện, không có nghĩa các chat tự chạy hoặc dùng checkout riêng. Thông tin tạo các chat local projectless là lịch sử tổ chức ban đầu; không suy từ đó trạng thái giao diện hiện tại.

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

Hồ sơ [phạm vi lab và dữ liệu giả lập](lab-scope-and-fixtures-v0.1.md) đã mô tả ABC Trading/CRM, hai chi nhánh, topology logic LAN/VPN, assets, tài khoản/role, dữ liệu, SC-01 và SC-02. [JSON fixture](lab-fixtures-v0.1.json) là dữ liệu thiết kế, chưa tạo tài khoản thật. Người dùng đã chọn mật khẩu + WebAuthn; đầu vào này đã được bước 02 tiếp nhận và xử lý tại mục 13.

Đã chọn nhóm control quản lý quyền truy cập để làm trước; control đầu tiên là yêu cầu MFA cho đăng nhập tương tác của tài khoản người dùng CRM trong phạm vi demo (xem mục 10). Risk matrix v0.1 là bản lịch sử tại mục 13; phương pháp v0.4-r3 đã đóng băng thiết kế tại mục 19. Tiêu chí control và test ID được giữ làm đầu vào thiết kế. Topology triển khai chi tiết, các control mở rộng, công nghệ, DB/API chưa chốt. Chưa chạy Atomic hoặc Caldera; chưa có xác nhận nhu cầu từ SME/consultant. Những hạn chế này phải được giữ trong báo cáo đồ án.

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

**Trạng thái lịch sử tại quyết định ngày 2026-10-06:** Bước 01 IN_PROGRESS; bước 02–06 NOT_STARTED. Trạng thái hiện hành xem mục 19.

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
| Nguồn tham khảo và giới hạn | [RM-01 v0.1](history/risk-v0.1/risk-method-v0.1.md) giải thích vai trò ISO/IEC 27005/27002 và ATT&CK; [CE-01 v0.1](control-evidence-v0.1.md) dẫn W3C/OWASP/MITRE. Không tuyên bố ISO đưa ra ma trận nội bộ. |
| Rubric và quy tắc có version | RM-01 v0.1: thang L/I 1–5, UNKNOWN, ma trận, input bắt buộc, inherent/current, rationale, confidence và snapshot. |
| Ví dụ tính nhất quán | RM-01 v0.1 có ví dụ 3×2=6 MODERATE, 4×4=16 HIGH và ca current thiếu evidence → NEEDS_REVIEW. Đây là ví dụ giả định, không phải điểm thực nghiệm. |
| Bộ control nhỏ và evidence | CE-01 v0.1 có AC-DEMO-01 chi tiết, AC-DEMO-02/03 và EX-DEMO-01 ở mức catalog; C01–C08 xác định phạm vi, đăng nhập, registration/recovery, verification và evidence. |
| Thiếu evidence khác thất bại | CE-01 v0.1 định nghĩa INSUFFICIENT_EVIDENCE/EVIDENCE_GAP tách NOT_SATISFIED/CONTROL_GAP; test lỗi → INCONCLUSIVE. |
| UNKNOWN và override | RM-01 v0.1 giữ NEEDS_REVIEW; override lưu old/new, quyền, reason, actor/time, không che thiếu dữ liệu. CE-01 v0.1 giữ assessment/evidence revision bất biến. |
| Kỳ vọng test trước khi chạy | [TC-01 v0.1](control-test-cases-v0.1.md) có 24 ca với expected results, gồm challenge replay/expiry, origin/RP ID, UV, enrollment, recovery, vòng đời tài khoản và quyền riêng. Chưa chạy lab. |

**Kiểm tra tài liệu:** đối chiếu AUTH-CRM-01, SC-01/SC-02, U101–U108 và quyền/branch với fixture bước 01; kiểm tra liên kết tài liệu và các status. Không có account thật, evidence revision hay risk score thực nghiệm. Mã control và threshold risk là quyết định thiết kế, chưa kiểm tra toàn văn ISO hoặc nhu cầu thực tế của SME.

**Quyết định và giới hạn:** Giữ password + WebAuthn với UV required; không TOTP fallback/passwordless. Người chỉ có mật khẩu không tự đăng ký khóa; recovery cần xác minh/phê duyệt độc lập. Giá trị TTL, giới hạn thử, chính sách phiên, CRM/IdP, hostname/RP ID, loại authenticator và tính bảo vệ phần cứng chưa chốt/kiểm chứng. Bộ catalog ngoài AC-DEMO-01 chưa có tiêu chí chi tiết hay assessment; SC-02 chưa chạy. Ví dụ risk chỉ minh họa tính toán; nếu đánh giá current dựa vào control chưa có evidence thì NEEDS_REVIEW.

**Dự kiến bàn giao tại thời điểm 2026-10-09; hiệu lực chuyển bước đã tạm dừng tại mục 14:** Bước 03 — tinh chỉnh luồng assessment → gap → treatment → retest theo RM-01/CE-01/TC-01, gồm đường thiếu evidence, lỗi test, thiếu quyền và lịch sử. Không tự bắt đầu kiến trúc, chọn stack hoặc triển khai lab từ bàn giao này.

**Làm rõ sau bàn giao:** Theo câu hỏi của người dùng, RM-01 v0.1 mục 5 đã đối chiếu công thức risk score của IBM Security Verify Access. Điểm IBM đánh giá một yêu cầu đăng nhập qua device fingerprint để ra quyết định truy cập; RM-01 đánh giá scenario và hậu quả ở mức SME. Có thể bổ sung điểm IBM như tín hiệu riêng khi có dữ liệu/thiết bị và policy phù hợp, nhưng không dùng thay impact hoặc bỏ WebAuthn bắt buộc. Chưa chọn triển khai phương án mở rộng này.

## 14. Mở lại phương pháp risk nhiều yếu tố — 2026-10-10 (lịch sử; bản hiện hành ở mục 19)

**Yêu cầu người dùng:** sửa theo mô hình nhiều yếu tố, xem công thức và nhận link control/evidence, ca kiểm thử và kế hoạch. Chưa xác nhận công thức/trọng số cụ thể. Bước 01 COMPLETE; bước 02 IN_PROGRESS; bước 03–06 NOT_STARTED. Việc ghi COMPLETE ở mục 13 không còn là trạng thái hiện hành.

**Đầu ra:** [RM-01 v0.2](history/risk-v0.2/risk-method-v0.2.md) và [fixture tính toán v0.2](history/risk-v0.2/risk-method-fixtures-v0.2.json). Giữ v0.1 làm lịch sử; [CE-01](control-evidence-v0.1.md) và [TC-01](control-test-cases-v0.1.md) tiếp tục là tài liệu thiết kế control, không phải test report.

**Công thức đề xuất:** P=0.40E+0.60F; L=1+(P−1)×G/5; I=max(C,T,A,B); R=L×I. E là cơ hội, F là mức dễ thực hiện, G là mức yếu control; C/T/A/B là các chiều hậu quả. G điều chỉnh khả thi bằng phép nhân; impact lấy mức lớn nhất để không che hậu quả nghiêm trọng. UNKNOWN chặn tính điểm; control failure vẫn được giữ riêng. Các hệ số do dự án đề xuất, không gán cho ISO/NIST/IBM.

**Phạm vi mới được làm rõ:** CONDITIONAL theo tiền điều kiện SC-01/SC-02, không suy xác suất năm từ điểm lab. Dùng chung profile nhiều tactic, không cộng điểm tactic/chuỗi. Lưu yếu tố, rationale, evidence revision và version để hỗ trợ review/AI sau này; chưa triển khai AI.

**Kiểm tra đã thực hiện:** đối chiếu phép tính ví dụ/fixture, biên phân mức, input thiếu/ngoài thang, tính đơn điệu và miền 1–25. Đây là kiểm tra tính nhất quán quy tắc, không phải hiệu chuẩn trọng số hay kiểm chứng CRM. Fixture tính toán không chứa evidence thật và không thay lab-fixtures-v0.1.json.

**Còn thiếu trước khi đóng bước 02:** người dùng review công thức 40/60, cách G điều chỉnh và cách lấy max impact; kiểm tra thứ tự ưu tiên của các ví dụ có phù hợp mong muốn; thống nhất rubric/ngưỡng và ghi nhận chấp thuận hoặc sửa version. Chưa có ý kiến SME hay risk score thực nghiệm. TTL, chính sách phiên, enrollment/recovery chi tiết và môi trường vẫn phải chốt trước các test liên quan, như giới hạn CE-01/TC-01 đã ghi.

**Việc tiếp theo duy nhất:** xem xét RM-01 v0.2 ngay trong bước 02; chưa mở bước 03.

## 15. Sửa theo năm phản hồi — RM-01 v0.3 — 2026-10-10 (lịch sử; bản hiện hành ở mục 19)

**Tại lần cập nhật v0.3:** bước 02 IN_PROGRESS. [Phương pháp v0.3](history/risk-v0.3/risk-method-v0.3.md), [fixture](history/risk-v0.3/risk-method-fixtures-v0.3.json) và [review/độ nhạy](history/risk-v0.3/risk-method-review-v0.3.md) thay v0.2 cho review; các bản cũ giữ lịch sử. Control/evidence CE-01 và ca kiểm thử control TC-01 tiếp tục là thiết kế chưa chạy lab.

**Điều đã sửa:** R chủ yếu so sánh trước/sau cùng scenario/tiền điều kiện; độ khả dĩ tiền điều kiện có nhãn/horizon riêng, không nhân vào R. Thêm cổng I=1 LOW và I=2 tối đa MODERATE; giữ raw score. F giả định bỏ đúng control đang chấm ở G; G tách coverage và sức cản từng đường, mapping ControlAssessment chỉ là gợi ý để reviewer xác nhận. UNKNOWN cho score_range/level_range khi context đủ; trường hợp impact max=5 xác định được vẫn giữ review và gap. Hiển thị R xấp xỉ, không ngụ ý độ chính xác đo lường. Template E/F và lý do/source dùng lại giảm công nhập SME.

**Nguồn:** đã kiểm tra NIST SP 800-30 Rev.1 final Task 2-4 và Phụ lục G: khởi phát và hậu quả sau khởi phát được phân biệt rồi tổ hợp; không coi công thức 40/60/G của đồ án là NIST. Đã đọc abstract Cox (2008) trên PubMed, ghi rõ chưa rà soát toàn văn; thêm giới hạn thứ bậc, thứ hạng và max impact.

**Kiểm tra hoàn tất:** 16 fixture, cổng impact và biên raw; cận UNKNOWN đối chiếu tổ hợp hợp lệ; độ nhạy ±1 mọi yếu tố trên toàn fixture với boundary/UNKNOWN/context-invalid ghi rõ. Báo cáo cho thấy MF-03 nhạy theo G±1 (±2.24) và C±1 (±3.24), lớn hơn trọng số ±10 điểm phần trăm (±0.64). Đây chỉ là kiểm tra phương pháp, chưa là hiệu chuẩn SME.

**Việc còn thiếu:** cặp MF-03/MF-04 PENDING_USER_REVIEW về ưu tiên khi hậu quả có độ rộng khác nhau; chính sách cổng và hiển thị cũng cần người dùng xem. Đã chuẩn bị [phiếu G-A](history/risk-v0.3/risk-g-rating-a-v0.3.md) và [phiếu G-B](history/risk-v0.3/risk-g-rating-b-v0.3.md) với 6 case tổng hợp; **NOT_RUN**, chưa có người chấm độc lập hoặc số liệu độ lệch. Cần thu điểm thật, báo mẫu số/UNKNOWN, phân xử lệch lớn hoặc khác nhãn và giữ lịch sử. Không đánh dấu COMPLETE chỉ vì đã có phiếu trống và kiểm tra số học.

**Việc tiếp theo:** review v0.3 trong bước 02, thực hiện/chốt phạm vi kiểm tra người chấm; chưa chuyển bước 03. Chưa có evidence lab hoặc risk score thực nghiệm; không triển khai AI, architecture, stack hay lab ở lần cập nhật này.

**Chỉnh thuật ngữ trong v0.3 — 2026-10-10:** Theo yêu cầu người dùng, dùng Integrity (I_integrity) — tính toàn vẹn thuộc CIA; Impact tổng hợp ký hiệu I_total. Đồng bộ công thức, ví dụ UNKNOWN, báo cáo độ nhạy và fixture v0.3; giữ điểm số/hệ số/ngưỡng. Mục 5 phân biệt rõ B là hậu quả nghiệp vụ bổ sung, không thuộc CIA. Các phiên bản lịch sử giữ nguyên.

## 16. Thống nhất UNKNOWN và tính chính xác — RM-01 v0.4 — 2026-10-10 (lịch sử; bản hiện hành ở mục 19)

**Tại lần cập nhật v0.4 ban đầu:** bước 01 COMPLETE; bước 02 IN_PROGRESS; bước 03–06 NOT_STARTED. Người dùng đã đồng ý áp dụng các sửa đổi sau khi review phản biện. [RM-01 v0.4](history/risk-v0.4-before-r2/risk-method-v0.4.md), [fixture v0.4](verification/risk-method-fixtures-v0.4.json), [báo cáo kiểm tra v0.4](history/risk-v0.4-before-r2/risk-method-review-v0.4.md) thay v0.3 cho công việc tiếp theo. Giữ các phiên bản cũ làm lịch sử; trạng thái phương pháp vẫn DRAFT_REVIEW.

**Quyết định đã áp dụng:** giữ P=0.40E+0.60F; L=1+(P−1)G/5; I_total=max(C,I_integrity,A,B); R=L×I_total. Dùng số nguyên R25=I_total×[25+(2E+3F−5)G] làm căn cứ lưu/so sánh/phân mức. Giá trị và cận của từng yếu tố đầu vào là số nguyên 1–5. Hệ số, cổng và ngưỡng không đổi, chưa hiệu chuẩn. Chấp nhận hệ quả G=1 ⇒ R≤9 như chỉ số rủi ro còn lại có điều kiện, có mức sàn dương; G=1 chỉ xác minh trong scope/thời điểm đã ghi. CRITICAL cần I_total≥4; P=1 khiến điểm không phụ thuộc G. Các hệ quả này không tự chấp nhận risk hoặc xóa gap.

**UNKNOWN thống nhất:** tính max của các cận thành phần cho cả G và impact, không luôn đặt cận trên 5. Aggregate có hai cận bằng nhau thì đã xác định, đặc biệt một đường bypass g=5 cộng đường UNKNOWN vẫn cho G=5. Hai cận R25 bằng nhau thì điền cả điểm và nhãn, kể cả MF-12/MF-13; còn UNKNOWN/việc xác nhận thì NEEDS_REVIEW. Thiếu context hoặc input/miền không hợp lệ không có điểm/range. Template chưa xác nhận không biến thành evidence. Gaps và control failures vẫn giữ riêng.

**Hiển thị:** cắt điểm xuống một chữ số thập phân; range làm tròn ra ngoài; nhãn từ R25 chính xác và cổng impact. Giữ CIA gồm C/I_integrity/A và B nghiệp vụ bổ sung, không đổi nghĩa Integrity. MF-03 hiển thị 12.9 HIGH; MF-04 12.3 HIGH; thứ tự ưu tiên vẫn cần lý do của reviewer.

**Kiểm tra:** kết quả kiểm tra tự động chi tiết ghi trong [báo cáo v0.4](history/risk-v0.4-before-r2/risk-method-review-v0.4.md): đối chiếu công thức nguyên, các bất biến/biên/cận, fixture hồi quy và bổ sung, độ nhạy ±1 từng yếu tố. Đây là kiểm tra số học và quy tắc, chưa là hiệu chuẩn SME hoặc kiểm thử CRM. [CE-01](control-evidence-v0.1.md) và [TC-01](control-test-cases-v0.1.md) giữ nguyên tiêu chí; 24 ca control chưa chạy.

**Còn thiếu sau review ngày 2026-10-11:** [phiếu G-A v0.4](review-forms/risk-g-rating-a-v0.4.md) và [phiếu G-B v0.4](review-forms/risk-g-rating-b-v0.4.md) vẫn trống, kiểm tra hai người NOT_RUN. Cần thực hiện hoặc chốt phạm vi kiểm tra người chấm, không coi phiếu trống là kết quả. Chưa có evidence lab/risk score thực nghiệm. Các giá trị TTL, chính sách phiên và môi trường vẫn TO_SET_BEFORE_LAB theo CE-01/TC-01.

**Việc tiếp theo:** tiếp tục review các mục còn thiếu trong bước 02. Sửa đổi v0.4 đã được cho phép, không yêu cầu phê duyệt lại các thay đổi này; chưa chuyển bước 03, kiến trúc, công nghệ hoặc triển khai.

### Review cặp MF-03/MF-04 theo yêu cầu người dùng — 2026-10-11 [SUPERSEDED bởi mục 17]

**Đoạn dưới giữ nguyên như lịch sử.** Kết luận hiện hành là NOT_RANKED, loại REVIEWER_DETERMINATION của trợ lý, không phải phê duyệt của người dùng/SME; xem báo cáo review mục 4 và mục 19 của kế hoạch.

Người dùng yêu cầu trợ lý tự đánh giá hai ca. **DESIGN_REVIEW_COMPLETED**, người review: trợ lý Codex; không yêu cầu người dùng tự chấm fixture. Điểm giữ MF-03=12.96 HIGH và MF-04=12.32 HIGH. Cả hai cùng nhóm HIGH. Đề xuất MF-04 trước trong ví dụ khi giả định độ khả dĩ tiền điều kiện tương đương và reviewer ưu tiên hậu quả rộng hơn, do vector (4,4,3,4) không thấp hơn (4,1,1,3) ở mọi chiều. E/F khác nhau nên đây là nhận xét có điều kiện, không là thứ tự bắt buộc từ công thức. Độ khả dĩ thực tế vẫn UNKNOWN, ưu tiên thực tế NOT_DETERMINED; không ghi thành phê duyệt của SME.

Đã cập nhật RM-01 v0.4 mục 5 và 9, báo cáo review mục 4–5 và README. Công thức, ngưỡng, fixture số học và phiếu G-A/G-B không đổi. Kiểm tra đồng bộ bản đọc và bảo toàn fixture; không cần chạy lại phép tính vì thay đổi chỉ là kết luận review. Bước 02 vẫn IN_PROGRESS; phần cần hoàn tất/chốt phạm vi còn lại là kiểm tra G độc lập. Review của trợ lý không được tính thành hai người chấm độc lập, không tự mở bước 03.

## 17. Bổ sung tiến độ impact, tính tái lập và đính chính review — 2026-10-11 (lịch sử; hiện hành ở mục 19)

**Tại thời điểm r2 ngày 2026-10-11:** bước 02 IN_PROGRESS; bước 01 COMPLETE, bước 03–06 NOT_STARTED. [RM-01 v0.4-r2 — snapshot trong gói lịch sử](history/risk-v0.4-r2.zip) giữ profile/công thức R25, trọng số, cổng và ngưỡng v0.4; thêm `IMPACT-PROGRESS-v0.1` cho theo dõi hậu quả và ghi revision tài liệu. Chưa kết thúc bước 02 từ nhận xét của tác giả.

**Đã sửa:** cùng loại CURRENT/INHERENT khi so trước/sau; không cộng scenario/tactic, ATT&CK chỉ metadata; confidence không nhân R và bất đồng giữ NEEDS_REVIEW. Các điều này bị thiếu khi biên tập bản trước, không có quyết định bãi bỏ. Thêm tiến độ từng chiều impact, trạng thái cải thiện/xấu đi/hỗn hợp/không đổi/chưa đủ/không so sánh được, với snapshot và evidence. Chênh lệch R không thay tiến độ hậu quả hoặc tiến độ gap; không suy quan hệ nhân quả với treatment nếu chưa có evidence liên hệ.

**Đính chính cặp minh họa:** đưa nhận xét cụ thể ra khỏi phương pháp. [Báo cáo review mục 4](verification/risk-method-review-v0.4.md) ghi `priority_decision=NOT_RANKED`, người review là trợ lý Codex, vì độ khả dĩ tiền điều kiện UNKNOWN và thứ tự R đảo khi thay trọng số chưa hiệu chuẩn. Đề xuất ưu tiên MF-04 có điều kiện tại mục 16 đã được thay thế; không phải quyết định hiện hành hoặc phê duyệt của SME. Cả hai vẫn HIGH theo profile.

**Tái lập:** công bố [fixture chính](verification/risk-method-fixtures-v0.4.json), [fixture bổ sung](verification/impact-progress-fixtures-v0.1.json), [script chỉ đọc](verification/verify-risk-v0.4.py), [hướng dẫn chạy](verification/README.md), [kết quả kiểm tra](verification/verification-results-v0.4.json), [phiếu A](review-forms/risk-g-rating-a-v0.4.md) và [phiếu B](review-forms/risk-g-rating-b-v0.4.md). Script độc lập không sửa expected hoặc phụ thuộc đường dẫn máy tác giả; kiểm tra số học không phải evidence CRM hoặc kiểm tra hai người chấm. Kết quả/counts chi tiết trong báo cáo và JSON lần chạy.

**Kiểm tra bổ sung:** cổng impact đổi nhãn đúng hai bộ E/F/G/I_total; hộp co điểm xác định E/F/I_total; bảng trọng số hai ca; tiến độ MF-04 dù R giữ nguyên; range [3.72,4.96] hiển thị [3.7,5.0] LOW–LOW. NIST đã đối chiếu bản PDF: Table G-2/G-4/G-5 đều ở trang in G-2, PDF trang 82.

**Còn thiếu:** review bản bổ sung r2; thực hiện hoặc chốt phạm vi kiểm tra người chấm G. A/B vẫn trống và NOT_RUN, chưa có độ lệch/đồng thuận. Các giả định cần evidence SME/lab, hiệu chuẩn, TTL/session và môi trường vẫn giữ đúng trạng thái; không suy đã triển khai từ fixture. Chưa chuyển bước 03.

## 18. Chuẩn hóa thư mục planning — 2026-10-11

Theo yêu cầu người dùng, phân biệt bản đang sử dụng với bản đã thay thế. [README của planning](README.md) là điểm bắt đầu, có thứ tự đọc và tóm tắt thay đổi. Cấp ngoài giữ kế hoạch, scope/dữ liệu lab, phương pháp risk hiện hành, control/evidence và test case. Bộ kiểm tra được gom vào [verification](verification/README.md); phiếu G v0.4 ở [review-forms](review-forms/risk-g-rating-a-v0.4.md); v0.1/v0.2/v0.3 đã thay thế và snapshot trước r2 ở [history](history/README.md).

Giữ đủ 26 tệp cũ, chuyển 16 tệp vào đúng nhóm và thêm 2 chỉ mục; không bỏ quyết định lịch sử. Sửa liên kết tương đối, gồm đường dẫn trong snapshot README vốn xuất phát từ docs/. Mục 16 trỏ đúng snapshot trước r2 khi dẫn phương pháp/báo cáo cũ. Giữ nguyên bytes của script, fixture JSON và kết quả đã lưu; chạy verifier sau di chuyển để xác nhận bộ kiểm tra còn tái lập được. Bước 02 vẫn IN_PROGRESS; việc tổ chức thư mục không thay công thức, rubric, kết quả số học hoặc trạng thái lab/người chấm.

## 19. Đóng băng thiết kế bước 02 và chuyển kiểm chứng G — 2026-10-12

**Trạng thái tại thời điểm đóng thiết kế ngày 2026-10-12:** bước 01 COMPLETE; bước 02 COMPLETE — DESIGN_FROZEN; bước 03–06 NOT_STARTED. Bàn giao hiện hành ngày 2026-10-13 xem mục 20. Bản phương pháp là [RM-01 v0.4-r3](risk-method-v0.4.md), profile CONDITIONAL-BASE-v0.4 không đổi. Việc đóng thiết kế không chứng minh hệ thống đã hoạt động, rubric đã được hiệu chuẩn hoặc risk đã được chấp nhận.

**Người ghi quyết định:** trợ lý Codex, `decision_type=REVIEWER_DETERMINATION`, ngày 2026-10-12, múi giờ Asia/Bangkok; theo đề nghị trong phản hồi cùng ngày về sửa tài liệu và chuyển kiểm chứng người chấm sang bước 06. Đây là quyết định phạm vi bàn giao thiết kế của trợ lý, không giả ghi phê duyệt của SME. Quyết định ưu tiên MF-03/MF-04 riêng có thời điểm và dòng người dùng xác nhận/đổi trong báo cáo review mục 4; chưa có xác nhận đó và không ép người dùng chấm fixture để đóng thiết kế.

| Điều kiện đóng thiết kế | Đối chiếu |
| --- | --- |
| Công thức/rubric/UNKNOWN có version, nguồn và giới hạn | RM-01 mục 1–8; R25, các bất biến, giới hạn max và cờ theo dõi impact |
| Kiểm tra tái lập, expected tách khỏi phép tính kiểm tra | [Gói verification](verification/README.md), fixture, script và JSON kết quả có hash |
| Quy tắc AI/fixture được giữ | RM-01 mục 3/8: nhãn độc lập, con người xác minh; NOT_IMPLEMENTED/ENROLLED_SIMULATED không là evidence thật |
| Control/evidence và test có kỳ vọng trước lab | CE-01 C01–C08; TC-01 có 24 ca thiết kế; lab fixture trỏ C04/C05, thresholds TO_SET_BEFORE_LAB |
| Chỉ mục/trạng thái không tự mâu thuẫn | docs/README là chỉ mục dự án, planning/README là chỉ mục công việc; mục 16 tự có SUPERSEDED; lịch sử r2 được đóng gói trong history |

**MF-03/MF-04:** giữ `priority_decision=NOT_RANKED`, `decision_type=REVIEWER_DETERMINATION`, người review là trợ lý Codex. Tiền điều kiện thực tế UNKNOWN và thứ tự R đảo theo trọng số chưa hiệu chuẩn; không có căn cứ xác nhận thứ tự xử lý SME. Không đồng nhất review phép tính với phê duyệt ưu tiên.

### VALID-G-01 — Kiểm chứng độ nhất quán giữa hai người chấm G (bước 06)

- **Trạng thái:** NOT_RUN. **Độ tin cậy giữa người chấm của rubric G:** UNVALIDATED — chưa được kiểm chứng.
- **Phụ trách:** người điều phối kiểm chứng ở bước 06, chưa phân công; cần hai người chấm độc lập A/B, chưa chỉ định. Trợ lý hoặc hai lượt tự chấm không thay hai người.
- **Đầu vào:** rubric có version, cùng sáu case tổng hợp GR-01…GR-06, [phiếu A](review-forms/risk-g-rating-a-v0.4.md) và [phiếu B](review-forms/risk-g-rating-b-v0.4.md), cùng evidence packet. Thu lượt đầu trước khi xem điểm của nhau; lưu danh tính/vai trò, thời điểm, điểm/UNKNOWN, coverage và rationale gốc.
- **Đầu ra:** số ca có số ở cả hai, số UNKNOWN và mẫu số; tỷ lệ trùng G, phân phối chênh lệch tuyệt đối, lệch ≥2, xung đột coverage/số–UNKNOWN, khác nhãn; biên bản phân xử có lý do và giữ cả hai lượt gốc. Mẫu nhỏ không đủ để tuyên bố độ tin cậy thống kê rộng.
- **Điều kiện hoàn tất hoạt động:** có hai phiếu độc lập và báo cáo đối chiếu/phân xử. Nếu kết quả chỉ ra rubric mơ hồ thì mở lại thiết kế, sửa version và kiểm tra lại; hoàn tất hoạt động không tự nghĩa rubric đã đạt một ngưỡng chất lượng. Không đặt ngưỡng sau khi nhìn kết quả để gọi PASS.
- **Khi không thực hiện được:** giữ NOT_RUN và nêu giới hạn trong báo cáo bước 06; quyết định thu hẹp phạm vi phải ghi người có quyền, thời điểm và lý do, không chuyển thành PASS. Kiểm chứng với case tổng hợp không chứng minh hiệu lực control CRM thật.

**Việc còn mở ngoài thiết kế bước 02:** VALID-G-01; hiệu chuẩn tham số/nhu cầu SME; giá trị TTL/giới hạn thử/chính sách phiên và môi trường lab; kiểm thử CRM, evidence thật và 24 ca TC-01. Những việc này thuộc triển khai/kiểm chứng sau; chỉ VALID-G-01 là mục kiểm chứng chuyển tiếp riêng từ review rubric của bước 02.

**Bàn giao:** bước 03 có thể bắt đầu khi người dùng yêu cầu tiếp tục, dùng bản r3 và CE-01/TC-01 để tinh chỉnh assessment → gap → treatment → retest, các nhánh thiếu evidence/lỗi/quyền và lịch sử bất biến. Lần sửa này chưa khởi động bước 03, kiến trúc, stack hoặc lab.

## 20. Bàn giao bước 02 → bước 03 — 2026-10-13

**Căn cứ chuyển bước:** người dùng yêu cầu “bạn hãy bàn giao cho bước 3” trong chat bước 02 ngày 2026-10-13 (Asia/Bangkok). Bước 02 COMPLETE — DESIGN_FROZEN theo mục 19. Bước 03 là bước duy nhất IN_PROGRESS, đang tiếp nhận và thiết kế luồng; bước 04–06 NOT_STARTED. Đây là cho phép chuyển công việc sang bước 03, không là xác nhận ưu tiên MF-03/MF-04 hoặc chấp nhận risk của SME.

**Bên giao:** chat `01a11017-50a3-7160-adb8-33610b115257` (bước 02), trợ lý Codex. **Bên nhận:** chat `01a11017-5d2d-7f61-9eca-72ad4a73d759` (bước 03). Bản gốc dùng chung ở D:/Projects/vn-digital-trust/docs; các bản trong outputs là bản đọc. Chat nhận đọc tài liệu gốc trước khi cập nhật; sources/ chỉ là tham chiếu, không ghi đè.

### Đầu vào đã bàn giao

| Tài liệu | Nội dung dùng ở bước 03 |
| --- | --- |
| [RM-01 v0.4-r3](risk-method-v0.4.md) | Profile CONDITIONAL-BASE-v0.4; rubric/UNKNOWN, điểm và review, impact_progress cùng các trường bổ sung r3 |
| [CE-01 v0.1](control-evidence-v0.1.md) | Control catalog, C01–C08, evidence revision, thiếu evidence khác control thất bại |
| [TC-01 v0.1](control-test-cases-v0.1.md) | 24 ca có expected results, chưa chạy CRM/lab |
| [Phạm vi lab](lab-scope-and-fixtures-v0.1.md), [fixture lab](lab-fixtures-v0.1.json) | Một SME/hai chi nhánh, quyền/scope, SC-01/SC-02; mật khẩu + WebAuthn; tiêu chí C04/C05 đã định nghĩa, ngưỡng còn TO_SET_BEFORE_LAB |
| [Bộ kiểm tra](verification/README.md), [kết quả](verification/verification-results-v0.4.json) | PASS ngày 2026-10-12: 26 ca chính, 625 tổ hợp, 50.625 hộp miền, 20 ca impact; đây là kiểm tra thiết kế tổng hợp |
| [Requirements kỹ thuật](../requirements/requirements-technical-v0.1.md), [use cases](../use-cases/use-cases-technical-v0.1.md), [domain model](../domain-model/domain-model-technical-v0.1.md) | Baseline để tinh chỉnh và truy vết; rà soát chỗ mô tả cũ chưa phản ánh RM-01 r3 thay vì tự thay công thức đã chốt |

### Công việc và điều kiện hoàn thành bước 03

1. Tinh chỉnh TUC-01…TUC-08, tập trung TUC-04…TUC-08: input/context → đánh giá risk/control → review → gap → treatment → evidence mới/retest → báo cáo và lịch sử. Làm rõ ai được thao tác, tiền điều kiện, dữ liệu vào/ra, trạng thái và audit.
2. Thiết kế nhánh đủ evidence, thiếu evidence/UNKNOWN, evidence chưa xác minh, input/context lỗi, bất đồng reviewer, thiếu quyền hoặc quyền hết hạn, test INCONCLUSIVE và control thất bại đã xác minh. Risk acceptance không biến control thất bại thành SATISFIED.
3. Retest tạo snapshot/evidence revision mới, giữ bản cũ; so cùng scenario/context/profile/rubric và cùng loại CURRENT hoặc INHERENT. Trình bày riêng R, impact_progress và gap_progress; score_determined không thay review status. Giữ verified_worsening ba trạng thái và impact_summary_before/after, kể cả khi max/điểm không đổi.
4. Tạo sơ đồ activity/sequence cho các luồng trọng tâm, render và đọc kiểm tra; nối requirement → use case/nhánh luồng → scenario/tiêu chí/test ID. Chuẩn bị walkthrough giả lập SC-01 và SC-02 để kiểm tra luồng mở rộng, không ghi thành evidence CRM hoặc test run thật.
5. Cập nhật chỉ mục/kế hoạch khi có đầu ra, ghi phần đáp ứng và giới hạn. Hoàn thành bước 03 khi truy vết và các nhánh trên được đối chiếu, sơ đồ đã kiểm tra; chuyển sang bước 04 theo bàn giao riêng. Bước 03 chỉ thiết kế luồng, chưa triển khai lab, chọn stack/DB/API hoặc kiến trúc chi tiết.

### Bất biến và việc còn mở phải giữ

- RM-01: dùng R25 nguyên, cổng impact và hiển thị đúng; max bão hòa/điểm xác định không xóa UNKNOWN hoặc gaps. Không cộng scenario/tactic; không dùng range để xếp hạng, confidence không nhân R.
- E/F có thể gợi ý từ template, G từ ControlAssessment nhưng cần người xác nhận; NOT_IMPLEMENTED/ENROLLED_SIMULATED không là evidence thật. AI hỗ trợ có nguồn; tái tạo nhãn công thức không chứng minh dự đoán tốt.
- VN Digital Trust quản lý assessment, CRM/lớp danh tính thực thi control. VPN là tiền điều kiện mạng; đăng nhập VN Digital Trust không chứng minh CRM đạt MFA. SC-02 có phiên đọc hợp lệ, không tự gắn MFA của đăng nhập mới để hạ G.
- MF-03/MF-04 vẫn NOT_RANKED, REVIEWER_DETERMINATION của trợ lý; xác nhận riêng của người dùng chưa được ghi nhận. Bàn giao này không tự điền dòng xác nhận đó.
- VALID-G-01 ở bước 06 vẫn NOT_RUN, rubric G UNVALIDATED giữa người chấm. Hai phiếu A/B còn trống. Chưa có hiệu chuẩn SME, evidence CRM, triển khai/lab hoặc kết quả 24 test; TTL/giới hạn thử/chính sách phiên và cấu hình môi trường phải chốt trước lab.

**Kiểm tra khi bàn giao:** đối chiếu file/version và hash của fixture/script với kết quả đã lưu; kiểm tra liên kết trong ba tài liệu điều phối được cập nhật. Không đổi phương pháp, fixture, control criteria hoặc kết quả số học ở lần bàn giao này; không tạo thêm bản phương pháp mới.

## 21. Kết quả bước 03 — 2026-10-13 [SUPERSEDED bởi mục 22]

**Đính chính 2026-10-17:** kiểm tra XML/nhãn của SVG tuyến tính không chứng minh sơ đồ UML đúng. Quyết định COMPLETE dưới đây là ghi nhận lịch sử, đã mở lại để sửa ở mục 22.

**Tiếp nhận:** chat bước 03 đọc bản gốc planning/README, kế hoạch, docs/README, requirements/use cases/domain model và tài liệu RM-01/CE-01/TC-01/lab. Người dùng đã yêu cầu bàn giao từ bước 02; không có quyết định thay profile hoặc phê duyệt risk SME mới.

**Đầu ra:** [Technical Use Cases v0.2](../use-cases/use-cases-technical-v0.2.md) tinh chỉnh TUC-01…08, tập trung TUC-04…08; [activity source](../use-cases/assessment-flow-v0.2.puml), [sequence source](../use-cases/retest-sequence-v0.2.puml), [activity SVG](../use-cases/assessment-flow-v0.2.svg) và [sequence SVG](../use-cases/retest-sequence-v0.2.svg). SVG là bản trình bày cùng nội dung cốt lõi của sơ đồ nguồn; chưa dùng PlantUML renderer. XML SVG được parse thành công và nhãn/chuỗi bước được đọc đối chiếu với use case. Bảng truy vết ở use case mục 9 nối requirements với UC/nhánh, SC-01/SC-02, CE-01/TC-01 và TAC. Walkthrough mục 8 là dữ liệu giả lập, không phải test run.

| Điều kiện bước 03 | Đối chiếu |
| --- | --- |
| Use case và trạng thái/quyền/input/output | Use case v0.2 mục 1–7: RBAC tại thao tác, context snapshot, risk/control/review/gap/treatment/report và audit |
| Nhánh thành công và ngoại lệ | Mục 3–6: input lỗi, UNKNOWN nhưng điểm xác định, evidence sai scope/hết hạn/chưa xác minh, INCONCLUSIVE, failure đã xác minh, bất đồng reviewer, thiếu/quá hạn quyền |
| Retest và lịch sử | Mục 6–7: revision/snapshot mới, so tương đương, R/impact/gap progress tách biệt, không tự đóng gap/task hay suy attribution |
| Sơ đồ render/đọc kiểm tra | Hai nguồn PlantUML và SVG, kiểm tra XML/nhãn theo mục 21; sơ đồ nguồn có nhánh, SVG là bản tóm lược trực quan |
| Truy vết và walkthrough | Mục 8–9: SC-01/SC-02, C04/C05, T12–T17/T23/T24, TAC/requirements; không giả lập thành evidence thật |

**Quyết định trạng thái:** bước 03 COMPLETE về **thiết kế luồng**; bước 01 COMPLETE, bước 02 COMPLETE — DESIGN_FROZEN, bước 04–06 NOT_STARTED. Không tự khởi động bước 04. Phần kiến trúc/stack/DB/API/triển khai lab ở bước sau. Không đổi RM-01, CE-01, TC-01 hoặc fixture. VALID-G-01 vẫn NOT_RUN, rubric G chưa được kiểm chứng giữa người chấm; A/B trống. TTL/session, ngưỡng vận hành, môi trường, evidence CRM và hiệu chuẩn SME vẫn chưa có. MF-03/MF-04 vẫn NOT_RANKED theo REVIEWER_DETERMINATION của trợ lý và chưa có xác nhận ưu tiên của người dùng/SME.

## 22. Đính chính sơ đồ và logic bước 03 — 2026-10-17

**Căn cứ:** người dùng phát hiện sequence SVG bị thay bằng chín hộp tuyến tính và activity SVG mất nhánh; tệp góp ý kèm bốn bất nhất giữa use case, nguồn UML và fixture. Bước 03 đã được mở lại IN_PROGRESS trong lúc sửa. **Mục 21 đã kết luận đạt gate sơ đồ quá sớm:** parse XML và đọc nhãn của hình tự vẽ không xác nhận UML nguồn được render đúng.

**Kết quả đã kiểm tra:** [use case v0.2-r1](../use-cases/use-cases-technical-v0.2.md), hai nguồn `.puml` và SVG/PNG render trực tiếp bằng PlantUML 1.2026.8; [biên bản kiểm tra và hash](../use-cases/diagram-validation-v0.2-r1.md), [script tái tạo](../use-cases/render-diagrams-v0.2.ps1), [fixture bổ sung luồng/quyền](../use-cases/flow-fixtures-v0.2.json). Đã đọc ảnh PNG; sequence có 5 lifeline, 7 alt, 3 opt; activity có 8 quyết định và các nhánh/hợp luồng. Render trả exit code 0; đối chiếu cấu trúc SVG, hash baseline và ID role. Bản trước sửa nằm trong [gói lịch sử](history/step03-v0.2-before-r1.zip).

**Đồng bộ logic:** ControlAssessment trước G của CURRENT; UNKNOWN khi thiếu căn cứ. Thêm quyền evidence.verify cho đường self-assessment nội bộ và reviewer được giao trong overlay, giữ hạn quyền. Status theo RM-01 là EVALUATED/NEEDS_REVIEW; thông tin self-assessment/review riêng. Risk Owner phê duyệt ưu tiên vận hành, reviewer có thể đề xuất; không tự xác nhận MF-03/MF-04. Sơ đồ giữ failure đã xác minh đồng thời với evidence gap của tiêu chí khác; retest evidence VERIFIED không tự đóng task/gap. Các ca FLOW-01…10 được walkthrough ở mức thiết kế, không ghi là ca runtime PASS.

**Đối chiếu gate bước 03:** use case/truy vết/walkthrough ở v0.2 đã được cập nhật và review; gate render nay có nguồn, renderer, hình ảnh đã đọc và hash thay thế kiểm tra thiếu ở mục 21. **Trạng thái sau sửa: bước 03 COMPLETE về thiết kế luồng — v0.2-r1.** Bước 01 COMPLETE; bước 02 COMPLETE — DESIGN_FROZEN; bước 04–06 NOT_STARTED. Đây là kết luận kiểm tra thiết kế của trợ lý, không là phê duyệt vận hành/risk SME hoặc yêu cầu bắt đầu bước 04.

VALID-G-01 vẫn NOT_RUN; TC-01 vẫn chưa chạy; chưa có CRM evidence, hiệu chuẩn SME hay lab. RM-01/CE-01/TC-01 và bộ verification không thay đổi. Lab fixture v0.1 giữ nguyên bytes; quyền bổ sung của bước 03 được ghi riêng có hash baseline, cần triển khai/kiểm thử ở bước sau. Không gửi tin sang chat khác.

## 23. Người dùng xác nhận sơ đồ hiện hành — 2026-10-18

**Căn cứ:** người dùng trực tiếp ghi trong chat bước 03: “hiện tại các sơ đồ đã được kiểm tra và không có vấn đề gì”. Ghi nhận ngày 2026-10-18, múi giờ Asia/Bangkok.

**Phạm vi xác nhận:** hai sơ đồ activity và sequence hiện hành của bước 03, revision v0.2-r1 đã sửa/render và kiểm tra ở mục 22. Người dùng xác nhận không còn vấn đề với các sơ đồ này. Nguồn và hash đầu ra đối chiếu tại [biên bản kiểm tra](../use-cases/diagram-validation-v0.2-r1.md).

**Trạng thái:** bước 03 COMPLETE về thiết kế luồng; xác nhận của người dùng về sơ đồ đã được ghi nhận. Bước 04–06 NOT_STARTED; bàn giao sang bước 04 thực hiện theo yêu cầu riêng. Xác nhận này có phạm vi sơ đồ; các trạng thái kiểm chứng lab, VALID-G-01 và quyết định risk SME tiếp tục theo mục 22.

## 24. Đóng gói và bàn giao bước 03 → bước 04 — 2026-10-18

**Căn cứ chuyển bước:** sau xác nhận sơ đồ ở mục 23, người dùng trực tiếp yêu cầu trong chat bước 03: “được rồi hãy đóng gói và bàn giao sang bước 4.” Bước 03 COMPLETE về thiết kế v0.2-r1; bước 04 là bước duy nhất IN_PROGRESS — tiếp nhận và thiết kế kiến trúc theo yêu cầu này; bước 05–06 NOT_STARTED. Xác nhận sơ đồ và yêu cầu bàn giao không thay thế phê duyệt risk của SME hoặc xác nhận ưu tiên MF-03/MF-04.

**Bên giao:** chat `01a11017-5d2d-7f61-9eca-72ad4a73d759` (bước 03). **Bên nhận:** chat `01a11017-6a8a-7dd3-ae84-92ec9c17c946` (bước 04). Tài liệu gốc làm việc tiếp tục là D:/Projects/vn-digital-trust/docs. Đọc planning/README, kế hoạch này và docs/README trước khi bắt đầu. Mục 22 ghi kiểm tra thiết kế đã sửa; mục 23 ghi xác nhận của người dùng; mục 24 là bàn giao hiện hành.

### Đầu vào được đóng gói

| Tài liệu | Vai trò cho bước 04 |
| --- | --- |
| [Use case v0.2-r1](../use-cases/use-cases-technical-v0.2.md) | TUC-01…08; dữ liệu/quyền, trạng thái, ngoại lệ, retest/report và truy vết |
| [Activity source](../use-cases/assessment-flow-v0.2.puml), [SVG](../use-cases/assessment-flow-v0.2.svg), [PNG](../use-cases/assessment-flow-v0.2.png) | Luồng có 8 quyết định, gồm control trước G, retest và điều kiện đóng |
| [Sequence source](../use-cases/retest-sequence-v0.2.puml), [SVG](../use-cases/retest-sequence-v0.2.svg), [PNG](../use-cases/retest-sequence-v0.2.png) | 5 lifeline, 7 alt, 3 opt; self-assessment, quyền hết hạn, snapshot và lịch sử |
| [Biên bản kiểm tra](../use-cases/diagram-validation-v0.2-r1.md), [script render](../use-cases/render-diagrams-v0.2.ps1) | Phiên bản renderer, lệnh tái tạo, hash và bằng chứng đã đọc ảnh |
| [FLOW-03-v0.2-r1](../use-cases/flow-fixtures-v0.2.json) | Overlay quyền/10 ca luồng thiết kế; dùng cùng baseline, không sửa baseline; thực thi NOT_RUN |
| [RM-01 v0.4-r3](risk-method-v0.4.md), [CE-01](control-evidence-v0.1.md), [TC-01](control-test-cases-v0.1.md), [verification](verification/README.md) | Phương pháp/control/criteria cố định và kiểm tra thiết kế tổng hợp; không phải kết quả CRM |
| [Scope lab](lab-scope-and-fixtures-v0.1.md), [baseline fixture](lab-fixtures-v0.1.json) | Một SME/hai chi nhánh, SC-01/SC-02, quyền CRM và tiền điều kiện |
| [Requirements](../requirements/requirements-technical-v0.1.md), [domain model](../domain-model/domain-model-technical-v0.1.md), [quyết định phạm vi](../scope/technical-first-scope-v0.1.md) | Nền để truy vết kiến trúc; cách diễn đạt cũ cần đối chiếu RM-01 r3 và use case r1 |

**Gói đọc cố định:** `vn-digital-trust-step03-to-step04-2026-10-18.zip` trong outputs của chat bước 03. Gói có START_HERE.md, MANIFEST.json với SHA-256 từng tệp và bản chụp docs giữ cấu trúc liên kết. Nhóm history/research và baseline cũ chỉ phục vụ truy vết; danh sách trên xác định đầu vào hiện hành. Gói không chứa JAR/Java, credentials hay evidence CRM. SHA-256 của ZIP được ghi cạnh ZIP trong tệp `.sha256`; mọi cập nhật tiếp theo diễn ra ở bản gốc D:, không ghi đè gói đã bàn giao.

**Kiểm tra khi đóng gói:** 9/9 hash của các đầu ra bước 03 khớp biên bản; hash baseline trong overlay khớp lab-fixtures-v0.1.json. Xác nhận nguồn được chụp nhất quán, đường dẫn gói an toàn, kiểm tra CRC ZIP và hash từng thành viên theo manifest. Không cần render lại vì bytes của nguồn/ảnh đã kiểm tra và được người dùng xác nhận không thay đổi. Đây là kiểm tra toàn vẹn gói, không chạy lại CRM/lab hoặc nâng trạng thái FLOW/TC.

### Phạm vi và điều kiện hoàn thành bước 04

1. Thiết kế trách nhiệm và ranh giới thành phần phục vụ inventory/context, scenario, evidence/verification, control assessment, risk evaluation, review, gap/treatment/retest, report và audit. Truy vết từng thành phần về TUC/yêu cầu/nhánh đã có.
2. Mô tả luồng dữ liệu và ranh giới tin cậy: VN Digital Trust, người dùng, nơi lưu evidence, CRM/lớp danh tính và lab bên ngoài; sơ đồ component/container/deployment hoặc tương đương phải được render từ nguồn và đọc ảnh kiểm tra.
3. Xác định cách bảo vệ đọc/ghi evidence và quyết định theo quyền/scope/expiry; lưu revision, verification decision, snapshot/version và audit; xử lý lỗi, thao tác lặp, cập nhật đồng thời và tránh kết quả mới ghi đè lịch sử. Đây là trách nhiệm/đảm bảo kiến trúc; chi tiết schema và API thuộc bước 05.
4. Đối chiếu kiến trúc bằng SC-01, SC-02 và các nhánh FLOW-01…10, gồm tự đánh giá không consultant, hết hạn quyền, thiếu evidence khác failure, failure đi cùng evidence gap, bất đồng review và retest không tương đương.
5. Có phương án deployment khả thi trong nguồn lực khoảng 16 GB RAM; ranh giới công cụ kiểm chứng bên ngoài, giả định và rủi ro kiến trúc rõ. Chọn stack, ERD, API contract thuộc bước 05; cài/chạy lab và prototype thuộc bước 06.
6. Cập nhật chỉ mục và kế hoạch với đầu ra, quyết định/lý do, kiểm tra thực hiện và việc còn thiếu. Chỉ hoàn thành bước 04 khi đủ đối chiếu trên; chuyển sang bước 05 theo bàn giao riêng.

### Các bất biến và giới hạn chuyển tiếp

- Một deployment/một SME/hai chi nhánh; quyền VN Digital Trust tách khỏi CRM. Mọi thao tác được bảo vệ, gồm đọc evidence, kiểm tra quyền/scope/trạng thái/expiry tại lúc thực hiện.
- Self-assessment không phụ thuộc consultant. Overlay bước 03 cấp evidence.verify và quyền đọc đúng scope cho U002/VDT_SECURITY; U004/VDT_REVIEWER chỉ xác minh trong phạm vi/thời hạn được giao. Xác minh evidence khác review độc lập; tự đánh giá phải giữ provenance. Risk Owner có risk.priority_approve để chốt ưu tiên vận hành; reviewer đề xuất. Đây là quyền thiết kế chưa triển khai.
- CURRENT: evidence/ControlAssessment trước xác nhận G theo coverage và strength từng đường; thiếu căn cứ giữ UNKNOWN. `status=EVALUATED|NEEDS_REVIEW` độc lập score_determined; assessment_mode/review_outcome riêng. Điểm xác định không xóa UNKNOWN/gap; không ánh xạ result trực tiếp sang G; không cộng scenario/tactic, không xếp hạng bằng range, confidence không nhân R.
- Evidence revision/context/criteria/profile/rubric/assessment/decision được giữ bất biến. Retest tạo bản mới; so cùng scenario/context/profile/rubric và cùng loại CURRENT hoặc INHERENT; khác thì NOT_COMPARABLE. R, impact_progress, gap_progress riêng; giữ verified_worsening=true/false/null, impact summaries và attribution.
- CONTROL_GAP khác EVIDENCE_GAP và có thể cùng tồn tại. Evidence VERIFIED, risk acceptance hoặc điểm giảm không tự làm control đạt/đóng gap/task. Closure cần tiêu chí, quyền và quyết định có audit.
- SC-01: mật khẩu + WebAuthn, UV required; VPN là tiền điều kiện mạng. SC-02 đã có phiên đọc hợp lệ, không dùng MFA đăng nhập mới để tự hạ G. Fixture NOT_IMPLEMENTED/ENROLLED_SIMULATED không là evidence thật.
- VALID-G-01 ở bước 06 vẫn NOT_RUN; A/B trống, rubric G chưa được kiểm chứng giữa người chấm. FLOW-01…10 và 24 ca TC chưa chạy; chưa có CRM evidence, hiệu chuẩn SME hoặc lab. TTL/session/ngưỡng/môi trường còn TO_SET_BEFORE_LAB. MF-03/MF-04 vẫn NOT_RANKED, REVIEWER_DETERMINATION của trợ lý, chưa có SME xác nhận.

**Tiếp nhận:** chat bước 04 ghi nhận trong chính chat đó và tiếp tục công việc kiến trúc được giao; kết quả/việc còn thiếu cập nhật vào kế hoạch chung. Không cần gửi tin trở lại bước 03, tạo thêm chat hoặc lịch chạy.

## 25. Kết quả bước 04 — kiến trúc v0.1, 2026-10-18

**Trạng thái:** COMPLETE về thiết kế kiến trúc; bước 05–06 vẫn NOT_STARTED. Tiếp nhận bàn giao mục 24 theo yêu cầu người dùng từ chat bước 03. Không có prototype, CRM evidence hoặc lab test mới.

**Đầu ra:** [kiến trúc kỹ thuật](../architecture/architecture-technical-v0.1.md), ba sơ đồ nguồn và SVG/PNG ([container](../architecture/container-v0.1.puml), [deployment](../architecture/deployment-v0.1.puml), [evidence/decision](../architecture/evidence-decision-flow-v0.1.puml)), [biên bản render/đọc ảnh](../architecture/diagram-validation-v0.1.md). Các tệp nằm trong `docs/architecture/`, không tạo kế hoạch riêng ở thư mục chat.

| Điều kiện mục 24 | Bằng chứng thiết kế |
| --- | --- |
| Trách nhiệm, truy vết thành phần | Kiến trúc §2 ánh xạ auth, context/scenario, control/evidence, verification, assessment/risk, review, treatment/retest, report/audit tới TUC và TFR/TNFR. |
| Luồng dữ liệu và ranh giới | Kiến trúc §1/3 và sơ đồ container/deployment tách user, VDT, protected evidence store, CRM identity, lab runner/receiver; ba sơ đồ đã render trực tiếp và đọc ảnh theo biên bản. |
| Quyền, snapshot/version, lỗi | Kiến trúc §4/5 thiết kế kiểm quyền/scope/expiry từng read/write/commit, revision/decision bất biến, idempotency, xung đột cập nhật, lỗi upload/test/tính toán, retest và closure có điều kiện. |
| SC-01/02 và FLOW-01…10 | Kiến trúc §6 đối chiếu từng ca với gate và kết quả giữ UNKNOWN/failure/gap riêng; không nâng fixture thành evidence thật. |
| Deployment, giả định và giới hạn | Kiến trúc §7: một app trên host/VM khoảng 16 GB, kho metadata/evidence riêng, backup; CRM/lab ngoài sản phẩm. Stack/ERD/API để bước 05, đo và test để bước 06. |
| Chỉ mục và kế hoạch | Mục này, `docs/README.md` và `docs/planning/README.md` dẫn tới đầu ra hiện hành. |

**Quyết định:** Giữ kiến trúc module trong một ứng dụng để có transaction và vận hành phù hợp đồ án; không buộc microservice. Intake thủ công từ CRM/lab giữ ranh giới tin cậy, mọi kết luận cần verification và assessment có provenance. Kho evidence tách metadata, nội dung chỉ qua policy gate; snapshot/decision bất biến để report `as_of` và retest tái lập. Đây là quyết định thiết kế, chưa chọn công nghệ.

**Giới hạn/việc còn thiếu:** FLOW-01…10, TC-01 T01–T24, VALID-G-01 vẫn NOT_RUN. Hai phiếu G trống, độ tin cậy giữa người chấm chưa kiểm chứng. Không có CRM evidence, SME calibration, lab execution hay phê duyệt SME cho MF-03/MF-04; các ca đó vẫn NOT_RANKED. TTL/session/ngưỡng/môi trường còn TO_SET_BEFORE_LAB. Bước 05 cần chọn stack, DB, API và chi tiết file/version/quyền/transaction; bước 06 cần triển khai, đo tài nguyên, kiểm thử restore/RBAC/luồng và lab khi đủ điều kiện.

**Thứ tự tiếp:** Bước 05 chỉ bắt đầu khi có bàn giao riêng theo kế hoạch; không coi việc đóng thiết kế bước 04 là triển khai hoặc kiểm chứng thành công.


## 26. Xác nhận và bàn giao bước 04 → bước 05, chờ lưu ý — 2026-10-19

**Căn cứ trực tiếp từ người dùng trong chat bước 04:** “Mình đã kiểm tra qua và thấy mọi thứ đã đúng, bạn hãy bàn giao sang cho bước 5 và trước khi bước 5 thực thi mình có 1 vài lưu ý , bạn làm ơn đừng cho bước 5 chạy ngay lập tức.” Ghi nhận theo Asia/Bangkok. Xác nhận này áp dụng cho đầu ra thiết kế bước 04; không thay thế kiểm chứng runtime hoặc phê duyệt risk của SME.

**Trạng thái hiện hành:** bước 01–04 COMPLETE về thiết kế; bước 05 **NOT_STARTED — WAITING_FOR_USER_NOTES** (đã bàn giao tài liệu, chờ lưu ý); bước 06 NOT_STARTED. Không có bước nào được khởi động bởi riêng việc bàn giao này.

**Bên giao:** chat bước 04 `01a11017-6a8a-7dd3-ae84-92ec9c17c946`. **Bên nhận:** chat bước 05 `01a11017-7725-7c80-84fe-349ae18b455f`. Bản làm việc chính tiếp tục là `D:/Projects/vn-digital-trust/docs`.

### Chỉ dẫn bắt buộc cho bên nhận

Trong lượt nhận bàn giao, chỉ xác nhận đã nhận và đang chờ lưu ý của người dùng; không dùng công cụ, nghiên cứu, chọn công nghệ, thiết kế ERD/API, tạo/sửa tệp, triển khai hoặc chạy lab. Không tự đặt IN_PROGRESS, không tạo lịch hay gửi tiếp sang chat khác. Bàn giao không phải lệnh bắt đầu. Chỉ bắt đầu sau khi người dùng đã cung cấp lưu ý và yêu cầu tiếp tục; khi đó đọc lại planning/README.md, kế hoạch này (mục 26), docs/README.md và AGENTS.md áp dụng, ghi các lưu ý vào kế hoạch trước khi thực hiện phần công việc được cho phép. Nếu chưa rõ người dùng đã cho phép bắt đầu, tiếp tục chờ.

### Đầu vào hiện hành cho bước 05 khi được bắt đầu

| Đầu vào | Cách dùng |
| --- | --- |
| [Kiến trúc v0.1](../architecture/architecture-technical-v0.1.md) | Trách nhiệm, policy gate, evidence/revision/decision, lỗi, retry/concurrency, retest/report và deployment |
| [Container](../architecture/container-v0.1.puml), [deployment](../architecture/deployment-v0.1.puml), [evidence/decision](../architecture/evidence-decision-flow-v0.1.puml), SVG/PNG và [biên bản](../architecture/diagram-validation-v0.1.md) | Đầu ra bước 04; người dùng đã kiểm tra và xác nhận |
| [Use case v0.2-r1](../use-cases/use-cases-technical-v0.2.md), activity/sequence và [FLOW overlay](../use-cases/flow-fixtures-v0.2.json) | TUC-01…08, nhánh lỗi/quyền/retest, bổ sung quyền theo assessment; không sửa baseline fixture |
| [RM-01 v0.4-r3](risk-method-v0.4.md), [CE-01](control-evidence-v0.1.md), [TC-01](control-test-cases-v0.1.md), [verification](verification/README.md) | Phương pháp/criteria đã đóng băng; fixture và kết quả số học là thiết kế, không là CRM evidence |
| [Phạm vi lab](lab-scope-and-fixtures-v0.1.md), [fixture](lab-fixtures-v0.1.json), [requirements](../requirements/requirements-technical-v0.1.md), [domain model](../domain-model/domain-model-technical-v0.1.md), [scope](../scope/technical-first-scope-v0.1.md) | Bối cảnh và truy vết. Câu chữ baseline cũ cần đối chiếu RM-01 r3/use case r1/kiến trúc hiện hành |

**Gói đọc cố định:** `C:/Users/trant/Documents/Codex/2026-10-06/vn-digital-trust-step-04/outputs/vn-digital-trust-step04-to-step05-2026-10-19.zip`. Có START_HERE.md ghi yêu cầu chờ, MANIFEST.json với SHA-256 từng thành viên và snapshot docs giữ cấu trúc thư mục. History/research là tài liệu truy vết, không là baseline hiện hành. Không giải nén đè D:. Hash ZIP ở tệp `.sha256` cạnh gói, tránh vòng tự tham chiếu hash của kế hoạch. Đã đối chiếu 11/11 tệp kiến trúc bản gốc với gói v0.1 trước bàn giao; bytes không thay đổi nên không render lại. Việc kiểm tra CRC/hash gói là kiểm tra toàn vẹn tài liệu, không nâng trạng thái FLOW/TC.

### Phạm vi và điều kiện hoàn thành bước 05 sau khi được cho phép

1. Ghi lưu ý của người dùng; chọn stack và cách triển khai có lý do, đáp ứng kiến trúc một ứng dụng/một SME và nguồn lực khoảng 16 GB, có giả định và trade-off rõ.
2. Thiết kế ERD và constraints cho context/scenario, control/evidence revisions, verification/assessment/decision snapshots, RBAC/scope/expiry, gap/treatment/retest/report/audit; giữ trạng thái độc lập và lịch sử bất biến.
3. Đặc tả API theo TUC/quyền/nhánh, gồm validation, lỗi, retry/idempotency, concurrency, transaction, authorization lúc đọc/ghi/commit, upload/download/export và file lifecycle; không rò nội dung ngoài scope.
4. Truy vết SC-01/SC-02, FLOW-01…10 và yêu cầu từ bước 03–04 vào thiết kế; render/đọc sơ đồ nếu tạo; ghi rõ giới hạn và các ca phải kiểm chứng ở bước 06.
5. Cập nhật kế hoạch/chỉ mục với quyết định, đầu ra, kiểm tra và việc còn thiếu. Không tự khởi động prototype/lab bước 06.

**Bất biến/giới hạn giữ nguyên:** self-assessment không phụ thuộc consultant; U002 được evidence.verify trong scope, U004 chỉ đúng assignment còn hạn; VDT auth tách CRM. CURRENT dùng evidence/ControlAssessment trước xác nhận G theo đường. UNKNOWN, status, score_determined, mode/outcome review, control/gap/task riêng; failure xác minh không bị INCONCLUSIVE che. Verification/acceptance/điểm giảm không tự đóng gap/task. Revision, criteria/context/profile/rubric/decision snapshots giữ bất biến; retest so tương đương cùng CURRENT hoặc INHERENT, khác thì NOT_COMPARABLE; R/impact/gap progress, verified_worsening, impact summaries và attribution riêng. Risk Owner có risk.priority_approve; reviewer chỉ đề xuất. SC-01 password + WebAuthn/UV, VPN là tiền điều kiện; SC-02 đã có phiên đọc, MFA login mới không tự hạ G. Không sửa sources/ hoặc thay RM-01 đã đóng băng một cách ngầm định.

**Chưa kiểm chứng:** FLOW-01…10, 24 TC và VALID-G-01 vẫn NOT_RUN; A/B trống; chưa có CRM evidence, lab hay hiệu chuẩn SME. TTL/session/ngưỡng/môi trường còn TO_SET_BEFORE_LAB. MF-03/MF-04 vẫn NOT_RANKED, REVIEWER_DETERMINATION của trợ lý, chưa có phê duyệt ưu tiên SME.

## 27. Khởi động bước 05 và tiếp nhận lưu ý — 2026-10-19

**Ủy quyền trực tiếp:** Người dùng trong chat bước 05: “Mình chỉ có lưu ý như vậy thôi, hãy bắt đầu bước 5.” Asia/Bangkok. Yêu cầu chờ tại mục 26 đã được đáp ứng. Bước 01–04 COMPLETE về thiết kế; bước 05 IN_PROGRESS; bước 06 NOT_STARTED. Phạm vi lượt này là thiết kế công nghệ, ERD/database, API, file/version và đối chiếu thiết kế; chưa triển khai prototype/lab.

**Lưu ý bắt buộc từ người dùng:** tệp đính kèm “Bảng đối chiếu 6 điểm cần nâng cấp…” và các mục 3.1–3.4 trong chat. Dùng domain-model-technical-v0.1 làm mốc khái niệm, không sửa mốc này hoặc sources/; thiết kế mới phải đáp ứng RM-01 v0.4-r3, CE-01/TC-01, use case v0.2-r1 và kiến trúc v0.1.

| Mã | Nội dung phải được đáp ứng ở bước 05 |
| --- | --- |
| NOTE-01 | Organization có Branch BR-HCM/BR-DN; RoleAssignment có scope/object scope, assignment assessment và access_expires_at; kiểm quyền lúc thực hiện. |
| NOTE-02 | EvidenceRevision giữ payload/provenance bất biến; VerificationDecision append-only riêng, actor/time/scope/reason/conclusion/mode; không dùng quyết định khác revision/scope hoặc hết hiệu lực. |
| NOTE-03 | ControlCriterionVersion và kết quả theo tiêu chí, execution PASS/FAIL/INCONCLUSIVE/NOT_READY, observation, đúng revision/verification decision; giữ CONTROL_GAP và EVIDENCE_GAP đồng thời. |
| NOTE-04 | RiskEvaluation lưu type, precondition/horizon, E/F và excluded controls/confirmation/bounds, vector C/I_integrity/A/B, từng đường G, R25/ranges/gates, UNKNOWN/status/score_determined/mode/review riêng; giữ đúng RM-01. |
| NOTE-05 | AssessmentComparison lưu before/after, comparability, R_progress/impact_progress/gap_progress, từng chiều, verified_worsening và summary, attribution và review độc lập. |
| NOTE-06 | Review dispute giữ cả nhận định, phân xử tạo snapshot mới; PriorityDecision/ClosureDecision riêng; idempotency key + payload hash và optimistic concurrency cho thực thể cập nhật. |
| NOTE-07 / 3.1 | Upload POST evidence-revisions đi Browser → Reverse proxy/TLS → Policy gate → intake; multipart không bỏ qua gate; kiểm lại trước commit. |
| NOTE-08 / 3.2 | Seed RBAC hợp nhất baseline lab-fixtures và permission_additions của flow-fixtures: evidence.read_assigned/evidence.verify cho Security/Reviewer đúng scope; risk.priority_approve cho Risk Owner. Giữ fixture lịch sử, tạo seed hiện hành có provenance. |
| NOTE-09 / 3.3 | Tách storage_state STAGED/COMMITTED/INTEGRITY_FAILED/ORPHANED; trạng thái xác minh từ decision; verification_mode SELF_ASSESSED/INDEPENDENT_REVIEWED; tách assessment_mode/review_outcome khỏi status/score_determined. Phân biệt kết quả control với điểm risk. |
| NOTE-10 / 3.4 | AuthenticationProfile AUTH-CRM-01/config có challenge_ttl_seconds, max_attempt_limit, session_idle_timeout_seconds, rp_id, allowed_origins. 120/5/900 là ví dụ chưa phê duyệt; giá trị/môi trường còn TO_SET_BEFORE_LAB; auth VDT tách CRM. |

**Cách kiểm tra:** truy vết NOTE-01…10 và SC-01/02, FLOW-01…10 vào tài liệu/schema/API; kiểm tra nhất quán quyền, enum, references, các nhánh lỗi và bất biến; render và đọc sơ đồ ERD; ghi kết quả thực tế vào mục tiếp theo trước khi quyết định trạng thái hoàn thành thiết kế.

**Giới hạn giữ nguyên:** FLOW, T01–T24, VALID-G-01 NOT_RUN; A/B trống; chưa có evidence CRM/SME calibration/lab; MF-03/MF-04 NOT_RANKED, chưa có phê duyệt SME. Không tự chuyển bước 06.

## 28. Kết quả bước 05 — thiết kế v0.1, 2026-10-21

**Trạng thái:** COMPLETE về thiết kế công nghệ/database/API theo phạm vi được người dùng cho phép tại mục 27. Bước 01–05 COMPLETE về thiết kế; bước 06 **NOT_STARTED**. Các yêu cầu “tiếp tục” trong chat bước 05 được thực hiện trên công việc đang dang dở. Chưa ghi nhận nghiệm thu Bước 05 của người dùng hoặc phê duyệt nghiệp vụ của SME.

**Đầu ra:** [chỉ mục thiết kế](../design/README.md), [quyết định công nghệ](../design/technology-decisions-v0.1.md), [data model](../design/data-model-v0.1.md), [DDL PostgreSQL](../design/schema-v0.1.sql), [API contract](../design/api-contract-v0.1.md), [OpenAPI](../design/openapi-v0.1.yaml), [storage/transaction](../design/storage-transactions-v0.1.md), [configuration](../design/configuration-v0.1.md), [config template](../design/config-template-v0.1.json), [RBAC seed](../design/rbac-seed-v0.1.json), [traceability](../design/traceability-v0.1.md) và [biên bản kiểm tra](../design/validation-v0.1.md). Có ba ERD cùng sơ đồ upload ở định dạng nguồn PlantUML, SVG và PNG.

| Điều kiện hoàn thành mục 26 | Bằng chứng |
| --- | --- |
| Tiếp nhận lưu ý và chọn công nghệ có lý do | NOTE-01…10 tại mục 27 và traceability; Django 5.2 LTS/DRF, PostgreSQL 17, Caddy, file store riêng, worker tuần tự; nguồn/trade-off/tài nguyên và giới hạn tại technology-decisions. |
| ERD/constraints/quyền/trạng thái/lịch sử | Data dictionary và DDL 106 bảng, gồm các bảng con/liên kết; revision/decision bất biến, scope/expiry, storage tách verification, assessment mode/outcome riêng, retest/report/as_of và closure. |
| API theo TUC/quyền/nhánh và file lifecycle | OpenAPI 3.1.1 có 92 paths/123 operations; API narrative và storage quy định auth/CSRF, gate, validation/lỗi, idempotency/OCC, commit/revoke, upload/scan/reconciliation và export. |
| Truy vết và sơ đồ đã đọc | Traceability NOTE/SC/FLOW/TFR/TNFR; bốn sơ đồ render SVG/PNG thành công và đã mở PNG kiểm tra theo biên bản. |
| Kế hoạch/chỉ mục/giới hạn | Mục này cùng docs/README.md, planning/README.md, design/README.md; bước 06 giữ NOT_STARTED. |

**Bốn lưu ý 3.1–3.4:** upload qua reverse proxy/TLS và policy gate; seed thêm đúng evidence.verify/evidence.read_assigned/risk.priority_approve theo scope; storage/verification và status/score/mode/outcome tách riêng; AUTH-CRM-01 có đủ năm trường cấu hình, ví dụ 120/5/900 không là giá trị hiệu lực.

**Kiểm tra thực hiện:** [21/21 kiểm tra tĩnh đạt](../design/verification/results-v0.1.json); cấu trúc OpenAPI/local refs/6 schema examples, permission catalog/seed provenance, DDL 390 statements/10 PLpgSQL functions, 287 FK targets và PK/UNIQUE tương ứng, cấu hình, link và hash. Tám đầu vào đóng băng không đổi SHA-256. Đã render và đọc bốn sơ đồ. Chưa chạy DDL, app hoặc các ca lab; kết quả parse không thay thế migration/transaction tests.

**Sửa sau review:** giải vòng tạo context/scenario/assessment, membership nhiều scenario, persistence snapshot/confirmation/request/approval, retest nhiều references, adjudication nhiều review, closure theo criterion/version, scope scenario_ids, EvidenceLink nhiều criterion và profile FK. Comparison giữ task version/attribution evidence; plan tùy chọn. Các sửa đã nằm trong DDL/API/dictionary cùng phiên bản; không sửa baseline RM/fixture/sources.

**Quyết định có chủ ý:** một ứng dụng module với DB transaction và kho tệp riêng; snapshot payload và children được khóa trong transaction tạo, mutable entity dùng version/history. Control không có điểm RM giữ score_determined=false cùng score_applicability=NOT_APPLICABLE. Seed Security thêm report.read và Risk Owner thêm assessment.adjudicate dưới extension có provenance; độc lập adjudicator vẫn theo actor, không theo số role.

**Giới hạn còn lại trước/ở bước 06:** chốt năm giá trị AUTH-CRM-01, môi trường, config owner và business scope approval; pin bản vá triển khai; chạy migration/seed/service thật; kiểm quyền/scope/expiry/revoke, idempotency/OCC, scanner/crash/restore/export, immutable/as_of/review/closure; đo tài nguyên. FLOW-01…10, T01–T24 và VALID-G-01 **NOT_RUN**; A/B trống; chưa có CRM evidence/SME calibration. MF-03/MF-04 **NOT_RANKED**, chưa có phê duyệt SME. Chưa triển khai prototype/lab.

**Gói xem lại:** `C:/Users/trant/Documents/Codex/2026-10-06/vn-digital-trust-step-05/outputs/vn-digital-trust-step05-v0.1-2026-10-21.zip`; có snapshot docs, START_HERE.md và MANIFEST.json (SHA-256 từng thành viên); SHA-256 của ZIP ở tệp cạnh gói. Bản xem trực tiếp ở outputs/step05-review/. Không giải nén đè bản làm việc D:. Hash/CRC chỉ kiểm toàn vẹn tài liệu. Bước 06 chỉ tiếp tục theo yêu cầu/bàn giao riêng của người dùng.


## 29. Khởi động bước 06 — 2026-10-23

**Ủy quyền trực tiếp:** Người dùng: “Hãy bắt đầu bước 6”. Khi hỏi môi trường CRM, người dùng trả lời: “Chưa có; chuẩn bị phương án lab local”. Bước 06 IN_PROGRESS. Bước 01–05 giữ COMPLETE về thiết kế.

**Phạm vi:** dựng prototype theo Django/PostgreSQL và thiết kế Bước 05; kiểm migration/quyền/bất biến, risk engine, evidence lifecycle; chuẩn bị phương án lab local riêng. Dự án ban đầu chưa có mã backend/frontend. Docker Desktop đã được khởi động để tạo môi trường kiểm thử riêng; không dùng database có sẵn.

**Thứ tự:** nền ứng dụng + DB/migration → seed/auth/RBAC → inventory/context/scenario → evidence/control/risk → review/treatment/retest/report → fault/restore + lab có cấu hình. Các kết quả kiểm được ghi ở docs/implementation. Các mục chưa thực hiện giữ NOT_RUN; chưa tự phê duyệt CRM profile hay tạo evidence CRM.

**Môi trường:** container phát triển local dùng Python 3.13/Debian trixie và PostgreSQL 17, pin image digest; khác cách đóng gói VM/systemd tham chiếu, không thay stack hay công thức. Chỉ bind loopback. Docker phát triển chưa là nghiệm thu cấu hình triển khai, TLS hoặc isolation của lab CRM.

### 29.1. Kết quả nền và danh mục quyền — 2026-10-23

Đã dựng mã nền Django 5.2.18/DRF 3.16.1 trên Python 3.13.17; image gốc và 17 dependency khóa theo phiên bản/hash. Migration runtime đã tạo 106 bảng trên PostgreSQL 17.11; transaction/search_path được điều chỉnh riêng cho Django, không sửa DDL thiết kế. 29 file thiết kế Bước 05 đối chiếu khớp bytes với gói bàn giao.

Đã triển khai module thuần cho cấu hình, policy authorization, RM-01/impact comparison và file storage/scanner client; chưa nối thành API nghiệp vụ. Trang nền thể hiện đang xây dựng, API nghiệp vụ trả 503; chưa chạy app service hoặc mở cổng truy cập app trực tiếp.

Đã nạp danh mục RBAC từ seed có kiểm hash nguồn: **4 role, 19 permission, 22 liên kết**, có đủ `evidence.verify`, `evidence.read_assigned` theo Security/Reviewer và `risk.priority_approve` của Risk Owner. Seed chạy lại không đổi row/UUID; drift bị từ chối; runtime chỉ đọc catalog. Chưa tạo user, scope hay role assignment; scope mô tả của role không tự tạo grant.

**Kết quả:** 121/121 unit/contract/HTTP checks trên Linux, 15/15 PostgreSQL foundation checks, 10/10 RBAC PostgreSQL checks. Model migration check không phát hiện thay đổi. Deploy check còn W005/W021 về HSTS subdomains/preload. Preflight CRM template BLOCKED với 35 vấn đề chưa cấu hình, gồm năm trường người dùng lưu ý; không dùng 120/5/900 như defaults. [Hồ sơ triển khai](../implementation/README.md), [kiểm chứng](../implementation/validation-v0.1.md), [catalog RBAC](../implementation/rbac-catalog-v0.1.md).

### 29.2. Chuyển dữ liệu Docker sang thư mục project ổ D

Theo yêu cầu tiếp theo của người dùng vì ổ C sắp đầy, đã chuyển WSL Docker data VHDX và Docker VMM VHDX sang **D:/Projects/vn-digital-trust/.runtime/docker-desktop**. Đường cũ ở C dùng NTFS junction; image, layer, build cache và named volume lưu vật lý ở D. `.runtime/` không đưa vào Git/image/gói báo cáo.

Đã xuất SQL trước chuyển, dừng Docker/DB, kiểm SHA-256 bản sao, khởi động lại và kiểm đầy đủ image/volume cùng 15/15 DB checks; sau đó xóa đúng hai VHDX dự phòng trên C. Giải phóng 3.675 GiB, C còn 24.247 GiB tại thời điểm ghi nhận. Bộ cài, log/config và đĩa hệ thống WSL nhỏ vẫn ở C. Docker VMM hiện không dùng; đĩa đó được kiểm hash, chưa chạy VMM. Chi tiết và lưu ý không đổi tên/xóa thư mục project khi Docker còn dùng: [biên bản lưu trữ](../implementation/docker-storage-v0.1.md).

### 29.3. Phương án lab local và phần tiếp theo

Đã chuẩn bị [phương án CRM local](../implementation/local-crm-lab-plan-v0.1.md): tách danh tính VDT/CRM; VPN là tiền điều kiện SC-01; password + WebAuthn/UV; SC-02 bắt đầu từ phiên đọc hợp lệ và receiver do lab kiểm soát. Có giai đoạn dựng, cấu hình phải chốt, ma trận evidence và trạng thái chưa chạy. Đây là kế hoạch, chưa triển khai CRM/VPN/TLS/receiver.

Tiếp theo: tài khoản/phiên/role assignment thực → Policy gate với DB và recheck commit/stream → Caddy/TLS + scanner/job/upload lifecycle → inventory/context/scenario/control/risk/review/retest/report → lỗi/restore/tài nguyên và CRM lab. Chưa có auth API, upload API, scanner daemon, kiểm cạnh tranh nhiều kết nối hoặc workflow end-to-end. FLOW-01…10, T01–T24 và VALID-G-01 giữ **NOT_RUN**; A/B trống, chưa có CRM evidence/calibration/SME approval; MF-03/MF-04 **NOT_RANKED**. **Bước 06 IN_PROGRESS**, không đóng bước từ kết quả nền.
