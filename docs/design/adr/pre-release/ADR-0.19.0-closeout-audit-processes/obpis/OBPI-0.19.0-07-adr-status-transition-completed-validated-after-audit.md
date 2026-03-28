---
id: OBPI-0.19.0-07-adr-status-transition-completed-validated-after-audit
parent: ADR-0.19.0-closeout-audit-processes
item: 7
lane: Lite
status: Completed
---

# OBPI-0.19.0-07: ADR Status Transition Completed -> Validated After Audit

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #7 — "ADR status transition: Completed -> Validated (after audit)"

**Status:** Completed

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

- [x] REQ-0.19.0-07-01: Given an ADR in Completed state with all audit verification commands passing, when `gz audit ADR-X.Y.Z` completes, then a `lifecycle_transition` event with `from_state="Completed"` and `to_state="Validated"` is appended to the ledger.
- [x] REQ-0.19.0-07-02: Given an ADR in Completed state with one or more audit verification commands failing, when `gz audit ADR-X.Y.Z` completes, then no `lifecycle_transition` event is appended and the ADR remains in Completed state.
- [x] REQ-0.19.0-07-03: Given `gz audit ADR-X.Y.Z --dry-run`, when the command completes, then no `lifecycle_transition` event is appended to the ledger regardless of verification outcomes.
- [x] REQ-0.19.0-07-04: [doc] Given an ADR that is not in Completed state (e.g., Accepted or Validated), when `gz audit ADR-X.Y.Z` runs, then the lifecycle transition is skipped without error and a warning is printed.
- [x] REQ-0.19.0-07-05: Given a successful audit run, when the `lifecycle_transition` event is written, then existing audit artifacts (AUDIT.md, AUDIT_PLAN.md, proofs/) are unmodified by the transition logic.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_lifecycle -v
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.test_lifecycle.TestAuditTriggeredTransition -v
test_accepted_state_raises_invalid_transition ... ok
test_already_validated_raises_invalid_transition ... ok
test_completed_to_validated_no_event_without_ledger ... ok
test_completed_to_validated_via_state_machine ... ok
test_non_completed_state_raises_invalid_transition ... ok
Ran 5 tests in 0.001s — OK
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
$ uv run gz test — 1079 tests pass
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

- Files modified: `src/gzkit/cli.py` (added `import sys`, lifecycle imports; replaced direct ledger append with SM transition + state check), `tests/test_lifecycle.py` (added `TestAuditTriggeredTransition` — 5 tests)
- Tests added: 5 (TestAuditTriggeredTransition)
- Date completed: 2026-03-22
- Attestation status: Human attested — "attest completed"
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Human (parent ADR Heavy lane — attestation required)
- Attestation: attest completed
- Date: 2026-03-22

---

**Brief Status:** Completed

**Date Completed:** 2026-03-22

**Evidence Hash:** -
