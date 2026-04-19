# ADR-pool.agent-execution-intelligence

- **Status:** Pool
- **Lane:** Heavy
- **Date:** 2026-04-05 (original) / 2026-04-19 (CAP-08 MODE per-invocation surface added — see Amendment History)
- **Origin:** SPEC-agent-capability-uplift Candidate B2
- **Amendments:** 2026-04-19 — added CAP-08 MODE subsection (per-invocation intent surface orthogonal to the OBPI-lifetime Tier) and enabler linkage to `ADR-pool.tdd-receipt-stream`; all original CAP-08 tier text, CAP-09/10/21/22 text, Non-Goals, Promotion Criteria, Origin preserved.

## Intent

Codify agent execution intelligence capabilities that improve runtime decision-making during governed pipeline execution. These capabilities address the gap between "agent follows rules" and "agent makes good judgment calls within rules."

## Target Scope

### CAP-08: Graduated Deviation Rules

Define a 4-tier agent autonomy model that governs how much an agent can deviate from a plan without human approval:

- **Tier 1 (Mechanical):** Execute exactly as planned; any deviation requires human approval
- **Tier 2 (Tactical):** Minor implementation adjustments allowed (ordering, naming); structural changes require approval
- **Tier 3 (Strategic):** Agent may propose and execute alternative approaches within OBPI scope; must document rationale
- **Tier 4 (Autonomous):** Agent may replan within ADR scope; human reviews at gate boundaries only

#### CAP-08 addendum (2026-04-19): MODE per-invocation intent surface

Tier is set at OBPI plan time and holds for the OBPI lifecycle (per Non-Goals below). MODE is a **complementary, finer-grained surface** that declares the operator's intent for a single session or skill invocation. Tier remains the structural ceiling; MODE cannot escalate authority beyond Tier, only declare current-turn intent within it.

**MODE declarations (operator-framed, per-invocation):**

| MODE | Authority | Typical use |
|---|---|---|
| `READ-ONLY` | No `Write`, `Edit`, `NotebookEdit`, or file-mutating tool calls; no `gz` subcommands with side effects; agent may Read, Grep, Glob, Bash (non-mutating), and report findings | Status checks, investigations, audits, exploratory reads |
| `PLAN-FIRST` | No file mutation or side-effectful `gz` subcommands until plan is presented and operator approves; plan mode / `EnterPlanMode` tooling where available | Implementation planning, scope negotiation |
| `IMPLEMENT` | Full Tier-authority; agent may mutate within Tier's deviation allowance and the active brief's Allowed Paths | Normal implementation work |

**Why MODE is orthogonal to Tier:**

- **Tier** answers: *"For this OBPI, how much deviation from the plan is allowed before human approval?"* (structural, OBPI-lifetime)
- **MODE** answers: *"For this turn/session, does the operator want the agent to act, plan, or only read?"* (intentional, per-invocation)

A Tier-4 Autonomous OBPI invoked under `MODE: READ-ONLY` still yields no mutation that turn — Tier ceiling is untouched but intent bounds current authority below the ceiling. Conversely, `MODE: IMPLEMENT` on a Tier-1 Mechanical OBPI still allows only mechanical execution; MODE declares intent but cannot raise Tier.

**Mechanical backstop (design intent, not pre-promotion decision):**

- MODE declaration emits a `mode_declared` event to the governance-event receipt stream (`ADR-pool.tdd-receipt-stream` — 2026-04-19 generalization, kind registry).
- Agent action that violates declared MODE emits a `mode_violation` event (or the MODE pair resolves as unpaired `mode_declared` with no matching `mode_resolved`, depending on pairing tension resolution in the stream ADR).
- Harness hook layer (`ADR-pool.harness-aware-execution-modes` Mode 2) can mechanically reject `Write`/`Edit` tool calls under `MODE: READ-ONLY`, closing the class of "rogue implementation on a read-only request" at the PreToolUse boundary.
- Behavioral circuit breakers (`ADR-pool.skill-behavioral-hardening`) consume the event sequence for anti-rationalization audits.

**Promotion independence consideration:** The 4-tier Tier model depends on pipeline-lifecycle stability (current Prerequisite) and is explicitly a post-1.0 concern (per Notes). The MODE surface has **no such prerequisite** — it operates at the session/skill granularity that already exists, and the 2026-04-19 evidence (insights report: 30 misunderstood-request events across 197 sessions) argues for it being promotable independently of the tier work. Promotion sequencing is a promotion-time decision; this addendum does not bind it.

### CAP-09: Goal-Backward Verification

4-level artifact assessment that verifies implementation against intent by working backward from the stated goal:

1. Does the code compile/pass lints?
2. Does the code satisfy the OBPI requirements?
3. Does the OBPI advance the ADR intent?
4. Does the ADR advance the project goal?

### CAP-10: Analysis Paralysis Guard (Stall Detection)

Detect when an agent is stuck in unproductive loops — repeated failed attempts, circular reasoning, or investigation without action — and escalate to the operator with a structured blocker envelope.

### CAP-21: Predictive Failure Analysis

Pattern-match against known failure modes before execution begins. When a plan resembles a previously-failed pattern (e.g., "editing a hook without reading the current hook first"), surface a warning before the agent proceeds.

### CAP-22: Auto-Advancing Workflow Detection (`gz next`)

Infer and execute the next governance action from current state, eliminating the need for operators to memorize the command sequence. The agent reads ledger state, active ADR/OBPI status, and recent events to determine what should happen next:

- **State signals consumed:** Ledger events (last `gate_checked`, `obpi_created`, `attestation`), OBPI completion status, ADR lifecycle state, pending reconciliation markers, uncommitted file changes
- **Decision table (deterministic, not LLM-inferred):**
  - ADR has 0 OBPIs → `gz specify`
  - OBPI authored but not implemented → `gz implement`
  - Implementation done, gates unchecked → `gz gates`
  - All gates pass, no attestation → `gz closeout`
  - Attestation recorded, not audited → `gz audit`
  - All OBPIs complete, ADR validated → `gz attest` (prompt human)
  - Dirty working tree after OBPI completion → `git-sync`
  - No active work → `gz status` (surface next priority from backlog)
- **Output modes:**
  - `gz next` — print what it would do and why, then execute
  - `gz next --dry-run` — print recommendation without executing
  - `gz next --explain` — show the full state assessment and decision rationale
- **Safety:** Never auto-executes Gate 5 (human attestation) or destructive operations. If the next step requires human judgment, `gz next` surfaces the action and waits.

**Inspired by:** [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-next` — auto-detects and runs the next workflow step by checking phase file state. gzkit's adaptation uses ledger events and a deterministic decision table rather than LLM inference for workflow routing.

## Non-Goals

- No LLM-based risk scoring — all assessments must be deterministic or rule-based
- No autonomous tier promotion — tier assignment is a human governance decision
- No retroactive tier changes — tier is set at plan time and holds for the OBPI lifecycle
- `gz next` does not skip human gates — it surfaces them, never bypasses them
- **MODE does not override Tier (2026-04-19).** MODE declares current-turn intent within Tier's structural ceiling; it cannot raise authority above the Tier assigned at OBPI plan time. A `MODE: IMPLEMENT` declaration on a Tier-1 Mechanical OBPI still grants only mechanical-execution authority.

## Dependencies

- **Complements:** ADR-pool.graduated-oversight-model (oversight tiers align with autonomy tiers)
- **Complements:** ADR-pool.controlled-agency-recovery (recovery protocol for tier violations)
- **Complements:** ADR-pool.structured-blocker-envelopes (stall detection produces blocker envelopes)
- **Prerequisite:** Stable pipeline lifecycle (ADR-0.12.0 series)
- **Enabler (2026-04-19, CAP-08 MODE only):** `ADR-pool.tdd-receipt-stream` — generalized governance-event receipt stream where `mode_declared` / `mode_resolved` / `mode_violation` events live. MODE subsection depends on the stream for its audit surface; the rest of this ADR does not.
- **Consumer/enforcer (2026-04-19):** `ADR-pool.harness-aware-execution-modes` Mode 2 hook authority may mechanically reject tool calls that violate declared MODE at the PreToolUse boundary.
- **Consumer (2026-04-19):** `ADR-pool.skill-behavioral-hardening` consumes MODE event sequences for anti-rationalization circuit breakers.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Pipeline lifecycle is stable enough to instrument (ADR-0.12.0 complete).
3. At least one tier model is validated against real OBPI execution history.
4. Stall detection heuristics are defined with deterministic thresholds.
5. `gz next` decision table is validated against at least 5 real ADR lifecycle sequences (no false routing).

## Inspired By

- [superpowers](https://github.com/obra/superpowers) — anti-rationalization tables and excuse detection
- [GSD](https://github.com/ai-labs/gsd) — structured plan execution with deviation tracking
- [BMAD](https://github.com/bmad-method) — goal-backward verification in multi-agent workflows

## Notes

- This is the highest-complexity candidate from the capability uplift spec. Consider decomposing into separate ADRs per capability if promotion scope is too large.
- CAP-08 and CAP-09 are tightly coupled — graduated deviation without goal-backward verification creates unchecked autonomy.
- CAP-10 and CAP-21 are independent and could be promoted separately as lighter-weight ADRs.
- CAP-22 (`gz next`) is also independent and could be promoted as a standalone Lite-lane ADR — it requires only ledger reads and a decision table, no new governance machinery.
- Post-1.0 concern per Architecture Planning Memo (2026-03-29) — foundations must lock first.
- **CAP-08 MODE subsection (2026-04-19) may be separately promotable.** It has no pipeline-lifecycle prerequisite, addresses a foundation-class defect (the 4.7 "rogue implementation on read-only request" pattern flagged in the 2026-04-19 insights report, ~30 misunderstood-request events across 197 sessions), and depends only on the governance-event receipt stream. Splitting it from the post-1.0 tier work is an option; this ADR does not pre-decide.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Candidate B2** (CAP-08, CAP-09, CAP-10, CAP-21). This pool ADR captures the execution intelligence capabilities that have no existing pool ADR coverage.
- [ADR-pool.tdd-receipt-stream](ADR-pool.tdd-receipt-stream.md) — enabler for CAP-08 MODE event surface (2026-04-19 generalization).
- [ADR-pool.harness-aware-execution-modes](ADR-pool.harness-aware-execution-modes.md) — Mode 2 hooks may mechanically enforce declared MODE at PreToolUse.
- [ADR-pool.skill-behavioral-hardening](ADR-pool.skill-behavioral-hardening.md) — circuit breakers consume MODE event sequences.

---

## Amendment History

### 2026-04-19 — CAP-08 MODE per-invocation intent surface

**Motivation.** The `/insights` 2026-04-19 session quantified a recurring behavioral defect: ~30 misunderstood-request events and ~42 wrong-approach events across 197 sessions (341 hours), with the "worst session" being a case where Claude autonomously began OBPI-01 implementation on a status-check request. The existing CAP-08 Tier model operates at OBPI-lifetime granularity and does not address per-invocation intent framing — the case where the operator's current-turn intent (read-only inspection) differs from the OBPI's assigned authority ceiling (e.g., Tier-3 Strategic). MODE fills that gap.

**What the amendment preserves.** The 4-tier CAP-08 model verbatim (Mechanical / Tactical / Strategic / Autonomous). All four original Non-Goals. All CAP-09, CAP-10, CAP-21, CAP-22 content. Origin (SPEC-agent-capability-uplift Candidate B2). All Dependencies. All Promotion Criteria. All Inspired By references. All original Notes.

**What the amendment adds.**

- CAP-08 addendum subsection with MODE declaration table (READ-ONLY / PLAN-FIRST / IMPLEMENT), orthogonal-to-Tier framing, mechanical-backstop sketch, and promotion-independence consideration.
- Non-Goal entry making the Tier-ceiling-override prohibition explicit for MODE.
- Dependencies entries for `tdd-receipt-stream` (enabler for event surface), `harness-aware-execution-modes` (consumer/enforcer), `skill-behavioral-hardening` (consumer).
- Note about potential independent promotion of CAP-08 MODE ahead of the full post-1.0 tier bundle.
- See Also entries for the three related pool ADRs.

**What it does NOT do.** It does not modify the 4-tier definitions; does not make MODE adjustable after plan time (MODE is per-invocation and operator-declared, not retroactively tier-changing); does not commit to a specific mechanical-backstop implementation (hook vs. CLI check vs. skill-layer rejection remain promotion-time decisions); does not force CAP-08 MODE to promote together with the tier model.

**Tracking.** Follow-on GHI will index this amendment once `ADR-pool.adr-amendment-tracking` is promoted.
