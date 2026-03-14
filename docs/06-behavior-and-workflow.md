# Section 5: Behavior and Workflow

This section defines actions, operations, workflows, rules, events, subscriptions, and transactions.

> **v2.0 Note — Inlining Change**: In SAO v2.0, many previously string-based cross-references have been replaced with direct object references (inlined relationships). Classes in this section now carry explicit back-reference attributes that make the bidirectional links between ontology concepts navigable from either side.

## Overview

The Behavior and Workflow section models how the system behaves, processes requests, executes business logic, and coordinates complex multi-step operations.

## Core Concepts

### Action (Abstract)

**Definition**: An atomic operation that can be performed.

**Key Attributes**:
- **category**: QUERY (read-only), COMMAND (state-changing), MUTATION (data modification)

**Relationships**:
- **allowed_by_permissions**: `Permission` entities required
- **performed_by_actor**: `Actor` performing the action
- **targets_resources**: `Resource` entities affected
- **emits_events_from_action**: `Event` entities emitted
- **validated_by_action_rules**: `Rule` entities that validate
- **executes_in_transaction**: `Transaction` context
- **allowed_in_states** *(v2.0)*: Back-reference to `State` entities that allow this action
- **executed_during_transition** *(v2.0)*: Back-reference to `Transition` entities that execute this action
- **executed_by_operation** *(v2.0)*: Back-reference to `Operation` entities that execute this action
- **executed_in_step** *(v2.0)*: Back-reference to `Step` entities that execute this action
- **recorded_in_audit** *(v2.0)*: Back-reference to `AuditEntry` entities that record this action

**Specialized Action Types**:

#### Query
Read-only action that retrieves data.
- **filters**: Query filters
- **projections**: Fields to return
- **Examples**: GetUser, SearchProducts, ListOrders

#### Command
Action that changes system state.
- **command_type**: CREATE, UPDATE, DELETE, EXECUTE, ARCHIVE, RESTORE
- **idempotency_key**: For idempotent execution
- **Examples**: CreateOrder, UpdateProfile, DeleteComment

---

### Operation

**Definition**: A named, invocable unit of behavior exposed via an interface.

**Purpose**: Represents a callable operation on a component or service.

**Relationships**:
- **exposed_by_component**: `Component` providing this operation
- **executes_operation_actions**: `Action` entities performed
- **accepts_input_schema**: `Schema` for input
- **produces_output_schema**: `Schema` for output
- **offered_on_screens**: `Screen` entities offering this operation
- **implemented_by_callables** *(v2.0)*: `Callable` entities that implement this operation
- **operation_tested_by_cases** *(v2.0)*: `TestCase` entities that test this operation

**Key Attributes**:
- **errors**: Possible error responses

**Example Operations**:
- PlaceOrder(order_details) -> OrderConfirmation
- AuthenticateUser(credentials) -> AuthToken
- ProcessPayment(payment_info) -> PaymentResult
- GenerateReport(parameters) -> Report

---

### Workflow

**Definition**: A coordinated sequence of actions achieving a business goal.

**Purpose**: Orchestrates multi-step business processes.

**Key Attributes**:
- **workflow_type**: SYNCHRONOUS, ASYNCHRONOUS, SAGA, CHOREOGRAPHY, ORCHESTRATION
- **steps**: Ordered list of `Step` entities

**Relationships**:
- **triggered_by_workflow_events**: `Event` entities that start the workflow

**Workflow Types**:

#### SYNCHRONOUS
Blocking workflow that waits for completion.
- **Use Case**: Real-time operations with immediate response
- **Example**: User registration during signup

#### ASYNCHRONOUS
Non-blocking workflow processed in background.
- **Use Case**: Long-running operations
- **Example**: Bulk data import

#### SAGA
Distributed transaction with compensating actions.
- **Use Case**: Cross-service transactions
- **Example**: Order placement with inventory reservation, payment, shipping

#### CHOREOGRAPHY
Event-driven coordination without central orchestrator.
- **Use Case**: Loosely coupled services
- **Example**: Order fulfillment via events

#### ORCHESTRATION
Centrally coordinated workflow.
- **Use Case**: Complex multi-step processes
- **Example**: Employee onboarding process

**Example Workflows**:
- Order fulfillment workflow
- User onboarding workflow
- Invoice generation workflow
- Password reset workflow

---

### Step

**Definition**: A discrete stage within a workflow.

**Key Attributes**:
- **order**: Execution order
- **condition**: Condition for execution
- **timeout_seconds**: Step timeout

**Relationships**:
- **executes_actions_in_step**: `Action` entities executed
- **followed_by_steps**: Next steps in sequence
- **compensated_by_step**: Compensating step for rollback

**Step Patterns**:
- **Sequential**: Steps execute in order
- **Parallel**: Steps execute concurrently
- **Conditional**: Steps execute based on conditions
- **Compensating**: Rollback steps for saga pattern

---

### Rule

**Definition**: A declarative constraint or trigger governing behavior.

**Key Attributes**:
- **category**: VALIDATION, BUSINESS, DERIVATION, CONSTRAINT, TRIGGER
- **condition**: Rule condition expression
- **action**: Action when rule fires
- **priority**: Evaluation priority
- **is_active**: Whether rule is currently active

**Relationships** *(v2.0 back-references)*:
- **validates_attributes**: Back-reference to `Attribute` entities validated by this rule
- **enforces_aggregate_invariants**: Back-reference to `Aggregate` entities whose invariants this rule enforces
- **governs_domain_entities**: Back-reference to `DomainEntity` entities governed by this rule
- **validates_actions**: Back-reference to `Action` entities validated by this rule
- **guards_transitions**: Back-reference to `Transition` entities guarded by this rule

**Rule Categories**:

#### VALIDATION Rules
Validate data integrity.
- **Examples**: "Email must be valid format", "Age must be >= 18"

#### BUSINESS Rules
Encode business logic.
- **Examples**: "Premium customers get 20% discount", "Orders over $100 ship free"

#### DERIVATION Rules
Compute derived values.
- **Examples**: "Total = sum of line items", "Tax = subtotal * tax_rate"

#### CONSTRAINT Rules
Enforce invariants.
- **Examples**: "Account balance cannot be negative", "Stock quantity must be non-negative"

#### TRIGGER Rules
Automate actions based on events.
- **Examples**: "Send email when order ships", "Alert when inventory low"

**Rule Evaluation**:
1. Check if rule is active
2. Evaluate condition
3. If condition true, execute action
4. Log rule execution

---

### Event

**Definition**: A notification that something occurred.

**Key Attributes**:
- **category**: DOMAIN_EVENT, INTEGRATION_EVENT, SYSTEM_EVENT, AUDIT_EVENT
- **correlation_id**: For tracing related events

**Relationships**:
- **emitted_by_component**: `Component` that produced the event
- **event_structured_by_schema**: `Schema` defining event payload
- **emitted_by_action** *(v2.0)*: Back-reference to `Action` entities that emit this event
- **triggers_transitions** *(v2.0)*: Back-reference to `Transition` entities triggered by this event
- **triggers_workflows** *(v2.0)*: Back-reference to `Workflow` entities triggered by this event
- **subscribed_by_subscriptions** *(v2.0)*: Back-reference to `Subscription` entities that subscribe to this event

**Event Categories**:

#### DOMAIN_EVENT
Significant occurrence in the domain.
- **Naming**: Past tense (OrderPlaced, PaymentProcessed)
- **Examples**: OrderCreated, UserRegistered, ProductUpdated

#### INTEGRATION_EVENT
Cross-service communication.
- **Purpose**: Integrate bounded contexts or services
- **Examples**: OrderShipped (from fulfillment to billing)

#### SYSTEM_EVENT
System-level technical events.
- **Examples**: ServiceStarted, CacheCleared, ConfigReloaded

#### AUDIT_EVENT
Compliance and audit trail.
- **Examples**: UserLoggedIn, PermissionChanged, DataExported

**Specialized Event Types**:

#### DomainEvent
Produced by aggregates within a bounded context.
- **produced_by_aggregate**: Source `Aggregate`

#### IntegrationEvent
For cross-service communication.
- **targeted_at_services**: Target `Service` entities

**Event-Driven Patterns**:
- **Event Sourcing**: Store events as source of truth
- **CQRS**: Separate read and write models
- **Event Notification**: Simple notification of change
- **Event-Carried State Transfer**: Event contains full state

---

### Subscription

**Definition**: A registration to receive events of a certain type.

**Key Attributes**:
- **filter**: Filter expression for event selection
- **delivery_mode**: Push or pull delivery

**Relationships**:
- **subscribes_to_event_types**: `Event` types subscribed to
- **subscribed_by_actor**: `Actor` subscribing
- **subscribes_to_interface**: `EventInterface` for delivery

**Subscription Patterns**:
- **Topic Subscription**: Subscribe to event topic
- **Pattern Matching**: Subscribe to events matching pattern
- **Content-Based**: Subscribe based on event content

---

### Transaction

**Definition**: A unit of work with ACID or BASE guarantees.

**Key Attributes**:
- **transaction_type**: LOCAL, DISTRIBUTED, SAGA, TWO_PHASE_COMMIT
- **isolation_level**: Transaction isolation level
- **timeout_seconds**: Transaction timeout

**Relationships**:
- **executes_actions**: `Action` entities in this transaction

**Transaction Types**:

#### LOCAL
Single database transaction with ACID guarantees.

#### DISTRIBUTED
Transaction across multiple resources.
- **Challenge**: Difficult to maintain ACID guarantees
- **Solution**: Two-phase commit or distributed transaction coordinator

#### SAGA
Pattern for long-running distributed transactions.
- **Approach**: Sequence of local transactions
- **Rollback**: Compensating transactions
- **Types**: Choreography-based or orchestration-based

#### TWO_PHASE_COMMIT
Distributed transaction protocol.
- **Phases**: Prepare phase, Commit phase
- **Guarantees**: Atomicity across resources
- **Drawback**: Performance and availability impact

---

## Behavioral Patterns

### Command Pattern
- Commands encapsulate requests as objects
- Support queuing, logging, undo operations
- Enable asynchronous execution

### Chain of Responsibility
- Rules evaluated in sequence
- First applicable rule handles request
- Supports priority-based evaluation

### State Pattern
- Behavior changes based on entity state
- Actions allowed in specific states
- Transitions trigger behaviors

### Observer Pattern
- Events notify subscribed observers
- Loose coupling between publisher and subscribers
- Support multiple subscribers

### Saga Pattern
- Coordinate distributed transactions
- Each step has compensating action
- Ensures eventual consistency

---

## Best Practices

### Action Design
1. **Idempotency**: Make commands idempotent when possible
2. **Validation**: Validate before executing
3. **Authorization**: Check permissions before execution
4. **Atomicity**: Keep actions atomic

### Workflow Design
1. **Compensation**: Define compensating actions for sagas
2. **Timeout**: Set appropriate timeouts
3. **Retries**: Implement retry logic with exponential backoff
4. **Monitoring**: Track workflow execution and failures

### Event Design
1. **Immutability**: Events should be immutable
2. **Minimal Payload**: Include only necessary data
3. **Versioning**: Version events for schema evolution
4. **Ordering**: Preserve event ordering when required

### Rule Design
1. **Declarative**: Express rules declaratively
2. **Testable**: Make rules easy to test
3. **Maintainable**: Keep rules simple and focused
4. **Auditable**: Log rule evaluations

---

## Relationships with Other Sections

- **Section 2 (Actors and Identity)**: Actors perform actions
- **Section 3 (Authorization)**: Actions require permissions
- **Section 4 (Domain Modeling)**: Actions operate on entities; events trigger transitions
- **Section 6 (Data Management)**: Actions recorded in audit logs
- **Section 7 (Integration)**: Integration events cross system boundaries
- **Section 9 (Observability)**: Events generate logs and metrics

---

## Example: Order Processing Workflow

```
Workflow: ProcessOrderWorkflow (SAGA)
  Trigger: OrderPlaced event

  Step 1: Reserve Inventory
    Actions: ReserveInventoryCommand
    Compensation: ReleaseInventoryCommand
    Timeout: 5 seconds

  Step 2: Authorize Payment
    Actions: AuthorizePaymentCommand
    Compensation: CancelAuthorizationCommand
    Timeout: 10 seconds

  Step 3: Create Shipment
    Actions: CreateShipmentCommand
    Compensation: CancelShipmentCommand
    Timeout: 5 seconds

  Step 4: Confirm Order
    Actions: ConfirmOrderCommand
    Events: OrderConfirmed

  Error Handling:
    - If any step fails, execute compensating actions in reverse order
    - Emit OrderFailed event
    - Notify customer of failure
```
