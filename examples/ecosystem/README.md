# Combined modernization fixture

`manifest.json` composes the existing SpecSpec modernization graph and bridge links with `software.ttl`. The latter supplies the required SAO fields for the example Java callable, extending the earlier type-only manifest into a graph that can pass both validation profiles.

Run `uv run python scripts/validate_rdf.py --ontology ecosystem` from the repository root. This applies both complete SHACL profiles and the current bridge shapes to one graph, then verifies the original local evidence fixtures. No inference is materialized and no source program is executed. All data is synthetic.

The independent SpecSpec example remains valid without SAO. Its endpoint-type bridge check is intentionally narrower than this full composition check.
