# Section 4: Domain Modeling

This section defines domain-driven design concepts including aggregates, entities, value objects, attributes, resources, states, and lifecycles.

## Overview

The Domain Modeling section provides a comprehensive framework for modeling business domains using Domain-Driven Design (DDD) principles. It supports defining domain entities, aggregates, value objects, and their lifecycle management.

## Core Concepts

### Aggregate

**Definition**: A cluster of domain entities treated as a single transactional unit. Corresponds to DDD aggregate concept.

**Purpose**: Enforces consistency boundaries and transactional integrity within the domain model.

**Key Attributes**:
- Inherits from `NamedEntity`
- **value_objects**: List of value objects within the aggregate

**Relationships**:
- **aggregates_entities**: `DomainEntity` instances within this aggregate
- **has_root_entity**: The root `DomainEntity` (required, single)
- **enforced_by_invariant_rules**: `Rule` entities that enforce aggregate invariants
- **persisted_in_stores**: `DataStore` entities where this aggregate is persisted
- **produced_by_aggregate**: `DomainEvent` entities produced
- **contained_in_bounded_context**: Parent `BoundedContext`

**Aggregate Design Principles**:
1. **Small Aggregates**: Keep aggregates as small as possible
2. **Consistency Boundaries**: Enforce invariants within aggregate boundaries
3. **Reference by ID**: Reference other aggregates by ID only
4. **Single Transaction**: Changes to aggregate should be in single transaction
5. **Eventual Consistency**: Use domain events for cross-aggregate consistency

**Example Aggregates**:
- **Order Aggregate**: Root = Order, Entities = OrderLineItems
- **User Account Aggregate**: Root = User, Entities = UserProfile, Preferences
- **Shopping Cart Aggregate**: Root = Cart, Entities = CartItems
- **Reservation Aggregate**: Root = Reservation, Entities = ReservationItems

---

### DomainEntity

**Definition**: A uniquely identifiable object within the domain.

**Purpose**: Represents business objects with distinct identity that persists over time.

**Key Attributes**:
- Inherits from `NamedEntity`
- Implements `Auditable` mixin
- **attributes**: List of `Attribute` entities
- **classifications**: Data classification types applied

**Relationships**:
- **aggregated_by**: Parent `Aggregate`
- **exposes_as_resource**: `Resource` entities that expose this entity externally
- **governed_by_lifecycle**: `Lifecycle` defining valid states and transitions
- **in_state**: Current `State` in the lifecycle
- **governed_by_rules**: `Rule` entities governing this entity
- **is_root_of_aggregate**: Aggregate for which this is the root entity

**Entity vs Value Object**:
- **Entity**: Has identity, mutable, compared by ID
- **Value Object**: No identity, immutable, compared by attributes

**Example Entities**:
- Customer (ID, name, email, created_at)
- Order (ID, order_number, customer_id, status)
- Product (ID, SKU, name, price)
- Invoice (ID, invoice_number, amount, due_date)

---

### ValueObject

**Definition**: An immutable domain object defined by its attributes.

**Purpose**: Represents descriptive aspects of the domain with no conceptual identity.

**Key Attributes**:
- Inherits from `NamedEntity`
- **attributes**: List of `Attribute` entities defining the value object

**Value Object Characteristics**:
1. **Immutable**: Cannot be modified after creation
2. **No Identity**: Compared by attribute values
3. **Replaceable**: Entire value object is replaced for updates
4. **Shareable**: Can be shared between entities safely

**Example Value Objects**:
- **Address**: street, city, state, postal_code, country
- **Money**: amount, currency
- **DateRange**: start_date, end_date
- **EmailAddress**: local_part, domain
- **PhoneNumber**: country_code, area_code, number
- **Coordinates**: latitude, longitude

---

### Attribute

**Definition**: A named property of an entity or value object.

**Purpose**: Defines the data fields and their characteristics within domain objects.

**Key Attributes**:
- Inherits from `NamedEntity`
- **category**: REQUIRED, OPTIONAL, COMPUTED, DERIVED, TRANSIENT
- **data_type**: Data type (string, integer, boolean, date, etc.)
- **is_identifier**: Whether this is an identifier attribute
- **is_indexed**: Whether this attribute should be indexed
- **default_value**: Default value if not specified
- **classification**: Data classification (PUBLIC, INTERNAL, CONFIDENTIAL, PII, etc.)

**Relationships**:
- **validated_by_rules**: `Rule` entities that validate this attribute

**Attribute Categories**:
- **REQUIRED**: Must have a value
- **OPTIONAL**: May be null
- **COMPUTED**: Calculated from other attributes
- **DERIVED**: Derived from other entities or data
- **TRANSIENT**: Not persisted in storage

**Data Classifications**:
- **PUBLIC**: Publicly accessible
- **INTERNAL**: Internal use only
- **CONFIDENTIAL**: Sensitive information
- **RESTRICTED**: Highly restricted
- **PII**: Personally Identifiable Information
- **PHI**: Protected Health Information
- **PCI**: Payment Card Industry data

**Example Attributes**:
```
Entity: Customer
Attributes:
  - id (REQUIRED, string, is_identifier=true)
  - email (REQUIRED, string, classification=PII)
  - name (REQUIRED, string, classification=PII)
  - phone (OPTIONAL, string, classification=PII)
  - loyalty_points (COMPUTED, integer)
  - created_at (REQUIRED, timestamp)
```

---

### Resource

**Definition**: A domain entity or value object exposed for external interaction.

**Purpose**: Represents the external API representation of domain objects.

**Relationships**:
- **represents_entity**: The `DomainEntity` this resource represents
- **classified_as_type**: `ResourceType` classification
- **targeted_by_actions**: `Action` entities that can target this resource

**Resource Design**:
- DTOs (Data Transfer Objects) for external representation
- May hide sensitive attributes
- May aggregate multiple entities
- May include computed fields for convenience

**Example Resources**:
- API representation of Customer entity
- GraphQL type for Product
- REST resource for Order
- Message payload for OrderCreated event

---

### ResourceType

**Definition**: A classification of resources sharing common structure and behavior.

**Purpose**: Groups similar resources and defines their schema.

**Relationships**:
- **structured_by_schema**: `Schema` defining the structure
- **governed_by_permissions**: `Permission` entities that apply
- **classifies_resources**: `Resource` instances of this type

**Example Resource Types**:
- CustomerResource
- OrderResource
- ProductResource
- InvoiceResource

---

### State

**Definition**: A discrete condition in an entity's lifecycle.

**Purpose**: Represents a specific stage in an entity's lifecycle with allowed actions.

**Key Attributes**:
- Inherits from `NamedEntity`
- **is_initial**: Whether this is the initial state
- **is_terminal**: Whether this is a final/terminal state

**Relationships**:
- **allows_actions_in_state**: `Action` entities allowed in this state
- **current_for_entities**: `DomainEntity` instances currently in this state
- **source_of_transitions**: `Transition` entities starting from this state
- **target_of_transitions**: `Transition` entities ending in this state

**Example States**:
- **Order States**: Draft, Submitted, Confirmed, Shipped, Delivered, Cancelled
- **User Account States**: Pending, Active, Suspended, Deactivated
- **Payment States**: Pending, Authorized, Captured, Refunded, Failed
- **Document States**: Draft, Review, Approved, Published, Archived

---

### Transition

**Definition**: A valid movement between states.

**Purpose**: Defines allowed state changes and their conditions.

**Relationships**:
- **transitions_from_state**: Source `State` (required)
- **transitions_to_state**: Target `State` (required)
- **triggered_by_events**: `Event` entities that trigger this transition
- **guarded_by_rules**: `Rule` entities that must be satisfied
- **executes_actions_on_transition**: `Action` entities executed during transition

**Transition Guards**:
Rules that must evaluate to true for the transition to be allowed.

**Transition Actions**:
Side effects that occur during the transition (e.g., send email, update inventory).

**Example Transitions**:
```
Order State Machine:
  Draft -> Submitted (event: SubmitOrder, guard: HasItems, action: NotifyWarehouse)
  Submitted -> Confirmed (event: ConfirmOrder, guard: PaymentAuthorized)
  Confirmed -> Shipped (event: ShipOrder, action: CreateShipment)
  Shipped -> Delivered (event: DeliverOrder, action: NotifyCustomer)
  Any -> Cancelled (event: CancelOrder, action: RefundPayment)
```

---

### Lifecycle

**Definition**: The complete set of states and transitions for an entity type.

**Purpose**: Defines the full state machine governing entity lifecycle.

**Key Attributes**:
- Inherits from `NamedEntity`
- **states**: List of all `State` entities in the lifecycle
- **transitions**: List of all `Transition` entities

**Relationships**:
- **starts_with_state**: Initial `State`
- **governs_entities**: `DomainEntity` instances following this lifecycle

**Lifecycle Patterns**:
- **Linear**: States progress in a single direction (e.g., onboarding flow)
- **Cyclic**: States can return to previous states (e.g., draft -> review -> draft)
- **Branching**: Multiple paths depending on conditions (e.g., approved/rejected)
- **Parallel**: Multiple independent state dimensions

**Example Lifecycles**:
- Order fulfillment lifecycle
- User registration lifecycle
- Content approval lifecycle
- Subscription lifecycle

---

## Domain-Driven Design Patterns

### Aggregates
- **Purpose**: Enforce consistency boundaries
- **Pattern**: Small aggregates with clear root entity
- **Communication**: Aggregates communicate via domain events

### Entities vs Value Objects
- **Entity**: Identified by ID, mutable, has lifecycle
- **Value Object**: Identified by attributes, immutable, replaceable

### Domain Events
- **Purpose**: Communicate changes between aggregates
- **Pattern**: Past-tense naming (OrderPlaced, PaymentProcessed)
- **Content**: Minimal data needed for consumers

### Repositories
- **Purpose**: Persist and retrieve aggregates
- **Pattern**: One repository per aggregate root
- **Interface**: Collection-like interface (add, remove, find)

### Domain Services
- **Purpose**: Operations that don't belong to a single entity
- **Pattern**: Stateless services operating on domain objects
- **Examples**: PricingService, InventoryService

---

## Best Practices

### Aggregate Design
1. **Small Aggregates**: Limit to what must be consistent
2. **Reference by ID**: Don't embed other aggregates
3. **Eventual Consistency**: Accept eventual consistency between aggregates
4. **Transactional Boundary**: One aggregate per transaction

### Entity Design
1. **Rich Domain Model**: Put behavior in entities, not services
2. **Encapsulation**: Protect invariants through methods
3. **Identity**: Use globally unique identifiers
4. **Lifecycle Management**: Define clear state machines

### Value Object Design
1. **Immutability**: Make value objects immutable
2. **Validation**: Validate in constructor
3. **Semantics**: Use value objects for domain concepts (Money, not decimal)
4. **Reuse**: Share value objects across entities

### State Machine Design
1. **Explicit States**: Make all states explicit
2. **Valid Transitions**: Define only valid transitions
3. **Guards**: Use guards for conditional transitions
4. **Actions**: Execute side effects in transition actions
5. **Testing**: Test all state transitions

---

## Relationships with Other Sections

- **Section 1 (Structural Foundation)**: Aggregates contained in bounded contexts
- **Section 3 (Authorization)**: Resources are subject to permissions
- **Section 5 (Behavior)**: Actions operate on entities and trigger transitions
- **Section 6 (Data Management)**: Aggregates persisted in data stores
- **Section 9 (Observability)**: Entities tracked for changes in audit logs

---

## Example: E-Commerce Order Aggregate

```
Aggregate: Order
  Root Entity: Order
    Attributes:
      - order_id (REQUIRED, UUID, identifier)
      - customer_id (REQUIRED, UUID)
      - order_date (REQUIRED, timestamp)
      - status (REQUIRED, string)
      - total_amount (COMPUTED, Money)

  Entities:
    - OrderLineItem
      Attributes:
        - line_item_id (REQUIRED, UUID, identifier)
        - product_id (REQUIRED, UUID)
        - quantity (REQUIRED, integer)
        - unit_price (REQUIRED, Money)
        - subtotal (COMPUTED, Money)

  Value Objects:
    - Money (amount, currency)
    - Address (street, city, state, postal_code)

  Lifecycle:
    States: Draft -> Submitted -> Confirmed -> Shipped -> Delivered
    Transitions:
      Draft -> Submitted: SubmitOrder event, HasItems guard
      Submitted -> Confirmed: ConfirmOrder event, PaymentAuthorized guard
      Confirmed -> Shipped: ShipOrder event
      Shipped -> Delivered: DeliverOrder event
      Any -> Cancelled: CancelOrder event

  Invariants:
    - Order must have at least one line item
    - Total must equal sum of line item subtotals
    - Cannot modify order after confirmation

  Domain Events:
    - OrderPlaced
    - OrderConfirmed
    - OrderShipped
    - OrderDelivered
    - OrderCancelled
```
