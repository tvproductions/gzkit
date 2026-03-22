---
id: OBPI-0.26.0-06-drift-detection
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-06: Drift Detection

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-06 — "Evaluate and absorb lib/drift_detection.py (384 lines) — governance drift detection and alerting"`

## OBJECTIVE

Evaluate `opsdev/lib/drift_detection.py` (384 lines) against gzkit and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). gzkit has no equivalent module for governance drift detection. The opsdev module provides 384 lines of dedicated drift detection — comparing declared governance state against actual filesystem/artifact state, identifying discrepancies, and generating structured drift reports. Drift detection is a critical governance primitive for maintaining integrity between what governance documents claim and what actually exists.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/drift_detection.py` (384 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Drift detection is fundamental to governance integrity — if governance documents say X exists but it doesn't, that's a governance failure

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building real-time drift monitoring or alerting infrastructure beyond detection

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
