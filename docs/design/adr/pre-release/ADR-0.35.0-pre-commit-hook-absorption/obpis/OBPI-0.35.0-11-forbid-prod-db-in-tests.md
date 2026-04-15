---
id: OBPI-0.35.0-11-forbid-prod-db-in-tests
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 11
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-11: forbid-prod-db-in-tests

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-11 — "Evaluate forbid-prod-db-in-tests — production DB guard in tests (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `forbid-prod-db-in-tests` pre-commit hook — prevents test files from referencing production database paths or connection strings. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce DB isolation at commit time), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit's test policy (which already mandates tempfile temp DBs) needs enforcement tooling beyond documentation.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `forbid-prod-db-in-tests`, implementation script
- **gzkit equivalent:** None (test policy documents the requirement but no enforcement hook)

## ASSUMPTIONS

- gzkit's test policy already mandates: "Unit tests MUST use tempfile temp DBs; NEVER use live/production databases"
- The hook enforces this policy at commit time by scanning test files for forbidden patterns
- Detection patterns may include hardcoded DB paths, connection strings, production hostnames
- The concept is governance-generic even though opsdev's patterns may be airline-specific

## NON-GOALS

- Changing the DB isolation policy
- Implementing database mocking or test fixtures
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `forbid-prod-db-in-tests` hook implementation completely
1. Document: what patterns it detects, which files it scans, how it reports violations
1. Evaluate whether the detection patterns are generic or airline-specific
1. Determine enforcement timing: pre-commit, Claude hook, or both
1. Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.35.0-11-01: Read the opsdev `forbid-prod-db-in-tests` hook implementation completely
- [x] REQ-0.35.0-11-02: Document: what patterns it detects, which files it scans, how it reports violations
- [x] REQ-0.35.0-11-03: Evaluate whether the detection patterns are generic or airline-specific
- [x] REQ-0.35.0-11-04: Determine enforcement timing: pre-commit, Claude hook, or both
- [x] REQ-0.35.0-11-05: Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude


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
