# VN Digital Trust — Use Cases v0.1

**Trạng thái:** Bản thiết kế use case cho prototype, ngày 2026-10-03.  
**Phạm vi:** Một deployment phục vụ một SME; nhân sự SME tự đánh giá là luồng chính; consultant review là tùy chọn.

## 1. Cách đọc và cơ sở của tài liệu

Một **use case** mô tả mục tiêu của một người dùng, các bước người đó và hệ thống thực hiện, kết quả, cùng những tình huống cần xử lý khi luồng chính không diễn ra. Đây chưa phải thiết kế màn hình, API hay cơ sở dữ liệu.

Tài liệu này dựa trên [Requirements Discovery v0.1](../requirements/requirements-discovery-v0.1.md), [bản đối chiếu với research](../requirements/requirements-research-alignment-review.md), `project-charter.md`, `problem-discovery-v0.1.md`, `hypotheses.md`, `assumptions-log.md` trong `D:/Projects/vn-digital-trust/docs/research`, và các quyết định đã chốt trong cuộc trò chuyện.

**Các giới hạn cần giữ:**

- Self-assessment là lựa chọn để xây prototype; nhu cầu thật của SME vẫn thuộc giả thuyết H4/A-007 và cần kiểm chứng.
- Applicability chỉ sử dụng **tập requirement và rule mẫu đã được rà soát**. Với context ngoài phạm vi mẫu hoặc dữ liệu chưa rõ, hệ thống báo **CẦN_XEM_XÉT**; không suy ra “không áp dụng”.
- “Có khả năng áp dụng” là kết quả hỗ trợ quyết định, không phải kết luận pháp lý. ISO/IEC controls và yêu cầu pháp luật không mặc nhiên tương đương nhau.
- Kết quả control phải phân biệt thiếu bằng chứng với bằng chứng cho thấy control chưa đạt. Câu trả lời questionnaire không tự chứng minh control đã đạt.
- Consultant review một assessment khác với người rà soát nội dung pháp lý, rule và mapping trước khi dùng cho prototype.
- Các mã trạng thái dưới đây là tên làm việc; domain model có thể đổi tên mà vẫn giữ ý nghĩa nghiệp vụ.

### Actor

| Mã | Vai trò | Quyền chính trong use case |
| --- | --- | --- |
| A1 | Quản trị tổ chức | Cấu hình một tổ chức, cấp tài khoản và vai trò. |
| A2 | IT/Security | Nhập hệ thống, tài sản, bằng chứng kỹ thuật, xử lý remediation. |
| A3 | Compliance/Privacy | Nhập hoạt động xử lý dữ liệu, vendor, trả lời questionnaire, cung cấp bằng chứng tài liệu. |
| A4 | Management | Xem báo cáo, ra quyết định chấp nhận rủi ro nếu được cấp quyền. |
| A5 | Consultant/Reviewer, tùy chọn | Kiểm tra bằng chứng và kết quả sơ bộ, yêu cầu bổ sung, điều chỉnh có lý do. |
| K1 | Người duy trì nội dung mẫu | Rà soát nguồn, rule, requirement, control và mapping trước khi đưa gói nội dung mẫu vào prototype. Đây là vai trò quản trị nội dung, không nhất thiết là tài khoản SME trong ứng dụng. |

Một người có thể có nhiều vai trò được cấp quyền. Hệ thống không có thao tác “tạo công ty” hoặc workspace nhiều khách hàng.

## 2. Bản đồ use case

| Mã | Mục tiêu | Actor chính | Nhóm FR liên quan |
| --- | --- | --- | --- |
| UC-01 | Thiết lập deployment và tổ chức | A1 | AUTH, ORG |
| UC-02 | Quản lý tài khoản và quyền | A1 | AUTH, AUD |
| UC-03 | Ghi nhận bối cảnh tổ chức | A2, A3 | ORG, SYS, AST, DATA, VND |
| UC-04 | Trả lời questionnaire | A3, A2 | QST |
| UC-05 | Xác định requirement có khả năng áp dụng | A3 | APP, REQ, QST |
| UC-06 | Ghi nhận và kiểm tra evidence | A2, A3; A5 nếu có | CTL, EVD, TECH, AUD |
| UC-07 | Tạo đánh giá control sơ bộ | A2, A3 | ASMT, EVD, CTL |
| UC-08 | Review và điều chỉnh kết quả | A5, tùy chọn | ASMT, APP, AUD |
| UC-09 | Xác định gap và lập remediation | A2, A3 | GAP, REM |
| UC-10 | Cập nhật evidence và đánh giá lại | A2, A3 | REM, EVD, ASMT, AUD |
| UC-11 | Xem và xuất readiness report | A4; A1, A2, A3 theo quyền | RPT |
| UC-12 | Duy trì gói rule và mapping mẫu | K1 | REQ, APP, CTL |

Luồng chính: **UC-01 → UC-02/03 → UC-04 → UC-05 → UC-06 → UC-07 → UC-09 → UC-10 → UC-11**. UC-08 có thể xen sau UC-05, UC-06 hoặc UC-07 khi có reviewer. UC-12 là điều kiện chuẩn bị nội dung, không phải bước SME phải thực hiện.

## 3. Chi tiết use cases

### UC-01 — Thiết lập deployment và tổ chức

**Mục tiêu:** Có một tổ chức và tài khoản quản trị đầu tiên để bắt đầu assessment.  
**Actor chính:** A1.  
**Kích hoạt:** Deployment mới được cài đặt.  
**Tiền điều kiện:** Chưa có organization profile trong deployment; người thực hiện có quyền khởi tạo hệ thống.  
**Hậu điều kiện thành công:** Chỉ một organization profile tồn tại; tài khoản admin có thể đăng nhập; thao tác khởi tạo được ghi nhận.  
**FR:** FR-AUTH-001 đến 005, FR-ORG-001 đến 003.

**Luồng chính**

1. Người cài đặt khởi tạo tài khoản admin đầu tiên bằng cơ chế setup được bảo vệ.
2. Admin đăng nhập và nhập tên tổ chức, ngành, quy mô, hoạt động và thông tin liên hệ cần thiết.
3. Hệ thống kiểm tra dữ liệu bắt buộc và lưu một organization profile.
4. Hệ thống đánh dấu initial setup hoàn tất; admin có thể chỉnh profile trong phần cài đặt sau này.

**Nhánh/ngoại lệ**

- Thiếu thông tin bắt buộc: hệ thống chỉ rõ trường cần bổ sung và chưa hoàn tất setup.
- Đã có profile: hệ thống chuyển đến chức năng cập nhật profile theo quyền; không tạo organization thứ hai.
- Tài khoản admin không xác thực được: không cho truy cập dữ liệu tổ chức.

### UC-02 — Quản lý tài khoản và quyền

**Mục tiêu:** Mỗi người có tài khoản riêng và chỉ truy cập phần được phép.  
**Actor chính:** A1.  
**Tiền điều kiện:** UC-01 hoàn tất; admin đã đăng nhập.  
**Hậu điều kiện thành công:** Tài khoản/vai trò được cập nhật; thay đổi quyền có audit record.  
**FR:** FR-AUTH-001 đến 005, FR-AUD-001 đến 002.

**Luồng chính**

1. Admin tạo tài khoản cho IT/Security, Compliance/Privacy, Management hoặc reviewer được mời.
2. Admin gán một hay nhiều vai trò có phạm vi quyền phù hợp.
3. Hệ thống lưu actor, thời gian, quyền cũ và quyền mới.
4. Người dùng đăng nhập; hệ thống chỉ hiển thị và cho thực hiện chức năng được cấp quyền.

**Nhánh/ngoại lệ**

- Tài khoản bị vô hiệu hóa: đăng nhập hoặc thao tác tiếp theo bị từ chối theo chính sách phiên.
- Người dùng cố truy cập chức năng không được phép: hệ thống từ chối và không thay đổi dữ liệu.
- Thu hồi quyền reviewer: reviewer không còn xem hay sửa assessment; các nhận xét cũ vẫn được giữ để truy vết.

### UC-03 — Ghi nhận bối cảnh tổ chức

**Mục tiêu:** Tạo thông tin thực tế đầu vào cho applicability và assessment.  
**Actor chính:** A2, A3.  
**Tiền điều kiện:** Người dùng đã đăng nhập và có quyền cập nhật từng loại thông tin.  
**Hậu điều kiện thành công:** Systems, assets, data processing và vendors được lưu với quan hệ đủ dùng cho scenario mẫu.  
**FR:** FR-ORG-002/003, FR-SYS-001 đến 003, FR-AST-001 đến 004, FR-DATA-001 đến 004, FR-VND-001 đến 003.

**Luồng chính**

1. A2 ghi nhận các information systems, mục đích, chủ sở hữu, hosting, mức độ phơi lộ và dữ liệu xử lý.
2. A2 ghi nhận tài sản IT và liên kết chúng với systems.
3. A3 ghi nhận nhóm dữ liệu và hoạt động xử lý: mục đích, vị trí lưu, bên xử lý, bên thứ ba và dấu hiệu chuyển dữ liệu ra nước ngoài.
4. A3 ghi nhận vendor, dịch vụ cung cấp, quyền tiếp cận dữ liệu và systems liên quan.
5. Hệ thống hiển thị bối cảnh đã ghi nhận để người dùng kiểm tra trước khi làm questionnaire.

**Nhánh/ngoại lệ**

- Không biết giá trị của một thuộc tính quan trọng: ghi “chưa rõ/cần xác minh” hoặc để thiếu có cảnh báo; không mặc định thành “không”.
- Chưa có system/vendor được tham chiếu: yêu cầu tạo hoặc chọn bản ghi hợp lệ trước khi liên kết.
- Context đổi sau một lần assessment: lần đánh giá cũ giữ snapshot; lần chạy mới dùng dữ liệu mới và version tương ứng.

### UC-04 — Trả lời questionnaire

**Mục tiêu:** Thu thập các sự kiện có cấu trúc mà người dùng SME có thể trả lời.  
**Actor chính:** A3; A2 hỗ trợ câu kỹ thuật.  
**Tiền điều kiện:** Có organization profile; questionnaire mẫu đã được nạp.  
**Hậu điều kiện thành công:** Một bộ câu trả lời có cấu trúc và version được lưu.  
**FR:** FR-QST-001 đến 005.

**Luồng chính**

1. Người dùng bắt đầu questionnaire cho assessment hiện tại.
2. Hệ thống hiển thị câu hỏi phù hợp dựa trên câu trả lời trước, ví dụ chỉ hỏi chi tiết chuyển dữ liệu khi có hoạt động xử lý liên quan.
3. Người dùng nhập câu trả lời dạng yes/no, lựa chọn, số, ngày hoặc nhiều lựa chọn và ghi chú nếu cần.
4. Hệ thống kiểm tra câu trả lời bắt buộc, lưu questionnaire version và cho người dùng kiểm tra lại.
5. Người dùng xác nhận các câu trả lời để chạy applicability.

**Nhánh/ngoại lệ**

- Chưa chắc câu trả lời: chọn “chưa rõ” nếu câu hỏi hỗ trợ; hệ thống chuyển tình huống liên quan sang cần xem xét.
- Đổi câu trả lời làm thay đổi nhánh: hệ thống đánh dấu các câu trả lời phụ thuộc cần xem lại, không âm thầm dùng dữ liệu cũ.
- Lưu tạm và tiếp tục sau là tính năng SHOULD; nếu prototype chưa hỗ trợ, giao diện phải nêu rõ trước khi người dùng bắt đầu.

### UC-05 — Xác định requirement có khả năng áp dụng

**Mục tiêu:** Cho người dùng thấy requirement mẫu nào có khả năng liên quan và vì sao.  
**Actor chính:** A3. **Actor hỗ trợ:** Rule engine.  
**Tiền điều kiện:** Context và questionnaire đủ cho những rule mẫu; gói nội dung từ UC-12 đã được nạp.  
**Hậu điều kiện thành công:** Lưu kết quả, dữ kiện kích hoạt, rule/version và requirement/version cho assessment hiện tại.  
**FR:** FR-APP-001 đến 007, FR-REQ-001 đến 005, FR-QST-005.

**Luồng chính**

1. A3 chọn phạm vi assessment và yêu cầu chạy applicability.
2. Hệ thống chụp snapshot bối cảnh và dùng rule deterministic trong gói nội dung đã rà soát.
3. Với mỗi kết quả, hệ thống hiển thị requirement **có khả năng áp dụng**, dữ kiện liên quan, ID/version của rule và tham chiếu nguồn của requirement.
4. A3 xem kết quả và ghi nhận điểm cần xác minh với người phụ trách hoặc reviewer.

**Nhánh/ngoại lệ**

- Dữ liệu cần thiết chưa rõ: kết quả là CẦN_XEM_XÉT cùng lý do, không tự coi là không áp dụng.
- Context nằm ngoài rule mẫu: hệ thống nêu giới hạn bao phủ và yêu cầu người dùng đánh giá thủ công; không kết luận pháp lý.
- Rule, nguồn hoặc mapping thiếu version/nguồn: không công bố kết quả như đã được rà soát; báo lỗi nội dung để xử lý.
- Reviewer có thể ghi nhận ý kiến về applicability nếu được cấp quyền; thay đổi kết quả phải có lý do và audit.

### UC-06 — Ghi nhận và kiểm tra evidence

**Mục tiêu:** Gắn bằng chứng thực tế với control và expected evidence.  
**Actor chính:** A2, A3. **Actor hỗ trợ:** A5 nếu được mời.  
**Tiền điều kiện:** Có các control liên quan và kỳ vọng về evidence.  
**Hậu điều kiện thành công:** Evidence có metadata, trạng thái kiểm tra, quan hệ với control và lịch sử thay đổi.  
**FR:** FR-CTL-001 đến 003, FR-EVD-001 đến 007, FR-TECH-001/002, FR-AUD-001/002.

**Luồng chính**

1. Người dùng mở control và xem mục tiêu, tiêu chí đánh giá, expected evidence.
2. Người dùng tải lên hoặc đăng ký evidence, bao gồm tệp, đường dẫn hồ sơ hoặc output kỹ thuật nhập thủ công theo phạm vi prototype.
3. Người dùng nhập nguồn, người phụ trách, thời gian thu thập và hiệu lực nếu có.
4. Hệ thống liên kết một evidence với một hay nhiều control/requirement phù hợp và ghi nhận người thao tác.
5. Người có quyền kiểm tra evidence và đặt trạng thái chưa kiểm tra, đã xác minh, từ chối hoặc hết hiệu lực.

**Nhánh/ngoại lệ**

- Evidence chưa được cung cấp: hiển thị “thiếu expected evidence”; không kết luận control thất bại.
- Evidence hết hạn hoặc bị từ chối: không dùng làm bằng chứng đạt control nếu tiêu chí đòi evidence hợp lệ.
- Evidence được thay thế: giữ tham chiếu bản cũ nếu chức năng versioning được triển khai; assessment cũ vẫn chỉ tới bản đã dùng.
- Output scanner/log nhập thủ công vẫn cần nguồn và thời gian; việc nhập không đồng nghĩa với kiểm chứng tự động.

### UC-07 — Tạo đánh giá control sơ bộ

**Mục tiêu:** Xác định trạng thái sẵn sàng của từng control trong một assessment.  
**Actor chính:** A2 hoặc A3 theo quyền. **Actor hỗ trợ:** Assessment engine.  
**Tiền điều kiện:** Có phạm vi, control/criteria và evidence liên quan.  
**Hậu điều kiện thành công:** Mỗi control có trạng thái sơ bộ, reasoning và references được lưu.  
**FR:** FR-ASMT-001 đến 005 và FR-ASMT-008, FR-CTL-003/005, FR-EVD-001 đến 006.

**Luồng chính**

1. Người dùng tạo assessment cho một phạm vi cụ thể.
2. Hệ thống chụp version của requirement, rule, control, mapping, criteria, questionnaire và evidence được sử dụng khi có dữ liệu này.
3. Hệ thống so sánh evidence hợp lệ với tiêu chí của control và tạo trạng thái sơ bộ.
4. Hệ thống hiển thị reasoning và các liên kết requirement → control → expected/provided evidence.
5. Người dùng xem kết quả; nếu có reviewer, có thể gửi cho UC-08.

**Nhánh/ngoại lệ**

- Chưa có evidence cần thiết hoặc evidence chưa xác minh: INSUFFICIENT_EVIDENCE; không suy ra NOT_SATISFIED.
- Evidence cho thấy tiêu chí không đạt: NOT_SATISFIED hoặc PARTIALLY_SATISFIED theo tiêu chí đã định.
- Control chưa được xem xét: NOT_ASSESSED.
- NOT_APPLICABLE chỉ được dùng khi có cơ sở áp dụng đã xem xét rõ; context ngoài rule mẫu không đủ để gán trạng thái này.
- Câu trả lời “có MFA” trong questionnaire không đủ để gán SATISFIED nếu control cần bằng chứng cấu hình.

### UC-08 — Review và điều chỉnh kết quả (tùy chọn)

**Mục tiêu:** Consultant kiểm tra assessment mà vẫn giữ được kết quả gốc và lý do thay đổi.  
**Actor chính:** A5.  
**Tiền điều kiện:** Reviewer được cấp quyền; đã có kết quả hoặc evidence để review.  
**Hậu điều kiện thành công:** Nhận xét/yêu cầu bổ sung hoặc kết quả điều chỉnh được ghi nhận có audit.  
**FR:** FR-APP-005, FR-EVD-005, FR-ASMT-005 đến 007, FR-AUD-001/002.

**Luồng chính**

1. Reviewer xem phạm vi, rule reasoning, control criteria và evidence liên quan.
2. Reviewer xác nhận kết quả hoặc yêu cầu bổ sung evidence.
3. Nếu điều chỉnh kết quả sơ bộ, reviewer chọn trạng thái mới và ghi lý do cụ thể.
4. Hệ thống lưu kết quả cũ, kết quả mới, reviewer, thời điểm, lý do và evidence tham chiếu.

**Nhánh/ngoại lệ**

- Không có reviewer: SME vẫn tiếp tục self-assessment; report ghi rõ trạng thái review của kết quả.
- Reviewer thiếu quyền hoặc không nhập lý do override: hệ thống từ chối thay đổi.
- Reviewer gặp câu hỏi pháp lý ngoài nội dung đã rà soát: ghi “cần xem xét chuyên môn”; không tự xác nhận applicability.

### UC-09 — Xác định gap và lập remediation

**Mục tiêu:** Biến kết quả assessment thành việc cần xử lý có thể theo dõi.  
**Actor chính:** A2, A3; A4 cho quyết định chấp nhận rủi ro nếu được cấp quyền.  
**Tiền điều kiện:** UC-07 đã tạo kết quả; UC-08 hoàn tất nếu review được yêu cầu trong scenario.  
**Hậu điều kiện thành công:** Gap có loại, mức ưu tiên, hành động đề xuất, người phụ trách và lịch xử lý.  
**FR:** FR-GAP-001 đến 004, FR-REM-001 đến 003 và FR-REM-006/007.

**Luồng chính**

1. Hệ thống tạo EVIDENCE_GAP cho bằng chứng thiếu/chưa đủ và CONTROL_GAP cho control không đạt; giữ nguồn reasoning.
2. Hệ thống ưu tiên gap theo tiêu chí minh bạch trong gói nội dung hoặc cấu hình prototype.
3. Người dùng xem hướng khắc phục đã được biên soạn, lý do và evidence cần nộp khi retest.
4. Người dùng tạo task, chỉ định owner, priority, due date và trạng thái.
5. Hệ thống giữ liên kết gap → assessment → control → requirement → evidence.

**Nhánh/ngoại lệ**

- Chưa rõ nguyên nhân: task có thể giao xác minh trước khi chọn biện pháp khắc phục.
- A4 chấp nhận rủi ro nếu có quyền: ghi người quyết định, thời gian, lý do; gap vẫn hiển thị trạng thái accepted risk, control không tự chuyển thành SATISFIED.
- Chưa có recommendation phù hợp: nêu cần người có chuyên môn xác định; không tạo hướng xử lý giả.

### UC-10 — Cập nhật evidence và đánh giá lại

**Mục tiêu:** Xác nhận kết quả sau remediation và bảo toàn lịch sử.  
**Actor chính:** A2, A3. **Actor hỗ trợ:** A5 nếu được mời.  
**Tiền điều kiện:** Có task/gap và evidence hoặc thay đổi cần kiểm tra lại.  
**Hậu điều kiện thành công:** Có kết quả reassessment, gap/task được cập nhật và lịch sử cũ được giữ.  
**FR:** FR-REM-004/005, FR-EVD-002 đến 007, FR-ASMT-001 đến 008, FR-AUD-001/002.

**Luồng chính**

1. Owner ghi việc đã thực hiện và cung cấp evidence mới.
2. Owner chuyển task sang READY_FOR_RETEST.
3. Người có quyền thực hiện retest theo criteria và nội dung version được chỉ định cho lần đánh giá mới.
4. Hệ thống lưu kết quả mới bên cạnh kết quả cũ; không sửa đè assessment lịch sử.
5. Nếu đạt điều kiện đóng, người có quyền chuyển task/gap sang CLOSED kèm thời điểm và căn cứ.

**Nhánh/ngoại lệ**

- Evidence mới vẫn thiếu: giữ EVIDENCE_GAP và yêu cầu bổ sung.
- Retest cho thấy control vẫn chưa đạt: giữ CONTROL_GAP hoặc cập nhật trạng thái theo tiêu chí.
- Rule/criteria đã đổi: bản đánh giá mới phải chỉ rõ version mới; không âm thầm diễn giải lại kết quả cũ.

### UC-11 — Xem và xuất readiness report

**Mục tiêu:** Management thấy phạm vi, kết quả, bằng chứng và các việc cần quyết định.  
**Actor chính:** A4; các actor khác theo quyền.  
**Tiền điều kiện:** Có ít nhất một assessment đã lưu.  
**Hậu điều kiện thành công:** Report cho một assessment cụ thể được tạo với traceability và giới hạn diễn giải.  
**FR:** FR-RPT-001 đến 006, FR-GAP-003, FR-ASMT-005.

**Luồng chính**

1. Người dùng chọn assessment và thời điểm cần báo cáo.
2. Hệ thống tổng hợp phạm vi, facts, requirement có khả năng áp dụng, phiên bản nội dung, trạng thái control/evidence, gap và task.
3. Hệ thống cho phép xem đường dẫn từ finding đến requirement, control, evidence và reasoning.
4. Hệ thống hiển thị rõ phần chưa có dữ liệu, chưa được review và phạm vi rule mẫu.
5. Người dùng xem hoặc xuất report theo định dạng prototype hỗ trợ.

**Nhánh/ngoại lệ**

- Một số kết quả còn CẦN_XEM_XÉT/INSUFFICIENT_EVIDENCE: report giữ nguyên trạng thái và lý do.
- Không có reviewer: report thể hiện đây là kết quả self-assessment/preliminary.
- Report nêu rõ đây là đánh giá readiness trong phạm vi đã chọn, không phải chứng nhận tuân thủ hay ý kiến pháp lý cuối cùng.

### UC-12 — Duy trì gói rule và mapping mẫu

**Mục tiêu:** Chỉ dùng nội dung có nguồn và giới hạn rõ trong prototype.  
**Actor chính:** K1, có thể là nhóm đồ án cùng người rà soát có chuyên môn.  
**Tiền điều kiện:** Đã chọn phạm vi pháp lý và scenario mẫu để nghiên cứu.  
**Hậu điều kiện thành công:** Gói requirement/rule/control/mapping có version, nguồn, ngày rà soát và giới hạn áp dụng, dùng được trong UC-05/07.  
**FR:** FR-APP-002/004/007, FR-REQ-001 đến 005, FR-CTL-001 đến 003 và FR-CTL-005; NFR-VRS-001, NFR-TST-001.

**Luồng chính**

1. K1 chọn một tập requirement mẫu và lưu nguồn, điều/khoản, hiệu lực, trạng thái cùng phạm vi áp dụng.
2. K1 mô tả rule đầu vào → kết quả mong đợi và các trường hợp “chưa rõ/ngoài phạm vi”.
3. K1 nối requirement với control, expected evidence và assessment criteria; ghi lý do mapping.
4. Nội dung được rà soát trước khi dùng trong scenario thử nghiệm; ghi vai trò/người rà soát, ngày, version và các điểm chưa giải quyết.
5. K1 chạy bộ ví dụ đầu vào/đầu ra cố định để xác nhận rule cho kết quả lặp lại.

**Nhánh/ngoại lệ**

- Chưa xác minh nguồn hoặc còn bất đồng về cách hiểu: giữ nội dung ở trạng thái draft, không xuất như kết luận đã review.
- Nguồn hết hiệu lực/thay thế/chuyển tiếp: tạo version mới và giữ version cũ cho assessment lịch sử.
- Một requirement liên quan nhiều control hoặc ngược lại: mapping hỗ trợ quan hệ nhiều-nhiều và giữ lý do.

UC-12 có thể được thực hiện bằng dữ liệu cấu hình/seed đã rà soát; v0.1 chưa cần màn hình biên tập pháp lý hoàn chỉnh.

## 4. Acceptance scenarios cho prototype

| ID | Dữ liệu đầu vào hoặc thao tác | Kết quả mong đợi |
| --- | --- | --- |
| AC-01 | Deployment mới, admin hoàn tất setup | Có đúng một organization profile; user thường không thấy thao tác tạo organization mới. |
| AC-02 | IT user thử đổi role của người khác | Bị từ chối; không thay đổi quyền. |
| AC-03 | Câu trả lời questionnaire chuyển từ “không” sang “có” về xử lý dữ liệu | Câu hỏi phụ xuất hiện và các câu trả lời phụ thuộc được rà soát lại. |
| AC-04 | Một bộ facts khớp rule mẫu đã review | Kết quả applicability đúng expected output, có rule ID/version và giải thích. |
| AC-05 | Facts thiếu hoặc ngoài phạm vi rule mẫu | Hiện CẦN_XEM_XÉT và lý do; không tự gán NOT_APPLICABLE. |
| AC-06 | Control yêu cầu backup evidence nhưng chưa nộp evidence | INSUFFICIENT_EVIDENCE và EVIDENCE_GAP; không kết luận backup không tồn tại. |
| AC-07 | Evidence hợp lệ chứng minh tiêu chí control không đạt | NOT_SATISFIED/PARTIALLY_SATISFIED theo criteria và CONTROL_GAP. |
| AC-08 | Reviewer override kết quả | Lưu kết quả trước/sau, reviewer, thời gian và lý do. |
| AC-09 | Thêm evidence, retest sau remediation | Có assessment mới; assessment và evidence tham chiếu cũ vẫn xem được. |
| AC-10 | Cùng input và cùng content version được chạy lại | Applicability và preliminary assessment cho kết quả nhất quán. |
| AC-11 | Xuất report | Có phạm vi, trạng thái evidence/gap/review, traceability và tuyên bố giới hạn pháp lý. |

**Scenario thử nghiệm:** ABC Trading trong `problem-discovery-v0.1.md` là doanh nghiệp giả lập để đi qua toàn bộ luồng. Expected legal/applicability outcomes phải được biên soạn và rà soát riêng trước khi dùng làm đáp án; tài liệu này không tự đặt ra kết quả pháp lý cho ABC Trading.

## 5. Các quyết định cần kiểm chứng qua nghiên cứu

1. **H4/A-007:** Người dùng SME có thực sự hoàn thành được self-assessment không, hay cần consultant hỗ trợ ở bước nào?
2. **H1/W-003:** Tập rule và mapping mẫu có đủ rõ để reviewer kiểm tra và cho kết quả nhất quán không?
3. **H3:** Data inventory trong UC-03 có quá nặng đối với SME không?
4. **H5/A-008:** Retest và evidence lifecycle có đem lại giá trị hơn một report tại một thời điểm không?
5. **Charter §12:** So sánh effort của scenario ABC Trading với quy trình spreadsheet/document thủ công; ghi quan sát và giới hạn thay vì giả định trước mức tiết kiệm.

## 6. Ngoài phạm vi use cases v0.1

Multi-tenant SaaS, dashboard consultant cho nhiều SME, full SOC/SIEM, quét hạ tầng diện rộng, tự động diễn giải pháp luật, AI quyết định compliance, nộp hồ sơ cho cơ quan nhà nước, nền tảng chứng nhận ISO hoàn chỉnh và GRC enterprise không thuộc prototype này. Đây là các giới hạn phạm vi, không phải cam kết triển khai trong phiên bản sau.
