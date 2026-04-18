---
id: OBPI-0.21.0-05-operator-docs-and-migration
parent: ADR-0.21.0-tests-for-spec
item: 5
lane: Heavy
status: attested_completed
---

# OBPI-0.21.0-05: Operator Docs and Migration Guide

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #5 — "Operator docs, annotation examples, and legacy test migration guide"

**Status:** Completed

## Objective

Produce operator-facing documentation with compliant `@covers` annotation examples, a migration guide for legacy tests, and a language-agnostic proof metadata contract for non-Python test stacks.

## Lane

**Heavy** — Documentation deliverable with external contract implications (defines the annotation standard).

## Allowed Paths

- `docs/user/concepts/test-traceability.md` — traceability concept guide
- `docs/user/runbook.md` — runbook updates for coverage workflow
- `docs/user/commands/covers.md` — if not already created in OBPI-03
- `tests/test_traceability.py` — smoke coverage for documented examples
- `features/test_traceability.feature` — BDD parity for documented operator flow

## Denied Paths

- `src/` — no code changes
- `tests/` — no test changes
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Concept guide MUST include at least 3 compliant `@covers` annotation examples.
1. REQUIREMENT: Migration guide MUST describe how to add `@covers` to existing tests incrementally.
1. REQUIREMENT: Language-agnostic section MUST define equivalent annotation patterns for non-Python (e.g., comment-based `// @covers REQ-X.Y.Z-NN-MM`).
1. REQUIREMENT: Documentation MUST make the language-agnostic proof metadata contract a first-class operator promise, not a hidden footnote.
1. REQUIREMENT: Documentation MUST state that non-Python proof metadata is doctrinally supported but remains runtime-undiscovered until a future ADR adds ingestion support.
1. REQUIREMENT: `uv run mkdocs build --strict` MUST pass.

> STOP-on-BLOCKERS: OBPIs 01-03 must be complete (the tooling being documented must exist).

## Quality Gates (Heavy)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Example syntax remains aligned with `tests/test_traceability.py`
- [x] Tests pass: `uv run -m unittest tests.test_traceability -v`

### Gate 3: Docs

- [x] `docs/user/concepts/test-traceability.md` updated with examples,
  migration guidance, and language-agnostic contract
- [x] `docs/user/runbook.md` updated with rollout/adoption workflow
- [x] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [x] Documented operator flow remains covered by
  `features/test_traceability.feature`
- [x] `uv run -m behave features/test_traceability.feature` passes

### Gate 5: Human

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.21.0-05-01: [doc] Given the concept guide, then it includes 3+ compliant annotation examples.
- [x] REQ-0.21.0-05-02: [doc] Given the migration guide, then it describes incremental adoption without breaking existing tests.
- [x] REQ-0.21.0-05-03: [doc] Given `uv run mkdocs build --strict`, then docs build succeeds.
- [x] REQ-0.21.0-05-04: [doc] Given the concept guide, then the language-agnostic proof metadata contract is presented as a first-class supported pattern.
- [x] REQ-0.21.0-05-05: [doc] Given the operator docs, then they state that non-Python proof metadata is documentation-only until a future ADR adds runtime discovery.

## Verification Commands (Concrete)

```bash
rg -n '@covers\("REQ-' docs/user/concepts/test-traceability.md
# Expected: at least 3 compliant Python examples are present

rg -n '// @covers|covers: REQ-|proof metadata' docs/user/concepts/test-traceability.md docs/user/runbook.md
# Expected: language-agnostic contract and migration guidance are present

uv run -m unittest tests.test_traceability -v
# Expected: documented syntax remains aligned with traceability tests

uv run -m behave features/test_traceability.feature
# Expected: documented operator flow remains behaviorally valid

uv run mkdocs build --strict
# Expected: docs build cleanly
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass
- [x] **Gate 3 (Docs):** Docs build passes
- [x] **Gate 4 (BDD):** Acceptance scenarios pass
- [x] **Gate 5 (Human):** Attestation recorded

### Implementation Summary

- Files created: docs/user/concepts/test-traceability.md (concept guide with 5 @covers examples, 4-step migration guide, language-agnostic proof metadata contract)
- Files modified: docs/user/runbook.md (added Test Traceability and Coverage Adoption section), mkdocs.yml (added nav entry)
- Tests added: (none — docs-only OBPI, existing tests verified aligned)
- Date completed: 2026-03-27

### Key Proof

```
$ rg -n '@covers\("REQ-' docs/user/concepts/test-traceability.md
44:    @covers("REQ-0.6.0-01-01")
61:    @covers("REQ-0.21.0-03-01")
62:    @covers("REQ-0.21.0-03-02")
77:    @covers("REQ-0.21.0-04-01")
171:    @covers("REQ-0.15.0-03-01")

$ uv run mkdocs build --strict
INFO - Documentation built in 0.94 seconds

$ uv run -m behave features/test_traceability.feature
7 scenarios passed, 0 failed, 0 skipped
```

---

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
