# Modeling patterns

Keep software, observations, obligations, implementation assertions, and verification results distinct. The [modernization fixture](../examples/specspec/modernization/README.md) shows how to connect them without treating an observed guard as a requirement or a proposed replacement as verified software.

**Every source, agent, and result in this example is synthetic.** The COBOL and Java files are illustrative excerpts, not complete executable modernization targets. The recorded behavioral comparison is `not_run`; graph validation does not change that outcome.

The patterns below use the existing [SpecSpec graph](../examples/specspec/modernization/graph.ttl), [bridge links](../examples/specspec/modernization/sao-links.ttl), and [SAO software instance](../examples/ecosystem/software.ttl). `demo:` abbreviates `urn:specspec:demo:`. Turtle excerpts show selected triples from those files, **not standalone conforming graphs**. Validate the complete fixture from the repository root:

```sh
nix develop -c python scripts/validate_rdf.py --ontology ecosystem
```

This passes with 242 data triples and checks the local evidence fixtures. It applies both ontology profiles and the bridge shapes without executing the sample programs.

## 1. Separate an observation from an obligation

The fixture gives observed behavior and intended behavior different identities:

| Node | Class | Mode and origin | Role |
|---|---|---|---|
| `demo:legacy-behavior` | **Claim** | `descriptive`, `observed` | Describes the COBOL rejection branch in the excerpt |
| `demo:no-overdraft` | **Requirement** | `normative`, `supplied` | Requires the replacement to reject excessive withdrawals without reducing the balance |
| `demo:modern-behavior` | **Claim** | `descriptive`, `observed` | Describes the Java guard throwing before an updated balance is returned |
| `demo:overdraft-criterion` | **AcceptanceCriterion** | `normative`, `supplied` | States the expected rejection and unchanged balance for the example scenario |

Both observed claims have `spec:review_status "unreviewed"`. Observed origin records how a claim arose; it is not an approval or a truth value.

```turtle
@prefix spec: <https://ontologies.corestory.ai/specspec/> .
@prefix demo: <urn:specspec:demo:> .

# Selected relationships; required metadata remains in graph.ttl.
demo:legacy-behavior a spec:Claim ;
    spec:origin "observed" ;
    spec:statement_mode "descriptive" ;
    spec:supporting_anchors demo:legacy-guard .

demo:no-overdraft a spec:Requirement ;
    spec:origin "supplied" ;
    spec:statement_mode "normative" ;
    spec:derived_from_claims demo:legacy-behavior ;
    spec:acceptance_criteria demo:overdraft-criterion .
```

`spec:derived_from_claims` preserves the premise behind the requirement; it does not automatically turn an observation into an obligation. The fixture separately records the supplied normative statement and its author. Requirements inherit **Claim**, but their `statement_mode` must be `normative`.

**Use this pattern when:** documenting behavior that a team may preserve, change, or reject. Keep the source observation even when the intended behavior differs.

## 2. Anchor a claim to a captured source state

Follow the legacy claim's evidence chain:

| Relationship | Fixture value |
|---|---|
| `demo:legacy-behavior` → `spec:supporting_anchors` | `demo:legacy-guard` |
| `demo:legacy-guard` → `spec:snapshot` | `demo:legacy-snapshot` |
| Anchor location | `spec:path "withdraw.cbl"`, `spec:line_start 8`, `spec:line_end 12` |
| Snapshot revision | `spec:revision` contains the SHA-256 digest of the local fixture |
| Local source mapping | `sources.json` maps the snapshot IRI to `source/withdraw.cbl` |

An **EvidenceAnchor** locates a region within a **SourceSnapshot**. Line coordinates are one-based and inclusive. A filename or moving branch name alone is not an immutable source state. The Java claim has a separate anchor, snapshot, and digest; it refers to lines 5–8 of [Account.java](../examples/specspec/modernization/source/Account.java), not the COBOL snapshot.

The [source manifest](../examples/specspec/modernization/sources.json) lets the validator compare the local bytes with `spec:revision`, check anchor paths, and check that anchors stay within the source. The `example.org` source identifiers are not fetched. These checks do not assess whether a cited passage adequately supports the claim.

Provenance has its own nodes: the observed claims point through `spec:generated_by` to `demo:extract`, a **SpecActivity**. That activity records `spec:input_snapshots`, `spec:performed_by`, and `spec:tool_version`. The fixture's extractor is a synthetic **SpecAgent**, not evidence that this repository includes an extraction engine.

**Use this pattern when:** retaining a reviewable trail from a statement to the exact source state and the activity that produced it.

## 3. Link an implementation assertion to a callable

A requirement is not a software method. The optional bridge gives the implementation assertion its own node and records a descriptive basis claim:

```turtle
@prefix sao: <https://ontologies.corestory.ai/sao/> .
@prefix spec: <https://ontologies.corestory.ai/specspec/> .
@prefix specsao: <https://ontologies.corestory.ai/specspec/sao/> .
@prefix demo: <urn:specspec:demo:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

demo:implementation-link a specsao:RequirementImplementationLink ;
    spec:id "urn:specspec:demo:implementation-link"^^xsd:anyURI ;
    spec:title "Proposed Java grounding"^^xsd:string ;
    specsao:requirement demo:no-overdraft ;
    specsao:callable <urn:specspec:demo:software:withdraw> ;
    specsao:basis_claim demo:modern-behavior .

<urn:specspec:demo:software:withdraw> a sao:CallableUnit ;
    sao:id "urn:specspec:demo:software:withdraw" ;
    sao:name "Account.withdraw" ;
    sao:callable_type "method" .
```

The bridge requires a **Requirement**, a **CallableUnit**, and a descriptive **Claim** as endpoints. In this fixture, the basis claim is still unreviewed and the link's title says “Proposed Java grounding.” A valid link records the assertion and its offered support; it does not prove that the callable satisfies the obligation.

The [bridge-only file](../examples/specspec/modernization/sao-links.ttl) declares only the callable's RDF type. The ecosystem fixture adds `sao:id`, `sao:name`, and `sao:callable_type`, allowing the complete SAO shapes to run. Check that software instance independently with:

```sh
nix develop -c python scripts/validate_rdf.py --ontology sao \
  examples/ecosystem/software.ttl
```

This passes with 4 data triples. It checks the graph's callable fields, not the Java method's behavior.

Choose the bridge class that matches your assertion:

| Bridge class | Relationship | Boundary |
|---|---|---|
| **SoftwareSubjectLink** | `specsao:subject` → knowledge item; `specsao:software_entity` → SAO **NamedEntity** | A mention is not an implementation claim |
| **RequirementImplementationLink** | `specsao:requirement` → requirement; `specsao:callable` → callable; `specsao:basis_claim` → descriptive claim | The current implementation target is **CallableUnit**, not an arbitrary component URI |
| **VerificationTestLink** | `specsao:result` → verification result; `specsao:test_case` → SAO **TestCase** | A test definition is distinct from a check's result |

Only **RequirementImplementationLink** is instantiated in this fixture. See [bridge boundaries](specspec/model.md#optional-bridge) before adding other link types to your data.

## 4. Record the decision and its remaining uncertainty

`demo:modernization-decision` is a **Decision** with `spec:status "proposed"`. It:

- addresses `demo:no-overdraft` through `spec:addresses_requirements`;
- lists `demo:java-option` and `demo:unchanged-option` through `spec:options`;
- names `demo:java-option` through `spec:chosen_option`;
- cites `demo:rationale` through `spec:rationale_claims`;
- retains `demo:scope-gap` through `spec:consequence_claims`.

The chosen option must belong to the listed options. A selected option does not make a proposed decision accepted or an implementation verified.

The rationale states supplied intent to preserve the guard. The separate `demo:scope-gap` claim has `spec:origin "inferred"`, cites both behavior claims through `spec:derived_from_claims`, and warns that matching guards does not establish equivalence of input domains, numeric precision, side effects, or transactions. Keep such limits as addressable claims rather than dropping them when producing a specification document.

## 5. Keep a scenario and its document representation distinct

`demo:excessive-withdrawal` is a **Scenario** that links to:

- the requirement through `spec:illustrates_requirements`;
- `demo:request-step` through `spec:steps`;
- the acceptance criterion through `spec:outcomes`.

The step requests 150.00 against a balance of 100.00. Its `spec:position 1` supplies ordering; Turtle triple order does not. The criterion states that rejection shall leave the balance at 100.00 and records a proposed `spec:verification_method`. These are scenario and acceptance statements, not executed test results.

`demo:spec-document` is a **SpecificationArtifact**. Its `spec:represents` links point to the target specification, requirement, and scenario. `demo:requirement-fragment`, an **ArtifactFragment**, points to that artifact through `spec:artifact` and uses `spec:selector` to identify a section. Neither the document nor its section is the **CallableUnit**.

The artifact's **RepresentationProfile** identifies an OpenSpec document convention. This is an illustrative mapping, not an implemented importer, renderer, or certified round trip. See [format mappings](specspec/format-mappings.md).

## 6. Leave an unexecuted check as `not_run`

The complete result record in the fixture is:

```turtle
@prefix spec: <https://ontologies.corestory.ai/specspec/> .
@prefix demo: <urn:specspec:demo:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

demo:comparison-result a spec:VerificationResult ;
    spec:activity demo:check ;
    spec:checked_snapshot demo:modern-snapshot ;
    spec:checks_claim demo:no-overdraft ;
    spec:id "urn:specspec:demo:comparison-result"^^xsd:anyURI ;
    spec:outcome "not_run" ;
    spec:result_anchors demo:report-anchor ;
    spec:title "Behavioral comparison pending"^^xsd:string .
```

`demo:check` records the planned verification activity and both input snapshots. The [report fixture](../examples/specspec/modernization/source/check-report.txt) explicitly says that behavioral comparison has not been executed. Validating this record checks its structure and supporting local fixture integrity; it cannot promote `not_run` to `passed`.

For a real check, record the actual activity, checked source state, scoped outcome, and result evidence. A passing result applies to that check and snapshot, not to universal behavioral equivalence.

## Trace the relationships with a query

This runnable query follows the requirement back to its source anchor and reads the comparison's recorded outcome. It reads the checked-in graph without inference or network access:

```sh
nix develop -c python - <<'PY'
from rdflib import Graph

graph = Graph().parse("examples/specspec/modernization/graph.ttl", format="turtle")
rows = graph.query("""
PREFIX spec: <https://ontologies.corestory.ai/specspec/>
PREFIX demo: <urn:specspec:demo:>
SELECT ?path ?start ?end ?outcome WHERE {
  demo:no-overdraft spec:derived_from_claims/spec:supporting_anchors ?anchor .
  ?anchor spec:path ?path ; spec:line_start ?start ; spec:line_end ?end .
  demo:comparison-result spec:checks_claim demo:no-overdraft ;
                         spec:outcome ?outcome .
}
""")
for row in rows:
    print(f"{row.path}:{row.start}-{row.end}; comparison={row.outcome}")
PY
```

The query prints:

```text
withdraw.cbl:8-12; comparison=not_run
```

## When adapting the fixture

- Give each SpecSpec knowledge record its own subject IRI and matching `spec:id` URI literal. Keep document, software, claim, and result identities separate. SAO retains its own literal `sao:id` convention; do not assume the same identity constraint applies to both models.
- Link records by RDF references and include the typed endpoint data needed for the selected profile. The fixture's **SpecificationGraph** envelope links its collections; it does not replace individual node metadata.
- Preserve supplied intent, review status, evidence revisions, and uncertainty. Replacing an implementation assertion is not a reason to rewrite the source observation.
- Run the relevant validation profile and source checks, then review evidence adequacy and behavior separately. Both models remain candidate/draft; these patterns add no new classes or semantics.

See [getting started](getting-started.md) for profile selection and [SpecSpec model notes](specspec/model.md) for the full constraint boundaries.
