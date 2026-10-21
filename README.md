# CoreStory Ontologies

A shared home for two complementary, interlinked RDF ontologies:

| Ontology | Scope | Namespace | Current version |
|---|---|---|---|
| [SAO — Systems Abstraction Ontology](docs/sao/README.md) | Software structures and abstractions | `https://ontologies.corestory.ai/sao/` | 3.0.0 candidate |
| [SpecSpec — Specification & Evidence Ontology](docs/specspec/README.md) | Specifications, claims, decisions, and supporting evidence | `https://ontologies.corestory.ai/specspec/` | 0.1.0 draft |

Both are authored in Turtle, with RDFS vocabulary, SHACL validation, and optional OWL supplements. Their namespaces and ontology versions remain separate. The Python project version describes shared tooling; the ontology versions are recorded in [the catalog](ontologies/catalog.json) and their RDF metadata.

SpecSpec's existing optional SAO bridge is retained for now. Its three link classes connect knowledge items to software entities. This repository reorganization does not change term meanings, IRIs, constraints, or inference axioms.

## Repository layout

```text
ontologies/
  catalog.json             # Namespaces, ontology versions, sources and products
  sao/
    vocabulary/            # Editable RDFS Turtle
    shapes/                # Editable SHACL Turtle
    axioms/                # Editable OWL Turtle
    manifests/             # Explicit local source lists
  specspec/
    vocabulary/
    shapes/
    axioms/
    manifests/
    bridges/sao/           # Current integration vocabulary, shapes and axioms
dist/                      # Assembled, committed Turtle distributions
docs/sao/                  # SAO guides, reference material and changelog
docs/specspec/             # SpecSpec model notes, mappings and changelog
examples/sao/
examples/specspec/
examples/ecosystem/        # One graph validated against both ontologies
tests/                     # RDF and composition regression tests
scripts/                   # Shared tooling and ontology-specific checks
legacy/sao/                # Historical LinkML baseline and its separate tests
```

## Build and validate

Use Python 3.13+ and uv. Run commands from the repository root; they do not depend on this checkout's directory name.

```sh
uv sync --locked
uv run python scripts/build_rdf.py
uv run python scripts/build_rdf.py --check
uv run python scripts/validate_rdf.py
uv run python scripts/validate_axioms.py
uv run python -m unittest discover -s tests
```

The default build assembles both ontologies. The default RDF validation checks the independent SAO and SpecSpec examples and a combined modernization graph, including evidence fixture integrity. CI also checks SAO's relationship example and the narrower bridge endpoint-type fixture. No inference is materialized during SHACL validation.

To work on just one ontology:

```sh
uv run python scripts/build_rdf.py --ontology sao
uv run python scripts/validate_rdf.py --ontology specspec
uv run python scripts/validate_axioms.py --ontology sao
```

To validate your own graph, select the applicable profile:

```sh
uv run python scripts/validate_rdf.py --ontology sao path/to/software.ttl
uv run python scripts/validate_rdf.py --ontology specspec path/to/specification.ttl
uv run python scripts/validate_rdf.py --ontology ecosystem path/to/combined.ttl
```

The ecosystem profile applies SAO, SpecSpec, and the existing bridge shapes together. The independent SpecSpec profile does not load SAO. SpecSpec's graph rules use SHACL-SPARQL, so a Core-only SHACL processor cannot run the entire profile.

## Distribution files

[dist/](dist/) contains separate vocabulary, SHACL and OWL files for each ontology: `sao.ttl`, `sao.shacl.ttl`, `sao.owl.ttl`, and the corresponding `specspec.*ttl` files. The `specspec-sao.*ttl` files contain only the current bridge layer. Consumers can load the layers they need; there are no automatic network imports.

The source reorganization does not change public namespace or term IRIs. Moving local build outputs into `dist/` changes repository paths; eventual CDN URL routing is a publishing decision. The intended documentation publishing model remains static output on a `site` branch, served through CoreStory's CDN. No publishing or persistent preview service is configured by this change.

## Legacy baseline

SAO's retained LinkML 2.1.0 baseline lives under [legacy/sao/](legacy/sao/README.md). LinkML is an optional dependency group, isolated from the ordinary RDF build, tests, and validation. It remains available for historical migration checks. SpecSpec has no active LinkML source.

See [CONTRIBUTING.md](CONTRIBUTING.md), [the repository layout notes](docs/repository-layout.md), and [the ecosystem example](examples/ecosystem/README.md).

## License

Copyright CoreStory, Inc. Both ontologies, documentation, and examples are licensed under [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for preserved attribution.
