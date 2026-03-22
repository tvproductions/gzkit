---
id: OBPI-0.34.0-13-insight-reminder
parent_adr: ADR-0.34.0-claude-hooks-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-13: insight-reminder

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-13 -- "Absorb insight-reminder.py -- reminds about pending insights"`

## OBJECTIVE

Absorb airlineops's `insight-reminder.py` hook into gzkit. This hook reminds the agent about pending insights that should be recorded -- detecting when the agent has made observations, decisions, or encountered patterns that should be captured in the insights ledger but have not yet been recorded. This complements the insight-harvester (OBPI-03) by ensuring insights are not lost. gzkit does not currently have this hook behavior. Evaluate and absorb.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/insight-reminder.py`
- **gzkit equivalent:** None -- this is a new behavior for gzkit

## ASSUMPTIONS

- Insight reminders are governance-generic -- all agent-governed projects benefit from capturing observations
- This hook complements the insight-harvester (OBPI-03) -- harvest and remind
- The reminder likely triggers at session boundaries or after significant work

## NON-GOALS

- Building an insight analysis system
- Forcing insight recording (this is a reminder, not a gate)

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops implementation completely
1. Evaluate governance generality (expected: governance-generic)
1. Adapt to gzkit hook module architecture
1. Implement and write tests
1. Document the absorption rationale

## ALLOWED PATHS

- `src/gzkit/hooks/` -- target for new hook behavior
- `tests/` -- tests for new hook behavior
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Absorption rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
