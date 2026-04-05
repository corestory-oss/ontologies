# Layer 3: Component-Level Representation

This document defines the SAO v2.0 classes that correspond to **C4 Level 3 (Component)** -- the logical building blocks inside a deployable unit, their responsibilities, and relationships. This layer sits between the code (Layer 4) and the container/service boundary (Layer 2).

Where Layer 4 answers "what does the source code look like?", Layer 3 answers "what are the logical parts of this application, what do they do, and how do they interact?"

---

## Scope

Layer 3 covers:

- **Component architecture** -- logical building blocks, operations they expose, capabilities and features they provide
- **Domain model** -- aggregates, entities, value objects, their attributes, relationships, and lifecycle
- **Behavior and workflow** -- actions, rules, events, workflows, and transactions
- **Authorization and policy** -- roles, permissions, policies, scopes, and constraints
- **Supporting structures** -- schemas, tests, annotations, imports, concurrency, and UI components

Unlike Layer 4, which splits into Modern and Legacy profiles based on programming paradigm, **Layer 3 is largely paradigm-agnostic**. A COBOL batch system and a Java microservice both have components, domain entities, business rules, and authorization models. The differences emerge in *how* these concepts are implemented (Layer 4), not in *what* they are (Layer 3).

The one exception is **UIComponent**, which specifically models modern component-tree UI frameworks (React, Angular, Vue) -- with concepts like props, lazy loading, server rendering, route binding, state store management, and parent/child component hierarchies. Legacy terminal screens (CICS BMS maps, RPG display files, MFS formats) are a fundamentally different model -- fixed-grid character maps with positional fields compiled from source members -- and are fully captured at Layer 4 via ScreenDefinition/ScreenField. This creates a deliberate asymmetry: modern UI has representation at both Layer 3 (UIComponent as a logical building block) and Layer 4 (EncapsulationUnit for the source file), while legacy UI lives entirely at Layer 4 (ScreenDefinition as a compiled source artifact).

---

## Summary

| # | Class | Definition | Group | SAO Section |
|---|---|---|---|---|
| 1 | Component | A logical building block within a module or service, grouping related operations | Component Architecture | 2 |
| 2 | Operation | A named, invocable unit of behavior exposed via a component's interface | Component Architecture | 6 |
| 3 | Capability | A business capability the system provides, realized by features and requiring permissions | Component Architecture | 2 |
| 4 | Feature | A user-facing feature that can be toggled, access-controlled, and categorized | Component Architecture | 2 |
| 5 | UIComponent | A UI component in a modern component-tree framework (React, Angular, Vue) | Component Architecture | 2 |
| 6 | Aggregate | A cluster of domain entities treated as a single transactional consistency boundary | Domain Model | 5 |
| 7 | DomainEntity | A uniquely identifiable object within the domain with identity, lifecycle, and state | Domain Model | 5 |
| 8 | ValueObject | An immutable domain object defined entirely by its attributes, with no identity | Domain Model | 5 |
| 9 | Attribute | A named property of a domain entity or value object (domain-level, not code-level) | Domain Model | 5 |
| 10 | DomainRelationship | A named, typed relationship between two domain entities with cardinality and composition | Domain Model | 26 |
| 11 | Resource | A domain entity or value object exposed for external interaction (API representation / DTO) | Domain Model | 5 |
| 12 | ResourceType | A classification of resources sharing common structure, permissions, and schema | Domain Model | 5 |
| 13 | State | A discrete condition in an entity's lifecycle (e.g., Draft, Active, Closed) | Lifecycle | 5 |
| 14 | Transition | A valid movement between two states, with guards, triggers, and side effects | Lifecycle | 5 |
| 15 | Lifecycle | The complete state machine for an entity type -- all states and valid transitions | Lifecycle | 5 |
| 16 | Action (abstract) | An atomic operation that can be performed; base for Query and Command | Behavior | 6 |
| 17 | Query | A read-only action that retrieves data, with filters and projections | Behavior | 6 |
| 18 | Command | A state-changing action (create, update, delete, execute, archive, restore) | Behavior | 6 |
| 19 | Rule | A declarative constraint or trigger governing validation, business logic, or invariants | Behavior | 6 |
| 20 | Event | A notification that something occurred in the system | Behavior | 6 |
| 21 | DomainEvent | An event produced by an aggregate within a bounded context | Behavior | 6 |
| 22 | IntegrationEvent | An event for cross-service communication | Behavior | 6 |
| 23 | Subscription | A registration to receive events of a certain type, with filtering | Behavior | 6 |
| 24 | Workflow | A coordinated sequence of actions achieving a business goal (saga, choreography, etc.) | Behavior | 6 |
| 25 | Step | A discrete stage within a workflow, with ordering and compensation | Behavior | 6 |
| 26 | Transaction | A unit of work with ACID or BASE guarantees (local, distributed, saga, 2PC) | Behavior | 6 |
| 27 | Role | A collection of permissions assignable to identities, with inheritance | Authorization | 4 |
| 28 | Permission | An atomic access grant connecting actions to resources, scoped and constrained | Authorization | 4 |
| 29 | Policy | A rule set for access decisions (RBAC, ABAC, REBAC, PBAC) | Authorization | 4 |
| 30 | Scope | A permission boundary defining where a permission applies (global, tenant, resource, field) | Authorization | 4 |
| 31 | Constraint | A contextual restriction on a permission (temporal, spatial, attribute, rate limit) | Authorization | 4 |
| 32 | Schema | A versioned data structure definition used by operations, resources, events, and messages | Supporting | 7 |
| 33 | SchemaVersion | A specific version of a schema, with migration support and compatibility tracking | Supporting | 7 |
| 34 | TestCase | A test case targeting a callable unit or operation, with assertions and fixtures | Supporting | 12 |
| 35 | Annotation | A metadata annotation or decorator attached to code elements (@Override, #[derive]) | Supporting | 12 |
| 36 | DefinitionReference | A reference from one code container to another (import, include, COPY, using) | Supporting | 12 |
| 37 | ConcurrencyPrimitive | A synchronization primitive used by callables to protect data (mutex, semaphore, lock) | Supporting | 12 |

**Total: 37 classes** (including 4 subtypes: Query, Command, DomainEvent, IntegrationEvent that inherit from abstract parents).

---

## Connections to Adjacent Layers

### Downward links to Layer 4 (Code)

These relationships connect Layer 3 concepts to their code-level implementations:

| Layer 3 class | Attribute | Layer 4 class | Description |
|---|---|---|---|
| Component | `implemented_by_code` | EncapsulationUnit, CallableUnit, DataStructure | Global slot -- code that implements this component |
| Operation | `implemented_by_callables` | CallableUnit | Methods/functions that implement this operation |
| DomainEntity | `mapped_from_structure` | DataStructure | Code-level data structures representing this entity |
| ValueObject | `mapped_from_structure_vo` | DataStructure | Code-level structures representing this value object |
| Attribute | `mapped_from_element` | DataElement | Code-level fields mapping to this domain attribute |
| TestCase | `tests_callable` | CallableUnit | Callable being tested |
| Annotation | `annotates_element` | EncapsulationUnit, CallableUnit, DataStructure, DataElement | Code elements bearing this annotation |
| ConcurrencyPrimitive | `used_by_callables` | CallableUnit | Callables using this primitive |
| ConcurrencyPrimitive | `protects_data_elements` | DataElement | Data elements guarded by this primitive |
| UIComponent | `ui_implements_encapsulation_unit` | EncapsulationUnit | Code unit rendering this UI component |

### Upward links to Layer 2 (Container)

These relationships connect Layer 3 concepts to their container-level parents:

| Layer 3 class | Attribute | Layer 2 class | Description |
|---|---|---|---|
| Component | `contained_in_module` | Module | Module containing this component |
| Aggregate | `contained_in_bounded_context` | BoundedContext | Bounded context owning this aggregate |
| Aggregate | `persisted_in_stores` | DataStore | Data stores backing this aggregate |
| Capability | `provided_by_modules` | Module | Modules providing this capability |
| Feature | `controlled_by_configs` | Configuration | Runtime feature configuration |
| IntegrationEvent | `targeted_at_services` | Service | Services receiving this event |
| Policy | `enforced_by_system` | System | System enforcing this policy |

---

## Component Architecture (5 classes)

### 1. Component

A logical building block within a module or service. Components group related operations and encapsulate a coherent responsibility.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `component_type` | string | No | Freeform type (e.g., "controller", "repository", "service", "gateway") |
| `language` | string | No | **Deprecated** -- use CodeContainer.written_in_language via Layer 4 |
| `source_location` | string | No | Source path hint |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `contained_in_module` | Module | No | `contains_components` | Parent module (Layer 2) |
| `exposes_operations` | Operation | Yes | `exposed_by_component` | Operations this component provides |
| `emits_events` | Event | Yes | `emitted_by_component` | Events produced |
| `dependencies` | Dependency | Yes | -- | Inline dependency declarations |
| `implemented_by_code` | EncapsulationUnit \| CallableUnit \| DataStructure | Yes | `implements_component` | Code implementations (Layer 4, global slot) |
| `tested_by_suites` | TestSuite | Yes | `tests_component` | Test suites |
| `has_coverage` | TestCoverage | No | `coverage_for_component` | Coverage metrics |
| `emits_metrics` | Metric | Yes | -- | Metrics emitted |
| `generates_logs` | Log | Yes | -- | Logs generated |
| `emits_metric` | Metric | Yes | `metric_emitted_by_component` | Named metric link |
| `component_serves_model` | MLModel | Yes | `model_served_by_component` | ML models served |
| `component_uses_concurrency_pattern` | ConcurrencyPattern | Yes | `pattern_used_by_component` | Concurrency patterns |

---

### 2. Operation

A named, invocable unit of behavior exposed via a component's interface. This is the primary bridge between the API surface (what the system exposes) and the code (what implements it).

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `errors` | string[] | No | Possible error responses |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `exposed_by_component` | Component | No | `exposes_operations` | Component providing this operation |
| `executes_operation_actions` | Action | Yes | `executed_by_operation` | Actions performed when invoked |
| `accepts_input_schema` | Schema | No | `defines_operation_input` | Input schema/contract |
| `produces_output_schema` | Schema | No | `defines_operation_output` | Output schema/contract |
| `implemented_by_callables` | CallableUnit | Yes | `implements_operation` | Code implementations (Layer 4) |
| `offered_on_screens` | Screen | Yes | `offers_operations` | Screens presenting this operation |
| `operation_tested_by_cases` | TestCase | Yes | `tests_operation` | Test cases |

---

### 3. Capability

A business capability that the system provides. Capabilities are realized by features and require specific permissions.

**Attributes:**

*No additional attributes beyond NamedEntity.*

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `realizes_features` | Feature | Yes | `realized_by_capabilities` | Features this capability realizes |
| `enables_features` | Feature | Yes | `enabled_by_capabilities` | Features enabled by this capability |
| `requires_permissions` | Permission | Yes | `required_by_capabilities` | Permissions needed |
| `provided_by_modules` | Module | Yes | `provides_capabilities` | Modules providing this (Layer 2) |

---

### 4. Feature

A user-facing feature that can be toggled, access-controlled, and categorized.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `category` | FeatureCategory | No | `core`, `optional`, `experimental`, `deprecated` |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `enabled_by_capabilities` | Capability | Yes | `enables_features` | Capabilities enabling this feature |
| `realized_by_capabilities` | Capability | Yes | `realizes_features` | Capabilities realizing this feature |
| `controlled_by_configs` | Configuration | Yes | `controls_features` | Feature flag configurations (Layer 2) |
| `accessible_by_roles` | Role | Yes | `can_access_features` | Roles with access |

**FeatureCategory Enum:**

| Value | Description |
|---|---|
| `core` | Core functionality, always active |
| `optional` | Optional, can be toggled |
| `experimental` | Under experimentation |
| `deprecated` | Scheduled for removal |

---

### 5. UIComponent

A UI component in a modern component-tree framework (React, Angular, Vue, Svelte). This class models the logical component hierarchy -- props, composition, routing, state management, lazy loading, and server rendering -- concepts specific to virtual-DOM and component-based architectures. It is **not** a general-purpose "screen" abstraction. Legacy terminal screens (CICS BMS maps, RPG display files) are fundamentally different -- fixed-grid character maps compiled from source -- and are modeled at Layer 4 via ScreenDefinition/ScreenField.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `component_type` | UIComponentType | **Yes** | Kind of UI component |
| `framework` | string | No | Framework (React, Angular, Vue, etc.) |
| `props` | UIProperty[] | No | Component properties (inline) |
| `emitted_events` | string[] | No | Events this component emits |
| `is_lazy_loaded` | boolean | No | Whether lazily loaded |
| `is_server_rendered` | boolean | No | Whether server-side rendered |
| `accessibility_role` | string | No | ARIA role |
| `source_location` | string | No | Source path |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `parent_ui_component` | UIComponent | No | `child_ui_components` | Parent in component tree |
| `child_ui_components` | UIComponent | Yes | `parent_ui_component` | Children in component tree |
| `renders_on_route` | Route | Yes | `route_renders_component` | Routes rendering this component |
| `managed_by_state` | StateStore | Yes | `manages_ui_components` | State stores managing this component |
| `ui_implements_encapsulation_unit` | EncapsulationUnit | No | `encapsulation_unit_renders_ui` | Code implementation (Layer 4) |

**UIComponentType Enum:**

| Value | Description |
|---|---|
| `page` | Full page component |
| `layout` | Layout wrapper |
| `form` | Form component |
| `widget` | Standalone widget |
| `modal` | Modal/dialog |
| `navigation` | Navigation component |
| `data_display` | Data display (table, chart, list) |
| `composite` | Composite of other components |
| `higher_order` | Higher-order component (wrapper) |
| `provider` | Context/state provider |

---

## Domain Model (7 classes)

### 6. Aggregate

A cluster of domain entities treated as a single transactional unit. The fundamental consistency boundary in domain-driven design.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `value_objects` | ValueObject[] | No | Value objects within this aggregate (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `has_root_entity` | DomainEntity | No | `is_root_of_aggregate` | **Required.** The root entity |
| `aggregates_entities` | DomainEntity | Yes | `aggregated_by` | Entities within this aggregate (inline) |
| `enforced_by_invariant_rules` | Rule | Yes | `enforces_aggregate_invariants` | Invariant rules |
| `persisted_in_stores` | DataStore | Yes | `persists_aggregates` | Backing data stores (Layer 2) |
| `contained_in_bounded_context` | BoundedContext | No | `contains_aggregates` | Parent bounded context (Layer 2) |
| `produces_domain_events` | DomainEvent | Yes | `produced_by_aggregate` | Domain events produced |

---

### 7. DomainEntity

A uniquely identifiable object within the domain. Entities have identity, lifecycle, and mutable state.

**Mixins:** `Auditable` (adds audit tracking fields)

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `attributes` | Attribute[] | No | Domain attributes (inline) |
| `classifications` | DataClassificationType[] | No | Data classification (PII, PHI, PCI, etc.) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `aggregated_by` | Aggregate | No | `aggregates_entities` | Parent aggregate |
| `is_root_of_aggregate` | Aggregate | No | `has_root_entity` | Aggregate for which this is root |
| `exposes_as_resource` | Resource | Yes | `represents_entity` | API resources exposing this entity |
| `governed_by_lifecycle` | Lifecycle | No | `governs_entities` | State machine governing this entity |
| `in_state` | State | No | `current_for_entities` | Current lifecycle state |
| `governed_by_rules` | Rule | Yes | `governs_domain_entities` | Business rules governing this entity |
| `mapped_from_structure` | DataStructure | Yes | `maps_to_domain_entity` | Code structures (Layer 4) |
| `outgoing_relationships` | DomainRelationship | Yes | `source_entity` | Relationships originating from this entity |
| `incoming_relationships` | DomainRelationship | Yes | `target_entity` | Relationships targeting this entity |

---

### 8. ValueObject

An immutable domain object defined entirely by its attributes, with no conceptual identity. Compared by value, not by ID.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `attributes` | Attribute[] | No | Attributes defining this value object (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `mapped_from_structure_vo` | DataStructure | Yes | `maps_to_value_object` | Code structures (Layer 4) |

---

### 9. Attribute

A named property of a domain entity or value object. This is the *domain-level* attribute (not the code-level DataElement, which lives at Layer 4).

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `data_type` | string | **Yes** | Data type |
| `category` | AttributeCategory | No | `required`, `optional`, `computed`, `derived`, `transient` |
| `is_identifier` | boolean | No | Whether this is an identity attribute |
| `is_indexed` | boolean | No | Whether indexed for querying |
| `default_value` | string | No | Default value |
| `classification` | DataClassificationType | No | Data sensitivity (PII, PHI, PCI, PUBLIC, etc.) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `validated_by_rules` | Rule | Yes | `validates_attributes` | Validation rules |
| `mapped_from_element` | DataElement | Yes | `maps_to_attribute` | Code-level fields (Layer 4) |

**AttributeCategory Enum:**

| Value | Description |
|---|---|
| `required` | Must have a value |
| `optional` | May be null |
| `computed` | Calculated from other attributes |
| `derived` | Derived from other entities or data |
| `transient` | Not persisted |

---

### 10. DomainRelationship

A named, typed relationship between two domain entities with cardinality, navigability, and composition semantics. Introduced in SAO v2.0 (Section 26).

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `cardinality` | Cardinality | **Yes** | Multiplicity of the relationship |
| `is_navigable` | boolean | No | Traversable from source to target |
| `is_bidirectional` | boolean | No | Traversable in both directions |
| `is_composition` | boolean | No | UML composition (strong ownership) vs aggregation |
| `foreign_key_field` | string | No | Implementing field in data layer |
| `join_entity` | string | No | Join table/entity for many-to-many |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `source_entity` | DomainEntity | No | `outgoing_relationships` | Entity originating the relationship |
| `target_entity` | DomainEntity | No | `incoming_relationships` | Entity referenced |

**Cardinality Enum:**

| Value | Description |
|---|---|
| `one_to_one` | 1:1 |
| `one_to_many` | 1:N |
| `many_to_one` | N:1 |
| `many_to_many` | M:N |

---

### 11. Resource

A domain entity or value object exposed for external interaction -- the API representation (DTO) of a domain object.

**Attributes:**

*No additional attributes beyond NamedEntity.*

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `represents_entity` | DomainEntity | No | `exposes_as_resource` | Domain entity this resource represents |
| `classified_as_type` | ResourceType | No | `classifies_resources` | Resource type classification |
| `targeted_by_actions` | Action | Yes | `targets_resources` | Actions that can target this resource |
| `affected_in_audit` | AuditEntry | Yes | `affects_resource` | Audit trail entries |

---

### 12. ResourceType

A classification of resources sharing common structure, permissions, and schema.

**Attributes:**

*No additional attributes beyond NamedEntity.*

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `structured_by_schema` | Schema | No | `structures_resource_types` | Schema defining this type's structure |
| `classifies_resources` | Resource | Yes | `classified_as_type` | Resource instances of this type |
| `governed_by_permissions` | Permission | Yes | `applies_to_resource_types` | Permissions governing access |

---

## Lifecycle (3 classes)

### 13. State

A discrete condition in an entity's lifecycle.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `is_initial` | boolean | No | Whether this is the starting state |
| `is_terminal` | boolean | No | Whether this is a final state |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `allows_actions_in_state` | Action | Yes | `allowed_in_states` | Actions allowed in this state |
| `current_for_entities` | DomainEntity | Yes | `in_state` | Entities currently in this state |
| `source_of_transitions` | Transition | Yes | `transitions_from_state` | Transitions out of this state |
| `target_of_transitions` | Transition | Yes | `transitions_to_state` | Transitions into this state |
| `initial_for_lifecycle` | Lifecycle | No | `starts_with_state` | Lifecycle for which this is the start |

---

### 14. Transition

A valid movement between two states, with guards, triggers, and side effects.

**Attributes:**

*No additional attributes beyond NamedEntity.*

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `transitions_from_state` | State | No | `source_of_transitions` | **Required.** Source state |
| `transitions_to_state` | State | No | `target_of_transitions` | **Required.** Target state |
| `triggered_by_events` | Event | Yes | `triggers_transitions` | Events that trigger this transition |
| `guarded_by_rules` | Rule | Yes | `guards_transitions` | Rules that must pass |
| `executes_actions_on_transition` | Action | Yes | `executed_during_transition` | Actions executed during transition |

---

### 15. Lifecycle

The complete state machine for an entity type -- all states and valid transitions.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `states` | State[] | No | All states (inline) |
| `transitions` | Transition[] | No | All transitions (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `starts_with_state` | State | No | `initial_for_lifecycle` | Initial state |
| `governs_entities` | DomainEntity | Yes | `governed_by_lifecycle` | Entities following this lifecycle |

---

## Behavior and Workflow (11 classes)

### 16. Action (abstract)

An atomic operation that can be performed. Abstract base for Query and Command.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `category` | ActionCategory | No | `query`, `command`, `mutation` |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `allowed_by_permissions` | Permission | Yes | `allows_actions` | Permissions required |
| `performed_by_actor` | Actor | No | `performs_actions` | Actor performing (Layer 2) |
| `targets_resources` | Resource | Yes | `targeted_by_actions` | Resources affected |
| `emits_events_from_action` | Event | Yes | `emitted_by_action` | Events emitted |
| `validated_by_action_rules` | Rule | Yes | `validates_actions` | Validation rules |
| `executes_in_transaction` | Transaction | No | `executes_actions` | Transaction context |
| `allowed_in_states` | State | Yes | `allows_actions_in_state` | States where this action is allowed |
| `executed_during_transition` | Transition | Yes | `executes_actions_on_transition` | Transitions executing this action |
| `executed_by_operation` | Operation | Yes | `executes_operation_actions` | Operations invoking this action |
| `executed_in_step` | Step | Yes | `executes_actions_in_step` | Workflow steps |
| `recorded_in_audit` | AuditEntry | Yes | `records_action` | Audit trail |

**ActionCategory Enum:**

| Value | Description |
|---|---|
| `query` | Read-only, retrieves data |
| `command` | Changes system state |
| `mutation` | Modifies data |

---

### 17. Query

A read-only action that retrieves data. Inherits all Action attributes and relationships.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `filters` | string[] | No | Query filter expressions |
| `projections` | string[] | No | Fields to return |

---

### 18. Command

An action that changes system state. Inherits all Action attributes and relationships.

**Additional Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `command_type` | CommandType | No | Kind of command |
| `idempotency_key` | string | No | Key for idempotent execution |

**CommandType Enum:**

| Value | Description |
|---|---|
| `create` | Create a new entity |
| `update` | Update existing entity |
| `delete` | Delete an entity |
| `execute` | Execute a process |
| `archive` | Archive an entity |
| `restore` | Restore an archived entity |

---

### 19. Rule

A declarative constraint or trigger governing behavior. Rules validate attributes, enforce aggregate invariants, guard transitions, and validate actions.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `category` | RuleCategory | No | Kind of rule |
| `condition` | string | No | Condition expression |
| `action` | string | No | Action when rule fires |
| `priority` | integer | No | Evaluation priority |
| `is_active` | boolean | No | Whether currently active |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `validates_attributes` | Attribute | Yes | `validated_by_rules` | Attributes validated |
| `enforces_aggregate_invariants` | Aggregate | Yes | `enforced_by_invariant_rules` | Aggregates with invariants |
| `governs_domain_entities` | DomainEntity | Yes | `governed_by_rules` | Entities governed |
| `validates_actions` | Action | Yes | `validated_by_action_rules` | Actions validated |
| `guards_transitions` | Transition | Yes | `guarded_by_rules` | Transitions guarded |

**RuleCategory Enum:**

| Value | Description |
|---|---|
| `validation` | Data integrity validation |
| `business` | Business logic |
| `derivation` | Computed/derived values |
| `constraint` | Invariant enforcement |
| `trigger` | Event-driven automation |

---

### 20. Event

A notification that something occurred in the system.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `category` | EventCategory | No | Kind of event |
| `correlation_id` | string | No | Correlation ID for tracing |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `emitted_by_component` | Component | No | `emits_events` | Source component |
| `event_structured_by_schema` | Schema | No | `structures_events` | Payload schema |
| `emitted_by_action` | Action | Yes | `emits_events_from_action` | Actions emitting this event |
| `triggers_transitions` | Transition | Yes | `triggered_by_events` | Transitions triggered |
| `triggers_workflows` | Workflow | Yes | `triggered_by_workflow_events` | Workflows triggered |
| `subscribed_by_subscriptions` | Subscription | Yes | `subscribes_to_event_types` | Subscriptions |

**EventCategory Enum:**

| Value | Description |
|---|---|
| `domain_event` | Significant domain occurrence (OrderPlaced, UserRegistered) |
| `integration_event` | Cross-service communication |
| `system_event` | Technical system event (ServiceStarted, CacheCleared) |
| `audit_event` | Compliance/audit trail (UserLoggedIn, PermissionChanged) |

---

### 21. DomainEvent

An event produced by an aggregate within a bounded context. Inherits all Event attributes and relationships.

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `produced_by_aggregate` | Aggregate | No | `produces_domain_events` | Source aggregate |

---

### 22. IntegrationEvent

An event for cross-service communication. Inherits all Event attributes and relationships.

**Additional Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `targeted_at_services` | Service | Yes | `receives_integration_events` | Target services (Layer 2) |

---

### 23. Subscription

A registration to receive events of a certain type.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `filter` | string | No | Filter expression for event selection |
| `delivery_mode` | string | No | Push or pull delivery |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `subscribes_to_event_types` | Event | Yes | `subscribed_by_subscriptions` | Event types subscribed to |
| `subscribed_by_actor` | Actor | No | `actor_subscriptions` | Subscribing actor (Layer 2) |
| `subscribes_to_interface` | EventInterface | No | `has_subscriptions` | Delivery interface |

---

### 24. Workflow

A coordinated sequence of actions achieving a business goal.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `workflow_type` | WorkflowType | No | Coordination pattern |
| `steps` | Step[] | No | Ordered steps (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `triggered_by_workflow_events` | Event | Yes | `triggers_workflows` | Events that start this workflow |

**WorkflowType Enum:**

| Value | Description |
|---|---|
| `synchronous` | Blocking, immediate response |
| `asynchronous` | Background processing |
| `saga` | Distributed transaction with compensating actions |
| `choreography` | Event-driven, no central orchestrator |
| `orchestration` | Centrally coordinated |

---

### 25. Step

A discrete stage within a workflow.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `order` | integer | No | Execution order |
| `condition` | string | No | Condition for execution |
| `timeout_seconds` | integer | No | Timeout |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `executes_actions_in_step` | Action | Yes | `executed_in_step` | Actions executed |
| `followed_by_steps` | Step | Yes | `follows_step` | Next steps |
| `follows_step` | Step | Yes | `followed_by_steps` | Previous steps |
| `compensated_by_step` | Step | No | `compensates_for_step` | Compensating step (saga rollback) |
| `compensates_for_step` | Step | No | `compensated_by_step` | Step this compensates for |

---

### 26. Transaction

A unit of work with ACID or BASE guarantees.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `transaction_type` | TransactionType | No | Kind of transaction |
| `isolation_level` | string | No | Isolation level |
| `timeout_seconds` | integer | No | Timeout |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `executes_actions` | Action | Yes | `executes_in_transaction` | Actions in this transaction |

**TransactionType Enum:**

| Value | Description |
|---|---|
| `local` | Single-database ACID |
| `distributed` | Cross-resource transaction |
| `saga` | Long-running with compensating actions |
| `two_phase_commit` | 2PC protocol |

---

## Authorization and Policy (5 classes)

### 27. Role

A collection of permissions that can be assigned to identities.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `is_system_role` | boolean | No | Whether this is a built-in system role |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `grants_permissions` | Permission | Yes | `granted_by_roles` | Permissions this role grants |
| `assigned_to_identities` | Identity | Yes | `has_roles` | Identities with this role (Layer 2) |
| `inherits_from_role` | Role | No | `inherited_by_roles` | Parent role |
| `inherited_by_roles` | Role | Yes | `inherits_from_role` | Child roles |
| `can_access_features` | Feature | Yes | `accessible_by_roles` | Features accessible |

---

### 28. Permission

An atomic access grant connecting actions to resources, scoped and constrained.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `constraints` | Constraint[] | No | Contextual constraints (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `allows_actions` | Action | Yes | `allowed_by_permissions` | Actions this permission enables |
| `granted_by_roles` | Role | Yes | `grants_permissions` | Roles granting this permission |
| `applies_to_resource_types` | ResourceType | Yes | `governed_by_permissions` | Resource types governed |
| `limited_by_scope` | Scope | No | `limits_permissions` | Scope boundary |
| `required_by_capabilities` | Capability | Yes | `requires_permissions` | Capabilities requiring this |
| `evaluated_by_policies` | Policy | Yes | `evaluates_permissions` | Policies evaluating this |

---

### 29. Policy

A rule set for access decisions, supporting multiple authorization models.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `policy_type` | PolicyType | No | Authorization model |
| `rules` | Rule[] | No | Policy rules (inline) |
| `priority` | integer | No | Evaluation priority |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `evaluates_permissions` | Permission | Yes | `evaluated_by_policies` | Permissions evaluated |
| `enforced_by_system` | System | No | `enforces_policies` | System enforcing this policy (Layer 1/2) |
| `guards_routes` | Route | Yes | `route_guarded_by` | Routes protected |

**PolicyType Enum:**

| Value | Description |
|---|---|
| `rbac` | Role-Based Access Control |
| `abac` | Attribute-Based Access Control |
| `rebac` | Relationship-Based Access Control |
| `pbac` | Policy-Based Access Control |

---

### 30. Scope

A permission boundary defining where a permission applies.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `scope_type` | ScopeType | No | Kind of scope |
| `resource_pattern` | string | No | Resource pattern (e.g., `orders/*`) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `limits_permissions` | Permission | Yes | `limited_by_scope` | Permissions bounded by this scope |

**ScopeType Enum:**

| Value | Description |
|---|---|
| `global` | Applies system-wide |
| `tenant` | Scoped to a tenant |
| `organization` | Scoped to an organization |
| `resource` | Scoped to a specific resource |
| `field` | Scoped to a field within a resource |

---

### 31. Constraint

A contextual restriction on a permission -- temporal, spatial, or attribute-based conditions.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `constraint_type` | ConstraintType | No | Kind of constraint |
| `expression` | string | No | Constraint expression |
| `parameters` | string[] | No | Parameters for the expression |

**ConstraintType Enum:**

| Value | Description |
|---|---|
| `temporal` | Time-based (business hours, expiry) |
| `spatial` | Location-based (geo-fence) |
| `attribute` | Attribute-based (user.department = resource.department) |
| `context` | Context-based (device, IP, session) |
| `rate_limit` | Rate limiting |

---

## Supporting Structures (6 classes)

### 32. Schema

A versioned data structure definition used by operations, resources, events, and messages.

**Mixins:** `Versionable`

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `schema_type` | SchemaType | No | Kind of schema |
| `definition` | string | No | Schema definition content |
| `schema_versions` | SchemaVersion[] | No | Version history (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `structures_resource_types` | ResourceType | Yes | `structured_by_schema` | Resource types using this schema |
| `structures_collections` | Collection | Yes | `collection_structured_by_schema` | Database collections (Layer 2) |
| `structures_events` | Event | Yes | `event_structured_by_schema` | Events using this schema |
| `structures_messages` | Message | Yes | `message_structured_by_schema` | Messages (Layer 2) |
| `defines_operation_input` | Operation | Yes | `accepts_input_schema` | Operations accepting this as input |
| `defines_operation_output` | Operation | Yes | `produces_output_schema` | Operations producing this as output |
| `validates_records` | Record | Yes | `conforms_to_schema` | Records validated (Layer 2) |

**SchemaType Enum:**

| Value | Description |
|---|---|
| `table_schema` | Database table schema |
| `document_schema` | Document/NoSQL schema |
| `event_schema` | Event payload schema |
| `api_schema` | API request/response schema |
| `message_schema` | Message schema |

---

### 33. SchemaVersion

A specific version of a schema, with migration support.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `version` | SemanticVersion | No | Version number |
| `definition` | string | No | Schema definition at this version |
| `migration_script` | string | No | Migration from previous version |
| `is_backward_compatible` | boolean | No | Whether backward compatible |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `version_of_schema` | Schema | No | `schema_versions` | Parent schema |

---

### 34. TestCase

A test case targeting a callable unit or operation.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `status` | TestCaseStatus | No | Test status |
| `priority` | string | No | Priority level |
| `is_automated` | boolean | No | Whether automated |
| `setup_fixture` | string | No | Setup fixture name |
| `teardown_fixture` | string | No | Teardown fixture name |
| `line_start` | integer | No | Starting line in source |
| `line_end` | integer | No | Ending line in source |
| `assertions` | TestAssertion[] | No | Assertions (inline) |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `belongs_to_suite` | TestSuite | No | `contains_test_cases` | Parent suite |
| `tests_callable` | CallableUnit | No | `tested_by_cases` | Callable tested (Layer 4) |
| `tests_operation` | Operation | No | `operation_tested_by_cases` | Operation tested |

---

### 35. Annotation

A metadata annotation or decorator attached to code elements.

**Global Slots:**

| Slot | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `annotates_element` | EncapsulationUnit \| CallableUnit \| DataStructure \| DataElement | Yes | `annotated_by` | Code elements bearing this annotation (Layer 4) |
| `affects_behavior_of` | EncapsulationUnit \| CallableUnit | Yes | -- | Code elements whose behavior is altered |

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `annotation_syntax` | string | No | Syntax form (e.g., `@Override`, `#[derive(Debug)]`) |
| `parameters` | string[] | No | Annotation parameters |

---

### 36. DefinitionReference

A reference from one code container to shared definitions -- imports, includes, COPY statements, using directives.

**Global Slots:**

| Slot | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `imports_symbols` | EncapsulationUnit \| CallableUnit \| DataStructure | Yes | `imported_via` | Symbols imported (Layer 4) |

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `reference_type` | ReferenceType | No | `import_module`, `import_symbol`, `include_source`, `inherit`, `implement` |
| `reference_path` | string | No | Path or module name |
| `alias` | string | No | Import alias |
| `is_wildcard` | boolean | No | Wildcard import (e.g., `import *`) |
| `scope` | string | No | Import scope |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `referencing_container` | CodeContainer | No | `has_references` | Source container (Layer 4) |
| `referenced_container` | CodeContainer | No | `referenced_via` | Target container (Layer 4) |

---

### 37. ConcurrencyPrimitive

A synchronization or concurrency primitive used by callables to protect data elements.

**Attributes:**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `primitive_type` | ConcurrencyPrimitiveType | **Yes** | Kind of primitive |
| `is_reentrant` | boolean | No | Whether reentrant |
| `timeout_ms` | integer | No | Lock timeout |
| `line_number` | integer | No | Source line |

**Relationships:**

| Relationship | Range | Multi | Inverse | Description |
|---|---|---|---|---|
| `used_by_callables` | CallableUnit | Yes | `uses_concurrency_primitives` | Callables using this (Layer 4) |
| `protects_data_elements` | DataElement | Yes | `protected_by_primitive` | Data elements guarded (Layer 4) |

---

## Relationship Map

```
                        ┌─────────── Layer 2 (Container) ───────────┐
                        │  Module, BoundedContext, Service,          │
                        │  DataStore, Configuration, System          │
                        └──────────┬───────────┬────────────────────┘
                                   │           │
                    contained_in_module    contained_in_bounded_context
                                   │           │
              ┌────────────────────▼───────────▼──────────────────────┐
              │              COMPONENT ARCHITECTURE                    │
              │                                                       │
              │  Component ──exposes_operations──► Operation           │
              │      │                               │    │           │
              │      ├──emits_events──► Event         │    │           │
              │      │                   │            │    │           │
              │  Capability ◄──────► Feature          │    │           │
              │      │                   │            │    │           │
              │      └──requires_permissions──┐       │    │           │
              │                               │       │    │           │
              │  UIComponent (tree)           │       │    │           │
              └──────────────────────────────┼───────┼────┼───────────┘
                                             │       │    │
              ┌──────────────────────────────┼───────┼────┼───────────┐
              │              DOMAIN MODEL    │       │    │            │
              │                              │       │    │            │
              │  Aggregate ──has_root──► DomainEntity │    │            │
              │      │                    │  ▲  │    │    │            │
              │      ├──value_objects──► ValueObject  │    │            │
              │      │                    │     │    │    │            │
              │      ├──invariant_rules──►Rule  │    │    │            │
              │      │                    │     │    │    │            │
              │      └──produces──► DomainEvent │    │    │            │
              │                              │  │    │    │            │
              │  DomainEntity ──attributes──► Attribute   │            │
              │       │                         │    │    │            │
              │       ├──lifecycle──► Lifecycle  │    │    │            │
              │       │    ├──states──► State    │    │    │            │
              │       │    └──transitions──► Transition   │            │
              │       │                              │    │            │
              │       ├──exposes_as──► Resource ──► ResourceType       │
              │       │                              │    │            │
              │       └──relationships──► DomainRelationship           │
              └──────────────────────────────────────┼────┼────────────┘
                                                     │    │
              ┌──────────────────────────────────────┼────┼────────────┐
              │              BEHAVIOR                 │    │            │
              │                                      │    │            │
              │  Action (Query, Command) ◄───────────┘    │            │
              │      │                                    │            │
              │      ├──targets──► Resource               │            │
              │      ├──emits──► Event ──► Subscription   │            │
              │      ├──validated_by──► Rule              │            │
              │      └──in_transaction──► Transaction     │            │
              │                                           │            │
              │  Workflow ──steps──► Step ──actions──► Action           │
              │      │         └──compensated_by──► Step               │
              │      └──triggered_by──► Event                          │
              └───────────────────────────────────────┬────────────────┘
                                                      │
              ┌───────────────────────────────────────┼────────────────┐
              │              AUTHORIZATION            │                │
              │                                       │                │
              │  Role ──grants──► Permission ◄──evaluates── Policy     │
              │    │                  │                                 │
              │    └──access──► Feature    ├──allows──► Action          │
              │                           ├──applies_to──► ResourceType │
              │                           ├──limited_by──► Scope        │
              │                           └──constraints──► Constraint  │
              └────────────────────────────────────────────────────────┘
                                             │
              ┌──────────────────────────────┼─────────────────────────┐
              │              SUPPORTING      │                         │
              │                              │                         │
              │  Schema ──versions──► SchemaVersion                    │
              │    │                                                   │
              │    ├──structures──► ResourceType, Event, Operation     │
              │                                                       │
              │  TestCase ──tests──► CallableUnit (L4), Operation      │
              │  Annotation ──annotates──► code elements (L4)          │
              │  DefinitionReference ──imports──► code elements (L4)   │
              │  ConcurrencyPrimitive ──protects──► DataElement (L4)   │
              └───────────────────────────────────────────────────────┘
                                   │
                    implemented_by_code, implemented_by_callables,
                    mapped_from_structure, mapped_from_element, ...
                                   │
                        ┌──────────▼────────────────────────┐
                        │  Layer 4 (Code)                    │
                        │  CodeContainer, EncapsulationUnit, │
                        │  CallableUnit, DataStructure, ...  │
                        └───────────────────────────────────┘
```
