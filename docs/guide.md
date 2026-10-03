# Systems Abstraction Ontology: A Guide

**Author:** Charath Ranganathan  
**CoreStory, Inc.**  
Version 1.0.0 · April 2026  
147 classes · 102 enums · 970 attributes · 214 bidirectional relationships  
LinkML Schema · Apache 2.0 License

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. SAO at a Glance](#2-sao-at-a-glance)
- [3. The Six Conceptual Layers](#3-the-six-conceptual-layers)
- [4. Layer 3: Code Structure — The Foundation](#4-layer-3-code-structure-the-foundation)
  - [4.1 The Core Containment Hierarchy](#41-the-core-containment-hierarchy)
  - [4.2 Behavioral Edges](#42-behavioral-edges)
  - [4.3 Internal Code Structure](#43-internal-code-structure)
  - [4.4 Platform-Specific Extensions (Sections 18–28)](#44-platform-specific-extensions-sections-1828)
- [5. Layer 4: Architecture & Integration — The System Map](#5-layer-4-architecture-integration-the-system-map)
  - [5.1 The Architectural Containment Hierarchy](#51-the-architectural-containment-hierarchy)
  - [5.2 Services and Interfaces](#52-services-and-interfaces)
  - [5.3 Integration Cluster](#53-integration-cluster)
- [6. Layer 5: Domain Model — The Business Entities](#6-layer-5-domain-model-the-business-entities)
  - [6.1 Aggregates, Entities, and Value Objects](#61-aggregates-entities-and-value-objects)
  - [6.2 Lifecycle and State Machines](#62-lifecycle-and-state-machines)
  - [6.3 Data Persistence Layer (Section 6)](#63-data-persistence-layer-section-6)
- [7. Layer 6: Business Intent — Behavior, Rules, and Purpose](#7-layer-6-business-intent-behavior-rules-and-purpose)
  - [7.1 Actors (Section 2)](#71-actors-section-2)
  - [7.2 Behavior (Section 5)](#72-behavior-section-5)
  - [7.3 Rules](#73-rules)
  - [7.4 Events](#74-events)
  - [7.5 Capability and Feature](#75-capability-and-feature)
- [8. Cross-Cutting Concerns](#8-cross-cutting-concerns)
  - [8.1 Authorization and Policy (Section 3)](#81-authorization-and-policy-section-3)
  - [8.2 Deployment and Operations (Section 8)](#82-deployment-and-operations-section-8)
  - [8.3 Observability (Section 9)](#83-observability-section-9)
  - [8.4 Governance and Compliance (Section 10)](#84-governance-and-compliance-section-10)
  - [8.5 Testing (Section 11)](#85-testing-section-11)
  - [8.6 UI/Frontend (Section 12)](#86-uifrontend-section-12)
  - [8.7 Build, CI/CD, and Dependencies (Sections 13–14)](#87-build-cicd-and-dependencies-sections-1314)
  - [8.8 Advanced Sections (15–17)](#88-advanced-sections-1517)
  - [8.9 Knowledge Artifacts (Section 30)](#89-knowledge-artifacts-section-30)
- [9. Section Index](#9-section-index)
- [10. The Glue: Bidirectional Relationships](#10-the-glue-bidirectional-relationships)
  - [10.1 Key Cross-Layer Bridges](#101-key-cross-layer-bridges)
- [11. Base Classes and Mixins](#11-base-classes-and-mixins)
- [12. Reading the SAO Effectively](#12-reading-the-sao-effectively)
- [Appendix A: Complete Class Inventory (147 classes)](#appendix-a-complete-class-inventory-147-classes)
- [Appendix B: Complete Enumeration Reference (102 enums)](#appendix-b-complete-enumeration-reference-102-enums)
- [Appendix C: Complete Bidirectional Relationship Pairs (226 rows)](#appendix-c-complete-bidirectional-relationship-pairs-226-rows)

---

## 1. Introduction

The Systems Abstraction Ontology (SAO) is a LinkML schema that provides a comprehensive, language-agnostic framework for modeling software systems. It covers everything from individual lines of code to business capabilities, from COBOL copybooks to Kubernetes deployments, from database constraints to compliance requirements.

This guide explains the SAO by organizing its 147 classes into six conceptual layers, ordered by abstraction. The lowest layers describe what a code parser can directly extract. The highest layers describe what the system means to the business. The layers in between bridge the two.

> **Why layers?** When CoreStory ingests a codebase, the parser fills the lower layers directly from source code. Higher layers are populated through inference — recognizing that a COBOL group item named `CUST-MSTR-REC` with a primary key and CRUD operations is a Customer domain entity. Understanding which classes live at which layer tells you what's extracted vs. what's inferred, and how confident you can be in each.

---

## 2. SAO at a Glance

| Metric | Count | Notes |
|---|---|---|
| Classes (total) | 147 | 6 abstract, 2 mixins, 139 concrete |
| Enumerations | 102 | With 804 permissible values |
| Attributes | 970 | Across all classes |
| Bidirectional relationships | 214 pairs | Every relationship has an explicit inverse |
| Global slots | 20 | Cross-domain relationship slots |
| Sections | 30 | Numbered thematic groupings |

---

## 3. The Six Conceptual Layers

The SAO's 147 classes organize into six layers of ascending abstraction, plus cross-cutting concerns that attach at every level.

| Layer | Abstraction | Key classes | How it is derived |
|---|---|---|---|
| 6 | Business intent | Capability, Feature, Actor, Workflow, Rule, Lifecycle | LLM inference + human validation |
| 5 | Domain model | Aggregate, DomainEntity, ValueObject, DomainRelationship | Pattern recognition + LLM |
| 4 | Architecture | System, BoundedContext, Module, Component, Service, Integration | Graph algorithms + package manifests |
| 3 | Code structure | CodeContainer, EncapsulationUnit, CallableUnit, DataStructure | Direct parsing (deterministic) |
| 2 | Runtime & ops | Deployment, Environment, Infrastructure, Metric, Trace, Alert | Config parsing + runtime telemetry |
| 1 | Cross-cutting | Identity, Role, Permission, Policy, TestSuite, KnowledgeArtifact | Mixed: parsing + inference |

Each layer consumes the outputs of the layer below it. Layer 3 is the foundation — everything else depends on it. The key insight is that layers 3 and 4 are largely structural (you can derive them from code organization and dependency graphs), while layers 5 and 6 require semantic understanding (recognizing business meaning in code patterns).

---

## 4. Layer 3: Code Structure — The Foundation

When CoreStory ingests a codebase, these are the classes populated directly from parsing source files. No inference is needed — this layer is a structured representation of what the code literally says.

### 4.1 The Core Containment Hierarchy

The code structure is modeled as a four-level containment hierarchy: **StorageLocation** (a directory or PDS library) contains **CodeContainers** (source files), which contain **EncapsulationUnits** (classes, COBOL programs, Rust modules), which contain **CallableUnits** (methods, functions, paragraphs) and **DataStructures** (structs, records, group items), which in turn contain **DataElements** (fields, variables).

| Class | What it represents | Examples |
|---|---|---|
| StorageLocation | Logical/physical code storage | Directory, PDS library, package namespace |
| CodeContainer | A single source file or member | Python .py file, COBOL member in PDS, JCL member |
| EncapsulationUnit | Logical boundary grouping code and data | Java class, COBOL program, Rust module, Go package |
| CallableUnit | Named, invocable unit of code | Method, function, COBOL paragraph, stored procedure |
| DataStructure | Composite data type | Struct, record, COBOL group item, protobuf message |
| DataElement | Individual data field or variable | Class field, local variable, COBOL data item, column |
| Parameter | Input/output to a callable (extends DataElement) | Method parameter with direction and passing mechanism |

### 4.2 Behavioral Edges

The power of this layer is in the edges between nodes. These are first-class entities that capture how execution and data flow through the code:

- **ControlFlow** — represents control transfer between code elements. Source and target can be **CallableUnits** or **Statements**. Types:
    - `call`
    - `async_call`
    - `branch`
    - `jump`
    - `return`
    - `throw`
    - `yield`
- **DataFlow** — represents data movement between **DataElements** through **CallableUnits** or **Statements**. Types:
    - `read`
    - `write`
    - `modify`
    - `define`
    - `use`
- **CallableUnit.invokes_callables** — the call graph. Bidirectional: every **CallableUnit** knows what it calls and what calls it.
- **CallableUnit.accesses_data_elements / modifies_data_elements** — read/write access patterns, essential for impact analysis.

### 4.3 Internal Code Structure

Within a **CallableUnit**, the SAO models the internal structure: **CodeBlock** entities contain **Statement** entities. This gives you statement-level resolution when needed — for example, to identify exactly which line performs a particular database write.

CodeBlock types:

- `sequential`
- `conditional`
- `loop`
- `try_catch`
- `transaction`
- `critical_section`
- `scope`

Statement categories:

- `declaration`
- `assignment`
- `invocation`
- `control_transfer`
- `io_operation`
- `data_manipulation`
- `transaction_control`
- `exception_handling`

Supporting classes include **DefinitionReference** (imports, includes, COBOL COPY statements, inheritance declarations), **Annotation** (Java annotations, Python decorators, C# attributes, COBOL compiler directives), and **TypeExpression** (a recursive type model for generics, unions, pointers, function types across all languages).

### 4.4 Platform-Specific Extensions (Sections 18–28)

The SAO extends its code-level model with specialized classes for platform-specific constructs. These are particularly important for mainframe modernization:

| Class | Section | What it captures |
|---|---|---|
| FileDefinition | 20 | File I/O declarations (COBOL SELECT, C fopen) with organization, access mode, record format, key fields |
| FileOperation | 20 | Specific I/O operations (`read`, `write`, `rewrite`, `delete`, `start`, `sort`, `merge`) |
| ScreenDefinition | 21 | Terminal screen/map definitions (CICS BMS maps, RPG display files) with rows, columns, fields |
| ScreenField | 21 | Individual screen field with position, length, input/protected flags, attribute byte |
| JobDefinition | 22 | Batch job definition (JCL JOB, scheduler entry) with class, priority, restart, scheduling |
| JobStep | 22 | Single step in a batch job with program name, condition codes, region size |
| DatasetAllocation | 22 | DD allocation within a job step (dataset name, disposition, space, record format) |
| IPCConnection | 23 | Inter-process communication link (CICS LINK/XCTL, shared memory, message queue, REST call) |
| PreprocessorDirective | 24 | Preprocessor/metaprogramming constructs (C preprocessor, Rust macros, COBOL COPY REPLACING) |
| ErrorModel | 19 | Module/language error handling strategy (`exception_based`, `return_value_based`, `condition_based`, `error_code_based`, `panic_recover`, `monadic`) |
| MemoryModel | 25 | Memory management model (GC type, ownership model, unsafe support) |
| OwnershipAnnotation | 25 | Ownership/lifetime annotations on data elements (Rust borrows, C++ smart pointers) |
| ProgrammingLanguage | 28 | Language as first-class entity with paradigms, type system, GC, preprocessor support |

> **Key design decision: enum-typed, not subclassed.** `EncapsulationUnit` is abstract, but there is no `CobolProgram` or `JavaClass` subclass. Instead, the `encapsulation_type` enum (33 values) captures what kind of thing it is. Similarly, `CallableUnit` uses a `callable_type` enum (53 values) from "method" to "paragraph" to "coroutine." This keeps the relationship graph uniform across languages, making cross-language analysis possible.

---

## 5. Layer 4: Architecture & Integration — The System Map

This layer models how the codebase is organized as a running system — the services, modules, components, and how they connect to each other and to the outside world.

### 5.1 The Architectural Containment Hierarchy

The containment at this layer is: **System** → **BoundedContext** → **Module** → **Component**. This maps directly to Domain-Driven Design (DDD) concepts.

| Class | DDD concept | What it represents | Example |
|---|---|---|---|
| System | Application | Top-level container for the entire software product | The CoreStory platform |
| BoundedContext | Bounded context | Semantic boundary where a domain model applies consistently | Orders context, Inventory context |
| Module | Deployable unit | Cohesive unit of functionality, often a package | Python package, Maven module, COBOL library |
| Component | Building block | Logical grouping within a module | Service class, repository, controller group |

A **BoundedContext** carries a `ubiquitous_language` attribute (the key terms used within it), a `context_map_relationship` (Customer-Supplier, Partnership, etc.), and upstream/downstream relationships to other contexts. This captures the DDD context map.

### 5.2 Services and Interfaces

A **Service** is an independently deployable runtime unit (microservice, monolith, serverless function, CICS transaction, batch program). It runs a **Module**, exposes **Endpoints** (with path, method, protocol, port), and connects to other services.

The system exposes itself through three types of **Interface**, each a subclass of the abstract `Interface` class:

- **UserInterface** — for human interaction. Contains **Screens**, each offering **Operations**. Types:
    - `web_ui`
    - `mobile_ui`
    - `desktop_ui`
    - `cli`
- **ProgrammaticInterface** — for machine-to-machine interaction. Contains **Endpoints**. Types:
    - `rest_api`
    - `graphql_api`
    - `grpc_api`
    - `sdk`
    - `soap_api`
- **EventInterface** — for event-driven interaction. Contains **Subscriptions**. Types:
    - `webhook`
    - `message_queue`
    - `event_stream`
    - `pub_sub`

### 5.3 Integration Cluster

The **Integration** class models connections to external systems. Each **Integration** connects to an **ExternalSystem** via a **Contract** through an **Adapter** (protocol translation component) protected by a **CircuitBreaker** (resilience pattern). **Messages** exchanged in integration are modeled with **Message** entities structured by **Schemas**.

- **ExternalSystem** types:
    - `third_party_service`
    - `partner_system`
    - `legacy_system`
    - `saas_application`
- **Contract** types:
    - `openapi`
    - `asyncapi`
    - `json_schema`
    - `protobuf`
    - `avro`
    - `graphql_schema`
    - `wsdl`

> **Bridge to Layer 3:** `Component.implemented_by_code` points to **EncapsulationUnits** and **CodeContainers**. `Module.mapped_from_directory` points to a **StorageLocation**. These are the links that connect the architectural view to actual code. Without them, the architecture is just a diagram — with them, every box traces to source lines.

---

## 6. Layer 5: Domain Model — The Business Entities

This is the DDD layer. It models the business things the system manages — the entities, their attributes, relationships, and how they persist.

### 6.1 Aggregates, Entities, and Value Objects

| Class | DDD concept | Key characteristic | Example |
|---|---|---|---|
| Aggregate | Aggregate | Transactional boundary, enforces invariants | Order (with OrderLines, ShippingAddress) |
| DomainEntity | Entity | Has identity, lifecycle, mutable state | Customer, Order, Policy, Claim |
| ValueObject | Value object | No identity, immutable, defined by attributes | Address, Money, DateRange, PhoneNumber |
| Attribute | Property | Named, typed property with classification | customer_name, order_total, status |
| DomainRelationship | Association | Typed relationship with cardinality and FK | Order has many OrderLines |

An **Aggregate** has a root **DomainEntity** (the one you address directly), may contain additional entities and value objects, is enforced by invariant **Rules**, persisted in **DataStores**, contained in a **BoundedContext**, and produces **DomainEvents** when its state changes.

A **DomainRelationship** captures cardinality (`one_to_one`, `one_to_many`, `many_to_many`), navigability, composition (lifecycle dependency), the foreign key field implementing it, and any join entity for many-to-many relationships. This is what gets projected into ERD diagrams.

### 6.2 Lifecycle and State Machines

A **Lifecycle** governs a **DomainEntity** through a set of **States** connected by **Transitions**. Each **State** can be initial or terminal, and allows specific **Actions**. Each **Transition** has a source state, target state, triggering **Events**, guarding **Rules**, and **Actions** executed during the transition.

For example: an Order entity might have states Pending, Confirmed, Shipped, Delivered, and Cancelled. The transition from Pending to Confirmed is triggered by a PaymentReceived event, guarded by a rule that verifies inventory availability, and executes an action that reserves stock.

### 6.3 Data Persistence Layer (Section 6)

The persistence model connects domain entities to their storage:

- **DataStore** — a persistence mechanism. Types:
    - `relational_db`
    - `document_db`
    - `key_value_store`
    - `graph_db`
    - `time_series_db`
    - `object_storage`
    - `search_index`
    - `cache`
    - `message_broker`
    - `data_lake`
    - `vsam`
    - `flat_file`
    - `isam`
    - `dead_letter_queue`
- **Collection** — a logical grouping of records within a store (table, collection, bucket), structured by a **Schema**.
- **Record** — a single persisted data instance, conforming to a **Schema**, with **DataLineage** tracking.
- **Schema / SchemaVersion** — structural definition of stored data, with versioning and migration scripts.
- **DataClassification** — sensitivity tagging, critical for compliance. Types:
    - `public`
    - `internal`
    - `confidential`
    - `restricted`
    - `pii`
    - `phi`
    - `pci`
- **RetentionPolicy** — rules for data lifecycle (retention days, archive timing, deletion strategy).
- **DatabaseConstraint / DatabaseIndex** (Section 27) — primary keys, foreign keys, unique/check constraints, and index types.

> **Bridge to Layer 3:** `DomainEntity.mapped_from_structure` ↔ `DataStructure.maps_to_domain_entity` is the inference bridge. The parser populates **DataStructures** from code; the inference engine recognizes which ones represent business concepts and populates **DomainEntities** from them. Similarly, `Attribute.mapped_from_element` ↔ `DataElement.maps_to_attribute` connects domain attributes to their code-level implementations.

---

## 7. Layer 6: Business Intent — Behavior, Rules, and Purpose

This is the most abstract and most valuable layer. It answers: what does this system do, what rules does it enforce, and who uses it for what purpose?

### 7.1 Actors (Section 2)

**Actor** is an abstract class with two concrete subtypes:

- **HumanActor** — represents human users. Types:
    - `end_user`
    - `administrator`
    - `operator`
    - `developer`
    - `auditor`
- **SystemActor** — represents automated entities. Types:
    - `internal_service`
    - `external_system`
    - `scheduled_process`
    - `ai_agent`
    - `message_trigger`

Each **Actor** has **Identities** (verified representations) backed by **Credentials**. **Identities** belong to **Tenants** and **Organizations**, enabling multi-tenant modeling. Credential types:

- `password`
- `token`
- `certificate`
- `api_key`
- `biometric`
- `mfa`
- `oauth`

### 7.2 Behavior (Section 5)

| Class | Role | Key attributes |
|---|---|---|
| Operation | Named, invocable unit of behavior exposed via an interface | Input/output schemas, implementing CallableUnits, exposed by Component |
| Action (abstract) | Atomic operation that can be performed | Permitted by Permissions, targets Resources, emits Events |
| Query (extends Action) | Read-only action that retrieves data | Filters, projections |
| Command (extends Action) | Action that changes system state | Command type (`create`, `update`, `delete`, `execute`, `archive`, `restore`), idempotency key |
| Workflow | Coordinated sequence achieving a business goal | Type: `synchronous`, `asynchronous`, `saga`, `choreography`, `orchestration` |
| Step | Discrete stage within a Workflow | Order, condition, timeout, compensation, preceding/following steps |
| Transaction | Unit of work with consistency guarantees | Type: `local`, `distributed`, `saga`, `two_phase_commit`; isolation level, timeout |

The key relationship chain is: **Actor** → **Action** → **Resource**. **Actors** perform **Actions** (**Queries** or **Commands**). **Actions** target **Resources** (exposed domain entities). **Actions** are allowed by **Permissions**, validated by **Rules**, executed within **Transactions**, and recorded in **AuditEntries**. **Operations** orchestrate **Actions** and are implemented by **CallableUnits**.

### 7.3 Rules

**Rule** is a central class with five categories. Each **Rule** has a condition, action expression, priority, and active flag.

- `validation` — input checks
- `business` — business logic constraints
- `derivation` — computed value rules
- `constraint` — invariant enforcement
- `trigger` — event-reactive rules

**Rules** connect broadly: they validate **Attributes**, enforce **Aggregate** invariants, govern **DomainEntities**, validate **Actions**, and guard **Transitions**. The **AlertRule** subclass extends **Rule** specifically for observability, monitoring **Metrics** and triggering **Alerts**.

### 7.4 Events

**Event** represents something that occurred, with two key subtypes: **DomainEvent** (significant domain occurrences produced by **Aggregates**) and **IntegrationEvent** (cross-service communication events targeted at **Services**). **Events** are structured by **Schemas**, trigger **Transitions**, trigger **Workflows**, and are consumed via **Subscriptions**.

### 7.5 Capability and Feature

These are the highest abstractions. A **Capability** is a discrete business or technical ability the system provides ("process claims," "manage inventory"). **Capabilities** are provided by **Modules**, require **Permissions**, and realize **Features**. A **Feature** is a user-facing manifestation of capabilities, controlled by **Configurations**, and accessible by specific **Roles**. Categories:

- `core`
- `optional`
- `experimental`
- `deprecated`

This is where generated PRDs and capability maps come from: **Feature** instances linked to their enabling **Capabilities**, required **Roles**, and controlling **Configurations**.

---

## 8. Cross-Cutting Concerns

These concerns don't sit in the vertical hierarchy — they attach to entities at every other layer.

### 8.1 Authorization and Policy (Section 3)

The authorization model follows the chain: **Role** → **Permission** → **Scope**. **Roles** grant **Permissions**. **Permissions** allow **Actions** on **ResourceTypes**, limited by **Scopes** (`global`, `tenant`, `organization`, `resource`, `field`). **Policy** entities evaluate Permissions against **Constraints** (`temporal`, `spatial`, `attribute`, `context`, `rate_limit`). Policy types:

- `rbac`
- `abac`
- `rebac`
- `pbac`

### 8.2 Deployment and Operations (Section 8)

- **Environment** — runtime context. Types:
    - `development`
    - `testing`
    - `staging`
    - `production`
    - `dr`
- **Deployment** — instance of a **Service** running in an **Environment** with replica count.
- **DeploymentUnit** — packaged artifact. Types:
    - `container`
    - `vm`
    - `serverless_function`
    - `binary`
    - `package`
- **Configuration** — runtime parameters. Types:
    - `environment_variable`
    - `config_file`
    - `secret`
    - `feature_flag`
    - `remote_config`
- **Infrastructure** — underlying resources. Types:
    - `compute`
    - `storage`
    - `network`
    - `load_balancer`
    - `dns`
    - `cdn`
    - `firewall`
    - `api_gateway`
    - `service_mesh`
- **Release** — versioned, deployable package of changes with changelog.

### 8.3 Observability (Section 9)

The three observability pillars:

- **Metric** — emitted by **Components**. Types:
    - `counter`
    - `gauge`
    - `histogram`
    - `summary`
- **Log/LogEntry** — timestamped discrete events.
- **Trace/Span** — causal chains of operations across services with span hierarchy.

**AlertRule** watches **Metrics**, fires **Alerts**, which escalate to **Incidents** that affect **Services**.

### 8.4 Governance and Compliance (Section 10)

**ComplianceRequirement** is implemented by **Controls** (with control IDs, implementation descriptions, and frequency). Controls are proven by **Evidence** (with collection timestamps and artifact URIs) and assessed in **RiskAssessments** (with threat/vulnerability analysis and residual risk levels). Compliance frameworks:

- `gdpr`
- `hipaa`
- `soc2`
- `pci_dss`
- `iso27001`
- `sox`
- `ccpa`
- `fedramp`

### 8.5 Testing (Section 11)

**TestSuite** contains **TestCases** with **TestAssertions**. **TestCoverage** tracks line, branch, function, and statement coverage percentages.

- TestSuite types:
    - `unit`
    - `integration`
    - `functional`
    - `end_to_end`
    - `performance`
    - `security`
    - `regression`
    - `smoke`
    - `contract`
- TestAssertion types:
    - `equality`
    - `truthiness`
    - `exception`
    - `type_check`
    - `containment`
    - `mock_verification`
    - `snapshot`
    - `custom`

### 8.6 UI/Frontend (Section 12)

**UIComponent** models frontend components with parent/child hierarchy, lazy loading, server rendering, and accessibility roles. **Route** defines navigation paths. **StateStore** models frontend state management. UIComponent types:

- `page`
- `layout`
- `form`
- `widget`
- `modal`
- `navigation`
- `data_display`
- `composite`
- `higher_order`
- `provider`

### 8.7 Build, CI/CD, and Dependencies (Sections 13–14)

**BuildPipeline** with **PipelineStages** produces **BuildArtifacts** stored in **ArtifactRegistries**. **PackageManager** tracks manifest and lock files. **PackageDependency** entities carry version constraints, resolved versions, scopes, licenses, and links to **KnownVulnerabilities** (with CVE IDs, CVSS scores, and fix versions).

### 8.8 Advanced Sections (15–17)

**Concurrency (Section 15):**

- ConcurrencyPrimitive types:
    - `mutex`
    - `semaphore`
    - `read_write_lock`
    - `spin_lock`
    - `condition_variable`
    - `barrier`
    - `latch`
    - `atomic`
- ConcurrencyPattern types:
    - `thread_pool`
    - `actor`
    - `channel`
    - `future_promise`
    - `async_await`
    - `fork_join`
    - `producer_consumer`
    - `reactor`
    - `proactor`
    - `csp`

**ML/Data Pipelines (Section 16):** **MLModel** (with type, framework, format, metrics, feature stores), **Dataset**, **DataPipeline** with **DataPipelineSteps**:

- `extract`
- `transform`
- `load`
- `validate`
- `deduplicate`
- `enrich`
- `aggregate`
- `partition`
- `train`
- `evaluate`
- `deploy_model`

**Infrastructure as Code (Section 17):** **IaCDefinition**, **IaCResource**, and **IaCModule**. IaC tool types:

- `terraform`
- `cloudformation`
- `pulumi`
- `ansible`
- `chef`
- `puppet`
- `kubernetes_manifest`
- `helm`
- `docker_compose`
- `bicep`
- `cdk`

### 8.9 Knowledge Artifacts (Section 30)

**KnowledgeArtifact** is the self-referential class. It represents documentation with supersession chains.

- Artifact types:
    - `adr`
    - `readme`
    - `design_doc`
    - `runbook`
    - `wiki_page`
    - `api_doc`
    - `onboarding_guide`
    - `postmortem`
    - `changelog`
    - `comment`
    - `diagram`
    - `rfc`
    - `sop`
- Status values:
    - `draft`
    - `published`
    - `accepted`
    - `superseded`
    - `deprecated`
    - `archived`

Critically, **KnowledgeArtifact** has `documents_*` relationships pointing to **System**, **BoundedContext**, **Module**, **Component**, **Service**, **Aggregate**, **DomainEntity**, and **Integration**. The SAO tracks its own output: generated specifications are themselves **KnowledgeArtifact** instances, linked back to the entities they describe.

---

## 9. Section Index

| Layer | Sections |
|---|---|
| 3 — Code structure | 1 (Structural Foundation, code parts), 18 (Type System), 19 (Error Handling), 20 (File I/O), 21 (Screen/Terminal), 22 (Job Control), 23 (IPC), 24 (Preprocessor), 25 (Memory/Ownership), 26 (Domain Entity Relationships), 27 (Database Schema), 28 (Programming Language) |
| 4 — Architecture | 1 (Structural Foundation, arch parts), 7 (Integration), 29 (Architectural Patterns) |
| 5 — Domain model | 4 (Domain Modeling), 6 (Data Management), 26 (Domain Entity Relationships), 27 (Database Schema Objects) |
| 6 — Business intent | 2 (Actors and Identity), 5 (Behavior and Workflow) |
| Cross-cut — Layer 1 | 3 (Authorization), 10 (Governance), 11 (Testing), 12 (UI/Frontend), 13 (Build/CI-CD), 14 (Dependencies), 30 (Knowledge Artifacts) |
| Cross-cut — Layer 2 | 8 (Deployment/Ops), 9 (Observability), 15 (Concurrency), 16 (ML/Data Pipelines), 17 (Infrastructure as Code) |

---

## 10. The Glue: Bidirectional Relationships

The SAO has 214 bidirectional relationship pairs. Every relationship has an explicit inverse, so you can traverse the graph in either direction.

### 10.1 Key Cross-Layer Bridges

| Bridge | Direction | What it connects |
|---|---|---|
| `DataStructure.maps_to_domain_entity` ↔ `DomainEntity.mapped_from_structure` | Layer 3 ↔ 5 | Code-level data structures to business entities |
| `Attribute.mapped_from_element` ↔ `DataElement.maps_to_attribute` | Layer 5 ↔ 3 | Domain attributes to code-level fields |
| `CallableUnit.implements_operation` ↔ `Operation.implemented_by_callables` | Layer 3 ↔ 6 | Code functions to business operations |
| `Component.implemented_by_code` ↔ code entities | Layer 4 ↔ 3 | Architecture components to source code |
| `Module.mapped_from_directory` ↔ `StorageLocation.maps_to_module` | Layer 4 ↔ 3 | Architecture modules to file system structure |
| `Module.provides_capabilities` ↔ `Capability.provided_by_modules` | Layer 4 ↔ 6 | Architecture to business purpose |
| `Service.runs_module` ↔ `Module.runs_as_services` | Layer 4 ↔ 4 | Runtime identity to logical structure |
| `KnowledgeArtifact.documents_*` ↔ `entity.*_documented_by_artifacts` | Layer 1 ↔ all | Documentation to everything it describes |

The complete list is in [Appendix C](#appendix-c-complete-bidirectional-relationship-pairs-226-rows).

---

## 11. Base Classes and Mixins

| Class | Type | Purpose | Used by |
|---|---|---|---|
| NamedEntity | Abstract | Base for all named entities. Provides id, name, description, tags, metadata. | Nearly every class |
| Metadata | Concrete | Common metadata (created_at, updated_at, created_by, version). | Inlined in NamedEntity |
| Versionable | Mixin | Versioning support (version, effective_from/to, is_current). | System, Module, CodeContainer, Schema, Contract, Release, BuildArtifact, MLModel, Dataset, IaCDefinition, KnowledgeArtifact |
| Auditable | Mixin | Audit trail support (audit_log reference). | DomainEntity |
| PlatformExtension | Abstract | Base for platform-specific extensions (platform attribute). | ExecutionEnvironmentDirective |

---

## 12. Reading the SAO Effectively

When working with the SAO, keep these principles in mind:

- **Follow the containment.** **System** → **BoundedContext** → **Module** → **Component** is the architectural spine. **StorageLocation** → **CodeContainer** → **EncapsulationUnit** → **CallableUnit** is the code spine. These two spines are bridged by `implemented_by_code` and `mapped_from_directory`.

- **Follow the bridges.** The `maps_to` / `mapped_from` pairs are where inference happens. If you're trying to understand how a code-level entity connects to a business concept, look for these bridge relationships.

- **Check the enums.** The SAO's 102 enums are where the real vocabulary lives. When you need to know what types of services exist, what kinds of callable units there are, or what database types are supported, the enums have the answer. See [Appendix B](#appendix-b-complete-enumeration-reference-102-enums) for the complete list.

- **Use the inverses.** Every bidirectional relationship can be traversed both ways. "What **CallableUnits** implement this **Operation**?" and "What **Operation** does this **CallableUnit** implement?" are both single-hop queries.

- **Know what's parsed vs. inferred.** Layer 3 is populated by the parser with high confidence. Layers 4–6 are populated by inference with varying confidence. When you see a **DomainEntity** or a **Capability**, remember that something (an algorithm, an LLM, or a human) had to recognize it — it wasn't just read from the source code.

---

---

## Appendix A: Complete Class Inventory (147 classes)

All 147 classes organized by conceptual layer. See [Section 3](#3-the-six-conceptual-layers) for layer definitions.

### Base classes and mixins (4 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `NamedEntity` | — | Abstract | Abstract base class for all named entities in the ontology |
| `Metadata` | — | Concrete | Common metadata for entities |
| `Versionable` | — | Mixin | Mixin for entities that support versioning |
| `Auditable` | — | Mixin | Mixin for entities requiring audit trails |

### Layer 3: Code structure (33 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `CodeContainer` | NamedEntity + Versionable | Concrete | A physical container of source code - may be a file, member in a library, or other storage unit depending on the platform. |
| `StorageLocation` | NamedEntity | Concrete | A logical or physical location for storing code containers. |
| `EncapsulationUnit` | NamedEntity | Abstract | A logical boundary that groups related code and data. Maps to: Class (OOP), Program (COBOL), Module (functional), Package (Java), Namespa... |
| `CallableUnit` | NamedEntity | Concrete | A named, invocable unit of code that performs a specific task. Maps to: Method (OOP), Function (procedural/functional), Paragraph (COBOL)... |
| `DataStructure` | NamedEntity | Concrete | A composite data type grouping related data elements. Maps to: Struct (C), Record (Pascal/COBOL), Class data (OOP), Type (Haskell), Dicti... |
| `DataElement` | NamedEntity | Concrete | An individual data field or variable. Maps to: Field (OOP), Variable (procedural), Column (database), Data item (COBOL), Property (C#), A... |
| `Parameter` | DataElement | Concrete | An input/output parameter for a callable unit. |
| `CodeBlock` | NamedEntity | Concrete | A logical grouping of statements within a callable unit. |
| `Statement` | NamedEntity | Concrete | A single executable instruction or declaration. |
| `DefinitionReference` | NamedEntity | Concrete | A reference from one code container to shared definitions. Maps to: Import (Python/Java), Include (C/C++), COPY (COBOL), Using (C#), Requ... |
| `ControlFlow` | NamedEntity | Concrete | Represents control flow between code elements. |
| `DataFlow` | NamedEntity | Concrete | Represents data flow between code elements. |
| `PlatformExtension` | NamedEntity | Abstract | Base class for platform-specific extensions |
| `ExecutionEnvironmentDirective` | PlatformExtension | Concrete | Platform-specific execution directives. Maps to: JCL (mainframe), Docker Compose, Kubernetes manifests, Shell scripts, Makefiles, build f... |
| `Annotation` | NamedEntity | Concrete | Metadata attached to code elements. Maps to: Annotations (Java), Decorators (Python), Attributes (C#), Pragmas (C/C++), Compiler directives. |
| `TypeExpression` | NamedEntity | Concrete | A recursive type model for expressing complex types (generics, unions, pointers, function types, etc.) across all languages. |
| `ErrorModel` | NamedEntity | Concrete | Describes how a module or language handles errors |
| `ExceptionType` | NamedEntity | Concrete | A declared exception or error type in a codebase |
| `FileDefinition` | NamedEntity | Concrete | A file defined for I/O in a program (COBOL SELECT, C fopen, etc.) |
| `FileOperation` | NamedEntity | Concrete | A specific I/O operation on a file definition |
| `ScreenDefinition` | NamedEntity | Concrete | A terminal screen or map definition for character-mode UIs |
| `ScreenField` | NamedEntity | Concrete | A field on a terminal screen definition |
| `JobDefinition` | NamedEntity | Concrete | A batch job definition (JCL JOB, scheduler entry, cron job) |
| `JobStep` | NamedEntity | Concrete | A single step within a batch job |
| `DatasetAllocation` | NamedEntity | Concrete | A dataset (DD) allocation within a job step |
| `IPCConnection` | NamedEntity | Concrete | A communication link between two programs/processes |
| `PreprocessorDirective` | NamedEntity | Concrete | A preprocessor directive, macro, or metaprogramming construct |
| `MemoryModel` | NamedEntity | Concrete | Describes how a language or module manages memory |
| `OwnershipAnnotation` | NamedEntity | Concrete | An ownership/lifetime annotation on a data element |
| `DomainRelationship` | NamedEntity | Concrete | A named, typed relationship between two domain entities (e.g., Order has many OrderLines, User belongs to Organization) |
| `DatabaseConstraint` | NamedEntity | Concrete | A constraint on a database table/collection |
| `DatabaseIndex` | NamedEntity | Concrete | An index on a database table/collection |
| `ProgrammingLanguage` | NamedEntity | Concrete | A programming language with its paradigms, type system, and runtime characteristics |

### Layer 4: Architecture and integration (19 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `System` | NamedEntity + Versionable | Concrete | Top-level container representing a software product, platform, or application |
| `BoundedContext` | NamedEntity | Concrete | A semantic boundary within which a domain model applies consistently. Corresponds to DDD bounded context concept. |
| `Module` | NamedEntity + Versionable | Concrete | A deployable, cohesive unit of functionality within a bounded context |
| `Component` | NamedEntity | Concrete | A logical building block within a module (class, function group, etc.) |
| `Interface` | NamedEntity | Abstract | A contract-defined boundary through which interaction occurs |
| `UserInterface` | Interface | Concrete | User-facing interface |
| `Screen` | NamedEntity | Concrete | A single screen or view in a user interface |
| `ProgrammaticInterface` | Interface | Concrete | Machine-to-machine interface |
| `EventInterface` | Interface | Concrete | Event-driven interface |
| `Service` | NamedEntity | Concrete | An independently deployable runtime unit |
| `Endpoint` | NamedEntity | Concrete | A specific addressable entry point on a service |
| `Dependency` | NamedEntity | Concrete | A lightweight dependency reference between components or services |
| `ExternalSystem` | NamedEntity | Concrete | A system outside this system's boundary |
| `Integration` | NamedEntity | Concrete | A configured connection to an external system |
| `Message` | NamedEntity | Concrete | A unit of data exchanged in integration |
| `Contract` | NamedEntity + Versionable | Concrete | A formal specification of integration behavior |
| `ContractVersion` | NamedEntity | Concrete | A specific iteration of a contract |
| `Adapter` | Component | Concrete | A component that translates between system and external protocols |
| `CircuitBreaker` | NamedEntity | Concrete | A resilience pattern preventing cascade failures |

### Layer 5: Domain model (17 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `Aggregate` | NamedEntity | Concrete | A cluster of domain entities treated as a single transactional unit. Corresponds to DDD aggregate concept. |
| `DomainEntity` | NamedEntity + Auditable | Concrete | A uniquely identifiable object within the domain |
| `ValueObject` | NamedEntity | Concrete | An immutable domain object defined by its attributes |
| `Attribute` | NamedEntity | Concrete | A named property of an entity or value object |
| `Resource` | NamedEntity | Concrete | A domain entity or value object exposed for external interaction |
| `ResourceType` | NamedEntity | Concrete | A classification of resources sharing common structure and behavior |
| `State` | NamedEntity | Concrete | A discrete condition in an entity's lifecycle |
| `Transition` | NamedEntity | Concrete | A valid movement between states |
| `Lifecycle` | NamedEntity | Concrete | The complete set of states and transitions for an entity type |
| `DataStore` | NamedEntity | Concrete | A persistence mechanism |
| `Collection` | NamedEntity | Concrete | A logical grouping of records (table, collection, bucket) |
| `Record` | NamedEntity | Concrete | A single persisted instance of data |
| `Schema` | NamedEntity + Versionable | Concrete | The structural definition of stored data |
| `SchemaVersion` | NamedEntity | Concrete | A specific iteration of a schema |
| `DataClassification` | NamedEntity | Concrete | A sensitivity or handling category |
| `RetentionPolicy` | NamedEntity | Concrete | Rules governing data lifecycle and deletion |
| `DataLineage` | NamedEntity | Concrete | The origin, transformation history, and movement of data |

### Layer 6: Business intent (17 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `Capability` | NamedEntity | Concrete | A discrete business or technical ability the system provides |
| `Feature` | NamedEntity | Concrete | A user-facing manifestation of one or more capabilities |
| `Actor` | NamedEntity | Abstract | Any entity that can initiate actions |
| `HumanActor` | Actor | Concrete | A human user of the system |
| `SystemActor` | Actor | Concrete | A system or automated actor |
| `Action` | NamedEntity | Abstract | An atomic operation that can be performed |
| `Query` | Action | Concrete | A read-only action that retrieves data |
| `Command` | Action | Concrete | An action that changes system state |
| `Operation` | NamedEntity | Concrete | A named, invocable unit of behavior exposed via an interface |
| `Workflow` | NamedEntity | Concrete | A coordinated sequence of actions achieving a business goal |
| `Step` | NamedEntity | Concrete | A discrete stage within a workflow |
| `Rule` | NamedEntity | Concrete | A declarative constraint or trigger governing behavior |
| `Event` | NamedEntity | Concrete | A notification that something occurred |
| `DomainEvent` | Event | Concrete | A significant occurrence in the domain |
| `IntegrationEvent` | Event | Concrete | An event for cross-service communication |
| `Subscription` | NamedEntity | Concrete | A registration to receive events of a certain type |
| `Transaction` | NamedEntity | Concrete | A unit of work with ACID or BASE guarantees |

### Cross-cutting: Security, governance, quality, knowledge (31 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `Identity` | NamedEntity | Concrete | A verified representation of an actor |
| `Credential` | NamedEntity | Concrete | Authentication material proving an identity claim |
| `Tenant` | NamedEntity | Concrete | An organizational boundary for multi-tenant systems |
| `Organization` | NamedEntity | Concrete | A logical grouping of users and resources within a tenant |
| `Role` | NamedEntity | Concrete | A named collection of permissions assignable to actors |
| `Permission` | NamedEntity | Concrete | A specific allowed action on a resource type or instance |
| `Policy` | NamedEntity | Concrete | A rule set governing access decisions |
| `Scope` | NamedEntity | Concrete | A boundary limiting where a permission applies |
| `Constraint` | NamedEntity | Concrete | A condition that must be satisfied for authorization |
| `AuditLog` | NamedEntity | Concrete | A tamper-evident record of system activities |
| `AuditEntry` | NamedEntity | Concrete | A single record within an audit log |
| `ComplianceRequirement` | NamedEntity | Concrete | A regulatory or policy obligation |
| `Control` | NamedEntity | Concrete | A measure implementing a compliance requirement |
| `Evidence` | NamedEntity | Concrete | Proof that a control is operating effectively |
| `RiskAssessment` | NamedEntity | Concrete | An evaluation of threats and vulnerabilities |
| `TestSuite` | NamedEntity | Concrete | A collection of related test cases |
| `TestCase` | NamedEntity | Concrete | A single test case that validates specific behavior |
| `TestAssertion` | NamedEntity | Concrete | An individual assertion within a test case |
| `TestCoverage` | NamedEntity | Concrete | Code coverage metrics for a component or module |
| `UIComponent` | NamedEntity | Concrete | A frontend user interface component that renders visual elements. |
| `UIProperty` | NamedEntity | Concrete | A property (prop) passed to a UI component |
| `Route` | NamedEntity | Concrete | A navigation route or URL path in a frontend application. |
| `StateStore` | NamedEntity | Concrete | A frontend state management store or container. |
| `BuildPipeline` | NamedEntity | Concrete | A CI/CD pipeline that automates build, test, and deployment processes. |
| `PipelineStage` | NamedEntity | Concrete | A discrete stage within a CI/CD pipeline |
| `BuildArtifact` | NamedEntity + Versionable | Concrete | An artifact produced by a build pipeline |
| `ArtifactRegistry` | NamedEntity | Concrete | A registry or repository for storing build artifacts. |
| `PackageManager` | NamedEntity | Concrete | A package/dependency management tool |
| `PackageDependency` | NamedEntity | Concrete | A declared dependency on an external package or library |
| `KnownVulnerability` | NamedEntity | Concrete | A known security vulnerability in a dependency |
| `KnowledgeArtifact` | NamedEntity + Versionable | Concrete | A knowledge artifact that documents some aspect of the system |

### Cross-cutting: Runtime, ops, infrastructure (26 classes)

| Class | Parent | Type | Description |
|---|---|---|---|
| `Environment` | NamedEntity | Concrete | A runtime context with specific configuration |
| `Deployment` | NamedEntity | Concrete | An instance of a service running in an environment |
| `DeploymentUnit` | NamedEntity | Concrete | The packaged artifact being deployed |
| `Configuration` | NamedEntity | Concrete | Runtime parameters for a deployment |
| `Infrastructure` | NamedEntity | Concrete | The underlying compute, storage, and network resources |
| `Release` | NamedEntity + Versionable | Concrete | A versioned, deployable package of changes |
| `Metric` | NamedEntity | Concrete | A quantitative measurement over time |
| `Log` | NamedEntity | Concrete | A timestamped record of discrete events |
| `LogEntry` | NamedEntity | Concrete | A single record within a log |
| `Trace` | NamedEntity | Concrete | A causal chain of operations across services |
| `Span` | NamedEntity | Concrete | A single unit of work within a trace |
| `Alert` | NamedEntity | Concrete | A notification triggered by metric thresholds or anomalies |
| `AlertRule` | Rule | Concrete | The condition that triggers an alert |
| `Incident` | NamedEntity | Concrete | A tracked degradation or outage event |
| `HealthCheck` | NamedEntity | Concrete | A probe verifying service availability |
| `ConcurrencyPrimitive` | NamedEntity | Concrete | A low-level synchronization primitive used in concurrent code. |
| `ConcurrencyPattern` | NamedEntity | Concrete | A high-level concurrency pattern used in the system. |
| `MLModel` | NamedEntity + Versionable | Concrete | A machine learning model defined, trained, or served by the system |
| `MLModelMetric` | NamedEntity | Concrete | A performance metric for an ML model |
| `Dataset` | NamedEntity + Versionable | Concrete | A dataset used for training, evaluation, or inference |
| `FeatureStore` | NamedEntity | Concrete | A centralized store for computed ML features. |
| `DataPipeline` | NamedEntity | Concrete | A data processing pipeline for ETL, feature engineering, or model training. |
| `DataPipelineStep` | NamedEntity | Concrete | A discrete step within a data pipeline |
| `IaCDefinition` | NamedEntity + Versionable | Concrete | An infrastructure-as-code definition that declaratively specifies infrastructure resources. |
| `IaCResource` | NamedEntity | Concrete | A single infrastructure resource defined in code |
| `IaCModule` | NamedEntity | Concrete | A reusable module of IaC definitions. |

---

## Appendix B: Complete Enumeration Reference (102 enums)

All 102 enumerations with their 804 permissible values, organized by topic. See [Section 4.4](#44-platform-specific-extensions-sections-1828) for context on code-structure enums and [Section 7.2](#72-behavior-section-5) for behavior enums.

### Structural

**`Cardinality`** — Relationship cardinality options  
Values (4): `one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`

**`InterfaceCategory`** — Categories of system interfaces  
Values (3): `user_interface`, `programmatic_interface`, `event_interface`

**`UserInterfaceType`** — Types of user interfaces  
Values (4): `web_ui`, `mobile_ui`, `desktop_ui`, `cli`

**`APIType`** — Types of programmatic interfaces  
Values (5): `rest_api`, `graphql_api`, `grpc_api`, `sdk`, `soap_api`

**`EventInterfaceType`** — Types of event interfaces  
Values (4): `webhook`, `message_queue`, `event_stream`, `pub_sub`

**`ServiceType`** — Types of runtime services  
Values (9): `microservice`, `monolith`, `function` (Serverless function or lambda), `job` (Batch processing job), `daemon`, `cics_transaction` (CICS online transaction), `ims_transaction` (IMS online transaction), `batch_program` (Mainframe batch program), `stored_proc_service` (Stored procedure exposed as service)

**`DependencyType`** — Types of dependencies  
Values (4): `runtime`, `build`, `optional`, `dev`

**`FeatureCategory`** — Categories of features  
Values (4): `core`, `optional`, `experimental`, `deprecated`

### Actors and identity

**`ActorCategory`** — Categories of actors  
Values (2): `human`, `system`

**`HumanActorType`** — Types of human actors  
Values (5): `end_user`, `administrator`, `operator`, `developer`, `auditor`

**`SystemActorType`** — Types of system actors  
Values (5): `internal_service`, `external_system`, `scheduled_process`, `ai_agent`, `message_trigger`

**`CredentialType`** — Types of authentication credentials  
Values (7): `password`, `token` (Token-based authentication (JWT, bearer token)), `certificate` (Digital certificate or X.509 certificate), `api_key`, `biometric`, `mfa` (Multi-factor authentication), `oauth` (OAuth 2.0 authentication flow)

### Authorization

**`PolicyType`** — Types of authorization policies  
Values (4): `rbac` (Role-Based Access Control), `abac` (Attribute-Based Access Control), `rebac` (Relationship-Based Access Control), `pbac` (Policy-Based Access Control)

**`ScopeType`** — Types of permission scopes  
Values (5): `global`, `tenant`, `organization`, `resource`, `field`

**`ConstraintType`** — Types of authorization constraints  
Values (5): `temporal`, `spatial`, `attribute`, `context` (Context-dependent constraint (device, IP, etc.)), `rate_limit`

### Domain modeling

**`AttributeCategory`** — Categories of entity attributes  
Values (5): `required`, `optional`, `computed`, `derived`, `transient`

**`ActionCategory`** — Categories of actions  
Values (3): `query`, `command`, `mutation`

**`CommandType`** — Types of commands  
Values (6): `create`, `update`, `delete`, `execute`, `archive`, `restore`

**`WorkflowType`** — Types of workflows  
Values (5): `synchronous`, `asynchronous`, `saga` (Saga pattern for distributed transactions), `choreography` (Event-driven choreography workflow), `orchestration`

**`RuleCategory`** — Categories of business rules  
Values (5): `validation`, `business`, `derivation`, `constraint`, `trigger`

**`EventCategory`** — Categories of events  
Values (4): `domain_event`, `integration_event`, `system_event`, `audit_event`

**`TransactionType`** — Types of transactions  
Values (4): `local`, `distributed`, `saga` (Saga pattern with compensating transactions), `two_phase_commit`

### Data management

**`DataStoreType`** — Types of data stores  
Values (14): `relational_db`, `document_db`, `key_value_store`, `graph_db`, `time_series_db`, `object_storage`, `search_index`, `cache`, `message_broker`, `data_lake`, `vsam` (IBM VSAM dataset), `flat_file` (Sequential or flat file), `isam` (Indexed Sequential Access Method file), `dead_letter_queue`

**`SchemaType`** — Types of data schemas  
Values (5): `table_schema`, `document_schema`, `event_schema`, `api_schema`, `message_schema`

**`DataClassificationType`** — Data sensitivity classifications  
Values (7): `public`, `internal`, `confidential`, `restricted`, `pii` (Personally Identifiable Information), `phi` (Protected Health Information), `pci` (Payment Card Industry data)

**`IntegrationType`** — Types of integrations  
Values (3): `inbound`, `outbound`, `bidirectional`

**`ExternalSystemType`** — Types of external systems  
Values (4): `third_party_service`, `partner_system`, `legacy_system`, `saas_application`

**`ProtocolType`** — Communication protocols  
Values (15): `http`, `https`, `websocket`, `grpc`, `amqp`, `mqtt`, `kafka`, `sftp`, `tcp`, `udp`, `corba` (Common Object Request Broker Architecture), `dcom` (Distributed Component Object Model), `rmi` (Java Remote Method Invocation), `named_pipe`, `shared_memory`

**`MessageType`** — Types of messages  
Values (6): `request`, `response`, `notification`, `command`, `event`, `query`

**`ContractType`** — Types of API contracts  
Values (7): `openapi`, `asyncapi`, `json_schema`, `protobuf`, `avro`, `graphql_schema`, `wsdl`

**`MessageFormat`** — Message serialization formats  
Values (7): `json`, `xml`, `protobuf`, `avro`, `thrift`, `msgpack`, `custom_binary`

### Deployment and operations

**`EnvironmentType`** — Types of deployment environments  
Values (5): `development`, `testing`, `staging`, `production`, `dr` (Disaster Recovery)

**`DeploymentUnitType`** — Types of deployment units  
Values (5): `container`, `vm`, `serverless_function`, `binary`, `package`

**`ConfigurationType`** — Types of configuration  
Values (5): `environment_variable`, `config_file`, `secret`, `feature_flag`, `remote_config`

**`InfrastructureType`** — Types of infrastructure  
Values (9): `compute`, `storage`, `network`, `load_balancer`, `dns`, `cdn`, `firewall`, `api_gateway` (API gateway or ingress controller), `service_mesh` (Service mesh control plane (Istio, Linkerd, etc.))

### Observability

**`MetricType`** — Types of metrics  
Values (4): `counter`, `gauge`, `histogram`, `summary`

**`LogType`** — Types of logs  
Values (6): `application`, `access`, `error`, `security`, `audit`, `debug`

**`HealthCheckType`** — Types of health checks  
Values (4): `liveness`, `readiness`, `dependency`, `startup`

### Governance

**`ComplianceFramework`** — Compliance frameworks  
Values (8): `gdpr`, `hipaa`, `soc2`, `pci_dss`, `iso27001`, `sox`, `ccpa`, `fedramp`

### Code structure

**`CodeContainerType`** — Types of code containers  
Values (13): `source_file`, `library_member` (Member of a partitioned dataset or library), `include_file` (Shared definitions file (header, copybook)), `script`, `configuration`, `schema_definition`, `notebook_cell`, `inline_code`, `jcl_member` (JCL member in a PDS), `rpg_source`, `pli_source`, `assembler_source`, `cl_source` (IBM CL (Control Language) source)

**`StorageLocationType`** — Types of storage locations  
Values (5): `directory`, `library` (Partitioned dataset or library (mainframe)), `package`, `namespace`, `module_path`

**`EncapsulationType`** — Types of encapsulation units across different paradigms  
Values (33): `class`, `interface`, `abstract_class`, `trait` (Trait (Rust, Scala) or mixin), `enum_class`, `record_class` (Record or data class (Java records, Python dataclass)), `singleton`, `program` (Standalone program (COBOL, Fortran)), `subprogram` (Callable subprogram or subroutine library), `unit` (Pascal/Delphi unit), `module` (Functional module (Haskell, OCaml, F#)), `namespace`, `package` (Package (Ada, Go)), `library`, `object` (JavaScript/prototype-based object), `component` (Component (React, Angular, Vue)), `service`, `controller` (Controller (MVC pattern)), `stored_procedure`, `function_package` (PL/SQL or T-SQL package), `trigger`, `view` (Database view definition), `script`, `batch_program`, `online_program` (Online transaction program (CICS, IMS)), `copybook` (COBOL copybook or include file), `composite`, `other`, `rpg_module`, `rpg_service_program`, `pli_procedure`, `pli_package`, `assembler_csect` (Assembler control section)

**`CallableType`** — Types of callable units across different paradigms  
Values (53): `method`, `static_method`, `constructor`, `destructor`, `property_getter`, `property_setter`, `operator_overload`, `conversion_operator`, `indexer`, `abstract_method`, `virtual_method`, `function`, `procedure`, `subroutine`, `paragraph` (COBOL paragraph), `section` (COBOL section or similar grouping), `lambda`, `closure`, `higher_order_function`, `curried_function`, `functor`, `event_handler`, `callback`, `delegate`, `signal_handler`, `stored_procedure`, `stored_function`, `trigger_body`, `cursor`, `coroutine`, `generator`, `async_function`, `thread_entry`, `task`, `test_case`, `test_fixture`, `mock`, `macro`, `template` (Template function (C++)), `generic_method`, `main_entry`, `interrupt_handler`, `exception_handler`, `finalizer`, `factory_method`, `extension_method`, `script_function`, `command`, `other`, `rpg_subprocedure`, `pli_entry` (PL/I ENTRY point), `assembler_entry` (Assembler entry point), `rpg_subroutine`

**`DataStructureType`** — Types of data structures across different paradigms  
Values (50): `class_data`, `inner_class`, `anonymous_class`, `struct`, `record`, `union`, `group_item` (COBOL group item (composite)), `algebraic_data_type`, `type_class`, `product_type`, `sum_type`, `array`, `dynamic_array`, `list`, `dictionary`, `set`, `queue`, `stack`, `tree`, `graph`, `table_structure`, `view_structure`, `cursor_structure`, `rowtype`, `value_object`, `dto`, `tuple`, `pair`, `enum`, `flags`, `configuration_object`, `message`, `event`, `command`, `json_schema`, `xml_schema`, `protobuf_message`, `avro_record`, `smart_pointer`, `reference_wrapper`, `copybook_structure`, `commarea` (CICS communication area), `linkage_section` (COBOL linkage section structure), `opaque_type`, `variant`, `other`, `rpg_data_structure`, `pli_structure`, `assembler_dsect` (Assembler dummy section), `cobol_file_descriptor` (COBOL FD (File Description) entry)

**`VisibilityType`** — Visibility modifiers for code elements  
Values (5): `public`, `private`, `protected`, `internal`, `package`

**`CallableCategory`** — Behavioral-role categories of callable units  
Values (3): `normal`, `operator`, `main_entry`

**`EntryPointType`** — Types of program entry points  
Values (5): `main_program`, `transaction_entry`, `event_handler`, `scheduled_entry`, `api_endpoint`

**`DataStructureCategory`** — Categories of data structures  
Values (6): `composite`, `collection`, `hierarchical`, `value_type`, `reference_type`, `union`

**`DataElementCategory`** — Categories of data elements  
Values (8): `field`, `static_field`, `local_variable`, `parameter`, `constant`, `global_variable`, `computed`, `temporary`

**`ParameterDirection`** — Parameter passing direction  
Values (4): `input`, `output`, `input_output`, `return`

**`PassingMechanism`** — Parameter passing mechanisms  
Values (4): `by_value`, `by_reference`, `by_name` (Pass by name (lazy evaluation)), `by_result` (Pass by result (copy-out))

**`CodeBlockType`** — Types of code blocks  
Values (7): `sequential`, `conditional`, `loop`, `try_catch`, `transaction`, `critical_section`, `scope`

**`StatementCategory`** — Categories of statements  
Values (8): `declaration`, `assignment`, `invocation`, `control_transfer`, `io_operation`, `data_manipulation`, `transaction_control`, `exception_handling`

**`ReferenceType`** — Types of definition references  
Values (5): `import_module`, `import_symbol`, `include_source`, `inherit`, `implement`

**`ControlFlowType`** — Types of control flow  
Values (7): `call`, `async_call`, `branch`, `jump`, `return`, `throw`, `yield`

**`DataFlowType`** — Types of data flow  
Values (5): `read`, `write`, `modify`, `define`, `use`

**`StorageClass`** — Storage classes for data elements  
Values (6): `automatic`, `static`, `heap`, `register`, `thread_local`, `external`

**`PersistenceType`** — How a data structure is persisted  
Values (12): `transient`, `database_table`, `database_view`, `file_record`, `serialized`, `cached`, `distributed_cache`, `message_queue`, `object_store`, `document_store`, `key_value_store`, `graph_database`

**`DatabaseType`** — Types of database management systems  
Values (14): `oracle`, `postgresql`, `sql_server`, `mysql`, `db2`, `teradata`, `sybase`, `informix`, `mongodb`, `cassandra`, `sqlite`, `ims_db` (IBM IMS hierarchical database), `adabas` (Software AG Adabas), `idms` (CA IDMS network database)

**`LinkageType`** — Types of callable linkage  
Values (4): `static`, `dynamic`, `inline`, `late_binding`

**`SecurityType`** — Database security context types  
Values (2): `definer`, `invoker`

**`StructureLayout`** — Memory layout strategies for structures  
Values (4): `sequential`, `explicit`, `auto`, `packed`

**`EqualitySemantics`** — How equality is determined for value types  
Values (4): `by_value`, `by_reference`, `by_identity`, `custom`

### Testing

**`TestSuiteType`** — Types of test suites  
Values (9): `unit`, `integration`, `functional`, `end_to_end`, `performance`, `security`, `regression`, `smoke`, `contract`

**`TestCaseStatus`** — Execution status of a test case  
Values (5): `passing`, `failing`, `skipped`, `flaky`, `pending`

**`AssertionType`** — Types of test assertions  
Values (8): `equality`, `truthiness`, `exception`, `type_check`, `containment`, `mock_verification`, `snapshot`, `custom`

### UI/Frontend

**`UIComponentType`** — Types of UI components  
Values (10): `page`, `layout`, `form`, `widget`, `modal`, `navigation`, `data_display`, `composite`, `higher_order`, `provider`

**`StateManagementType`** — Types of frontend state management  
Values (6): `local_state`, `global_store`, `context`, `url_state`, `server_state`, `form_state`

**`RouteType`** — Types of routes/navigation paths  
Values (6): `page_route`, `api_route`, `layout_route`, `redirect`, `catch_all`, `guarded`

### Build and CI/CD

**`PipelineType`** — Types of CI/CD pipelines  
Values (7): `build`, `test`, `deploy`, `release`, `integration`, `delivery`, `validation`

**`PipelineStageType`** — Types of pipeline stages  
Values (11): `checkout`, `build`, `test`, `lint`, `security_scan`, `package`, `publish`, `deploy`, `approval`, `rollback`, `notify`

**`ArtifactType`** — Types of build artifacts  
Values (8): `container_image`, `binary`, `archive`, `package`, `library`, `documentation`, `report`, `load_module` (Mainframe load module)

### Dependency management

**`PackageManagerType`** — Types of package managers  
Values (11): `npm`, `pip`, `maven`, `gradle`, `nuget`, `cargo`, `go_modules`, `bundler`, `composer`, `conan`, `none`

**`DependencyScope`** — Scope/context of a dependency  
Values (6): `production`, `development`, `test`, `build`, `optional`, `provided`

**`VulnerabilitySeverity`** — Severity of a known vulnerability  
Values (5): `critical`, `high`, `medium`, `low`, `none`

### Concurrency

**`ConcurrencyPrimitiveType`** — Types of concurrency primitives  
Values (8): `mutex`, `semaphore`, `read_write_lock`, `spin_lock`, `condition_variable`, `barrier`, `latch`, `atomic`

**`ConcurrencyPatternType`** — Types of concurrency patterns  
Values (10): `thread_pool`, `actor`, `channel`, `future_promise`, `async_await`, `fork_join`, `producer_consumer`, `reactor`, `proactor`, `csp`

### ML/Data pipelines

**`MLModelType`** — Types of machine learning models  
Values (10): `classification`, `regression`, `clustering`, `recommendation`, `nlp`, `computer_vision`, `generative`, `reinforcement_learning`, `time_series`, `anomaly_detection`

**`DataPipelineType`** — Types of data pipelines  
Values (7): `etl`, `elt`, `streaming`, `feature_engineering`, `training`, `inference`, `data_quality`

**`DataPipelineStepType`** — Types of data pipeline steps  
Values (11): `extract`, `transform`, `load`, `validate`, `deduplicate`, `enrich`, `aggregate`, `partition`, `train`, `evaluate`, `deploy_model`

### Infrastructure as Code

**`IaCToolType`** — Types of infrastructure-as-code tools  
Values (11): `terraform`, `cloudformation`, `pulumi`, `ansible`, `chef`, `puppet`, `kubernetes_manifest`, `helm`, `docker_compose`, `bicep`, `cdk`

**`IaCResourceType`** — Types of infrastructure resources defined in code  
Values (10): `compute`, `network`, `storage`, `database`, `messaging`, `identity`, `monitoring`, `dns`, `cdn`, `secret`

### Type system

**`TypeKind`** — Classification of type expressions  
Values (13): `primitive`, `generic`, `union`, `intersection`, `alias`, `pointer`, `reference`, `array_of`, `function_type`, `tuple_type`, `optional_type`, `constrained` (Type with constraints (e.g., sized, bounded)), `opaque`

### Error handling

**`ErrorHandlingStrategy`** — Language-level error handling paradigms  
Values (6): `exception_based`, `return_value_based` (Errors returned as values (Go, Rust Result)), `condition_based` (Common Lisp condition system), `error_code_based` (Integer/enum error codes (C, COBOL)), `panic_recover` (Go-style panic/recover), `monadic` (Haskell Either/Maybe, Rust Result)

**`ExceptionCheckedness`** — Whether exceptions must be declared/caught  
Values (3): `checked` (Compiler-enforced handling (Java checked)), `unchecked` (No compile-time enforcement), `not_applicable` (Language does not use exceptions)

### File I/O

**`FileOrganization`** — How records are organized within a file  
Values (10): `sequential`, `indexed`, `relative`, `vsam_ksds` (VSAM Key-Sequenced Data Set), `vsam_esds` (VSAM Entry-Sequenced Data Set), `vsam_rrds` (VSAM Relative Record Data Set), `partitioned_dataset` (Partitioned dataset (PDS/PDSE)), `generation_data_group` (Generation data group (GDG)), `line_sequential`, `heap`

**`FileAccessMode`** — How records are accessed during I/O  
Values (3): `sequential_access`, `random_access`, `dynamic_access` (Both sequential and random in same open)

**`RecordFormat`** — Physical record format on storage  
Values (5): `fixed`, `variable`, `undefined`, `spanned` (Records spanning multiple blocks), `stream`

**`FileOperationType`** — Types of file I/O operations  
Values (9): `read`, `write`, `rewrite` (Update existing record in place), `delete`, `start` (Position cursor for sequential read), `open`, `close`, `sort`, `merge`

### Screen/Terminal

**`ScreenType`** — Types of terminal/screen definitions  
Values (5): `bms_map` (CICS Basic Mapping Support map), `rpg_display_file` (RPG display file (DSPF)), `character_terminal` (Generic character-mode terminal), `tui` (Text User Interface (ncurses, etc.)), `form_based` (Form-based screen definition)

### Job control

**`JobStepType`** — Types of job steps in batch processing  
Values (6): `exec_program` (Execute a program), `exec_proc` (Execute a cataloged procedure), `utility` (Run a system utility (SORT, IEBCOPY, etc.)), `sort`, `file_transfer`, `conditional` (Conditional step based on return codes)

**`DatasetDisposition`** — Dataset allocation dispositions (JCL)  
Values (7): `new_dataset`, `old_dataset`, `shared`, `modify`, `catalog`, `delete_disp`, `pass` (Pass dataset to next step)

### IPC

**`IPCMechanism`** — Inter-process communication mechanisms  
Values (17): `cics_link` (CICS LINK to another program), `cics_xctl` (CICS XCTL transfer of control), `ims_schedule` (IMS message scheduling), `shared_memory`, `pipe`, `rmi` (Java Remote Method Invocation), `corba`, `database_mediated` (Communication via shared database tables), `message_queue`, `socket`, `named_pipe`, `signal`, `semaphore`, `dcom`, `rest_call` (HTTP-based inter-process call), `grpc_call` (gRPC inter-process call), `event_bus` (Event bus communication)

### Preprocessor

**`MetaprogrammingType`** — Types of preprocessor/metaprogramming mechanisms  
Values (9): `c_preprocessor`, `rust_macro_declarative`, `rust_macro_procedural`, `cobol_copy_replacing` (COBOL COPY ... REPLACING statement), `template_metaprogramming` (C++ template metaprogramming), `python_metaclass`, `lisp_macro`, `java_annotation_processor`, `code_generator`

### Memory/Ownership

**`OwnershipModel`** — Memory ownership models  
Values (9): `owned`, `borrowed_shared` (Shared/immutable borrow (Rust &T)), `borrowed_mutable` (Exclusive mutable borrow (Rust &mut T)), `moved`, `copied`, `reference_counted` (Rc/Arc (Rust), shared_ptr (C++)), `garbage_collected`, `manual` (Manual malloc/free), `stack_allocated`

**`LifetimeScope`** — Lifetime/scope of a value  
Values (5): `static_lifetime`, `function_scope`, `block_scope`, `named_lifetime` (Rust named lifetime ('a)), `heap_lifetime`

### Database schema

**`DatabaseConstraintType`** — Types of database constraints  
Values (5): `primary_key`, `foreign_key`, `unique`, `check`, `not_null`

**`IndexType`** — Types of database indexes  
Values (4): `btree`, `hash`, `gin` (Generalized Inverted Index (PostgreSQL)), `fulltext`

### Architectural patterns

**`ArchitecturalPatternType`** — Types of architectural patterns  
Values (20): `cqrs` (Command Query Responsibility Segregation), `event_sourcing` (Event sourcing pattern), `hexagonal` (Hexagonal (ports and adapters) architecture), `clean_architecture` (Clean architecture (Uncle Bob)), `layered` (Traditional layered architecture), `microservice` (Microservice architecture), `modular_monolith` (Modular monolith architecture), `pipe_and_filter` (Pipe and filter architecture), `saga` (Saga pattern for distributed transactions), `strangler_fig` (Strangler fig migration pattern), `bff` (Backend for Frontend pattern), `api_gateway` (API gateway pattern), `sidecar` (Sidecar pattern), `event_driven` (Event-driven architecture), `batch_sequential` (Batch sequential processing), `transaction_script` (Transaction script pattern), `table_module` (Table module pattern), `domain_model` (Domain model pattern), `repository` (Repository pattern), `plugin` (Plugin architecture)

### Knowledge artifacts

**`KnowledgeArtifactType`** — Types of knowledge artifacts  
Values (13): `adr` (Architecture Decision Record), `readme` (README documentation), `design_doc` (Design document), `runbook` (Operational runbook), `wiki_page` (Wiki page), `api_doc` (API documentation), `onboarding_guide` (Onboarding guide), `postmortem` (Incident postmortem), `changelog` (Changelog), `comment` (Code or review comment), `diagram` (Architecture or design diagram), `rfc` (Request for Comments), `sop` (Standard Operating Procedure)

**`KnowledgeArtifactStatus`** — Status of a knowledge artifact  
Values (6): `draft`, `published`, `accepted`, `superseded`, `deprecated`, `archived`

### Programming language

**`ProgrammingParadigm`** — Programming paradigms  
Values (7): `object_oriented`, `procedural`, `functional`, `logic`, `concatenative`, `data_driven`, `multi_paradigm`

---

## Appendix C: Complete Bidirectional Relationship Pairs (226 rows)

Every bidirectional relationship in the SAO. Each row shows one pair: the forward attribute on Class A and its inverse on Class B. See [Section 10](#10-the-glue-bidirectional-relationships) for how these bridges work.

> **Note on the count:** This appendix lists 226 rows, while the summary in Section 2 counts 214 symmetric pairs. The difference arises from two factors: (1) 16 rows here are polymorphic expansions — attributes like `annotates_element`, `imports_symbols`, `defined_in_container`, and `contains_callable_units` use `any_of` ranges targeting multiple classes, so one logical relationship is expanded into separate rows per target class even though only one side declares the `inverse:` in the schema; (2) the Section 2 total includes 4 global slot pairs that are not listed in this appendix.

### Layer 3: Code structure (73 pairs)

| Class A | Attribute (forward) | Class B | Attribute (inverse) |
|---|---|---|---|
| `Annotation` | `annotates_element` | `EncapsulationUnit` | `annotated_by` |
| `Annotation` | `annotates_element` | `CallableUnit` | `annotated_by` |
| `Annotation` | `annotates_element` | `DataStructure` | `annotated_by` |
| `Annotation` | `annotates_element` | `DataElement` | `annotated_by` |
| `CallableUnit` | `callable_affected_by_directives` | `PreprocessorDirective` | `directive_affects_callables` |
| `CallableUnit` | `has_file_operations` | `FileOperation` | `performed_in_callable` |
| `CallableUnit` | `contains_blocks` | `CodeBlock` | `contained_in_callable` |
| `CallableUnit` | `defined_in_container` | `CodeContainer` | `contains_code_elements` |
| `CallableUnit` | `handles_exception_types` | `ExceptionType` | `handled_by_callables` |
| `CallableUnit` | `has_parameters` | `Parameter` | `parameter_of` |
| `CallableUnit` | `implements_operation` | `Operation` | `implemented_by_callables` |
| `CallableUnit` | `invokes_callables` | `CallableUnit` | `invoked_by_callables` |
| `CallableUnit` | `overrides_callable` | `CallableUnit` | `overridden_by_callables` |
| `CallableUnit` | `raises_exception_types` | `ExceptionType` | `raised_by_callables` |
| `CallableUnit` | `has_return_type` | `TypeExpression` | `return_type_of_callables` |
| `CallableUnit` | `tested_by_cases` | `TestCase` | `tests_callable` |
| `CallableUnit` | `uses_concurrency_primitives` | `ConcurrencyPrimitive` | `used_by_callables` |
| `CallableUnit` | `uses_file_definitions` | `FileDefinition` | `used_by_callables` |
| `CodeBlock` | `contains_statements` | `Statement` | `contained_in_block` |
| `CodeBlock` | `has_parent_block` | `CodeBlock` | `has_child_blocks` |
| `CodeContainer` | `contained_in_storage_location` | `StorageLocation` | `contains_containers` |
| `CodeContainer` | `has_file_definitions` | `FileDefinition` | `file_defined_in_container` |
| `CodeContainer` | `has_preprocessor_directives` | `PreprocessorDirective` | `directive_defined_in_container` |
| `CodeContainer` | `has_screen_definitions` | `ScreenDefinition` | `screen_defined_in_container` |
| `CodeContainer` | `contains_knowledge_artifacts` | `KnowledgeArtifact` | `stored_in_container` |
| `CodeContainer` | `has_references` | `DefinitionReference` | `referencing_container` |
| `CodeContainer` | `implements_component` | `Component` | `implemented_by_code` |
| `CodeContainer` | `includes_definitions` | `CodeContainer` | `included_in_containers` |
| `CodeContainer` | `referenced_via` | `DefinitionReference` | `referenced_container` |
| `CodeContainer` | `references_containers` | `CodeContainer` | `referenced_by_containers` |
| `CodeContainer` | `written_in_language` | `ProgrammingLanguage` | `language_used_by_containers` |
| `DataElement` | `contained_in_unit` | `EncapsulationUnit` | `contains_callable_units` |
| `DataElement` | `declared_type` | `TypeExpression` | `type_of_data_elements` |
| `DataElement` | `mapped_from_screen_fields` | `ScreenField` | `maps_to_data_element` |
| `DataElement` | `maps_to_attribute` | `Attribute` | `mapped_from_element` |
| `DataElement` | `has_ownership_annotations` | `OwnershipAnnotation` | `annotates_data_element` |
| `DataElement` | `has_parent_element` | `DataElement` | `has_child_elements` |
| `DataElement` | `protected_by_primitive` | `ConcurrencyPrimitive` | `protects_data_elements` |
| `DataStructure` | `contained_in_unit` | `EncapsulationUnit` | `contains_callable_units` |
| `DataStructure` | `defined_in_container` | `CodeContainer` | `contains_code_elements` |
| `DataStructure` | `maps_to_domain_entity` | `DomainEntity` | `mapped_from_structure` |
| `DataStructure` | `maps_to_value_object` | `ValueObject` | `mapped_from_structure_vo` |
| `DataStructure` | `has_parent_structure` | `DataStructure` | `has_child_structures` |
| `DataStructure` | `passed_via_ipc` | `IPCConnection` | `ipc_passes_data` |
| `DataStructure` | `persisted_in_collection` | `Collection` | `persists_structures` |
| `DataStructure` | `structure_contains_elements` | `DataElement` | `contained_in_structure` |
| `DefinitionReference` | `imports_symbols` | `EncapsulationUnit` | `imported_via` |
| `DefinitionReference` | `imports_symbols` | `CallableUnit` | `imported_via` |
| `DefinitionReference` | `imports_symbols` | `DataStructure` | `imported_via` |
| `EncapsulationUnit` | `affected_by_directives` | `PreprocessorDirective` | `directive_affects_encapsulation_units` |
| `EncapsulationUnit` | `contains_callable_units` | `CallableUnit` | `contained_in_unit` |
| `EncapsulationUnit` | `defined_in_container` | `CodeContainer` | `contains_code_elements` |
| `EncapsulationUnit` | `encapsulation_unit_renders_ui` | `UIComponent` | `ui_implements_encapsulation_unit` |
| `EncapsulationUnit` | `error_model_for_module` | `ErrorModel` | `modules_using_error_model` |
| `EncapsulationUnit` | `executed_by_job_steps` | `JobStep` | `step_executes_program` |
| `EncapsulationUnit` | `extends_units` | `EncapsulationUnit` | `extended_by_units` |
| `EncapsulationUnit` | `implements_component` | `Component` | `implemented_by_code` |
| `EncapsulationUnit` | `implements_contracts` | `Contract` | `implemented_by_units` |
| `EncapsulationUnit` | `has_incoming_ipc_connections` | `IPCConnection` | `has_target_program` |
| `EncapsulationUnit` | `memory_model_for_module` | `MemoryModel` | `modules_using_memory_model` |
| `EncapsulationUnit` | `has_outgoing_ipc_connections` | `IPCConnection` | `has_source_program` |
| `EncapsulationUnit` | `screen_used_by_programs` | `ScreenDefinition` | `program_uses_screens` |
| `ErrorModel` | `error_model_for_languages` | `ProgrammingLanguage` | `has_default_error_model` |
| `ExceptionType` | `has_parent_exception` | `ExceptionType` | `has_child_exceptions` |
| `FileDefinition` | `file_operations` | `FileOperation` | `operates_on_file` |
| `FileDefinition` | `mapped_from_dataset_allocations` | `DatasetAllocation` | `maps_to_file_definition` |
| `JobDefinition` | `contains_job_steps` | `JobStep` | `step_in_job` |
| `JobDefinition` | `depends_on_jobs` | `JobDefinition` | `depended_on_by_jobs` |
| `JobStep` | `allocates_datasets` | `DatasetAllocation` | `allocated_in_step` |
| `MemoryModel` | `memory_model_for_languages` | `ProgrammingLanguage` | `has_default_memory_model` |
| `Parameter` | `has_type` | `TypeExpression` | `type_of_parameters` |
| `ScreenDefinition` | `contains_screen_fields` | `ScreenField` | `field_on_screen` |
| `StorageLocation` | `has_parent_location` | `StorageLocation` | `contains_locations` |

### Layer 4: Architecture and integration (47 pairs)

| Class A | Attribute (forward) | Class B | Attribute (inverse) |
|---|---|---|---|
| `BoundedContext` | `contains_aggregates` | `Aggregate` | `contained_in_bounded_context` |
| `BoundedContext` | `contains_modules` | `Module` | `contained_in_context` |
| `BoundedContext` | `context_documented_by_artifacts` | `KnowledgeArtifact` | `documents_bounded_context` |
| `BoundedContext` | `upstream_from` | `BoundedContext` | `downstream_from` |
| `Component` | `component_documented_by_artifacts` | `KnowledgeArtifact` | `documents_component` |
| `Component` | `component_serves_model` | `MLModel` | `model_served_by_component` |
| `Component` | `component_uses_concurrency_pattern` | `ConcurrencyPattern` | `pattern_used_by_component` |
| `Component` | `emits_events` | `Event` | `emitted_by_component` |
| `Component` | `emits_metric` | `Metric` | `metric_emitted_by_component` |
| `Component` | `exposes_operations` | `Operation` | `exposed_by_component` |
| `Component` | `has_coverage` | `TestCoverage` | `coverage_for_component` |
| `Component` | `tested_by_suites` | `TestSuite` | `tests_component` |
| `Contract` | `has_versions` | `ContractVersion` | `version_of_contract` |
| `EventInterface` | `has_subscriptions` | `Subscription` | `subscribes_to_interface` |
| `ExternalSystem` | `integrated_via` | `Integration` | `integrates_with_system` |
| `Integration` | `integration_documented_by_artifacts` | `KnowledgeArtifact` | `documents_integration` |
| `Integration` | `integration_governed_by_contract` | `Contract` | `governs_integrations` |
| `Integration` | `protected_by_breaker` | `CircuitBreaker` | `protects_integrations` |
| `Integration` | `uses_adapter` | `Adapter` | `used_by_integrations` |
| `Interface` | `defined_by_contract` | `Contract` | `defines_interfaces` |
| `Message` | `validated_by_contract` | `Contract` | `validates_messages` |
| `Module` | `contains_components` | `Component` | `contained_in_module` |
| `Module` | `depends_on_module` | `Module` | `depended_on_by_module` |
| `Module` | `mapped_from_directory` | `StorageLocation` | `maps_to_module` |
| `Module` | `module_documented_by_artifacts` | `KnowledgeArtifact` | `documents_module` |
| `Module` | `module_has_coverage` | `TestCoverage` | `coverage_for_module` |
| `Module` | `module_has_dependencies` | `PackageDependency` | `dependency_of_module` |
| `Module` | `module_managed_by_package_manager` | `PackageManager` | `manages_dependencies_for_module` |
| `Module` | `module_tested_by_suites` | `TestSuite` | `tests_module` |
| `Module` | `provides_capabilities` | `Capability` | `provided_by_modules` |
| `Module` | `runs_as_services` | `Service` | `runs_module` |
| `ProgrammaticInterface` | `has_endpoints` | `Endpoint` | `belongs_to_interface` |
| `Screen` | `offers_operations` | `Operation` | `offered_on_screens` |
| `Service` | `affected_by_incidents` | `Incident` | `affects_services` |
| `Service` | `depends_on_service` | `Service` | `depended_on_by_service` |
| `Service` | `deployed_as` | `Deployment` | `deploys_service` |
| `Service` | `exposes_endpoints` | `Endpoint` | `exposed_by_service` |
| `Service` | `receives_integration_events` | `IntegrationEvent` | `targeted_at_services` |
| `Service` | `service_documented_by_artifacts` | `KnowledgeArtifact` | `documents_service` |
| `System` | `assessed_by` | `RiskAssessment` | `assesses_system` |
| `System` | `contains_bounded_contexts` | `BoundedContext` | `contained_in_system` |
| `System` | `enforces_policies` | `Policy` | `enforced_by_system` |
| `System` | `exposes_interfaces` | `Interface` | `exposed_by_system` |
| `System` | `has_integrations` | `Integration` | `belongs_to_system` |
| `System` | `must_comply_with` | `ComplianceRequirement` | `applies_to_systems` |
| `System` | `system_documented_by_artifacts` | `KnowledgeArtifact` | `documents_system` |
| `UserInterface` | `contains_screens` | `Screen` | `part_of_ui` |

### Layer 5: Domain model (41 pairs)

| Class A | Attribute (forward) | Class B | Attribute (inverse) |
|---|---|---|---|
| `Aggregate` | `aggregate_documented_by_artifacts` | `KnowledgeArtifact` | `documents_aggregate` |
| `Aggregate` | `aggregates_entities` | `DomainEntity` | `aggregated_by` |
| `Aggregate` | `enforced_by_invariant_rules` | `Rule` | `enforces_aggregate_invariants` |
| `Aggregate` | `has_root_entity` | `DomainEntity` | `is_root_of_aggregate` |
| `Aggregate` | `persisted_in_stores` | `DataStore` | `persists_aggregates` |
| `Aggregate` | `produces_domain_events` | `DomainEvent` | `produced_by_aggregate` |
| `Attribute` | `validated_by_rules` | `Rule` | `validates_attributes` |
| `Collection` | `collection_structured_by_schema` | `Schema` | `structures_collections` |
| `Collection` | `governed_by_retention_policy` | `RetentionPolicy` | `governs_collections` |
| `Collection` | `has_constraints` | `DatabaseConstraint` | `constraint_on_collection` |
| `Collection` | `has_indexes` | `DatabaseIndex` | `index_on_collection` |
| `Collection` | `stores_records` | `Record` | `stored_in_collection` |
| `DataStore` | `hosted_on_infrastructure` | `Infrastructure` | `hosts_datastores` |
| `DataStore` | `store_file_definitions` | `FileDefinition` | `persisted_in_store` |
| `DataStore` | `store_read_by_pipelines` | `DataPipeline` | `pipeline_reads_from_stores` |
| `DataStore` | `store_written_by_pipelines` | `DataPipeline` | `pipeline_writes_to_stores` |
| `DomainEntity` | `entity_documented_by_artifacts` | `KnowledgeArtifact` | `documents_domain_entity` |
| `DomainEntity` | `exposes_as_resource` | `Resource` | `represents_entity` |
| `DomainEntity` | `governed_by_lifecycle` | `Lifecycle` | `governs_entities` |
| `DomainEntity` | `governed_by_rules` | `Rule` | `governs_domain_entities` |
| `DomainEntity` | `in_state` | `State` | `current_for_entities` |
| `DomainEntity` | `has_incoming_relationships` | `DomainRelationship` | `has_target_entity` |
| `DomainEntity` | `has_outgoing_relationships` | `DomainRelationship` | `has_source_entity` |
| `Record` | `conforms_to_schema` | `Schema` | `validates_records` |
| `Record` | `has_lineage` | `DataLineage` | `tracks_record` |
| `Record` | `source_of_lineage` | `DataLineage` | `derived_from_records` |
| `Resource` | `affected_in_audit` | `AuditEntry` | `affects_resource` |
| `Resource` | `classified_as_type` | `ResourceType` | `classifies_resources` |
| `Resource` | `targeted_by_actions` | `Action` | `targets_resources` |
| `ResourceType` | `structured_by_schema` | `Schema` | `structures_resource_types` |
| `RetentionPolicy` | `governs_audit_logs` | `AuditLog` | `auditlog_governed_by_retention` |
| `RetentionPolicy` | `governs_logs` | `Log` | `log_governed_by_retention` |
| `Schema` | `has_versions` | `SchemaVersion` | `version_of_schema` |
| `Schema` | `structures_messages` | `Message` | `message_structured_by_schema` |
| `State` | `allows_actions_in_state` | `Action` | `allowed_in_states` |
| `State` | `initial_for_lifecycle` | `Lifecycle` | `starts_with_state` |
| `State` | `source_of_transitions` | `Transition` | `transitions_from_state` |
| `State` | `target_of_transitions` | `Transition` | `transitions_to_state` |
| `Transition` | `executes_actions_on_transition` | `Action` | `executed_during_transition` |
| `Transition` | `guarded_by_rules` | `Rule` | `guards_transitions` |
| `Transition` | `triggered_by_events` | `Event` | `triggers_transitions` |

### Layer 6: Business intent (25 pairs)

| Class A | Attribute (forward) | Class B | Attribute (inverse) |
|---|---|---|---|
| `Action` | `emits_events_from_action` | `Event` | `emitted_by_action` |
| `Action` | `executed_by_operation` | `Operation` | `executes_operation_actions` |
| `Action` | `executed_in_step` | `Step` | `executes_actions_in_step` |
| `Action` | `executes_in_transaction` | `Transaction` | `executes_actions` |
| `Action` | `recorded_in_audit` | `AuditEntry` | `records_action` |
| `Action` | `validated_by_action_rules` | `Rule` | `validates_actions` |
| `Actor` | `has_subscriptions` | `Subscription` | `subscribed_by_actor` |
| `Actor` | `audit_actions_performed` | `AuditEntry` | `audit_performed_by_actor` |
| `Actor` | `has_identities` | `Identity` | `represents_actor` |
| `Actor` | `owns_controls` | `Control` | `owned_by_actor` |
| `Actor` | `performs_actions` | `Action` | `performed_by_actor` |
| `Actor` | `verifies_evidence` | `Evidence` | `verified_by_actor` |
| `Capability` | `enables_features` | `Feature` | `enabled_by_capabilities` |
| `Capability` | `realizes_features` | `Feature` | `realized_by_capabilities` |
| `Capability` | `requires_permissions` | `Permission` | `required_by_capabilities` |
| `Event` | `event_structured_by_schema` | `Schema` | `structures_events` |
| `Event` | `subscribed_by_subscriptions` | `Subscription` | `subscribes_to_event_types` |
| `Feature` | `accessible_by_roles` | `Role` | `can_access_features` |
| `Feature` | `controlled_by_configs` | `Configuration` | `controls_features` |
| `Operation` | `accepts_input_schema` | `Schema` | `defines_operation_input` |
| `Operation` | `operation_tested_by_cases` | `TestCase` | `tests_operation` |
| `Operation` | `produces_output_schema` | `Schema` | `defines_operation_output` |
| `Step` | `compensated_by_step` | `Step` | `compensates_for_step` |
| `Step` | `followed_by_steps` | `Step` | `follows_step` |
| `Workflow` | `triggered_by_workflow_events` | `Event` | `triggers_workflows` |

### Cross-cutting: Security, governance, quality, knowledge (22 pairs)

| Class A | Attribute (forward) | Class B | Attribute (inverse) |
|---|---|---|---|
| `AuditLog` | `contains_entries` | `AuditEntry` | `entry_in_audit_log` |
| `BuildArtifact` | `artifact_stored_in_registry` | `ArtifactRegistry` | `stores_artifacts` |
| `BuildPipeline` | `pipeline_produces_artifacts` | `BuildArtifact` | `artifact_produced_by_pipeline` |
| `BuildPipeline` | `pipeline_trains_model` | `MLModel` | `model_trained_by_pipeline` |
| `BuildPipeline` | `pipeline_uses_iac` | `IaCDefinition` | `iac_used_by_pipeline` |
| `Control` | `mitigates_risks` | `RiskAssessment` | `mitigated_by_controls` |
| `Identity` | `belongs_to_tenant` | `Tenant` | `contains_identities` |
| `Identity` | `has_roles` | `Role` | `assigned_to_identities` |
| `Identity` | `member_of_organizations` | `Organization` | `has_identity_members` |
| `PackageDependency` | `has_transitive_dependencies` | `PackageDependency` | `transitive_dependency_of` |
| `Permission` | `allows_actions` | `Action` | `allowed_by_permissions` |
| `Permission` | `applies_to_resource_types` | `ResourceType` | `governed_by_permissions` |
| `Permission` | `evaluated_by_policies` | `Policy` | `evaluates_permissions` |
| `Permission` | `limited_by_scope` | `Scope` | `limits_permissions` |
| `Policy` | `guards_routes` | `Route` | `route_guarded_by` |
| `Role` | `grants_permissions` | `Permission` | `granted_by_roles` |
| `Role` | `inherits_from_role` | `Role` | `inherited_by_roles` |
| `Route` | `has_parent_route` | `Route` | `has_child_routes` |
| `TestSuite` | `contains_test_cases` | `TestCase` | `belongs_to_suite` |
| `UIComponent` | `managed_by_state` | `StateStore` | `manages_ui_components` |
| `UIComponent` | `has_parent_ui_component` | `UIComponent` | `has_child_ui_components` |
| `UIComponent` | `renders_on_route` | `Route` | `route_renders_component` |

### Cross-cutting: Runtime, ops, infrastructure (18 pairs)

| Class A | Attribute (forward) | Class B | Attribute (inverse) |
|---|---|---|---|
| `Alert` | `escalates_to_incident` | `Incident` | `escalated_from_alerts` |
| `Alert` | `triggered_by_rule` | `AlertRule` | `triggers_alerts` |
| `Dataset` | `dataset_used_by_pipeline` | `DataPipeline` | `pipeline_uses_dataset` |
| `Deployment` | `deployment_configured_by` | `Configuration` | `configures_deployments` |
| `Deployment` | `deploys_release` | `Release` | `deployed_in_deployments_as_release` |
| `Deployment` | `deploys_unit` | `DeploymentUnit` | `deployed_in_deployments` |
| `Environment` | `deployed_by_pipelines` | `BuildPipeline` | `pipeline_deploys_to_environments` |
| `Environment` | `env_configured_by` | `Configuration` | `configures_environments` |
| `Environment` | `hosts_deployments` | `Deployment` | `deployed_in_environment` |
| `Environment` | `uses_infrastructure` | `Infrastructure` | `used_by_environments` |
| `Infrastructure` | `infrastructure_provisioned_by_iac` | `IaCDefinition` | `iac_provisions_infrastructure` |
| `Log` | `contains_entries` | `LogEntry` | `entry_in_log` |
| `MLModel` | `model_trained_by_pipeline` | `DataPipeline` | `pipeline_trains_model` |
| `MLModel` | `model_uses_feature_store` | `FeatureStore` | `provides_features_to_models` |
| `Metric` | `monitored_by_alert_rules` | `AlertRule` | `monitors_metrics` |
| `Span` | `child_of_span` | `Span` | `parent_of_spans` |
| `Trace` | `starts_with_span` | `Span` | `root_of_trace` |
| `Trace` | `contains_spans` | `Span` | `belongs_to_trace` |
