# CoreStory Ontologies

A shared home for two complementary, interlinked RDF ontologies:

| Ontology | Scope | Namespace | Current version |
|---|---|---|---|
| [SAO — Systems Abstraction Ontology](docs/sao/README.md) | Software structures and abstractions | `https://ontologies.corestory.ai/sao/` | 3.0.0 candidate |
| [SpecSpec — Specification & Evidence Ontology](docs/specspec/README.md) | Specifications, claims, decisions, and supporting evidence | `https://ontologies.corestory.ai/specspec/` | 0.1.0 draft |

Both are authored in Turtle, with RDFS vocabulary, SHACL validation, and optional OWL supplements. Their namespaces and ontology versions remain separate. The Python project version describes shared tooling; the ontology versions are recorded in [the catalog](ontologies/catalog.json) and their RDF metadata.

SpecSpec's existing optional SAO bridge is retained for now. Its link classes connect knowledge items to software entities, and glossary terms to each other. This repository reorganization does not change term meanings, IRIs, constraints, or inference axioms.

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
scripts/                   # Shared tooling, static docs builder and ontology checks
nix/                       # Reproducible builds, checks, preview and dev shell
web/                       # Website prose, templates, styles, brand assets and Garden pins
legacy/sao/                # Historical LinkML baseline and its separate tests
```

## Build, check and preview

The normal workflow uses Nix, following Plot's flake/direnv pattern:

```sh
nix build                     # Static HTML docs → result/
nix run .#preview             # Local preview at http://127.0.0.1:4173/; Ctrl-C stops it
nix flake check               # RDF, composition, docs and link checks
nix build .#ontologies        # Turtle distributions → result/
nix run .#prepare-site        # Check/build committed main and prepare local site branch
```

If your existing direnv setup is active, run `direnv allow` once to load the pinned development tools automatically when entering this checkout. Otherwise use `nix develop`. Neither command starts a server or rebuilds the docs automatically.

The static site has a branded prose homepage, a combined RDF Garden browser under `reference/`, HTML guides under `guides/` and downloadable Turtle under `dist/`. Edit website prose in `web/pages/`; layouts, styles and official brand assets live alongside it. No application server or runtime Nix/Python installation is required.

`main` contains editable sources. The intended `site` branch contains only the generated contents of the site build's `result/`, committed locally and pushed for the host to serve. Generated files are never edited by hand. CI invokes `nix flake check`, which validates source and builds/checks the static site; it does not publish. `nix run .#prepare-site` checks and builds committed local `main`, then creates or updates local `site` without switching your checkout. Review it, then push explicitly with `git push origin site`. Hosting integration is configured separately.

See [Nix and publishing explained](docs/nix-and-publishing.md) for the command meanings, lockfile, direnv, local preview and CDN details.

Inside the Nix development environment, maintainers can refresh committed distributions or run individual tools:

```sh
python scripts/build_rdf.py
python scripts/build_rdf.py --check
python scripts/validate_rdf.py
python scripts/validate_axioms.py
python -m unittest discover -s tests
```

To validate your own graph, select a profile:

```sh
nix develop -c python scripts/validate_rdf.py --ontology sao path/to/software.ttl
nix develop -c python scripts/validate_rdf.py --ontology specspec path/to/specification.ttl
nix develop -c python scripts/validate_rdf.py --ontology ecosystem path/to/combined.ttl
```

The ecosystem profile applies SAO, SpecSpec and the current bridge shapes together. The independent SpecSpec profile does not load SAO. SpecSpec's graph rules use SHACL-SPARQL, so a Core-only SHACL processor cannot run the entire profile. SHACL validation does not materialize OWL inferences.

## Distribution files

[dist/](dist/) contains separate vocabulary, SHACL and OWL files for each ontology: `sao.ttl`, `sao.shacl.ttl`, `sao.owl.ttl`, and the corresponding `specspec.*ttl` files. The `specspec-sao.*ttl` files contain only the current bridge layer. Consumers can load the layers they need; there are no automatic network imports.

The source reorganization does not change public namespace or term IRIs. Moving local build outputs into `dist/` changes repository paths; eventual CDN URL routing is a publishing decision. The intended documentation publishing model remains static output on a `site` branch, served through CoreStory's CDN. Static builds and local preview are available. Publication is designed around a generated `site` branch; this checkout does not configure automatic branch updates or hosting.

## Legacy baseline

SAO's retained LinkML 2.1.0 baseline lives under [legacy/sao/](legacy/sao/README.md). LinkML is an optional dependency group, isolated from the ordinary RDF build, tests, and validation. It remains available for historical migration checks. SpecSpec has no active LinkML source.

See [CONTRIBUTING.md](CONTRIBUTING.md), [the repository layout notes](docs/repository-layout.md), and [the ecosystem example](examples/ecosystem/README.md).

## License

Copyright CoreStory, Inc. Both ontologies, documentation, and examples are licensed under [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for preserved attribution.
