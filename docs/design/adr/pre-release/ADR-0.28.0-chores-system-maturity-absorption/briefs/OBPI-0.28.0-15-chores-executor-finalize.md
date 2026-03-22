---
id: OBPI-0.28.0-15-chores-executor-finalize
parent_adr: ADR-0.28.0-chores-system-maturity-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-15: Chores Executor Finalize

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-15 — "Evaluate and absorb chores_tools/executor_finalize.py (622 lines) — executor finalization and cleanup pipeline"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/executor_finalize.py` (622 lines) and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module is the largest single module in the chores system — providing the finalization and cleanup pipeline that runs after chore execution completes. At 622 lines, it handles result persistence, artifact cleanup, ledger entries, execution receipts, state transitions, and post-execution hooks. gzkit has no equivalent finalization pipeline. This is one of the modules specifically called out in the ADR's critical constraint as likely needing absorption.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/executor_finalize.py` (622 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- This module is explicitly called out in the ADR as likely needing upstream absorption
- At 622 lines, this is the largest module — careful evaluation needed to separate generic finalization from opsdev-specific logic
- Finalization likely depends on models (OBPI-0.28.0-18), logging (OBPI-0.28.0-12), and recommendations (OBPI-0.28.0-14)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Absorbing domain-specific finalization hooks — only generic pipeline infrastructure

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
