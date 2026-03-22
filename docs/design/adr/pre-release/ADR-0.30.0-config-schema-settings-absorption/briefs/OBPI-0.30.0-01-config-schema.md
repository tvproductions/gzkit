---
id: OBPI-0.30.0-01-config-schema
parent_adr: ADR-0.30.0-config-schema-settings-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-01: Config Schema

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-01 --- "Evaluate and absorb config/schema.py (590 lines) --- Pydantic settings models and schema validation"`

## OBJECTIVE

Evaluate opsdev's `config/schema.py` (590 lines) against gzkit's `config.py` (171 lines) and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (project-specific). The opsdev module provides Pydantic settings models with typed configuration, load-time validation, and schema enforcement. gzkit's current config.py is significantly smaller and lacks Pydantic settings models, so the comparison must determine the exact capability gap.

## SOURCE MATERIAL

- **opsdev:** `config/schema.py` (590 lines)
- **gzkit equivalent:** `src/gzkit/config.py` (171 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- The 419-line gap likely indicates missing Pydantic settings models and validation in gzkit

## NON-GOALS

- Rewriting from scratch --- absorb or adapt, don't reinvent
- Changing opsdev --- this is upstream absorption only
- Breaking existing gzkit config consumers during absorption

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: settings model coverage, validation depth, type safety, extensibility
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is project-specific

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
