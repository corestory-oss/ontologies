# Changelog

## Unreleased proposal: term mapping link

- Add **TermMappingLink** to the optional SAO bridge. It records that a SAO **GlossaryTerm** matches a term in another glossary, using SKOS mapping kinds (`exact_match`, `close_match`, `broad_match`, `narrow_match`, `related_match`), and requires a basis **Claim** for origin, confidence, and review. A mapping never merges terms.
- Core SpecSpec is unchanged and does not depend on the bridge. No inference axioms are added.

## 0.1.0 — initial draft

- Independent specification and evidence core, now authored as modular Turtle.
- RDFS vocabulary, SHACL/SHACL-SPARQL validation, optional OWL property declarations and explicit distribution manifests, following SAO's layout.
- LinkML authoring and generated JSON Schema tooling replaced by RDFLib, pySHACL and owlrl.
- Original class/property contracts and synthetic instance identities retained, with documented RDF representation differences and regression coverage.
- Optional SAO bridge; no SAO definitions are relocated or modified.
- Source-grounded modernization example and illustrative external format mappings.
