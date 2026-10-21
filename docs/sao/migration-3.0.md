# SAO 3.0.0 candidate: relationship redesign

This is a tentative, unreleased major-version bump. It changes the RDF relationship contract and graph validation. It is not a published release or a claim that all LinkML semantics have been migrated. The ontology namespace and class IRIs stay unchanged.

## Generic relationships

| Forward predicate | Inverse | Allowed class pairs |
|---|---|---|
| `has_versions` | `version_of` | Contract → ContractVersion; Schema → SchemaVersion |
| `contains_entries` | `entry_in` | AuditLog → AuditEntry; Log → LogEntry |
| `uses` | `used_by_callables` | CallableUnit → FileDefinition or ConcurrencyPrimitive |
| `has_constraints` | `constrains` | Collection → DatabaseConstraint; Permission → authorization Constraint |
| `contains_unit_members` | `contained_in_unit` | EncapsulationUnit → CallableUnit, DataStructure, or DataElement (including subclasses) |

SHACL keeps the class pairings specific. For example, Contract cannot have a SchemaVersion merely because both use `has_versions`. No common version, entry, resource, or constraint superclass is introduced to achieve this.

The reverse `constrains` relation remains single-valued on DatabaseConstraint, preserving its existing collection ownership. Authorization Constraint may constrain multiple Permissions; no exclusive ownership is assumed. Existing single-value and required constraints elsewhere are preserved.

## Participant roles remain distinct

| Relation | Inverse |
|---|---|
| Actor `owns_subscriptions` Subscription | Subscription `subscribed_by_actor` Actor |
| EventInterface `subscriptions_to_interface` Subscription | Subscription `subscribes_to_interface` EventInterface |
| FileDefinition `operations_on_file` FileOperation | FileOperation `operates_on_file` FileDefinition |
| CallableUnit `operations_in_callable` FileOperation | FileOperation `performed_in_callable` CallableUnit |

Subscriber versus subscribed-to interface, and operated-on file versus performing callable, remain different roles. They are not inferred from one vague inverse relation.

## Typed unit membership

`contains_callable_units`, `contains_data_structures`, and new `unit_contains_data_elements` are subproperties of `contains_unit_members`. Their asserted edges imply generic membership and thus the `contained_in_unit` inverse.

`unit_contains_data_elements` is also a subproperty of `contains_data_elements`. Generic `contains_data_elements` remains valid on EncapsulationUnit and DataStructure, but is not globally a subproperty of unit membership: a structure's field must not make the structure an encapsulation unit. Use the new unit-specific predicate when asserting direct unit data membership and expecting its inverse entailment. The broader predicate remains a useful projection, not a complete substitute for the unit-specific assertion.

Generic membership does not automatically populate the type-specific indexes. For example, `contained_in_unit` on a DataElement yields `contains_unit_members`, not `contains_callable_units`.

## Data and producer migration

| Old predicate | Replacement |
|---|---|
| `version_of_contract`, `version_of_schema` | `version_of` |
| `entry_in_audit_log`, `entry_in_log` | `entry_in` |
| `uses_file_definitions`, `uses_concurrency_primitives` | `uses`; merge and deduplicate the old resource lists |
| `constraint_on_collection` | `constrains` |
| Actor `has_subscriptions` | `owns_subscriptions` |
| EventInterface `has_subscriptions` | `subscriptions_to_interface` |
| FileDefinition `has_file_operations` | `operations_on_file` |
| CallableUnit `has_file_operations` | `operations_in_callable` |
| EncapsulationUnit `contains_data_elements` asserted as direct unit membership | Prefer `unit_contains_data_elements`; structure containment stays `contains_data_elements` |

Update internal extraction predicates, query templates, graph fixtures, and stored edges. Do not choose a role replacement from an untyped or ambiguously typed subject without resolving its intended role. No automatic rewrite is performed by loading the ontology.

Nine replaced predicates retain only retirement metadata (`owl:deprecated true`) for identification and migration diagnostics. They have no compatibility aliases, inverses, or class/range semantics in the new contract. SHACL explicitly rejects their use even though the overall profile remains open. This prevents an old graph from appearing conformant merely because its replaced edges were ignored.

Do not reuse old specific inverse IRIs as aliases for the generic inverse: that would reintroduce the original cross-type inference problem. Original 2.1.0 YAML, legacy examples, and the inverse audit remain historical baselines and are not relabeled 3.0.0.

## Verification

The profile now has 217 uniquely paired inverse axioms. Regression tests cover positive and negative class pairs, heterogeneous callable resources, distinct participant roles, typed membership and inverse materialization, retired predicate rejection, and version metadata consistency. The normal SHACL command still validates without OWL materialization; reasoning is an explicit consumer choice.

```sh
uv run python scripts/build_rdf.py
uv run python scripts/validate_axioms.py
uv run python scripts/validate_rdf.py
uv run python -m unittest discover -s tests
```

Version 3.0.0 is proposed in the RDF and project metadata for review. No release tag, package publication, or CDN deployment is created by this change.
