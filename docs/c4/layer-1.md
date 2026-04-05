# Layer 1: System Context Representation

This document defines the SAO v2.0 classes that correspond to **C4 Level 1 (System Context)** -- the outermost zoom level, where the system is viewed as a black box. Layer 1 answers the big-picture questions: what is this system, who uses it (actors), what sits outside it (external systems), and how is it governed (compliance and risk).

Where Layer 2 answers "what containers and services make up the system?", Layer 1 answers "what is the system, who interacts with it, and what rules constrain it?"

---

## Scope

Layer 1 covers:

- **The system itself** -- the top-level named entity representing the software product, platform, or application
- **Actors and identity** -- human users, automated agents, their verified identities, credentials, and organizational membership
- **Multi-tenancy** -- tenant boundaries for systems that serve multiple isolated customer populations
- **External systems** -- third-party services, partner systems, legacy systems, and SaaS applications outside the system boundary
- **Compliance and governance** -- regulatory obligations, controls implementing those obligations, evidence of control effectiveness, and risk assessments

Layer 1 is **paradigm-agnostic**. These concepts apply equally to a legacy mainframe CICS system, a monolithic Java EE application, and a modern cloud-native microservices platform. Every software system has actors who use it, external systems it depends on, and governance constraints it must satisfy. The differences in how these concepts are realized emerge at Layer 2 (containers) and below.

---

## Summary

| # | Class | Definition | Group | SAO Section |
|---|---|---|---|---|
| 1 | System | Top-level container representing a software product, platform, or application | System | 1 |
| 2 | Actor (abstract) | Any entity that can initiate actions -- base class for HumanActor and SystemActor | Actors & Identity | 2 |
| 3 | HumanActor | A human user of the system | Actors & Identity | 2 |
| 4 | SystemActor | A system or automated actor | Actors & Identity | 2 |
| 5 | Identity | A verified representation of an actor | Actors & Identity | 2 |
| 6 | Credential | Authentication material proving an identity claim | Actors & Identity | 2 |
| 7 | Organization | A logical grouping of users and resources within a tenant | Actors & Identity | 2 |
| 8 | Tenant | An organizational boundary for multi-tenant systems | Multi-tenancy | 2 |
| 9 | ExternalSystem | A system outside this system's boundary | External Systems | 7 |
| 10 | ComplianceRequirement | A regulatory or policy obligation | Compliance & Governance | 10 |
| 11 | Control | A measure implementing a compliance requirement | Compliance & Governance | 10 |
| 12 | Evidence | Proof that a control is operating effectively | Compliance & Governance | 10 |
| 13 | RiskAssessment | An evaluation of threats and vulnerabilities | Compliance & Governance | 10 |

**Total: 13 classes** (including 2 subtypes: HumanActor and SystemActor that inherit from the abstract Actor).

---

## Connections to Adjacent Layers

### Downward links to Layer 2 (Container)

These relationships connect Layer 1 concepts to the internal structure of the system:

| Layer 1 class | Attribute | Layer 2 class | Description |
|---|---|---|---|
| System | `contains_bounded_contexts` | BoundedContext | Bounded contexts within this system |
| System | `has_integrations` | Integration | Integration connections owned by this system |
| System | `exposes_interfaces` | Interface | Interfaces the system exposes to the outside world |
| Identity | `belongs_to_tenant` | Tenant | Tenant an identity belongs to (Tenant links further down) |
| Tenant | `settings` | Configuration | Tenant-specific configuration values |
| ExternalSystem | `integrated_via` | Integration | Integrations connecting to this external system |

### Cross-layer links to Layer 3 (Component)

These relationships connect Layer 1 concepts to component-level and behavioral abstractions:

| Layer 1 class | Attribute | Layer 3 class | Description |
|---|---|---|---|
| System | `enforces_policies` | Policy | Authorization policies enforced at the system level |
| Actor | `performs_actions` | Action | Actions initiated by this actor |
| Identity | `has_roles` | Role | Roles assigned to this identity |
| Actor | `actor_subscriptions` | Subscription | Event subscriptions registered by this actor |

---

## System (1 class)

### 1. System

Top-level container representing a software product, platform, or application. This is the root node of the entire SAO model -- everything else is contained within or connected to a System.

**Mixins:** `Versionable` (adds `version`, `effective_from`, `effective_to`, `is_current`)

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `version` | SemanticVersion | No | Semantic version (from Versionable) |
| `effective_from` | Timestamp | No | Version start date (from Versionable) |
| `effective_to` | Timestamp | No | Version end date (from Versionable) |
| `is_current` | boolean | No | Whether this is the current version (from Versionable) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contains_bounded_contexts` | BoundedContext | Yes | `contained_in_system` | Bounded contexts within this system (Layer 2) |
| `has_integrations` | Integration | Yes | `belongs_to_system` | Integration connections (Layer 2) |
| `enforces_policies` | Policy | Yes | `enforced_by_system` | Authorization policies enforced (Layer 3) |
| `must_comply_with` | ComplianceRequirement | Yes | `applies_to_systems` | Compliance obligations |
| `assessed_by` | RiskAssessment | Yes | `assesses_system` | Risk assessments performed |
| `exposes_interfaces` | Interface | Yes | `exposed_by_system` | Interfaces exposed to external consumers (Layer 2) |

---

## Actors & Identity (6 classes)

### 2. Actor (abstract)

Any entity that can initiate actions. This is the abstract base class for HumanActor and SystemActor -- it is never instantiated directly. Actors have identities, perform actions, own controls, and subscribe to events.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `category` | ActorCategory | No | `human` or `system` |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `has_identities` | Identity | Yes | `represents_actor` | Verified identities for this actor |
| `performs_actions` | Action | Yes | `performed_by_actor` | Actions initiated (Layer 3) |
| `audit_actions_performed` | AuditEntry | Yes | `audit_performed_by_actor` | Audit trail of actions |
| `actor_subscriptions` | Subscription | Yes | `subscribed_by_actor` | Event subscriptions (Layer 3) |
| `owns_controls` | Control | Yes | `owned_by_actor` | Compliance controls owned |
| `verifies_evidence` | Evidence | Yes | `verified_by_actor` | Evidence verified by this actor |

**ActorCategory Enum:**

| Value | Description |
|---|---|
| `human` | A human user |
| `system` | An automated system or agent |

---

### 3. HumanActor

A human user of the system. Inherits all attributes and relationships from Actor.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `actor_type` | HumanActorType | No | Specific type of human actor |
| `email` | string | No | Email address |

**Relationships:**

*Inherits all relationships from Actor.*

**HumanActorType Enum:**

| Value | Description |
|---|---|
| `end_user` | Regular end user |
| `administrator` | System administrator |
| `operator` | Operations staff |
| `developer` | Software developer |
| `auditor` | Compliance or security auditor |

---

### 4. SystemActor

A system or automated actor. Inherits all attributes and relationships from Actor.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `actor_type` | SystemActorType | No | Specific type of system actor |
| `service_account` | string | No | Service account identifier |

**Relationships:**

*Inherits all relationships from Actor.*

**SystemActorType Enum:**

| Value | Description |
|---|---|
| `internal_service` | An internal service within the system |
| `external_system` | An external system acting as a client |
| `scheduled_process` | A cron job or scheduled task |
| `ai_agent` | An AI/ML agent or bot |
| `message_trigger` | A message-driven trigger |

---

### 5. Identity

A verified representation of an actor. An actor may have multiple identities (e.g., one per tenant, one per authentication provider). Identities hold credentials, are assigned roles, and belong to tenants and organizations.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `identity_type` | string | No | Freeform identity type label |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `credentials` | Credential | Yes | -- | Authentication credentials (inline) |
| `has_roles` | Role | Yes | `assigned_to_identities` | Roles assigned to this identity (Layer 3) |
| `belongs_to_tenant` | Tenant | No | `contains_identities` | Tenant this identity belongs to |
| `member_of_organizations` | Organization | Yes | `has_identity_members` | Organizations this identity is a member of |
| `represents_actor` | Actor | No | `has_identities` | Actor this identity represents |

---

### 6. Credential

Authentication material proving an identity claim. Credentials are inlined within Identity (not standalone top-level entities).

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `credential_type` | CredentialType | No | Type of credential |
| `expires_at` | Timestamp | No | Expiration timestamp |
| `is_active` | boolean | No | Whether the credential is currently active |

**Relationships:**

*No outgoing relationships. Credentials are inlined within Identity via `credentials`.*

**CredentialType Enum:**

| Value | Description |
|---|---|
| `password` | Password-based authentication |
| `token` | Token-based authentication (JWT, bearer token) |
| `certificate` | Digital certificate or X.509 certificate |
| `api_key` | API key |
| `biometric` | Biometric authentication |
| `mfa` | Multi-factor authentication |
| `oauth` | OAuth 2.0 authentication flow |

---

### 7. Organization

A logical grouping of users and resources within a tenant. Organizations can form hierarchies via parent/child relationships.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `parent` | Organization | No | -- | Parent organization in the hierarchy |
| `children` | Organization | Yes | -- | Child organizations |
| `has_identity_members` | Identity | Yes | `member_of_organizations` | Identities belonging to this organization |

---

## Multi-tenancy (1 class)

### 8. Tenant

An organizational boundary for multi-tenant systems. Tenants contain organizations, identities, and tenant-specific configuration.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `organizations` | Organization | Yes | -- | Organizations within this tenant (inline) |
| `settings` | Configuration | Yes | -- | Tenant-specific configuration (Layer 2) |
| `contains_identities` | Identity | Yes | `belongs_to_tenant` | Identities scoped to this tenant |

---

## External Systems (1 class)

### 9. ExternalSystem

A system outside this system's boundary. External systems are integrated via Integration objects and classified by type.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `system_type` | ExternalSystemType | No | Category of external system |
| `owner` | string | No | Team or organization that owns the external system |
| `sla` | string | No | Service level agreement description |
| `documentation_url` | URI | No | Link to external system documentation |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `integrated_via` | Integration | Yes | `integrates_with_system` | Integrations connecting to this system (Layer 2) |

**ExternalSystemType Enum:**

| Value | Description |
|---|---|
| `third_party_service` | Third-party service (Stripe, Twilio, etc.) |
| `partner_system` | Partner or affiliate system |
| `legacy_system` | Legacy system being integrated |
| `saas_application` | SaaS application |

---

## Compliance & Governance (4 classes)

### 10. ComplianceRequirement

A regulatory or policy obligation that the system must satisfy. Requirements reference a compliance framework, contain controls, and apply to one or more systems.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `framework` | ComplianceFramework | No | Compliance framework this requirement belongs to |
| `effective_date` | Timestamp | No | Date the requirement takes effect |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `controls` | Control | Yes | -- | Controls implementing this requirement (inline) |
| `applies_to_systems` | System | Yes | `must_comply_with` | Systems subject to this requirement |

**ComplianceFramework Enum:**

| Value | Description |
|---|---|
| `gdpr` | General Data Protection Regulation (EU) |
| `hipaa` | Health Insurance Portability and Accountability Act |
| `soc2` | SOC 2 Trust Services Criteria |
| `pci_dss` | Payment Card Industry Data Security Standard |
| `iso27001` | ISO/IEC 27001 Information Security Management |
| `sox` | Sarbanes-Oxley Act |
| `ccpa` | California Consumer Privacy Act |
| `fedramp` | Federal Risk and Authorization Management Program |

---

### 11. Control

A measure implementing a compliance requirement. Controls are owned by actors, produce evidence, and mitigate risks.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `control_id` | string | No | External control identifier (e.g., "SOC2-CC6.1") |
| `implementation` | string | No | Description of how the control is implemented |
| `frequency` | string | No | How often the control is executed (e.g., "daily", "continuous") |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `evidence` | Evidence | Yes | -- | Evidence proving this control works (inline) |
| `owned_by_actor` | Actor | No | `owns_controls` | Actor responsible for this control |
| `mitigates_risks` | RiskAssessment | Yes | `mitigated_by_controls` | Risk assessments this control mitigates |

---

### 12. Evidence

Proof that a control is operating effectively. Evidence is collected at a point in time, references an artifact, and may be verified by an actor.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `evidence_type` | string | No | Freeform type of evidence (e.g., "log export", "screenshot", "report") |
| `collected_at` | Timestamp | No | When the evidence was collected |
| `artifact_uri` | URI | No | URI to the evidence artifact |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `verified_by_actor` | Actor | No | `verifies_evidence` | Actor who verified this evidence |

---

### 13. RiskAssessment

An evaluation of threats and vulnerabilities affecting the system. Risk assessments are linked to the system they evaluate and the controls that mitigate identified risks.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique identifier (from NamedEntity) |
| `name` | string | **Yes** | Human-readable name (from NamedEntity) |
| `description` | string | No | Free-text description (from NamedEntity) |
| `tags` | string[] | No | Freeform tags (from NamedEntity) |
| `metadata` | Metadata | No | Created/updated timestamps and version (from NamedEntity, inline) |
| `assessed_at` | Timestamp | No | When the assessment was performed |
| `risk_level` | string | No | Overall risk level (e.g., "low", "medium", "high", "critical") |
| `threats` | string[] | No | Identified threats |
| `vulnerabilities` | string[] | No | Identified vulnerabilities |
| `residual_risk` | string | No | Risk remaining after controls are applied |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `mitigated_by_controls` | Control | Yes | `mitigates_risks` | Controls that reduce this risk |
| `assesses_system` | System | No | `assessed_by` | System being assessed |

---

## Relationship Map

```
                        ┌──────────────────────────────────────────────┐
                        │  Layer 2 (Container)                         │
                        │  BoundedContext, Integration, Interface,      │
                        │  Module, Service, Configuration, ...         │
                        └────────────────────▲─────────────────────────┘
                                             │
              contains_bounded_contexts, has_integrations,
              exposes_interfaces, settings, integrated_via
                                             │
┌─────────────────────────────────────────────┼────────────────────────────────┐
│                          SYSTEM             │                                │
│                                             │                                │
│                        ┌────────────────────┴──┐                             │
│                        │       System          │                             │
│                        │  (Versionable)        │                             │
│                        └──┬───┬───┬───┬───┬────┘                             │
│       must_comply_with    │   │   │   │   │  assessed_by                     │
│              ┌────────────┘   │   │   │   └──────────────┐                   │
│              ▼                │   │   │                   ▼                   │
│  ┌───────────────────┐       │   │   │       ┌───────────────────┐           │
│  │ ComplianceRequirement│    │   │   │       │  RiskAssessment   │           │
│  │   (framework)     │       │   │   │       │  (risk_level)     │           │
│  │        │          │       │   │   │       │        │          │           │
│  │  controls▼        │       │   │   │       └────────┼──────────┘           │
│  │   Control         │       │   │   │    mitigated_by_controls              │
│  │     │  │          │       │   │   │                │                      │
│  │  evidence│ owned_by│      │   │   │    ◄───────────┘                      │
│  │     ▼  │  _actor  │      │   │   │                                        │
│  │  Evidence  │      │       │   │   │                                        │
│  │     │      │      │       │   │   │                                        │
│  └─────┼──────┼──────┘       │   │   │                                        │
│  verified_by  │              │   │   │                                        │
│  _actor │     │              │   │   │  enforces_policies ──► Policy (L3)     │
│         ▼     ▼              │   │   │                                        │
│  ┌──────────────────────┐    │   │   │                                        │
│  │      ACTORS          │◄───┘   │   │                                        │
│  │                      │        │   │                                        │
│  │  Actor (abstract)    │        │   │                                        │
│  │    ├── HumanActor    │        │   │                                        │
│  │    └── SystemActor   │        │   │                                        │
│  │         │            │        │   │                                        │
│  │   has_identities     │        │   │                                        │
│  │         ▼            │        │   │                                        │
│  │      Identity ───────┼── has_roles ──► Role (L3)                          │
│  │         │    │       │        │   │                                        │
│  │  credentials │       │        │   │                                        │
│  │         ▼    │       │        │   │                                        │
│  │    Credential│       │        │   │                                        │
│  │              │ belongs_to_tenant                                           │
│  │              │       │        │   │                                        │
│  │              ▼       │        │   │                                        │
│  │           Tenant ────┼── settings ──► Configuration (L2)                  │
│  │              │       │        │   │                                        │
│  │        organizations │        │   │                                        │
│  │              ▼       │        │   │                                        │
│  │         Organization │        │   │                                        │
│  │          (hierarchy) │        │   │                                        │
│  └──────────────────────┘        │   │                                        │
│                                  │   │                                        │
│  ┌──────────────────────┐        │   │                                        │
│  │   ExternalSystem     │◄───────┘   │                                        │
│  │   (system_type,      │            │                                        │
│  │    owner, sla)       │────── integrated_via ──► Integration (L2)          │
│  └──────────────────────┘            │                                        │
│                                      │                                        │
│  performs_actions ──► Action (L3)     │                                        │
│  actor_subscriptions ──► Subscription (L3)                                   │
└──────────────────────────────────────────────────────────────────────────────┘
                                       │
                    enforces_policies, has_roles, performs_actions,
                    actor_subscriptions, ...
                                       │
                        ┌──────────────▼────────────────────────┐
                        │  Layer 3 (Component)                   │
                        │  Policy, Role, Action, Subscription,   │
                        │  Component, Aggregate, Workflow, ...   │
                        └───────────────────────────────────────┘
```
