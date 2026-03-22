---
id: OBPI-0.26.0-10-cli-audit-lib
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-10: CLI Audit Library

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-10 — "Evaluate and absorb lib/cli_audit.py (238 lines) — CLI audit infrastructure and contract verification"`

## OBJECTIVE

Evaluate `opsdev/lib/cli_audit.py` (238 lines) against gzkit's partial CLI audit in `cli.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides 238 lines of dedicated CLI audit infrastructure — verifying CLI command contracts, checking help text compliance, validating exit codes, and auditing flag conventions. gzkit has partial coverage in cli.py via `gz cli audit`, but the comparison must determine whether gzkit's inline approach matches the depth of opsdev's dedicated CLI audit library.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/cli_audit.py` (238 lines)
- **gzkit equivalent:** Partial in `src/gzkit/cli.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- CLI audit infrastructure is domain-agnostic — any CLI framework benefits from contract verification
- gzkit's cli.py likely mixes CLI audit logic with command handling rather than providing a reusable audit library

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying the existing `gz cli audit` command contract without Heavy lane approval

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
