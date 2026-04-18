---
id: OBPI-0.25.0-09-schema-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 9
status: attested_completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-09: Schema Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-09 — "Evaluate and absorb core/schema.py (90 lines) — schema definition utilities"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/schema.py` (90 lines) against gzkit's `schemas/__init__.py` (49 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides schema definition utilities and validation patterns. gzkit has a smaller schemas module, so the comparison must determine whether airlineops provides additional schema infrastructure worth absorbing.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/schema.py` (90 lines)
- **gzkit equivalent:** `src/gzkit/schemas/__init__.py` (49 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's schema approach may differ architecturally (Pydantic-first vs. JSON Schema-first)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Redesigning gzkit's schema architecture unless airlineops has a demonstrably superior approach

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

- [ ] REQ-0.25.0-09-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-09-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-09-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-09-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-09-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/schema.py
# Expected: airlineops source under review exists

test -f src/gzkit/schemas/__init__.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-09-schema-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Comparison Analysis

### airlineops `core/schema.py` (90 lines)

SQLite DDL helpers extracted from the data warehouse ingestion pipeline
(`OBPI-0.1.8-23 Phase 2`). Provides four functions:

- `infer_sql_type(val)` — maps Python types to SQL column types
  (bool/int -> INTEGER, float -> REAL, else -> TEXT)
- `ensure_table_with_schema(conn, table, canonical_schema)` — creates a SQLite
  table from an explicit column schema with idempotent ALTER TABLE for new columns
- `ensure_table(conn, table, sample)` — creates a SQLite table from a sample
  dictionary with inferred types
- `normalize_union_rows(rows)` — normalizes heterogeneous dictionaries to a
  superset of all keys for uniform SQL INSERT

**Single call site:** `airlineops/warehouse/ingest/loader/io.py` (the JSONL-to-
SQLite data warehouse loader). Not imported anywhere else in airlineops.

### gzkit `schemas/__init__.py` (49 lines)

JSON Schema loading for governance artifact validation. Provides two functions:

- `load_schema(name)` — loads a JSON schema from the `gzkit.schemas` package
  using `importlib.resources`
- `get_schema_path(name)` — returns the filesystem path to a schema file

Backed by 7 JSON Schema files (manifest, ADR, OBPI, PRD, persona, agents,
ledger) totaling ~755 lines. gzkit has zero SQLite usage anywhere in its
codebase.

### Comparison Summary

| Dimension | airlineops `core/schema.py` | gzkit `schemas/__init__.py` |
|-----------|---------------------------|----------------------------|
| Domain | SQLite DDL for data warehouse | JSON Schema for governance validation |
| Purpose | Dynamic table creation during JSONL ingestion | Static schema loading for document validation |
| Database dependency | sqlite3 (direct) | None |
| Call sites | 1 (warehouse loader) | Multiple (validation commands) |
| Reuse potential | Airline-domain data pipeline | Governance toolkit |

These modules share only the word "schema" in their paths. They address
completely different problems in completely different domains.

## Decision: Exclude

**Rationale:** The airlineops `core/schema.py` module is airline-domain data
warehouse infrastructure. It provides SQLite DDL helpers specifically designed
for the JSONL-to-SQL ingestion pipeline — a concern that exists nowhere in
gzkit and has no governance application.

**Subtraction test:** `airlineops - gzkit = pure airline domain`. SQLite DDL
helpers for data warehouse ingestion are exactly the kind of domain-specific
code that should remain in airlineops. gzkit's schema infrastructure serves a
fundamentally different purpose (JSON Schema validation of governance
artifacts).

**Why not Absorb:** gzkit has no SQLite usage. Absorbing SQLite DDL helpers
would introduce an unused dependency with no consumer. The functions are tightly
coupled to the warehouse ingestion workflow and would need to be significantly
redesigned to serve any other purpose.

**Why not Confirm:** The modules are not equivalent implementations of the same
concern — they solve different problems entirely. "Confirm" implies gzkit
already covers the need; in this case, the need (SQLite DDL for data
warehouse ingestion) does not exist in gzkit.

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

Before this OBPI, it was unclear whether airlineops's `core/schema.py` contained reusable schema infrastructure that gzkit was missing. After thorough comparison, the two modules solve entirely different problems: airlineops provides SQLite DDL helpers for data warehouse JSONL-to-SQL ingestion, while gzkit provides JSON Schema loading for governance artifact validation. The Exclude decision confirms the subtraction test holds: this is pure airline-domain code with no governance application.

### Key Proof


- Decision: Exclude
- airlineops core/schema.py: 90 lines, SQLite DDL helpers for warehouse ingestion
- gzkit schemas/__init__.py: 49 lines, JSON Schema loading for governance validation
- gzkit has zero SQLite usage anywhere in its codebase
- airlineops schema.py has exactly one call site: warehouse/ingest/loader/io.py

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Rationale: airlineops core/schema.py is SQLite DDL for warehouse ingestion; gzkit has zero SQLite usage
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-09

## Closing Argument

The airlineops `core/schema.py` module provides SQLite DDL helpers for the data
warehouse JSONL-to-SQL ingestion pipeline. gzkit's `schemas/__init__.py` serves
an entirely different purpose: loading JSON Schema files for governance artifact
validation. These modules share no functional overlap. The airlineops module is
used in exactly one place (the warehouse loader), has no governance application,
and introduces a dependency (sqlite3) that gzkit does not use. **Decision:
Exclude** — this is pure airline-domain infrastructure that correctly remains in
airlineops.
