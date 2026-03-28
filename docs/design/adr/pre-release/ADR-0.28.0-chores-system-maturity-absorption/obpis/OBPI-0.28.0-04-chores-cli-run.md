---
id: OBPI-0.28.0-04-chores-cli-run
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-04: Chores CLI Run

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-04 — "Evaluate and absorb chores_tools/cli_run.py (247 lines) — run subcommand implementation"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/cli_run.py` (247 lines) against gzkit's run functionality in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides a dedicated run subcommand with rich executor pipeline integration (run/log/summary/recommendations/finalize stages), progress tracking, and error handling. At 247 lines, it represents the largest CLI subcommand — the user-facing orchestrator of the executor pipeline. gzkit's run logic is embedded in the monolith without the pipeline depth.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/cli_run.py` (247 lines)
- **gzkit equivalent:** Run logic in `src/gzkit/commands/chores.py` (embedded)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- The 247-line dedicated module with full executor pipeline integration likely represents functionality gzkit is missing entirely
- This OBPI depends heavily on OBPI-0.28.0-10 through OBPI-0.28.0-15 (executor pipeline modules)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Implementing the executor pipeline itself — that is covered by OBPI-0.28.0-10 through OBPI-0.28.0-15

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
