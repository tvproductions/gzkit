# GZKit Campaign Architecture Review

You are operating **inside the GZKit repository**. I want you to perform a serious architectural and roadmap review of GZKit against the state of the art in agentic software development as of **August 2026**.

This is not a request to chase fashionable tools or rewrite GZKit around whatever is newest. GZKit has substantial prior design work and roughly eight months of development behind it. The purpose of this exercise is to determine whether its **current architecture, roadmap, and Road-to-1.0 campaign are converging on the right product** given how the agentic coding ecosystem has evolved.

The governing premise for this review is:

> **GZKit must be capable of facilitating the complete modern agentic software-development flow—not necessarily by owning or reimplementing every layer, but by making the layers coherent, composable, observable, governable, and verifiable.**

In other words, GZKit should be able to act as the durable project/process substrate through which a strong coding harness, repository contracts, specs, skills, tools, isolated execution, verification, review, and eval can work together.

Do not assume the present roadmap already reflects this architecture. Inspect what is actually in the repository.

## 1. Start by reconstructing GZKit as it exists today

Before recommending changes, inspect the repository sufficiently to understand:

* the stated product vision;
* current architecture;
* implemented capabilities;
* planned capabilities;
* ADRs and other architectural records;
* roadmap documents;
* the current **Road-to-1.0 campaign**;
* milestones and completion criteria;
* existing workflow/process abstractions;
* current treatment of specs, plans, tasks, sessions, artifacts, evidence, validation, and state;
* agent/harness integrations;
* model/vendor assumptions;
* skills or reusable procedure support;
* MCP or other tool integration;
* orchestration/subagent support;
* AFK or autonomous-loop designs;
* eval/verification concepts;
* CLI surfaces;
* persistence/state mechanisms;
* tests and acceptance criteria;
* known technical debt or incomplete areas.

Distinguish carefully among:

1. what is implemented;
2. what is designed but not implemented;
3. what exists only as intent;
4. what appears obsolete or superseded;
5. what is genuinely on the critical path to 1.0.

Do not infer implementation from documentation alone.

## 2. Use this model of the August 2026 agentic-development stack

The ecosystem has matured enough that "agentic coding framework" is no longer a single category. Treat the modern stack as several interacting layers.

## A. Project intent and durable contracts

Examples include:

* product intent;
* specifications;
* ADRs;
* architectural constraints;
* BDD/Gherkin behaviors;
* acceptance criteria;
* repository instructions such as `AGENTS.md`;
* implementation plans;
* persistent project state.

Question for GZKit:

> Can GZKit provide a durable, machine-readable and human-readable representation of what the project intends, what constraints govern it, and what constitutes acceptable completion?

## B. Coding-agent harness

Examples include:

* Claude Code;
* OpenAI Codex;
* Gemini CLI;
* Kiro;
* GitHub Copilot;
* OpenCode;
* Amp;
* Factory Droid;
* Roo;
* Cline;
* Pi;
* OpenHands;
* goose.

The important 2026 insight is that the harness itself contributes enormously to capability. Modern harnesses increasingly supply:

* context management;
* shell/filesystem access;
* planning;
* subagents;
* permissions;
* tool invocation;
* memory/context compression;
* lifecycle hooks;
* MCP;
* agent loops.

Question for GZKit:

> Does GZKit work *with* strong commodity harnesses rather than unnecessarily reimplementing them?

GZKit should not need to become another Claude Code, Codex, Pi, or OpenHands unless there is a very specific architectural reason.

Vendor neutrality remains desirable where practical, but neutrality should mean **portable project/process semantics**, not lowest-common-denominator behavior.

## C. Skills and reusable agent expertise

A major change in 2026 is the rise of **portable Agent Skills**, often represented through `SKILL.md`.

Relevant examples include:

* Superpowers;
* Matt Pocock's skills;
* Anthropic's skills;
* Vercel's skills ecosystem;
* Trail of Bits security skills;
* Semgrep skills;
* other domain-specific skill packs.

The emerging conceptual separation is:

* `AGENTS.md` / repository instructions = how to work **in this project**;
* Skills = how to perform **this kind of task**;
* MCP/native tools = what external **capabilities and information** are available.

Superpowers is particularly important as an example of expressing a development methodology through composable skills: brainstorming, planning, TDD, debugging, review, execution discipline, etc.

Matt Pocock's library is another useful example of reusable engineering judgment expressed as portable procedures.

Question for GZKit:

> Can skills be first-class participants in a GZKit-governed workflow without GZKit needing to copy their contents or hard-code knowledge of individual libraries?

Consider:

* discovery;
* declaration;
* selection;
* compatibility;
* provenance;
* trust;
* versioning;
* invocation;
* observability;
* supply-chain safety;
* project-specific policy about allowed skills.

Do not assume GZKit should build its own giant skills marketplace.

## D. Tools and external capabilities

MCP has become a major interoperability substrate, alongside native harness tools.

Question:

> Can GZKit describe, permit, constrain, observe, and reason about tools available to an agent without needing to own the tool runtime?

Think about:

* MCP servers;
* filesystem;
* shell;
* GitHub;
* browsers;
* databases;
* issue trackers;
* CI;
* external APIs;
* custom project tools.

This overlaps strongly with GZKit's governance and evidence responsibilities.

## E. Spec/process methodologies

Important examples include:

* Spec Kit;
* OpenSpec;
* GSD;
* BMAD;
* Agent OS;
* Superpowers when viewed as a methodology.

These differ significantly.

Spec Kit emphasizes intent/specification and an increasingly extensible workflow model.

OpenSpec offers a lighter brownfield-oriented proposal/spec/design/tasks/archive model.

GSD emphasizes context engineering, decomposition, planning, fresh-context execution, and increasingly Pi-based orchestration.

BMAD is a much larger end-to-end methodology with specialized agents and workflows.

Agent OS has become notable for deliberately shrinking and allowing stronger native coding agents to perform more of the mechanics.

The lesson is **not** that GZKit should reproduce all of them.

Question:

> Can GZKit accommodate different methodologies while preserving the underlying project invariants that matter?

GZKit should know the difference between:

* project truth;
* methodology;
* harness behavior;
* ephemeral agent reasoning.

Avoid locking durable project semantics to one workflow fashion.

## F. Fresh-context execution and orchestration

One of the strongest 2026 patterns is:

> **fresh context + externalized durable state + executable completion criteria**

This appears in:

* Ralph loops;
* GSD;
* Pi-based orchestration;
* subagent systems;
* agent teams;
* long-running autonomous workflows.

The point is not the specific Ralph shell loop. The architectural principle is that state belongs outside the model context and work should be divisible into bounded units that fresh agents can resume reliably.

Question:

> Does GZKit have a coherent model for sessions, tasks, handoffs, context boundaries, resumability, agent identity, provenance, and durable state?

This is especially important to evaluate against GZKit's existing AFK/autonomous-loop designs.

## G. Implementation

Actual software construction remains the center of the process:

* repository modification;
* tests;
* migrations;
* code generation;
* documentation;
* refactoring;
* Git operations;
* build execution.

Question:

> Does GZKit maintain sufficient contact with what the agent actually changed, rather than merely recording that a workflow step was supposedly completed?

Evidence should derive from reality wherever possible.

## H. Deterministic verification

This is becoming a critical separation.

Examples:

* unit/integration tests;
* Gherkin/BDD;
* type checking;
* linting;
* static analysis;
* security analysis;
* property checks;
* architectural invariants;
* build reproducibility;
* performance thresholds;
* artifact inspection.

A key principle should be:

> Agent assertion is not evidence of completion.

Question:

> Does GZKit distinguish claims, evidence, verification results, findings, and acceptance decisions?

Verification needs to be explicit, replayable where practical, and attributable.

## I. Independent agent review

There is increasing value in separating implementation from review.

Possible patterns:

* fresh-context reviewer;
* specialist review agent;
* security review;
* architecture review;
* adversarial review;
* diff inspection;
* requirement-to-implementation trace review.

Question:

> Can GZKit represent review as a distinct activity with its own evidence, findings, disposition, and provenance rather than treating the implementer's self-review as sufficient?

## J. Eval

Eval is moving from benchmark research into normal software-engineering architecture.

Relevant developments include:

* SWE-bench;
* Terminal-Bench;
* Harbor;
* DeepSWE;
* project-specific task suites;
* executable acceptance environments;
* property-based correctness approaches;
* regression evals for agent behavior.

I increasingly see the lifecycle as having two bookends:

```text
SPEC / INTENT
      |
      v
construction + validation
      |
      v
EVAL
```

BDD/Gherkin tests are already a form of eval for observable behavior, but they are not necessarily the entire eval story.

Question:

> Does GZKit have a serious model for evaluating whether both the software artifact and the agentic process achieved what the project intended?

This includes the possibility of evals for:

* product behavior;
* architectural adherence;
* process compliance;
* agent reliability;
* regression;
* task completion;
* evidence quality;
* tool usage;
* autonomy safety.

## 3. Use this as the target conceptual flow

GZKit must be able to facilitate this entire topology:

```text
                       INTENT
                         |
          specs / ADRs / behaviors / constraints
                         |
                         v
               +-------------------+
               | strong commodity  |
               | coding harness    |
               | Codex/Claude/Pi/...|
               +-------------------+
                  |       |       |
                  |       |       +---- MCP / native tools
                  |       +------------ skills
                  +-------------------- project instructions
                         |
                  bounded agent work
             fresh contexts / subagents
              sessions / delegation
                         |
                         v
                   IMPLEMENTATION
                         |
                         v
              DETERMINISTIC VERIFICATION
          tests / BDD / types / lint / static
         analysis / architectural invariants
                         |
                         v
                INDEPENDENT REVIEW
                         |
                         v
                        EVAL
                         |
                         v
           findings / evidence / decisions
                         |
                         +----> feeds future intent,
                               planning and project state
```

The important word is **facilitate**.

GZKit does **not** have to implement each box internally.

Its job may instead be to provide:

* durable state;
* contracts;
* coordination;
* schemas;
* adapters;
* orchestration;
* lifecycle semantics;
* provenance;
* evidence;
* policy;
* observability;
* verification;
* reporting;
* resumability;
* interoperability.

Determine which responsibilities genuinely belong to GZKit.

## 4. Evaluate GZKit against several architectural principles

Use these as explicit review criteria.

## Principle 1: Project state must outlive model context

Anything essential to continuation, verification, governance, or explanation must not exist only in an LLM conversation.

## Principle 2: Harnesses should be replaceable

A project governed through GZKit should ideally survive switching among Codex, Claude Code, Pi, OpenCode, etc., even if capabilities differ.

Do not confuse portability with identical behavior.

## Principle 3: Skills should be composable

GZKit should be able to use Superpowers, Matt Pocock's skills, and other skill libraries without absorbing them into GZKit's core.

## Principle 4: Evidence outranks narrative

A statement such as "tests pass" is weaker than recorded test execution.

A statement such as "requirement satisfied" is weaker than traceable evidence showing that it is.

## Principle 5: Facts, findings, judgments, and decisions are different things

Do not collapse them.

## Principle 6: Verification should be executable wherever possible

Prefer commands, tests, schemas, queries, structured comparisons, and reproducible inspections over prose assurances.

## Principle 7: Context boundaries are an architectural resource

Long conversations are not automatically better.

GZKit should make bounded work, fresh agents, handoffs, and resumption safe and normal.

## Principle 8: Methodology should not become project truth

Spec Kit, GSD, Superpowers, BMAD, OpenSpec, etc. are implementation/process choices.

Durable project intent and evidence should remain usable if the methodology changes.

## Principle 9: Human supervision remains first-class

Do not design toward an assumption that future models make supervision unnecessary.

GZKit should increase the quality and leverage of supervision rather than merely maximize autonomous token consumption.

## Principle 10: Do not solve orchestration by adding indiscriminate agent complexity

More agents, more loops, more prompts, and more tokens are not inherently improvements.

Every additional mechanism needs a clear architectural reason.

## 5. Assess the current Road-to-1.0 campaign against this model

This is the central deliverable.

Inspect the existing Road-to-1.0 plan and classify every significant milestone or workstream as one of:

* **Foundational for this target architecture**
* **Useful but non-critical for 1.0**
* **Premature**
* **Redundant with modern harness capability**
* **Over-engineered**
* **Missing**
* **Mis-sequenced**
* **Should be replaced by an integration/adaptation strategy**
* **Should explicitly move post-1.0**

I want you to identify whether we are currently spending Road-to-1.0 effort building machinery that modern harnesses, Skills, MCP, or external tooling now provide better.

Conversely, identify things GZKit uniquely needs to own and that the roadmap may currently underweight.

Pay particular attention to whether 1.0 has a coherent **vertical slice** from:

```text
intent
  -> planned work
  -> agent execution
  -> implementation evidence
  -> verification
  -> review
  -> eval
  -> durable findings/state
```

A 1.0 that contains many isolated subsystems but cannot demonstrate that complete loop would concern me.

## 6. Challenge GZKit's existing abstractions

Do not preserve an abstraction merely because we invested time in it.

For each major GZKit concept, ask:

1. What real problem does this solve?
2. Does that problem still exist in August 2026?
3. Is the harness now better positioned to solve it?
4. Is a portable Skill better positioned to solve it?
5. Is MCP/native tooling better positioned to solve it?
6. Does this belong in durable project state?
7. Does GZKit need to own it, describe it, observe it, or merely integrate with it?
8. What invariant would be lost if GZKit removed it?

Retain abstractions because they preserve important invariants, not because they are historically part of the design.

## 7. Specifically assess GZKit's relationship to these ecosystem components

Do not perform superficial feature comparisons. Ask what relationship GZKit should have to each category.

## Harnesses

* Codex
* Claude Code
* Pi
* OpenCode
* Kiro
* Gemini CLI
* OpenHands
* Cline/Roo
* other compatible harnesses

Should GZKit integrate, adapt, orchestrate, observe, or remain agnostic?

## Methodologies

* Superpowers
* Spec Kit
* OpenSpec
* GSD
* BMAD
* Agent OS

Which concepts should GZKit support generically?

Which should remain completely external?

### Skills

* Superpowers skills
* Matt Pocock's skills
* Anthropic/OpenAI-compatible Agent Skills
* domain-specific libraries

What should GZKit know about a skill?

Potentially:

* name/version;
* provenance;
* hash;
* trust policy;
* declared purpose;
* harness compatibility;
* invocation;
* outputs;
* evidence produced.

But do not assume all of these are necessary.

### Tool protocols

* MCP
* native harness tools

What governance or evidence should GZKit add?

### Autonomous execution

* Ralph-style loops
* GSD fresh-context agents
* Pi orchestration
* harness-native subagents

What is the smallest coherent GZKit abstraction that supports these without becoming yet another orchestration engine?

### Eval

Determine what a **GZKit-native eval story** should mean.

This is especially important.

## 8. Preserve what has always been valuable about GZKit

Do not interpret this exercise as permission to reduce GZKit to a thin prompt wrapper.

The project has been aiming at deeper problems than "make the coding model smarter."

Preserve or strengthen any genuinely valuable work around:

* project state;
* process integrity;
* evidence;
* artifact identity;
* durable history;
* deterministic reporting;
* architectural traceability;
* supervision surfaces;
* cross-session continuity;
* vendor portability;
* inspectability;
* replay/reconstruction;
* human review;
* explicit decisions;
* error detection;
* quality controls.

The question is whether those ideas are implemented through the **right boundaries**.

## 9. Be skeptical of two opposite failure modes

## Failure mode A: GZKit tries to own everything

This would lead toward:

* custom harness;
* custom skill system;
* custom agent protocol;
* custom MCP equivalent;
* custom spec methodology;
* custom orchestrator;
* custom evaluator;
* enormous complexity.

Avoid this unless ownership is truly necessary.

## Failure mode B: GZKit becomes trivial

At the other extreme:

```text
AGENTS.md + a few prompts + call Claude/Codex
```

would not justify GZKit's existence.

The useful center is likely:

> **GZKit owns durable project/process semantics, evidence, governance, lifecycle integrity, and evaluation surfaces while integrating strong external execution capabilities.**

Test that hypothesis rather than simply accepting it.

## 10. Evaluate whether the architecture has a natural control loop

I want you to look for something like:

```text
intent
   |
   v
work definition
   |
   v
execution
   |
   v
evidence capture
   |
   v
verification
   |
   v
review
   |
   v
eval
   |
   v
finding / decision / changed understanding
   |
   +---------------------> updated intent / next work
```

This should not be an infinite autonomous loop.

It is a **project learning and control loop**.

Determine whether GZKit presently has the concepts required to express it cleanly.

## 11. Deliverables

Produce a substantive review with these sections.

### A. Executive assessment

In approximately 5–10 paragraphs:

* What is GZKit becoming today?
* Is that still the right product?
* How well aligned is it with the August 2026 architecture described above?
* Is the Road-to-1.0 campaign pointed in the right direction?

Give me a clear judgment.

### B. Current-state architecture

Describe the architecture that actually exists now.

Separate:

* implemented;
* partial;
* designed;
* planned.

### C. State-of-the-art alignment matrix

Use a table with at least:

| Modern capability | GZKit current state | Existing mechanism | Gap | 1.0 relevance | Recommendation |

Include all major layers from this prompt.

### D. GZKit ownership boundary

Produce a table:

| Capability | GZKit should own | GZKit should integrate | Harness/skill/tool should own | Rationale |

This may be the most important architectural output.

### E. Road-to-1.0 critique

Walk through the current campaign.

Identify:

* what remains correct;
* what should change;
* what should be reordered;
* what should be removed;
* what is missing.

Do not merely append more work to the existing roadmap.

Seek simplification.

### F. Proposed revised Road-to-1.0

If revisions are warranted, propose them.

Prefer a small number of coherent milestones culminating in an end-to-end demonstrable system.

For every milestone state:

* purpose;
* capabilities;
* invariants established;
* acceptance criteria;
* dependencies;
* what is explicitly deferred.

### G. The 1.0 demonstration

Describe the scenario that should prove GZKit 1.0 exists.

I expect something stronger than "all planned commands implemented."

For example, the demonstration might involve:

1. a real repository;
2. durable intent/specification;
3. repository instructions;
4. one or more approved skills;
5. a supported coding harness;
6. bounded work assigned to an agent;
7. implementation;
8. captured evidence;
9. deterministic tests/BDD/analysis;
10. fresh-context review;
11. project-specific eval;
12. a final structured finding/decision;
13. the ability for another agent or human to reconstruct what happened.

Determine the correct form.

### H. Architectural risks

Identify the five to ten largest risks between the current repository and that 1.0.

Include risks such as:

* abstraction overreach;
* accidental reinvention;
* excessive token/process overhead;
* harness coupling;
* context pollution;
* weak verification;
* false evidence;
* workflow ceremony;
* schema complexity;
* migration burden;
* unimplemented design accumulation.

### I. Decisions required now

Produce a short list of architectural decisions that we should settle before continuing the campaign.

For each state:

* decision;
* alternatives;
* recommendation;
* why it matters now.

## 12. Distinguish 1.0 from the eventual vision

Do not turn this analysis into a demand that every possible state-of-the-art capability ship before 1.0.

I want two things kept separate:

### GZKit architecture must be able to facilitate the whole flow

That means its conceptual boundaries must not foreclose skills, MCP, subagents, fresh contexts, external harnesses, independent review, or eval.

### GZKit 1.0 needs only the minimum coherent implementation that proves the architecture

Avoid a Road-to-1.0 that becomes endless because we keep discovering more ecosystem features.

A good 1.0 should be **architecturally complete but intentionally narrow in implementation**.

## 13. Do not make novelty the goal

Some of the best answers may be boring.

If `AGENTS.md` is sufficient for a concern, use it.

If an Agent Skill should own a procedure, let it.

If Codex or Claude Code already provides excellent subagent execution, do not recreate it.

If MCP solves transport/tool discovery, integrate it.

If Git is the right durable state mechanism for something, use Git.

If Gherkin already expresses a behavioral eval adequately, do not invent a second DSL.

The goal is not for GZKit to contain more technology.

The goal is for it to create **more reliable agentic software engineering**.

## 14. Be willing to challenge prior GZKit thinking

We have spent substantial time on this project. That increases the danger of sunk-cost reasoning.

If the repository contains machinery that made sense in late 2025 but no longer makes sense in August 2026, say so.

Likewise, if ideas we already designed have become *more* important because the ecosystem has caught up with them—particularly evidence, durable state, verification, context isolation, agent supervision, and eval—say that too.

Do not optimize for agreement with the existing roadmap.

Optimize for getting GZKit to the right 1.0.

## 15. Final synthesis

End the review by completing these sentences explicitly:

> **GZKit 1.0 should be:** ...
> **GZKit should own:** ...
> **GZKit should deliberately not own:** ...
> **The most important architectural invariant is:** ...
> **The largest mistake the current Road-to-1.0 could make is:** ...
> **The single most important change I recommend to the campaign is:** ...
> **The end-to-end proof that GZKit has reached 1.0 is:** ...

Do the repository inspection first. Ground your conclusions in the actual state of GZKit, its current roadmap, and its Road-to-1.0 campaign rather than treating this prompt as a replacement specification.

The purpose of this exercise is to determine whether the work already underway is converging on a system that can serve as the **durable control, evidence, and evaluation substrate for modern agentic software development**, while allowing increasingly capable commodity agents, skills, and tools to do the work they are best positioned to do.
