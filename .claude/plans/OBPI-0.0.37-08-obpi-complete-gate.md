# Plan: OBPI-0.0.37-08 — gz obpi complete fail-close gate

**OBPI:** OBPI-0.0.37-08-obpi-complete-gate
**ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy
**Context:** OBPI-06 (brief reconcile CLI) and OBPI-07 (pipeline Stage 1 gate) are landed.

## Context

`gz obpi complete` currently allows Stage 5 completion even when no `brief_reconciled`
ledger event exists for the OBPI, or when the most recent receipt is stale/drifted.
This OBPI wires the Stage 5 fail-close gate (the CIC-2 in-flight-drift-catching half):

- Missing receipt → exit 3
- Stale receipt (allowed-path mtime newer than receipt_ts) → exit 3 naming drifted path
- Fresh receipt but `has_drift=True` → exit 3 naming drifted dimensions
- Escape hatch `--accept-stale-reconciliation --reason "<text>"` (≥10 chars) → emits
  `brief_reconcile_drift_overridden` ledger event BEFORE completion, then completes normally

The `--accept-stale-reconciliation` check is in-function (mirrors `--accept-uncovered`
precedent); `--reason` is a companion flag, not a nested argparse group.

## Files

- `src/gzkit/commands/obpi_complete.py` — new `_enforce_reconcile_receipt_gate()` + wire
- `src/gzkit/governance/events.py` — new `brief_reconcile_drift_overridden_event()` function
- `.gzkit/schemas/ledger_events.json` — add `brief_reconcile_drift_overridden` event type
- `tests/commands/test_obpi_complete_reconcile_gate.py` — 6 REQ-derived unit tests
- `features/brief_reconcile.feature` — Stage 5 + escape-hatch scenarios @REQ-0.0.37-08-*
- `src/gzkit/cli/parser_artifacts.py` — `--accept-stale-reconciliation` + `--reason` flags
- `docs/user/manpages/obpi-complete.md` — document new flags
- `docs/user/runbook.md` — "2am Stage 5 escape" runbook entry
- `docs/design/adr/.../obpis/OBPI-0.0.37-08-obpi-complete-gate.md` — this brief

## Steps

### Step 1: Register new ledger event schema

In `.gzkit/schemas/ledger_events.json`, append the `brief_reconcile_drift_overridden`
event type with required fields:
`brief_id, override_ts, attestor, reason, original_receipt_id (opt), original_drift_dimensions (array)`.

### Step 2: Add event factory to events.py

In `src/gzkit/governance/events.py`, add:
```python
def brief_reconcile_drift_overridden_event(
    *,
    brief_id: str,
    attestor: str,
    reason: str,
    original_receipt_id: str | None,
    original_drift_dimensions: list[str],
) -> LedgerEvent
```

### Step 3: Add reconcile receipt gate in obpi_complete.py

Add `_enforce_reconcile_receipt_gate()` that:
1. Reads `.gzkit/ledger.jsonl` for most recent `brief_reconciled` event matching `obpi_id`
2. If absent → `_fail(exit_code=3)` with "Completion blocked: no `brief_reconciled` receipt"
3. If stale via `is_receipt_fresh` → `_fail(exit_code=3)` naming drifted path
4. If fresh but `has_drift=True` → `_fail(exit_code=3)` naming drifted dimensions
5. If `accept_stale_reconciliation=True` → emit `brief_reconcile_drift_overridden_event`
   to ledger and return (bypass the fail-close checks above)

### Step 4: Wire gate into obpi_complete_cmd

Add params `accept_stale_reconciliation: bool = False` and
`accept_stale_reconciliation_reason: str | None = None` to `obpi_complete_cmd`.

In-function pairing check: if `accept_stale_reconciliation` and not
`accept_stale_reconciliation_reason` (or len < 10): `_fail` with
"--accept-stale-reconciliation requires --reason '<text>' (min 10 chars)".

Call `_enforce_reconcile_receipt_gate(...)` right after `_resolve_and_validate`,
before the security gate.

### Step 5: Add argparse flags in parser_artifacts.py

After `--accept-security-floor`, add:
```
--accept-stale-reconciliation   (store_true, dest=accept_stale_reconciliation)
--reason                        (default=None, dest=accept_stale_reconciliation_reason)
```
Pass both to `obpi_complete_cmd`.

### Step 6: Write 6 unit tests (TDD — RED first)

New file `tests/commands/test_obpi_complete_reconcile_gate.py`:

1. REQ-01: missing receipt → exit 3 + "Completion blocked: no `brief_reconciled` receipt"
2. REQ-02: stale receipt (mtime > receipt_ts) → exit 3 + stale path name
3. REQ-03: fresh receipt has_drift=True → exit 3 + "has_drift"
4. REQ-04 (pass case): fresh has_drift=False → gate passes
5. REQ-04 (flag check): --accept-stale-reconciliation without --reason → error
6. REQ-05: --accept-stale-reconciliation --reason "10+ chars" → emits override event, completes

Each test decorates with `@covers("REQ-0.0.37-08-NN")`.

### Step 7: Add BDD scenarios to brief_reconcile.feature

Append scenarios tagged `@REQ-0.0.37-08-01` through `@REQ-0.0.37-08-07`.

### Step 8: Update docs

- `docs/user/manpages/obpi-complete.md`: document `--accept-stale-reconciliation --reason`
- `docs/user/runbook.md`: add "2am Stage 5 escape" runbook entry

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_obpi_complete_reconcile_gate -v
uv run mkdocs build --strict
uv run python -c "
events_txt = open('.gzkit/schemas/ledger_events.json').read()
assert 'brief_reconcile_drift_overridden' in events_txt
print('REQ-07 OK')
"
```
