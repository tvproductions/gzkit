---
id: OBPI-0.35.0-03-ty-check
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-03: ty-check

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-03 — "Evaluate ty-check — type checking (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `ty-check` pre-commit hook against gzkit's existing `ty-check` hook. Both repos have this hook for static type checking. Compare configurations: exclude patterns, arguments, error thresholds, and stages. Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's configuration is superior).

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `ty-check`
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `ty-check`

## ASSUMPTIONS

- Both hooks use the same underlying tool (ty check)
- Differences are likely in exclude patterns (opsdev excludes `features/**`, gzkit may differ)
- Type checking at commit time is fast enough for pre-commit enforcement
- Both repos may have different type error baselines

## NON-GOALS

- Changing the ty type checker itself
- Evaluating ty vs. mypy or other type checkers
- Modifying opsdev's configuration

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `.pre-commit-config.yaml` entries for `ty-check` completely
1. Document differences: args, exclude patterns, stages, error handling
1. Evaluate which configuration is more robust/complete
1. Record decision with rationale: Absorb / Confirm

## ALLOWED PATHS

- `.pre-commit-config.yaml` — hook configuration
- `tests/` — tests for hook configuration
- `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
