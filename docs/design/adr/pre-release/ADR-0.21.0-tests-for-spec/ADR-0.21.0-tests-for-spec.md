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

**Critical Constraint:** This ADR deepens the Test→Spec edge of the triangle
defined in ADR-0.20.0. It builds on the REQ entity model and linkage schema
from 0.20.0 — it does NOT redefine them. The `@covers` decorator feeds
linkage records into the triangle framework. REQ existence validation consumes
the brief-extraction output from ADR-0.20.0, loaded once per process into a
deterministic cached requirement registry before import-time linkage
registration.

**Anti-Pattern Warning:** A failed implementation looks like: `@covers` decorators that are syntactically valid but semantically unchecked — tests claim to cover REQs that don't exist, and nothing detects the mismatch. The decorator must validate against actual REQ entities from briefs.

**Integration Points:**

- `src/gzkit/triangle.py` — REQ entity model and linkage types from ADR-0.20.0
- `src/gzkit/traceability.py` — `@covers` decorator, scanner, coverage reporting
- `src/gzkit/commands/covers.py` — CLI surface
- Existing test files — consumers of `@covers`
- `gz adr audit-check` — consumer of coverage data

---

## Feature Checklist — Appraisal of Completeness

1. **OBPI-0.21.0-01:** `@covers` decorator with REQ format validation,
   brief-backed REQ existence validation, and linkage registration
2. **OBPI-0.21.0-02:** Coverage anchor scanner: walk test tree, discover
   annotations, produce LinkageRecords, and compute ADR/OBPI/REQ rollups
3. **OBPI-0.21.0-03:** `gz covers` CLI with ADR/OBPI/REQ granularity and
   human/JSON/plain output
4. **OBPI-0.21.0-04:** ADR audit integration: wire coverage into
   `gz adr audit-check`
5. **OBPI-0.21.0-05:** Operator docs, migration guide, and language-agnostic
   proof metadata contract for non-Python stacks

Support obligations for the checklist above:

- External contract changed (Heavy lane): new `gz covers` CLI command, changes
  to audit output, and operator-facing traceability doctrine
- stdlib unittest guards decorator validation, scanner behavior, CLI output,
  and audit integration
- BDD scenarios cover `gz covers` and audit-surface proof expectations
- Docs updated in `docs/user/commands/covers.md`,
  `docs/user/concepts/test-traceability.md`, and migration/runbook guidance
- Each numbered ADR checklist item maps to one brief and one concrete
  verification-command set

## Intent

gzkit OBPI briefs contain REQ-level acceptance criteria (`REQ-<semver>-<obpi>-<seq>`), and tests can reference these via `@covers` decorators. But today, the `@covers` mechanism is informal — there's no validation that referenced REQs exist, no scanning to discover all annotations, and no reporting surface to show coverage gaps. An auditor checking whether an OBPI's requirements are actually proven by tests must manually grep test files and cross-reference brief sections.

This ADR formalizes the Test→Spec edge of the triangle (defined in ADR-0.20.0) by:
1. Giving `@covers` decorator real validation (referenced REQ must exist in a brief)
2. Building a scanner that discovers all `@covers` annotations across the test tree
3. Exposing coverage via `gz covers` CLI at three granularity levels (ADR, OBPI, REQ)
4. Feeding coverage data into ADR audit so requirement proof is automated

## Decision

- Formalize `@covers` as a decorator that registers test→REQ linkage,
  validates the REQ identifier format, and fail-closes when the referenced REQ
  is not present in the extracted brief-defined requirement set.
- Build a coverage anchor scanner that walks the test tree, discovers all `@covers` annotations, and produces LinkageRecords (using the triangle data model from ADR-0.20.0).
- Expose coverage reporting via `gz covers` CLI with three granularity levels: by ADR (`gz covers ADR-0.20.0`), by OBPI (`gz covers OBPI-0.20.0-01`), or all (`gz covers`).
- Integrate coverage data into `gz adr audit-check` so requirement fulfillment is part of the audit pipeline.
- Produce operator documentation with compliant annotation examples, a
  migration guide for legacy tests, and a language-agnostic proof metadata
  contract (comments, frontmatter, or config-file annotations) for non-Python
  test stacks so the doctrine is portable without making Python decorators the
  only valid proof surface. In ADR-0.21.0 this contract is documentation-only;
  any runtime ingestion of non-Python proof metadata requires a future ADR.

### Boundary with ADR-0.20.0

| Owned by 0.20.0 | Owned by 0.21.0 |
|------------------|-----------------|
| REQ entity model | `@covers` decorator implementation and REQ existence validation |
| Triangle vertex/edge types | Coverage anchor scanning |
| LinkageRecord schema | `gz covers` CLI |
| Drift detection engine | ADR audit integration |
| `gz drift` CLI | Operator docs, migration guide, and language-agnostic proof metadata contract |

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Inline comments instead of decorators** | Comments are not programmatically discoverable without fragile regex. Decorators register in Python's runtime and are scannable via AST. |
| **Mandatory 100% REQ coverage** | Too aggressive for initial rollout. Advisory reporting first, with a coverage floor (similar to 40% line coverage) as a future gate. |
| **Single-level coverage (REQ only)** | Operators need to ask "is ADR-0.15.0 fully proven?" not just "is REQ-0.15.0-03-02 proven?" Multi-level rollup is essential. |
| **Python-only proof contract** | Would lock the doctrine to one test-stack syntax. gzkit needs a portable proof metadata contract so non-Python tests can declare equivalent REQ linkage without pretending decorators exist everywhere. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | @covers decorator, validation, and registration | No mechanism to declare test→REQ linkage, and invalid or non-existent REQ claims would silently pollute coverage data. |
| 2 | Coverage anchor scanner | @covers exists but nothing collects the annotations. No aggregate view. |
| 3 | gz covers CLI | Scanner works but operators can't invoke it. No external surface. |
| 4 | ADR audit integration | Coverage data exists but audit doesn't use it. Auditors still grep manually. |
| 5 | Operator docs, migration guide, and language-agnostic proof metadata contract | Tooling exists but developers cannot adopt it safely, and non-Python stacks have no sanctioned equivalent proof syntax. |

## Interfaces

- **CLI (external contract):** `uv run gz covers` — new command
- **CLI (external contract):** `uv run gz adr audit-check` — gains coverage section
- **Internal:** `src/gzkit/traceability.py` — decorator, scanner, coverage engine
- **Decorator contract:** `@covers("REQ-X.Y.Z-NN-MM")` on test methods

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.21.0-01 | `@covers` decorator with REQ format validation, brief-backed REQ existence validation, and linkage registration | Lite | Pending |
| 2 | OBPI-0.21.0-02 | Coverage anchor scanner: walk test tree, discover annotations, produce LinkageRecords | Lite | Pending |
| 3 | OBPI-0.21.0-03 | `gz covers` CLI with ADR/OBPI/REQ granularity and human/JSON/plain output | Heavy | Pending |
| 4 | OBPI-0.21.0-04 | ADR audit integration: wire coverage into `gz adr audit-check` | Heavy | Pending |
| 5 | OBPI-0.21.0-05 | Operator docs, annotation examples, legacy test migration guide, and language-agnostic proof metadata contract | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.21.0-*.md`

**Dependency Graph:**

```text
OBPI-01 (@covers decorator)
  └──► OBPI-02 (scanner)
         └──► OBPI-03 (CLI) ──► OBPI-04 (audit integration)
                              └──► OBPI-05 (docs)
```

**Critical path:** OBPI-01 → OBPI-02 → OBPI-03 → OBPI-04

**Verification spine:**

- OBPI-01: `uv run -m unittest tests.test_traceability -v`
- OBPI-02: `uv run -m unittest tests.test_traceability -v`
- OBPI-03: `uv run gz covers --help`,
  `uv run -m behave features/test_traceability.feature`
- OBPI-04: `uv run gz adr audit-check ADR-0.20.0 --json`
- OBPI-05: `uv run mkdocs build --strict`

## Non-Goals

- No immediate mandate for branch-level 100% requirement coverage.
- No replacement of code coverage tools — requirement coverage is orthogonal to line coverage.
- No lock-in to decorator syntax if equivalent metadata surfaces emerge later.
- No runtime implementation for non-Python proof discovery in this ADR beyond
  documenting the equivalent metadata contract and migration path.
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

## Long-Term Validity Guards

- `tests/test_traceability.py` is the regression contract for decorator
  behavior, unknown-REQ rejection, scanner rollups, and audit/CLI integration.
- `features/test_traceability.feature` is the external-surface regression
  contract for `gz covers` and audit proof reporting.
- `docs/user/concepts/test-traceability.md` and `docs/user/runbook.md` define
  the operator-facing proof metadata contract. Non-Python patterns remain
  documentation-only until a future ADR adds discovery/runtime support.
- Any future runtime ingestion of comment/frontmatter/config-file proof
  metadata without a new ADR is invalid and should be treated as doctrinal
  drift.

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
| 0.21.0 | Completed | Jeff | 2026-03-27 | completed |
