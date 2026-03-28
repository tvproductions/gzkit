---
id: OBPI-0.24.0-03-skills-surface-and-index
parent: ADR-0.24.0-skill-documentation-contract
item: 3
status: Pending
lane: lite
date: 2026-03-21
---

# OBPI-0.24.0-03: Skills Documentation Surface and Index

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.24.0-03 — "Create docs/user/skills/ surface with index page and mkdocs.yml integration"`

## OBJECTIVE

Create the `docs/user/skills/` directory with a categorized index page and integrate it into mkdocs.yml site navigation, parallel to the existing `docs/user/commands/` surface.

## ASSUMPTIONS

- The skill category field from SKILL.md metadata can be used to organize the index
- The index follows the same pattern as `docs/user/commands/index.md`
- mkdocs.yml already has a User Guide section where this can be added

## NON-GOALS

- Writing individual skill manpages (covered by OBPI-05)
- Automating index generation from SKILL.md files (future chore)
- Restructuring existing command documentation

## REQUIREMENTS (FAIL-CLOSED)

1. Create `docs/user/skills/index.md` with categorized skill listing (using SKILL.md category metadata)
1. Each skill in the index has a one-line description and link to its manpage
1. Add `docs/user/skills/` to mkdocs.yml navigation under User Guide
1. `uv run mkdocs build --strict` passes with the new surface
1. Index categories match SKILL.md `category` metadata (e.g., adr-operations, governance, validation)

## ALLOWED PATHS

- `docs/user/skills/index.md`
- `mkdocs.yml`
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes with index
- [ ] Code Quality: `uv run gz lint` passes

## VERIFICATION COMMANDS

- `uv run mkdocs build --strict`
- `test -f docs/user/skills/index.md`
- `rg -n "Skills:" mkdocs.yml`
- `rg -n "adr-operations|validation|operations" docs/user/skills/index.md`
