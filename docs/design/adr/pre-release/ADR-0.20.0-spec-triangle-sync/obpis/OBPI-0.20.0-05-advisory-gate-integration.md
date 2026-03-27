---
id: OBPI-0.20.0-05-advisory-gate-integration
parent: ADR-0.20.0-spec-triangle-sync
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.20.0-05: Advisory Gate Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #5 — "Advisory gate integration: wire drift into `gz check`"

**Status:** Completed

## Objective

Integrate drift detection as an advisory (non-blocking) check in `gz check`. When drift exists, `gz check` warns the operator but does not fail gates. This establishes the rollout path from advisory to required.

## Lane

**Heavy** — Changes existing `gz check` CLI output (external contract change).

## Allowed Paths

- `src/gzkit/commands/check.py` — add advisory drift check (or equivalent check integration point)
- `src/gzkit/cli.py` — if check command registration needs updates
- `tests/test_triangle.py` — integration tests for advisory check
- `docs/user/commands/check.md` — update check command docs with drift section
- `docs/user/runbook.md` — update runbook with drift checking workflow
- `features/check_drift_advisory.feature` — BDD acceptance scenarios for advisory output
- `features/steps/check_drift_advisory_steps.py` — BDD step implementations

## Denied Paths

- `src/gzkit/triangle.py` — data model is read-only at this point
- `src/gzkit/commands/drift.py` — standalone command belongs to OBPI-04
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz check` MUST include drift detection in its output when drift exists.
1. REQUIREMENT: Drift check MUST be advisory — warn but do not change `gz check` exit code based on drift alone.
1. REQUIREMENT: Advisory output MUST clearly label drift findings as "advisory" to distinguish from blocking checks.
1. REQUIREMENT: `gz check --json` MUST include drift section in its JSON output with an `advisory: true` flag.
1. REQUIREMENT: Drift check MUST reuse the same engine as `gz drift` — no separate implementation.
1. NEVER: Make drift a blocking check in this OBPI. Rollout to required is a future decision.
1. ALWAYS: Drift advisory runs after all blocking checks complete.

> STOP-on-BLOCKERS: OBPI-04 must be complete (`gz drift` CLI must work standalone first).

## Quality Gates (Heavy)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Unit tests verify advisory drift appears in `gz check` output
- [x] Unit tests verify exit code unchanged by advisory drift
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [x] `docs/user/commands/check.md` updated with drift advisory section
- [x] `docs/user/runbook.md` updated with drift workflow
- [x] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [x] `features/check_drift_advisory.feature` with advisory drift scenarios
- [x] `uv run -m behave features/check_drift_advisory.feature` passes

### Gate 5: Human

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.20.0-05-01: Given a repository with drift, when `gz check` is run, then output includes advisory drift warnings.
- [x] REQ-0.20.0-05-02: Given a repository with drift, when `gz check` is run, then exit code is 0 (drift is advisory, not blocking).
- [x] REQ-0.20.0-05-03: Given a repository with no drift, when `gz check` is run, then no drift section appears in output.
- [x] REQ-0.20.0-05-04: Given `gz check --json`, when drift exists, then JSON output includes a drift object with `advisory: true`.
- [x] REQ-0.20.0-05-05: Given advisory drift findings including unjustified code changes, when `gz check` is run, then the output labels them as advisory rather than blocking.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Gate 3 (Docs):** Docs updated, docs build passes
- [x] **Gate 4 (BDD):** Advisory scenarios pass
- [x] **Gate 5 (Human):** Human attestation recorded
- [x] **Code Quality:** Lint, format, type checks clean

## Evidence

### Implementation Summary

- Added `DriftAdvisoryResult` model and `run_drift_advisory()` to `src/gzkit/quality.py`
- Updated `CheckResult` with optional `drift` field and `run_all_checks()` to include advisory drift
- Added `--json` support and `_render_drift_advisory()` to `src/gzkit/commands/quality.py`
- Added `--json` flag to `check` command in `src/gzkit/cli/main.py`
- 7 unit tests in `TestDriftAdvisoryResult` covering all 5 REQs
- BDD feature `features/check_drift_advisory.feature` with advisory contract scenario
- Updated `docs/user/commands/check.md` and `docs/user/runbook.md`

### Key Proof

```text
$ uv run gz check --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['drift'])"
{'advisory': True, 'has_drift': False, ...}
```

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.test_triangle.TestDriftAdvisoryResult -v
Ran 7 tests in 0.004s — OK
$ uv run gz test — 1720 tests pass
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict — pass
$ uv run gz validate --documents — pass
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/check_drift_advisory.feature
1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
4 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-27
```

## Human Attestation

- Attestor: `human:jeff`
- Attestation: attest completed
- Date: 2026-03-27

---

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
