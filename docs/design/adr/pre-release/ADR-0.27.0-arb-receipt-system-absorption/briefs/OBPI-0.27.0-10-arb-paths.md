---
id: OBPI-0.27.0-10-arb-paths
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-10: ARB Paths

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-10 — "Evaluate and absorb arb/paths.py (43 lines) — ARB path resolution and directory layout"`

## OBJECTIVE

Evaluate `opsdev/arb/paths.py` (43 lines) against gzkit's current path resolution patterns and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing path resolution is sufficient), or Exclude (environment-specific). The opsdev module centralizes ARB directory layout: receipt storage paths, schema paths, archive paths, and directory creation. gzkit currently has path resolution in `config.py` and scattered across modules. The comparison must determine whether a dedicated ARB paths module provides cleaner architecture than integrating ARB paths into gzkit's existing path resolution.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/paths.py` (43 lines)
- **gzkit equivalent:** Path resolution in `src/gzkit/config.py` and module-level constants

## ASSUMPTIONS

- The governance value question governs: does a dedicated paths module improve architecture over inline path constants?
- At 43 lines, this is the smallest ARB module — likely a utility that other modules depend on
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- This module is foundational — if the receipt system is adopted, paths must be resolved somewhere

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Redesigning gzkit's entire path resolution strategy — scope is ARB-specific paths

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: path resolution strategy, directory creation, cross-platform safety
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's existing path resolution is sufficient
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
