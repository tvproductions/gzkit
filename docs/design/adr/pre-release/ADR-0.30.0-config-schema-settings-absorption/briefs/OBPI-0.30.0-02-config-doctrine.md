---
id: OBPI-0.30.0-02-config-doctrine
parent_adr: ADR-0.30.0-config-schema-settings-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-02: Config Doctrine

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-02 --- "Evaluate and absorb config/doctrine.py (745 lines) --- doctrine enforcement and compliance rules"`

## OBJECTIVE

Evaluate opsdev's `config/doctrine.py` (745 lines) against gzkit's doctrine enforcement (currently documentation-only, no programmatic enforcement). Determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (project-specific). The opsdev module provides programmatic doctrine enforcement --- gzkit enforces doctrine through documentation and human review only. The 745-line gap represents a fundamental capability difference that must be evaluated honestly.

## SOURCE MATERIAL

- **opsdev:** `config/doctrine.py` (745 lines)
- **gzkit equivalent:** No programmatic equivalent --- doctrine enforcement is documentation-only

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Programmatic doctrine enforcement is governance-generic by nature --- the question is whether opsdev's specific enforcement rules are generic or project-specific

## NON-GOALS

- Rewriting from scratch --- absorb or adapt, don't reinvent
- Changing opsdev --- this is upstream absorption only
- Replacing gzkit's documentation-based doctrine if programmatic enforcement is not warranted

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Document comparison: enforcement rules, compliance checking, violation reporting, extensibility
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why documentation-based enforcement is sufficient
1. If Exclude: document why the enforcement rules are project-specific

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
