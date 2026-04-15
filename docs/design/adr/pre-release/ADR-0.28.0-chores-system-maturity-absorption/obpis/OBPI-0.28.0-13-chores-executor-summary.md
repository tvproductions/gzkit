---
id: OBPI-0.28.0-13-chores-executor-summary
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 13
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-13: Chores Executor Summary

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-13 — "Evaluate and absorb chores_tools/executor_summary.py (161 lines) — executor summary generation"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/executor_summary.py` (161 lines) against gzkit's summary output in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides structured summary generation after chore execution — aggregating results across chores, computing pass/fail rates, identifying trends, and producing both human-readable and machine-readable (`--json`) summaries. gzkit's summary output is basic console printing without aggregation or trend analysis.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/executor_summary.py` (161 lines)
- **gzkit equivalent:** Basic summary output in `src/gzkit/commands/chores.py` (inline)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Structured summaries enable both operator visibility and machine-readable output per CLI doctrine

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a general-purpose reporting engine — this is chore execution summaries

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.28.0-13-01: Read both implementations completely
- [x] REQ-0.28.0-13-02: Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
- [x] REQ-0.28.0-13-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.28.0-13-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.28.0-13-05: If Confirm: document why gzkit's implementation is sufficient
- [x] REQ-0.28.0-13-06: If Exclude: document why the module is domain-specific


## ALLOWED PATHS

- `src/gzkit/chores_tools/` — target for absorbed modules
- `src/gzkit/commands/chores.py` — existing monolith (may be refactored)
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
