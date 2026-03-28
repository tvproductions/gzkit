---
id: OBPI-0.27.0-09-arb-supabase-sync
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 9
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-09: ARB Supabase Sync

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-09 — "Evaluate and absorb arb/supabase_sync.py (157 lines) — Supabase receipt synchronization"`

## OBJECTIVE

Evaluate `opsdev/arb/supabase_sync.py` (157 lines) against gzkit's current approach to receipt persistence and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module synchronizes local receipt artifacts to Supabase for centralized storage, cross-environment querying, and long-term retention. gzkit currently has no external receipt sync because it has no receipt system. The comparison must determine whether Supabase sync is a reusable persistence pattern or an opsdev-specific integration that does not generalize.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/supabase_sync.py` (157 lines)
- **gzkit equivalent:** No direct equivalent — no external receipt synchronization

## ASSUMPTIONS

- This module is the most likely candidate for Exclude — Supabase is an environment-specific backend choice
- If the pattern (sync receipts to external store) is valuable, the abstraction may be worth absorbing even if the Supabase implementation is excluded
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- External service dependencies (Supabase client, API keys) are inherently environment-specific

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a generic receipt sync abstraction layer — scope is evaluating the concrete Supabase module

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: sync protocol, error handling, idempotency, external service coupling
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests (mock external service)
1. If Confirm: document why local receipt storage is sufficient
1. If Exclude: document why the module is environment-specific (likely outcome)

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
