# Turtle authority migration

## What is authoritative now

`rdf/vocabulary/*.ttl` are the editable RDFS vocabulary sources. They are no longer regenerated from LinkML. `rdf/shapes/*.ttl` are the editable initial validation profile. `scripts/build_rdf.py` reads their manifests, assembles `sao.ttl`, `sao.shacl.ttl`, and the optional `sao.owl.ttl` supplement, and checks freshness. It imports RDFLib, not LinkML. RDF validation uses pySHACL and these Turtle sources.

The first Turtle-authority step preserved the 2.1.0 vocabulary graph. The [3.0.0 candidate](migration-3.0.md) now deliberately changes relationship predicates and their validation. Class IRIs and the ontology namespace remain stable. Editing Turtle changes the next distribution without editing YAML.

## Initial SHACL coverage

The initial shapes were bootstrapped once from the resolved SAO 2.1.0 LinkML model, using a small migration translator because the standard generator stopped on `contained_in_unit.inverse` referring to a class-local slot. No inverse declaration was corrected or silently reinterpreted.

All 147 classes have named node shapes. The initial layer contains 1,866 property shapes after inheritance, including required fields, single-value cardinality, class ranges, scalar datatypes, enum membership, inherited datatype patterns, and seven `any_of` constraints. Shape and property-shape IRIs are separate from domain terms. The historical counts are recorded in [the bootstrap report](shacl-bootstrap-report.json); they do not freeze future Turtle editing.

Shapes are open: extra predicates are allowed. Vocabulary hierarchy is supplied during validation, so inherited base-class targets and `sh:class` constraints can recognize subclasses. We do not materialize OWL inferences. Validation uses SHACL Core and performs meta-validation of the shapes themselves.

Required LinkML `id` fields remain literal properties alongside RDF subjects. That preserves the initial constraints while their future mapping is decided. The bootstrap is not a proof that the RDF validation profile equals LinkML instance validation.

## What is still pending

- Complete internal producer/query/data migration to the proposed 3.0.0 relationship contract. The seven audited groups have candidate resolutions and the supplement now carries 217 inverse pairs; SHACL validation still does not materialize OWL inferences.
- Decide the closed-world validation policy and treatment of abstract classes.
- Define how identifier fields map to RDF subjects and how JSON/YAML inlining and mixin conventions are preserved, retired, or represented in a serialization profile.
- Establish validation coverage with richer positive and negative graphs, including relationship references, enum lists, alternative ranges, and subclass overrides.
- Decide whether documentation and downstream JSON/type generation should be driven from RDF, retained as compatibility exports, or discontinued.
- Add consistency checks between descriptive enum annotations and class-specific SHACL allowed-value lists.

Legacy YAML and its tooling remain available as a historical comparison baseline. CI still checks that baseline on its own; it does not require authored Turtle to equal a new LinkML export. Do not remove it until the above decisions and coverage justify doing so.

## Commands

```sh
uv run python scripts/build_rdf.py
uv run python scripts/build_rdf.py --check
uv run python scripts/validate_rdf.py examples/rdf/system.ttl
uv run python -m unittest discover -s tests
```

Historical tools under `scripts/migration/` require explicit output locations. `bootstrap_shapes.py` refuses to write into an already populated directory. These are migration tools, not authoring or build commands.
