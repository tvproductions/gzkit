---
id: OBPI-0.27.0-02-step-reporter
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-02: Step Reporter

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-02 — "Evaluate and absorb arb/step_reporter.py (138 lines) — generic QA step receipt generation"`

## OBJECTIVE

Evaluate `opsdev/arb/step_reporter.py` (138 lines) against gzkit's current ARB skill-only approach for generic QA steps and determine: Absorb (opsdev adds governance value), Confirm (gzkit's native command execution is sufficient), or Exclude (environment-specific). The opsdev module wraps arbitrary QA commands (unittest, coverage, ty), captures execution metadata (exit code, duration, stdout/stderr), and generates structured step receipts. gzkit currently executes QA steps directly with no receipt layer. The comparison must determine whether step receipts provide governance evidence that raw command output cannot.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/step_reporter.py` (138 lines)
- **gzkit equivalent:** Native QA command execution via skill-only ARB approach (no structured receipts)

## ASSUMPTIONS

- The governance value question governs: do structured receipts enable deterministic validation that raw output cannot?
- opsdev wins where receipt artifacts provide audit trail value; gzkit wins where simplicity suffices
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 138 lines, this module is likely focused and reusable with minimal opsdev-specific coupling

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing native QA command execution if skill-only approach is confirmed as sufficient

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: receipt structure, execution metadata capture, error handling, persistence patterns
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's skill-only approach is sufficient
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
