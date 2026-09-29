# Đối chiếu Requirements Discovery v0.1 với research

Ngày đối chiếu: 2026-09-30.

## 1. Kết luận

Bản requirements đi đúng hướng của research: SME, applicability theo context, requirement → control → evidence → assessment, phân biệt thiếu evidence với thiếu control, ưu tiên remediation và báo cáo readiness. Tuy nhiên, bản hiện tại chưa thể hiện đầy đủ các giới hạn nghiên cứu và tiêu chí đánh giá trong charter. Nên bổ sung các điểm dưới đây trước khi dùng làm baseline cho use cases và domain model.

Đây là đối chiếu tính nhất quán giữa các tài liệu; không xác minh tính đúng đắn hoặc hiệu lực của các quy định pháp luật.

## 2. Nguồn đã đọc

- [Project Charter v0.1](D:/Projects/vn-digital-trust/docs/research/project-charter.md) — nguồn chính cho scope.
- [Problem Discovery v0.1](D:/Projects/vn-digital-trust/docs/research/problem-discovery-v0.1.md) — bối cảnh và hướng giải pháp.
- [Hypotheses Register](D:/Projects/vn-digital-trust/docs/research/hypotheses.md) — các giả thuyết chưa được kiểm chứng.
- [Assumptions Log](D:/Projects/vn-digital-trust/docs/research/assumptions-log.md) — giới hạn khi dùng assumption để xây prototype.
- Bản requirements được tạo trong cuộc trò chuyện, cùng các quyết định mới của người dùng về single-tenant, RBAC, self-assessment và reviewer tùy chọn.

## 3. Những phần đã liên kết tốt

| Nội dung research | Requirements hiện tại | Nhận xét |
| --- | --- | --- |
| Charter §6–8: context và inventories | FR-ORG, FR-SYS, FR-AST, FR-DATA, FR-VND | Có đầy đủ các nhóm chính; giữ data flow ở mức cơ bản. |
| Charter §10: applicability trước assessment | FR-QST, FR-APP | Questionnaire thu thập facts và rule giải thích kết quả phù hợp với hướng đã chọn. |
| Charter §7: chuỗi requirement/control/evidence/result | FR-REQ, FR-CTL, FR-EVD, FR-ASMT | Có mapping nhiều-nhiều và traceability. |
| Problem Discovery §10: evidence có context | FR-EVD-001 đến 007 | Có expected/provided evidence, metadata, verification và reuse. |
| Charter §12: phát hiện thiếu evidence và control gap | FR-ASMT-004, FR-GAP-002 | Phân biệt INSUFFICIENT_EVIDENCE với NOT_SATISFIED là điểm phù hợp quan trọng. |
| Charter §6–8: remediation và reporting | FR-GAP, FR-REM, FR-RPT | Có prioritization, task, retest và report; còn thiếu recommendation rõ ràng. |
| Charter §9–10; W-005: technical evidence có giới hạn | FR-TECH | Manual import phù hợp; liệt kê Wazuh/Nmap không có nghĩa phải tích hợp chúng trong v0.1. |
| Charter §13: một người phát triển, máy khoảng 16 GB | NFR-DEP-001 | Phù hợp với prototype nhẹ. |
| Charter §3, §10: readiness, human review | FR-ASMT-005 đến 007, FR-RPT-004 | Không cấp chứng nhận pháp lý; override có lý do và audit. |

## 4. Các điểm cần chỉnh trước khi chốt baseline

### 4.1. Giới hạn tập rules và regulatory coverage — quan trọng

**Nguồn:** Assumptions A-003, A-004, W-003; Hypothesis H1.

FR-APP và FR-REQ mới yêu cầu deterministic rules, nguồn pháp lý và version. Chưa yêu cầu rõ chỉ dùng một tập requirement/mapping/example pathways đã được review cho prototype.

**Đề xuất:** Ghi rõ tập nội dung được chọn, phạm vi đã review, nguồn, ngày/version và người hoặc vai trò review. Những context chưa được bao phủ phải hiện trạng thái cần làm rõ hoặc review; không tự suy ra NOT_APPLICABLE. Đây là đề xuất triển khai giới hạn đã có trong research.

Reviewer duyệt nội dung rules/mappings và consultant review một assessment là hai trách nhiệm khác nhau. Có thể duyệt nội dung mẫu trước khi đưa vào prototype, không cần xây workflow phê duyệt nội dung lớn trong v0.1.

### 4.2. Self-assessment là lựa chọn thiết kế, H4 vẫn chưa được kiểm chứng

**Nguồn:** Charter §5; H4; A-007.

Người dùng đã chọn SME self-assessment làm happy path và consultant là reviewer tùy chọn. Quyết định đó hợp lệ để xây prototype, nhưng không chứng minh SME thực tế thích self-assessment.

**Đề xuất:** Thêm ghi chú “prototype design decision; H4 remains unvalidated” và liên kết H4/A-007. Giữ nhu cầu thử cả self-service và assisted workflow khi validation.

Single-tenant và RBAC là quyết định cụ thể hóa sau research. Charter nói consultant có thể hỗ trợ nhiều SME không bắt buộc một deployment phải chứa nhiều SME; v0.1 không cung cấp dashboard đa khách hàng.

### 4.3. Thiếu phiên bản control, mapping và tiêu chí assessment

**Nguồn:** Charter §10.4; Problem Discovery §14.

FR-REQ-004 giữ phiên bản requirement, FR-QST-005 giữ questionnaire/rule; control và mapping chưa có yêu cầu version rõ ràng. Nếu mapping hoặc criteria thay đổi, kết quả lịch sử có thể không tái hiện được chỉ bằng requirement version.

**Đề xuất:** Assessment phải tham chiếu phiên bản control, requirement-control mapping, assessment criteria và evidence được dùng. Lần cập nhật sau không thay đổi ý nghĩa của kết quả cũ.

### 4.4. Có remediation task nhưng thiếu recommendation cụ thể

**Nguồn:** Charter §6.6 và §8.

FR-REM hiện chủ yếu quản lý task, owner, trạng thái và retest. Charter còn yêu cầu hướng dẫn tổ chức nên làm gì để khắc phục gap.

**Đề xuất:** Mỗi gap có hướng dẫn hành động, lý do và evidence cần cung cấp khi retest. Dùng nội dung curated/template và rule; không cần AI.

### 4.5. Thiếu tiêu chí nghiệm thu và kế hoạch đánh giá nghiên cứu

**Nguồn:** Charter §11–13; Problem Discovery §13; W-001.

NFR-TST mới yêu cầu rule test được. Bản requirements chưa chuyển success criteria của charter thành các trường hợp đánh giá cụ thể.

**Đề xuất:** Thêm phần validation cho synthetic SME ABC Trading, gồm hoàn thành flow; applicability so với expected result đã review; traceability; phân biệt thiếu evidence/failed control; độ nhất quán khi lặp lại với cùng inputs và versions; effort so với spreadsheet/document baseline. Ghi kết quả thực nghiệm và giới hạn, không tự đặt accuracy hay phần trăm tiết kiệm thời gian chưa có cơ sở.

### 4.6. Danh sách deferred dễ bị hiểu thành cam kết roadmap

**Nguồn:** Charter §9; H5; A-008.

Charter loại một số năng lực khỏi v0.1; điều này chưa có nghĩa chúng sẽ được xây trong v0.2. Bản requirements còn bỏ sót việc nêu rõ full ISO certification platform, enterprise GRC replacement và critical-infrastructure/government-system compliance platform.

**Đề xuất:** Bổ sung exclusions theo charter và ghi “out of v0.1; future consideration only, no delivery commitment”. Giữ AI ở vai trò hỗ trợ; không mô tả AI compliance decisions như mục tiêu tương lai đã được chốt. Evidence expiry và retest ở prototype không chứng minh giá trị continuous readiness của H5.

### 4.7. Quyền chấp nhận rủi ro cần rõ hơn

**Nguồn:** Problem Discovery §11; FR-REM-003 có ACCEPTED_RISK.

Actor Management hiện chỉ được mô tả là xem báo cáo. Requirement chưa nêu ai được chấp nhận rủi ro và theo điều kiện nào.

**Đề xuất:** Chỉ vai trò được cấp quyền mới được ghi nhận risk acceptance, kèm người quyết định, thời điểm và lý do. Accepted risk không chuyển control thành SATISFIED. Đây là chi tiết cần làm rõ trong RBAC, không cần thêm một module enterprise risk.

Business departments, system/data owners và procurement có thể cung cấp thông tin thông qua IT/Compliance trong v0.1; không nhất thiết tạo thêm từng role riêng.

## 5. Cách liên kết tài liệu khi cập nhật

```text
Project Charter                  → scope, objectives, success criteria
Problem Discovery                → context, stakeholders, solution rationale
Hypotheses + Assumptions Log      → chưa kiểm chứng gì, giới hạn nào phải giữ
Quyết định người dùng             → single-tenant, RBAC, self-assessment, optional reviewer
Requirements Discovery           → chức năng, ràng buộc và acceptance criteria
Use Cases → Domain Model         → bước tiếp theo sau khi bổ sung baseline
```

Nên thêm một bảng traceability ngắn ở requirements: nhóm FR/NFR → mục charter hoặc H/A/W liên quan. Các quyết định mới ghi riêng là quyết định thiết kế để không biến thành research finding.

## 6. Phạm vi của lần đối chiếu này

Bản requirements hiện có đủ cấu trúc để tiếp tục hoàn thiện. Các vấn đề chính là thiếu ràng buộc và traceability về research, chưa có mâu thuẫn nền tảng buộc phải đổi mô hình single-tenant hoặc bỏ self-assessment. Báo cáo này đề xuất các sửa đổi; bản requirements và bốn file research chưa được sửa trong lần đối chiếu này.
