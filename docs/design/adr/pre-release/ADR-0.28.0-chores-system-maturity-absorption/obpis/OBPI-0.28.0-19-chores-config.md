---
id: OBPI-0.28.0-19-chores-config
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 19
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-19: Chores Config

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-19 — "Evaluate and absorb config/opsdev/chores.json (config) — chore definitions and lane configuration"`

## OBJECTIVE

Evaluate `opsdev/config/opsdev/chores.json` against gzkit's chore configuration and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev config provides a JSON-driven chore definition schema with lane selection, execution parameters, dependency declarations, scheduling hints, and metadata. gzkit's chore configuration may be simpler or structured differently. The comparison must determine whether opsdev's config-driven approach — particularly lane selection and dependency declarations — represents a maturity level gzkit should adopt.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/config/opsdev/chores.json` (config file)
- **gzkit equivalent:** `config/chores.json` or inline configuration in `src/gzkit/commands/chores.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Config schema changes must be validated by the parser (OBPI-0.28.0-17) and consumed by the planner (OBPI-0.28.0-16)
- Domain-specific chore entries (opsdev-only chores) should be excluded; the schema and structure should be evaluated for absorption
- Config-driven lane selection aligns with gzkit's governance model

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Absorbing opsdev-specific chore entries — only the schema, structure, and lane selection patterns

## REQUIREMENTS (FAIL-CLOSED)

1. Read both config files completely
1. Document comparison: schema completeness, lane selection model, dependency declarations, extensibility
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt schema to gzkit conventions and update parser/planner
1. If Confirm: document why gzkit's configuration is sufficient
1. If Exclude: document why the configuration is domain-specific

## ALLOWED PATHS

- `config/` — target for absorbed configuration schemas
- `src/gzkit/chores_tools/` — parser and planner that consume config
- `tests/` — tests for config loading and validation
- `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
