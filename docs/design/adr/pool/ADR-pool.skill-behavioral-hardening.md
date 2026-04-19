---
id: ADR-pool.skill-behavioral-hardening
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: https://github.com/obra/superpowers
amendments:
  - date: 2026-04-19
    scope: Added cross-cutting "Skill-intent scope invariant" anti-rationalization pattern under Target Scope, with consumer linkage to MODE events in ADR-pool.tdd-receipt-stream. Existing 4 enriched skills, 3 new skills, all Non-Goals, all Promotion Criteria, and superpowers Inspired By preserved verbatim. No new CLI/events/infra introduced by the amendment (skill-layer SKILL.md only, consistent with original Non-Goals).
---

# ADR-pool.skill-behavioral-hardening: Skill Behavioral Hardening

## Status

Proposed

## Date

2026-03-15 (original) / 2026-04-19 (cross-cutting scope-invariant pattern added — see Amendment History)

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance skill robustness

---

## Intent

Enrich existing gzkit governance skills with behavioral defense patterns harvested from the superpowers project. gzkit skills today are procedural ("run this command, validate this output") but do not defend against agent rationalization — the primary failure mode where agents convince themselves to skip governance steps. Superpowers has proven that explicit anti-rationalization tables, circuit breakers, and stricter RED-GREEN-REFACTOR enforcement dramatically reduce this failure mode.

This ADR does not create new governance infrastructure. It strengthens the skill layer that already exists by adding behavioral defense at the OBPI execution level.

---

## Target Scope

### Enrich existing skills with anti-rationalization defense

Add rationalization tables and circuit breaker patterns to governance skills where agents most commonly take shortcuts:

- **`test`** — Rewrite from skeleton stub to enforce strict RED-GREEN-REFACTOR with anti-rationalization table. TDD is already a gzkit feature (Gate 2); this makes enforcement stricter at the skill level.
- **`gz-obpi-pipeline`** — Add rationalization defense for skipping verification, claiming completion without evidence, and bypassing ceremony. Add explicit circuit breakers.
- **`gz-plan`** — Add defense against rushing decomposition, skipping discovery questions, and premature ADR generation. Add dialogue discipline (one question at a time, YAGNI enforcement).
- **`git-sync`** — Add defense against bypassing lint/test gates and direct push.

### Create new methodology skills

Fill genuine gaps where gzkit has no coverage:

- **`gz-debug`** — Systematic 4-phase debugging methodology (root cause investigation, pattern analysis, hypothesis testing, implementation) with 3-fix circuit breaker.
- **`gz-verify`** — Verification-before-completion evidence gate. Prevents premature completion claims across all pipeline stages.
- **`gz-review-response`** — Technical evaluation of code review feedback, not performative agreement.

### Cross-skill integration

Wire new and enriched skills into the existing skill ecosystem with correct cross-references and control surface sync.

### Cross-cutting anti-rationalization patterns (2026-04-19 amendment)

The patterns below are not per-skill defenses but **invariants inherited by every skill** once this ADR promotes. They ship as a shared `.gzkit/skills/_patterns/` include (or equivalent skill-template mechanism) that enriched and new skills reference rather than copy. Promotion-time decides the include mechanism; this amendment declares the patterns.

#### Skill-intent scope invariant (canonical home)

**Defect class.** Agents invoke a named skill with a narrow declared scope (e.g. `gz-adr-status` — a status-check skill) and proceed to action beyond that scope (start implementation, create files, run pipelines) without explicit operator authorization. The 2026-04-19 `/insights` evidence: ~30 misunderstood-request events and ~42 wrong-approach events across 197 sessions; the operator-ranked "worst session of the project" was exactly this defect (Claude auto-implementing OBPI-01 on an ADR status-check request).

**Invariant (skill-layer, prose):** A skill's declared scope — its name, its frontmatter `description`, its body prose — bounds the actions the agent takes in that skill's invocation. Tool calls that mutate state (`Write`, `Edit`, `NotebookEdit`, file-mutating `gz` subcommands, `git` mutations) beyond that scope require explicit operator authorization before the tool call, not after. "If the skill seems to reveal problems, report them and wait for direction" is the default; escalation beyond the skill's scope is opt-in, not opt-out.

**Anti-rationalization table format (inherited by every skill that adopts the pattern):**

| Rationalization | Rebuttal |
|---|---|
| *"The user will want this fixed anyway — I'll save them a round trip."* | The round trip is cheap (30 seconds); the wrong-direction implementation is expensive (minutes to hours of discarded work). Report and wait. |
| *"The problem is obvious — I should just fix it."* | The *problem* being obvious is not evidence that the *fix* is in scope. Report the problem; fix authority is a separate grant. |
| *"The skill is ambiguous about whether I can act on findings."* | Ambiguity defaults to the narrower reading. If the skill's name is `*-status`, `*-check`, `*-report`, `*-audit`, `*-scan`, `*-list`, `*-view`, the default is read-only. |
| *"I've already read the problem — it would be inefficient to stop now."* | Efficiency is not a governance authority. Operator approval is. |
| *"The user said to be autonomous (auto mode) — this falls under that."* | Auto mode authorizes autonomous *execution within declared scope*. It does not authorize scope expansion. "Do not take overly destructive actions" is an explicit auto-mode constraint; silent scope expansion on a read-only invocation is adjacent to that class. |

**Circuit breaker (skill-layer):** When an agent detects itself drafting a `Write`/`Edit`/mutating-tool call whose intent is outside the declared skill scope, the skill's circuit breaker requires the agent to: (a) halt the mutating call, (b) report the finding that would motivate the call with file references, (c) explicitly request operator authorization to proceed, and (d) only after receiving authorization, continue. The circuit breaker is triggered by the agent's own reflection step that every enriched skill ends with — *"Did I stay within the declared scope? If no, halt and report."*

**Consumer linkage to receipt stream (non-mandatory for skill layer, optional for enforcement layer):**

- Under the governance-event receipt stream (`ADR-pool.tdd-receipt-stream` — 2026-04-19 generalization), MODE declarations emit `mode_declared` / `mode_resolved` events. A skill whose name or declaration implies read-only scope SHOULD emit `mode_declared` with `mode: READ-ONLY` at entry.
- A mutating tool call that violates the declared MODE SHOULD emit a `scope_widened` event *before* execution if operator-authorized, or a `mode_violation` event if not.
- This gives the circuit breaker an auditable surface; repeated `mode_violation` events within a session is a signal `ADR-pool.agent-execution-intelligence` CAP-10 (Analysis Paralysis Guard) can consume.
- **Skill-layer-only constraint preserved:** the pattern itself is markdown in SKILL.md; event emission is *consumer* behavior of the separate receipt-stream ADR and does not add governance infrastructure to this ADR.

**Default read-only skill-name prefixes (promotion-time refinement):** the pattern applies most strongly to skills whose names match `*-status`, `*-check`, `*-report`, `*-audit`, `*-scan`, `*-list`, `*-view`, `*-show`, `*-explain`, `*-trace`. Promotion-time will refine this list against the current skill catalog.

---

## Non-Goals

- No new CLI commands, ledger event types, or pipeline stage changes.
- No duplication of superpowers skills available at runtime via the installed plugin (brainstorming, plan writing, subagent orchestration, git worktrees, skill authoring TDD).
- No changes to the gate covenant or lane model.
- No new governance infrastructure — all changes are SKILL.md markdown files.

---

## Dependencies

- **Blocks on**: None. This work is independent and can proceed immediately.
- **Related**: ADR-pool.task-level-governance (the TASK tier will consume these behavioral patterns once formalized).
- **Consumer linkage (2026-04-19, optional)**: `ADR-pool.tdd-receipt-stream` — the generalized governance-event receipt stream supplies `mode_declared`/`mode_resolved`/`mode_violation`/`scope_widened`/`scope_narrowed` kinds that the skill-intent scope invariant can emit to for audit surface. Consumer-only: the stream ADR owns the event types; this ADR describes the skill-layer pattern that emits them. The skill-layer defense stands without the stream; the stream adds mechanical auditability.
- **Consumer linkage (2026-04-19, optional)**: `ADR-pool.agent-execution-intelligence` CAP-08 MODE subsection — MODE declaration is the per-invocation intent surface that the scope invariant references. If CAP-08 MODE promotes first, this ADR's scope-invariant pattern integrates with it; if this ADR promotes first, the pattern stands on its own with manual MODE declarations in SKILL.md body prose.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Anti-rationalization table format is agreed (consistent structure across all enriched skills).
2. Circuit breaker pattern is agreed (failure count, escalation action, human gate).
3. New skill scope is confirmed (gz-debug, gz-verify, gz-review-response are the right set).
4. Acceptance criteria can be defined for each enriched/new skill independently.

---

## Notes

- Superpowers (github.com/obra/superpowers) demonstrates that treating agent rationalization as the primary failure mode and defending against it explicitly with tables of excuses and rebuttals is highly effective.
- gzkit's hooks already enforce governance mechanically (pipeline-gate blocks writes, plan-audit-gate blocks plan exit). This ADR adds rhetorical defense at the skill layer to catch drift BEFORE hooks need to block.
- TDD is already Gate 2 in gzkit. The `test` skill rewrite makes RED-GREEN-REFACTOR enforcement stricter, not adding a new capability.
- The three new skills (gz-debug, gz-verify, gz-review-response) have no superpowers equivalent that integrates with gzkit's governance model (ledger, pipeline, OBPI scope).

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-15, CAP-16, CAP-17, CAP-19** (native TDD, debugging, code review, anti-rationalization). Spec adds competitive source attribution and design rationale from superpowers, spec-kit, GSD, and BMAD patterns.
- [ADR-pool.tdd-receipt-stream](ADR-pool.tdd-receipt-stream.md) — 2026-04-19 consumer linkage: governance-event receipt stream supplying MODE/scope event kinds for the skill-intent scope invariant's audit surface.
- [ADR-pool.agent-execution-intelligence](ADR-pool.agent-execution-intelligence.md) — 2026-04-19 consumer linkage: CAP-08 MODE addendum is the per-invocation intent surface the scope invariant references.

---

## Amendment History

### 2026-04-19 — Cross-cutting skill-intent scope invariant

**Motivation.** The 2026-04-19 `/insights` session quantified the operator-labeled "worst session of the project" as a specific class of defect: Claude autonomously began OBPI-01 implementation work when the operator invoked a status-check skill. Across 197 sessions, ~30 misunderstood-request events and ~42 wrong-approach events reflect the same class. The existing skill-behavioral-hardening Target Scope enriches four specific skills with their own anti-rationalization patterns, but does not address the cross-cutting invariant that every skill's declared scope bounds the actions taken within it. This amendment adds that cross-cutting pattern as a canonical home.

**What the amendment preserves.** Intent verbatim ("strengthens the skill layer that already exists by adding behavioral defense at the OBPI execution level"). All four original Non-Goals, especially *"No new CLI commands, ledger event types, or pipeline stage changes"* and *"all changes are SKILL.md markdown files"* — the amendment's pattern is markdown in SKILL.md; event emission is consumer behavior of the stream ADR, not infrastructure added here. All four enriched-skill entries (`test`, `gz-obpi-pipeline`, `gz-plan`, `git-sync`) verbatim with their original per-skill defense descriptions. All three new-skill entries (`gz-debug`, `gz-verify`, `gz-review-response`). Cross-skill integration. All four Promotion Criteria. Superpowers Inspired By.

**What the amendment adds.**

- New § Target Scope subsection "Cross-cutting anti-rationalization patterns (2026-04-19 amendment)" with the skill-intent scope invariant as its first named pattern.
- Anti-rationalization table with 5 rebuttals covering the specific rationalizations observed in session evidence (round-trip, obvious-problem, ambiguity, efficiency, auto-mode).
- Circuit breaker sketch for skill-layer self-detection.
- Consumer linkage to the governance-event receipt stream and CAP-08 MODE (both clearly labeled *optional* and *non-mandatory* to preserve the skill-layer-only Non-Goal).
- Default read-only skill-name prefix list for promotion-time refinement.
- Dependencies entries noting the two consumer linkages.
- See Also entries linking to the stream ADR and CAP-08.

**What it does NOT do.** It does not add new CLI commands (the receipt-stream linkage consumes events that the stream ADR owns). It does not add new ledger event types (same). It does not modify the gate covenant or lane model. It does not pre-commit to an include mechanism for the shared pattern (promotion-time decision). It does not pre-resolve the skill-name prefix list (promotion-time refines it). It does not pre-require stream-ADR promotion — the skill-layer pattern stands alone.

**Tracking.** Follow-on GHI will index this amendment once `ADR-pool.adr-amendment-tracking` is promoted.
