---
id: OBPI-0.25.0-07-types-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 7
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-07: Types Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-07 — "Evaluate and absorb core/types.py (40 lines) — core type definitions"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/types.py` (40 lines) and determine:
Absorb (airlineops is better) or Exclude (domain-specific). The airlineops
module provides core type definitions used across the codebase. gzkit
currently has no dedicated types module, so the comparison must determine
whether these type definitions are generic enough to belong in gzkit.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/types.py` (40 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- At 40 lines, this is likely type aliases or protocols — quick to evaluate

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Creating a comprehensive type system — only absorb what exists

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/types.py` (40 lines) defines a single `LoadResult` dataclass tracking airline dataset load operation results. Every field is tied to airline ETL pipeline semantics: `dataset` identifies an airline dataset (e.g., BTS/FAA), `period` tracks the time window, `sqlite_path`/`staging_table`/`plain_table` map to the airline data warehouse schema, `rows_staging`/`rows_curated` count ETL pipeline throughput, `parquet_path` references columnar export artifacts, `transport`/`write_mode` control data movement, and `inserted`/`updated`/`dedup_dropped` track ETL mutation counts. The optional `meta` dict carries additional pipeline metadata.

gzkit has no types module, no `LoadResult` equivalent, and no ETL/data pipeline use case. gzkit's domain is governance artifact management — ADRs, OBPIs, ledger events, content types — none of which involve dataset loads, staging tables, or dedup operations.

Additionally, the module uses `@dataclass` rather than Pydantic `BaseModel`, violating gzkit's data model policy (see `.claude/rules/models.md`). Even if the type were generic, it would require a full rewrite to conform to gzkit conventions (`ConfigDict(frozen=True, extra="forbid")`, `Field(...)` with descriptions).

The module's docstring confirms its origin: "Extracted from warehouse ingest module to avoid tight coupling and support upcoming modularization (admission/schema/QC centralization)." This is airline warehouse infrastructure, not generic infrastructure.

## COMPARISON ANALYSIS

| Dimension | airlineops (40 lines, 1 file) | gzkit | Assessment |
|-----------|-------------------------------|-------|------------|
| Purpose | Dataset load result type for airline ETL pipeline | No equivalent — governance artifact management | **No overlap** — entirely different domains |
| Data model | `LoadResult` (`@dataclass`) with 15 fields | No types module exists | No comparison possible |
| Domain coupling | `dataset`, `period`, `staging_table`, `plain_table`, `rows_staging`, `rows_curated` — airline data warehouse | ADR, OBPI, ledger, content type — governance | Both are domain-specific |
| ETL fields | `parquet_path`, `transport`, `write_mode`, `inserted`, `updated`, `dedup_dropped` — pipeline operations | N/A — no ETL/pipeline concept | Airline-specific |
| Convention compliance | `@dataclass` — violates gzkit Pydantic policy | Pydantic `BaseModel` everywhere | Would require full rewrite |
| Immutability | Mutable dataclass (no `frozen=True`) | `ConfigDict(frozen=True)` convention | Convention mismatch |
| Validation | None — no field validation | Pydantic validation built-in | airlineops has no validation |
| Origin | "Extracted from warehouse ingest module" (docstring) | N/A | Airline warehouse infrastructure |
| Generic constructs | None — all fields are domain-specific | N/A | Nothing to extract |
| Test coverage | N/A (not evaluated in airlineops context) | N/A (no module to test) | N/A |

### Subtraction Test

Removing gzkit from airlineops's `types.py` leaves: a `LoadResult` dataclass for airline dataset load operations with fields for dataset identity (`dataset`, `period`), warehouse schema (`sqlite_path`, `staging_table`, `plain_table`), ETL throughput (`rows_staging`, `rows_curated`), export artifacts (`artifact_path`, `parquet_path`), pipeline control (`transport`, `write_mode`), and mutation tracking (`inserted`, `updated`, `dedup_dropped`). Every field is an airline data pipeline concept. There are zero generic constructs to extract. The subtraction test is unambiguous: this module is pure airline domain code.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

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

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, new gzkit module/tests are added or updated — N/A (Exclude decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Exclude` decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the absorbed pattern changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Exclude decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-07-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-07-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Ten-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-07-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-07-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-07-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/types.py
# Expected: airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-07-types-pattern.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-07-types-pattern.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Exclude)
- [x] **Gate 3 (Docs):** Decision rationale completed with comparison table
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Exclude, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for an Exclude decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Exclude decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented evaluation of whether airlineops's `core/types.py` contained reusable type definitions for gzkit. The module name "types" suggests generic shared types, but after reading the implementation completely, it defines a single `LoadResult` dataclass for airline dataset load operations. Every field — `dataset`, `period`, `staging_table`, `plain_table`, `rows_staging`, `rows_curated`, `parquet_path`, `transport`, `write_mode`, `inserted`, `updated`, `dedup_dropped` — is an airline ETL pipeline concept. The docstring confirms its origin: "Extracted from warehouse ingest module." Additionally, the module uses `@dataclass` rather than Pydantic `BaseModel`, violating gzkit's data model policy. gzkit has no types module, no `LoadResult` equivalent, and no ETL/data pipeline use case. The subtraction test is decisive: there are zero generic constructs to extract.

### Key Proof


- Decision: Exclude
- Comparison: ten-dimension analysis in Comparison Analysis section
- airlineops types.py: 40 lines, single `LoadResult` dataclass for airline ETL pipeline results
- All 15 fields are airline-domain: dataset identity, warehouse schema, ETL throughput, export artifacts, pipeline control, mutation tracking
- gzkit equivalent: none — no types module, no ETL use case
- Convention violation: `@dataclass` instead of Pydantic `BaseModel`
- Subtraction test: zero generic constructs — fails completely

### Implementation Summary


- Decision: Exclude — airlineops `core/types.py` (40 lines) is airline-domain-specific
- Module: single `LoadResult` dataclass for airline dataset load operation results
- Subtraction test: all 15 fields are airline ETL pipeline concepts (dataset, staging_table, rows_curated, parquet_path, etc.)
- Convention violation: uses `@dataclass` instead of Pydantic `BaseModel`
- Origin: "Extracted from warehouse ingest module" (module docstring)
- Files created: none
- Files modified: this brief only (Exclude decision with ten-dimension comparison analysis)
- Tests added: none (no code changes)
- Date: 2026-04-09

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-09

## Closing Argument

airlineops's `core/types.py` (40 lines) defines a single `LoadResult` dataclass tracking airline dataset load operation results with 15 fields. Every field is an airline ETL pipeline concept: `dataset` and `period` identify the airline dataset and time window, `sqlite_path`/`staging_table`/`plain_table` map to the airline data warehouse schema, `rows_staging`/`rows_curated` count ETL throughput, `parquet_path` references columnar export artifacts, `transport`/`write_mode` control data movement, and `inserted`/`updated`/`dedup_dropped` track mutation counts. The module's docstring confirms its origin: "Extracted from warehouse ingest module to avoid tight coupling and support upcoming modularization." The module uses `@dataclass` rather than Pydantic `BaseModel`, violating gzkit's data model policy. gzkit has no types module, no `LoadResult` equivalent, no ETL/data pipeline use case, and no warehouse infrastructure. There are zero generic constructs to extract. The subtraction test is unambiguous: this is pure airline domain code. **Decision: Exclude.**
