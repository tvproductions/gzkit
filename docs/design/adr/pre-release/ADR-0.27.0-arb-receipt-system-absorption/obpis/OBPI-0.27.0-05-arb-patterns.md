---
id: OBPI-0.27.0-05-arb-patterns
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-05: ARB Patterns

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-05 — "Evaluate and absorb arb/patterns.py (253 lines) — pattern detection across receipt history"`

## OBJECTIVE

Evaluate `opsdev/arb/patterns.py` (253 lines) against gzkit's current approach to QA trend analysis and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module is the largest in the ARB subsystem and performs cross-receipt pattern detection: identifying recurring violations by rule, file, and category; tracking violation trends over time; computing frequency and severity metrics. gzkit currently has no equivalent — each QA run is independent with no cross-run analysis. The comparison must determine whether pattern detection across receipt history provides governance value that justifies the 253-line complexity.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/patterns.py` (253 lines)
- **gzkit equivalent:** No direct equivalent — QA runs are independent

## ASSUMPTIONS

- The governance value question governs: does cross-receipt pattern detection surface insights that single-run output cannot?
- opsdev wins where trend analysis identifies systemic issues invisible in individual runs
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 253 lines, this is the most complex ARB module — complexity-vs-value ratio is critical
- This module is consumed by advise (OBPI-04) and likely depends on receipt storage (OBPI-10)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building statistical analysis beyond deterministic pattern matching

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: pattern detection algorithms, trend metrics, dependency chain, complexity cost
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why independent QA runs are sufficient for governance
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
