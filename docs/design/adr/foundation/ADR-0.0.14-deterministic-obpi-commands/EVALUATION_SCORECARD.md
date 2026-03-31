<!-- markdownlint-disable-file MD013 MD036 MD041 -->

ADR EVALUATION SCORECARD
========================

**ADR:** ADR-0.0.14 — Deterministic OBPI Commands
**Evaluator:** Claude Opus 4.6 (gz-adr-eval)
**Date:** 2026-03-31

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Before/after concrete: skills write lock files + JSONL directly vs all writes through CLI. "So what" is governance-core violation + untestable/unauditable state transitions. |
| 2 | Decision Justification | 15% | 3 | 0.45 | Four decisions well-justified. Standalone `attest` was considered and rejected with clear rationale (invalid state elimination). Could be stronger on counterarguments for folding attest into complete. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | All 8 items necessary and independently testable. Minor gap: no `--dry-run` consideration for either command (CLI doctrine recommends it). Not a structural defect. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | Clean 3-OBPI split. OBPI-01 and OBPI-02 parallelizable; OBPI-03 sequential with declared dependency. Domain-driven boundaries (lock primitive, completion transaction, skill migration). |
| 5 | Lane Assignment | 10% | 4 | 0.40 | All three correctly Heavy: OBPI-01/02 introduce new CLI subcommands, OBPI-03 changes observable skill behavior. Gate obligations acknowledged per brief. |
| 6 | Scope Discipline | 10% | 2 | 0.20 | Scope is functionally clear but non-goals are NOT explicitly enumerated. Implied non-goals (no config-driven TTL, no standalone attest, no pipeline restructuring) should be stated. |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | Every OBPI has concrete verification commands. Lock: claim/check/list/release sequence. Complete: happy path + rollback on failure. Migration: grep for zero direct writes. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | Names 7 integration points with exact paths. References existing subcommand registration pattern. Anti-pattern ("dual-path writes") clearly defined. Django parallel is apt. |

**WEIGHTED TOTAL: 3.40/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 (lock) | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 (complete) | 4 | 4 | 4 | 3 | 3 | 3.6 |
| 03 (migration) | 3 | 3 | 4 | 3 | 4 | 3.4 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. No dimension scores 1. PASS.**

**OBPI Notes:**

- **OBPI-01 Size (3):** Four subcommands + lock_manager.py + tests + BDD may push to 3-4 days.
- **OBPI-02 Clarity (3):** Rollback mechanism specified as "all-or-nothing" but HOW
  (temp files + rename? read/restore on failure?) is left to implementation planning.
  The requirement is clear; the strategy is open. Acceptable for a brief.
- **OBPI-03 Testability (3):** Verification is grep-based (zero direct writes) + docs build.
  No unit tests since it's skill prose, but the grep check is deterministic.

--- Overall Verdict ---

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

**ACTION ITEMS (non-blocking, recommended for implementation planning):**

1. **Add non-goals section** to ADR: explicitly state no config-driven TTL, no standalone
   `gz obpi attest`, no pipeline stage restructuring, no lock-to-pipeline coupling.
   (Addresses Scope Discipline score of 2.)
2. **Consider `--dry-run`** for `gz obpi complete` during OBPI-02 planning — the CLI
   doctrine recommends it and an atomic 6-step transaction is a strong candidate.
3. **Clarify rollback strategy** during OBPI-02 implementation planning — temp-file-then-rename
   is the recommended pattern for atomic file+ledger writes.
