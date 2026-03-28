---
id: OBPI-0.34.0-08-pipeline-gate
parent: ADR-0.34.0-claude-hooks-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-08: pipeline-gate

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-08 -- "Compare pipeline-gate.py -- gates pipeline progression"`

## OBJECTIVE

Compare airlineops's `pipeline-gate.py` hook against gzkit's equivalent hook behavior. This hook gates pipeline progression -- preventing the agent from advancing to the next pipeline stage without completing the current stage's requirements. Determine whether gzkit's existing pipeline gating covers the same enforcement depth.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/pipeline-gate.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- pipeline gating behavior in existing modules

## ASSUMPTIONS

- Pipeline gating is critical for governance enforcement -- prevents stage skipping
- gzkit likely has pipeline gating in its hook infrastructure
- airlineops's version may enforce additional stage completion criteria

## NON-GOALS

- Changing pipeline stage definitions
- Modifying gate criteria without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: gating criteria per stage, enforcement mechanism, bypass prevention
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's pipeline gating is sufficient

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
