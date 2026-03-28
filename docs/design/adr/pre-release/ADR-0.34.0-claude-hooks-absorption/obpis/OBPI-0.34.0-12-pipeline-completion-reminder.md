---
id: OBPI-0.34.0-12-pipeline-completion-reminder
parent: ADR-0.34.0-claude-hooks-absorption
item: 12
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-12: pipeline-completion-reminder

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-12 -- "Compare pipeline-completion-reminder.py -- reminds about incomplete pipelines"`

## OBJECTIVE

Compare airlineops's `pipeline-completion-reminder.py` hook against gzkit's equivalent hook behavior. This hook reminds the agent about incomplete pipeline steps -- detecting when the agent is about to finish work without completing all required governance pipeline stages. Determine whether gzkit's existing reminder behavior covers the same scenarios.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/pipeline-completion-reminder.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- pipeline completion reminder behavior in existing modules

## ASSUMPTIONS

- Pipeline completion reminders prevent agents from skipping governance steps
- gzkit likely has some form of completion reminder
- airlineops's version may detect additional incomplete-pipeline scenarios

## NON-GOALS

- Blocking agent completion (this is a reminder, not a gate)
- Changing pipeline stage definitions

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: detection triggers, reminder messages, covered pipeline stages
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's reminder behavior is sufficient

## ALLOWED PATHS

- `src/gzkit/hooks/` -- target for absorbed hook behavior
- `tests/` -- tests for absorbed hook behavior
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
