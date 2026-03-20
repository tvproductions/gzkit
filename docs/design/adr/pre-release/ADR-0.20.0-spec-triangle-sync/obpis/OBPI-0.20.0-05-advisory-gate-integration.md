---
id: OBPI-0.20.0-05-advisory-gate-integration
parent: ADR-0.20.0-spec-triangle-sync
item: 5
lane: Heavy
status: Accepted
---

# OBPI-0.20.0-05: Advisory Gate Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #5 — "Advisory gate integration: wire drift into `gz check`"

**Status:** Accepted

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

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Unit tests verify advisory drift appears in `gz check` output
- [ ] Unit tests verify exit code unchanged by advisory drift
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [ ] `docs/user/commands/check.md` updated with drift advisory section
- [ ] `docs/user/runbook.md` updated with drift workflow
- [ ] `uv run mkdocs build --strict` passes

### Gate 5: Human

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.20.0-05-01: Given a repository with drift, when `gz check` is run, then output includes advisory drift warnings.
- [ ] REQ-0.20.0-05-02: Given a repository with drift, when `gz check` is run, then exit code is 0 (drift is advisory, not blocking).
- [ ] REQ-0.20.0-05-03: Given a repository with no drift, when `gz check` is run, then no drift section appears in output.
- [ ] REQ-0.20.0-05-04: Given `gz check --json`, when drift exists, then JSON output includes a drift object with `advisory: true`.

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Gate 3 (Docs):** Docs updated, docs build passes
- [ ] **Gate 5 (Human):** Human attestation recorded
- [ ] **Code Quality:** Lint, format, type checks clean

## Evidence

### Gate 2 (TDD)

```text
# Paste test output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs build output here
```

### Gate 5 (Human)

```text
# Record attestation here
```

## Human Attestation

- Attestor: `human:<name>`
- Attestation:
- Date:

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
