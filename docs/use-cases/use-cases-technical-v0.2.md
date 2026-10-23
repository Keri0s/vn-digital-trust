# VN Digital Trust — Technical Use Cases v0.2 (bước 03)

**Ngày:** 2026-10-13; **revision v0.2-r1:** 2026-10-17. **Trạng thái:** thiết kế luồng; chưa triển khai hoặc kiểm thử CRM. **Nguồn ưu tiên:** [RM-01 v0.4-r3](../planning/risk-method-v0.4.md), [CE-01](../planning/control-evidence-v0.1.md), [TC-01](../planning/control-test-cases-v0.1.md), [phạm vi lab](../planning/lab-scope-and-fixtures-v0.1.md), [requirements](../requirements/requirements-technical-v0.1.md). Bản [v0.1](use-cases-technical-v0.1.md) là baseline trước RM-01 r3; tài liệu này tinh chỉnh luồng, không sửa profile tính.

## 1. Quyền, tiền điều kiện và quy ước chung

Một deployment phục vụ một SME, hai chi nhánh nằm trong cùng organization. Admin quản lý user/role VN Digital Trust; IT/Security nhập dữ liệu kỹ thuật và evidence; Risk Owner xác nhận hậu quả, treatment và risk acceptance khi được cấp quyền; reviewer tùy chọn xem xét/điều chỉnh có lý do. Mọi thao tác đọc evidence, sửa assessment, review, chấp nhận risk và xuất report đều kiểm tra quyền đang hiệu lực tại thời điểm thao tác. Quyền hết hạn/thu hồi giữa phiên làm thao tác bị từ chối và ghi audit, không hoàn tất bằng quyền đã có lúc mở màn hình. Quyền VN Digital Trust không cấp quyền CRM; VPN là tiền điều kiện mạng, không là evidence CRM MFA.

Mỗi lần đánh giá gắn scenario, loại CURRENT/INHERENT/ILLUSTRATIVE, context và tiền điều kiện snapshot, profile/rubric version, actor/time, nguồn/giả định, control criteria version, evidence revision và status đánh giá và thông tin review. CURRENT cần evidence môi trường thật; fixture `NOT_IMPLEMENTED`/`ENROLLED_SIMULATED` chỉ là dữ liệu thiết kế. ILLUSTRATIVE không được đưa vào risk register như kết quả thực. Template/AI có nguồn chỉ gợi ý E/F/G; người có quyền xác nhận từng yếu tố. Không suy G từ ATT&CK, số tactic hoặc việc đăng nhập ứng dụng này.

Các trạng thái độc lập: `score_determined` (điểm tính được hay không), `status` (`NEEDS_REVIEW`/`EVALUATED`, đúng RM-01 §6.4), `control_result`, `gap_status`, `treatment_status`. Điểm xác định có thể vẫn NEEDS_REVIEW. `EVALUATED` chỉ khi đáp ứng RM-01 §6.4; không dùng `REVIEWED` thay trạng thái này. Theo dõi riêng `assessment_mode=SELF_ASSESSED|REVIEWER_ASSISTED` và `review_outcome=NOT_REQUESTED|PENDING|CONFIRMED|DISPUTED`, kèm actor/scope/time; review CONFIRMED không tự đổi status hoặc xóa UNKNOWN/gap. Người kiểm tra chính bài của mình vẫn là SELF_ASSESSED; review độc lập phải có người khác và phạm vi đã thực sự kiểm tra. `R25` nguyên dùng tính/so mức theo RM-01, hiển thị điểm và range theo quy tắc RM-01; confidence không nhân R, range không dùng xếp hạng. Risk acceptance không sửa raw result, evidence, control result hay gap.

## 2. TUC-01 đến TUC-03 — chuẩn bị bối cảnh

| UC | Actor và đầu vào | Đầu ra và nhánh bắt buộc |
| --- | --- | --- |
| TUC-01 — tổ chức/quyền | Admin xác thực; organization duy nhất, user, vai trò, thời hạn quyền | Role assignment/revocation có actor/time và audit. Từ chối tạo organization thứ hai; user thiếu quyền không thể cấp quyền. |
| TUC-02 — inventory/context | IT/Security; system, asset, DataAsset, vendor, owner, nguồn/giả định | Context có version và giá trị UNKNOWN; cập nhật không sửa snapshot cũ. Thiếu owner/quan hệ/scope được đánh dấu để review. |
| TUC-03 — scenario | IT/Security soạn; Risk Owner xác nhận hậu quả; tài sản/dữ liệu, sự kiện, điều kiện, hậu quả, ranh giới, nguồn | RiskScenario DRAFT→ACTIVE khi đủ target/owner/context; finding đơn lẻ không tự thành scenario. SC-01 giả định đã qua VPN, biết mật khẩu nhưng chưa có WebAuthn/phiên; SC-02 giả định U102 đã có phiên đọc hợp lệ và xét chuyển ba bản ghi đến receiver lab. |

## 3. TUC-04 — Risk assessment

**Tiền điều kiện:** scenario/context và assessment type rõ; actor có quyền; method/profile/rubric đã version. **Input:** E/F, G theo đường trọng yếu, vector C/I_integrity/A/B, cận đã xác nhận, evidence/reason/source, precondition plausibility/horizon. **Output:** RiskEvaluation snapshot gồm P/L/I_total/R25, điểm/nhãn hoặc range, score_determined, status, missing_factors/paths, determination_reasons, actor/time.

1. Actor chọn scenario, scope, loại assessment và chụp context/tiền điều kiện; đối chiếu asset, owner, data flow và control liên quan.
2. Template đề xuất E/F có nguồn; actor xác nhận hoặc ghi UNKNOWN. Đối với CURRENT, TUC-05/06 kiểm tra evidence và tạo ControlAssessment trước khi xác nhận coverage/strength từng đường G ở TUC-04. Có thể dùng ControlAssessment đã có nếu cùng scope/criteria và evidence còn dùng được, ghi chính xác revision. Thiếu căn cứ thì đường G là UNKNOWN; vẫn có thể tính cận/điểm theo RM-01 nếu context hợp lệ, nhưng giữ NEEDS_REVIEW. Không ánh xạ máy móc SATISFIED thành G=1 hoặc failure thành G=5. Risk Owner xác nhận từng chiều impact và rationale.
3. Kiểm tra dữ liệu: thiếu context thiết yếu, miền ngoài 1–5, cận đảo hoặc mâu thuẫn → NEEDS_REVIEW, `score_determined=false`, mọi score/range/nhãn null; lưu validation issues. Không tự kẹp hoặc gán LOW.
4. Với input hợp lệ, tính cận chính xác. Hai cận R25 bằng nhau → có điểm/nhãn và `score_determined=true` ngay cả khi yếu tố UNKNOWN; vẫn NEEDS_REVIEW nếu thiếu evidence, đường G, xác nhận hoặc bất đồng. Hai cận khác nhau → range và NEEDS_REVIEW; không dùng range để ưu tiên tự động.
5. Lưu snapshot bất biến; reviewer có quyền ghi nhận xét hoặc quyết định mới có lý do, giá trị trước/sau, actor/time. Tranh chấp factor được xử lý UNKNOWN với cận đã xác nhận; tranh chấp context thiết yếu thì không tính range. Không lấy trung bình ý kiến.

## 4. TUC-05 — Control và evidence

**Tiền điều kiện:** scenario, scope và control catalog/criteria version. IT/Security có quyền tạo RiskControlLink, ControlImplementation và đăng ký EvidenceItem/Revision; người xác minh phải có quyền tường minh `evidence.verify` cùng quyền đọc đúng scope, đang hiệu lực. Thiết kế bước 03 cấp quyền này cho IT/Security nội bộ (U002) để tự đánh giá; optional Reviewer (U004) chỉ được xác minh trong assessment được giao và trước hạn truy cập. Khi U004 không tham gia/hết hạn, U002 vẫn thực hiện đường self-assessment với audit và nhãn SELF_ASSESSED. Tự xác minh yêu cầu kiểm tra nguồn, nội dung, phạm vi và hiệu lực thực tế; lời khai “đã làm” không thành evidence VERIFIED. `assessment.review` không ngầm cấp `evidence.verify`. Xem [fixture bổ sung quyền và ca luồng](flow-fixtures-v0.2.json); baseline bước 01 được giữ nguyên. Mỗi link ghi mục tiêu và phạm vi; catalog không chứng minh triển khai. EvidenceRevision ghi nguồn, owner, collected_at, valid_until, phạm vi, trạng thái, file/reference và hash nếu có. Một revision có thể hỗ trợ nhiều control nhưng mỗi EvidenceLink nêu phạm vi/tiêu chí. Bản mới không ghi đè bản đã dùng. UNVERIFIED/REJECTED/EXPIRED/sai scope không được dùng để kết luận đạt hoặc thất bại. Kiểm tra quyền đọc riêng trước khi mở evidence nhạy cảm.

## 5. TUC-06 — Control assessment và review

**Tiền điều kiện:** ControlImplementation hoặc trường hợp chưa triển khai, criteria version, scope/test expectation và quyền đánh giá. **Output:** ControlAssessment snapshot với result, criteria, evidence revision, observation, test execution status, reasoning, actor/time, review decision; Gap tương ứng chỉ được tạo ở TUC-07.

1. Đối chiếu từng tiêu chí với evidence VERIFIED, còn hiệu lực, đúng scope và nguồn có thể kiểm tra. Test PASS chỉ khi chạy đúng và observation/log chứng minh expected; FAIL khi vi phạm đã xác minh; lỗi chạy/thiếu telemetry → INCONCLUSIVE.
2. Với từng tiêu chí, không có evidence dùng được, chỉ có khai báo, evidence chưa xác minh/hết hạn/sai scope, hoặc test INCONCLUSIVE → chưa đủ căn cứ; ghi rõ lý do/việc cần xác minh. Khi tổng hợp, nếu chưa có failure đã xác minh và chưa chứng minh đủ các tiêu chí thì `INSUFFICIENT_EVIDENCE` (hoặc `NOT_ASSESSED` nếu chưa khởi sự). Không suy control thất bại từ test lỗi hoặc thiếu alert. Nếu tiêu chí khác đã có failure xác minh, giữ kết quả failure theo criteria và CONTROL_GAP, đồng thời giữ EVIDENCE_GAP của phần chưa rõ; không để INCONCLUSIVE che failure đã biết.
3. Evidence hợp lệ chứng minh tiêu chí không đạt → `NOT_SATISFIED` hoặc `PARTIALLY_SATISFIED` theo criteria; evidence hợp lệ chứng minh đầy đủ tiêu chí → `SATISFIED`. Căn cứ phải gắn phiên bản criteria và revision cụ thể.
4. Reviewer tùy chọn xác nhận hoặc yêu cầu bổ sung. Bất đồng giữ NEEDS_REVIEW, cả hai nhận định và evidence; quyết định phân xử có quyền/lý do/actor/time tạo revision quyết định mới. Không sửa assessment gốc.

## 6. TUC-07 — Gap, treatment, retest

1. Từ `INSUFFICIENT_EVIDENCE` tạo `EVIDENCE_GAP`; từ `NOT_SATISFIED`/phần không đạt đã xác minh tạo `CONTROL_GAP`; `NOT_ASSESSED` giữ pending assessment, không kết luận failure. Gap gắn scenario, control, criteria, assessment, reason và owner.
2. Hiển thị R/range, impact vector, evidence gaps/control failures, tiền điều kiện và plausibility cạnh nhau. Risk Owner/Management có quyền `risk.priority_approve` chốt ưu tiên xử lý chéo scenario với lý do; IT/Security hoặc Reviewer có thể đề xuất. “Reviewer determination” trong RM-01 là nhận định review, không tự cấp quyền phê duyệt ưu tiên vận hành cho consultant. Quyết định review và phê duyệt SME lưu riêng; không cộng tactic/scenario, không xếp theo range. MF-03/MF-04 vẫn NOT_RANKED theo quyết định review hiện hành, chưa có SME xác nhận.
3. IT/Security tạo TreatmentTask có owner, action, due date, expected retest evidence; Risk Owner duyệt/accept nếu được cấp quyền, kèm scope, reason, time. ACCEPT giữ nguyên control failure và gap; task không tự đóng.
4. Sau thực hiện, nộp EvidenceRevision mới và yêu cầu retest. Retest chụp context/criteria/profile/rubric và revision mới, chạy lại TUC-06 và TUC-04 khi có căn cứ risk mới. Bản trước, kể cả report cũ, bất biến. Test INCONCLUSIVE giữ gap cần xử lý; kết quả mới đạt chỉ đóng gap khi người có quyền xác minh tiêu chí và ghi quyết định đóng. Không suy điểm R giảm là do treatment nếu thiếu evidence liên hệ (`treatment_attribution` riêng).
5. So trước/sau chỉ khi cùng scenario, context/tiền điều kiện, profile/rubric và cùng loại CURRENT hoặc INHERENT; khác thì `NOT_COMPARABLE` và giải thích. Trình bày riêng `R_progress`, `impact_progress` và `gap_progress`. Impact lưu từng chiều, `verified_worsening=true/false/null`, `impact_summary_before/after` gồm I_total/range và số chiều bằng max/range. `INCOMPLETE` không che chiều đã xác minh xấu đi; max hoặc R không đổi vẫn có thể có tiến bộ/xấu đi từng chiều. Task chỉ CLOSED khi điều kiện task được xác minh và có actor/time, không tự động bởi điểm.

## 7. TUC-08 — Report và history

Người có quyền chọn phạm vi/as_of/assessment và nhận view cố định theo snapshot: inventory, scenario, E/F/G và vector impact, method/profile/rubric, R25/score/range và status đánh giá và thông tin review, control result/criteria/evidence revision, gap/treatment/task, R/impact/gap progress, quyết định và audit. Từ finding truy ngược toàn chuỗi; báo cáo cũ mở đúng snapshot cũ. Quyền đọc evidence được kiểm tra tại lúc mở, có thể ẩn nội dung và vẫn hiển thị metadata truy vết. Report phân biệt self-assessment, reviewer disagreement, UNKNOWN/INCONCLUSIVE và phạm vi chưa kiểm chứng; không chứng nhận pháp lý.

## 8. Walkthrough tổng hợp (không phải CRM evidence)

| Ca | Chuỗi kiểm tra luồng | Kết quả thiết kế mong đợi |
| --- | --- | --- |
| SC-01 | TUC-03 ghi đã qua VPN, biết mật khẩu U102, chưa có WebAuthn/phiên. TUC-05 gắn AC-DEMO-01; C04/C05 yêu cầu enrollment/recovery độc lập. Nếu chưa có evidence CRM, TUC-06 ghi INSUFFICIENT_EVIDENCE; TUC-07 mở EVIDENCE_GAP. Khi test T12/T16 được thực thi và xác minh vi phạm mới được ghi CONTROL_GAP. Evidence mới + T13–T17/T23 và retest tạo revision/snapshot mới. | Không coi VPN hay login VN Digital Trust là MFA CRM; test lỗi T23 INCONCLUSIVE; chưa suy G hay CURRENT từ fixture. |
| SC-02 | TUC-03 ghi U102 có phiên đọc ba bản ghi; data flow đến AST-RECEIVER, ranh giới tin cậy và đích chính sách còn TO_SET_BEFORE_LAB. TUC-05 gắn EX-DEMO-01; T24 chưa sẵn sàng. TUC-04 E có thể gợi ý 5 nhưng F/G chưa xác nhận. | NEEDS_REVIEW và evidence gap/pending theo criteria; không hạ G nhờ MFA đăng nhập mới. Chỉ so retest khi đường/đích/context giữ tương đương. |

## 9. Truy vết requirement → UC/nhánh → tiêu chí/test

| Requirements | UC/nhánh | Scenario/criteria/test hoặc kiểm tra |
| --- | --- | --- |
| TFR-AUTH-001–004; TNFR-SEC-001; TFR-AUD-001 | TUC-01; quyền hết hạn ở TUC-04–08 | TAC-01, TAC-08; audit quyền/review/accept |
| TFR-INV-001–005; TFR-CTX-001–004 | TUC-02/03; context UNKNOWN | SC-01/02, TAC-02/03/05 |
| TFR-RISK-001–008; TNFR-TRC-001; TNFR-REP-001 | TUC-03/04; input lỗi, UNKNOWN, điểm xác định vẫn review, bất đồng | RM-01 §§2–6; MF-12/13/17; TAC-04/05 |
| TFR-CTL-001–005; TFR-EVD-001–007 | TUC-05/06; evidence sai scope/hết hạn/chưa xác minh | CE-01 C01–C08; T01–T24; TAC-06/07 |
| TFR-EVD-005/006; TFR-TRT-001 | TUC-06/07; INCONCLUSIVE khác failure, EVIDENCE_GAP khác CONTROL_GAP | T23, T24; TAC-06/07 |
| TFR-TRT-002–006 | TUC-07; accept/retest/history/so sánh | RM-01 §5.1; TAC-08/09; SC-01/02 |
| TFR-RPT-001–003; TNFR-EXP-001; TFR-AUD-001 | TUC-08; report as_of và giới hạn | TAC-10; SC-01/02 |

## 10. Giới hạn và việc chuyển tiếp

Sơ đồ nguồn ở [activity](assessment-flow-v0.2.puml) và [sequence](retest-sequence-v0.2.puml); bản render trực tiếp bằng PlantUML ở [activity SVG](assessment-flow-v0.2.svg) và [sequence SVG](retest-sequence-v0.2.svg). [Biên bản kiểm tra](diagram-validation-v0.2-r1.md) ghi phiên bản renderer, hash và kiểm tra hình ảnh. Đây là đặc tả hành vi, chưa chọn kiến trúc, stack, DB/API hay cách tích hợp lab. CE-01 C04/C05 đã có criteria nhưng TTL/session, ngưỡng và môi trường vẫn TO_SET_BEFORE_LAB. TC-01 gồm 24 ca thiết kế chưa chạy. VALID-G-01 thuộc bước 06, NOT_RUN; hai phiếu G A/B trống, rubric chưa được kiểm chứng giữa người chấm. Chưa có evidence CRM, hiệu chuẩn SME hay risk acceptance SME.

## 11. Đính chính v0.2-r1 — 2026-10-17

Hai SVG ngày 2026-10-13 là hình tuyến tính viết tay, không bảo toàn UML của nguồn. Chúng đã được thay bằng render trực tiếp; nguồn activity giữ các nhánh quyền/context/input/evidence/retest và bổ sung điều kiện đóng. Sequence giữ năm đường đời, message và alt/opt; thêm đường self-assessment, kiểm tra quyền hết hạn, failure/inconclusive và đóng gap có điều kiện.

Đồng bộ bốn điểm góp ý: ControlAssessment đi trước G của CURRENT; evidence.verify có người nội bộ thực hiện; status dùng EVALUATED/NEEDS_REVIEW theo RM-01; Risk Owner chốt ưu tiên vận hành. Bổ sung quyền là đặc tả bước 03, chưa phải quyền đã triển khai. Snapshot trước sửa nằm trong [gói lịch sử](../planning/history/step03-v0.2-before-r1.zip). Không thay calculation profile, criteria hoặc dữ liệu kiểm chứng của bước 02.
