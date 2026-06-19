ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.73-verification-layer-binding-audit
Evaluator: Codex manual review using gz-adr-evaluate rubric
Date: 2026-06-19

CLI PRE-SCREEN

`gz adr eval` scorecard dated 2026-06-18 reported 3.55/4.0 and GO while also
recording a score of 1 for Feature Checklist. That verdict is invalid under the
evaluation framework: any dimension scoring 1 must be revised regardless of the
weighted total. The pre-screen also listed only 8 OBPIs while the package now
contains 9, and it did not account for OBPI-02's repudiated completion state.

--- ADR-Level Scores ---

| # | Dimension | Weight | CLI | Manual | Weighted | Findings |
|---|-----------|--------|-----|--------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 3 | 0.45 | The root problem is real and specific, but the package now contains stale before/after claims: runtime fidelity passes while OBPI-02 says the central mechanism was invalid. |
| 2 | Decision Justification | 15% | 4 | 2 | 0.30 | Decisions were expanded from 6 to 9 OBPIs without a fresh defensible decomposition or updated transcript; the current ADR asserts both success and repudiation. |
| 3 | Feature Checklist | 15% | 1 | 1 | 0.15 | Checklist and OBPI set drifted repeatedly; the scorecard itself missed OBPI-09 and the transcript still describes 6 OBPIs. |
| 4 | OBPI Decomposition | 15% | 4 | 1 | 0.15 | OBPI-02 is repudiated, OBPI-08/09 are blocked behind it, and OBPI-09 is a cross-cutting validator plus multi-surface retrofit that is too broad for one clear work unit. |
| 5 | Lane Assignment | 10% | 4 | 2 | 0.20 | Heavy assignments are broadly plausible for command surfaces, but Lite/Heavy obligations are not coherent while the package is frozen and partially repudiated. |
| 6 | Scope Discipline | 10% | 4 | 1 | 0.10 | Scope expanded from 6 to 9 OBPIs and now includes waiver-ratchet governance across many surfaces before repairing the foundational OBPI-02 defect. |
| 7 | Evidence Requirements | 10% | 4 | 1 | 0.10 | `gz adr fidelity` previously passed 5/5 despite missing OBPI-08/09 and despite OBPI-02 repudiation; evidence was not proving the thesis. |
| 8 | Architectural Alignment | 10% | 4 | 2 | 0.20 | The intended trust-boundary pattern aligns with gzkit doctrine, but the current artifact violates that doctrine by trusting stale derived green checks. |

WEIGHTED TOTAL: 1.65/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | Finding |
|------|-------------|-------------|-------|------|---------|-----|---------|
| 01 qc-step-registry-and-classifier | 3 | 3 | 4 | 3 | 3 | 3.2 | Useful foundation, but downstream evidence shows the registry did not force behavioral binding. |
| 02 qc-binding-validate-scope | 2 | 1 | 4 | 1 | 2 | 2.0 | Repudiated: central negative-control mechanism shipped green-by-construction. Must be repaired before later OBPIs proceed. |
| 03 fidelity-assertions-and-gate | 3 | 3 | 4 | 3 | 3 | 3.2 | Valuable gate, but its usefulness depends on complete assertions and honest consumers. |
| 04 closeout-audit-fidelity-repoint | 2 | 2 | 4 | 2 | 2 | 2.4 | Later audit found block-less ADR bypass; consumer wiring did not fully enforce the thesis. |
| 05 absorb-dispatch-attestation-pool | 3 | 3 | 3 | 3 | 3 | 3.0 | Plausible scoped absorption, but its pool concern is still visible in state output and needs recheck after repair. |
| 06 self-check-facade-regression-corpus | 2 | 2 | 4 | 2 | 2 | 2.4 | Self-check passed while acknowledged `_NEGATIVE_CONTROL_DEBT` remained; this is not a complete self-check. |
| 07 evaluate-truth-binding | 3 | 3 | 3 | 3 | 3 | 3.0 | Remediation is plausible but must be re-evaluated after the scorecard false-GO defect. |
| 08 fidelity-presence-enforcement | 2 | 3 | 4 | 3 | 3 | 3.0 | Necessary correction, but frozen until OBPI-02 is repaired. |
| 09 waiver-ratchet-honesty-contract | 1 | 2 | 3 | 1 | 1 | 1.6 | Too broad: one OBPI spans a new validator, registry, many retrofits, docs, tests, and QC-binding integration. Split or defer after OBPI-02 repair. |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[ ] GO
[ ] CONDITIONAL GO
[x] NO GO

ACTION ITEMS:
1. Freeze ADR-0.0.73 implementation at the package level: OBPI-08 and OBPI-09 stay Draft until OBPI-02 is repaired and this scorecard is re-run.
2. Repair OBPI-02 so the QC-binding mechanism cannot pass while bound steps lack genuine negative controls.
3. Keep `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` red until it covers the OBPI-02 repair, OBPI-08, and OBPI-09.
4. Rework OBPI-09 into a smaller, defensible decomposition or defer it behind the repaired verification-layer port.

> Consider: uv run -m gzkit justify OBPI-0.0.73-02-qc-binding-validate-scope
