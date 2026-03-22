---
id: OBPI-0.26.0-07-adr-traceability
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-07: ADR Traceability

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-07 — "Evaluate and absorb lib/adr_traceability.py (277 lines) — ADR-to-artifact traceability chains"`

## OBJECTIVE

Evaluate `opsdev/lib/adr_traceability.py` (277 lines) against gzkit and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). gzkit has no equivalent module for ADR-to-artifact traceability. The opsdev module provides 277 lines of dedicated traceability chain construction — linking ADRs to their implementing artifacts (code, tests, docs) and verifying that every governance decision has traceable evidence. Traceability is a core governance primitive that underpins audit compliance.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/adr_traceability.py` (277 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Traceability chains (ADR -> OBPI -> code -> tests -> docs) are fundamental to governance auditing

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a generic dependency graph beyond ADR governance traceability

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
