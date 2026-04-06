# ADR-pool.agent-execution-intelligence

- **Status:** Pool
- **Lane:** Heavy
- **Date:** 2026-04-05
- **Origin:** SPEC-agent-capability-uplift Candidate B2

## Intent

Codify agent execution intelligence capabilities that improve runtime decision-making during governed pipeline execution. These capabilities address the gap between "agent follows rules" and "agent makes good judgment calls within rules."

## Target Scope

### CAP-08: Graduated Deviation Rules

Define a 4-tier agent autonomy model that governs how much an agent can deviate from a plan without human approval:

- **Tier 1 (Mechanical):** Execute exactly as planned; any deviation requires human approval
- **Tier 2 (Tactical):** Minor implementation adjustments allowed (ordering, naming); structural changes require approval
- **Tier 3 (Strategic):** Agent may propose and execute alternative approaches within OBPI scope; must document rationale
- **Tier 4 (Autonomous):** Agent may replan within ADR scope; human reviews at gate boundaries only

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

## Dependencies

- **Complements:** ADR-pool.graduated-oversight-model (oversight tiers align with autonomy tiers)
- **Complements:** ADR-pool.controlled-agency-recovery (recovery protocol for tier violations)
- **Complements:** ADR-pool.structured-blocker-envelopes (stall detection produces blocker envelopes)
- **Prerequisite:** Stable pipeline lifecycle (ADR-0.12.0 series)

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

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Candidate B2** (CAP-08, CAP-09, CAP-10, CAP-21). This pool ADR captures the execution intelligence capabilities that have no existing pool ADR coverage.
