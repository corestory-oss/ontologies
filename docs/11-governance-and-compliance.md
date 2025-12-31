# Section 10: Governance and Compliance

This section defines compliance requirements, controls, evidence, and risk assessments.

## Overview

The Governance and Compliance section provides frameworks for ensuring the system meets regulatory requirements, implements appropriate controls, and manages risks.

## Core Concepts

### ComplianceRequirement

**Definition**: A regulatory or policy obligation.

**Purpose**: Documents requirements from compliance frameworks that the system must satisfy.

**Key Attributes**:
- **framework**: Compliance framework (GDPR, HIPAA, SOC2, PCI_DSS, ISO27001, SOX, CCPA, FEDRAMP)
- **controls**: List of `Control` entities implementing this requirement
- **effective_date**: When requirement became effective

**Relationships**:
- **applies_to_systems**: `System` entities that must comply

**Compliance Frameworks**:

#### GDPR (General Data Protection Regulation)
European Union data protection and privacy regulation.
- **Key Requirements**:
  - Lawful basis for processing
  - Data subject rights (access, erasure, portability)
  - Data minimization
  - Privacy by design
  - Breach notification (72 hours)

#### HIPAA (Health Insurance Portability and Accountability Act)
US healthcare data privacy and security regulation.
- **Key Requirements**:
  - Protected Health Information (PHI) safeguards
  - Access controls and audit trails
  - Encryption of PHI
  - Business associate agreements
  - Breach notification

#### SOC 2 (Service Organization Control 2)
Security, availability, and confidentiality framework.
- **Trust Service Criteria**:
  - Security
  - Availability
  - Processing Integrity
  - Confidentiality
  - Privacy

#### PCI-DSS (Payment Card Industry Data Security Standard)
Credit card data security standard.
- **Key Requirements**:
  - Secure network and systems
  - Protect cardholder data
  - Access control measures
  - Network monitoring
  - Security policy

#### ISO 27001
Information security management system standard.
- **Key Requirements**:
  - Risk assessment
  - Security controls (Annex A)
  - Management review
  - Continuous improvement
  - Documentation

#### SOX (Sarbanes-Oxley Act)
US financial reporting and corporate governance regulation.
- **Key Requirements**:
  - Internal controls for financial reporting
  - Audit trails
  - Segregation of duties
  - Change management

#### CCPA (California Consumer Privacy Act)
California consumer privacy regulation.
- **Key Requirements**:
  - Right to know what data is collected
  - Right to delete personal information
  - Right to opt-out of data sale
  - Non-discrimination

#### FedRAMP (Federal Risk and Authorization Management Program)
US federal cloud security program.
- **Key Requirements**:
  - Security controls (based on NIST 800-53)
  - Continuous monitoring
  - Annual assessment
  - Incident response

---

### Control

**Definition**: A measure implementing a compliance requirement.

**Purpose**: Specific security or compliance controls implemented to satisfy requirements.

**Key Attributes**:
- **control_id**: Identifier (e.g., SOC2-CC6.1, ISO27001-A.9.2.1)
- **implementation**: How control is implemented
- **evidence**: List of `Evidence` entities demonstrating effectiveness
- **frequency**: Assessment frequency (daily, monthly, quarterly, annual)

**Relationships**:
- **owned_by_actor**: `Actor` responsible for this control
- **mitigates_risks**: `RiskAssessment` entities mitigated

**Control Types**:

#### Preventive Controls
Prevent security incidents from occurring.
- Examples: Access controls, encryption, firewalls, input validation

#### Detective Controls
Detect security incidents after they occur.
- Examples: Logging, monitoring, intrusion detection, audits

#### Corrective Controls
Correct issues after detection.
- Examples: Incident response, patching, backups, recovery procedures

#### Administrative Controls
Policies, procedures, and training.
- Examples: Security policies, training programs, background checks

#### Technical Controls
Technology-based controls.
- Examples: Encryption, authentication, firewalls, antivirus

#### Physical Controls
Physical security measures.
- Examples: Locks, badges, surveillance, environmental controls

**Example Controls**:

**SOC2 CC6.1 - Logical Access**:
- Control: Multi-factor authentication required for all administrative access
- Implementation: Enforce MFA via identity provider for admin roles
- Evidence: MFA enrollment reports, access logs showing MFA verification
- Frequency: Quarterly review

**PCI-DSS 3.4 - Encryption of Cardholder Data**:
- Control: Encrypt cardholder data at rest using AES-256
- Implementation: Database-level encryption for payment_methods table
- Evidence: Encryption configuration, key management logs
- Frequency: Annual audit

**GDPR Article 32 - Security of Processing**:
- Control: Encryption of personal data in transit
- Implementation: TLS 1.3 for all API endpoints
- Evidence: SSL/TLS scan reports, certificate management logs
- Frequency: Monthly scans

---

### Evidence

**Definition**: Proof that a control is operating effectively.

**Purpose**: Demonstrates to auditors that controls are implemented and effective.

**Key Attributes**:
- **evidence_type**: Type of evidence (screenshot, log export, test result, policy document)
- **collected_at**: Collection timestamp
- **artifact_uri**: Location of evidence artifact

**Relationships**:
- **verified_by_actor**: `Actor` who verified the evidence

**Types of Evidence**:

#### Screenshots
Visual proof of configurations or settings.
- Examples: Security group rules, MFA settings, encryption enabled

#### Log Exports
Extracted log files demonstrating control operation.
- Examples: Access logs, authentication logs, change logs

#### Test Results
Results from automated or manual testing.
- Examples: Vulnerability scans, penetration tests, security assessments

#### Policy Documents
Written policies and procedures.
- Examples: Security policy, incident response plan, acceptable use policy

#### Attestations
Signed statements from responsible parties.
- Examples: Background check confirmations, training completion certificates

#### Automated Reports
Reports from security tools and systems.
- Examples: SIEM reports, compliance dashboards, configuration baselines

**Evidence Best Practices**:
1. **Automated Collection**: Automate evidence collection when possible
2. **Timestamping**: Timestamp all evidence
3. **Integrity**: Protect evidence from tampering
4. **Retention**: Retain evidence per compliance requirements
5. **Accessibility**: Make evidence accessible for audits

---

### RiskAssessment

**Definition**: An evaluation of threats and vulnerabilities.

**Purpose**: Identify, analyze, and prioritize risks to the system.

**Key Attributes**:
- **assessed_at**: Assessment date
- **risk_level**: Overall risk level (Low, Medium, High, Critical)
- **threats**: List of identified threats
- **vulnerabilities**: List of identified vulnerabilities
- **residual_risk**: Remaining risk after mitigations

**Relationships**:
- **mitigated_by_controls**: `Control` entities mitigating risks
- **assesses_system**: `System` being assessed

**Risk Assessment Process**:

1. **Asset Identification**
   Identify assets to protect (data, systems, services)

2. **Threat Identification**
   Identify potential threats
   - Internal threats (malicious insiders, human error)
   - External threats (hackers, malware, DDoS)
   - Environmental threats (natural disasters, power outages)

3. **Vulnerability Identification**
   Identify weaknesses that threats could exploit
   - Software vulnerabilities
   - Misconfigurations
   - Weak access controls
   - Social engineering susceptibility

4. **Risk Analysis**
   Assess likelihood and impact of each risk
   - **Likelihood**: Probability of occurrence (Rare, Unlikely, Possible, Likely, Almost Certain)
   - **Impact**: Consequences if realized (Insignificant, Minor, Moderate, Major, Catastrophic)
   - **Risk Level**: Likelihood × Impact

5. **Risk Evaluation**
   Determine which risks require treatment
   - **Accept**: Accept low risks
   - **Mitigate**: Implement controls to reduce risk
   - **Transfer**: Transfer risk (insurance, outsourcing)
   - **Avoid**: Eliminate risk-causing activities

6. **Control Implementation**
   Implement controls to mitigate risks

7. **Residual Risk Assessment**
   Assess remaining risk after controls

8. **Documentation**
   Document assessment, decisions, and controls

**Risk Matrix Example**:
```
Impact →
  Catastrophic: L, M, H, C, C
  Major:        L, M, H, H, C
  Moderate:     L, M, M, H, H
  Minor:        L, L, M, M, H
  Insignificant:L, L, L, M, M

                ↑ Likelihood
                Rare, Unlikely, Possible, Likely, Almost Certain

L = Low risk
M = Medium risk
H = High risk
C = Critical risk
```

**Example Risk Assessment**:

**Risk**: Unauthorized access to customer PII
- **Threat**: External attacker exploiting weak authentication
- **Vulnerability**: Single-factor authentication for user accounts
- **Likelihood**: Likely (attacks are common)
- **Impact**: Major (data breach, regulatory fines, reputation damage)
- **Risk Level**: HIGH
- **Controls**:
  - Implement multi-factor authentication
  - Enforce strong password policy
  - Monitor for suspicious login attempts
  - Encrypt PII at rest and in transit
- **Residual Risk**: MEDIUM (controls reduce but don't eliminate risk)

---

## Governance Framework

### Policy Hierarchy
1. **Policies**: High-level statements (Security Policy, Privacy Policy)
2. **Standards**: Specific requirements (Password Standard, Encryption Standard)
3. **Procedures**: Step-by-step instructions (Incident Response Procedure)
4. **Guidelines**: Recommendations and best practices

### Roles and Responsibilities
- **Chief Information Security Officer (CISO)**: Overall security responsibility
- **Data Protection Officer (DPO)**: Privacy and data protection
- **Compliance Officer**: Regulatory compliance
- **Control Owners**: Responsible for specific controls
- **Auditors**: Independent verification

### Governance Processes
- **Risk Management**: Ongoing risk assessment and treatment
- **Compliance Management**: Track and demonstrate compliance
- **Audit Management**: Coordinate and respond to audits
- **Incident Management**: Handle security incidents
- **Change Management**: Control changes to systems and controls

---

## Best Practices

### Compliance
1. **Framework Mapping**: Map requirements to controls
2. **Continuous Monitoring**: Monitor controls continuously
3. **Regular Audits**: Conduct internal audits
4. **Evidence Collection**: Automate evidence collection
5. **Gap Analysis**: Identify and address gaps

### Control Implementation
1. **Defense in Depth**: Layer multiple controls
2. **Automation**: Automate controls when possible
3. **Testing**: Regularly test control effectiveness
4. **Documentation**: Document all controls
5. **Ownership**: Assign clear ownership

### Risk Management
1. **Regular Assessments**: Conduct risk assessments regularly
2. **Threat Intelligence**: Monitor emerging threats
3. **Vulnerability Management**: Scan and remediate vulnerabilities
4. **Risk Register**: Maintain centralized risk register
5. **Treatment Plans**: Document risk treatment decisions

### Audit Readiness
1. **Continuous Evidence**: Collect evidence continuously
2. **Documentation**: Maintain complete documentation
3. **Mock Audits**: Conduct internal mock audits
4. **Remediation**: Address findings promptly
5. **Collaboration**: Work cooperatively with auditors

---

## Relationships with Other Sections

- **Section 1 (Structural Foundation)**: Systems must comply with requirements
- **Section 2 (Actors and Identity)**: Controls owned by actors
- **Section 3 (Authorization)**: Access controls implement security requirements
- **Section 6 (Data Management)**: Data classification and retention for compliance
- **Section 9 (Observability)**: Audit logs provide evidence

---

## Example: GDPR Compliance

```
ComplianceRequirement: GDPR Article 32 - Security of Processing
  Framework: GDPR
  Effective Date: 2018-05-25

  Controls:
    Control: Encryption of Personal Data
      ID: GDPR-32-ENC
      Implementation: AES-256 encryption for PII at rest, TLS 1.3 in transit
      Owner: CISO
      Evidence:
        - Database encryption configuration screenshot
        - SSL/TLS scan report (monthly)
        - Key management audit log
      Frequency: Monthly

    Control: Access Control to Personal Data
      ID: GDPR-32-AC
      Implementation: RBAC with least privilege, MFA for admin access
      Owner: Identity Team Lead
      Evidence:
        - Role definitions and assignments
        - MFA enforcement report
        - Access review logs (quarterly)
      Frequency: Quarterly

    Control: Regular Security Testing
      ID: GDPR-32-TEST
      Implementation: Quarterly penetration testing, monthly vulnerability scans
      Owner: Security Team Lead
      Evidence:
        - Penetration test reports
        - Vulnerability scan results
        - Remediation tracking
      Frequency: Quarterly (pen test), Monthly (vuln scan)

RiskAssessment: GDPR Data Breach Risk
  Assessed At: 2024-01-15
  Risk Level: MEDIUM

  Threats:
    - External attacker targeting customer PII
    - Insider threat (malicious employee)
    - Accidental data exposure (misconfiguration)

  Vulnerabilities:
    - Public S3 buckets (historical issue)
    - Insufficient logging of PII access

  Controls:
    - GDPR-32-ENC (Encryption)
    - GDPR-32-AC (Access Control)
    - GDPR-32-TEST (Security Testing)
    - Automated S3 bucket policy enforcement
    - SIEM monitoring for PII access

  Residual Risk: LOW

  Risk Treatment:
    - Accept residual risk
    - Review quarterly
    - Cyber insurance policy covers data breach costs
```
