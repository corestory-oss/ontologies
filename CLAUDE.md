# Project: Software Application Ontology (SAO)

## Style conventions for guide.md

### Two-tier formatting for ontology names

- **Bold** for class and entity names in prose (e.g., **ControlFlow**, **DataStore**, **Actor**). Bold flows naturally in sentences, signals "this is an important concept," and is easy to spot when skimming.
- **Monospace** for enum values, attribute names, and literal identifiers (e.g., `web_ui`, `rest_api`, `contained_in_unit`). Monospace signals "this is the exact string in `sao.yml`."
- When a class name appears as part of a dotted-path reference (e.g., `Component.implemented_by_code`), use monospace — the whole expression is a literal identifier.

### Enum value listings

- When referencing enum/type values that are defined as `permissible_values` in `sao.yml`, always use the exact enum value name in monospace backticks (e.g., `web_ui`, not "web UI" or "Web UI").
- When listing enum values in bullet points, list each value as an individual sub-bullet under the main bullet, in monospace.
- In table cells where sub-bullets aren't feasible, use monospace backticks inline (e.g., `create`, `update`, `delete`).
- Use the actual permissible_value names from sao.yml, not paraphrased/human-friendly names.
