---
id: OBPI-0.21.0-05-operator-docs-and-migration
parent: ADR-0.21.0-tests-for-spec
item: 5
lane: Heavy
status: Accepted
---

# OBPI-0.21.0-05: Operator Docs and Migration Guide

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #5 — "Operator docs, annotation examples, and legacy test migration guide"

**Status:** Accepted

## Objective

Produce operator-facing documentation with compliant `@covers` annotation examples, a migration guide for legacy tests, and a language-agnostic proof metadata contract for non-Python test stacks.

## Lane

**Heavy** — Documentation deliverable with external contract implications (defines the annotation standard).

## Allowed Paths

- `docs/user/concepts/test-traceability.md` — traceability concept guide
- `docs/user/runbook.md` — runbook updates for coverage workflow
- `docs/user/commands/covers.md` — if not already created in OBPI-03

## Denied Paths

- `src/` — no code changes
- `tests/` — no test changes
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Concept guide MUST include at least 3 compliant `@covers` annotation examples.
1. REQUIREMENT: Migration guide MUST describe how to add `@covers` to existing tests incrementally.
1. REQUIREMENT: Language-agnostic section MUST define equivalent annotation patterns for non-Python (e.g., comment-based `// @covers REQ-X.Y.Z-NN-MM`).
1. REQUIREMENT: `uv run mkdocs build --strict` MUST pass.

> STOP-on-BLOCKERS: OBPIs 01-03 must be complete (the tooling being documented must exist).

## Acceptance Criteria

- [ ] REQ-0.21.0-05-01: Given the concept guide, then it includes 3+ compliant annotation examples.
- [ ] REQ-0.21.0-05-02: Given the migration guide, then it describes incremental adoption without breaking existing tests.
- [ ] REQ-0.21.0-05-03: Given `uv run mkdocs build --strict`, then docs build succeeds.

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 3 (Docs):** Docs build passes
- [ ] **Gate 5 (Human):** Attestation recorded

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
