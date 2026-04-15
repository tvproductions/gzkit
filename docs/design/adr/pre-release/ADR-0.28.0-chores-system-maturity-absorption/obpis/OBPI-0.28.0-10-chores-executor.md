---
id: OBPI-0.28.0-10-chores-executor
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-10: Chores Executor

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-10 — "Evaluate and absorb chores_tools/executor.py (40 lines) — executor entry point and dispatch"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/executor.py` (40 lines) against gzkit's executor logic in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides a thin executor entry point that dispatches to the decomposed pipeline stages (run, log, summary, recommendations, finalize). gzkit has executor logic embedded in the monolith without pipeline decomposition. This is the orchestrator that ties together OBPI-0.28.0-11 through OBPI-0.28.0-15.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/executor.py` (40 lines)
- **gzkit equivalent:** Executor logic in `src/gzkit/commands/chores.py` (embedded, not decomposed)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 40 lines, this is a thin dispatch layer — its value comes from enabling the decomposed pipeline
- This module is the linchpin that connects the 5 executor stage modules

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Implementing individual executor stages — those are covered by OBPI-0.28.0-11 through OBPI-0.28.0-15

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

- [x] REQ-0.28.0-10-01: Read both implementations completely
- [x] REQ-0.28.0-10-02: Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
- [x] REQ-0.28.0-10-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.28.0-10-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.28.0-10-05: If Confirm: document why gzkit's implementation is sufficient
- [x] REQ-0.28.0-10-06: If Exclude: document why the module is domain-specific


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
