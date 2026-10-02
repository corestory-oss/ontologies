# Contributing to SAO

SAO is a LinkML schema and documentation project. `sao.yml` is the entry point
for the authoritative schema modules in `schema/`; `CHANGELOG.md` records changes
and migration guidance.

## Setup and checks

Install uv, then run from the repository root:

```bash
uv sync --locked
uv run linkml-lint --validate-only sao.yml
uv run python scripts/check_schema.py
uv run gen-json-schema sao.yml > /tmp/sao.schema.json
uv run linkml-validate --exit-on-first-failure -s sao.yml -C System examples/system.yaml
uv run linkml-validate --exit-on-first-failure -s sao.yml -C Aggregate examples/aggregate.yaml
uv run linkml-validate --exit-on-first-failure -s sao.yml -C Integration examples/integration.yaml
```

The metamodel check validates schema structure. Instance validation checks the
selected target class; it does not verify that every referenced ID exists in a
complete graph or that inverse relationships have been populated.

## Editing schema modules

Edit the existing definition in its topic file under `schema/`. Shared enums,
types, base classes, and global slots belong in `schema/common.yaml`. If you add
a module, add its extension-free relative path to the imports in `sao.yml`.
Imported files use `.yaml`, as expected by LinkML's relative-import resolver.
Keep the `sao` prefix and default range consistent across modules. Validate and
generate from the root entry point so cross-topic references resolve.

The import check rejects duplicate definitions that LinkML could otherwise
silently shadow. For a mechanical reorganization, compare against an earlier
schema snapshot as well:

```bash
uv run python scripts/check_schema.py --compare /tmp/sao-before.yml
```

This compares resolved definitions (including descriptions and comments),
inherited attributes and constraints, root metadata, and expanded term IRIs.
Only source-file and import provenance are excluded from the comparison. A
baseline with local imports must retain its accompanying module files.

## Proposing a change

Open an issue or pull request in this repository. Explain the modeling need,
include a small example, and describe compatibility or migration implications.
Update affected documentation and examples alongside schema changes. Record
user-visible changes under the Unreleased section of `CHANGELOG.md`.

For ontology names in prose, use **bold** for class names and `monospace` for
attribute names, enum values, and dotted paths. Use exact names from `sao.yml`.

Do not submit credentials, private customer data, or material you do not have
permission to contribute. Identify copied or adapted third-party material,
its source, and its license so maintainers can review required attribution.

## Licensing contributions

By intentionally submitting a contribution for inclusion in SAO, you submit it
under the Apache License, Version 2.0, unless you explicitly state otherwise,
consistent with Section 5 of [LICENSE](LICENSE). Retain existing attribution.
