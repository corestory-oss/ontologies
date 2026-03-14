# Software Application Ontology (SAO)

## Overview

The Software Application Ontology (SAO) is a comprehensive ontology for modeling software applications.

The ontology is described in LinkML.

* **Version**: 2.0.0
* **License**: Proprietary - Copyright (c) 2025 CoreStory, Inc.
* **Schema ID**: https://ontology.example.org/software-application

## Purpose

SAO provides a structured vocabulary and semantic model for describing:
- Software system architecture and structure
- Domain-driven design concepts
- Security and authorization models
- Integration patterns and external system connections
- Deployment and operational concerns
- Observability and monitoring
- Compliance and governance requirements

## Key Features

- **Comprehensive Coverage**: Models all aspects of modern software applications
- **DDD-Aligned**: Built on Domain-Driven Design principles
- **Cloud-Native**: Supports microservices, containers, and cloud deployment
- **Compliance-Ready**: Includes models for GDPR, HIPAA, SOC2, PCI-DSS, and more
- **Interoperable**: Based on LinkML standard for semantic modeling
- **Extensible**: Designed for extension and customization
- **Legacy-Ready**: First-class support for COBOL, RPG, PL/I, Assembler, JCL, CICS, IMS alongside modern languages

## Documentation Structure

The ontology is organized into 28 major sections:

### [01. Enumerations](docs/01-enumerations.md)
Defines all enumeration types used throughout the ontology, including:
- Interface types (UI, API, Event)
- Service and dependency types
- Actor types (human and system)
- Security credentials and policies
- Data classifications
- Deployment and infrastructure types
- Compliance frameworks

### [02. Structural Foundation](docs/02-structural-foundation.md)
Core architectural elements:
- **System**: Top-level container for applications
- **BoundedContext**: Domain boundaries (DDD)
- **Module**: Deployable units of functionality
- **Component**: Logical building blocks
- **Service**: Runtime deployable units
- **Interface**: User, programmatic, and event interfaces
- **Capability** and **Feature**: Business and user-facing functionality

### [03. Actors and Identity](docs/03-actors-and-identity.md)
Identity and access management:
- **Actor**: Human and system actors
- **Identity**: Authenticated representations
- **Credential**: Authentication mechanisms
- **Tenant**: Multi-tenancy support
- **Organization**: Hierarchical organizational structures

### [04. Authorization and Policy](docs/04-authorization-and-policy.md)
Access control and security:
- **Role**: Collections of permissions
- **Permission**: Atomic access grants
- **Policy**: Rule sets for access decisions (RBAC, ABAC, REBAC, PBAC)
- **Scope**: Permission boundaries
- **Constraint**: Contextual access restrictions

### [05. Domain Modeling](docs/05-domain-modeling.md)
Domain-driven design concepts:
- **Aggregate**: Transactional consistency boundaries
- **DomainEntity**: Identifiable domain objects
- **ValueObject**: Immutable value types
- **Attribute**: Entity properties with classifications
- **State** and **Transition**: Lifecycle management
- **Resource**: External API representations

### [06. Behavior and Workflow](docs/06-behavior-and-workflow.md)
System behavior and processes:
- **Action**: Queries and commands
- **Operation**: Invocable units of behavior
- **Workflow**: Multi-step business processes (Saga, Choreography, Orchestration)
- **Rule**: Validation, business logic, and constraints
- **Event**: Domain, integration, system, and audit events
- **Transaction**: ACID and distributed transactions

### [07. Data Management](docs/07-data-management.md)
Data persistence and governance:
- **DataStore**: Various database types (SQL, NoSQL, cache, etc.)
- **Collection** and **Record**: Data organization
- **Schema**: Versioned data structures
- **DataClassification**: Sensitivity levels (PII, PHI, PCI)
- **RetentionPolicy**: Data lifecycle management
- **DataLineage**: Provenance tracking
- **AuditLog**: Tamper-evident audit trails

### [08. Integration](docs/08-integration.md)
External system connectivity:
- **ExternalSystem**: Third-party and legacy systems
- **Integration**: Configured connections (inbound, outbound, bidirectional)
- **Message**: Data exchange units
- **Contract**: API specifications (OpenAPI, AsyncAPI, gRPC, etc.)
- **Adapter**: Protocol and format translation
- **CircuitBreaker**: Resilience patterns

### [09. Deployment and Operations](docs/09-deployment-and-operations.md)
Runtime and deployment:
- **Environment**: Dev, test, staging, production
- **Deployment**: Service instances with configurations
- **DeploymentUnit**: Containers, VMs, functions, binaries
- **Configuration**: Runtime parameters and secrets
- **Infrastructure**: Compute, storage, network resources
- **Release**: Versioned deployment packages

### [10. Observability](docs/10-observability.md)
Monitoring and troubleshooting:
- **Metric**: Time-series measurements (counters, gauges, histograms)
- **Log**: Timestamped event records
- **Trace** and **Span**: Distributed request tracing
- **Alert** and **AlertRule**: Threshold-based notifications
- **Incident**: Tracked outages and degradations
- **HealthCheck**: Service availability probes

### [11. Governance and Compliance](docs/11-governance-and-compliance.md)
Regulatory compliance and risk:
- **ComplianceRequirement**: Regulatory obligations (GDPR, HIPAA, SOC2, etc.)
- **Control**: Security and compliance measures
- **Evidence**: Proof of control effectiveness
- **RiskAssessment**: Threat and vulnerability analysis

### [12. Code Structure](docs/12-code-structure.md)
Implementation-level code modeling with paradigm-agnostic design:
- **CodeContainer**: Physical code storage (files, library members, scripts)
- **StorageLocation**: Directory structures and libraries
- **EncapsulationUnit**: Logical code boundaries (classes, programs, modules) - supports OOP, procedural, functional, and mainframe paradigms
- **CallableUnit**: Invocable code (methods, functions, paragraphs, procedures)
- **DataStructure**: Data organization (classes, records, structs, group items)
- **DataElement**: Fields, properties, and variables
- **ControlFlow** and **DataFlow**: Code execution and data movement
- **Maps to Architecture**: Links code to Components, Operations, and Domain Entities

### [13-17. Extended Modeling](docs/13-extended-modeling.md)
New sections added in v2.0 for cross-cutting concerns:
- **Section 18 - Type System**: `TypeExpression` for recursive type modeling (generics, unions, pointers, function types)
- **Section 19 - Error Handling**: `ErrorModel` and `ExceptionType` for language-level error paradigms
- **Section 20 - File I/O**: `FileDefinition` and `FileOperation` for file-based I/O (COBOL SELECT, VSAM, etc.)
- **Section 21 - Screen/Terminal**: `ScreenDefinition` and `ScreenField` for character-mode UI modeling
- **Section 22 - Job Control**: `JobDefinition`, `JobStep`, `DatasetAllocation` for batch orchestration (JCL, schedulers)
- **Section 23 - IPC**: `IPCConnection` for inter-process communication (CICS LINK, shared memory, pipes)
- **Section 24 - Preprocessor**: `PreprocessorDirective` for macros and metaprogramming constructs
- **Section 25 - Memory/Ownership**: `MemoryModel` and `OwnershipAnnotation` for Rust-style ownership, GC models
- **Section 26 - Domain Relationships**: `DomainRelationship` connecting domain entities with cardinality
- **Section 27 - Database Schema**: `DatabaseConstraint` and `DatabaseIndex` for schema-level constraints
- **Section 28 - Programming Language**: `ProgrammingLanguage` as first-class entity with paradigms and type discipline

## Core Design Principles

### 1. Domain-Driven Design (DDD)
- Bounded contexts align with business domains
- Aggregates enforce transactional boundaries
- Ubiquitous language within contexts
- Context mapping for inter-context relationships

### 2. Separation of Concerns
- Clear boundaries between sections
- Minimal coupling, high cohesion
- Well-defined relationships between entities

### 3. Multi-Paradigm Support
- Monolithic and microservices architectures
- Various deployment models (containers, VMs, serverless)
- Multiple integration patterns (sync, async, event-driven)
- Flexible authorization models (RBAC, ABAC, REBAC)
- Legacy mainframe paradigms (COBOL, RPG, PL/I, Assembler)
- File-based I/O and batch job orchestration

### 4. Compliance by Design
- Built-in data classification
- Audit logging throughout
- Retention policy support
- Evidence collection for compliance

### 5. Cloud-Native and DevOps
- Environment-based configuration
- Infrastructure as code support
- CI/CD pipeline integration
- Observability as first-class concern

## Common Use Cases

### Enterprise Application Modeling
Model complex enterprise systems with:
- Multiple bounded contexts for different business domains
- Integration with legacy systems and third-party services
- Role-based access control with organizational hierarchies
- Compliance with multiple regulatory frameworks

### Microservices Architecture
Define microservices ecosystems with:
- Service dependencies and communication patterns
- Event-driven integration
- Distributed tracing and monitoring
- Service mesh and API gateway patterns

### SaaS Platform Design
Build multi-tenant SaaS applications with:
- Tenant isolation and organization hierarchies
- Feature flags and capability-based licensing
- Data classification and regional compliance
- Usage metrics and billing integration

### API Platform Documentation
Document API platforms with:
- OpenAPI/AsyncAPI contract management
- Version management and breaking change tracking
- Integration patterns and adapter implementations
- Rate limiting and circuit breaker configurations

### Compliance and Governance
Demonstrate compliance with:
- Mapping regulatory requirements to controls
- Evidence collection and audit trails
- Risk assessment and mitigation tracking
- Data retention and lineage tracking

## Technical Details

### Technology Stack
- **Modeling Language**: LinkML (Linked Data Modeling Language)
- **Schema Format**: YAML
- **Validation**: LinkML validation tools
- **Code Generation**: Support for Python, TypeScript, JSON Schema, RDF
- **Global Slots**: Only ~20 multi-domain and base identification slots remain global; all single-use relationships are inlined as class attributes

### Semantic Web Support
- RDF/RDFS compatible
- SKOS concept schemes for enumerations
- Dublin Core metadata terms
- Schema.org alignment where applicable

### Extensibility
The ontology can be extended through:
- **Specialization**: Subclass existing classes
- **Mixins**: Add cross-cutting concerns
- **Custom Enumerations**: Add domain-specific enums
- **Additional Relationships**: Define new slots
- **Annotations**: Add metadata to any element

## Getting Started

### 1. Review the Documentation
Start with the [Structural Foundation](docs/02-structural-foundation.md) to understand core concepts, then explore other sections based on your needs.

### 2. Understand the Domain
Familiarize yourself with:
- Domain-Driven Design concepts
- Your application's bounded contexts
- Current architecture and technology stack

### 3. Map Your System
Begin modeling by:
1. Defining your System and BoundedContexts
2. Identifying Modules and Components
3. Mapping domain Aggregates and Entities
4. Documenting Integrations
5. Defining Authorization model
6. Adding Observability and Compliance metadata

### 4. Generate Artifacts
Use LinkML tools to generate:
- JSON Schema for validation
- Python/TypeScript classes for applications
- RDF for semantic web integration
- Documentation sites

## Examples

### Simple E-Commerce System
```yaml
System:
  id: ecommerce-platform
  name: E-Commerce Platform
  contains_bounded_contexts:
    - Catalog Context
    - Order Context
    - Customer Context
    - Payment Context
```

### Bounded Context with Aggregate
```yaml
BoundedContext:
  id: order-context
  name: Order Management
  contains_aggregates:
    - Order Aggregate

Aggregate:
  id: order-aggregate
  name: Order
  has_root_entity: Order
  aggregates_entities:
    - OrderLineItem
  value_objects:
    - Money
    - Address
```

### Integration with External Service
```yaml
Integration:
  id: stripe-integration
  integration_type: BIDIRECTIONAL
  protocol: HTTPS
  integrates_with_system: Stripe Payment Gateway
  uses_adapter: Stripe Adapter
  protected_by_breaker: Payment Circuit Breaker
  integration_governed_by_contract: Stripe API Contract v2023
```

## Best Practices

### Modeling
1. **Start Top-Down**: Begin with System and BoundedContexts
2. **Identify Aggregates**: Define transactional boundaries early
3. **Use Ubiquitous Language**: Name entities using domain terminology
4. **Keep Aggregates Small**: Limit to what must be consistent
5. **Document Assumptions**: Use description fields extensively

### Integration
1. **Define Contracts First**: Specify APIs before implementation
2. **Version Everything**: Use semantic versioning
3. **Plan for Failure**: Include circuit breakers and retries
4. **Monitor Integrations**: Define metrics and alerts

### Security
1. **Classify Data**: Tag all data with appropriate classifications
2. **Least Privilege**: Grant minimal necessary permissions
3. **Audit Everything**: Enable comprehensive audit logging
4. **Regular Reviews**: Periodically review access and controls

### Compliance
1. **Map Requirements**: Link compliance requirements to controls
2. **Collect Evidence**: Automate evidence collection
3. **Document Risks**: Maintain risk register
4. **Plan Audits**: Prepare for audits continuously

## Tools and Resources

### LinkML Tools
- **linkml-validate**: Validate YAML instances against schema
- **gen-pydantic**: Generate Pydantic models
- **gen-typescript**: Generate TypeScript interfaces
- **gen-json-schema**: Generate JSON Schema
- **gen-graphql**: Generate GraphQL schema

### Visualization
- **linkml-viz**: Generate visual diagrams
- **OntoGraf**: Ontology visualization (Protégé plugin)

### Validation
- **Shape Expressions**: SHACL/ShEx for validation
- **JSON Schema**: Generated schemas for instance validation

## Versioning and Evolution

### Version 2.0.0 (Current)
- **Structural refactor**: ~340 single-use global slots inlined as class attributes for improved readability
- **18 new classes** spanning type system, error handling, file I/O, screen definitions, job control, IPC, preprocessor, memory model, domain relationships, database schema objects, and programming language
- **17 new enums** for type kinds, error strategies, file organization, screen types, job steps, IPC mechanisms, ownership models, and more
- **8 existing enums extended** with legacy platform values (RPG, PL/I, Assembler, VSAM, JCL)
- **6 inheritance fixes**: SchemaVersion, ContractVersion, LogEntry, AuditEntry, Span, Screen changed from parent inheritance to NamedEntity with containment
- **Orphaned Cardinality enum** wired to new DomainRelationship class
- **ChannelType enum** removed (Slack-specific, unused)
- **CallableCategory enum** cleaned to 3 behavioral-role values
- **6 deprecated attributes** with migration paths to typed replacements
- **Programming Language** as first-class entity replacing bare string fields

### Version 1.0.0 (Historical)
- Initial comprehensive ontology release
- All 12 major sections defined
- Support for common compliance frameworks
- Cloud-native and microservices patterns
- Paradigm-agnostic code structure modeling supporting modern (Java, Python, C#) and legacy (COBOL, mainframe) systems

### Future Roadmap
- **v2.1**: Enhanced event sourcing patterns
- **v2.2**: Service mesh and API gateway extensions

### Schema Evolution Guidelines
- Use semantic versioning
- Maintain backward compatibility in minor versions
- Deprecate before removing in major versions
- Provide migration guides for breaking changes

## Contributing

We welcome contributions! Areas of interest:
- Additional compliance framework mappings
- Domain-specific extensions
- Example implementations
- Documentation improvements
- Validation rules and constraints
- Code generators and tools

## Support and Community

- **Issues**: GitHub issue tracker
- **Discussions**: GitHub discussions
- **Documentation**: This documentation site
- **Examples**: See `/examples` directory

## License

Proprietary and Confidential - Copyright (c) 2025 CoreStory, Inc. All rights reserved.

This software is the proprietary and confidential information of CoreStory, Inc.
Unauthorized copying, distribution, or use is strictly prohibited.

See LICENSE file for complete terms.

## References

### Standards and Specifications
- [LinkML](https://linkml.io/) - Linked Data Modeling Language
- [RDF](https://www.w3.org/RDF/) - Resource Description Framework
- [SKOS](https://www.w3.org/2004/02/skos/) - Simple Knowledge Organization System
- [Dublin Core](https://www.dublincore.org/) - Metadata terms

### Design Principles
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) - Eric Evans
- [Microservices Patterns](https://microservices.io/patterns/) - Chris Richardson
- [12-Factor App](https://12factor.net/) - Heroku
- [Cloud Native Computing Foundation](https://www.cncf.io/)

### Compliance Frameworks
- [GDPR](https://gdpr.eu/) - General Data Protection Regulation
- [HIPAA](https://www.hhs.gov/hipaa/) - Health Insurance Portability and Accountability Act
- [SOC 2](https://www.aicpa.org/soc) - Service Organization Control 2
- [PCI-DSS](https://www.pcisecuritystandards.org/) - Payment Card Industry Data Security Standard
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html) - Information Security Management

## Citation

If you use this ontology in your research or projects, please cite:

```
Software Application Ontology (SAO)
Version 2.0.0
https://ontology.example.org/software-application
Copyright (c) 2025 CoreStory, Inc. All rights reserved.
```

---

**Last Updated**: 2026-03-14
**Schema Version**: 2.0.0
**Documentation Version**: 2.0.0
