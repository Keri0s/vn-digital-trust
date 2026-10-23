# Truy vết và điều kiện chuyển bước v0.1

Ngày 2026-10-20. Phạm vi là **đối chiếu thiết kế**. Các hàng bên dưới nêu vị trí thiết kế và expected behavior; không là kết quả chạy FLOW/TC. Kết quả kiểm tra tài liệu thực tế được ghi riêng trong [validation-v0.1](validation-v0.1.md).

## 1. Mười lưu ý của người dùng

| Lưu ý kế hoạch §27 | Nơi hiện thực trong thiết kế | Điều kiện phải giữ khi triển khai |
| --- | --- | --- |
| NOTE-01 — Branch, scope/assignment/expiry | data-model/schema: organizations, branches, role assignments và scope targets; API tổ chức/quyền; seed RBAC | BR-HCM/BR-DN cùng ORG-ABC; user thuộc branch không tự có mọi quyền branch; scope phải hợp lệ ở read/create/list/commit. |
| NOTE-02 — revision và verification riêng | data-model/schema EvidenceRevision/VerificationDecision; API evidence revisions/verification; storage §3–4 | Append-only decision trỏ đúng revision/scope; SELF_ASSESSED không thành independent; snapshot cũ trỏ decision đã dùng. |
| NOTE-03 — criteria và test granularity | ControlCriterionVersion, criterion outcomes/test executions/evidence links; API control assessments | C01–C08 và T01–T24 có định danh riêng; test status không thay control result; failure và missing evidence có thể đồng thời. |
| NOTE-04 — đầy đủ RM-01 | RiskEvaluation, factors, paths, impacts, method/profile/rubric; API risk evaluation | R25 nguyên và ranges; score_determined độc lập status; factor/path UNKNOWN và confirmation còn lại phải hiện. Không sửa công thức. |
| NOTE-05 — retest/impact | AssessmentComparison và API retest/comparison | Cùng CURRENT/CURRENT hoặc INHERENT/INHERENT, context/profile/rubric tương đương; R/impact/gap riêng; verified_worsening không bị INCOMPLETE che. |
| NOTE-06 — decisions/OCC/idempotency | ReviewRequest/Decision, PriorityDecision, ClosureDecision, mutable versions; API contract và storage §5 | Giữ cả ý kiến, phân xử tạo snapshot mới; owner approval riêng; retry không nhân đôi, stale write không ghi đè. |
| NOTE-07 — đường upload | upload-sequence-v0.1; API multipart; storage §1–3 | Browser→TLS proxy→Policy gate→intake; kiểm lại trước commit. Không có endpoint upload public bỏ gate. |
| NOTE-08 — seed permissions | rbac-seed-v0.1.json và configuration; API permission annotations | Hợp nhất baseline + FLOW, giữ provenance và scopes; không cấp cả ba permission cho mọi role. |
| NOTE-09 — trạng thái độc lập | data-model state dictionary; schema/API enums; storage state companion | storage_state khác verification_mode; risk status khác review; pending request không bị mất khi đổi enum. Control score_applicability=NOT_APPLICABLE. |
| NOTE-10 — AUTH-CRM-01 | configuration-v0.1.md + config-template-v0.1.json; AuthenticationProfile version | Năm trường được đặt tên/kiểu/validation; examples120/5/900 không là effective config; CRM tách auth VDT. |

## 2. SC/FLOW → quyết định thiết kế → kiểm thử bước 06

| Ca | Thiết kế đáp ứng | Ca kiểm chứng cần thực thi (hiện NOT_RUN) |
| --- | --- | --- |
| SC-01 | Context snapshot ghi VPN là tiền điều kiện; AUTH-CRM-01 password+WebAuthn/UV; AC-DEMO-01 version criteria; ControlAssessment trước G CURRENT | T01–T18 + T23; fixture NOT_IMPLEMENTED/ENROLLED_SIMULATED không được làm evidence; thử đường password-only/enrollment/recovery/UV. |
| SC-02 | Scenario/data-flow có source, destination, boundary, phiên đọc đã có; EX-DEMO-01; thiếu policy/path hiện validation issue/UNKNOWN | T24 NOT_READY đến khi cấu hình đích/đường/phạm vi có phê duyệt; MFA đăng nhập mới không tự giảm G. |
| FLOW-01 | U002 có evidence.read_assigned+evidence.verify ở scope vận hành; decision SELF_ASSESSED; không yêu cầu consultant | Tạo evidence thật trong lab, verify nội bộ, chạy control assessment; không giả độc lập và không tự CONFIRMED toàn assessment. |
| FLOW-02 | U004 assignment ASM-DEMO-01 và expiry; read/verify/review mỗi hành động có gate | Trong assignment cho phép; ngoài assignment list/detail/create FK/download/export đều bị chặn và không rò object. |
| FLOW-03 | Gate ở đầu và trước commit/phát bytes; auth guard version, revoke, DB time | Boundary trước, đúng và sau 2026-10-31T17:00:00+07:00 bằng test clock cô lập; revoke giữa upload/export/download; U002 không phụ thuộc U004. |
| FLOW-04 | PriorityProposal tách PriorityDecision, risk.priority_approve chỉ Risk Owner trong scope | Reviewer đề xuất được nhưng không approve; approve thiếu reason/scope bị từ chối; MF-03/MF-04 không có approval tự sinh. |
| FLOW-05 | Evidence use kiểm revision/decision/expiry/storage; test INCONCLUSIVE giữ thiếu căn cứ | T23 mất telemetry: không PASS, không suy control failure hoặc LOW; giữ EVIDENCE_GAP và G UNKNOWN. |
| FLOW-06 | Criterion outcomes độc lập, nhiều gap theo criterion; risk score/status riêng | Một criterion failure xác minh + một criterion unknown → CONTROL_GAP và EVIDENCE_GAP cùng tồn tại; điểm xác định vẫn có NEEDS_REVIEW. |
| FLOW-07 | Context required issues, current vs illustrative, per-path rationale | SC-02 thiếu đích/đường → issues; không promote synthetic observation thành CURRENT hoặc dùng MFA login mới để hạ G. |
| FLOW-08 | Evidence/retest append revision; ClosureDecision riêng | New evidence VERIFIED nhưng control FAIL/INCONCLUSIVE → snapshot mới và task/gap còn mở. Acceptance hoặc R giảm cũng không tự đóng. |
| FLOW-09 | Comparison semantic key, individual impacts, max count, nullable verified_worsening, attribution | Cùng key tạo ba tiến độ; khác type/context/profile → NOT_COMPARABLE; case R không đổi nhưng một impact giảm hoặc tăng vẫn hiện; closure yêu cầu decision. |
| FLOW-10 | Tách lỗi cấu trúc request khỏi lỗi domain đánh giá; validation issues được lưu | Sai JSON/type → 400/422 theo API không snapshot rác; request hợp cấu trúc nhưng thiếu context/miền factor sai → snapshot NEEDS_REVIEW, score/range/level null theo RM. |

## 3. Requirement/TUC và cụm dữ liệu/API

| Nhóm | TUC | Cụm dữ liệu và contract |
| --- | --- | --- |
| TFR-AUTH-001–004; TNFR-SEC-001 | 01, toàn bộ | Organization singleton, users/roles/assignments/sessions, scope gate, policy version và audit; không tự đăng ký công khai. |
| TFR-INV-001–005; TFR-CTX-001–004 | 02–03 | Systems/assets/data assets/vendors, quan hệ N:N, owner/criticality/source/UNKNOWN, branch và data flow, context snapshots/version. |
| TFR-RISK-001–008; TNFR-TRC-001/REP-001 | 03–04 | Scenarios, assessment container, risk methods/profile/rubric, E/F/G+impact and exact calculation snapshots; register lọc actual CURRENT/INHERENT phù hợp, không ghi ILLUSTRATIVE thành thực. |
| TFR-CTL-001–005 | 05 | Catalog/version/criteria/expectation, implementation scope hoặc declared NOT_IMPLEMENTED, risk-control links và applicability reason. |
| TFR-EVD-001–007; TNFR-PRV-001 | 05–06 | Evidence revisions/storage, links N:N, verification decisions, criterion outcomes/test status; protected bytes và reference thủ công. |
| TFR-TRT-001–006 | 07 | Gap, priority proposal/approval, treatment decisions/tasks, acceptance, retest/comparison, closure checks/decisions. |
| TFR-RPT-001–003; TFR-AUD-001–002; TNFR-EXP-001/USA-001 | 08 | Report graph/as_of, exports với expiry/gate, audit append-only; UNKNOWN và giới hạn bằng ngôn ngữ nghiệp vụ. |
| TNFR-DEP-001 | Tất cả | Stack một ứng dụng/DB/kho file trên VM; ngân sách RAM là ước lượng, phép đo và restore gate ở bước 06. |

## 4. Quy tắc chuyển nghĩa từ baseline sang bước 05

Đây là thiết kế chi tiết có truy vết, không viết lại domain model ngày 05/10 hoặc fixture gốc. Các tên lịch sử trong payload/input import phải có `source_schema_version`; chuyển nghĩa qua adapter có kiểm tra hoặc giữ nguyên bản cũ, không sửa snapshot đã tồn tại.

| Giá trị/khái niệm cũ | Canonical bước 05 | Điều kiện/chú thích |
| --- | --- | --- |
| EvidenceRevision chứa verification status | VerificationDecision + effective status view | `EXPIRED` là điều kiện thời gian/hiệu lực, không cập nhật lại decision VERIFIED cũ. storage state ở companion row. |
| assessment_mode=REVIEWER_ASSISTED | Không ánh xạ tự động thành INDEPENDENT_REVIEWED | Chỉ gắn independent khi actor khác, đúng scope và có quyết định thực đã hoàn thành; hỗ trợ của reviewer chưa đủ. |
| review_outcome=NOT_REQUESTED | NONE | Giữ bản gốc trong raw legacy payload nếu nhập lịch sử. |
| review_outcome=PENDING | ReviewRequest.status=PENDING, outcome vẫn NONE hoặc kết quả đã có | Request lifecycle và kết quả review độc lập; request mới không xóa kết quả cũ. |
| review_outcome=CONFIRMED/DISPUTED | CONFIRMED/DISPUTED | Gắn đúng target snapshot/decision, không tự sửa assessment.status. |
| Chỉnh assessment đã lưu | ADJUSTED_NEW_SNAPSHOT với replacement ID và decision mới | Giữ original + review finding; người phân xử khác các bên xung đột; replacement phải qua validation đầy đủ. |
| score_determined trên control | boolean false + score_applicability=NOT_APPLICABLE | RM-01 tính điểm risk, không định nghĩa điểm control. Control dùng control_result và độ đủ evidence theo criteria; false ở đây không có nghĩa rủi ro chưa tính được. |

## 5. Gate trước prototype/lab

| Gate | Người/đầu vào cần có | Trạng thái tại bước 05 |
| --- | --- | --- |
| ENV-01 | Môi trường CRM/hostname/RP ID/origins/TLS/VPN/receiver và scope được xác định | TO_SET_BEFORE_LAB |
| CFG-01 | TTL/attempt/session, enrollment/recovery/notification/revoke policy, approval actor/time/version | TO_SET_BEFORE_LAB; ví dụ không là cấu hình chạy |
| BUILD-01 | Pin patch/dependency/image/package/scanner signatures, build/migration PostgreSQL thật | NOT_RUN |
| APP-01 | RBAC/list/create/read/download/export, revocation/expiry, reference network, upload/lifecycle | NOT_RUN |
| TX-01 | Crash/retry/idempotency/concurrency/snapshot atomicity/guard thời gian/audit failure | NOT_RUN |
| STORE-01 | Manifest backup + restore, integrity/missing files và quyền sau restore | NOT_RUN |
| PERF-01 | RAM/CPU/disk/file quotas/worker trên tài nguyên đã chọn | NOT_RUN; budget chưa đo |
| CRM-01 | T01–T24 và FLOW-01…10 với evidence thực tế và test clock/bối cảnh rõ | NOT_RUN; T24 hiện NOT_READY |
| VALID-G-01 | Hai người chấm thực A/B độc lập theo quy tắc đã ghi, không lấy trợ lý chấm hai lần làm thay thế | NOT_RUN; hai phiếu trống |
| SME-01 | Hiệu chuẩn/phê duyệt ưu tiên/acceptance của người có thẩm quyền | NOT_RECORDED; MF-03/MF-04 NOT_RANKED |

Không tự chạy bước 06 từ việc tài liệu bước 05 đạt kiểm tra thiết kế. Việc triển khai DB/app/lab phải theo lượt bắt đầu bước 06 và các gate thích hợp.
