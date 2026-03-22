---
id: OBPI-0.28.0-01-chores-cli
parent_adr: ADR-0.28.0-chores-system-maturity-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-01: Chores CLI

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-01 — "Evaluate and absorb chores_tools/cli.py (60 lines) — CLI entry point and subcommand registration"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/cli.py` (60 lines) against gzkit's `commands/chores.py` CLI entry point and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides a dedicated CLI entry point that registers subcommands (plan, run, advise, audit, status, ack, register) via a modular dispatch pattern. gzkit's current equivalent bundles all CLI logic in a single 667-line file, so the comparison must determine whether opsdev's decomposed entry point pattern should replace gzkit's monolithic approach.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/cli.py` (60 lines)
- **gzkit equivalent:** `src/gzkit/commands/chores.py` (667 lines, monolithic — CLI entry point embedded)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- A 60-line focused entry point vs embedded logic in a 667-line monolith suggests clear separation-of-concerns advantage

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying the existing `gz chores` CLI command contract without Heavy lane approval

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
