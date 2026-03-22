---
id: OBPI-0.26.0-12-docs-lib
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-12: Documentation Library

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-12 — "Evaluate and absorb lib/docs.py (218 lines) — documentation generation and validation"`

## OBJECTIVE

Evaluate `opsdev/lib/docs.py` (218 lines) against gzkit and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). gzkit has no equivalent module for documentation generation and validation. The opsdev module provides 218 lines of dedicated documentation library capabilities — generating governance documentation from structured data, validating documentation completeness against governance requirements, and ensuring documentation tracks behavior changes. This aligns with gzkit's Gate 5 runbook-code covenant requirement that documentation is a first-class deliverable.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/docs.py` (218 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Documentation generation and validation is a governance primitive that aligns with gzkit's documentation-as-first-class-deliverable principle

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a general-purpose documentation framework — focus on governance documentation

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
