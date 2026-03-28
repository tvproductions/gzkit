---
id: OBPI-0.30.0-05-config-test-suites-json
parent: ADR-0.30.0-config-schema-settings-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-05: Config Test Suites JSON

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-05 --- "Evaluate and absorb config/opsdev/test_suites.json --- test suite configuration schema and data"`

## OBJECTIVE

Evaluate opsdev's `config/opsdev/test_suites.json` against gzkit's test suite configuration to determine: Absorb (the schema pattern is governance-generic), Confirm (gzkit's test config is sufficient), or Exclude (project-specific test suite definitions). The evaluation must separate the schema pattern (how test suites are configured) from the data content (which test suites are defined) --- the pattern may be generic even if the data is project-specific.

## SOURCE MATERIAL

- **opsdev:** `config/opsdev/test_suites.json`
- **gzkit equivalent:** Current test configuration in gzkit's config layer

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- The schema pattern (suite definition, runner configuration, timeout settings) is likely governance-generic
- The specific test suite definitions are likely project-specific
- gzkit should own the schema pattern; projects should own their suite definitions

## NON-GOALS

- Absorbing project-specific test suite definitions as gzkit defaults
- Changing the test execution model without Heavy lane approval
- Duplicating test suite configuration across gzkit and opsdev

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev test_suites.json completely
1. Separate schema pattern from data content
1. Document comparison: schema structure, suite definition model, runner configuration
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: extract the generic schema pattern and write tests
1. If Exclude: document why gzkit's current test config is sufficient

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
