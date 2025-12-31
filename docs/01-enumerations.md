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

- **CORE**: Core essential feature
- **OPTIONAL**: Optional add-on feature
- **EXPERIMENTAL**: Experimental or beta feature
- **DEPRECATED**: Deprecated feature scheduled for removal
