---
id: OBPI-0.35.0-20-adr-drift-check
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 20
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-20: adr-drift-check

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-20 — "Evaluate adr-drift-check — ADR drift detection (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `adr-drift-check` pre-commit hook — detects when ADR implementation state drifts from declared status (e.g., code changes that should update an ADR's status from Proposed to Implementing). gzkit does not currently have this hook. Determine: Absorb-PreCommit (detect drift on every commit), Absorb-Claude (detect during agent sessions), Absorb-Both, or Exclude. The key question is whether ADR drift detection at commit time prevents governance staleness.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `adr-drift-check`, implementation script
- **gzkit equivalent:** None (gzkit has `gz adr audit-check` but not as a pre-commit hook)

## ASSUMPTIONS

- ADR status drift is a real governance risk — code changes without ADR status updates
- The hook likely detects: code changes in ADR-scoped paths without corresponding ADR updates
- gzkit's `gz adr audit-check` performs similar analysis but requires manual invocation
- Pre-commit enforcement would catch drift before it accumulates

## NON-GOALS

- Auto-updating ADR status (the hook detects, not resolves)
- Changing the ADR lifecycle definitions
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `adr-drift-check` hook implementation completely
1. Document: how it detects drift, what ADR fields it checks, what triggers violations
1. Evaluate whether gzkit needs commit-time ADR drift detection
1. Determine enforcement timing: pre-commit, Claude hook, or both
1. Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.35.0-20-01: Read the opsdev `adr-drift-check` hook implementation completely
- [x] REQ-0.35.0-20-02: Document: how it detects drift, what ADR fields it checks, what triggers violations
- [x] REQ-0.35.0-20-03: Evaluate whether gzkit needs commit-time ADR drift detection
- [x] REQ-0.35.0-20-04: Determine enforcement timing: pre-commit, Claude hook, or both
- [x] REQ-0.35.0-20-05: Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude


## ALLOWED PATHS

- `.pre-commit-config.yaml` — hook configuration
- `src/gzkit/hooks/` — hook implementations
- `.claude/hooks/` — Claude hook configurations
- `tests/` — tests for absorbed hooks
- `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
