# Shared repository layout

The checkout remains named `sao/` for now. Its directory name and GitHub repository name are independent of ontology namespaces, so a later rename to `ontologies/` does not require changing any term IRI.

The former SAO `rdf/` tree is now `ontologies/sao/`. The former sibling SpecSpec `rdf/` tree was copied to `ontologies/specspec/`. Both keep their manifests, vocabulary/shapes/axioms boundaries, and authored Turtle unchanged. The sibling checkout was left intact as a migration reference; it is no longer a dependency of this repository.

SAO's documentation and examples moved to `docs/sao/` and `examples/sao/`; SpecSpec's equivalents live beside them. RDF tests are namespaced under `tests/sao/` and `tests/specspec/`, and shared composition tests live at `tests/` level. Shared command-line entry points call namespaced validators under `scripts/validators/`, avoiding collisions between previously identical script names.

Assembled outputs now live under `dist/`. They remain checked in and verified for RDF graph equivalence. `ontologies/catalog.json` explicitly associates independent ontology versions, source directories, and distribution products. Source manifests continue to resolve files relative to their ontology directory.

The original SAO LinkML entry point and modules moved together to `legacy/sao/`, preserving local imports. Their tests and optional toolchain are isolated from the RDF checks. This preserves existing migration evidence without making LinkML a runtime requirement for either ontology.

The combined example composes the existing SpecSpec graph, bridge links, and a small SAO callable record. It passes both complete SHACL profiles on one graph, rather than merely checking external endpoint types. Independent profiles remain available.

This is a packaging and layout change. It does not merge namespaces, change modeled concepts, introduce inference rules, remove the current bridge, publish a site, or establish a final ecosystem release policy. Source graph equivalence and existing regression tests guard that boundary.

## Reorganization verification

[The verification report](reorganization-report.json) records graph-equivalent assembly of all ten existing manifests, including SAO's reasoning manifest. All 85 authored Turtle source files and 33 retained legacy schema files are byte-identical to their former locations. The ordinary RDF suite also checks composition failures and a build after changing the checkout directory name.
