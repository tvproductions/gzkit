---
id: OBPI-0.30.0-04-config-git-sync-json
parent: ADR-0.30.0-config-schema-settings-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-04: Config Git Sync JSON

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-04 --- "Evaluate and absorb config/opsdev/git_sync.json --- git-sync configuration schema and data"`

## OBJECTIVE

Evaluate opsdev's `config/opsdev/git_sync.json` against gzkit's git-sync configuration to determine: Absorb (the schema pattern is governance-generic), Confirm (gzkit's git-sync config is sufficient), or Exclude (project-specific git-sync definitions). The evaluation must separate the schema pattern (how git-sync is configured) from the data content (which paths and repos are synced) --- the pattern may be generic even if the data is project-specific.

## SOURCE MATERIAL

- **opsdev:** `config/opsdev/git_sync.json`
- **gzkit equivalent:** Current git-sync configuration in gzkit's config layer

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- The schema pattern (structure, path mapping, sync rules) is likely governance-generic
- The specific sync targets and paths are likely project-specific
- gzkit should own the schema pattern; projects should own their sync definitions

## NON-GOALS

- Absorbing project-specific sync paths as gzkit defaults
- Changing the git-sync model without Heavy lane approval
- Duplicating sync configuration across gzkit and opsdev

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev git_sync.json completely
1. Separate schema pattern from data content
1. Document comparison: schema structure, path mapping rules, sync semantics
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: extract the generic schema pattern and write tests
1. If Exclude: document why gzkit's current git-sync config is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.30.0-04-01: Read the opsdev git_sync.json completely
- [x] REQ-0.30.0-04-02: Separate schema pattern from data content
- [x] REQ-0.30.0-04-03: Document comparison: schema structure, path mapping rules, sync semantics
- [x] REQ-0.30.0-04-04: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.30.0-04-05: If Absorb: extract the generic schema pattern and write tests
- [x] REQ-0.30.0-04-06: If Exclude: document why gzkit's current git-sync config is sufficient


## ALLOWED PATHS

- `src/gzkit/` --- target for absorbed modules
- `tests/` --- tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/` --- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
