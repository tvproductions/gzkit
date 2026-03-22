---
id: OBPI-0.32.0-09-gates
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-09: gates

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-09 -- "Compare gates -- opsdev gates_tools.py 55 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `gates` command (gates_tools.py, 55 lines) against gzkit's gates implementation in cli.py. The gates command runs quality gates (lint, test, typecheck, docs) for an ADR. Determine whether opsdev's implementation offers additional gate types, better failure reporting, or gate-level parallelism that gzkit lacks.

## SOURCE MATERIAL

- **opsdev:** `gates_tools.py` (55 lines)
- **gzkit equivalent:** `cli.py` (gates section)

## ASSUMPTIONS

- Both implementations orchestrate the same underlying quality checks
- 55 lines is relatively small; implementations may be comparable
- Gate failure reporting and exit code handling are critical

## NON-GOALS

- Adding new gate types without justification
- Changing gate execution order

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: gate types, execution order, failure reporting, exit codes
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation is sufficient

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed improvements
- `tests/` -- tests for absorbed improvements
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
