# Getting started

Choose **SAO** to describe software, **SpecSpec** to describe requirements and evidence, or **ecosystem** to validate a graph that connects both. Start with the published Turtle example below; no repository access, extractor, application server, or source-program execution is required.

**New to the idea?** Read [Before the graph: tell the system’s story](start-here.md) first. It explains the purpose and example without commands or RDF prerequisites.

## Choose a profile

| Repository profile | Use it for | What the repository validator loads |
|---|---|---|
| `sao` | Systems, components, callables, data, and operating context | SAO vocabulary and SHACL shapes |
| `specspec` | Claims, requirements, scenarios, decisions, source snapshots, and verification results | SpecSpec core vocabulary and shapes, including SHACL-SPARQL rules; no SAO dependency |
| `ecosystem` | SpecSpec knowledge linked to SAO software entities | Both vocabularies, both complete SHACL profiles, and the current SpecSpec–SAO bridge |

SAO is a **3.0.0 candidate, unreleased**. SpecSpec is a **0.1.0 modeling draft**. Their namespaces and versions remain separate; `ecosystem` is a validation profile, not a third ontology. See the [catalog](../ontologies/catalog.json), [SAO overview](sao/README.md), and [SpecSpec overview](specspec/README.md). Retain the downloaded files together, or pin a repository revision when you have access; these models are not stable releases.

## Run a public example — no checkout required

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and have `curl` available. Run this in a writable directory that does not already contain `ontology-quickstart`. It downloads the SAO vocabulary, its complete SHACL profile, a minimal System instance, and their license notices as individual files. There is no ZIP and no private checkout dependency. The first `uv` invocation may download Python and packages.

<!-- public-quickstart:start -->
```sh
set -eu
SITE_BASE="${SITE_BASE:-https://ontologies.corestory.ai}"
mkdir ontology-quickstart
cd ontology-quickstart
curl --fail --silent --show-error "$SITE_BASE/dist/sao.ttl" -o sao.ttl
curl --fail --silent --show-error "$SITE_BASE/dist/sao.shacl.ttl" -o sao.shacl.ttl
curl --fail --silent --show-error "$SITE_BASE/source/examples/sao/rdf/system.ttl" -o system.ttl
curl --fail --silent --show-error "$SITE_BASE/source/LICENSE" -o LICENSE
curl --fail --silent --show-error "$SITE_BASE/source/NOTICE" -o NOTICE
uv tool run --from pyshacl==0.30.1 pyshacl \
  --metashacl --inference none --ont-graph sao.ttl --shacl sao.shacl.ttl system.ttl
```
<!-- public-quickstart:end -->

Expected output:

```text
Validation Report
Conforms: True
```

This pins pySHACL to the repository lock's `0.30.1` version, not its transitive dependencies. It meta-validates the shapes and checks the example with `inference="none"`; it does not load optional OWL axioms. To check your own SAO data, replace `system.ttl` in the final command. Give instance nodes explicit SAO RDF types: generic pySHACL can report a vacuous pass when no shapes target your data. Unlike the repository wrapper, this command does not reject that case automatically or check evidence digests and anchors.

The default URL names this site's intended public origin. When testing a candidate or a mounted preview, export `SITE_BASE` to its origin and mount path, without a trailing slash, before running the same block. A download failure exits before validation; do not replace a missing file with an HTML page or assume the origin is already deployed.

## Run all repository fixtures — repository access required

The rest of the repository commands require an authorized, complete checkout. This site's browsable source collection is a reviewed reference subset, **not** a runnable build checkout: it omits the project environment, Nix build definitions, and website build assets. Do not run `nix develop` or `uv sync` inside a downloaded source directory.

From the complete repository root, use Git and Nix with flake support. Nix supplies the Python/RDF tools; the first invocation may download dependencies. See [Nix setup and command meanings (repository access required)](nix-and-publishing.md).

```sh
nix develop -c python scripts/validate_rdf.py
```

With no data path or profile, this checks all three bundled examples. The validator output is:

```text
sao: SHACL meta-validation and conformance pass (3 data triples).
specspec: SHACL meta-validation and conformance pass (232 data triples).
ecosystem: SHACL meta-validation and conformance pass (242 data triples).
```

The SpecSpec and ecosystem defaults also check the synthetic local source fixtures: SHA-256 revisions, source paths, and anchor bounds. They do not execute the COBOL or Java excerpts. The example's behavioral comparison remains `not_run`.

If you use Python tooling without Nix, install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use the locked environment instead:

```sh
uv sync --locked
uv run --locked python scripts/validate_rdf.py
```

The project requires Python 3.13 or later. The ordinary RDF workflow does not need the optional legacy LinkML dependency group.

## Validate one graph — repository access required

These commands use real files in this repository:

```sh
# A minimal SAO System instance.
nix develop -c python scripts/validate_rdf.py --ontology sao \
  examples/sao/rdf/system.ttl

# SpecSpec claims and requirements, plus local evidence integrity checks.
nix develop -c python scripts/validate_rdf.py --ontology specspec \
  --sources examples/specspec/modernization/sources.json \
  examples/specspec/modernization/graph.ttl

# Compose and validate the bundled software, knowledge, and bridge data.
nix develop -c python scripts/validate_rdf.py --ontology ecosystem
```

For your own graph, replace the sample data path and select a profile explicitly. To validate your own combined Turtle file, append its path to the ecosystem command. Without a data path, ecosystem assembles the files in the [example manifest](../examples/ecosystem/manifest.json); it does not scan your checkout for graphs.

**Supplying a data path does not automatically enable source-file checks**, even when the path names the bundled SpecSpec example. Supply `--sources` when you want them. The [fixture manifest](../examples/specspec/modernization/sources.json) maps snapshot IRIs to files relative to the manifest's directory. Those files must stay within that directory, and their SHA-256 digests must match the graph's `spec:revision` values. The checker reads these local files; it does not fetch the graph's `source_uri` URLs.

The validator reads editable ontology sources, not `dist/`, except when you explicitly supply a distribution as an argument. Give instance nodes explicit RDF types; the CLI refuses a graph with no explicitly typed nodes recognized by the selected profile.

### Use the narrower bridge check deliberately

If you have a SpecSpec graph and only a small manifest of software identities and types, use:

```sh
nix develop -c python scripts/validate_rdf.py --ontology specspec \
  --sao-vocabulary dist/sao.ttl \
  --bridge-data examples/specspec/modernization/sao-links.ttl
```

This checks the default SpecSpec graph and bridge link endpoint types. Its output explicitly says: `Bridge endpoint types checked; full SAO instance shapes were not applied.` It is not a substitute for ecosystem validation. The [combined example](../examples/ecosystem/README.md) adds the required SAO fields so both full profiles can run against one graph.

## Keep the three layers separate

| Layer | Purpose | Example distributions |
|---|---|---|
| RDFS vocabulary | Defines classes, predicates, descriptions, and class hierarchies. Domain/range statements describe entailments, not required fields. | [sao.ttl](../dist/sao.ttl), [specspec.ttl](../dist/specspec.ttl) |
| SHACL | Checks instance constraints such as required properties, value types, allowed values, and typed references. SpecSpec also uses SHACL-SPARQL graph rules. | [sao.shacl.ttl](../dist/sao.shacl.ttl), [specspec.shacl.ttl](../dist/specspec.shacl.ttl) |
| Optional OWL | Supplies SAO inverse axioms and SpecSpec property declarations for consumers that choose to use them. It does not replace SHACL. | [sao.owl.ttl](../dist/sao.owl.ttl), [specspec.owl.ttl](../dist/specspec.owl.ttl) |

The [bridge vocabulary](../dist/specspec-sao.ttl), [bridge shapes](../dist/specspec-sao.shacl.ttl), and [bridge OWL declarations](../dist/specspec-sao.owl.ttl) contain only the integration layer; load them alongside the relevant core files. Loading a bridge distribution alone does not load either ontology. The tooling uses explicit local manifests, not automatic network imports.

SHACL validation uses the vocabulary's class hierarchy but runs with `inference="none"`; it does not materialize optional OWL inferences. A SHACL Core-only processor cannot run every SpecSpec rule.

**Conformance is not truth.** A pass says the supplied graph meets the applied constraints. It does not establish extraction completeness, evidence adequacy, correct implementation, or behavioral equivalence. Digest and anchor checks establish local fixture integrity, not the truth of a claim about those bytes. See [SpecSpec model boundaries](specspec/model.md) and [SAO validation limits](sao/turtle-migration.md).

## Read failures and check your checkout — repository access required

- A SHACL failure exits nonzero and reports the affected node, property or rule. Compare it with the selected profile's shapes; adding OWL reasoning is not a fix for missing required data.
- A missing profile for a supplied data file is a CLI error. Choose `sao`, `specspec`, or `ecosystem`.
- A fixture digest, path, or anchor error means the graph and local evidence files disagree. Inspect the source revision and anchor before changing either.

These read-only checks help distinguish graph errors from repository drift:

```sh
nix develop -c python scripts/build_rdf.py --check
nix develop -c python scripts/validate_axioms.py
nix develop -c python -m unittest discover -s tests
```

The first checks that committed distributions match their editable sources. The second checks the ontology supplements; it does not verify your software. The third runs the regression suite.

Continue with [modeling patterns](modeling-patterns.md) for the overdraft example. For current SAO relationship names, consult the [3.0.0 migration notes](sao/migration-3.0.md): many longer SAO guides describe the retained LinkML baseline. For contribution rules, see [CONTRIBUTING.md](../CONTRIBUTING.md).
