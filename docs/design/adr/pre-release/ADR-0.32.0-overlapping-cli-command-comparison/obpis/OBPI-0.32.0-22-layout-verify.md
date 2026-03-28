---
id: OBPI-0.32.0-22-layout-verify
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 22
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-22: layout-verify

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-22 -- "Compare layout-verify -- opsdev layout_tools.py 44 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `layout-verify` command (layout_tools.py, 44 lines) against gzkit's equivalent in cli.py. The layout-verify command validates that the repository directory structure matches the expected layout. Determine whether opsdev's 44-line implementation checks layout aspects that gzkit misses.

## SOURCE MATERIAL

- **opsdev:** `layout_tools.py` (44 lines)
- **gzkit equivalent:** `cli.py` (layout-verify section)

## ASSUMPTIONS

- Both validate repository directory structure against a manifest or convention
- 44 lines is small; implementations are likely comparable
- Layout validation is a governance safeguard

## NON-GOALS

- Changing layout conventions
- Adding new required directories without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: directories checked, validation rules, error reporting
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
