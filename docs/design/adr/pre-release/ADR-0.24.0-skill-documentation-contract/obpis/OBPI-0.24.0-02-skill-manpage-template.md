---
id: OBPI-0.24.0-02-skill-manpage-template
parent: ADR-0.24.0-skill-documentation-contract
item: 2
status: Completed
lane: lite
date: 2026-03-21
---

# OBPI-0.24.0-02: Skill Manpage Template

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.24.0-02 — "Define skill manpage template with required sections distinct from SKILL.md"`

## OBJECTIVE

Create a standardized skill manpage template at `docs/user/skills/_TEMPLATE.md` with required sections that serve operators (not agents). The template must be distinct from SKILL.md and parallel in rigor to command manpages.

## ASSUMPTIONS

- Command manpage structure in `docs/user/commands/` is the model to follow
- Skill manpages need additional sections not found in command manpages (e.g., Supporting Files, Related Skills)
- The template is prescriptive — all sections are required for every skill manpage

## NON-GOALS

- Modifying the SKILL.md template or agent instruction format
- Changing the command manpage template
- Writing actual skill manpages (covered by OBPI-05)

## REQUIREMENTS (FAIL-CLOSED)

1. Template must include at minimum: Purpose, When to Use, What to Expect, Invocation, Supporting Files, Related Skills/Commands
1. Template must NOT duplicate SKILL.md agent-facing content; it must translate for operators
1. Template must include a "When to Use" section that situates the skill in workflow context (connecting to runbook)
1. Template must document supporting files when a skill has assets, configs, or subagent definitions
1. Place template at `docs/user/skills/_TEMPLATE.md`

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.24.0-02-01: Template must include at minimum: Purpose, When to Use, What to Expect, Invocation, Supporting Files, Related Skills/Commands
- [x] REQ-0.24.0-02-02: Template must NOT duplicate SKILL.md agent-facing content; it must translate for operators
- [x] REQ-0.24.0-02-03: Template must include a "When to Use" section that situates the skill in workflow context (connecting to runbook)
- [x] REQ-0.24.0-02-04: Template must document supporting files when a skill has assets, configs, or subagent definitions
- [x] REQ-0.24.0-02-05: Place template at `docs/user/skills/_TEMPLATE.md`


## ALLOWED PATHS

- `docs/user/skills/_TEMPLATE.md`
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run mkdocs build --strict` passes with template
- [x] Code Quality: `uv run gz lint` passes

## VERIFICATION COMMANDS

- `uv run mkdocs build --strict`
- `rg -n "^## (Purpose|When to Use|What to Expect|Invocation|Supporting Files|Related Skills/Commands)$" docs/user/skills/_TEMPLATE.md`
- `rg -n "operator|workflow|SKILL\\.md" docs/user/skills/_TEMPLATE.md`

## Closing Argument

### Implementation Summary

- Created: `docs/user/skills/_TEMPLATE.md` — prescriptive skill manpage template with 6 required sections
- Sections: Purpose, When to Use, What to Expect, Invocation, Supporting Files, Related Skills and Commands
- Guidance: HTML comments instruct authors on audience, tone, and SKILL.md differentiation
- Linkage: When to Use section includes concrete runbook-linking example per taxonomy linkage model
- Supporting Files: Pre-seeded table with universal SKILL.md baseline entry and Read/Write columns

### Key Proof

```bash
$ rg -n "^## (Purpose|When to Use|What to Expect|Invocation|Supporting Files|Related Skills and Commands)$" docs/user/skills/_TEMPLATE.md
10:## Purpose
17:## When to Use
28:## What to Expect
36:## Invocation
54:## Supporting Files
64:## Related Skills and Commands
```

```bash
$ uv run mkdocs build --strict
INFO - Documentation built in 0.99 seconds
```

All 5 FAIL-CLOSED requirements verified by independent spec reviewer (PASS, 5/5 MET, docs quality 5/5).
