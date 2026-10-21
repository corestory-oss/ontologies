# Phase 3: Architecture and Integration (Layers 2 & 4)

This phase bridges the physical code structure extracted in Phases 1-2 to logical architectural concepts. It maps directories to **Modules**, groups them into **BoundedContexts**, identifies **Components** and **Services**, extracts **Interfaces** and **Endpoints**, and documents **ExternalSystem** connections.

**Automation level**: 60-70%. Module and service identification can be largely automated from build manifests and deployment configs. Bounded context identification requires judgment and is the most subjective step in the entire extraction process.

**Input**: Phase 1 outputs (**StorageLocation**, **CodeContainer**, **ProgrammingLanguage**) + Phase 2 outputs (**EncapsulationUnit**, **CallableUnit**, **DataStructure**, **DefinitionReference**) + build manifests + deployment configs + documentation

**Output**: **System**, **BoundedContext**, **Module**, **Component**, **Service**, **Interface** (and subtypes **UserInterface**, **ProgrammaticInterface**, **EventInterface**), **Endpoint**, **Screen**, **Subscription**, **ExternalSystem**, **Integration**, **Contract**, **Adapter**, **CircuitBreaker**, **Dependency**, **Capability**, **Feature**

---

## Overview

Phase 3 establishes the architectural skeleton of the application. Where Phase 2 asks "what code exists?", Phase 3 asks "how is that code organized into deployable, meaningful units?"

Two critical bridges are established in this phase:

1. **Code-to-Module bridge**: `Module.mapped_from_directory` links to a **StorageLocation**, and `StorageLocation.maps_to_module` provides the inverse. This connects the physical file tree to the logical module structure.
2. **Code-to-Component bridge**: `Component.implemented_by_code` links to **EncapsulationUnit** (or **CodeContainer**) instances, and the inverse `EncapsulationUnit.implements_component` links back. This connects individual code units to their architectural role.

These bridges are what make SAO a true cross-layer ontology rather than a collection of disconnected models.

---

## Step 1: Create the System instance

Every extraction produces exactly one **System** instance. This is the root container from which all other architectural entities are reachable.

The extraction agent MUST create the **System** before proceeding to any other step in this phase. Set the following attributes:

- `name` -- the application or product name
- `description` -- a concise summary of what the system does
- `version` -- the version being extracted (inherited from the `Versionable` mixin)

```yaml
systems:
  - name: order-platform
    description: >-
      E-commerce order management platform handling order placement,
      payment processing, and fulfillment tracking.
    version: 2.4.1
```

All subsequent entities in this phase will be linked back to this **System** instance via relationship attributes such as `contains_bounded_contexts`, `has_integrations`, and `exposes_interfaces`.

---

## Step 2: Map StorageLocations to Modules

Create one **Module** for each cohesive, deployable unit of code. The goal is to transform the flat directory tree from Phase 1 into a logical module structure.

### Heuristic: what constitutes a Module?

A **Module** is a cohesive, deployable unit of code. Use these signals to identify module boundaries:

- A top-level package or directory with its own build manifest (`pom.xml`, `package.json`, `build.gradle`, `Cargo.toml`)
- A separate build target within a monorepo
- A directory that represents a distinct functional area and could be deployed independently
- In mainframe systems, a partition of programs grouped by function (e.g., all batch programs for a subsystem)

### Required attributes

- `name` -- the module name, typically matching the directory or package name
- `mapped_from_directory` -- MUST reference the corresponding **StorageLocation** from Phase 1

### Establishing the bridge

The extraction agent MUST set both sides of the code-to-module bridge:

- `Module.mapped_from_directory` pointing to the **StorageLocation**
- `StorageLocation.maps_to_module` pointing back to the **Module**

### Module dependencies

Use the **DefinitionReference** instances from Phase 2 to infer inter-module dependencies. When code in Module A imports or references code in Module B, set `depends_on_module` on Module A to include Module B.

### Optional enrichment

- `is_optional` -- whether the module is an optional plugin or extension
- `required_features` -- feature flags needed to enable the module
- `architectural_patterns` -- applicable patterns (e.g., `layered`, `hexagonal`, `cqrs`)
- `dependencies` -- inline **Dependency** instances with `dependency_type` (`runtime`, `build`, `optional`, `dev`)

```yaml
modules:
  - name: order-service
    mapped_from_directory: storage-locations/src-orders
    depends_on_module:
      - payment-module
      - inventory-module
    architectural_patterns:
      - hexagonal
    dependencies:
      - name: spring-boot-starter-web
        dependency_type: runtime
      - name: junit-jupiter
        dependency_type: dev

  - name: payment-module
    mapped_from_directory: storage-locations/src-payments
    is_optional: false
```

On the **StorageLocation** side, set the inverse:

```yaml
storage_locations:
  - name: src-orders
    location_path: src/main/java/com/example/orders
    maps_to_module: order-service
```

---

## Step 3: Group Modules into BoundedContexts

Create **BoundedContext** instances representing the DDD semantic boundaries within the system. This is the most subjective step in the extraction process -- the extraction agent SHOULD flag bounded context assignments for human review.

### Decision tree for identifying bounded context boundaries

Use these signals, ordered from strongest to weakest:

1. **Separate databases** -- if two modules use different databases or schemas, they are almost certainly in separate contexts
2. **Separate deployment units** -- independently deployed services map to separate contexts
3. **Separate teams** -- if different teams own different modules, those modules likely belong to different contexts
4. **Clear domain-oriented package names** -- directories like `orders/`, `inventory/`, `users/`, `payments/` are strong candidates for separate contexts
5. **Distinct ubiquitous language** -- if the same term (e.g., "account") means different things in different parts of the code, those parts belong to different contexts

When boundaries are unclear (e.g., a monolith with no clear domain separation), start with a single **BoundedContext** and refine later as domain understanding deepens.

### Required attributes

- `name` -- the context name, typically a domain concept (e.g., "Order Management", "Inventory")
- `contained_in_system` -- MUST reference the **System** instance
- `contains_modules` -- MUST list the **Module** instances in this context

### Recommended attributes

- `ubiquitous_language` -- list of key domain terms used within this context
- `context_map_relationship` -- the DDD relationship pattern as a free-text string (e.g., "Customer-Supplier", "Partnership", "Shared Kernel", "Conformist", "Anti-Corruption Layer")
- `upstream_from` / `downstream_from` -- other **BoundedContext** instances this context depends on or is depended on by
- `architectural_patterns` -- applicable patterns (e.g., `cqrs`, `event_sourcing`, `domain_model`)

### System-level link

The extraction agent MUST also set `System.contains_bounded_contexts` to reference all created **BoundedContext** instances.

```yaml
systems:
  - name: order-platform
    contains_bounded_contexts:
      - order-management-context
      - inventory-context
      - payment-context

bounded_contexts:
  - name: order-management-context
    contained_in_system: order-platform
    contains_modules:
      - order-service
    ubiquitous_language:
      - order
      - line item
      - fulfillment
      - shipment
    context_map_relationship: "Upstream to Inventory (Customer-Supplier)"
    downstream_from:
      - payment-context
    architectural_patterns:
      - domain_model
      - cqrs

  - name: payment-context
    contained_in_system: order-platform
    contains_modules:
      - payment-module
    ubiquitous_language:
      - payment
      - refund
      - transaction
      - settlement
    upstream_from:
      - order-management-context
```

---

## Step 4: Identify Components within Modules

Create **Component** instances representing the logical building blocks within each module. Components group related **EncapsulationUnit** instances by their architectural role.

### Heuristic: what constitutes a Component?

Group EncapsulationUnits by stereotype or architectural role:

- **Controller/Handler layer** -- classes annotated with `@Controller`, `@RestController`, or similar
- **Service layer** -- classes annotated with `@Service` or named `*Service`
- **Repository/DAO layer** -- classes annotated with `@Repository` or implementing data access
- **DTO/Model layer** -- data transfer objects, request/response models
- **Domain layer** -- domain entities, value objects, aggregates
- **Configuration layer** -- configuration classes, factories, dependency injection setup

### Required attributes

- `name` -- the component name (e.g., "OrderController", "PaymentService", "OrderRepository")
- `component_type` -- a free-text string describing the component's role (e.g., "controller", "service", "repository", "adapter")
- `contained_in_module` -- MUST reference the parent **Module**

### Establishing the bridge

The extraction agent MUST set both sides of the code-to-component bridge:

- `Component.implemented_by_code` -- list of **EncapsulationUnit** (or **CodeContainer**) instances that implement this component
- `EncapsulationUnit.implements_component` -- pointing back to the **Component**

### Module-level link

Set `Module.contains_components` to reference all components within the module.

```yaml
modules:
  - name: order-service
    contains_components:
      - order-controller
      - order-service-component
      - order-repository
      - order-dto-layer

components:
  - name: order-controller
    component_type: controller
    contained_in_module: order-service
    implemented_by_code:
      - OrderController       # EncapsulationUnit
      - OrderExceptionHandler  # EncapsulationUnit

  - name: order-service-component
    component_type: service
    contained_in_module: order-service
    implemented_by_code:
      - OrderService
      - OrderValidationService
      - OrderNotificationService

  - name: order-repository
    component_type: repository
    contained_in_module: order-service
    implemented_by_code:
      - OrderRepository
      - OrderItemRepository
```

On the **EncapsulationUnit** side, set the inverse:

```yaml
encapsulation_units:
  - name: OrderController
    encapsulation_type: class
    implements_component: order-controller
```

---

## Step 5: Extract Services

Create **Service** instances from deployment manifests. A **Service** represents an independently deployable runtime unit.

### Where to find services

Scan for deployment artifacts:

- **Dockerfiles** and `docker-compose.yml` -- each service definition is a **Service**
- **Kubernetes manifests** -- each Deployment, StatefulSet, or CronJob is a **Service**
- **Serverless configs** (`serverless.yml`, SAM templates, `functions/`) -- each function is a **Service**
- **JCL procedures** -- each batch job or CICS transaction is a **Service**
- **Procfiles**, `systemd` units, Windows Services -- each process definition is a **Service**

### Required attributes

- `name` -- the service name, matching the deployment artifact name
- `service_type` -- one of: `microservice`, `monolith`, `function`, `job`, `daemon`, `cics_transaction`, `ims_transaction`, `batch_program`, `stored_proc_service`
- `runs_module` -- MUST reference the **Module** this service runs

### Recommended attributes

- `depends_on_service` -- other **Service** instances this service depends on
- `exposes_endpoints` -- **Endpoint** instances exposed by this service (see Step 6)

### Module-level inverse

Set `Module.runs_as_services` on the corresponding module.

```yaml
services:
  - name: order-api
    service_type: microservice
    runs_module: order-service
    depends_on_service:
      - payment-api
      - inventory-api

  - name: order-processor
    service_type: job
    runs_module: order-service
    description: Nightly batch job for order reconciliation

  - name: payment-api
    service_type: microservice
    runs_module: payment-module
```

On the **Module** side:

```yaml
modules:
  - name: order-service
    runs_as_services:
      - order-api
      - order-processor
```

---

## Step 6: Extract Interfaces and Endpoints

**Interface** is an abstract class with three concrete subtypes. The extraction agent MUST determine which subtype to use based on the nature of the interface.

### UserInterface

Use for any human-facing interface. Set `category` to `user_interface`.

**Required attributes**:

- `name` -- the interface name
- `category` -- `user_interface`
- `ui_type` -- one of: `web_ui`, `mobile_ui`, `desktop_ui`, `cli`

**UserInterface** MAY contain **Screen** instances with `route` and `offers_operations` attributes.

```yaml
user_interfaces:
  - name: order-management-ui
    category: user_interface
    ui_type: web_ui
    exposed_by_system: order-platform
    screens:
      - name: order-list-screen
        route: /orders
      - name: order-detail-screen
        route: /orders/:id
      - name: create-order-screen
        route: /orders/new
```

### ProgrammaticInterface

Use for machine-to-machine interfaces. Set `category` to `programmatic_interface`.

**Required attributes**:

- `name` -- the interface name
- `category` -- `programmatic_interface`
- `api_type` -- one of: `rest_api`, `graphql_api`, `grpc_api`, `sdk`, `soap_api`

**ProgrammaticInterface** MAY contain **Endpoint** instances. Each **Endpoint** SHOULD specify `path`, `method`, and `protocol`.

```yaml
programmatic_interfaces:
  - name: order-rest-api
    category: programmatic_interface
    api_type: rest_api
    base_url: https://api.example.com/v2
    exposed_by_system: order-platform
    has_endpoints:
      - name: list-orders
        path: /orders
        method: GET
        protocol: https
      - name: create-order
        path: /orders
        method: POST
        protocol: https
      - name: get-order
        path: /orders/{id}
        method: GET
        protocol: https
      - name: cancel-order
        path: /orders/{id}/cancel
        method: POST
        protocol: https
```

**Endpoint** instances MAY also be linked to a **Service** via `exposed_by_service` / `Service.exposes_endpoints`.

### EventInterface

Use for event-driven interfaces. Set `category` to `event_interface`.

**Required attributes**:

- `name` -- the interface name
- `category` -- `event_interface`
- `event_type` -- one of: `webhook`, `message_queue`, `event_stream`, `pub_sub`

**EventInterface** MAY specify `topics` and contain **Subscription** instances.

```yaml
event_interfaces:
  - name: order-events
    category: event_interface
    event_type: pub_sub
    topics:
      - order.created
      - order.fulfilled
      - order.cancelled
    exposed_by_system: order-platform
    has_subscriptions:
      - name: inventory-order-subscription
        filter: "order.created"
        delivery_mode: at_least_once
```

### Linking interfaces

Interfaces MAY be linked at the **System** level via `System.exposes_interfaces`, or they MAY be linked to specific services via the **Endpoint** relationship. The extraction agent SHOULD use `System.exposes_interfaces` for the primary linkage and add service-level endpoint links for additional precision.

---

## Step 7: Identify External Systems and Integrations

Create an **ExternalSystem** for each system outside the extraction boundary that this system interacts with.

### Identifying external systems

Scan these sources:

- **Configuration files** -- database connection strings, API base URLs, message broker addresses
- **Environment variables** -- `DATABASE_URL`, `REDIS_HOST`, `STRIPE_API_KEY`
- **Infrastructure-as-Code** -- Terraform resources, CloudFormation stacks
- **Import statements** -- SDK imports for third-party services (e.g., `import stripe`, `import boto3`)
- **Docker Compose** -- linked services (PostgreSQL, Redis, RabbitMQ)

### Required ExternalSystem attributes

- `name` -- the external system name
- `system_type` -- one of: `third_party_service`, `partner_system`, `legacy_system`, `saas_application`

### Optional ExternalSystem attributes

- `owner` -- the team or vendor that owns the external system
- `sla` -- service level agreement
- `documentation_url` -- link to API docs

### Creating Integrations

For each connection between the system and an external system, create an **Integration** instance.

**Required Integration attributes**:

- `name` -- a descriptive name for the integration
- `integration_type` -- one of: `inbound`, `outbound`, `bidirectional`
- `integrates_with_system` -- reference to the **ExternalSystem**
- `belongs_to_system` -- reference to the **System**

**Recommended Integration attributes**:

- `protocol` -- one of: `http`, `https`, `websocket`, `grpc`, `amqp`, `mqtt`, `kafka`, `sftp`, `tcp`, `udp`, `corba`, `dcom`, `rmi`, `named_pipe`, `shared_memory`
- `integration_governed_by_contract` -- a **Contract** if one exists
- `uses_adapter` -- an **Adapter** if protocol translation is needed
- `protected_by_breaker` -- a **CircuitBreaker** if resilience patterns are in place

### Optional supporting entities

**Contract** -- create when a formal API specification exists:

- `contract_type` -- one of: `openapi`, `asyncapi`, `json_schema`, `protobuf`, `avro`, `graphql_schema`, `wsdl`
- `definition` -- the contract definition or path to the spec file

**Adapter** (extends **Component**) -- create when protocol translation occurs:

- `source_protocol` and `target_protocol` -- the protocols being translated between
- `transformation` -- description of the data transformation

**CircuitBreaker** -- create when resilience patterns are detected (e.g., Hystrix, Resilience4j, Polly):

- `failure_threshold` -- number of failures before opening
- `reset_timeout_seconds` -- time before attempting half-open
- `half_open_requests` -- requests allowed in half-open state

### System-level link

Set `System.has_integrations` to reference all **Integration** instances.

```yaml
external_systems:
  - name: stripe-payments
    system_type: third_party_service
    owner: Stripe Inc.
    documentation_url: https://stripe.com/docs/api

  - name: order-database
    system_type: legacy_system
    owner: Platform Team

  - name: notification-broker
    system_type: third_party_service
    owner: Platform Team

integrations:
  - name: stripe-payment-integration
    integration_type: outbound
    protocol: https
    integrates_with_system: stripe-payments
    belongs_to_system: order-platform
    integration_governed_by_contract: stripe-api-contract
    uses_adapter: stripe-adapter
    protected_by_breaker: stripe-circuit-breaker

  - name: order-db-integration
    integration_type: bidirectional
    protocol: tcp
    integrates_with_system: order-database
    belongs_to_system: order-platform

contracts:
  - name: stripe-api-contract
    contract_type: openapi
    definition: "specs/stripe-api-v3.yaml"

adapters:
  - name: stripe-adapter
    component_type: adapter
    source_protocol: https
    target_protocol: https
    transformation: "Maps internal PaymentRequest to Stripe charge API format"

circuit_breakers:
  - name: stripe-circuit-breaker
    failure_threshold: 5
    reset_timeout_seconds: 30
    half_open_requests: 3
```

---

## Capabilities and Features

If the extraction scope warrants it, the extraction agent MAY create **Capability** and **Feature** instances at this stage.

- **Capability** represents a discrete business or technical ability the system provides. Link via `provided_by_modules` to the **Module** instances that deliver it, and via `enables_features` to the **Feature** instances it supports.
- **Feature** represents a user-facing manifestation of one or more capabilities. Set `category` to one of: `core`, `optional`, `experimental`, `deprecated`.

These entities are often better populated in Phase 5 (Business Intent) when domain understanding is richer. Creating placeholders here and refining later is acceptable.

```yaml
capabilities:
  - name: order-placement
    provided_by_modules:
      - order-service
    enables_features:
      - place-order-feature

features:
  - name: place-order-feature
    category: core
    enabled_by_capabilities:
      - order-placement
```

---

## Phase 3 Checklist

Before proceeding to Phase 4, verify the following:

- [ ] A single **System** instance exists with `name`, `description`, and `version`
- [ ] Every top-level package or directory identified in Phase 1 maps to a **Module** via `mapped_from_directory` / `maps_to_module`
- [ ] Every **Module** is assigned to a **BoundedContext** via `contained_in_context` / `contains_modules`
- [ ] **Components** are identified within each module and linked to **EncapsulationUnit** instances via `implemented_by_code` / `implements_component`
- [ ] **Services** are identified from deployment manifests and linked to modules via `runs_module` / `runs_as_services`
- [ ] **Interfaces** are extracted and categorized by subtype (**UserInterface**, **ProgrammaticInterface**, **EventInterface**)
- [ ] **Endpoints** are documented for programmatic interfaces with `path`, `method`, and `protocol`
- [ ] **ExternalSystem** instances exist for every external dependency
- [ ] **Integration** instances connect the system to each external system with `integration_type` and `protocol`
- [ ] Module dependencies (`depends_on_module`) are captured from Phase 2 import analysis
- [ ] All inverse relationships are set (both sides of every bridge)
- [ ] Bounded context assignments are flagged for human review
