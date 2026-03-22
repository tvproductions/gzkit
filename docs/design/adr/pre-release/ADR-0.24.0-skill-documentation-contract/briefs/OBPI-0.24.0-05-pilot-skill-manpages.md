---
id: OBPI-0.24.0-05-pilot-skill-manpages
parent_adr: ADR-0.24.0-skill-documentation-contract
status: Pending
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

## PILOT CANDIDATES

Representative skills spanning categories:

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

## ALLOWED PATHS

- `docs/user/skills/*.md`
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes with all pilot manpages
- [ ] Code Quality: `uv run gz lint` passes
