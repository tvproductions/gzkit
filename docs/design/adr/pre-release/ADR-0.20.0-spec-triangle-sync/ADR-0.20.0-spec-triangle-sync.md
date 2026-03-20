---
id: ADR-0.20.0-spec-triangle-sync
status: Proposed
semver: 0.20.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-20
promoted_from: ADR-pool.spec-triangle-sync
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.20.0: Spec-Test-Code Triangle Sync

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit existing REQ identifier usage in OBPI briefs — catalog how `REQ-<semver>-<obpi>-<seq>` appears today and whether the format is consistent.
  1. Catalog existing `@covers` decorator usage in tests — determine the baseline linkage surface.
  1. Map existing `gz validate` and `gz check` output to understand where drift checks would integrate.

Separate prep from change via distinct commits. STOP if REQ identifier format is inconsistent across existing briefs.

**Date Added:** 2026-03-20
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.20.0
**Area:** Governance Traceability Infrastructure

## Agent Context Frame — MANDATORY

**Role:** Traceability architect building the spec-test-code sync framework for gzkit's governance model.

**Purpose:** When this ADR is complete, gzkit can detect when governance specs (REQ-level requirements in OBPI briefs), tests, and code drift out of sync. Operators and agents get a `gz drift` command that reports unlinked specs, orphan tests, and code changes without spec justification — making silent drift visible before it reaches audit.

**Goals:**

- REQ entity has a formal Pydantic model with identifier scheme and lifecycle
- Brief REQ sections are machine-parseable and extractable
- Drift detection engine computes unlinked specs, orphan tests, and unjustified code changes
- `gz drift` CLI surface exposes drift reports in human/JSON/plain modes
- Drift integrates as an advisory check in `gz check`

**Critical Constraint:** This ADR defines the triangle FRAMEWORK — the vertices, edges, and drift detection model. The concrete `@covers` decorator mechanism and deep test traceability enforcement belong to ADR-0.21.0 (tests-for-spec). This ADR provides the data model and detection engine that 0.21.0 builds on.

**Anti-Pattern Warning:** A failed implementation looks like: drift detection that only works on manually maintained linkage files rather than extracting linkage from existing governance artifacts (briefs, tests). The triangle must be derived from artifacts that already exist in the workflow, not from new metadata that agents must remember to maintain.

**Integration Points:**

- `src/gzkit/triangle.py` — triangle data model and drift detection engine
- `src/gzkit/commands/drift.py` — CLI surface
- OBPI briefs — REQ sections are the "spec" vertex of the triangle
- Test files — `@covers` decorators are the "test→spec" edge (mechanism owned by ADR-0.21.0)
- `gz check` — drift becomes an advisory check

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract changed (Heavy lane): new `gz drift` CLI command, changes to `gz check` output
- Tests
  - stdlib unittest guards REQ model, linkage extraction, and drift detection
  - BDD scenarios for `gz drift` CLI contract
- Docs
  - `gz drift` command documentation in `docs/user/commands/`
  - Runbook updated with drift checking workflow
- OBPI mapping
  - Each numbered ADR checklist item maps to one brief; acceptance recorded in the brief

## Intent

gzkit governs work at the ADR and OBPI levels with ledger traceability and gate enforcement. OBPI briefs contain REQ-level requirements (`REQ-<semver>-<obpi>-<seq>`) and tests reference them via `@covers` decorators. But today, nothing detects when these linkages break — a REQ can exist with no test proving it, a test can claim to cover a REQ that was removed, and code can change without any corresponding spec or test delta.

This ADR introduces the spec-test-code triangle as a formal framework: three vertices (Spec, Test, Code), three edges (covers, proves, justifies), and a drift detection engine that identifies broken linkages. The framework is deterministic — it extracts linkage from existing governance artifacts rather than requiring new metadata files.

The triangle concept draws from Drew Breunig's "spec-driven triangle" framing and BEADS graph discipline (dependency-aware edges, machine-readable IDs, query-first surfaces), adapted to gzkit's ledger-first storage model.

## Decision

- Define the triangle data model: three vertex types (Spec/REQ, Test, Code), three edge types (covers, proves, justifies), and a LinkageRecord that captures observed relationships.
- Formalize the REQ entity as a Pydantic model with identifier scheme `REQ-<semver>-<obpi>-<seq>`, extractable from OBPI brief acceptance criteria sections.
- Build a brief REQ extractor that parses existing OBPI briefs to discover REQ entities and their status (checked/unchecked).
- Build a drift detection engine that, given extracted REQs and test linkage data, computes: unlinked specs (REQs with no test), orphan tests (tests claiming non-existent REQs), and coverage gaps.
- Expose drift via `gz drift` CLI with human-readable (default), `--json`, and `--plain` output modes.
- Integrate drift as an advisory check in `gz check` — warn on drift but do not fail gates (advisory→required rollout is a future decision).
- All checks are deterministic — no LLM inference. Structured signals (REQ IDs, @covers decorators, file change sets) provide sufficient data for drift detection.

### Boundary with ADR-0.21.0

This ADR defines the triangle framework and data model. ADR-0.21.0 (tests-for-spec) deepens the Test→Spec edge specifically:

| Owned by 0.20.0 | Owned by 0.21.0 |
|------------------|-----------------|
| REQ entity model | `@covers` decorator enforcement |
| Triangle vertex/edge types | Coverage anchor scanning |
| Brief REQ extraction | Requirement-level coverage reporting |
| Drift detection engine | ADR audit traceability integration |
| `gz drift` CLI | Language-agnostic proof metadata |
| Advisory gate integration | Migration plan for legacy tests |

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **LLM-based drift detection** | Non-deterministic — two runs on the same codebase could produce different results. Governance checks must be reproducible. LLM inference is reserved for cases where structured signals are absent; REQ IDs and @covers are structured signals. |
| **Manual linkage files** | Requires agents to maintain a separate mapping file. Drift detection should extract from artifacts that already exist in the workflow (briefs, tests, commits). |
| **Code coverage as proxy for spec coverage** | Code coverage measures line execution, not requirement fulfillment. A test can achieve 100% line coverage while proving zero requirements. |
| **Merge with ADR-0.21.0** | Tests-for-spec is one edge of the triangle (Test→Spec). Merging would create a scope that's too large — the triangle framework is useful independently of deep @covers enforcement. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | REQ entity and triangle data model | No typed representation of requirements or triangle relationships. Everything downstream operates on untyped strings. |
| 2 | Brief REQ extraction | The "spec" vertex of the triangle has no data source. Drift detection cannot know what requirements exist. |
| 3 | Drift detection engine | Linkage data exists but nothing computes drift. Broken linkages remain invisible. |
| 4 | gz drift CLI | Drift engine exists but operators and agents cannot invoke it. No external surface. |
| 5 | Advisory gate integration | Drift is queryable but not part of the standard quality check flow. Agents don't see drift unless they explicitly run `gz drift`. |

## Interfaces

- **CLI (external contract):** `uv run gz drift` — new command, human/JSON/plain output
- **CLI (external contract):** `uv run gz check` — gains advisory drift check
- **Internal:** `src/gzkit/triangle.py` — triangle data model and drift engine
- **Input contract:** OBPI briefs with `## Acceptance Criteria` containing `REQ-<semver>-<obpi>-<seq>` identifiers

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.20.0-01 | REQ entity model, triangle vertex/edge types, linkage record schema | Lite | Pending |
| 2 | OBPI-0.20.0-02 | Brief REQ extraction: parse OBPI briefs to discover REQ entities | Lite | Pending |
| 3 | OBPI-0.20.0-03 | Drift detection engine: compute unlinked specs, orphan tests, coverage gaps | Lite | Pending |
| 4 | OBPI-0.20.0-04 | `gz drift` CLI surface with human/JSON/plain output modes | Heavy | Pending |
| 5 | OBPI-0.20.0-05 | Advisory gate integration: wire drift into `gz check` | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.20.0-*.md`

**Dependency Graph:**

```text
OBPI-01 (data model)
  ├──► OBPI-02 (brief extraction)  ─┐
  │                                  ├──► OBPI-04 (CLI surface) ──► OBPI-05 (gate integration)
  └──► OBPI-03 (drift engine)     ─┘
```

**Critical path:** OBPI-01 → OBPI-02 → OBPI-03 → OBPI-04 → OBPI-05

**Parallelization:** After OBPI-01, OBPIs 02 and 03 can run concurrently (extraction and detection are independent). OBPI-04 needs both. OBPI-05 needs OBPI-04.

## Non-Goals

- No replacement of ADR/OBPI governance authority.
- No mandatory heavy orchestration runtime.
- No hard requirement for one specific coding agent provider.
- No `@covers` decorator enforcement or scanning — that is ADR-0.21.0 scope.
- No LLM inference for drift detection — deterministic checks only.
- No required (fail-closed) drift gates — advisory mode only in this ADR.

### Scope Creep Guardrails

If any of these emerge during implementation, create a new ADR rather than expanding this one:

- `@covers` decorator scanning and coverage enforcement → ADR-0.21.0
- TASK entity definition or lifecycle → ADR-0.22.0
- Execution memory graph or session history → `ADR-pool.execution-memory-graph`
- Drift auto-remediation (automatically fixing broken linkages) → new pool ADR

## Rationale

gzkit's governance model produces structured artifacts at every tier — ADRs with checklist items, OBPI briefs with REQ-level acceptance criteria, tests with `@covers` decorators, and code with commit messages referencing governance IDs. These artifacts form a triangle of mutual dependencies:

1. **Spec→Test:** Every REQ should have a test proving it.
2. **Test→Code:** Every test should exercise actual implementation.
3. **Code→Spec:** Every significant code change should trace to a governance justification.

Today, these linkages exist but nothing validates them. A brief can declare `REQ-0.15.0-03-02` with no corresponding test. A test can claim `@covers("REQ-0.15.0-03-02")` for a REQ that was renamed or removed. Code can change without any spec delta. These gaps are invisible until audit, when they surface as evidence failures.

The triangle-sync framework makes drift visible early — during implementation, not during audit. The advisory-first rollout ensures adoption is gradual: agents see drift warnings in `gz check` output but are not blocked by them until the tooling is proven reliable.

## Consequences

- New `gz drift` CLI command becomes part of the operator surface
- `gz check` output gains an advisory drift section
- REQ entities gain a formal Pydantic model — first step toward the full four-tier hierarchy
- ADR-0.21.0 (tests-for-spec) builds on this data model for deep traceability
- ADR-0.22.0 (task-level-governance) extends the model with TASK entities

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_triangle.py`
- **BDD (external contract changed):** `features/triangle_drift.feature`
- **Docs:** `docs/user/commands/drift.md`, updated `docs/user/runbook.md`

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note in the brief once Four Gates are green.
- Include the exact command to reproduce the observed behavior, if applicable:

`uv run gz drift`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.20.0`
- **Promoted from:** `ADR-pool.spec-triangle-sync`

### Source & Contracts

- CLI / contracts: `src/gzkit/commands/drift.py`
- Core modules: `src/gzkit/triangle.py`

### Tests

- Unit: `tests/test_triangle.py`
- BDD: `features/triangle_drift.feature`

### Docs

- Commands: `docs/user/commands/drift.md`
- Runbook: `docs/user/runbook.md` (updated)

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---|---|---|---|---|
| src/gzkit/triangle.py | P | REQ model, drift detection | Test output | |
| src/gzkit/commands/drift.py | P | `gz drift` CLI surface | Test output | |
| docs/user/commands/drift.md | P | Command documentation | Rendered docs | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.20.0 | Pending | | | |
