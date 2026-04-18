---
id: OBPI-0.25.0-22-adr-traceability-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 22
status: attested_completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-22: ADR Traceability Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-22 — "Evaluate and absorb opsdev/lib/adr_traceability.py (277 lines) — ADR-to-artifact relationship inference"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/adr_traceability.py` (277 lines) against
gzkit's traceability surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers ADR-to-artifact relationship inference. gzkit's
equivalent surface spans `triangle.py` (372 lines) and `traceability.py`
(418 lines) — approximately 790+ lines across 2 modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/adr_traceability.py` (277 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/triangle.py`, `src/gzkit/traceability.py` (~790+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's traceability engine around airlineops's approach

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

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Comparison

### airlineops `adr_traceability.py` (277 lines)

| Function | Lines | Assessment |
|----------|-------|-----------|
| `load_adrs()` | 143-176 | ADR file scanning with keyword/title extraction; gzkit uses `scan_briefs()` for structured REQ extraction from OBPI briefs — different granularity |
| `collect_artifacts()` | 187-215 | Filesystem walk for `.feature`/`.py` files, reads first 25-40 lines as text; gzkit uses `scan_test_tree()` with AST parsing — more precise |
| `infer()` | 244-257 | Heuristic keyword-match scoring with threshold (>=0.4); gzkit uses declarative `@covers` decorators — explicit vs fuzzy |
| `generate_text_report()` | 260-277 | Plain-text score report; gzkit uses `compute_coverage()` producing structured `CoverageReport` with per-ADR/OBPI/REQ rollups |
| `_score_artifact()` | 218-241 | Keyword coverage (capped 0.7) + slug/phrase/domain bonuses; contains airline-specific domain bonuses (econ, ops, market, qsi, gravity, shares, turnaround, utilization) — fails subtraction test |
| `ADR`/`Artifact`/`Scored` dataclasses | 83-112 | stdlib `dataclass`; violates gzkit Pydantic `BaseModel` policy |
| Module-level path resolution | 29-36 | Hardcoded `Path(__file__).parents[3]` + `airlineops.paths.subpaths` import — airlineops-specific, non-portable |

### gzkit traceability surface

| Module | Lines | Capabilities |
|--------|-------|-------------|
| `src/gzkit/triangle.py` | 372 | REQ entity model (Pydantic), triangle vertex/edge types, `scan_briefs()` for REQ extraction, `detect_drift()` for spec-test-code drift detection |
| `src/gzkit/traceability.py` | 418 | `@covers` decorator for test-to-REQ linkage, AST-based `scan_test_tree()`, `compute_coverage()` with multi-level rollups |
| `gz-adr-map` skill | workflow | ADR-to-artifact traceability via `gz state --json` + `gz adr audit-check` |
| `gz state` / `gz adr audit-check` CLI | commands | Workflow-driven ADR-to-artifact mapping with governance ledger awareness |

### Capability Comparison

| Dimension | airlineops | gzkit | Winner |
|-----------|-----------|-------|--------|
| Traceability approach | Heuristic keyword inference (fuzzy) | Declarative `@covers` annotations (precise) | gzkit |
| ADR-to-artifact mapping | `infer()` with score thresholds | `gz-adr-map` skill + `gz state --json` | gzkit (governance-aware) |
| Coverage measurement | Sum of heuristic scores | `compute_coverage()` with per-REQ/OBPI/ADR rollups | gzkit |
| Test discovery | Filesystem walk, text head sampling (25-40 lines) | AST-based `scan_test_tree()`, static analysis | gzkit |
| Drift detection | Not present | `detect_drift()` — unlinked specs, orphan tests, unjustified code changes | gzkit |
| Domain specificity | Airline bonuses (econ, ops, market, qsi, gravity, shares) | Domain-neutral | gzkit (passes subtraction test) |
| Data model | stdlib `dataclass` | Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` | gzkit |
| Path resolution | Hardcoded `Path(__file__).parents[3]` + `airlineops.paths.subpaths` | Config-aware `_find_project_root()` via `.gzkit/` marker | gzkit |

## Decision: Confirm

gzkit's existing traceability surface is architecturally superior and already covers all functional capabilities provided by airlineops `adr_traceability.py`. No absorption is warranted.

**Rationale:**

1. **Declarative vs heuristic:** gzkit's `@covers` decorator provides auditable, precise test-to-requirement linkage. airlineops's `infer()` produces fuzzy confidence scores via keyword matching — unsuitable for governance compliance where false positives are costly.
2. **Coverage depth:** gzkit's `compute_coverage()` produces structured `CoverageReport` with per-REQ, per-OBPI, and per-ADR rollups. airlineops sums heuristic scores with no structured breakdown.
3. **Drift detection:** gzkit has `detect_drift()` that identifies unlinked specs, orphan tests, and unjustified code changes. airlineops has no equivalent capability.
4. **Domain bonuses fail subtraction test:** `_score_artifact()` lines 235-241 contain airline-specific domain terms (`econ`, `economics`, `doctrine`, `ops`, `operations`, `turnaround`, `utilization`, `market`, `qsi`, `gravity`, `shares`). Removing these would reduce the module to generic keyword matching with no advantage over gzkit's declarative approach.
5. **AST precision:** gzkit's `scan_test_tree()` uses static AST analysis to discover `@covers` annotations without importing or executing test files. airlineops's `collect_artifacts()` reads first 25-40 lines of file text — coarse and brittle.
6. **Convention compliance:** airlineops uses stdlib `dataclass` (ADR, Artifact, Scored); gzkit uses Pydantic `BaseModel` with validation, immutability, and serialization throughout — consistent with the project's data model policy.

### Gate 4 (BDD): N/A

No operator-visible behavior change. This is a Confirm decision — no code was added, removed, or modified. The existing traceability infrastructure continues to function identically.

## Acceptance Criteria

- [x] REQ-0.25.0-22-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-22-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [x] REQ-0.25.0-22-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [x] REQ-0.25.0-22-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [x] REQ-0.25.0-22-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr_traceability.py
# Expected: airlineops source under review exists

test -f src/gzkit/traceability.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-22-adr-traceability-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (no code changes — Confirm decision)
- [x] **Gate 3 (Docs):** Decision rationale completed with side-by-side comparison
- [x] **Gate 4 (BDD):** N/A — Confirm decision, no operator-visible behavior change
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

gzkit's traceability surface (`triangle.py` at 372 lines and `traceability.py` at 418 lines — 790+ lines total) surpasses airlineops's heuristic inference module (`adr_traceability.py` at 277 lines) on every governance-relevant dimension. The `@covers` decorator provides auditable, precise test-to-REQ linkage; `compute_coverage()` delivers structured multi-level rollups at REQ, OBPI, and ADR levels; `detect_drift()` catches unlinked specs and orphan tests proactively. The airlineops module's unique capability — heuristic keyword scoring — produces fuzzy confidence values unsuitable for governance compliance, and its domain-specific bonuses (`econ`, `ops`, `market`, `qsi`, `gravity`, `shares`) fail the subtraction test. gzkit's `gz-adr-map` skill and `gz state --json` command provide governance-aware ADR-to-artifact mapping through the central ledger, replacing the need for heuristic inference. No absorption is warranted; gzkit's implementation is the stronger pattern.

### Implementation Summary


- **Decision:** Confirm — gzkit's existing traceability surface is sufficient
- **Patterns evaluated:** 7 airlineops `adr_traceability.py` functions (277 lines)
- **gzkit equivalents:** `triangle.py` (372 lines) + `traceability.py` (418 lines) + `gz-adr-map` skill + `gz state`/`gz adr audit-check` commands
- **Traceability approach:** gzkit uses declarative `@covers`; airlineops uses heuristic keyword inference
- **Domain specificity:** airlineops contains airline-domain scoring bonuses that fail subtraction test
- **Code changes:** None — Confirm decision, no absorption warranted

### Key Proof


```bash
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-22-adr-traceability-pattern.md
# Expected: "## Decision: Confirm"
```

### Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-11
- Attestation: attest completed
