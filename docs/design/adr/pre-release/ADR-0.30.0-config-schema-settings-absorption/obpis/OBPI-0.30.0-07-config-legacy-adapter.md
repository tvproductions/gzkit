---
id: OBPI-0.30.0-07-config-legacy-adapter
parent: ADR-0.30.0-config-schema-settings-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-07: Config Legacy Adapter

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-07 --- "Evaluate and absorb legacy adapter bridges --- backward-compatible config migration"`

## OBJECTIVE

Evaluate opsdev's legacy adapter bridges against gzkit's config migration strategy to determine: Absorb (opsdev has reusable migration patterns), Confirm (gzkit does not need legacy adapters), or Exclude (project-specific migration logic). The evaluation must assess how opsdev handles backward-compatible configuration transitions --- a governance-generic concern when config schemas evolve.

## SOURCE MATERIAL

- **opsdev:** Legacy adapter bridges in config infrastructure
- **gzkit equivalent:** Current config migration handling (if any)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Config schema evolution and backward compatibility are governance-generic concerns
- If opsdev's adapters bridge specific historical config formats, they may be project-specific
- If opsdev's adapters provide a generic migration pattern (version detection, schema upgrade, deprecation warnings), the pattern is reusable

## NON-GOALS

- Absorbing project-specific config format migrations
- Supporting unlimited historical config versions
- Changing gzkit's config format without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev legacy adapter implementation completely
1. Separate the migration pattern from project-specific format transitions
1. Document comparison: migration strategy, version detection, deprecation handling
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: extract the generic migration pattern and write tests
1. If Exclude: document why gzkit does not need legacy adapters

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.30.0-07-01: Read the opsdev legacy adapter implementation completely
- [x] REQ-0.30.0-07-02: Separate the migration pattern from project-specific format transitions
- [x] REQ-0.30.0-07-03: Document comparison: migration strategy, version detection, deprecation handling
- [x] REQ-0.30.0-07-04: Record decision with rationale: Absorb / Adapt / Exclude
- [x] REQ-0.30.0-07-05: If Absorb: extract the generic migration pattern and write tests
- [x] REQ-0.30.0-07-06: If Exclude: document why gzkit does not need legacy adapters


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
