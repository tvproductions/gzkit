---
id: ADR-pool.insights-browsable-by-topic
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: EveryInc/compound-engineering-plugin
---

# ADR-pool.insights-browsable-by-topic: Insights Browsable By Topic

## Status

Pool

## Intent

Add a browsable-by-topic surface over the existing `.gzkit/insights/agent-insights.jsonl` stream so agents starting work in a known area can read relevant prior corrections without parsing the full append-only log. Every Inc's Compound Engineering plugin uses `docs/solutions/<category>/` markdown directory with YAML frontmatter (`module`, `tags`, `problem_type`) categorized by problem domain (`developer-experience/`, `integrations/`, `workflow/`, `skill-design/`). CE's `AGENTS.md` § Repository Docs Convention names this as the *"compounding-learning"* surface — when implementing or debugging in a documented area, the agent reads relevant solutions as context, closing the loop where today's correction becomes tomorrow's orientation.

gzkit's current `.gzkit/insights/agent-insights.jsonl` is *auditable* (append-only, T2 ledger-adjacent, schema-validated by `gz validate --insights-shape` per advisory-rules-audit row #17a) but **not discoverable**. There is no obvious "read insights relevant to current scope" entry point. The 60+ records accumulated since 2026-03 contain pattern-level corrections (skill-feedback, agent-failure-mode evidence, doctrine drift observations, operator course-corrections) that would inform an agent starting work on a related surface — but only if surfaced. The current read pattern is essentially `grep` over the JSONL, which is neither efficient nor reliable as agent behavior.

The doctrinal axis: how does gzkit add discoverability without violating the state-doctrine principle that *"derived views are never source-of-truth"* ([`docs/governance/state-doctrine.md`](../../governance/state-doctrine.md))? The JSONL must remain the T2 system-of-record; any browsable surface is T3 derived view subject to the freshness invariants in `docs/governance/layer-three-derived-views.md`.

## Decision

_(Pool — design conversation in progress. The shape of the browsable surface is the load-bearing question; the JSONL source-of-truth is preserved across all paths.)_

Open surface decisions:

- **Indexing vocabulary.** What metadata categorizes insights? File paths? OBPI IDs? Skill names? Doctrine areas? Tag union? CE uses `module`, `tags`, `problem_type` as frontmatter axes.
- **Browsable surface shape.** Directory tree (CE-aligned), CLI query interface, in-context augmentation (SessionStart hook), or hybrid.
- **Read-loop integration.** When does an agent consult the browsable surface? SessionStart? OBPI-start? File-edit-time? Advisor pre-call? Multiple trigger points?
- **Freshness.** If a derived view is generated, what validator scope ensures it's regenerated on JSONL writes? Per state-doctrine, T3 derived views are never source-of-truth and must be regeneratable with a fail-closed freshness check.
- **Existing-records migration.** Are the 60+ JSONL records re-indexed under the new vocabulary, or grandfathered (indexed only by trivial metadata, the rest only via full-text fallback)?

## Alternatives Considered

### Path A — CE-style markdown directory

**Shape.** Generate `.gzkit/insights/by-scope/<scope>/INDEX.md` (or `docs/governance/insights-by-scope/<scope>/`) from JSONL on each new append. Each scope's `INDEX.md` lists relevant insights with short summaries + JSONL line references. Agents read the relevant scope's `INDEX.md` as orientation context when starting work in that area. Validator: `gz validate --insights-index-fresh` fail-closes when JSONL has appended since the index was last regenerated. Canonical regenerator: `gz insights register` (or similar) on every JSONL append; integrated into `gz check` and the JSONL-write code path.

**Strengths.**

- Direct CE prior art; the pattern is shipped at 16.7k★ scale.
- Browsable in `gh` web UI / IDE / agent context window without special tooling.
- The fail-closed freshness validator preserves state-doctrine T3 invariants (precedent: `gz register-adrs` + `gz validate --adr-status-fresh` per `.claude/rules/governance-core.md`).

**Weaknesses.**

- New derived surface to maintain; another T3 view to regenerate.
- Scope vocabulary must be pre-decided (file paths? OBPI IDs? skill names? doctrine areas?) — the wrong vocabulary makes the surface low-signal and incurs migration cost.
- Generation cost on every JSONL append (mitigated by batched regeneration on `gz check`).

### Path B — CLI query interface only

**Shape.** Add `gz insights query --scope <X> [--type <improvement|defect|...>] [--since <date>]` that returns matching records from JSONL at runtime. No derived files. Agents invoke the query when entering a known scope. Documentation in `AGENTS.md` or skill SKILL.md prescribes when to query.

**Strengths.**

- No derived surface; no T3 freshness problem.
- Query semantics evolve flexibly without surface migration.
- Smaller diff than Path A.

**Weaknesses.**

- Requires the agent to *know* to query — runtime discovery, not in-context discovery. The "agent forgot to query" failure mode is unmechanized.
- The query becomes a per-turn cost; agents may skip it under context pressure or as a graceful-degradation exit (anti-vibing operative claim 4).
- No browsable view in `gh` web UI; harder to surface during human review.

### Path C — Hybrid: CLI primary, index for high-frequency scopes

**Shape.** CLI query (Path B) is the primary interface. Markdown indexes (Path A) are generated only for documented "high-frequency scopes" (e.g., the most-corrected doctrine areas, the most-active skills). The operator decides which scopes get an index; the rest are queryable but not browsable.

**Strengths.**

- Composes Path A and Path B's strengths.
- Limits T3 derived-view surface to what's measurably useful.
- Lets the index vocabulary evolve based on which scopes have enough density to warrant browsing.

**Weaknesses.**

- Two surfaces to maintain; operator must curate the index roster.
- *"Which scopes are high-frequency enough"* is itself a judgment surface; without explicit thresholds, the curation becomes ad-hoc.
- The CLI-vs-index split may confuse agents about which surface to consult first.

### Path D — SessionStart hook augmentation

**Shape.** Extend the existing SessionStart hook (`scripts/session_orientation.py`) to load top-N most-recent insights (or top-N most-relevant per current branch/PR context) into the orientation block automatically. No separate browsable surface; the discoverability is *injected* at session start.

**Strengths.**

- Zero new derived surface.
- Read-loop integration is automatic — every session reads insights without agent action.
- Aligns with the existing SessionStart re-injection pattern that `docs/governance/harness-engineering-appraisal.md` names as a context-management strength.

**Weaknesses.**

- Context-window cost: top-N insights eat into the session's window budget. Per the `--instructions-files-budget` rule (advisory-rules-audit row #17b), `AGENTS.md` is gated at 40k chars; adding insights to orientation may push toward that budget.
- "Most relevant" detection is itself an inferential ranking, which is the failure mode anti-vibing operative claim 4 names (pattern-matching from training memory).
- Doesn't help mid-session lookup; only orientation-time injection. An agent entering a new scope mid-session has no signal.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related artifacts

- **CE plugin's `docs/solutions/<category>/`** — the markdown-by-topic prior art (categories: `developer-experience`, `integrations`, `workflow`, `skill-design`) with YAML frontmatter (`module`, `tags`, `problem_type`)
- **`.gzkit/insights/agent-insights.jsonl`** — current JSONL source-of-truth (T2; schema-validated by `gz validate --insights-shape`)
- **`docs/governance/state-doctrine.md`** — T3 derived-view doctrine; any browsable surface lands as T3
- **`docs/governance/layer-three-derived-views.md`** — T3 view inventory (GHI #214); the new browsable surface (if any) would register here
- **`.claude/rules/governance-core.md` § ADR status index regeneration** — precedent for T3 view with fail-closed freshness validator (`gz register-adrs` + `gz validate --adr-status-fresh`)
- **`scripts/session_orientation.py`** + SessionStart hook — current orientation injection mechanism; Path D's extension point
- **`docs/governance/harness-engineering-appraisal.md` § Third confirming thesis** — surfaces CE's compounding-learning loop as an operator-decision item
- **`ADR-pool.skill-feedback-loop`** — adjacent compounding-learning ADR; the feedback events that ADR would emit could also be browsable under this ADR's chosen surface

### Promotion guidance

The promotion author must commit to one of Path A, B, C, or D (or a fifth alternative grounded in evidence). The resulting feature ADR must include:

- Scope vocabulary decision (file paths / OBPI IDs / skill names / doctrine areas / tag union, or composite).
- T3 view freshness validator (`gz validate --insights-index-fresh` or equivalent) if a derived surface is chosen.
- Read-loop integration plan: when does an agent consult the surface? (At minimum: documented trigger points in `AGENTS.md` Behavior Rules.)
- Migration plan for the existing 60+ JSONL records: are they re-indexed under the new vocabulary, or grandfathered?
- For Path A or C: which scopes get indexes initially, and what threshold promotes a scope to "indexed"?
- For Path D: budget impact on `--instructions-files-budget` and the ranking algorithm's anti-vibing posture.

### Inspired by

[EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — the `docs/solutions/<category>/` pattern + `/ce-compound` skill embody the most concrete compounding-learning loop in published prior art. CE's framing (*"each unit of engineering work should make subsequent units easier"*) operationalizes the loop by making prior corrections *browsable from the same surface the agent reads as orientation*. gzkit's `.gzkit/insights/agent-insights.jsonl` already captures the corrections (T2-auditable); this ADR is the home for adding the T3-discoverable layer on top, preserving the source-of-truth invariant.
