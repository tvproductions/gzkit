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

## Non-Goals

- No LLM-based risk scoring — all assessments must be deterministic or rule-based
- No autonomous tier promotion — tier assignment is a human governance decision
- No retroactive tier changes — tier is set at plan time and holds for the OBPI lifecycle

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

## Inspired By

- [superpowers](https://github.com/obra/superpowers) — anti-rationalization tables and excuse detection
- [GSD](https://github.com/ai-labs/gsd) — structured plan execution with deviation tracking
- [BMAD](https://github.com/bmad-method) — goal-backward verification in multi-agent workflows

## Notes

- This is the highest-complexity candidate from the capability uplift spec. Consider decomposing into separate ADRs per capability if promotion scope is too large.
- CAP-08 and CAP-09 are tightly coupled — graduated deviation without goal-backward verification creates unchecked autonomy.
- CAP-10 and CAP-21 are independent and could be promoted separately as lighter-weight ADRs.
- Post-1.0 concern per Architecture Planning Memo (2026-03-29) — foundations must lock first.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Candidate B2** (CAP-08, CAP-09, CAP-10, CAP-21). This pool ADR captures the execution intelligence capabilities that have no existing pool ADR coverage.
