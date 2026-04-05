# Software Application Ontology (SAO)

A comprehensive, language-agnostic ontology for modeling software applications — from individual lines of code to business capabilities, from COBOL copybooks to Kubernetes deployments.

* **Version**: 2.0.0
* **Author**: Charath Ranganathan
* **License**: Proprietary - Copyright (c) 2025 CoreStory, Inc.
* **Schema**: LinkML (YAML)

147 classes · 102 enums · 970 attributes · 214 bidirectional relationships

## Key Features

- **Comprehensive Coverage**: Models all aspects of modern software applications
- **DDD-Aligned**: Built on Domain-Driven Design principles (Aggregates, Bounded Contexts, Ubiquitous Language)
- **Cloud-Native**: Supports microservices, containers, serverless, and cloud deployment
- **Compliance-Ready**: Includes models for GDPR, HIPAA, SOC2, PCI-DSS, ISO 27001, and more
- **Legacy-Ready**: First-class support for COBOL, RPG, PL/I, Assembler, JCL, CICS, IMS alongside modern languages
- **Interoperable**: Based on LinkML standard with RDF/RDFS, SKOS, and Dublin Core alignment
- **Extensible**: Designed for subclassing, mixins, custom enumerations, and additional relationships

## Documentation

**Start here:** [The SAO Guide](docs/guide.md) — a layered walkthrough of all 147 classes organized by abstraction level, from code structure to business intent.

### Section deep dives

| Doc | Topic | Key classes |
|---|---|---|
| [01 Enumerations](docs/01-enumerations.md) | All enum types | 102 enums with 804 permissible values |
| [02 Structural Foundation](docs/02-structural-foundation.md) | Architecture | System, BoundedContext, Module, Component, Service, Interface |
| [03 Actors and Identity](docs/03-actors-and-identity.md) | Identity | Actor, Identity, Credential, Tenant, Organization |
| [04 Authorization and Policy](docs/04-authorization-and-policy.md) | Access control | Role, Permission, Policy, Scope, Constraint |
| [05 Domain Modeling](docs/05-domain-modeling.md) | DDD | Aggregate, DomainEntity, ValueObject, Attribute, Lifecycle |
| [06 Behavior and Workflow](docs/06-behavior-and-workflow.md) | Behavior | Action, Operation, Workflow, Rule, Event, Transaction |
| [07 Data Management](docs/07-data-management.md) | Persistence | DataStore, Collection, Schema, DataClassification, RetentionPolicy |
| [08 Integration](docs/08-integration.md) | External systems | ExternalSystem, Integration, Contract, Adapter, CircuitBreaker |
| [09 Deployment and Operations](docs/09-deployment-and-operations.md) | Runtime | Environment, Deployment, Configuration, Infrastructure, Release |
| [10 Observability](docs/10-observability.md) | Monitoring | Metric, Log, Trace, Alert, Incident, HealthCheck |
| [11 Governance and Compliance](docs/11-governance-and-compliance.md) | Compliance | ComplianceRequirement, Control, Evidence, RiskAssessment |
| [12 Code Structure](docs/12-code-structure.md) | Code modeling | CodeContainer, EncapsulationUnit, CallableUnit, DataStructure |
| [13 Extended Modeling](docs/13-extended-modeling.md) | Sections 18–28 | TypeExpression, ErrorModel, FileDefinition, JobDefinition, IPC, etc. |

### Other resources

- [C4 Model Mapping](docs/c4/) — SAO classes mapped to C4 architecture layers ([Layer 1](docs/c4/layer-1.md), [Layer 2](docs/c4/layer-2.md), [Layer 3](docs/c4/layer-3.md), [Layer 4](docs/c4/layer-4.md))
- [Whitepaper](docs/whitepaper.md) — "Beyond Grep and Vector Search: The Case for Ontology-driven Extraction of Software Requirements"

## Getting Started

1. Read the [SAO Guide](docs/guide.md) for a conceptual overview
2. Define your **System** and **BoundedContexts**
3. Identify **Modules** and **Components**
4. Map domain **Aggregates** and **Entities**
5. Document **Integrations**, **Authorization**, and **Compliance** metadata

Use LinkML tools to generate artifacts from the schema:
- `linkml-validate` — validate YAML instances
- `gen-pydantic` / `gen-typescript` — generate typed models
- `gen-json-schema` — generate JSON Schema for validation
- `gen-graphql` — generate GraphQL schema

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
  integration_type: bidirectional
  protocol: https
  integrates_with_system: Stripe Payment Gateway
  uses_adapter: Stripe Adapter
  protected_by_breaker: Payment Circuit Breaker
  integration_governed_by_contract: Stripe API Contract v2023
```

## Technical Details

- **Modeling Language**: [LinkML](https://linkml.io/) (Linked Data Modeling Language)
- **Semantic Web**: RDF/RDFS compatible, SKOS concept schemes, Dublin Core metadata, Schema.org alignment
- **Global Slots**: ~20 multi-domain relationship slots; all single-use relationships inlined as class attributes
- **Extensibility**: Subclass existing classes, add mixins, define custom enumerations, or add new relationship slots

## Version History

### Version 2.0.0 (Current)
- Structural refactor: ~340 single-use global slots inlined as class attributes
- 18 new classes spanning type system, error handling, file I/O, screen definitions, job control, IPC, preprocessor, memory model, domain relationships, database schema, and programming language
- 17 new enums for type kinds, error strategies, file organization, screen types, job steps, IPC mechanisms, ownership models, and more
- 8 existing enums extended with legacy platform values (RPG, PL/I, Assembler, VSAM, JCL)
- Programming Language as first-class entity replacing bare string fields

### Version 1.0.0
- Initial comprehensive ontology release with 12 major sections
- Paradigm-agnostic code structure modeling supporting modern and legacy systems

### Roadmap
- **v2.1**: Enhanced event sourcing patterns
- **v2.2**: Service mesh and API gateway extensions

## Contributing

We welcome contributions! Areas of interest: additional compliance framework mappings, domain-specific extensions, example implementations, documentation improvements, validation rules, and code generators.

## License

Proprietary and Confidential - Copyright (c) 2025 CoreStory, Inc. All rights reserved.

See LICENSE file for complete terms.

## References

- [LinkML](https://linkml.io/) — Linked Data Modeling Language
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) — Eric Evans
- [Microservices Patterns](https://microservices.io/patterns/) — Chris Richardson
- [GDPR](https://gdpr.eu/) | [HIPAA](https://www.hhs.gov/hipaa/) | [SOC 2](https://www.aicpa.org/soc) | [PCI-DSS](https://www.pcisecuritystandards.org/) | [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

## Citation

```
Software Application Ontology (SAO)
Version 2.0.0
Copyright (c) 2025 CoreStory, Inc. All rights reserved.
```

---

**Last Updated**: 2026-04-04
**Schema Version**: 2.0.0
