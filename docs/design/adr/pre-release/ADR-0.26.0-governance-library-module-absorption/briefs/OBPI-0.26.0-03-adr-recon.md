---
id: OBPI-0.26.0-03-adr-recon
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-03: ADR Reconciliation

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-03 — "Evaluate and absorb lib/adr_recon.py (607 lines) — ADR reconciliation and consistency checking"`

## OBJECTIVE

Evaluate `opsdev/lib/adr_recon.py` (607 lines) against gzkit and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). gzkit has no equivalent module for ADR reconciliation and consistency checking. The opsdev module provides 607 lines of dedicated reconciliation logic — verifying that ADR metadata, OBPI briefs, ledger entries, and filesystem artifacts are mutually consistent. This is a critical governance primitive for detecting configuration drift and ensuring governance integrity.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/adr_recon.py` (607 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Reconciliation is fundamental to governance integrity and is domain-agnostic

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building reconciliation for non-governance artifacts (e.g., business data reconciliation)

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
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
