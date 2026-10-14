# Inverse relationship audit and OWL supplement

`rdf/axioms/relationships.ttl` is editable source for the optional inverse supplement. `sao.owl.ttl` is its assembled distribution, not a replacement for `sao.ttl`. Load the vocabulary plus supplement using `rdf/manifests/reasoning.json`, or load the two complete distributions into one graph. There are no `owl:imports` and no automatic network fetches.

## What was carried over

The retained SAO 2.1.0 baseline contains 536 contextual inverse declarations across 435 property IRIs. This includes inherited uses and declared global slots. The audit resolves names against both global and class-local properties and checks that endpoints exist in the Turtle vocabulary. It checks reciprocal uniqueness, resource-valued ranges, all uses of each property (including uses with no local inverse declaration), and whether the inverse on each range class can point back to the declaring class under the named class hierarchy.

208 pairs pass these checks. Each is emitted once as `owl:inverseOf`, with both endpoints declared `owl:ObjectProperty`. OWL inverse relationships are symmetric: one axiom supports inference in both directions. The supplement contains 627 triples, including metadata. This is a declaration-consistency check, not a proof of arbitrary graph conformance.

No declared inverse name was missing when resolved against the complete property vocabulary. The earlier standard SHACL generator error involved a class-local property that its lookup did not resolve, rather than a missing RDF property.

## Seven unresolved groups

| Shared property | Competing or incompatible inverse declarations | Decision needed |
|---|---|---|
| `has_subscriptions` | `subscribed_by_actor`, `subscribes_to_interface` | Separate actor subscriptions from interface subscriptions, or define a different shared relationship model. |
| `has_file_operations` | `operates_on_file`, `performed_in_callable` | Separate file and callable ownership/context. |
| `has_versions` | `version_of_contract`, `version_of_schema` | Decide whether to use separate version relations or a genuinely generic version model. |
| `contains_entries` | `entry_in_audit_log`, `entry_in_log` | Decide whether audit and operational entries share one modeled containment relation. |
| `used_by_callables` | `uses_concurrency_primitives`, `uses_file_definitions` | Separate resource-specific inverse relationships or explicitly model generic callable usage. |
| `has_constraints` | `constraint_on_collection` | Collection uses refer to DatabaseConstraint, while Permission uses the same property for authorization Constraint without declaring an inverse. A global axiom would incorrectly apply to both. |
| `contained_in_unit` | `contains_callable_units` | The forward slot is also used by DataStructure and DataElement (inherited by Parameter), but the reverse slot accepts CallableUnit. Decide the intended containment relations. |

All 19 properties participating in these groups are withheld from the inverse supplement; their original vocabulary and shapes are unchanged. Adding several global inverse axioms for one shared property would entail equivalence between the competing inverse properties. Class-local intended meanings cannot be recovered merely by applying global `owl:inverseOf` axioms.

The detailed declarations, class contexts, and reasons are in [inverse-audit.json](inverse-audit.json). This report is a historical migration snapshot. Normal builds do not regenerate the editable OWL source from LinkML.

## Validation and inference

```sh
uv run python scripts/build_rdf.py
uv run python scripts/validate_axioms.py
uv run python -m unittest discover -s tests
```

The check reads the current Turtle shapes to ensure all class-local ranges can participate in the inverse, checks that inverse endpoints exist, the supplement retains uniquely paired partners, and the reasoning manifest assembles precisely the vocabulary plus axioms. Regression tests use an actual OWL-RL reasoner to infer the reverse edge for every accepted pair in both directions. They also test that withheld properties do not acquire those inverse entailments.

The SHACL validator continues to run without OWL materialization. Enabling inference before validation can change conformance results, particularly where required reverse relationships become inferred instead of explicitly supplied. Loading `sao.owl.ttl` alone does not execute reasoning; a consumer must invoke a suitable reasoner.

See the [OWL 2 property axiom specification](https://www.w3.org/TR/owl2-syntax/#Inverse_Object_Properties) for inverse semantics. The remaining modeling decisions above are deliberately not resolved by this mechanical migration.
