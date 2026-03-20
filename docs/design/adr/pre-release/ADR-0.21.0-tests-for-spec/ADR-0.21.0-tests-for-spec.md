---
id: ADR-0.21.0-tests-for-spec
status: Proposed
semver: 0.21.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-20
promoted_from: ADR-pool.tests-for-spec
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.21.0: Tests as Spec Verification Surface

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit existing `@covers` decorator usage across tests/ — count how many tests have it, how many don't, what REQ/OBPI/ADR IDs are referenced.
  1. Catalog the REQ identifier format consistency across all OBPI briefs — confirm `REQ-<semver>-<obpi>-<seq>` is the universal pattern.
  1. Review ADR-0.20.0's triangle data model to understand the REQ entity and linkage types this ADR builds on.

**Date Added:** 2026-03-20
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.21.0
**Area:** Test Traceability Infrastructure

## Agent Context Frame — MANDATORY

**Role:** Traceability engineer connecting tests to governance specs via the `@covers` mechanism.

**Purpose:** When this ADR is complete, every test in gzkit can declare which governance requirement it proves via `@covers("REQ-X.Y.Z-NN-MM")`. A `gz covers` command reports which requirements have test proof and which don't. ADR audit integrates coverage data so auditors can verify requirement fulfillment without manual inspection.

**Goals:**

- `@covers` decorator formalized with validation and registration
- Coverage anchor scanner discovers all `@covers` annotations across the test tree
- `gz covers` CLI reports coverage by ADR/OBPI/REQ level
- ADR audit uses coverage data to verify requirement fulfillment
- Operator documentation with migration guide for legacy tests

**Critical Constraint:** This ADR deepens the Test→Spec edge of the triangle defined in ADR-0.20.0. It builds on the REQ entity model and linkage schema from 0.20.0 — it does NOT redefine them. The `@covers` decorator feeds linkage records into the triangle framework.

**Anti-Pattern Warning:** A failed implementation looks like: `@covers` decorators that are syntactically valid but semantically unchecked — tests claim to cover REQs that don't exist, and nothing detects the mismatch. The decorator must validate against actual REQ entities from briefs.

**Integration Points:**

- `src/gzkit/triangle.py` — REQ entity model and linkage types from ADR-0.20.0
- `src/gzkit/traceability.py` — `@covers` decorator, scanner, coverage reporting
- `src/gzkit/commands/covers.py` — CLI surface
- Existing test files — consumers of `@covers`
- `gz adr audit-check` — consumer of coverage data

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract changed (Heavy lane): new `gz covers` CLI command, changes to audit output
- Tests
  - stdlib unittest guards decorator registration, scanner, and coverage computation
  - BDD scenarios for `gz covers` CLI
- Docs
  - Command documentation in `docs/user/commands/covers.md`
  - Annotation guide in `docs/user/concepts/test-traceability.md`
- OBPI mapping
  - Each numbered checklist item maps to one brief

## Intent

gzkit OBPI briefs contain REQ-level acceptance criteria (`REQ-<semver>-<obpi>-<seq>`), and tests can reference these via `@covers` decorators. But today, the `@covers` mechanism is informal — there's no validation that referenced REQs exist, no scanning to discover all annotations, and no reporting surface to show coverage gaps. An auditor checking whether an OBPI's requirements are actually proven by tests must manually grep test files and cross-reference brief sections.

This ADR formalizes the Test→Spec edge of the triangle (defined in ADR-0.20.0) by:
1. Giving `@covers` decorator real validation (referenced REQ must exist in a brief)
2. Building a scanner that discovers all `@covers` annotations across the test tree
3. Exposing coverage via `gz covers` CLI at three granularity levels (ADR, OBPI, REQ)
4. Feeding coverage data into ADR audit so requirement proof is automated

## Decision

- Formalize `@covers` as a decorator that registers test→REQ linkage and validates the REQ identifier format.
- Build a coverage anchor scanner that walks the test tree, discovers all `@covers` annotations, and produces LinkageRecords (using the triangle data model from ADR-0.20.0).
- Expose coverage reporting via `gz covers` CLI with three granularity levels: by ADR (`gz covers ADR-0.20.0`), by OBPI (`gz covers OBPI-0.20.0-01`), or all (`gz covers`).
- Integrate coverage data into `gz adr audit-check` so requirement fulfillment is part of the audit pipeline.
- Produce operator documentation with compliant annotation examples and a migration guide for legacy tests.
- Define a language-agnostic proof metadata contract (comments, frontmatter, or config-file annotations) for non-Python test stacks.

### Boundary with ADR-0.20.0

| Owned by 0.20.0 | Owned by 0.21.0 |
|------------------|-----------------|
| REQ entity model | `@covers` decorator implementation |
| Triangle vertex/edge types | Coverage anchor scanning |
| LinkageRecord schema | `gz covers` CLI |
| Drift detection engine | ADR audit integration |
| `gz drift` CLI | Operator docs and migration guide |

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Inline comments instead of decorators** | Comments are not programmatically discoverable without fragile regex. Decorators register in Python's runtime and are scannable via AST. |
| **Mandatory 100% REQ coverage** | Too aggressive for initial rollout. Advisory reporting first, with a coverage floor (similar to 40% line coverage) as a future gate. |
| **Single-level coverage (REQ only)** | Operators need to ask "is ADR-0.15.0 fully proven?" not just "is REQ-0.15.0-03-02 proven?" Multi-level rollup is essential. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | @covers decorator and registration | No mechanism to declare test→REQ linkage. Coverage is undiscoverable. |
| 2 | Coverage anchor scanner | @covers exists but nothing collects the annotations. No aggregate view. |
| 3 | gz covers CLI | Scanner works but operators can't invoke it. No external surface. |
| 4 | ADR audit integration | Coverage data exists but audit doesn't use it. Auditors still grep manually. |
| 5 | Operator docs and migration guide | Tooling exists but developers don't know how to use it. Adoption stalls. |

## Interfaces

- **CLI (external contract):** `uv run gz covers` — new command
- **CLI (external contract):** `uv run gz adr audit-check` — gains coverage section
- **Internal:** `src/gzkit/traceability.py` — decorator, scanner, coverage engine
- **Decorator contract:** `@covers("REQ-X.Y.Z-NN-MM")` on test methods

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.21.0-01 | `@covers` decorator with REQ validation and linkage registration | Lite | Pending |
| 2 | OBPI-0.21.0-02 | Coverage anchor scanner: walk test tree, discover annotations, produce LinkageRecords | Lite | Pending |
| 3 | OBPI-0.21.0-03 | `gz covers` CLI with ADR/OBPI/REQ granularity and human/JSON/plain output | Heavy | Pending |
| 4 | OBPI-0.21.0-04 | ADR audit integration: wire coverage into `gz adr audit-check` | Heavy | Pending |
| 5 | OBPI-0.21.0-05 | Operator docs, annotation examples, and legacy test migration guide | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.21.0-*.md`

**Dependency Graph:**

```text
OBPI-01 (@covers decorator)
  └──► OBPI-02 (scanner)
         └──► OBPI-03 (CLI) ──► OBPI-04 (audit integration)
                              └──► OBPI-05 (docs)
```

**Critical path:** OBPI-01 → OBPI-02 → OBPI-03 → OBPI-04

## Non-Goals

- No immediate mandate for branch-level 100% requirement coverage.
- No replacement of code coverage tools — requirement coverage is orthogonal to line coverage.
- No lock-in to decorator syntax if equivalent metadata surfaces emerge later.
- No changes to the REQ entity model — that belongs to ADR-0.20.0.

### Scope Creep Guardrails

- Full triangle drift detection → ADR-0.20.0
- TASK entity or lifecycle → ADR-0.22.0
- Enforcement as a blocking gate → future ADR (rollout from advisory)

## Rationale

Requirement-level test traceability is the missing link between governance specs and implementation proof. Code coverage tools measure line execution, but "100% lines covered" says nothing about whether the code fulfills its governance requirements. A test that exercises every line of a function may not verify the specific behavior that the REQ demands.

The `@covers` pattern — already informally used in gzkit — makes this explicit: each test declares which requirement it proves, and tooling can aggregate, report, and audit this linkage. Combined with ADR-0.20.0's triangle framework, this creates a closed loop: specs define requirements, tests prove them, and drift detection catches gaps.

## Consequences

- `@covers` becomes a first-class governance mechanism in gzkit's test infrastructure
- `gz covers` becomes a new operator surface
- ADR audit gains automated requirement proof checking
- Legacy tests without `@covers` are not broken but are reported as uncovered
- ADR-0.22.0 (task-level-governance) can link TASKs to REQs through the same traceability chain

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_traceability.py`
- **BDD (external contract changed):** `features/test_traceability.feature`
- **Docs:** `docs/user/commands/covers.md`, `docs/user/concepts/test-traceability.md`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.21.0`
- **Promoted from:** `ADR-pool.tests-for-spec`
- **Depends on:** ADR-0.20.0 (REQ entity model, triangle framework)

### Source & Contracts

- Core modules: `src/gzkit/traceability.py`
- CLI: `src/gzkit/commands/covers.py`

### Tests

- Unit: `tests/test_traceability.py`
- BDD: `features/test_traceability.feature`

### Docs

- Commands: `docs/user/commands/covers.md`
- Concepts: `docs/user/concepts/test-traceability.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---|---|---|---|---|
| src/gzkit/traceability.py | P | @covers, scanner, coverage engine | Test output | |
| src/gzkit/commands/covers.py | P | `gz covers` CLI | Test output | |
| docs/user/commands/covers.md | P | Command docs | Rendered docs | |
| docs/user/concepts/test-traceability.md | P | Annotation guide | Rendered docs | |

### SIGN-OFF

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.21.0 | Pending | | | |
