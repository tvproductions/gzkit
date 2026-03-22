---
id: OBPI-0.26.0-05-ledger-schema
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-05: Ledger Schema

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-05 — "Evaluate and absorb lib/ledger_schema.py (501 lines) — ledger schema definitions and validation"`

## OBJECTIVE

Evaluate `opsdev/lib/ledger_schema.py` (501 lines) against gzkit's partial ledger schema in `ledger.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides 501 lines of dedicated ledger schema definitions and validation — schema versioning, entry type definitions, migration logic, and structural validation. gzkit has partial coverage in ledger.py, but the comparison must determine whether gzkit's inline schema handling adequately covers what opsdev implements as a dedicated schema library with versioning and migration support.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/ledger_schema.py` (501 lines)
- **gzkit equivalent:** Partial in `src/gzkit/ledger.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Ledger schema management (versioning, migration, validation) is a governance primitive that belongs in gzkit
- gzkit's ledger.py likely handles schema inline without the versioning and migration depth that a dedicated 501-line module provides

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing ledger module — the goal is enriching schema capabilities

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient despite lacking dedicated schema management
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
