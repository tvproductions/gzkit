---
id: OBPI-0.35.0-02-ruff-format
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-02: ruff-format

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-02 — "Evaluate ruff-format — code formatting (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `ruff-format` pre-commit hook against gzkit's existing `ruff-format` hook. Both repos have this hook, but they may differ in configuration (arguments, file patterns, exclude patterns, stages). Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's configuration is superior). Document any configuration differences and their implications.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `ruff-format`
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `ruff-format`

## ASSUMPTIONS

- Both hooks use the same underlying tool (ruff format)
- Differences are likely in configuration: args, exclude patterns, file types, stages
- opsdev's configuration may be more battle-tested from higher commit volume
- gzkit's configuration may be more tailored to governance tooling patterns

## NON-GOALS

- Changing ruff itself — this is about hook configuration, not the formatter
- Evaluating ruff format vs. other formatters
- Modifying opsdev's configuration

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `.pre-commit-config.yaml` entries for `ruff-format` completely
1. Document differences: args, exclude patterns, file types, stages, versions
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
