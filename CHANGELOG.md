# Changelog

All notable changes to the Software Application Ontology (SAO) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Enrich LinkML attribute, shared-slot, and enum value descriptions from the
  existing documentation, and add class-purpose comments without changing the model.
- Replace the placeholder schema ID and term prefix with `https://sao.corestory.ai/`.
  Consumers using the old namespace must update schema references and term IRIs.
- Prepare the repository for Apache License 2.0 distribution: replace the
  proprietary license, add attribution, and align project metadata.
- Refresh the README for schema version 2.1.0 and add validated instance examples.
- Add contribution guidance and CI checks for schema and example validation.

## [2.1.0] - 2026-04-18

This release standardizes the naming convention for relationship attributes. Every plain-noun relationship attribute has been renamed to a verb-prefixed form so the ontology reads uniformly across all layers.

### Rename rule

- `contains_*` when the inverse is `part_of_*` or `contained_in_*` (composition).
- `has_*` otherwise (association).

### Removed

Four v2.0-migration-leftover attributes that duplicated newer relationships:

| Class | Removed attribute | Use instead |
|---|---|---|
| `UserInterface` | `screens` | `contains_screens` (renamed from `ui_screens`) |
| `AuditLog` | `entries` | `contains_entries` (renamed from `audit_log_entries`) |
| `Log` | `entries` | `contains_entries` (renamed from `log_entries`) |
| `Trace` | `spans` | `contains_spans` (renamed from `trace_spans`) |

### Changed — forward attribute renames

Simple-collection attributes (renamed to `has_*` or `contains_*`):

| Class | Old name | New name |
|---|---|---|
| `Actor` | `actor_subscriptions` | `has_subscriptions` |
| `Aggregate` | `value_objects` | `has_value_objects` |
| `AuditLog` | `audit_log_entries` | `contains_entries` |
| `BuildPipeline` | `stages` | `has_stages` |
| `CallableUnit` | `callable_file_operations` | `has_file_operations` |
| `CallableUnit` | `return_type_expression` | `has_return_type` |
| `CodeContainer` | `container_file_definitions` | `has_file_definitions` |
| `CodeContainer` | `container_preprocessor_directives` | `has_preprocessor_directives` |
| `CodeContainer` | `container_screen_definitions` | `has_screen_definitions` |
| `ComplianceRequirement` | `controls` | `has_controls` |
| `Component` | `dependencies` | `has_dependencies` |
| `Contract` | `contract_versions` | `has_versions` |
| `Control` | `evidence` | `has_evidence` |
| `DataElement` | `ownership_annotations` | `has_ownership_annotations` |
| `DataPipeline` | `steps` | `has_steps` |
| `DataStore` | `collections` | `has_collections` |
| `Dataset` | `schema` | `has_schema` |
| `Dependency` | `target` | `has_target` |
| `Endpoint` | `operations` | `has_operations` |
| `FileDefinition` | `file_operations` | `has_file_operations` |
| `IaCDefinition` | `resources` | `has_resources` |
| `Identity` | `credentials` | `has_credentials` |
| `Integration` | `messages` | `has_messages` |
| `Lifecycle` | `states` | `has_states` |
| `Lifecycle` | `transitions` | `has_transitions` |
| `Log` | `log_entries` | `contains_entries` |
| `MLModel` | `input_schema` | `has_input_schema` |
| `MLModel` | `metrics` | `has_metrics` |
| `MLModel` | `output_schema` | `has_output_schema` |
| `Module` | `dependencies` | `has_dependencies` |
| `PackageDependency` | `known_vulnerabilities` | `has_known_vulnerabilities` |
| `Parameter` | `parameter_type` | `has_type` |
| `Permission` | `constraints` | `has_constraints` |
| `Policy` | `rules` | `has_rules` |
| `ProgrammingLanguage` | `default_error_model` | `has_default_error_model` |
| `ProgrammingLanguage` | `default_memory_model` | `has_default_memory_model` |
| `Release` | `artifacts` | `has_artifacts` |
| `Schema` | `schema_versions` | `has_versions` |
| `Service` | `health_checks` | `has_health_checks` |
| `StateStore` | `state_shape` | `has_state_shape` |
| `Tenant` | `organizations` | `has_organizations` |
| `Tenant` | `settings` | `has_settings` |
| `TestCase` | `assertions` | `has_assertions` |
| `Trace` | `trace_spans` | `contains_spans` |
| `TypeExpression` | `type_parameters` | `has_type_parameters` |
| `UIComponent` | `props` | `has_props` |
| `UserInterface` | `ui_screens` | `contains_screens` |
| `ValueObject` | `attributes` | `has_attributes` |
| `Workflow` | `steps` | `has_steps` |

Tree/role/directional attributes (renamed to `has_*` for uniformity):

| Class | Old name | New name |
|---|---|---|
| `CodeBlock` | `parent_block` | `has_parent_block` |
| `CodeBlock` | `child_blocks` | `has_child_blocks` |
| `ControlFlow` | `source_callable` | `has_source_callable` |
| `ControlFlow` | `target_callable` | `has_target_callable` |
| `ControlFlow` | `source_statement` | `has_source_statement` |
| `ControlFlow` | `target_statement` | `has_target_statement` |
| `DataElement` | `parent_element` | `has_parent_element` |
| `DataElement` | `child_elements` | `has_child_elements` |
| `DataFlow` | `source_element` | `has_source_element` |
| `DataFlow` | `target_element` | `has_target_element` |
| `DataFlow` | `through_callable` | `has_through_callable` |
| `DataFlow` | `through_statement` | `has_through_statement` |
| `DataStructure` | `parent_structure` | `has_parent_structure` |
| `DataStructure` | `child_structures` | `has_child_structures` |
| `DomainEntity` | `incoming_relationships` | `has_incoming_relationships` |
| `DomainEntity` | `outgoing_relationships` | `has_outgoing_relationships` |
| `DomainRelationship` | `source_entity` | `has_source_entity` |
| `DomainRelationship` | `target_entity` | `has_target_entity` |
| `EncapsulationUnit` | `incoming_ipc_connections` | `has_incoming_ipc_connections` |
| `EncapsulationUnit` | `outgoing_ipc_connections` | `has_outgoing_ipc_connections` |
| `ExceptionType` | `parent_exception` | `has_parent_exception` |
| `ExceptionType` | `child_exceptions` | `has_child_exceptions` |
| `IaCModule` | `child_resources` | `has_child_resources` |
| `IPCConnection` | `ipc_source_program` | `has_source_program` |
| `IPCConnection` | `ipc_target_program` | `has_target_program` |
| `Organization` | `parent` | `has_parent` |
| `Organization` | `children` | `has_children` |
| `Route` | `parent_route` | `has_parent_route` |
| `Route` | `child_routes` | `has_child_routes` |
| `StorageLocation` | `parent_location` | `has_parent_location` |
| `UIComponent` | `parent_ui_component` | `has_parent_ui_component` |
| `UIComponent` | `child_ui_components` | `has_child_ui_components` |

### Added

- New inverse relationships on target classes for a subset of the renamed
  attributes that previously lacked an inverse (e.g., `ValueObject.belongs_to_aggregate`,
  `Credential.credential_for_identity`, `Configuration.setting_for_tenant`,
  `Organization.organization_in_tenant`). The remaining forward-only relationships
  retain single-direction traversal semantics as before; a follow-up pass may
  add inverses across the board if bidirectional traversal is needed.
- `DataPipeline.pipeline_trains_model` (the inverse of `MLModel.model_trained_by_pipeline`).
  The inverse was previously declared on `BuildPipeline` by mistake, leaving
  the `MLModel → DataPipeline` side dangling. Moved to the correct class.

### Fixed

- `BuildPipeline.pipeline_trains_model` removed; ML model training is a
  `DataPipeline` concern, not a CI/CD concern. The attribute now lives on
  `DataPipeline`.

### Migration guide

Consumers of the ontology should update queries and tooling as follows:

1. Replace every old attribute name with its new name per the tables above.
2. Any code that relied on the removed duplicate attributes (`UserInterface.screens`,
   `AuditLog.entries`, `Log.entries`, `Trace.spans`) must switch to the
   canonical `contains_*` replacement.

### Documentation

The authoritative reference for v2.1 is `sao.yml` itself. The `docs/` tree has
been updated for the most-distinctive renames (e.g., `ui_screens` → `contains_screens`,
`default_error_model` → `has_default_error_model`) but some ambiguous names that
also appear as prose in the docs (e.g., "entries," "steps," "rules") may still
reference the old attribute names in explanatory text. A full documentation
sweep is tracked as a follow-up.

## [2.0.0]

- See git history for v2.0 changes; prior to this release the repository did
  not maintain a changelog. Key v2.0 work: inlining single-use relationship
  slots as class attributes, code-structure layer expansion, and introduction
  of the bidirectional-relationship pattern that v2.1 generalizes.
