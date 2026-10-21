# Section 7: Integration

This section defines integration with external systems, including adapters, circuit breakers, messages, and contracts.

> **v2.0 Note**: In SAO v2.0.0, many cross-entity relationships are now inlined directly on the owning class rather than declared as standalone slot references. Classes such as `Contract` gain back-reference attributes that make navigating the ontology more explicit. Additionally, `ContractVersion` has been restructured from subclass inheritance to composition (it is now `is_a: NamedEntity` with an explicit reference attribute back to its parent `Contract`).

## Overview

The Integration section provides comprehensive modeling of connections to external systems, communication protocols, message formats, and API contracts.

## Core Concepts

### ExternalSystem

**Definition**: A system outside this system's boundary.

**Key Attributes**:
- **system_type**: `third_party_service`, `partner_system`, `legacy_system`, `saas_application`
- **owner**: System owner or vendor
- **sla**: Service level agreement
- **documentation_url**: API documentation URL

**Relationships**:
- **integrated_via**: `Integration[]` (inlined) connecting to this system

**External System Types**:
- `third_party_service`: External SaaS or API service (Stripe, SendGrid, Twilio)
- `partner_system`: Business partner's system
- `legacy_system`: Existing legacy system being integrated
- `saas_application`: Software-as-a-Service application

---

### Integration

**Definition**: A configured connection to an external system.

**Key Attributes**:
- **integration_type**: `inbound` (receiving data), `outbound` (sending data), `bidirectional`
- **protocol**: Communication protocol (HTTP, GRPC, KAFKA, etc.)
- **messages**: List of messages exchanged

**Relationships**:
- **integrates_with_system**: Target `ExternalSystem`
- **uses_adapter**: `Adapter` for protocol translation
- **protected_by_breaker**: `CircuitBreaker` for resilience
- **integration_governed_by_contract**: `Contract` defining API
- **belongs_to_system**: Parent `System`

**Integration Types**:
- `inbound`: Receive data from external system (webhooks, API calls)
- `outbound`: Send data to external system (API calls, events)
- `bidirectional`: Two-way communication

**Integration Patterns**:
- **Request-Response**: Synchronous API calls
- **Event-Driven**: Asynchronous event publishing/subscribing
- **Batch**: Periodic bulk data exchange
- **Streaming**: Continuous data streams

---

### Message

**Definition**: A unit of data exchanged in integration.

**Key Attributes**:
- **message_type**: `request`, `response`, `notification`, `command`, `event`, `query`

**Relationships**:
- **message_structured_by_schema**: `Schema` defining message structure
- **validated_by_contract**: `Contract` validating message

**Message Types**:
- `request`: Request message expecting a response
- `response`: Response to a request
- `notification`: One-way notification (no response expected)
- `command`: Command for action execution
- `event`: Event notification
- `query`: Query for data retrieval

**Message Patterns**:
- **Envelope Pattern**: Wrap payload in standard envelope (headers, metadata)
- **Claim Check**: Store large payload separately, pass reference
- **Canonical Data Model**: Transform all messages to canonical format
- **Message Transformation**: Convert between formats

---

### Contract

**Definition**: A formal specification of integration behavior.

**Key Attributes**:
- Implements `Versionable` mixin
- **contract_type**: `openapi`, `asyncapi`, `json_schema`, `protobuf`, `avro`, `graphql_schema`, `wsdl`
- **definition**: Contract definition
- **contract_versions**: List of contract versions

**Relationships**:
- **defines_interfaces**: `Interface` entities defined
- **governs_integrations**: `Integration` entities governed
- **validates_messages**: `Message` entities validated
- **implemented_by_units**: `EncapsulationUnit` entities implementing this contract
- **contract_versions**: `ContractVersion[]` (v2.0 back-reference from `ContractVersion.version_of_contract`)

**Contract Types**:
- `openapi`: REST API specification (Swagger)
- `asyncapi`: Async API specification (events, messages)
- `json_schema`: JSON data structure schema
- `protobuf`: Protocol Buffers schema
- `avro`: Apache Avro schema
- `graphql_schema`: GraphQL type system
- `wsdl`: SOAP web service description

**Contract-First vs Code-First**:
- **Contract-First**: Define contract, generate code
- **Code-First**: Write code, generate contract
- **Best Practice**: Contract-first for external APIs

---

### ContractVersion

**Definition**: A specific iteration of a contract.

> **v2.0 Change**: `ContractVersion` is now `is_a: NamedEntity` (previously `is_a: Contract`). Instead of inheriting from `Contract`, it uses the `version_of_contract` attribute to reference its parent `Contract`.

**Key Attributes**:
- **version**: Semantic version number
- **definition**: Contract at this version
- **breaking_changes**: List of breaking changes from previous version

**Relationships**:
- **version_of_contract**: `Contract` that this version belongs to

**API Versioning Strategies**:
- **URL Versioning**: `/api/v1/users`, `/api/v2/users`
- **Header Versioning**: `Accept: application/vnd.api+json;version=1`
- **Query Parameter**: `/api/users?version=1`
- **Content Negotiation**: `Accept: application/vnd.api.v1+json`

**Breaking vs Non-Breaking Changes**:
- **Breaking**: Remove field, change type, rename field
- **Non-Breaking**: Add optional field, add new endpoint

---

### Adapter

**Definition**: A component that translates between system and external protocols.

**Key Attributes**:
- Inherits from `Component`
- **source_protocol**: Protocol to translate from
- **target_protocol**: Protocol to translate to
- **transformation**: Data transformation logic

**Relationships**:
- **used_by_integrations**: `Integration` entities using this adapter

**Adapter Pattern Uses**:
- Protocol translation (HTTP -> GRPC)
- Data format conversion (XML -> JSON)
- Message routing
- API versioning support
- Anti-corruption layer (DDD pattern)

**Example Adapters**:
- REST to SOAP adapter
- JSON to XML converter
- Legacy system adapter
- Third-party API wrapper

---

### CircuitBreaker

**Definition**: A resilience pattern preventing cascade failures.

**Key Attributes**:
- **failure_threshold**: Number of failures before opening circuit
- **reset_timeout_seconds**: Seconds before attempting half-open
- **half_open_requests**: Requests allowed in half-open state

**Relationships**:
- **protects_integrations**: `Integration` entities protected

**Circuit Breaker States**:
1. **Closed**: Normal operation, requests pass through
2. **Open**: Too many failures, requests fail immediately
3. **Half-Open**: Testing if external system recovered

**State Transitions**:
- **Closed -> Open**: Failure threshold reached
- **Open -> Half-Open**: Reset timeout elapsed
- **Half-Open -> Closed**: Test requests succeed
- **Half-Open -> Open**: Test requests fail

**Benefits**:
- Prevent cascade failures
- Fail fast
- Give external system time to recover
- Reduce load on failing systems

---

## Integration Patterns

### API Gateway Pattern
Single entry point for all client requests:
- Routing to backend services
- Authentication and authorization
- Rate limiting
- Request/response transformation
- Circuit breaking

### Backend for Frontend (BFF)
Separate backend for each frontend:
- Optimized for specific client needs
- Reduces over-fetching
- Simplifies mobile/web differences

### Event-Driven Integration
Asynchronous communication via events:
- Loose coupling
- Scalability
- Eventual consistency
- Event sourcing support

### Saga Pattern
Distributed transactions across services:
- Choreography: Services coordinate via events
- Orchestration: Central coordinator
- Compensating transactions for rollback

### Anti-Corruption Layer (ACL)
Translation layer protecting domain model:
- Isolates from external model changes
- Domain integrity preservation
- Adapter pattern implementation

---

## Communication Protocols

### HTTP/HTTPS
- **Use Case**: REST APIs, webhooks
- **Pros**: Universal, firewall-friendly, well-understood
- **Cons**: Overhead, connection per request

### WebSocket
- **Use Case**: Real-time bidirectional communication
- **Pros**: Full-duplex, low latency
- **Cons**: Requires persistent connection

### gRPC
- **Use Case**: High-performance inter-service communication
- **Pros**: Fast, efficient, strongly typed
- **Cons**: Limited browser support, complexity

### AMQP (Advanced Message Queuing Protocol)
- **Use Case**: Enterprise messaging (RabbitMQ)
- **Pros**: Reliable, transaction support
- **Cons**: Complexity, setup overhead

### MQTT
- **Use Case**: IoT, lightweight messaging
- **Pros**: Lightweight, pub-sub
- **Cons**: Limited features

### Kafka Protocol
- **Use Case**: Event streaming, log aggregation
- **Pros**: High throughput, durability
- **Cons**: Operational complexity

---

## Best Practices

### Integration Design
1. **Loose Coupling**: Minimize dependencies between systems
2. **Asynchronous**: Use async communication when possible
3. **Idempotency**: Make operations idempotent
4. **Retry Logic**: Implement exponential backoff
5. **Circuit Breaking**: Protect against failures

### Contract Management
1. **Versioning**: Version all contracts
2. **Backward Compatibility**: Maintain compatibility when possible
3. **Breaking Changes**: Communicate and plan breaking changes
4. **Documentation**: Keep API documentation up to date
5. **Testing**: Contract testing (Pact, Spring Cloud Contract)

### Error Handling
1. **Graceful Degradation**: Degrade functionality, don't crash
2. **Timeouts**: Set appropriate timeouts
3. **Fallbacks**: Provide fallback responses
4. **Monitoring**: Monitor integration health
5. **Alerting**: Alert on integration failures

### Security
1. **Authentication**: Use API keys, OAuth, mutual TLS
2. **Authorization**: Validate permissions
3. **Encryption**: Use TLS for data in transit
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Validate all external input

### Performance
1. **Caching**: Cache responses when appropriate
2. **Connection Pooling**: Reuse connections
3. **Compression**: Compress large payloads
4. **Pagination**: Paginate large result sets
5. **Async Processing**: Use async for long operations

---

## Relationships with Other Sections

- **Section 1 (Structural Foundation)**: Systems have integrations
- **Section 5 (Behavior)**: Integration events trigger workflows
- **Section 6 (Data Management)**: Messages structured by schemas
- **Section 8 (Deployment)**: Services expose integration endpoints
- **Section 9 (Observability)**: Integration metrics and logs

---

## Example: Payment Gateway Integration

```
ExternalSystem: StripePaymentGateway
  Type: third_party_service
  Owner: Stripe, Inc.
  SLA: 99.99% uptime
  Documentation: https://stripe.com/docs/api

Integration: PaymentProcessingIntegration
  Type: bidirectional
  Protocol: HTTPS

  Adapter: StripeAdapter
    Source: Internal payment model
    Target: Stripe API format
    Transformation:
      - Map internal currency codes to ISO 4217
      - Convert amounts to cents
      - Transform payment methods

  Circuit Breaker:
    Failure Threshold: 5
    Reset Timeout: 60 seconds
    Half-Open Requests: 3

  Messages:
    - CreatePaymentRequest (command)
      Schema: PaymentRequestSchema v1.0
      Fields: amount, currency, payment_method, metadata

    - PaymentSucceededEvent (event)
      Schema: PaymentEventSchema v1.0
      Fields: payment_id, status, amount, timestamp

    - RefundPaymentRequest (command)
    - PaymentFailedEvent (event)

  Contract: StripeAPIContract
    Type: openapi
    Version: 2023-10-16
    Definition: OpenAPI 3.0 specification

  Error Handling:
    - Network Errors: Retry with exponential backoff (max 3 attempts)
    - 4xx Errors: Log and return error to caller
    - 5xx Errors: Trigger circuit breaker
    - Timeout: 10 seconds

  Monitoring:
    - Success rate metric
    - Latency percentiles (p50, p95, p99)
    - Error rate by type
    - Circuit breaker state changes
```
