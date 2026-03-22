<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.26.0: Governance Library Module Absorption
Evaluator: Codex (`gz-adr-eval`)
Date: 2026-03-22

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 4 | 0.60 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 3.15/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem is concrete in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md):
   opsdev holds a substantial package of reusable governance-library modules,
   gzkit has only partial or missing equivalents, and the subtraction test is
   explicit. The module inventory and before/after state are clear, and the ADR
   now summarizes the cross-reference matrix directly. It remains a 3 because
   the matrix is still a high-level summary rather than a deeper capability
   audit with findings per module.

2. **Decision Justification - 3/4**
   The ADR now has an alternatives table, a checklist necessity table, and the
   existing anti-pattern framing in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md).
   It now defends module-by-module comparison against grouped and
   gzkit-by-default shortcuts, and it fixes the stale companion-source path to
   `../airlineops/src/opsdev/lib/`. That is solid and internally consistent.

3. **Feature Checklist - 4/4**
   The structural defect is fixed. The ADR now presents 12 numbered capability
   items that map 1:1 to the 12 briefs, and the necessity table explains the
   concrete loss if any item is removed. The items are consistent in
   granularity and logically ordered.

4. **OBPI Decomposition - 3/4**
   The package now has an explicit dependency graph, critical path, and
   verification spine in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md).
   The module-per-brief split is auditable and parallelizable. It remains a 3
   rather than a 4 because effort still varies materially across the largest
   modules, especially ADR management, references, and ADR reconciliation.

5. **Lane Assignment - 3/4**
   Heavy lane is now justified more precisely: every comparison may culminate in
   absorption into shared runtime or operator-facing surfaces, and Gate 4 is
   explicitly conditional on actual operator-visible change. That aligns the
   lane rationale with `AGENTS.md` better than the earlier blanket assertion.

6. **Scope Discipline - 3/4**
   The ADR now includes `## Non-Goals` and `### Scope Creep Guardrails` in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md).
   The boundaries are clear: no hidden architectural rewrite, no forced
   absorption, no bundling of multiple module decisions into one undocumented
   rationale.

7. **Evidence Requirements - 3/4**
   The package now has an ADR-level verification spine and every brief now
   carries Gate 4 treatment, acceptance criteria, concrete verification
   commands, and a heavy completion checklist. An evaluator can now write the
   proof plan directly from the package. It stays at 3 because most proof is
   still grep/path/test driven rather than richer module-specific runtime
   checks.

8. **Architectural Alignment - 3/4**
   The ADR names real local integration points and now follows the same
   structural pattern as strong local heavy ADRs, especially
   [ADR-0.25.0-core-infrastructure-pattern-absorption.md](../ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md):
   alternatives, necessity, dependency framing, scope guardrails, and long-term
   validity guards. It is solidly aligned with repository standards.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 4 | 3 | 4 | 2 | 3 | 3.2 |
| 02 | 4 | 3 | 4 | 2 | 3 | 3.2 |
| 03 | 4 | 3 | 4 | 2 | 3 | 3.2 |
| 04 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 05 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 06 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 07 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 08 | 4 | 3 | 3 | 4 | 3 | 3.4 |
| 09 | 4 | 3 | 3 | 4 | 3 | 3.4 |
| 10 | 4 | 3 | 3 | 4 | 3 | 3.4 |
| 11 | 4 | 3 | 3 | 4 | 3 | 3.4 |
| 12 | 4 | 3 | 3 | 4 | 3 | 3.4 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **Package-wide strength:** each brief now owns one module, one decision
  envelope, one proof contract, and one Heavy-lane gate stack. That makes the
  package reviewable rather than impressionistic.
- **Package-wide improvement:** the earlier proof defect is resolved. Every
  brief now defines acceptance criteria, verification commands, Gate 4
  treatment, and a completion checklist.
- **No-equivalent briefs (02, 03, 06, 07, 09, 12)** no longer preserve an
  impossible `Confirm` branch, which materially improves clarity and execution
  safety.
- **Path-level defect fixed:** the package now points at the real companion
  source root `../airlineops/src/opsdev/lib/` instead of the stale and missing
  `../opsdev/lib/`.
- **Largest residual risk:** actual implementation effort still varies sharply
  across modules, so the schedule may be uneven even though the decision
  framing is now sound.

## Red-Team Challenges

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | Pass | The ADR now includes a necessity table for all 12 checklist items, and each item names the concrete upstream decision gap that would remain if removed. |
| 2 | Scope | Pass | The ADR now states ADR-level non-goals and scope-creep guardrails. The strongest "should be in scope" candidate is the cross-reference matrix itself, but the ADR frames it as prerequisite evidence rather than hidden implementation scope. |
| 3 | Alternative | Fail | The current one-module-per-brief shape is defensible, but OBPI-01 through OBPI-03 still look oversized because each bundles comparison, decision, absorption path, tests, and Heavy-lane proof. The ADR acknowledges this risk but does not yet define the split trigger or fallback decomposition. |
| 4 | Dependency | Pass | The dependency graph is explicit: comparison work can run in parallel after the matrix is assembled, and only absorb-path implementation creates downstream work. That is a resilient graph with a clear single gating prerequisite. |
| 5 | Gold Standard | Pass | Against [ADR-0.25.0-core-infrastructure-pattern-absorption.md](../ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md), this ADR now matches the expected heavy-ADR structure. Its remaining weakness is the still-unsummarized audit matrix, but that is not a structural blocker. |
| 6 | Timeline | Pass | The ADR names the critical path and the parallel comparison tranche explicitly. The theoretical minimum wall-clock time is: cross-reference matrix first, then all 12 comparisons in parallel, then only the winning absorb-path modules proceed to adaptation and proof. |
| 7 | Evidence | Pass | Every brief now provides concrete verification commands, a gate stack, and completion criteria. The proof contract is generic in places, but it is no longer underspecified. |
| 8 | Consumer | Pass | The package now answers the primary maintainer questions directly: the ADR summarizes the cross-reference matrix, and Gate 4 now names `features/heavy_lane_gate4.feature` as the concrete behavioral-proof artifact for operator-visible CLI or generated-surface changes. |
| 9 | Regression | Pass | The ADR now includes long-term validity guards and explicitly says `Confirm` is not a permanent exemption. Silent drift remains possible, but the document now defines the doctrinal checks that should trigger re-opened comparison. |
| 10 | Parity | Pass | The weakest claim is "gzkit's governance layer is at least as capable as opsdev's for all generic governance patterns." Red-team view: that does not hold today; it only holds if the comparison-and-absorption program succeeds. The ADR survives the challenge because it frames that as the program objective, not as already-proven current state. |

**RED-TEAM FAILURE COUNT: 1**
**RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO**

### Red-Team Findings

1. **OBPI size risk remains real.** The largest comparison units still combine
   evaluation and possible implementation/proof obligations into one brief.
   That is manageable, but only if execution explicitly splits the absorb path
   once a module comparison confirms substantial work.
2. **Consumer-facing evidence is now concrete.** The ADR summarizes the
   cross-reference matrix and names
   `features/heavy_lane_gate4.feature` as the Gate 4 artifact when
   operator-visible behavior changes.

### Red-Team Verdict

GO. The package survives adversarial review because the failures are limited to
execution-risk and evidence-specificity concerns rather than structural
incoherence. The ADR is ready for proposal/defense review, but implementation
should treat the two findings above as active risks.

## Overall Verdict

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

## Action Items

1. No blocking structural actions.
2. Optional improvement: summarize the tidy-first cross-reference audit in the
   ADR once gathered to strengthen Problem Clarity from solid to exemplary.
3. Optional improvement: if any `Absorb` path changes operator-visible
   behavior outside the current heavy-lane CLI/generated-surface path, record
   the exact additional Gate 4 artifact in the affected brief.
4. Warning: if implementation planning shows OBPI-01 through OBPI-03 are
   larger than expected, split the execution path while preserving the current
   decision-record shape.
