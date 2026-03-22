---
id: OBPI-0.34.0-09-session-staleness-check
parent_adr: ADR-0.34.0-claude-hooks-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-09: session-staleness-check

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-09 -- "Compare session-staleness-check.py -- checks for stale session state"`

## OBJECTIVE

Compare airlineops's `session-staleness-check.py` hook against gzkit's equivalent hook behavior. This hook checks whether the agent's session state is stale -- detecting when governance state has changed on disk (by another agent or human) since the session began, preventing the agent from operating on outdated information. Determine whether gzkit's existing staleness detection covers the same scenarios.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/session-staleness-check.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- staleness detection behavior in existing modules

## ASSUMPTIONS

- Session staleness is a real problem in multi-agent and human+agent workflows
- gzkit likely has some form of staleness detection
- airlineops's version may check additional state signals (world state hash, ledger modification time)

## NON-GOALS

- Building real-time state synchronization
- Handling multi-agent conflict resolution (only detection)

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: staleness signals, detection mechanism, user notification
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's staleness detection is sufficient

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
