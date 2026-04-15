---
id: OBPI-0.35.0-06-xenon-complexity
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-06: xenon-complexity

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-06 — "Evaluate xenon-complexity — complexity ceilings (compare with gzkit)"`

## OBJECTIVE

Compare opsdev's `xenon-complexity` pre-commit hook against gzkit's existing complexity enforcement. Both repos enforce cyclomatic complexity ceilings. Compare configurations: threshold values (A/B/C ratings), exclude patterns, and error handling. Determine: Confirm (gzkit's version is sufficient) or Absorb (opsdev's configuration is superior).

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `xenon-complexity`
- **gzkit equivalent:** `.pre-commit-config.yaml` entry for `xenon-complexity`

## ASSUMPTIONS

- Both hooks use xenon for cyclomatic complexity measurement
- Differences may exist in threshold values (-a, -b, -c flags)
- opsdev may have tuned thresholds based on operational experience
- Complexity checking is fast enough for pre-commit enforcement

## NON-GOALS

- Changing the complexity metric tool
- Evaluating xenon vs. radon or other complexity tools
- Modifying opsdev's thresholds

## REQUIREMENTS (FAIL-CLOSED)

1. Read both `.pre-commit-config.yaml` entries for `xenon-complexity` completely
1. Document differences: threshold values, exclude patterns, stages
1. Evaluate which configuration is more appropriate for governance tooling
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.35.0-06-01: Read both `.pre-commit-config.yaml` entries for `xenon-complexity` completely
- [x] REQ-0.35.0-06-02: Document differences: threshold values, exclude patterns, stages
- [x] REQ-0.35.0-06-03: Evaluate which configuration is more appropriate for governance tooling
- [x] REQ-0.35.0-06-04: Record decision with rationale: Absorb / Confirm


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
