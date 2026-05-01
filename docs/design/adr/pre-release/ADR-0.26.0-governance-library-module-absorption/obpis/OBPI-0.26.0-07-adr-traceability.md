---
id: OBPI-0.26.0-07-adr-traceability
parent: ADR-0.26.0-governance-library-module-absorption
item: 7
status: Completed
lane: heavy
date: 2026-03-21
decision: Confirm
paired_with: OBPI-0.25.0-22-adr-traceability-pattern
---

# OBPI-0.26.0-07: ADR Traceability

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-07 — "Evaluate and absorb lib/adr_traceability.py (277 lines) — ADR-to-artifact traceability chains"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/adr_traceability.py` (277 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). gzkit has
no equivalent module for ADR-to-artifact traceability. The opsdev module
provides dedicated traceability-chain construction linking ADRs to their
implementing artifacts, making this a strong absorption candidate unless the
logic is ops-specific.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/adr_traceability.py` (277 lines)
- **gzkit equivalent:** None (per parent-ADR Tidy First Plan table). Body-level
  observation in `## Comparison`: gzkit ships `src/gzkit/traceability.py`
  (418 L) + `src/gzkit/triangle.py` (372 L) + `tests/test_traceability.py` —
  evaluated and decided **Confirm** under
  OBPI-0.25.0-22-adr-traceability-pattern (attested 2026-04-09). Parent-ADR
  header is intentionally not amended (mirror of OBPI-0.26.0-04 / -05 / -06
  pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any decision binds future
governance-library absorption work. The brief frontmatter records a doctrine
choice (Confirm-by-reference to OBPI-0.25.0-22) that future agents will treat
as canonical, so Heavy scrutiny applies even though no code changes under
this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- ~~No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path~~ — **brief-scaffold defect**: gzkit has a superior existing equivalent (`traceability.py` + `triangle.py`); the canonical OBPI-0.25.0-22 evaluated this exact source artifact and decided Confirm; the precedent (also surfaced under OBPI-0.26.0-04, attested) establishes that `decision: Confirm` is the structurally correct verdict despite this assumption. The defect class is the third instance across ADR-0.26.0 briefs (also present in OBPI-06 wording); tracked under GHI #376 as part of the duplicate-OBPI surface.
- Traceability chains (ADR -> OBPI -> code -> tests -> docs) are fundamental to governance auditing
- The actual gzkit comparison surface for opsdev `lib/adr_traceability.py` is
  the `src/gzkit/traceability.py` + `src/gzkit/triangle.py` pair plus
  `tests/test_traceability.py`, already evaluated and confirmed superior
  under OBPI-0.25.0-22 — recorded in `## Comparison` body section
  (parent-ADR-authored Source Material header not amended)

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a generic dependency graph beyond ADR governance traceability
- Re-running the comparison work already attested under
  OBPI-0.25.0-22-adr-traceability-pattern (2026-04-09) on identical source
  material — divergent rationale on identical material is itself a
  doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude (Confirm permitted by precedent despite stale brief Assumption — see above).
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's existing module is superior.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/`
  for a Confirm-by-reference outcome (the existing module was already
  evaluated as superior under OBPI-0.25.0-22; this brief introduces no new
  code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a
  governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — understand the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-04-adr-governance brief (Completed) — Confirm-by-reference structural precedent that established `decision: Confirm` is accepted by the validator despite the brief Assumptions' "no Confirm path" wording
- [x] Sibling OBPI-0.26.0-06-drift-detection brief (Completed 2026-05-01) — same-day Absorb-by-reference sibling that confirmed the in-flight scaffold-drift correction recipe (ALL-CAPS → title case, Lane/Denied Paths/Discovery Checklist additions)
- [x] OBPI-0.25.0-22-adr-traceability-pattern brief (attested 2026-04-09) — canonical precedent for the same source-module evaluation; recorded **Decision: Confirm** with six-point rationale anchored on declarative-vs-heuristic, coverage depth, drift detection, domain-bonus subtraction-test failure, AST precision, and convention compliance
- [x] `src/gzkit/schemas/obpi.json` — required headers contract (validator caught ALL-CAPS heading drift; corrected to title case)
- [x] GHI #376 (open) — duplicate-OBPI tracking surface; this brief is the fourth structural instance of the same defect for `lib/adr_traceability.py`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/adr_traceability.py` (277 lines) — opsdev source under review
- [x] Required path exists: `src/gzkit/traceability.py` (418 lines) — gzkit `@covers` + linkage scanner + coverage computation
- [x] Required path exists: `src/gzkit/triangle.py` (372 lines) — gzkit REQ entity model, triangle vertex/edge types, `scan_briefs()`, `detect_drift()`
- [x] Required path exists: `tests/test_traceability.py` — test coverage for the gzkit traceability surface
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `adr_traceability.py` reviewed: anticipates "Strong absorption candidate unless traceability semantics are ops-specific"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/adr_traceability.py` structure confirmed at lines 29-36 (module-level path resolution — `Path(__file__).parents[3]` + `airlineops.paths.subpaths` — airlineops-specific, non-portable), 83-112 (`ADR`/`Artifact`/`Scored` stdlib dataclasses — violates gzkit Pydantic policy), 143-176 (`load_adrs()` ADR file scanning), 187-215 (`collect_artifacts()` filesystem walk reading first 25-40 lines as text — coarse), 218-241 (`_score_artifact()` keyword coverage + airline-specific domain bonuses: `econ`, `economics`, `doctrine`, `ops`, `operations`, `turnaround`, `utilization`, `market`, `qsi`, `gravity`, `shares` — fails subtraction test), 244-257 (`infer()` heuristic keyword-match scoring with >=0.4 threshold — fuzzy, false-positive-prone), 260-277 (`generate_text_report()` plain-text score report)
- [x] `src/gzkit/traceability.py` structure confirmed: `@covers` decorator (precise test-to-REQ linkage), AST-based `scan_test_tree()` (static analysis without import/execute), `compute_coverage()` (structured `CoverageReport` with per-REQ/OBPI/ADR rollups), Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` throughout
- [x] `src/gzkit/triangle.py` structure confirmed: `ReqId`/`ReqEntity`/`DiscoveredReq` models, `VertexType`/`EdgeType`/`VertexRef`/`LinkageRecord` (covers/proves/justifies edges), `scan_briefs()` (walks `docs/design/adr/`, parses YAML frontmatter, extracts checkbox-state REQ entities), `detect_drift()` pure function (unlinked specs, orphan tests, unjustified code changes)
- [x] `tests/test_traceability.py` confirmed via `tests/test_feature_decisions.py:12`, `tests/test_flag_models.py:16`, `tests/test_traceability.py:13,342,356` — `from gzkit.traceability import covers` is a project-wide import surface
- [x] Duplicate-OBPI surface check: same source module `lib/adr_traceability.py` evaluated under both ADR-0.25.0/OBPI-22 (Confirm, attested 2026-04-09) and ADR-0.26.0/OBPI-07 (this brief) — defect tracked under **GHI #376** (will be extended via fourth-instance comment in Stage 5)

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-07-adr-traceability` (vacuous parity-gate pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`; covered by `gz covers` parity gate)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **N/A**, Confirm outcome; existing `traceability.py` + `triangle.py` + `tests/test_traceability.py` already constitute the superior surface (per OBPI-0.25.0-22 precedent)

### Gate 3: Docs

- [x] Completed brief records a final `Confirm` decision (frontmatter `decision: Confirm` + `## Decision` body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (eight-dimension table from OBPI-0.25.0-22 precedent + seven-point Decision rationale + duplicate-OBPI tracking)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-07-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb` or `Exclude` (or `Confirm` per the
  OBPI-0.25.0-22 / OBPI-0.26.0-04 precedent that supersedes the brief
  Assumptions' stale "no Confirm path" wording). **Decision: Confirm** —
  see frontmatter and `## Decision` below.
- [x] REQ-0.26.0-07-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (eight-dimension capability table) and
  `## Decision` (seven-point rationale anchored on OBPI-0.25.0-22).
- [x] REQ-0.26.0-07-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests needed to carry the pattern safely.
  **N/A — Confirm outcome.** This REQ is vacuously satisfied.
- [x] REQ-0.26.0-07-04: [doc] Given an `Exclude` (or `Confirm`) outcome,
  then the brief explains why the pattern is ops-specific or otherwise not
  fit for gzkit (or why gzkit's existing implementation is superior). See
  `## Decision` — gzkit's `@covers`+AST architecture is materially superior
  to opsdev's heuristic keyword inference on six dimensions, plus opsdev's
  `_score_artifact` carries airline-specific domain bonuses that fail the
  subtraction test.
- [x] REQ-0.26.0-07-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Confirm outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change —
  nothing operator-visible changes under this brief.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/adr_traceability.py
# Expected: opsdev source under review exists

test -f src/gzkit/traceability.py && test -f src/gzkit/triangle.py
# Expected: gzkit existing modules exist (confirmed superior under OBPI-0.25.0-22)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: brief frontmatter and Decision body record the Confirm verdict
# (OBPI-0.26.0-07-specific verification command)

rg -n 'OBPI-0.25.0-22' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: brief cites the canonical precedent in body and Closing Argument
# (OBPI-0.26.0-07-specific verification command)

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-07-adr-traceability
# Expected: OBPI-scoped tests remain green (vacuous pass on [doc] REQ pattern via _synthesize_doc_proof_linkage)

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: completed brief captures Gate 4 N/A rationale
```

## Comparison

### Source-material observation

The brief Source Material header at line 31 of the parent-ADR-authored
scaffold names "gzkit equivalent: None" — mirroring the parent ADR's Tidy
First Plan table at `ADR-0.26.0-...md:32`. That assertion is stale at
authoring time: gzkit ships `src/gzkit/traceability.py` (418 L) +
`src/gzkit/triangle.py` (372 L), evaluated as **architecturally superior** to
opsdev's `lib/adr_traceability.py` under
**OBPI-0.25.0-22-adr-traceability-pattern** (attested 2026-04-09).

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/adr_traceability.py` | 277 | opsdev module: heuristic keyword-match `infer()`, stdlib `dataclass` models, airline-specific domain bonuses |
| `src/gzkit/traceability.py` | 418 | gzkit `@covers` decorator + AST-based `scan_test_tree()` + `compute_coverage()` with structured `CoverageReport` |
| `src/gzkit/triangle.py` | 372 | gzkit REQ entity model, triangle vertex/edge types, `scan_briefs()`, pure `detect_drift()` |
| `tests/test_traceability.py` | (multi-class) | Test coverage exercising decorator + scanner + coverage computation |

This observation is body-level (Comparison section); the parent-ADR-authored
Source Material header is intentionally not amended (mirror of the
OBPI-0.26.0-04 / -05 / -06 pattern).

### Per-dimension comparison (re-anchored from OBPI-0.25.0-22 precedent)

The eight-dimension capability table established by
OBPI-0.25.0-22-adr-traceability-pattern (2026-04-09, attested) holds for the
gzkit/opsdev capability shape because the source artifact is identical
(`lib/adr_traceability.py`, 277 lines) and the gzkit surface in
`traceability.py` + `triangle.py` preserves the
declarative-decorator-plus-AST-scanner architecture. Line anchors are
refreshed to the current files; capability deltas are noted inline.

| Dimension | opsdev `lib/adr_traceability.py` (277 L) | gzkit `traceability.py` + `triangle.py` (790 L) | Winner |
|-----------|------------------------------------------|--------------------------------------------------|--------|
| Traceability approach | Heuristic keyword inference (`infer()` at lines 244-257; threshold ≥0.4; fuzzy) | Declarative `@covers("REQ-X.Y.Z-NN-MM")` annotations (precise; auditable) | gzkit |
| ADR-to-artifact mapping | `infer()` with score thresholds; `_score_artifact()` keyword coverage capped at 0.7 + slug/phrase/domain bonuses | `gz-adr-map` skill + `gz state --json` workflow with governance-ledger awareness | gzkit (governance-aware) |
| Coverage measurement | Sum of heuristic scores via `generate_text_report()` (lines 260-277); plain-text output | `compute_coverage()` producing structured `CoverageReport` with per-REQ, per-OBPI, and per-ADR rollups | gzkit |
| Test discovery | `collect_artifacts()` filesystem walk reading first 25-40 lines as text (lines 187-215) — coarse and brittle | AST-based `scan_test_tree()` static analysis without importing/executing test files | gzkit |
| Drift detection | Not present | `triangle.detect_drift()` (pure function) reports unlinked specs, orphan tests, unjustified code changes | gzkit |
| Domain specificity | `_score_artifact()` lines 235-241 contain airline-specific domain bonuses: `econ`, `economics`, `doctrine`, `ops`, `operations`, `turnaround`, `utilization`, `market`, `qsi`, `gravity`, `shares` — **fails subtraction test** | Domain-neutral; no airline or domain-specific scoring terms | gzkit (passes subtraction test) |
| Data model | `ADR`/`Artifact`/`Scored` stdlib `dataclass` (lines 83-112); violates gzkit `.claude/rules/models.md` policy | Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` throughout per gzkit data-model policy | gzkit |
| Path resolution | Hardcoded `Path(__file__).parents[3]` + `airlineops.paths.subpaths` import (lines 29-36) — airlineops-specific, non-portable | Config-aware `_find_project_root()` via `.gzkit/` marker (cross-project portable) | gzkit |

### Cross-platform / convention-compliance observations

opsdev `lib/adr_traceability.py` carries three structural conflicts with
gzkit doctrine that absorb-by-copy could not eliminate:

1. **Airline domain bonuses in `_score_artifact()`** — `econ`, `economics`,
   `doctrine`, `ops`, `operations`, `turnaround`, `utilization`, `market`,
   `qsi`, `gravity`, `shares`. Removing these reduces the module to generic
   keyword matching with no advantage over the existing gzkit declarative
   approach (the absorption would be net-negative).
2. **stdlib `dataclass`** — violates `.claude/rules/models.md` (Pydantic
   `BaseModel` with `ConfigDict` is the canonical data-model policy).
3. **Module-level airlineops path imports** — `airlineops.paths.subpaths`
   is not a transferable surface; gzkit cannot depend on it without
   inverting the upstream/downstream relationship.

Per OBPI-0.25.0-22's analysis, these are not adapt-and-clean fixes — they
are structural mismatches with gzkit's declarative-precision-first doctrine
that make the absorbed module strictly worse than the existing
`@covers`+AST surface.

## Decision

**Confirm** (by reference to OBPI-0.25.0-22-adr-traceability-pattern,
attested 2026-04-09). gzkit's existing traceability surface
(`traceability.py` 418 L + `triangle.py` 372 L + `tests/test_traceability.py`)
is architecturally superior to opsdev's `lib/adr_traceability.py` (277 L)
on eight named dimensions; absorbing the opsdev module would degrade
governance compliance (heuristic false positives) and inject airline-specific
domain bonuses that fail the subtraction test. No absorption is warranted.

### Brief-scaffold defect (surfaced)

The brief Assumptions section at line 36 reads "No existing gzkit
equivalent means either Absorb or Exclude — there is no Confirm path."
That assumption is **stale and incorrect**:

- gzkit DOES have an existing equivalent (`traceability.py` + `triangle.py`).
- OBPI-0.25.0-22 already evaluated this exact source artifact and decided
  **Confirm** with full six-point rationale — the precedent attests the
  Confirm verdict on identical source.
- OBPI-0.26.0-04 (sibling brief on `lib/adr_governance.py`) carried the
  same Assumptions wording yet successfully landed `decision: Confirm`
  with the validator accepting the verdict.

The Assumptions wording is itself a brief-scaffold defect — the third
instance of this defect class across ADR-0.26.0 briefs (also present in
OBPI-06's wording, surfaced and noted in that brief's
Source-material observation). The defect is tracked structurally under the
broader GHI #376 duplicate-OBPI surface; the doctrine here is that
authoritative precedent (OBPI-0.25.0-22) overrides stale brief assumptions.

### Rationale

1. **Canonical precedent.** OBPI-0.25.0-22-adr-traceability-pattern
   evaluated the same opsdev source file (`lib/adr_traceability.py`,
   277 lines) against gzkit's traceability surface three weeks earlier
   (attested 2026-04-09) and recorded **Decision: Confirm** with a
   six-point rationale anchored on declarative-vs-heuristic, coverage
   depth, drift detection, domain-bonus subtraction-test failure, AST
   precision, and convention compliance. The source artifact is
   byte-for-byte identical at this brief's authoring time.
   Re-running the comparison with divergent rationale would be
   doctrine drift; Confirm-by-reference is the structurally correct
   landing.

2. **Declarative vs heuristic.** gzkit's `@covers` decorator provides
   auditable, precise test-to-requirement linkage. opsdev's `infer()`
   produces fuzzy confidence scores via keyword matching — unsuitable
   for governance compliance where false positives are costly. The
   architectural difference is structural: declarative annotations
   cannot drift from intent the way heuristic scoring can.

3. **Coverage depth.** gzkit's `compute_coverage()` produces a
   structured `CoverageReport` with per-REQ, per-OBPI, and per-ADR
   rollups. opsdev's `generate_text_report()` sums heuristic scores
   into a plain-text report with no structured breakdown — unusable
   for the structured ARB-receipt-driven evidence pattern gzkit
   relies on.

4. **Drift detection capability gap.** gzkit's
   `triangle.detect_drift()` identifies unlinked specs (REQs with no
   `@covers` linkage), orphan tests (`@covers` referencing non-existent
   REQs), and unjustified code changes (changed `src/` files with no
   `JUSTIFIES` edge). opsdev has no equivalent capability — the
   absorption would not add this surface; it would only add a
   regressed traceability primitive.

5. **Domain bonuses fail subtraction test.** opsdev `_score_artifact()`
   lines 235-241 contain airline-specific domain terms (`econ`,
   `economics`, `doctrine`, `ops`, `operations`, `turnaround`,
   `utilization`, `market`, `qsi`, `gravity`, `shares`). Removing these
   would reduce the module to generic keyword matching with no
   advantage over gzkit's declarative approach. The subtraction test
   asks: "if we strip the airline-specific parts, what remains?" The
   answer here is "a worse version of what gzkit already has."

6. **AST precision.** gzkit's `scan_test_tree()` uses static AST
   analysis to discover `@covers` annotations without importing or
   executing test files. opsdev's `collect_artifacts()` reads the
   first 25-40 lines of file text — coarse, brittle, and cannot
   detect annotations in deeper file regions or in conditional
   import scopes.

7. **Convention compliance.** opsdev uses stdlib `dataclass`
   (`ADR`/`Artifact`/`Scored` at lines 83-112); gzkit uses Pydantic
   `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`
   throughout — consistent with `.claude/rules/models.md` (Pydantic
   over dataclasses; immutability with explicit error messages;
   `extra="forbid"` rejects typos). Absorbing opsdev would inject a
   convention-violating data-model surface.

### Tracking the duplicate-evaluation signal

This brief is the fourth OBPI evaluating an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered:

| OBPI | Parent ADR | Source | Decision | Status |
|------|------------|--------|----------|--------|
| OBPI-0.25.0-20 | ADR-0.25.0 | `lib/adr_governance.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-04 | ADR-0.26.0 | (same) | Confirm-by-reference | attested |
| OBPI-0.25.0-29 | ADR-0.25.0 | `lib/ledger_schema.py` | Exclude | attested 2026-04-13 |
| OBPI-0.26.0-05 | ADR-0.26.0 | (same) | Exclude-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-26 | ADR-0.25.0 | `lib/drift_detection.py` | Absorb | attested 2026-04-09 |
| OBPI-0.26.0-06 | ADR-0.26.0 | (same) | Absorb-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-22 | ADR-0.25.0 | `lib/adr_traceability.py` | Confirm | attested 2026-04-09 |
| **OBPI-0.26.0-07** | **ADR-0.26.0** | **(same)** | **Confirm-by-reference** (this brief) | **in-flight** |

The duplicate-OBPI surface is structurally identical to GHI #376's canonical
defect. Same root cause: the ADR-0.26.0 authoring did not check whether
ADR-0.25.0's earlier absorption sweep had already covered each module in
scope. Same proposed mitigation: `gz validate --absorption-duplicates`
would catch this fourth instance alongside the prior three.

Resolution: extend GHI #376 with this `lib/adr_traceability.py` fourth
instance via `gh issue comment` rather than file a parallel GHI. Root cause
and mitigation are identical; tracking unification keeps the ADR-0.26.0
closeout-audit footprint single. The Confirm-by-reference verdict here
closes the in-flight duplicate; GHI #376 carries the long-term tracking
surface.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing traceability surface continues to function identically;
no new commands, flags, output formats, or behavioral changes are
introduced. `features/heavy_lane_gate4.feature` is not touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #7 captured verbatim above (`OBPI Entry (Level 1 WBS)` line).
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-07-adr-traceability` remains green; vacuous pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`. Existing test coverage at `tests/test_traceability.py` exists from OBPI-0.25.0-22 (Confirm decided gzkit's surface is superior). Evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above (`## Decision`, seven-point rationale + brief-scaffold-defect surfacing + duplicate-evaluation tracking + Gate 4 N/A) with concrete capability deltas across eight dimensions and the architectural-superiority observation.
- [x] **Gate 4 (BDD):** N/A — the Confirm-by-reference outcome introduces no operator-visible behavior change. `features/heavy_lane_gate4.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger entry type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

### Implementation Summary


- Decision: Confirm — by reference to OBPI-0.25.0-22-adr-traceability-pattern (attested 2026-04-09). gzkit's `src/gzkit/traceability.py` (418 L) + `src/gzkit/triangle.py` (372 L) + `tests/test_traceability.py` already constitute an architecturally superior traceability surface to opsdev's `lib/adr_traceability.py` (277 L) on eight named dimensions.
- Modules compared: opsdev `adr_traceability.py` (277 L; heuristic keyword `infer()`, stdlib `dataclass` models, airline-specific domain bonuses, text-line file-head sampling) vs gzkit traceability surface (declarative `@covers` decorator, AST-based `scan_test_tree()`, structured `CoverageReport` with per-REQ/OBPI/ADR rollups, pure `detect_drift()` for unlinked specs / orphan tests / unjustified code changes, Pydantic `BaseModel` throughout).
- Architectural superiority across eight dimensions: declarative vs heuristic, ADR-mapping (governance-aware vs threshold-scored), coverage depth (structured rollups vs heuristic sums), test discovery (AST static vs text-line), drift detection (native vs absent), domain specificity (neutral vs airline-bonus-laden), data model (Pydantic vs stdlib dataclass), path resolution (config-aware vs hardcoded).
- Subtraction test failure on opsdev: `_score_artifact()` lines 235-241 contain airline-specific domain bonuses (`econ`, `economics`, `doctrine`, `ops`, `operations`, `turnaround`, `utilization`, `market`, `qsi`, `gravity`, `shares`); removing them reduces the module to generic keyword matching with no advantage over gzkit's declarative approach.
- Brief-scaffold-defect surfaced: brief Assumptions line 36 reads "no Confirm path" but gzkit HAS a superior equivalent; the precedent OBPI-0.25.0-22 attests Confirm; OBPI-0.26.0-04 already established `decision: Confirm` is validator-accepted despite the assumption. Third instance of the same scaffold-defect class across ADR-0.26.0 briefs.
- Duplicate-OBPI surface tracked under **GHI #376** — fourth structural instance after OBPI-0.26.0-04 (`lib/adr_governance.py`), OBPI-0.26.0-05 (`lib/ledger_schema.py`), OBPI-0.26.0-06 (`lib/drift_detection.py`). Resolution: extend GHI #376 with a fourth-instance comment in Stage 5; do not file parallel GHI.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings (`OBJECTIVE`, `SOURCE MATERIAL`, `ASSUMPTIONS`, `NON-GOALS`, `REQUIREMENTS (FAIL-CLOSED)`, `ALLOWED PATHS`, `QUALITY GATES (Heavy)`, `ADR ITEM`) renamed to title case; added missing `Lane`, `Denied Paths`, `Discovery Checklist` sections; corrected `status: Pending` (capital P) to allowed lowercase `pending`; renamed `Verification Commands (Concrete)` → `Verification` and added two OBPI-specific verification commands.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits — Confirm decided existing surface is superior; modifying it would invalidate the OBPI-0.25.0-22 attestation.

### Key Proof


```bash
rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Confirms brief frontmatter and ## Decision body record the Confirm verdict.

rg -c 'OBPI-0.25.0-22' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: ≥10 — brief cites the canonical precedent across body, Decision rationale, Implementation Summary, Closing Argument.

test -f src/gzkit/traceability.py && test -f src/gzkit/triangle.py
# Expected: both gzkit modules exist (Confirm precedent under OBPI-0.25.0-22 attests they are superior).

uv run gz covers OBPI-0.26.0-07-adr-traceability --json
# Expected: {"summary": {"total_reqs": ..., "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): ruff `arb-ruff-879e001d0b4c4b049ed8c24c69738883`, typecheck `arb-step-typecheck-e48828d89a7643eab2f67982b8997c18`, unittest (OBPI-scoped, canonical) `arb-step-unittest-c3137487029644b7b2e5d035557d218a`, mkdocs `arb-step-mkdocs-3d48daf11a07408980e43eda6bb441b9`. REQ→@covers parity: `gz covers OBPI-0.26.0-07-adr-traceability --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`). Mirroring the OBPI-04/05/06 sibling precedent: pre-existing failures (GHI #377 insight schema regression, GHI #378 expired `release.drift_command` flag) remain disclosed in the broader ADR-0.26.0 evidence trail; not introduced by this brief.

## Human Attestation

- Attestor: `g0`
- Date: 2026-05-01
- Attestation: attest completed — OBPI-0.26.0-07 Confirm-by-reference verdict on opsdev lib/adr_traceability.py (277 L). Anchored on OBPI-0.25.0-22-adr-traceability-pattern (attested 2026-04-09, identical 277-line source) and OBPI-0.26.0-04 sibling precedent for `decision: Confirm` despite stale brief Assumptions. Eight-dimension capability comparison authored at brief :238; seven-point rationale at :301; brief-scaffold-defect surfaced at :280 (third instance across ADR-0.26.0); Gate 4 N/A at :390 (zero operator-visible change). Heavy-lane Stage 3 ARB receipts cited inline in Key Proof: lint arb-ruff-879e001d0b4c4b049ed8c24c69738883, typecheck arb-step-typecheck-e48828d89a7643eab2f67982b8997c18, OBPI-scoped unittest arb-step-unittest-c3137487029644b7b2e5d035557d218a, mkdocs arb-step-mkdocs-3d48daf11a07408980e43eda6bb441b9. REQ→@covers parity: 5×[doc] REQs, uncovered_reqs:0 via _synthesize_doc_proof_linkage. No `src/` or `tests/` edits (Confirm preserves OBPI-0.25.0-22 attestation). GHI #376 to be extended with fourth-instance comment in this ceremony.

### Closing Argument

**Confirm-by-reference.** opsdev's `lib/adr_traceability.py` (277 lines)
provides ADR-to-artifact traceability via heuristic keyword inference
(`infer()` with score thresholds), stdlib `dataclass` models, and
airline-specific domain bonuses (`econ`, `ops`, `market`, `qsi`,
`gravity`, `shares`, et al). gzkit's existing traceability surface —
`src/gzkit/traceability.py` (418 L `@covers` decorator + AST-based
`scan_test_tree()` + structured `CoverageReport` computation) plus
`src/gzkit/triangle.py` (372 L REQ entity model + triangle vertex/edge
types + pure `detect_drift()` for unlinked specs / orphan tests /
unjustified code changes) plus `tests/test_traceability.py` — is
architecturally superior on eight dimensions: declarative vs heuristic
linkage, governance-aware ADR mapping, structured coverage rollups,
AST static analysis, native drift detection, domain neutrality, Pydantic
convention compliance, and config-aware path resolution.

The opsdev module's airline-specific domain bonuses fail the subtraction
test: removing them yields generic keyword matching with no advantage
over gzkit's declarative approach. Absorbing the opsdev pattern would
degrade governance compliance (heuristic false positives are unacceptable
in audit contexts) and inject convention-violating stdlib `dataclass`
models. Not absorbed.

This brief is the fourth evaluation of an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered.
The brief Assumptions section's "no Confirm path" wording is itself a
brief-scaffold defect — gzkit HAS a superior equivalent — and the
precedent (OBPI-0.25.0-22 with Decision: Confirm, attested 2026-04-09)
attests the Confirm verdict on identical source. OBPI-0.26.0-04 already
established the precedent that `decision: Confirm` is validator-accepted
despite the brief assumption; this brief follows that precedent. GHI #376
extended to track this fourth occurrence of the duplicate-OBPI defect so
the absorption sweep does not silently recur. No code under `src/gzkit/`
or `tests/` is modified by this brief; modifying the existing module
would invalidate the 2026-04-09 OBPI-0.25.0-22 attestation. Gate 4 N/A:
zero operator-visible behavior change.
