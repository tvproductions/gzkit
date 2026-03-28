---
id: OBPI-0.32.0-11-closeout
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 11
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-11: closeout

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-11 -- "Compare closeout -- opsdev governance lifecycle vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `closeout` command (governance lifecycle implementation) against gzkit's closeout in cli.py. Closeout is a critical governance ceremony that finalizes ADRs, runs gate checks, and triggers attestation. Determine whether opsdev's lifecycle implementation includes steps, validations, or safeguards that gzkit's version lacks.

## SOURCE MATERIAL

- **opsdev:** closeout governance lifecycle implementation
- **gzkit equivalent:** `cli.py` (closeout section)

## ASSUMPTIONS

- Closeout is governance-critical; thoroughness and correctness matter more than brevity
- opsdev may have a more mature lifecycle with additional pre-checks
- gzkit's closeout should run full gate+attest pipeline per governance rules

## NON-GOALS

- Changing the closeout ceremony contract
- Removing any governance safeguards

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: lifecycle steps, gate checks, attestation integration, error handling
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's closeout lifecycle is sufficient

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
