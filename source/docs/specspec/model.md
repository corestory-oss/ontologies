# Model notes and boundaries

## Statements and software

SAO describes software structure and behavior. SpecSpec describes statements, obligations, decisions, and evidence about software. A normative requirement and a descriptive statement that the software implements it are separate nodes.

A requirement inherits Claim so it carries statement-level provenance, review, and support. It restricts `statement_mode` to `normative`. A general Claim may be descriptive, normative, or hypothetical. AcceptanceCriterion has the same normative restriction.

UseCase expresses a goal and participants; Scenario contains ordered steps and claims describing conditions and outcomes. Their prose is contextual. Assertions needing separate provenance should be Claim nodes, not buried in a document description.

## Evidence and identity

A SourceSnapshot identifies a captured source state using an immutable revision. EvidenceAnchor locates a region within it. A filename alone is insufficient grounding. Line coordinates are one-based and inclusive. A selector can locate a non-line-oriented region.

A source anchor supports or contradicts a claim. Derived claims also reference their premise claims. This provides a traversable evidence chain, but neither a link nor an origin tag establishes truth. Runtime observations can be captured as snapshots just as code can.

SpecActivity records responsible agents, inputs and optional tool/model versions. Claim links back to the producing activity. Authorship and review responsibility are distinct. The current model records a review disposition, not a full append-only review history.

## Document representations

SpecificationArtifact identifies a document. ArtifactFragment maps a section to one or more knowledge nodes. RepresentationProfile identifies an external convention. A document is not given an SAO class merely because it mentions a software component.

The initial draft preserves context, rationale and consequences through dedicated fields and claim relationships. It does not attempt lossless round trips through every external format. Native text should be retained when an adapter would otherwise discard meaning.

## Optional bridge

`ontologies/specspec/bridges/sao/` owns three initial link classes: SoftwareSubjectLink, RequirementImplementationLink and VerificationTestLink. Their subject and target properties have explicit class ranges in SHACL. Both endpoints are identified references; records do not need to be nested inside one another.

The software-target ranges deliberately differ: a subject link may mention any SAO NamedEntity; an implementation link currently targets CallableUnit; a verification link targets TestCase. Further link classes should state their intended range rather than weakening all links to arbitrary URIs. These link nodes preserve the draft exchange design and its qualified relationships.

Core SpecSpec class names avoid colliding with SAO’s existing NamedEntity, Evidence and KnowledgeArtifact. Core manifests do not include the bridge. Optional integration explicitly loads both vocabularies and the bridge, without network imports.

## Draft constraints and limits

SHACL checks required properties, scalar cardinality, enum values, numeric bounds, normative statement mode, and typed references. SHACL-SPARQL checks canonical identity, source anchor coordinates, claim premise cycles, observed/inferred support, confidence basis, review responsibility, scenario positions, chosen decision membership, and baseline membership for proposed requirement removals/replacements.

Every knowledge node uses its identifier as its RDF subject IRI. The existing `spec:id` URI literal is retained and must match that IRI. Scenario step order comes from `ScenarioStep.position`, starting at one; Turtle triple order is irrelevant. See [RDF migration details](rdf-migration.md) for the representation differences from the earlier record format.

The fixture manifest enables content-digest and line-bound checks for local example sources. General validation cannot determine from a revision string whether an external source is truly immutable or whether an assertion is faithful to it. Evidence adequacy, confidence calibration, claim scope, semantic contradictions and behavioral equivalence require tooling and human review beyond these checks.

Stabilization questions include evidence-link qualification, review history, inference activities with multiple conclusions, versioned knowledge identities, transformation plans, governance-specific classes, and external graph validation. No current field implies universal behavioral equivalence or automatic acceptance.

## RDFS, SHACL and OWL layers

`ontologies/specspec/vocabulary/` defines the vocabulary in RDFS. Reused predicates have class-specific usage constraints in SHACL. A property with several intended domains or ranges uses `schema:domainIncludes` or `schema:rangeIncludes` annotations; multiple `rdfs:domain` statements would infer membership in every domain. An annotation does not enforce a constraint. SHACL is the validation contract.

`ontologies/specspec/axioms/` supplies optional OWL object/datatype property declarations. This draft has no declared inverses, transitivity or disjointness. The conversion does not invent them. Loading the OWL supplement does not replace SHACL validation or establish that claims are true.
