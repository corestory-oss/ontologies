# SpecSpec

**Specification & Evidence Ontology**

Part of the [CoreStory Ontologies repository](../../README.md). Run commands from the repository root.

SpecSpec is an RDF vocabulary for requirements, scenarios, decisions, descriptive claims, and the evidence supporting them. Its namespace is `https://ontologies.corestory.ai/specspec/` (`spec:`).

The goal is to read existing software, lift grounded knowledge into rich specifications, and use those specifications to guide replacement implementations while retaining the evidence chain. The ontology also represents supplied intent and proposed changes. Observed behavior, intended behavior, and verification outcomes remain distinct.

This is a **0.1.0 modeling draft**. It does not yet implement document importers, renderers, or a modernization engine. The namespace is a proposed identifier space; this checkout does not configure hosting or CDN publication.

## Authoritative sources

Edit the modular Turtle files under `ontologies/specspec/`. The layout follows SAO: RDFS vocabulary, SHACL validation, and an optional OWL supplement are separate layers. LinkML is no longer required.

| Directory | Contents |
|---|---|
| `ontologies/specspec/vocabulary/` | Classes, predicates, descriptions, inheritance and enum annotations |
| `ontologies/specspec/shapes/` | Class/property constraints and graph rules in SHACL and SHACL-SPARQL |
| `ontologies/specspec/axioms/` | Optional OWL object/datatype property declarations |
| `ontologies/specspec/bridges/sao/` | Optional vocabulary, shapes and OWL declarations connecting SpecSpec to SAO |
| `ontologies/specspec/manifests/` | Explicit source lists used to assemble each distribution |
| `examples/specspec/modernization/` | Synthetic Turtle instance graph and supporting source fixtures |
| `scripts/` | RDF assembly, validation and fixture integrity checks |
| `tests/` | Migration preservation and validation regression tests |

Vocabulary and shape modules cover common identity/provenance, specifications, decisions, evidence, representations and the graph envelope. Graph rules live in `ontologies/specspec/shapes/rules.ttl`.

The assembled core products are `dist/specspec.ttl`, `dist/specspec.shacl.ttl` and `dist/specspec.owl.ttl`. They are build outputs; edit their sources and rebuild. The three corresponding `specspec-sao.*ttl` products contain **only the optional bridge layer** and are loaded alongside the core. Core SpecSpec has no SAO dependency, and the bridge does not copy or modify SAO definitions.

## Important distinctions

- A document can describe many knowledge items and software entities. Its identity is not the identity of any one of them.
- `Claim.origin` records observed, inferred, or supplied origin. It does not establish truth. Review status and optional confidence are separate fields.
- Descriptive claims state existing behavior. Requirements and acceptance criteria state obligations. An observation can motivate a requirement without automatically becoming one.
- Evidence points into an identified source state, not a moving branch. A supporting link records support offered, not proof.
- Verification results refer to a specific check and snapshot. A passing result is scoped to that check.
- Regeneration should retain supplied intent and record contradictions for review. The ontology represents these distinctions; it does not implement a regeneration policy.

See [model notes](model.md), [format mappings](format-mappings.md), [RDF migration details](rdf-migration.md), and [the modernization example](../../examples/specspec/modernization/README.md).

## Build and validate

Python 3.13+, uv, RDFLib, pySHACL and owlrl provide the shared ecosystem tooling. The lockfile pins the environment.

```sh
uv sync --locked
uv run python scripts/build_rdf.py
uv run python scripts/build_rdf.py --check
uv run python scripts/validate_rdf.py
uv run python scripts/validate_axioms.py
uv run python -m unittest discover -s tests
```

Assembly checks each manifest against its source directory and verifies that distributions round-trip as equivalent RDF graphs. `--check` detects stale distributions regardless of Turtle formatting or triple order. Validation reads the editable sources, checks the shapes against SHACL's own shapes, then checks instance conformance and local fixture integrity. It does not prove claims or execute the sample programs.

To validate your own Turtle graph:

```sh
uv run python scripts/validate_rdf.py --ontology specspec path/to/graph.ttl
```

The validator requires explicitly typed SpecSpec instance nodes. RDFS class hierarchies are supplied to SHACL; optional OWL declarations are not needed for validation. The profile includes SHACL-SPARQL, so a SHACL Core-only processor cannot run every check.

To check bridge endpoint types against the co-located SAO vocabulary:

```sh
uv run python scripts/validate_rdf.py --ontology specspec \
  --sao-vocabulary dist/sao.ttl \
  --bridge-data examples/specspec/modernization/sao-links.ttl
```

This loads the core, bridge and supplied SAO vocabulary explicitly. It checks the link endpoints against their declared types; it does not apply SAO's full instance shapes to the example's small external identity/type manifest. There are no network imports. Core validation is independent of SAO; the ecosystem profile checks the full composition. CI also exercises the narrower bridge check against a synthetic vocabulary fixture.

## Scope and next decisions

This conversion retains the existing 21 core classes, eight enums and three bridge classes. It changes representation and tooling, with [documented RDF representation differences](rdf-migration.md). The proposed model expansions remain separate work.

The old SpecSpec document convention is a reference for stable IDs and evidence chains, not a required output format. Existing formats can be views of this graph. Initial mappings are illustrative, not certified adapters.

KnowledgeArtifact and governance classes have not been removed from SAO or migrated wholesale. `SpecificationArtifact` remains a distinct draft term for document representations; its eventual relationship to SAO's `KnowledgeArtifact` needs agreement. Compliance-specific requirements, controls, and risk assessments need a separate modeling pass.

Before stabilizing: review class boundaries, decide bridge coverage and release pinning, choose representation adapters, and define provenance/review policies. Specifications and sources have their own revisions; the ontology version describes the vocabulary. SAO and SpecSpec are intended for open-source release; hosting and release hardening remain separate work.

Copyright © 2026 CoreStory, Inc. Licensed under [Apache License 2.0](../../LICENSE).
