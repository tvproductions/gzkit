---
id: OBPI-0.34.0-07-plan-audit-gate
parent: ADR-0.34.0-claude-hooks-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-07: plan-audit-gate

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-07 -- "Compare plan-audit-gate.py -- gates plan execution with audit checks"`

## OBJECTIVE

Compare airlineops's `plan-audit-gate.py` hook against gzkit's equivalent hook behavior. This hook gates plan execution by running audit checks before allowing the agent to proceed with implementation -- ensuring plans meet governance standards before work begins. Determine whether gzkit's existing plan gating covers the same audit depth.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/plan-audit-gate.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- plan gating behavior in existing modules

## ASSUMPTIONS

- Plan auditing before execution is a governance enforcement pattern
- gzkit likely has some form of plan gating
- airlineops's version may check additional audit criteria from operational experience

## NON-GOALS

- Changing plan format or requirements
- Adding new audit criteria without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: audit checks, gating criteria, failure messages, bypass prevention
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's plan gating is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.34.0-07-01: Read both implementations completely
- [x] REQ-0.34.0-07-02: Document comparison: audit checks, gating criteria, failure messages, bypass prevention
- [x] REQ-0.34.0-07-03: Record decision: gzkit sufficient, or absorb airlineops improvements
- [x] REQ-0.34.0-07-04: If absorbing: integrate into gzkit hook module architecture and write tests
- [x] REQ-0.34.0-07-05: If confirming: document why gzkit's plan gating is sufficient


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
