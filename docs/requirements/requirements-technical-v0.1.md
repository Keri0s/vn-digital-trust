# VN Digital Trust — Technical Requirements v0.1

**Trạng thái:** Baseline thiết kế cho prototype, 2026-10-05.

**Phạm vi:** Cybersecurity readiness, asset inventory và risk management cho một SME. [Quyết định phạm vi](../scope/technical-first-scope-v0.1.md) là nguồn ưu tiên cho v0.1; các tài liệu pháp lý trước đây được giữ làm lịch sử discovery.

Các mức **MUST / SHOULD / COULD** là ưu tiên xây prototype, không khẳng định nhu cầu đã được SME thực tế xác nhận. Mã TFR tách biệt với mã FR của baseline pháp lý trước đó.

## 1. Actor và trách nhiệm

| Actor | Trách nhiệm v0.1 |
| --- | --- |
| Organization Administrator | Cấu hình tổ chức, tài khoản và quyền. |
| IT/Security | Ghi nhận tài sản, tình huống rủi ro, control và evidence; theo dõi khắc phục. |
| Risk Owner / Management | Xác nhận tác động kinh doanh, xem ưu tiên, duyệt hoặc chấp nhận rủi ro nếu được cấp quyền. |
| Consultant/Reviewer (tùy chọn) | Xem assessment và evidence, yêu cầu bổ sung, điều chỉnh có lý do. |

Một người có thể giữ nhiều vai trò; đối tượng thử nghiệm có thể là SME tự đánh giá. Consultant-assisted workflow vẫn là giả thuyết cần kiểm chứng với người dùng.

## 2. Functional requirements

### A. Tổ chức, tài khoản và quyền

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-AUTH-001 | MUST | Tạo đúng một organization profile khi triển khai; không có thao tác tạo SME thứ hai trong cùng deployment. |
| TFR-AUTH-002 | MUST | Yêu cầu người dùng đăng nhập để vào chức năng được bảo vệ. |
| TFR-AUTH-003 | MUST | Quản trị viên tạo/vô hiệu hóa user và gán vai trò; hệ thống thực thi RBAC khi đọc/sửa dữ liệu. |
| TFR-AUTH-004 | MUST | Ghi actor cho thay đổi về quyền, kết quả đánh giá, evidence và quyết định xử lý rủi ro. |

### B. Hệ thống và tài sản

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-INV-001 | MUST | Ghi nhận InformationSystem với tên, mục đích, owner, hosting, mức phơi lộ và mức quan trọng; cho phép “chưa rõ” khi thiếu thông tin. |
| TFR-INV-002 | MUST | Ghi nhận Asset với loại, owner, trạng thái và hệ thống liên quan. |
| TFR-INV-003 | MUST | Liên kết nhiều Asset với nhiều InformationSystem và giữ quan hệ khi cập nhật inventory. |
| TFR-INV-004 | MUST | Ghi nhận giá trị business/criticality của tài sản hoặc hệ thống cùng người đánh giá và lý do. |
| TFR-INV-005 | SHOULD | Cho phép tìm, lọc, cập nhật và đánh dấu ngừng sử dụng mà không làm mất lịch sử assessment. |

### C. Bối cảnh dữ liệu và nhà cung cấp

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-CTX-001 | MUST | Ghi nhận DataAsset hoặc nhóm dữ liệu quan trọng, mức nhạy cảm theo tiêu chí nội bộ và hệ thống lưu/xử lý. |
| TFR-CTX-002 | MUST | Ghi nhận Vendor/cloud/SaaS provider và liên kết với hệ thống hoặc tài sản phụ thuộc. |
| TFR-CTX-003 | MUST | Dùng bối cảnh dữ liệu và vendor làm đầu vào cho mô tả tác động rủi ro; không tự suy ra nghĩa vụ pháp lý. |
| TFR-CTX-004 | SHOULD | Hiển thị thông tin bối cảnh còn thiếu để người dùng xác minh trước khi đánh giá rủi ro. |

### D. Risk register và phương pháp đánh giá

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-RISK-001 | MUST | Tạo RiskScenario gắn với tài sản/hệ thống, mô tả sự kiện có thể xảy ra, điều kiện/điểm yếu liên quan và hậu quả. |
| TFR-RISK-002 | MUST | Gán owner cho từng RiskScenario và ghi nguồn thông tin/giả định của mô tả. |
| TFR-RISK-003 | MUST | Ghi likelihood, impact, lý do và mức tin cậy hoặc “chưa đủ dữ liệu” cho mỗi lần RiskEvaluation. |
| TFR-RISK-004 | MUST | Xếp mức rủi ro bằng một phương pháp/ma trận có version, tiêu chí công khai và kết quả lặp lại với cùng đầu vào. |
| TFR-RISK-005 | MUST | Nếu thiếu likelihood/impact hoặc điều kiện đánh giá thiết yếu, trả NEEDS_REVIEW; không tự gán mức rủi ro thấp. |
| TFR-RISK-006 | MUST | Giữ lịch sử các lần RiskEvaluation và bản mô tả scenario/context đã dùng; cập nhật inventory, scenario, control hoặc phương pháp không sửa đè kết quả cũ. |
| TFR-RISK-007 | MUST | Hiển thị risk register theo owner, hệ thống/tài sản, mức rủi ro, trạng thái xử lý và lần đánh giá gần nhất. |
| TFR-RISK-008 | SHOULD | Cho phép reviewer nhận xét/điều chỉnh một lần đánh giá với lý do, actor và thời điểm. |

Một phát hiện kỹ thuật hoặc điểm yếu được nhập thủ công là thông tin đầu vào; nó không tự động tạo mức rủi ro.

### E. Control và triển khai

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-CTL-001 | MUST | Duy trì một catalog control mẫu có mục tiêu, mô tả, kỳ vọng bằng chứng và tiêu chí đánh giá có version. |
| TFR-CTL-002 | MUST | Ghi nhận ControlImplementation của một control trên tài sản/hệ thống cụ thể, owner và trạng thái khai báo. |
| TFR-CTL-003 | MUST | Liên kết RiskScenario với một hoặc nhiều control được chọn và ghi lý do; một control có thể chưa được triển khai trên tài sản/hệ thống. |
| TFR-CTL-004 | MUST | Truy vết risk → control implementation → evidence → kết quả kiểm tra. |
| TFR-CTL-005 | SHOULD | Cho phép đánh dấu control không phù hợp với một phạm vi cụ thể khi có lý do; không mặc định tất cả control áp dụng cho mọi tài sản. |

### F. Evidence và kiểm tra control

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-EVD-001 | MUST | Tải lên hoặc đăng ký evidence thủ công, gồm tệp cấu hình, ảnh, log, báo cáo scanner hoặc tài liệu quy trình. |
| TFR-EVD-002 | MUST | Ghi nguồn, owner, thời gian thu thập, khoảng hiệu lực nếu có và trạng thái UNVERIFIED/VERIFIED/REJECTED/EXPIRED. |
| TFR-EVD-003 | MUST | Liên kết một evidence revision với nhiều control implementation khi phù hợp. |
| TFR-EVD-004 | MUST | Giữ đúng revision đã dùng trong một assessment khi evidence được thay thế. |
| TFR-EVD-005 | MUST | Đánh giá control theo tiêu chí và evidence: SATISFIED, PARTIALLY_SATISFIED, NOT_SATISFIED, INSUFFICIENT_EVIDENCE hoặc NOT_ASSESSED. |
| TFR-EVD-006 | MUST | Thiếu hoặc chưa xác minh evidence không được tự đổi thành NOT_SATISFIED. Evidence hợp lệ chứng minh tiêu chí không đạt mới có thể tạo control failure. |
| TFR-EVD-007 | SHOULD | Lưu hash cho tệp evidence và hiển thị khi bản gốc thay đổi. |

### G. Gap, quyết định xử lý và đánh giá lại

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-TRT-001 | MUST | Tạo EVIDENCE_GAP khi thiếu bằng chứng và CONTROL_GAP khi biện pháp không đạt; liên kết với control result và risk liên quan. |
| TFR-TRT-002 | MUST | Ưu tiên xử lý bằng quy tắc giải thích được dựa trên RiskEvaluation và trạng thái control/evidence; không dùng điểm số ẩn. |
| TFR-TRT-003 | MUST | Tạo TreatmentTask với owner, hành động, deadline, trạng thái và bằng chứng cần cho retest. |
| TFR-TRT-004 | MUST | Chỉ người có quyền mới được chấp nhận rủi ro, kèm lý do, phạm vi và thời điểm; việc chấp nhận không chuyển control thất bại thành SATISFIED. |
| TFR-TRT-005 | MUST | Sau xử lý, cho phép nộp evidence mới và tạo assessment/re-evaluation mới; giữ lịch sử trước đó. |
| TFR-TRT-006 | SHOULD | Hiển thị hướng xử lý được biên soạn cho các gap mẫu và nêu rõ khi chưa có hướng phù hợp. |

### H. Báo cáo và audit

| ID | Ưu tiên | Yêu cầu |
| --- | --- | --- |
| TFR-RPT-001 | MUST | Tạo báo cáo tại một thời điểm với phạm vi, inventory liên quan, risk register, phương pháp/version, control/evidence status, gap và task. |
| TFR-RPT-002 | MUST | Từ một finding, người xem truy được risk scenario, tài sản/hệ thống, đánh giá, control, evidence và quyết định xử lý. |
| TFR-RPT-003 | MUST | Hiển thị dữ liệu chưa rõ, evidence chưa xác minh và kết quả chưa review; không trình bày báo cáo như chứng nhận tuân thủ pháp luật. |
| TFR-AUD-001 | MUST | Lưu actor, action, target, time và giá trị trước/sau khi phù hợp cho thay đổi quan trọng. |
| TFR-AUD-002 | SHOULD | Có phần tóm tắt dễ đọc cho management về rủi ro ưu tiên và việc đang quá hạn. |

## 3. Non-functional requirements

| ID | Yêu cầu |
| --- | --- |
| TNFR-SEC-001 | Kiểm tra authentication/authorization trên mọi thao tác được bảo vệ; không lưu mật khẩu/token dạng plaintext. |
| TNFR-TRC-001 | Mỗi kết quả có thể truy ngược tới input snapshot, phương pháp/version, người đánh giá, control và evidence revision. |
| TNFR-EXP-001 | Hiển thị lý do của risk level, control result và ưu tiên gap bằng ngôn ngữ người dùng SME hiểu được. |
| TNFR-REP-001 | Cùng input và cùng phiên bản phương pháp/tiêu chí tạo cùng kết quả tự động; thay đổi phiên bản không sửa assessment cũ. |
| TNFR-USA-001 | Người dùng có thể chọn “chưa rõ” thay vì buộc trả lời có/không khi thiếu dữ kiện. |
| TNFR-DEP-001 | Prototype chạy được trong môi trường phát triển cục bộ với nguồn lực máy cá nhân khoảng 16 GB RAM. |
| TNFR-PRV-001 | Evidence và thông tin tài sản chỉ được người có quyền xem; dữ liệu thử nghiệm mặc định là synthetic/controlled. |

## 4. Nguồn và mức độ kiểm chứng

| Nhóm | Cơ sở | Cần kiểm chứng |
| --- | --- | --- |
| Tổ chức/RBAC | Quyết định single-tenant và nhiều người dùng từ discovery trước | Vai trò thực tế và quyền tối thiểu. |
| Inventory và context | [Project Charter §6–8](../research/project-charter.md); [Problem Discovery §9–13](../research/problem-discovery-v0.1.md) | SME có thể thu thập những thông tin nào, mất bao lâu (H3). |
| Risk scenario/evaluation | Quyết định phạm vi kỹ thuật ngày 2026-10-05; charter có hướng risk-based | Phương pháp đánh giá, rubric và mức ưu tiên có được người dùng hiểu, áp dụng nhất quán không. |
| Control/evidence/gap | Charter §6–10; W-004/W-005 trong Assumptions Log | Tiêu chí đánh giá control và khả năng xác minh evidence trong scenario. |
| Self-assessment và reviewer | Quyết định thiết kế; H4/A-007 chưa kiểm chứng | Thử self-service và consultant-assisted với người dùng. |

Các trường và trạng thái là đề xuất để prototype chạy hết luồng; không phải phát biểu rằng doanh nghiệp thực tế hoặc pháp luật yêu cầu đúng những biểu mẫu này.

## 5. Acceptance scenarios tối thiểu

1. ABC Trading giả lập ghi nhận CRM, tài sản hỗ trợ, dữ liệu khách hàng và vendor; tạo một tình huống truy cập trái phép có owner.
2. Lần đánh giá rủi ro ghi likelihood/impact cùng lý do; cùng input/method version cho cùng mức rủi ro.
3. Thiếu impact hoặc chưa xác định asset owner được hiển thị là thiếu dữ kiện và cần review; hệ thống không tự xếp LOW.
4. Control MFA không có evidence dùng được → INSUFFICIENT_EVIDENCE và EVIDENCE_GAP; evidence xác minh cho thấy MFA tắt → NOT_SATISFIED và CONTROL_GAP.
5. Thêm evidence và retest tạo kết quả mới; report cũ vẫn tham chiếu đúng evidence và phương pháp cũ.
6. User không có quyền không thể sửa role hoặc chấp nhận rủi ro; risk acceptance được phép vẫn không thay đổi kết quả control.
7. Report hiển thị lý do và giới hạn của kết quả, không có điểm “tuân thủ pháp luật”.

## 6. Ngoài phạm vi

Regulatory applicability engine, legal requirement repository, nộp hồ sơ pháp lý và mapping nghĩa vụ pháp lý; full SOC/SIEM, phát hiện real-time, quét hạ tầng diện rộng, AI quyết định rủi ro và multi-tenant SaaS. Chúng không phải cam kết roadmap.
