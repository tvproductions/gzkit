---
id: OBPI-0.35.0-08-forbid-pytest
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-08: forbid-pytest

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-08 — "Evaluate forbid-pytest — pytest prohibition enforcement (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `forbid-pytest` pre-commit hook against gzkit's existing pytest prohibition enforcement. Both repos prohibit pytest in favor of stdlib unittest. Compare: detection patterns (import statements, conftest.py, pytest.ini), error messages, and file patterns scanned. Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's detection is more comprehensive).

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `forbid-pytest`, implementation script
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `forbid-pytest`

## ASSUMPTIONS

- Both hooks enforce the same policy: no pytest, use stdlib unittest
- Differences may exist in detection patterns (opsdev may catch more pytest artifacts)
- Both should detect: `import pytest`, `conftest.py`, `pytest.ini`, `@pytest.fixture`
- Pre-commit timing is ideal — catch pytest introduction before it's committed

## NON-GOALS

- Debating pytest vs. unittest — the policy is decided
- Modifying opsdev's implementation
- Changing the prohibition policy

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `forbid-pytest` hook implementations completely
1. Document differences: detection patterns, file globs, error messages
1. Evaluate which detection is more comprehensive
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.35.0-08-01: Read both `forbid-pytest` hook implementations completely
- [x] REQ-0.35.0-08-02: Document differences: detection patterns, file globs, error messages
- [x] REQ-0.35.0-08-03: Evaluate which detection is more comprehensive
- [x] REQ-0.35.0-08-04: Record decision with rationale: Absorb / Confirm


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
