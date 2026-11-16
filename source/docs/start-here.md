# Before the graph: tell the system’s story

You do not need to know RDF to understand the idea. Start with a familiar problem: **someone needs to change a system, but the code, requirements, and reasons for past decisions tell different parts of its story.**

An ontology gives those parts shared names and explicit relationships. It helps you say which software, which requirement, which claim, and which evidence you mean. It does not make the story true merely by organizing it.

## One system. Different questions.

Imagine four people looking at the same change:

| Reader | The question they need answered |
|---|---|
| An agent | What must this change preserve, and what evidence should I inspect? |
| A product manager | What behavior do we require, and what has not been verified? |
| An engineer | Where is that behavior implemented, and what does the source show? |
| An executive | What decision is proposed, and what uncertainty remains? |

The goal is not four unrelated summaries. It is different explanations that return to the **same identities, statements, and evidence**. These are questions the model can help you organize—not a claim that this repository generates four product experiences.

## What is an ontology, in plain language?

Think of a shared map legend. A team agrees what counts as a road, a station, or a boundary, and how those things can connect. The legend does not survey the land; it gives people a consistent way to describe it.

For software, the named things might be a system, a callable, a requirement, or a decision. A relationship says something specific: a claim cites a source anchor; an anchor belongs to a captured source state.

A **graph** is those things and their connections. It need not look like a complicated network diagram. A table showing “this claim cites this source” already conveys the relationship.

## Why two ontologies?

**SAO—the Systems Abstraction Ontology—describes the software.** Its vocabulary includes systems, modules, callables, domain concepts, and operating context.

**SpecSpec—the Specification & Evidence Ontology—describes statements about it.** Its vocabulary includes requirements, claims, decisions, source evidence, and verification results.

The distinction protects meaning:

- A method is not a requirement.
- A statement about behavior is not the behavior itself.
- A source citation is not proof that the statement is correct.
- A proposed decision is not an accepted decision.

An optional bridge connects particular knowledge items to particular software entities. The models remain distinct, and SpecSpec can be used without SAO.

## Follow one behavior: reject an overdraft

The repository includes a **synthetic example**, not a customer case or an executed modernization. A COBOL excerpt and a proposed Java replacement both contain an amount-versus-balance guard. The graph keeps the following records separate:

| Part of the story | What the example records |
|---|---|
| Observation | The legacy excerpt displays a rejection when the requested amount exceeds the balance. The claim is marked `observed` and `unreviewed`. |
| Requirement | The replacement shall reject excessive withdrawals without reducing the balance. This is supplied intent, not an obligation automatically discovered in code. |
| Decision | Use a Java guard; the decision remains `proposed`. |
| Implementation assertion | An explicit link relates the requirement to the Java callable, with a separate descriptive claim as its basis. |
| Evidence | That Java claim cites an anchor at `Account.java:5–8`, within a captured source snapshot. |
| Verification | The behavioral comparison is `not_run`. It is not a pass. |

Now ask the same questions from different seats. Product can inspect the required behavior. Engineering can inspect the guard. An agent can identify an unverified obligation. An executive can see that a decision is proposed and the comparison remains unrun.

**The answer’s level of detail can change. Its evidence and status must not.** A shorter executive explanation must not turn `not_run` into “verified.”

Read the [worked example](../examples/specspec/modernization/README.md) when you want the full source context, or follow the [modeling patterns](modeling-patterns.md) to see the exact relationships.

## What the technical layers do

You can learn these names when you need them:

| Name | Plain-language job |
|---|---|
| Turtle | A text syntax for writing the graph. |
| RDFS vocabulary | Names the classes, properties, and class relationships. |
| SHACL validation | Checks whether supplied data meets the declared constraints. |
| Optional OWL supplements | Add declared reasoning relationships for consumers that choose to use them. |

Validation can catch a missing field or an invalid relationship endpoint. It cannot establish that a source really supports a claim, that a change is safe, or that two programs behave identically. Those need separate evidence and review.

## Your first useful step

Choose **one behavior**, not the whole estate. Write down what you observe, what you require, what decision is proposed, and what remains unchecked. Identify the source state behind each observation.

Then choose a next step:

1. **Understand the vocabulary:** read the [SAO overview](sao/README.md) and [SpecSpec model notes](specspec/model.md).
2. **Inspect the example:** follow the [modeling patterns](modeling-patterns.md), without installing anything.
3. **Run a real check:** use [getting started](getting-started.md) to validate the bundled graph with Nix or uv.

SAO **3.0.0 is a candidate**, and SpecSpec **0.1.0 is a draft**. The repository supplies models, validation tooling, and examples—not an automatic modernization service. See the [catalog](../ontologies/catalog.json) and [model boundaries](specspec/model.md) before depending on a particular version.
