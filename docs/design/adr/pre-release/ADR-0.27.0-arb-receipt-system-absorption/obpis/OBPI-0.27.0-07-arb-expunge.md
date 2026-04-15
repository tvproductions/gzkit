---
id: OBPI-0.27.0-07-arb-expunge
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-07: ARB Expunge

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-07 — "Evaluate and absorb arb/expunge.py (114 lines) — receipt expungement and hard deletion"`

## OBJECTIVE

Evaluate `opsdev/arb/expunge.py` (114 lines) against gzkit's current approach to artifact deletion and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module provides hard deletion of receipt artifacts with confirmation prompts, batch deletion, and audit logging of expunged receipts. This differs from tidy (OBPI-06) which is policy-based cleanup; expunge is explicit operator-initiated deletion. gzkit currently has no receipt expungement because it has no receipts. The comparison must determine whether explicit expungement is a necessary operational capability if receipts are adopted.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/expunge.py` (114 lines)
- **gzkit equivalent:** No direct equivalent — no receipt artifacts to expunge

## ASSUMPTIONS

- The governance value question governs: if receipts are adopted, does operator-initiated deletion become necessary?
- This module's value is contingent on whether the receipt system itself is adopted (OBPIs 01-05)
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 114 lines, this is a focused utility module with clear operational purpose

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Designing a general artifact deletion system — scope is receipt-specific

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: deletion safety (confirmation, dry-run), batch support, audit logging
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why receipt expungement is unnecessary
1. If Exclude: document why the module is environment-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-07-01: Read both implementations completely
- [x] REQ-0.27.0-07-02: Document comparison: deletion safety (confirmation, dry-run), batch support, audit logging
- [x] REQ-0.27.0-07-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-07-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-07-05: If Confirm: document why receipt expungement is unnecessary
- [x] REQ-0.27.0-07-06: If Exclude: document why the module is environment-specific


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
