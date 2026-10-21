# SAO legacy LinkML baseline

This is the retained SAO 2.1.0 comparison model. The current SAO 3.0.0 candidate is authored in Turtle under `ontologies/sao/`; SpecSpec is authored under `ontologies/specspec/`. The legacy model is intentionally not relabeled as the newer RDF contract.

From the repository root:

```sh
uv sync --locked --group legacy
uv run --group legacy linkml-lint --validate-only legacy/sao/sao.yml
uv run --group legacy python scripts/migration/sao/check_schema.py
uv run --group legacy python -m unittest discover -s legacy/sao/tests
uv run --group legacy gen-json-schema legacy/sao/sao.yml > /tmp/sao.schema.json
uv run --group legacy gen-doc --render-imports --directory /tmp/sao-reference legacy/sao/sao.yml
uv run --group legacy linkml-validate --exit-on-first-failure -s legacy/sao/sao.yml -C System examples/sao/system.yaml
uv run --group legacy linkml-validate --exit-on-first-failure -s legacy/sao/sao.yml -C Aggregate examples/sao/aggregate.yaml
uv run --group legacy linkml-validate --exit-on-first-failure -s legacy/sao/sao.yml -C Integration examples/sao/integration.yaml
```

The schema's local module imports remain unchanged. Migration tools under `scripts/migration/sao/` default to this relocated schema and require explicit output paths for one-time generation. Do not use them to overwrite current Turtle sources. The historical baseline is archived, is not checked by CI, and is not imported by the normal RDF build or test suite. The commands above remain available for manual historical comparisons.
