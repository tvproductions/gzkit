# Plan: OBPI-0.0.71-01-completion-repudiation-event

## OBPI Reference

**OBPI:** `OBPI-0.0.71-01-completion-repudiation-event`
**Parent ADR:** `ADR-0.0.71-completion-repudiation`
**Lane:** Heavy
**ADR Checklist Item #1:** `obpi_completion_repudiated` ledger event model + factory + `ledger.json` schema entry + state-resolution semantics (flip ledger_completed, set repudiated, NOT withdrawn; genuine re-completion clears repudiated); unit tests

## Context

gzkit has an append-only ledger and a sacrosanct Gate-5, but no governed lever to reverse a fabricated completion attestation. The only counter-event (`obpi_withdrawn`) is permanent retirement. ADR-0.0.71 adds a first-class repudiation primitive: an `obpi_completion_repudiated` ledger event that reverses a completion without the sticky `withdrawn` retirement, so the OBPI stays live for genuine re-completion.

This OBPI delivers the engine layer (event model + factory + schema + state-resolution). The CLI verb (`gz obpi repudiate`) is OBPI-02.

## Files

### Create
- `tests/test_completion_repudiation.py` — TDD unit tests for model validation + state-resolution semantics

### Modify
- `src/gzkit/events.py` — add `ObpiCompletionRepudiatedEvent` model + add to `TypedLedgerEvent` union
- `src/gzkit/ledger_events.py` — add `obpi_completion_repudiated_event()` factory
- `src/gzkit/ledger.py` — add `_apply_obpi_completion_repudiated_metadata()` + wire into `_apply_graph_event_metadata`; also clear `repudiated` in `_apply_obpi_receipt_metadata` on genuine re-completion
- `src/gzkit/schemas/ledger.json` — add `obpi_completion_repudiated` event schema entry

## Steps

### Step 1: Write RED tests (tests/test_completion_repudiation.py)

Write all tests **before any source changes** (TDD RED phase). Tests derive from brief REQs:

- `TestObpiCompletionRepudiatedEventModel` (covers REQ-01, REQ-02):
  - `test_empty_attestor_fails_closed` — `Field(min_length=1)` on `attestor` raises `ValidationError`
  - `test_empty_reason_fails_closed` — `Field(min_length=1)` on `reason` raises `ValidationError`
  - `test_invalid_cause_rejected` — `Literal[...]` discriminant rejects unknown cause values
  - `test_valid_construction_round_trips` — valid event serializes and deserializes correctly
  - `test_cause_enum_exhaustive` — all three valid cause values construct without error

- `TestObpiCompletionRepudiatedStateResolution` (covers REQ-03, REQ-04, REQ-05):
  - `test_repudiation_flips_ledger_completed_false` — applying event sets `ledger_completed=False`, `repudiated=True`
  - `test_repudiation_sets_repudiated_reason` — `repudiated_reason` is populated
  - `test_repudiation_does_not_set_withdrawn` — `withdrawn` remains absent/False
  - `test_genuine_recompletion_clears_repudiated` — subsequent `obpi_receipt_emitted` with `attested_completed` clears `repudiated`
  - `test_repudiated_obpi_visible_in_default_graph` — repudiated OBPI is NOT filtered by `_hide_withdrawn_obpis`

- `TestObpiCompletionRepudiatedSchemaRoundTrip` (covers REQ-06):
  - `test_schema_entry_exists` — `obpi_completion_repudiated` key present in `LEDGER_SCHEMA["events"]`
  - `test_model_roundtrip_validate_deserialize` — event serializes to dict matching schema fields

### Step 2: Add `ObpiCompletionRepudiatedEvent` to events.py

Insert after `ObpiWithdrawnEvent` (line ~268):

```python
class ObpiCompletionRepudiatedEvent(_EventBase):
    """obpi_completion_repudiated event — governed reversal of fabricated Gate-5 (ADR-0.0.71)."""

    event: Literal["obpi_completion_repudiated"]
    repudiated_receipt: str
    cause: Literal["model-induced-fabrication", "operator-error", "verification-invalid"]
    attestor: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
```

Add `ObpiCompletionRepudiatedEvent` to the `TypedLedgerEvent` union (after `ObpiWithdrawnEvent` in the union list, ~line 510).

### Step 3: Add factory to ledger_events.py

Insert after `obpi_withdrawn_event`:

```python
def obpi_completion_repudiated_event(
    obpi_id: str,
    parent: str,
    repudiated_receipt: str,
    cause: str,
    attestor: str,
    reason: str,
) -> LedgerEvent:
    """Create an obpi_completion_repudiated event."""
    return LedgerEvent(
        event="obpi_completion_repudiated",
        id=obpi_id,
        parent=parent,
        extra={
            "repudiated_receipt": repudiated_receipt,
            "cause": cause,
            "attestor": attestor,
            "reason": reason,
        },
    )
```

### Step 4: Add state-resolution to ledger.py

**4a.** Add `_apply_obpi_completion_repudiated_metadata` static method after `_apply_obpi_withdrawn_metadata`:

```python
@staticmethod
def _apply_obpi_completion_repudiated_metadata(
    graph: dict[str, dict[str, Any]],
    canonical_id: str,
    event: LedgerEvent,
) -> None:
    if event.event != "obpi_completion_repudiated" or canonical_id not in graph:
        return
    if graph[canonical_id].get("type") != "obpi":
        return
    graph[canonical_id]["ledger_completed"] = False
    graph[canonical_id]["repudiated"] = True
    graph[canonical_id]["repudiated_reason"] = event.extra.get("reason")
```

**4b.** Wire into `_apply_graph_event_metadata` — add call after `_apply_obpi_withdrawn_metadata`:

```python
cls._apply_obpi_completion_repudiated_metadata(graph, canonical_id, event)
```

**4c.** In `_apply_obpi_receipt_metadata`, inside the `if obpi_completion in {"completed", "attested_completed"}:` block, add:

```python
graph[canonical_id]["repudiated"] = False
graph[canonical_id]["repudiated_reason"] = None
```

This ensures genuine re-completion clears `repudiated` (Boundary Invariant 5).

### Step 5: Add schema entry to ledger.json

Add `obpi_completion_repudiated` entry to the `events` object (after `obpi_completion_uncovered_accept`):

```json
"obpi_completion_repudiated": {
  "required": ["repudiated_receipt", "cause", "attestor", "reason"],
  "properties": {
    "repudiated_receipt": {
      "type": "string",
      "min_length": 1
    },
    "cause": {
      "type": "string",
      "enum": ["model-induced-fabrication", "operator-error", "verification-invalid"]
    },
    "attestor": {
      "type": "string",
      "min_length": 1
    },
    "reason": {
      "type": "string",
      "min_length": 1
    }
  }
}
```

### Step 6: GREEN phase — run tests and fix

```bash
uv run -m unittest tests.test_completion_repudiation -v
```

Fix until all tests pass.

### Step 7: Quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_completion_repudiation -v
```

## Notes

- `destination-in-mind`: The approach was determined from the brief before writing this plan — `ObpiWithdrawnEvent` is the direct structural sibling and the factory/state-resolver pattern is identical.
- `rejected-alternatives`: No alternative to the `_EventBase` subclass approach was seriously considered since every other OBPI event uses it. Considered using a standalone `obpi_id` field instead of relying on `_EventBase.id`, but the existing withdrawal pattern uses `id` for the subject OBPI, so consistency wins.
- The `repudiated` flag in graph state is NEW — no existing code references it yet. `_hide_withdrawn_obpis` checks `info.get("withdrawn")` only, so repudiated OBPIs will remain visible without any changes to state.py (REQ-05 satisfied implicitly).
- `_apply_obpi_receipt_metadata` already handles `ledger_completed=True` on `attested_completed`; we add a `repudiated` clear in the same block for invariant 5.
