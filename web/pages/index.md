<div class="hero" markdown="1">
<p class="eyebrow">CORESTORY OPEN ONTOLOGIES</p>

# Understand software.<br>Connect its evidence.

<p class="lead">A shared vocabulary for the structures of software and the specifications, decisions, and evidence that explain it.</p>

<div class="actions">
<a class="button primary" href="reference/">Explore the ontologies <span aria-hidden="true">↗</span></a>
<a class="button secondary" href="guides/">Read the guides <span aria-hidden="true">→</span></a>
</div>

<p class="hero-note">Authored in Turtle. Defined with RDFS, validated with SHACL, and supplemented with OWL.</p>
</div>

<section class="ontology-section" aria-labelledby="two-ontologies" markdown="1">
<p class="eyebrow">ONE ECOSYSTEM · TWO PERSPECTIVES</p>

## Two ontologies, a connected understanding. {#two-ontologies}

Software structure and specification describe different aspects of the same system. SAO and SpecSpec give each a vocabulary, with links between them.

<div class="ontology-grid" markdown="1">
<article class="ontology-card sao" markdown="1">
<p class="card-kicker">SOFTWARE STRUCTURE <span>{{sao_version}} · candidate</span></p>

### SAO

#### Systems Abstraction Ontology

Describe software through its structures and abstractions: systems, modules, callable units, data stores, and their relationships.

<a class="text-link" href="reference/#sao:">Explore SAO →</a>
<a class="subtle-link" href="guides/docs/sao/README.html">Read the SAO guide</a>
</article>
<article class="ontology-card specspec" markdown="1">
<p class="card-kicker">SPECIFICATION &amp; EVIDENCE <span>{{specspec_version}} · draft</span></p>

### SpecSpec

#### Specification &amp; Evidence Ontology

Describe requirements, claims, decisions, and supporting evidence. Connect what a system should do to what is known about its implementation.

<a class="text-link" href="reference/#spec:">Explore SpecSpec →</a>
<a class="subtle-link" href="guides/docs/specspec/README.html">Read the SpecSpec guide</a>
</article>
</div>
</section>

<section class="connected-section" aria-labelledby="grounded" markdown="1">
<p class="eyebrow">FROM STRUCTURE TO UNDERSTANDING</p>

## Keep specifications grounded. {#grounded}

Code tells part of a system's story. Requirements, business rules, and evidence add context. These ontologies support a graph that connects those perspectives, so a specification can be traced to the software and evidence behind it.

<div class="connection" aria-label="Software structures connect to specifications through evidence"><span>Software structures<small>SAO</small></span><b aria-hidden="true">↔</b><span>Specifications &amp; evidence<small>SpecSpec</small></span></div>

[See an example using both ontologies →](guides/examples/ecosystem/README.html)
</section>

<section class="download-section" aria-labelledby="downloads" markdown="1">
<p class="eyebrow">USE THE VOCABULARIES</p>

## Take the graph with you. {#downloads}

Download the layers you need. The vocabularies, validation shapes, and inference supplements are separate files. The current SAO–SpecSpec bridge is available as an optional layer.

| Ontology | Vocabulary · RDFS | Validation · SHACL | Inference · OWL |
|---|---|---|---|
| **SAO** | [sao.ttl](dist/sao.ttl) | [sao.shacl.ttl](dist/sao.shacl.ttl) | [sao.owl.ttl](dist/sao.owl.ttl) |
| **SpecSpec** | [specspec.ttl](dist/specspec.ttl) | [specspec.shacl.ttl](dist/specspec.shacl.ttl) | [specspec.owl.ttl](dist/specspec.owl.ttl) |
| **Optional bridge** | [specspec-sao.ttl](dist/specspec-sao.ttl) | [specspec-sao.shacl.ttl](dist/specspec-sao.shacl.ttl) | [specspec-sao.owl.ttl](dist/specspec-sao.owl.ttl) |

The ontologies and documentation are licensed under Apache 2.0. SAO {{sao_version}} is a release candidate; SpecSpec {{specspec_version}} is a draft. See the [guides](guides/) for scope and current modeling choices.
</section>
