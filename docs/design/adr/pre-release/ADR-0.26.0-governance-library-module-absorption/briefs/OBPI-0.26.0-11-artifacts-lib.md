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

Evaluate `../airlineops/src/opsdev/lib/artifacts.py` (232 lines) against
gzkit's partial artifact management in `src/gzkit/sync.py` and determine:
Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude
(domain-specific). The opsdev module provides dedicated artifact management for
discovery, cataloging, integrity verification, and sync primitives for
governance artifacts. gzkit has partial coverage in `src/gzkit/sync.py`, but
the comparison must determine whether gzkit's sync-focused approach covers the
full artifact lifecycle that opsdev's dedicated library addresses.

## SOURCE MATERIAL

- **opsdev:** `../airlineops/src/opsdev/lib/artifacts.py` (232 lines)
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

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior, the brief names
  `features/governance_library.feature` or equivalent module-level behavioral
  proof
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.26.0-11-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.26.0-11-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between opsdev and gzkit.
- [ ] REQ-0.26.0-11-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.26.0-11-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.26.0-11-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/artifacts.py
# Expected: opsdev source under review exists

test -f src/gzkit/sync.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-11-artifacts-lib.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-11-artifacts-lib.md
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
