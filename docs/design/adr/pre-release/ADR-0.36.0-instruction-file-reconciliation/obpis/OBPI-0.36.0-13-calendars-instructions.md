---
id: OBPI-0.36.0-13-calendars-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 13
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-13: calendars-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-13 — "Evaluate calendars.instructions.md for generic pattern extraction"`

## OBJECTIVE

Evaluate airlineops's `calendars.instructions.md` for extractable generic patterns. This file has no gzkit counterpart and is nominally domain-specific (airline calendar/schedule operations). However, it may contain generic patterns applicable to date/time handling: timezone conventions, date formatting, calendar arithmetic, scheduling patterns, temporal data validation. Determine: Extract (generic patterns warrant a new gzkit rules file) or Exclude (entirely domain-specific).

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/calendars.instructions.md`
- **gzkit equivalent:** None

## ASSUMPTIONS

- The file is likely primarily airline-domain-specific (calendars = airline schedules)
- Generic patterns may exist in: timezone handling, date formatting, temporal data validation
- Do not assume the file is entirely domain-specific without reading it
- If generic patterns are minimal, Exclude is the appropriate decision

## NON-GOALS

- Importing airline scheduling patterns into gzkit
- Creating temporal data governance in gzkit (unless generic patterns warrant it)
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops `calendars.instructions.md` completely
1. Categorize each section as: generic (applicable to any project with dates/times) or domain-specific (airline calendars)
1. If generic patterns exist: document what to extract and propose scope
1. Record decision with rationale: Extract / Exclude

## ALLOWED PATHS

- `.claude/rules/` — target for new rules file if extracted
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
