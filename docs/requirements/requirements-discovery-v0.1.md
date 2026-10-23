# VN Digital Trust — Requirements Discovery v0.1

**Status:** Working requirements baseline for prototype v0.1; regulatory content and user need remain subject to validation.

**Scope:** One deployment for one Vietnamese SME; self-assessment is the primary journey.

**Basis:** [Project Charter](../research/project-charter.md), [Problem Discovery](../research/problem-discovery-v0.1.md), [Hypotheses](../research/hypotheses.md), [Assumptions Log](../research/assumptions-log.md), and subsequent project decisions.

## 1. Scope assumptions

- **Single tenant:** One deployment serves one SME organization. Initial setup configures its organization profile and first administrator once. There is no user-facing “Create Company” or SaaS onboarding flow.
- **Multiple users:** People in the same organization sign in with individual accounts and role-based access control (RBAC). Authentication supports authorization and accountability.
- **Primary workflow:** SME staff conduct a self-assessment. An external consultant may be granted a reviewer role, but review is optional.
- **Decision model:** Structured facts and versioned, deterministic rules identify *potentially applicable* requirements. Curated mappings connect requirements to controls. Evidence and explicit criteria drive preliminary control assessments.
- **Positioning:** The product supports readiness and decisions. It does not issue legal opinions, certify compliance, or conclude that an organization has violated the law.
- **AI:** Any later AI capability may assist with explanation or drafting; it has no decision authority in v0.1.
- **Evidence status:** SME preference for self-assessment is a design assumption for the prototype, not a validated market finding (H4, A-007). The prototype must permit comparison with consultant-assisted work.
- **Regulatory coverage:** Demonstrations use a selected, bounded set of example requirements, rules, controls and mappings. Each legal pathway must be reviewed and its scope recorded before it is presented as a reviewed example (W-003, A-003, A-004). Unreviewed content remains marked as draft.
- **Unknown context:** Missing, uncertain or uncovered context requires review. It must not silently become NOT_APPLICABLE or a legal conclusion.

## 2. Actors

| ID | Actor | Main responsibilities |
| --- | --- | --- |
| ACT-01 | Organization Administrator | Configure organization, manage users and roles, maintain settings. |
| ACT-02 | IT / Security User | Maintain systems and assets, provide technical evidence, perform remediation. |
| ACT-03 | Compliance / Privacy User | Answer context questions, maintain data processing information, provide policy and document evidence. |
| ACT-04 | Management | View dashboard, gaps, remediation progress, and reports. |
| ACT-05 | Consultant / Reviewer (optional) | Review evidence and preliminary results, request more evidence, and justify overrides. |

Roles describe permissions, not separate tenants. One person may hold more than one authorized role.

## 3. Core user journey

1. An administrator completes initial setup: organization profile and first admin account.
2. Authorized users sign in and record systems, assets, data processing, and vendors.
3. Staff answer a branching questionnaire that captures structured facts.
4. The applicability engine evaluates versioned rules and explains potentially applicable requirements.
5. Users inspect mapped controls and submit supporting evidence.
6. The assessment engine produces preliminary, explainable control states; a reviewer may intervene if enabled.
7. The system creates readiness gaps, users assign remediation, submit new evidence, and retest.
8. Management receives a report with scope, findings, evidence status, and traceability.

## 4. Functional requirements

Priorities describe the **planned prototype**, not evidence that a feature is legally required or wanted by representative users: **MUST** = baseline capability; **SHOULD** = desired if feasible; **COULD** = future option. Requirement IDs remain stable for use-case traceability.

### A. Authentication and authorization

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-AUTH-001 | MUST | Require authentication for protected functionality. |
| FR-AUTH-002 | MUST | Associate each user with one or more roles. |
| FR-AUTH-003 | MUST | Enforce RBAC on viewing and changing organization data, assessments, evidence, and reports. |
| FR-AUTH-004 | MUST | Let an administrator create and disable accounts and assign or change roles. |
| FR-AUTH-005 | MUST | Attribute security-relevant changes to the authenticated user. |

### B. Organization Profile

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-ORG-001 | MUST | Configure one organization profile during initial setup, including name, industry, size, activities, locations, and contacts as relevant. |
| FR-ORG-002 | MUST | Let authorized users update the profile after setup. |
| FR-ORG-003 | MUST | Supply relevant profile attributes to applicability evaluation and preserve the context used by an assessment. |

### C. Information Systems

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-SYS-001 | MUST | Register information systems such as CRM, HRM, websites, ERP, and SaaS services. |
| FR-SYS-002 | MUST | Record purpose, owner, hosting model, internet exposure, criticality, and data handled. |
| FR-SYS-003 | SHOULD | Relate systems to assets, data, applications, and vendors. |

### D. Asset Inventory

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-AST-001 | MUST | Register IT assets. |
| FR-AST-002 | MUST | Classify assets, including server, endpoint, network device, application, database, cloud resource, and SaaS. |
| FR-AST-003 | MUST | Record an owner or responsible party when applicable. |
| FR-AST-004 | MUST | Link an asset to one or more information systems. |

### E. Data Inventory

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-DATA-001 | MUST | Register important data assets. |
| FR-DATA-002 | MUST | Classify data, including personal, sensitive, employee, customer, contract, and business data; avoid assuming every category follows the same regulatory path. |
| FR-DATA-003 | MUST | Record processing purpose, data type, system, storage location, controller/processor context, third parties, and international transfer indicator. |
| FR-DATA-004 | SHOULD | Model basic source → system → processor → storage → destination relationships. |

### F. Vendor / Third Party

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-VND-001 | MUST | Register vendors and third-party service providers. |
| FR-VND-002 | MUST | Record service, data access, systems involved, and processing role. |
| FR-VND-003 | MUST | Link vendors to systems, data, and processing activities. |

### G. Questionnaire

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-QST-001 | MUST | Present an assessment questionnaire for organization and assessment context. |
| FR-QST-002 | MUST | Branch conditionally based on prior answers. |
| FR-QST-003 | MUST | Store typed answers, such as boolean, enum, number, date, and multi-select. |
| FR-QST-004 | SHOULD | Save an incomplete questionnaire and resume it later. |
| FR-QST-005 | MUST | Preserve the questionnaire and rule versions used for an assessment. |

Questionnaire answers establish facts; a “yes” answer about a control does not itself prove that the control is satisfied.

### H. Applicability Engine

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-APP-001 | MUST | Evaluate relevant organization, system, data, vendor, and questionnaire context. |
| FR-APP-002 | MUST | Apply deterministic, versioned applicability rules. |
| FR-APP-003 | MUST | Identify requirements as *potentially applicable based on available context*. |
| FR-APP-004 | MUST | Explain each result with the triggering facts, rule ID, and rule version. |
| FR-APP-005 | SHOULD | Allow an authorized reviewer to review applicability results. |
| FR-APP-006 | MUST | Return a distinct NEEDS_REVIEW/UNKNOWN result with reasons when inputs are missing, uncertain or outside the reviewed rule coverage; do not infer NOT_APPLICABLE. |
| FR-APP-007 | MUST | Run only versioned rules from the selected content set and expose each rule's source, coverage boundary and review status. Draft rules must be identified as draft. |

### I. Regulatory Requirement Repository

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-REQ-001 | MUST | Maintain structured regulatory requirement records. |
| FR-REQ-002 | MUST | Keep legal source, article/clause, effective date, status, and version references. |
| FR-REQ-003 | MUST | Support active, superseded, transitional, and inactive lifecycle states or equivalents. |
| FR-REQ-004 | MUST | Preserve the requirement version used in historical assessments. |
| FR-REQ-005 | MUST | Record the selected legal content set's source, scope, version, review status, reviewer/role and review date where available; do not present unreviewed material as legally validated. |

### J. Controls

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-CTL-001 | MUST | Maintain a structured security and governance control catalog. |
| FR-CTL-002 | MUST | Support many-to-many requirement ↔ control mappings. |
| FR-CTL-003 | MUST | Define each control's objective, expected implementation, evidence expectations, and assessment criteria. |
| FR-CTL-004 | COULD | Map a control to additional frameworks in a future release. |
| FR-CTL-005 | MUST | Version controls, requirement-control mappings, evidence expectations and assessment criteria, including mapping rationale, so historical results remain interpretable. |

### K. Evidence

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-EVD-001 | MUST | Define expected evidence for assessable controls. |
| FR-EVD-002 | MUST | Let authorized users upload or register evidence. |
| FR-EVD-003 | MUST | Record source, owner, collection time, validity period, and verification state. |
| FR-EVD-004 | MUST | Allow one evidence item to support multiple controls or requirements. |
| FR-EVD-005 | MUST | Track unverified, verified, rejected, and expired states or equivalents. |
| FR-EVD-006 | MUST | Detect expected evidence that has not been provided. |
| FR-EVD-007 | MUST | Retain each evidence revision used by an assessment when evidence is replaced, so historical results still point to the submitted version. |

### L. Assessment

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-ASMT-001 | MUST | Create an assessment for a defined scope and retain its context and versions. |
| FR-ASMT-002 | MUST | Assess controls against explicit criteria, structured answers, available evidence, and approved technical evidence. |
| FR-ASMT-003 | MUST | Support NOT_ASSESSED, SATISFIED, PARTIALLY_SATISFIED, NOT_SATISFIED, NOT_APPLICABLE, and INSUFFICIENT_EVIDENCE or equivalent states. |
| FR-ASMT-004 | MUST | Distinguish a failed control from insufficient evidence; missing backup evidence does not prove backups do not exist. |
| FR-ASMT-005 | MUST | Mark automated rule-based results as preliminary where human review may be needed. |
| FR-ASMT-006 | SHOULD | Permit an authorized reviewer to override a result with justification. |
| FR-ASMT-007 | MUST | Audit any override with old and new results, reviewer, time, and reason. |
| FR-ASMT-008 | MUST | Preserve a reference or snapshot of the facts, questionnaire, rules, requirements, controls, mappings, criteria and evidence versions used for each assessment. Later updates must not rewrite prior results. |

### M. Readiness Gap

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-GAP-001 | MUST | Create readiness gaps from assessment outcomes. |
| FR-GAP-002 | MUST | Distinguish CONTROL_GAP from EVIDENCE_GAP; finer types may follow later. |
| FR-GAP-003 | MUST | Trace each gap to assessment, control, requirement, and relevant evidence or missing evidence. |
| FR-GAP-004 | MUST | Prioritize gaps using transparent criteria, such as deterministic severity and risk rules. |

### N. Remediation

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-REM-001 | MUST | Convert a gap into a remediation task. |
| FR-REM-002 | MUST | Record owner, priority, due date, and status. |
| FR-REM-003 | MUST | Support open, in progress, ready for retest, closed, and accepted risk states or equivalents. |
| FR-REM-004 | MUST | Permit retesting after remediation and new evidence. |
| FR-REM-005 | MUST | Retain prior assessment and remediation history after closure. |
| FR-REM-006 | MUST | Show a curated remediation recommendation for a supported gap, including action, reason and evidence expected at retest; state when no reviewed recommendation exists. |
| FR-REM-007 | MUST | Allow only an authorized role to record risk acceptance with decision maker, time and reason. Accepted risk must not change an unsatisfied control to SATISFIED. |

### O. Reporting

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-RPT-001 | MUST | Generate a readiness report for a selected assessment. |
| FR-RPT-002 | MUST | Include scope, potentially applicable requirements, control results, evidence status, gaps, and remediation items. |
| FR-RPT-003 | SHOULD | Provide a management-oriented executive summary. |
| FR-RPT-004 | MUST | State that the report is a readiness assessment, not definitive legal certification. |
| FR-RPT-005 | MUST | Trace findings to controls, requirements, evidence, and assessment reasoning. |
| FR-RPT-006 | MUST | Disclose the reviewed content set, coverage limits, unresolved/unknown results and whether a human reviewer participated. |

### P. Technical Evidence

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-TECH-001 | MUST | Represent technical evidence sources, such as configurations, logs, API results, Wazuh, Nmap, Greenbone, or scanners. |
| FR-TECH-002 | SHOULD | Permit manual import or registration of technical assessment outputs in v0.1. |
| FR-TECH-003 | COULD | Provide a future integration interface without changing the core assessment model. |

### Q. Audit Trail

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-AUD-001 | MUST | Record significant changes, including evidence, assessment, role, remediation closure, and reviewer override changes. |
| FR-AUD-002 | MUST | Record actor, action, target, timestamp, and old/new values where appropriate. |

## 5. Non-functional requirements

| ID | Requirement |
| --- | --- |
| NFR-SEC-001 | Require authentication and authorization for protected functions. |
| NFR-SEC-002 | Never store passwords, credentials, or tokens in plaintext. |
| NFR-SEC-003 | Support evidence integrity checks, such as cryptographic hashes. |
| NFR-EXP-001 | Make applicability and assessment reasoning inspectable and traceable. |
| NFR-TRC-001 | Preserve regulation → requirement → control → evidence → assessment → gap → remediation traceability. |
| NFR-VRS-001 | Version regulatory rules, requirements, questionnaire context, and assessments. |
| NFR-USA-001 | Use language and workflows SME users can understand without knowing the internal data model. |
| NFR-MNT-001 | Allow regulatory content and control mappings to be maintained without rewriting application source code. |
| NFR-TST-001 | Make applicability and assessment rules testable with fixed inputs and expected outputs. |
| NFR-DEP-001 | Keep prototype deployment lightweight enough for a resource-constrained development environment (approximately 16 GB RAM). |
| NFR-VAL-001 | Support repeatable tests using a synthetic SME and reviewed expected outcomes; record observed results and limitations. |
| NFR-VAL-002 | Make it possible to compare prototype assessment effort and traceability with a manual spreadsheet/document baseline without assuming a performance threshold in advance. |

## 6. Outside prototype v0.1

These are exclusions from the prototype, **not delivery commitments for v0.2+**.

- Multi-tenant SaaS onboarding, billing and a consultant dashboard spanning multiple SME deployments.
- Fully automatic legal interpretation, legal approval or AI compliance decisions.
- Real-time SIEM ingestion, full SOC, XDR/EDR, and automated penetration testing.
- Enterprise-scale discovery and production-scale cloud scanning.
- Automated government submission.
- Full ISO/IEC 27001 certification platform and enterprise GRC replacement.
- Critical-infrastructure or government-system compliance platform.
- Full FDI compliance platform, investment scoring and FDI recommendations.
- Complete AI threat-detection platform, additional framework mappings and automated technical integrations beyond the selected v0.1 examples.

## 7. Core design rules

1. Start with one organization per deployment.
2. Use the questionnaire to collect facts, not legal conclusions.
3. Evaluate applicability with deterministic, versioned rules.
4. Maintain curated requirement-to-control mappings.
5. Base control assessments on explicit criteria and evidence.
6. Treat insufficient evidence separately from a failed control.
7. Permit justified human review and keep an audit trail.
8. Limit AI to assistance; humans and deterministic rules retain decision authority.
9. Expose unknown, unreviewed and out-of-coverage contexts instead of interpreting silence as non-applicability.

## 8. Requirement provenance

The following links show why a **group** exists. They do not claim that each field, status name or interaction detail has been validated with a real SME.

| Requirement group | Basis | Remaining validation |
| --- | --- | --- |
| AUTH, ORG | Single-tenant and RBAC project decisions; Charter §6–8 organization context | Test permissions and onboarding with users. |
| SYS, AST, DATA, VND | Charter §6–8; Problem Discovery §9, §11 | Check data-entry effort and missing-information patterns (H3). |
| QST, APP, REQ | Charter §7–8, §10; Assumptions A-003/A-004/W-003; Hypothesis H1 | Review selected legal pathways, rule inputs and expected outputs. |
| CTL, EVD, ASMT, TECH | Charter §6–8, §10; Problem Discovery §10; W-004/W-005 | Review mapping rationale and distinguish evidence gaps from control failures. |
| GAP, REM, RPT, AUD | Charter §6–8, §12; Problem Discovery §9–11 | Observe task completion, retest and report interpretation. |
| Self-assessment primary, consultant optional | Project decision; H4/A-007 remain unvalidated | Compare self-service and consultant-assisted completion. |

The content reviewer who checks legal sources/rules/mappings is a separate responsibility from the optional consultant who reviews an SME's assessment. The prototype may load a reviewed content set through configuration; a full legal-content approval UI is not required.

## 9. Prototype acceptance and research evaluation

Use the **synthetic** ABC Trading scenario from Problem Discovery §13. Its input facts are test data, not evidence about a real SME. Legal/applicability expected results must be defined and reviewed separately before being used as reference answers.

1. Complete the path from organization context and inventories through questionnaire, applicability, control mapping, evidence, gap, remediation and report.
2. Compare rule results with expected outputs for the selected reviewed scenarios, including a missing-fact and an out-of-coverage case.
3. Trace a finding from requirement to control, expected/provided evidence, assessment reasoning, gap and remediation.
4. Show that missing evidence yields INSUFFICIENT_EVIDENCE/EVIDENCE_GAP while evidence of unmet criteria can yield NOT_SATISFIED/CONTROL_GAP.
5. Repeat an assessment with identical facts and content versions to check consistent outputs; change inputs or versions to check preserved history.
6. Observe time, handoffs and corrections in a manual spreadsheet/document exercise and a prototype exercise. Record method, results and limitations without inventing an accuracy or time-saving target.
7. Test both SME self-service and consultant-assisted use when participants become available; log observed difficulty and revise H4/A-007 only with evidence.

## 10. Open research decisions

- Select and review the first legal content set, its rule coverage and expected outputs. Until this is complete, rule examples remain drafts and cannot support a claim of legally correct applicability.
- Validate whether target SME users can complete the questionnaire and inventory without consultant help (H4, H3).
- Test whether recurring evidence tracking adds value beyond a point-in-time assessment before expanding lifecycle automation (H5/A-008).

## 11. Final v0.1 flow

```text
Installation → Initial setup (organization profile + admin account)
             → Login / RBAC
             → Systems + Assets + Data Processing + Vendors
             → Branching Questionnaire → Structured Context
             → Versioned Applicability Rules
             → Potentially Applicable Requirements + Explanation
             → Curated Controls → Expected Evidence
             → Submitted / Imported Evidence → Preliminary Assessment
             → Optional Consultant Review
             → Control Gaps + Evidence Gaps → Prioritized Remediation
             → New Evidence → Retest / Reassessment
             → Traceable Readiness Report (no legal certification)
```
