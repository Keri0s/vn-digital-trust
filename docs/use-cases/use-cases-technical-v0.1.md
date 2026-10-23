# VN Digital Trust — Technical Use Cases v0.1

**Trạng thái:** Thiết kế use case cho prototype kỹ thuật, 2026-10-05.

**Nguồn:** [Quyết định phạm vi](../scope/technical-first-scope-v0.1.md) và [Technical Requirements v0.1](../requirements/requirements-technical-v0.1.md). Tài liệu use case pháp lý cũ được giữ để truy vết lịch sử, không dùng làm luồng triển khai v0.1.

## 1. Actor và bản đồ luồng

| Actor | Mục tiêu |
| --- | --- |
| Admin | Thiết lập một SME, tạo tài khoản, cấp quyền. |
| IT/Security | Nhập inventory, risk scenario, control, evidence và công việc xử lý. |
| Risk Owner/Management | Xác nhận tác động, xem ưu tiên, quyết định xử lý/chấp nhận rủi ro nếu có quyền. |
| Consultant/Reviewer, tùy chọn | Xem lại kết quả và evidence, ghi nhận nhận xét/điều chỉnh có lý do. |

| UC | Tên | Actor chính | Nhóm yêu cầu |
| --- | --- | --- | --- |
| TUC-01 | Thiết lập tổ chức và quyền | Admin | AUTH |
| TUC-02 | Ghi nhận hệ thống, tài sản và bối cảnh | IT/Security | INV, CTX |
| TUC-03 | Mô tả tình huống rủi ro | IT/Security; Risk Owner | RISK |
| TUC-04 | Đánh giá và xếp mức rủi ro | Risk Owner; IT/Security | RISK |
| TUC-05 | Gắn control và thu thập evidence | IT/Security | CTL, EVD |
| TUC-06 | Đánh giá control và review | IT/Security; Reviewer tùy chọn | EVD, RISK |
| TUC-07 | Xử lý gap/rủi ro và đánh giá lại | IT/Security; Risk Owner | TRT |
| TUC-08 | Xem báo cáo và lịch sử | Management | RPT, AUD |

Luồng chính: **TUC-01 → TUC-02 → TUC-03 → TUC-04 → TUC-05 → TUC-06 → TUC-07 → TUC-08**. TUC-04 có thể lặp sau khi xử lý; báo cáo có thể xuất trước hoặc sau TUC-07.

## 2. Chi tiết use cases

### TUC-01 — Thiết lập tổ chức và quyền

**Mục tiêu:** Có một hồ sơ SME và tài khoản cá nhân theo vai trò.  
**Tiền điều kiện:** Deployment chưa cấu hình hoặc admin đã xác thực để quản lý user.  
**Kết quả:** Một organization profile; user/role được lưu và thay đổi quyền có audit.  
**Yêu cầu:** TFR-AUTH-001 đến 004.

**Luồng chính**

1. Người cài đặt khởi tạo admin đầu tiên bằng setup được bảo vệ.
2. Admin đăng nhập, cấu hình hồ sơ tổ chức và tạo user.
3. Admin gán vai trò IT/Security, Risk Owner/Management hoặc Reviewer tùy chọn.
4. Hệ thống áp dụng quyền khi user truy cập inventory, đánh giá, evidence và quyết định chấp nhận rủi ro.

**Nhánh:** Deployment đã có tổ chức → chỉ cho cập nhật profile; user bị vô hiệu hóa/thiếu quyền → từ chối thao tác; audit vẫn giữ thay đổi trước đó.

### TUC-02 — Ghi nhận hệ thống, tài sản và bối cảnh

**Mục tiêu:** Biết đối tượng nào cần bảo vệ và yếu tố nào làm tăng tác động.  
**Tiền điều kiện:** User có quyền nhập inventory.  
**Kết quả:** Systems, assets, data assets và vendors có owner/quan hệ; mục chưa rõ được đánh dấu.  
**Yêu cầu:** TFR-INV-001 đến 005, TFR-CTX-001 đến 004.

**Luồng chính**

1. IT/Security ghi nhận hệ thống, mục đích, owner, hosting, mức quan trọng và mức phơi lộ.
2. Ghi nhận tài sản và liên kết chúng với các hệ thống được hỗ trợ.
3. Ghi nhận nhóm dữ liệu quan trọng và vendor/cloud/SaaS có liên quan.
4. Risk Owner xác nhận hoặc bổ sung tác động kinh doanh và lý do cho mức quan trọng.
5. Hệ thống hiển thị thông tin thiếu trước khi đánh giá rủi ro.

**Nhánh:** Chưa biết owner/criticality → giữ trạng thái cần xác minh, không tự điền mức thấp; asset đã ngừng sử dụng → đánh dấu trạng thái, không xóa khỏi assessment lịch sử.

### TUC-03 — Mô tả tình huống rủi ro

**Mục tiêu:** Chuyển mối lo kỹ thuật thành một tình huống có đối tượng, sự kiện và hậu quả rõ ràng.  
**Tiền điều kiện:** Có system/asset để gắn scenario.  
**Kết quả:** RiskScenario có owner, nguồn thông tin và giả định.  
**Yêu cầu:** TFR-RISK-001/002.

**Luồng chính**

1. IT/Security chọn hệ thống/tài sản chịu ảnh hưởng.
2. Mô tả sự kiện có thể xảy ra, ví dụ truy cập trái phép CRM; điều kiện liên quan; hậu quả dự kiến.
3. Gắn owner và nguồn thông tin, ví dụ cấu hình hiện tại hoặc cuộc trao đổi với người phụ trách.
4. Hệ thống lưu scenario vào risk register ở trạng thái chưa đánh giá.

**Nhánh:** Chỉ có finding từ scanner → giữ finding như thông tin đầu vào; người dùng phải nêu tài sản và hậu quả trước khi đánh giá risk. Thiếu owner → đưa vào danh sách cần bổ sung.

### TUC-04 — Đánh giá và xếp mức rủi ro

**Mục tiêu:** Ước lượng likelihood/impact và giải thích mức ưu tiên.  
**Tiền điều kiện:** Có RiskScenario; phương pháp/ma trận đánh giá đã được chọn và có version.  
**Kết quả:** Một RiskEvaluation có inputs, reasoning, method version, kết quả hoặc NEEDS_REVIEW.  
**Yêu cầu:** TFR-RISK-003 đến 008.

**Luồng chính**

1. Risk Owner và IT/Security xem scenario cùng bối cảnh tài sản, dữ liệu, vendor và control hiện có.
2. Người đánh giá chọn likelihood, impact, ghi lý do, nguồn và mức tin cậy.
3. Hệ thống dùng phương pháp có version để xếp mức rủi ro, hiển thị quy tắc đã áp dụng.
4. Người dùng lưu kết quả; reviewer tùy chọn có thể nhận xét hoặc điều chỉnh với lý do.

**Nhánh:** Thiếu dữ liệu thiết yếu → NEEDS_REVIEW, không tự gán LOW; phương pháp đổi → tạo lần đánh giá mới, giữ kết quả cũ; thiếu quyền điều chỉnh → từ chối.

### TUC-05 — Gắn control và thu thập evidence

**Mục tiêu:** Biết biện pháp bảo vệ nào áp dụng cho phạm vi đã chọn và có bằng chứng gì.  
**Tiền điều kiện:** Có risk scenario, tài sản/hệ thống và catalog control mẫu.  
**Kết quả:** Risk-control link, ControlImplementation và EvidenceRevision được ghi nhận.  
**Yêu cầu:** TFR-CTL-001 đến 005, TFR-EVD-001 đến 004/007.

**Luồng chính**

1. IT/Security chọn control từ catalog, nêu vì sao control giúp xử lý scenario.
2. Ghi control được triển khai trên hệ thống/tài sản nào, owner và trạng thái khai báo.
3. Hệ thống hiển thị tiêu chí và evidence kỳ vọng của phiên bản control.
4. Người dùng tải lên hoặc đăng ký evidence, nhập nguồn, thời gian thu thập và phạm vi hiệu lực.
5. Người có quyền kiểm tra evidence và ghi trạng thái xác minh.

**Nhánh:** Chưa có evidence → để trống và hiển thị kỳ vọng còn thiếu; evidence hết hạn/từ chối → không dùng làm căn cứ đạt; một evidence dùng cho nhiều control → liên kết rõ từng trường hợp.

### TUC-06 — Đánh giá control và review

**Mục tiêu:** Phân biệt control đạt, chưa đạt và chưa đủ bằng chứng.  
**Tiền điều kiện:** ControlImplementation có tiêu chí đã version; assessment scope được xác định.  
**Kết quả:** ControlAssessment có result, reasoning, evidence revisions và trạng thái review.  
**Yêu cầu:** TFR-EVD-005/006, TFR-RISK-008, TFR-AUTH-004.

**Luồng chính**

1. Hệ thống chụp snapshot của context, method, control criteria và evidence revisions.
2. Người có quyền so evidence hợp lệ với tiêu chí của control.
3. Kết quả được ghi SATISFIED, PARTIALLY_SATISFIED, NOT_SATISFIED, INSUFFICIENT_EVIDENCE hoặc NOT_ASSESSED, kèm lý do.
4. Nếu có reviewer, reviewer xác nhận hoặc yêu cầu bổ sung; thay đổi kết quả cần lý do, actor và thời gian.

**Nhánh:** Thiếu evidence → INSUFFICIENT_EVIDENCE; evidence hợp lệ chứng minh MFA tắt → có thể NOT_SATISFIED theo criteria; câu trả lời “đã bật MFA” không thay thế bằng chứng cấu hình.

### TUC-07 — Xử lý gap/rủi ro và đánh giá lại

**Mục tiêu:** Biến kết quả thành hành động và kiểm tra kết quả sau xử lý.  
**Tiền điều kiện:** Có RiskEvaluation và/hoặc ControlAssessment.  
**Kết quả:** Gap/task/treatment decision được lưu; retest tạo bản kết quả mới.  
**Yêu cầu:** TFR-TRT-001 đến 006.

**Luồng chính**

1. Hệ thống tạo EVIDENCE_GAP hoặc CONTROL_GAP theo kết quả control; người dùng xem risk liên quan.
2. Hệ thống đề xuất mức ưu tiên theo quy tắc công khai; người có quyền xác nhận kế hoạch xử lý.
3. Owner được giao task, deadline và bằng chứng cần bổ sung.
4. Sau xử lý, owner nộp evidence mới và yêu cầu retest.
5. Người có quyền đánh giá lại; hệ thống giữ cả kết quả trước và sau.

**Nhánh:** Người có quyền chọn chấp nhận rủi ro → lưu lý do/phạm vi/thời điểm, không đổi control result; chưa có hướng khắc phục mẫu → chuyển người phụ trách xác định; retest chưa đạt → giữ gap mở.

### TUC-08 — Xem báo cáo và lịch sử

**Mục tiêu:** Management hiểu rủi ro hiện tại, phần chưa rõ và việc cần làm.  
**Tiền điều kiện:** Có assessment/risk register.  
**Kết quả:** Report tại thời điểm được chọn và liên kết truy vết; người không có quyền không xem evidence nhạy cảm.  
**Yêu cầu:** TFR-RPT-001 đến 003, TFR-AUD-001/002.

**Luồng chính**

1. Management chọn phạm vi và lần đánh giá.
2. Hệ thống tổng hợp inventory liên quan, risk scenario/evaluation, method version, control/evidence status, gaps và tasks.
3. Người xem mở một finding để xem tài sản, lý do, control, evidence và quyết định xử lý.
4. Report ghi rõ mục chưa đánh giá, evidence chưa xác minh, rủi ro đã chấp nhận và giới hạn của kết quả.

**Nhánh:** Chưa có likelihood/impact → report hiển thị NEEDS_REVIEW; chưa có reviewer → report ghi kết quả self-assessment; phiên bản cũ được xem với dữ liệu/evidence của thời điểm cũ.

## 3. Acceptance scenarios

| ID | Input/thao tác | Kết quả cần quan sát |
| --- | --- | --- |
| TAC-01 | Tạo deployment và hai user khác vai trò | Một organization; quyền thao tác khác nhau; thay đổi role có audit. |
| TAC-02 | CRM có asset, dữ liệu khách hàng và vendor | Inventory thể hiện quan hệ, owner và thông tin chưa rõ. |
| TAC-03 | Tạo scenario truy cập trái phép CRM | Scenario có tài sản/hệ thống, sự kiện, hậu quả, owner và nguồn. |
| TAC-04 | Đánh giá cùng scenario hai lần với cùng inputs/method version | Cùng kết quả tự động; lý do và version hiển thị. |
| TAC-05 | Thiếu impact | NEEDS_REVIEW, không gán LOW. |
| TAC-06 | Thiếu MFA evidence | INSUFFICIENT_EVIDENCE và EVIDENCE_GAP. |
| TAC-07 | Evidence đã xác minh cho thấy MFA tắt | NOT_SATISFIED theo criteria và CONTROL_GAP. |
| TAC-08 | Quản lý chấp nhận rủi ro | Có actor, lý do, thời điểm; control result vẫn giữ nguyên. |
| TAC-09 | Nộp evidence mới, retest | Có kết quả mới; kết quả/evidence cũ vẫn xem được. |
| TAC-10 | Xuất report | Có risk, control, evidence, gap, task, method version và giới hạn; không có kết luận pháp lý. |

## 4. Điểm cần kiểm chứng với người dùng

Các thao tác nhập inventory/risk có thể quá nặng với SME. Người dùng thực tế có thể không phân biệt risk scenario với finding, hoặc chưa quen giải thích likelihood/impact. Khi phỏng vấn hoặc thử prototype, ghi nhận số bước cần hỗ trợ, câu trả lời “chưa rõ”, lỗi hiểu thuật ngữ và thời gian hoàn thành. Những quan sát này sẽ quyết định mức hướng dẫn trong UI và việc có cần consultant hỗ trợ.
