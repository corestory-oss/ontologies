# RDFS Turtle export

[`sao.ttl`](../sao.ttl) is a generated RDFS vocabulary projection of the complete LinkML import closure. It describes the ontology, not a populated software graph. `sao.yml` and `schema/*.yaml` remain the editable source.

```sh
uv run python scripts/export_rdfs.py
uv run python scripts/export_rdfs.py --check
```

The export preserves class and property IRIs, labels, descriptions, class inheritance and mixins as `rdfs:subClassOf`, and property hierarchy where declared. Named scalar types and enums are represented as `rdfs:Datatype`. Declared enum values and their descriptions are annotations using `export:permissibleValue` and `rdf:value`; RDFS does not close the datatype to those values. Value annotation records have stable IRIs under `https://ontologies.corestory.ai/sao/export/values/`. These are not enum individuals to substitute for the string values in existing SAO data.

A property gets `rdfs:domain` or `rdfs:range` when its declarations agree on a single class or datatype. Where a shared property has multiple domains or ranges, alternatives are documented using Schema.org `domainIncludes` / `rangeIncludes`. These annotations do not add RDFS typing entailments. Multiple RDFS domain/range axioms would mean intersection and could misclassify existing data. Property descriptions carry class context where applicable; the export does not retain the pairing between each class and its local property range as a formal constraint.

This is intentionally an RDFS projection, not a lossless conversion. Required fields, cardinality, identifiers, inverses, inlining, abstractness, closed enums, and value constraints remain in LinkML. Mixins become class membership via subclass edges; their LinkML implementation details are not represented. RDFS domain/range are inference statements, not validation rules. Use LinkML validation for instance conformance; SHACL can be considered separately if RDF validation is needed.

The export uses RDF, RDFS, SKOS, Dublin Core and Schema.org vocabulary, plus one documented export annotation. It emits no OWL axioms or restrictions. CI checks that the committed Turtle parses and is graph-equivalent to a fresh export.

References: [RDFS 1.1](https://www.w3.org/TR/rdf-schema/), [Schema.org domainIncludes](https://schema.org/domainIncludes), [Schema.org rangeIncludes](https://schema.org/rangeIncludes).
