---
id: OBPI-0.20.0-01-req-entity-and-triangle-data-model
parent: ADR-0.20.0-spec-triangle-sync
item: 1
lane: Lite
status: in_progress
---

# OBPI-0.20.0-01: REQ Entity and Triangle Data Model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #1 — "REQ entity model, triangle vertex/edge types, linkage record schema"

**Status:** Completed

## Objective

Define the foundational Pydantic data models for the spec-test-code triangle: the REQ entity with its identifier scheme, triangle vertex types (Spec, Test, Code), edge types (covers, proves, justifies), and the LinkageRecord that captures observed relationships between vertices.

## Lane

**Lite** — Internal data model; no external CLI/API/schema contract changes in this OBPI. The `gz drift` CLI surface ships in OBPI-04.

## Allowed Paths

- `src/gzkit/triangle.py` — triangle data model: REQ entity, vertex/edge types, linkage records
- `tests/test_triangle.py` — triangle data model unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI surface belongs to OBPI-04
- `src/gzkit/cli.py` — CLI integration belongs to OBPI-04/05
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Define REQ entity with identifier scheme `REQ-<semver>-<obpi_item>-<criterion_index>` (e.g., `REQ-0.15.0-03-02`).
1. REQUIREMENT: REQ model MUST include: id, description, status (checked/unchecked), parent OBPI reference.
1. REQUIREMENT: Define three vertex types: Spec (a REQ entity), Test (a test method/function), Code (a source file/function).
1. REQUIREMENT: Define three edge types: covers (test→spec), proves (test→code), justifies (code→spec).
1. REQUIREMENT: Define LinkageRecord model capturing: source vertex, target vertex, edge type, evidence source (file path, line number).
1. REQUIREMENT: All models MUST use Pydantic BaseModel with `ConfigDict(frozen=True, extra="forbid")`.
1. REQUIREMENT: REQ identifier MUST be parseable from a string using a classmethod or standalone function.
1. NEVER: Vendor-specific references in the data model.
1. ALWAYS: Type hints use modern syntax (`str | None`, `list[str]`).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Quality Gates (Lite)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item referenced

### Gate 2: TDD

- [x] Unit tests validate REQ model creation and identifier parsing
- [x] Unit tests validate vertex/edge type enums
- [x] Unit tests validate LinkageRecord serialization roundtrip
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [x] REQ-0.20.0-01-01: Given a valid REQ string `REQ-0.15.0-03-02`, when parsed, then returns a REQ entity with semver=0.15.0, obpi_item=03, criterion_index=02.
- [x] REQ-0.20.0-01-02: Given an invalid REQ string `REQ-invalid`, when parsed, then raises a ValidationError.
- [x] REQ-0.20.0-01-03: Given a LinkageRecord with source=Test vertex and target=Spec vertex, when serialized to JSON and back, then roundtrip preserves all fields.
- [x] REQ-0.20.0-01-04: Given all three edge types, when enumerated, then exactly {covers, proves, justifies} are present.

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Coverage:** Coverage >= 40% maintained
- [x] **OBPI Completion:** Record evidence in brief

## Evidence

### Implementation Summary

- Files created: `src/gzkit/triangle.py`, `tests/test_triangle.py`
- Tests added: 32 unit tests covering REQ parsing, vertex/edge enums, LinkageRecord roundtrip
- Date completed: 2026-03-27

### Key Proof

```text
$ uv run -m unittest tests.test_triangle -v
Ran 32 tests in 0.001s — OK
```

### Gate 2 (TDD)

```text
Ran 32 tests in 0.001s — OK (tests/test_triangle.py)
Full suite: 1663 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

## Human Attestation

- Attestor: Jeffry Babb
- Attestation: completed
- Date: 2026-03-27

---

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
