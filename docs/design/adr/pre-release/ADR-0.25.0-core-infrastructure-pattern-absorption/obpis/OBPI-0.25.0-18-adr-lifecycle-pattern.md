---
id: OBPI-0.25.0-18-adr-lifecycle-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 18
status: Pending
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-18: ADR Lifecycle Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-18 — "Evaluate and absorb opsdev/lib/adr.py (1603 lines) — ADR index generation, status tables, title normalization"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/adr.py` (1603 lines) against gzkit's ADR
lifecycle surface and determine: Absorb (airlineops has reusable patterns gzkit
lacks), Confirm (gzkit already covers this domain), or Exclude (domain-specific,
does not belong in gzkit). The airlineops module covers ADR index generation,
status tables, and title normalization. gzkit's equivalent surface spans
`registry.py` (220 lines), `sync.py` (361 lines), `commands/register.py`
(400 lines), and `core/models.py` (338 lines) — approximately 1300+ lines
across 4+ modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/adr.py` (1603 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/registry.py`, `src/gzkit/sync.py`, `src/gzkit/commands/register.py`, `src/gzkit/core/models.py` (~1300+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap — most will yield Absorb or Confirm rather than Exclude

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's ADR lifecycle around airlineops's monolithic module

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

- [ ] REQ-0.25.0-18-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-18-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-18-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-18-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-18-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr.py
# Expected: airlineops source under review exists

test -f src/gzkit/registry.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-18-adr-lifecycle-pattern.md
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
