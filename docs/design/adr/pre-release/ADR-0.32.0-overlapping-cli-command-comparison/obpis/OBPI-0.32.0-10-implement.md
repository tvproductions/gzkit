---
id: OBPI-0.32.0-10-implement
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-10: implement

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-10 -- "Compare implement -- opsdev dev_tools.py 40 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `implement` command (dev_tools.py, 40 lines) against gzkit's implement command in cli.py. The implement command marks an ADR/OBPI as in-progress and sets up the development context. At 40 lines both implementations are likely small; determine whether they handle the same workflow steps.

## SOURCE MATERIAL

- **opsdev:** `dev_tools.py` (40 lines)
- **gzkit equivalent:** `cli.py` (implement section)

## ASSUMPTIONS

- Both are lightweight workflow commands
- 40 lines suggests minimal orchestration
- The comparison may reveal equivalent implementations

## NON-GOALS

- Expanding implement command scope
- Changing the development workflow

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: workflow steps, state transitions, validation checks
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
