# Systems Abstraction Ontology (SAO)

A comprehensive, language-agnostic ontology for modeling software systems — from individual lines of code to business capabilities, from COBOL copybooks to Kubernetes deployments.

SAO describes software systems—their structure, behavior, domain concepts, and
operating context—including libraries, services, batch programs, and applications.

* **Version**: 2.1.0
* **Author**: Charath Ranganathan
* **License**: [Apache License 2.0](LICENSE)
* **Schema**: LinkML (YAML), with a generated [RDFS Turtle vocabulary](sao.ttl)

147 classes · 102 enums · 970 attributes · 214 bidirectional relationships

## Key Features

- **Comprehensive Coverage**: Models all aspects of software systems
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

### Local setup and validation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run
these commands from the repository root. `uv sync` installs Python 3.13 if needed
and the LinkML toolchain pinned in `uv.lock`.

```bash
uv sync --locked
uv run linkml-lint --validate-only sao.yml
uv run python scripts/check_schema.py
uv run gen-json-schema sao.yml > /tmp/sao.schema.json
uv run linkml-validate --exit-on-first-failure -s sao.yml -C System examples/system.yaml
uv run linkml-validate --exit-on-first-failure -s sao.yml -C Aggregate examples/aggregate.yaml
uv run linkml-validate --exit-on-first-failure -s sao.yml -C Integration examples/integration.yaml
```

This repository contains an ontology and documentation; it does not include a
codebase extractor or a deployed application. The [extraction playbook](docs/extraction/00-overview.md)
describes how to populate the ontology. Multi-class snippets in the guides are
conceptual illustrations; validate an individual instance with an explicit
`-C` target class as shown above.

For RDFS consumers, use [`sao.ttl`](sao.ttl), or load the topic files listed in
[`rdf/manifest.json`](rdf/manifest.json) into one graph. Regenerate both forms with
`uv run python scripts/export_rdfs.py`; see [export semantics and limits](docs/rdfs-export.md).

Other LinkML generators include `gen-pydantic`, `gen-typescript`, and `gen-graphql`.

## Schema layout

`sao.yml` is the entry point for the complete ontology. It imports the topic
modules in [schema/](schema/); continue passing `sao.yml` to validators and
generators. Each definition has one home. Enums used in one topic live with
that topic; shared enums, types, base classes, and global slots live in
[schema/common.yaml](schema/common.yaml). Cross-topic references are resolved
through the entry point, so the topic files are not standalone schemas.

The split preserves the public `sao` term namespace. Each module has its own
schema ID under `https://ontologies.corestory.ai/sao/schema/`, used by LinkML
for definition provenance; these IDs do not change class or property IRIs.

Generate the full Markdown reference, including imported definitions, with:

```bash
uv run gen-doc --render-imports --directory /tmp/sao-reference sao.yml
```

`--render-imports` also includes the standard LinkML types. Without this flag,
the documentation generator omits definitions in the topic modules.

## Examples

The files under [examples/](examples/) are standalone instances checked against
the schema. Reference relationships use entity IDs; relationships declared with
`inlined_as_list: true` embed objects. See the examples for both representations.

### Simple E-Commerce System

```yaml
id: ecommerce-platform
name: E-Commerce Platform
contains_bounded_contexts:
  - id: catalog-context
    name: Catalog Context
  - id: order-context
    name: Order Context
  - id: customer-context
    name: Customer Context
  - id: payment-context
    name: Payment Context
```

### Order Aggregate

```yaml
id: order-aggregate
name: Order
has_root_entity: order
aggregates_entities:
  - id: order
    name: Order
  - id: order-line-item
    name: Order Line Item
has_value_objects:
  - money
  - address
```

### Integration with External Service

```yaml
id: stripe-integration
name: Stripe Integration
integration_type: bidirectional
protocol: https
integrates_with_system: stripe-payment-gateway
uses_adapter: stripe-adapter
protected_by_breaker: payment-circuit-breaker
integration_governed_by_contract: stripe-api-contract
```

### Schema namespace

The schema ID and `sao` term prefix are both `https://ontologies.corestory.ai/sao/`.
For example, the **System** class IRI is `https://ontologies.corestory.ai/sao/System`.
Applications using the earlier `ontology.example.org` or `https://sao.corestory.ai/`
namespaces should migrate their schema references and term IRIs. The
documentation site will be rendered to the `site` branch and published through
CoreStory's CDN.

## Technical Details

- **Modeling Language**: [LinkML](https://linkml.io/) (Linked Data Modeling Language)
- **Semantic Web**: RDF/RDFS compatible, SKOS concept schemes, Dublin Core metadata, Schema.org alignment
- **Global Slots**: ~20 multi-domain relationship slots; all single-use relationships inlined as class attributes
- **Extensibility**: Subclass existing classes, add mixins, define custom enumerations, or add new relationship slots

## Version History

### Version 2.1.0 (Current)
- Relationship attributes standardized to verb-prefixed names
- Duplicate relationship attributes removed and ML training inverse corrected
- See [CHANGELOG.md](CHANGELOG.md) for the complete migration guide

### Version 2.0.0
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

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, validation, and submission guidance. Areas of interest: additional compliance framework mappings, domain-specific extensions, example implementations, documentation improvements, validation rules, and code generators.

## License

Copyright (c) 2025 CoreStory, Inc.

The schema, documentation, and examples in this repository are licensed under
[Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.
Third-party tools and dependencies retain their respective licenses.

## References

- [LinkML](https://linkml.io/) — Linked Data Modeling Language
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) — Eric Evans
- [Microservices Patterns](https://microservices.io/patterns/) — Chris Richardson
- [GDPR](https://gdpr.eu/) | [HIPAA](https://www.hhs.gov/hipaa/) | [SOC 2](https://www.aicpa.org/soc) | [PCI-DSS](https://www.pcisecuritystandards.org/) | [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

## Citation

```
Systems Abstraction Ontology (SAO)
Version 2.1.0
Copyright (c) 2025 CoreStory, Inc.
Licensed under the Apache License, Version 2.0.
```

---

**Last Updated**: 2026-10-02
**Schema Version**: 2.1.0
