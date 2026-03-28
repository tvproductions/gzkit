---
id: OBPI-0.28.0-02-chores-cli-core
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-02: Chores CLI Core

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-02 — "Evaluate and absorb chores_tools/cli_core.py (61 lines) — shared CLI utilities and argument parsing"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/cli_core.py` (61 lines) against gzkit's shared CLI utilities and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides shared argument parsing helpers, common option definitions, and CLI utility functions used across all chores subcommands. gzkit currently has no equivalent shared layer for chores CLI — each function in the monolith handles its own argument parsing inline.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/cli_core.py` (61 lines)
- **gzkit equivalent:** Inline argument handling in `src/gzkit/commands/chores.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Shared CLI utilities reduce duplication across subcommands and enforce consistent behavior

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Creating a generic CLI framework — this is chores-specific shared utilities

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
