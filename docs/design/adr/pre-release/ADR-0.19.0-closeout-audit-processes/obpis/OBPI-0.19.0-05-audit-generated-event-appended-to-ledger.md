---
id: OBPI-0.19.0-05-audit-generated-event-appended-to-ledger
parent: ADR-0.19.0-closeout-audit-processes
item: 5
lane: Lite
status: Completed
---

# OBPI-0.19.0-05: `audit_generated` Event Appended to Ledger

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #5 - "OBPI-0.19.0-05: `audit_generated` event appended to ledger"

**Status:** Completed

## Objective

Add an `audit_generated` ledger event factory function to `src/gzkit/ledger.py` and have `audit_cmd()` in `src/gzkit/cli.py` append this event to the ledger after successfully creating the AUDIT.md and AUDIT_PLAN.md artifacts, so that the audit lifecycle is recorded in the governance ledger and downstream consumers (status surfaces, artifact graph, reconciliation) can detect whether an ADR has been audited.

## Lane

**Lite** - Inherited from parent ADR-0.19.0-closeout-audit-processes (lite per ledger `adr_created` event).

> This OBPI adds an internal ledger event type and a `ledger.append()` call inside an existing command. It does not change CLI flags, exit codes, subcommand surface, or machine-readable output schemas. The ledger event is an internal governance record, not an external contract.

## Allowed Paths

- `src/gzkit/cli.py` - `audit_cmd()` function (line ~2634): add `ledger.append(audit_generated_event(...))` call after artifact creation succeeds
- `src/gzkit/ledger.py` - Add `audit_generated_event()` factory function following the existing pattern (e.g., `closeout_initiated_event()` at line ~208); optionally extend `_apply_graph_event_metadata()` to surface audit state in the artifact graph
- `tests/test_ledger.py` - Add tests for the `audit_generated_event()` factory function: correct event type, required fields, serialization round-trip
- `tests/test_audit_pipeline.py` - Add integration test verifying that `audit_cmd()` appends the `audit_generated` event to the ledger with correct ADR ID, artifact paths, and result summary

## Denied Paths

- `src/gzkit/commands/common.py` - No changes to shared CLI utilities
- `data/schemas/` - No new JSON schemas for this event (ledger events are schema-validated at the LedgerEvent model level)
- `docs/user/commands/audit.md` - No CLI contract change
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `audit_generated_event()` MUST be a module-level factory function in `src/gzkit/ledger.py` returning a `LedgerEvent` with `event="audit_generated"`.
2. REQUIREMENT: The event `id` field MUST be the canonical ADR identifier (e.g., `ADR-0.19.0-closeout-audit-processes`).
3. REQUIREMENT: The event `extra` dict MUST include `audit_file` (relative path to AUDIT.md), `audit_plan_file` (relative path to AUDIT_PLAN.md), and `passed` (boolean indicating whether all verification commands succeeded).
4. REQUIREMENT: `audit_cmd()` MUST call `ledger.append()` with the `audit_generated` event only after both AUDIT.md and AUDIT_PLAN.md have been written successfully and before the JSON/human output is rendered.
5. NEVER: The `audit_generated` event MUST NOT be appended during `--dry-run` mode.
6. NEVER: The `audit_generated` event MUST NOT be appended if the attestation blocker fires (exit 1 before artifact creation).
7. ALWAYS: The factory function MUST follow the existing pattern established by `closeout_initiated_event()`: positional `adr_id`, keyword-optional extras, returns `LedgerEvent`.

> STOP-on-BLOCKERS: if `LedgerEvent` model or `Ledger.append()` is unavailable, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- [ ] Related OBPIs: OBPI-0.19.0-02 (end-to-end audit pipeline), OBPI-0.19.0-04 (enriched audit report)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/ledger.py` contains `LedgerEvent` model (line ~47) and factory functions (lines 111-317)
- [ ] `src/gzkit/ledger.py` contains `Ledger.append()` method (line ~980)
- [ ] `src/gzkit/cli.py` contains `audit_cmd()` function (line ~2634)

**Existing Code (understand current state):**

- [ ] `src/gzkit/ledger.py` lines 208-222: `closeout_initiated_event()` — pattern to follow for new event factory
- [ ] `src/gzkit/ledger.py` lines 225-242: `audit_receipt_emitted_event()` — related audit event for reference
- [ ] `src/gzkit/cli.py` lines 2741-2774: AUDIT.md write and output rendering — insertion point for ledger append
- [ ] `tests/test_ledger.py` lines 1-23: existing test imports and pattern for event factory tests

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

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification: event factory exists and returns correct shape
uv run python -c "
from gzkit.ledger import audit_generated_event, LedgerEvent
e = audit_generated_event(
    adr_id='ADR-0.19.0-test',
    audit_file='docs/design/adr/pre-release/ADR-0.19.0-test/audit/AUDIT.md',
    audit_plan_file='docs/design/adr/pre-release/ADR-0.19.0-test/audit/AUDIT_PLAN.md',
    passed=True,
)
assert isinstance(e, LedgerEvent), 'must return LedgerEvent'
assert e.event == 'audit_generated', f'wrong event type: {e.event}'
assert e.id == 'ADR-0.19.0-test', f'wrong id: {e.id}'
d = e.model_dump()
assert d['audit_file'].endswith('AUDIT.md'), 'missing audit_file'
assert d['audit_plan_file'].endswith('AUDIT_PLAN.md'), 'missing audit_plan_file'
assert d['passed'] is True, 'missing passed'
print('PASS: audit_generated_event factory validated')
"

# Run specific tests
uv run -m unittest tests.test_ledger -v -k audit_generated
uv run -m unittest tests.test_audit_pipeline -v
```

## Acceptance Criteria

- [x] REQ-0.19.0-05-01: Given `src/gzkit/ledger.py`, when `audit_generated_event()` is called with `adr_id`, `audit_file`, `audit_plan_file`, and `passed`, then it returns a `LedgerEvent` with `event="audit_generated"`, `id=adr_id`, and extras containing all three fields.
- [x] REQ-0.19.0-05-02: Given a successful `gz audit ADR-X.Y.Z` run (not dry-run), when AUDIT.md and AUDIT_PLAN.md are written, then the ledger file contains a new `audit_generated` event with the correct ADR ID and `passed` reflecting whether all verification commands succeeded.
- [x] REQ-0.19.0-05-03: Given `gz audit ADR-X.Y.Z --dry-run`, when the command completes, then no `audit_generated` event is appended to the ledger.
- [x] REQ-0.19.0-05-04: Given an ADR without attestation (blocker fires at line ~2650), when `gz audit ADR-X.Y.Z` exits with code 1, then no `audit_generated` event is appended to the ledger.
- [x] REQ-0.19.0-05-05: Given the `audit_generated_event()` factory, when `model_dump()` is called on the result, then the serialized dict contains `schema`, `event`, `id`, `ts`, `audit_file`, `audit_plan_file`, and `passed` at the top level (extras flattened per `LedgerEvent._serialize`).

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
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
$ uv run -m unittest tests.test_ledger.TestAuditGeneratedEvent tests.test_audit_pipeline.TestAuditGeneratedLedgerEvent -v
test_event_type ... ok
test_extra_fields ... ok
test_passed_false ... ok
test_serialization_round_trip ... ok
test_attestation_blocker_no_audit_generated_event ... ok
test_audit_generated_event_in_ledger ... ok
test_audit_generated_passed_false_on_failure ... ok
test_dry_run_no_audit_generated_event ... ok
Ran 8 tests in 0.386s — OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed!
$ uv run gz typecheck
All checks passed!
$ uv run gz test
Ran 1060 tests in 14.196s — OK
```

### Value Narrative

Before this OBPI, `gz audit` created AUDIT.md and AUDIT_PLAN.md files but left no trace in the governance ledger. Downstream status surfaces (`gz adr status`, `gz state`) had no way to determine whether an ADR had been audited, and reconciliation tools could not verify audit completion programmatically. After this OBPI, every successful audit run appends an `audit_generated` event to the ledger, making audit completion a queryable, first-class lifecycle fact that status surfaces and reconciliation can consume.

### Key Proof

```text
$ uv run python -c "
from gzkit.ledger import audit_generated_event
e = audit_generated_event(
    adr_id='ADR-0.19.0-closeout-audit-processes',
    audit_file='docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/audit/AUDIT.md',
    audit_plan_file='docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/audit/AUDIT_PLAN.md',
    passed=True,
)
print(e.model_dump())
"
{'schema': 'gzkit.ledger.v1', 'event': 'audit_generated', 'id': 'ADR-0.19.0-closeout-audit-processes', 'ts': '2026-03-22T...', 'audit_file': 'docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/audit/AUDIT.md', 'audit_plan_file': 'docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/audit/AUDIT_PLAN.md', 'passed': True}
```

### Implementation Summary

- Files modified: `src/gzkit/ledger.py`, `src/gzkit/cli.py`, `tests/test_ledger.py`, `tests/test_audit_pipeline.py`
- Tests added: 8 (4 unit + 4 integration)
- Date completed: 2026-03-22
- Attestation status: Completed (human attested)
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff (Lite lane under Heavy parent ADR — human attestation required)
- Attestation: Completed
- Date: 2026-03-22

---

**Brief Status:** Completed

**Date Completed:** 2026-03-22

**Evidence Hash:** -
