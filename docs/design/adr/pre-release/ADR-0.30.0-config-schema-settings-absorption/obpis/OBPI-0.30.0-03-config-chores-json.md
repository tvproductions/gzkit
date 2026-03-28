---
id: OBPI-0.30.0-03-config-chores-json
parent: ADR-0.30.0-config-schema-settings-absorption
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-03: Config Chores JSON

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-03 --- "Evaluate and absorb config/opsdev/chores.json --- chore configuration schema and data"`

## OBJECTIVE

Evaluate opsdev's `config/opsdev/chores.json` against gzkit's chore configuration to determine: Absorb (the schema pattern is governance-generic), Confirm (gzkit's chore config is sufficient), or Exclude (project-specific chore definitions). The evaluation must separate the schema pattern (how chores are configured) from the data content (which chores are defined) --- the pattern may be generic even if the data is project-specific.

## SOURCE MATERIAL

- **opsdev:** `config/opsdev/chores.json`
- **gzkit equivalent:** Current chore configuration in gzkit's config layer

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- The schema pattern (structure, validation, extensibility) is likely governance-generic
- The specific chore definitions are likely project-specific
- gzkit should own the schema pattern; projects should own their chore definitions

## NON-GOALS

- Absorbing project-specific chore definitions as gzkit defaults
- Changing the chore management model without Heavy lane approval
- Duplicating chore data across gzkit and opsdev

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev chores.json completely
1. Separate schema pattern from data content
1. Document comparison: schema structure, validation rules, extensibility, defaults
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: extract the generic schema pattern and write tests
1. If Exclude: document why gzkit's current chore config is sufficient

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
