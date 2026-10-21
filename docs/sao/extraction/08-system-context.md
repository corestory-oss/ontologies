# Phase 8: System Context (Layer 1)

**Input:** All outputs from Phases 1--7
**Output:** Finalized **System** instance with complete top-level relationships

---

## 1. Overview

Phase 8 is the capstone of the SAO extraction process. Where prior phases built individual layers from the bottom up -- code structure, architecture, domain model, business intent, cross-cutting concerns, and bridge stitching -- this phase zooms out to the highest level and asks: **does the complete picture hold together?**

The **System** instance was created in Phase 3 with minimal attributes (`name`, `description`, `version`). At that point, only **BoundedContext** and **Module** instances existed to link to it. Now, with all seven prior phases complete, the **System** MUST be revisited and finalized with every top-level relationship populated.

This phase serves two purposes:

1. **Assembly.** Populate all remaining top-level attributes on the **System** instance.
2. **Sanity check.** Verify that the full ontology tells a coherent, complete story when viewed from the root.

**Automation level**: Low. This phase is primarily a review and assembly step. Attribute population can be scripted, but the coherence judgment requires human or LLM reasoning.

---

## 2. Finalize the System Instance

The **System** class (defined in `legacy/sao/sao.yml` as `is_a: NamedEntity` with the `Versionable` mixin) has the following top-level relationship attributes. The extraction agent MUST verify that each is populated.

### Attribute checklist

| Attribute | Range | Populated in | Action |
|---|---|---|---|
| `contains_bounded_contexts` | **BoundedContext** (multivalued) | Phase 3 | Verify all contexts are linked |
| `has_integrations` | **Integration** (multivalued) | Phase 3 | Verify all integrations are linked |
| `exposes_interfaces` | **Interface** (multivalued) | Phase 3 | Verify all top-level interfaces are linked |
| `enforces_policies` | **Policy** (multivalued) | Phase 6 | Verify all policies are linked |
| `must_comply_with` | **ComplianceRequirement** (multivalued) | Phase 6 | Verify all compliance requirements are linked |
| `assessed_by` | **RiskAssessment** (multivalued) | Phase 6 | Verify all risk assessments are linked |
| `system_documented_by_artifacts` | **KnowledgeArtifact** (multivalued) | Phase 6 | Link relevant documentation artifacts |

> **Note on Environments.** The **Environment** class does not have a direct relationship to **System** in the current schema. Environments are linked to **Deployment** instances via `Environment.hosts_deployments`. The extraction agent SHOULD NOT attempt to add an `has_environments` attribute to **System**.

### Walk-through

For each attribute, the extraction agent MUST:

1. **Collect** all instances of the target class produced across Phases 1--7.
2. **Verify** that every relevant instance appears in the System's attribute list. An instance is "relevant" if it belongs to this system (as opposed to being an external entity like **ExternalSystem**).
3. **Flag** any instance that exists but is not linked. This is either a gap (fix it) or a deliberate exclusion (document why).

### Complete YAML example

The following shows a finalized **System** instance for an e-commerce order platform:

```yaml
systems:
  - name: order-platform
    description: >-
      E-commerce order management platform handling order placement,
      payment processing, fulfillment tracking, and customer notifications.
    version: 2.4.1
    contains_bounded_contexts:
      - name: ordering
        description: Handles order lifecycle from cart to confirmation
        contained_in_system: order-platform
        contains_modules:
          - order-api
          - order-domain
          - order-persistence
        contains_aggregates:
          - Order
          - Cart
      - name: payments
        description: Processes payments and manages refunds
        contained_in_system: order-platform
        contains_modules:
          - payment-gateway
          - payment-ledger
        contains_aggregates:
          - Payment
          - Refund
      - name: fulfillment
        description: Tracks shipment and delivery status
        contained_in_system: order-platform
        contains_modules:
          - fulfillment-service
          - shipping-adapter
        contains_aggregates:
          - Shipment
    has_integrations:
      - name: stripe-payment-integration
        description: Payment processing via Stripe API
        belongs_to_system: order-platform
      - name: warehouse-integration
        description: Fulfillment sync with warehouse management system
        belongs_to_system: order-platform
      - name: email-notification-integration
        description: Transactional emails via SendGrid
        belongs_to_system: order-platform
    exposes_interfaces:
      - name: storefront-ui
        description: Customer-facing web storefront
        exposed_by_system: order-platform
      - name: order-rest-api
        description: REST API for order operations
        exposed_by_system: order-platform
      - name: admin-dashboard
        description: Internal admin interface for order management
        exposed_by_system: order-platform
    enforces_policies:
      - name: rate-limiting-policy
        description: API rate limiting at 1000 req/min per client
        enforced_by_system: order-platform
      - name: data-retention-policy
        description: Order data retained for 7 years per regulatory requirements
        enforced_by_system: order-platform
    must_comply_with:
      - name: pci-dss
        description: Payment Card Industry Data Security Standard
        applies_to_systems:
          - order-platform
      - name: gdpr
        description: General Data Protection Regulation for EU customer data
        applies_to_systems:
          - order-platform
    assessed_by:
      - name: annual-security-assessment
        description: Annual penetration test and security audit
        assesses_system: order-platform
    system_documented_by_artifacts:
      - name: architecture-decision-records
        description: Collection of ADRs documenting key architectural decisions
        documents_system: order-platform
      - name: api-documentation
        description: OpenAPI specs and developer guides
        documents_system: order-platform
      - name: runbook
        description: Operational runbook for incident response
        documents_system: order-platform
```

---

## 3. System-Level Sanity Checks

Once the **System** instance is fully populated, the extraction agent MUST perform the following verification checks.

### 3.1 Completeness

Every **BoundedContext** produced in Phase 3 MUST appear in `System.contains_bounded_contexts`. To verify:

1. Collect all **BoundedContext** instances from the extraction output.
2. Compare against the list in `System.contains_bounded_contexts`.
3. Any **BoundedContext** not linked to the **System** is orphaned -- either link it or justify its exclusion.

The same check applies to **Integration**, **Interface**, **Policy**, **ComplianceRequirement**, **RiskAssessment**, and **KnowledgeArtifact** instances.

### 3.2 Consistency

Cross-check counts and references for internal consistency:

- The number of **Integration** instances SHOULD roughly correspond to the number of distinct **ExternalSystem** instances. If there are significantly more integrations than external systems, some external systems may have multiple integration points (valid). If there are external systems with no integration, they may be incompletely modeled.
- The number of top-level **Interface** instances linked to the **System** SHOULD match the number of distinct user-facing or API-facing entry points discovered in Phase 3.
- Every **BoundedContext** SHOULD contain at least one **Module**. A context with no modules is likely a modeling gap.

### 3.3 Coverage

Estimate what percentage of the codebase has been decomposed:

- **By files**: How many source files are mapped to a **StorageLocation** that is transitively reachable from the **System**? Aim for > 90%.
- **By modules**: How many top-level directories or build modules are represented as **Module** instances? Aim for 100%.
- **By code units**: How many **EncapsulationUnit** and **CallableUnit** instances exist relative to the number of classes/functions in the codebase?

Coverage below 80% SHOULD trigger a review of Phases 1--2 to identify unmapped areas.

### 3.4 Coherence

This is the most subjective check. Read the following in sequence:

1. `System.name` and `System.description`
2. The `name` and `description` of each **BoundedContext**
3. The `name` and `description` of each **Integration**
4. The `name` of each top-level **Interface**

Ask: does this tell a coherent story? Can a newcomer read these names and descriptions and understand what the system does, how it is organized, and what it connects to? If not, revise descriptions until the narrative is clear.

---

## 4. Generating a System Summary

As a final validation artifact, the extraction agent SHOULD generate a human-readable summary from the extracted ontology. This summary serves as both documentation and a smoke test -- if anything looks wrong in the summary, the underlying data likely has a gap.

### Summary template

```
System: {System.name} (v{System.version})
{System.description}

Architecture
  Bounded contexts: {count}
    {for each: name -- description}
  Modules: {total count across all contexts}
  Components: {total count across all modules}

Domain Model
  Aggregates: {count}
  Domain entities: {count}
  Value objects: {count}

Integration Landscape
  External systems: {count}
  Integrations: {count}
    {for each: name -- description}

Actors
  Human actors: {count}
    {for each: name (actor_type)}
  System actors: {count}
    {for each: name}

Interfaces
  User interfaces: {count}
  Programmatic interfaces: {count}
  Event interfaces: {count}

Governance
  Policies: {count}
  Compliance requirements: {count}

Documentation
  Knowledge artifacts: {count}
```

### Example output

```
System: order-platform (v2.4.1)
E-commerce order management platform handling order placement,
payment processing, fulfillment tracking, and customer notifications.

Architecture
  Bounded contexts: 3
    ordering -- Handles order lifecycle from cart to confirmation
    payments -- Processes payments and manages refunds
    fulfillment -- Tracks shipment and delivery status
  Modules: 6
  Components: 14

Domain Model
  Aggregates: 4
  Domain entities: 12
  Value objects: 8

Integration Landscape
  External systems: 3
  Integrations: 3
    stripe-payment-integration -- Payment processing via Stripe API
    warehouse-integration -- Fulfillment sync with warehouse management system
    email-notification-integration -- Transactional emails via SendGrid

Actors
  Human actors: 3
    CustomerUser (end_user)
    SupportAgent (operator)
    PlatformAdmin (administrator)
  System actors: 2
    PaymentWebhookHandler
    WarehouseSync

Interfaces
  User interfaces: 2
  Programmatic interfaces: 1
  Event interfaces: 0

Governance
  Policies: 2
  Compliance requirements: 2

Documentation
  Knowledge artifacts: 3
```

The extraction agent SHOULD review this summary with a domain expert. If the summary accurately reflects the system as understood by stakeholders, the extraction is complete.

---

## 5. Phase 8 Checklist

Before proceeding to Validation (doc 09), confirm every item:

- [ ] **System instance is complete.** All seven relationship attributes on **System** have been reviewed and populated (or explicitly marked as empty with justification).
- [ ] **All BoundedContexts are linked.** Every **BoundedContext** appears in `System.contains_bounded_contexts`. No orphaned contexts exist.
- [ ] **All Integrations are linked.** Every **Integration** appears in `System.has_integrations`.
- [ ] **All top-level Interfaces are linked.** Every system-level **Interface** appears in `System.exposes_interfaces`.
- [ ] **Policies and compliance linked.** All **Policy** instances appear in `System.enforces_policies`. All **ComplianceRequirement** instances appear in `System.must_comply_with`.
- [ ] **Risk assessments linked.** All **RiskAssessment** instances appear in `System.assessed_by`.
- [ ] **Documentation linked.** Relevant **KnowledgeArtifact** instances appear in `System.system_documented_by_artifacts`.
- [ ] **System summary generated.** A human-readable summary has been produced and reviewed for accuracy.
- [ ] **Coherence verified.** The system narrative (names, descriptions, relationships) tells a coherent story.

Once all items are confirmed, the extraction is structurally complete. Proceed to [Phase 9: Validation](09-validation.md) for schema-level validation, completeness scoring, and gap analysis.
