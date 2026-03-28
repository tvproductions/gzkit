---
id: OBPI-0.34.0-04-instruction-router
parent: ADR-0.34.0-claude-hooks-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-04: instruction-router

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-04 -- "Compare instruction-router.py -- routes instructions based on context"`

## OBJECTIVE

Compare airlineops's `instruction-router.py` hook against gzkit's equivalent hook behavior. This hook routes contextual instructions to the agent based on the current work context -- loading relevant rules, skills, and governance constraints based on what files are being edited or what command is being executed. Determine whether gzkit's existing instruction routing covers the same behavior.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/instruction-router.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- instruction routing behavior in existing modules

## ASSUMPTIONS

- gzkit likely has instruction routing in its hook infrastructure
- airlineops's version may route based on different context signals
- The comparison must examine routing logic, context detection, and instruction loading

## NON-GOALS

- Changing the instruction file format
- Modifying Claude Code's hook trigger system

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: context signals, routing logic, instruction sources, fallback behavior
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's routing is sufficient

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
