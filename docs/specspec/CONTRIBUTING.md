# Contributing to SpecSpec

Follow the shared [repository contribution guide](../../CONTRIBUTING.md). Run commands from the repository root.

Edit the appropriate Turtle module under `ontologies/specspec/vocabulary/`, `shapes/` or `axioms/`, and update the corresponding manifest for new files. Existing SAO link definitions remain under `ontologies/specspec/bridges/sao/` pending a separate modeling decision. Keep the independent core free of a mandatory SAO dependency.

The migration baseline and regression tests document the original draft's class IRIs and constraints. A deliberate model change should update them and explain compatibility implications. Do not silently broaden the model during a tooling change.

Use `uv run python scripts/validate_rdf.py --ontology specspec` for the independent example, or `--ontology ecosystem` for full composition with SAO. To reproduce the narrower endpoint-type bridge check:

```sh
uv run python scripts/validate_rdf.py --ontology specspec \
  --sao-vocabulary dist/sao.ttl \
  --bridge-data examples/specspec/modernization/sao-links.ttl
```

The endpoint-type check does not apply the full SAO instance shapes. The ecosystem profile does, using the completed synthetic callable example.
