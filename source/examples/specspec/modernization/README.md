# A source-grounded modernization example

All sources, agents, and results here are synthetic fixtures, not production evidence. The COBOL and Java files are illustrative excerpts, not complete executable modernization targets.

Follow these distinct identities in `graph.ttl`:

1. `legacy-behavior` describes the old guard and cites an immutable source snapshot and line anchor.
2. `no-overdraft` records supplied intent to preserve it. The descriptive observation does not automatically become an obligation.
3. `modernization-decision` records a proposed implementation choice and its rationale.
4. `modern-behavior` describes the Java guard with a separate anchor and snapshot.
5. `comparison-result` records `not_run`. Matching a guard does not establish whole-program equivalence.
6. `spec-document` represents multiple knowledge items; it is not the software callable itself.

The normative acceptance criterion is deliberately separated from the observed Java behavior. The example does not infer successful modernization from either one.

`sources.json` maps snapshots to local fixture files so validation can check their SHA-256 digests and anchor bounds. `sao-links.ttl` contains an optional typed implementation link plus an external identity/type manifest. That manifest is not a complete SAO graph; bridge validation checks link types against the supplied manifest and core graph, not the existence or correctness of a production software graph.


The Turtle graph preserves the original 29 record identities and adds an explicit `SpecificationGraph` envelope linking the collections. Records are IRI nodes; relationships are RDF references. `ScenarioStep.position` supplies sequence order.

From the repository root, run `uv run python scripts/validate_rdf.py` to check SHACL conformance, fixture digests and anchor bounds. The Python check reads only the local files listed in `sources.json`; the `example.org` identifiers are not fetched.
