<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.26.0: Governance Library Module Absorption
Evaluator: Codex (`gz-adr-eval`)
Date: 2026-03-22

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 2 | 0.30 |
| 3 | Feature Checklist | 15% | 2 | 0.30 |
| 4 | OBPI Decomposition | 15% | 2 | 0.30 |
| 5 | Lane Assignment | 10% | 2 | 0.20 |
| 6 | Scope Discipline | 10% | 2 | 0.20 |
| 7 | Evidence Requirements | 10% | 2 | 0.20 |
| 8 | Architectural Alignment | 10% | 2 | 0.20 |

**WEIGHTED TOTAL: 2.15/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem is concrete in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md):
   opsdev holds a large set of governance-library modules, gzkit only has
   partial or missing equivalents, and the subtraction test is explicit. The
   before/after state is understandable and the module inventory is specific.
   It remains a 3 because the tidy-first audit is still promised rather than
   summarized, so the baseline evidence is asserted more than demonstrated.

2. **Decision Justification - 2/4**
   The ADR has a clear decision envelope and a useful anti-pattern warning in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md),
   but it stops short of a full justification stack. There is no
   `Alternatives Considered` section, no necessity table explaining why each
   checklist item must exist, and limited treatment of counterarguments such as
   why some modules should stay inline or stay repo-local.

3. **Feature Checklist - 2/4**
   The package does contain 12 WBS rows and 12 corresponding briefs, so the
   work inventory is complete. The structural weakness is that
   `## Feature Checklist — Appraisal of Completeness` is not itself a 12-item
   capability checklist; it is a short set of meta-obligations. That leaves
   the ADR without a necessity table or a direct answer to "what capability is
   lost if item N disappears?" which stronger local ADRs already provide.

4. **OBPI Decomposition - 2/4**
   One module per brief is a defensible boundary and the numbering is complete.
   The score stays at 2 because the package does not publish a dependency
   graph, critical path, or parallelization plan, and several briefs bundle
   comparison, decision, absorption, adaptation, and tests into work units that
   likely exceed the intended 1-3 day size, especially
   [OBPI-0.26.0-01-adr-management.md](./briefs/OBPI-0.26.0-01-adr-management.md),
   [OBPI-0.26.0-02-references.md](./briefs/OBPI-0.26.0-02-references.md), and
   [OBPI-0.26.0-03-adr-recon.md](./briefs/OBPI-0.26.0-03-adr-recon.md).

5. **Lane Assignment - 2/4**
   The ADR explains why the parent work is Heavy in broad terms, and it does
   acknowledge human attestation and possible BDD proof. The weakness is the
   blanket application of Heavy to all 12 briefs without a more granular
   argument against the `AGENTS.md` rule that Heavy is reserved for external
   contract changes. Some modules may indeed change shared runtime or
   operator-facing behavior, but that case is not made item by item.

6. **Scope Discipline - 2/4**
   Scope is implied through the module list and brief-level non-goals, but the
   ADR itself does not provide ADR-level `Non-Goals`, explicit scope-creep
   guardrails, or a tested explanation of what is intentionally excluded. That
   makes the overall package boundary understandable but still too implicit.

7. **Evidence Requirements - 2/4**
   The package names broad evidence classes in
   [ADR-0.26.0-governance-library-module-absorption.md](./ADR-0.26.0-governance-library-module-absorption.md)
   and every brief includes a Heavy gate checklist. The defect is that the
   proof contract is still generic: `tests/test_lib_*.py`, possible BDD, and
   documented rationale. The briefs do not include concrete verification
   commands, module-specific acceptance criteria, or explicit Gate 4 handling
   per outcome, so "done" is not yet operationally precise.

8. **Architectural Alignment - 2/4**
   The ADR names real integration points in `src/gzkit/cli.py`,
   `src/gzkit/ledger.py`, `src/gzkit/validate.py`, and `src/gzkit/sync.py`,
   which is useful. It still trails the strongest local exemplars, especially
   [ADR-0.25.0-core-infrastructure-pattern-absorption.md](../ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md),
   because it lacks the alternatives table, necessity table, dependency graph,
   verification spine, and ADR-level scope guardrails that repository-standard
   heavy ADRs now use.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 3 | 2 | 4 | 2 | 3 | 2.8 |
| 02 | 3 | 2 | 4 | 2 | 2 | 2.6 |
| 03 | 3 | 2 | 4 | 2 | 2 | 2.6 |
| 04 | 3 | 2 | 4 | 2 | 3 | 2.8 |
| 05 | 3 | 2 | 4 | 2 | 3 | 2.8 |
| 06 | 3 | 2 | 4 | 3 | 2 | 2.8 |
| 07 | 3 | 2 | 4 | 3 | 2 | 2.8 |
| 08 | 3 | 2 | 3 | 3 | 3 | 2.8 |
| 09 | 3 | 2 | 3 | 3 | 2 | 2.6 |
| 10 | 3 | 2 | 3 | 3 | 3 | 2.8 |
| 11 | 3 | 2 | 3 | 3 | 3 | 2.8 |
| 12 | 3 | 2 | 3 | 3 | 2 | 2.6 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **Package-wide strength:** the 12 briefs cleanly cover the 12 modules named
  in the ADR, and each brief establishes a comparison frame, a target surface,
  and a decision envelope.
- **Package-wide defect:** every brief uses nearly identical proof language.
  Testability bottoms out at 2 across the board because the package never gets
  to concrete verification commands or module-specific acceptance checks.
- **No-equivalent briefs (02, 03, 06, 07, 09, 12)** preserve an impossible
  `Confirm` branch in `## REQUIREMENTS (FAIL-CLOSED)` even though their
  objectives say there is no gzkit equivalent. That is a clarity defect.
- **Largest scheduling risk:** the biggest modules still look oversized for a
  single OBPI once comparison, adaptation, tests, and heavy-lane proof are all
  included.

## Red-Team Challenges

Not run. Re-run `gz-adr-eval ADR-0.26.0 --red-team` to add the 10-challenge
adversarial review.

## Overall Verdict

[ ] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[x] NO GO - Structural revision required

## Action Items

1. Replace the current meta-only feature checklist with 12 numbered capability
   items and add a necessity table explaining the concrete loss if any one is
   removed.
2. Add `Alternatives Considered`, ADR-level `Non-Goals`, and explicit scope
   guardrails so the package boundary is defended instead of implied.
3. Publish the dependency graph, critical path, and verification spine at the
   ADR level; then add concrete verification commands, acceptance criteria, and
   Gate 4 handling to every brief.
4. Remove impossible `Confirm` branches from briefs that explicitly declare
   "gzkit equivalent: None" and re-score the package after those clarity
   defects are fixed.
