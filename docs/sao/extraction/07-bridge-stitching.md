# Phase 7: Bridge Relationships and Graph Stitching

**Input:** All outputs from Phases 1-6 (complete entity instances across all SAO layers)
**Output:** Verified and completed cross-layer relationships; orphan report; symmetry verification results

---

## 1. Overview

The SAO's power lies in its cross-layer bridges. They connect code to architecture, architecture to domain, and domain to business intent. Without them, each layer is an isolated catalog; with them, the SAO becomes a navigable graph where any question — "what code implements this business capability?" or "what business purpose does this function serve?" — is answerable by traversal.

After independent extraction in Phases 1-6, bridges are often incomplete or inconsistent. Each phase focuses on its own layer and creates entities with forward references that may not yet have targets, or creates targets without backlinks. This is expected and by design: each phase is self-contained so it can be executed and validated independently.

Phase 7 is a systematic verification and gap-filling pass. It does not create new entities. It examines the relationships between existing entities, identifies missing or asymmetric links, and completes them. The SAO documents 214 bidirectional relationship pairs; the most critical are the eight cross-layer bridges described in this document.

This phase is not about discovery. If an entity is missing, the extraction agent SHOULD return to the appropriate earlier phase to create it. Phase 7 only stitches together what already exists.

---

## 2. The Eight Critical Bridges

The SAO guide identifies eight cross-layer bridges that form the connective tissue of the ontology. Each bridge is a bidirectional relationship pair connecting entities in different conceptual layers. The extraction agent MUST verify all eight bridges and fill any gaps.

### Bridge 1: Module to StorageLocation

| Attribute | Value |
|---|---|
| Forward | `Module.mapped_from_directory` --> **StorageLocation** |
| Inverse | `StorageLocation.maps_to_module` --> **Module** |
| Layers | Layer 4 (Architecture) <-> Layer 3 (Code Structure) |

**What it connects.** This bridge links the logical module structure (how architects think about the system) to the physical directory tree (how the file system organizes the code). It is typically the first bridge established, since **Modules** are created directly from **StorageLocations** in Phase 3.

**Verification.** Every **Module** SHOULD have at least one `mapped_from_directory` reference to a **StorageLocation**. Every top-level **StorageLocation** (one that represents a cohesive package or directory tree) SHOULD have a `maps_to_module` reference back to a **Module**.

**Common gap.** Modules created in Phase 3 sometimes lack backlinks to the **StorageLocations** identified in Phase 1. This happens when Phase 3 creates Modules from build manifests rather than from the directory walk, or when a Module spans multiple directories and only one is linked. The extraction agent MUST walk the Module list and verify each has a `mapped_from_directory` value. If a Module has no mapped directory, check Phase 1 outputs for the matching **StorageLocation** and add the link in both directions.

### Bridge 2: Component to EncapsulationUnit

| Attribute | Value |
|---|---|
| Forward | `Component.implemented_by_code` --> **EncapsulationUnit** (list) |
| Inverse | `EncapsulationUnit.implements_component` --> **Component** |
| Layers | Layer 4 (Architecture) <-> Layer 3 (Code Structure) |

**What it connects.** This bridge links architectural components (logical groupings of functionality) to the code units that implement them. A single **Component** may be implemented by many **EncapsulationUnits**, but each **EncapsulationUnit** with an architectural role SHOULD link to exactly one **Component**.

**Verification.** Every **Component** MUST have at least one `implemented_by_code` reference. Every **EncapsulationUnit** that plays a clear architectural role (controllers, services, repositories, domain models) SHOULD have an `implements_component` reference.

**Common gap.** Utility and helper classes often remain unlinked. This is acceptable -- not every **EncapsulationUnit** has a meaningful architectural role. However, the extraction agent SHOULD verify that the unlinked units are genuinely utilities rather than overlooked implementation classes. A quick check: if an **EncapsulationUnit** is referenced by a **CallableUnit** that implements an **Operation**, it likely belongs to a **Component**.

### Bridge 3: DomainEntity to DataStructure

| Attribute | Value |
|---|---|
| Forward | `DomainEntity.mapped_from_structure` --> **DataStructure** |
| Inverse | `DataStructure.maps_to_domain_entity` --> **DomainEntity** |
| Layers | Layer 5 (Domain) <-> Layer 3 (Code Structure) |

**What it connects.** This bridge links business-meaningful entities (the domain model) to their code-level representations (classes, structs, records). It is the primary bridge between "what the business cares about" and "what the code defines."

**Verification.** Every **DomainEntity** MUST have a `mapped_from_structure` reference. Not every **DataStructure** needs a domain mapping -- DTOs, internal value holders, configuration objects, and framework scaffolding do not represent domain concepts.

**Common gap.** DomainEntities created in Phase 4 are sometimes synthesized from documentation or domain knowledge without being linked back to their originating **DataStructure**. The extraction agent MUST verify that each **DomainEntity** traces to at least one code-level structure. If no matching **DataStructure** exists, return to Phase 2 to extract it.

### Bridge 4: Attribute to DataElement

| Attribute | Value |
|---|---|
| Forward | `Attribute.mapped_from_element` --> **DataElement** |
| Inverse | `DataElement.maps_to_attribute` --> **Attribute** |
| Layers | Layer 5 (Domain) <-> Layer 3 (Code Structure) |

**What it connects.** This is the field-level counterpart to Bridge 3. It links individual domain attributes to their code-level data elements (fields, columns, properties).

**Verification.** Every **Attribute** on a **DomainEntity** SHOULD have a `mapped_from_element` reference. Computed or derived attributes that have no direct code-level representation MAY omit this bridge.

**Common gap.** Attributes are often created in Phase 4 by examining **DomainEntities** without tracing each field back to a specific **DataElement**. The extraction agent SHOULD walk each **DomainEntity**, compare its **Attributes** to the **DataElements** on the linked **DataStructure** (from Bridge 3), and establish the field-level mappings.

### Bridge 5: Operation to CallableUnit

| Attribute | Value |
|---|---|
| Forward | `Operation.implemented_by_callables` --> **CallableUnit** (list) |
| Inverse | `CallableUnit.implements_operation` --> **Operation** |
| Layers | Layer 6 (Business Intent) <-> Layer 3 (Code Structure) |

**What it connects.** This bridge links business operations (what the system does from a user's perspective) to the code that implements them. A single **Operation** is typically implemented by multiple **CallableUnits** working together.

**Verification.** Every **Operation** MUST have at least one `implemented_by_callables` reference. Not every **CallableUnit** implements an **Operation** -- internal methods, private helpers, and framework callbacks do not represent business operations.

**Common gap.** Operations created in Phase 5 are often synthesized from use case analysis without tracing back to implementing code. The extraction agent MUST verify each **Operation** links to at least one **CallableUnit**. Start from the **Operation**, identify the entry-point **CallableUnit** (typically a controller method or API handler), and link it.

### Bridge 6: Capability to Module

| Attribute | Value |
|---|---|
| Forward | `Capability.provided_by_modules` --> **Module** (list) |
| Inverse | `Module.provides_capabilities` --> **Capability** (list) |
| Layers | Layer 6 (Business Intent) <-> Layer 4 (Architecture) |

**What it connects.** This bridge links high-level business capabilities (what the system can do) to the architectural modules that provide them. It answers the question: "which part of the codebase is responsible for this business capability?"

**Verification.** Every **Capability** SHOULD link to at least one **Module** via `provided_by_modules`. Every **Module** that has a clear business purpose SHOULD list its capabilities via `provides_capabilities`.

**Common gap.** Capabilities synthesized in Phase 5 from business documentation are often left floating without links to the implementing modules. The extraction agent SHOULD examine each **Capability**, determine which **Module(s)** contribute to it, and establish the links in both directions.

### Bridge 7: Service to Module

| Attribute | Value |
|---|---|
| Forward | `Service.runs_module` --> **Module** |
| Inverse | `Module.runs_as_services` --> **Service** (list) |
| Layers | Layer 4 (Architecture runtime) <-> Layer 4 (Architecture logical) |

**What it connects.** This bridge links runtime deployment units (services, processes, containers) to the logical module structure. While both entities live in Layer 4, they represent different perspectives: **Module** is the logical grouping of code, while **Service** is the runtime incarnation.

**Verification.** Every **Service** SHOULD link to the **Module** it runs via `runs_module`. Every **Module** that has a deployment manifest (Dockerfile, Kubernetes deployment, serverless config) SHOULD link to its corresponding **Service** via `runs_as_services`.

**Common gap.** Services identified from deployment manifests in Phase 3 are sometimes not linked to their **Module** because the naming conventions differ (e.g., the Kubernetes deployment is named `order-svc` but the module is named `orders`). The extraction agent SHOULD match services to modules by examining deployment configs, entry points, and build targets.

### Bridge 8: KnowledgeArtifact to Documented Entities

| Attribute | Value |
|---|---|
| Forward | `KnowledgeArtifact.documents_system`, `documents_bounded_context`, `documents_module`, `documents_component`, `documents_aggregate`, `documents_domain_entity`, etc. |
| Inverse | `System.system_documented_by_artifacts`, `Module.module_documented_by_artifacts`, etc. |
| Layers | Cross-cutting <-> All layers |

**What it connects.** This bridge links documentation artifacts (READMEs, ADRs, wiki pages, API docs, runbooks) to the entities they describe. Unlike the other bridges, this one fans out across all layers.

**Verification.** Every **KnowledgeArtifact** SHOULD link to at least one entity it documents via the appropriate `documents_*` attribute. Key entities -- **System**, **BoundedContexts**, critical **Modules** -- SHOULD have at least one `*_documented_by_artifacts` reference.

**Common gap.** KnowledgeArtifacts created in Phase 6 are often cataloged without linking to the specific entities they describe. The extraction agent SHOULD read each **KnowledgeArtifact**'s content (or summary) and match it to the most relevant entity. A README in a module directory documents that **Module**. An ADR about authentication documents the relevant **Component** and **BoundedContext**.

---

## 3. Graph Connectivity Checks

After verifying all eight bridges, the extraction agent MUST perform three traversal checks to confirm the graph is fully connected.

### Top-down traversal

Starting from the **System** instance, verify that every entity is reachable by following containment and bridge relationships downward:

```
System
  └─ contains_bounded_contexts ──> BoundedContext (each one)
       └─ contains_modules ──> Module (each one)
            └─ contains_components ──> Component (each one)
                 └─ implemented_by_code ──> EncapsulationUnit (each one)
                      └─ contains_callable_units ──> CallableUnit (each one)
```

Every **BoundedContext** MUST be reachable from the **System**. Every **Module** MUST be reachable from a **BoundedContext**. Every **Component** MUST be reachable from a **Module**. If any entity is unreachable, the containment hierarchy has a gap that MUST be fixed.

### Bottom-up traversal

Starting from any **CallableUnit**, verify that you can trace upward to the **System**:

```
CallableUnit
  └─ contained_in_unit ──> EncapsulationUnit
       └─ implements_component ──> Component
            └─ part_of_module ──> Module
                 └─ belongs_to_bounded_context ──> BoundedContext
                      └─ part_of_system ──> System
```

Select a sample of **CallableUnits** (at minimum, every entry-point callable such as API handlers, event listeners, and scheduled tasks) and verify each can be traced to the **System**. Any break in the chain indicates a missing relationship.

### Cross-layer traversal

Starting from a **DomainEntity**, verify that you can reach both the code layer (downward) and the architectural layer (upward):

```
DomainEntity
  ├─ mapped_from_structure ──> DataStructure (down to code)
  │    └─ contained_in_unit ──> EncapsulationUnit
  └─ part_of_aggregate ──> Aggregate (up to architecture)
       └─ owned_by_bounded_context ──> BoundedContext
            └─ part_of_system ──> System
```

This traversal confirms that the domain model is properly anchored to both code and architecture. Every **DomainEntity** MUST be reachable from both directions.

---

## 4. Orphan Detection

An **orphan** is an entity with no incoming or outgoing cross-layer relationships. Orphans indicate extraction gaps -- entities that were created but never connected to the broader graph.

### Acceptable orphans

Some entities MAY legitimately have no cross-layer bridges:

- **EncapsulationUnits** that are pure utilities, internal helpers, or framework-generated scaffolding
- **CallableUnits** that are private methods, getters/setters, or framework callbacks
- **DataStructures** that are DTOs, internal value holders, or configuration objects
- **DataElements** on non-domain structures

These entities still MUST have intra-layer relationships (e.g., an **EncapsulationUnit** MUST still have `contained_in_container` linking it to a **CodeContainer**), but they do not need cross-layer bridges.

### Entities that MUST NOT be orphans

The following entity types MUST have at least the specified cross-layer relationships:

| Entity type | Required relationship(s) |
|---|---|
| **System** | `contains_bounded_contexts` |
| **BoundedContext** | `contains_modules`, `part_of_system` |
| **Module** | `mapped_from_directory`, `belongs_to_bounded_context` |
| **Component** | `implemented_by_code`, `part_of_module` |
| **Service** | `runs_module` |
| **DomainEntity** | `mapped_from_structure`, `part_of_aggregate` |
| **Aggregate** | `root_entity`, `owned_by_bounded_context` |
| **Operation** | `implemented_by_callables` |
| **Capability** | `provided_by_modules` |
| **KnowledgeArtifact** | At least one `documents_*` reference |

### Systematic orphan check

For each entity type in the table above, the extraction agent MUST:

1. List all instances of that type
2. For each instance, verify the required relationship(s) exist and point to valid targets
3. Record any orphans in an orphan report
4. For each orphan, either fill the missing relationship or document why the entity is intentionally unlinked

The orphan report SHOULD be structured as a table:

| Entity type | Entity name | Missing relationship | Resolution |
|---|---|---|---|
| **Module** | `analytics` | `mapped_from_directory` | Linked to **StorageLocation** `src/analytics` |
| **DomainEntity** | **PaymentMethod** | `mapped_from_structure` | Linked to **DataStructure** `PaymentMethod` in `payments/models.py` |
| **Capability** | **ReportGeneration** | `provided_by_modules` | Linked to **Module** `reporting` |

---

## 5. Relationship Symmetry Verification

Every bidirectional relationship pair in the SAO MUST be symmetric: if entity A references entity B via a forward relationship, then entity B MUST reference entity A via the corresponding inverse relationship. Asymmetric links are a data integrity problem that will cause traversal failures.

### Verification procedure

For each of the eight critical bridges, the extraction agent MUST perform the following check:

1. **Forward scan.** For each instance of the source entity type, read the forward relationship attribute. For every target entity referenced, verify that the target's inverse attribute includes the source entity.

2. **Inverse scan.** For each instance of the target entity type, read the inverse relationship attribute. For every source entity referenced, verify that the source's forward attribute includes the target entity.

3. **Record asymmetries.** Any case where A.forward references B but B.inverse does not reference A (or vice versa) is an asymmetry that MUST be fixed.

Example verification for Bridge 2 (**Component** to **EncapsulationUnit**):

```
For each Component c:
  For each EncapsulationUnit eu in c.implemented_by_code:
    ASSERT eu.implements_component == c
    If not: set eu.implements_component = c

For each EncapsulationUnit eu where eu.implements_component is set:
  Let c = eu.implements_component
  ASSERT eu in c.implemented_by_code
  If not: append eu to c.implemented_by_code
```

### Common asymmetries and fixes

| Asymmetry | Typical cause | Fix |
|---|---|---|
| Forward set, inverse missing | Entity created in an earlier phase before the target existed | Set the inverse on the target entity |
| Inverse set, forward missing | Target entity created with a backlink but source not updated | Add the reference to the source entity's forward attribute |
| Both set but pointing to different entities | Copy-paste error or entity renamed after linking | Determine the correct pairing and fix both sides |
| Dangling reference | Reference points to an entity ID that does not exist | Either create the missing entity (return to the appropriate phase) or remove the dangling reference |

---

## 6. Phase 7 Checklist

Before proceeding to Phase 8, the extraction agent MUST confirm all of the following:

- [ ] **Bridge 1** (Module <-> StorageLocation): All Modules have `mapped_from_directory`; all relevant StorageLocations have `maps_to_module`
- [ ] **Bridge 2** (Component <-> EncapsulationUnit): All Components have `implemented_by_code`; all architecturally significant EncapsulationUnits have `implements_component`
- [ ] **Bridge 3** (DomainEntity <-> DataStructure): All DomainEntities have `mapped_from_structure`
- [ ] **Bridge 4** (Attribute <-> DataElement): All domain Attributes have `mapped_from_element` where a direct mapping exists
- [ ] **Bridge 5** (Operation <-> CallableUnit): All Operations have `implemented_by_callables`
- [ ] **Bridge 6** (Capability <-> Module): All Capabilities have `provided_by_modules`
- [ ] **Bridge 7** (Service <-> Module): All Services have `runs_module`; all deployed Modules have `runs_as_services`
- [ ] **Bridge 8** (KnowledgeArtifact <-> entities): All KnowledgeArtifacts link to at least one documented entity
- [ ] **Top-down traversal** passes: System -> BoundedContext -> Module -> Component -> EncapsulationUnit is fully connected
- [ ] **Bottom-up traversal** passes: sampled CallableUnits trace back to System
- [ ] **Cross-layer traversal** passes: DomainEntities reach both code and architecture
- [ ] **Orphan report** generated and reviewed; no entity in the MUST-connect list is orphaned
- [ ] **Bidirectional symmetry** verified for all eight bridges; no asymmetric links remain
- [ ] **No dangling references**: every entity ID referenced in a relationship resolves to an existing entity
