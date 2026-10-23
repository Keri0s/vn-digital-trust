# VN Digital Trust — Mô hình dữ liệu v0.1

**Ngày:** 2026-10-20; cập nhật đối chiếu 2026-10-21. **Phạm vi:** thiết kế bước 05; chưa triển khai migration, prototype hoặc lab.

Tài liệu mô tả [DDL PostgreSQL 17](../Dac-ta-ky-thuat/schema-v0.1.sql), các quan hệ trong ERD và ánh xạ sang [API contract](../Dac-ta-ky-thuat/openapi-v0.1.yaml). Baseline nghiệp vụ là RM-01 v0.4-r3 (calculation profile v0.4), CE-01/TC-01 v0.1, use case v0.2-r1, kiến trúc v0.1 và NOTE-01…10 tại mục 27 của kế hoạch. Mô hình khái niệm hiện hành được giữ nguyên làm nguồn tham chiếu; DDL này là thiết kế vật lý bổ sung.

## 1. Quy ước và phạm vi

- Một SME trên một database; `organization.singleton=true` và UNIQUE giới hạn tối đa một organization. Khởi tạo organization vẫn là trách nhiệm migration/seed.
- Khóa chính là UUID do server cấp; mã nghiệp vụ (`code`) phục vụ hiển thị và truy vết. Tên file, URL hoặc mã từ client không trở thành đường dẫn lưu trữ.
- Thời điểm dùng `timestamptz`; API trao đổi thời gian ISO 8601 có múi giờ. Server ghi actor/thời điểm của quyết định.
- `sha256_hex` là 64 ký tự hex thường; `score_1_5` là số nguyên 1–5; `nonempty_text` loại chuỗi rỗng/toàn khoảng trắng.
- `version bigint > 0` là phiên bản ghi của thực thể mutable. `snapshot_registry.lineage_id/revision_number` định danh chuỗi thay thế snapshot, UNIQUE theo cặp. Version tài liệu/phương pháp/tiêu chí là mã riêng, không đồng nhất với optimistic concurrency.
- JSONB giữ nội dung có cấu trúc thay đổi theo `schema_version`, raw input hoặc căn cứ giải thích. FK dùng cho quan hệ quyết định; không thay FK quan trọng bằng ID nằm trong JSONB.
- Snapshot và quyết định mới giữ lịch sử. Chỉnh sửa context hoặc quyền hiện tại không sửa kết luận đã chụp; quyền đọc kết quả cũ vẫn được kiểm tra ở thời điểm truy cập.

## 2. Các nhóm dữ liệu

Các bảng dùng chung `id uuid PRIMARY KEY`; bảng con không lặp toàn bộ metadata của snapshot. Với bảng có `id REFERENCES snapshot_registry`, `created_by`, `created_at`, `scope_id`, `content_hash` nằm ở registry và được trả chung trong API. Các cột dưới đây là nhóm thông tin có ý nghĩa, không thay thế khai báo type/NULL/constraint đầy đủ trong DDL.

`snapshot_registry.api_payload_schema_version/api_payload` giữ DTO canonical của snapshot để tái tạo đầy đủ cấu trúc API, nguồn và metadata. Service đồng bộ payload với typed columns/FK/children trước tính hash; JSON không thay thế kiểm scope hoặc quan hệ có FK. Raw claim của risk/control vẫn được giữ tại trường raw_input tương ứng, phân biệt với dữ liệu có hiệu lực.

### 2.1. Organization, tài khoản và quyền

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `organization` | `code`, `name`, `singleton`, `version` | Tối đa một SME. Chi nhánh là phạm vi hoạt động trong SME. |
| `branch` | Organization; `code`, `name`, `active`, `version` | Mã duy nhất; seed BR-HCM/BR-DN là dữ liệu demo. |
| `app_user` | Organization; `code`, `login_name`, `display_name`, `status`, `version`, password hash, last login, email | Tài khoản VDT độc lập danh tính CRM; login duy nhất. Password dùng hasher/validator Django; giá trị mặc định `!` vô hiệu đăng nhập, không là mật khẩu mặc định. Không công khai đăng ký tài khoản. |
| `user_branch` | User ↔ branch | UNIQUE cặp user/branch; membership không tự cấp quyền vào mọi đối tượng chi nhánh. |
| `role`, `permission`, `role_permission` | Danh mục role, permission và bảng nối | Mã duy nhất; UNIQUE cặp role/permission. Seed có nguồn baseline và permission bổ sung, không suy quyền từ tên role. |
| `scope` | Organization, `scope_kind`, `description`, `content_hash`, `created_txid` | Bộ selector bất biến. `ORGANIZATION` và `SELECTED` được phân biệt rõ; tập rỗng không tự thành wildcard. |
| `scope_branch` | Scope ↔ branch | UNIQUE cặp; branch giao với object scope khi tính quyền. |
| `scope_object` | Scope → đúng một system/asset/data asset/scenario/assessment | CHECK đúng một FK có giá trị; `UNIQUE NULLS NOT DISTINCT` chặn selector trùng dù có cột NULL. |
| `role_assignment` | User, role, scope, `valid_from`, `access_expires_at`, `revoked_at`, `granted_by`, `version` | Nếu có expiry thì phải sau valid_from. Assignment hết hạn tại đúng mốc expiry. |
| `assignment_assessment` | Assignment ↔ assessment | UNIQUE cặp. Consultant reviewer phải có assignment assessment còn hiệu lực, cùng object scope. |
| `authorization_guard` | Một dòng/organization; `version` | Điểm đồng bộ thay đổi quyền với thao tác dài. Service phải thực sự khóa/kiểm version; có bảng chưa đủ loại bỏ race. |
| `vdt_session` | User, hash token, issued/expiry/last seen/revoked, `version` | Không lưu token phiên nguyên văn. CHECK expiry sau issued; server kiểm user/session hiện hành ở mỗi thao tác. |

### 2.2. Inventory, scenario và hồ sơ assessment

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `information_system` | Mã, tên, owner, mục đích, hosting/exposure/criticality, `facts`, `version` | Thực thể mutable; dữ kiện chưa biết giữ trạng thái/nguồn trong cấu trúc facts. |
| `asset` | Mã, tên, loại, owner, branch, status, `facts`, `version` | Branch có thể chưa có; không suy rằng NULL là tất cả chi nhánh. |
| `data_asset` | Mã, tên, owner, branch, sensitivity, description, `version` | Dữ liệu nghiệp vụ được quản lý riêng khỏi thiết bị/hệ thống. |
| `vendor` | Mã, tên, owner, mô tả dịch vụ, `version` | Lưu phụ thuộc nhà cung cấp, chưa đánh giá tuân thủ pháp lý. |
| `system_asset`, `system_data_asset`, `system_vendor` | Quan hệ nhiều–nhiều từ system | UNIQUE từng cặp; system_asset giữ relationship, system_vendor giữ dependency. |
| `data_flow` | Source asset, destination asset, data asset, channel, trust boundary, destination policy, facts | Ba FK bắt buộc; dùng được cho SC-02. Policy đích chưa xác nhận không trở thành policy đã triển khai. |
| `risk_scenario` | Mã, tên, owner, context snapshot, event, preconditions, consequence, source, status, `version` | Owner có thể NULL ở draft nhưng ACTIVE cần owner. ATT&CK là metadata nguồn có version, không sinh điểm tự động. |
| `scenario_target` | Scenario → system hoặc asset | CHECK đúng một target; UNIQUE NULLS NOT DISTINCT tránh liên kết trùng. |
| `assessment` | Mã, owner, primary scenario tùy chọn, workflow `OPEN/ARCHIVED`, `version` | Hồ sơ quản lý nhiều snapshot; `OPEN` không phải kết quả đánh giá `EVALUATED`. |
| `assessment_scenario` | Assessment ↔ scenario | UNIQUE cặp; membership chính thức cho phép hồ sơ chứa nhiều scenario. Cột scenario_id ở assessment chỉ chọn scenario hiển thị chính. |
| `context_snapshot` | Assessment và scenario/version tùy chọn, schema version, facts, scenario description, preconditions, unknown facts, input versions, fingerprint môi trường | Cho phép context bootstrap trước scenario/assessment. Registry cung cấp actor/time/scope/hash. Facts và input_versions là JSON object; chụp dữ kiện cần tái lập. |
| `scenario_snapshot` | Registry, scenario/source version, context snapshot, code/name/event/consequences/owner, attack metadata/sources, target snapshot | UNIQUE scenario/source version; RiskEvaluation trỏ exact scenario snapshot. Chụp nội dung/mục tiêu, không chỉ trỏ scenario mutable. |
| `mutable_entity_history` | Loại/ID thực thể, version, schema, recorded/effective time, actor, scope, state snapshot, hash | UNIQUE loại/ID/version; dùng tái dựng dữ kiện mutable tại thời điểm báo cáo. `entity_id` đa hình không có FK tổng quát: service kiểm loại và đích. |

Inventory, scenario và assessment giữ thêm `api_payload_schema_version`/`api_payload` để bảo toàn DTO canonical: KnownText, UNKNOWN/reason/source, scope và metadata có cấu trúc không bị mất khi chiếu ra các cột tìm kiếm. Các FK typed là quan hệ chính thức. Service kiểm JSON theo schema API và cập nhật JSON, cột chiếu, các bảng nối, history cùng transaction; không nhận default `{}` như bằng chứng payload đã đủ. Payload không chứa password, token hoặc write_context. Lịch sử copy canonical payload cùng version để report as_of không lấy thông tin hiện tại.

### 2.3. Danh mục version và cấu hình CRM

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `control_definition_version` | Control code/version, objective, source, hash | UNIQUE code/version; tiêu chí thuộc đúng phiên bản định nghĩa. |
| `control_criterion_version` | Control version, criterion code/version, mandatory, requirement, evidence expectation, hash | UNIQUE control/code/version. Tiêu chí mandatory không biến mất khi điểm risk thấp. |
| `test_case_version` | Code/version, preconditions, action, expected result, hash | UNIQUE code/version; expected result được chốt trước execution. |
| `test_case_criterion` | Test version ↔ criterion version | UNIQUE cặp; một test có thể hỗ trợ nhiều tiêu chí, không đồng nhất execution với control result. |
| `risk_method_version` | Method code, document revision, calculation profile, rubric version, progress rule version, definition, hash | UNIQUE bộ method/document/profile/rubric. RM-01 v0.4-r3 vẫn dùng calculation profile v0.4; đổi câu chữ và đổi công thức là hai loại version. |
| `control_implementation` | Control version, owner, scope, declared status, rationale, authentication profile version tùy chọn, `version` | Trạng thái khai báo chưa là evidence về hiệu lực; cấu hình CRM được tham chiếu đúng version. |
| `scenario_control` | Scenario, control version, implementation tùy chọn, scope, rationale, actor/time, canonical API payload | Liên kết bất biến lựa chọn control theo mục tiêu scenario; UNIQUE NULLS NOT DISTINCT cho bộ ba. |
| `authentication_profile_version` | Registry, code/revision, system, configuration/implementation state; TTL/attempt/session/revocation policy; rp_id/origins; enrollment/recovery/notification; approver/time | UNIQUE code/revision; các duration có miền số. Chỉ password + WebAuthn, user verification bắt buộc, không TOTP fallback/passwordless trong baseline. |

`AUTH-CRM-01` là cấu hình control được đánh giá ở CRM. `TO_SET_BEFORE_LAB`, `PROPOSED`, `APPROVED` mô tả mức chốt cấu hình; không nói đã kiểm chứng hiệu lực. DDL yêu cầu các trường cốt lõi và approver/time khi APPROVED. Service còn phải kiểm môi trường, origin hợp lệ, quan hệ TTL, toàn bộ chính sách cần thiết và quyền phê duyệt. Ví dụ 120/5/900 không được seed thành giá trị đã phê duyệt. Phiên VDT ở `vdt_session` là cơ chế khác.

Authentication profile còn giữ `environment`, `scope_owner_approval_reference` và `approval_reason`; APPROVED cần lý do không rỗng. Owner của inventory và scenario draft có thể chưa xác định; context phải phản ánh UNKNOWN này. Service chặn kết luận hoàn tất nếu thiếu owner/context thiết yếu, thay vì tạo user giả để thỏa FK.

### 2.4. Evidence, storage và thực thi test

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `evidence_item` | Mã logic, owner, assessment, scope, nguồn, `head_revision_id`, `version` | Head chỉ tới revision của chính item bằng FK ghép. Head mutable; payload revision bất biến. |
| `evidence_revision` | Registry, item, revision number, predecessor, FILE/REFERENCE, collected/valid until, source/provenance/redaction/environment, content hash/size/media type/original name hoặc URI | UNIQUE item/revision; predecessor cùng item bằng FK ghép, không tự trỏ. FILE cần hash/size, không URI; REFERENCE cần URI, không size. |
| `evidence_storage` | Một dòng/revision; storage state, blob key, scanner verdict, verified hash, last check, failure reason, version | Blob key duy nhất; đây là trạng thái vật lý mutable, không sửa kết luận verification lịch sử. |
| `verification_decision` | Registry, exact revision, predecessor, VERIFIED/REJECTED, mode, valid until, reason, source/provenance checks | Quyết định append-only; predecessor cùng revision. Scope/actor/time được lấy từ registry. |
| `evidence_link` | Registry, exact revision, implementation, criterion version tùy chọn, rationale | Một revision có thể phục vụ nhiều control; service kiểm scope và criterion thuộc control tương ứng. |
| `evidence_link_criterion` | Evidence link ↔ criterion version | UNIQUE cặp; tập nhiều criterion chính thức của API. Chèn cùng transaction với link, không thêm/sửa/xóa sau commit. Cột criterion đơn trên link chỉ là tham chiếu chính tùy chọn. |
| `evidence_request`, `evidence_request_criterion` | Registry, assessment, người được yêu cầu cung cấp, description/due; danh sách criterion version | Yêu cầu thu thập có lịch sử riêng; UNIQUE request/criterion. Request không là evidence hoặc kết quả verification. |
| `test_execution` | Registry, assessment, test case version, authentication profile version tùy chọn, execution status, start/finish, environment/preconditions, expected/observed, telemetry | Finish không trước start; execution khác NOT_READY phải có start. Test lỗi hoặc thiếu telemetry không tự kết luận control đạt/thất bại. |
| `test_execution_evidence` | Execution, exact revision, exact verification decision | FK ghép quyết định/revision ngăn dùng quyết định của revision khác; UNIQUE bộ ba. |
| `storage_event` | Storage, from/to state, audit event, time, reason, observed hash | Lịch sử chuyển trạng thái vật lý; không dùng một cột VERIFIED trên evidence_storage. |

`content_hash` trong registry là hash của snapshot canonical; `content_sha256` ở revision là hash bytes evidence. Hai giá trị có mục đích khác nhau. `original_filename` chỉ để hiển thị an toàn. URI tham chiếu không khiến server tự fetch; việc xác minh nguồn không được dựa riêng vào chuỗi URL.

### 2.5. Kết quả control theo tiêu chí

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `control_assessment` | Registry, assessment/context, control version/implementation, implementation snapshot, result, status, mode/review, predecessor, reasoning, unresolved issues | `score_determined=false`, `score_applicability=NOT_APPLICABLE` là CHECK bắt buộc. Không có điểm risk cho control. |
| `control_assessment_criterion` | Assessment control, criterion version, scope, result, execution status, observation, reasoning; raw input, missing reasons, verified failure, test case codes/run reference | UNIQUE control assessment/criterion/scope. Giữ claim ban đầu và kết luận có hiệu lực riêng; boolean verified_failure do service xác định từ evidence. |
| `criterion_evidence` | Criterion result, revision, verification decision | FK ghép exact revision/decision; UNIQUE bộ ba. |
| `criterion_test_execution` | Criterion result ↔ test execution | UNIQUE cặp; server xác nhận execution đúng criterion, context và môi trường. |

`SATISFIED` cần tiêu chí và evidence tương ứng; `INSUFFICIENT_EVIDENCE` mô tả thiếu căn cứ. Một control có failure đã xác minh và thiếu evidence ở tiêu chí khác vẫn giữ đồng thời hai loại gap. `status` cho biết mức hoàn tất hồ sơ, còn `result` cho biết kết luận control; không suy G trực tiếp từ result.

### 2.6. RiskEvaluation và căn cứ tính RM-01

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `risk_evaluation` | Registry, assessment/context/scenario snapshot/method, type, intended basis, preconditions/horizon/plausibility/confidence, raw input, input validity; aggregate/cận E/F/G/I_total/P/L/R25; raw/final levels/gates; status/score/mode/review; path inventory, missing/determination/review reasons; predecessor | DDL kiểm miền, thứ tự cận, công thức P/L/R25, NULL khi input invalid và sự nhất quán score_determined với hai cận. Score và hai cận score sinh từ R25/25. |
| `risk_factor` | E hoặc F; known value hoặc bounds; source kind, confirmation/bounds confirmation, actor/time, disputed, rationale/source | UNIQUE evaluation/factor. Known value phải bằng hai cận, CONFIRMED, không disputed. UNKNOWN mặc định [1,5]; miền hẹp cần bounds confirmation. |
| `excluded_control` | Evaluation, control version, F_COUNTERFACTUAL/INHERENT, rationale | UNIQUE evaluation/control/kind; tách tập bỏ control để chấm F khỏi giả định loại bỏ trong INHERENT. |
| `risk_path` | Evaluation/path code, description, coverage, strength, applicability và xác nhận, g/bounds, confirmation/bounds actor/time, disputed, rationale/source | UNIQUE evaluation/path. N/A phải được xác nhận và g/cận NULL. VERIFIED_UNCOVERED đòi g=5 và strength=NONE. |
| `risk_path_control` | Path, control assessment, criterion result tùy chọn, coverage/strength reasons | FK ghép criterion/result assessment ngăn ghép criterion của assessment khác. Mapping chỉ là căn cứ; không có phép đổi control result → g cố định. |
| `impact_factor` | Một trong C/I_integrity/A/B; value/bounds, confirmation/bounds actor/time, disputed, rationale/source | UNIQUE evaluation/dimension. Quy tắc known/bounds như risk_factor. Đủ bốn chiều là bất biến tập hợp do service kiểm. |
| `factor_evidence` | Đúng một E/F factor, path hoặc impact factor; revision và verification decision | CHECK đúng một đích; FK ghép exact revision/decision. |
| `risk_validation_issue` | Evaluation, issue code, field path, message, source | Giữ lỗi nghiệp vụ và vị trí input; không bỏ raw input sai miền để “làm sạch” lịch sử. |
| `input_confirmation` | Registry, assessment, target snapshot, target type, field path, bounds tùy loại, reason | FACTOR_BOUND/PATH_BOUND có cận hợp lệ; PATH_NOT_APPLICABLE không có cận. Quyết định không sửa input snapshot đích. |
| `input_confirmation_evidence` | Confirmation, revision, verification decision | FK ghép exact revision/decision; UNIQUE bộ ba. |
| `risk_input_confirmation` | Evaluation mới, confirmation, field path | UNIQUE bộ ba; snapshot mới ghi rõ đã dùng confirmation nào cho trường nào. |
| `impact_confirmation`, `impact_confirmation_dimension` | Registry, evaluation được review/reason; dimension và exact impact factor | UNIQUE confirmation/dimension. Service kiểm factor thuộc đúng evaluation/dimension và quyền risk.impact_review. |
| `risk_impact_confirmation` | Evaluation mới ↔ impact confirmation | UNIQUE cặp; lưu quyết định được dùng để chuẩn hóa impact ở bản mới. |

Các giá trị raw do client nộp nằm trong `raw_input`; các dòng typed chỉ biểu diễn input có hiệu lực sau xác minh. Điểm `6`, `1.5` hoặc cận đảo ngược không ép về `score_1_5`: lưu raw, ghi issues, tạo kết quả `input_valid=false`, `NEEDS_REVIEW`, `score_determined=false`, toàn bộ score/R25/nhãn/cận tính toán NULL. Request sai quyền, tham chiếu ngoài scope hoặc lỗi cấu trúc giao thức bị từ chối ở API, không trở thành một kết quả risk hợp lệ.

Với dữ liệu cấu trúc hợp lệ nhưng chưa đủ căn cứ, giữ UNKNOWN. Service chuẩn hóa template PROPOSED, source chưa xác minh, điểm đang tranh chấp và claim confirmation không có quyết định phù hợp thành UNKNOWN; không coi cờ boolean từ client là phê duyệt. Cận hẹp cần chính căn cứ giới hạn miền đã được xác nhận.

`G=max(g của các đường applicable)` và `I_total=max(C,I_integrity,A,B)` được tính bằng hai đầu miền theo RM-01. Aggregate xác định không xóa UNKNOWN của thành phần. Ví dụ `(C,I_integrity,A,B)=(5,UNKNOWN,1,2)` có I_total=5 nhưng vẫn NEEDS_REVIEW; số chiều bằng max nằm trong [1,2]. E=F=1 có thể cho score xác định dù G chưa biết.

R25 là số nguyên chuẩn:

```text
P = (2E + 3F) / 5
L = 1 + (P − 1) × G / 5
R25 = I_total × (25 + (2E + 3F − 5) × G)
score = R25 / 25
```

Hai cận R25 bằng nhau mới cho `score_determined=true`. Raw level dùng ngưỡng 125/250/425; impact gate giữ LOW khi I_total=1, tối đa MODERATE khi I_total=2. Service kiểm level/gate theo method version, không dùng điểm hiển thị đã làm tròn. Hiển thị điểm/cận dưới cắt xuống một chữ số thập phân, cận trên làm tròn lên; kết quả chính xác vẫn lưu riêng. Confidence không nhân vào R; số technique ATT&CK không tạo likelihood.

### 2.7. Gap, treatment, retest và so sánh

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `gap` | Assessment/scope, CONTROL_GAP hoặc EVIDENCE_GAP, nguồn control/risk, criterion tùy chọn, owner/description/state/version, closure decision | Có ít nhất một nguồn assessment; CLOSED cần closure reference. Không UNIQUE theo source loại bỏ gap thứ hai. |
| `treatment_plan` | Assessment, owner, scope, objective, response, state/version | Response MITIGATE/AVOID/TRANSFER/ACCEPT là ý định xử lý; ACCEPT vẫn cần quyết định acceptance riêng. |
| `treatment_task` | Plan tùy chọn, scenario/scope, code, owner, description, due, expected retest evidence, state/version, closure decision | API v0.1 hỗ trợ task độc lập; danh sách expected_retest_evidence phải có phần tử. CLOSED cần closure reference; READY_FOR_RETEST chưa phải đã hoàn tất. |
| `task_gap` | Task ↔ gap | UNIQUE cặp; service kiểm cùng assessment/phạm vi và đóng từng đích đúng tiêu chí. |
| `treatment_approval` | Registry, task/exact task version, APPROVED/REJECTED, reason | Phê duyệt hành động xử lý riêng khỏi quyết định đóng; sửa task phải đánh giá lại approval tương ứng. |
| `retest_request` | Assessment/scope/context, primary task/control tùy chọn, baseline risk tùy chọn, requester/time/reason, state/version | Request mutable về workflow. Membership baseline/task/evidence ở bảng con là chính thức; service yêu cầu baseline hợp lệ. |
| `retest_baseline_control`, `retest_task`, `retest_evidence` | Request → các control assessment, task và evidence revision | UNIQUE từng cặp; giữ nhiều đầu vào như arrays trong API, không lấy một phần tử rồi bỏ phần còn lại. |
| `retest_result` | Registry, request, primary control tùy chọn/risk assessment mới, conclusion/reason | Lưu output riêng, giữ nguyên baseline và evidence revision đã dùng trước đó. |
| `retest_result_control` | Result → các control assessment mới | UNIQUE cặp; service kiểm là output mới, đúng phạm vi và ít nhất một output có ý nghĩa. |
| `assessment_comparison` | Registry, before/after risk, progress rule, treatment plan tùy chọn, comparability/checks/reasons, R/impact progress, verified_worsening, mode/review, attribution/reason/confirmer | Before ≠ after. Không comparable phải ghi lý do, hai progress NOT_COMPARABLE, verified_worsening NULL. SUPPORTED cần INDEPENDENT_REVIEWED, CONFIRMED và confirmer/time. |
| `comparison_treatment` | Comparison → task và exact task version | UNIQUE comparison/task. Version phải phân giải được từ mutable_entity_history; treatment plan chỉ là grouping tùy chọn. |
| `comparison_attribution_evidence` | Comparison, exact revision/verification decision, purpose | FK ghép ngăn quyết định sai revision; UNIQUE bộ ba. Purpose ghi vai trò căn cứ quy kết liên hệ treatment. |
| `comparison_impact_dimension` | Comparison, dimension, before/after impact factor, direction/reason | UNIQUE comparison/dimension. Service kiểm FK thuộc đúng before/after và cùng dimension. |
| `comparison_impact_summary` | Comparison, BEFORE/AFTER; I_total/cận, max count/cận | UNIQUE comparison/side. Số đơn chỉ có khi hai cận tương ứng co lại; max xác định không buộc count xác định. |
| `comparison_gap` | Comparison, gap, CLOSED/STILL_OPEN/NEW, state before/after, reason, closure decision | UNIQUE comparison/gap; CLOSED đòi quyết định đóng. |

Comparison chỉ diễn giải tiến bộ khi cùng scenario/sự kiện, scope, context và tiền điều kiện tương thích, cùng profile/rubric, cùng assessment type CURRENT–CURRENT hoặc INHERENT–INHERENT. Service tính và lưu từng phép kiểm; FK chỉ bảo đảm đích tồn tại, không chứng minh comparability. CURRENT–INHERENT hoặc thay đổi trọng yếu trả NOT_COMPARABLE. Hai snapshot EVALUATED vẫn có thể không so được.

`R_progress`, `impact_progress`, `gap_progress` độc lập. Nếu còn range thì `R_progress=UNDETERMINED` khi context so được; không lấy trung điểm tính mức giảm. `verified_worsening` là ba giá trị true/false/null. Attribution SUPPORTED cần review độc lập CONFIRMED và tập task/evidence xác định; giảm R không tự chứng minh quan hệ nhân quả, không tự đóng gap/task. Constraint trigger hoãn `supported_attribution_payload` đòi ít nhất một comparison_treatment và comparison_attribution_evidence trước commit. Service còn kiểm actor độc lập, task version, evidence usable và liên hệ với các chiều đủ căn cứ.

### 2.8. Review, phân xử và quyết định nghiệp vụ

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `review_request` | Target snapshot/type, requester, reviewer assignment, requested/expiry, due tùy chọn, lifecycle, reason/version | FK ghép target ID/kind. Due là hạn mong muốn; expiry bắt buộc do server giới hạn theo assignment/chính sách. PENDING riêng khỏi review_outcome. |
| `review_decision` | Registry, request, original/resulting snapshots, outcome, original/reviewer opinions, reason/evidence basis, attribution confirmation | Một quyết định/request; original ≠ resulting. Confirmed hay disputed đều tạo snapshot kết quả mới. |
| `adjudication_decision`, `adjudication_review` | Registry, primary review tùy chọn và tập review decisions; original/disputed/replacement/resulting snapshots, resolved fields, outcome/reason | Outcome ADJUSTED_NEW_SNAPSHOT; kết quả khác các snapshot đầu vào. UNIQUE adjudication/review. Không sửa nhận định người chấm. |
| `priority_proposal`, `priority_proposal_member` | Assessment, proposer/time, proposal/reason; các risk evaluation và proposed rank | Proposal giữ đề xuất; UNIQUE proposal/evaluation, rank nếu có phải dương. Không cấp quyền phê duyệt. |
| `priority_decision`, `priority_decision_member` | Registry, proposal/previous decision, NOT_RANKED/RANKED, decision type, approval_action, user confirmation/reason; evaluation/rank/rationale | RANKED cần RISK_OWNER_APPROVAL và confirmation khác NOT_RECORDED. Approval action APPROVE/REJECT bắt buộc cho Risk Owner, NULL với reviewer determination; REJECT giữ NOT_RANKED. |
| `risk_acceptance` | Registry, exact risk evaluation, previous acceptance, validity interval, conditions, residual limitations, reason, ACCEPTED/REVOKED | Khoảng hiệu lực hợp lệ; thu hồi bằng quyết định mới. Không sửa raw risk, UNKNOWN, failure hoặc gap. |
| `closure_decision` | Registry, đúng một gap/task, primary control assessment/retest result tùy chọn, APPROVED/REJECTED, criteria met, reason/limitations, target version trước/sau | APPROVED cần criteria_met và version sau = trước+1; REJECTED giữ version. Service kiểm đúng target/permission. |
| `closure_evidence` | Closure, revision, verification decision | FK ghép exact revision/decision; giữ căn cứ đóng lịch sử. |
| `closure_criterion`, `closure_criterion_evidence` | Closure, criterion version, control assessment, satisfied/reason; exact revision/verification quyết định từng criterion | UNIQUE các bộ liên kết; lưu đủ nhiều tiêu chí như API, không thay bằng một boolean tổng. |

Độc lập review là điều kiện về actor và quyền, không phải nhãn client tự chọn. Service phải lấy actor từ phiên, kiểm assignment còn hiệu lực và actor khác tác giả đối tượng được review; verification độc lập cũng phải đối chiếu người thực hiện/thu thập theo quy tắc. `INDEPENDENT_REVIEWED` không tự có nghĩa CONFIRMED, EVALUATED hoặc score đã xác định.

Review disputed giữ cả ý kiến và bằng chứng, tạo snapshot mới NEEDS_REVIEW. Yếu tố tranh chấp trở thành UNKNOWN với cận được xác nhận nếu có. Tranh chấp context thiết yếu có thể chặn cả range. Phân xử dùng candidate được dựng từ input đã giải quyết và quyết định có quyền; không lấy trung bình hoặc thay trực tiếp snapshot gốc.

### 2.9. Report, audit và vận hành

| Bảng | Dữ liệu và quan hệ chính | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| `report_snapshot` | Registry, assessment, as_of, schema version, title, limitations, frozen context | Báo cáo là snapshot; frozen_context là JSON object, không đọc lại latest inventory để thay quá khứ. |
| `report_snapshot_member` | Report → registry snapshot, section code | UNIQUE report/reference/section; không tự trỏ. Section và kind phải tương thích do service kiểm. |
| `report_gap_snapshot` | Report, gap/source version, kind/state/owner/description, closure decision | UNIQUE report/gap; bản chụp trạng thái, CLOSED cần closure. |
| `report_task_snapshot` | Report, task/source version, state/owner/description/due, closure decision | UNIQUE report/task; snapshot không đổi khi task hiện tại đổi. |
| `audit_event` | Recorded time, actor/session, action/target, outcome/reason code, correlation ID, scope, authorization version/gate time, safe metadata | ALLOWED/DENIED/FAILED; JSON object. Không ghi token, password, evidence bytes hoặc dữ liệu nhạy cảm nguyên văn. |
| `idempotency_operation` | Organization/principal/method/canonical path/key; request hash/expected version, state/lease/time, result status/IDs/metadata, version | UNIQUE namespace thao tác; SUCCEEDED phải có 2xx. Hash khác với cùng key bị conflict; replay vẫn kiểm quyền hiện hành. |
| `upload_operation` | Idempotency op, evidence item/revision, receiving/scan/stage/commit state, temporary/final key, actual hash/size, expected item version, lease, scanner versions/failure, version | Một operation/idempotency; revision một lần. COMMITTED cần revision ID. File ngoài DB cần reconciliation. |
| `background_job` | Requester/session, idempotency, kind/scope, payload/schema, queue state, attempts/lease/deadline/failure/version, fencing token | EXPORT/RECONCILE_STORAGE/BACKUP_MANIFEST; worker tái kiểm quyền, input version và deadline, kiểm token để worker hết lease không phát hành kết quả. |
| `export_artifact` | Một artifact/job, report, requester/scope, private storage key/hash/size, created/expiry, state/version | AVAILABLE/EXPIRED/REMOVED/INTEGRITY_FAILED; hết hạn sau created. Download kiểm quyền và hash hiện hành. |

Audit là lịch sử thao tác; snapshot là dữ liệu nghiệp vụ tái lập. Không dùng audit thay cho lưu decisions, inputs hoặc graph báo cáo. Với thao tác bị từ chối, ghi audit an toàn ngoài transaction nghiệp vụ bị rollback, theo cơ chế vận hành được quy định trong tài liệu storage/transactions.

## 3. Trạng thái và NULL

| Trục | Giá trị lưu | Ý nghĩa |
| --- | --- | --- |
| Hoàn tất đánh giá | `EVALUATED`, `NEEDS_REVIEW` | Đủ căn cứ/hồ sơ; không đồng nhất với có số. |
| Có điểm risk | `score_determined=true/false` | Chỉ true khi R25_lo=R25_hi với input hợp lệ. Control luôn false + NOT_APPLICABLE. |
| Loại risk | `CURRENT`, `INHERENT`, `ILLUSTRATIVE` | INHERENT giữ controls bị loại; ILLUSTRATIVE phải ghi intended basis, không vào register như kết quả thật. |
| Mode | `SELF_ASSESSED`, `INDEPENDENT_REVIEWED` | Ai thực hiện và đã có review độc lập hợp lệ hay chưa. |
| Outcome review | `NONE`, `CONFIRMED`, `DISPUTED`, `ADJUSTED_NEW_SNAPSHOT` | Đóng băng trong từng snapshot. Chờ review nằm ở lifecycle request. |
| Control result | `NOT_ASSESSED`, `SATISFIED`, `PARTIALLY_SATISFIED`, `NOT_SATISFIED`, `INSUFFICIENT_EVIDENCE` | Kết luận control, không có phép đổi cố định thành risk score. |
| Test execution | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_READY` | Trạng thái thực thi test/thu quan sát; tách control result. |
| Evidence decision | `VERIFIED`, `REJECTED` | Theo revision, scope, actor và hiệu lực của decision. Không có decision dùng được được suy ra ở service. |
| File storage | `STAGED`, `COMMITTED`, `INTEGRITY_FAILED`, `ORPHANED` | Tình trạng bytes; VERIFIED không thay thế trạng thái này. |
| Xác nhận | `PROPOSED`, `CONFIRMED` | Có quyết định/căn cứ phù hợp; client claim không đủ. |
| Scope kind | `ORGANIZATION`, `SELECTED` | Cách chọn phạm vi; mọi chiều đã chọn giao nhau. |
| Scenario | `DRAFT`, `ACTIVE`, `RETIRED` | Service kiểm đủ context trước ACTIVE. |
| Request review | `PENDING`, `COMPLETED`, `CANCELLED`, `EXPIRED` | Workflow mutable riêng khỏi kết quả snapshot. |
| Gap | `OPEN`, `IN_PROGRESS`, `CLOSED` | CLOSED qua ClosureDecision hợp lệ. |
| Plan | `DRAFT`, `ACTIVE`, `COMPLETED`, `CANCELLED` | Mức tiến triển kế hoạch; không phải điểm control/risk. |
| Task | `OPEN`, `IN_PROGRESS`, `READY_FOR_RETEST`, `CLOSED`, `CANCELLED` | PATCH thông thường không cấp phép vượt qua closure. |
| R progress | `DOWN`, `UP`, `SAME`, `NOT_COMPARABLE`, `UNDETERMINED` | UNDETERMINED khi so được context nhưng còn range. |
| Impact progress | `NOT_COMPARABLE`, `INCOMPLETE`, `MIXED`, `IMPROVED`, `WORSENED`, `UNCHANGED` | Tính từ bốn chiều và căn cứ; không cộng hoặc lấy trung bình. |
| Attribution | `SUPPORTED`, `REVIEW_REQUIRED` | Review quan hệ với treatment; tách riêng comparability và impact progress. |

NULL phải đọc cùng trạng thái: factor NULL + bounds là UNKNOWN; input invalid làm output/cận NULL; path N/A đã xác nhận có g/cận NULL; `verified_worsening=NULL` là chưa kết luận/không so được, không tương đương false. Các FK tùy chọn NULL không trao thêm quyền hoặc khẳng định “không có rủi ro”.

## 4. Ràng buộc DB và bất biến service

| Bất biến | DB thực thi/biểu diễn | Service phải kiểm trước commit |
| --- | --- | --- |
| Một SME, định danh | PK, UNIQUE, organization singleton | Seed đúng một organization; tất cả đối tượng và selector cùng deployment. |
| Scope | FK selector, CHECK đúng một object | Intersection branch/object, containment parent, assignment assessment, user active/expiry; không mở rộng scope từ mảng rỗng. |
| Revision/evidence | FK ghép predecessor/head/decision với exact item hoặc revision | Chọn quyết định đang có hiệu lực, đúng scope/môi trường/time, chưa bị quyết định mới thay thế; FILE phải COMMITTED và hash đúng. |
| Snapshot graph | Registry, FK, append-only và cơ chế đóng graph | Hash canonical bao đủ nội dung/link; insert đủ children trong transaction; không bỏ cạnh khỏi hash. |
| Input risk | Miền integer, bounds, checks công thức và NULL branch | Không cast/kẹp raw input trước validation; xác nhận nguồn/loại, aggregate từ đúng các yếu tố, đủ 2 E/F + 4 impact, rà soát path inventory. |
| Known/UNKNOWN | CHECK known=hai cận, confirmed, not disputed; hẹp cần confirmation | Kiểm chính actor, decision ID và evidence cho confirmation; unsupported claims → UNKNOWN. |
| EVALUATED | CHECK input hợp lệ/điểm xác định/path inventory/missing arrays | Không còn UNKNOWN/tranh chấp/căn cứ thiếu; arrays phải phản ánh thực tế, không chỉ gửi mảng rỗng. |
| Mode review | Enum; snapshots/decisions liên kết | Actor độc lập, permission/assignment hiện hành, target đúng loại; kết quả tạo mới. |
| Retest/comparison | FK before/after, CHECK non-comparable output, summary bounds; SUPPORTED đòi independent+confirmed và children task/evidence | Snapshot mới sau baseline; cùng assessment/type/context thích hợp; đúng từng chiều; ba progress riêng; xác minh task version, evidence và quan hệ treatment. |
| Priority/acceptance | CHECK kiểu quyết định, rank dương, hiệu lực | Risk Owner đủ quyền; rank đầy đủ/không trùng; không xếp từ midpoint/range; acceptance không che UNKNOWN. |
| Closure | CHECK một target, APPROVED cần criteria, CLOSED có reference | Decision APPROVED đúng target, đúng expected_version; evidence/retest/criteria hợp lệ; actor có quyền. |
| Workflow | Enum và version | Chuyển trạng thái cho phép; tăng version đúng một lần, ghi history/audit cùng transaction. |
| Report | FK thành viên, frozen JSON và child snapshots | Tất cả đầu vào không sau as_of; dùng historical versions; current quyền đủ cho toàn graph khi đọc/export. |

Constraint cục bộ không chứng minh bất biến liên bảng hoặc quyền. Ví dụ FK `risk_path_control` bảo đảm criterion result thuộc control assessment nhưng không bảo đảm cùng scenario/environment; FK `closure_decision_id` chỉ chứng minh có decision, chưa chứng minh decision phê duyệt đúng gap. Các phép kiểm này là gate bắt buộc của service, không phải hướng dẫn tùy chọn cho UI.

## 5. Giao dịch, bất biến version và FK

Các dữ liệu mutable gồm inventory, user/session/assignment, hồ sơ assessment, implementation, item head/storage, gap/task/plan, request và queue. Mỗi mutation dùng version dự kiến, khóa các dòng phụ thuộc cần thiết, kiểm quyền và dependencies ngay trước commit, tăng version, ghi `mutable_entity_history`/audit theo phạm vi yêu cầu. Optimistic concurrency không chỉ so version đối tượng đích: context, evidence head, permissions và task được dùng làm căn cứ cũng cần dependency version.

Các snapshot và quyết định là append-only. Bản mới được chèn với registry và toàn bộ child/link trong một transaction; bản cũ không UPDATE/DELETE. `created_txid` là dấu transaction do server đóng, không nhận từ client. Chặn UPDATE/DELETE riêng bảng cha chưa đủ: cần chặn chèn thêm child vào graph đã commit và chặn TRUNCATE/DDL/disable-trigger ở runtime role. Quyền migration owner được tách khỏi runtime role.

DDL thực hiện các lớp này bằng `reject_history_change`, `stamp_transaction`, `require_open_parent` và `require_snapshot_kind`. Trigger cuối kiểm typed payload đúng snapshot_kind và cùng transaction registry; constraint trigger `snapshot_has_payload` hoãn tới cuối transaction để chặn registry không có payload. `check_version_increment` đòi mutable version tăng đúng một; vẫn cần điều kiện expected version khi UPDATE để phát hiện client đọc cũ. Hash nội dung, đủ tập children và mọi quy tắc nghiệp vụ liên bảng tiếp tục do service kiểm.

Retest request chỉ được đổi state/version; `protect_retest_inputs` bảo vệ toàn bộ input còn lại. Các bảng con baseline control/task/evidence được chèn trong transaction tạo request, sau đó chặn sửa/xóa/chèn muộn. Muốn thay bộ input phải tạo request mới; thay state không mở lại tập con đã đóng.

`lineage_id` do server cấp, dùng lại chỉ cho các revision của cùng đối tượng snapshot logic. UNIQUE lineage/revision ngăn hai số revision trùng, không tự bảo đảm predecessor đúng dòng lịch sử. Service đồng bộ revision_number trong registry với số revision typed nếu resource có cả hai, kiểm kind/đối tượng, predecessor và số tăng. Gán lineage tùy ý từ client bị cấm.

Trình tự FK điển hình là scope + selectors → registry → typed parent → children/links → state cập nhật → audit/history/idempotency success. Evidence item được tạo trước revision; head chỉ đổi ở transaction cuối chuyển storage COMMITTED, FK ghép bảo đảm head thuộc item. Closure decision được tạo trước khi đổi gap/task sang CLOSED. Không dùng cascade delete để xóa lịch sử. Các quan hệ self-reference/predecessor phải giữ cùng đối tượng, không chu kỳ và đúng thứ tự tạo; FK và CHECK tự-trỏ chưa thay cho kiểm cả chuỗi.

File bytes nằm ngoài transaction PostgreSQL. Upload đi qua policy gate trước intake, ghi khu tạm và quét, xác minh hash. Transaction ngắn đầu tạo revision bất biến và storage STAGED, chưa đổi item head. Sau flush/rename, transaction cuối kiểm lại quyền/dependencies/hash, chuyển storage COMMITTED, đổi head/version và ghi audit/idempotency cùng nhau. Nếu bước cuối rollback, revision STAGED không được dùng cho verification/assessment hoặc download. Reconciliation giữ/dọn STAGED/ORPHANED theo lease và manifest, không tự commit bằng quyền cũ. Lỗi integrity sau commit cập nhật storage và event, không sửa payload/decision cũ.

`check_storage_transition` cho phép STAGED → COMMITTED/ORPHANED, COMMITTED → INTEGRITY_FAILED, INTEGRITY_FAILED → COMMITTED. Chuyển lại COMMITTED chỉ sau phục hồi đúng bytes/hash và audit; trigger không tự xác minh filesystem. REFERENCE không có bytes nội bộ, COMMITTED chỉ ghi nhận metadata đã lưu. Chi tiết crash recovery, reauthorization và backup ở [thiết kế storage/giao dịch](storage-transactions-v0.1.md).

Idempotency được định danh bởi organization + principal + method + canonical path + key và hash payload canonical. Cùng key cùng payload trả kết quả gốc sau kiểm quyền; khác payload trả conflict. Worker và upload dài không giữ quyền từ lúc enqueue: kiểm lại trước commit/phát nội dung, đồng bộ với `authorization_guard` và expiry. Lease/deadline tránh hai worker cùng hoàn tất; chỉ đánh dấu success sau khi transaction nghiệp vụ thành công.

Index hiện tại ưu tiên active assignment, snapshot theo scope/time, revision theo item, verification theo revision, control/risk theo context, open gap, audit theo actor/target, history as_of và queue/upload lease. PostgreSQL không tự tạo index cho mọi FK; bước 06 kiểm query plan với workload thực và bổ sung index có căn cứ, không coi danh sách thiết kế là hiệu năng đã đạt.

## 6. Ánh xạ API sang SQL

API trả DTO theo nghiệp vụ; một resource có thể tổng hợp registry, bảng typed và children. Không yêu cầu tên JSON trùng tên cột. Các ánh xạ dưới đây phải được adapter thực hiện rõ, không lược bỏ metadata khi ghi.

| API/field | Nơi lưu hoặc cách dựng |
| --- | --- |
| Resource snapshot `id`, `created_by`, `created_at`, `content_sha256`, `scope` | ID chung với registry; `snapshot_registry.created_by/created_at/content_hash`; scope + selectors. Hash bytes của evidence vẫn là trường riêng của revision. |
| Mutable resource `version`, updated metadata | Version ở bảng thực thể; actor/time và canonical state của version trong `mutable_entity_history`. |
| Inventory `KnownText`, `sources`, `scope`, `state` và metadata có cấu trúc | `api_payload` có schema version; FK typed/cột chiếu/bảng nối phải khớp canonical payload. Không biến UNKNOWN thành chuỗi rỗng rồi bỏ lý do/nguồn. |
| Snapshot `revision_number` | `snapshot_registry.revision_number` với `lineage_id`; typed revision number ở evidence/auth profile phải được service đồng bộ. |
| `Scope.branch_ids/system_ids/asset_ids/data_asset_ids/scenario_ids/assessment_ids` | `scope_branch` và các dòng `scope_object` typed; service tạo scope_kind và content hash. Mọi arrays đều bắt buộc ở API, có thể rỗng nhưng không cấp wildcard. |
| Snapshot canonical DTO | `snapshot_registry.api_payload`/schema version; đồng bộ các cột typed và children, không để thêm ID ngoài scope ẩn trong JSON. |
| `ScenarioSnapshot`, `scenario_snapshot_id` | `scenario_snapshot` và FK trên risk_evaluation; scenario membership qua assessment_scenario, không dựa duy nhất primary display scenario. |
| `RiskEvaluation.inputs` | `risk_evaluation.raw_input` canonical, giữ claim ban đầu kể cả sai miền. |
| `RiskEvaluation.effective_inputs` | Factors/paths/impact/excluded-control rows và các căn cứ đã được server chuẩn hóa; không thay raw input. |
| `E`, `F`, `C`, `I_integrity`, `A`, `B`, `paths[].path_id` | `risk_factor.factor_code`; `impact_factor.dimension`; `risk_path.path_code`. |
| `not_applicable` | Đảo nghĩa với `risk_path.applicable`; chỉ loại đường khỏi max khi có confirmation hợp lệ. |
| Factor/path `confirmation_decision_ids`; `impact_confirmation_ids` | `risk_input_confirmation` với field_path và `risk_impact_confirmation`; đích là append-only input/impact confirmations, actor/time/scope lấy từ registry. |
| `precondition_plausibility` | `risk_evaluation.plausibility`: LOW/MEDIUM/HIGH/UNKNOWN. MEDIUM ở đây là nhãn plausibility riêng; risk level dùng MODERATE. |
| `R25`, `R25_range`, `G_range`, `I_total_range` | `r25`, cặp `r25_lo/r25_hi`, `g_lo/g_hi`, `i_total_lo/i_total_hi`; NULL object khi input invalid. |
| `P`, `L`, `P_range`, `L_range` | P/L đơn dựng khi hai cận tương ứng bằng nhau; ranges từ `p_lo/p_hi`, `l_lo/l_hi`. |
| `score`, `score_range` | Generated numeric từ R25; API serialize decimal string chính xác, không binary floating point. |
| `display_score`, `display_score_range` | Dựng từ R25 nguyên theo floor/ceil một chữ số thập phân, không lưu làm đầu vào phân mức. |
| `raw_level_range`, `level_range`, `possible_impact_gates` | Các cột level lo/hi và `impact_gate_possibilities`. |
| `validation_issues` | `risk_validation_issue`; control issues nằm trong snapshot unresolved issues có schema. |
| `EvidenceUse` | Các bảng `criterion_evidence`, `factor_evidence`, `test_execution_evidence`, `closure_evidence`; scope được kiểm với registry của revision/decision và scope tiêu chí/snapshot. |
| `EvidenceLinkInput.criterion_version_ids`, `purpose` | `evidence_link_criterion` và `evidence_link.rationale`; không bỏ các tiêu chí sau phần tử đầu. |
| `RiskControlLinkInput.scope`, `purpose` | `scenario_control.scope_id/rationale`, created actor/time và canonical payload; link append-only. |
| `ControlImplementationWrite.authentication_profile_version_id` | FK cùng tên trên control_implementation; snapshot assessment còn chụp cấu hình implementation đã dùng. |
| `supersedes_*` | Predecessor/supersedes FK tương ứng; không phải UPDATE resource cũ. |
| `ReviewRequest.requested_reviewer_id`, `due_at` | Reviewer user được chọn qua reviewer_assignment_id hợp lệ; due_at giữ riêng, expires_at do server giới hạn, không lấy NULL due làm quyền vô hạn. |
| `Adjudication.review_decision_ids`, `resolved_fields` | `adjudication_review` và `adjudication_decision.resolved_fields`; cột primary review chỉ phục vụ tham chiếu chính. |
| `PriorityDecision.decision` | `priority_decision.approval_action=APPROVE/REJECT`, độc lập với kết quả RANKED/NOT_RANKED và decision_type. |
| Retest `before_control_assessment_ids`, `task_ids`, `new_evidence_revision_ids` | `retest_baseline_control`, `retest_task`, `retest_evidence`; context và reason nằm trên request. |
| Retest `after_control_assessment_ids`, `after_risk_evaluation_id` | `retest_result_control` và `retest_result.risk_evaluation_id`; request hoàn tất gắn result snapshot. |
| Retest `state=ASSESSMENTS_RECORDED` | DB `retest_request.state=COMPLETED`; REQUESTED ánh xạ trực tiếp. Không có endpoint v0.1 tạo IN_PROGRESS/CANCELLED nên service không phát sinh các trạng thái DB mở rộng đó trong luồng API hiện hành. |
| `TaskWrite.expected_retest_evidence`, `scope`, `scenario_id` | Các cột trực tiếp ở treatment_task; plan_id tùy chọn cho task độc lập. |
| `ClosureInput.criteria[]` | `closure_criterion` + `closure_criterion_evidence`; target/version trước-sau trên closure_decision; primary control ID không thay thế tập criteria. |
| `control_result`, criterion `reason` | `control_assessment.result`, `control_assessment_criterion.result/reasoning`; kiểm riêng execution status. |
| Criterion `test_case_codes`, `test_run_reference`, `missing_reasons`, `verified_failure` | Các cột cùng tên trên control_assessment_criterion; raw_input giữ claim ban đầu. Test code chỉ được service resolve sang test_case_version phù hợp; codes/reference không thay exact execution/evidence link. |
| Comparison `comparability`, `R_progress` | `comparable` boolean ↔ COMPARABLE/NOT_COMPARABLE; `r_progress`. |
| Comparison `impact_dimensions`, summaries, gap_progress | Các bảng `comparison_impact_dimension`, `comparison_impact_summary`, `comparison_gap`. |
| `ComparisonInput.treatment_task_ids`, `attribution_evidence_uses` | `comparison_treatment` giữ task version tại thời điểm chụp; `comparison_attribution_evidence` giữ revision/decision/purpose. Chỉ review độc lập xác nhận mới tạo snapshot SUPPORTED. |
| Comparison `R25_change`, `score_change`, dimension lists | Dựng từ exact snapshots/directions khi comparable và xác định; còn range thì change NULL. |
| `impact_progress_rule_version` | `risk_method_version.progress_rule_version` qua FK của comparison. |
| `ReportSnapshot.graph`, member ID arrays | `frozen_context`, `report_snapshot_member`, report gap/task snapshots và historical inventory đã đóng băng; không đọc latest thay thế. |
| `GapSnapshot`, `TaskSnapshot` | ID riêng của report child; created actor/time từ report registry; scope phải lấy bản chụp của source version trong frozen graph/history, không scope mutable hiện tại. |
| `write_context`, If-Match/expected version, Idempotency-Key | Command metadata cho dependency/authorization/version checks, `idempotency_operation` và audit; không coi là dữ liệu nghiệp vụ do client tự xác nhận. |

Các endpoint ghi snapshot (`/context-snapshots`, `/control-assessments`, `/risk-evaluations`, `/review-decisions`, `/adjudications`, `/assessment-comparisons`, `/closure-decisions`, `/reports`) gọi một transaction service chuyên biệt; không phát endpoint PATCH tùy ý lên các bảng lịch sử. `/evidence-items/{id}/evidence-revisions` dùng luồng upload qua gate và intake; multipart không được miễn auth/scope. Metadata read và content download có quyền riêng.

## 7. Truy vết và giới hạn kiểm chứng

| Yêu cầu | Nhóm dữ liệu |
| --- | --- |
| NOTE-01 | Organization/branch, scope selectors, assignment assessment/expiry, authorization guard. |
| NOTE-02 | Revision, verification decision, exact composite FK, registry actor/time/scope. |
| NOTE-03 | Versioned criteria, criterion results/test execution/evidence, đồng thời hai gap kinds. |
| NOTE-04 | Raw/effective risk inputs, E/F/exclusions, per-path G, impact vector, R25/bounds/gates và trạng thái độc lập. |
| NOTE-05 | Comparison, dimension/summary/gap children, attribution và review. |
| NOTE-06 | Pending request riêng, review/adjudication/priority/closure snapshots, version/idempotency. |
| NOTE-07 | Upload operation, storage states, transaction recheck và evidence item head. |
| NOTE-08 | Role/permission/assignment với provenance của seed; service không suy quyền từ UI. |
| NOTE-09 | Storage state, verification mode, assessment mode/review outcome/status/score phân biệt. |
| NOTE-10 | Authentication profile version riêng CRM, cấu hình chưa phê duyệt giữ TO_SET_BEFORE_LAB. |

Đây là thiết kế dữ liệu. Chưa chạy migration/transaction/permission/fault tests, CRM, T01–T24, FLOW hoặc VALID-G-01; các mục đó thuộc bước 06 và vẫn NOT_RUN. Phiếu G A/B còn trống; chưa xác nhận độ tin cậy giữa người chấm hoặc hiệu chuẩn SME. ILLUSTRATIVE, fixture và metadata tool/test không được trình bày như evidence môi trường thật. MF-03/MF-04 giữ NOT_RANKED và chưa có phê duyệt SME.
