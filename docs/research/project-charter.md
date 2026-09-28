# Project Charter v0.1

## 1. Document purpose

Tài liệu này là bản charter ngắn gọn và là nguồn tham chiếu chính cho phạm vi v0.1. Các ghi chép nghiên cứu, giả thuyết và assumption được quản lý riêng trong:

- `problem-discovery-v0.1.md`
- `hypotheses.md`
- `assumptions-log.md`

## 2. Project overview

**Working title:** Vietnam Cybersecurity & Data Compliance Readiness Platform  
**Project type:** Cybersecurity / Compliance / GRC / Decision-Support Platform  
**Version:** v0.1 — Problem Discovery & Initial Scope  
**Primary target:** Vietnamese SMEs  
**Secondary target:** Cybersecurity and compliance consultants supporting SMEs

## 3. Vision

Xây dựng một nền tảng hỗ trợ doanh nghiệp Việt Nam đánh giá mức độ sẵn sàng về cybersecurity, bảo vệ dữ liệu, các yêu cầu pháp lý liên quan tại Việt Nam và khả năng cung cấp evidence cho những biện pháp bảo vệ đã triển khai.

Nền tảng đóng vai trò **pre-assessment**, **continuous readiness**, **decision support** và **evidence management**. Hệ thống không thay thế chuyên gia pháp lý, chuyên gia cybersecurity, kiểm toán độc lập hoặc nền tảng GRC quy mô lớn.

## 4. Core problem statement

Các doanh nghiệp Việt Nam, đặc biệt là SME, có thể phải đồng thời quản lý cybersecurity controls, dữ liệu cá nhân, third-party services và các yêu cầu pháp lý Việt Nam trong khi không có đội ngũ cybersecurity/compliance chuyên biệt.

Control, regulation, evidence và operational information có thể nằm phân tán trong nhiều hệ thống, tài liệu và phòng ban. Vì vậy, doanh nghiệp khó trả lời:

> Hiện tại tổ chức đã sẵn sàng đến mức nào và còn thiếu những gì để đáp ứng các yêu cầu cybersecurity và data compliance có liên quan?

Project khám phá một cách tiếp cận **Vietnam-specific, evidence-driven và risk-based** để xác định các potential control/evidence readiness gaps và hỗ trợ ưu tiên remediation. Hệ thống không đưa ra kết luận pháp lý cuối cùng về tình trạng tuân thủ.

## 5. Target users

### Primary user — Vietnamese SME

Đối tượng ban đầu là SME có sử dụng cloud/SaaS, xử lý dữ liệu khách hàng hoặc nhân viên, có tài sản IT nhưng nguồn lực security/compliance hạn chế và có thể chưa biết bắt đầu assessment từ đâu.

Primary need:

> Tôi cần biết doanh nghiệp đang thiếu gì, evidence nào cần có và nên ưu tiên xử lý việc gì.

### Secondary user — Cybersecurity / compliance consultant

Consultant có thể dùng hệ thống để hỗ trợ assessment nhiều SME, thu thập evidence, mapping requirement, theo dõi remediation và tạo readiness report.

Việc SME có thực sự muốn self-assessment, hay phù hợp hơn với consultant-assisted assessment, vẫn là giả thuyết cần kiểm chứng.

## 6. Objectives v0.1

Prototype cần chứng minh được một workflow có khả năng:

1. Mô tả organization context, systems/assets, data và vendors.
2. Hỗ trợ xác định những requirement có khả năng áp dụng.
3. Liên kết requirement với security/governance controls và expected evidence.
4. Ghi nhận provided evidence và assessment result có traceability.
5. Xác định potential readiness gaps.
6. Hỗ trợ risk prioritization và remediation recommendation.
7. Sinh readiness report dễ đọc và giải thích được.

## 7. Core workflow

```text
Organization Profile
        ↓
System / Asset Inventory
        ↓
Data and Vendor Inventory
        ↓
Applicability Assessment
        ↓
Regulatory Requirements
        ↓
Security / Governance Controls
        ↓
Expected and Provided Evidence
        ↓
Gap Assessment
        ↓
Risk Prioritization
        ↓
Remediation Recommendation
        ↓
Readiness Report
```

Traceability backbone:

```text
Requirement
    → Control
    → Expected Evidence
    → Provided Evidence
    → Assessment Result
```

Đây là business readiness workflow, không phải khẳng định rằng pháp luật yêu cầu mọi doanh nghiệp thực hiện theo đúng một chuỗi bước cố định.

## 8. Scope v0.1

- Organization profiling.
- Basic asset/system inventory.
- Basic data inventory and data-flow context.
- Vendor inventory.
- Regulatory applicability decision support.
- Requirement repository.
- Requirement-to-control mapping.
- Control assessment.
- Evidence management.
- Gap/readiness assessment.
- Risk prioritization.
- Remediation recommendations.
- Readiness reporting.

## 9. Out of scope v0.1

- Full SOC hoặc production-scale SIEM ingestion.
- Real-time threat detection, XDR, EDR hoặc malware detection.
- Enterprise asset discovery hoặc large-scale cloud scanning.
- Full automated penetration testing.
- Full ISO 27001 certification platform.
- Automatic legal interpretation, legal approval hoặc government submission.
- Enterprise-scale GRC replacement.
- Critical-infrastructure hoặc government-system compliance platform.
- Full FDI compliance platform.
- Complete AI threat-detection platform.

## 10. Design principles

> **Đề xuất cấu trúc mới:** Phần này được rút ra từ định hướng và giới hạn đã có trong tài liệu gốc; đây không phải research finding mới.

1. **Applicability before assessment.** Không dùng một checklist giống nhau cho mọi tổ chức.
2. **Evidence over checkbox.** Kết quả cần gắn với expected và provided evidence.
3. **Traceability over opaque scoring.** Kết luận phải truy ngược được tới requirement, control và evidence.
4. **Versioned regulation and controls.** Requirement cần hỗ trợ hiệu lực, thay thế và giai đoạn chuyển tiếp.
5. **Readiness is not legal certification.** Nền tảng hỗ trợ quyết định, không cung cấp legal advice hoặc chứng nhận tuân thủ.
6. **Human review remains necessary.** Những quyết định cần diễn giải pháp lý/chuyên môn không được tự động hóa như kết luận cuối cùng.
7. **Selected technical evidence may strengthen validation.** Technical evidence chỉ nên được bổ sung theo phạm vi kiểm soát được, không biến v0.1 thành SOC/SIEM project.

## 11. Research questions

> **Đề xuất cấu trúc mới:** Các câu hỏi dưới đây chuyển hướng đã có thành câu hỏi nghiên cứu; chúng chưa phải kết luận đã được chứng minh.

- **RQ1:** Làm thế nào biểu diễn các yêu cầu cybersecurity và data protection liên quan tại Việt Nam dưới dạng applicability rules có thể quản lý và kiểm thử?
- **RQ2:** Làm thế nào ánh xạ applicable requirements tới security/governance controls và verifiable evidence với traceability rõ ràng?
- **RQ3:** Một evidence-driven assessment workflow có thể nhận diện potential readiness gaps trong synthetic SME environment với reasoning giải thích được hay không?
- **RQ4:** Workflow đề xuất khác quy trình spreadsheet/document-based manual assessment như thế nào về traceability, consistency và assessment effort?

## 12. Success criteria

### 12.1 Product acceptance

Một synthetic SME có thể hoàn thành đầy đủ core workflow: organization profile; inventories; applicability questions; relevant requirements; control mapping; evidence registration; gap identification; remediation prioritization; readiness report.

### 12.2 Research evaluation

Prototype tạo đủ dữ liệu để đánh giá:

- Applicability decision correctness against a reviewed test scenario.
- Requirement-to-control traceability.
- Control-to-evidence traceability.
- Detection of missing evidence and potential control gaps.
- Consistency of repeated assessments.
- Assessment effort compared with a manual spreadsheet/document workflow.

Không đặt trước accuracy hoặc time-reduction threshold khi chưa có experiment và baseline để bảo vệ con số đó.

## 13. Constraints

- Single student developer.
- Laptop khoảng 16 GB RAM.
- Limited financial resources.
- Primarily local development.
- Synthetic / controlled test data.

Thiết kế ưu tiên correct domain model, regulatory mapping, evidence model, assessment logic, explainability và testability; không tối ưu sớm cho enterprise production load.

## 14. Current phase and scope decision

```text
Problem Discovery v0.1        completed
Project Charter v0.1         refactored
Requirements Discovery v0.1  next
Use Cases
Domain Model
Architecture v0.1
Prototype v0.1
Validation
Research / Scope v0.2
```

Phạm vi problem v0.1 được tạm thời freeze. Major scope changes chỉ nên được đưa vào khi có new evidence, user feedback, regulatory requirement, technical necessity hoặc prototype findings.

