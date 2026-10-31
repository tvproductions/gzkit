# gz mx repair

Repair an unreadable, missing or unbound marker. Runs no guard.

## Usage

<!-- gz-validate-skip: command-shape -->
```bash
gz mx repair --attestor ATTESTOR
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--attestor ATTESTOR` | Operator identity repairing the marker (required; never an agent) |

## Runtime Behavior

The condition is on only when the marker is present, parses, is bound to a still-open
`mx_session_opened` event and is not exiting. Anything else is normal operation at full
strength, and this is the recovery that announcement names.

| The marker reads | Open sessions | What the repair does |
|---|---|---|
| unreadable, missing, naming another session, or left `exiting` by a killed exit | one | Rewrites it from that session's `mx_session_opened` event |
| unreadable, naming a closed session, or left `exiting` | none | Removes it |
| on | any | Nothing |
| missing | none | Nothing |
| anything it would change | two or more | Refuses with exit 1 |

- Validates that `--attestor` is non-empty, and fails closed (exit 1) otherwise. Rewriting a
  marker lowers protection again, so it is the operator's act.
- Each change books one `mx_marker_repaired` ledger event carrying the cause and the action.
- Do not run it while `gz mx exit` is running: it would clear the `exiting` hold.
- Runs **no guard** and leaves the `mx-session` lock and the session's lease alone.
- The marker is committed, so the repaired file is a working-tree change to commit.

Operator ruling 2026-10-31, verbatim *"b"* (GHI #1273).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Marker repaired, or nothing to repair |
| 1 | Validation failure: empty attestor or more than one open session |
| 2 | System/IO error |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# The banner reported an unreadable marker
gz mx repair --attestor g0
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- [`gz mx exit`](mx-exit.md) — the full-strength exit gate
