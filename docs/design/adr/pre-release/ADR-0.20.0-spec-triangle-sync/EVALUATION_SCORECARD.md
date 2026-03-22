# ADR EVALUATION SCORECARD

ADR: ADR-0.20.0: Spec-Test-Code Triangle Sync
Evaluator: Codex (`gz-adr-eval`)
Date: 2026-03-22

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

WEIGHTED TOTAL: 3.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem statement is concrete and operational in [ADR-0.20.0-spec-triangle-sync.md](./ADR-0.20.0-spec-triangle-sync.md): missing spec-test-code linkage leaves audit-relevant drift invisible. It is solid, though not exemplary, because it still lacks quantified repository baseline evidence.
2. **Decision Justification - 3/4**
   The ADR names its decisions and rejected alternatives clearly in [ADR-0.20.0-spec-triangle-sync.md](./ADR-0.20.0-spec-triangle-sync.md). The boundary with ADR-0.21.0 is now internally coherent: 0.20.0 consumes existing linkage signals, while 0.21.0 owns enforcement and deeper proof semantics.
3. **Feature Checklist - 3/4**
   The checklist now maps cleanly 1:1 to the five OBPI briefs, and each item has a concrete necessity statement in [ADR-0.20.0-spec-triangle-sync.md](./ADR-0.20.0-spec-triangle-sync.md). The earlier unowned promises have been removed or assigned.
4. **OBPI Decomposition - 3/4**
   The decomposition is now stable and domain-shaped: model, extraction, engine, CLI, and advisory integration each have a distinct owner. None of the current OBPIs hide a second unowned capability.
5. **Lane Assignment - 3/4**
   Lite/Heavy assignments are now defensible. OBPIs 01-03 remain internal, while OBPIs 04-05 explicitly carry Heavy-lane docs, BDD, and attestation obligations in [OBPI-0.20.0-04-gz-drift-cli-surface.md](./obpis/OBPI-0.20.0-04-gz-drift-cli-surface.md) and [OBPI-0.20.0-05-advisory-gate-integration.md](./obpis/OBPI-0.20.0-05-advisory-gate-integration.md).
6. **Scope Discipline - 3/4**
   The package now holds a consistent scope line: deterministic extraction of existing `@covers` references is in scope, while enforcement and deeper requirement-level semantics remain in ADR-0.21.0. The scope is bounded and no longer self-contradictory.
7. **Evidence Requirements - 3/4**
   Each OBPI now has a concrete verification path consistent with the contract it claims. The package does not over-promise a drift category that lacks a report field, CLI contract, or acceptance criterion.
8. **Architectural Alignment - 3/4**
   The ADR names concrete integration points, input contracts, and guardrails in [ADR-0.20.0-spec-triangle-sync.md](./ADR-0.20.0-spec-triangle-sync.md), and it stays deterministic and repository-local in the same spirit as validated [ADR-0.10.0-obpi-runtime-surface.md](../ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md).

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 02 | 3 | 4 | 4 | 4 | 4 | 3.8 |
| 03 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 04 | 3 | 4 | 4 | 3 | 3 | 3.4 |
| 05 | 3 | 4 | 4 | 4 | 3 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any dimension must be revised.

## OBPI Notes

- **OBPI-01** is exemplary: tightly scoped, independent, and directly verifiable.
- **OBPI-02** is strong and naturally depends only on the REQ model from OBPI-01.
- **OBPI-03** now has a clean contract: unlinked specs, orphan tests, and unjustified code changes are all explicitly defined and testable.
- **OBPI-04** is structurally sound: consuming existing `@covers` references fits the clarified ADR boundary, and the CLI proof obligations are concrete.
- **OBPI-05** is back in line with Heavy-lane expectations now that Gate 4 is explicitly present.

## Red-Team Challenges

| # | Challenge | Result (Pass/Fail) | Notes |
|---|-----------|-------------------|-------|
| 1 | So What? | Pass | The ADR includes a concrete necessity table for all five checklist items in [ADR-0.20.0-spec-triangle-sync.md](./ADR-0.20.0-spec-triangle-sync.md). |
| 2 | Scope | Pass | The scope line is coherent: 0.20.0 consumes existing linkage signals; 0.21.0 owns enforcement and deeper test-traceability semantics. |
| 3 | Alternative | Pass | Five OBPIs is a defensible granularity for a Heavy ADR spanning model, extraction, engine, CLI, and advisory integration. |
| 4 | Dependency | Pass | The dependency graph is explicit and no longer hides any unowned capability behind a downstream surface. |
| 5 | Gold Standard | Pass | Compared against validated [ADR-0.10.0-obpi-runtime-surface.md](../ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md), this ADR is now comparable in decomposition coherence and evidence framing. |
| 6 | Timeline | Pass | The critical path and available parallel stages are explicit in [ADR-0.20.0-spec-triangle-sync.md](./ADR-0.20.0-spec-triangle-sync.md). |
| 7 | Evidence | Pass | The package now claims only the drift categories it actually defines and verifies in the briefs. |
| 8 | Consumer | Pass | A maintainer or operator can now answer what `gz drift` reports without inferring an unsupported intermediate category. |
| 9 | Regression | Pass | The main prior regression risk was semantic overclaiming; that defect is removed by narrowing the contract to the implemented categories. |
| 10 | Parity | Pass | The remaining doctrine claims now match the decomposition and evidence contract. |

RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO
RED-TEAM RESULT: 0 failures -> GO

## Overall Verdict

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

ACTION ITEMS:
1. No blocking structural actions.
2. Optional improvement: add quantified repository baseline evidence in the ADR intent/rationale to strengthen Problem Clarity from solid to exemplary.
3. Optional improvement: cite one or two concrete local module exemplars alongside the conceptual rationale to strengthen Architectural Alignment.
