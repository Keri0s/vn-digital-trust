# Problem Discovery v0.1

## 1. Purpose and evidence status

Tài liệu này lưu phần research narrative được tách khỏi Project Charter v0.1. Nó mô tả những khoảng trống, giải pháp hiện có, stakeholders và hướng solution đã được nhận diện trong buổi research.

Các nhận định thị trường chưa có citation ngay trong nguồn v0.1 được diễn đạt thận trọng bằng các từ như **có thể**, **may** hoặc **cần kiểm chứng**. Tài liệu không bổ sung fact mới. Các claim cần kiểm chứng được liên kết về `hypotheses.md` và `assumptions-log.md`.

## 2. Problem context

Nguồn v0.1 mô tả một bối cảnh trong đó doanh nghiệp phải quản lý cybersecurity risks, dữ liệu, third parties và nhiều nhóm requirement, trong khi capability và nguồn lực có thể hạn chế. Các vấn đề được xem xét gồm ransomware, credential theft, phishing, data breach, cloud security, third-party risk và các mối đe dọa mới liên quan đến AI.

Research direction không kết luận rằng doanh nghiệp Việt Nam thiếu cybersecurity tools. Trọng tâm là khả năng xác định applicability, kết nối requirement với control và evidence, rồi duy trì một cái nhìn có thể giải thích về readiness.

## 3. Operational capability gap

Không phải doanh nghiệp nào cũng có đủ nguồn lực để xây dựng SOC nội bộ, đội ngũ security chuyên trách, monitoring 24/7, threat detection, incident response, vulnerability management hoặc governance/compliance team riêng.

Đối với SME, hạn chế tiềm năng về nhân sự, chi phí, kiến thức, công cụ và quy trình có thể làm việc xây dựng một chương trình cybersecurity hoàn chỉnh trở nên khó khăn.

Project không xây dựng full SOC. Câu hỏi nghiệp vụ trung tâm là:

> Tổ chức hiện thiếu control hoặc evidence nào để đạt mức readiness phù hợp?

Mức độ phổ biến của từng hạn chế trong toàn bộ thị trường SME Việt Nam chưa được chứng minh trong nguồn v0.1 và cần nghiên cứu định lượng/định tính riêng.

## 4. Compliance and regulatory gap

Doanh nghiệp hoạt động tại Việt Nam có thể phải xử lý nhiều nhóm vấn đề liên quan tới cybersecurity, bảo vệ và quản trị dữ liệu, cross-border transfer, quản trị hệ thống thông tin, third-party processing, security controls và hồ sơ/evidence phục vụ đánh giá.

Vấn đề không chỉ là biết một văn bản có tồn tại. Tổ chức còn phải xác định requirement nào có khả năng áp dụng cho entity, system, data và processing activity cụ thể.

Đối với cross-border processing, nguồn v0.1 nhấn mạnh rằng không nên giả định mọi loại dữ liệu dùng chung một regulatory workflow. Data category và legal context khác nhau có thể dẫn tới requirement, impact assessment, evidence, reporting hoặc review path khác nhau. Việc xác định pathway cụ thể cần được kiểm tra trong legal baseline ở phase sau.

## 5. International frameworks and Vietnamese requirements

Các framework quốc tế được xem xét trong nguồn v0.1 gồm ISO/IEC 27001, NIST Cybersecurity Framework và CIS Controls. Chúng cung cấp baseline cho governance, risk management, access control, asset management, incident response, business continuity, third-party risk và security operations.

Tuy nhiên, framework control không mặc nhiên tương đương 1:1 với một nghĩa vụ pháp lý cụ thể tại Việt Nam. Project vì vậy khám phá một regulatory mapping layer:

```text
Vietnamese Regulation
        ↓
Legal Requirement
        ↓
Security / Governance Control
        ↓
Expected Evidence
```

Nhu cầu và giá trị thực tế của mapping layer này vẫn là hypothesis cần validation.

## 6. Existing solution landscape

### 6.1 International frameworks and assurance criteria

Các ví dụ được ghi nhận trong nguồn gồm ISO/IEC 27001, NIST CSF, CIS Controls và SOC 2 assurance framework. Chúng có thể cung cấp security governance model, risk-management framework, control baseline và audit/assurance criteria.

### 6.2 GRC platforms

Nguồn v0.1 nêu ServiceNow, Archer và các GRC platform khác như những giải pháp có thể hỗ trợ risk, compliance, control, evidence và audit workflow.

Tài liệu không kết luận các nền tảng này thiếu hỗ trợ Việt Nam. Mức độ cần custom configuration, local expertise hoặc manual mapping phải được kiểm tra platform-by-platform.

### 6.3 Technical security tools

Vulnerability scanner, VAPT, SIEM, XDR, EDR và cloud-security tools tập trung vào technical vulnerability, monitoring, detection, configuration assessment hoặc incident investigation. Chúng không nhất thiết tự giải quyết regulatory applicability hay legal-evidence mapping.

### 6.4 Professional services

Nguồn v0.1 ghi nhận doanh nghiệp có thể thuê Big Four, cybersecurity consulting firms, Viettel Cyber Security, VNPT, CMC, MSSP hoặc consultant khác cho pentest, security/compliance assessment, audit, incident response và consulting.

Vì vậy, project không sử dụng claim “Việt Nam không có giải pháp cybersecurity compliance”. Opportunity đang được khám phá là guided assessment, continuous readiness và evidence-driven decision support cho tổ chức có nguồn lực hạn chế.

## 7. Core problem synthesis

Các control, regulatory materials, evidence và operational information có thể phân tán giữa nhiều system, document và department. Một tổ chức vì vậy có thể khó trả lời đồng thời:

- Requirement nào có khả năng áp dụng?
- Control nào hỗ trợ requirement đó?
- Evidence nào được kỳ vọng và evidence nào hiện có?
- Potential gap nằm ở đâu?
- Remediation nào nên được ưu tiên?

Working problem direction:

> Organizations may lack a unified and accessible method to determine regulatory applicability, map Vietnamese requirements to security controls, collect evidence, identify potential gaps and continuously understand cybersecurity/data-compliance readiness.

Đây là research direction, không phải kết luận thị trường đã được xác nhận.

## 8. Proposed solution concept

Solution concept liên kết organization context với applicability, requirement, control, evidence, gap, risk và remediation. Thay vì chỉ dùng `Compliant / Not compliant`, kết quả phải truy ngược được:

```text
Requirement
    → Control
    → Expected Evidence
    → Provided Evidence
    → Assessment Result
```

### Regulatory decision support

Một decision path tiềm năng:

```text
Is personal or regulated data processed?
              ↓
Where is data stored?
              ↓
Is data transferred internationally?
              ↓
What type of data and processing context?
              ↓
Which requirements may apply?
              ↓
Which documents, assessments or evidence may be required?
```

Output là decision support có reasoning, không phải automatic legal interpretation.

## 9. Business readiness workflow

### Discover

Ghi nhận systems, applications, assets, data, SaaS/cloud services, vendors, data owners/processors và data flows.

### Assess

So sánh current state với applicable regulatory requirements, security/governance controls, internal policy và selected industry framework để thực hiện gap assessment.

### Remediate

Theo dõi remediation như MFA, access control, logging, encryption, policy, vendor contract, consent, retention hoặc security configuration.

### Evidence and regulatory preparation

Thu thập evidence, duy trì documentation, chuẩn bị impact assessment hoặc filing khi applicable, lưu audit trail và theo dõi thay đổi.

Đây là workflow do project đề xuất để tổ chức thông tin; không phải sequence pháp lý bắt buộc.

## 10. Evidence findings and direction

Evidence không nên chỉ là thư mục file độc lập. Nó cần được gắn với requirement/control và có thể hỗ trợ nhiều mapping.

Ví dụ:

- Consent-related evidence: record, timestamp, purpose, user action, consent version.
- Access-control evidence: IAM policy, MFA configuration, access-review report, audit log.
- Các nhóm khác trong nguồn v0.1: system logs, architecture/network/data-flow diagrams, data inventory, vendor contracts, DPA, privacy/security policies, incident-response plan, assignment records, risk/impact assessments, backup configuration và security-assessment reports.

Specific evidence requirement phải được xác định theo từng requirement và context, không áp dụng đồng nhất cho mọi doanh nghiệp.

## 11. Stakeholders

| Stakeholder | Vai trò trong workflow |
|---|---|
| Management | Business ownership, budget, risk acceptance, strategic decisions |
| Legal / Compliance / Privacy | Regulatory interpretation, contracts, privacy documents, impact assessment, compliance evidence |
| IT / Security | Infrastructure, IAM, logging, encryption, network security, incident response, configuration, technical evidence |
| Business departments | Data collection, operational processing, consent and business-application usage |
| System / Data Owner | Purpose, data types, access, business requirements |
| Procurement / Vendor Management | Third-party onboarding, contracts, SaaS management, vendor requirements and risk |

Các business department ví dụ trong nguồn v0.1 gồm HR, Marketing, Sales và Customer Service.

## 12. Why SME is the initial segment

SME được chọn vì scope ban đầu có thể kiểm soát hơn, organization/assets/workflows có thể ít phức tạp hơn enterprise, nhu cầu guidance có thể cao và mô hình guided assessment có thể phù hợp.

Các lý do về nhu cầu, willingness to self-assess và resource constraints cần được validation; chúng không nên được trình bày như thống kê đại diện khi chưa có dữ liệu.

Domain model vẫn nên có khả năng mở rộng, nhưng enterprise workflow không thuộc phạm vi v0.1.

## 13. Synthetic organization for prototype testing

```text
Organization: ABC Trading
Employees: 80

Systems:
- Website
- CRM
- HRM
- Microsoft 365
- AWS
- Google Analytics

Data:
- Customer PII
- Employee data
- Contract data

Vendors:
- Microsoft
- AWS
- CRM SaaS Provider
```

Đây là synthetic scenario, không phải case study của doanh nghiệp thật. Nó có thể dùng để test regulatory mapping, evidence collection, assessment engine, remediation workflow và dashboard/report.

## 14. Domain and architecture directions carried forward

Các hướng dưới đây là design direction, chưa phải architecture decision cuối cùng:

- Lightweight web application, backend, PostgreSQL, regulatory knowledge base, rule/assessment engine, evidence repository và reporting dashboard.
- Modular architecture để mở rộng sau.
- Requirement record có thể cần: identifier, legal source/article, effective dates, status, applicability, type, expected evidence, related controls, supersession và transitional rule.
- Regulation/control lifecycle cần được versioned thay vì hard-code như static text.

Chi tiết được chuyển sang Requirements Discovery, Domain Model và Architecture v0.1.

## 15. Product positioning hypothesis

Current proposed positioning:

> A Vietnam-focused cybersecurity and data compliance readiness platform for SMEs that uses regulatory decision support, control mapping and evidence-driven assessment to identify potential readiness gaps and support prioritized remediation.

Potential differentiator:

> Security Controls × Vietnamese Regulation × Evidence × Continuous Readiness

Cả positioning và differentiator đều là hypothesis. Project không tuyên bố chưa có giải pháp cạnh tranh tương tự khi chưa hoàn thành market comparison.

## 16. Next research activities

- SME and consultant interviews.
- Global GRC platform comparison.
- Vietnamese compliance-consulting workflow.
- Data-mapping and evidence-collection difficulty.
- Cross-border data decision paths.
- Third-party risk.
- Regulation update mechanism.
- Selected technical-evidence integration.
- Manual versus platform-assisted assessment experiment.

AI governance, cloud evidence automation, FDI requirements và enterprise workflows thuộc hướng nghiên cứu sau v0.1 và không chặn prototype đầu tiên.

