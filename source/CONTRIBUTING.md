# Contributing to CoreStory Ontologies

Edit the appropriate ontology under `ontologies/sao/` or `ontologies/specspec/`. Vocabulary, validation shapes and reasoning axioms are separate Turtle layers. Add or remove files in the matching manifest. Do not edit assembled files under `dist/` directly.

Run `nix flake check` and `nix build` as described in the root README, then include the rebuilt distributions with your source edits. The default checks cover both ontologies and their composition. Add focused valid/invalid examples for changes to constraints or relationships. Shared tooling and tests must work without a sibling SpecSpec checkout.

Class and property IRIs, ranges, required fields, and OWL implications are compatibility contracts. A shared repository permits one PR to update both ontologies, but changes in meaning still need explicit modeling review and migration guidance. This layout change does not authorize redesigning or removing the existing bridge.

Ontology versions live in `ontologies/catalog.json` and RDF metadata; update both deliberately when changing a module version. The root Python package version belongs to the tooling, not either ontology. Separate namespace/version identities do not require separate repositories or lockstep semantic-version bumps.

Use one repository-level [changelog](CHANGELOG.md) for shared tooling/layout changes and the ontology-specific changelogs for model changes: [SAO](docs/sao/CHANGELOG.md), [SpecSpec](docs/specspec/CHANGELOG.md).

Historical LinkML commands and tests are documented under [legacy/sao/](legacy/sao/README.md). They use an optional Python dependency group for manual historical comparisons and are not part of active CI. Do not regenerate editable Turtle sources from the legacy model.

Keep terms self-documenting and examples synthetic. Avoid private implementation vocabularies and customer data. Retain corporate and original-author attribution. Contributions are submitted under Apache License 2.0, consistent with Section 5 of [LICENSE](LICENSE).
