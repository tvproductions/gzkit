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

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Example syntax remains aligned with `tests/test_traceability.py`
- [ ] Tests pass: `uv run -m unittest tests.test_traceability -v`

### Gate 3: Docs

- [ ] `docs/user/concepts/test-traceability.md` updated with examples,
  migration guidance, and language-agnostic contract
- [ ] `docs/user/runbook.md` updated with rollout/adoption workflow
- [ ] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [ ] Documented operator flow remains covered by
  `features/test_traceability.feature`
- [ ] `uv run -m behave features/test_traceability.feature` passes

### Gate 5: Human

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.21.0-05-01: Given the concept guide, then it includes 3+ compliant annotation examples.
- [ ] REQ-0.21.0-05-02: Given the migration guide, then it describes incremental adoption without breaking existing tests.
- [ ] REQ-0.21.0-05-03: Given `uv run mkdocs build --strict`, then docs build succeeds.
- [ ] REQ-0.21.0-05-04: Given the concept guide, then the language-agnostic proof metadata contract is presented as a first-class supported pattern.
- [ ] REQ-0.21.0-05-05: Given the operator docs, then they state that non-Python proof metadata is documentation-only until a future ADR adds runtime discovery.

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

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Docs build passes
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
