# Phase 4: Domain Model (Layer 5)

**Input:** Phase 2 outputs (**DataStructure**, **DataElement**) + Phase 3 outputs (**BoundedContext**, **Module**)
**Output:** **Aggregate**, **DomainEntity**, **ValueObject**, **Attribute**, **DomainRelationship**, **Lifecycle**, **State**, **Transition**, **DataStore**, **Collection**, **Schema**, **SchemaVersion**, **DataClassification**, **RetentionPolicy**, **DatabaseConstraint**, **DatabaseIndex**

---

## 1. Overview

Phase 4 is where extraction moves from deterministic parsing to inferential reasoning. Prior phases catalogued files (Phase 1), parsed code structures (Phase 2), and identified architectural boundaries (Phase 3). This phase recognizes *business meaning* in those code structures using Domain-Driven Design patterns.

The key insight: a COBOL group item named `CUST-MSTR-REC` with a primary key field and CRUD operations is not just a **DataStructure** -- it is a **Customer** domain entity. A Java class with `@Entity`, a primary key, and repository methods is an **Order** aggregate root. This phase surfaces those facts.

Automation level: 40--50%. Deterministic heuristics (presence of `@Entity`, primary key fields, ORM annotations) handle part of the classification, but an LLM or human analyst MUST confirm business names, aggregate boundaries, and lifecycle semantics.

### Critical bridge

Phase 4 establishes the central bridge between code and domain:

- `DomainEntity.mapped_from_structure` links to the **DataStructure**(s) from Phase 2
- `DataStructure.maps_to_domain_entity` is the inverse
- `Attribute.mapped_from_element` links to the **DataElement**(s) from Phase 2
- `DataElement.maps_to_attribute` is the inverse

These bidirectional links MUST be established for every **DomainEntity** and **Attribute** created in this phase.

---

## 2. Step 1: Classify DataStructures

Iterate over every **DataStructure** produced in Phase 2 and apply the following decision tree.

### Decision tree

```
For each DataStructure:
│
├─ Has unique identifier + CRUD operations + persisted?
│  └─ → Create a DomainEntity
│
├─ No unique identifier + immutable + used as property of another structure?
│  └─ → Create a ValueObject
│
├─ DTO, transport object, configuration, utility type?
│  └─ → Leave as DataStructure only (no domain mapping)
│
└─ Ambiguous → Flag for human review
```

### Signals by language

| Signal | Language | Implies |
|---|---|---|
| `@Entity`, `@Table` | Java/JPA | DomainEntity |
| `@Embeddable` | Java/JPA | ValueObject |
| `class Meta: db_table` | Python/Django | DomainEntity |
| `01 ... RECORD` with PK and FD | COBOL | DomainEntity |
| `01 ... GROUP` (no PK, used inline) | COBOL | ValueObject |
| `CREATE TABLE` with `PRIMARY KEY` | SQL DDL | DomainEntity |
| `frozen<>` UDT | Cassandra CQL | ValueObject |

---

## 3. Step 2: Create DomainEntities and map Attributes

For each **DataStructure** classified as a domain entity, create a **DomainEntity** instance.

### Required attributes

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Clean business name -- e.g., "Customer", not "CUST-MSTR-REC" |
| `mapped_from_structure` | **DataStructure** (multivalued) | MUST link to the originating structure(s) |
| `attributes` | **Attribute** list (inlined) | One per meaningful field |
| `classifications` | `DataClassificationType` list | If the entity holds sensitive data |

### Creating Attributes

For each meaningful field (skip framework noise like serialization IDs), create an **Attribute**:

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Clean business name for the field |
| `category` | `AttributeCategory` | One of: `required`, `optional`, `computed`, `derived`, `transient` |
| `data_type` | string (required) | Data type: `string`, `integer`, `boolean`, `date`, `timestamp`, `decimal`, etc. |
| `is_identifier` | boolean | `true` for primary key / unique identifier fields |
| `is_indexed` | boolean | `true` if the field is indexed |
| `default_value` | string | Default value if discoverable |
| `classification` | `DataClassificationType` | One of: `public`, `internal`, `confidential`, `restricted`, `pii`, `phi`, `pci` |
| `mapped_from_element` | **DataElement** (multivalued) | MUST link to the originating element(s) |

### Establishing bridges

The extraction agent MUST set both sides of every bridge:

1. `DomainEntity.mapped_from_structure` → the **DataStructure**
2. `DataStructure.maps_to_domain_entity` → the **DomainEntity**
3. `Attribute.mapped_from_element` → the **DataElement**
4. `DataElement.maps_to_attribute` → the **Attribute**

### YAML example

```yaml
DomainEntity:
  - name: Customer
    mapped_from_structure: CUST-MSTR-REC
    classifications:
      - pii
    attributes:
      - name: customer_id
        data_type: string
        category: required
        is_identifier: true
        mapped_from_element: CUST-ID
      - name: name
        data_type: string
        category: required
        classification: pii
        mapped_from_element: CUST-NAME
      - name: email
        data_type: string
        category: required
        classification: pii
        mapped_from_element: CUST-EMAIL
      - name: loyalty_points
        data_type: integer
        category: computed
        mapped_from_element: CUST-LOYALTY-PTS
      - name: created_at
        data_type: timestamp
        category: required
        mapped_from_element: CUST-CREATE-DT
```

---

## 4. Step 3: Create ValueObjects

For each **DataStructure** classified as a value object, create a **ValueObject** instance.

### Required attributes

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Clean business name (e.g., "Money", "Address") |
| `attributes` | **Attribute** list (inlined) | Component fields |
| `mapped_from_structure_vo` | **DataStructure** (multivalued) | MUST link to the originating structure(s) |

The inverse `DataStructure.maps_to_value_object` MUST also be set.

### Common value object patterns

- **Money**: `amount` + `currency`
- **Address**: `street`, `city`, `state`, `postal_code`, `country`
- **DateRange**: `start_date`, `end_date`
- **Coordinates**: `latitude`, `longitude`
- **PhoneNumber**: `country_code`, `area_code`, `number`

### YAML example

```yaml
ValueObject:
  - name: Money
    mapped_from_structure_vo: AMOUNT-FIELDS
    attributes:
      - name: amount
        data_type: decimal
        category: required
        mapped_from_element: AMT-VALUE
      - name: currency
        data_type: string
        category: required
        default_value: "USD"
        mapped_from_element: AMT-CURRENCY

  - name: Address
    mapped_from_structure_vo: CUST-ADDR-GRP
    attributes:
      - name: street
        data_type: string
        category: required
        classification: pii
        mapped_from_element: CUST-ADDR-STREET
      - name: city
        data_type: string
        category: required
        mapped_from_element: CUST-ADDR-CITY
      # ... state, postal_code, country follow the same pattern
```

---

## 5. Step 4: Group into Aggregates

Create **Aggregate** instances that define transactional consistency boundaries around related entities and value objects.

### Heuristics for identifying aggregate boundaries

The extraction agent SHOULD use the following signals:

1. **Co-loaded entities** -- entities that are always fetched and saved together (e.g., Order and OrderLineItem loaded in the same repository method)
2. **Shared transaction boundary** -- entities modified within the same `@Transactional` method, the same CICS `SYNCPOINT`, or the same database transaction
3. **Root-controls-access** -- a root entity that mediates all access to its children (e.g., `Order.addLineItem()` rather than direct `OrderLineItem` creation)
4. **Cascade delete** -- if deleting entity A always deletes entity B, they belong in the same aggregate
5. **Bounded context alignment** -- aggregates SHOULD NOT cross **BoundedContext** boundaries

### Required attributes

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Aggregate name (typically same as root entity) |
| `has_root_entity` | **DomainEntity** (required) | The root entity -- MUST be set |
| `aggregates_entities` | **DomainEntity** list | Non-root entities in the aggregate |
| `has_value_objects` | **ValueObject** list (inlined) | Value objects within the aggregate |
| `enforced_by_invariant_rules` | **Rule** list | Invariant rules (if known at this point) |
| `persisted_in_stores` | **DataStore** list | Where the aggregate is persisted |
| `contained_in_bounded_context` | **BoundedContext** | Parent bounded context from Phase 3 |

### Linking to BoundedContext

Set `Aggregate.contained_in_bounded_context` to the **BoundedContext** identified in Phase 3. The inverse `BoundedContext.contains_aggregates` MUST also be set.

### YAML example

```yaml
Aggregate:
  - name: Order
    has_root_entity: Order
    aggregates_entities:
      - OrderLineItem
    value_objects:
      - Money           # defined in Step 3
    enforced_by_invariant_rules:
      - OrderMustHaveAtLeastOneItem
      - TotalMustEqualSumOfLineItems
    persisted_in_stores:
      - OrderDatabase
    contained_in_bounded_context: OrderManagement
```

---

## 6. Step 5: Extract DomainRelationships

Create a **DomainRelationship** for each association between domain entities.

### Required attributes

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Descriptive name (e.g., "OrderHasLineItems") |
| `has_source_entity` | **DomainEntity** | The entity that owns or originates the relationship |
| `has_target_entity` | **DomainEntity** | The entity that is referenced |
| `cardinality` | `Cardinality` (required) | One of: `one_to_one`, `one_to_many`, `many_to_one`, `many_to_many` |
| `is_navigable` | boolean | Whether the relationship can be traversed source → target |
| `is_bidirectional` | boolean | Whether it can be navigated in both directions |
| `is_composition` | boolean | `true` if the target's lifecycle depends on the source |
| `foreign_key_field` | string | The field implementing this relationship in the data layer |
| `join_entity` | string | For `many_to_many`, the join table or entity name |

### Sources for discovering relationships

| Source | Language / Platform | Example |
|---|---|---|
| ORM annotations | Java (`@ManyToOne`, `@OneToMany`) | `@OneToMany(mappedBy = "order")` |
| ORM declarations | Python/Django (`ForeignKey`, `ManyToManyField`) | `ForeignKey(Customer, on_delete=CASCADE)` |
| FK constraints | SQL DDL | `FOREIGN KEY (customer_id) REFERENCES customers(id)` |
| Record references | COBOL | `CUST-ID` field in `ORDER-REC` referencing `CUST-MSTR-REC` |
| ActiveRecord | Ruby on Rails (`belongs_to`, `has_many`) | `has_many :order_line_items` |

### Composition vs. association

Set `is_composition` to `true` when:

- The child entity cannot exist without the parent (e.g., **OrderLineItem** cannot exist without **Order**)
- Cascade delete is configured (`on_delete=CASCADE`, `CascadeType.ALL`)
- The child has no independent access path (no standalone repository)

### YAML example

```yaml
DomainRelationship:
  - name: OrderHasLineItems
    source_entity: Order
    target_entity: OrderLineItem
    cardinality: one_to_many
    is_composition: true
    is_navigable: true
    is_bidirectional: true
    foreign_key_field: order_id

  - name: OrderBelongsToCustomer
    source_entity: Order
    target_entity: Customer
    cardinality: many_to_one
    is_composition: false
    is_navigable: true
    is_bidirectional: true
    foreign_key_field: customer_id

  - name: StudentEnrolledInCourses
    source_entity: Student
    target_entity: Course
    cardinality: many_to_many
    is_composition: false
    is_navigable: true
    is_bidirectional: true
    join_entity: Enrollment
```

---

## 7. Step 6: Extract Lifecycles and State Machines

Look for evidence of state management in the codebase and create lifecycle definitions.

### Signals for state machines

- Status/state fields with constrained values (enums, finite string sets)
- State transition methods (e.g., `order.submit()`, `order.cancel()`)
- Workflow definitions (state machine DSLs, workflow engines)
- Guard conditions (e.g., `if order.status == 'CONFIRMED' then allow ship`)
- COBOL paragraph names following transition patterns (e.g., `1000-PROCESS-NEW-ORDER`, `2000-CONFIRM-ORDER`)

### Creating instances

Create a **Lifecycle** with `name`, `states` (inlined **State** list), `transitions` (inlined **Transition** list), `starts_with_state` (initial **State**), and `governs_entities` (the **DomainEntity** instances that follow this lifecycle).

For each **State**, set `name`, `is_initial`, `is_terminal`, and optionally `allows_actions_in_state`.

For each **Transition**, set `name`, `transitions_from_state` (required), `transitions_to_state` (required), and optionally `triggered_by_events`, `guarded_by_rules`, and `executes_actions_on_transition`.

Link `DomainEntity.governed_by_lifecycle` → **Lifecycle** for each entity that has state behavior.

### YAML example

```yaml
Lifecycle:
  - name: OrderLifecycle
    governs_entities:
      - Order
    starts_with_state: Draft
    states:
      - name: Draft
        is_initial: true
        is_terminal: false
        allows_actions_in_state:
          - AddLineItem
          - RemoveLineItem
      - name: Submitted
        is_initial: false
        is_terminal: false
      - name: Confirmed
        is_initial: false
        is_terminal: false
      - name: Shipped
        is_initial: false
        is_terminal: false
      - name: Delivered
        is_initial: false
        is_terminal: true
      - name: Cancelled
        is_initial: false
        is_terminal: true
    transitions:
      - name: SubmitOrder
        transitions_from_state: Draft
        transitions_to_state: Submitted
        triggered_by_events:
          - OrderSubmitted
        guarded_by_rules:
          - OrderMustHaveAtLeastOneItem
      - name: ConfirmOrder
        transitions_from_state: Submitted
        transitions_to_state: Confirmed
        guarded_by_rules:
          - PaymentMustBeAuthorized
      - name: ShipOrder
        transitions_from_state: Confirmed
        transitions_to_state: Shipped
        executes_actions_on_transition:
          - CreateShipment
          - NotifyCustomer
      - name: DeliverOrder
        transitions_from_state: Shipped
        transitions_to_state: Delivered
      - name: CancelOrder
        transitions_from_state: Submitted   # also valid from Confirmed
        transitions_to_state: Cancelled
        executes_actions_on_transition:
          - RefundPayment
```

---

## 8. Step 7: Identify DataStores and Collections

Create persistence infrastructure instances that capture where aggregates are stored.

### Creating DataStore instances

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | E.g., "OrderDatabase", "CustomerVSAM" |
| `store_type` | `DataStoreType` | See permissible values below |
| `connection_string` | string | Connection URI if discoverable |
| `collections` | **Collection** list (inlined) | Tables, collections, or buckets |

#### `store_type` permissible values

`relational_db`, `document_db`, `key_value_store`, `graph_db`, `time_series_db`, `object_storage`, `search_index`, `cache`, `message_broker`, `data_lake`, `vsam`, `flat_file`, `isam`, `dead_letter_queue`

### Creating Collection instances

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Table/collection/bucket name |
| `collection_structured_by_schema` | **Schema** | Schema that defines the structure |
| `persists_structures` | **DataStructure** list | Link to Phase 2 DataStructures stored here |
| `has_constraints` | **DatabaseConstraint** list (inlined) | PK, FK, unique, check constraints |
| `has_indexes` | **DatabaseIndex** list (inlined) | Index definitions |
| `governed_by_retention_policy` | **RetentionPolicy** | Data retention rules |

### Creating Schema and SchemaVersion

If DDL files or migration scripts exist, create a **Schema** with `schema_type` (one of: `table_schema`, `document_schema`, `event_schema`, `api_schema`, `message_schema`) and `definition` (the DDL or schema content). Add **SchemaVersion** instances to `has_versions` for each migration, setting `version`, `migration_script`, and `is_backward_compatible`.

### Creating DatabaseConstraint and DatabaseIndex instances

For each **Collection**, create **DatabaseConstraint** instances with `constraint_type` (required, one of: `primary_key`, `foreign_key`, `unique`, `check`, `not_null`), `columns`, and -- for foreign keys -- `reference_table` and `reference_columns`. For `check` constraints, set `expression`.

Create **DatabaseIndex** instances with `index_type` (required, one of: `btree`, `hash`, `gin`, `fulltext`), `columns`, and optionally `is_unique`, `is_partial`, and `filter_expression`.

### DataClassification and RetentionPolicy

If data sensitivity or retention requirements are discoverable (from comments, annotations, compliance documentation):

- Create **DataClassification** with `classification_type` (one of: `public`, `internal`, `confidential`, `restricted`, `pii`, `phi`, `pci`), `handling_requirements`, and `encryption_required`.
- Create **RetentionPolicy** with `retention_days`, `archive_after_days`, and `deletion_strategy`.

### Linking aggregates to stores

Set `Aggregate.persisted_in_stores` → **DataStore** and the inverse `DataStore.persists_aggregates`.

Set `DataStore.collections` → **Collection** list (inlined).

Set `Collection.persists_structures` → **DataStructure** and the inverse `DataStructure.persisted_in_collection`.

### YAML example

```yaml
DataStore:
  - name: OrderDatabase
    store_type: relational_db
    persists_aggregates:
      - Order
    collections:
      - name: orders
        collection_structured_by_schema: OrderTableSchema
        persists_structures:
          - ORDER-REC
        has_constraints:
          - name: pk_orders
            constraint_type: primary_key
            columns: [order_id]
          - name: fk_orders_customer
            constraint_type: foreign_key
            columns: [customer_id]
            reference_table: customers
            reference_columns: [customer_id]
          - name: chk_order_total
            constraint_type: check
            expression: "total_amount >= 0"
        has_indexes:
          - name: idx_orders_customer
            index_type: btree
            columns: [customer_id]
          - name: idx_orders_status
            index_type: btree
            columns: [status]
        governed_by_retention_policy: OrderRetention

      - name: order_line_items
        persists_structures: [ORDER-LINE-REC]
        has_constraints:
          - name: pk_order_lines
            constraint_type: primary_key
            columns: [line_item_id]

Schema:
  - name: OrderTableSchema
    schema_type: table_schema
    definition: "CREATE TABLE orders (order_id UUID PRIMARY KEY, ...);"
    schema_versions:
      - name: OrderTable_v1
        version: "1.0.0"
        is_backward_compatible: true
      - name: OrderTable_v2
        version: "2.0.0"
        migration_script: "ALTER TABLE orders ADD COLUMN discount_code VARCHAR(20);"
        is_backward_compatible: true

DataClassification:
  - name: CustomerPII
    classification_type: pii
    handling_requirements: ["Must be encrypted at rest", "Access requires audit logging"]
    encryption_required: true

RetentionPolicy:
  - name: OrderRetention
    retention_days: 2555
    archive_after_days: 365
    deletion_strategy: "anonymize"
```

---

## 9. Phase 4 Checklist

Before proceeding to Phase 5, verify the following:

- [ ] Every persistent **DataStructure** from Phase 2 has been evaluated against the decision tree (Section 2)
- [ ] **DomainEntity** instances have clean business names and `mapped_from_structure` bridges
- [ ] **Attribute** instances have `mapped_from_element` bridges back to **DataElement**
- [ ] **ValueObject** instances have `mapped_from_structure_vo` bridges
- [ ] **Aggregate** instances have `has_root_entity` set (required) and are assigned to a **BoundedContext** via `contained_in_bounded_context`
- [ ] **DomainRelationship** instances capture entity associations with correct `cardinality`, `is_composition`, and `foreign_key_field`
- [ ] **Lifecycle**, **State**, and **Transition** instances are created where state patterns exist in the code
- [ ] **DataStore** and **Collection** instances identify all persistence mechanisms
- [ ] **DatabaseConstraint** and **DatabaseIndex** instances capture schema-level metadata where DDL or migrations are available
- [ ] **DataClassification** and **RetentionPolicy** instances are created where data sensitivity or retention requirements are discoverable
- [ ] All bidirectional inverse links are set on both sides of every relationship
