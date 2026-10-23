# Hợp đồng API VN Digital Trust v0.1

Ngày 2026-10-20; đối chiếu API/SQL cập nhật 2026-10-21. Thiết kế bước 05 cho một SME, hai chi nhánh; chưa triển khai dịch vụ hoặc chạy lab. [OpenAPI 3.1.1](openapi-v0.1.yaml) định nghĩa đường dẫn, method, header, kiểu dữ liệu, trường bắt buộc và ví dụ; tài liệu này quy định ý nghĩa nghiệp vụ. Dùng cùng [storage/giao dịch](storage-transactions-v0.1.md), [mô hình dữ liệu](data-model-v0.1.md), [schema](schema-v0.1.sql), [cấu hình](configuration-v0.1.md) và [RBAC seed](rbac-seed-v0.1.json).

Nguồn đối chiếu: [kế hoạch §27, NOTE-01…10](../planning/execution-plan-v0.1.md#27-khởi-động-bước-05-và-tiếp-nhận-lưu-ý--2026-10-19), [use case v0.2-r1](../use-cases/use-cases-technical-v0.2.md), [RM-01 v0.4-r3](../planning/risk-method-v0.4.md), [CE-01](../planning/control-evidence-v0.1.md), [TC-01](../planning/control-test-cases-v0.1.md). Công thức/rule RM-01 đã đóng băng; API không tạo phương pháp chấm điểm mới.

## 1. Quy ước giao tiếp và đường kiểm quyền

Base path là `/api/v1`; bảng dưới viết đường dẫn sau prefix này. JSON dùng UTF-8; UUID định danh nội bộ, mã nghiệp vụ như SC-01 không thay UUID. Timestamp truyền ISO 8601 có múi giờ, lưu UTC; thời gian hiện hành và actor do server xác định. Decimal kết quả dùng chuỗi ổn định, R25 dùng số nguyên. Request không nhận các trường kết quả, actor, thời gian ghi nhận hoặc hash snapshot do client tự gán; object đóng theo schema, trường ngoài contract bị từ chối.

Mọi request đi Browser → Caddy reverse proxy/TLS → Django/DRF → policy gate → module. Upload/download/export cũng đi cùng đường này. Chỉ CSRF bootstrap và đăng nhập trong API không yêu cầu phiên; health tối thiểu ở cấu hình triển khai không trả domain data. Không công khai DB, worker hoặc đường dẫn kho tệp.

VDT dùng cookie `__Host-vdt_session` với Secure, HttpOnly, SameSite=Lax, Path=/, không Domain. `GET /auth/csrf` cấp CSRF token; mọi request thay đổi trạng thái, kể cả login, cần `X-CSRFToken`. Login đổi session ID; logout hủy phiên và cookie. Session VDT, quyền VDT và profile CRM là ba đối tượng riêng; đăng nhập VDT không chứng minh CRM MFA hoặc cấp quyền CRM.

Gate yêu cầu đồng thời phiên hợp lệ, user active, permission, organization/branch/object scope, assessment assignment nếu áp dụng, chưa revoke và `server_time < expires_at`. Đúng thời điểm hết hạn là deny. Các chiều scope giao nhau; mảng scope rỗng không cấp quyền. `assessment_ids` trong payload không tự tạo assignment; branch của hồ sơ user không tự cấp quyền chi nhánh. Nested IDs và quan hệ xuyên tài nguyên đều phải cùng organization và nằm trong scope hiện hành.

List lọc quyền trước phân trang, count, tìm kiếm hoặc tạo cursor. Cursor opaque, `limit` mặc định 50, tối đa 200; `q` là tìm tên/mã thuần văn bản. Bộ lọc không mở rộng quyền. Detail ngoài scope không tiết lộ tồn tại; dùng 404 theo chính sách chống dò ID. Thiếu quyền cho một thao tác đã biết dùng 403. Report không cấp quyền mở bytes evidence.

## 2. Bảng endpoint theo use case

Ký hiệu `GET/POST /x` chỉ hai method trên collection; detail và command được liệt kê riêng. OpenAPI là danh mục đầy đủ, gồm schema request/response và quyền của từng operation.

| UC | Endpoint | Kết quả và ràng buộc |
| --- | --- | --- |
| TUC-01 | `GET /auth/csrf`; `GET/POST/DELETE /auth/session`; `POST /auth/password` | Bootstrap/login/session/logout/đổi mật khẩu VDT; không ghi credential vào response/audit. |
| TUC-01 | `GET/PATCH /organization`; `GET/POST /branches`; `GET/PATCH /branches/{id}` | Một organization duy nhất; quản lý chi nhánh có version. |
| TUC-01 | `GET/POST /users`; `GET/PATCH /users/{id}`; `POST /users/{id}/credential-resets` | Quản trị user; reset buộc đổi mật khẩu, disable/revoke có hiệu lực tại gate. |
| TUC-01 | `GET /permissions`, `/roles`; `GET/POST /role-assignments`; `GET /role-assignments/{id}`; `POST /role-assignments/{id}/revocations` | Cấp/thu hồi quyền, scope, assigned assessment, hiệu lực và expiry; có audit. |
| TUC-02 | `GET/POST /systems`, `/assets`, `/data-assets`, `/vendors`, `/data-flows`; `GET/PATCH /{collection}/{id}` | Inventory mutable, giữ lịch sử thay đổi; UNKNOWN cần lý do/nguồn. |
| TUC-02 | `POST /context-snapshots`; `GET /context-snapshots/{id}` | Chụp context bất biến; sửa inventory không thay giá trị đã chụp. |
| TUC-03 | `GET/POST /scenarios`; `GET/PATCH /scenarios/{id}`; `POST /scenarios/{id}/transitions`; `GET /scenario-snapshots/{id}` | DRAFT→ACTIVE cần target/owner/context hợp lệ; snapshot lưu sự kiện, hậu quả, scope và nguồn. |
| TUC-04 | `GET/POST /assessments`; `GET /assessments/{id}`; `POST /risk-evaluations`; `GET /risk-evaluations/{id}` | Assessment là hồ sơ; RiskEvaluation là snapshot đầu vào, effective inputs và kết quả RM-01. |
| TUC-04 | `GET /risk-register`; `POST /impact-confirmations`; `GET /impact-confirmations/{id}` | Register lấy CURRENT/INHERENT được phép; xác nhận impact append-only theo scope. |
| TUC-05 | `GET/POST /control-definitions`; `GET /control-definitions/{id}`, `/control-criteria/{id}` | Version catalog/criteria bất biến; catalog không chứng minh triển khai. |
| TUC-05 | `GET/POST /control-implementations`; `GET/PATCH /control-implementations/{id}`; `POST /risk-control-links`; `GET /risk-control-links/{id}` | Gắn control, scenario, implementation và scope. |
| TUC-05 | `GET/POST /authentication-profiles`; `GET /authentication-profiles/{id}` | Append profile CRM có trạng thái cấu hình; không triển khai CRM hoặc bắt đầu lab. |
| TUC-05 | `GET/POST /evidence-items`; `GET /evidence-items/{id}`; `POST /evidence-items/{id}/evidence-revisions` | Tạo logical item và revision FILE/REFERENCE; upload chỉ thành công sau COMMITTED. |
| TUC-05 | `GET /evidence-revisions/{id}`, `/evidence-revisions/{id}/content`; `GET/POST /evidence-links` | Metadata/bytes/link cần quyền evidence và `assessment_id` tại các read operation được khai báo. |
| TUC-05 | `POST /evidence-revisions/{id}/verification-decisions`; `GET /verification-decisions/{id}`; `POST /evidence-requests`; `GET /evidence-requests/{id}` | Quyết định xác minh tách revision; yêu cầu bổ sung không tự tạo hoặc xác minh evidence. |
| TUC-06 | `POST /control-assessments`; `GET /control-assessments/{id}`; `POST /input-confirmations`; `GET /input-confirmations/{id}` | Snapshot theo criterion; confirmation riêng cho cận UNKNOWN hoặc loại đường N/A. |
| TUC-06 | `POST /review-requests`; `GET /review-requests/{id}`; `POST /review-requests/{id}/cancellation`; `POST /review-decisions`; `GET /review-decisions/{id}` | Request có lifecycle; quyết định review tạo snapshot mới, giữ bản gốc. |
| TUC-06 | `POST /adjudications`; `GET /adjudications/{id}` | Phân xử bằng candidate snapshot đã được tạo hợp lệ; ghi quyết định và snapshot kết quả mới. |
| TUC-07 | `GET/POST /gaps`, `/treatment-tasks`; `GET/PATCH /gaps/{id}`, `/treatment-tasks/{id}` | Gap/task có version và lịch sử; PATCH không được đóng. |
| TUC-07 | `POST /treatment-approvals`, `/risk-acceptances`, `/priority-proposals`, `/priority-decisions`; `GET /{collection}/{id}` | Approval/acceptance/proposal/priority là các quyết định riêng. |
| TUC-07 | `POST /retests`; `GET /retests/{id}`; `POST /retests/{id}/completion`; `POST /assessment-comparisons`; `GET /assessment-comparisons/{id}` | Retest tham chiếu revision/snapshot mới; so sánh R, impact, gap độc lập. |
| TUC-07 | `POST /closure-decisions`; `GET /closure-decisions/{id}` | Đóng đúng gap hoặc task khi tiêu chí, evidence/retest và expected version hợp lệ. |
| TUC-08 | `POST /reports`; `GET /reports/{id}`; `POST /reports/{id}/exports`; `GET /exports/{id}`, `/exports/{id}/content`; `GET /audit-events` | Report đóng băng graph as_of; export bất đồng bộ; audit chỉ trong scope quản trị. |

## 3. Ma trận phân quyền

Trong `x-required-permissions`, các phần tử của mảng là AND, dấu `|` trong một phần tử là OR. Bảng là nhóm quyền chính; các OR cho đọc từng snapshot được ghi chính xác ở OpenAPI. Mọi quyền dưới đây còn phải qua scope/assignment/expiry và kiểm tra trường nhạy cảm.

| Domain/thao tác | Quyền ghi/command | Quyền đọc và điều kiện bổ sung |
| --- | --- | --- |
| Organization/branch | `organization.manage` | Cùng quyền; không hàm ý quyền evidence/report. |
| User/credential | `users.manage` | Cùng quyền; đổi mật khẩu cá nhân yêu cầu phiên của chính user. |
| Role/assignment | `roles.assign` | Cùng quyền; không cho client tự mở rộng scope được phép cấp. |
| Inventory/context | `inventory.manage` | List cần quyền quản lý; detail thêm OR `assessment.run`, `assessment.review`, `risk.impact_review`, `report.read` trong scope. |
| Scenario | `risk.propose` | Detail/snapshot thêm OR quyền assessment/impact/report như OpenAPI; ACTIVE vẫn cần đủ điều kiện nghiệp vụ. |
| Assessment/risk evaluation | `assessment.run` | OR theo operation giữa run/review/impact/report/adjudicate; ILLUSTRATIVE không vào register vận hành. |
| Xác nhận impact | `risk.impact_review` | Risk Owner đúng ownership/delegation; không tự tạo evidence hoặc review độc lập. |
| Control definition/implementation/link | `control.manage` | Read bổ sung run/review; link detail cho report.read; không suy SATISFIED từ catalog. |
| Profile CRM | `control.manage` | Cùng quyền và profile/system scope; APPROVED thêm kiểm tra config owner hiện hành. |
| Evidence item/revision/link | `evidence.submit` | Metadata và bytes cần `evidence.read_assigned`; scope phải chứa assessment và evidence liên kết. |
| Xác minh evidence | `evidence.verify` **AND** `evidence.read_assigned` | Đúng revision/scope; tự xác minh có nhãn SELF_ASSESSED. |
| Yêu cầu evidence | `evidence.request` | Read OR request/submit theo scope. |
| Control assessment/retest/comparison | `assessment.run` | Read run/review hoặc report/adjudicate tại operation cho phép. |
| Review request/cancel | `assessment.run` OR `assessment.review` | Creator hoặc reviewer được giao mới được cancel PENDING; đọc thêm adjudicate. |
| Review decision/input confirmation | `assessment.review` | Reviewer được giao, còn hạn, khác tác giả; không ngầm cấp evidence.verify. |
| Phân xử | `assessment.adjudicate` | Risk Owner đúng ownership/delegation, tách actor theo §8; không ngầm cấp assessment.run. |
| Gap/task | `treatment.update` | OR update/approve/report; patch chỉ tiến độ được phép, không đóng. |
| Treatment approval/closure | `treatment.approve` | Closure kiểm riêng từng tiêu chí và target; không suy từ risk.accept. |
| Risk acceptance | `risk.accept` | Scope/reason/thời hạn rõ; giữ nguyên raw risk, control failure và gap. |
| Priority | Proposal: `risk.propose` OR `assessment.review`; approval: `risk.priority_approve` | Quyết định review và phê duyệt ưu tiên SME là hai record riêng. |
| Report/export | `report.read` | Bytes evidence cần thêm evidence.read_assigned trên từng revision; kiểm lại khi chạy/công bố/tải. |
| Audit | `organization.manage` | Chỉ metadata audit trong organization, không chứa credential hoặc bytes evidence. |

Seed hiện hành hợp nhất fixture baseline và FLOW overlay có provenance. Bước 05 bổ sung tường minh `report.read` cho VDT_SECURITY để tự đánh giá nội bộ vẫn có báo cáo, và `assessment.adjudicate` cho VDT_RISK_OWNER để phân xử có trách nhiệm. Closure dùng `treatment.approve`; quyền này không được suy từ giảm R, VERIFIED hoặc acceptance. Admin không có toàn quyền nghiệp vụ. Reviewer U004 chỉ theo assessment được giao và trước expiry; U002 có evidence.read_assigned/evidence.verify cho self-assessment, U003 có risk.priority_approve. Các assignment seed là dữ liệu thiết kế, chưa provision tài khoản hoặc phê duyệt ưu tiên thật.

## 4. Response, lỗi vận chuyển và lỗi nghiệp vụ

GET trả 200; create snapshot/decision/revision trả 201 cùng Location sau commit; PATCH trả tài nguyên mới với strong ETag; logout trả 204. Export trả 202 cùng Location theo dõi job. Response có X-Request-ID và no-store theo OpenAPI; download attachment dùng private, no-store và nosniff. List trả `items`, `next_cursor`; không dùng tổng số ngoài scope. ETag của mutable aggregate là version dạng `"7"`; snapshot bất biến có content hash khi được trả ETag.

Lỗi dùng `application/problem+json`, schema `Problem`: type, title, status, code, request_id; detail và issues là dữ liệu đã lọc nhạy cảm. Mã HTTP không thay thế machine code. Không trả stack trace, storage path, credential hoặc nội dung object ngoài scope.

| HTTP | Ý nghĩa và cách xử lý |
| --- | --- |
| 400 / 415 / 422 | JSON/header không parse được; media type không hỗ trợ; hoặc sai cấu trúc/kiểu/enum/trường bắt buộc. Sửa request, dùng key mới nếu payload thay đổi. |
| 401 / 403 / 404 | Phiên không hợp lệ; thiếu quyền/CSRF/đã hết hạn; hoặc object không tồn tại/không được tiết lộ. Không tạo domain result. |
| 409 | Xung đột trạng thái/quan hệ; `DEPENDENCY_CHANGED`; cùng key khác hash; hoặc `OPERATION_IN_PROGRESS`. Đọc lại dependency; riêng operation đang chạy dùng Retry-After và cùng key/payload. |
| 412 / 428 | If-Match sai version / thiếu điều kiện version hoặc dependency bắt buộc. Không ghi đè mất thay đổi. |
| 413 / 429 | Vượt kích thước / hạn mức hoặc số thao tác đồng thời. Không có revision sẵn sàng. |
| 503 / 500 | Scanner/DB/phụ thuộc tạm không sẵn sàng / lỗi nội bộ. Rollback mutation chưa commit; retry lỗi tạm bằng cùng key/payload. |

**Lỗi miền RM-01 được lưu khác lỗi vận chuyển:** request đúng cấu trúc và được phép nhưng E/F/G/impact ngoài 1–5, số phân số, cận đảo/mâu thuẫn hoặc thiếu context thiết yếu tạo 201 với RiskEvaluation bất biến: `status=NEEDS_REVIEW`, `score_determined=false`, mọi computed numeric/range/level null, `validation_issues` chỉ vị trí lỗi; giữ nguyên `inputs`. Không clamp, ép kiểu, gán LOW hoặc trả 422 để làm mất lịch sử nghiệp vụ này. Chuỗi `"6"` thay vì JSON number, malformed UUID hoặc trường lạ vẫn là lỗi vận chuyển 422, không tạo snapshot. UNKNOWN có context hợp lệ là nhánh tính cận hợp lệ của RM-01.

## 5. Idempotency, OCC và transaction

Domain mutation dùng `Idempotency-Key` UUID theo operation trong OpenAPI; auth là các command phiên riêng. Key duy nhất theo `(organization, principal, method, canonical_path, key)`. Hash request gồm payload chuẩn hóa, expected version và bytes digest thực của file; boundary multipart không thuộc hash. Cùng key/cùng hash sau thành công trả cùng resource/status sau kiểm lại quyền hiện hành, không tạo quyết định/revision thứ hai. Cùng key khác hash trả 409; operation đang chạy trả 409 OPERATION_IN_PROGRESS/Retry-After. Không tin digest do client khai để replay multipart chưa kiểm chứng bytes.

Replay thành công không yêu cầu aggregate còn version cũ, vì mutation đã commit; vẫn phải kiểm hash và quyền hiện tại. Request mới dùng key mới phải kiểm current version. Giữ key/hash/result suốt vòng đời hồ sơ v0.1; thay retention sau này phải giữ tombstone đủ ngăn tạo lại thao tác. Không cache bytes hoặc response nhạy cảm để trả vượt quyền đã bị thu hồi.

Mutable resource và command trên parent dùng strong `If-Match` tại các operation khai báo; thiếu trả 428, sai trả 412. PATCH chỉ thay trường gửi lên; nested object/array thay toàn bộ, trường bỏ qua giữ nguyên, empty patch hoặc chỉ write_context bị từ chối. Snapshot/decision append-only không có PATCH để sửa lịch sử.

`write_context.dependencies` khai ID/version chính xác đã đọc. Server tự tìm đầy đủ phụ thuộc từ graph; thiếu mutable head bắt buộc trả 428, dependency đã đổi trả 409 DEPENDENCY_CHANGED. Mảng rỗng chỉ hợp lệ khi tạo root không có mutable dependency; không dùng để bỏ gate. Criteria/context/revision cố định vẫn cần kiểm usability và expiry trước commit. Closure còn kiểm `expected_version` của target; retest completion kiểm If-Match của retest.

Assessment + children/input/decision + audit + idempotency success commit nguyên khối. Gap/task chỉ tạo bằng thao tác tường minh hoặc command có danh sách yêu cầu rõ. Audit nghiệp vụ lỗi thì rollback; audit denial ghi tối thiểu sau rollback. Khóa theo auth guard → aggregate theo ID ổn định → dependency → audit/idempotency. Không giữ transaction/row lock trong upload, scan hoặc download dài.

Gate cuối dùng guard quyền dùng chung với grant/revoke/disable/session revoke và giờ DB hiện hành sát commit. Thu hồi hoàn tất trước gate cuối phải được nhìn thấy; cache quyền cũ không đủ. Deadlock/serialization failure rollback và retry có giới hạn. [Storage §5](storage-transactions-v0.1.md#5-transaction-khóa-và-idempotency) quy định crash windows, thứ tự lock và kiểm expiry trong transaction.

## 6. Upload, revision và xác minh

`POST /evidence-items/{id}/evidence-revisions` nhận đúng một file + một phần metadata JSON qua multipart, hoặc `EvidenceReferenceInput` qua JSON. Giới hạn: file 20 MiB, metadata 64 KiB, toàn multipart 21 MiB; một upload đang xử lý/principal, hai/host, scanner tuần tự. Kiểm byte khi stream độc lập Content-Length. Allowlist TXT/LOG UTF-8, JSON, CSV, PDF, PNG, JPEG kiểm extension cùng signature/MIME; không nhận archive, executable, HTML/SVG hoặc macro.

Upload đi đủ proxy/gate, stream quarantine → kiểm hash/metadata/type/scan → ghi STAGED → fsync/rename nguyên tử → transaction cuối kiểm quyền/version/expiry → COMMITTED + audit/idempotency → 201. Scanner thiếu/lỗi/chữ ký cũ/timeout trả 503; nội dung không an toàn 422, media sai 415, oversize 413. Không trả thành công cho STAGED; scanner không tạo VerificationDecision hoặc kết luận control. Tệp đã vào final path trước DB commit vẫn chưa dùng được.

| Trạng thái/khía cạnh | Ý nghĩa hợp đồng |
| --- | --- |
| `storage_state` | STAGED→COMMITTED hoặc ORPHANED; COMMITTED→INTEGRITY_FAILED nếu bytes mất/hỏng. Restore đúng digest/kích thước có audit mới trở lại COMMITTED. ORPHANED không tự commit. |
| `verification_status` | UNVERIFIED, VERIFIED, REJECTED hoặc EXPIRED là projection theo đúng revision/assessment/scope/thời điểm; không lấy latest decision toàn cục. |
| `verification_mode` | SELF_ASSESSED hoặc INDEPENDENT_REVIEWED trên quyết định; null khi chưa có quyết định hiệu lực. |
| `availability` | AVAILABLE/UNAVAILABLE/INTEGRITY_FAILED nói về khả năng truy cập payload; không thay kết luận nội dung. |

FILE lưu bytes/hash server tính/kích thước/type cùng source, owner, collected_at, valid_until, scope, environment, config version và redaction bất biến. `client_sha256` chỉ là giá trị kỳ vọng. REFERENCE lưu URI/mô tả và hash manifest metadata chuẩn hóa; không phải hash nội dung từ xa. Server không fetch URL, DNS, redirect hoặc preview. Verifier ghi observation và observed_content_sha256 khi có; cần tái lập bytes thì nộp FILE revision.

VerificationDecision append-only, chỉ VERIFIED/REJECTED, có actor/time/scope/reason/observation/mode và supersedes khi cần. Các checkbox client là khai báo cần đối chiếu, không tự chứng minh provenance. `evidence.verify` cần cả quyền đọc; independent mode phải có actor khác người nộp evidence và người thực hiện công việc được đánh giá, cùng reviewer assignment còn hiệu lực. Revision mới không thừa kế kết luận revision cũ. Quyết định hết hạn, sai scope, storage lỗi hoặc môi trường thay đổi làm evidence không dùng được cho đánh giá mới.

Download chỉ FILE COMMITTED và integrity hợp lệ; mở và phát cùng file handle an toàn. REFERENCE trả 409 REFERENCE_HAS_NO_BYTES ở endpoint content. Gate chạy trước phát bytes và theo dõi expiry/revocation trong stream; dừng khi quyền mất, bytes đã phát không thu hồi được. Trả attachment, không render inline, không public/signed URL bỏ gate. Retry sau crash không tự dùng quyền cũ; reconciler dọn orphan theo lease/grace, không tự công bố revision.

## 7. Snapshot đánh giá và tên trường

Context có thể tạo từ inventory và scope trước khi có scenario/assessment; các liên kết assessment/scenario tùy chọn trong SQL không buộc client dựng một vòng tham chiếu giả. Scenario sau đó trỏ context, ScenarioSnapshot chụp đầy đủ nội dung và target của đúng source version. Một assessment chứa nhiều scenario qua `assessment_scenario`; `scenario_ids` của API phải được lưu đủ tập, và mỗi RiskEvaluation phải thuộc membership này.

ControlAssessment đóng băng implementation/context, criterion version, execution status PASS/FAIL/INCONCLUSIVE/NOT_READY, observation, evidence revision và VerificationDecision ID cụ thể cho từng tiêu chí. Server kiểm lại evidence ở commit và suy aggregate result. INCONCLUSIVE/NOT_READY/thiếu telemetry không chứng minh failure; failure đã xác minh ở tiêu chí khác vẫn giữ, nên CONTROL_GAP và EVIDENCE_GAP có thể cùng tồn tại. `score_determined=false`, `score_applicability=NOT_APPLICABLE` nói rõ control không có điểm risk.

RiskEvaluation giữ `inputs` gốc, `effective_inputs` sau xác thực căn cứ, context/scenario snapshot, assessment type/precondition/horizon, E/F và excluded controls, vector C/I_integrity/A/B, từng đường G, confirmation IDs, method/profile/rubric và `computed`. CURRENT cần ControlAssessment trước để xác nhận coverage/strength; `SYNTHETIC_DESIGN` không tạo kết quả môi trường thật. Không ánh xạ máy móc control_result sang G. E/F có căn cứ phù hợp có thể được tác giả có assessment.run xác nhận trong self-assessment; impact cần risk.impact_review.

Thiếu căn cứ thì UNKNOWN với miền đầy đủ theo RM-01; cận hẹp hoặc loại đường N/A cần input-confirmation được reviewer đủ quyền xác nhận. Template/AI/assumption có nguồn không tự thành evidence. Hai cận R25 bằng nhau có thể xác định điểm dù còn UNKNOWN; status vẫn NEEDS_REVIEW nếu thiếu điều kiện RM-01 §6.4. Hai cận khác nhau trả range, không tự xếp ưu tiên. Confidence không nhân điểm; ILLUSTRATIVE không vào risk register vận hành; không cộng risk của các scenario.

| API v0.1 | Ánh xạ/ý nghĩa trong lưu trữ và use case |
| --- | --- |
| `created_at`, `created_by` | Thời điểm server ghi nhận và actor; `effective_at`/`collected_at` là thời điểm sự việc được khai báo. Tên SQL và bảng nguồn xem data-model. |
| `EvidenceRevision.storage_state`, `version` | Projection của storage lifecycle có guard; payload/provenance revision bất biến. |
| `verification_status`, `effective_verification_decision_id` | Projection theo scope/assessment/time; quyết định append-only lưu riêng. |
| `assessment_mode` | SELF_ASSESSED hoặc INDEPENDENT_REVIEWED; thay tên mô tả REVIEWER_ASSISTED ở use case r1 chỉ khi độc lập thực sự được kiểm tra. |
| `review_outcome` | NONE/CONFIRMED/DISPUTED/ADJUSTED_NEW_SNAPSHOT; NONE tương ứng chưa có quyết định, không đồng nghĩa đang có request pending. |
| `ReviewRequest.lifecycle` | PENDING/COMPLETED/CANCELLED/EXPIRED; giữ vòng đời request riêng khỏi outcome snapshot. |
| `status`, `score_determined`, `control_result` | Ba chiều riêng: độ đầy đủ đánh giá, có điểm risk xác định, kết quả control. Không dùng REVIEWED thay EVALUATED. |
| `E`, `F`, `G`, `P`, `L`, `I_total`, `R25`, `R_progress` | Tên wire giữ ký hiệu RM-01; SQL chuẩn hóa tên cột và child records theo bảng mapping trong data-model, không đổi công thức. |
| `precondition_plausibility` | `risk_evaluation.plausibility`: LOW/MEDIUM/HIGH/UNKNOWN; MEDIUM ở trục này khác MODERATE của risk level. |
| `InputConfirmation`, `ImpactConfirmation` | Các bảng `input_confirmation`, `impact_confirmation` và bảng con lưu đúng snapshot, field/dimension và evidence basis; evaluation mới liên kết các decision đã dùng. |
| `EvidenceRequest`, `TreatmentApproval` | `evidence_request` + criterion children; `treatment_approval` ghi đúng task/version. Đây là dữ liệu nghiệp vụ được lưu riêng, không chỉ audit. |
| `AdjudicationInput.review_decision_ids`, `resolved_fields` | Tập quyết định ở `adjudication_review`; các trường đã phân xử ở `adjudication_decision.resolved_fields`. Không lấy riêng phần tử đầu rồi bỏ phần còn lại. |
| `ClosureInput.criteria`, `expected_version` | `closure_criterion` + `closure_criterion_evidence` giữ từng criterion/assessment/revision/verification; decision giữ target_version_before/after. |
| `Retest.state` | API REQUESTED/ASSESSMENTS_RECORDED; ASSESSMENTS_RECORDED ánh xạ SQL `retest_request.state=COMPLETED`. Các trạng thái nội bộ khác không tự trở thành enum wire mới. |

Mỗi canonical snapshot có schema version và SHA-256; chuỗi decimal/UTC/sort key phải ổn định. Hash kiểm tra thay đổi dữ liệu, không là chữ ký chống quản trị viên DB. Serializer phải dựng đúng graph và trường tổng hợp; một response object không ngụ ý một bảng SQL duy nhất.

## 8. Review, tranh chấp và phân xử

Initial assessment/comparison chỉ SELF_ASSESSED, outcome NONE. ReviewRequest trỏ đúng snapshot và reviewer được giao; tạo/cancel request không thay mode/outcome bản gốc. Cancel chỉ PENDING; due_at hoặc assignment expiry chặn nộp quyết định, request hết due_at ghi EXPIRED. `due_at` là hạn yêu cầu tùy chọn; SQL `expires_at` là hạn server bắt buộc, bị giới hạn bởi assignment và policy review lifetime. Reviewer có assessment.review vẫn cần evidence.read_assigned để đọc nguồn và evidence.verify nếu muốn xác minh.

`POST /review-decisions` khóa request PENDING, kiểm actor khác tác giả và assignment còn hiệu lực, rồi commit decision + request COMPLETED + snapshot mới nguyên khối. CONFIRMED không xóa UNKNOWN, gap hoặc tự chuyển EVALUATED. DISPUTED giữ cả giá trị/nhận định và nguồn; tranh chấp factor dùng UNKNOWN/cận hợp lệ, tranh chấp context thiết yếu để null toàn bộ score/range. Không lấy trung bình ý kiến hoặc ghi đè snapshot gốc.

`POST /adjudications` dùng assessment.adjudicate của Risk Owner, scope/ownership/delegation đúng; actor phải khác original assessor và disputed reviewer. Một assessment.run actor khác adjudicator và reviewer tạo candidate replacement hợp lệ, trỏ superseded disputed snapshot. Command phân xử nhận IDs của original/disputed/candidate, decisions, resolved_fields và reason; server kiểm type, ancestry, scope, input và dependency, tạo final snapshot copy + decision nguyên khối với ADJUSTED_NEW_SNAPSHOT. Candidate và hai nhận định trước giữ nguyên. Thiếu actor độc lập có quyền thì giữ NEEDS_REVIEW; gán thêm role cho cùng người không đáp ứng độc lập.

## 9. Retest, so sánh, ưu tiên và đóng

Task v0.1 có thể độc lập, không bắt buộc client tạo treatment plan; SQL `treatment_task.plan_id` nullable. Task vẫn cần scenario/scope/owner/action và ít nhất một expected_retest_evidence. TreatmentApproval ghi đúng task version đã được duyệt; sửa task đòi kiểm lại giá trị approval tương ứng.

Retest tạo record gắn assessment, tập before control snapshots, before risk tùy chọn, context snapshot, task_ids và new_evidence_revision_ids. Các tập lưu đủ qua `retest_baseline_control`, `retest_task`, `retest_evidence`; output control lưu qua `retest_result_control`. Completion kiểm baseline/output đúng scope, ít nhất một output có ý nghĩa, rồi chuyển API state sang ASSESSMENTS_RECORDED; không sửa kết quả trước hoặc đóng task. Context/criteria/profile/rubric và revision dùng trong retest được chụp. INCONCLUSIVE giữ phần gap chưa giải quyết; giảm risk không chứng minh treatment là nguyên nhân.

Comparison kiểm cùng scenario/event, scope/context/preconditions, method/profile/rubric và cùng CURRENT hoặc cùng INHERENT. ID context khác chỉ được coi tương đương khi nội dung đã được kiểm; không so dựa vào ID hoặc timestamp đơn thuần. Không tương đương thì lưu NOT_COMPARABLE kèm lý do. Trình bày riêng R_progress, impact_progress, gap_progress; từng chiều C/I_integrity/A/B có before/after/progress, verified_worsening và summaries. INCOMPLETE không che chiều đã xác minh xấu đi; max/R không đổi vẫn có thể đổi từng chiều.

Comparison đầu có treatment_attribution=REVIEW_REQUIRED. Chỉ review độc lập CONFIRMED với liên hệ implementation/retest/evidence cho từng chiều mới tạo snapshot mới có SUPPORTED; không tự suy từ giảm R. PriorityProposal và PriorityDecision riêng, phê duyệt cần risk.priority_approve. MF-03/MF-04 vẫn NOT_RANKED theo nhận định review hiện hành, chưa có phê duyệt SME.

ClosureDecision cần treatment.approve, target GAP/TASK, expected_version, từng criterion và evidence/retest còn dùng được. Transaction khóa target rồi ghi decision + CLOSED + audit; closure thành công tăng target version đúng một. Từng criterion giữ exact revision/verification decision, không chỉ một cờ verified tổng. Approval hành động xử lý, risk acceptance, evidence VERIFIED, control SATISFIED hoặc điểm giảm không tự đóng; đóng gap cũng không tự đóng task khác. PATCH gap/task không nhận CLOSED; lịch sử quyết định không bị thay bằng trạng thái hiện hành.

## 10. Report, as_of và export

ReportSnapshot đóng băng IDs và graph metadata inventory/context/scenario/control/risk/comparison/gap/task/decision tại `as_of`. Chỉ dữ liệu đã được server recorded trước hoặc bằng as_of được chọn; evidence nộp muộn với collected_at cũ không xuất hiện ngược thời gian. Mở report cũ dùng giá trị đã chụp, không truy latest để thay. Scope hiện hành vẫn kiểm cho từng phần; trường nguồn nhạy cảm được lọc/ẩn theo policy và biểu thị hạn chế, không thay giá trị snapshot gốc.

Export JSON/PDF là job durable có PENDING/READY/FAILED/EXPIRED; 202 không có nghĩa đã tạo xong tệp. Worker kiểm quyền người yêu cầu khi chạy, trước công bố và mỗi download; include_evidence_bytes cần quyền evidence trên từng revision. Artifact có expiry, hash và kích thước; quá hạn không phát bytes. Không dùng service account để nâng quyền request. Report ghi rõ self-assessment, disagreement, UNKNOWN/INCONCLUSIVE và phần chưa kiểm chứng; không là chứng nhận pháp lý.


Scope có `scenario_ids` cùng các chiều organization/branch/system/asset/data_asset/assessment; các chiều có giá trị giao nhau và không tự tạo quyền. SQL `scope_object.scenario_id` giữ hạn chế này khi create/read.

EvidenceLink lưu tập `criterion_version_ids` ở `evidence_link_criterion`. RiskControlLink dùng `scenario_control` với scope, actor/time và guard bất biến; ControlImplementation giữ exact `authentication_profile_version_id`. Comparison lưu task/version ở `comparison_treatment` và căn cứ ở `comparison_attribution_evidence`. `SUPPORTED` cần review độc lập CONFIRMED cùng task/evidence; không bắt buộc treatment plan. Canonical DTO ở `snapshot_registry.api_payload` phải khớp typed fields/children trước tính hash, không dùng JSON để bỏ qua FK hoặc kiểm scope.

## 11. Profile CRM, ví dụ và gate chuyển tiếp

AuthenticationProfile là version bất biến của AUTH-CRM-01 với challenge_ttl_seconds, max_attempt_limit, session_idle_timeout_seconds, rp_id, allowed_origins cùng environment/bootstrap/recovery policy. TO_SET_BEFORE_LAB cho phép trường chưa chốt null; PROPOSED cần năm giá trị và bối cảnh/policy đầy đủ; APPROVED thêm config owner hiện hành đúng system scope, approval_reason và actor/time server ghi. control.manage đơn lẻ không đủ phê duyệt. C01 scope approval là nguồn quyết định riêng tại control_scope_approval_reference, không tự suy từ profile approval.

120/5/900 chỉ là ví dụ chưa phê duyệt. Origin phải HTTPS và phù hợp RP ID; thiếu cấu hình, môi trường, policy hoặc phê duyệt cần thiết tiếp tục chặn lab. APPROVED không nghĩa lab PASS, không đổi cấu hình xác thực VDT và không tự khởi chạy kiểm thử.

Ví dụ đầy đủ nằm trong `components.schemas.*.examples` của OpenAPI: `AuthenticationProfileInput` cho TO_SET_BEFORE_LAB; `EvidenceReferenceInput` cho manifest reference; `RiskEvaluationInput` cho ILLUSTRATIVE E=6; `RiskComputed` cho kết quả RM_DOMAIN_INVALID; `Problem` cho DEPENDENCY_CHANGED. UUID, nguồn và timestamp trong ví dụ là dữ liệu tổng hợp, không CRM evidence. Khi triển khai phải thay bằng ID hợp lệ và đủ dependency; không dùng ví dụ mảng rỗng để bỏ kiểm version.

Ví dụ header cho một mutation mới: `Idempotency-Key: 00000000-0000-4000-8000-000000000090`, `If-Match: "7"` nếu operation yêu cầu, và CSRF token của phiên. Mất response sau commit thì gửi lại đúng key/payload để nhận resource cũ; sửa payload hoặc đọc lại sau conflict để thực hiện ý định mới thì dùng key mới. Ví dụ nghiệp vụ E=6 trả snapshot NEEDS_REVIEW; thay E bằng chuỗi `"6"` trả 422 không tạo snapshot.

Gate thiết kế cần parse OpenAPI/schema, đối chiếu endpoint↔permission↔DDL và NOTE-01…10; kết quả kiểm tra được ghi trong hồ sơ validation bước 05. Gate triển khai bước 06 cần kiểm RBAC/scope/expiry tại đầu và sát commit, cùng-key race, OCC/dependency conflict, scanner/crash windows, snapshot as_of, review independence, closure và export expiry/restore. FLOW-01…10, T01–T24, VALID-G-01 vẫn NOT_RUN; chưa có CRM evidence, hiệu chuẩn SME hoặc lab. Tài liệu này không chuyển bước 06 sang trạng thái bắt đầu.

