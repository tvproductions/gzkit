---
id: OBPI-0.28.0-06-chores-cli-audit
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-06: Chores CLI Audit

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-06 — "Evaluate and absorb chores_tools/cli_audit.py (150 lines) — audit subcommand implementation"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/cli_audit.py` (150 lines) and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides a dedicated audit subcommand for chore execution history review, compliance verification, and evidence trail inspection. gzkit currently has no equivalent chores audit capability — audit functionality exists at the ADR level but not at the chores level. The comparison must determine whether chore-level auditing is a generic infrastructure need.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/cli_audit.py` (150 lines)
- **gzkit equivalent:** None (no chores-specific audit subcommand)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Chore-level auditing may be generic infrastructure if it tracks execution history and compliance

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's ADR-level audit system — this is chores-specific auditing

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
