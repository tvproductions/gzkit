---
id: OBPI-0.30.0-08-config-settings-validation
parent: ADR-0.30.0-config-schema-settings-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-08: Config Settings Validation

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-08 --- "Evaluate and absorb settings validation and env loading --- environment variable integration and validation"`

## OBJECTIVE

Evaluate opsdev's settings validation and environment variable loading against gzkit's configuration validation to determine: Absorb (opsdev has superior validation and env integration), Confirm (gzkit's validation is sufficient), or Exclude (project-specific validation logic). The evaluation must assess how opsdev validates settings at load time, integrates environment variables, and reports validation errors --- capabilities that ensure config correctness before any command executes.

## SOURCE MATERIAL

- **opsdev:** Settings validation and env loading patterns in config infrastructure
- **gzkit equivalent:** Current validation in `src/gzkit/config.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Settings validation at load time is governance-generic (fail-fast on bad config)
- Environment variable integration (12-factor app style) is governance-generic
- If opsdev validates project-specific settings, those rules are project-specific; the validation framework is generic

## NON-GOALS

- Absorbing project-specific validation rules as gzkit defaults
- Implementing full 12-factor app configuration --- only load-time validation and env integration
- Changing gzkit's config loading contract without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev settings validation and env loading implementation completely
1. Map validation capabilities against gzkit's current config validation
1. Document comparison: validation depth, env var integration, error reporting, fail-fast behavior
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's current validation is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.30.0-08-01: Read the opsdev settings validation and env loading implementation completely
- [x] REQ-0.30.0-08-02: Map validation capabilities against gzkit's current config validation
- [x] REQ-0.30.0-08-03: Document comparison: validation depth, env var integration, error reporting, fail-fast behavior
- [x] REQ-0.30.0-08-04: Record decision with rationale: Absorb / Adapt / Exclude
- [x] REQ-0.30.0-08-05: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.30.0-08-06: If Exclude: document why gzkit's current validation is sufficient


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
