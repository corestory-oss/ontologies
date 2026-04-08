# Validation

**Input:** Complete extraction outputs from all 8 phases (Phases 1--8)
**Output:** Validated SAO instance, gap report, coverage metrics

---

## 1. Overview

Validation is the quality assurance gate that ensures the extracted ontology is structurally valid, relationally complete, and semantically coherent. It operates at three levels:

1. **Structural validation** — Does the output conform to the LinkML schema (`sao.yml`)? Required attributes present, enum values valid, types correct.
2. **Relational validation** — Are all relationships bidirectionally symmetric, referentially intact, and populated where required?
3. **Semantic validation** — Does the extraction make business sense? Are bounded context boundaries reasonable? Do capabilities match what the system actually does?

Validation runs after all phases complete, but individual phases MAY also be validated incrementally. Running `linkml-validate` after each phase catches structural issues early and avoids compounding errors across phases.

---

## 2. Structural Validation

### 2.1 Running `linkml-validate`

The primary structural validation tool is `linkml-validate` from the LinkML toolkit. Run it against the extraction output:

```bash
linkml-validate -s sao.yml extracted-output.yaml
```

This checks:

- **Required attributes** — Every instance has all attributes marked as `required: true` in the schema
- **Enum value validity** — Every enum-typed attribute uses a value from the schema's `permissible_values`
- **Type correctness** — Strings are strings, integers are integers, lists are lists
- **Cardinality constraints** — `multivalued: true` attributes contain lists; single-valued attributes contain scalars
- **Class validity** — Every instance uses a class name defined in the schema

### 2.2 Common Errors and Fixes

**Missing required field:**
```
Validation error: 'name' is a required property
  in EncapsulationUnit at index 14
```
Fix: Go back to the phase that produced this instance and populate the missing attribute. Every **EncapsulationUnit** MUST have a `name`.

**Misspelled enum value:**
```
Validation error: 'rest-api' is not valid under any of the given schemas
  in Interface at index 3, attribute 'interface_type'
```
Fix: Use the exact `permissible_values` from `sao.yml`. The correct value is `rest_api`, not `rest-api`. Enum values in SAO use underscores, not hyphens.

**Wrong data type:**
```
Validation error: 42 is not of type 'string'
  in CallableUnit at index 7, attribute 'name'
```
Fix: Ensure the value is a string. Wrap numeric-looking names in quotes in YAML.

**Scalar where list expected:**
```
Validation error: 'OrderService' is not of type 'array'
  in Module at index 2, attribute 'contains_components'
```
Fix: Use a YAML list even for single values:
```yaml
contains_components:
  - OrderService
```

**Unknown class name:**
```
Validation error: 'Microservice' is not a valid class
```
Fix: SAO does not define a **Microservice** class. Use **Service** with `service_type: microservice` instead. Consult the guide or `sao.yml` for the correct class.

### 2.3 Incremental Validation

The extraction agent SHOULD run `linkml-validate` after completing each phase, not just at the end. This catches issues before downstream phases build on invalid data:

```bash
# After Phase 1
linkml-validate -s sao.yml phase1-output.yaml

# After Phase 2 (append to growing output)
linkml-validate -s sao.yml phases1-2-output.yaml
```

---

## 3. Relational Validation

Structural validation confirms that individual instances are well-formed. Relational validation confirms that the relationships between instances are correct and complete.

### 3.1 Bidirectional Symmetry

Every bidirectional relationship pair in SAO MUST be symmetric. If entity A references entity B through a relationship, entity B MUST reference entity A through the inverse relationship.

**Example:** If `Module.contains_components` includes **OrderComponent**, then `Component.part_of_module` on **OrderComponent** MUST reference that **Module**.

The SAO defines 214+ bidirectional relationship pairs (see guide.md Appendix C). The extraction agent MUST verify symmetry for every populated pair.

**Systematic verification approach:**

1. Collect all relationship pairs from the extraction output
2. For each pair (e.g., `contains_components` / `part_of_module`):
   - Iterate over all instances of the source class
   - For each reference in the forward relationship, verify the inverse exists on the target
   - For each reference in the inverse relationship, verify the forward exists on the source
3. Report any asymmetries as errors

**Common asymmetry causes:**
- Entity added in one phase but the inverse relationship populated in a different phase, and one was skipped
- Copy-paste errors when manually building YAML
- Phase 7 (Bridge Stitching) not run or incomplete

### 3.2 Referential Integrity

Every reference MUST point to an entity that exists in the extraction output. The extraction agent MUST check for:

- **Dangling references** — A relationship attribute references an ID that does not correspond to any instance in the output. For example, `Component.implemented_by_code` references `UserService` but no **EncapsulationUnit** with that ID exists.
- **Duplicate IDs** — Two instances of the same class share the same `id`. Every entity MUST have a unique identifier within its class.
- **Cross-class type errors** — A relationship references an entity of the wrong class. For example, `Module.contains_components` references a **CallableUnit** instead of a **Component**.

**Verification approach:**

1. Build an index of all entity IDs, grouped by class
2. For every relationship attribute on every instance, verify the referenced ID exists and is the correct class
3. Check for duplicate IDs within each class

### 3.3 Required Relationships

Certain relationships are essential for a coherent SAO instance. The following table lists relationships that MUST or SHOULD be populated for key classes:

| Class | Relationship | Target | Requirement |
|---|---|---|---|
| **EncapsulationUnit** | `defined_in_container` | **CodeContainer** | MUST |
| **CallableUnit** | `contained_in_unit` | **EncapsulationUnit** | MUST |
| **DataStructure** | `defined_in_unit` | **EncapsulationUnit** | MUST |
| **DataElement** | `part_of_structure` | **DataStructure** | MUST |
| **Component** | `implemented_by_code` | **EncapsulationUnit** | MUST |
| **Component** | `part_of_module` | **Module** | MUST |
| **Module** | `mapped_from_directory` | **StorageLocation** | MUST |
| **Module** | `part_of_context` | **BoundedContext** | MUST |
| **BoundedContext** | `part_of_system` | **System** | MUST |
| **DomainEntity** | `mapped_from_structure` | **DataStructure** | MUST |
| **Aggregate** | `has_root_entity` | **DomainEntity** | MUST |
| **Operation** | `implemented_by_callables` | **CallableUnit** | MUST |
| **Service** | `runs_module` | **Module** | SHOULD |
| **Capability** | `provided_by_modules` | **Module** | SHOULD |
| **Feature** | `realizes_capabilities` | **Capability** | SHOULD |
| **Workflow** | `has_steps` | **Step** | MUST |
| **Rule** | `enforced_by` | **CallableUnit** | SHOULD |
| **Interface** | `exposed_by_component` | **Component** | SHOULD |

An entity missing a MUST relationship is an extraction error that MUST be corrected. An entity missing a SHOULD relationship SHOULD be investigated -- it may indicate a gap in extraction or a legitimate case where the relationship does not apply.

---

## 4. Completeness Checks

Beyond individual relationship correctness, the extraction agent MUST verify overall coverage. Use this checklist to assess whether the extraction captured the full scope of the codebase:

### 4.1 Containment Chain Completeness

- [ ] Every source file in scope has a corresponding **CodeContainer**
- [ ] Every **CodeContainer** maps to at least one **EncapsulationUnit** (unless the file is pure configuration, a script with no classes/modules, or a data file)
- [ ] Every **EncapsulationUnit** contains at least one **CallableUnit** or **DataStructure** (unless it is an empty marker class or interface)
- [ ] Every **Component** maps to at least one **EncapsulationUnit** via `implemented_by_code`
- [ ] Every **Module** contains at least one **Component** via `contains_components`
- [ ] Every **BoundedContext** contains at least one **Module** via `contains_modules`
- [ ] The **System** contains at least one **BoundedContext** via `has_bounded_contexts`

### 4.2 Domain Model Completeness

- [ ] Every **DomainEntity** has at least one **Attribute** (entities without attributes are likely extraction gaps)
- [ ] Every **Aggregate** has a root **DomainEntity** via `has_root_entity`
- [ ] Every **DomainEntity** links back to a **DataStructure** via `mapped_from_structure`
- [ ] **ValueObjects** identified where appropriate (immutable, identity-less data types)

### 4.3 Business Intent Completeness

- [ ] At least one **HumanActor** or **SystemActor** exists
- [ ] **Operations** exist for key business workflows (CRUD, domain-specific actions)
- [ ] Every **Operation** traces to at least one **CallableUnit** via `implemented_by_callables`
- [ ] **Capabilities** exist for each major functional area
- [ ] **Features** link to **Capabilities** via `realizes_capabilities`

### 4.4 Cross-Cutting Completeness

- [ ] **Deployments** exist if deployment manifests were provided
- [ ] **TestSuites** exist if test files were found in Phase 1
- [ ] **Roles** and **Permissions** exist if authentication/authorization code was found
- [ ] **KnowledgeArtifacts** link to the entities they document

---

## 5. Coverage Metrics

Quantitative metrics help assess extraction quality and identify areas needing attention.

### 5.1 File Coverage

**Definition:** The percentage of source files in scope that have a **CodeContainer** with at least one **EncapsulationUnit** parsed from them.

```
file_coverage = (files_with_encapsulation_units / total_source_files) * 100
```

| Threshold | Assessment |
|---|---|
| > 90% | Good -- most code is captured |
| 70--90% | Acceptable -- review uncovered files for extraction gaps |
| < 70% | Needs work -- significant portions of the codebase are missing |

Files legitimately excluded from encapsulation unit parsing (config files, static assets, data files) SHOULD be documented but not counted against coverage.

### 5.2 Class Instantiation

**Definition:** The percentage of the 147 SAO classes that have at least one instance in the extraction output.

```
class_instantiation = (classes_with_instances / 147) * 100
```

Not all 147 classes will apply to every codebase. A typical extraction SHOULD instantiate 60--80% of classes. Classes that are not instantiated SHOULD be reviewed to confirm they genuinely do not apply, rather than being overlooked.

| Threshold | Assessment |
|---|---|
| > 80% | Comprehensive extraction |
| 60--80% | Typical -- review unused classes for applicability |
| < 60% | May indicate gaps -- verify against codebase characteristics |

### 5.3 Relationship Density

**Definition:** The average number of populated relationship attributes per entity instance.

```
relationship_density = total_populated_relationships / total_entity_instances
```

Low relationship density (< 2 relationships per entity on average) suggests entities are isolated and not well-connected. SAO's value comes from the relationships between entities -- an ontology of disconnected nodes provides little insight.

### 5.4 Bridge Coverage

**Definition:** The percentage of the 8 key cross-layer bridges (from guide.md Section 10.1) that are fully populated.

The 8 critical bridges are:

1. `DataStructure.maps_to_domain_entity` ↔ `DomainEntity.mapped_from_structure` (Layer 3 ↔ 5)
2. `Attribute.mapped_from_element` ↔ `DataElement.maps_to_attribute` (Layer 5 ↔ 3)
3. `CallableUnit.implements_operation` ↔ `Operation.implemented_by_callables` (Layer 3 ↔ 6)
4. `Component.implemented_by_code` ↔ code entities (Layer 4 ↔ 3)
5. `Module.mapped_from_directory` ↔ `StorageLocation.maps_to_module` (Layer 4 ↔ 3)
6. `Module.provides_capabilities` ↔ `Capability.provided_by_modules` (Layer 4 ↔ 6)
7. `Service.runs_module` ↔ `Module.runs_as_services` (Layer 4 ↔ 4)
8. `KnowledgeArtifact.documents_*` ↔ `entity.*_documented_by_artifacts` (Layer 1 ↔ all)

A bridge is "fully populated" when at least one instance of each side of the relationship pair exists and the pair is bidirectionally symmetric. All 8 bridges SHOULD be populated for a complete extraction.

### 5.5 Coverage Summary Report

The extraction agent SHOULD produce a summary report at the end of validation:

```
=== SAO Extraction Coverage Report ===
File coverage:        94% (188/200 source files)
Class instantiation:  68% (100/147 classes)
Relationship density: 3.4 relationships/entity
Bridge coverage:      8/8 (100%)

Uncovered files: 12 (config/data files excluded)
Unused classes:  47 (reviewed — not applicable to this codebase)
```

---

## 6. Semantic Validation

Structural and relational validation can be automated. Semantic validation requires human judgment. This level asks whether the extraction *makes sense*, not just whether it is technically correct.

### 6.1 Domain Model Review

A domain expert SHOULD review:

- **Bounded context boundaries** — Do they align with actual team boundaries or business subdomains? Are contexts too broad (a monolith forced into one context) or too narrow (every class in its own context)?
- **Aggregate identification** — Is each **Aggregate** a true consistency boundary? Does the root entity make sense as the transactional unit?
- **Entity vs. Value Object classification** — Are **DomainEntities** genuinely identity-bearing? Are **ValueObjects** genuinely immutable and identity-less?

### 6.2 Business Intent Review

A domain expert SHOULD review:

- **Capability descriptions** — Do they match what the system actually does, or are they aspirational?
- **Feature scope** — Are **Features** granular enough to be meaningful but not so granular they duplicate **Operations**?
- **Actor types** — Are `actor_type` values correct? Is a `scheduled_process` really a scheduled process, or is it an `internal_service` that happens to run on a timer?
- **Rule accuracy** — Do extracted **Rules** reflect actual business constraints, or are they implementation artifacts?

### 6.3 Architecture Review

A domain expert SHOULD review:

- **Module boundaries** — Do they reflect logical groupings, or are they just mirroring the directory structure without architectural meaning?
- **Component responsibilities** — Does each **Component** have a single, coherent responsibility?
- **Service identification** — Are **Services** correctly identified from deployment manifests, or are some missing?

### 6.4 Flagging Confidence Levels

The extraction agent SHOULD annotate entities with confidence indicators using the `tags` or `metadata` attributes:

- Entities from Phases 1--2 (deterministic parsing): high confidence, no flag needed
- Entities from Phase 3 (heuristic inference): flag with `confidence: medium`
- Entities from Phases 4--5 (LLM inference): flag with `confidence: low` and `needs_review: true`

Human reviewers SHOULD prioritize entities flagged with `confidence: low`.

---

## 7. Iteration and Gap-Filling

Validation almost always reveals gaps. This section describes common gap patterns and an iterative workflow for closing them.

### 7.1 Common Gap Patterns

**Missing cross-layer bridges.** Code entities exist (Phase 2) and architectural entities exist (Phase 3), but `implemented_by_code` and `part_of_module` relationships are not populated. This typically means Phase 7 (Bridge Stitching) was incomplete.

**Unclassified DataStructures.** **DataStructures** were parsed in Phase 2 but never evaluated for domain entity status in Phase 4. Every **DataStructure** SHOULD be assessed -- even if the conclusion is that it is a utility type and not a **DomainEntity**.

**Missing business rules.** **Rules** embedded in conditional logic, validation methods, or guard clauses are often missed by automated extraction. Look for methods named `validate*`, `check*`, `assert*`, `is_valid`, or `can_*` that were not captured as **Rule** instances.

**Incomplete call graph.** Dynamic dispatch (reflection, dependency injection, event buses) means some **ControlFlow** edges are invisible to static analysis. The extraction agent SHOULD document known limitations and flag areas where dynamic dispatch is likely.

**Missing events.** Event publishing through generic mechanisms (e.g., `eventBus.publish(new Event(...))`) may not be detected as **DomainEvent** or **IntegrationEvent** instances. Search for event bus, message broker, and pub/sub patterns that Phase 5 may have missed.

**Orphaned entities.** Entities that exist but have no relationships to other entities. An **EncapsulationUnit** with no `defined_in_container`, no `implements_component`, and no **CallableUnits** is likely an extraction error.

### 7.2 Iterative Workflow

Validation and gap-filling follow a convergent loop:

```
Validate → Identify gaps → Prioritize → Extract missing entities → Re-validate
```

**Step 1: Validate.** Run all three levels of validation (structural, relational, semantic).

**Step 2: Identify gaps.** Compile a gap report listing every error, missing relationship, and coverage shortfall.

**Step 3: Prioritize.** Not all gaps are equally important. Prioritize by:
1. Structural errors (MUST fix -- the output is invalid without these)
2. Missing MUST relationships (required for a coherent ontology)
3. Missing cross-layer bridges (these are what make SAO valuable)
4. Missing SHOULD relationships (important but not blocking)
5. Coverage shortfalls (nice to have, diminishing returns)

**Step 4: Extract.** Go back to the relevant phase and extract the missing entities or relationships. This does not require re-running the entire phase -- target the specific gaps.

**Step 5: Re-validate.** Run validation again to confirm the gaps are closed and no new issues were introduced.

### 7.3 When to Stop

Extraction is complete when:

- `linkml-validate` passes with no errors
- All bidirectional relationships are symmetric
- No dangling references exist
- All MUST relationships are populated
- File coverage exceeds the target threshold (> 90% recommended)
- All 8 critical bridges are populated
- A human reviewer has signed off on the domain model and business intent layers
- Successive iterations produce diminishing returns (each round catches fewer gaps)

The extraction agent SHOULD define coverage targets upfront and track progress toward them. Perfection is not the goal -- a well-connected, structurally valid ontology with 90%+ coverage is far more useful than an incomplete extraction with 100% coverage of a small subset.

---

## 8. Validation Checklist

Use this checklist as a final sign-off gate before declaring extraction complete:

### Structural
- [ ] `linkml-validate -s sao.yml extracted-output.yaml` passes with no errors
- [ ] All enum values match `permissible_values` in `sao.yml`
- [ ] All required attributes are populated
- [ ] No type errors (strings where lists expected, etc.)

### Relational
- [ ] All bidirectional relationships are symmetric (forward and inverse match)
- [ ] No dangling references (every referenced ID exists)
- [ ] No duplicate IDs within the same class
- [ ] All MUST relationships populated (see Section 3.3 table)

### Completeness
- [ ] File coverage > 90%
- [ ] Every **Module** has at least one **Component**
- [ ] Every **Component** traces to code via `implemented_by_code`
- [ ] Every **DomainEntity** has at least one **Attribute**
- [ ] Every **Aggregate** has a root entity
- [ ] Every **Operation** traces to **CallableUnits**

### Bridges
- [ ] All 8 critical cross-layer bridges populated (see Section 5.4)
- [ ] Bridge relationships are bidirectionally symmetric

### Semantic
- [ ] Domain model reviewed by human expert
- [ ] Bounded context boundaries validated
- [ ] Capability and feature descriptions match system behavior
- [ ] Actor types verified
- [ ] Low-confidence entities reviewed and accepted or corrected

### Reporting
- [ ] Coverage report generated (Section 5.5)
- [ ] Gap report generated and all critical gaps addressed
- [ ] Remaining known limitations documented
