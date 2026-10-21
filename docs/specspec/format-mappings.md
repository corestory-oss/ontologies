# Existing formats as representations

These are proposed mappings for adapter design, not claims of exact equivalence, conformance, or implemented import/export support. The graph vocabulary is independent of document headings and folder conventions. External profile versions should be pinned when adapters are implemented.

| Convention | Native concept | Initial SpecSpec representation | Important limit |
|---|---|---|---|
| OpenSpec | Current behavior specs, requirements and scenarios | Specification, Requirement, Scenario, ArtifactFragment | Distinguish a stated requirement from evidence that current code satisfies it. |
| OpenSpec | Change proposal, design and spec deltas | ChangeProposal, Decision, RequirementReplacement | Task execution and complete native delta syntax are not modeled yet. |
| arc42 | Context, building-block, runtime and deployment views | SpecificationArtifact and ArtifactFragment linked through the SAO bridge | Software structures belong in SAO; a view can describe many entities. |
| arc42 | Quality requirements and architecture decisions | Requirement, Scenario, Decision | Full quality-scenario dimensions and template section ordering are not modeled yet. |
| MADR | Context, considered options, decision and consequences | Decision, DecisionOption and rationale/consequence Claim nodes | Preserve native drivers, tradeoffs and prose; there is no lossless adapter yet. |
| Old SpecSpec | Stable concept IDs, origin and code anchors | SpecElement IDs, Claim.origin, SourceSnapshot and EvidenceAnchor | Its mandatory abstraction ladder and proprietary Markdown layout are not core ontology requirements. |
| PRD / user-authored use-case documents | Goals, requirements and interactions | Specification, Requirement, UseCase, Scenario | PRD is a family of conventions; identify the specific template with a RepresentationProfile. |

Authoritative references used for this initial mapping:

- [OpenSpec overview](https://github.com/Fission-AI/OpenSpec/blob/main/docs/overview.md): specs and change artifacts.
- [arc42 template overview](https://arc42.org/overview/): architecture documentation views and sections.
- [MADR template](https://adr.github.io/madr/decisions/adr-template.html): decision context, alternatives, outcome and consequences.

No external template text or code is copied into this repository. These are semantic mappings written for this draft. The old SpecSpec checkout was consulted locally as background; its normative document instructions are not adopted as instructions for this ontology.
