<!-- markdownlint-disable-file MD013 -->

# ADR Evaluation Scorecard

```text
ADR EVALUATION SCORECARD
═══════════════════════════

ADR: ADR-0.0.6-documentation-cross-coverage-enforcement
Evaluator: Claude Opus 4.6
Date: 2026-03-26

─── ADR-Level Scores ───────────────────────────

| # | Dimension              | Weight | Score (1-4) | Weighted |
|---|------------------------|--------|-------------|----------|
| 1 | Problem Clarity        | 15%    | 4           | 0.60     |
| 2 | Decision Justification | 15%    | 4           | 0.60     |
| 3 | Feature Checklist      | 15%    | 3           | 0.45     |
| 4 | OBPI Decomposition     | 15%    | 4           | 0.60     |
| 5 | Lane Assignment        | 10%    | 4           | 0.40     |
| 6 | Scope Discipline       | 10%    | 4           | 0.40     |
| 7 | Evidence Requirements  | 10%    | 3           | 0.30     |
| 8 | Architectural Alignment| 10%    | 4           | 0.40     |

WEIGHTED TOTAL: 3.75/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

─── ADR Dimension Detail ──────────────────────

1. Problem Clarity (4/4): Cites specific incident (4 QC capabilities #29-#32
   merged without coverage on 2026-03-23). Names 5 undocumented commands.
   6-surface gap analysis table with current tooling column. References Gate 5
   Runbook-Code Covenant as the violated obligation.

2. Decision Justification (4/4): 4 decisions with independent rationale. 6
   alternatives rejected with specific reasoning. Cites COMMAND_DOCS at
   common.py:36-75, OBPI-0.0.3-09 AST precedent. Runtime introspection
   acknowledged as viable but AST preferred for CI safety.

3. Feature Checklist (3/4): 3 items at consistent granularity (discover, declare,
   enforce). Each maps to one OBPI. Minor gap: no explicit mention of how
   existing gz cli audit output changes for operators after integration.

4. OBPI Decomposition (4/4): 3 briefs with full template structure. Explicit
   lane rationale per OBPI. Dependency graph documented (01||02 -> 03).
   Allowed/Denied paths prevent cross-OBPI scope leak. Heavy OBPIs include
   Gate 3 and Gate 5 sections.

5. Lane Assignment (4/4): Heavy/Lite assignments are individually justified.
   OBPI-01 Heavy: changes gz cli audit output (operator-visible). OBPI-02
   Lite: config file only. OBPI-03 Heavy: adds new chore to gz chores
   interface. Gate 3/5 obligations acknowledged in Heavy briefs.

6. Scope Discipline (4/4): 4 explicit non-goals (auto-generation, skill docs,
   content quality, replacing gz cli audit). Each fences off an adjacent concern.
   "Extends, does not replace" stated explicitly. Self-contained with no
   unresolved dependencies.

7. Evidence Requirements (3/4): Each OBPI has Verification section with concrete
   commands and 4 REQ-numbered acceptance criteria. Heavy OBPIs include Gate 3
   and Gate 5 gates. Minor weakness: OBPI-01 verification assumes gz cli audit
   is already extended (circular).

8. Architectural Alignment (4/4): Three-layer ASCII architecture diagram.
   References cli_audit.py, common.py:36-75, OBPI-0.0.3-09, gzkit.chores.json.
   Q&A Transcript provides discovery provenance. Consequences section addresses
   positive and negative impacts.

─── OBPI-Level Scores ──────────────────────────

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01   | 4           | 4           | 4     | 3    | 4       | 3.8 |
| 02   | 4           | 4           | 3     | 4    | 4       | 3.8 |
| 03   | 2           | 4           | 3     | 3    | 4       | 3.2 |

OBPI AVERAGE: 3.60/4.0
OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on
any dimension must be revised.

All OBPIs above threshold. No dimension scores 1.

OBPI-03 scores 2 on Independence (depends on both 01 and 02) which is
expected for an integration OBPI and correctly documented.

─── Red-Team Challenges ────────────────────────

Not requested for this evaluation.

| # | Challenge      | Result | Notes                                    |
|---|----------------|--------|------------------------------------------|
| 1 | So What?       | --     | Not evaluated                            |
| 2 | Scope          | --     | Not evaluated                            |
| 3 | Alternative    | --     | Not evaluated                            |
| 4 | Dependency     | --     | Not evaluated                            |
| 5 | Gold Standard  | --     | Not evaluated                            |
| 6 | Timeline       | --     | Not evaluated                            |
| 7 | Evidence       | --     | Not evaluated                            |
| 8 | Consumer       | --     | Not evaluated                            |
| 9 | Regression     | --     | Not evaluated                            |
| 10| Parity         | --     | Not evaluated                            |

─── Overall Verdict ────────────────────────────

[X] GO - Ready for proposal/defense review

ADR-0.0.6 is a well-grounded Heavy-lane ADR with incident-driven problem
framing, evidence-backed decisions, explicit lane rationale per OBPI, and a
clean three-layer architecture that extends existing tooling rather than
replacing it.

ACTION ITEMS:
1. Clarify how gz cli audit output changes for operators after OBPI-01
   integration -- the checklist mentions extending it but doesn't describe
   the new output format.
2. OBPI-01 verification section references the extended gz cli audit which
   is the deliverable itself -- add an independent verification command
   (e.g., direct scanner module invocation).
3. Consider whether OBPI-03's --json flag warrants a schema in data/schemas/
   for consumer stability.
```
