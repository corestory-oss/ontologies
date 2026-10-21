# Layer 2: Container-Level Representation

This document defines the SAO v2.0 classes that correspond to **C4 Level 2 (Container)** -- the deployable services, data stores, interfaces, pipelines, and operational infrastructure that compose a system. This layer sits between the system context (Layer 1) and the component internals (Layer 3).

Where Layer 1 answers "what systems exist and how do they interact?", Layer 2 answers "what are the running parts of this system -- its services, databases, message brokers, build pipelines, and how are they deployed, monitored, and integrated?"

---

## Scope

Layer 2 covers:

- **Structural decomposition** -- bounded contexts, modules, services, dependencies
- **Interfaces and endpoints** -- user interfaces, APIs, event interfaces, screens, routes
- **Data management** -- data stores, collections, records, classifications, retention, lineage, audit, database schema objects
- **Integration** -- external system connections, messages, contracts, adapters, circuit breakers
- **Deployment and runtime** -- environments, deployments, deployment units, configuration, infrastructure, releases
- **Observability** -- metrics, logs, traces, spans, alerts, alert rules, incidents, health checks
- **Build and CI/CD** -- pipelines, pipeline stages, build artifacts, artifact registries
- **Dependency management** -- package managers, package dependencies, known vulnerabilities
- **Infrastructure as code** -- IaC definitions, modules, resources
- **ML and data pipelines** -- data pipelines, steps, datasets, ML models, model metrics, feature stores
- **Testing** -- test suites, coverage, assertions
- **Frontend supporting** -- state stores, UI properties, concurrency patterns

Like Layer 3, **Layer 2 is paradigm-agnostic**. A mainframe CICS system and a cloud-native microservice architecture both have services, data stores, deployments, and integrations. The differences emerge in how these are implemented (Layers 3 and 4), not in what they are (Layer 2).

---

> **NamedEntity base attributes.** Every class in this document extends `NamedEntity`, which provides `id` (string, required), `name` (string, required), `description` (string), `tags` (string[]), and `metadata` (Metadata, inline). These are not repeated in individual class tables.

---

## Summary

| # | Class | Definition | Group | SAO Section |
|---|---|---|---|---|
| 1 | BoundedContext | A semantic boundary within which a domain model applies consistently (DDD) | Structural | 1 |
| 2 | Module | A deployable, cohesive unit of functionality within a bounded context | Structural | 1 |
| 3 | Service | An independently deployable runtime unit | Structural | 1 |
| 4 | Interface (abstract) | A contract-defined boundary through which interaction occurs | Structural | 1 |
| 5 | Dependency (inline) | A lightweight dependency reference between components or services | Structural | 1 |
| 6 | UserInterface | A user-facing interface (web, mobile, desktop, CLI) | Interfaces & Endpoints | 1 |
| 7 | ProgrammaticInterface | A machine-to-machine interface (REST, GraphQL, gRPC, SDK, SOAP) | Interfaces & Endpoints | 1 |
| 8 | EventInterface | An event-driven interface (webhook, message queue, event stream, pub/sub) | Interfaces & Endpoints | 1 |
| 9 | Screen | A single screen or view in a user interface | Interfaces & Endpoints | 1 |
| 10 | Endpoint | A specific addressable entry point on a service | Interfaces & Endpoints | 1 |
| 11 | Route | A navigation route or URL path in a frontend application | Interfaces & Endpoints | 12 |
| 12 | DataStore | A persistence mechanism (relational DB, document DB, cache, message broker, etc.) | Data Management | 6 |
| 13 | Collection | A logical grouping of records (table, collection, bucket) | Data Management | 6 |
| 14 | Record | A single persisted instance of data | Data Management | 6 |
| 15 | DataClassification | A sensitivity or handling category for data | Data Management | 6 |
| 16 | RetentionPolicy | Rules governing data lifecycle and deletion | Data Management | 6 |
| 17 | DataLineage | The origin, transformation history, and movement of data | Data Management | 6 |
| 18 | AuditLog | A tamper-evident record of system activities | Data Management | 6 |
| 19 | AuditEntry | A single record within an audit log | Data Management | 6 |
| 20 | DatabaseConstraint (inline) | A constraint on a database table/collection | Data Management | 27 |
| 21 | DatabaseIndex (inline) | An index on a database table/collection | Data Management | 27 |
| 22 | Integration | A configured connection to an external system | Integration | 7 |
| 23 | Message (inline) | A unit of data exchanged in integration | Integration | 7 |
| 24 | Contract | A formal specification of integration behavior | Integration | 7 |
| 25 | ContractVersion (inline) | A specific iteration of a contract | Integration | 7 |
| 26 | Adapter | A component that translates between system and external protocols (extends Component from L3) | Integration | 7 |
| 27 | CircuitBreaker | A resilience pattern preventing cascade failures | Integration | 7 |
| 28 | Environment | A runtime context with specific configuration | Deployment & Runtime | 8 |
| 29 | Deployment | An instance of a service running in an environment | Deployment & Runtime | 8 |
| 30 | DeploymentUnit | The packaged artifact being deployed | Deployment & Runtime | 8 |
| 31 | Configuration | Runtime parameters for a deployment | Deployment & Runtime | 8 |
| 32 | Infrastructure | The underlying compute, storage, and network resources | Deployment & Runtime | 8 |
| 33 | Release | A versioned, deployable package of changes | Deployment & Runtime | 8 |
| 34 | Metric | A quantitative measurement over time | Observability | 9 |
| 35 | Log | A timestamped record of discrete events | Observability | 9 |
| 36 | LogEntry (inline) | A single record within a log | Observability | 9 |
| 37 | Trace | A causal chain of operations across services | Observability | 9 |
| 38 | Span (inline) | A single unit of work within a trace | Observability | 9 |
| 39 | Alert | A notification triggered by metric thresholds or anomalies | Observability | 9 |
| 40 | AlertRule | The condition that triggers an alert (extends Rule from L3) | Observability | 9 |
| 41 | Incident | A tracked degradation or outage event | Observability | 9 |
| 42 | HealthCheck (inline) | A probe verifying service availability | Observability | 9 |
| 43 | BuildPipeline | A CI/CD pipeline automating build, test, and deployment | Build & CI/CD | 13 |
| 44 | PipelineStage (inline) | A discrete stage within a CI/CD pipeline | Build & CI/CD | 13 |
| 45 | BuildArtifact | An artifact produced by a build pipeline | Build & CI/CD | 13 |
| 46 | ArtifactRegistry | A registry or repository for storing build artifacts | Build & CI/CD | 13 |
| 47 | PackageManager | A package/dependency management tool | Dependency Management | 14 |
| 48 | PackageDependency | A declared dependency on an external package or library | Dependency Management | 14 |
| 49 | KnownVulnerability (inline) | A known security vulnerability in a dependency | Dependency Management | 14 |
| 50 | IaCDefinition | An infrastructure-as-code definition for declarative resource provisioning | Infrastructure as Code | 17 |
| 51 | IaCModule | A reusable module of IaC definitions | Infrastructure as Code | 17 |
| 52 | IaCResource (inline) | A single infrastructure resource defined in code | Infrastructure as Code | 17 |
| 53 | DataPipeline | A data processing pipeline for ETL, feature engineering, or model training | ML & Data Pipelines | 16 |
| 54 | DataPipelineStep (inline) | A discrete step within a data pipeline | ML & Data Pipelines | 16 |
| 55 | Dataset | A dataset used for training, evaluation, or inference | ML & Data Pipelines | 16 |
| 56 | MLModel | A machine learning model defined, trained, or served by the system | ML & Data Pipelines | 16 |
| 57 | MLModelMetric (inline) | A performance metric for an ML model | ML & Data Pipelines | 16 |
| 58 | FeatureStore | A centralized store for computed ML features | ML & Data Pipelines | 16 |
| 59 | TestSuite | A collection of related test cases | Testing | 11 |
| 60 | TestCoverage | Code coverage metrics for a component or module | Testing | 11 |
| 61 | TestAssertion (inline) | An individual assertion within a test case | Testing | 11 |
| 62 | StateStore | A frontend state management store or container | Frontend Supporting | 12 |
| 63 | UIProperty (inline) | A property (prop) passed to a UI component | Frontend Supporting | 12 |
| 64 | ConcurrencyPattern | A high-level concurrency pattern used in the system | Frontend Supporting | 15 |

**Total: 64 classes** (including 3 Interface subtypes, 1 Component subtype, and 1 Rule subtype that inherit from parents).

---

## Connections to Adjacent Layers

### Upward links to Layer 1 (System Context)

These relationships connect Layer 2 concepts to system-context entities:

| Layer 2 class | Attribute | Layer 1 class | Description |
|---|---|---|---|
| BoundedContext | `contained_in_system` | System | System owning this bounded context |
| Integration | `belongs_to_system` | System | System owning this integration |
| Integration | `integrates_with_system` | ExternalSystem | External system connected via this integration |
| Interface | `exposed_by_system` | System | System exposing this interface |

> **Note:** **Policy** (Layer 3) also has an upward link to Layer 1 via `enforced_by_system` → **System**. It is documented in the Layer 3 cross-layer section rather than here, since Policy is not a Layer 2 class.

### Downward links to Layer 3 (Component)

These relationships connect Layer 2 concepts to their component-level internals:

| Layer 2 class | Attribute | Layer 3 class | Description |
|---|---|---|---|
| Module | `contains_components` | Component | Components within this module |
| BoundedContext | `contains_aggregates` | Aggregate | Aggregates within this bounded context |
| DataStore | `persists_aggregates` | Aggregate | Aggregates backed by this data store |
| Configuration | `controls_features` | Feature | Features controlled by this config (feature flags) |
| Service | `receives_integration_events` | IntegrationEvent | Integration events received by this service |
| Collection | `collection_structured_by_schema` | Schema | Schema defining collection structure |
| Module | `provides_capabilities` | Capability | Capabilities provided by this module |
| Route | `route_renders_component` | UIComponent | UI component rendered on this route |
| Route | `route_guarded_by` | Policy | Policies guarding this route |
| Screen | `offers_operations` | Operation | Operations accessible from this screen |
| Endpoint | `operations` | Operation | Operations served by this endpoint |

### Intra-layer links (within Layer 2)

| Layer 2 class | Attribute | Layer 2 class | Description |
|---|---|---|---|
| Contract | `defines_interfaces` | Interface | Interfaces defined by this contract |
| Module | `runs_as_services` | Service | Services running this module |

### Downward links to Layer 4 (Code)

| Layer 2 class | Attribute | Layer 4 class | Description |
|---|---|---|---|
| Collection | `persists_structures` | DataStructure | Code-level data structures persisted in this collection |
| Contract | `implemented_by_units` | EncapsulationUnit | Code units implementing this contract |

---

## A. Structural (5 classes)

### 1. BoundedContext

A semantic boundary within which a domain model applies consistently. Corresponds to the DDD bounded context concept.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `ubiquitous_language` | string[] | No | Key terms in the ubiquitous language for this context |
| `context_map_relationship` | string | No | Relationship pattern (e.g., Customer-Supplier, Partnership) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_system` | System | No | `contains_bounded_contexts` | Parent system (Layer 1) |
| `contains_modules` | Module | Yes | `contained_in_context` | Modules within this context |
| `upstream_from` | BoundedContext | Yes | `downstream_from` | Contexts upstream (this context depends on them) |
| `downstream_from` | BoundedContext | Yes | `upstream_from` | Contexts downstream (they depend on this one) |
| `contains_aggregates` | Aggregate | Yes | `contained_in_bounded_context` | Aggregates within this context (Layer 3) |

---

### 2. Module

A deployable, cohesive unit of functionality within a bounded context.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `is_optional` | boolean | No | Whether this module is optional |
| `required_features` | string[] | No | Features required for this module |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_context` | BoundedContext | No | `contains_modules` | Parent bounded context |
| `contains_components` | Component | Yes | `contained_in_module` | Components within this module (Layer 3) |
| `depends_on_module` | Module | Yes | `depended_on_by_module` | Modules this one depends on |
| `depended_on_by_module` | Module | Yes | `depends_on_module` | Modules depending on this one |
| `provides_capabilities` | Capability | Yes | `provided_by_modules` | Capabilities provided (Layer 3) |
| `runs_as_services` | Service | Yes | `runs_module` | Services running this module |
| `dependencies` | Dependency | Yes | -- | Inline dependency declarations |
| `mapped_from_directory` | StorageLocation | No | `maps_to_module` | Source directory (Layer 4) |
| `module_tested_by_suites` | TestSuite | Yes | `tests_module` | Test suites for this module |
| `module_has_coverage` | TestCoverage | No | `coverage_for_module` | Coverage metrics |
| `module_managed_by_package_manager` | PackageManager | No | `manages_dependencies_for_module` | Package manager |
| `module_has_dependencies` | PackageDependency | Yes | `dependency_of_module` | Package dependencies |

---

### 3. Service

An independently deployable runtime unit.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `service_type` | ServiceType | No | Kind of service |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `has_health_checks` | HealthCheck | Yes | -- | Health check probes (inline) |
| `emits_metrics` | Metric | Yes | -- | Metrics emitted |
| `exposes_endpoints` | Endpoint | Yes | `exposed_by_service` | Endpoints exposed (inline) |
| `depends_on_service` | Service | Yes | `depended_on_by_service` | Services this one depends on |
| `depended_on_by_service` | Service | Yes | `depends_on_service` | Services depending on this one |
| `deployed_as` | Deployment | Yes | `deploys_service` | Deployment instances |
| `runs_module` | Module | No | `runs_as_services` | Module this service runs |
| `receives_integration_events` | IntegrationEvent | Yes | `targeted_at_services` | Integration events received (Layer 3) |
| `affected_by_incidents` | Incident | Yes | `affects_services` | Incidents affecting this service |

**ServiceType Enum:**

| Value | Description |
|---|---|
| `microservice` | Microservice |
| `monolith` | Monolith |
| `function` | Serverless function or lambda |
| `job` | Batch processing job |
| `daemon` | Daemon process |
| `cics_transaction` | CICS online transaction |
| `ims_transaction` | IMS online transaction |
| `batch_program` | Mainframe batch program |
| `stored_proc_service` | Stored procedure exposed as service |

---

### 4. Interface (abstract)

A contract-defined boundary through which interaction occurs. Abstract base for UserInterface, ProgrammaticInterface, and EventInterface.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `category` | InterfaceCategory | No | `user_interface`, `programmatic_interface`, `event_interface` |
| `authentication_required` | boolean | No | Whether authentication is required |
| `rate_limit` | integer | No | Rate limit (requests per unit time) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `defined_by_contract` | Contract | No | `defines_interfaces` | Contract defining this interface |
| `exposed_by_system` | System | No | `exposes_interfaces` | System exposing this interface (Layer 1) |

**InterfaceCategory Enum:**

| Value | Description |
|---|---|
| `user_interface` | User-facing interface |
| `programmatic_interface` | Machine-to-machine interface |
| `event_interface` | Event-driven interface |

---

### 5. Dependency

A lightweight dependency reference between components or services. Typically inlined within Module or Component.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `dependency_type` | DependencyType | No | Kind of dependency |
| `target` | NamedEntity | No | Target entity |
| `version_constraint` | string | No | Version constraint expression |
| `is_optional` | boolean | No | Whether optional |

**DependencyType Enum:**

| Value | Description |
|---|---|
| `runtime` | Required at runtime |
| `build` | Required at build time |
| `optional` | Optional dependency |
| `dev` | Development-only dependency |

---

## B. Interfaces & Endpoints (6 classes)

### 6. UserInterface

A user-facing interface. Inherits all Interface attributes and relationships.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `ui_type` | UserInterfaceType | No | Kind of user interface |
| `contains_screens` | Screen | Yes | Screens in this interface |

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contains_screens` | Screen | Yes | `part_of_ui` | Screens in this interface |

**UserInterfaceType Enum:**

| Value | Description |
|---|---|
| `web_ui` | Web-based UI |
| `mobile_ui` | Mobile application UI |
| `desktop_ui` | Desktop application UI |
| `cli` | Command-line interface |

---

### 7. ProgrammaticInterface

A machine-to-machine interface. Inherits all Interface attributes and relationships.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `api_type` | APIType | No | Kind of API |
| `base_url` | URI | No | Base URL |

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `has_endpoints` | Endpoint | Yes | `belongs_to_interface` | Endpoints in this interface (inline) |

**APIType Enum:**

| Value | Description |
|---|---|
| `rest_api` | REST API |
| `graphql_api` | GraphQL API |
| `grpc_api` | gRPC API |
| `sdk` | Software Development Kit |
| `soap_api` | SOAP API |

---

### 8. EventInterface

An event-driven interface. Inherits all Interface attributes and relationships.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `event_type` | EventInterfaceType | No | Kind of event interface |
| `topics` | string[] | No | Topic names |

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `has_subscriptions` | Subscription | Yes | `subscribes_to_interface` | Subscriptions to this interface (Layer 3) |

**EventInterfaceType Enum:**

| Value | Description |
|---|---|
| `webhook` | Webhook callback |
| `message_queue` | Message queue |
| `event_stream` | Event stream |
| `pub_sub` | Publish/subscribe |

---

### 9. Screen

A single screen or view in a user interface.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `route` | string | No | URL route or path |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `part_of_ui` | UserInterface | No | `contains_screens` | Parent user interface |
| `offers_operations` | Operation | Yes | `offered_on_screens` | Operations accessible from this screen (Layer 3) |

---

### 10. Endpoint

A specific addressable entry point on a service.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `path` | string | No | URL path |
| `method` | string | No | HTTP method or equivalent |
| `operations` | Operation[] | No | Operations served |
| `protocol` | ProtocolType | No | Communication protocol |
| `port` | integer | No | Port number |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `exposed_by_service` | Service | No | `exposes_endpoints` | Service exposing this endpoint |
| `belongs_to_interface` | ProgrammaticInterface | No | `has_endpoints` | Parent programmatic interface |

**ProtocolType Enum:**

| Value | Description |
|---|---|
| `http` | HTTP |
| `https` | HTTPS |
| `websocket` | WebSocket |
| `grpc` | gRPC |
| `amqp` | AMQP |
| `mqtt` | MQTT |
| `kafka` | Kafka |
| `sftp` | SFTP |
| `tcp` | TCP |
| `udp` | UDP |
| `corba` | Common Object Request Broker Architecture |
| `dcom` | Distributed Component Object Model |
| `rmi` | Java Remote Method Invocation |
| `named_pipe` | Named pipe |
| `shared_memory` | Shared memory |

---

### 11. Route

A navigation route or URL path in a frontend application.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `path_pattern` | string | **Yes** | URL path pattern |
| `route_type` | RouteType | No | Kind of route |
| `http_methods` | string[] | No | Allowed HTTP methods |
| `is_dynamic` | boolean | No | Whether the route has dynamic segments |
| `is_authenticated` | boolean | No | Whether authentication is required |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `route_renders_component` | UIComponent | No | `renders_on_route` | UI component rendered (Layer 3) |
| `has_parent_route` | Route | No | `has_child_routes` | Parent route |
| `has_child_routes` | Route | Yes | `has_parent_route` | Child routes |
| `route_guarded_by` | Policy | Yes | `guards_routes` | Policies guarding this route (Layer 3) |

**RouteType Enum:**

| Value | Description |
|---|---|
| `page_route` | Full page route |
| `api_route` | API route |
| `layout_route` | Layout wrapper route |
| `redirect` | Redirect |
| `catch_all` | Catch-all/wildcard route |
| `guarded` | Guarded/protected route |

---

## C. Data Management (10 classes)

### 12. DataStore

A persistence mechanism.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `store_type` | DataStoreType | No | Kind of data store |
| `connection_string` | string | No | Connection string |
| `collections` | Collection[] | No | Collections within this store (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `hosted_on_infrastructure` | Infrastructure | No | `hosts_datastores` | Hosting infrastructure |
| `persists_aggregates` | Aggregate | Yes | `persisted_in_stores` | Aggregates backed by this store (Layer 3) |
| `store_read_by_pipelines` | DataPipeline | Yes | `pipeline_reads_from_stores` | Pipelines reading from this store |
| `store_written_by_pipelines` | DataPipeline | Yes | `pipeline_writes_to_stores` | Pipelines writing to this store |
| `store_file_definitions` | FileDefinition | Yes | `persisted_in_store` | File definitions mapped to this store (Layer 4) |

**DataStoreType Enum:**

| Value | Description |
|---|---|
| `relational_db` | Relational database |
| `document_db` | Document database |
| `key_value_store` | Key-value store |
| `graph_db` | Graph database |
| `time_series_db` | Time series database |
| `object_storage` | Object/blob storage |
| `search_index` | Search index (Elasticsearch, Solr) |
| `cache` | Cache (Redis, Memcached) |
| `message_broker` | Message broker |
| `data_lake` | Data lake |
| `vsam` | IBM VSAM dataset |
| `flat_file` | Sequential or flat file |
| `isam` | Indexed Sequential Access Method file |
| `dead_letter_queue` | Dead letter queue |

---

### 13. Collection

A logical grouping of records (table, collection, bucket).

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `indexes` | string[] | No | Index definitions as strings (**deprecated** -- use `has_indexes`) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `collection_structured_by_schema` | Schema | No | `structures_collections` | Schema defining structure (Layer 3) |
| `governed_by_retention_policy` | RetentionPolicy | No | `governs_collections` | Retention policy |
| `stores_records` | Record | Yes | `stored_in_collection` | Records stored |
| `persists_structures` | DataStructure | Yes | `persisted_in_collection` | Code-level data structures persisted (Layer 4) |
| `has_constraints` | DatabaseConstraint | Yes | `constraint_on_collection` | Database constraints (inline) |
| `has_indexes` | DatabaseIndex | Yes | `index_on_collection` | Database indexes (inline) |

---

### 14. Record

A single persisted instance of data.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `classifications` | DataClassificationType[] | No | Data sensitivity classifications |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `stored_in_collection` | Collection | No | `stores_records` | Parent collection |
| `conforms_to_schema` | Schema | No | `validates_records` | Schema this record conforms to (Layer 3) |
| `has_lineage` | DataLineage | No | `tracks_record` | Lineage tracking |
| `source_of_lineage` | DataLineage | Yes | `derived_from_records` | Lineage entries where this record is a source |

---

### 15. DataClassification

A sensitivity or handling category for data.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `classification_type` | DataClassificationType | No | Classification level |
| `handling_requirements` | string[] | No | Handling requirements |
| `encryption_required` | boolean | No | Whether encryption is required |

**DataClassificationType Enum:**

| Value | Description |
|---|---|
| `public` | Public data |
| `internal` | Internal use only |
| `confidential` | Confidential |
| `restricted` | Restricted access |
| `pii` | Personally Identifiable Information |
| `phi` | Protected Health Information |
| `pci` | Payment Card Industry data |

---

### 16. RetentionPolicy

Rules governing data lifecycle and deletion.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `retention_days` | integer | No | Days to retain data |
| `archive_after_days` | integer | No | Days before archival |
| `deletion_strategy` | string | No | Deletion strategy |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `governs_collections` | Collection | Yes | `governed_by_retention_policy` | Collections governed |
| `governs_logs` | Log | Yes | `log_governed_by_retention` | Logs governed |
| `governs_audit_logs` | AuditLog | Yes | `auditlog_governed_by_retention` | Audit logs governed |

---

### 17. DataLineage

The origin, transformation history, and movement of data.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `source` | string | No | Data source |
| `transformations` | string[] | No | Transformation descriptions |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `derived_from_records` | Record | Yes | `source_of_lineage` | Source records |
| `tracks_record` | Record | No | `has_lineage` | Record tracked |

---

### 18. AuditLog

A tamper-evident record of system activities.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `entries` | AuditEntry[] | No | Entries (legacy attribute) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `auditlog_governed_by_retention` | RetentionPolicy | No | `governs_audit_logs` | Retention policy |
| `contains_entries` | AuditEntry | Yes | `entry_in_audit_log` | Audit entries |

---

### 19. AuditEntry

A single record within an audit log.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `timestamp` | Timestamp | **Yes** | When the action occurred |
| `outcome` | string | No | Action outcome |
| `details` | string | No | Additional details |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `entry_in_audit_log` | AuditLog | No | `contains_entries` | Parent audit log |
| `audit_performed_by_actor` | Actor | No | `audit_actions_performed` | Actor who performed the action |
| `records_action` | Action | No | `recorded_in_audit` | Action recorded (Layer 3) |
| `affects_resource` | Resource | No | `affected_in_audit` | Resource affected (Layer 3) |

---

### 20. DatabaseConstraint

A constraint on a database table/collection. Typically inlined within Collection.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `constraint_type` | DatabaseConstraintType | **Yes** | Kind of constraint |
| `columns` | string[] | No | Constrained columns |
| `reference_table` | string | No | Referenced table (for foreign keys) |
| `reference_columns` | string[] | No | Referenced columns (for foreign keys) |
| `expression` | string | No | Expression (for CHECK constraints) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `constraint_on_collection` | Collection | No | `has_constraints` | Parent collection |

**DatabaseConstraintType Enum:**

| Value | Description |
|---|---|
| `primary_key` | Primary key |
| `foreign_key` | Foreign key |
| `unique` | Unique constraint |
| `check` | Check constraint |
| `not_null` | Not-null constraint |

---

### 21. DatabaseIndex

An index on a database table/collection. Typically inlined within Collection.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `index_type` | IndexType | **Yes** | Kind of index |
| `columns` | string[] | No | Indexed columns |
| `is_unique` | boolean | No | Whether unique |
| `is_partial` | boolean | No | Whether a partial index |
| `filter_expression` | string | No | Filter for partial indexes |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `index_on_collection` | Collection | No | `has_indexes` | Parent collection |

**IndexType Enum:**

| Value | Description |
|---|---|
| `btree` | B-tree index |
| `hash` | Hash index |
| `gin` | Generalized Inverted Index (PostgreSQL) |
| `fulltext` | Full-text index |

---

## D. Integration (6 classes)

### 22. Integration

A configured connection to an external system.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `integration_type` | IntegrationType | No | Direction of integration |
| `protocol` | ProtocolType | No | Communication protocol |
| `messages` | Message[] | No | Messages exchanged (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `integrates_with_system` | ExternalSystem | No | `integrated_via` | External system (Layer 1) |
| `uses_adapter` | Adapter | No | `used_by_integrations` | Protocol adapter |
| `protected_by_breaker` | CircuitBreaker | No | `protects_integrations` | Circuit breaker |
| `integration_governed_by_contract` | Contract | No | `governs_integrations` | Governing contract |
| `belongs_to_system` | System | No | `has_integrations` | Parent system (Layer 1) |

**IntegrationType Enum:**

| Value | Description |
|---|---|
| `inbound` | Inbound integration |
| `outbound` | Outbound integration |
| `bidirectional` | Bidirectional integration |

---

### 23. Message

A unit of data exchanged in integration. Typically inlined within Integration.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `message_type` | MessageType | No | Kind of message |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `message_structured_by_schema` | Schema | No | `structures_messages` | Payload schema (Layer 3) |
| `validated_by_contract` | Contract | No | `validates_messages` | Contract validating this message |

**MessageType Enum:**

| Value | Description |
|---|---|
| `request` | Request message |
| `response` | Response message |
| `notification` | Notification |
| `command` | Command message |
| `event` | Event message |
| `query` | Query message |

---

### 24. Contract

A formal specification of integration behavior.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `contract_type` | ContractType | No | Kind of contract |
| `definition` | string | No | Contract definition content |
| `has_versions` | ContractVersion[] | No | Version history (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `defines_interfaces` | Interface | Yes | `defined_by_contract` | Interfaces defined by this contract |
| `implemented_by_units` | EncapsulationUnit | Yes | `implements_contracts` | Code units implementing this contract (Layer 4) |
| `validates_messages` | Message | Yes | `validated_by_contract` | Messages validated |
| `governs_integrations` | Integration | Yes | `integration_governed_by_contract` | Integrations governed |

**ContractType Enum:**

| Value | Description |
|---|---|
| `openapi` | OpenAPI/Swagger |
| `asyncapi` | AsyncAPI |
| `json_schema` | JSON Schema |
| `protobuf` | Protocol Buffers |
| `avro` | Apache Avro |
| `graphql_schema` | GraphQL schema |
| `wsdl` | WSDL (SOAP) |

---

### 25. ContractVersion

A specific iteration of a contract. Typically inlined within Contract.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `version` | SemanticVersion | No | Version number |
| `definition` | string | No | Contract definition at this version |
| `breaking_changes` | string[] | No | Breaking changes in this version |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `version_of_contract` | Contract | No | `has_versions` | Parent contract |

---

### 26. Adapter

A component that translates between system and external protocols.

> **Inherits all Component attributes and relationships from Layer 3.** Adapter extends Component (`is_a: Component`), so it has `component_type`, `language`, `source_location`, `contained_in_module`, `exposes_operations`, `emits_events`, `dependencies`, `implemented_by_code`, `tested_by_suites`, `has_coverage`, `emits_metrics`, `generates_logs`, `emits_metric`, `component_serves_model`, and `component_uses_concurrency_pattern` -- all inherited.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `source_protocol` | ProtocolType | No | Source protocol being translated from |
| `target_protocol` | ProtocolType | No | Target protocol being translated to |
| `transformation` | string | No | Transformation logic description |

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `used_by_integrations` | Integration | Yes | `uses_adapter` | Integrations using this adapter |

---

### 27. CircuitBreaker

A resilience pattern preventing cascade failures.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `failure_threshold` | integer | No | Number of failures before opening |
| `reset_timeout_seconds` | integer | No | Seconds before attempting half-open |
| `half_open_requests` | integer | No | Requests allowed in half-open state |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `protects_integrations` | Integration | Yes | `protected_by_breaker` | Integrations protected |

---

## E. Deployment & Runtime (6 classes)

### 28. Environment

A runtime context with specific configuration.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `environment_type` | EnvironmentType | No | Kind of environment |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `hosts_deployments` | Deployment | Yes | `deployed_in_environment` | Deployments in this environment |
| `env_configured_by` | Configuration | Yes | `configures_environments` | Configuration entries |
| `uses_infrastructure` | Infrastructure | Yes | `used_by_environments` | Infrastructure used |
| `deployed_by_pipelines` | BuildPipeline | Yes | `pipeline_deploys_to_environments` | Pipelines deploying to this environment |

**EnvironmentType Enum:**

| Value | Description |
|---|---|
| `development` | Development environment |
| `testing` | Testing environment |
| `staging` | Staging/pre-production |
| `production` | Production environment |
| `dr` | Disaster Recovery |

---

### 29. Deployment

An instance of a service running in an environment.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `replicas` | integer | No | Number of replicas |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `deploys_service` | Service | No | `deployed_as` | Service being deployed |
| `deployed_in_environment` | Environment | No | `hosts_deployments` | Target environment |
| `deploys_unit` | DeploymentUnit | No | `deployed_in_deployments` | Deployment unit |
| `deployment_configured_by` | Configuration | Yes | `configures_deployments` | Configuration entries |
| `deploys_release` | Release | No | `deployed_in_deployments_as_release` | Release being deployed |

---

### 30. DeploymentUnit

The packaged artifact being deployed.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `unit_type` | DeploymentUnitType | No | Kind of deployment unit |
| `artifact_uri` | URI | No | Location of the artifact |
| `checksum` | string | No | Integrity checksum |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `deployed_in_deployments` | Deployment | Yes | `deploys_unit` | Deployments using this unit |

**DeploymentUnitType Enum:**

| Value | Description |
|---|---|
| `container` | Container image |
| `vm` | Virtual machine image |
| `serverless_function` | Serverless function package |
| `binary` | Compiled binary |
| `package` | Software package |

---

### 31. Configuration

Runtime parameters for a deployment.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `config_type` | ConfigurationType | No | Kind of configuration |
| `value` | string | No | Configuration value |
| `is_secret` | boolean | No | Whether this is a secret |
| `source` | string | No | Configuration source |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `controls_features` | Feature | Yes | `controlled_by_configs` | Features controlled (Layer 3) |
| `configures_environments` | Environment | Yes | `env_configured_by` | Environments configured |
| `configures_deployments` | Deployment | Yes | `deployment_configured_by` | Deployments configured |

**ConfigurationType Enum:**

| Value | Description |
|---|---|
| `environment_variable` | Environment variable |
| `config_file` | Configuration file |
| `secret` | Secret/credential |
| `feature_flag` | Feature flag |
| `remote_config` | Remote configuration |

---

### 32. Infrastructure

The underlying compute, storage, and network resources.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `infra_type` | InfrastructureType | No | Kind of infrastructure |
| `provider` | string | No | Cloud/infrastructure provider |
| `region` | string | No | Deployment region |
| `specifications` | string | No | Resource specifications |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `hosts_datastores` | DataStore | Yes | `hosted_on_infrastructure` | Data stores hosted |
| `used_by_environments` | Environment | Yes | `uses_infrastructure` | Environments using this infrastructure |
| `infrastructure_provisioned_by_iac` | IaCDefinition | Yes | `iac_provisions_infrastructure` | IaC definitions provisioning this |

**InfrastructureType Enum:**

| Value | Description |
|---|---|
| `compute` | Compute resources |
| `storage` | Storage resources |
| `network` | Network resources |
| `load_balancer` | Load balancer |
| `dns` | DNS |
| `cdn` | Content delivery network |
| `firewall` | Firewall |
| `api_gateway` | API gateway or ingress controller |
| `service_mesh` | Service mesh control plane (Istio, Linkerd, etc.) |

---

### 33. Release

A versioned, deployable package of changes.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `version` | SemanticVersion | No | Release version |
| `changelog` | string | No | Release changelog |
| `artifacts` | DeploymentUnit[] | No | Artifacts in this release |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `deployed_in_deployments_as_release` | Deployment | Yes | `deploys_release` | Deployments of this release |

---

## F. Observability (9 classes)

### 34. Metric

A quantitative measurement over time.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `metric_type` | MetricType | No | Kind of metric |
| `unit` | string | No | Unit of measurement |
| `labels` | string[] | No | Metric labels/dimensions |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `metric_emitted_by_component` | Component | No | `emits_metric` | Component emitting this metric (Layer 3) |
| `monitored_by_alert_rules` | AlertRule | Yes | `monitors_metrics` | Alert rules monitoring this metric |

**MetricType Enum:**

| Value | Description |
|---|---|
| `counter` | Monotonically increasing counter |
| `gauge` | Point-in-time value |
| `histogram` | Distribution of values |
| `summary` | Quantile summary |

---

### 35. Log

A timestamped record of discrete events.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `log_type` | LogType | No | Kind of log |
| `entries` | LogEntry[] | No | Entries (legacy attribute) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `log_governed_by_retention` | RetentionPolicy | No | `governs_logs` | Retention policy |
| `contains_entries` | LogEntry | Yes | `entry_in_log` | Log entries |

**LogType Enum:**

| Value | Description |
|---|---|
| `application` | Application log |
| `access` | Access log |
| `error` | Error log |
| `security` | Security log |
| `audit` | Audit log |
| `debug` | Debug log |

---

### 36. LogEntry

A single record within a log. Typically inlined within Log.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `timestamp` | Timestamp | No | When the entry was recorded |
| `level` | string | No | Log level (DEBUG, INFO, WARN, ERROR, etc.) |
| `message` | string | No | Log message |
| `context` | string | No | Contextual information |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `entry_in_log` | Log | No | `contains_entries` | Parent log |

---

### 37. Trace

A causal chain of operations across services.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `trace_id` | string | No | Distributed trace identifier |
| `spans` | Span[] | No | Spans in this trace (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `starts_with_span` | Span | No | `root_of_trace` | Root span |
| `contains_spans` | Span | Yes | `belongs_to_trace` | All spans |

---

### 38. Span

A single unit of work within a trace. Typically inlined within Trace.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `span_id` | string | No | Span identifier |
| `operation_name` | string | No | Name of the operation |
| `start_time` | Timestamp | No | Start timestamp |
| `end_time` | Timestamp | No | End timestamp |
| `status` | string | No | Span status |
| `attributes` | string[] | No | Span attributes/tags |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `belongs_to_trace` | Trace | No | `contains_spans` | Parent trace |
| `child_of_span` | Span | No | `parent_of_spans` | Parent span |
| `parent_of_spans` | Span | Yes | `child_of_span` | Child spans |
| `root_of_trace` | Trace | No | `starts_with_span` | Trace where this is root |

---

### 39. Alert

A notification triggered by metric thresholds or anomalies.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `severity` | string | No | Alert severity |
| `triggered_at` | Timestamp | No | When triggered |
| `acknowledged_at` | Timestamp | No | When acknowledged |
| `resolved_at` | Timestamp | No | When resolved |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `triggered_by_rule` | AlertRule | No | `triggers_alerts` | Rule that triggered this alert |
| `escalates_to_incident` | Incident | Yes | `escalated_from_alerts` | Incidents escalated to |

---

### 40. AlertRule

The condition that triggers an alert.

> **Inherits all Rule attributes and relationships from Layer 3.** AlertRule extends Rule (`is_a: Rule`), so it has `category` (RuleCategory), `condition`, `action`, `priority`, `is_active`, `validates_attributes`, `enforces_aggregate_invariants`, `governs_domain_entities`, `validates_actions`, and `guards_transitions` -- all inherited.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `condition` | string | No | Alert condition expression (overrides Rule.condition) |
| `threshold` | float | No | Threshold value |
| `duration_seconds` | integer | No | Duration before triggering |
| `notification_channels` | string[] | No | Notification channels |

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `monitors_metrics` | Metric | Yes | `monitored_by_alert_rules` | Metrics monitored |
| `triggers_alerts` | Alert | Yes | `triggered_by_rule` | Alerts triggered |

---

### 41. Incident

A tracked degradation or outage event.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `severity` | string | No | Incident severity |
| `status` | string | No | Current status |
| `started_at` | Timestamp | No | When the incident started |
| `resolved_at` | Timestamp | No | When resolved |
| `root_cause` | string | No | Root cause description |
| `postmortem_url` | URI | No | Post-mortem document URL |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `escalated_from_alerts` | Alert | Yes | `escalates_to_incident` | Alerts that escalated to this incident |
| `affects_services` | Service | Yes | `affected_by_incidents` | Services affected |

---

### 42. HealthCheck

A probe verifying service availability. Typically inlined within Service.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `check_type` | HealthCheckType | No | Kind of health check |
| `endpoint` | string | No | Probe endpoint |
| `interval_seconds` | integer | No | Check interval |
| `timeout_seconds` | integer | No | Timeout |
| `success_threshold` | integer | No | Consecutive successes required |
| `failure_threshold` | integer | No | Consecutive failures before unhealthy |

**HealthCheckType Enum:**

| Value | Description |
|---|---|
| `liveness` | Is the process alive? |
| `readiness` | Is the service ready to accept traffic? |
| `dependency` | Are dependencies healthy? |
| `startup` | Has the service finished starting? |

---

## G. Build & CI/CD (4 classes)

### 43. BuildPipeline

A CI/CD pipeline that automates build, test, and deployment processes.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `pipeline_type` | PipelineType | **Yes** | Kind of pipeline |
| `platform` | string | No | CI/CD platform (GitHub Actions, Jenkins, etc.) |
| `trigger` | string[] | No | Trigger events |
| `trigger_branches` | string[] | No | Branches that trigger this pipeline |
| `source_file` | string | No | Pipeline definition file path |
| `stages` | PipelineStage[] | No | Pipeline stages (inline) |
| `timeout_minutes` | integer | No | Pipeline timeout |
| `is_parallelizable` | boolean | No | Whether stages can run in parallel |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `pipeline_deploys_to_environments` | Environment | Yes | `deployed_by_pipelines` | Target environments |
| `pipeline_produces_artifacts` | BuildArtifact | Yes | `artifact_produced_by_pipeline` | Artifacts produced |
| `pipeline_trains_model` | MLModel | Yes | `model_trained_by_pipeline` | ML models trained |
| `pipeline_uses_iac` | IaCDefinition | Yes | `iac_used_by_pipeline` | IaC definitions used |

**PipelineType Enum:**

| Value | Description |
|---|---|
| `build` | Build pipeline |
| `test` | Test pipeline |
| `deploy` | Deployment pipeline |
| `release` | Release pipeline |
| `integration` | Integration pipeline |
| `delivery` | Continuous delivery pipeline |
| `validation` | Validation pipeline |

---

### 44. PipelineStage

A discrete stage within a CI/CD pipeline. Typically inlined within BuildPipeline.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `stage_type` | PipelineStageType | **Yes** | Kind of stage |
| `order` | integer | No | Execution order |
| `depends_on_stages` | string[] | No | Stage dependencies (by name) |
| `condition` | string | No | Execution condition |
| `runner` | string | No | Runner/agent label |
| `timeout_minutes` | integer | No | Stage timeout |
| `environment_variables` | string[] | No | Environment variables |
| `is_manual` | boolean | No | Whether manual approval is required |

**PipelineStageType Enum:**

| Value | Description |
|---|---|
| `checkout` | Source code checkout |
| `build` | Build/compile |
| `test` | Run tests |
| `lint` | Lint/static analysis |
| `security_scan` | Security scanning |
| `package` | Package artifacts |
| `publish` | Publish artifacts |
| `deploy` | Deploy to environment |
| `approval` | Manual approval gate |
| `rollback` | Rollback step |
| `notify` | Send notifications |

---

### 45. BuildArtifact

An artifact produced by a build pipeline.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `artifact_type` | ArtifactType | **Yes** | Kind of artifact |
| `artifact_uri` | URI | No | Artifact location |
| `size_bytes` | integer | No | Size in bytes |
| `checksum` | string | No | Integrity checksum |
| `build_number` | string | No | Build number or identifier |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `artifact_produced_by_pipeline` | BuildPipeline | No | `pipeline_produces_artifacts` | Pipeline that produced this artifact |
| `artifact_stored_in_registry` | ArtifactRegistry | No | `stores_artifacts` | Registry storing this artifact |

**ArtifactType Enum:**

| Value | Description |
|---|---|
| `container_image` | Container image (Docker) |
| `binary` | Compiled binary |
| `archive` | Archive (ZIP, TAR) |
| `package` | Software package (NPM, PyPI, etc.) |
| `library` | Library |
| `documentation` | Documentation artifact |
| `report` | Report (test, coverage, etc.) |
| `load_module` | Mainframe load module |

---

### 46. ArtifactRegistry

A registry or repository for storing build artifacts.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `registry_type` | string | No | Kind of registry (Docker Hub, Nexus, ECR, etc.) |
| `base_url` | URI | No | Registry base URL |
| `is_private` | boolean | No | Whether the registry is private |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `stores_artifacts` | BuildArtifact | Yes | `artifact_stored_in_registry` | Artifacts stored |

---

## H. Dependency Management (3 classes)

### 47. PackageManager

A package/dependency management tool.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `manager_type` | PackageManagerType | **Yes** | Kind of package manager |
| `manifest_file` | string | No | Manifest file name (package.json, pom.xml, etc.) |
| `lock_file` | string | No | Lock file name |
| `registry_url` | URI | No | Package registry URL |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `manages_dependencies_for_module` | Module | Yes | `module_managed_by_package_manager` | Modules managed |

**PackageManagerType Enum:**

| Value | Description |
|---|---|
| `npm` | NPM (Node.js) |
| `pip` | pip (Python) |
| `maven` | Maven (Java) |
| `gradle` | Gradle (Java/Kotlin) |
| `nuget` | NuGet (.NET) |
| `cargo` | Cargo (Rust) |
| `go_modules` | Go Modules |
| `bundler` | Bundler (Ruby) |
| `composer` | Composer (PHP) |
| `conan` | Conan (C/C++) |
| `none` | No package manager |

---

### 48. PackageDependency

A declared dependency on an external package or library.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `package_name` | string | **Yes** | Package name |
| `version_constraint` | string | No | Version constraint (e.g., ^1.2.0) |
| `resolved_version` | string | No | Resolved version |
| `scope` | DependencyScope | No | Dependency scope |
| `is_direct` | boolean | No | Whether this is a direct dependency |
| `license` | string | No | Package license |
| `has_known_vulnerabilities` | KnownVulnerability[] | No | Known vulnerabilities (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `dependency_of_module` | Module | No | `module_has_dependencies` | Module declaring this dependency |
| `has_transitive_dependencies` | PackageDependency | Yes | `transitive_dependency_of` | Transitive dependencies |
| `transitive_dependency_of` | PackageDependency | Yes | `has_transitive_dependencies` | Packages depending on this transitively |

**DependencyScope Enum:**

| Value | Description |
|---|---|
| `production` | Production dependency |
| `development` | Development-only |
| `test` | Test-only |
| `build` | Build-only |
| `optional` | Optional dependency |
| `provided` | Provided by runtime |

---

### 49. KnownVulnerability

A known security vulnerability in a dependency. Typically inlined within PackageDependency.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `cve_id` | string | No | CVE identifier |
| `severity` | VulnerabilitySeverity | **Yes** | Severity level |
| `cvss_score` | float | No | CVSS score |
| `affected_versions` | string | No | Affected version range |
| `fixed_version` | string | No | Version with fix |
| `advisory_url` | URI | No | Security advisory URL |

**VulnerabilitySeverity Enum:**

| Value | Description |
|---|---|
| `critical` | Critical severity |
| `high` | High severity |
| `medium` | Medium severity |
| `low` | Low severity |
| `none` | No severity / informational |

---

## I. Infrastructure as Code (3 classes)

### 50. IaCDefinition

An infrastructure-as-code definition that declaratively specifies infrastructure resources.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `tool` | IaCToolType | **Yes** | IaC tool |
| `source_file` | string | No | Source file path |
| `provider` | string | No | Cloud provider |
| `resources` | IaCResource[] | No | Resources defined (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `iac_provisions_infrastructure` | Infrastructure | Yes | `infrastructure_provisioned_by_iac` | Infrastructure provisioned |
| `iac_used_by_pipeline` | BuildPipeline | Yes | `pipeline_uses_iac` | Pipelines using this definition |

**IaCToolType Enum:**

| Value | Description |
|---|---|
| `terraform` | Terraform |
| `cloudformation` | AWS CloudFormation |
| `pulumi` | Pulumi |
| `ansible` | Ansible |
| `chef` | Chef |
| `puppet` | Puppet |
| `kubernetes_manifest` | Kubernetes manifest |
| `helm` | Helm chart |
| `docker_compose` | Docker Compose |
| `bicep` | Azure Bicep |
| `cdk` | AWS/Azure CDK |

---

### 51. IaCModule

A reusable module of IaC definitions.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `source` | string | No | Module source (registry path, git URL, etc.) |
| `input_variables` | string[] | No | Input variable names |
| `output_values` | string[] | No | Output value names |
| `has_child_resources` | IaCResource[] | No | Resources within this module (inline) |

---

### 52. IaCResource

A single infrastructure resource defined in code. Typically inlined within IaCDefinition or IaCModule.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `resource_type` | IaCResourceType | **Yes** | Kind of resource |
| `provider_resource_type` | string | No | Provider-specific type (e.g., aws_instance, azurerm_storage_account) |
| `properties` | string[] | No | Resource properties |
| `depends_on_resources` | string[] | No | Resource dependencies (by name) |
| `is_managed` | boolean | No | Whether Terraform/IaC manages lifecycle |

**IaCResourceType Enum:**

| Value | Description |
|---|---|
| `compute` | Compute resource |
| `network` | Network resource |
| `storage` | Storage resource |
| `database` | Database resource |
| `messaging` | Messaging resource |
| `identity` | Identity/IAM resource |
| `monitoring` | Monitoring resource |
| `dns` | DNS resource |
| `cdn` | CDN resource |
| `secret` | Secret management resource |

---

## J. ML & Data Pipelines (6 classes)

### 53. DataPipeline

A data processing pipeline for ETL, feature engineering, or model training.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `pipeline_type` | DataPipelineType | **Yes** | Kind of pipeline |
| `orchestrator` | string | No | Orchestrator (Airflow, Dagster, etc.) |
| `schedule` | string | No | Cron expression or schedule |
| `source_file` | string | No | Pipeline definition file |
| `steps` | DataPipelineStep[] | No | Pipeline steps (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `pipeline_reads_from_stores` | DataStore | Yes | `store_read_by_pipelines` | Data stores read from |
| `pipeline_writes_to_stores` | DataStore | Yes | `store_written_by_pipelines` | Data stores written to |
| `pipeline_uses_dataset` | Dataset | Yes | `dataset_used_by_pipeline` | Datasets used |

**DataPipelineType Enum:**

| Value | Description |
|---|---|
| `etl` | Extract-Transform-Load |
| `elt` | Extract-Load-Transform |
| `streaming` | Streaming pipeline |
| `feature_engineering` | Feature engineering |
| `training` | Model training |
| `inference` | Model inference |
| `data_quality` | Data quality checks |

---

### 54. DataPipelineStep

A discrete step within a data pipeline. Typically inlined within DataPipeline.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `step_type` | DataPipelineStepType | **Yes** | Kind of step |
| `order` | integer | No | Execution order |
| `depends_on_steps` | string[] | No | Step dependencies (by name) |
| `transformation_logic` | string | No | Transformation description |
| `input_schema` | string | No | Input schema |
| `output_schema` | string | No | Output schema |

**DataPipelineStepType Enum:**

| Value | Description |
|---|---|
| `extract` | Extract data from source |
| `transform` | Transform data |
| `load` | Load data into target |
| `validate` | Validate data quality |
| `deduplicate` | Remove duplicates |
| `enrich` | Enrich with additional data |
| `aggregate` | Aggregate data |
| `partition` | Partition data |
| `train` | Train ML model |
| `evaluate` | Evaluate model performance |
| `deploy_model` | Deploy trained model |

---

### 55. Dataset

A dataset used for training, evaluation, or inference.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `format` | string | No | Data format (CSV, Parquet, etc.) |
| `storage_uri` | URI | No | Storage location |
| `row_count` | integer | No | Number of rows/records |
| `schema` | Schema | No | Dataset schema (Layer 3) |
| `classification` | DataClassificationType | No | Data classification |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `dataset_used_by_pipeline` | DataPipeline | Yes | `pipeline_uses_dataset` | Pipelines using this dataset |

---

### 56. MLModel

A machine learning model defined, trained, or served by the system.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `model_type` | MLModelType | **Yes** | Kind of ML model |
| `framework` | string | No | ML framework (TensorFlow, PyTorch, etc.) |
| `model_format` | string | No | Serialization format (ONNX, SavedModel, etc.) |
| `model_uri` | URI | No | Model artifact location |
| `input_schema` | DataStructure | No | Input data structure (Layer 4) |
| `output_schema` | DataStructure | No | Output data structure (Layer 4) |
| `metrics` | MLModelMetric[] | No | Performance metrics (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `model_trained_by_pipeline` | DataPipeline | No | `pipeline_trains_model` | Training pipeline |
| `model_served_by_component` | Component | No | `component_serves_model` | Serving component (Layer 3) |
| `model_uses_feature_store` | FeatureStore | Yes | `provides_features_to_models` | Feature stores used |

**MLModelType Enum:**

| Value | Description |
|---|---|
| `classification` | Classification model |
| `regression` | Regression model |
| `clustering` | Clustering model |
| `recommendation` | Recommendation model |
| `nlp` | Natural Language Processing model |
| `computer_vision` | Computer vision model |
| `generative` | Generative model |
| `reinforcement_learning` | Reinforcement learning model |
| `time_series` | Time series model |
| `anomaly_detection` | Anomaly detection model |

---

### 57. MLModelMetric

A performance metric for an ML model. Typically inlined within MLModel.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `metric_name` | string | **Yes** | Metric name (accuracy, F1, RMSE, etc.) |
| `value` | float | No | Metric value |
| `dataset` | string | No | Evaluation dataset name |

---

### 58. FeatureStore

A centralized store for computed ML features.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `platform` | string | No | Feature store platform (Feast, Tecton, etc.) |
| `storage_backend` | string | No | Storage backend |
| `feature_count` | integer | No | Number of features |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `provides_features_to_models` | MLModel | Yes | `model_uses_feature_store` | Models using this feature store |

---

## K. Testing (3 classes)

### 59. TestSuite

A collection of related test cases.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `suite_type` | TestSuiteType | **Yes** | Kind of test suite |
| `framework` | string | No | Testing framework |
| `source_location` | string | No | Source file path |
| `total_cases` | integer | No | Total test cases |
| `passing_cases` | integer | No | Passing test cases |
| `failing_cases` | integer | No | Failing test cases |
| `skipped_cases` | integer | No | Skipped test cases |
| `execution_time_ms` | integer | No | Total execution time in milliseconds |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contains_test_cases` | TestCase | Yes | `belongs_to_suite` | Test cases in this suite (Layer 3) |
| `tests_component` | Component | No | `tested_by_suites` | Component tested (Layer 3) |
| `tests_module` | Module | No | `module_tested_by_suites` | Module tested |

**TestSuiteType Enum:**

| Value | Description |
|---|---|
| `unit` | Unit tests |
| `integration` | Integration tests |
| `functional` | Functional tests |
| `end_to_end` | End-to-end tests |
| `performance` | Performance tests |
| `security` | Security tests |
| `regression` | Regression tests |
| `smoke` | Smoke tests |
| `contract` | Contract tests |

---

### 60. TestCoverage

Code coverage metrics for a component or module.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `line_coverage_percent` | float | No | Line coverage percentage |
| `branch_coverage_percent` | float | No | Branch coverage percentage |
| `function_coverage_percent` | float | No | Function coverage percentage |
| `statement_coverage_percent` | float | No | Statement coverage percentage |
| `uncovered_lines` | integer[] | No | Uncovered line numbers |
| `coverage_tool` | string | No | Coverage tool (Istanbul, JaCoCo, etc.) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `coverage_for_component` | Component | No | `has_coverage` | Component measured (Layer 3) |
| `coverage_for_module` | Module | No | `module_has_coverage` | Module measured |

---

### 61. TestAssertion

An individual assertion within a test case. Typically inlined within TestCase.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `assertion_type` | AssertionType | No | Kind of assertion |
| `expected_value` | string | No | Expected value |
| `line_number` | integer | No | Source line number |

**AssertionType Enum:**

| Value | Description |
|---|---|
| `equality` | Equality check |
| `truthiness` | True/false check |
| `exception` | Exception expected |
| `type_check` | Type assertion |
| `containment` | Contains/includes check |
| `mock_verification` | Mock call verification |
| `snapshot` | Snapshot comparison |
| `custom` | Custom assertion |

---

## L. Frontend Supporting (3 classes)

### 62. StateStore

A frontend state management store or container.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `management_type` | StateManagementType | **Yes** | Kind of state management |
| `framework` | string | No | State management framework (Redux, Vuex, Zustand, etc.) |
| `has_state_shape` | DataStructure | No | Shape of the state tree (Layer 4) |
| `actions` | string[] | No | Action names |
| `selectors` | string[] | No | Selector names |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `manages_ui_components` | UIComponent | Yes | `managed_by_state` | UI components managed (Layer 3) |

**StateManagementType Enum:**

| Value | Description |
|---|---|
| `local_state` | Component-local state |
| `global_store` | Global state store |
| `context` | Context/provider pattern |
| `url_state` | URL-based state |
| `server_state` | Server-side state (React Query, SWR) |
| `form_state` | Form state management |

---

### 63. UIProperty

A property (prop) passed to a UI component. Typically inlined within UIComponent.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `data_type` | string | No | Property data type |
| `is_required` | boolean | No | Whether the prop is required |
| `default_value` | string | No | Default value |
| `is_reactive` | boolean | No | Whether the prop is reactive |

---

### 64. ConcurrencyPattern

A high-level concurrency pattern used in the system.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `pattern_type` | ConcurrencyPatternType | **Yes** | Kind of pattern |
| `max_concurrency` | integer | No | Maximum concurrency level |
| `framework` | string | No | Framework or library |
| `shared_resources` | string[] | No | Shared resources |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `pattern_used_by_component` | Component | Yes | `component_uses_concurrency_pattern` | Components using this pattern (Layer 3) |

**ConcurrencyPatternType Enum:**

| Value | Description |
|---|---|
| `thread_pool` | Thread pool |
| `actor` | Actor model |
| `channel` | Channel-based communication |
| `future_promise` | Future/Promise |
| `async_await` | Async/Await |
| `fork_join` | Fork-Join |
| `producer_consumer` | Producer-Consumer |
| `reactor` | Reactor pattern |
| `proactor` | Proactor pattern |
| `csp` | Communicating Sequential Processes |

---

## Relationship Map

```
                        ┌──────────── Layer 1 (System Context) ─────────────┐
                        │  System, ExternalSystem, ComplianceRequirement,   │
                        │  RiskAssessment, Actor, Identity, Tenant, ...     │
                        └──────────┬──────────────┬─────────────────────────┘
                                   │              │
                    contained_in_system     integrates_with_system
                    exposed_by_system       belongs_to_system
                                   │              │
┌──────────────────────────────────▼──────────────▼────────────────────────────┐
│                         LAYER 2 (Container)                                  │
│                                                                              │
│  ┌─ STRUCTURAL ──────────────────────────────────────────────────────────┐   │
│  │  BoundedContext ──contains_modules──► Module ──runs_as_services──►    │   │
│  │       │                                │          Service             │   │
│  │       │                                │            │                 │   │
│  │       └──upstream/downstream──►BC      ├──depends──►Module            │   │
│  │                                        └──dependencies──►Dependency   │   │
│  │  Interface (abstract)                                                 │   │
│  │    ├── UserInterface ──screens──► Screen                              │   │
│  │    ├── ProgrammaticInterface ──endpoints──► Endpoint                  │   │
│  │    └── EventInterface ──subscriptions──► (L3)                         │   │
│  │  Route (tree) ──guarded_by──► Policy (L3)                             │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ DATA MANAGEMENT ────────────────────────────────────────────────────┐   │
│  │  DataStore ──collections──► Collection ──stores──► Record             │   │
│  │      │                         ├──constraints──► DatabaseConstraint   │   │
│  │      │                         └──indexes──► DatabaseIndex            │   │
│  │      └──hosted_on──► Infrastructure                                   │   │
│  │                                                                       │   │
│  │  DataClassification    RetentionPolicy ──governs──► Collection, Log   │   │
│  │  DataLineage ──tracks/derives──► Record                               │   │
│  │  AuditLog ──entries──► AuditEntry ──records──► Action (L3)            │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ INTEGRATION ────────────────────────────────────────────────────────┐   │
│  │  Integration ──adapter──► Adapter ──(extends Component, L3)           │   │
│  │      ├──breaker──► CircuitBreaker                                     │   │
│  │      ├──contract──► Contract ──versions──► ContractVersion            │   │
│  │      └──messages──► Message                                           │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ DEPLOYMENT & RUNTIME ───────────────────────────────────────────────┐   │
│  │  Environment ──hosts──► Deployment ──deploys──► Service               │   │
│  │      │                      ├──unit──► DeploymentUnit                 │   │
│  │      │                      ├──config──► Configuration                │   │
│  │      │                      └──release──► Release                     │   │
│  │      └──infra──► Infrastructure ◄──iac──── IaCDefinition              │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ OBSERVABILITY ──────────────────────────────────────────────────────┐   │
│  │  Metric ◄──monitors── AlertRule ──triggers──► Alert                   │   │
│  │  Log ──entries──► LogEntry                      │                     │   │
│  │  Trace ──spans──► Span (tree)        escalates──► Incident            │   │
│  │  HealthCheck (inline in Service)           │──affects──► Service       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ BUILD & CI/CD ─────────────────────────────────────────────────────┐   │
│  │  BuildPipeline ──stages──► PipelineStage                              │   │
│  │      ├──produces──► BuildArtifact ──stored_in──► ArtifactRegistry     │   │
│  │      ├──deploys_to──► Environment                                     │   │
│  │      └──uses_iac──► IaCDefinition                                     │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ DEPENDENCY MANAGEMENT ──────────────────────────────────────────────┐   │
│  │  PackageManager ──manages──► Module                                   │   │
│  │  PackageDependency ──vulnerabilities──► KnownVulnerability            │   │
│  │      └──transitive──► PackageDependency                               │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ IaC ───────────────────────────────────────────────────────────────┐   │
│  │  IaCDefinition ──resources──► IaCResource                             │   │
│  │  IaCModule ──child_resources──► IaCResource                           │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ ML & DATA PIPELINES ───────────────────────────────────────────────┐   │
│  │  DataPipeline ──steps──► DataPipelineStep                             │   │
│  │      ├──reads/writes──► DataStore                                     │   │
│  │      └──uses──► Dataset                                               │   │
│  │  MLModel ──metrics──► MLModelMetric                                   │   │
│  │      └──features──► FeatureStore                                      │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ TESTING ───────────────────────────────────────────────────────────┐   │
│  │  TestSuite ──tests──► Component (L3), Module                          │   │
│  │  TestCoverage ──covers──► Component (L3), Module                      │   │
│  │  TestAssertion (inline in TestCase, L3)                               │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ FRONTEND SUPPORTING ───────────────────────────────────────────────┐   │
│  │  StateStore ──manages──► UIComponent (L3)                             │   │
│  │  UIProperty (inline in UIComponent, L3)                               │   │
│  │  ConcurrencyPattern ──used_by──► Component (L3)                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                    contains_components, contains_aggregates,
                    persists_aggregates, controls_features, ...
                                   │
                        ┌──────────▼────────────────────────────┐
                        │  Layer 3 (Component)                   │
                        │  Component, Aggregate, DomainEntity,   │
                        │  Operation, Rule, Event, Workflow, ... │
                        └───────────────────────────────────────┘
```
