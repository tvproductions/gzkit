# Plan: OBPI-0.0.64-01-task-id-worklog-schema-additive

**OBPI:** OBPI-0.0.64-01-task-id-worklog-schema-additive
**Parent ADR:** ADR-0.0.64-task-envelope-and-planning-decomposition
**Lane:** Heavy / Foundation
**Date:** 2026-05-28

## Destination-in-mind (plan-before-exploration disclosure, Step 6a)

Before investigation I knew: add `task_id: str | None = None` to 8 Pydantic
event models in `events.py` and mirror in `ledger.json`. Investigation
confirmed all 8 exist in both surfaces with their exact class/property names.
No surprises; approach unchanged.

## Rejected alternatives (plan-before-exploration disclosure, Step 6a)

1. **Make field required** — would break 7,897 pre-restoration ledger events;
   rejected per ADR Alternative 3.
2. **Add a new abstract mixin `_WorklogEventBase`** — extra indirection for a
   single optional field; rejected; simpler to add field on each class directly.
3. **JSON-schema `anyOf` null union** — `["string", "null"]` type array is the
   accepted nullable form in the existing schema; `anyOf` is heavier; rejected.

## Context

ADR-0.0.64 Decision item 1: nullable `task_id` field on 8 worklog event types
enables per-labor-unit TASK attribution to propagate with every governance
event. This OBPI delivers the schema channel only; OBPI-02 (decorator),
OBPI-03 (subdivision CLI), OBPI-04 (validator), and OBPI-05 (readback) layer
on top.

## Files

**Modified:**
- `src/gzkit/events.py` — add `task_id: str | None = None` to 8 event models
- `src/gzkit/schemas/ledger.json` — add `task_id` nullable property to 8 event entries

**Created:**
- `tests/governance/test_task_id_worklog_field.py` — REQ-derived @covers tests

## Steps

### Step 1: Write RED tests (TDD discipline)

Create `tests/governance/test_task_id_worklog_field.py` with tests derived
from the 6 REQs. Tests must fail before implementation (RED phase).

REQ-01: Each of 8 event models accepts `task_id=None` AND a valid TASK ID
REQ-02: Each of 8 event models rejects unknown fields (extra="forbid" guard)
REQ-03: `ledger.json` validates legacy events (no task_id) AND new-shape events
REQ-04: The 4 TASK-boundary models are NOT changed (regression guard)
REQ-05: JSON schema `task_id` property is not in the event's `required` array
REQ-06: STRUCTURAL-FENCE — no change to auto_start_obpi_tasks / auto_complete_obpi_tasks

### Step 2: Add `task_id` field to 8 Pydantic event models in `src/gzkit/events.py`

Target classes (verified in file):
- `ArtifactEditedEvent` (line 114)
- `AttestedEvent` (line 122)
- `GateCheckedEvent` (line 131)
- `AuditReceiptEmittedEvent` (line 151)
- `ArtifactRenamedEvent` (line 172)
- `ObpiCompletionUncoveredAcceptEvent` (line 264)
- `IntrinsicComplexityAttestationEvent` (line 355)
- `CompositionRenderedEvent` (line 391)

Field shape (per `.gzkit/rules/models.md` + `.gzkit/rules/pythonic.md`):
```python
task_id: str | None = Field(default=None, description="TASK identifier for worklog attribution")
```

DO NOT touch:
- `_TaskEventBase` (line 314) — TASK-boundary events already carry required `task_id`
- `TaskStartedEvent`, `TaskCompletedEvent`, `TaskBlockedEvent`, `TaskEscalatedEvent`

### Step 3: Add `task_id` property to 8 event entries in `src/gzkit/schemas/ledger.json`

For each of the 8 event entries in `d["events"]`:
- Add `"task_id": {"type": ["string", "null"]}` to the `"properties"` dict
- Confirm `task_id` is NOT in the event's `"required"` array (or that array stays unchanged)

Target event keys: `artifact_edited`, `attested`, `gate_checked`,
`audit_receipt_emitted`, `artifact_renamed`, `obpi_completion_uncovered_accept`,
`intrinsic-complexity-attestation`, `composition_rendered`

### Step 4: Run GREEN (confirm tests pass)

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.governance.test_task_id_worklog_field -v
```

### Step 5: Full quality suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
```

### Step 6: Present OBPI Acceptance Ceremony

Human attestation gate per ADR-0.0.36 (universal).

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/governance/test_task_id_worklog_field.py
uv run gz validate --documents

# Schema-additive proof
uv run python -c "from gzkit.events import ArtifactEditedEvent; print(ArtifactEditedEvent.model_fields['task_id'])"
uv run python -c "import json,pathlib; s=json.loads(pathlib.Path('src/gzkit/schemas/ledger.json').read_text()); print('task_id present' if 'task_id' in str(s) else 'MISSING')"
```

## Notes

- All 8 target event classes confirmed present in `src/gzkit/events.py`
- All 8 target event keys confirmed in `src/gzkit/schemas/ledger.json`
- 12 sibling-ADR scope collisions flagged by plan audit are advisory only —
  all sibling OBPIs are `attested_completed`; the surfaces are legitimately shared
- REQ-06 is STRUCTURAL-FENCE — verified at plan-time (no task.py edits planned);
  regression guard via grep in test confirms no change to auto_start/complete
