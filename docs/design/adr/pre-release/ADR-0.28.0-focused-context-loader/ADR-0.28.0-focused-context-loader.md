---
id: ADR-0.28.0-focused-context-loader
status: Proposed
kind: feature
semver: 0.28.0
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-05-24
promoted_from: ADR-pool.focused-context-loader
---

# ADR-0.28.0-focused-context-loader: Focused Context Loader

## Persona

Craftsperson; governance-aware; treats per-turn context budget as the scarce resource the
five-move recovery plan (`docs/governance/get-out-of-jail-plan-2026-05-23.md`) was designed
to defend. Builds a single-purpose loader rather than a configurable framework. Resists
the temptation to bundle adjacent context-management ideas (`prime-context-hooks`,
`progressive-context-disclosure`) into this scope.

## Intent

**Today (before-state):** every Codex/Claude session that opens an ADR loads `AGENTS.md`
(~30 KB), `CLAUDE.md`, every skill mirror under `.claude/skills/`, and the relevant rule
files under `.claude/rules/` — orientation alone consumes ~40 KB of the per-turn budget
before any productive work begins. The namespace-router skills shipped under Move 1
(ADR-0.27.0) shrink the surface but cannot themselves deliver the ADR-scoped payload.

**Target-state (after-state):** a single CLI verb, `gz context <ADR-ID>`, will produce one
Markdown document containing the target ADR, its OBPI brief contents, the test paths that
cover its REQs (via `@covers` decorators), and the governance rules in effect for the
current gate. The document is < 30 KB for any non-pathological foundation ADR and is
suitable for piping verbatim into any agent harness. Together with Move 1's routers, an
ADR session becomes "load AGENTS.md (lean) + invoke `gz context` once," replacing
"reload the encyclopedia every turn."

This is Move 2 of the get-out-of-jail recovery plan — second-highest leverage move after
the namespace router, because Move 3 (AGENTS.md ≤ 5 KB) cannot land safely until the
context loader exists to absorb what AGENTS.md no longer carries.

---

## Decision

Promote `ADR-pool.focused-context-loader` into active implementation under the
following numbered decisions; each is grounded in the recovery-plan rationale that
"the bottleneck is promotion velocity, not insight":

1. **Add a single CLI verb, `gz context <ADR-ID>`**, registered next to `gz adr` and
   `gz state` in `src/gzkit/cli/`, because adding a verb is the lowest-surface change
   that delivers the focused payload — adding a flag to an existing verb would couple
   the loader to that verb's lifecycle, and a separate top-level command preserves the
   "one verb, one purpose" shape that the namespace routers point at.
2. **Render the payload as Markdown, not JSON or rich frames**, because the consumer is
   any LLM harness and Markdown is the lowest-friction format every harness already
   ingests; JSON would force every consumer to re-render, and rich-terminal frames would
   degrade when piped. Rationale parallels Move 1's choice of skill files as Markdown.
3. **Discover related tests via `@covers` decorators first, naming-convention second**,
   because `@covers` is already a load-bearing audit surface (see
   `.claude/rules/adr-audit.md` and `src/gzkit/trust_audits.py` covers-check); reusing
   it avoids inventing a second discovery channel and keeps the audit/loader views in
   lock-step. Naming-convention is the documented fallback for legacy tests without
   decorators.
4. **Ship two OBPIs (`context-core` + `context-slim`) under one feature ADR**, not one
   monolithic OBPI and not three (one per output section), because the meaningful
   variation is the rules section (governance vs. non-governance harness) and every
   other split would either bundle unrelated work or fragment the renderer.
5. **Lite lane**, because the verb adds no schema, ledger event, or runtime contract;
   it reads existing artifacts and writes to stdout. Heavy lane would require a
   first-class output schema, which is correctly out of scope here — the payload's
   shape is "whatever a human or harness reads," not a typed contract.

The promotion is bounded by the get-out-of-jail plan's anti-temptation list: no new
foundation ADR, no new validator scope beyond what Move 2 names, no scope creep into
the adjacent `prime-context-hooks` or `progressive-context-disclosure` pool ADRs. ---

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 0
- Logic/Engine: 0
- Interface: 0
- Observability: 0
- Lineage: 0
- Dimension Total: 0
- Baseline Range: 1-2
- Baseline Selected: 2
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 2

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.28.0-01: **context-core** — Implement `gz context <ADR-ID>` rendering the target ADR file, associated OBPI brief contents, related test file paths (discovered via `@covers` decorators or naming convention), and applicable governance rules (lane, current gate, next required action) as a single Markdown payload suitable for piping to an AI agent.
- [ ] OBPI-0.28.0-02: **context-slim** — Implement `gz context --slim <ADR-ID>` variant that omits the governance-rules section for non-governance agent harnesses. ---

## Target Scope

- **context-core** — Implement `gz context <ADR-ID>` rendering the target ADR file, associated OBPI brief contents, related test file paths (discovered via `@covers` decorators or naming convention), and applicable governance rules (lane, current gate, next required action) as a single Markdown payload suitable for piping to an AI agent.
- **context-slim** — Implement `gz context --slim <ADR-ID>` variant that omits the governance-rules section for non-governance agent harnesses.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md — this is a complementary focused view.
- No automatic context injection into agent sessions (manual piping only).

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.prime-context-hooks (complementary, not dependent)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Context payload format is accepted.
3. ADR-to-test discovery mechanism is agreed upon.

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — load-on-demand context management
that only loads `project.md` + relevant `tasks.md` + specific specs, reducing token
consumption and preventing context drift.

---

## Notes

- This is the agent-efficiency counterpart to prime-context-hooks.
- Could replace the current AGENTS.md monolith with composable context fragments.
- Key metric: tokens consumed before agent starts productive work.
- Consider: integrate with Claude Code's `/context` or CLAUDE.md conventions?

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.focused-context-loader` on 2026-05-24; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Add `--context` flag to `gz adr report`** — rejected. Would couple the loader to
   the report verb's lifecycle and conflate "show ADR status" with "package ADR for an
   agent harness." The namespace routers point at distinct verbs by design; folding
   loader output into report breaks that separation. See exemplar: ADR-0.27.0 chose a
   new router skill layer rather than overloading existing skills.
2. **Generate a JSON payload, let consumers render** — rejected per Decision item 2.
   Anti-pattern: every harness re-implementing a Markdown renderer is the opposite of
   the load-on-demand simplicity the OpenSpec exemplar (`inspired_by: openspec` in
   the pool ADR) demonstrates.
3. **One monolithic OBPI covering core + slim together** — rejected. The `--slim`
   variant is independently testable and ships a distinct user-facing affordance;
   bundling violates the OBPI decomposition matrix's single-narrative principle.
4. **Three OBPIs split by output section (ADR / brief / tests-and-rules)** — rejected.
   Splits along the renderer's internal seams rather than along user-visible variation;
   produces overlapping allowed-paths and forces synchronization on every cross-section
   change. The eval scorecard already flagged `OBPI allowed paths overlap` as a risk to
   watch.
5. **Auto-inject context into agent sessions via hook** — rejected as out-of-scope per
   the pool ADR's Non-Goals. That work lives in `ADR-pool.prime-context-hooks`; this
   ADR delivers the payload, not the injection mechanism.
6. **Keep this work in the pool backlog until reprioritized** — rejected. The
   get-out-of-jail recovery plan (`docs/governance/get-out-of-jail-plan-2026-05-23.md`)
   identifies this as Move 2, blocking Move 3 (AGENTS.md shrink). Deferral would extend
   the recovery timeline beyond 14 days.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.28.0 | Completed | g0 | 2026-05-24 | Completed |
