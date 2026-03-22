<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.21.0: Tests as Spec Verification Surface
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

**WEIGHTED TOTAL: 3.00/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem is concrete in
   [ADR-0.21.0-tests-for-spec.md](./ADR-0.21.0-tests-for-spec.md): informal
   `@covers` usage leaves auditors grepping tests by hand, and the desired
   after-state is specific. It is not exemplary because the ADR does not
   quantify the current baseline from the tidy-first audit it calls out.

2. **Decision Justification - 3/4**
   The ADR names decisions and three alternatives in
   [ADR-0.21.0-tests-for-spec.md](./ADR-0.21.0-tests-for-spec.md), but the
   package no longer has a structural contradiction around validation. The ADR
   intent, anti-pattern warning, and
   [OBPI-0.21.0-01-covers-decorator-and-registration.md](./obpis/OBPI-0.21.0-01-covers-decorator-and-registration.md)
   now agree that `@covers` must validate both REQ syntax and brief-backed REQ
   existence. The language-agnostic proof metadata contract is also justified
   explicitly as a portability decision rather than a hidden add-on.

3. **Feature Checklist - 3/4**
   The five numbered checklist items now map 1:1 to five briefs, and the
   necessity table names the loss for each item in
   [ADR-0.21.0-tests-for-spec.md](./ADR-0.21.0-tests-for-spec.md). Semantic
   validation ownership is explicit in OBPI-01, and the language-agnostic proof
   metadata contract is now a first-class checklist promise inside OBPI-05
   instead of an implied footnote.

4. **OBPI Decomposition - 3/4**
   The package is decomposed along real boundaries: decorator, scanner, CLI,
   audit integration, and docs. The dependency graph is explicit and acyclic.
   It stops at solid rather than exemplary because OBPI-05 still bundles
   operator docs, migration guidance, and the language-agnostic proof contract
   into a single documentation-heavy unit.

5. **Lane Assignment - 3/4**
   The Lite assignments for OBPIs 01-02 are defensible, and Heavy for the new
   CLI and audit output is correct. The package now carries Heavy-lane
   obligations consistently into
   [OBPI-0.21.0-03-gz-covers-cli.md](./obpis/OBPI-0.21.0-03-gz-covers-cli.md),
   [OBPI-0.21.0-04-adr-audit-integration.md](./obpis/OBPI-0.21.0-04-adr-audit-integration.md),
   and
   [OBPI-0.21.0-05-operator-docs-and-migration.md](./obpis/OBPI-0.21.0-05-operator-docs-and-migration.md)
   with explicit BDD and human-attestation treatment.

6. **Scope Discipline - 3/4**
   The ADR has explicit non-goals and guardrails in
   [ADR-0.21.0-tests-for-spec.md](./ADR-0.21.0-tests-for-spec.md), and its
   boundary with ADR-0.20.0 is clearly stated. The exclusions are good, but
   the argument for the language-agnostic contract being in scope now is still
   lighter than the rest of the package.

7. **Evidence Requirements - 3/4**
   The package now includes explicit verification-command sections for all five
   OBPIs, plus an ADR-level verification spine in
   [ADR-0.21.0-tests-for-spec.md](./ADR-0.21.0-tests-for-spec.md). An evaluator
   can now read the command set directly from the package instead of inventing
   it, and the Heavy briefs carry concrete docs/BDD verification paths.

8. **Architectural Alignment - 3/4**
   The ADR has strong local alignment: it cites
   `src/gzkit/triangle.py`, `src/gzkit/traceability.py`,
   `src/gzkit/commands/covers.py`, and the ADR-0.20.0 boundary. It is solid,
   but not exemplary, because it relies more on intent than on concrete local
   exemplars for similar CLI and audit-surface patterns.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 02 | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 03 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 04 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 05 | 3 | 3 | 4 | 3 | 3 | 3.2 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **OBPI-01** is valuable and reasonably sized, but its clarity is reduced by
  its dependency on ADR-0.20.0's upstream REQ extraction contract, though the
  brief now owns both syntax and existence validation clearly.
- **OBPI-02** is a coherent follow-on unit with clear value and declared
  dependency on OBPI-01.
- **OBPI-03** has a sound Heavy surface, but its proof contract would be
  stronger with explicit verification commands and example outputs, which the
  brief now provides directly.
- **OBPI-04** is correctly positioned after the CLI, yet its Heavy-lane
  obligations are now explicit, including Gate 4 treatment for the
  operator-facing output change.
- **OBPI-05** has clear operator value, but most of its acceptance proof still
  depends on manual reading more than runtime surfaces do; still, the brief now
  includes concrete grep/build/test commands and treats the language-agnostic
  contract as a first-class deliverable.

## Red-Team Challenges

| # | Challenge | Result (Pass/Fail) | Notes |
|---|-----------|-------------------|-------|
| 1 | So What? | Pass | The necessity table gives a concrete repository/operator loss for each of the five checklist items. |
| 2 | Scope | Pass | The ADR now distinguishes runtime scope from doctrine scope: non-Python proof metadata is in scope as documentation, but runtime ingestion is explicitly out of scope pending a future ADR. |
| 3 | Alternative | Pass | Five OBPIs remains defensible: decorator, scanner, CLI, audit integration, and operator adoption each own a distinct surface. |
| 4 | Dependency | Pass | OBPI-03 is the obvious single point of downstream dependency, but the graph names that openly and keeps the blocked branches explicit. |
| 5 | Gold Standard | Pass | Against ADR-0.20.0, this package now matches the local standard for numbered checklist mapping, Heavy-lane gate structure, and verification-command specificity. |
| 6 | Timeline | Pass | The critical path is explicit, and OBPI-05 can run in parallel with OBPI-04 after OBPI-03 lands. |
| 7 | Evidence | Pass | Every OBPI now exposes concrete commands, and the ADR carries a verification spine rather than forcing the evaluator to infer one. |
| 8 | Consumer | Pass | The remaining maintainer question about REQ-existence validation is now answered: the decorator consumes a cached requirement registry derived from ADR-0.20.0 brief extraction. |
| 9 | Regression | Pass | Long-term guards are now named: unit tests protect decorator/scanner behavior, BDD protects operator surfaces, and non-Python proof metadata is explicitly barred from runtime ingestion without a future ADR. |
| 10 | Parity | Pass | The weakest claim is portability, and the ADR now defends it correctly by limiting 0.21.0 to doctrine/documentation portability rather than overstating runtime parity. |

**RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO**
**RED-TEAM RESULT: 0 failures -> GO**

## Overall Verdict

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

## Action Items

1. No blocking structural actions.
2. Optional improvement: quantify the current repository baseline from the
   tidy-first audit to strengthen Problem Clarity from solid to exemplary.
3. Optional improvement: add one or two local command-surface exemplars to the
   ADR rationale to strengthen Architectural Alignment.
