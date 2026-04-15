---
id: OBPI-0.24.0-05-pilot-skill-manpages
parent: ADR-0.24.0-skill-documentation-contract
item: 5
status: Completed
lane: lite
date: 2026-03-21
---

# OBPI-0.24.0-05: Pilot Batch of Skill Manpages

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.24.0-05 — "Write pilot batch of skill manpages to validate template"`

## OBJECTIVE

Write manpages for a representative set of skills using the template from OBPI-02, validating that the template works across different skill categories and complexity levels.

## ASSUMPTIONS

- The template (OBPI-02) and surface (OBPI-03) are completed before this OBPI begins
- A pilot batch of 5-8 skills across different categories is sufficient to validate the template
- The pilot should include skills with supporting files (assets, configs) to validate that section

## NON-GOALS

- Writing manpages for all 52 skills (future chore work)
- Modifying SKILL.md files based on manpage authoring insights
- Automating manpage generation

## PILOT SET (minimum)

Required pilot skills spanning categories:

1. `gz-adr-map` (adr-operations) — workflow-based, no backing command, multiple steps
1. `gz-adr-create` (adr-operations) — complex skill with assets, templates, and co-creation rules
1. `gz-arb` (validation) — wraps QA tools, has receipt artifacts
1. `gz-check` (validation) — composite skill running multiple checks
1. `gz-session-handoff` (operations) — cross-session workflow with document artifacts
1. `gz-chore-runner` (operations) — orchestrates chore lifecycle

## REQUIREMENTS (FAIL-CLOSED)

1. Write manpages for at least 5 skills across at least 3 categories
1. Each manpage follows the template from OBPI-02
1. Each manpage includes a "When to Use" section with concrete operator scenarios
1. Skills with supporting files must have their assets documented in the manpage
1. All manpages render correctly via `uv run mkdocs build --strict`
1. Index (OBPI-03) updated with links to all pilot manpages

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.24.0-05-01: Write manpages for at least 5 skills across at least 3 categories
- [x] REQ-0.24.0-05-02: Each manpage follows the template from OBPI-02
- [x] REQ-0.24.0-05-03: Each manpage includes a "When to Use" section with concrete operator scenarios
- [x] REQ-0.24.0-05-04: Skills with supporting files must have their assets documented in the manpage
- [x] REQ-0.24.0-05-05: All manpages render correctly via `uv run mkdocs build --strict`
- [x] REQ-0.24.0-05-06: Index (OBPI-03) updated with links to all pilot manpages


## ALLOWED PATHS

- `docs/user/skills/*.md`
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run mkdocs build --strict` passes with all pilot manpages
- [x] Code Quality: `uv run gz lint` passes

## VERIFICATION COMMANDS

- `uv run mkdocs build --strict`
- `test -f docs/user/skills/gz-adr-map.md docs/user/skills/gz-adr-create.md docs/user/skills/gz-arb.md docs/user/skills/gz-check.md docs/user/skills/gz-session-handoff.md docs/user/skills/gz-chore-runner.md`
- `rg -n "^## When to Use$" docs/user/skills/gz-adr-map.md docs/user/skills/gz-adr-create.md docs/user/skills/gz-arb.md docs/user/skills/gz-check.md docs/user/skills/gz-session-handoff.md docs/user/skills/gz-chore-runner.md`

## Closing Argument

### Implementation Summary

- Created: 6 pilot skill manpages in `docs/user/skills/` spanning 3 categories
- Categories: ADR Operations (gz-adr-map, gz-adr-create), Code Quality (gz-arb, gz-check, gz-chore-runner), Agent Operations (gz-session-handoff)
- Template: All 6 manpages follow OBPI-02 template with 6 required sections each
- Supporting files: Documented in gz-adr-create (ADR template asset), gz-check (openai.yaml), gz-session-handoff (2 assets), gz-chore-runner (chore registry + proofs)
- Navigation: 6 entries added to mkdocs.yml under Skills section
- Validation: `uv run mkdocs build --strict` passes with all pilot manpages

### Key Proof

```bash
$ rg -c "^## (Purpose|When to Use|What to Expect|Invocation|Supporting Files|Related Skills and Commands)$" docs/user/skills/gz-*.md
docs/user/skills/gz-adr-create.md:6
docs/user/skills/gz-adr-map.md:6
docs/user/skills/gz-arb.md:6
docs/user/skills/gz-check.md:6
docs/user/skills/gz-chore-runner.md:6
docs/user/skills/gz-session-handoff.md:6
```

All 6 manpages contain all 6 required template sections (36 total). `uv run mkdocs build --strict` built in 1.02 seconds with zero errors.
