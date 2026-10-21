# Section 4: Domain Modeling

This section defines domain-driven design concepts including aggregates, entities, value objects, attributes, resources, states, and lifecycles.

> **v2.0 Note — Inlining Change**: In SAO v2.0, many previously string-based cross-references have been replaced with direct object references (inlined relationships). Classes in this section now carry explicit back-reference attributes that make the bidirectional links between ontology concepts navigable from either side.

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
- **produces_domain_events**: `DomainEvent` entities produced
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
- **outgoing_relationships** *(v2.0)*: `DomainRelationship` entities where this entity is the source
- **incoming_relationships** *(v2.0)*: `DomainRelationship` entities where this entity is the target

**Entity vs Value Object**:
- **Entity**: Has identity, mutable, compared by ID
- **Value Object**: No identity, immutable, compared by attributes

**Example Entities**:
- Customer (ID, name, email, created_at)
- Order (ID, order_number, customer_id, status)
- Product (ID, SKU, name, price)
- Invoice (ID, invoice_number, amount, due_date)

---

### DomainRelationship *(v2.0)*

**Definition**: A named, typed relationship between two domain entities (e.g., "Order has many OrderLines", "User belongs to Organization"). Wires the previously orphaned `Cardinality` enum into the domain model.

**Purpose**: Explicitly captures how domain entities relate to each other, including cardinality, navigability, and composition semantics. This is a major addition in SAO v2.0 (Section 26).

**Key Attributes**:
- Inherits from `NamedEntity`
- **cardinality** (range: `Cardinality`, required): The multiplicity of the relationship (e.g., `one_to_one`, `one_to_many`, `many_to_many`) — wires the previously orphaned `Cardinality` enum
- **is_navigable** (boolean): Whether the relationship is traversable from source to target
- **is_bidirectional** (boolean): Whether the relationship can be navigated in both directions
- **is_composition** (boolean): Whether this represents UML composition (strong ownership) vs aggregation (weak ownership)
- **foreign_key_field** (string): The implementing field in the data layer
- **join_entity** (string): For many-to-many relationships, the join table or entity

**Relationships**:
- **source_entity**: The `DomainEntity` that owns or originates the relationship (inverse: `has_outgoing_relationships` on DomainEntity)
- **target_entity**: The `DomainEntity` that is referenced by the relationship (inverse: `has_incoming_relationships` on DomainEntity)

**Example Domain Relationships**:
```
DomainRelationship: OrderHasLineItems
  source_entity: Order
  target_entity: OrderLineItem
  cardinality: one_to_many
  is_composition: true
  is_navigable: true
  is_bidirectional: true
  foreign_key_field: order_id

DomainRelationship: UserBelongsToOrganization
  source_entity: User
  target_entity: Organization
  cardinality: many_to_one
  is_composition: false
  is_navigable: true
  is_bidirectional: true
  foreign_key_field: organization_id

DomainRelationship: StudentEnrolledInCourses
  source_entity: Student
  target_entity: Course
  cardinality: many_to_many
  is_composition: false
  is_navigable: true
  is_bidirectional: true
  join_entity: Enrollment
```

---

### ValueObject

**Definition**: An immutable domain object defined by its attributes.

**Purpose**: Represents descriptive aspects of the domain with no conceptual identity.

**Key Attributes**:
- Inherits from `NamedEntity`
- **attributes**: List of `Attribute` entities defining the value object
- **mapped_from_structure_vo** *(v2.0)*: Back-reference to the `DataStructure` that maps to this value object

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
- **category**: `required`, `optional`, `computed`, `derived`, `transient`
- **data_type**: Data type (string, integer, boolean, date, etc.)
- **is_identifier**: Whether this is an identifier attribute
- **is_indexed**: Whether this attribute should be indexed
- **default_value**: Default value if not specified
- **classification**: Data classification (`public`, `internal`, `confidential`, `pii`, etc.)

**Relationships**:
- **validated_by_rules**: `Rule` entities that validate this attribute
- **mapped_from_element** *(v2.0)*: Back-reference to the `DataElement` that maps to this attribute

**Attribute Categories**:
- `required`: Must have a value
- `optional`: May be null
- `computed`: Calculated from other attributes
- `derived`: Derived from other entities or data
- `transient`: Not persisted in storage

**Data Classifications**:
- `public`: Publicly accessible
- `internal`: Internal use only
- `confidential`: Sensitive information
- `restricted`: Highly restricted
- `pii`: Personally Identifiable Information
- `phi`: Protected Health Information
- `pci`: Payment Card Industry data

**Example Attributes**:
```
Entity: Customer
Attributes:
  - id (required, string, is_identifier=true)
  - email (required, string, classification=pii)
  - name (required, string, classification=pii)
  - phone (optional, string, classification=pii)
  - loyalty_points (computed, integer)
  - created_at (required, timestamp)
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
- **initial_for_lifecycle** *(v2.0)*: Back-reference to the `Lifecycle` for which this is the initial state

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
      - order_id (required, UUID, identifier)
      - customer_id (required, UUID)
      - order_date (required, timestamp)
      - status (required, string)
      - total_amount (computed, Money)

  Entities:
    - OrderLineItem
      Attributes:
        - line_item_id (required, UUID, identifier)
        - product_id (required, UUID)
        - quantity (required, integer)
        - unit_price (required, Money)
        - subtotal (computed, Money)

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
