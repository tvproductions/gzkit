---
id: OBPI-0.20.0-01-req-entity-and-triangle-data-model
parent: ADR-0.20.0-spec-triangle-sync
item: 1
lane: Lite
status: Accepted
---

# OBPI-0.20.0-01: REQ Entity and Triangle Data Model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #1 — "REQ entity model, triangle vertex/edge types, linkage record schema"

**Status:** Accepted

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

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item referenced

### Gate 2: TDD

- [ ] Unit tests validate REQ model creation and identifier parsing
- [ ] Unit tests validate vertex/edge type enums
- [ ] Unit tests validate LinkageRecord serialization roundtrip
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [ ] REQ-0.20.0-01-01: Given a valid REQ string `REQ-0.15.0-03-02`, when parsed, then returns a REQ entity with semver=0.15.0, obpi_item=03, criterion_index=02.
- [ ] REQ-0.20.0-01-02: Given an invalid REQ string `REQ-invalid`, when parsed, then raises a ValidationError.
- [ ] REQ-0.20.0-01-03: Given a LinkageRecord with source=Test vertex and target=Spec vertex, when serialized to JSON and back, then roundtrip preserves all fields.
- [ ] REQ-0.20.0-01-04: Given all three edge types, when enumerated, then exactly {covers, proves, justifies} are present.

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Coverage:** Coverage >= 40% maintained
- [ ] **OBPI Completion:** Record evidence in brief

## Evidence

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/type check output here
```

## Human Attestation

- Attestor: `n/a` (Lite lane)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
