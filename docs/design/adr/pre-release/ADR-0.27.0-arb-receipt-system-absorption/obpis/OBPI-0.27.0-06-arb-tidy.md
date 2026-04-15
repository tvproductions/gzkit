---
id: OBPI-0.27.0-06-arb-tidy
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-06: ARB Tidy

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-06 — "Evaluate and absorb arb/tidy.py (170 lines) — receipt cleanup and lifecycle management"`

## OBJECTIVE

Evaluate `opsdev/arb/tidy.py` (170 lines) against gzkit's current approach to artifact lifecycle and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module manages receipt lifecycle: age-based cleanup, retention policies, dry-run previews, and summary reporting of tidied artifacts. gzkit currently has no receipt lifecycle management because it has no receipts. The comparison must determine whether receipt lifecycle management is a necessary consequence of adopting the receipt system, or an unnecessary complexity layer.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/tidy.py` (170 lines)
- **gzkit equivalent:** No direct equivalent — no receipt artifacts to manage

## ASSUMPTIONS

- The governance value question governs: if receipts are adopted, does lifecycle management become necessary?
- This module's value is contingent on whether the receipt system itself is adopted (OBPIs 01-05)
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 170 lines, this module addresses a real operational concern (disk growth) if receipts are persisted

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Designing a general artifact lifecycle system — scope is receipt-specific

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: retention policies, cleanup strategies, dry-run support, reporting
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why receipt lifecycle management is unnecessary
1. If Exclude: document why the module is environment-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-06-01: Read both implementations completely
- [x] REQ-0.27.0-06-02: Document comparison: retention policies, cleanup strategies, dry-run support, reporting
- [x] REQ-0.27.0-06-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-06-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-06-05: If Confirm: document why receipt lifecycle management is unnecessary
- [x] REQ-0.27.0-06-06: If Exclude: document why the module is environment-specific


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
