---
id: OBPI-0.16.0-05-content-lifecycle-state-machine
parent: ADR-0.16.0-cms-architecture-formalization
item: 5
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.16.0-05 — content-lifecycle-state-machine

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-0.16.0-cms-architecture-formalization.md`
- OBPI Entry: `OBPI-0.16.0-05 — "Explicit Pydantic-enforced lifecycle transitions; ledger-recorded state changes"`

## OBJECTIVE (Lite)

Implement content lifecycle as an explicit state machine. Each content type has defined
states and allowed transitions. State changes are validated by Pydantic before being
recorded in the ledger. Invalid transitions (e.g., Pool → Completed, skipping Proposed →
Accepted) raise validation errors. The state machine is the Django parallel to model
save() — you cannot persist invalid state.

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `src/gzkit/lifecycle.py` (new — state machine module)
- `src/gzkit/ledger.py` (add transition validation before event recording)
- `tests/test_lifecycle.py` (new)

## DENIED PATHS (Lite)

- `.gzkit/ledger.jsonl` (never edit directly)
- CI files, lockfiles

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. `LifecycleStateMachine` class with `transition(artifact_id, from_state, to_state)` method
1. Per-content-type transition tables (ADR: Pool→Draft→Proposed→Accepted→Completed→Validated; OBPI: Accepted→Completed; Skill: draft→active→deprecated→retired)
1. `transition()` validates against allowed transitions; raises `InvalidTransitionError` for violations
1. Successful transitions emit a ledger event (`lifecycle_transition` or similar)
1. `gz validate` checks current artifact states against lifecycle rules — flags artifacts in impossible states
1. Backward-compatible: existing artifacts in valid states pass; no existing workflow breaks

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.16.0-05-01: `LifecycleStateMachine` class with `transition(artifact_id, from_state, to_state)` method
- [x] REQ-0.16.0-05-02: Per-content-type transition tables (ADR: Pool→Draft→Proposed→Accepted→Completed→Validated; OBPI: Accepted→Completed; Skill: draft→active→deprecated→retired)
- [x] REQ-0.16.0-05-03: `transition()` validates against allowed transitions; raises `InvalidTransitionError` for violations
- [x] REQ-0.16.0-05-04: Successful transitions emit a ledger event (`lifecycle_transition` or similar)
- [x] REQ-0.16.0-05-05: `gz validate` checks current artifact states against lifecycle rules — flags artifacts in impossible states
- [x] REQ-0.16.0-05-06: Backward-compatible: existing artifacts in valid states pass; no existing workflow breaks


## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — all tests pass (676 tests, 21 lifecycle-specific)
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 21 tests in 0.001s — OK
Full suite: 676 tests in 9.1s — OK
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
Coverage: src/gzkit/lifecycle.py — 100.00%
```

### Implementation Summary

- Module added: `src/gzkit/lifecycle.py` with `LifecycleStateMachine` class
- Transition tables: per-content-type (ADR, OBPI, PRD, Constitution, Rule, Skill)
- Error handling: `InvalidTransitionError` for invalid state transitions
- Ledger integration: `lifecycle_transition_event()` in `src/gzkit/ledger.py`

### Key Proof

```text
$ uv run -m unittest tests.test_lifecycle.TestTransitionTables.test_adr_pool_cannot_skip_to_completed -v
test_adr_pool_cannot_skip_to_completed ... ok
```

Pool → Completed raises InvalidTransitionError; only Pool → Draft is allowed.

## Human Attestation

- Attestor: `Jeff`
- Attestation: `attest completed`
- Date: `2026-03-19`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-19

**Evidence Hash:** -
