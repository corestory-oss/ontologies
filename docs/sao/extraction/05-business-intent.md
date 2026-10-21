# Phase 5: Business Intent

**Input:** All prior phase outputs (Phases 1--4) + documentation + domain knowledge
**Output:** **HumanActor**, **SystemActor**, **Operation**, **Query**, **Command**, **Rule**, **DomainEvent**, **IntegrationEvent**, **Subscription**, **Workflow**, **Step**, **Transaction**, **Capability**, **Feature**, **Message**

---

## 1. Overview

Phase 5 is the highest-abstraction layer in the SAO extraction process. Where earlier phases answer "what is the code?" and "how is it structured?", this phase answers **"what does the system do, and for whom?"**

This is the most inferential phase in the playbook. Most entities here cannot be parsed mechanically from source code -- they MUST be inferred from documentation, naming conventions, interaction patterns, and domain knowledge. Estimated automation: 20--30%. The remaining 70--80% requires LLM inference combined with human validation.

Key characteristics of Phase 5 extraction:

- **Documentation is a critical input.** User stories, API docs, product specs, and README files are often the primary source for actors, capabilities, and features.
- **Every entity produced in this phase SHOULD be flagged for human review.** Even when an LLM can plausibly infer a business intent, a domain expert MUST validate the result before it is considered authoritative.
- **Prior phase outputs are prerequisites.** Phase 5 builds on the **CallableUnit**, **Component**, **Module**, **DomainEntity**, **Aggregate**, and **Schema** instances produced in Phases 2--4. Without them, the bridge from code to intent cannot be established.

---

## 2. Step 1: Identify Actors

**Actor** is an abstract class representing any entity that can initiate actions. The extraction agent MUST NOT instantiate **Actor** directly; instead, use its concrete subtypes **HumanActor** and **SystemActor**.

### HumanActor

Set `actor_type` to one of:

- `end_user` -- regular end user of the system
- `administrator` -- system administrator with elevated privileges
- `operator` -- operations personnel managing system runtime
- `developer` -- software developer or engineer
- `auditor` -- compliance or security auditor

Set `name`, `description`, and `email` where known.

**Sources:** authentication/authorization code (role definitions, user role enums), user-facing documentation, API consumer descriptions.

```yaml
- HumanActor:
    name: CustomerUser
    description: End user who browses products and places orders
    category: human
    actor_type: end_user
    has_identities:
      - CustomerIdentity
```

### SystemActor

Set `actor_type` to one of:

- `internal_service` -- internal service within the system
- `external_system` -- external third-party system
- `scheduled_process` -- scheduled or cron-based process
- `ai_agent` -- artificial intelligence agent or bot
- `message_trigger` -- message or event-triggered automation

Set `name`, `description`, and `service_account` where known.

**Sources:** scheduled jobs (cron, Quartz, CICS START), message consumers (Kafka listeners, RabbitMQ handlers), external API clients, service-to-service authentication configs.

```yaml
- SystemActor:
    name: PaymentGateway
    description: External payment processing system (Stripe)
    category: system
    actor_type: external_system
    service_account: stripe-webhook-svc

- SystemActor:
    name: NightlyReportGenerator
    description: Scheduled process that generates daily sales reports
    category: system
    actor_type: scheduled_process
    service_account: report-gen-cron
```

### Linking Actors to Identities

The extraction agent SHOULD link `Actor.has_identities` to **Identity** instances. Identity extraction is detailed in Phase 6 (Cross-Cutting Concerns); in Phase 5, the agent SHOULD create placeholder references that Phase 6 will resolve.

---

## 3. Step 2: Extract Operations

Create an **Operation** for each named, invocable business action exposed via an interface. An **Operation** bridges the gap between a user-visible action and the code that implements it.

### Required attributes

| Attribute | Description |
|---|---|
| `name` | Operation name (e.g., `PlaceOrder`, `AuthenticateUser`) |
| `description` | What the operation does in business terms |
| `accepts_input_schema` | Reference to the input **Schema** |
| `produces_output_schema` | Reference to the output **Schema** |

### Key relationships

- `Operation.implemented_by_callables` -- MUST link to one or more **CallableUnit** instances from Phase 2. This is the essential bridge from business intent to code.
- `Operation.exposed_by_component` -- SHOULD link to the **Component** that exposes this operation.
- `Operation.executes_operation_actions` -- links to the **Action** instances (Queries and Commands) the operation performs.
- `Operation.offered_on_screens` -- links to **Screen** instances where the operation appears in a UI.

**Sources:** API endpoint handlers (REST controllers, gRPC service methods), service facade methods, CICS transaction handlers, GraphQL resolvers.

```yaml
- Operation:
    name: PlaceOrder
    description: Accepts a cart and creates a confirmed order
    errors:
      - InsufficientInventoryError
      - PaymentDeclinedError
    exposed_by_component: OrderService
    accepts_input_schema: PlaceOrderRequest
    produces_output_schema: OrderConfirmation
    implemented_by_callables:
      - OrderController.placeOrder
      - OrderService.processOrder
    executes_operation_actions:
      - CreateOrderCommand
```

---

## 4. Step 3: Classify Actions as Queries or Commands

**Action** is an abstract class with two concrete subtypes: **Query** (read-only) and **Command** (state-changing). The extraction agent MUST classify every business action into one of these subtypes.

### Common attributes (inherited from Action)

| Attribute | Description |
|---|---|
| `category` | `query`, `command`, or `mutation` |
| `performed_by_actor` | The **Actor** who performs this action |
| `targets_resources` | **Resource** instances affected |
| `validated_by_action_rules` | **Rule** instances that validate this action |
| `emits_events_from_action` | **Event** instances emitted by this action |
| `executes_in_transaction` | **Transaction** context for this action |

### Query

A read-only action that retrieves data without side effects.

| Attribute | Description |
|---|---|
| `filters` | Query filter expressions |
| `projections` | Fields to return |

```yaml
- Query:
    name: SearchProducts
    description: Search product catalog by keyword and category
    category: query
    performed_by_actor: CustomerUser
    filters:
      - "keyword LIKE '%term%'"
      - "category = :category"
    projections:
      - id
      - name
      - price
      - thumbnail_url
    targets_resources:
      - ProductCatalog
```

### Command

An action that changes system state.

| Attribute | Description |
|---|---|
| `command_type` | `create`, `update`, `delete`, `execute`, `archive`, `restore` |
| `idempotency_key` | Key for idempotent execution |

```yaml
- Command:
    name: CreateOrder
    description: Creates a new order from the customer's cart
    category: command
    command_type: create
    performed_by_actor: CustomerUser
    idempotency_key: cart_id
    targets_resources:
      - OrderAggregate
    validated_by_action_rules:
      - InventoryAvailabilityRule
      - MinimumOrderAmountRule
    emits_events_from_action:
      - OrderCreated
```

### Classification heuristic

| Signal | Classification |
|---|---|
| HTTP GET, GraphQL query, SQL SELECT | **Query** |
| HTTP POST/PUT/DELETE, SQL INSERT/UPDATE/DELETE | **Command** |
| Method name starts with `get`, `find`, `list`, `search`, `fetch` | **Query** |
| Method name starts with `create`, `update`, `delete`, `process`, `submit` | **Command** |
| Returns data without persistence writes | **Query** |
| Triggers events, writes to a data store, or changes entity state | **Command** |
| CICS RECEIVE MAP followed by SEND MAP only | **Query** |
| CICS WRITE / REWRITE / DELETE on VSAM/DB2 | **Command** |

When a method both reads and writes (e.g., `transferFunds`), classify it as a **Command** with `category` set to `mutation`.

---

## 5. Step 4: Extract Rules

Create a **Rule** for each validation constraint, business policy, guard clause, or derivation logic.

### Required attributes

| Attribute | Description |
|---|---|
| `name` | Descriptive rule name |
| `category` | `validation`, `business`, `derivation`, `constraint`, `trigger` |
| `condition` | The rule predicate (the "if" part) |
| `action` | What happens when the rule fires (the "then" part) |
| `priority` | Evaluation order (lower = higher priority) |
| `is_active` | Whether the rule is currently active |

### Key relationships

- `Rule.validates_actions` -- which **Action** instances this rule validates
- `Rule.validates_attributes` -- which **Attribute** instances this rule constrains
- `Rule.governs_domain_entities` -- which **DomainEntity** instances this rule governs
- `Rule.guards_transitions` -- which **Transition** instances this rule guards (for state machines)
- `Rule.enforces_aggregate_invariants` -- which **Aggregate** instances this rule protects

### Rule categories explained

| Category | Purpose | Typical source |
|---|---|---|
| `validation` | Data integrity checks | `@NotNull`, `@Size`, `@Pattern`, input validators |
| `business` | Business logic constraints | Policy checks, eligibility rules, discount logic |
| `derivation` | Computed/derived values | `total = sum(lineItems)`, `tax = subtotal * rate` |
| `constraint` | Domain invariants | Balance >= 0, stock >= 0, unique email |
| `trigger` | Event-driven automation | "When order ships, send email", "When inventory low, alert" |

**Sources:** validation annotations (`@NotNull`, `@Size`, `@Valid`), if/throw patterns, guard clauses, policy service methods, COBOL paragraph-level condition checks (IF/EVALUATE), database constraints.

```yaml
- Rule:
    name: MinimumOrderAmountRule
    category: business
    condition: "order.total >= 10.00"
    action: "Allow order to proceed"
    priority: 1
    is_active: true
    validates_actions:
      - CreateOrder
    governs_domain_entities:
      - Order

- Rule:
    name: EmailFormatValidation
    category: validation
    condition: "email matches RFC 5322 pattern"
    action: "Reject with INVALID_EMAIL error"
    priority: 1
    is_active: true
    validates_attributes:
      - User.email
```

---

## 6. Step 5: Extract Events

**Event** is the base class for notifications that something occurred. The extraction agent MUST use its concrete subtypes: **DomainEvent** and **IntegrationEvent**.

### Common attributes (inherited from Event)

| Attribute | Description |
|---|---|
| `name` | Event name, past tense by convention (e.g., `OrderPlaced`) |
| `category` | `domain_event`, `integration_event`, `system_event`, `audit_event` |
| `correlation_id` | For tracing related events |
| `event_structured_by_schema` | **Schema** defining the event payload |
| `emitted_by_component` | **Component** that produces the event |

### DomainEvent

A significant occurrence within a bounded context, produced by an **Aggregate**.

- Set `produced_by_aggregate` to reference the originating **Aggregate**.
- Set `category` to `domain_event`.

```yaml
- DomainEvent:
    name: OrderPlaced
    description: Emitted when a customer successfully places an order
    category: domain_event
    produced_by_aggregate: OrderAggregate
    event_structured_by_schema: OrderPlacedPayload
    emitted_by_component: OrderService
```

### IntegrationEvent

A cross-service communication event that bridges bounded contexts or external systems.

- Set `targeted_at_services` to reference the **Service** instances that consume the event.
- Set `category` to `integration_event`.

```yaml
- IntegrationEvent:
    name: OrderShippedNotification
    description: Published to notify billing and notification services
    category: integration_event
    targeted_at_services:
      - BillingService
      - NotificationService
    event_structured_by_schema: OrderShippedPayload
```

### Subscription

Create a **Subscription** for each event consumer registration.

| Attribute | Description |
|---|---|
| `name` | Subscription name |
| `filter` | Filter expression for event selection |
| `delivery_mode` | Push or pull delivery |
| `subscribes_to_event_types` | **Event** instances subscribed to |
| `subscribed_by_actor` | **Actor** that owns the subscription |
| `subscribes_to_interface` | **EventInterface** for delivery |

```yaml
- Subscription:
    name: BillingOrderShippedSubscription
    filter: "event.type = 'OrderShippedNotification'"
    delivery_mode: push
    subscribes_to_event_types:
      - OrderShippedNotification
    subscribed_by_actor: BillingService
```

### Message

Create a **Message** when the integration involves explicit message payloads (e.g., message queues, topic-based messaging).

```yaml
- Message:
    name: OrderShippedMessage
    message_type: event
    message_structured_by_schema: OrderShippedPayload
```

**Sources:** event publishing code (`EventBus.publish()`, Kafka `ProducerRecord`, RabbitMQ `basicPublish`), event handler annotations (`@EventHandler`, `@KafkaListener`), CICS START commands, domain event classes, message broker configurations.

---

## 7. Step 6: Extract Workflows

Create a **Workflow** for each multi-step business process that coordinates multiple actions toward a business goal.

### Workflow attributes

| Attribute | Description |
|---|---|
| `name` | Workflow name |
| `workflow_type` | `synchronous`, `asynchronous`, `saga`, `choreography`, `orchestration` |
| `steps` | Ordered list of **Step** instances |
| `triggered_by_workflow_events` | **Event** instances that start the workflow |

### Step attributes

| Attribute | Description |
|---|---|
| `name` | Step name |
| `order` | Execution order (integer) |
| `condition` | Condition for execution |
| `timeout_seconds` | Step timeout in seconds |
| `executes_actions_in_step` | **Action** instances executed during this step |
| `followed_by_steps` | Next **Step** instances in the sequence |
| `compensated_by_step` | Compensating **Step** for saga rollback |

### Transaction

Create a **Transaction** for each transaction boundary encountered.

| Attribute | Description |
|---|---|
| `name` | Transaction name |
| `transaction_type` | `local`, `distributed`, `saga`, `two_phase_commit` |
| `isolation_level` | Transaction isolation level (e.g., `read_committed`) |
| `timeout_seconds` | Transaction timeout in seconds |
| `executes_actions` | **Action** instances within this transaction |

**Sources:** saga implementations, orchestration engines (Temporal, Camunda, Step Functions), multi-step handler methods, COBOL paragraph sequences with EXEC CICS SYNCPOINT, Spring `@Transactional` boundaries, database transaction blocks.

```yaml
- Workflow:
    name: OrderFulfillmentSaga
    workflow_type: saga
    triggered_by_workflow_events:
      - OrderPlaced
    steps:
      - Step:
          name: ReserveInventory
          order: 1
          timeout_seconds: 5
          executes_actions_in_step:
            - ReserveInventoryCommand
          compensated_by_step: ReleaseInventory
          followed_by_steps:
            - AuthorizePayment
      - Step:
          name: AuthorizePayment
          order: 2
          timeout_seconds: 10
          executes_actions_in_step:
            - AuthorizePaymentCommand
          compensated_by_step: CancelAuthorization
          followed_by_steps:
            - CreateShipment
      - Step:
          name: CreateShipment
          order: 3
          timeout_seconds: 5
          executes_actions_in_step:
            - CreateShipmentCommand
          compensated_by_step: CancelShipment
          followed_by_steps:
            - ConfirmOrder
      - Step:
          name: ConfirmOrder
          order: 4
          executes_actions_in_step:
            - ConfirmOrderCommand

- Transaction:
    name: OrderCreationTransaction
    transaction_type: local
    isolation_level: read_committed
    timeout_seconds: 30
    executes_actions:
      - CreateOrder
      - DeductInventory
```

### Compensation steps for sagas

For each forward step in a saga workflow, the extraction agent SHOULD create a corresponding compensation step and link it via `compensated_by_step`. Compensation steps are themselves **Step** instances:

```yaml
- Step:
    name: ReleaseInventory
    order: 1
    executes_actions_in_step:
      - ReleaseInventoryCommand
```

---

## 8. Step 7: Synthesize Capabilities and Features

**Capability** and **Feature** represent the highest level of abstraction in SAO. They describe what the system can do and how users experience it.

### Capability

A discrete business or technical ability the system provides.

| Attribute | Description |
|---|---|
| `name` | Capability name |
| `description` | What this capability provides |
| `provided_by_modules` | **Module** instances that implement this capability |
| `requires_permissions` | **Permission** instances needed (from Phase 6) |
| `realizes_features` | **Feature** instances this capability realizes |
| `enables_features` | **Feature** instances this capability enables |

### Feature

A user-facing manifestation of one or more capabilities.

| Attribute | Description |
|---|---|
| `name` | Feature name |
| `category` | `core`, `optional`, `experimental`, `deprecated` |
| `enabled_by_capabilities` | **Capability** instances that enable this feature |
| `realized_by_capabilities` | **Capability** instances that realize this feature |
| `controlled_by_configs` | **Configuration** instances (for feature flags) |
| `accessible_by_roles` | **Role** instances that can access this feature |

**Sources:** product documentation, feature flag configurations (LaunchDarkly, Unleash, `@FeatureToggle`), capability-oriented package structure, marketing materials, user stories.

```yaml
- Capability:
    name: OrderManagement
    description: Ability to create, track, modify, and cancel customer orders
    provided_by_modules:
      - OrderModule
      - InventoryModule
    requires_permissions:
      - orders.create
      - orders.read
      - orders.update
      - orders.cancel
    realizes_features:
      - OnlineOrdering
    enables_features:
      - OrderTracking
      - OrderHistory

- Feature:
    name: OnlineOrdering
    description: Allows customers to place orders through the web storefront
    category: core
    enabled_by_capabilities:
      - OrderManagement
      - PaymentProcessing
      - InventoryManagement
    realized_by_capabilities:
      - OrderManagement
    controlled_by_configs:
      - OnlineOrderingFeatureFlag
    accessible_by_roles:
      - Customer
      - Administrator

- Feature:
    name: BetaRecommendationEngine
    description: AI-powered product recommendations on product pages
    category: experimental
    enabled_by_capabilities:
      - RecommendationEngine
    controlled_by_configs:
      - RecommendationEngineToggle
    accessible_by_roles:
      - BetaCustomer
```

---

## 9. Phase 5 Checklist

Before proceeding to Phase 6, verify the following:

- [ ] **Actors identified.** Both **HumanActor** and **SystemActor** instances created with correct `actor_type` values. Every actor has a `name` and `description`.
- [ ] **Operations extracted.** Each named business action has an **Operation** instance. Every **Operation** MUST link to at least one **CallableUnit** via `implemented_by_callables`.
- [ ] **Actions classified.** Every business action is classified as a **Query** or **Command** with correct `category` and (for commands) `command_type`.
- [ ] **Rules extracted.** Validation constraints, business policies, and guard clauses captured as **Rule** instances with `category`, `condition`, and `action` set.
- [ ] **Events identified.** Significant domain occurrences captured as **DomainEvent** instances; cross-service events captured as **IntegrationEvent** instances. Each event has a `category` and links to its producing **Aggregate** or target services.
- [ ] **Subscriptions created.** Event consumers registered as **Subscription** instances linking events to actors.
- [ ] **Workflows extracted.** Multi-step business processes captured as **Workflow** instances with ordered **Step** sequences. Saga workflows include compensation steps.
- [ ] **Transactions defined.** Transaction boundaries captured as **Transaction** instances with `transaction_type` and `isolation_level`.
- [ ] **Capabilities and Features synthesized.** System abilities captured as **Capability** instances; user-facing features captured as **Feature** instances with appropriate `category`.
- [ ] **Human review flagged.** All entities produced in this phase are marked for domain expert validation.
