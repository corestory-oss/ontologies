# SAO Extraction Playbook: Overview

This document series is a step-by-step playbook for decomposing any software codebase into SAO-conformant YAML. It covers modern cloud-native applications, legacy mainframe systems, and everything in between.

## How to use this series

**Audience.** These documents are written for both software engineers performing manual extraction and LLM agents (e.g., Claude Code) performing automated extraction. The term "extraction agent" refers to whoever or whatever is performing the work.

**Reading path.** Start here, then follow the phases in order. Each phase document is self-contained: it states its inputs, outputs, steps, and the SAO classes it populates. Once you are familiar with the overall flow, you can use individual phase documents as standalone references.

**Notation conventions.** This series follows the formatting conventions established in the SAO documentation:

- **Bold** for class and entity names in prose (e.g., **ControlFlow**, **DataStore**, **Actor**)
- `Monospace` for enum values, attribute names, and literal identifiers (e.g., `web_ui`, `rest_api`, `contained_in_unit`)
- `Dotted.path` references in monospace (e.g., `Component.implemented_by_code`)

**RFC 2119 keywords.** Throughout this series:

- **MUST** — required for a valid SAO instance
- **SHOULD** — strongly recommended; omission requires justification
- **MAY** — optional enrichment that adds value but is not required

---

## Prerequisites and inputs

Before starting extraction, gather the following:

### Required inputs

| Input | Purpose |
|---|---|
| Full source tree | Repository access (all branches relevant to the extraction scope) |
| Build manifests | `pom.xml`, `package.json`, `Cargo.toml`, `go.mod`, Makefile, JCL procs, etc. |
| Dependency lock files | `package-lock.json`, `Cargo.lock`, `poetry.lock`, etc. |

### Strongly recommended inputs

| Input | Purpose |
|---|---|
| Deployment manifests | Dockerfiles, Kubernetes YAML, docker-compose, serverless configs, JCL |
| API schemas | OpenAPI, GraphQL, gRPC `.proto`, WSDL |
| Database schemas | DDL scripts, migration files, ORM model definitions |
| Documentation | READMEs, wikis, ADRs, API docs, runbooks |
| CI/CD configs | GitHub Actions, Jenkinsfile, GitLab CI, Azure Pipelines |
| IaC definitions | Terraform, CloudFormation, Pulumi |

### Optional inputs (if available)

| Input | Purpose |
|---|---|
| Runtime telemetry | Logs, traces, APM data |
| Config files | `application.yml`, `.env`, feature flag configs |
| Test suites | Test files, coverage reports |

### Identification checklist

Before extraction begins, identify and record:

1. **Programming language(s)** present in the repository
2. **Build system** (Maven, Gradle, npm, Cargo, Make, etc.)
3. **Package manager** and dependency resolution mechanism
4. **Deployment model** (containers, VMs, mainframe LPAR, serverless, bare metal)
5. **External dependencies** visible from configuration (databases, message brokers, third-party APIs)
6. **Architectural style** if apparent (monolith, microservices, modular monolith, mainframe batch/online)

### Tools needed

| Tool category | Purpose | Phase |
|---|---|---|
| Language-appropriate AST parser | Code structure extraction | Phase 2 |
| LinkML validator (`linkml-validate`) | Schema validation | Phase 9 (Validation) |
| LLM with large context window | Semantic inference | Phases 4-5 |
| YAML serializer | Output generation | All phases |

---

## Extraction philosophy

### Bottom-up, then top-down

Extract the mechanical layers first, then infer the semantic layers from them. Code structure (Layer 3) is deterministic — a parser can extract it with near-perfect accuracy. Architecture (Layer 4) is heuristic — it can be inferred from code organization with high confidence. Domain model (Layer 5) and business intent (Layer 6) are inferential — they require semantic reasoning and human validation.

This matches the SAO guide's core insight:

> Layers 3 and 4 are largely structural (you can derive them from code organization and dependency graphs), while layers 5 and 6 require semantic understanding (recognizing business meaning in code patterns).

### Confidence gradient

Each extraction phase operates at a different confidence level:

| Confidence | Meaning | Phases |
|---|---|---|
| **Deterministic** | Extracted directly from AST; no interpretation needed | Phase 1, Phase 2 |
| **Heuristic** | Inferred from structural patterns with high confidence | Phase 3 |
| **Inferential** | Requires semantic reasoning; may need correction | Phases 4-5 |
| **Manual** | Requires human domain expert validation | Parts of Phases 5-6 |

When populating SAO instances, the extraction agent SHOULD be aware of which confidence level applies and flag inferential results for human review.

### Incremental extraction

You do not need to extract everything at once. Start with a single bounded context or module, complete it through all phases, then expand. This approach:

- Validates your extraction process on a manageable scope
- Produces usable output quickly
- Reveals gaps in your tooling or understanding early

### Idempotency

Re-running a phase with the same inputs SHOULD produce the same outputs. Phases should be designed as deterministic transformations wherever possible, with non-deterministic steps (LLM inference) clearly marked.

---

## Phase dependency map

The eight extraction phases execute in a defined order. Each phase consumes the outputs of prior phases.

```
Phase 1: Inventory ─────────────────────────────────┐
    │                                                │
    v                                                │
Phase 2: Code Structure (Layer 3) ──────────────┐   │
    │                                            │   │
    v                                            │   │
Phase 3: Architecture (Layers 2/4) ─────────┐   │   │
    │                                        │   │   │
    ├───> Phase 4: Domain Model (Layer 5)    │   │   │
    │         │                              │   │   │
    │         v                              │   │   │
    ├───> Phase 5: Business Intent (Layer 6) │   │   │
    │                                        │   │   │
    ├───> Phase 6: Cross-Cutting ◄───────────┘   │   │
    │         (parallel with 3-5)                │   │
    v                                            │   │
Phase 7: Bridge Stitching ◄──────────────────────┘   │
    │          (requires all prior)                   │
    v                                                │
Phase 8: System Context (Layer 1) ◄──────────────────┘
    │          (capstone)
    v
  Validation (doc 09)
```

### Phase summary table

| Phase | Doc | SAO layers | Primary technique | Automation | Key outputs |
|---|---|---|---|---|---|
| 1. Inventory | [01](01-inventory.md) | 3 (partial) | File system traversal | High | **StorageLocation**, **CodeContainer**, **ProgrammingLanguage** |
| 2. Code structure | [02](02-code-structure.md) | 3 | AST parsing | High | **EncapsulationUnit**, **CallableUnit**, **DataStructure**, **ControlFlow**, **DataFlow** |
| 3. Architecture | [03](03-architecture.md) | 2, 4 | Heuristic + manifest parsing | Medium | **System**, **BoundedContext**, **Module**, **Component**, **Service**, **Interface** |
| 4. Domain model | [04](04-domain-model.md) | 5 | LLM inference + patterns | Medium-Low | **Aggregate**, **DomainEntity**, **ValueObject**, **DataStore** |
| 5. Business intent | [05](05-business-intent.md) | 6 | LLM inference + docs | Low | **Actor**, **Operation**, **Rule**, **Event**, **Workflow**, **Capability** |
| 6. Cross-cutting | [06](06-cross-cutting.md) | 1, 2 | Mixed | Medium | **Role**, **Permission**, **TestSuite**, **Deployment**, **Metric** |
| 7. Bridge stitching | [07](07-bridge-stitching.md) | All | Verification | Medium | Cross-layer relationship completeness |
| 8. System context | [08](08-system-context.md) | 1 | Capstone assembly | Low | Finalized **System** with all top-level links |

After all phases: [Validation](09-validation.md) | [Worked Example](10-worked-example.md) | [Reference](11-reference.md)

---

## Document index

| Doc | Title | Description |
|---|---|---|
| **00** (this doc) | Overview | How to use, prerequisites, philosophy, phase map |
| [**01**](01-inventory.md) | Inventory | Phase 1: file tree, languages, dependencies |
| [**02**](02-code-structure.md) | Code Structure | Phase 2: the foundation layer (8 sub-phases) |
| [**03**](03-architecture.md) | Architecture | Phase 3: system, contexts, modules, components, services |
| [**04**](04-domain-model.md) | Domain Model | Phase 4: aggregates, entities, value objects, persistence |
| [**05**](05-business-intent.md) | Business Intent | Phase 5: actors, operations, rules, events, workflows |
| [**06**](06-cross-cutting.md) | Cross-Cutting | Phase 6: security, testing, deployment, observability |
| [**07**](07-bridge-stitching.md) | Bridge Stitching | Phase 7: cross-layer relationship verification |
| [**08**](08-system-context.md) | System Context | Phase 8: capstone assembly |
| [**09**](09-validation.md) | Validation | Completeness checks, iteration, gap-filling |
| [**10**](10-worked-example.md) | Worked Example | End-to-end extraction of a small order service |
| [**11**](11-reference.md) | Reference | Technique table, class checklist, decision trees |

---

## Relationship to other SAO documentation

| Document | Role | When to consult |
|---|---|---|
| [SAO Guide](../guide.md) | Explains what each class means and how classes relate | When you need to understand a class's purpose or attributes |
| [sao.yml](../../sao.yml) | The canonical LinkML schema | When you need exact attribute names, types, or enum values |
| Section deep-dives ([01](../01-enumerations.md)–[13](../13-extended-modeling.md)) | Detailed per-section documentation with YAML examples | When you need attribute-level detail for a specific section |
| [Whitepaper](../whitepaper.md) | Theoretical grounding for ontology-based extraction | Background reading on why this approach works |
