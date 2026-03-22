---
id: OBPI-0.26.0-01-adr-management
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-01: ADR Management

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-01 — "Evaluate and absorb lib/adr.py (1,588 lines) — ADR management primitives"`

## OBJECTIVE

Evaluate `opsdev/lib/adr.py` (1,588 lines) against gzkit's partial ADR management in `cli.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module is the largest in the library at 1,588 lines, providing comprehensive ADR lifecycle management including creation, status transitions, validation, and querying. gzkit's current equivalent is partial coverage scattered across cli.py, which mixes ADR management logic with CLI command handling. The 1,588-line dedicated module almost certainly contains governance depth that a monolithic CLI file does not replicate.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/adr.py` (1,588 lines)
- **gzkit equivalent:** Partial in `src/gzkit/cli.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- A 1,588-line dedicated ADR management library almost certainly surpasses partial coverage in a monolithic CLI file — the comparison must be brutally honest about this gap
- Separating ADR management into a dedicated library module is architecturally superior to embedding it in CLI command handling

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying the existing `gz adr` CLI command contract without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient despite the massive line-count gap
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
