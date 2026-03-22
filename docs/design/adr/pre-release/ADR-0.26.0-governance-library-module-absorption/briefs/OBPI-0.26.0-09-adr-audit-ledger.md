---
id: OBPI-0.26.0-09-adr-audit-ledger
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-09: ADR Audit Ledger

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-09 — "Evaluate and absorb lib/adr_audit_ledger.py (249 lines) — audit ledger for ADR lifecycle events"`

## OBJECTIVE

Evaluate `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). gzkit has
no equivalent module for a dedicated ADR audit ledger. The opsdev module
provides ADR-specific audit-ledger management for recording lifecycle events in
a structured append-only trail, making this a strong absorption candidate
unless the logic is ops-specific.

## SOURCE MATERIAL

- **opsdev:** `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- ADR audit trails are a governance primitive — every governance framework needs lifecycle event recording
- This module likely layers on top of the general ledger, adding ADR-specific event types and query patterns

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing ledger infrastructure — this adds ADR-specific audit semantics

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

- [ ] REQ-0.26.0-09-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`.
- [ ] REQ-0.26.0-09-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between opsdev and gzkit.
- [ ] REQ-0.26.0-09-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.26.0-09-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is ops-specific or otherwise not fit for gzkit.
- [ ] REQ-0.26.0-09-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr_audit_ledger.py
# Expected: opsdev source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-09-adr-audit-ledger.md
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
