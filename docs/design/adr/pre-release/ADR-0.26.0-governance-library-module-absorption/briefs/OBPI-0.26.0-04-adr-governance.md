---
id: OBPI-0.26.0-04-adr-governance
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-04: ADR Governance

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-04 — "Evaluate and absorb lib/adr_governance.py (535 lines) — ADR governance policy enforcement"`

## OBJECTIVE

Evaluate `opsdev/lib/adr_governance.py` (535 lines) against gzkit's partial governance enforcement in `ledger.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides 535 lines of dedicated governance policy enforcement — lane determination, gate validation, attestation requirements, and compliance checks. gzkit has partial coverage in ledger.py, but the comparison must determine whether gzkit's ledger-centric approach adequately covers the governance policy enforcement patterns that opsdev implements as a dedicated library.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/adr_governance.py` (535 lines)
- **gzkit equivalent:** Partial in `src/gzkit/ledger.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Governance policy enforcement is a core governance primitive that belongs in gzkit
- gzkit's ledger.py may embed some governance enforcement but likely lacks the breadth of a dedicated 535-line governance module

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing ledger infrastructure if it is already sufficient for its own purposes

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient despite the dedicated module gap
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
