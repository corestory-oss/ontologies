# 11. Reference Material

> SAO Extraction Playbook -- Appendix

This appendix consolidates the reference tables, decision trees, and taxonomies
referenced throughout the extraction playbook. Use it as a quick-lookup companion
during any extraction phase.

---

## 11.1 Extraction Technique Reference

Each row maps a concrete technique to the SAO classes it populates. The
*Automation level* column indicates how much of the work a tool can do
without human judgment.

| Technique | What it extracts | SAO classes populated | Automation |
|---|---|---|---|
| File system traversal | Directory structure, file inventory | **StorageLocation**, **CodeContainer**, **ProgrammingLanguage** | High |
| Dependency manifest parsing | Package dependencies | **PackageManager**, **PackageDependency**, **KnownVulnerability** | High |
| AST parsing | Code structure | **EncapsulationUnit**, **CallableUnit**, **DataStructure**, **DataElement**, **Parameter**, **TypeExpression** | High |
| Import/include analysis | Code references | **DefinitionReference** | High |
| Call graph construction | Invocation relationships | **ControlFlow** | High |
| Data flow analysis | Read/write patterns | **DataFlow** | Medium-High |
| Deployment manifest parsing | Runtime topology | **Service**, **Deployment**, **Environment**, **Infrastructure**, **DeploymentUnit** | High |
| API schema parsing | Interface contracts | **Interface**, **Endpoint**, **Contract**, **Schema** | High |
| Database schema extraction | Persistence model | **DataStore**, **Collection**, **DatabaseConstraint**, **DatabaseIndex** | High |
| Package/directory heuristics | Architectural grouping | **Module**, **Component** | Medium |
| Naming convention analysis | Stereotypes, roles | **Component** type classification | Medium |
| CI/CD config parsing | Build/deploy pipelines | **BuildPipeline**, **PipelineStage**, **BuildArtifact** | High |
| Test file analysis | Test inventory | **TestSuite**, **TestCase**, **TestCoverage** | High |
| LLM semantic inference (domain) | Domain model | **DomainEntity**, **ValueObject**, **Aggregate**, **DomainRelationship** | Medium-Low |
| LLM semantic inference (business) | Business intent | **Actor**, **Operation**, **Rule**, **Workflow**, **Capability**, **Feature** | Low |
| LLM document analysis | Documentation content | **KnowledgeArtifact**, **Actor**, **Feature**, **ComplianceRequirement** | Medium-Low |
| Runtime analysis (APM/traces) | Dynamic behavior | **Trace**, **Span**, **Metric** | Medium |
| Manual expert review | Business validation | All higher-layer classes | Manual |

**Reading the table.** A technique tagged *High* can run unattended and its
output can be trusted without review. *Medium* outputs SHOULD be spot-checked.
*Low* and *Manual* outputs MUST be reviewed by a domain expert before they are
considered authoritative.

---

## 11.2 SAO Class Checklist by Extraction Phase

The tables below map every one of the 147 SAO classes to its **primary**
extraction phase. Some classes could reasonably appear in more than one phase;
the assignment reflects where the class is *first* created and populated. Later
phases MAY enrich attributes added in an earlier phase.

For each class, **required attributes** (those marked `required: true` in
`legacy/sao/sao.yml`) are listed after the arrow. Every class inherits `id` and `name`
from **NamedEntity** (except **Metadata**, **Versionable**, and **Auditable**,
which are standalone).

### Base classes and mixins (4 classes)

These are not extracted directly; they provide inherited structure.

| Class | Required attrs | Notes |
|---|---|---|
| **NamedEntity** | `id`, `name` | Abstract base for all named entities |
| **Metadata** | *(none beyond inherited)* | Attached automatically to entities |
| **Versionable** | *(none beyond inherited)* | Mixin for versioned entities |
| **Auditable** | *(none beyond inherited)* | Mixin for auditable entities |

### Phase 1 -- Inventory (6 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **StorageLocation** | `location_path` | Directories, repositories, library members |
| **CodeContainer** | `container_path` | Source files, COBOL copybooks, includes |
| **ProgrammingLanguage** | *(none beyond inherited)* | Detected from file extensions / shebang lines |
| **PackageManager** | `manager_type` | npm, pip, Maven, NuGet, etc. |
| **PackageDependency** | `package_name` | One entry per declared dependency |
| **KnownVulnerability** | `severity` | From CVE databases / `npm audit` / Snyk |

### Phase 2 -- Code Structure (27 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **EncapsulationUnit** | `encapsulation_type` | Class, module, program, namespace |
| **CallableUnit** | `callable_type` | Method, function, paragraph, subroutine |
| **DataStructure** | `structure_type` | Struct, record, class data, type alias |
| **DataElement** | `data_type` | Field, variable, column, property |
| **Parameter** | `data_type` | Inherits from **DataElement** |
| **TypeExpression** | `type_kind` | Generic, union, pointer, function type |
| **ControlFlow** | *(none beyond inherited)* | Call edges between callable units |
| **DataFlow** | *(none beyond inherited)* | Read/write edges between elements |
| **DefinitionReference** | *(none beyond inherited)* | Import, include, COPY, using |
| **CodeBlock** | *(none beyond inherited)* | Logical groupings within callables |
| **Statement** | *(none beyond inherited)* | Individual instructions or declarations |
| **Annotation** | *(none beyond inherited)* | Decorators, attributes, pragmas |
| **PlatformExtension** | *(none beyond inherited)* | Abstract base for platform-specific classes |
| **ExecutionEnvironmentDirective** | *(none beyond inherited)* | JCL, Docker Compose, Makefiles |
| **FileDefinition** | *(none beyond inherited)* | COBOL SELECT, C fopen targets |
| **FileOperation** | `operation_type` | Read, write, rewrite, delete on files |
| **ScreenDefinition** | `screen_type` | BMS maps, CICS screens, curses forms |
| **ScreenField** | *(none beyond inherited)* | Individual fields on screen definitions |
| **JobDefinition** | *(none beyond inherited)* | JCL JOB, cron entries, scheduler jobs |
| **JobStep** | `step_type` | EXEC PGM, EXEC PROC, script steps |
| **DatasetAllocation** | *(none beyond inherited)* | DD allocations within job steps |
| **IPCConnection** | `mechanism` | MQ, TCP, pipes, shared memory |
| **PreprocessorDirective** | `directive_type` | #define, #include, macros, templates |
| **ErrorModel** | `strategy` | Per-module error handling approach |
| **ExceptionType** | *(none beyond inherited)* | Declared exception/error types |
| **MemoryModel** | `primary_model` | GC, manual, ownership, reference-counted |
| **OwnershipAnnotation** | `ownership` | Rust lifetimes, C++ smart pointers |

### Phase 3 -- Architecture and Integration (20 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **System** | *(none beyond inherited)* | Top-level container |
| **BoundedContext** | *(none beyond inherited)* | DDD context boundary |
| **Module** | *(none beyond inherited)* | Deployable unit of functionality |
| **Component** | *(none beyond inherited)* | Logical building block within a module |
| **Service** | *(none beyond inherited)* | Independently deployable runtime unit |
| **Interface** | *(none beyond inherited)* | Abstract: contract-defined boundary |
| **UserInterface** | *(none beyond inherited)* | User-facing interface |
| **ProgrammaticInterface** | *(none beyond inherited)* | Machine-to-machine interface |
| **EventInterface** | *(none beyond inherited)* | Event-driven interface |
| **Screen** | *(none beyond inherited)* | Single screen/view in a UI |
| **Endpoint** | *(none beyond inherited)* | Addressable entry point on a service |
| **Subscription** | *(none beyond inherited)* | Registration to receive events |
| **ExternalSystem** | *(none beyond inherited)* | System outside the boundary |
| **Integration** | *(none beyond inherited)* | Configured connection to external system |
| **Contract** | *(none beyond inherited)* | Formal spec of integration behavior |
| **ContractVersion** | *(none beyond inherited)* | Specific iteration of a contract |
| **Adapter** | *(none beyond inherited)* | Translates between protocols |
| **CircuitBreaker** | *(none beyond inherited)* | Resilience pattern for cascading failures |
| **Dependency** | *(none beyond inherited)* | Lightweight dependency between components |
| **Message** | *(none beyond inherited)* | Unit of data exchanged in integration |

### Phase 4 -- Domain Model (18 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **Aggregate** | `has_root_entity` | DDD aggregate; MUST reference a root entity |
| **DomainEntity** | *(none beyond inherited)* | Uniquely identifiable domain object |
| **ValueObject** | *(none beyond inherited)* | Immutable, identity-less domain object |
| **Attribute** | `data_type` | Named property of entity or value object |
| **DomainRelationship** | `cardinality` | Typed relationship between domain entities |
| **Lifecycle** | *(none beyond inherited)* | Complete state machine for an entity type |
| **State** | *(none beyond inherited)* | Discrete condition in an entity lifecycle |
| **Transition** | `transitions_from_state`, `transitions_to_state` | Valid movement between states |
| **DataStore** | *(none beyond inherited)* | Persistence mechanism (RDBMS, NoSQL, etc.) |
| **Collection** | *(none beyond inherited)* | Table, collection, bucket |
| **Record** | *(none beyond inherited)* | Single persisted data instance |
| **Schema** | *(none beyond inherited)* | Structural definition of stored data |
| **SchemaVersion** | *(none beyond inherited)* | Specific iteration of a schema |
| **DataClassification** | *(none beyond inherited)* | Sensitivity or handling category |
| **RetentionPolicy** | *(none beyond inherited)* | Data lifecycle and deletion rules |
| **DatabaseConstraint** | `constraint_type` | Primary key, foreign key, unique, check |
| **DatabaseIndex** | `index_type` | B-tree, hash, full-text, spatial |
| **DataLineage** | *(none beyond inherited)* | Origin and transformation history |

### Phase 5 -- Business Intent (18 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **Actor** | *(none beyond inherited)* | Abstract: any entity that initiates actions |
| **HumanActor** | *(none beyond inherited)* | A human user of the system |
| **SystemActor** | *(none beyond inherited)* | An automated actor |
| **Operation** | *(none beyond inherited)* | Named unit of behavior on an interface |
| **Action** | *(none beyond inherited)* | Abstract: atomic operation |
| **Query** | *(none beyond inherited)* | Read-only action |
| **Command** | *(none beyond inherited)* | State-changing action |
| **Rule** | *(none beyond inherited)* | Declarative constraint or trigger |
| **AlertRule** | *(none beyond inherited)* | Condition that triggers an alert |
| **Event** | *(none beyond inherited)* | Notification that something occurred |
| **DomainEvent** | *(none beyond inherited)* | Significant domain occurrence |
| **IntegrationEvent** | *(none beyond inherited)* | Cross-service communication event |
| **Workflow** | *(none beyond inherited)* | Coordinated action sequence |
| **Step** | *(none beyond inherited)* | Discrete stage within a workflow |
| **Transaction** | *(none beyond inherited)* | Unit of work with ACID/BASE guarantees |
| **Resource** | *(none beyond inherited)* | Entity/VO exposed for external interaction |
| **ResourceType** | *(none beyond inherited)* | Classification of resources |
| **Capability** | *(none beyond inherited)* | Business or technical ability |
| **Feature** | *(none beyond inherited)* | User-facing manifestation of capabilities |

### Phase 6 -- Cross-Cutting Concerns (54 classes)

#### Security and identity (9 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **Identity** | *(none beyond inherited)* | Verified representation of an actor |
| **Credential** | *(none beyond inherited)* | Authentication material |
| **Tenant** | *(none beyond inherited)* | Multi-tenant boundary |
| **Organization** | *(none beyond inherited)* | Logical grouping of users/resources |
| **Role** | *(none beyond inherited)* | Named collection of permissions |
| **Permission** | *(none beyond inherited)* | Allowed action on a resource |
| **Policy** | *(none beyond inherited)* | Rule set governing access decisions |
| **Scope** | *(none beyond inherited)* | Boundary limiting permission applicability |
| **Constraint** | *(none beyond inherited)* | Condition for authorization |

#### Governance and compliance (5 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **ComplianceRequirement** | *(none beyond inherited)* | Regulatory or policy obligation |
| **Control** | *(none beyond inherited)* | Measure implementing a requirement |
| **Evidence** | *(none beyond inherited)* | Proof of control effectiveness |
| **RiskAssessment** | *(none beyond inherited)* | Threat/vulnerability evaluation |
| **KnowledgeArtifact** | *(none beyond inherited)* | Documentation artifact |

#### Audit (2 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **AuditLog** | *(none beyond inherited)* | Tamper-evident activity record |
| **AuditEntry** | `timestamp` | Single record in an audit log |

#### Testing (4 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **TestSuite** | `suite_type` | Collection of related test cases |
| **TestCase** | *(none beyond inherited)* | Single test validating behavior |
| **TestAssertion** | *(none beyond inherited)* | Individual assertion in a test |
| **TestCoverage** | *(none beyond inherited)* | Coverage metrics for a component |

#### UI/Frontend (4 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **UIComponent** | `component_type` | Frontend component rendering visuals |
| **UIProperty** | *(none beyond inherited)* | Prop passed to a UI component |
| **Route** | `path_pattern` | Navigation route or URL path |
| **StateStore** | `management_type` | Frontend state management container |

#### Build, CI/CD (4 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **BuildPipeline** | `pipeline_type` | CI/CD pipeline definition |
| **PipelineStage** | `stage_type` | Discrete stage in a pipeline |
| **BuildArtifact** | `artifact_type` | Artifact produced by a build |
| **ArtifactRegistry** | *(none beyond inherited)* | Registry for storing artifacts |

#### Deployment and operations (7 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **Release** | *(none beyond inherited)* | Versioned deployable package |
| **Environment** | *(none beyond inherited)* | Runtime context with configuration |
| **Deployment** | *(none beyond inherited)* | Service instance in an environment |
| **DeploymentUnit** | *(none beyond inherited)* | Packaged artifact being deployed |
| **Configuration** | *(none beyond inherited)* | Runtime parameters |
| **Infrastructure** | *(none beyond inherited)* | Compute, storage, and network resources |
| **HealthCheck** | *(none beyond inherited)* | Probe verifying service availability |

#### Observability (7 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **Metric** | *(none beyond inherited)* | Quantitative measurement over time |
| **Log** | *(none beyond inherited)* | Timestamped event record |
| **LogEntry** | *(none beyond inherited)* | Single record within a log |
| **Trace** | *(none beyond inherited)* | Causal chain across services |
| **Span** | *(none beyond inherited)* | Single unit of work in a trace |
| **Alert** | *(none beyond inherited)* | Notification from metric threshold |
| **Incident** | *(none beyond inherited)* | Tracked degradation or outage |

#### Concurrency (2 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **ConcurrencyPrimitive** | `primitive_type` | Mutex, semaphore, lock, barrier |
| **ConcurrencyPattern** | `pattern_type` | Actor model, CSP, thread pool |

#### ML/AI (5 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **MLModel** | `model_type` | ML model defined/trained/served |
| **MLModelMetric** | `metric_name` | Performance metric for an ML model |
| **Dataset** | *(none beyond inherited)* | Training, evaluation, or inference data |
| **FeatureStore** | *(none beyond inherited)* | Centralized store for ML features |
| **DataPipeline** | `pipeline_type` | ETL, feature engineering pipeline |
| **DataPipelineStep** | `step_type` | Discrete step in a data pipeline |

#### Infrastructure as Code (3 classes)

| Class | Required attrs | Notes |
|---|---|---|
| **IaCDefinition** | `tool` | Terraform, CloudFormation, Pulumi, etc. |
| **IaCResource** | `resource_type` | Single infrastructure resource in code |
| **IaCModule** | *(none beyond inherited)* | Reusable module of IaC definitions |

**Total: 4 base + 6 + 27 + 20 + 18 + 18 + 54 = 147 classes.**

---

## 11.3 Decision Trees

### Decision Tree 1: DataStructure Classification

Use this tree after Phase 2 (code structure extraction) to decide whether a
**DataStructure** should also be promoted to a Phase 4 domain entity.

```
Does this DataStructure have a unique identifier field?
├── YES: Does it have CRUD operations performed on it?
│   ├── YES: Is it persisted to storage?
│   │   ├── YES --> DomainEntity (high confidence)
│   │   └── NO  --> DomainEntity candidate (verify with domain expert)
│   └── NO: Is it immutable with no identity?
│       ├── YES --> ValueObject
│       └── NO  --> Likely just a DataStructure (no domain mapping)
└── NO: Is it immutable and used as a property of another structure?
    ├── YES --> ValueObject
    └── NO  --> Utility/transport structure (no domain mapping)
```

**Guidance.** When the answer is "DomainEntity candidate," create a
**DomainEntity** with `confidence: medium` and flag it for expert review in
Phase 5. Do NOT discard potential domain entities silently.

### Decision Tree 2: BoundedContext Boundary Identification

Use this tree in Phase 3 to decide how many **BoundedContext** instances to
create and where their boundaries lie.

```
Are there explicit context boundaries?
├── Separate databases
│   └── Each database boundary = one BoundedContext
├── Separate deployment units
│   └── Each deployment unit = one BoundedContext
├── DDD annotations present (@BoundedContext, module-info, etc.)
│   └── Follow annotated boundaries
├── Separate teams (CODEOWNERS, repo-per-team)
│   └── Each team's code = candidate BoundedContext
└── NO explicit boundaries:
    Look at top-level package/directory structure
    ├── Clear domain-oriented packages? (orders/, inventory/, users/)
    │   └── YES --> Each domain package = candidate BoundedContext
    └── NO  --> Start with one BoundedContext, refine later
```

**Guidance.** When multiple signals conflict (e.g., one database but separate
deploy units), prefer the boundary that yields the **most cohesive** domain
model. Document the reasoning in the **BoundedContext** `description` attribute.

### Decision Tree 3: Platform Extension Applicability

Use this tree at the start of Phase 2 to decide which platform-specific SAO
classes are relevant to the codebase.

```
What language/platform is the codebase?
├── COBOL / PL/I / RPG / Assembler (Mainframe):
│   └── Extract: FileDefinition, ScreenDefinition, ScreenField,
│       JobDefinition, JobStep, DatasetAllocation, IPCConnection
├── C / C++:
│   └── Extract: PreprocessorDirective, MemoryModel,
│       OwnershipAnnotation (C++ smart pointers)
├── Rust:
│   └── Extract: MemoryModel, OwnershipAnnotation
│       (ownership semantics, lifetimes)
├── Any language with macros / metaprogramming:
│   └── Extract: PreprocessorDirective
│       (set metaprogramming_type accordingly)
└── All languages:
    └── Extract: ErrorModel (per-module error handling strategy),
        ExceptionType (declared error/exception types)
```

**Guidance.** If the codebase uses multiple languages, apply the relevant
branches for each language. A polyglot system MAY have **MemoryModel** entries
for Rust components alongside **PreprocessorDirective** entries for C
components.

### Decision Tree 4: Rule vs. Workflow vs. Implementation Detail

Use this tree in Phase 5 when deciding whether a piece of logic deserves a
business-intent entity or should remain as code structure only.

```
Does this code enforce a business constraint or validate business data?
├── YES --> Rule
│   (set rule_category: validation, business, constraint, etc.)
│
Does this code coordinate multiple steps toward a business goal?
├── YES --> Workflow with Steps
│
Does this code simply implement a technical mechanism
with no business meaning?
├── YES --> Implementation detail
│   (leave in code structure; no Phase 5 entity)
│
Is this code a guard condition on a state transition?
├── YES --> Rule that guards a Transition
│   (link via the Transition's guard_conditions attribute)
```

**Guidance.** When in doubt, ask: "Would a business analyst recognize this
logic as meaningful?" If yes, it SHOULD be a **Rule** or **Workflow**. If only
a developer would care, it is an implementation detail.

---

## 11.4 Confidence Taxonomy

Every extracted entity SHOULD be mentally tagged with one of the following
confidence levels. This drives review prioritization: higher-layer entities
(inferential, manual) get reviewed first.

| Level | Definition | Typical phases | Review needed? |
|---|---|---|---|
| **Deterministic** | Extracted directly from AST, file system, or structured config; no interpretation involved | Phase 1, Phase 2 | No |
| **Heuristic** | Inferred from structural patterns -- naming conventions, package layout, stereotyped annotations -- with high but not absolute confidence | Phase 3 (Module, Component grouping) | Spot-check |
| **Inferential** | Requires semantic reasoning; an LLM or human applied business understanding to classify or name the entity | Phase 4, Phase 5 (DomainEntity, Rule, Capability) | Yes -- human review |
| **Manual** | Requires a human domain expert with business context; cannot be reliably automated | Business rules, compliance, capability definitions | Mandatory |

### Applying the taxonomy

1. **During extraction:** tag each entity with its confidence level as you
   create it. Use a `confidence` attribute or extraction-log annotation.
2. **During review:** sort entities by confidence level, lowest first.
   Inferential and manual entities MUST be reviewed before the extraction is
   considered complete.
3. **During maintenance:** if an entity's confidence was originally
   *inferential* and a domain expert has validated it, promote it to
   *heuristic* or *deterministic* as appropriate.

### Confidence by extraction technique

| Technique | Typical confidence |
|---|---|
| File system traversal | Deterministic |
| AST parsing | Deterministic |
| Dependency manifest parsing | Deterministic |
| Database schema extraction | Deterministic |
| API schema parsing | Deterministic |
| CI/CD config parsing | Deterministic |
| Test file analysis | Deterministic |
| Import/include analysis | Deterministic |
| Call graph construction | Deterministic |
| Data flow analysis | Heuristic |
| Package/directory heuristics | Heuristic |
| Naming convention analysis | Heuristic |
| Deployment manifest parsing | Heuristic |
| LLM semantic inference (domain) | Inferential |
| LLM semantic inference (business) | Inferential |
| LLM document analysis | Inferential |
| Runtime analysis (APM/traces) | Heuristic |
| Manual expert review | Manual |

---

## 11.5 Quick-Reference: Required Attributes Summary

The following classes have attributes marked `required: true` beyond the
universal `id` and `name` inherited from **NamedEntity**. If a class is not
listed here, only `id` and `name` are mandatory.

| Class | Required attributes |
|---|---|
| **Aggregate** | `has_root_entity` |
| **Attribute** | `data_type` |
| **AuditEntry** | `timestamp` |
| **BuildArtifact** | `artifact_type` |
| **BuildPipeline** | `pipeline_type` |
| **CallableUnit** | `callable_type` |
| **CodeContainer** | `container_path` |
| **ConcurrencyPattern** | `pattern_type` |
| **ConcurrencyPrimitive** | `primitive_type` |
| **DataElement** | `data_type` |
| **DataPipeline** | `pipeline_type` |
| **DataPipelineStep** | `step_type` |
| **DataStructure** | `structure_type` |
| **DatabaseConstraint** | `constraint_type` |
| **DatabaseIndex** | `index_type` |
| **DomainRelationship** | `cardinality` |
| **EncapsulationUnit** | `encapsulation_type` |
| **ErrorModel** | `strategy` |
| **FileOperation** | `operation_type` |
| **IaCDefinition** | `tool` |
| **IaCResource** | `resource_type` |
| **IPCConnection** | `mechanism` |
| **JobStep** | `step_type` |
| **KnownVulnerability** | `severity` |
| **MemoryModel** | `primary_model` |
| **MLModel** | `model_type` |
| **MLModelMetric** | `metric_name` |
| **OwnershipAnnotation** | `ownership` |
| **PackageDependency** | `package_name` |
| **PackageManager** | `manager_type` |
| **Parameter** | `data_type` |
| **PipelineStage** | `stage_type` |
| **PreprocessorDirective** | `directive_type` |
| **Route** | `path_pattern` |
| **ScreenDefinition** | `screen_type` |
| **StateStore** | `management_type` |
| **StorageLocation** | `location_path` |
| **TestSuite** | `suite_type` |
| **Transition** | `transitions_from_state`, `transitions_to_state` |
| **TypeExpression** | `type_kind` |
| **UIComponent** | `component_type` |

---

*End of reference appendix. Return to [00-overview.md](00-overview.md) for the
playbook table of contents.*
