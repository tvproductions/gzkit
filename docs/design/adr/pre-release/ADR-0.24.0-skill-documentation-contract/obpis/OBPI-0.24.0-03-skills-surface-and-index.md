---
id: OBPI-0.24.0-03-skills-surface-and-index
parent: ADR-0.24.0-skill-documentation-contract
item: 3
status: Completed
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

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.24.0-03-01: Create `docs/user/skills/index.md` with categorized skill listing (using SKILL.md category metadata)
- [x] REQ-0.24.0-03-02: Each skill in the index has a one-line description and link to its manpage
- [x] REQ-0.24.0-03-03: Add `docs/user/skills/` to mkdocs.yml navigation under User Guide
- [x] REQ-0.24.0-03-04: `uv run mkdocs build --strict` passes with the new surface
- [x] REQ-0.24.0-03-05: Index categories match SKILL.md `category` metadata (e.g., adr-operations, governance, validation)


## ALLOWED PATHS

- `docs/user/skills/index.md`
- `mkdocs.yml`
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run mkdocs build --strict` passes with index
- [x] Code Quality: `uv run gz lint` passes

## VERIFICATION COMMANDS

- `uv run mkdocs build --strict`
- `test -f docs/user/skills/index.md`
- `rg -n "Skills:" mkdocs.yml`
- `rg -n "adr-operations|validation|operations" docs/user/skills/index.md`

## Closing Argument

### Implementation Summary

- Created: `docs/user/skills/index.md` — categorized skill index with 52 entries across 8 categories
- Categories: ADR Lifecycle, ADR Operations, ADR Audit, OBPI Pipeline, Code Quality, Governance Infrastructure, Agent Operations, Cross-Repository
- Each: skill entry has one-line description and relative link to manpage location
- Modified: `mkdocs.yml` — added Skills nav entry between Concepts and Commands
- Linked: index intro references Documentation Taxonomy for audience split context

### Key Proof

```bash
$ grep -c "\.md)" docs/user/skills/index.md
52

$ grep "Skills:" mkdocs.yml
  - Skills:

$ uv run mkdocs build --strict
INFO - Documentation built in 0.94 seconds
```

All 5 FAIL-CLOSED requirements verified by independent spec reviewer (PASS, 5/5 MET, docs quality 4/5).
