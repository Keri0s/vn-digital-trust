# VN Digital Trust — Domain Model v0.1

**Status:** Conceptual model for the v0.1 prototype, 2026-10-03.  
**Inputs:** [Requirements Discovery v0.1](D:/Projects/vn-digital-trust/docs/requirements/requirements-discovery-v0.1.md), [Use Cases v0.1](D:/Projects/vn-digital-trust/docs/use-cases/use-cases-v0.1.md), [Project Charter](D:/Projects/vn-digital-trust/docs/research/project-charter.md), [Assumptions Log](D:/Projects/vn-digital-trust/docs/research/assumptions-log.md).

This is a **business/domain model**, not a database schema. Names, cardinalities and invariants describe what the prototype must remember. SQL tables, APIs and screens come later.

PlantUML views: [organization context](domain-context-v0.1.puml), [curated content](domain-content-v0.1.puml), and [assessment/evidence](domain-assessment-v0.1.puml). The views split one conceptual model into readable parts.

## 1. Boundary and core language

- **Deployment:** one installed instance. It contains exactly one Organization after setup. No company-signup or multi-tenant workspace.
- **Assessment:** a point-in-time evaluation with a defined scope and fixed references to the context, questions, rules, requirements, controls, criteria and evidence used.
- **Content set:** a selected collection of versioned legal references, applicability rules, controls, mappings and guidance. A content set may be draft; only reviewed examples can be labelled reviewed.
- **Potentially applicable:** a rule result based on known context. It is decision support, not a legal determination.
- **Evidence gap:** expected evidence is absent, unverified, rejected or expired. It does not prove that the control has failed.
- **Control gap:** available, valid evidence and explicit criteria support a result that the control is not fully satisfied.
- **Content reviewer:** checks rules and mappings before a content set is used as a reviewed example. This role is distinct from an optional consultant reviewing an SME assessment.

## 2. Conceptual entities

### A. Organization and context

| Entity | Meaning and minimum data | Key relationships | FR / UC |
| --- | --- | --- | --- |
| Organization | The SME configured once; name, industry, size, activities, locations, contacts | Owns users, inventories and assessments | ORG; UC-01/03 |
| User | Individual identity, status and authentication reference; credentials are handled separately | Has roles; appears in audit/review/task records | AUTH; UC-02 |
| RoleAssignment | A user's permission role in this deployment | Joins User and Role | AUTH, AUD; UC-02 |
| InformationSystem | CRM, HRM, website, SaaS or another logical system; purpose, owner, hosting, exposure, criticality | Relates to assets, processing activities and vendors | SYS; UC-03 |
| Asset | Server, endpoint, application, database or cloud resource; type, owner | May support several systems | AST; UC-03 |
| DataAsset | A named data set/category with classification and owner | Used by processing activities | DATA; UC-03 |
| ProcessingActivity | Purpose, role/context, storage, transfer indicator and known/unknown flags | Uses systems and data assets; may involve vendors | DATA; UC-03 |
| Vendor | External provider; service, data access and processing role | May support several systems/activities | VND; UC-03 |

The many-to-many links between systems/assets, activities/data and activities/vendors can be represented by explicit association records when implementation needs metadata such as purpose or effective dates. An unanswered “international transfer?” is **unknown**, not “no”.

### B. Questionnaire and curated knowledge

| Entity | Meaning and minimum data | Key relationships | FR / UC |
| --- | --- | --- | --- |
| QuestionnaireVersion | Immutable version of a question set and branching conditions | Has questions; referenced by an AnswerSet | QST; UC-04 |
| AnswerSet | Answers submitted for one assessment context | Belongs to organization/assessment; has answers | QST, ASMT; UC-04/07 |
| Answer | Question ID, typed value or UNKNOWN, answerer and time | Belongs to AnswerSet | QST; UC-04 |
| ContentSetVersion | Selected content package; ID/version, coverage boundary, draft/reviewed status, review date and role | References versions of rules, requirements, controls and mappings | APP, REQ; UC-12 |
| LegalSourceVersion | Source document identifier, title, effective dates/status and version | Cited by RequirementVersion | REQ; UC-12 |
| RequirementVersion | Stable requirement ID plus immutable version, source article/clause and lifecycle status | Target of rules; maps to controls | REQ; UC-05/12 |
| ApplicabilityRuleVersion | Stable rule ID/version, input fact keys, deterministic predicate, coverage and explanation template | Produces ApplicabilityResult for a requirement | APP; UC-05/12 |
| ControlVersion | Stable control ID/version, objective and expected implementation | Mapped to requirements; has criteria and evidence expectations | CTL; UC-06/07 |
| RequirementControlMappingVersion | Versioned many-to-many link and mapping rationale | Joins RequirementVersion and ControlVersion | CTL; UC-12 |
| AssessmentCriterionVersion | Explicit test for a control; version and expected outcome logic | Belongs to ControlVersion; used by ControlResult | CTL, ASMT; UC-07/12 |
| EvidenceExpectationVersion | Description/type of evidence expected for a control and its criterion | Belongs to ControlVersion; compared with provided evidence | EVD; UC-06/12 |
| RemediationGuidanceVersion | Curated action, reason and expected retest evidence for a supported gap | Referenced by a gap/task where available | REM; UC-09/12 |

Content can be loaded from reviewed configuration or seed data in v0.1. The model does not require an in-app legal editing or approval workflow. A content set with no completed review stays **DRAFT**; its outputs must be labelled accordingly.

### C. Assessment, evidence and follow-up

| Entity | Meaning and minimum data | Key relationships | FR / UC |
| --- | --- | --- | --- |
| Assessment | Scope, time, status, actor and snapshot/reference bundle for context and content versions | Owns applicability and control results | ASMT; UC-05/07/10 |
| ContextSnapshot | The organization, system, asset, data and vendor facts used for a run, including unknown values | Immutable input to Assessment | ORG, APP, ASMT; UC-03/05/07 |
| ApplicabilityResult | RequirementVersion, outcome, triggering facts, rule/version, reasoning and review status | Belongs to Assessment; may connect to control results through mapping | APP; UC-05/08 |
| EvidenceItem | Logical piece of evidence, owner and source type | Has one or more revisions; may support many controls | EVD, TECH; UC-06 |
| EvidenceRevision | Specific submitted file/reference/output, collection time, validity, hash if used, verification state | Immutable version of EvidenceItem | EVD; UC-06/10 |
| EvidenceSupport | Which EvidenceRevision supports which ControlVersion/expectation and why | Many-to-many association; may also capture a direct requirement link where justified | EVD, CTL; UC-06/07 |
| ControlResult | ControlVersion and criterion versions, outcome, reasoning, used evidence revisions, preliminary/reviewed state | Belongs to Assessment; may produce gaps | ASMT; UC-07/08 |
| ReviewDecision | Reviewer, target result, old/new outcome where changed, reason and time | Appended to assessment/applicability/control result history | ASMT, AUD; UC-08 |
| Gap | EVIDENCE_GAP or CONTROL_GAP, priority, reason and references to result and missing/present evidence | May have remediation tasks | GAP; UC-09 |
| RemediationTask | Owner, due date, priority, action, status and retest reference | Belongs to Gap; may cite guidance | REM; UC-09/10 |
| RiskAcceptance | Authorized decision maker, date, reason and scope | Relates to Gap or task; does not alter ControlResult to SATISFIED | REM, AUTH, AUD; UC-09 |
| AuditEvent | Actor, action, target, time, previous/new value where appropriate | References security-relevant changes | AUD; UC-02/06/08/10 |

The same EvidenceRevision can support multiple ControlResults through EvidenceSupport. An Assessment references the **specific** revisions used, so replacing a file later does not change an older report.

## 3. Relationships and cardinality

| Relationship | Cardinality | Rule |
| --- | --- | --- |
| Deployment → Organization | 1 → 1 after setup | No second organization in v0.1. |
| Organization → User / Assessment / inventory records | 1 → many | All operational records belong to the one organization. |
| User ↔ Role | many ↔ many through RoleAssignment | A user may hold more than one role. |
| InformationSystem ↔ Asset | many ↔ many | A shared asset may support several systems. |
| ProcessingActivity ↔ DataAsset / InformationSystem / Vendor | many ↔ many | Relationship records may carry business context. |
| QuestionnaireVersion → AnswerSet → Answer | 1 → many → many | The submitted version and answers stay available. |
| ContentSetVersion → rule / requirement / control / mapping versions | 1 → many references | Referenced versions are fixed for each published set. |
| RequirementVersion ↔ ControlVersion | many ↔ many through RequirementControlMappingVersion | Mapping rationale and version are preserved. |
| Assessment → ContextSnapshot / AnswerSet / ContentSetVersion | 1 → 1 / 1 / 1 | Inputs needed to interpret the run are fixed. |
| Assessment → ApplicabilityResult / ControlResult | 1 → many | A result belongs to one run. |
| EvidenceItem → EvidenceRevision | 1 → many | Revisions are not overwritten. |
| EvidenceRevision ↔ ControlVersion | many ↔ many through EvidenceSupport | One piece of evidence can be reused. |
| ControlResult → Gap | 1 → 0..many | Gap type preserves the distinction between evidence and control. |
| Gap → RemediationTask | 1 → 0..many | A gap may require several actions. |
| Result → ReviewDecision | 1 → 0..many | Each adjustment is appended, not substituted silently. |

## 4. Invariants and state rules

1. **Tenant boundary:** There is only one Organization per deployment. Every operational record is scoped to it, including any invited reviewer account.
2. **No silent inference:** UNKNOWN input or a scenario outside reviewed rule coverage yields NEEDS_REVIEW. NOT_APPLICABLE requires an explicit, justified result.
3. **Evidence is not a questionnaire answer:** An answer can help set context but cannot by itself satisfy a criterion that expects evidence.
4. **Evidence gap versus control gap:** Missing/unverified/rejected/expired required evidence yields INSUFFICIENT_EVIDENCE where the criterion cannot otherwise be decided. Valid evidence of unmet criteria may yield NOT_SATISFIED or PARTIALLY_SATISFIED.
5. **History is stable:** Assessments, results, content versions, evidence revisions and review decisions used by a report remain interpretable after later edits or retests.
6. **Reviewer override:** Only an authorized reviewer may adjust a preliminary result; old outcome, new outcome, reason, actor and time are kept.
   A ReviewDecision targets one ApplicabilityResult **or** one ControlResult, never both.
7. **Risk acceptance:** Authorized management may accept a documented risk. This changes treatment status, not the assessed control outcome.
8. **Reporting boundary:** A report identifies its scope, reviewed/draft content status, unresolved results and reviewer participation; it is not a legal certificate.

### Working state vocabularies

| Object | v0.1 states or outcomes |
| --- | --- |
| ContentSetVersion | DRAFT, REVIEWED, RETIRED |
| ApplicabilityResult | POTENTIALLY_APPLICABLE, NOT_APPLICABLE_WITH_REASON, NEEDS_REVIEW |
| EvidenceRevision verification | UNVERIFIED, VERIFIED, REJECTED, EXPIRED |
| ControlResult | NOT_ASSESSED, SATISFIED, PARTIALLY_SATISFIED, NOT_SATISFIED, NOT_APPLICABLE, INSUFFICIENT_EVIDENCE |
| Gap | OPEN, IN_PROGRESS, READY_FOR_RETEST, CLOSED, ACCEPTED_RISK as treatment status where appropriate |
| RemediationTask | OPEN, IN_PROGRESS, READY_FOR_RETEST, CLOSED, ACCEPTED_RISK |

These labels are provisional. In particular, gap type, gap lifecycle and risk treatment are **separate dimensions** even if an interface presents them together.

## 5. One synthetic walkthrough

Use ABC Trading from Problem Discovery §13 as a **test fixture**, not a case study. It has a CRM, customer data and a CRM SaaS vendor. A user records the CRM as an InformationSystem, customer data as a DataAsset, the relevant ProcessingActivity and the SaaS provider as a Vendor.

The questionnaire creates an AnswerSet. A selected, reviewed **example** ContentSetVersion can evaluate the facts and create an ApplicabilityResult. This document does **not** assign an actual legal requirement to ABC Trading. The expected legal outcome remains open until the sample pathway is reviewed.

For a separate technical-control example, assume the selected content set contains a control criterion requiring MFA configuration evidence. If no usable evidence is submitted, the ControlResult is INSUFFICIENT_EVIDENCE and the Gap is EVIDENCE_GAP. If verified configuration evidence shows MFA is disabled, the control may be NOT_SATISFIED and produce CONTROL_GAP. A new EvidenceRevision and retest create a **new** result while the first assessment remains readable.

## 6. Traceability to current use cases

| UC | Main entities exercised |
| --- | --- |
| UC-01/02 | Organization, User, RoleAssignment, AuditEvent |
| UC-03 | InformationSystem, Asset, DataAsset, ProcessingActivity, Vendor |
| UC-04 | QuestionnaireVersion, AnswerSet, Answer |
| UC-05 | ContextSnapshot, ContentSetVersion, ApplicabilityRuleVersion, RequirementVersion, ApplicabilityResult |
| UC-06 | ControlVersion, EvidenceExpectationVersion, EvidenceItem, EvidenceRevision, EvidenceSupport |
| UC-07/08 | Assessment, AssessmentCriterionVersion, ControlResult, ReviewDecision |
| UC-09/10 | Gap, RemediationGuidanceVersion, RemediationTask, RiskAcceptance, new EvidenceRevision and Assessment |
| UC-11 | Assessment and all referenced result/evidence/content versions |
| UC-12 | ContentSetVersion, LegalSourceVersion, RequirementVersion, ApplicabilityRuleVersion, ControlVersion, mapping/criteria/expectation/guidance versions |

## 7. Decisions before database and architecture

- **Legal sample set:** Select a narrow set of sources and have applicability pathways and expected outputs reviewed. This is required before claiming legally correct results; it does not block modelling or implementation with clearly labelled draft data.
- **Assessment scope:** Decide whether the first demo runs at organization level, system level, processing activity level, or a defined combination. The model preserves a scope field without fixing an SQL design yet.
- **Evidence storage:** Decide whether v0.1 stores files locally or registers references; in either case preserve revision identity and access control.
- **Review workflow:** Decide whether consultant review is exercised in the first demo or only shown as an optional path; no multi-client reviewer dashboard is assumed.
- **Entity refinement:** Translate many-to-many conceptual links into explicit association tables only after choosing the prototype database and queries.

The next modelling artifact should be a **small, reviewed content/rule sample and acceptance fixture** for ABC Trading, followed by architecture v0.1. The research evaluation must still test H1/H3/H4/H5 rather than treating this model as validation.
