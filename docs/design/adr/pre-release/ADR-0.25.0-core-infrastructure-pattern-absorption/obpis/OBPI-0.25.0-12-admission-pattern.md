---
id: OBPI-0.25.0-12-admission-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 12
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-12: Admission Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-12 — "Evaluate and absorb core/admission.py (34 lines) — admission control patterns"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/admission.py` (34 lines) and
determine: Absorb (airlineops is better) or Exclude (domain-specific). The
airlineops module provides admission control and precondition validation.
gzkit currently has no dedicated admission control module, so the comparison
must determine whether this pattern is generic infrastructure or
airline-specific workflow logic.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/admission.py` (34 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Admission control is a governance primitive (Kubernetes-style) that likely belongs in gzkit

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Building a full admission controller framework beyond what airlineops provides

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

- [ ] REQ-0.25.0-12-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`.
- [ ] REQ-0.25.0-12-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-12-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-12-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit.
- [ ] REQ-0.25.0-12-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/admission.py
# Expected: airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-12-admission-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Comparison Analysis

### airlineops `core/admission.py` (34 lines)

A thin facade created during OBPI-0.1.8-23 that wraps
`airlineops.warehouse.ingest.config.cadence.closest_admitted`. Provides one
function:

- `resolve_effective_period(period, *, closest)` — returns the effective period
  token accounting for `--closest`. Only applies for YYYY-MM style monthly
  periods when `closest=True`. Falls back to the provided period on any error.

**Single import dependency:** `airlineops.warehouse.ingest.config.cadence` — the
warehouse ingestion cadence configuration module that defines which periods are
admitted for data loading.

Despite the generic-sounding module name "admission", this module has nothing to
do with Kubernetes-style admission control or generic precondition validation. It
is a period-token resolver for the airline data warehouse ingestion pipeline.

### gzkit equivalent: None

gzkit has no period resolution, cadence management, warehouse ingest, or data
loading concepts. There is no functional equivalent and no need for one — gzkit
is a governance toolkit, not a data pipeline.

### Comparison Summary

| Dimension | airlineops `core/admission.py` | gzkit |
|-----------|-------------------------------|-------|
| Domain | Airline data warehouse period resolution | Governance toolkit (no warehouse concepts) |
| Purpose | Resolve YYYY-MM period tokens to closest admitted period | N/A |
| Dependencies | `airlineops.warehouse.ingest.config.cadence` | N/A |
| Call sites | Warehouse data loading pipeline | N/A |
| Reuse potential | None — tightly coupled to airline cadence configuration | N/A |

## Decision: Exclude

**Rationale:** The airlineops `core/admission.py` module is a thin facade for
airline warehouse cadence resolution. The module name "admission" is misleading —
it does not implement generic admission control or precondition validation. It
wraps a single function from `airlineops.warehouse.ingest.config.cadence` to
resolve YYYY-MM period tokens to "closest admitted" periods during data warehouse
loads. This is pure airline-domain data pipeline infrastructure.

**Subtraction test:** `airlineops - gzkit = pure airline domain`. Period
resolution for warehouse data ingestion is exactly the kind of domain-specific
code that should remain in airlineops. gzkit has no warehouse, no cadence
configuration, and no period token concepts.

**Why not Absorb:** The module's single function depends on
`airlineops.warehouse.ingest.config.cadence` — a deep warehouse dependency that
cannot be imported without the entire airlineops warehouse dependency tree.
gzkit has no data warehouse, no period admission windows, and no cadence
configuration. Absorbing this module would introduce dead code with no consumer.

**Why not Confirm:** No gzkit equivalent exists, but the need (warehouse period
admission resolution) does not exist in gzkit either. "Confirm" implies gzkit
already covers the same concern — here, the concern itself is out of scope.

## Gate 4 (BDD): N/A

No operator-visible behavior changes. The Exclude decision means no code is
absorbed and no gzkit commands or surfaces are affected. No behavioral proof
is required.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (no absorption, existing tests remain green)
- [x] **Gate 3 (Docs):** Decision rationale completed
- [x] **Gate 4 (BDD):** N/A recorded with rationale (no operator-visible behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

### Value Narrative

Before this OBPI, it was unclear whether airlineops's `core/admission.py`
contained reusable admission control infrastructure that gzkit was missing. The
module name suggested Kubernetes-style admission control — a governance primitive
that could plausibly belong in gzkit. After reading the implementation, the
module is a 34-line facade for warehouse period-token resolution, tightly coupled
to airline cadence configuration. The Exclude decision confirms the subtraction
test holds: this is pure airline-domain data pipeline code with no governance
application.

### Key Proof


- Decision: Exclude
- airlineops core/admission.py: 34 lines, 1 function (resolve_effective_period)
- Single dependency: airlineops.warehouse.ingest.config.cadence
- gzkit equivalent: none (no warehouse, cadence, or period concepts exist)
- Module name admission is misleading — no generic admission control pattern present

### Implementation Summary


- Decision: Exclude — airlineops core/admission.py is a warehouse period-resolution facade with no governance application
- Source reviewed: airlineops core/admission.py (34 lines, 1 function resolve_effective_period)
- Dependency: imports from airlineops.warehouse.ingest.config.cadence — deep warehouse pipeline coupling
- gzkit equivalent: none — gzkit has no warehouse, cadence, or period concepts
- Files created: none
- Files modified: this brief only (comparison analysis, decision rationale, evidence)
- Tests added: none (no code changes for Exclude outcome)
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-10

## Closing Argument

The airlineops `core/admission.py` module provides a single-function facade for
resolving YYYY-MM period tokens via the warehouse cadence configuration. Despite
the generic-sounding module name "admission", the implementation is a 34-line
wrapper around `airlineops.warehouse.ingest.config.cadence.closest_admitted` with
no generic admission control semantics. gzkit has no warehouse, no cadence
configuration, and no period resolution needs. **Decision: Exclude** — this is
pure airline-domain data pipeline infrastructure that correctly remains in
airlineops.
