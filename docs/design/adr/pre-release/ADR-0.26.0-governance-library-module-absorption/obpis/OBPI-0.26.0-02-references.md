---
id: OBPI-0.26.0-02-references
parent: ADR-0.26.0-governance-library-module-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-02: References

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-02 — "Evaluate and absorb lib/references.py (797 lines) — cross-reference resolution and link management"`

## OBJECTIVE

Evaluate `../airlineops/src/opsdev/lib/references.py` (797 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). gzkit has
no equivalent module for cross-reference resolution and link management. The
opsdev module provides dedicated reference tracking for resolving links between
ADRs, OBPIs, artifacts, and governance documents, making this a strong
absorption candidate unless the logic is ops-specific.

## SOURCE MATERIAL

- **opsdev:** `../airlineops/src/opsdev/lib/references.py` (797 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Cross-reference resolution is a domain-agnostic governance primitive that any governance framework needs

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a generic link-resolution framework beyond governance needs

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Exclude` decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior, the brief names
  `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.26.0-02-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`.
- [ ] REQ-0.26.0-02-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between opsdev and gzkit.
- [ ] REQ-0.26.0-02-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.26.0-02-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is ops-specific or otherwise not fit for gzkit.
- [ ] REQ-0.26.0-02-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/references.py
# Expected: opsdev source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-02-references.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-02-references.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-02-references.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Decision rationale completed
- [ ] **Gate 4 (BDD):** Behavioral proof present or `N/A` recorded with rationale
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

*To be authored at completion from delivered evidence.*
