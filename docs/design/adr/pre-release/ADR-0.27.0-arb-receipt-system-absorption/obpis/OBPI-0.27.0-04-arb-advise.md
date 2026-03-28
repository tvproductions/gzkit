---
id: OBPI-0.27.0-04-arb-advise
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-04: ARB Advise

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-04 — "Evaluate and absorb arb/advise.py (196 lines) — receipt analysis and recurring pattern advice"`

## OBJECTIVE

Evaluate `opsdev/arb/advise.py` (196 lines) against gzkit's current approach to QA feedback and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module analyzes receipt history, identifies recurring violations and patterns, categorizes findings by severity and frequency, and generates actionable advice. gzkit currently has no equivalent — QA feedback comes from raw command output. The comparison must determine whether structured advice from receipt analysis provides governance value beyond what developers can derive from reading raw lint/test output.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/advise.py` (196 lines)
- **gzkit equivalent:** No direct equivalent — raw QA command output only

## ASSUMPTIONS

- The governance value question governs: does receipt-based advice surface patterns that raw output cannot?
- opsdev wins where pattern analysis across receipt history reveals recurring issues invisible in single-run output
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- This module depends on receipt storage (OBPI-10) and likely patterns (OBPI-05) — evaluation should note dependencies

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building an AI-powered advice engine — this is deterministic pattern analysis

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: analysis depth, pattern categorization, advice quality, dependency chain
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why raw QA output is sufficient for governance
1. If Exclude: document why the module is environment-specific

## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
