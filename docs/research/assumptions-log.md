# Assumptions Log

## 1. Purpose

Tài liệu này ngăn các assumption, simplification hoặc research note bị trình bày lại như fact. Mỗi entry giữ nguyên ý nghĩa từ nguồn v0.1 và nêu cách sử dụng an toàn trong các tài liệu tiếp theo.

## 2. Status definitions

- **Rejected:** Không được dùng lại như premise của project.
- **Incorrect simplification:** Cách diễn đạt tuyệt đối hóa làm sai hoặc mất điều kiện/context.
- **Unverified:** Có thể hợp lý nhưng chưa đủ evidence đại diện.
- **Working assumption:** Tạm dùng để xây prototype; phải ghi rõ giới hạn.
- **Validated:** Chỉ dùng khi có source/evidence và phạm vi validation được ghi lại.

## 3. Rejected assumptions

### A-001 — “International cybersecurity frameworks are mainly technical”

**Status:** Rejected.  
**Reason:** ISO 27001 và NIST CSF cũng bao gồm governance, risk, policy và organizational controls.  
**Safe replacement:** International frameworks provide both technical and governance-oriented structures; they do not automatically equal specific Vietnamese legal requirements.  
**Impact:** Không được dùng assumption này để tạo false contrast giữa framework và regulation.

### A-002 — “No cybersecurity compliance assessment services exist in Vietnam”

**Status:** Rejected.  
**Reason:** Nguồn v0.1 đã ghi nhận các provider và service category về security assessment, consulting và audit.  
**Safe replacement:** Existing services are available; the project explores guided assessment, evidence traceability and continuous readiness for a constrained target segment.  
**Impact:** Không claim project lấp một thị trường hoàn toàn trống.

## 4. Incorrect simplifications

### A-003 — “All Vietnamese personal data must be stored in Vietnam”

**Status:** Incorrect simplification.  
**Reason:** Applicability phụ thuộc regulation, entity, data category và context.  
**Safe replacement:** Data-location and localization obligations must be evaluated through a reviewed applicability path for the relevant context.  
**Required follow-up:** Legal baseline và versioned decision rules.

### A-004 — “All cross-border transfers require the same approval workflow”

**Status:** Incorrect simplification.  
**Reason:** Data category và legal framework khác nhau có thể tạo regulatory pathways khác nhau.  
**Safe replacement:** The system must support context-dependent applicability and decision paths rather than one static cross-border checklist.  
**Required follow-up:** Build only reviewed example pathways in v0.1.

## 5. Unverified assumptions

### A-005 — “Most Vietnamese companies do not have SOC”

**Status:** Unverified.  
**Risk:** “Most” là market statistic cần representative evidence.  
**Safe replacement:** Some target SMEs may lack an internal SOC or dedicated security team; participant selection must verify this at case level.  
**Validation:** Representative survey/source or clearly bounded interview sample.

### A-006 — “Global GRC platforms are always slow to update Vietnamese regulation”

**Status:** Unverified; absolute wording is not allowed.  
**Risk:** Platform capabilities, content packs, partners và update cycles khác nhau.  
**Safe replacement:** The effort required to represent selected Vietnamese requirements must be evaluated platform-by-platform.  
**Validation:** Versioned comparison matrix with primary product documentation where possible.

### A-007 — “SMEs prefer self-assessment”

**Status:** Unverified working assumption extracted from the proposed delivery model.  
**Risk:** SMEs may prefer consultant-led or consultant-assisted assessment.  
**Safe replacement:** Test both self-service and assisted workflows; keep consultant as a secondary user.  
**Related hypothesis:** H4.

### A-008 — “Continuous evidence tracking is more valuable than a one-time report”

**Status:** Unverified.  
**Risk:** The target segment may only need point-in-time assessment.  
**Safe replacement:** Continuous readiness is a candidate value proposition to be validated after the initial workflow.  
**Related hypothesis:** H5.

### A-009 — “SME scope is inherently simple”

**Status:** Unverified working assumption.  
**Risk:** Company size does not guarantee simple data flows, vendor relationships or legal context.  
**Safe replacement:** SME is a scope boundary for v0.1; each test organization still requires context-based assessment.

## 6. Prototype working assumptions

Các assumption dưới đây được phép dùng để build, nhưng không được trình bày như market fact hoặc legal conclusion.

| ID | Working assumption | Boundary |
|---|---|---|
| W-001 | ABC Trading is a useful test organization | Synthetic scenario only; not representative evidence |
| W-002 | A lightweight local architecture is sufficient | Prototype v0.1 only; no production-scale claim |
| W-003 | Organization, asset, data and vendor context can drive sample applicability rules | Only reviewed sample rules may produce demonstrable results |
| W-004 | Requirement → Control → Evidence → Result is the core traceability chain | Must be tested for exceptions and many-to-many relationships |
| W-005 | Selected technical evidence can be represented as evidence objects | Does not imply automated verification or full SOC integration |

## 7. Validated assumptions

Chưa có entry nào được đánh dấu **Validated** trong nguồn v0.1. Khi cập nhật, phải ghi rõ evidence, source/date, phạm vi áp dụng và limitations.

## 8. Change template

```markdown
### A-XXX — Assumption statement

**Previous status:**
**New status:**
**Evidence:**
**Scope of validation:**
**Limitations:**
**Decision / document changes:**
```
