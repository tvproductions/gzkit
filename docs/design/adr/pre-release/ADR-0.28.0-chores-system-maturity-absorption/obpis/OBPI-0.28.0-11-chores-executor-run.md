---
id: OBPI-0.28.0-11-chores-executor-run
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 11
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-11: Chores Executor Run

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-11 — "Evaluate and absorb chores_tools/executor_run.py (339 lines) — executor run stage with chore execution logic"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/executor_run.py` (339 lines) against gzkit's execution logic in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides the core execution stage of the executor pipeline — subprocess management, timeout handling, output capture, error classification, and execution result modeling. At 339 lines, this is the second largest module and the heart of actual chore execution. gzkit's execution logic is embedded in the monolith without the same depth of error handling and result modeling.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/executor_run.py` (339 lines)
- **gzkit equivalent:** Execution logic in `src/gzkit/commands/chores.py` (embedded)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 339 lines with subprocess management and error classification, this likely represents significant depth gzkit is missing
- Must use list-form subprocess calls per cross-platform policy

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Implementing the executor dispatch — that is covered by OBPI-0.28.0-10

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

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
