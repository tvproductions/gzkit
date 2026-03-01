# Agent Input Disciplines: A Practitioner's Reference

## Mapping Nate B. Jones's four-discipline taxonomy to Anthropic and OpenAI engineering guidance

This document synthesizes three bodies of work into a single reference for practitioners building agent-assisted workflows. The organizing framework comes from Nate B. Jones's video "If You're Prompting Like It's Last Month, You're Already Late" (February 2026), which identifies four disciplines of agent input and five primitives of specification engineering. The supporting evidence comes from Anthropic's engineering publications on context engineering and long-running agent harnesses, and from OpenAI's practical guide to building agents and their Codex long-horizon task documentation.

The three sources converge on a shared finding: as agents run longer and more autonomously, the human work of specifying, constraining, and evaluating their output becomes more demanding, not less. What follows is a discipline-by-discipline guide to what that work looks like in practice, with vendor-specific corroboration and concrete implementation patterns.

## Discipline 1: Prompt Craft

Jones defines prompt craft as the foundational skill of writing clear instructions for a single AI interaction. It is synchronous, session-based, and individual. You sit in front of a chat window, write an instruction, evaluate the output, and iterate.

Jones's requirements for good prompt craft: clear instructions, relevant examples and counter-examples, appropriate guardrails, explicit output format, and clear rules for resolving ambiguity and conflicts.

### What Anthropic says

Anthropic's prompt engineering documentation (docs.anthropic.com) covers the mechanics in detail: be clear and direct, use examples (few-shot prompting), give Claude a role, use XML tags to structure input, chain complex prompts, and let Claude think step by step. Their context engineering post (September 2025) positions prompt engineering as "the natural progression" that context engineering builds on, not replaces.

Their specific guidance on system prompts: "extremely clear and use simple, direct language that presents ideas at the right altitude for the agent." The right altitude sits between two failure modes. One extreme is hardcoded, brittle logic that tries to elicit exact behavior. The other extreme is vague, high-level guidance that "falsely assumes shared context." The optimal zone is "specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics."

On examples, Anthropic advises against stuffing a list of every edge case into a prompt. Instead, "curate a set of diverse, canonical examples that effectively portray the expected behavior of the agent." For an LLM, they write, "examples are the pictures worth a thousand words."

### What OpenAI says

OpenAI's practical guide to building agents (April 2025) frames instructions as one of three foundational components alongside models and tools. Their guidance: "every step in your routine corresponds to a specific action or output." Being explicit about the action, and even the wording of a user-facing message, "leaves less room for errors in interpretation."

On edge cases: "A robust routine anticipates common variations and includes instructions on how to handle them with conditional steps or branches." They recommend writing instructions "as if teaching a human," and suggest using advanced models to automatically convert existing documents into structured agent instructions.

Their Codex prompting guide adds that instructions should be written "as if teaching a human who has no shared context," which parallels Jones's emphasis on self-containment.

### Jones's assessment

Prompt craft is table stakes. Necessary but no longer differentiating. Jones compares it to ten-finger typing: once a professional differentiator, now simply assumed. The key limitation is that prompt craft was the whole game when AI interactions were synchronous and session-based. It breaks the moment agents start running for hours without checking in.

## Discipline 2: Context Engineering

Jones defines context engineering as the set of strategies for curating and maintaining the optimal set of tokens during an LLM task. This is the shift from crafting a single instruction to curating the entire information environment an agent operates within: system prompts, tool definitions, retrieved documents, message history, memory systems, MCP connections.

Jones's framing: "Your 200 tokens are 0.02% of what the model sees. The other 99.98%, that's context engineering."

### What Anthropic says

Anthropic published the foundational piece on context engineering in September 2025. Their definition: "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts."

Their guiding principle: "finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome." This is not about filling the context window. It is about keeping it clean.

The concept of context rot is central to their argument. Drawing on needle-in-a-haystack benchmarking, they observe that as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases. Context, therefore, "must be treated as a finite resource with diminishing marginal returns." Every new token introduced "depletes this budget by some amount, increasing the need to carefully curate the tokens available to the LLM."

On tools specifically: "One of the most common failure modes we see is bloated tool sets that cover too much functionality or lead to ambiguous decision points about which tool to use. If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."

Their recommended approach to context retrieval follows a "just in time" pattern. Rather than pre-processing all relevant data up front, agents maintain lightweight identifiers (file paths, stored queries, web links) and use these references to dynamically load data into context at runtime using tools. Claude Code uses this approach: the model writes targeted queries, stores results, and uses Bash commands to analyze large volumes of data without loading the full data objects into context.

Compaction is Anthropic's primary mechanism for long-running context management. In Claude Code, when a conversation nears the context window limit, the system passes the message history to the model to summarize and compress the most critical details. The model "preserves architectural decisions, unresolved bugs, and implementation details while discarding redundant tool outputs or messages." The agent continues with compressed context plus the five most recently accessed files.

### What OpenAI says

OpenAI's approach to context engineering appears across several documents. Their skills framework (February 2026) defines skills as "reusable, versioned instructions you can mount into containers so that agents can execute tasks more reliably." A skill is a SKILL.md manifest with YAML frontmatter, including a short "Use when vs. don't use when" block directly in the description.

A notable finding from their skills rollout: "making skills available can initially reduce correct triggering." The fix was adding negative examples and edge case coverage. Glean, an enterprise AI search company, saw skill-based routing initially drop triggering by about 20% in targeted evals, then recover after they added negative examples and edge cases in descriptions.

OpenAI's server-side compaction works similarly to Anthropic's. Unlike simple truncation, compaction allows agents to run for hours or days. Triple Whale, an e-commerce platform, reports their agent Moby "successfully navigated a session involving 5 million tokens and 150 tool calls without a drop in accuracy."

Their Codex long-horizon documentation (February 2026) describes the harness that supplies "structured context (repo metadata, file tree, diffs, command outputs) and enforces a disciplined 'done when' routine." This is why, they note, "Codex models feel better on Codex surfaces than a generic chat window."

### Implementation patterns

Both vendors converge on the same pattern for agent project files:

Anthropic's pattern: CLAUDE.md files, agent specifications, RAG pipeline design, memory architectures. For Claude Code, the recommended approach is a project-level markdown file that encodes conventions, constraints, and quality standards.

OpenAI's pattern: AGENTS.md files, skills with SKILL.md manifests, rules files. Both vendors have converged on the same open standard for skill packaging: a SKILL.md markdown file with YAML frontmatter.

Jones's observation: "People who are 10x more effective with AI than their peers are not writing 10x better prompts. They're building 10x better context infrastructure."

## Discipline 3: Intent Engineering

Jones defines intent engineering as the practice of encoding organizational purpose, goals, values, trade-off hierarchies, and decision boundaries into infrastructure that agents can act against. Context engineering tells agents what to know. Intent engineering tells agents what to want.

Jones's proof case: Klarna's AI agent resolved 2.3 million customer conversations in the first month. It optimized for resolution time (capability) rather than customer satisfaction (intent). Klarna had to rehire human agents and is still dealing with the trust aftermath.

### What Anthropic says

Anthropic does not use the term "intent engineering" explicitly, but their guidance addresses the same concern. Their system prompt guidance emphasizes encoding "the right altitude" of instruction, which includes not just what to do but the heuristics for how to decide. Their long-running agent harness documentation (November 2025) describes encoding constraints like "It is unacceptable to remove or edit tests" because without that constraint, the model would silently rewrite its own acceptance criteria.

Their agent harness uses a structured feature list in JSON where each feature has a pass/fail status. The agent is instructed to edit this file only by changing the status of a passes field, never by removing or editing the tests themselves. This is an intent constraint: the agent must pursue completion without redefining what completion means.

### What OpenAI says

OpenAI's practical guide addresses intent through their guardrails framework. They define guardrails as "critical at every stage, from input filtering and tool use to human-in-the-loop intervention, helping ensure agents operate safely and predictably in production." Their guidance includes: classify guardrails as input, output, or tool-level; implement human-in-the-loop for high-stakes decisions; and define clear escalation paths.

Their agent building documentation recommends defining "clear actions" where "every step in your routine corresponds to a specific action or output," and capturing edge cases where "a robust routine anticipates common variations and includes instructions on how to handle them."

The Codex long-horizon documentation describes a "runbook" that "tells Codex exactly how to operate: follow the plan, keep diffs scoped, run validations, update docs." This is intent encoded as operational procedure.

### Jones's framing

Intent engineering sits above context engineering the way strategy sits above tactics. "You can have perfect context and terrible intent alignment. You cannot have good intent alignment without good context." The disciplines are cumulative.

Jones also notes that failure at higher levels of the hierarchy is more serious. A bad prompt might waste your morning. Bad intent engineering can damage an entire organization, as Klarna demonstrated.

## Discipline 4: Specification Engineering

Jones defines specification engineering as the practice of writing documents that autonomous agents can execute against over extended time horizons without human intervention. This is the highest level because it concerns not just a single agent's context window but the entire organizational document corpus treated as agent-readable specification.

Jones identifies five primitives. Each is detailed below with vendor corroboration.

### Primitive 1: Self-Contained Problem Statements

Jones's definition: "Can you state a problem with enough context that the task is plausibly solvable without the agent going out and getting more information?" This is Toby Lutke's formulation applied as a specification discipline.

Jones's training exercise: take a request you would normally make conversationally (like "update the dashboard to show Q3 numbers") and rewrite it as if the person receiving it has never seen your dashboard, does not know what Q3 means in your organizational context, does not know what database to query, and has no access to any information other than what you include.

Anthropic corroboration: their system prompt guidance warns against the failure mode where engineers "provide vague, high-level guidance that fails to give the LLM concrete signals for desired outputs or falsely assumes shared context." Their long-running agent documentation shows the consequence: when given the high-level prompt "build a clone of claude.ai," the agent tried to one-shot the entire application and failed.

OpenAI corroboration: their practical guide states that instructions should be written so that "every step in your routine corresponds to a specific action or output" and that each step should leave "less room for errors in interpretation." Their Codex documentation describes a pattern where the initial prompt is treated as "the full project specification" from which the agent generates a milestone-based plan.

### Primitive 2: Acceptance Criteria

Jones's definition: "If you can't describe what done looks like, an agent can't know when to stop." The agent will stop at whatever point its internal heuristics say the task is complete, "which may bear no relationship to what you needed."

Jones's example: "build a login page" versus "build a login page that handles email passwords, social OAuth via Google and GitHub, progressive disclosure of 2FA, session persistence for 30 days, and rate limiting after five failed attempts."

Jones's training exercise: for every task you delegate, write three sentences that an independent observer could use to verify the output without asking you any questions. If you cannot write those sentences, you probably do not understand the task well enough to delegate it.

Anthropic corroboration: their long-running agent harness uses a structured feature list with over 200 features, each with explicit steps and a pass/fail status field. The feature list is the acceptance criteria made machine-readable. The agent is prohibited from editing the tests themselves.

OpenAI corroboration: their Codex long-horizon documentation describes "a progress log that serves as shared memory and audit trail." The coding agent is expected to commit progress to git with descriptive messages and "keep diffs scoped." The plan mode in Codex "breaks a larger task into a clear, reviewable sequence of steps before making changes, so you can align on approach upfront."

### Primitive 3: Constraint Architecture

Jones's definition: four categories that turn a loose specification into a reliable one.

1. Musts: what the agent has to do.
2. Must-nots: what the agent cannot do.
3. Preferences: what the agent should prefer when multiple valid approaches exist.
4. Escalation triggers: what the agent should escalate rather than decide autonomously.

Jones notes that the CLAUDE.md pattern emerging in the coding community is a practical implementation of constraint architecture. The best CLAUDE.md files are "concise, extremely high-signal constraint documents." The community consensus is that "every line needs to earn its place."

Jones's training exercise: before delegating a task, write down what a smart, well-intentioned person might do that would technically satisfy the request but produce the wrong outcome. Those failure modes become your constraint architecture.

Anthropic corroboration: their context engineering post warns against "bloated tool sets that cover too much functionality or lead to ambiguous decision points." Their long-running agent documentation includes explicit must-nots: "It is unacceptable to remove or edit tests." The initializer/coder agent pattern is itself a constraint architecture, separating environment setup from incremental coding to prevent the agent from trying to do too much at once.

OpenAI corroboration: their practical guide recommends defining "clear actions" and "capturing edge cases" as conditional steps or branches. Their skills framework includes a "Use when vs. don't use when" block directly in the skill description. The Codex runbook tells the agent "exactly how to operate," which is a constraint document.

### Primitive 4: Decomposition

Jones's definition: large tasks need to be broken into components that can be executed independently, tested independently, and integrated predictably.

Jones's training exercise: take any project you estimate at a few days of work and decompose it into subtasks that each take less than two hours, have clear input/output boundaries, and can be verified independently of the other tasks. That is the granularity at which agents work best.

Jones adds that in 2026, "you do not have to pre-specify all of those two-hour tasks when you are writing a prompt, but you do have to understand what all of those tasks are." The human's job is to "provide the break patterns that a planner agent can use to break up larger work in a reliable executable fashion."

Anthropic corroboration: their long-running agent harness splits every complex project into an environment setup phase, a progress documentation phase, and an incremental coding session, each independently verifiable. The coding agent is instructed to work on "only one feature at a time." The initializer agent writes a comprehensive feature list, and each subsequent session picks up one feature, implements it, tests it end-to-end, and commits before moving to the next.

OpenAI corroboration: their practical guide recommends starting with single-agent systems and evolving to multi-agent systems "only when needed." When multi-agent systems are warranted, they describe a manager pattern where "a central orchestrator delegates to specialized agents." Their Codex documentation describes a pattern where the initial prompt generates a milestone-based plan with checkpoints the agent can finish and verify.

OpenAI's skills documentation adds: "Skills become living SOPs (standard operating procedures): updated as your org evolves, and executed consistently by agents." This is decomposition at the organizational level.

### Primitive 5: Evaluation Design

Jones's definition: "How do you know the output is good? Not does it look reasonable, but can you prove measurably, consistently that this is good."

Jones's training exercise: for every recurring AI task, build three to five test cases with known good outputs and run them periodically, especially after model updates. This catches regressions, builds intuition for where models fail, and creates institutional knowledge about what good looks like for your specific use cases.

Anthropic corroboration: their long-running agent harness includes end-to-end testing through browser automation. The coding agent is explicitly prompted to test features end-to-end rather than relying on unit tests or curl commands against a development server. They found that "providing Claude with testing tools dramatically improved performance, as the agent was able to identify and fix bugs that weren't obvious from the code alone."

OpenAI corroboration: OpenAI publishes extensive agent evaluation documentation. Their practical guide recommends building evals early and iterating. Their Codex documentation describes a validation routine where the agent runs verification and repairs failures as it goes. Their skills documentation notes that Glean saw tool accuracy jump from 73% to 85% by using the skills framework with negative examples and edge case coverage.

## Cross-Vendor Convergence

Despite different terminology and product architectures, Anthropic and OpenAI converge on the same structural findings:

1. Long-running agents fail predictably without specification infrastructure. Anthropic's Opus 4.5 tried to one-shot a web app. OpenAI's Codex documentation describes the same failure mode as "building something impressive but wrong." Both vendors solved the problem with the same pattern: an initializer that creates a plan, a progress log, and incremental execution against a structured feature list.

2. Context is a finite resource with diminishing returns. Both vendors implement compaction (summarizing and compressing context when it grows too large). Both vendors recommend just-in-time retrieval over up-front loading. Both vendors warn against bloated tool sets and redundant instructions.

3. Constraint documents are more valuable than long instructions. Anthropic's CLAUDE.md pattern and OpenAI's AGENTS.md pattern serve the same function. Both vendors have converged on the SKILL.md open standard for packaging reusable agent instructions. The community consensus across both platforms is that these documents should be concise and high-signal.

4. Evaluation is non-negotiable. Both vendors provide evaluation frameworks. Both recommend testing end-to-end rather than relying on proxy measures. Both recommend running evals after model updates to catch regressions.

5. The human work does not decrease. This is the most consistent finding across all three sources. Jones frames it as "the specification tax." Anthropic's engineering documentation describes increasingly elaborate human-authored scaffolding for each generation of model. OpenAI's direction statement for Codex reads: "stronger teammate behavior, tighter integration with your real context, and guardrails that keep work reliable, reviewable, and easy to ship." The word "guardrails" appears repeatedly in both vendors' documentation, and guardrails are human-authored artifacts.

## gzkit Operationalization

This reference is implemented in `gzkit` through runtime and governance surfaces:

- `uv run gz readiness audit` for four-discipline/five-primitive scoring.
- `docs/governance/governance_runbook.md` for readiness-driven remediation workflow.
- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `.github/discovery-index.json` as core context/constraint surfaces.
- OBPI templates and brief workflows for self-contained problem statements, acceptance criteria, and decomposition.
- Gate evidence (`gz check`, `gz implement`, `gz gates`, `gz closeout`, `gz attest`) for evaluation design and human authority boundaries.

## Source Documents

Nate B. Jones, "If You're Prompting Like It's Last Month, You're Already Late" (video, February 2026).

Anthropic Engineering, "Effective context engineering for AI agents" (September 29, 2025). <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

Anthropic Engineering, "Effective harnesses for long-running agents" (November 26, 2025). <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>

OpenAI, "A practical guide to building agents" (April 2025). <https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf>

OpenAI Developers, "Long horizon tasks with Codex" (February 2026). <https://developers.openai.com/cookbook/examples/codex/long_horizon_tasks/>

OpenAI Developers, "Shell + Skills + Compaction: Tips for long-running agents that do real work" (February 2026). <https://developers.openai.com/blog/skills-shell-tips/>

Anthropic, Prompt Engineering Documentation. <https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview>

OpenAI Codex, "AGENTS.md" documentation. <https://developers.openai.com/codex/guides/agents-md>

Luo et al., "Towards a Science of AI Agent Reliability" (arXiv 2602.16666).
