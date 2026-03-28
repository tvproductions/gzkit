---
id: OBPI-0.25.0-14-os-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 14
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-14: OS Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-14 — "Evaluate and absorb common/os.py (241 lines) — cross-platform file operations"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/common/os.py` (241 lines) and determine:
Absorb (airlineops is better) or Exclude (domain-specific). The airlineops
module provides cross-platform file operations, path normalization, and OS
abstraction. gzkit currently has no dedicated OS abstraction module, only a
cross-platform development policy rule. The comparison must determine whether
airlineops's battle-tested OS utilities should become a gzkit module that
enforces the cross-platform policy in code.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/common/os.py` (241 lines)
- **gzkit equivalent:** Cross-platform rule only (`.claude/rules/cross-platform.md`)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit code equivalent means either Absorb or Exclude — there is no Confirm path
- Cross-platform OS utilities are definitively generic infrastructure

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Replacing Python's pathlib — the module should augment it with project-specific utilities

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, new gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Exclude` decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the absorbed pattern changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.25.0-14-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`.
- [ ] REQ-0.25.0-14-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-14-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-14-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit.
- [ ] REQ-0.25.0-14-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/common/os.py
# Expected: airlineops source under review exists

test -f .claude/rules/cross-platform.md
# Expected: current gzkit comparison doctrine exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-14-os-pattern.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-14-os-pattern.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Decision rationale completed
- [ ] **Gate 4 (BDD):** Behavioral proof present or `N/A` recorded with rationale
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

*To be authored at completion from delivered evidence.*
