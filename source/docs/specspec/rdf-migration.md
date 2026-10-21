# Turtle source migration

SpecSpec now follows SAO's source layout: modular RDFS vocabulary, SHACL shapes and graph rules, optional OWL declarations, explicit assembly manifests, and assembled Turtle distributions under `dist/`. The ordinary build and validation environment contains no LinkML dependency. The previous schema and generated JSON Schema/documentation paths have been removed from the active tree.

This is a representation migration of the 0.1.0 draft, not the proposed ontology redesign. All 21 core classes, eight enums, three optional bridge classes, class inheritance, descriptions, property IRIs, and 29 modernization example record identities are retained. The original 257 induced class/property contracts are recorded in [the migration baseline](rdf-migration-baseline.json) and checked against the Turtle sources by the tests. The prior authoring tree was archived outside this checkout before conversion.

## Representation choices

- Each record's identifier becomes its RDF subject IRI. The existing `spec:id` literal is also retained, with datatype `xsd:anyURI`. A SHACL-SPARQL constraint checks that it matches the subject IRI. Identical RDF triples collapse naturally; duplicated record occurrences have no separate identity in RDF. Distinct nodes cannot reuse the same canonical identifier.
- References become IRI objects. Class inheritance uses `rdfs:subClassOf`; SHACL validates the expected class of each reference using the supplied vocabulary. Missing or mistyped targets fail validation.
- The former inlined graph envelope becomes an explicit `SpecificationGraph` node referencing the same records. RDF has no nested-record ownership or array insertion order. Scenario ordering uses the existing `ScenarioStep.position`, with unique consecutive positions starting at one.
- Concrete leaf class shapes are closed to catch unknown properties. The `SpecElement` and `Claim` superclass shapes remain open so their subclass targets can carry subclass properties. The bridge's shapes are also open for combined graphs. This intentionally differs from strict JSON object field closure on standalone superclass/bridge records; it is not a claim of byte-for-byte or validation-language equivalence.
- Enums retain their literal values and descriptions in vocabulary annotations. SHACL `sh:in` lists enforce membership. Custom RDFS enum datatype declarations alone do not enforce the allowed values.
- Required fields, scalar cardinality, datatypes, class ranges, bounds and normative statement mode are expressed in SHACL. Cross-field and graph constraints previously implemented in Python are SHACL-SPARQL constraints in `ontologies/specspec/shapes/rules.ttl`. These need a processor supporting SHACL-SPARQL in addition to SHACL Core.
- Source-file SHA-256, path containment and file line bounds remain Python fixture checks. SHACL alone cannot compare the graph with these local files. The fixtures are synthetic and no sample program is executed.

## Shared properties and reasoning

One predicate can be used by several classes. Class-specific ranges remain attached to the appropriate SHACL property shapes. Vocabulary terms with multiple intended domains/ranges use `schema:domainIncludes` / `schema:rangeIncludes` annotations to avoid accidental intersection inference. These annotations are descriptive; SHACL supplies the constraints.

The OWL supplement classifies properties as object or datatype properties. No inverse, transitive, disjointness or behavioral-equivalence axioms are introduced. The ontology version remains 0.1.0 because this remains the same unpublished modeling draft; release/version policy still needs agreement.

## Composition and validation

The manifests enumerate local Turtle files; the builder merges their triples and checks coverage and graph-equivalent round trips. Each core layer has its own manifest. The bridge has three additional manifests and distributions containing only bridge definitions. It depends on the core and an explicitly supplied SAO vocabulary. Nothing is fetched through `owl:imports`.

The validator reads source modules so it cannot silently validate stale distributions. `scripts/build_rdf.py --check` separately verifies that shipped distributions match those sources. It rejects graphs without explicitly typed SpecSpec instance nodes, avoiding an empty-target success.

The tests check the captured class/property contracts, enum membership, class descriptions and inheritance, build equivalence, independent core, invalid typed references, provenance/review rules, decision and baseline membership, scenario order, identity, and fixture integrity. Bridge checks use a synthetic SAO vocabulary in CI; a real SAO vocabulary can be supplied separately. They validate endpoint types rather than the full SAO instance profile.

Full model equivalence across all possible future RDF entailments is not asserted. The representation choices above make the differences explicit while retaining the current draft's modeled information and validation intent.
