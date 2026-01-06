# Enumerations

This document describes all enumeration types defined in the Software Application Ontology (SAO).

## Table of Contents
- [Cardinality](#cardinality)
- [Channel Types](#channel-types)
- [Interface Types](#interface-types)
- [Service and Dependency Types](#service-and-dependency-types)
- [Actor Types](#actor-types)
- [Security and Authorization](#security-and-authorization)
- [Domain Modeling](#domain-modeling)
- [Behavior and Workflow](#behavior-and-workflow)
- [Data Management](#data-management)
- [Integration](#integration)
- [Deployment and Operations](#deployment-and-operations)
- [Observability](#observability)
- [Compliance](#compliance)
- [Features](#features)
- [Code Structure](#code-structure)

## Cardinality

Defines relationship cardinality options between entities.

- **ONE_TO_ONE**: One-to-one relationship
- **ONE_TO_MANY**: One-to-many relationship
- **MANY_TO_ONE**: Many-to-one relationship
- **MANY_TO_MANY**: Many-to-many relationship

## Channel Types

Types of communication channels in the system.

- **PUBLIC_CHANNEL**: Public communication channel accessible to all users
- **PRIVATE_CHANNEL**: Private communication channel with restricted access
- **MPIM**: Multi-party instant messaging
- **IM**: Direct instant messaging between two parties

## Interface Types

### Interface Categories

- **USER_INTERFACE**: Human-facing interface for user interaction
- **PROGRAMMATIC_INTERFACE**: Machine-to-machine API interface
- **EVENT_INTERFACE**: Event-driven asynchronous interface

### User Interface Types

- **WEB_UI**: Web browser-based user interface
- **MOBILE_UI**: Mobile device (iOS/Android) user interface
- **DESKTOP_UI**: Desktop application user interface
- **CLI**: Command-line interface

### API Types

- **REST_API**: RESTful HTTP-based API
- **GRAPHQL_API**: GraphQL query language API
- **GRPC_API**: gRPC remote procedure call API
- **SDK**: Software development kit for programmatic access
- **SOAP_API**: SOAP protocol-based web service API

### Event Interface Types

- **WEBHOOK**: HTTP callback for event notifications
- **MESSAGE_QUEUE**: Queue-based asynchronous messaging
- **EVENT_STREAM**: Continuous stream of events
- **PUB_SUB**: Publish-subscribe messaging pattern

## Service and Dependency Types

### Service Types

- **MICROSERVICE**: Small, independently deployable service
- **MONOLITH**: Single-tier monolithic application
- **FUNCTION**: Serverless function or lambda
- **JOB**: Batch processing job
- **DAEMON**: Background service or daemon process

### Dependency Types

- **RUNTIME**: Required at runtime for execution
- **BUILD**: Required at build/compile time
- **OPTIONAL**: Optional dependency for additional features
- **DEV**: Required only for development/testing

## Actor Types

### Actor Categories

- **HUMAN**: Human user or operator
- **SYSTEM**: Automated system or service

### Human Actor Types

- **END_USER**: Regular end user of the system
- **ADMINISTRATOR**: System administrator with elevated privileges
- **OPERATOR**: Operations personnel managing system runtime
- **DEVELOPER**: Software developer or engineer
- **AUDITOR**: Compliance or security auditor

### System Actor Types

- **INTERNAL_SERVICE**: Internal service within the system
- **EXTERNAL_SYSTEM**: External third-party system
- **SCHEDULED_PROCESS**: Scheduled or cron-based process
- **AI_AGENT**: Artificial intelligence agent or bot
- **MESSAGE_TRIGGER**: Message or event-triggered automation

## Security and Authorization

### Credential Types

- **PASSWORD**: Username and password credentials
- **TOKEN**: Token-based authentication (JWT, bearer token)
- **CERTIFICATE**: Digital certificate or X.509 certificate
- **API_KEY**: API key for service authentication
- **BIOMETRIC**: Biometric authentication (fingerprint, face recognition)
- **MFA**: Multi-factor authentication
- **OAUTH**: OAuth 2.0 authentication flow

### Policy Types

- **RBAC**: Role-Based Access Control
- **ABAC**: Attribute-Based Access Control
- **REBAC**: Relationship-Based Access Control
- **PBAC**: Policy-Based Access Control

### Scope Types

- **GLOBAL**: System-wide global scope
- **TENANT**: Limited to a specific tenant
- **ORGANIZATION**: Limited to an organization within a tenant
- **RESOURCE**: Limited to a specific resource or resource type
- **FIELD**: Limited to specific fields within a resource

### Constraint Types

- **TEMPORAL**: Time-based constraint (date/time ranges)
- **SPATIAL**: Location or geography-based constraint
- **ATTRIBUTE**: Attribute or property-based constraint
- **CONTEXT**: Context-dependent constraint (device, IP, etc.)
- **RATE_LIMIT**: Rate limiting or quota-based constraint

## Domain Modeling

### Attribute Categories

- **REQUIRED**: Required attribute that must have a value
- **OPTIONAL**: Optional attribute that may be null
- **COMPUTED**: Computed or calculated attribute
- **DERIVED**: Derived from other attributes
- **TRANSIENT**: Transient attribute not persisted

### Action Categories

- **QUERY**: Read-only query action
- **COMMAND**: State-changing command action
- **MUTATION**: Data mutation or modification action

### Command Types

- **CREATE**: Create a new entity
- **UPDATE**: Update an existing entity
- **DELETE**: Delete an entity
- **EXECUTE**: Execute an operation or process
- **ARCHIVE**: Archive an entity for retention
- **RESTORE**: Restore an archived entity

## Behavior and Workflow

### Workflow Types

- **SYNCHRONOUS**: Synchronous blocking workflow
- **ASYNCHRONOUS**: Asynchronous non-blocking workflow
- **SAGA**: Saga pattern for distributed transactions
- **CHOREOGRAPHY**: Event-driven choreography workflow
- **ORCHESTRATION**: Centrally orchestrated workflow

### Rule Categories

- **VALIDATION**: Validation rule for data integrity
- **BUSINESS**: Business logic or domain rule
- **DERIVATION**: Derivation rule for computed values
- **CONSTRAINT**: Constraint or invariant rule
- **TRIGGER**: Event trigger or automation rule

### Event Categories

- **DOMAIN_EVENT**: Domain-specific business event
- **INTEGRATION_EVENT**: Integration or cross-service event
- **SYSTEM_EVENT**: System-level technical event
- **AUDIT_EVENT**: Audit trail or compliance event

### Transaction Types

- **LOCAL**: Local transaction within a single database
- **DISTRIBUTED**: Distributed transaction across multiple resources
- **SAGA**: Saga pattern with compensating transactions
- **TWO_PHASE_COMMIT**: Two-phase commit protocol

## Data Management

### Data Store Types

- **RELATIONAL_DB**: Relational database (SQL)
- **DOCUMENT_DB**: Document-oriented database (NoSQL)
- **KEY_VALUE_STORE**: Key-value store (Redis, DynamoDB)
- **GRAPH_DB**: Graph database (Neo4j)
- **TIME_SERIES_DB**: Time-series database
- **OBJECT_STORAGE**: Object storage (S3, blob storage)
- **SEARCH_INDEX**: Search index (Elasticsearch, Solr)
- **CACHE**: In-memory cache
- **MESSAGE_BROKER**: Message broker or queue
- **DATA_LAKE**: Data lake for analytics

### Schema Types

- **TABLE_SCHEMA**: Relational database table schema
- **DOCUMENT_SCHEMA**: Document or JSON schema
- **EVENT_SCHEMA**: Event payload schema
- **API_SCHEMA**: API request/response schema
- **MESSAGE_SCHEMA**: Message format schema

### Data Classification Types

- **PUBLIC**: Publicly accessible information
- **INTERNAL**: Internal use only information
- **CONFIDENTIAL**: Confidential sensitive information
- **RESTRICTED**: Highly restricted information
- **PII**: Personally Identifiable Information
- **PHI**: Protected Health Information
- **PCI**: Payment Card Industry data

## Integration

### Integration Types

- **INBOUND**: Inbound integration receiving data
- **OUTBOUND**: Outbound integration sending data
- **BIDIRECTIONAL**: Bidirectional two-way integration

### External System Types

- **THIRD_PARTY_SERVICE**: Third-party external service
- **PARTNER_SYSTEM**: Partner or vendor system
- **LEGACY_SYSTEM**: Legacy system being integrated
- **SAAS_APPLICATION**: Software-as-a-Service application

### Protocol Types

- **HTTP**: Hypertext Transfer Protocol
- **HTTPS**: HTTP Secure (TLS/SSL)
- **WEBSOCKET**: WebSocket protocol for bidirectional communication
- **GRPC**: gRPC protocol
- **AMQP**: Advanced Message Queuing Protocol
- **MQTT**: Message Queuing Telemetry Transport
- **KAFKA**: Apache Kafka protocol
- **SFTP**: Secure File Transfer Protocol
- **TCP**: Transmission Control Protocol
- **UDP**: User Datagram Protocol

### Message Types

- **REQUEST**: Request message expecting a response
- **RESPONSE**: Response message to a request
- **NOTIFICATION**: One-way notification message
- **COMMAND**: Command message for action execution
- **EVENT**: Event notification message
- **QUERY**: Query message for data retrieval

### Contract Types

- **OPENAPI**: OpenAPI (Swagger) specification
- **ASYNCAPI**: AsyncAPI specification for async APIs
- **JSON_SCHEMA**: JSON Schema specification
- **PROTOBUF**: Protocol Buffers schema
- **AVRO**: Apache Avro schema
- **GRAPHQL_SCHEMA**: GraphQL schema definition
- **WSDL**: Web Services Description Language

## Deployment and Operations

### Environment Types

- **DEVELOPMENT**: Development environment for active development
- **TESTING**: Testing environment for QA and integration testing
- **STAGING**: Pre-production staging environment
- **PRODUCTION**: Live production environment
- **DR**: Disaster Recovery

### Deployment Unit Types

- **CONTAINER**: Container image (Docker, etc.)
- **VM**: Virtual machine image
- **SERVERLESS_FUNCTION**: Serverless function deployment package
- **BINARY**: Compiled binary executable
- **PACKAGE**: Application package (JAR, WAR, etc.)

### Configuration Types

- **ENVIRONMENT_VARIABLE**: Environment variable configuration
- **CONFIG_FILE**: Configuration file (YAML, JSON, properties)
- **SECRET**: Secret or sensitive configuration value
- **FEATURE_FLAG**: Feature flag or toggle
- **REMOTE_CONFIG**: Remote configuration service

### Infrastructure Types

- **COMPUTE**: Compute resources (VMs, containers)
- **STORAGE**: Storage resources (disks, volumes)
- **NETWORK**: Network infrastructure
- **LOAD_BALANCER**: Load balancer
- **DNS**: DNS service
- **CDN**: Content Delivery Network
- **FIREWALL**: Firewall or security group

## Observability

### Metric Types

- **COUNTER**: Monotonically increasing counter
- **GAUGE**: Value that can increase or decrease
- **HISTOGRAM**: Distribution of values in buckets
- **SUMMARY**: Summary statistics (quantiles, etc.)

### Log Types

- **APPLICATION**: Application-level logs
- **ACCESS**: Access and request logs
- **ERROR**: Error and exception logs
- **SECURITY**: Security event logs
- **AUDIT**: Audit trail logs
- **DEBUG**: Debug and diagnostic logs

### Health Check Types

- **LIVENESS**: Liveness probe for service health
- **READINESS**: Readiness probe for traffic acceptance
- **DEPENDENCY**: Health check for dependencies
- **STARTUP**: Startup probe during initialization

## Compliance

### Compliance Frameworks

- **GDPR**: General Data Protection Regulation (EU)
- **HIPAA**: Health Insurance Portability and Accountability Act
- **SOC2**: Service Organization Control 2
- **PCI_DSS**: Payment Card Industry Data Security Standard
- **ISO27001**: ISO 27001 Information Security Management
- **SOX**: Sarbanes-Oxley Act
- **CCPA**: California Consumer Privacy Act
- **FEDRAMP**: Federal Risk and Authorization Management Program

## Features

### Feature Categories

- **core**: Core essential feature
- **optional**: Optional add-on feature
- **experimental**: Experimental or beta feature
- **deprecated**: Deprecated feature scheduled for removal

## Code Structure

### Code Container Types

Types of physical code storage units.

- **source_file**: Standard source code file
- **library_member**: Member of a partitioned dataset or library (mainframe)
- **include_file**: Header or include file
- **script**: Executable script
- **configuration**: Configuration file
- **schema_definition**: Database or API schema definition
- **notebook_cell**: Jupyter/computational notebook cell
- **inline_code**: Embedded code (e.g., JavaScript in HTML, SQL in code)

### Storage Location Types

Types of storage locations for code containers.

- **directory**: Filesystem directory
- **library**: Partitioned dataset (mainframe) or static library
- **package**: Language package or module
- **namespace**: Logical namespace grouping
- **module_path**: Module search path

### Encapsulation Types

Types of encapsulation units across different programming paradigms.

**Object-Oriented:**
- **class**: Object-oriented class
- **interface**: Interface or contract definition
- **abstract_class**: Abstract base class
- **trait**: Trait (Rust, Scala) or mixin
- **enum_class**: Enumeration class
- **record_class**: Immutable record class (Java, C#)
- **singleton**: Singleton pattern implementation

**Procedural:**
- **program**: Standalone program (COBOL, Fortran, C)
- **subprogram**: Subprogram or subroutine module
- **unit**: Pascal/Ada unit

**Functional:**
- **module**: Functional module (Haskell, OCaml, F#)
- **namespace**: Namespace grouping
- **package**: Package grouping
- **library**: Library module

**Mainframe:**
- **batch_program**: Batch processing program
- **online_program**: Online transaction program (CICS, IMS)
- **copybook**: COBOL copybook

**Database:**
- **stored_procedure**: Database stored procedure package
- **function_package**: Function package (Oracle, PostgreSQL)
- **trigger**: Database trigger
- **view**: Database view

**Other:**
- **object**: Module-level object (Scala)
- **component**: Component definition
- **service**: Service class
- **controller**: Controller class
- **script**: Script module
- **composite**: Composite structure
- **other**: Other encapsulation types

### Callable Types

Types of callable/invocable code units across different paradigms.

**Object-Oriented Methods:**
- **method**: Instance method in OOP
- **static_method**: Static/class method
- **constructor**: Object constructor
- **destructor**: Object destructor/finalizer
- **property_getter**: Property getter method
- **property_setter**: Property setter method
- **operator_overload**: Operator overloading method
- **conversion_operator**: Type conversion operator
- **indexer**: Indexer/subscript operator
- **abstract_method**: Abstract method declaration
- **virtual_method**: Virtual/overridable method

**Procedural:**
- **function**: Function (procedural or functional programming)
- **procedure**: Procedure/subroutine
- **subroutine**: Subroutine
- **paragraph**: COBOL paragraph
- **section**: COBOL section

**Functional:**
- **lambda**: Anonymous lambda function
- **closure**: Closure
- **higher_order_function**: Higher-order function
- **curried_function**: Curried function
- **functor**: Functor

**Event Handling:**
- **event_handler**: Event handler
- **callback**: Callback function
- **delegate**: Delegate
- **signal_handler**: Signal handler

**Database:**
- **stored_procedure**: Database stored procedure
- **stored_function**: Database function
- **trigger_body**: Trigger implementation
- **cursor**: Database cursor

**Concurrency:**
- **coroutine**: Coroutine
- **generator**: Generator function
- **async_function**: Async/await function
- **thread_entry**: Thread entry point
- **task**: Task/future/promise

**Testing:**
- **test_case**: Unit test case
- **test_fixture**: Test fixture/setup method
- **mock**: Mock function

**Other:**
- **macro**: Preprocessor macro
- **template**: Template/generic function
- **generic_method**: Generic method
- **main_entry**: Main entry point
- **interrupt_handler**: Interrupt service routine
- **exception_handler**: Exception handler
- **finalizer**: Finalizer/cleanup method
- **factory_method**: Factory method
- **extension_method**: Extension method
- **script_function**: Script function
- **command**: Command/action function
- **other**: Other callable types

### Data Structure Types

Types of data structures across different paradigms.

**Object-Oriented:**
- **class_data**: Data members of a class
- **inner_class**: Inner/nested class
- **anonymous_class**: Anonymous class

**Procedural:**
- **struct**: C/C++ struct
- **record**: Pascal/Ada record or COBOL record
- **union**: C union

**COBOL/Mainframe:**
- **group_item**: COBOL group item (composite data)
- **copybook_structure**: COBOL copybook structure
- **commarea**: CICS communication area

**Functional:**
- **algebraic_data_type**: Algebraic data type (Haskell, ML)
- **type_class**: Type class
- **product_type**: Product type (tuple-like)
- **sum_type**: Sum/variant type

**Collections:**
- **array**: Fixed-size array
- **dynamic_array**: Dynamic/resizable array
- **list**: List structure
- **dictionary**: Dictionary/map/hash table
- **set**: Set structure
- **queue**: Queue structure
- **stack**: Stack structure
- **tree**: Tree structure
- **graph**: Graph structure

**Database:**
- **table_structure**: Database table structure
- **view_structure**: Database view structure
- **cursor_structure**: Cursor structure
- **rowtype**: Database row type

**Domain-Driven Design:**
- **value_object**: DDD value object
- **dto**: Data Transfer Object

**Other:**
- **tuple**: Tuple
- **pair**: Key-value pair
- **enum**: Enumeration
- **flags**: Bit flags
- **configuration_object**: Configuration data
- **message**: Message structure
- **event**: Event data
- **command**: Command data
- **json_schema**: JSON schema structure
- **xml_schema**: XML schema structure
- **protobuf_message**: Protocol Buffers message
- **avro_record**: Avro record
- **smart_pointer**: Smart pointer wrapper
- **reference_wrapper**: Reference wrapper

### Visibility Types

Visibility/access levels for code elements.

- **public**: Publicly accessible
- **private**: Private to containing unit
- **protected**: Protected (accessible to subclasses)
- **internal**: Internal to assembly/package
- **package**: Package-level visibility
- **module**: Module-level visibility
- **file**: File-level visibility

### Callable Categories

Categories of callable behavior.

- **synchronous**: Synchronous/blocking execution
- **asynchronous**: Asynchronous/non-blocking execution
- **event_driven**: Event-driven execution
- **reactive**: Reactive/stream-based execution

### Entry Point Types

Types of entry points for callables.

- **main**: Main entry point
- **constructor**: Object constructor
- **destructor**: Object destructor
- **initializer**: Initializer/setup
- **event_handler**: Event handler entry
- **callback**: Callback entry

### Data Structure Categories

Categories of data structures.

- **simple**: Simple/primitive data
- **composite**: Composite/aggregate data
- **collection**: Collection of items
- **reference**: Reference/pointer

### Data Element Categories

Categories of data elements.

- **field**: Class/struct field
- **property**: Property with accessors
- **variable**: Local or module variable
- **constant**: Constant value
- **parameter**: Function/method parameter

### Parameter Directions

Direction of parameter data flow.

- **input**: Input parameter (read-only)
- **output**: Output parameter (write-only)
- **input_output**: Input/output parameter (read-write)
- **return**: Return value

### Passing Mechanisms

Mechanisms for passing parameters.

- **by_value**: Pass by value (copy)
- **by_reference**: Pass by reference
- **by_name**: Pass by name (lazy evaluation)
- **by_need**: Pass by need (call-by-need)

### Code Block Types

Types of code blocks.

- **conditional**: Conditional block (if/else)
- **loop**: Loop block (for/while)
- **try_catch**: Exception handling block
- **synchronized**: Synchronized/locked block
- **transaction**: Transaction block
- **scope**: Scoping block

### Statement Categories

Categories of code statements.

- **assignment**: Assignment statement
- **invocation**: Method/function call
- **return**: Return statement
- **declaration**: Variable/constant declaration
- **control**: Control flow statement
- **exception**: Exception handling statement

### Reference Types

Types of code references (imports/includes).

- **import**: Import statement (Python, Java)
- **include**: Include directive (C/C++)
- **using**: Using directive (C#)
- **require**: Require statement (Ruby, Node.js)
- **copy**: COBOL COPY statement

### Control Flow Types

Types of control flow between code elements.

- **call**: Function/method call
- **conditional_branch**: Conditional branch (if/switch)
- **unconditional_branch**: Unconditional branch (goto)
- **loop**: Loop iteration
- **exception**: Exception throw/catch
- **return**: Return from callable

### Data Flow Types

Types of data flow between elements.

- **parameter_passing**: Parameter passed to callable
- **return_value**: Value returned from callable
- **field_access**: Access to field/property
- **assignment**: Assignment to variable
- **reference**: Reference to data

### Storage Classes

Storage classes for data elements.

- **automatic**: Automatic/stack storage
- **static**: Static storage
- **heap**: Heap-allocated storage
- **register**: Register storage
- **thread_local**: Thread-local storage

### Persistence Types

How data structures are persisted.

- **transient**: Not persisted
- **database**: Persisted in database
- **file**: Persisted in file
- **memory**: In-memory only
- **cache**: Cached storage

### Database Types

Database system types.

- **relational**: Relational database (SQL)
- **document**: Document database (MongoDB)
- **key_value**: Key-value store (Redis)
- **graph**: Graph database (Neo4j)
- **columnar**: Columnar database (Cassandra)
- **time_series**: Time-series database

### Linkage Types

Linkage types for code units.

- **static**: Static linkage
- **dynamic**: Dynamic linkage
- **external**: External linkage
- **internal**: Internal linkage

### Security Types

Security attributes for code elements.

- **public**: Public/unrestricted
- **authenticated**: Requires authentication
- **authorized**: Requires authorization
- **encrypted**: Encrypted at rest/transit
- **audited**: Audited access

### Structure Layouts

Memory layout for structures.

- **sequential**: Sequential layout
- **packed**: Packed layout (no padding)
- **explicit**: Explicit layout with offsets
- **union**: Union layout (overlapping)

### Equality Semantics

How equality is determined.

- **reference**: Reference/identity equality
- **value**: Value/structural equality
- **custom**: Custom equality logic

### Message Formats

Message/data formats.

- **json**: JSON format
- **xml**: XML format
- **protobuf**: Protocol Buffers
- **avro**: Apache Avro
- **msgpack**: MessagePack
- **yaml**: YAML format
- **csv**: CSV format
- **binary**: Binary format
