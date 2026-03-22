---
id: OBPI-0.35.0-04-unittest
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-04: unittest

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-04 — "Evaluate unittest — smoke tests (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `unittest` pre-commit hook against gzkit's existing `unittest` hook. Both repos run unittest smoke tests at commit time. Compare configurations: test discovery patterns, timeout settings, verbosity flags, and which test subsets are selected for the smoke run. Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's configuration is superior).

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `unittest`
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `unittest`

## ASSUMPTIONS

- Both hooks use stdlib unittest as the test runner
- Smoke tests at commit time must be fast (<=60s per test policy)
- Differences may exist in test discovery, selection, or timeout configuration
- opsdev may run a different subset of tests than gzkit

## NON-GOALS

- Changing the test framework or test runner
- Evaluating unittest vs. pytest (pytest is forbidden by policy)
- Modifying test content — this is about the hook configuration

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `.pre-commit-config.yaml` entries for `unittest` completely
1. Document differences: discovery patterns, args, timeout, stages
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
