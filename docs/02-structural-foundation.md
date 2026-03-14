# Section 1: Structural Foundation

This section defines the core structural elements of a software application, providing the hierarchical organization from system down to individual components.

> **v2.0 Note**: In SAO v2.0, all single-use relationship slots have been inlined as class attributes. Classes no longer reference global `slots:` for single-domain relationships. Back-reference attributes are now defined directly on the relevant classes.

## Overview

The Structural Foundation provides a comprehensive framework for modeling software architecture at multiple levels of granularity, aligned with Domain-Driven Design (DDD) principles.

## Core Concepts

### System

**Definition**: Top-level container representing a software product, platform, or application.

**Purpose**: The System is the root entity that encapsulates all aspects of a software application, including its bounded contexts, integrations, policies, and compliance requirements.

**Key Attributes**:
- Inherits from `NamedEntity`
- Implements `Versionable` mixin
- Contains bounded contexts
- Has integrations with external systems
- Enforces security policies
- Must comply with regulatory requirements
- Is assessed for risks
- Exposes interfaces to users and other systems

**Relationships**:
- **contains_bounded_contexts**: Links to `BoundedContext` entities within the system
- **has_integrations**: Links to `Integration` entities for external system connections
- **enforces_policies**: Links to `Policy` entities that govern access control
- **must_comply_with**: Links to `ComplianceRequirement` entities
- **assessed_by**: Links to `RiskAssessment` entities
- **exposes_interfaces**: Links to `Interface` entities (user, programmatic, event)

**Example Use Cases**:
- Enterprise resource planning (ERP) system
- E-commerce platform
- Customer relationship management (CRM) system
- Financial trading platform

---

### BoundedContext

**Definition**: A semantic boundary within which a domain model applies consistently. Corresponds to the DDD bounded context concept.

**Purpose**: Isolates domain models to prevent ambiguity and maintain consistency within a specific business domain or subdomain.

**Key Attributes**:
- Inherits from `NamedEntity`
- **ubiquitous_language**: Key terms in the shared language for this context
- **context_map_relationship**: Relationship pattern (e.g., Customer-Supplier, Partnership)

**Relationships**:
- **contained_in_system**: Parent `System`
- **contains_modules**: Child `Module` entities
- **upstream_from**: Bounded contexts this one depends on
- **downstream_from**: Bounded contexts that depend on this one
- **contains_aggregates**: `Aggregate` entities within this context

**Context Mapping Patterns**:
- **Customer-Supplier**: Downstream context depends on upstream
- **Partnership**: Two contexts collaborate as equals
- **Shared Kernel**: Shared subset of the domain model
- **Conformist**: Downstream conforms to upstream model
- **Anti-Corruption Layer**: Translation layer between contexts

**Example Use Cases**:
- Order Management context in an e-commerce system
- Patient Care context in a healthcare system
- Trading context in a financial platform
- Inventory context in a warehouse system

---

### Module

**Definition**: A deployable, cohesive unit of functionality within a bounded context.

**Purpose**: Provides a logical grouping of related components that can be independently versioned and deployed.

**Key Attributes**:
- Inherits from `NamedEntity`
- Implements `Versionable` mixin
- **dependencies**: List of module dependencies with types (runtime, build, optional, dev)
- **is_optional**: Whether the module is optional
- **required_features**: Features needed to enable this module
- **mapped_from_directory**: Directory path this module is mapped from *(v2.0)*
- **module_tested_by_suites**: `TestSuite` entities that test this module *(v2.0)*
- **module_has_coverage**: `CoverageReport` entities for this module *(v2.0)*
- **module_managed_by_package_manager**: `PackageManager` managing this module *(v2.0)*
- **module_has_dependencies**: `Dependency` entities for this module *(v2.0)*

**Relationships**:
- **contained_in_context**: Parent `BoundedContext`
- **contains_components**: Child `Component` entities
- **depends_on_module**: Other modules this module depends on
- **depended_on_by_module**: Modules that depend on this module
- **provides_capabilities**: `Capability` entities offered by this module
- **runs_as_services**: `Service` entities that execute this module

**Dependency Types**:
- **RUNTIME**: Required at runtime for execution
- **BUILD**: Required at build/compile time
- **OPTIONAL**: Optional dependency for additional features
- **DEV**: Required only for development/testing

**Example Use Cases**:
- Payment processing module
- Authentication and authorization module
- Notification module
- Analytics module

---

### Component

**Definition**: A logical building block within a module (class, function group, service handler, etc.).

**Purpose**: Represents the finest-grained structural element that encapsulates specific functionality and can emit events, metrics, and logs.

**Key Attributes**:
- Inherits from `NamedEntity`
- **component_type**: Type of component (e.g., class, service, handler)
- **language**: Implementation language *(deprecated in v2.0 -- use `written_in_language` on CodeContainer instead)*
- **source_location**: Path to source code
- **dependencies**: Component-level dependencies
- **emits_metrics**: Metrics emitted by this component
- **generates_logs**: Logs generated by this component

**Back-Reference Attributes** *(v2.0)*:
- **tested_by_suites**: `TestSuite` entities that test this component
- **has_coverage**: `CoverageReport` entities for this component
- **component_serves_model**: `DomainModel` entities this component serves
- **component_uses_concurrency_pattern**: `ConcurrencyPattern` entities used by this component

**Relationships**:
- **contained_in_module**: Parent `Module`
- **exposes_operations**: `Operation` entities that can be invoked
- **emits_events**: `Event` entities produced by this component

**Component Types**:
- **Class**: Object-oriented class
- **Service**: Stateless service component
- **Handler**: Event or request handler
- **Repository**: Data access component
- **Controller**: API controller
- **Processor**: Business logic processor

**Example Use Cases**:
- OrderController class
- PaymentGatewayService
- EmailNotificationHandler
- UserRepository

---

### Capability

**Definition**: A discrete business or technical ability the system provides.

**Purpose**: Represents what the system can do, abstracting the implementation details.

**Relationships**:
- **realizes_features**: `Feature` entities enabled by this capability
- **requires_permissions**: `Permission` entities needed to use this capability

**Example Use Cases**:
- Process credit card payments
- Send email notifications
- Generate PDF reports
- Authenticate users via OAuth

---

### Feature

**Definition**: A user-facing manifestation of one or more capabilities.

**Purpose**: Represents functionality as perceived by end users or consumers of the system.

**Key Attributes**:
- Inherits from `NamedEntity`
- **category**: Feature category (CORE, OPTIONAL, EXPERIMENTAL, DEPRECATED)

**Relationships**:
- **enabled_by_capabilities**: `Capability` entities that enable this feature
- **controlled_by_configs**: `Configuration` entities that control availability
- **accessible_by_roles**: `Role` entities that can access this feature

**Feature Categories**:
- **CORE**: Essential feature required for basic operation
- **OPTIONAL**: Add-on feature that can be enabled/disabled
- **EXPERIMENTAL**: Beta feature under development
- **DEPRECATED**: Feature scheduled for removal

**Example Use Cases**:
- Dark mode toggle
- Multi-factor authentication
- Advanced search filters
- Export to Excel

---

### Interface

**Definition**: A contract-defined boundary through which interaction occurs (abstract base class).

**Purpose**: Defines how actors and systems interact with the application.

**Key Attributes**:
- **category**: Interface category (USER_INTERFACE, PROGRAMMATIC_INTERFACE, EVENT_INTERFACE)
- **authentication_required**: Whether authentication is required
- **rate_limit**: Requests per minute limit

**Relationships**:
- **defined_by_contract**: `Contract` entity specifying the interface

**Specialized Interface Types**:

#### UserInterface
User-facing interface for human interaction.

**Attributes**:
- **ui_type**: WEB_UI, MOBILE_UI, DESKTOP_UI, CLI
- **screens**: List of `Screen` entities

#### ProgrammaticInterface
Machine-to-machine API interface.

**Attributes**:
- **api_type**: REST_API, GRAPHQL_API, GRPC_API, SDK, SOAP_API
- **base_url**: Base URL for the API
- **has_endpoints**: `Endpoint` entities

#### EventInterface
Event-driven asynchronous interface.

**Attributes**:
- **event_type**: WEBHOOK, MESSAGE_QUEUE, EVENT_STREAM, PUB_SUB
- **topics**: Event topics or channels
- **has_subscriptions**: `Subscription` entities

---

### Screen

**Definition**: A single screen or view in a user interface.

**Purpose**: Represents a specific UI view that offers operations to users.

**Key Attributes**:
- Inherits from `NamedEntity` *(v2.0 change: Screen no longer inherits from UserInterface)*
- **route**: URL route or navigation path
- **part_of_ui**: The `UserInterface` this screen belongs to (range: UserInterface, inverse: `ui_screens`)

> **v2.0 Note**: Screen's parent class changed from `UserInterface` to `NamedEntity`. The relationship to a UserInterface is now expressed via the `part_of_ui` attribute. Correspondingly, UserInterface now has a `ui_screens` attribute to reference its screens.

**Relationships**:
- **offers_operations**: `Operation` entities available on this screen

**Example Use Cases**:
- Login screen
- Dashboard view
- User profile page
- Settings panel

---

### Service

**Definition**: An independently deployable runtime unit.

**Purpose**: Represents a running process that exposes endpoints and can be deployed independently.

**Key Attributes**:
- Inherits from `NamedEntity`
- **service_type**: MICROSERVICE, MONOLITH, FUNCTION, JOB, DAEMON
- **health_checks**: Health check definitions
- **emits_metrics**: Metrics emitted by the service

**Relationships**:
- **exposes_endpoints**: `Endpoint` entities
- **depends_on_service**: Service dependencies
- **depended_on_by_service**: Services that depend on this one
- **deployed_as**: `Deployment` entities

**Service Types**:
- **MICROSERVICE**: Small, independently deployable service
- **MONOLITH**: Single-tier monolithic application
- **FUNCTION**: Serverless function or lambda
- **JOB**: Batch processing job
- **DAEMON**: Background service or daemon process

**Example Use Cases**:
- Order processing microservice
- User authentication service
- Payment gateway service
- Nightly batch job for report generation

---

### Endpoint

**Definition**: A specific addressable entry point on a service.

**Purpose**: Represents a concrete API endpoint or service entry point.

**Key Attributes**:
- **path**: URL path or route
- **method**: HTTP method or operation type
- **operations**: Operations available at this endpoint
- **protocol**: Communication protocol
- **port**: Port number

**Relationships**:
- **exposed_by_service**: Parent `Service`
- **belongs_to_interface**: `ProgrammaticInterface` this endpoint is part of

**Example Use Cases**:
- `POST /api/v1/orders`
- `GET /api/v1/users/{id}`
- `PUT /api/v1/products/{id}`
- `DELETE /api/v1/sessions/{id}`

---

### Dependency

**Definition**: A required relationship between components or services.

**Purpose**: Documents dependencies for build, deployment, and runtime management.

**Key Attributes**:
- Inherits from `NamedEntity`
- **dependency_type**: RUNTIME, BUILD, OPTIONAL, DEV
- **target**: Target entity of the dependency
- **version_constraint**: Version constraint expression
- **is_optional**: Whether the dependency is optional

**Example Use Cases**:
- Runtime dependency on PostgreSQL database
- Build dependency on TypeScript compiler
- Optional dependency on Redis for caching
- Dev dependency on Jest for testing

---

## Architectural Patterns

### Layered Architecture
The structural foundation supports layered architecture by allowing modules to be organized into presentation, application, domain, and infrastructure layers.

### Microservices Architecture
Services can be independently deployed and scaled, with clear dependency relationships and communication through endpoints.

### Domain-Driven Design
Bounded contexts align with business domains, aggregates enforce transactional boundaries, and modules provide cohesive units of functionality.

### Modular Monolith
A system can start as a modular monolith with well-defined module boundaries, making it easier to extract microservices later.

---

## Best Practices

1. **Bounded Context Boundaries**: Keep bounded contexts aligned with business domains, not technical layers.

2. **Module Cohesion**: Ensure modules have high internal cohesion and low coupling with other modules.

3. **Dependency Management**: Document all dependencies explicitly with appropriate types and version constraints.

4. **Interface Contracts**: Define clear contracts for all interfaces to enable independent evolution.

5. **Service Granularity**: Choose service granularity based on team organization, deployment needs, and business capabilities.

6. **Capability-Feature Mapping**: Keep capabilities implementation-agnostic and map features to capabilities for flexibility.

---

## Relationships with Other Sections

- **Section 2 (Actors and Identity)**: Actors interact with interfaces and perform operations
- **Section 3 (Authorization)**: Policies govern access to capabilities and features
- **Section 4 (Domain Modeling)**: Aggregates are contained within bounded contexts
- **Section 5 (Behavior)**: Components expose operations and emit events
- **Section 6 (Data Management)**: Aggregates are persisted in data stores
- **Section 7 (Integration)**: Systems integrate with external systems
- **Section 8 (Deployment)**: Services are deployed as deployment units
- **Section 9 (Observability)**: Components emit metrics and logs
- **Section 10 (Governance)**: Systems must comply with requirements
