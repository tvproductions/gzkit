---
id: OBPI-0.19.0-07-adr-status-transition-completed-validated-after-audit
parent: ADR-0.19.0-closeout-audit-processes
item: 7
lane: Lite
status: Draft
---

# OBPI-0.19.0-07: ADR Status Transition Completed -> Validated After Audit

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #7 — "ADR status transition: Completed -> Validated (after audit)"

**Status:** Draft

## Objective

Make `audit_cmd()` automatically transition the ADR lifecycle status from Completed to Validated after a successful audit pass by calling `LifecycleStateMachine.transition()` and appending a `lifecycle_transition` event to the ledger, eliminating the current requirement for operators to manually invoke `gz adr emit-receipt` to record the post-audit state change.

## Lane

**Lite** — Internal lifecycle automation; no new CLI subcommands, flags, or output schema changes. The `Completed -> Validated` transition already exists in `ADR_TRANSITIONS` (lifecycle.py line 59). This OBPI wires the existing state machine into `audit_cmd` so the transition fires automatically on audit success.

## Allowed Paths

- `src/gzkit/cli.py` — `audit_cmd()` function to add lifecycle transition call after successful audit
- `src/gzkit/lifecycle.py` — `LifecycleStateMachine` class (consumed, not modified unless edge-case handling needed)
- `src/gzkit/ledger.py` — `lifecycle_transition_event()` factory and `Ledger` class (consumed, not modified)
- `tests/test_lifecycle.py` — new test cases for the audit-triggered transition path

## Denied Paths

- `src/gzkit/commands/attest.py` — attestation flow is separate; OBPI-09 handles its deprecation
- `docs/user/commands/` — no new CLI surface; existing command docs remain valid
- `.gzkit/ledger.jsonl` — never edited manually
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `audit_cmd()` MUST call `LifecycleStateMachine.transition(adr_id, "ADR", "Completed", "Validated")` only when all audit verification commands pass (zero failures).
1. REQUIREMENT: The `lifecycle_transition` event MUST be appended to the ledger with `from_state="Completed"` and `to_state="Validated"` after the audit proof artifacts are written.
1. REQUIREMENT: When `--dry-run` is active, the transition MUST NOT be executed or recorded.
1. REQUIREMENT: When audit has any failures (non-zero `failures` counter), the transition MUST NOT fire and the ADR MUST remain in Completed state.
1. REQUIREMENT: If the ADR is not in Completed state when audit runs, the transition MUST be skipped gracefully (no crash) and a warning printed to stderr.
1. NEVER: Bypass the `LifecycleStateMachine` validation — always use `sm.transition()`, never append the event directly.
1. ALWAYS: Preserve the existing audit output (proof files, AUDIT.md, AUDIT_PLAN.md) unchanged.

> STOP-on-BLOCKERS: if `LifecycleStateMachine` or `lifecycle_transition_event` are missing from `lifecycle.py`/`ledger.py`, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`

**Context:**

- [ ] `src/gzkit/lifecycle.py` — `ADR_TRANSITIONS` table, `LifecycleStateMachine.transition()` method
- [ ] `src/gzkit/ledger.py` — `lifecycle_transition_event()` factory, `Ledger.append()`, `Ledger.get_artifact_graph()`
- [ ] `src/gzkit/cli.py` lines 2634-2774 — `audit_cmd()` current implementation

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/lifecycle.py` exists with `LifecycleStateMachine` class
- [ ] `src/gzkit/ledger.py` exists with `lifecycle_transition_event()` factory
- [ ] `ADR_TRANSITIONS` includes `TransitionRule(from_state="Completed", to_state="Validated")`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `LifecycleStateMachine` usage in existing commands
- [ ] Test patterns: `tests/test_lifecycle.py` — `TestStateMachineIntegration` class

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [ ] REQ-0.19.0-07-01: Given an ADR in Completed state with all audit verification commands passing, when `gz audit ADR-X.Y.Z` completes, then a `lifecycle_transition` event with `from_state="Completed"` and `to_state="Validated"` is appended to the ledger.
- [ ] REQ-0.19.0-07-02: Given an ADR in Completed state with one or more audit verification commands failing, when `gz audit ADR-X.Y.Z` completes, then no `lifecycle_transition` event is appended and the ADR remains in Completed state.
- [ ] REQ-0.19.0-07-03: Given `gz audit ADR-X.Y.Z --dry-run`, when the command completes, then no `lifecycle_transition` event is appended to the ledger regardless of verification outcomes.
- [ ] REQ-0.19.0-07-04: Given an ADR that is not in Completed state (e.g., Accepted or Validated), when `gz audit ADR-X.Y.Z` runs, then the lifecycle transition is skipped without error and a warning is printed.
- [ ] REQ-0.19.0-07-05: Given a successful audit run, when the `lifecycle_transition` event is written, then existing audit artifacts (AUDIT.md, AUDIT_PLAN.md, proofs/) are unmodified by the transition logic.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_lifecycle -v
```

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Value Narrative

**Before:** After a successful `gz audit`, the ADR remains in Completed state. Operators must separately invoke `gz adr emit-receipt` to transition the ADR to Validated, creating a manual gap where audited ADRs appear incomplete in status dashboards.

**After:** `gz audit` automatically transitions the ADR from Completed to Validated when all verification commands pass, ensuring the ledger reflects the true governance state without manual intervention.

### Key Proof

```bash
# After implementation, a successful audit will produce:
$ uv run gz audit ADR-0.19.0
  lint: PASS
  typecheck: PASS
  test: PASS
  Lifecycle transition: Completed -> Validated (ADR-0.19.0-closeout-audit-processes)
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane — self-closeable after evidence)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
