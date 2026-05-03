---
id: OBPI-0.0.25-01-implement-coverage-gate
parent: ADR-0.0.25-obpi-completion-req-coverage-gate
item: 1
lane: Heavy
status: Completed
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

**Prerequisites**

- [x] AGENTS.md § OBPI Acceptance Protocol read; foundation+heavy ⇒ brief-level Gate 5 attestation required.
- [x] `.claude/rules/tests.md` § TASK-Driven Workflow + REQ-derivation rule read; tests assert REQ semantics, not strings.
- [x] `.claude/rules/pythonic.md` § Imports rule read; AST-based discovery satisfies "no lazy/runtime introspection".
- [x] `.claude/rules/cross-platform.md` v0.2.0 read; relative paths render via `.as_posix()`.

**Existing Code**

- [x] `src/gzkit/commands/obpi_complete.py` — actual `gz obpi complete` handler (brief allowlist names `obpi.py` re-exporter; routing rationale in plan).
- [x] `src/gzkit/commands/obpi_complete.py:275-354` — `_enforce_attestation_receipt_gate` precedent for shape, ordering, fail-closed predicate.
- [x] `src/gzkit/traceability.py:209` — `scan_test_tree` AST scanner reused by `discover_covers`.
- [x] `src/gzkit/triangle.py:182` — `extract_reqs_from_brief` REQ parser reused by `parse_brief_reqs`.
- [x] `tests/governance/test_type_ignore_syntax.py` — exemplar of an existing AST-based audit pattern.
- [x] `tests/commands/test_obpi_complete.py` — fixture/mock-rig precedent for OBPI-0.0.24-02 wire tests.

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


gz covers OBPI-0.0.25-01 --json reports total_reqs=6, covered_reqs=6, uncovered_reqs=0, coverage_percent=100.0. Full unittest sweep clean (receipt arb-step-unittest-047406a8259a4f708aceceef1e0bb2e2). Lint clean (arb-ruff-d03778f1c09946b0bec1b2ba22eaef85). Typecheck clean (arb-step-typecheck-4a6ec87d5dc34c48a3720374fb6e2db5). mkdocs --strict clean in 3.77s (arb-step-mkdocs-77755a52cb71448a982a37eaab653aa0). gz validate --documents passes 1 scope. gz obpi precomplete reports READY: 5/5 preconditions met.

### Implementation Summary


- Module: src/gzkit/governance/req_coverage.py — new module exporting parse_brief_reqs(Path) -> list[str], discover_covers(req_id, Path) -> list[TestRef], frozen Pydantic TestRef. Reuses traceability.scan_test_tree for AST-safe @covers discovery and triangle.extract_reqs_from_brief for canonical REQ-line parsing.
- Wire: src/gzkit/commands/obpi_complete.py — added _qualified_to_unittest_target, _any_covering_test_passes, _enforce_req_coverage_gate; wired the gate into obpi_complete_cmd as section 4a-ter (between receipt-binding gate and TTY gate). Heavy/foundation = exit 3 on uncovered or failing-cover REQ; lite-non-foundation = warn-only.
- Tests added: tests/governance/test_req_coverage.py (10 unit tests), tests/commands/test_obpi_complete_coverage_gate.py (6 wire tests covering REQ-01..06).
- Tests modified: tests/commands/test_obpi_complete.py, tests/commands/test_runtime.py, tests/test_obpi_complete_cmd.py — patched out the new gate in 5 pre-existing fixtures.
- Date completed: 2026-05-03
- Attestation status: attested (operator: g0)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.25-01 wires the REQ-coverage gate into gz obpi complete: parse_brief_reqs + discover_covers in the new src/gzkit/governance/req_coverage.py compose with _enforce_req_coverage_gate inserted at section 4a-ter, fail-closed on heavy/foundation, warn-only on lite-non-foundation. 6/6 REQ acceptance criteria covered (gz covers reports uncovered_reqs=0). Full ARB sweep green: ruff (arb-ruff-d03778f1c09946b0bec1b2ba22eaef85), typecheck (arb-step-typecheck-4a6ec87d5dc34c48a3720374fb6e2db5), unittest (arb-step-unittest-047406a8259a4f708aceceef1e0bb2e2), mkdocs --strict (arb-step-mkdocs-77755a52cb71448a982a37eaab653aa0). Plan-audit receipt PASS; precomplete 5/5 preconditions ready.
- Date: 2026-05-03

---

**Brief Status:** Completed

**Date Completed:** 2026-05-03

**Evidence Hash:** -
