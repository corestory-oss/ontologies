# Enumerations

This document describes all enumeration types defined in the Software Application Ontology (SAO).

## Table of Contents
- [Cardinality](#cardinality)
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
- [Type System](#type-system)
- [Error Handling](#error-handling)
- [File Operations](#file-operations)
- [Screen and Terminal](#screen-and-terminal)
- [Batch Processing](#batch-processing)
- [Inter-Process Communication](#inter-process-communication)
- [Metaprogramming](#metaprogramming)
- [Memory and Ownership](#memory-and-ownership)
- [Database Constraints and Indexes](#database-constraints-and-indexes)
- [Programming Paradigms](#programming-paradigms)

## Cardinality

Defines relationship cardinality options between entities.

- `one_to_one`: One-to-one relationship
- `one_to_many`: One-to-many relationship
- `many_to_one`: Many-to-one relationship
- `many_to_many`: Many-to-many relationship

## Interface Types

### Interface Categories

- `user_interface`: Human-facing interface for user interaction
- `programmatic_interface`: Machine-to-machine API interface
- `event_interface`: Event-driven asynchronous interface

### User Interface Types

- `web_ui`: Web browser-based user interface
- `mobile_ui`: Mobile device (iOS/Android) user interface
- `desktop_ui`: Desktop application user interface
- `cli`: Command-line interface

### API Types

- `rest_api`: RESTful HTTP-based API
- `graphql_api`: GraphQL query language API
- `grpc_api`: gRPC remote procedure call API
- `sdk`: Software development kit for programmatic access
- `soap_api`: SOAP protocol-based web service API

### Event Interface Types

- `webhook`: HTTP callback for event notifications
- `message_queue`: Queue-based asynchronous messaging
- `event_stream`: Continuous stream of events
- `pub_sub`: Publish-subscribe messaging pattern

## Service and Dependency Types

### Service Types

- `microservice`: Small, independently deployable service
- `monolith`: Single-tier monolithic application
- `function`: Serverless function or lambda
- `job`: Batch processing job
- `daemon`: Background service or daemon process
- `cics_transaction`: CICS online transaction
- `ims_transaction`: IMS online transaction
- `batch_program`: Mainframe batch program
- `stored_proc_service`: Stored procedure exposed as service

### Dependency Types

- `runtime`: Required at runtime for execution
- `build`: Required at build/compile time
- `optional`: Optional dependency for additional features
- `dev`: Required only for development/testing

## Actor Types

### Actor Categories

- `human`: Human user or operator
- `system`: Automated system or service

### Human Actor Types

- `end_user`: Regular end user of the system
- `administrator`: System administrator with elevated privileges
- `operator`: Operations personnel managing system runtime
- `developer`: Software developer or engineer
- `auditor`: Compliance or security auditor

### System Actor Types

- `internal_service`: Internal service within the system
- `external_system`: External third-party system
- `scheduled_process`: Scheduled or cron-based process
- `ai_agent`: Artificial intelligence agent or bot
- `message_trigger`: Message or event-triggered automation

## Security and Authorization

### Credential Types

- `password`: Username and password credentials
- `token`: Token-based authentication (JWT, bearer token)
- `certificate`: Digital certificate or X.509 certificate
- `api_key`: API key for service authentication
- `biometric`: Biometric authentication (fingerprint, face recognition)
- `mfa`: Multi-factor authentication
- `oauth`: OAuth 2.0 authentication flow

### Policy Types

- `rbac`: Role-Based Access Control
- `abac`: Attribute-Based Access Control
- `rebac`: Relationship-Based Access Control
- `pbac`: Policy-Based Access Control

### Scope Types

- `global`: System-wide global scope
- `tenant`: Limited to a specific tenant
- `organization`: Limited to an organization within a tenant
- `resource`: Limited to a specific resource or resource type
- `field`: Limited to specific fields within a resource

### Constraint Types

- `temporal`: Time-based constraint (date/time ranges)
- `spatial`: Location or geography-based constraint
- `attribute`: Attribute or property-based constraint
- `context`: Context-dependent constraint (device, IP, etc.)
- `rate_limit`: Rate limiting or quota-based constraint

## Domain Modeling

### Attribute Categories

- `required`: Required attribute that must have a value
- `optional`: Optional attribute that may be null
- `computed`: Computed or calculated attribute
- `derived`: Derived from other attributes
- `transient`: Transient attribute not persisted

### Action Categories

- `query`: Read-only query action
- `command`: State-changing command action
- `mutation`: Data mutation or modification action

### Command Types

- `create`: Create a new entity
- `update`: Update an existing entity
- `delete`: Delete an entity
- `execute`: Execute an operation or process
- `archive`: Archive an entity for retention
- `restore`: Restore an archived entity

## Behavior and Workflow

### Workflow Types

- `synchronous`: Synchronous blocking workflow
- `asynchronous`: Asynchronous non-blocking workflow
- `saga`: Saga pattern for distributed transactions
- `choreography`: Event-driven choreography workflow
- `orchestration`: Centrally orchestrated workflow

### Rule Categories

- `validation`: Validation rule for data integrity
- `business`: Business logic or domain rule
- `derivation`: Derivation rule for computed values
- `constraint`: Constraint or invariant rule
- `trigger`: Event trigger or automation rule

### Event Categories

- `domain_event`: Domain-specific business event
- `integration_event`: Integration or cross-service event
- `system_event`: System-level technical event
- `audit_event`: Audit trail or compliance event

### Transaction Types

- `local`: Local transaction within a single database
- `distributed`: Distributed transaction across multiple resources
- `saga`: Saga pattern with compensating transactions
- `two_phase_commit`: Two-phase commit protocol

## Data Management

### Data Store Types

- `relational_db`: Relational database (SQL)
- `document_db`: Document-oriented database (NoSQL)
- `key_value_store`: Key-value store (Redis, DynamoDB)
- `graph_db`: Graph database (Neo4j)
- `time_series_db`: Time-series database
- `object_storage`: Object storage (S3, blob storage)
- `search_index`: Search index (Elasticsearch, Solr)
- `cache`: In-memory cache
- `message_broker`: Message broker or queue
- `data_lake`: Data lake for analytics
- `vsam`: IBM VSAM dataset
- `flat_file`: Sequential or flat file
- `isam`: Indexed Sequential Access Method file
- `dead_letter_queue`: Dead letter queue

### Schema Types

- `table_schema`: Relational database table schema
- `document_schema`: Document or JSON schema
- `event_schema`: Event payload schema
- `api_schema`: API request/response schema
- `message_schema`: Message format schema

### Data Classification Types

- `public`: Publicly accessible information
- `internal`: Internal use only information
- `confidential`: Confidential sensitive information
- `restricted`: Highly restricted information
- `pii`: Personally Identifiable Information
- `phi`: Protected Health Information
- `pci`: Payment Card Industry data

## Integration

### Integration Types

- `inbound`: Inbound integration receiving data
- `outbound`: Outbound integration sending data
- `bidirectional`: Bidirectional two-way integration

### External System Types

- `third_party_service`: Third-party external service
- `partner_system`: Partner or vendor system
- `legacy_system`: Legacy system being integrated
- `saas_application`: Software-as-a-Service application

### Protocol Types

- `http`: Hypertext Transfer Protocol
- `https`: HTTP Secure (TLS/SSL)
- `websocket`: WebSocket protocol for bidirectional communication
- `grpc`: gRPC protocol
- `amqp`: Advanced Message Queuing Protocol
- `mqtt`: Message Queuing Telemetry Transport
- `kafka`: Apache Kafka protocol
- `sftp`: Secure File Transfer Protocol
- `tcp`: Transmission Control Protocol
- `udp`: User Datagram Protocol
- `corba`: Common Object Request Broker Architecture
- `dcom`: Distributed Component Object Model
- `rmi`: Java Remote Method Invocation
- `named_pipe`: Named pipe protocol
- `shared_memory`: Shared memory protocol

### Message Types

- `request`: Request message expecting a response
- `response`: Response message to a request
- `notification`: One-way notification message
- `command`: Command message for action execution
- `event`: Event notification message
- `query`: Query message for data retrieval

### Contract Types

- `openapi`: OpenAPI (Swagger) specification
- `asyncapi`: AsyncAPI specification for async APIs
- `json_schema`: JSON Schema specification
- `protobuf`: Protocol Buffers schema
- `avro`: Apache Avro schema
- `graphql_schema`: GraphQL schema definition
- `wsdl`: Web Services Description Language

## Deployment and Operations

### Environment Types

- `development`: Development environment for active development
- `testing`: Testing environment for QA and integration testing
- `staging`: Pre-production staging environment
- `production`: Live production environment
- `dr`: Disaster Recovery

### Deployment Unit Types

- `container`: Container image (Docker, etc.)
- `vm`: Virtual machine image
- `serverless_function`: Serverless function deployment package
- `binary`: Compiled binary executable
- `package`: Application package (JAR, WAR, etc.)

### Configuration Types

- `environment_variable`: Environment variable configuration
- `config_file`: Configuration file (YAML, JSON, properties)
- `secret`: Secret or sensitive configuration value
- `feature_flag`: Feature flag or toggle
- `remote_config`: Remote configuration service

### Infrastructure Types

- `compute`: Compute resources (VMs, containers)
- `storage`: Storage resources (disks, volumes)
- `network`: Network infrastructure
- `load_balancer`: Load balancer
- `dns`: DNS service
- `cdn`: Content Delivery Network
- `firewall`: Firewall or security group
- `api_gateway`: API gateway or ingress controller
- `service_mesh`: Service mesh control plane (Istio, Linkerd, etc.)

## Observability

### Metric Types

- `counter`: Monotonically increasing counter
- `gauge`: Value that can increase or decrease
- `histogram`: Distribution of values in buckets
- `summary`: Summary statistics (quantiles, etc.)

### Log Types

- `application`: Application-level logs
- `access`: Access and request logs
- `error`: Error and exception logs
- `security`: Security event logs
- `audit`: Audit trail logs
- `debug`: Debug and diagnostic logs

### Health Check Types

- `liveness`: Liveness probe for service health
- `readiness`: Readiness probe for traffic acceptance
- `dependency`: Health check for dependencies
- `startup`: Startup probe during initialization

## Compliance

### Compliance Frameworks

- `gdpr`: General Data Protection Regulation (EU)
- `hipaa`: Health Insurance Portability and Accountability Act
- `soc2`: Service Organization Control 2
- `pci_dss`: Payment Card Industry Data Security Standard
- `iso27001`: ISO 27001 Information Security Management
- `sox`: Sarbanes-Oxley Act
- `ccpa`: California Consumer Privacy Act
- `fedramp`: Federal Risk and Authorization Management Program

## Features

### Feature Categories

- `core`: Core essential feature
- `optional`: Optional add-on feature
- `experimental`: Experimental or beta feature
- `deprecated`: Deprecated feature scheduled for removal

## Code Structure

### Code Container Types

Types of physical code storage units.

- `source_file`: Standard source code file
- `library_member`: Member of a partitioned dataset or library (mainframe)
- `include_file`: Header or include file
- `script`: Executable script
- `configuration`: Configuration file
- `schema_definition`: Database or API schema definition
- `notebook_cell`: Jupyter/computational notebook cell
- `inline_code`: Embedded code (e.g., JavaScript in HTML, SQL in code)
- `jcl_member`: JCL member in a PDS
- `rpg_source`: RPG source
- `pli_source`: PL/I source
- `assembler_source`: Assembler source
- `cl_source`: IBM CL source

### Storage Location Types

Types of storage locations for code containers.

- `directory`: Filesystem directory
- `library`: Partitioned dataset (mainframe) or static library
- `package`: Language package or module
- `namespace`: Logical namespace grouping
- `module_path`: Module search path

### Encapsulation Types

Types of encapsulation units across different programming paradigms.

**Object-Oriented:**
- `class`: Object-oriented class
- `interface`: Interface or contract definition
- `abstract_class`: Abstract base class
- `trait`: Trait (Rust, Scala) or mixin
- `enum_class`: Enumeration class
- `record_class`: Record or data class (Java records, Python dataclass)
- `singleton`: Singleton pattern implementation

**Procedural:**
- `program`: Standalone program (COBOL, Fortran)
- `subprogram`: Callable subprogram or subroutine library
- `unit`: Pascal/Delphi unit

**Functional:**
- `module`: Functional module (Haskell, OCaml, F#)
- `namespace`: Namespace grouping
- `package`: Package grouping
- `library`: Library module

**Mainframe:**
- `batch_program`: Batch processing program
- `online_program`: Online transaction program (CICS, IMS)
- `copybook`: COBOL copybook

**Database:**
- `stored_procedure`: Database stored procedure package
- `function_package`: Function package (Oracle, PostgreSQL)
- `trigger`: Database trigger
- `view`: Database view

**Other:**
- `object`: JavaScript/prototype-based object
- `component`: Component (React, Angular, Vue)
- `service`: Service class
- `controller`: Controller (MVC pattern)
- `script`: Script module
- `composite`: Composite structure
- `other`: Other encapsulation types
- `rpg_module`: RPG module
- `rpg_service_program`: RPG service program
- `pli_procedure`: PL/I procedure
- `pli_package`: PL/I package
- `assembler_csect`: Assembler control section

### Callable Types

Types of callable/invocable code units across different paradigms.

**Object-Oriented Methods:**
- `method`: Instance method in OOP
- `static_method`: Static/class method
- `constructor`: Object constructor
- `destructor`: Object destructor/finalizer
- `property_getter`: Property getter method
- `property_setter`: Property setter method
- `operator_overload`: Operator overloading method
- `conversion_operator`: Type conversion operator
- `indexer`: Indexer/subscript operator
- `abstract_method`: Abstract method declaration
- `virtual_method`: Virtual/overridable method

**Procedural:**
- `function`: Function (procedural or functional programming)
- `procedure`: Procedure/subroutine
- `subroutine`: Subroutine
- `paragraph`: COBOL paragraph
- `section`: COBOL section

**Functional:**
- `lambda`: Anonymous lambda function
- `closure`: Closure
- `higher_order_function`: Higher-order function
- `curried_function`: Curried function
- `functor`: Functor

**Event Handling:**
- `event_handler`: Event handler
- `callback`: Callback function
- `delegate`: Delegate
- `signal_handler`: Signal handler

**Database:**
- `stored_procedure`: Database stored procedure
- `stored_function`: Database function
- `trigger_body`: Trigger implementation
- `cursor`: Database cursor

**Concurrency:**
- `coroutine`: Coroutine
- `generator`: Generator function
- `async_function`: Async/await function
- `thread_entry`: Thread entry point
- `task`: Task/future/promise

**Testing:**
- `test_case`: Unit test case
- `test_fixture`: Test fixture/setup method
- `mock`: Mock function

**Other:**
- `macro`: Preprocessor macro
- `template`: Template/generic function
- `generic_method`: Generic method
- `main_entry`: Main entry point
- `interrupt_handler`: Interrupt service routine
- `exception_handler`: Exception handler
- `finalizer`: Finalizer/cleanup method
- `factory_method`: Factory method
- `extension_method`: Extension method
- `script_function`: Script function
- `command`: Command/action function
- `other`: Other callable types
- `rpg_subprocedure`: RPG subprocedure
- `pli_entry`: PL/I ENTRY point
- `assembler_entry`: Assembler entry point
- `rpg_subroutine`: RPG subroutine

### Data Structure Types

Types of data structures across different paradigms.

**Object-Oriented:**
- `class_data`: Data members of a class
- `inner_class`: Inner/nested class
- `anonymous_class`: Anonymous class

**Procedural:**
- `struct`: C/C++ struct
- `record`: Pascal/Ada record or COBOL record
- `union`: C union

**COBOL/Mainframe:**
- `group_item`: COBOL group item (composite data)
- `copybook_structure`: COBOL copybook structure
- `commarea`: CICS communication area

**Functional:**
- `algebraic_data_type`: Algebraic data type (Haskell, ML)
- `type_class`: Type class
- `product_type`: Product type (tuple-like)
- `sum_type`: Sum/variant type

**Collections:**
- `array`: Fixed-size array
- `dynamic_array`: Dynamic/resizable array
- `list`: List structure
- `dictionary`: Dictionary/map/hash table
- `set`: Set structure
- `queue`: Queue structure
- `stack`: Stack structure
- `tree`: Tree structure
- `graph`: Graph structure

**Database:**
- `table_structure`: Database table structure
- `view_structure`: Database view structure
- `cursor_structure`: Cursor structure
- `rowtype`: Database row type

**Domain-Driven Design:**
- `value_object`: DDD value object
- `dto`: Data Transfer Object

**Other:**
- `tuple`: Tuple
- `pair`: Key-value pair
- `enum`: Enumeration
- `flags`: Bit flags
- `configuration_object`: Configuration data
- `message`: Message structure
- `event`: Event data
- `command`: Command data
- `json_schema`: JSON schema structure
- `xml_schema`: XML schema structure
- `protobuf_message`: Protocol Buffers message
- `avro_record`: Avro record
- `smart_pointer`: Smart pointer wrapper
- `reference_wrapper`: Reference wrapper
- `rpg_data_structure`: RPG data structure
- `pli_structure`: PL/I structure
- `assembler_dsect`: Assembler dummy section
- `cobol_file_descriptor`: COBOL FD entry
- `linkage_section`: COBOL linkage section structure
- `opaque_type`: Opaque type
- `variant`: Variant type
- `other`: Other data structure types

### Visibility Types

Visibility/access levels for code elements.

- `public`: Publicly accessible
- `private`: Private to containing unit
- `protected`: Protected (accessible to subclasses)
- `internal`: Internal to assembly/package
- `package`: Package-level visibility

### Callable Categories

Behavioral-role categories of callable units.

- `normal`: Normal callable
- `operator`: Operator overload
- `main_entry`: Main entry point

### Entry Point Types

Types of entry points for callables.

- `main_program`: Main program entry point
- `transaction_entry`: Transaction entry point
- `event_handler`: Event handler entry
- `scheduled_entry`: Scheduled entry point
- `api_endpoint`: API endpoint entry

### Data Structure Categories

Categories of data structures.

- `composite`: Composite/aggregate data
- `collection`: Collection of items
- `hierarchical`: Hierarchical data
- `value_type`: Value type
- `reference_type`: Reference type
- `union`: Union type

### Data Element Categories

Categories of data elements.

- `field`: Class/struct field
- `static_field`: Static field
- `local_variable`: Local variable
- `parameter`: Function/method parameter
- `constant`: Constant value
- `global_variable`: Global variable
- `computed`: Computed data element
- `temporary`: Temporary data element

### Parameter Directions

Direction of parameter data flow.

- `input`: Input parameter (read-only)
- `output`: Output parameter (write-only)
- `input_output`: Input/output parameter (read-write)
- `return`: Return value

### Passing Mechanisms

Mechanisms for passing parameters.

- `by_value`: Pass by value (copy)
- `by_reference`: Pass by reference
- `by_name`: Pass by name (lazy evaluation)
- `by_result`: Pass by result (copy-out)

### Code Block Types

Types of code blocks.

- `sequential`: Sequential block
- `conditional`: Conditional block (if/else)
- `loop`: Loop block (for/while)
- `try_catch`: Exception handling block
- `transaction`: Transaction block
- `critical_section`: Critical section (synchronized/locked block)
- `scope`: Scoping block

### Statement Categories

Categories of code statements.

- `declaration`: Variable/constant declaration
- `assignment`: Assignment statement
- `invocation`: Method/function call
- `control_transfer`: Control transfer statement
- `io_operation`: I/O operation statement
- `data_manipulation`: Data manipulation statement
- `transaction_control`: Transaction control statement
- `exception_handling`: Exception handling statement

### Reference Types

Types of code references (imports/includes).

- `import_module`: Import module reference
- `import_symbol`: Import symbol reference
- `include_source`: Include source reference
- `inherit`: Inheritance reference
- `implement`: Implementation reference

### Control Flow Types

Types of control flow between code elements.

- `call`: Function/method call
- `async_call`: Asynchronous call
- `branch`: Conditional branch
- `jump`: Unconditional jump
- `return`: Return from callable
- `throw`: Exception throw
- `yield`: Yield control

### Data Flow Types

Types of data flow between elements.

- `read`: Read data
- `write`: Write data
- `modify`: Modify data
- `define`: Define data
- `use`: Use data

### Storage Classes

Storage classes for data elements.

- `automatic`: Automatic/stack storage
- `static`: Static storage
- `heap`: Heap-allocated storage
- `register`: Register storage
- `thread_local`: Thread-local storage
- `external`: External storage

### Persistence Types

How data structures are persisted.

- `transient`: Not persisted
- `database_table`: Persisted in database table
- `database_view`: Persisted as database view
- `file_record`: Persisted as file record
- `serialized`: Serialized persistence
- `cached`: Cached storage
- `distributed_cache`: Distributed cache
- `message_queue`: Message queue persistence
- `object_store`: Object store persistence
- `document_store`: Document store persistence
- `key_value_store`: Key-value store persistence
- `graph_database`: Graph database persistence

### Database Types

Database system types.

- `oracle`: Oracle database
- `postgresql`: PostgreSQL database
- `sql_server`: SQL Server database
- `mysql`: MySQL database
- `db2`: IBM DB2 database
- `teradata`: Teradata database
- `sybase`: Sybase database
- `informix`: Informix database
- `mongodb`: MongoDB database
- `cassandra`: Cassandra database
- `sqlite`: SQLite database
- `ims_db`: IBM IMS hierarchical database
- `adabas`: Software AG Adabas
- `idms`: CA IDMS network database

### Linkage Types

Linkage types for code units.

- `static`: Static linkage
- `dynamic`: Dynamic linkage
- `inline`: Inline linkage
- `late_binding`: Late binding linkage

### Security Types

Database security context types.

- `definer`: Executes with definer's privileges
- `invoker`: Executes with invoker's privileges

### Structure Layouts

Memory layout for structures.

- `sequential`: Sequential layout
- `explicit`: Explicit layout with offsets
- `auto`: Automatic layout
- `packed`: Packed layout (no padding)

### Equality Semantics

How equality is determined.

- `by_value`: Value/structural equality
- `by_reference`: Reference equality
- `by_identity`: Identity equality
- `custom`: Custom equality logic

### Message Formats

Message/data formats.

- `json`: JSON format
- `xml`: XML format
- `protobuf`: Protocol Buffers
- `avro`: Apache Avro
- `thrift`: Apache Thrift
- `msgpack`: MessagePack
- `custom_binary`: Custom binary format

## Type System

### Type Kinds

Classification of type expressions.

- `primitive`: Primitive type
- `generic`: Generic/parameterized type
- `union`: Union type
- `intersection`: Intersection type
- `alias`: Type alias
- `pointer`: Pointer type
- `reference`: Reference type
- `array_of`: Array type
- `function_type`: Function type
- `tuple_type`: Tuple type
- `optional_type`: Optional/nullable type
- `constrained`: Constrained type
- `opaque`: Opaque type

## Error Handling

### Error Handling Strategies

Language-level error handling paradigms.

- `exception_based`: Exception-based error handling
- `return_value_based`: Return value-based error handling (Go, Rust Result)
- `condition_based`: Condition-based error handling (Common Lisp)
- `error_code_based`: Error code-based error handling (C, COBOL)
- `panic_recover`: Panic and recover error handling (Go)
- `monadic`: Monadic error handling (Haskell Either/Maybe)

### Exception Checkedness

Whether exceptions must be declared/caught.

- `checked`: Checked exception (Java checked)
- `unchecked`: Unchecked exception
- `not_applicable`: Not applicable

## File Operations

### File Organization

How records are organized.

- `sequential`: Sequential organization
- `indexed`: Indexed organization
- `relative`: Relative organization
- `vsam_ksds`: VSAM Key-Sequenced Data Set
- `vsam_esds`: VSAM Entry-Sequenced Data Set
- `vsam_rrds`: VSAM Relative Record Data Set
- `partitioned_dataset`: Partitioned dataset (PDS/PDSE)
- `generation_data_group`: Generation data group (GDG)
- `line_sequential`: Line-sequential organization
- `heap`: Heap organization

### File Access Modes

How records are accessed.

- `sequential_access`: Sequential access
- `random_access`: Random access
- `dynamic_access`: Dynamic access

### Record Formats

Physical record format.

- `fixed`: Fixed-length records
- `variable`: Variable-length records
- `undefined`: Undefined-length records
- `spanned`: Spanned records
- `stream`: Stream format

### File Operation Types

File I/O operations.

- `read`: Read operation
- `write`: Write operation
- `rewrite`: Rewrite/update operation
- `delete`: Delete operation
- `start`: Start/position operation
- `open`: Open operation
- `close`: Close operation
- `sort`: Sort operation
- `merge`: Merge operation

## Screen and Terminal

### Screen Types

Terminal/screen types.

- `bms_map`: CICS BMS map
- `rpg_display_file`: RPG display file
- `character_terminal`: Character-mode terminal
- `tui`: Text-based user interface
- `form_based`: Form-based screen

## Batch Processing

### Job Step Types

Batch job step types.

- `exec_program`: Execute program step
- `exec_proc`: Execute procedure step
- `utility`: Utility step
- `sort`: Sort step
- `file_transfer`: File transfer step
- `conditional`: Conditional step

### Dataset Dispositions

JCL dataset dispositions.

- `new_dataset`: New dataset
- `old_dataset`: Old dataset (exclusive)
- `shared`: Shared dataset
- `modify`: Modify existing dataset
- `catalog`: Catalog dataset
- `delete_disp`: Delete dataset
- `pass`: Pass dataset to next step

## Inter-Process Communication

### IPC Mechanisms

IPC mechanisms.

- `cics_link`: CICS LINK command
- `cics_xctl`: CICS XCTL (transfer control)
- `ims_schedule`: IMS schedule call
- `shared_memory`: Shared memory
- `pipe`: Pipe
- `rmi`: Java Remote Method Invocation
- `corba`: CORBA invocation
- `database_mediated`: Database-mediated communication
- `message_queue`: Message queue
- `socket`: Socket communication
- `named_pipe`: Named pipe
- `signal`: Signal
- `semaphore`: Semaphore
- `dcom`: Distributed COM
- `rest_call`: REST API call
- `grpc_call`: gRPC inter-process call
- `event_bus`: Event bus communication

## Metaprogramming

### Metaprogramming Types

Preprocessor/metaprogramming mechanisms.

- `c_preprocessor`: C preprocessor macros
- `rust_macro_declarative`: Rust declarative macros
- `rust_macro_procedural`: Rust procedural macros
- `cobol_copy_replacing`: COBOL COPY REPLACING
- `template_metaprogramming`: Template metaprogramming (C++)
- `python_metaclass`: Python metaclass
- `lisp_macro`: Lisp macro
- `java_annotation_processor`: Java annotation processor
- `code_generator`: Code generator

## Memory and Ownership

### Ownership Models

Memory ownership models.

- `owned`: Owned value
- `borrowed_shared`: Shared/immutable borrow
- `borrowed_mutable`: Mutable borrow
- `moved`: Moved value
- `copied`: Copied value
- `reference_counted`: Reference-counted
- `garbage_collected`: Garbage-collected
- `manual`: Manual memory management
- `stack_allocated`: Stack-allocated

### Lifetime Scopes

Value lifetime scopes.

- `static_lifetime`: Static lifetime
- `function_scope`: Function scope
- `block_scope`: Block scope
- `named_lifetime`: Named lifetime (Rust 'a)
- `heap_lifetime`: Heap lifetime

## Database Constraints and Indexes

### Database Constraint Types

Database constraints.

- `primary_key`: Primary key constraint
- `foreign_key`: Foreign key constraint
- `unique`: Unique constraint
- `check`: Check constraint
- `not_null`: NOT NULL constraint

### Index Types

Database index types.

- `btree`: B-tree index
- `hash`: Hash index
- `gin`: PostgreSQL GIN index
- `fulltext`: Full-text index

## Programming Paradigms

### Programming Paradigm Types

Programming paradigms.

- `object_oriented`: Object-oriented programming
- `procedural`: Procedural programming
- `functional`: Functional programming
- `logic`: Logic programming
- `concatenative`: Concatenative programming
- `data_driven`: Data-driven programming
- `multi_paradigm`: Multi-paradigm programming
