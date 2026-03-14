---
id: ADR-pool.progressive-context-disclosure
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.storage-simplicity-profile
inspired_by: openbrain-ob1, 12-factor-agents, openspec, anthropic-long-running-agents, claude-agent-sdk, openai-agents-sdk
---

# ADR-pool.progressive-context-disclosure: Progressive Context Disclosure for Long-Running Agent Sessions

## Status

Pool

## Date

2026-03-14

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Agent context engineering and session reliability

---

## Intent

Design a progressive context disclosure system that manages what context gets
loaded when during agent sessions, replacing the current all-or-nothing model
(AGENTS.md + CLAUDE.md + all skills) with demand-driven, layered context
retrieval. The system should serve both design sessions (brainstorming,
planning, architectural decisions) and execution sessions (OBPI implementation,
arb evidence, pipeline operations) with appropriate context depth.

The core insight: a 1M token context window is a capacity upgrade, not a quality
upgrade. More hay in the haystack does not help find the needle. The right
context at the right time beats all the context all the time.

---

## Motivation

### The Compounding Context Problem

Every gzkit session currently starts with a fixed context payload: AGENTS.md,
CLAUDE.md, skill files, and whatever the operator manually provides. This
creates three failure modes:

1. **Context starvation**: the agent lacks project history, prior decisions,
   arb evidence, and cross-ADR connections that would improve its work.
2. **Context flooding**: loading everything consumes tokens before productive
   work begins and dilutes attention on what matters now.
3. **Context amnesia**: each session starts from zero. Session handoffs exist
   as a skill but are not fluid enough to create true continuity.

### Inspiration: Open Brain (OB1)

Nate B. Jones' Open Brain architecture demonstrates key principles applicable
to gzkit's context management challenge:

- **Agent-readable knowledge infrastructure**: data stored in formats agents
  can query natively, not just human-readable prose.
- **Time-bridging**: linking events, decisions, and patterns across sessions
  separated by days, weeks, or months.
- **Cross-category reasoning**: surfacing connections between artifacts an
  operator would not think to cross-reference manually.
- **Dual-surface access**: both agent (MCP) and human (CLI/visual) doors into
  the same data, each optimized for its consumer.
- **Compounding advantage**: every session captured makes the next session
  smarter. The system improves with use.
- **Model outputs driving model inputs**: the agent's reasoning about what it
  needs informs what context it pulls next, creating an agentic retrieval loop.

### Validation: Anthropic's Long-Running Agent Harness

Anthropic's own engineering research on effective harnesses for long-running
agents independently validates core assumptions in this design:

- **"Context compaction alone is insufficient"**: even frontier models with
  large context windows fall short without structured context management.
  Progressive disclosure is not a nice-to-have; it is architecturally required.
- **Explicit memory artifacts over implicit context**: their harness uses
  structured files (`claude-progress.txt`, `feature_list.json`, git history)
  as the primary context recovery mechanism -- not the context window itself.
  This validates Option C's session frames and Option A's structured payloads.
- **JSON over Markdown for machine-readable state**: structured formats reduce
  the likelihood of agents modifying specifications. Supports typed, structured
  tier payloads over prose dumps.
- **Session opening as progressive disclosure**: their coding agent follows an
  L0 -> L1 pattern at session start: orient (pwd, read progress, read git log)
  then focus (read feature list, verify existing state) then execute. This is
  the tier model in practice.
- **Verification before continuation**: every session starts by testing
  existing functionality before new work. Maps directly to arb evidence flowing
  into L1 context payloads.
- **Single-feature-per-session constraint**: scoped work prevents context
  exhaustion. Supports scoped context loading (`--scope ADR-0.13.0`).
- **Two-agent architecture (Initializer + Coding Agent)**: the initializer
  creates context infrastructure; the coding agent consumes it. This maps to
  the split between design sessions (which produce context) and execution
  sessions (which consume it).

### What This Is Not

This is not a replication of OB1's household/CRM/job-hunt use cases. This is
the appropriation of OB1's architectural principles for long-running engineering
context continuity in governance-heavy agent work.

---

## Design Options

Three architectural approaches are explored below. They are not mutually
exclusive; they represent a natural progression from immediately useful to
architecturally complete.

### Option A: Context Tiers -- Progressive Loader

**Concept**: Formalize context loading as discrete tiers (L0--L3). The agent
starts at L0 and escalates as needed, either by self-request via MCP or by
operator trigger via CLI.

**Tier definitions**:

| Tier | Name | Contents | Trigger |
|------|------|----------|---------|
| L0 | Orient | Project identity, active ADR, current lane, last session summary, open blockers | Session start (always) |
| L1 | Focus | Active OBPI brief, recent arb results, open defects, last 3 session decisions | On-demand (agent or operator) |
| L2 | Deep | Full ADR history, constraint library, lessons learned, cross-ADR linkage, test evidence map | Agent-requested or operator-triggered |
| L3 | Synthesis | Cross-artifact pattern detection, time-bridging alerts, staleness analysis, governance health narrative | Agent-driven, schedule-compatible |

**CLI surface**:

- `gz context --tier L0` (default at session start)
- `gz context --tier L1 --scope ADR-0.13.0`
- `gz context --tier L2 --scope ADR-0.13.0`
- `gz context --synthesis` (L3, may invoke LLM for pattern detection)

**MCP surface**:

- `get_context(tier, scope)` -- agent self-serves the tier it needs mid-session
- Returns structured payload, not prose dump

**Storage**: file-based by default (JSONL + markdown rendering). Optional
Supabase backend for richer queries. Same interface either way.

**Integration points**:

- `gz prime` becomes the L0 renderer
- `gz context` becomes the L1/L2 renderer
- Session handoff becomes L0 state capture at session end
- Arb evidence feeds into L1/L2 payloads

**Trade-offs**:

- (+) Clean mental model, easy to explain, immediately implementable
- (+) Natural evolution of existing `gz prime` and `gz context` pool ADRs
- (-) Risk of rigid tier boundaries that do not match real workflows
- (-) Requires deciding tier contents upfront; may need revision as usage patterns emerge

---

### Option B: Context Graph -- Demand-Pulled Knowledge Web

**Concept**: Model all gzkit artifacts as nodes in a knowledge graph with typed
relationships. The agent navigates the graph by following edges from its current
focus, loading only connected context on demand.

**Node types**:

- ADR (feature intent)
- OBPI (delivery unit)
- Session (temporal context frame)
- Arb Result (quality evidence)
- Defect (known issues)
- Lesson (accumulated learning)
- Constraint (rejection-derived rules)
- Decision (point-in-time choices with rationale)

**Edge types**:

- `parent` (OBPI -> ADR)
- `evidence` (Arb Result -> OBPI)
- `discovered` (Defect -> Session)
- `resolved_by` (Defect -> OBPI)
- `constrains` (Constraint -> ADR scope)
- `continues` (Session -> Session, temporal chain)
- `validates` (Test -> OBPI)
- `related` (cross-cutting connections)
- `informed_by` (Decision -> prior context)

**Navigation model**:

The agent starts with a focus node (e.g., the active OBPI) and traverses edges
to pull in related context. Each traversal loads only the connected artifact,
not the entire graph.

**CLI surface**:

- `gz graph show <node-id>` -- display node and immediate edges
- `gz graph traverse <node-id> --depth 2` -- walk N edges deep
- `gz graph query --type defect --related-to ADR-0.13.0` -- filtered traversal

**MCP surface**:

- `navigate(from_node, relationship, depth)` -- agent walks the graph
- `search(query, node_types)` -- semantic or keyword search across nodes

**Storage**: graph stored as JSONL edge list (file-based, Tier A). Optional
database backend for indexed traversal and semantic search (Tier C). Artifacts
remain markdown files; the graph is the index, not a replacement.

**Accumulation model**: every session, every arb run, every defect, every
operator decision adds nodes and edges. The graph grows richer over time. This
is the compounding advantage from OB1 applied to governance artifacts.

**Trade-offs**:

- (+) Most flexible, most aligned with OB1's cross-category reasoning
- (+) Naturally supports time-bridging and pattern discovery
- (+) Graph quality improves with use (compounding)
- (-) Higher implementation complexity
- (-) Graph consistency depends on disciplined edge creation (hooks, ledger events)
- (-) Cold-start problem: graph is empty until sessions accumulate

---

### Option C: Session Memory Stack -- Layered Context Accumulator

**Concept**: Treat context like a call stack. Each session pushes a frame.
Frames persist across sessions. New sessions inherit the stack and can pop/push
as needed. Progressive disclosure is the agent reading down the stack -- most
recent first, deeper history on demand.

**Frame layers**:

| Layer | Contents | Persistence |
|-------|----------|-------------|
| Current frame | Active OBPI, current pipeline stage, uncommitted changes, in-progress decisions | Written at session end |
| Recent frames | Last 3--5 sessions: decisions made, arb results, defects found, branch state | Auto-maintained |
| Deep frames | Older sessions compressed into summaries with links to full artifacts | Auto-summarized |
| Foundation | Project constants: constitution, PRD, governance rules, lane config | Static, rarely changes |

**CLI surface**:

- `gz session push` -- capture current frame at session end
- `gz session stack` -- display frame summaries (most recent first)
- `gz session peek --depth 3` -- load N frames into context
- `gz session search <query>` -- search across all frames

**MCP surface**:

- `get_frame(depth)` -- agent retrieves specific frame
- `search_frames(query)` -- temporal search across sessions

**Storage**: frames are structured JSONL documents (one per session). Summaries
auto-generated at configurable intervals. Optional Supabase for semantic search
across frames.

**Session handoff evolution**: the current session handoff skill becomes the
frame capture mechanism. Instead of a manual skill invocation, frame capture
happens automatically or via `gz session push`. Resume becomes `gz session peek`.

**Trade-offs**:

- (+) Natural evolution of existing session handoff system
- (+) Temporal model is intuitive for operators
- (+) Low implementation barrier -- extends what exists
- (-) Purely temporal model may miss cross-cutting concerns (cross-ADR patterns)
- (-) Compression/summarization quality directly affects deep frame usefulness
- (-) Stack metaphor may be too rigid for non-linear work patterns

---

## Recommended Progression

These three options form a natural implementation progression, not competing
alternatives:

1. **Start with A (Context Tiers)**: immediately useful progressive loader.
   Solves the "right context at the right time" problem today. `gz prime`
   becomes L0, `gz context` handles L1/L2. Ship value fast.

2. **Layer C underneath (Session Memory Stack)**: evolve session handoffs into
   persistent frames that feed the tier payloads. L0 draws from the most recent
   frame. L1/L2 draw from the frame stack. The tiers become views over
   accumulated session history.

3. **Build toward B (Context Graph)**: as the system matures, model the
   relationships between artifacts, sessions, evidence, and decisions as a
   navigable graph. The tiers become dynamic queries over the graph. The session
   stack becomes temporal edges in the graph. Full cross-category reasoning and
   time-bridging become possible.

At each stage, the CLI is the trigger/orchestrator/actuator. MCP is the
callable retrieval channel for agents to self-serve context mid-session. Storage
follows the storage-simplicity-profile: file-based (Tier A/B) by default,
optional database backend (Tier C) when teams want semantic search, vector
similarity, or richer queries -- consistent with arb's existing optional
Supabase integration.

---

## Agent SDK Integration Posture

### Claude Agent SDK as Runtime Substrate

The Claude Agent SDK (`claude-agent-sdk`, Python and TypeScript) provides
runtime primitives that directly serve progressive context disclosure. When a
Claude agent environment is detected, gzkit should leverage these primitives
rather than reimplementing them. When Claude is not the runtime, the CLI surface
remains fully functional standalone.

**Adoption stance**: optional integration, never hard dependency. Consistent
with the storage-simplicity-profile and the MCP posture. The SDK is an
accelerator, not a requirement.

### SDK Primitives and Their Progressive Disclosure Roles

| SDK Primitive | Progressive Disclosure Role |
|---|---|
| **Session resume/fork** | Built-in session continuity. Sessions persist as JSONL at `~/.claude/projects/<cwd>/`. gzkit session frames (Option C) can be derived from or coordinated with SDK session transcripts. Resume by ID eliminates manual handoff for Claude-hosted sessions. Fork enables exploratory design branches. |
| **SessionStart hook** | Automatic L0 injection. A `SessionStart` hook fires before the agent acts and can invoke `gz context --tier L0` to inject the orient payload. Zero operator effort for basic context priming. |
| **PostToolUse hooks** | Context escalation triggers. When the agent reads an ADR (`Read` on an ADR path), a `PostToolUse` hook can surface related L1 context (OBPI brief, recent arb results, open defects). The agent gets contextual enrichment without explicitly requesting it. |
| **Subagents** | L3 synthesis without context pollution. Spawn a subagent with `AgentDefinition` for cross-artifact pattern detection, time-bridging analysis, or governance health synthesis. The subagent receives targeted context, reasons across it, and returns a summary -- the main agent's context window stays clean. |
| **MCP integration** | Native MCP server consumption. The SDK's `mcp_servers` option connects gzkit's context MCP server with zero extra wiring. The agent calls `get_context(tier, scope)` as a tool, same as any other MCP tool. |
| **Hooks (PreToolUse)** | Context-aware guardrails. A `PreToolUse` hook on `Edit`/`Write` can check whether the agent has loaded sufficient context for the scope it is modifying -- e.g., block edits to files under an ADR scope if L1 context for that ADR has not been loaded. |

### OpenAI Agents SDK as Runtime Substrate

The OpenAI Agents SDK (`openai-agents`) provides a parallel set of runtime
primitives for Codex and OpenAI-hosted agent environments. The same adoption
stance applies: optional integration, never hard dependency.

| SDK Primitive | Progressive Disclosure Role |
|---|---|
| **Sessions with history limiting** | `SessionSettings(limit=N)` retrieves only the N most recent conversation items. This is progressive disclosure of conversation history built into the framework. gzkit can set the limit based on tier: L0 = recent items only, L2 = full history. |
| **Multiple session backends** | SQLite (in-memory or file), Redis, SQLAlchemy, Dapr. Maps directly to gzkit's storage tier model: SQLite for Tier A/B, Redis/SQLAlchemy for Tier C. |
| **Handoffs with input filters** | When one agent delegates to another, `input_filter` controls what conversation history transfers. Context filtering on agent transitions maps to tier-scoped context loading when switching between design and execution agents. |
| **Guardrails** | Input/output validation layers. Can enforce context-loading requirements: reject agent runs that lack required governance context for their scope. |
| **MCP integration** | Native tool support for MCP servers, same as Claude SDK. gzkit's context MCP server is consumed identically. |
| **Tracing** | Built-in observability for agent workflows. Can feed into gzkit's session frames: trace data becomes evidence of what the agent did and why. |
| **Multi-provider via LiteLLM** | Works with 100+ LLMs. Progressive disclosure is model-agnostic; the context management layer should not assume a specific model provider. |

### Cross-SDK Design Principles

Both SDKs confirm the same architectural pattern: the agent runtime provides
session persistence and tool execution; the application (gzkit) provides
domain-specific context management on top. Progressive disclosure is the
application-layer concern; the SDK provides the plumbing.

Key design constraints that apply across both SDKs:

- **gzkit owns the context semantics**. The SDK provides session persistence
  (raw transcripts); gzkit provides governance context (interpreted state).
  Neither replaces the other.
- **Tier loading is SDK-agnostic**. `gz context --tier L1 --scope ADR-0.13.0`
  produces the same payload regardless of whether it is consumed by a Claude
  hook, an OpenAI guardrail, or a standalone CLI invocation.
- **MCP is the universal retrieval channel**. Both SDKs support MCP natively.
  The gzkit context MCP server works identically in both environments.

### Detection and Activation

gzkit should detect the agent runtime environment and activate the appropriate
SDK integration when available:

- **Claude Code session**: detected via environment variables or hook
  infrastructure. Activate SessionStart/PostToolUse hooks for automatic
  context tier loading.
- **Claude Agent SDK programmatic use**: detected via `claude-agent-sdk` import
  availability. Expose `AgentDefinition` for context-synthesis subagents and
  hook callbacks for tier escalation.
- **Codex / OpenAI Agents SDK**: detected via `openai-agents` import
  availability or Codex environment markers. Expose guardrails for context
  validation, session settings for history limiting, and handoff input filters
  for tier-scoped context transfer.
- **Non-SDK environments**: CLI-only surface. `gz context`, `gz prime`,
  `gz session` commands work standalone. MCP server available if configured.

### Session Continuity Coordination

Agent SDK session persistence and gzkit session frames (Option C) are
complementary, not competing:

- **SDK sessions** capture the full agent transcript (prompts, tool calls,
  results). They are the raw record of what happened.
- **gzkit session frames** capture structured governance state (active OBPI,
  pipeline stage, decisions, arb results). They are the interpreted record of
  what matters.

In Claude environments, a `SessionEnd` hook can trigger `gz session push` to
capture the governance frame when a session ends. On resume, a `SessionStart`
hook loads the governance frame (L0) while the SDK restores the conversation
transcript.

In OpenAI environments, the same coordination occurs through guardrails
(pre-run context injection) and session callbacks (`session_input_callback`
for merging governance context with conversation history).

Both layers serve continuity; neither replaces the other.

---

## Relationship to Existing Pool ADRs

| Pool ADR | Relationship |
|----------|-------------|
| ADR-pool.prime-context-hooks | L0 renderer. `gz prime` becomes the session-start context surface. This ADR provides the layered architecture above it. |
| ADR-pool.focused-context-loader | L1/L2 renderer. `gz context` becomes the on-demand focused loader. This ADR adds the progressive disclosure framework. |
| ADR-pool.execution-memory-graph | Graph substrate (Option B). Provides the node/edge schema that the context graph builds on. |
| ADR-pool.pause-resume-handoff-runtime | Session frame infrastructure (Option C). Handoff create/resume become frame push/peek. |
| ADR-pool.constraint-library | Node type in the context graph. Constraints surface in L2 context payloads. |
| ADR-pool.storage-simplicity-profile | Binding guidance for storage tier decisions across all three options. |

---

## Target Scope

- Define the progressive disclosure model and its relationship to design
  sessions vs. execution sessions.
- Specify the L0--L3 tier contract: what each tier contains, token budget
  targets, and structured output format.
- Define the MCP callable interface for agent-driven context retrieval.
- Specify how session history accumulates and feeds future context payloads.
- Define the CLI command surface for operator-triggered context loading.
- Establish the arb integration: how quality evidence flows into context tiers.
- Document the progression path from tiers to session stack to graph.

---

## Non-Goals

- No replacement of ADR/OBPI artifacts as governance authority.
- No mandatory external database dependency.
- No replication of OB1's consumer use cases (household, CRM, job search).
- No automatic context injection without operator or agent consent.
- No deprecation of AGENTS.md or canonical control surfaces.

---

## Dependencies

- **Blocks on**: ADR-pool.storage-simplicity-profile
- **Blocked by**: ADR-pool.storage-simplicity-profile
- **Related**: ADR-pool.prime-context-hooks, ADR-pool.focused-context-loader,
  ADR-pool.execution-memory-graph, ADR-pool.pause-resume-handoff-runtime,
  ADR-pool.constraint-library

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The progressive disclosure tier model (L0--L3) is accepted with concrete
   payload definitions and token budget targets.
2. The CLI and MCP interface contracts are approved.
3. The relationship to existing pool ADRs (prime-context-hooks,
   focused-context-loader, execution-memory-graph, pause-resume-handoff-runtime)
   is resolved: which are subsumed, which are complementary.
4. Storage tier assignment (A/B/C) is agreed per option.
5. At least one design session or execution session scenario is walked through
   end-to-end demonstrating the progressive disclosure flow.

---

## Inspired By

- [Open Brain (OB1)](https://github.com/NateBJones-Projects/OB1) -- agent-readable
  knowledge infrastructure, semantic retrieval, cross-category reasoning,
  dual-surface access, compounding context advantage.
- [12-factor-agents](https://github.com/humanlayer/12-factor-agents) --
  Factor 3 (own your context window), Factor 5 (unify execution state and
  business state), Factor 6 (launch/pause/resume).
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) -- load-on-demand context
  management, composable context fragments.
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) --
  Anthropic engineering validation that structured memory artifacts, progressive
  session initialization, and verification-before-continuation are required for
  multi-context-window agent work.
- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) --
  runtime primitives (session resume/fork, hooks, subagents, MCP) that serve as
  the substrate for progressive disclosure when Claude is the agent runtime.
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) --
  sessions with history limiting, handoffs with input filters, guardrails, and
  multi-provider support that serve as the substrate for progressive disclosure
  in Codex/OpenAI agent environments.

---

## Notes

- The key architectural insight from OB1 is not the database or the MCP server;
  it is the principle that model outputs should drive model inputs. An agent's
  reasoning about what it needs should inform what context it pulls next. This
  creates an agentic retrieval loop that compounds with use.
- Progressive disclosure is a general-purpose context management strategy, not
  specific to gzkit. gzkit is well-positioned to pioneer it because it already
  has structured, typed, layered artifacts with explicit relationships.
- The arb system's optional Supabase integration establishes the precedent for
  Tier C storage. This ADR extends that pattern to context retrieval.
- Session handoff evolution (Option C) is the lowest-risk starting point but
  the graph model (Option B) is the long-term architectural target.
- Token budget awareness should be a first-class concern: each tier should have
  a target token envelope so the system can reason about context window
  utilization.
- Anthropic's long-running agent research confirms the two-agent pattern
  (initializer creates context, coding agent consumes it) as effective. gzkit's
  design/execution session split is a governance-native expression of this
  pattern: design sessions produce structured context artifacts (ADRs, OBPIs,
  plans), execution sessions consume them through progressive disclosure.
- The Anthropic harness's `claude-progress.txt` + `feature_list.json` + git
  history trio is a minimal implementation of what this ADR generalizes into
  session frames (Option C) and tier payloads (Option A). gzkit's advantage is
  that it already has richer structured artifacts to draw from.
- The Claude Agent SDK provides the runtime substrate for progressive
  disclosure in Claude environments. Its session resume/fork, hooks, subagents,
  and MCP support map directly onto the tier loading, context escalation,
  synthesis, and retrieval patterns described here. Adoption follows the same
  "optional, never hard dependency" posture as storage and MCP.
- The SDK's session persistence (raw transcripts) and gzkit's session frames
  (interpreted governance state) are complementary layers. Neither replaces the
  other. A SessionEnd hook bridging the two creates automatic continuity.
