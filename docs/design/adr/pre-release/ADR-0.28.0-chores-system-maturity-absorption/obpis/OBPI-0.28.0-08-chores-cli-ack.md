---
id: OBPI-0.28.0-08-chores-cli-ack
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-08: Chores CLI Ack

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-08 — "Evaluate and absorb chores_tools/cli_ack.py (76 lines) — acknowledge subcommand implementation"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/cli_ack.py` (76 lines) and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides an acknowledge subcommand that allows operators to acknowledge chore results, mark recommendations as addressed, or dismiss findings. gzkit currently has no equivalent acknowledgment workflow for chores. The comparison must determine whether chore acknowledgment is generic infrastructure for operator-driven chore lifecycle management.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/cli_ack.py` (76 lines)
- **gzkit equivalent:** None (no chores acknowledgment subcommand)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Acknowledgment workflows align with governance-first principles (human attestation of automated results)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a general-purpose acknowledgment framework — this is chores-specific

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/chores_tools/` — target for absorbed modules
- `src/gzkit/commands/chores.py` — existing monolith (may be refactored)
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
