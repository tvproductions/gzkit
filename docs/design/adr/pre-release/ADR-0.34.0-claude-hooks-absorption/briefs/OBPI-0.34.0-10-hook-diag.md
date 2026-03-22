---
id: OBPI-0.34.0-10-hook-diag
parent_adr: ADR-0.34.0-claude-hooks-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-10: hook-diag

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-10 -- "Absorb hook-diag.py -- hook diagnostics and debugging"`

## OBJECTIVE

Absorb airlineops's `hook-diag.py` hook into gzkit. This hook provides diagnostics and debugging information for the hook system itself -- reporting which hooks are active, their trigger configuration, execution times, and any errors. gzkit does not currently have this hook behavior. Hook diagnostics are essential for debugging governance enforcement issues. Evaluate and absorb.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/hook-diag.py`
- **gzkit equivalent:** None -- this is a new behavior for gzkit

## ASSUMPTIONS

- Hook diagnostics are governance-generic -- any hook system benefits from self-diagnosis
- This is a meta-hook (hooks about hooks) that aids debugging
- Particularly valuable when hooks fail silently or behave unexpectedly

## NON-GOALS

- Building a hook profiling system
- Adding hook execution tracing beyond what airlineops provides

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
