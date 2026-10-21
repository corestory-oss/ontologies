# Ecosystem changelog

## Unreleased

- Combine SAO and SpecSpec in one repository, retaining separate namespaces and ontology versions.
- Move authoritative Turtle modules into `ontologies/sao/` and `ontologies/specspec/`; preserve the existing SpecSpec–SAO bridge.
- Group documentation, examples, and regression tests by ontology. Assemble committed distribution files into `dist/`.
- Share the RDF build/validation toolchain and CI, including a full combined SHACL example.
- Isolate SAO's historical LinkML baseline and checks under `legacy/sao/`, with an optional dependency group.
- Preserve the authored RDF graphs and the earlier ontology changelogs: [SAO](docs/sao/CHANGELOG.md), [SpecSpec](docs/specspec/CHANGELOG.md).
