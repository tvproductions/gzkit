---
id: OBPI-0.35.0-15-interrogate
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 15
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-15: interrogate

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-15 — "Evaluate interrogate — docstring coverage (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `interrogate` pre-commit hook against gzkit's existing docstring coverage enforcement. Both repos use interrogate to measure and enforce docstring coverage. Compare configurations: coverage thresholds, exclude patterns, verbosity, and which module paths are included. Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's configuration is superior).

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `interrogate`
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `interrogate`

## ASSUMPTIONS

- Both hooks use the same underlying tool (interrogate)
- Differences may exist in coverage thresholds (--fail-under percentage)
- opsdev may have different exclude patterns based on its module structure
- Docstring coverage checking is fast enough for pre-commit enforcement

## NON-GOALS

- Changing the docstring coverage threshold policy
- Evaluating interrogate vs. other docstring tools
- Modifying opsdev's configuration

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `.pre-commit-config.yaml` entries for `interrogate` completely
1. Document differences: thresholds, exclude patterns, verbosity, stages
1. Evaluate which configuration is more appropriate for governance tooling
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
