---
id: OBPI-0.25.0-33-arb-analysis-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 33
status: Pending
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-33: ARB Analysis Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-33 — "Evaluate and absorb opsdev/arb/ (603 lines total) — receipt advise, validate, and pattern extraction"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/arb/` (603 lines total across multiple files)
against gzkit's ARB analysis surface and determine: Absorb, Confirm, or
Exclude. The airlineops package covers receipt advise, validate, and pattern
extraction. gzkit's equivalent surface spans `commands/closeout_ceremony.py`
(579 lines), `commands/obpi_complete.py` (648 lines), `instruction_eval.py`
(465 lines), and `instruction_audit.py` (319 lines) — approximately 2000+
lines across 4+ modules providing step-driven receipt validation, OBPI
completion with evidence gathering, and instruction evaluation with pattern
extraction.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/arb/` (603 lines total)
- **gzkit equivalent:** Distributed across `src/gzkit/commands/closeout_ceremony.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/instruction_eval.py`, `src/gzkit/instruction_audit.py` (~2000+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 3x larger surface suggests more mature ARB handling — comparison will verify
- The airlineops ARB package may have multiple files — all must be read for complete comparison

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's ARB/receipt architecture around airlineops's package layout

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

- [ ] REQ-0.25.0-33-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-33-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-33-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-33-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-33-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -d ../airlineops/src/opsdev/arb
# Expected: airlineops source package under review exists

test -f src/gzkit/commands/closeout_ceremony.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-33-arb-analysis-pattern.md
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
