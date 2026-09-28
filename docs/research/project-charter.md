# Project Charter

## Project Name

Vietnam Digital Trust & Cybersecurity Readiness

## 1. Background

To be researched.

## 2. Problem Statement

What cybersecurity and digital-trust problems do Vietnamese enterprises
face when demonstrating their readiness to international partners and investors?

## 3. Target Users

- Vietnamese enterprises
- Cybersecurity / IT teams
- Security assessors and consultants
- International partners conducting cybersecurity due diligence

## 4. Project Objectives

The project aims to design and prototype a platform that can:

- Assess cybersecurity readiness
- Map regulatory requirements to security controls
- Collect and manage assessment evidence
- Validate selected controls using technical security data
- Identify security gaps and remediation actions
- Support cybersecurity due-diligence workflows

## 5. Core Concept

Regulation
→ Security Requirement
→ Security Control
→ Evidence
→ Technical Validation
→ Finding
→ Risk
→ Remediation
→ Due Diligence

## 6. Scope

### In Scope

- Cybersecurity readiness
- Vietnamese cybersecurity regulatory requirements
- Security control assessment
- Asset and system inventory
- Evidence management
- Vulnerability management
- Security monitoring
- Incident readiness
- Data security
- Operational resilience
- Supply-chain security
- Enterprise Digital Twin
- SOC/Wazuh integration

### Out of Scope

- Legal certification
- Automatic declaration of legal compliance
- Investment recommendation
- Prediction of FDI
- Production penetration testing without authorization
- Fully autonomous security decision-making

## 7. Research Questions

RQ1:
How can Vietnamese cybersecurity requirements be translated into
measurable security controls?

RQ2:
How can technical security evidence be used to validate those controls?

RQ3:
Can an integrated assessment platform improve evidence traceability
compared with a manual assessment workflow?

RQ4:
How can cybersecurity readiness information support security
due diligence for international partnerships and investment?

## 8. Experimental Approach

A synthetic enterprise environment will be created.

The environment will contain:

- realistic business assets
- users and systems
- security configurations
- vulnerabilities
- security telemetry
- simulated security incidents
- compliance evidence

Technical telemetry may be generated using tools such as:

- Wazuh
- Nmap
- Greenbone/OpenVAS
- Sysmon
- MITRE ATT&CK-based tests

Expected results will be recorded as ground truth and compared with
platform assessment results.

## 9. Success Metrics

Potential metrics include:

- control assessment accuracy
- classification accuracy
- evidence traceability
- false positive rate
- false negative rate
- detection coverage
- assessment time
- remediation verification rate

Exact target values will be determined during experiment design.

## 10. Expected Contribution

The project explores an integrated approach connecting:

Vietnamese regulatory requirements
+
cybersecurity controls
+
technical security evidence
+
enterprise security assessment
+
digital-trust due diligence

The intended contribution is a reproducible prototype and assessment
methodology rather than a legal certification system.

## 11. Current Status

Phase 1 — Problem Definition and Requirements Engineering