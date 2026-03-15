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

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` — all tests pass
- [ ] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean
