---
id: OBPI-0.26.0-11-artifacts-lib
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-11: Artifacts Library

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-11 — "Evaluate and absorb lib/artifacts.py (232 lines) — artifact management and sync primitives"`

## OBJECTIVE

Evaluate `opsdev/lib/artifacts.py` (232 lines) against gzkit's partial artifact management in `sync.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides 232 lines of dedicated artifact management — discovery, cataloging, integrity verification, and sync primitives for governance artifacts (receipts, schemas, manifests). gzkit has partial coverage in sync.py, but the comparison must determine whether gzkit's sync-focused approach covers the full artifact lifecycle that opsdev's dedicated library addresses.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/artifacts.py` (232 lines)
- **gzkit equivalent:** Partial in `src/gzkit/sync.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Artifact management (discovery, cataloging, integrity) is a governance primitive that belongs in gzkit
- gzkit's sync.py may handle artifact sync but may lack discovery and integrity verification depth

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing sync infrastructure — the goal is enriching artifact management capabilities

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
