---
id: OBPI-0.34.0-01-obpi-completion-validator
parent_adr: ADR-0.34.0-claude-hooks-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-01: obpi-completion-validator

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-01 -- "Compare obpi-completion-validator.py -- validates OBPI completion claims"`

## OBJECTIVE

Compare airlineops's `obpi-completion-validator.py` hook against gzkit's equivalent hook behavior. This hook validates that OBPI completion claims are legitimate -- checking that acceptance criteria are met, tests pass, and evidence exists before allowing an agent to mark an OBPI as complete. Determine whether gzkit's existing hook covers the same validation depth or whether airlineops's implementation is more thorough.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/obpi-completion-validator.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- OBPI validation behavior in existing modules

## ASSUMPTIONS

- gzkit likely has some OBPI completion validation in its hook infrastructure
- airlineops's version may have additional validation checks from operational use
- The comparison must compare actual validation logic, not just hook trigger configuration

## NON-GOALS

- Changing OBPI completion criteria
- Modifying hook trigger events

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: validation checks, evidence requirements, error messages
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's validation is sufficient

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
