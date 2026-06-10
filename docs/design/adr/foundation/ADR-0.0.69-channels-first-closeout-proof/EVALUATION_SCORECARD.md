<!-- markdownlint-disable-file MD013 MD022 MD036 MD041 -->

# ADR EVALUATION SCORECARD

**ADR:** ADR-0.0.69-channels-first-closeout-proof
**Evaluator:** Manual — narrator persona dispatch; spec-reviewer (agent ac342ad152d1184e2), quality-reviewer (agent ac7a89b6d71815b59)
**Date:** 2026-06-09
**Red-team:** NOT RUN

---

## CLI Pre-Screen (superseded by this document)

**Evaluator:** gz adr eval (deterministic) · **Date:** 2026-06-10 · **Verdict:** GO, 3.90/4.0

| # | Dimension | Weight | CLI Score | CLI Weighted | CLI Finding |
|---|-----------|--------|-----------|--------------|-------------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No source file path references in ADR |

**CLI misfires identified by manual review:**

- **D3 false positive:** CLI verified 4-item↔4-brief mapping but did not check Decision-deliverable coverage. Gap: Decision item 5's first clause ("untagged REQ → unproven" gate behavior) has no covering REQ in any brief.
- **D4 false positive (internal inconsistency):** CLI scored D4=4 while itself flagging OBPI-03 Size=2. A decomposition containing a 4–5 day unit cannot be Exemplary.
- **D7 false positive:** CLI accepted final-state commands as sufficient. OBPI-03 REQ #7's ordering constraint (pre-audit before gate repoint) has no mechanical proof path — process-only enforcement.
- **D8 false negative:** CLI's source-path check requires `src/gzkit/`-prefixed references. ADR uses standard short module references with line numbers; all verified accurate against live codebase by quality-reviewer. Short references are the correct style for ADR Decision prose; full paths live in brief Allowed Paths.

---

## Manual ADR-Level Scores

| # | Dimension | Weight | Score (1–4) | Weighted | Reconciliation vs. CLI |
|---|-----------|--------|-------------|----------|------------------------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Agrees. Before-state named at `req_kind.py:182/218` (hardcoded "advisory-support") and FENCE "grandfathered" at :220; 19 ln-carrying briefs counted; GHI #543/#538 anchored; after-state testable via exit codes 0/3/2. |
| 2 | Decision Justification | 15% | 4 | 0.60 | Agrees. Three alternatives dismissed with concrete architectural reasons (Option B drift surface; Option C leaves FENCE advisory = #538 itself; auto-populate = Layer-3-as-source-of-truth, Architectural Boundary 6); named local precedent (`--adr-status-fresh`/`--session-green-gate` in `run_*_audit` + `_build_check_steps()`); operator rulings 6.1-A/6.2-A present verbatim. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | CLI MISFIRE (false positive). Decision item 5's first clause — `--closeout-proof` reports an untagged REQ as unproven — is gate behavior with no covering REQ. REQ-0.0.69-03-02 covers only the re-run-command clause; REQ-0.0.69-03-05 covers only the one-time 0.0.41 backfill. |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | CLI MISFIRE (inconsistency). CLI scored 4 while itself flagging OBPI-03 Size=2. OBPI-03 spans ~9 integration surfaces (4–5 day unit); OBPI-01/02 share `req_kind.py` (coordination risk, partitioned via Allowed/Denied paths); dependency chain fully serial 01+02→03→04 (sound — surface boundaries require it). |
| 5 | Lane Assignment | 10% | 4 | 0.40 | Agrees. All four OBPIs Heavy; each independently justified by runtime-contract changes; CLI flag + schema property removals verified at `parser_maintenance.py:600–604` and `obpi_brief_structure.json:61–85`. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Agrees. Three explicit non-goals with rationale; Boundary Invariant 3 fences ADR-0.0.68 surfaces; per-brief Denied Paths name sibling scopes; five pre-mortem failure scenarios present. |
| 7 | Evidence Requirements | 10% | 3 | 0.30 | CLI MISFIRE (false positive). OBPI-03 REQ #7's ordering constraint (19-brief read-only pre-audit BEFORE gate repoint) is process-enforced only. REQ-0.0.69-03-05 requires a ledger event but not one timestamped before the repoint commit; no mechanical proof path exists. |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | CLI MISFIRE (false negative). ADR uses standard short module references with line numbers throughout Decision — all verified accurate against live codebase by quality-reviewer. Full paths live in brief Allowed Paths (correct split). Zero-rewiring claim for ADR-0.0.68 verified sound: session-green gate asserts `gz check` delegation, not a frozen scope list. |

**WEIGHTED TOTAL: 3.60/4.0**

Calculation: (4+4+3+3)×0.15 + (4+4+3+4)×0.10 = 2.10 + 1.50 = 3.60

**THRESHOLD: 3.0 (GO) · 2.5 (CONDITIONAL GO) · <2.5 (NO GO)**

---

## OBPI-Level Scores

| OBPI | Short Name | Ind. | Test. | Value | Size | Clarity | Avg |
|------|------------|------|-------|-------|------|---------|-----|
| 01 | support-channel-ledger-and-validator-dispatch | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 02 | structural-fence-channel-boundary-invariants-anchor | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 03 | closeout-proof-derived-view | 3 | 3 | 4 | 2 | 3 | 3.0 |
| 04 | retire-ln-closeout-proof-binding-surface | 3 | 4 | 3 | 2 | 4 | 3.2 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 requires revision.**

All four OBPIs meet the average threshold. No dimension scores 1 anywhere.

**Per-OBPI annotations:**

- **OBPI-02 Independence=3:** shares `req_kind.py` with OBPI-01; risk managed by Allowed/Denied path partitioning in each brief.
- **OBPI-03 Size=2:** ~9 integration surfaces estimated; budget 4–5 days. See Action Item 2.
- **OBPI-03 Testability=3:** pre-audit ordering constraint (read-only 19-brief audit before gate repoint commit) is process-enforced only. See Action Item 3.
- **OBPI-03 Clarity=3:** untagged REQ IDs across the 19 existing briefs are not enumerated in the brief; implementing agent cannot count expected backfill volume without running the pre-audit.
- **OBPI-04 Independence=3:** depends on OBPI-03 gate repoint completing before ln-surface retirement begins.
- **OBPI-04 Size=2:** broad mechanical deletion across code, 19 briefs, and docs; scope is wide even if each change is low-complexity.
- **OBPI-04 Value=3:** ln-surface retirement is necessary cleanup but delivers no new user-visible capability; removing it weakens completeness rather than leaving a visible gap.

---

## Red-Team Challenges

Protocol was **NOT invoked** for this evaluation (no `--red-team` flag passed to the pipeline).

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | N/R | — |
| 2 | Scope | N/R | — |
| 3 | Alternative | N/R | — |
| 4 | Dependency | N/R | — |
| 5 | Gold Standard | N/R | — |
| 6 | Timeline | N/R | — |
| 7 | Evidence | N/R | — |
| 8 | Consumer | N/R | — |
| 9 | Regression | N/R | — |
| 10 | Parity | N/R | — |

---

## Persona Dispatch Attestation

| Agent | Role | Dimensions | Status | Notes |
|-------|------|------------|--------|-------|
| ac342ad152d1184e2 | spec-reviewer | D1, D3, D4, D7; all OBPI rubrics | PASS | Verified all 20 REQs carry exactly one [kind] tag; FENCE REQs map to named Boundary Invariant entries (Inv 1 ↔ REQ-0.0.69-02-04, Inv 2 ↔ REQ-0.0.69-03-06); both operator rulings 6.1-A/6.2-A present verbatim in OBPI-03; 1:1 checklist↔brief sync confirmed. |
| ac7a89b6d71815b59 | quality-reviewer | D2, D5, D6, D8 | COHERENT | Independently verified every cited line number, function, and module against live codebase. Cosmetic note: "advisory-support" citation points at docstring line 182; assignment is line 218 — both verified present and consistent; no accuracy defect. |

---

## Overall Verdict

**[x] GO — Ready for operator proposal/defense review**

[ ] CONDITIONAL GO

[ ] NO GO

Weighted total 3.60/4.0 meets the 3.0 GO threshold. No dimension scores 1. All OBPI averages >= 3.0. CLI pre-screen verdict (GO, 3.90/4.0) is superseded by this manual evaluation (GO, 3.60/4.0). Three CLI false positives (D3, D4, D7) and one CLI false negative (D8) identified and reconciled above. Action items below are non-blocking; none prevents implementation from beginning.

---

## Action Items (non-blocking — address before implementation begins)

1. **Add a covering REQ to OBPI-03 for ruling 6.2-A's first clause.** `--closeout-proof` reporting a REQ with no inline [kind] tag as unproven is gate behavior currently untracked by any REQ. REQ-0.0.69-03-02 covers the re-run-command clause only; REQ-0.0.69-03-05 covers the 0.0.41 one-time backfill only. The gate behavior itself needs its own REQ. **ADDRESSED 2026-06-09:** REQ-0.0.69-03-07 [behavior] added to OBPI-03 in the same session, with a matching Requirements clause.
2. **OBPI-03 sizing — budget 4–5 days or pre-split the seam-fix/manpage tail.** The pre-audit may surface a larger-than-expected volume of untagged REQs across the 19 existing briefs. Implementing agent should signal early if the scope exceeds the budget; a seam split at the pre-audit/repoint boundary is the natural fallback.
3. **Pre-audit sequencing is process-enforced only.** The 19-brief read-only pre-audit must precede the gate repoint commit. No mechanical enforcement exists. Implementing agent records pre-audit ledger evidence before the repoint commit; reviewer checks event timestamps at closeout attestation.
4. **Boundary Invariant 3 (ADR-0.0.68 surfaces untouched) is verified by closeout inspection only.** `--closeout-proof` does not enforce this mechanically — deliberate, per non-goals. Named here so attestation covers it consciously rather than by assumption.

---

*Manual evaluation date: 2026-06-09. This scorecard supersedes the CLI pre-screen (gz adr eval, dated 2026-06-10, 3.90/4.0). Narrator persona dispatch complete; no further evaluation stages pending prior to operator proposal/defense review.*
