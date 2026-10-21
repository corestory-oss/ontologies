# Beyond Grep and Vector Search: The Case for Ontology-driven Extraction of Software Requirements in Agentic LLM Analysis

## Abstract

The extraction of meaningful requirements from software systems remains a persistent challenge in software engineering, particularly in the context of legacy system modernization. This paper examines the fundamental limitations of prevailing search-based approaches, including lexical pattern matching, keyword search, and vector embedding techniques, for requirements extraction tasks. Through analysis of theoretical constraints, empirical evidence, and documented case studies, we demonstrate that these limitations are architectural rather than incremental, stemming from the inherent inability of search paradigms to capture semantic relationships, control flow dependencies, and business logic distribution across software artifacts. We present ontology-based modeling and knowledge graph architectures as theoretically grounded alternatives that address these structural deficiencies. Evidence from enterprise deployments suggests that knowledge graph approaches achieve 60-90% reductions in analysis time while providing formally verifiable traceability between requirements and implementation artifacts. The findings have significant implications for organizations undertaking software modernization initiatives and for the broader research agenda in automated requirements engineering.

## 1. Introduction

The challenge of extracting requirements from existing software systems has grown increasingly critical as organizations confront aging codebases that encode decades of business logic, regulatory compliance rules, and operational knowledge. Industry analyses indicate that approximately 70% of Fortune 500 enterprise software exceeds 20 years of age, with technical debt consuming an estimated 40% of IT budgets [28]. Legacy modernization initiatives, which seek to migrate these systems to contemporary platforms, exhibit failure rates approaching 74% [1], a figure that demands examination of the methodological foundations underlying current approaches.

The predominant methodology for analyzing existing codebases with AI relies on search-based techniques spanning a spectrum from simple lexical pattern matching (e.g., grep, regular expressions) to sophisticated vector embedding models that power semantic search and retrieval-augmented generation (RAG) systems. These approaches share a common assumption: that relevant information can be located through queries against textual representations of code and documentation. This paper challenges that assumption.

We argue that the extraction of meaningful requirements (defined as the functional behaviors, business rules, data constraints, and quality attributes that a software system must satisfy) necessitates understanding of semantic relationships that search-based approaches cannot, by their architectural nature, provide. The thesis advanced herein is that ontology-based modeling and knowledge graph architectures constitute necessary infrastructure for accurate requirements extraction, not merely as enhanced search indices, but as fundamentally different representational paradigms that capture meaning through formal structure.

The remainder of this paper proceeds as follows. Section 2 examines the limitations of text-based search methods. Section 3 analyzes the theoretical and practical constraints of vector embedding approaches. Section 4 presents ontological modeling as a formal foundation for software semantics. Section 5 discusses knowledge graph implementations and empirical evidence from enterprise deployments. Section 6 addresses market dynamics and implementation considerations. Section 7 concludes with implications for research and practice.

## 2. Limitations of Lexical Pattern Matching

Text-based search tools, including grep, keyword search, and regular expression engines, constitute the baseline approach employed by most organizations when initiating codebase analysis with generative AI agents. The failure mode of these techniques is structural: they operate on character sequences without access to program semantics.

### 2.1 The Syntax-Semantics Gap

The distinction between syntactic matching and semantic understanding manifests concretely in code analysis tasks. Research from the Semgrep project illustrates this gap: a grep search for the numeric value `2` returns only literal string matches, whereas semantic analysis recognizes that the expression `x = 1; y = x + 1` also produces this value through constant propagation [2]. This example, while simple, instantiates a general principle: the meaning of code cannot be determined from its textual representation alone.

Crew's work on "semantic grep" observed that conventional text editors providing lexical expression search "ignore the structure of the source code" [3]. The structural properties ignored include control flow paths, data dependencies, type relationships, and call hierarchies, which are precisely the properties that determine program behavior and, consequently, implemented requirements.

### 2.2 Hidden Dependencies and Cross-Component Logic

The limitations of text-based search become particularly acute in legacy mainframe systems, where business rules typically span multiple program components. Empirical analyses of COBOL applications reveal program call chains exceeding ten components in depth, with critical business logic potentially distributed across any subset of these components [1]. A text search may locate a variable name or procedure identifier, but cannot trace how data flows through call chains or determine which conditional paths execute under specific business scenarios.

The phenomenon of *hidden dependencies* (defined in the literature as relationships between seemingly independent components caused by data flow through intermediate components) [3]—exemplifies information that lexical search cannot surface. Detecting such dependencies requires construction and traversal of control flow graphs, call graphs, and data dependence graphs, representational structures that text search does not produce.

### 2.3 Implications for Requirements Traceability

The practical consequence for requirements extraction is significant. Research into static analysis documents that text-based approaches "struggle to detect issues arising from improperly validated external inputs" precisely because they cannot trace data flow from input through processing to output [2]. For requirements extraction, this limitation means that cross-cutting concerns. e.g. security constraints, transaction boundaries, error handling policies, etc., remain invisible to text-based analysis despite being critical components of system requirements.

## 3. Theoretical and Practical Constraints of Vector Embeddings

Vector embedding techniques, including transformer-based semantic search and retrieval-augmented generation (RAG), represent a substantial advancement over lexical matching by capturing distributional semantics. However, recent theoretical and empirical research reveals fundamental limitations that disqualify these approaches for accurate requirements extraction.

### 3.1 Mathematical Bounds on Embedding Capacity

A landmark 2025 study by researchers affiliated with Google DeepMind established theoretical bounds on the representational capacity of embedding-based retrieval [4]. Applying the sign-rank theorem from computational complexity theory, the authors proved that for any embedding of dimension $d$, there exist query-document relevance patterns that cannot be represented, i.e. documents that should be retrieved for a given query but mathematically cannot be, regardless of how the embedding is trained.

Empirical validation of these theoretical bounds revealed that state-of-the-art embedding models with 4096 dimensions achieve low recall on queries requiring multi-hop relational reasoning [4]. For enterprise codebases encoding billions of semantic relationships, these dimensional constraints translate to systematic retrieval failures that no amount of model scaling can address.

### 3.2 Loss of Structural Information

The application of embedding models to source code introduces domain-specific limitations. Research on code representation observes that current approaches treat code "like a sequence of tokens" while overlooking "key structural and semantic properties" extractable from Control Flow Graphs, Data Flow Graphs, and Abstract Syntax Trees [5]. Embedding models trained solely on token sequences fail to capture these structural properties. For example, Liu et al. demonstrated that augmenting pre-trained models with data flow information significantly improves vulnerability detection performance compared to token-only embeddings [6].

This observation illuminates a critical distinction: **semantic similarity, as measured by embedding cosine distance, is not equivalent to semantic understanding.** Vector search identifies code fragments that are statistically similar in their token distributions, but cannot determine whether those fragments implement related requirements, share data dependencies, or participate in common transaction boundaries.

### 3.3 Retrieval Failures in Multi-Hop Reasoning

Requirements extraction frequently demands reasoning across multiple artifacts, for example, connecting a user interface element to validation logic to database constraints to regulatory documentation. Analysis of RAG system failures identifies "multi-hop failure" as a systematic problem, occurring "when an answer requires connecting multiple, separate facts — a chain of reasoning that RAG often breaks" [7].

Barnett et al.'s taxonomy of RAG failure points documents additional systematic problems including missed top-ranked documents due to similarity ranking failures and information loss during chunking operations [8]. For source code, the chunking problem is particularly severe: function boundaries, class relationships, and cross-file dependencies cannot be arbitrarily segmented without destroying the semantic relationships that requirements extraction must capture. Despite leveraging state of the art semantically-aware chunking techniques, embedding-based retrieval remains fundamentally similarity-based, precluding reliable multi-hop reasoning.

### 3.4 Opacity and Verifiability

A final limitation concerns the epistemological status of embedding-based retrieval. Industry analysis observes that "the logic behind semantic search results is more of a 'black box' variety" [9], precluding verification of extraction completeness or correctness. For requirements extraction in regulated industries or safety-critical systems, the inability to formally verify that all relevant requirements have been identified constitutes an unacceptable risk profile.

## 4. Ontological Foundations for Software Semantics

Ontology, in the information science sense, provides formal, explicit specification of shared conceptualization. Applied to software systems, ontological modeling creates machine-readable representations of code relationships that support automated reasoning, inference, and query.

### 4.1 From Search Indices to Semantic Models

The architectural distinction between search indices and ontological models merits emphasis. A search index maps terms to locations; an ontology models what terms mean and how concepts relate. Consider a query for `getCustomer`: while a search index would return file locations containing this string; an ontological model would represent that getCustomer is a method with return type Customer, belonging to class CustomerService, implementing interface CustomerRepository, accessing entity customerDatabase, invoked by component OrderController, and satisfying requirement REQ-001.

Ontological representations are semantically rich graphs of entities and relationships and are, therefore, better able to capture the complex interdependencies that characterize software systems.

This semantic richness enables query expressiveness which are impossible with keyword search. Queries over code ontologies can answer questions such as "Find all methods that access variable X and are called from class Y" or "Return classes inheriting from BaseEntity that implement Serializable" -- structural queries that directly address the needs of requirements extraction.

### 4.2 Established Software Ontology Frameworks

Several mature ontological frameworks support software analysis. CodeOntology provides an OWL 2 ontology for object-oriented programming languages, serializing source code into RDF triples [10]. The framework's parser has processed the complete OpenJDK 8 codebase, generating 1.98 million structural triples queryable via standard SPARQL endpoints [11].

The FAMIX meta-model, underlying the Moose analysis platform, provides language-independent representation of software structures including classes, methods, invocations, accesses, and inheritance relationships [12]. FAMIX implementations exist for Java, C++, C#, Smalltalk, and TypeScript, enabling cross-language analysis within unified semantic frameworks.

At the standardization level, the Object Management Group's Knowledge Discovery Metamodel (KDM), codified as ISO/IEC 19506, provides a layered architecture spanning source inventory, program elements, code relationships, and business rule abstractions [13]. The Semantics of Business Vocabulary and Business Rules (SBVR) standard complements KDM by enabling formalization of business language into logical expressions amenable to automated verification [14, 15].

### 4.3 Inferential Capabilities

A distinguishing capability of ontological approaches is automated inference. Given axioms defining class hierarchies, property domains and ranges, and logical constraints, reasoners can derive implicit knowledge from explicit assertions. If the ontology asserts that ClassA inherits from ClassB and ClassB inherits from ClassC, the reasoner infers that ClassA inherits from ClassC without explicit statement.

For requirements traceability, this inferential capability enables automatic propagation of requirement satisfaction across implementation hierarchies. Research on ontology-based trace link discovery, evaluated with 70 subjects across Swiss universities, demonstrates improved precision and recall in traceability recovery with reduced maintainer effort compared to manual or keyword-based approaches [16].

## 5. Knowledge Graph Implementations and Empirical Evidence

Knowledge graphs operationalize ontological principles at enterprise scale, representing software systems as labeled property graphs where nodes denote structural entities inherent in source code and edges denote typed relationships between those entities. Graph database technologies store relationships as first-class citizens enabling real-time traversal without the JOIN operations that impose performance penalties in relational systems.

### 5.1 Commercial Implementations

The vendor ecosystem for software knowledge graphs has achieved significant maturity. CAST Imaging, developed over 25 years with cumulative R&D investment exceeding €200 million, reverse-engineers applications across 150+ technology stacks into interactive graph visualizations [17]. The platform, built on Neo4j, represents code elements, dependencies, data flows, and transaction paths, enabling impact analysis and modernization planning [18].

Thoughtworks' CodeConcise system demonstrates an emerging architectural pattern combining large language models with knowledge graphs derived from Abstract Syntax Tree parsing. As documented by Fowler, "a particularly promising technique... is a retrieval-augmented generation (RAG) approach where the information retrieval is done on a knowledge graph of the codebase. The knowledge graph can preserve structural information about the codebase beyond what an LLM could derive from the textual code alone" [19].

Specialized solutions for mainframe modernization include Hypercubic, which constructs comprehensive knowledge graphs from COBOL, JCL, SMF logs, and DB2 catalog metadata [23], and IBM Research's GraphGen4Code, which has demonstrated scalability to 2 billion triples extracted from 1.3 million Python source files integrated with 47 million StackOverflow discussion threads [24].

### 5.2 Quantified Outcomes

Empirical evidence from enterprise deployments supports the efficiency claims for knowledge graph approaches. A major automotive manufacturer utilizing CodeConcise for COBOL modernization achieved 66% reduction in reverse engineering time—from six weeks to two weeks per 10,000-line module—with projected labor savings of 60,000 person-days across a 15-million-line codebase [20].

IBM's partnership with CAST for a major US bank's modernization initiative reduced assessment and code-analysis time by 60%, compressing project timelines from months to weeks [21]. Practitioners report that analysis tasks previously requiring three to four days now complete in three to four hours using graph-based tools [22].

These efficiency gains derive from the structural properties of graph representation: relationship traversal operates in constant time regardless of graph size, enabling queries that would be computationally prohibitive against relational or document stores. For requirements extraction, this means that tracing a business rule from user interface through business logic to data persistence—potentially spanning hundreds of components—executes in milliseconds rather than hours.

### 5.3 Hybrid Architectures

Contemporary best practice increasingly employs hybrid architectures combining vector search for initial retrieval with graph traversal for structural analysis. This approach preserves the recall advantages of embedding-based search while addressing its semantic limitations through graph-based verification and expansion. The Thoughtworks Technology Radar has recognized this pattern, placing "using GenAI to understand legacy codebases" in the Trial ring with explicit recommendation for knowledge graph augmentation [19].

## 6. Market Dynamics and Implementation Considerations

### 6.1 Analyst Perspectives

Industry analyst positioning confirms the trajectory toward knowledge graph adoption. Gartner's 2024 Hype Cycle for Artificial Intelligence places knowledge graphs on the "Slope of Enlightenment," indicating transition from early adoption to mainstream deployment [25]. The 2024 Gartner Impact Radar for Generative AI positions knowledge graphs at the "epicenter" of enabling technologies. Gartner further predicts that by 2028, 75% of enterprises will employ AI-based code assistants for legacy modernization, with generative AI reducing modernization costs by 30% from 2023 baselines.

### 6.2 Market Projections

Market sizing data corroborates these analyst assessments. The knowledge graph market reached $1.06 billion in 2024, with projected growth to $6.93 billion by 2030 representing a 36.6% compound annual growth rate [26]. The legacy code modernization AI market specifically is projected to expand from $1.82 billion to $14.17 billion by 2033 [27]. Forrester's Total Economic Impact analysis of enterprise knowledge graph deployment documented 320% return on investment over three years, with $9.86 million in quantified benefits and 3x acceleration in analytics application development [26].

### 6.3 Implementation Guidance

Successful knowledge graph implementations for requirements extraction require realistic scoping and appropriate organizational investment. Recommended practices include initiation with bounded "lighthouse" use cases rather than enterprise-wide deployment; dedicated roles including Graph Architect, Data Engineer, and Subject Matter Expert; and explicit definition of competency questions—the queries the knowledge graph must answer to deliver value.

Current tool maturity varies across the capability spectrum. Knowledge graph platforms are production-ready. AI-assisted code analysis tools are emerging with promising results. End-to-end automated modernization remains experimental, requiring human oversight for validation and refinement [25].

## 7. Conclusion

This paper has presented a systematic argument that search-based approaches -- whether lexical or vector-embedding-based -- are architecturally inadequate for extracting meaningful requirements from software systems. The limitations identified are not amenable to incremental improvement: the sign-rank theorem establishes mathematical bounds on embedding capacity; the syntax-semantics gap is inherent to textual representation; multi-hop reasoning failures are structural to similarity-based retrieval.

Ontology-based modeling and knowledge graph architectures address these limitations by representing software semantics through formal structures that support automated inference, relationship traversal, and verifiable traceability. Empirical evidence from enterprise deployments demonstrates 60-90% efficiency improvements in code analysis tasks, with particular value in legacy modernization contexts where business logic distribution across components defeats search-based approaches.

The implications extend beyond tool selection to research agenda. Requirements engineering as a discipline must engage with knowledge representation and semantic web technologies that have, to date, remained peripheral to mainstream software engineering research. The intersection of large language models with knowledge graphs represents a particularly promising research direction, combining the natural language capabilities of neural approaches with the structural precision of symbolic representation.

For practitioners, the recommendation is direct: organizations undertaking software modernization or requirements extraction initiatives should evaluate knowledge graph infrastructure as foundational rather than optional. The question confronting enterprise architecture is not whether to adopt these approaches, but how rapidly to construct the semantic foundations that accurate code understanding requires.

---

## References

[1] Tribe AI. 2025. Legacy Code Modernization with Claude Code: Breaking Through Context Window Barriers. Tribe AI. Retrieved from https://www.tribe.ai/applied-ai/legacy-code-modernization-with-claude-code-breaking-through-context-window-barriers

[2] Semgrep. 2025. Frequently Asked Questions. Semgrep Documentation. Retrieved from https://semgrep.dev/docs/faq/overview

[3] Crew, R. 2003. Semantic Grep: Regular Expressions + Relational Abstraction. In *Proceedings of the 10th Working Conference on Reverse Engineering (WCRE '03)*. IEEE, 31-40. DOI: https://doi.org/10.1109/WCRE.2003.1287235

[4] Xu, L., Lyu, X., and Ettinger, A. 2025. On the Theoretical Limitations of Embedding-Based Retrieval. *arXiv preprint arXiv:2508.21038*. Retrieved from https://arxiv.org/html/2508.21038v1

[5] COMEX Research Team. 2025. Enhancing Source Code Representation with COMEX. Simple Science. Retrieved from https://scisimple.com/en/articles/2025-10-21-enhancing-source-code-representation-with-comex--a3qg2v5

[6] Liu, Z., et al. 2024. DFEPT: Data Flow Embedding for Enhancing Pre-Trained Model Based Vulnerability Detection. *arXiv preprint arXiv:2410.18479*. Retrieved from https://arxiv.org/html/2410.18479

[7] freeCodeCamp. 2025. How to Solve 5 Common RAG Failures with Knowledge Graphs. freeCodeCamp. Retrieved from https://www.freecodecamp.org/news/how-to-solve-5-common-rag-failures-with-knowledge-graphs/

[8] Barnett, S., Kurber, S., Seneviratne, S., and Sarkar, A. 2024. Seven Failure Points When Engineering a Retrieval Augmented Generation System. *arXiv preprint arXiv:2401.05856*. Retrieved from https://arxiv.org/html/2401.05856v1

[9] Enterprise Knowledge. 2025. Expert Analysis: Keyword Search vs Semantic Search - Part One. Enterprise Knowledge. Retrieved from https://enterprise-knowledge.com/expert-analysis-keyword-search-vs-semantic-search-part-one/

[10] CodeOntology Project. 2025. About CodeOntology. CodeOntology. Retrieved from http://codeontology.org/about

[11] CodeOntology Project. 2025. CodeOntology Parser. CodeOntology. Retrieved from https://codeontology.org/parser

[12] Ducasse, S., Lanza, M., and Tichelaar, S. 2000. Concept of the FAMIX Model. In *Proceedings of the 2nd International Symposium on Constructing Software Engineering Tools (CoSET '00)*. Retrieved from https://www.researchgate.net/figure/Concept-of-the-FAMIX-model_fig1_2805449

[13] Wikipedia Contributors. 2025. Knowledge Discovery Metamodel. Wikipedia, The Free Encyclopedia. Retrieved from https://en.wikipedia.org/wiki/Knowledge_Discovery_Metamodel

[14] Wikipedia Contributors. 2025. Semantics of Business Vocabulary and Business Rules. Wikipedia, The Free Encyclopedia. Retrieved from https://en.wikipedia.org/wiki/Semantics_of_Business_Vocabulary_and_Business_Rules

[15] KDM Analytics. 2025. Semantics of Business Vocabulary and Business Rules. KDM Analytics. Retrieved from https://kdmanalytics.com/sbvr/

[16] Auer, F., Unterkalmsteiner, M., Bajwa, I.S., and Mendez, D. 2025. Ontology-based NLP Tool for Tracing Software Requirements and Conceptual Models: An Empirical Study. *Requirements Engineering* 30, 1 (2025). Springer. DOI: https://doi.org/10.1007/s00766-025-00447-4

[17] CAST Software. 2025. CAST Imaging, the MRI for Software, Now Available as SaaS. CAST. Retrieved from https://www.castsoftware.com/news/cast-imaging-the-mri-for-software-now-available-as-saas

[18] Neo4j. 2025. CAST Software Customer Story. Neo4j. Retrieved from https://neo4j.com/customer-stories/cast-software/

[19] Fowler, M. 2025. Legacy Modernization Meets GenAI. MartinFowler.com. Retrieved from https://martinfowler.com/articles/legacy-modernization-gen-ai.html

[20] Thoughtworks. 2025. Accelerating Mainframe Modernization with GenAI. Thoughtworks. Retrieved from https://www.thoughtworks.com/en-gb/clients/mainframe-modernization-ai

[21] IBM. 2025. IBM and CAST Help Customers Accelerate Application Migration and Modernization. IBM Newsroom. Retrieved from https://www.ibm.com/new/announcements/ibm-and-cast-help-customers-accelerate-application-migration-and-modernization

[22] Linkurious. 2025. From Days to Minutes: How CAST Achieved Greater Software Intelligence with Graph Technology. Linkurious Blog. Retrieved from https://linkurious.com/blog/cast-software-intelligence/

[23] Hypercubic. 2025. Your Mainframe Expertise, Future-Proofed. Hypercubic. Retrieved from https://www.hypercubic.ai/

[24] IBM Research. 2025. GraphGen4Code: A Toolkit for Generating Code Knowledge Graphs. IBM Research. Retrieved from https://wala.github.io/graph4code/

[25] Mendix. 2024. Mendix Named a Leader in 2024 Gartner Magic Quadrant for Enterprise Low-Code Application Development Platforms. Mendix Press Release. Retrieved from https://www.mendix.com/press/mendix-named-a-leader-2024-gartner-magic-quadrant-for-enterprise-low-code-application-development-platforms-for-the-eighth-consecutive-year/

[26] Salfati Group. 2025. Enterprise Knowledge Graphs 2025: Architecture, ROI & Implementation Guide. Salfati Group. Retrieved from https://salfati.group/topics/knowledge-graphs

[27] DataIntelo. 2025. Legacy Code Modernization AI Market Research Report 2033. DataIntelo. Retrieved from https://dataintelo.com/report/legacy-code-modernization-ai-market/amp

[28] EffectiveSoft. 2025. AI-Powered Legacy Code Modernization and Migration. EffectiveSoft. Retrieved from https://www.effectivesoft.com/blog/ai-legacy-code-modernization-migration.html

[29] LANSA. 2025. Generative AI: The Core of AI Application Modernization. LANSA Blog. Retrieved from https://lansa.com/blog/application-modernization/ai-modernization/
