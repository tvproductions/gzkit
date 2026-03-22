---
id: OBPI-0.27.0-01-ruff-reporter
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-01: Ruff Reporter

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-01 — "Evaluate and absorb arb/ruff_reporter.py (247 lines) — Ruff lint receipt generation with structured findings"`

## OBJECTIVE

Evaluate `opsdev/arb/ruff_reporter.py` (247 lines) against gzkit's current ARB skill-only approach for Ruff linting and determine: Absorb (opsdev adds governance value), Confirm (gzkit's native `uv run ruff check` is sufficient), or Exclude (environment-specific). The opsdev module wraps Ruff execution, captures JSON output, transforms violations into structured receipt findings, and persists receipts to disk. gzkit currently invokes Ruff directly via native commands with no structured receipt layer. The comparison must determine whether structured Ruff receipts provide governance evidence that raw Ruff output cannot.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/ruff_reporter.py` (247 lines)
- **gzkit equivalent:** Native `uv run ruff check .` via skill-only ARB approach (no structured receipts)

## ASSUMPTIONS

- The governance value question governs: do structured receipts enable deterministic validation that raw output cannot?
- opsdev wins where receipt artifacts provide audit trail value; gzkit wins where simplicity suffices
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- The 247-line module likely contains both reusable receipt infrastructure and opsdev-specific wiring

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying gzkit's existing native Ruff invocation if skill-only approach is confirmed as sufficient

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: receipt structure, finding categorization, error handling, persistence patterns
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
