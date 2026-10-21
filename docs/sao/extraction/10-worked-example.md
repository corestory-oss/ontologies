# Worked Example: Order Service

This document walks a small Python/Flask order service through all eight extraction phases, showing the SAO YAML output growing at each step. The goal is to demonstrate the end-to-end process on a concrete codebase small enough to fit in a single document.

---

## 1. The Example Codebase

The example is a minimal order management microservice with five files.

### `app.py` -- Flask application entry point

```python
from flask import Flask, request, jsonify
from models import db, Order, OrderItem
from services import OrderService

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
db.init_app(app)

order_service = OrderService()

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    order = order_service.create_order(data)
    return jsonify(order.to_dict()), 201

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = order_service.get_order(order_id)
    return jsonify(order.to_dict()), 200

@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    order = order_service.cancel_order(order_id)
    return jsonify(order.to_dict()), 200

if __name__ == "__main__":
    app.run(debug=True)
```

### `models.py` -- SQLAlchemy models

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", cascade="all,delete-orphan")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
```

### `services.py` -- Business logic

```python
from models import db, Order, OrderItem

class OrderService:
    def create_order(self, data):
        order = Order(customer_id=data["customer_id"])
        for item_data in data["items"]:
            order.items.append(OrderItem(**item_data))
        order.total_amount = sum(i.quantity * i.unit_price for i in order.items)
        db.session.add(order)
        db.session.commit()
        return order

    def get_order(self, order_id):
        return Order.query.get_or_404(order_id)

    def cancel_order(self, order_id):
        order = self.get_order(order_id)
        if order.status != "pending":
            raise ValueError("Only pending orders can be cancelled")
        order.status = "cancelled"
        db.session.commit()
        self._emit_event("OrderCancelled", {"order_id": order.id})
        return order

    def _emit_event(self, event_type, payload):
        pass  # placeholder
```

### `requirements.txt` and `Dockerfile`

`requirements.txt` declares two direct dependencies: `Flask==3.0.0` and `Flask-SQLAlchemy==3.1.1`. The `Dockerfile` builds a `python:3.12-slim` image, installs dependencies, copies source, exposes port 5000, and runs `app.py`.

---

## 2. Phase 1: Inventory

Phase 1 walks the file tree and produces the physical inventory.

```yaml
# Phase 1 output

storage_locations:
  - name: order-service-root
    location_path: "."
    location_type: directory
    contains_containers:
      - app-py
      - models-py
      - services-py
      - requirements-txt
      - dockerfile

code_containers:
  - id: app-py
    name: app.py
    container_path: app.py
    container_type: source_file
    line_count: 27
    contained_in_storage_location: order-service-root
    written_in_language: python-lang

  - id: models-py
    name: models.py
    container_path: models.py
    container_type: source_file
    line_count: 20
    contained_in_storage_location: order-service-root
    written_in_language: python-lang

  - id: services-py
    name: services.py
    container_path: services.py
    container_type: source_file
    line_count: 27
    contained_in_storage_location: order-service-root
    written_in_language: python-lang

  - id: requirements-txt
    name: requirements.txt
    container_path: requirements.txt
    container_type: configuration
    line_count: 2
    contained_in_storage_location: order-service-root

  - id: dockerfile
    name: Dockerfile
    container_path: Dockerfile
    container_type: configuration
    line_count: 7
    contained_in_storage_location: order-service-root

programming_languages:
  - id: python-lang
    name: Python
    paradigms:
      - object_oriented
      - procedural
      - functional
      - multi_paradigm
    type_discipline: dynamic_strong
    has_gc: true
    has_preprocessor: false
    language_used_by_containers:
      - app-py
      - models-py
      - services-py

package_managers:
  - name: pip
    manager_type: pip
    manifest_file: requirements.txt

package_dependencies:
  - name: flask-dep
    package_name: Flask
    version_constraint: "==3.0.0"
    scope: production
    is_direct: true
    license: BSD-3-Clause

  - name: flask-sqlalchemy-dep
    package_name: Flask-SQLAlchemy
    version_constraint: "==3.1.1"
    scope: production
    is_direct: true
    license: BSD-3-Clause
```

---

## 3. Phase 2: Code Structure

Phase 2 parses each source file and populates the structural layer.

Three **EncapsulationUnit** instances (one per class), seven **CallableUnit** instances (three route handlers + four service methods), two **DataStructure** instances (one per model), and ten **DataElement** instances (one per column).

```yaml
# Phase 2 output (adds to Phase 1)

encapsulation_units:
  - id: order-class
    name: Order
    encapsulation_type: class
    qualified_name: models.Order
    stereotype: Model
    line_start: 6
    line_end: 14
    defined_in_container: models-py

  - id: order-item-class
    name: OrderItem
    encapsulation_type: class
    qualified_name: models.OrderItem
    stereotype: Model
    line_start: 16
    line_end: 21
    defined_in_container: models-py

  - id: order-service-class
    name: OrderService
    encapsulation_type: class
    qualified_name: services.OrderService
    stereotype: Service
    line_start: 3
    line_end: 27
    defined_in_container: services-py

callable_units:
  # Flask route handlers (module-level functions in app.py)
  - id: create-order-route
    name: create_order
    callable_type: function
    defined_in_container: app-py
    line_start: 12
    line_end: 15

  - id: get-order-route
    name: get_order
    callable_type: function
    defined_in_container: app-py
    line_start: 17
    line_end: 19

  - id: cancel-order-route
    name: cancel_order
    callable_type: function
    defined_in_container: app-py
    line_start: 21
    line_end: 24

  # OrderService methods
  - id: create-order-method
    name: create_order
    callable_type: method
    return_type: Order
    contained_in_unit: order-service-class
    line_start: 4
    line_end: 13

  - id: get-order-method
    name: get_order
    callable_type: method
    return_type: Order
    contained_in_unit: order-service-class
    line_start: 15
    line_end: 16

  - id: cancel-order-method
    name: cancel_order
    callable_type: method
    return_type: Order
    contained_in_unit: order-service-class
    line_start: 18
    line_end: 25

  - id: emit-event-method
    name: _emit_event
    callable_type: method
    visibility: private
    contained_in_unit: order-service-class

data_structures:
  - id: order-structure
    name: Order
    structure_type: class_data
    structure_category: composite
    persistence_type: database_table
    line_start: 6
    line_end: 14
    defined_in_container: models-py
    contained_in_unit: order-class
    structure_contains_elements:
      - order-id-elem
      - order-customer-id-elem
      - order-status-elem
      - order-total-amount-elem
      - order-created-at-elem

  - id: order-item-structure
    name: OrderItem
    structure_type: class_data
    structure_category: composite
    persistence_type: database_table
    line_start: 16
    line_end: 21
    defined_in_container: models-py
    contained_in_unit: order-item-class
    structure_contains_elements:
      - item-id-elem
      - item-order-id-elem
      - item-product-name-elem
      - item-quantity-elem
      - item-unit-price-elem

data_elements:
  # Order fields (5 elements, showing first two; remainder follow same pattern)
  - id: order-id-elem
    name: id
    data_type: integer
    element_category: field
    contained_in_structure: order-structure

  - id: order-customer-id-elem
    name: customer_id
    data_type: string
    element_category: field
    contained_in_structure: order-structure

  # ... order-status-elem (string), order-total-amount-elem (float),
  #     order-created-at-elem (datetime) -- same pattern

  # OrderItem fields (5 elements, showing first two)
  - id: item-id-elem
    name: id
    data_type: integer
    element_category: field
    contained_in_structure: order-item-structure

  - id: item-order-id-elem
    name: order_id
    data_type: integer
    element_category: field
    contained_in_structure: order-item-structure

  # ... item-product-name-elem (string), item-quantity-elem (integer),
  #     item-unit-price-elem (float) -- same pattern

definition_references:
  - id: app-imports-models
    name: app-imports-models
    reference_type: import_symbol
    reference_path: models
    referencing_container: app-py
    referenced_container: models-py

  - id: app-imports-services
    name: app-imports-services
    reference_type: import_symbol
    reference_path: services
    referencing_container: app-py
    referenced_container: services-py

  - id: services-imports-models
    name: services-imports-models
    reference_type: import_symbol
    reference_path: models
    referencing_container: services-py
    referenced_container: models-py

control_flows:
  - id: route-calls-create
    name: create_order_route_calls_service
    flow_type: call
    source_callable: create-order-route
    target_callable: create-order-method

  - id: route-calls-get
    name: get_order_route_calls_service
    flow_type: call
    source_callable: get-order-route
    target_callable: get-order-method

  - id: route-calls-cancel
    name: cancel_order_route_calls_service
    flow_type: call
    source_callable: cancel-order-route
    target_callable: cancel-order-method

  - id: cancel-calls-get
    name: cancel_order_calls_get_order
    flow_type: call
    source_callable: cancel-order-method
    target_callable: get-order-method

  - id: cancel-calls-emit
    name: cancel_order_calls_emit_event
    flow_type: call
    source_callable: cancel-order-method
    target_callable: emit-event-method
```

---

## 4. Phase 3: Architecture

Phase 3 establishes the logical architecture: a single **System**, one **Module**, one **BoundedContext**, three **Components**, one **Service**, and the REST API.

```yaml
# Phase 3 output (adds to Phases 1-2)

systems:
  - id: order-service-system
    name: Order Service
    description: >-
      Microservice for creating, retrieving, and cancelling customer orders.
    version: 1.0.0
    contains_bounded_contexts:
      - order-mgmt-context
    exposes_interfaces:
      - order-rest-api
    has_integrations:
      - order-db-integration

bounded_contexts:
  - id: order-mgmt-context
    name: Order Management
    contained_in_system: order-service-system
    contains_modules:
      - order-module
    ubiquitous_language:
      - order
      - order item
      - cancellation

modules:
  - id: order-module
    name: order-service
    mapped_from_directory: order-service-root
    contained_in_context: order-mgmt-context
    contains_components:
      - order-api-component
      - order-service-component
      - order-repository-component
    runs_as_services:
      - order-api-service

components:
  - id: order-api-component
    name: Order API Controller
    component_type: controller
    contained_in_module: order-module
    implemented_by_code: [app-py]

  - id: order-service-component
    name: Order Service
    component_type: service
    contained_in_module: order-module
    implemented_by_code: [order-service-class]

  - id: order-repository-component
    name: Order Repository
    component_type: repository
    contained_in_module: order-module
    implemented_by_code: [order-class, order-item-class]

services:
  - id: order-api-service
    name: order-api
    service_type: microservice
    runs_module: order-module
    exposes_endpoints:
      [create-order-endpoint, get-order-endpoint, cancel-order-endpoint]

programmatic_interfaces:
  - id: order-rest-api
    name: Order REST API
    category: programmatic_interface
    api_type: rest_api
    exposed_by_system: order-service-system
    has_endpoints:
      - { id: create-order-endpoint, path: /orders, method: POST, protocol: http }
      - { id: get-order-endpoint, path: /orders/{id}, method: GET, protocol: http }
      - { id: cancel-order-endpoint, path: /orders/{id}/cancel, method: PUT, protocol: http }

external_systems:
  - id: order-database-ext
    name: SQLite Database
    system_type: third_party_service

integrations:
  - id: order-db-integration
    name: Order Database Integration
    integration_type: bidirectional
    protocol: tcp
    integrates_with_system: order-database-ext
    belongs_to_system: order-service-system
```

---

## 5. Phase 4: Domain Model

Phase 4 maps the **DataStructure** instances from Phase 2 to domain concepts.

```yaml
# Phase 4 output (adds to Phases 1-3)

domain_entities:
  - id: order-entity
    name: Order
    mapped_from_structure: order-structure
    governed_by_lifecycle: order-lifecycle
    attributes:
      - name: id
        data_type: integer
        category: required
        is_identifier: true
        mapped_from_element: order-id-elem
      - name: customer_id
        data_type: string
        category: required
        mapped_from_element: order-customer-id-elem
      - name: status
        data_type: string
        category: required
        mapped_from_element: order-status-elem
      - name: total_amount
        data_type: decimal
        category: derived        # computed from line items
        mapped_from_element: order-total-amount-elem
      - name: created_at
        data_type: timestamp
        category: required
        mapped_from_element: order-created-at-elem

  - id: order-item-entity
    name: OrderItem
    mapped_from_structure: order-item-structure
    attributes:
      - { name: id, data_type: integer, category: required,
          is_identifier: true, mapped_from_element: item-id-elem }
      - { name: order_id, data_type: integer, category: required,
          mapped_from_element: item-order-id-elem }
      - { name: product_name, data_type: string, category: required,
          mapped_from_element: item-product-name-elem }
      - { name: quantity, data_type: integer, category: required,
          mapped_from_element: item-quantity-elem }
      - { name: unit_price, data_type: decimal, category: required,
          mapped_from_element: item-unit-price-elem }

# Backlinks on DataStructures
# order-structure.maps_to_domain_entity: order-entity
# order-item-structure.maps_to_domain_entity: order-item-entity

aggregates:
  - id: order-aggregate
    name: Order
    has_root_entity: order-entity
    aggregates_entities:
      - order-item-entity
    enforced_by_invariant_rules:
      - pending-cancel-rule
    persisted_in_stores:
      - order-datastore
    contained_in_bounded_context: order-mgmt-context

# Backlink on BoundedContext
# order-mgmt-context.contains_aggregates: [order-aggregate]

domain_relationships:
  - id: order-has-items
    name: OrderHasItems
    source_entity: order-entity
    target_entity: order-item-entity
    cardinality: one_to_many
    is_composition: true
    is_navigable: true
    is_bidirectional: true
    foreign_key_field: order_id

lifecycles:
  - id: order-lifecycle
    name: OrderLifecycle
    governs_entities:
      - order-entity
    starts_with_state: pending-state
    states:
      - id: pending-state
        name: pending
        is_initial: true
        is_terminal: false
      - id: confirmed-state
        name: confirmed
        is_initial: false
        is_terminal: false
      - id: cancelled-state
        name: cancelled
        is_initial: false
        is_terminal: true
    transitions:
      - name: ConfirmOrder
        transitions_from_state: pending-state
        transitions_to_state: confirmed-state
      - name: CancelOrder
        transitions_from_state: pending-state
        transitions_to_state: cancelled-state
        guarded_by_rules:
          - pending-cancel-rule

data_stores:
  - id: order-datastore
    name: OrderDatabase
    store_type: relational_db
    persists_aggregates: [order-aggregate]
    collections:
      - name: orders
        persists_structures: [order-structure]
        has_constraints:
          - { name: pk_orders, constraint_type: primary_key, columns: [id] }
        has_indexes:
          - { name: idx_orders_customer_id, index_type: btree, columns: [customer_id] }
      - name: order_items
        persists_structures: [order-item-structure]
        has_constraints:
          - { name: pk_order_items, constraint_type: primary_key, columns: [id] }
          - { name: fk_order_items_order, constraint_type: foreign_key,
              columns: [order_id], reference_table: orders, reference_columns: [id] }
```

---

## 6. Phase 5: Business Intent

Phase 5 captures actors, operations, commands, queries, rules, and events.

```yaml
# Phase 5 output (adds to Phases 1-4)

human_actors:
  - id: customer-actor
    name: Customer
    description: End user who creates and manages orders
    category: human
    actor_type: end_user

operations:
  - id: create-order-op
    name: CreateOrder
    description: Creates a new order with line items
    exposed_by_component: order-api-component
    implemented_by_callables:
      - create-order-route
      - create-order-method

  - id: get-order-op
    name: GetOrder
    description: Retrieves an order by its identifier
    exposed_by_component: order-api-component
    implemented_by_callables:
      - get-order-route
      - get-order-method

  - id: cancel-order-op
    name: CancelOrder
    description: Cancels a pending order
    exposed_by_component: order-api-component
    implemented_by_callables:
      - cancel-order-route
      - cancel-order-method

commands:
  - id: create-order-cmd
    name: CreateOrder
    category: command
    command_type: create
    performed_by_actor: customer-actor
    targets_resources:
      - order-aggregate
    emits_events_from_action: []

  - id: cancel-order-cmd
    name: CancelOrder
    category: command
    command_type: execute
    performed_by_actor: customer-actor
    targets_resources:
      - order-aggregate
    validated_by_action_rules:
      - pending-cancel-rule
    emits_events_from_action:
      - order-cancelled-event

queries:
  - id: get-order-query
    name: GetOrder
    category: query
    performed_by_actor: customer-actor
    targets_resources:
      - order-aggregate

rules:
  - id: pending-cancel-rule
    name: OnlyPendingOrdersCancellable
    category: business
    condition: "order.status == 'pending'"
    action: "Allow cancellation to proceed"
    priority: 1
    is_active: true
    validates_actions:
      - cancel-order-cmd
    governs_domain_entities:
      - order-entity
    guards_transitions:
      - CancelOrder  # transition name from Phase 4

domain_events:
  - id: order-cancelled-event
    name: OrderCancelled
    description: Emitted when a pending order is successfully cancelled
    category: domain_event
    produced_by_aggregate: order-aggregate
    emitted_by_component: order-service-component
```

---

## 7. Phase 6: Cross-Cutting Concerns (Brief)

Phase 6 covers deployment, environments, and testing. This small codebase has minimal cross-cutting infrastructure, but the Dockerfile provides deployment information.

```yaml
# Phase 6 output (adds to Phases 1-5)

environments:
  - id: dev-env
    name: development
    environment_type: development
    hosts_deployments:
      - order-dev-deployment

deployment_units:
  - id: order-container-unit
    name: order-service-container
    unit_type: container
    artifact_uri: "order-service:latest"

deployments:
  - id: order-dev-deployment
    name: order-service-dev
    replicas: 1
    deploys_service: order-api-service
    deployed_in_environment: dev-env
    deploys_unit: order-container-unit

test_suites:
  - id: order-unit-tests
    name: Order Service Unit Tests
    suite_type: unit
    framework: pytest
    source_location: tests/
    tests_component: order-service-component
    tests_module: order-module
```

---

## 8. Phase 7: Bridge Stitching

Phase 7 verifies all eight cross-layer bridges. No new entities are created; only missing links are filled.

| # | Bridge | Forward | Inverse | Status |
|---|---|---|---|---|
| 1 | Module to StorageLocation | `order-module.mapped_from_directory` = `order-service-root` | `order-service-root.maps_to_module` = `order-module` | Pass |
| 2 | Component to EncapsulationUnit | All 3 components have `implemented_by_code` set | Inverse `implements_component` set on each EncapsulationUnit | Pass |
| 3 | DomainEntity to DataStructure | `order-entity` -> `order-structure`; `order-item-entity` -> `order-item-structure` | `maps_to_domain_entity` set on both structures | Pass |
| 4 | Attribute to DataElement | All 10 Attributes have `mapped_from_element` | `maps_to_attribute` set on all 10 DataElements | Pass |
| 5 | Operation to CallableUnit | Each Operation links to its route handler + service method | `implements_operation` set on each CallableUnit | Pass |
| 6 | Aggregate to BoundedContext | `order-aggregate.contained_in_bounded_context` = `order-mgmt-context` | `order-mgmt-context.contains_aggregates` = `[order-aggregate]` | Pass |
| 7 | Service to Module | `order-api-service.runs_module` = `order-module` | `order-module.runs_as_services` = `[order-api-service]` | Pass |
| 8 | Deployment to Service | `order-dev-deployment.deploys_service` = `order-api-service` | `order-api-service.deployed_as` = `order-dev-deployment` | Pass |

All eight bridges verified. The graph is fully connected from **Environment** down through **Deployment**, **Service**, **Module**, **Component**, **EncapsulationUnit**, **DataStructure**, **DomainEntity**, and up through **Aggregate**, **BoundedContext**, to **System**.

---

## 9. Phase 8: System Context

Phase 8 finalizes the **System** instance with all top-level relationships populated.

```yaml
# Phase 8 -- finalized System

systems:
  - id: order-service-system
    name: Order Service
    description: >-
      Microservice for creating, retrieving, and cancelling customer orders.
    version: 1.0.0
    contains_bounded_contexts:
      - order-mgmt-context
    exposes_interfaces:
      - order-rest-api
    has_integrations:
      - order-db-integration
```

All top-level attributes verified:

- `contains_bounded_contexts` -- one context: **Order Management**
- `exposes_interfaces` -- one interface: **Order REST API** with three endpoints
- `has_integrations` -- one integration: **Order Database Integration**
- `enforces_policies` -- none (no auth policies extracted)
- `must_comply_with` -- none (no compliance requirements in scope)

The **System** is the single root from which the entire graph is reachable.

---

## 10. Complete Extraction Summary

The full extraction is the union of all YAML blocks shown in Phases 1-8 above. The following table summarizes the instance counts.

| Phase | SAO Classes produced | Count |
|---|---|---|
| 1 -- Inventory | **StorageLocation**, **CodeContainer**, **ProgrammingLanguage**, **PackageManager**, **PackageDependency** | 10 |
| 2 -- Code Structure | **EncapsulationUnit**, **CallableUnit**, **DataStructure**, **DataElement**, **DefinitionReference**, **ControlFlow** | 30 |
| 3 -- Architecture | **System**, **BoundedContext**, **Module**, **Component**, **Service**, **ProgrammaticInterface**, **Endpoint**, **ExternalSystem**, **Integration** | 13 |
| 4 -- Domain Model | **DomainEntity**, **Aggregate**, **DomainRelationship**, **Lifecycle**, **State**, **DataStore**, **Collection** | 11 |
| 5 -- Business Intent | **HumanActor**, **Operation**, **Command**, **Query**, **Rule**, **DomainEvent** | 9 |
| 6 -- Cross-Cutting | **Environment**, **Deployment**, **DeploymentUnit**, **TestSuite** | 4 |
| **Total** | **37 distinct classes** | **77** |

### Key observations

1. Even a five-file codebase produces 77 SAO instances across 37 distinct classes. Real applications will produce thousands.
2. The bridges are what make the extraction valuable. Without them, the 77 instances would be seven isolated clusters. With them, every instance is reachable from the **System** root.
3. The YAML is additive: each phase appends new instance blocks and backlinks without modifying earlier outputs. This makes incremental extraction and review practical.
4. Phase 2 (Code Structure) produces the most instances by count, but Phase 4 (Domain Model) and Phase 5 (Business Intent) add the most semantic value.
