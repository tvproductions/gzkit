---
id: OBPI-0.28.0-14-chores-executor-recommendations
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 14
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-14: Chores Executor Recommendations

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-14 — "Evaluate and absorb chores_tools/executor_recommendations.py (254 lines) — executor recommendations engine"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/executor_recommendations.py` (254 lines) and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides a recommendations engine that analyzes chore execution results and generates actionable suggestions — identifying recurring failures, recommending configuration changes, flagging chores that should be promoted or retired, and suggesting execution order optimizations. gzkit has no equivalent capability. This is one of the modules specifically called out in the ADR's critical constraint as likely needing absorption.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/executor_recommendations.py` (254 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- This module is explicitly called out in the ADR as likely needing upstream absorption
- The recommendations engine depends on structured execution logs (OBPI-0.28.0-12) and summary data (OBPI-0.28.0-13)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a general-purpose recommendation system — this is chore-execution-specific recommendations

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
