# VN Digital Trust — Technical Domain Model v0.1

**Trạng thái:** Mô hình khái niệm cho prototype kỹ thuật, 2026-10-05.

**Nguồn:** [Quyết định phạm vi](../scope/technical-first-scope-v0.1.md), [Technical Requirements](../requirements/requirements-technical-v0.1.md), [Technical Use Cases](../use-cases/use-cases-technical-v0.1.md). [Sơ đồ PlantUML](domain-model-technical-v0.1.puml) thể hiện các quan hệ chính.

Đây là domain model, chưa phải lược đồ database. Một số quan hệ nhiều-nhiều sẽ thành bảng liên kết khi thiết kế lưu trữ.

## 1. Bốn khối dữ liệu chính

1. **Context:** tổ chức, hệ thống, tài sản, dữ liệu, vendor và người phụ trách.
2. **Risk:** tình huống rủi ro, phương pháp đánh giá có version và từng lần đánh giá.
3. **Protection:** định nghĩa control, việc triển khai control trên một phạm vi cụ thể, tiêu chí và evidence.
4. **Action/history:** gap, quyết định xử lý, task, reviewer, audit và snapshot báo cáo.

## 2. Entity và ý nghĩa

### A. Context

| Entity | Thuộc tính khái niệm | Quan hệ |
| --- | --- | --- |
| Organization | ID, tên, ngành, quy mô, contact | Một deployment có đúng một Organization sau setup. |
| User | ID, trạng thái, danh tính đăng nhập | Thuộc Organization, có RoleAssignment. |
| RoleAssignment | User, role, thời điểm cấp/thu hồi | Quy định quyền nhập, review, chấp nhận rủi ro và xem report. |
| InformationSystem | ID, tên, mục đích, owner, hosting, exposure, criticality | Gồm hoặc dùng nhiều Asset; liên quan DataAsset/Vendor/RiskScenario. |
| Asset | ID, loại, owner, trạng thái, criticality | Có thể hỗ trợ nhiều InformationSystem. |
| DataAsset | ID, loại dữ liệu, mức nhạy cảm nội bộ, owner | Liên quan một hoặc nhiều InformationSystem; giúp mô tả impact. |
| Vendor | ID, dịch vụ, owner nội bộ, loại phụ thuộc | Có thể hỗ trợ nhiều InformationSystem. |
| ContextSnapshot | Bản chụp facts, giá trị UNKNOWN, mô tả scenario và trạng thái triển khai control tại một thời điểm | Một RiskAssessment dùng đúng một snapshot. |

DataAsset và Vendor chỉ là bối cảnh cho risk/impact trong v0.1. Chúng không kích hoạt rule pháp lý.

### B. Risk

| Entity | Thuộc tính khái niệm | Quan hệ |
| --- | --- | --- |
| RiskScenario | ID, sự kiện, điều kiện/điểm yếu, hậu quả, owner, nguồn, giả định | Gắn ít nhất một Asset hoặc InformationSystem. |
| RiskMethodVersion | ID/version, định nghĩa likelihood/impact, ma trận/quy tắc, ngày áp dụng | Được từng RiskEvaluation tham chiếu; không sửa bản đã dùng. |
| RiskAssessment | ID, phạm vi, thời điểm, người bắt đầu, status | Chụp ContextSnapshot; chứa RiskEvaluation và ControlAssessment. |
| RiskEvaluation | Scenario ID cùng mô tả đã chụp, likelihood, impact, rationale, confidence, result, actor/time | Thuộc một RiskAssessment; dùng một RiskMethodVersion. |
| ReviewDecision | Target result, reviewer, old/new value, reason, time | Có thể điều chỉnh RiskEvaluation hoặc ControlAssessment; không xóa kết quả gốc. |

**RiskScenario** mô tả khả năng xảy ra một sự kiện và hậu quả; **RiskEvaluation** là nhận định ở một thời điểm. Một scenario có thể có nhiều evaluations trước/sau xử lý. Một scanner finding chỉ là nguồn thông tin, chưa phải scenario hoặc mức rủi ro.

### C. Control và evidence

| Entity | Thuộc tính khái niệm | Quan hệ |
| --- | --- | --- |
| ControlDefinitionVersion | ID/version, mục tiêu, mô tả, tiêu chí và kỳ vọng evidence | Một định nghĩa có thể được chọn cho nhiều RiskScenario. |
| RiskControlLink | Scenario, ControlDefinitionVersion, lý do chọn | Ghi control dự kiến, ngay cả khi chưa có triển khai. |
| ControlImplementation | ControlDefinitionVersion, Asset/System scope, owner, trạng thái khai báo | Có thể được dùng để xử lý nhiều RiskScenario. |
| EvidenceExpectationVersion | Control/version, loại/tính chất evidence cần có | Được ControlAssessment dùng theo version. |
| EvidenceItem | ID, owner, nguồn, loại | Có nhiều EvidenceRevision. |
| EvidenceRevision | Version, file/reference, collected_at, valid_until, verification status, hash nếu có | Immutable khi đã dùng trong assessment. |
| EvidenceLink | EvidenceRevision, ControlImplementation, phạm vi và lý do hỗ trợ | Cho phép tái sử dụng evidence khi phù hợp. |
| ControlAssessment | Implementation hoặc control chưa triển khai, result, criteria version, reasoning, evidence revisions, actor/time | Thuộc RiskAssessment; có thể tạo Gap. |

**ControlDefinitionVersion** mô tả biện pháp chung (ví dụ MFA). **ControlImplementation** mô tả MFA trên CRM của ABC Trading; sự tồn tại của định nghĩa không chứng minh CRM đã bật MFA.

### D. Gap, treatment và lịch sử

| Entity | Thuộc tính khái niệm | Quan hệ |
| --- | --- | --- |
| Gap | EVIDENCE_GAP/CONTROL_GAP, reason, priority, status | Gắn ControlAssessment và RiskScenario liên quan. |
| TreatmentDecision | RiskScenario, lựa chọn xử lý, decision maker, reason, time, scope | Chấp nhận rủi ro là một lựa chọn cần quyền; không thay ControlAssessment. |
| TreatmentTask | Gap hoặc TreatmentDecision, owner, hành động, due date, status, retest evidence | Có thể dẫn đến RiskAssessment mới. |
| AuditEvent | Actor, action, target, time, old/new value | Lưu thao tác quan trọng. |

Report là **view từ một RiskAssessment đã lưu** cùng các gap/treatment liên quan. Có thể lưu một ReportSnapshot nếu cần xuất báo cáo cố định; prototype không phải quyết định ngay cấu trúc file/bảng cho report.

## 3. Quan hệ và cardinality

| Quan hệ | Cardinality / điều kiện |
| --- | --- |
| Deployment → Organization | Chính xác 1 sau setup. |
| Organization → User, System, Asset, RiskAssessment | 1 → nhiều; mọi bản ghi vận hành thuộc cùng SME. |
| User ↔ Role | Nhiều-nhiều qua RoleAssignment. |
| InformationSystem ↔ Asset | Nhiều-nhiều; một asset có thể phục vụ nhiều system. |
| InformationSystem ↔ DataAsset / Vendor | Nhiều-nhiều; các liên kết lưu vai trò/phạm vi nếu cần. |
| RiskScenario → InformationSystem / Asset | Ít nhất một target; có thể có cả hai. |
| RiskScenario ↔ ControlDefinitionVersion | Nhiều-nhiều qua RiskControlLink. |
| ControlDefinitionVersion → ControlImplementation | 1 → 0..n; catalog không đồng nghĩa đã triển khai. |
| EvidenceItem → EvidenceRevision | 1 → 1..n. |
| EvidenceRevision ↔ ControlImplementation | Nhiều-nhiều qua EvidenceLink. |
| RiskAssessment → ContextSnapshot | 1 → 1. |
| RiskAssessment → RiskEvaluation / ControlAssessment | 1 → 0..n. |
| RiskEvaluation → RiskMethodVersion | n → 1. |
| ControlAssessment → Gap | 1 → 0..n. |
| Gap → TreatmentTask | 1 → 0..n. |
| RiskScenario → TreatmentDecision | 1 → 0..n theo lịch sử. |

## 4. Bất biến nghiệp vụ

1. **Một SME:** Không có organization thứ hai hoặc dữ liệu SME khác trong cùng deployment.
2. **Không biến UNKNOWN thành LOW:** Thiếu likelihood/impact hoặc facts quan trọng → NEEDS_REVIEW.
3. **Risk result có nguồn:** Mỗi RiskEvaluation lưu input, rationale, actor, method version và result. Tính lại với cùng input/version phải nhất quán.
4. **Catalog khác triển khai:** Một control có trong catalog hoặc được liên kết với risk không chứng minh nó đã có trên hệ thống.
   Mỗi ControlImplementation phải có phạm vi là ít nhất một Asset hoặc InformationSystem.
5. **Thiếu evidence khác control thất bại:** Evidence thiếu/chưa xác minh/hết hạn có thể tạo INSUFFICIENT_EVIDENCE. NOT_SATISFIED cần căn cứ theo criteria.
6. **Lịch sử bất biến:** Sửa asset/scenario, trạng thái triển khai control, evidence hoặc risk method tạo bản đánh giá mới; report cũ vẫn đọc theo snapshot và reference/version cũ.
7. **Review có trách nhiệm:** Override cần quyền, reason, old/new value, actor và time.
   Một ReviewDecision nhắm vào đúng một RiskEvaluation hoặc một ControlAssessment.
8. **Risk acceptance không sửa control:** TreatmentDecision ACCEPT không biến NOT_SATISFIED thành SATISFIED và không xóa risk register.
9. **Không kết luận pháp lý:** Report kỹ thuật nêu phạm vi và giới hạn; không có “compliant/non-compliant” đối với pháp luật.

## 5. Working states

| Đối tượng | Giá trị đề xuất |
| --- | --- |
| RiskScenario | DRAFT, ACTIVE, RETIRED |
| RiskEvaluation | NEEDS_REVIEW, EVALUATED; risk level phụ thuộc RiskMethodVersion |
| EvidenceRevision | UNVERIFIED, VERIFIED, REJECTED, EXPIRED |
| ControlAssessment | NOT_ASSESSED, SATISFIED, PARTIALLY_SATISFIED, NOT_SATISFIED, INSUFFICIENT_EVIDENCE |
| Gap type | EVIDENCE_GAP, CONTROL_GAP |
| TreatmentDecision type | MITIGATE, ACCEPT, AVOID, TRANSFER/SHARE; v0.1 chỉ cần triển khai rõ MITIGATE và ACCEPT, loại khác có thể là ghi nhận quyết định |
| TreatmentTask | OPEN, IN_PROGRESS, READY_FOR_RETEST, CLOSED |

Risk level, control result, gap type và treatment decision là **bốn trục khác nhau**. Không gộp chúng vào một cột “status”.

## 6. Ví dụ ABC Trading

**Context:** CRM là InformationSystem; tài khoản quản trị CRM là Asset hoặc thành phần của system; dữ liệu khách hàng là DataAsset; CRM SaaS Provider là Vendor.

**Scenario:** Người không được phép truy cập CRM và lấy dữ liệu khách hàng. Risk Owner mô tả tác động, IT/Security bổ sung điều kiện kỹ thuật và evidence hiện có. Lần đánh giá đầu tiên lưu RiskMethodVersion và lý do likelihood/impact.

**Control:** MFA là một ControlDefinitionVersion được chọn để xử lý scenario. CRM có ControlImplementation tương ứng. Nếu chưa có EvidenceRevision xác minh, ControlAssessment là INSUFFICIENT_EVIDENCE. Nếu evidence đã xác minh cho thấy MFA tắt, kết quả có thể là NOT_SATISFIED theo criteria của control. Mỗi trường hợp tạo loại Gap tương ứng.

**Treatment:** Task yêu cầu bật MFA hoặc bổ sung bằng chứng, theo gap thực tế. Retest tạo ControlAssessment và RiskEvaluation mới nếu đánh giá rủi ro thay đổi. Kết quả cũ vẫn xem được.

Ví dụ này minh họa quan hệ dữ liệu; likelihood, impact và kết luận control cụ thể cần được xác định bằng tiêu chí thử nghiệm, không được đoán trước.

## 7. Các quyết định cần chốt trước khi code

- Chọn rubric likelihood/impact và risk matrix mẫu có version, nguồn tham khảo, giới hạn và bộ test cố định. Hiện model chưa áp đặt thang điểm.
- Xác định danh sách control mẫu nhỏ và tiêu chí/evidence cụ thể cho ABC Trading.
- Chọn phạm vi assessment đầu tiên: CRM system và các tài sản liên quan là ứng viên dễ kiểm thử.
- Chọn nơi lưu evidence (file local hay reference) và cơ chế kiểm soát quyền; cả hai phải giữ được revision.
- Thử với người dùng hoặc consultant để xác định cách nhập inventory/risk có quá nặng không.
