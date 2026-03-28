---
id: OBPI-0.30.0-06-config-workspace-patterns
parent: ADR-0.30.0-config-schema-settings-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.30.0-06: Config Workspace Patterns

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.30.0-config-schema-settings-absorption/ADR-0.30.0-config-schema-settings-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.30.0-06 --- "Evaluate and absorb workspace pointer patterns --- workspace discovery and multi-project support"`

## OBJECTIVE

Evaluate opsdev's workspace pointer patterns against gzkit's workspace discovery to determine: Absorb (opsdev has superior workspace patterns), Confirm (gzkit's workspace handling is sufficient), or Exclude (project-specific workspace logic). The evaluation must assess how opsdev discovers and manages workspace roots, companion project pointers, and multi-project configurations --- capabilities that gzkit may need for governing multi-repo environments.

## SOURCE MATERIAL

- **opsdev:** Workspace pointer patterns in config infrastructure
- **gzkit equivalent:** Current workspace discovery in `src/gzkit/config.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Workspace discovery (finding project root, resolving companion paths) is governance-generic
- Multi-project workspace support may be needed for gzkit to govern companion repositories
- If workspace patterns are tightly coupled to opsdev's specific project layout, they may need adaptation

## NON-GOALS

- Absorbing project-specific workspace layouts as gzkit defaults
- Implementing full monorepo support --- only workspace discovery and pointer resolution
- Changing gzkit's project root detection without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev workspace pattern implementation completely
1. Map workspace discovery capabilities against gzkit's current handling
1. Document comparison: root detection, companion resolution, multi-project support
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's current workspace handling is sufficient

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
