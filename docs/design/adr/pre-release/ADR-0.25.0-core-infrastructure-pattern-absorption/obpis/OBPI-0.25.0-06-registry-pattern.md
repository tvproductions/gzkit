---
id: OBPI-0.25.0-06-registry-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-06: Registry Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-06 — "Evaluate and absorb core/registry.py (86 lines) — registry pattern implementation"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/registry.py` (86 lines) against gzkit's `registry.py` (217 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides a registry pattern with lookup facades. gzkit's equivalent is already 2.5x larger, suggesting gzkit may be more sophisticated — but the comparison must verify this.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/registry.py` (86 lines)
- **gzkit equivalent:** `src/gzkit/registry.py` (217 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's larger implementation may already subsume airlineops's capabilities

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Merging registry patterns if they serve fundamentally different purposes

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
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

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

- [ ] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.25.0-06-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-06-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-06-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-06-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-06-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/registry.py
# Expected: airlineops source under review exists

test -f src/gzkit/registry.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-06-registry-pattern.md
# Expected: completed brief records one final decision

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
