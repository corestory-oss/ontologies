# RDFS Turtle export

[`dist/sao.ttl`](../../dist/sao.ttl) is an assembled distribution of the editable RDFS vocabulary sources. It describes the ontology, not a populated software graph. `ontologies/sao/vocabulary/*.ttl` are now editable source. LinkML remains a legacy baseline during migration.

```sh
uv run python scripts/build_rdf.py
uv run python scripts/build_rdf.py --check
```

The export preserves class and property IRIs, labels, descriptions, class inheritance and mixins as `rdfs:subClassOf`, and property hierarchy where declared. Named scalar types and enums are represented as `rdfs:Datatype`. Declared enum values and their descriptions are annotations using `export:permissibleValue` and `rdf:value`; RDFS does not close the datatype to those values. Value annotation records have stable IRIs under `https://ontologies.corestory.ai/sao/export/values/`. These are not enum individuals to substitute for the string values in existing SAO data.

A property gets `rdfs:domain` or `rdfs:range` when its declarations agree on a single class or datatype. Where a shared property has multiple domains or ranges, alternatives are documented using Schema.org `domainIncludes` / `rangeIncludes`. These annotations do not add RDFS typing entailments. Multiple RDFS domain/range axioms would mean intersection and could misclassify existing data. Property descriptions carry class context where applicable; the export does not retain the pairing between each class and its local property range as a formal constraint.

This is intentionally an RDFS projection, not a lossless conversion. RDFS alone cannot enforce required fields, cardinality, identifiers, inverses, inlining, abstractness, closed enums, or value constraints. The initial SHACL layer now covers some of these; LinkML is retained as a baseline for the remaining migration. Mixins become class membership via subclass edges; their LinkML implementation details are not represented. RDFS domain/range are inference statements, not validation rules. An initial SHACL profile is now available as `dist/sao.shacl.ttl`; its coverage and limitations are documented in [migration status](turtle-migration.md). Legacy LinkML validation remains available for its JSON/YAML baseline.

The export uses RDF, RDFS, SKOS, Dublin Core and Schema.org vocabulary, plus one documented export annotation. Logical OWL axioms remain in the optional supplement. The vocabulary uses `owl:deprecated` annotations to identify predicates rejected by the 3.0.0 profile; those annotations provide no compatibility inference. CI checks that the complete export and every topic file match regeneration, and that assembling the files in the manifest yields exactly the complete graph.

References: [RDFS 1.1](https://www.w3.org/TR/rdf-schema/), [Schema.org domainIncludes](https://schema.org/domainIncludes), [Schema.org rangeIncludes](https://schema.org/rangeIncludes).

## Modular sources and distribution

`ontologies/sao/vocabulary/` contains editable topic files corresponding to the original split. `ontology.ttl` contains vocabulary metadata. `common.ttl` contains shared properties and built-in datatypes. `ontologies/sao/manifests/vocabulary.json` lists the complete vocabulary assembly; `ontologies/sao/manifests/shapes.json` lists the SHACL assembly.

Each file has its own prefix declarations. Load files individually into the same graph; no `owl:imports` or Turtle inclusion mechanism is used. Shared property semantics are authored once in `common.ttl`, not recomputed independently per topic.

```python
import json
from pathlib import Path
from rdflib import Graph

root = Path("ontologies/sao")
manifest = json.loads((root / "manifests/vocabulary.json").read_text())
graph = Graph()
for filename in manifest["files"]:
    graph.parse(root / filename, format="turtle")
```

The assembly equals `dist/sao.ttl`. Both distributions are generated artifacts; edit their source topic files instead. Initial shape nodes and enum list cells have stable named IRIs; standard anonymous Turtle shapes are also supported by assembly comparisons.
