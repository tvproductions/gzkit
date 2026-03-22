---
id: OBPI-0.35.0-16-check-todos-fixmes
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-16: check-todos-fixmes

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-16 — "Evaluate check-todos-fixmes — TODO/FIXME tracking (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `check-todos-fixmes` pre-commit hook against gzkit's existing TODO/FIXME tracking enforcement. Both repos track TODO and FIXME comments. Compare configurations: detection patterns, file types scanned, severity levels, and whether the hook blocks commits or just reports. Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's detection is more comprehensive).

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `check-todos-fixmes`, implementation script
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `check-todos-fixmes`

## ASSUMPTIONS

- Both hooks detect TODO and FIXME comments in source code
- Differences may exist in: patterns detected (TODO, FIXME, HACK, XXX), file types, reporting
- The hook may warn or block depending on configuration
- Both repos have a governance requirement to track technical debt markers

## NON-GOALS

- Changing the TODO/FIXME tracking policy
- Automatically resolving TODOs
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `check-todos-fixmes` hook implementations completely
1. Document differences: detection patterns, file types, severity, blocking behavior
1. Evaluate which detection is more comprehensive
1. Record decision with rationale: Absorb / Confirm

## ALLOWED PATHS

- `.pre-commit-config.yaml` — hook configuration
- `src/gzkit/hooks/` — hook implementations
- `tests/` — tests for hook configuration
- `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
