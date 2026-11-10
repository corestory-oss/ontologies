# Section 29: Glossary Terms

This section defines business glossaries and their terms, and how a term is bound to the system entities it describes. It is a proposed addition to the SAO 3.0.0 candidate.

## Overview

Organizations keep business vocabularies in glossaries owned by different groups. The same word often means different things in different glossaries, and different words often mean the same thing. A label alone cannot tell these cases apart. What decides them is what each term refers to.

SAO therefore models a term as its own node, scoped to one glossary, and binds it to the entities it describes: data elements, rules, capabilities, domain entities, or any other **NamedEntity**. Two terms with the same label are two nodes. Nothing in this module merges terms by label, and no axiom infers that two terms are the same.

**BoundedContext** keeps its free-text `ubiquitous_language` attribute. A **Glossary** can be linked to a bounded context when it records that context's language.

## Core Concepts

### Glossary

**Definition**: A curated set of business terms maintained by one owner, such as a department, data-governance team, or bounded context.

**Purpose**: Scopes the labels and definitions of its terms. Corresponds to a SKOS concept scheme and to a glossary or domain in data-catalog tools.

**Key Attributes**:
- Inherits from `NamedEntity`

**Relationships**:
- **contains_terms**: `GlossaryTerm` entities defined in this glossary (inverse of `contained_in_glossary`)
- **scoped_to_bounded_context**: The `BoundedContext` whose language this glossary records (optional, single)

### GlossaryTerm

**Definition**: A business term defined in one glossary, with its labels, definition, and the system entities it describes.

**Purpose**: Gives business vocabulary a place in the graph that consumers can join to code and data, and that glossary tools can exchange without a custom mapping.

**Key Attributes**:
- Inherits from `NamedEntity`
- **preferred_label**: Preferred display label (required); at most one per language and at most one without a language tag
- **alternative_labels**: Synonyms within this glossary
- **short_codes**: Abbreviations or codes, such as a field-name prefix. A shared short code is not evidence that two terms mean the same thing.
- **hidden_labels**: Search-only labels, such as common misspellings
- **term_definition**: What the term means in this glossary; at most one per language

Preferred, alternative, hidden, and short-code labels on one term must differ from each other, following the SKOS rule that these label kinds are disjoint.

**Relationships**:
- **contained_in_glossary**: The defining `Glossary` (required, single)
- **describes_entities**: System entities this term describes. Any `NamedEntity` except another `GlossaryTerm`.
- **has_broader_terms** / **has_narrower_terms**: More general and more specific terms in the same glossary (inverses of each other)
- **related_to_terms**: Associated terms in the same glossary (symmetric)

## SKOS alignment

Each glossary class and property is a subclass or subproperty of its SKOS counterpart, so a SKOS consumer can read a SAO glossary after ordinary RDFS reasoning. Glossary exports from catalog tools generally use these same SKOS terms.

| SAO | SKOS |
|---|---|
| **Glossary** | `skos:ConceptScheme` |
| **GlossaryTerm** | `skos:Concept` |
| `contained_in_glossary` | `skos:inScheme` |
| `preferred_label` | `skos:prefLabel` |
| `alternative_labels`, `short_codes` | `skos:altLabel` |
| `hidden_labels` | `skos:hiddenLabel` |
| `term_definition` | `skos:definition` |
| `has_broader_terms` / `has_narrower_terms` | `skos:broader` / `skos:narrower` |
| `related_to_terms` | `skos:related` |

`describes_entities` has no SKOS counterpart. SKOS describes concepts, not the software or data they refer to.

## Matching terms across glossaries

Relations between terms in different glossaries are assertions that need provenance: who or what made the match, how confident it is, and whether a person has reviewed it. They are not part of this SAO module. The optional SpecSpec–SAO bridge provides **TermMappingLink** for them. Each link cites a SpecSpec **Claim** that carries origin, confidence, and review status. Its `mapping_relation` values correspond to the SKOS mapping properties (`exact_match` to `skos:exactMatch`, and so on). A mapping links two terms; it never merges them.

## Example

[examples/sao/rdf/glossary.ttl](../../examples/sao/rdf/glossary.ttl) has two synthetic glossaries. Both define "Balance", bound to different fields, so the two terms are distinct. A synonym in the other glossary shares no words with "Balance" but is bound to the same field. [examples/ecosystem/glossary-mapping.ttl](../../examples/ecosystem/glossary-mapping.ttl) records the reviewed cross-glossary match between those synonyms.
