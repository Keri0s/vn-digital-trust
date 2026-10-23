# VN Digital Trust — Kiến trúc kỹ thuật v0.1 (bước 04)

**Ngày:** 2026-10-18. **Trạng thái:** thiết kế kiến trúc; chưa triển khai hay kiểm thử lab. Đầu vào hiện hành: [use case v0.2-r1](use-cases-technical-v0.2.md), [RM-01 v0.4-r3](risk-method-v0.4.md), [CE-01](control-evidence-v0.1.md), [requirements](requirements-technical-v0.1.md), [scope/fixture](lab-scope-and-fixtures-v0.1.md). Sơ đồ nguồn và bản render: [container](../So-do-PNG/container-v0.1.png), [deployment](../So-do-PNG/deployment-v0.1.png), [luồng evidence/decision](../So-do-PNG/evidence-decision-flow-v0.1.png).

## 1. Quyết định ranh giới

Một deployment chứa đúng một SME với hai chi nhánh. Ứng dụng VN Digital Trust (VDT) là hệ thống ghi nhận và đánh giá; CRM cùng lớp danh tính CRM thực thi các control được đánh giá. Tài khoản, phiên và RBAC của VDT độc lập với CRM; VPN chỉ là tiền điều kiện mạng trong SC-01. Lab, Atomic Red Team, Caldera và nơi nhận thử SC-02 ở ngoài ranh giới sản phẩm, không có đường tự động ghi kết luận vào risk register. V0.1 nhận tệp hoặc tham chiếu do người dùng có quyền nộp, với provenance và xác minh thủ công. Dữ liệu demo là giả lập/được kiểm soát.

Ranh giới logic trong một ứng dụng: giao diện, cổng xác thực/phân quyền, dịch vụ nghiệp vụ và kho lưu. Không yêu cầu microservice. Tách module để giữ trách nhiệm và kiểm soát quyền; lựa chọn framework, DB, API và cấu trúc bảng thuộc bước 05.

## 2. Thành phần và trách nhiệm

| Thành phần logic | Trách nhiệm, đầu vào và đầu ra | Truy vết |
| --- | --- | --- |
| Giao diện người dùng và report viewer | Nhập context/scenario, hiển thị UNKNOWN, provenance, trạng thái độc lập, lịch sử và giới hạn; yêu cầu đọc evidence riêng khi mở; không tự tính/chốt quyết định | TUC-01–08; TNFR-USA-001, TNFR-EXP-001 |
| Auth/session và policy gate | Xác thực user VDT; kiểm tra user active, permission, object scope, assessment assignment và thời hạn ở mọi read/write/export, ngay lúc thực hiện; từ chối có audit; không tin quyền do UI gửi | TUC-01, 04–08; TFR-AUTH-001–004, TNFR-SEC-001, TNFR-PRV-001; FLOW-01–04 |
| Inventory/context & scenario | Một organization; quản lý system/asset/DataAsset/vendor, owner, chi nhánh, data flow, tiền điều kiện, nguồn và UNKNOWN; version context; chỉ kích hoạt scenario khi đủ căn cứ | TUC-02/03; TFR-INV-001–005, TFR-CTX-001–004, TFR-RISK-001/002; FLOW-07/10 |
| Control catalog/implementation | Giữ criteria version và scope, link scenario–control–implementation, kể cả chưa triển khai/N/A có lý do; không coi catalog là evidence | TUC-05; TFR-CTL-001–005; CE-01 |
| Evidence intake & protected store | Nhận tệp hoặc reference, quét/giới hạn định dạng và kích thước theo chính sách bước 05, gắn nguồn/owner/time/scope/hash, tạo revision bất biến; nội dung evidence lưu kín, không phục vụ qua static URL; xử lý lỗi upload bằng trạng thái chưa sẵn sàng | TUC-05/08; TFR-EVD-001–004/007, TNFR-PRV-001; FLOW-05 |
| Evidence verification | Người có `evidence.verify` và quyền đọc đúng scope kiểm tra nguồn, nội dung, hiệu lực, test execution/telemetry rồi thêm verification decision (actor/time/reason); không sửa bytes/revision; tự xác minh ghi SELF_ASSESSED, không giả độc lập | TUC-05/06; TFR-EVD-002/005/006; FLOW-01–03/05/06 |
| Control assessment | Đọc criteria snapshot và evidence revision/verification còn hợp lệ đúng scope; ghi kết quả/observation/test status theo từng tiêu chí; giữ failure đã xác minh cùng phần chưa biết; output snapshot bất biến | TUC-06; TFR-EVD-003–006; FLOW-05/06/08 |
| Risk evaluation engine | Kiểm tra context/miền; với CURRENT yêu cầu ControlAssessment trước xác nhận coverage/strength từng đường G; tính chính xác theo profile RM-01 từ snapshot, giữ UNKNOWN, score_determined và status độc lập | TUC-04; TFR-RISK-003–006, TNFR-TRC-001, TNFR-REP-001; FLOW-07/10 |
| Review & decision | Nhận xét/đính chính có lý do tạo decision revision; reviewer độc lập khác actor đánh giá và chỉ trong assignment còn hạn; giữ assessment_mode và review_outcome; Risk Owner chốt ưu tiên bằng `risk.priority_approve`; acceptance riêng | TUC-04/06/07; TFR-RISK-008, TFR-TRT-002/004; FLOW-02–04 |
| Gap, treatment & retest | Tạo/giữ EVIDENCE_GAP và CONTROL_GAP đồng thời khi cần; quản task, acceptance và closure có điều kiện/quyền/audit; retest tạo revision/snapshot mới, so tương đương trước khi báo R/impact/gap progress | TUC-07; TFR-TRT-001–006; FLOW-05/06/08/09 |
| Snapshot/report & audit | Báo cáo `as_of` trỏ tới snapshot/version cố định; metadata truy vết được nhưng nội dung evidence luôn kiểm quyền lại; audit append-only cho quyền, đọc nhạy cảm, kiểm chứng, assessment, decision, closure, export và lỗi bị từ chối | TUC-08; TFR-RPT-001–003, TFR-AUD-001/002; FLOW-03/08/09 |

## 3. Luồng dữ liệu và ranh giới tin cậy

1. User → VDT qua kết nối bảo vệ. UI chỉ gửi intent và dữ liệu; server lấy identity/session của VDT và kiểm quyền trên từng đối tượng. Branch là thuộc tính scope, không là tenant khác. Assignment reviewer gắn assessment cụ thể và expiry; role chung không mở mọi evidence.
2. CRM/identity CRM/lab → người thu thập → evidence intake. File/reference và log là dữ liệu **không tin cậy**. Ghi provenance, môi trường, đường/tiêu chí, thời điểm, redaction và hash. Reference bên ngoài không được server tự truy xuất tùy ý; cách cho phép nguồn/đích và xử lý malware thuộc bước 05. Không nhập secret, assertion đầy đủ hay dữ liệu khách hàng thật.
3. Intake → kho metadata và kho nội dung evidence. Metadata dùng để lọc/truy vết; bytes chỉ qua handler đã kiểm quyền/scope/expiry tại thời điểm tải xuống. Link một revision với nhiều control giữ scope/criteria của từng link. File mất/hỏng/hash khác thì báo unavailable/integrity issue, không lặng lẽ dùng lại VERIFIED.
4. Verification → ControlAssessment → risk CURRENT. Verification chỉ cho biết revision được kiểm tra trong scope/time; khi hết hạn/sai scope hoặc môi trường thay đổi, assessment mới không tái sử dụng như evidence còn dùng được. Control result không ánh xạ cố định sang G: actor xác nhận coverage và strength từng đường, kèm rationale/source. Từ G và impact, engine tính theo profile bất biến; template/AI chỉ gợi ý.
5. Assessment/decision → gap/treatment/retest → report. Mỗi bước trỏ ID và version đầu vào. Report cũ giữ view của thời điểm đã chọn; nếu quyền đọc nội dung evidence đã mất, chỉ metadata được phép hiển thị. Export phải kiểm quyền với toàn bộ scope tại lúc tạo; artifact xuất chứa dữ liệu nhạy cảm nên có quản lý truy cập/hạn dùng theo quyết định bước 05.

Sơ đồ [container](../So-do-PNG/container-v0.1.png) biểu diễn các ranh giới trên; [luồng quyết định](../So-do-PNG/evidence-decision-flow-v0.1.png) biểu diễn trình tự xác minh, assessment, review và retest.

## 4. Quyền, revision và giao dịch

**Policy gate:** Với mỗi read/write, lấy principal VDT đang active, quyền hiện hành, object scope và assignment/expiry hiện hành; đánh giá trong server trước đọc nội dung hoặc commit. Với giao dịch dài (upload, export, xác minh), kiểm lại ngay trước commit/phát nội dung. Hết hạn tại đúng mốc expiry là từ chối. Cache quyền nếu có phải bị vô hiệu khi thu hồi và không được vượt expiry. Từ chối trả kết quả tối thiểu, không rò tồn tại/nội dung đối tượng ngoài scope; audit actor/action/target/time/reason an toàn. U002/VDT_SECURITY có `evidence.read_assigned` và `evidence.verify` trong phạm vi vận hành; U004/VDT_REVIEWER chỉ assessment/evidence được giao và trước hạn. `assessment.review` không ngầm cấp `evidence.verify`; `evidence.verify` không cấp CRM access hay quyền phê duyệt ưu tiên. Self-assessment hoạt động khi không có consultant; independent review yêu cầu actor khác người thực hiện.

**Append-only domain history:** EvidenceItem là danh tính logic, EvidenceRevision là bytes/reference + nguồn/hash/scope/validity bất biến. VerificationDecision trỏ đúng revision và lưu người/giờ/lý do/kết luận; quyết định mới không sửa quyết định cũ. ControlAssessment chụp criteria version, implementation scope, revision IDs, verification decisions, observation và test execution status. RiskEvaluation chụp scenario/context/tiền điều kiện, assessment type, method/profile/rubric, per-path G coverage/strength, impact vector/range, raw calculation/R25, status, score_determined, missing/review reasons. Review, priority approval, risk acceptance, gap closure và report là bản ghi quyết định/snapshot riêng, trỏ các bản đã dùng. `assessment_mode` và `review_outcome` tách khỏi status. Audit ghi thay đổi và truy cập nhạy cảm nhưng không thay thế domain snapshot.

**Lỗi và lặp:** Validation sai context/miền trả NEEDS_REVIEW, score/range/level null và issues; upload chưa hoàn tất không tạo evidence dùng được; test timeout/thiếu telemetry là INCONCLUSIVE; tính toán lỗi không commit nửa snapshot. Dùng khóa thao tác/idempotency token ở biên ghi để retry không nhân đôi revision/task/decision; cùng token nhưng payload khác bị từ chối. Mỗi update dựa trên revision/version đã đọc; nếu người khác thay quyền, context, criteria, evidence hoặc task trước commit, từ chối conflict và yêu cầu đọc lại. Một transaction gắn snapshot, link và audit/decision liên quan; nếu lưu file ngoài transaction metadata, dùng trạng thái staged → committed và dọn orphan an toàn. Event/background work nếu có phải tái kiểm quyền và version tại lúc phát hành kết quả; không dùng quyền của lúc enqueue.

**Không tự đóng:** VERIFIED không làm SATISFIED; SATISFIED mới không tự đóng gap/task; điểm R giảm hay risk acceptance không xóa failure. Closure cần đối chiếu tiêu chí, evidence/test mới phù hợp, người có quyền xác nhận, actor/time/reason và quyết định riêng. Bất đồng review giữ cả nhận định, NEEDS_REVIEW khi liên quan; phân xử tạo revision mới. Không đổi quá khứ để “sửa” kết quả.

## 5. Retest và so sánh

Retest lấy EvidenceRevision và ControlAssessment mới, rồi RiskEvaluation mới nếu có căn cứ; mọi snapshot trước vẫn mở được. Comparison chỉ được diễn giải khi cùng scenario/sự kiện, context/phạm vi/tiền điều kiện, profile/rubric và cùng loại CURRENT hoặc INHERENT. Khác bất kỳ điều kiện trọng yếu → NOT_COMPARABLE với lý do; không quy chênh lệch cho treatment. Ba kết quả riêng: R_progress, impact_progress với từng chiều C/I_integrity/A/B và `verified_worsening=true|false|null`, gap_progress. Lưu `impact_summary_before/after` gồm I_total/range và số chiều đạt max/range; `treatment_attribution` độc lập. Range không dùng tự xếp hạng. Priority cross-scenario do Risk Owner có quyền chốt với reason, không sinh từ score/range; reviewer chỉ đề xuất.

## 6. Walkthrough SC và FLOW (thiết kế, chưa chạy)

| Ca | Đường qua kiến trúc và điểm chặn |
| --- | --- |
| SC-01 | Context ghi đã qua VPN, biết mật khẩu nhưng chưa có WebAuthn/phiên; evidence từ CRM về C01–C08 (gồm enrollment/recovery/UV) vào intake, verification, ControlAssessment rồi mới xác nhận G. Fixture NOT_IMPLEMENTED/ENROLLED_SIMULATED không thành evidence. Thiếu evidence → INSUFFICIENT_EVIDENCE/EVIDENCE_GAP; password-only hoặc UV bypass đã xác minh → failure/CONTROL_GAP. |
| SC-02 | Context ghi phiên đọc hợp lệ, ba bản ghi, đường tới receiver lab và policy đích còn TO_SET_BEFORE_LAB. EX-DEMO-01 cần evidence riêng về export/đích; MFA cho đăng nhập mới không hạ G. Nếu thiếu đường/chính sách, giữ UNKNOWN/NEEDS_REVIEW; lab receiver không nằm trong VDT. |
| FLOW-01/02/03 | Policy gate cho U002 tự xác minh trong scope, U004 đúng assessment được giao; kiểm thời hạn ở mỗi read/verify/review, từ chối tại/sau expiry. Review độc lập và verification là hai quyết định khác nhau. |
| FLOW-04 | Review proposal lưu riêng; chỉ Risk Owner có `risk.priority_approve` chốt ưu tiên. MF-03/MF-04 vẫn NOT_RANKED, không suy phê duyệt SME. |
| FLOW-05/06 | Thiếu evidence hoặc T23 lỗi → INCONCLUSIVE/INSUFFICIENT_EVIDENCE và EVIDENCE_GAP; failure xác minh trên tiêu chí khác vẫn giữ CONTROL_GAP đồng thời. |
| FLOW-07 | SC-02 giữ precondition phiên đọc và scope xuất dữ liệu; thiếu evidence đường/đích không tự nhận control có hiệu lực. |
| FLOW-08/09 | Revision/snapshot mới cho retest; fail/INCONCLUSIVE không đóng gap. Closure đòi quyết định. Khác context/profile/rubric/type → NOT_COMPARABLE, giữ hai lịch sử. |
| FLOW-10 | Context thiết yếu/miền sai không có điểm, range hoặc nhãn; validation issues được giữ và hiển thị. |

Các hàng trên là đối chiếu thiết kế với fixture FLOW-03-v0.2-r1, không phải kết quả test chạy. FLOW-01…10 và TC-01 T01–T24 đều NOT_RUN.

## 7. Deployment 16 GB và giới hạn

Phương án triển khai một host local/VM: trình duyệt người dùng → reverse proxy/TLS → một tiến trình ứng dụng (các module trên) → kho metadata giao dịch + vùng lưu evidence riêng với quyền file riêng; backup nhất quán metadata và evidence, kiểm thử restore ở bước 06. CRM/identity CRM, VPN, lab runner và receiver là dịch vụ ngoài VDT, có thể ở host/VM khác hoặc mô phỏng bằng dữ liệu giả lập. Không cài công cụ tấn công vào ứng dụng VDT. Với khoảng 16 GB RAM, một app và kho dữ liệu nhỏ, upload giới hạn, tác vụ nền tuần tự, không bắt buộc broker/search cluster/AI server; kích thước dữ liệu, thông lượng và tài nguyên thực tế cần đo ở bước 06. [Deployment diagram](../So-do-PNG/deployment-v0.1.png) là topology logic, không chốt OS, DB, framework hay port.

Rủi ro còn mở: tham số TTL/session/ngưỡng và môi trường CRM phải đặt trước lab; nguồn reference ngoài có thể mất hoặc biến đổi; hash phát hiện thay đổi nhưng không chứng minh nguồn đúng; clock/expiry cần đồng hồ nhất quán; backup/restore và quyền file cần thử; reviewer nội bộ tự xác minh không tạo độc lập; rubric G chưa kiểm chứng giữa hai người chấm (VALID-G-01 NOT_RUN); chưa có evidence CRM, hiệu chuẩn SME hoặc phê duyệt ưu tiên. Kết quả hiện chỉ là kiến trúc đề xuất, không là chứng nhận tuân thủ.

## 8. Chuyển tiếp bước 05

Thiết kế bước 05 cần chọn stack/DB/storage và API contract để hiện thực transaction, idempotency, optimistic concurrency, object-scope authorization, metadata/bytes isolation, immutable version chain, export access và restore. Phải ánh xạ các snapshot/decision và trạng thái riêng trên vào ERD/API, không thay RM-01/CE-01. Bước 06 kiểm chứng bằng prototype/lab, gồm VALID-G-01, FLOW/TC và tài nguyên thực tế.
