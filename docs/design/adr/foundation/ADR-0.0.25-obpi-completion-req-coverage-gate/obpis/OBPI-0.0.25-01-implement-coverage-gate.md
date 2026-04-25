---
id: OBPI-0.0.25-01-implement-coverage-gate
parent: ADR-0.0.25-obpi-completion-req-coverage-gate
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.25-01-implement-coverage-gate: REQ-coverage gate inside `gz obpi complete`

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/ADR-0.0.25-obpi-completion-req-coverage-gate.md`
- **Checklist Item:** #1 — "Implement the REQ-coverage gate in `gz obpi complete` (parse acceptance criteria, locate `@covers`, run scoped unittest, fail-closed on heavy/foundation)"

**Status:** Draft

## Objective

Add a pre-emission check inside `gz obpi complete` that parses the brief's `## Acceptance Criteria` section for REQ-IDs, locates `@covers(REQ-…)`-decorated tests, runs them scoped, and fails closed when any REQ has zero passing covered tests on heavy/foundation lanes.

## Lane

**Heavy** — Modifies completion runtime contract.

## Allowed Paths

- `src/gzkit/commands/obpi.py` — gate logic in `complete` subcommand
- `src/gzkit/governance/req_coverage.py` (new module) — REQ parsing and `@covers` discovery
- `tests/governance/test_req_coverage.py` — unit tests for the new module
- `tests/commands/test_obpi_complete_coverage_gate.py` — wiring tests
- `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/commands/adr_emit_receipt.py` — mirrored gate lands in OBPI-02
- `AGENTS.md`, `docs/user/runbook.md` — doc updates in OBPI-03
- `features/**` — BDD coverage in OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New module `src/gzkit/governance/req_coverage.py` with two pure functions: `parse_brief_reqs(brief_path: Path) -> list[str]` (returns REQ-IDs from `## Acceptance Criteria`) and `discover_covers(req_id: str, tests_root: Path) -> list[TestRef]` (returns module:class:test_method tuples for `@covers(REQ-<id>)`-decorated tests).
2. REQUIREMENT: `gz obpi complete <OBPI-ID>` calls `parse_brief_reqs` on the closing brief, then `discover_covers` per REQ, then runs the discovered tests scoped via the existing `unittest` runner.
3. REQUIREMENT: If any REQ has zero `@covers` matches, OR any covered test fails, AND the parent ADR is heavy or foundation, exit 3 with a structured message naming each gap.
4. REQUIREMENT: If lite-non-foundation, log a warning naming each gap and proceed with completion.
5. REQUIREMENT: Test discovery uses AST parsing (not regex) of the test files to honor the existing `.claude/rules/pythonic.md` § Imports rule (no lazy/runtime introspection that imports test modules).
6. REQUIREMENT: REQ-ID parsing tolerates the canonical brief shape `- [ ] REQ-X.Y.Z-NN-MM: <description>` and skips non-REQ checklist items.
7. REQUIREMENT: Duplicate `@covers` decorators (same REQ on multiple tests) count toward coverage; one passing test is sufficient.
8. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.25-01-NN)`.
9. REQUIREMENT: Tests use `tempfile`-backed brief and test fixtures; NEVER touch the live test corpus or briefs in tests.
10. REQUIREMENT: NEVER include the operator's personal email in code or fixtures.
11. REQUIREMENT: The gate runs AFTER OBPI-0.0.24's receipt-binding gate (or in parallel — whichever lands first; document the ordering).
12. REQUIREMENT: TDD discipline: Red-Green-Refactor per behavior increment.

> STOP-on-BLOCKERS: if the existing brief schema or `## Acceptance Criteria` section convention has changed materially since this OBPI was authored, STOP and reconcile.

## Discovery Checklist

- [ ] AGENTS.md § OBPI Acceptance Protocol
- [ ] `.claude/rules/tests.md` § TASK-Driven Workflow (REQ-derivation rule)
- [ ] `src/gzkit/commands/obpi.py` — existing `complete` subcommand structure
- [ ] `tests/governance/` — example of an existing AST-based audit (e.g., `test_type_ignore_syntax.py`)
- [ ] An existing brief's `## Acceptance Criteria` section as input fixture template

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] RGR per behavior increment, observed RED before GREEN
- [ ] `uv run gz test` passes
- [ ] Coverage does not regress below 40%

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] Manpage updates land in OBPI-03

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios in OBPI-03

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_req_coverage.py tests/commands/test_obpi_complete_coverage_gate.py -v
# Smoke test against a fixture brief with an uncovered REQ
```

## Acceptance Criteria

- [ ] REQ-0.0.25-01-01: Given a heavy-lane brief whose every `## Acceptance Criteria` REQ has at least one passing `@covers`-decorated test, when `gz obpi complete` runs, then the gate passes and completion proceeds.
- [ ] REQ-0.0.25-01-02: Given a heavy-lane brief with one REQ lacking any `@covers` decorator, when `gz obpi complete` runs, then exit 3 with a structured message naming the uncovered REQ.
- [ ] REQ-0.0.25-01-03: Given a foundation-kind lite-lane brief with the same gap, when `gz obpi complete` runs, then exit 3 (foundation overrides lite).
- [ ] REQ-0.0.25-01-04: Given a lite-non-foundation brief with the same gap, when `gz obpi complete` runs, then a warning is logged and completion proceeds.
- [ ] REQ-0.0.25-01-05: Given a heavy-lane brief whose covered test currently fails, when `gz obpi complete` runs, then exit 3 (gate runs the test and observes failure).
- [ ] REQ-0.0.25-01-06: Given a brief with multiple `@covers` decorators per REQ, when `gz obpi complete` runs, then any one passing test satisfies the REQ.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle; tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Pass + failing-gate transcripts on fixture briefs
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RGR observations + final unittest output
```

### Code Quality

```text
# Paste lint/typecheck output
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
