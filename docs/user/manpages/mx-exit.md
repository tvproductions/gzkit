# gz mx exit

Close the Maintenance Hangar — hard gate.

## Usage

<!-- gz-validate-skip: command-shape -->
```bash
gz mx exit --attestor ATTESTOR
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--attestor ATTESTOR` | Operator identity who signs airworthiness (required; never an agent) |

## Runtime Behavior

- Validates that `--attestor` is non-empty; fails closed (exit 1) if empty or whitespace-only —
  no marker is cleared, no ledger event is emitted.
- Checks the hangar is open (`marker.is_active`). Fails closed (exit 1) if not.
- Temporarily removes the marker file so `checkpoint.resolve()` sees no active session —
  every guard emits at its real `GZ_<LEVEL>` severity (no advisory demotion).
- Runs every guard at full strength against the project.
- If any guard is red: restores the marker, exits 3 — hangar stays open.
- If all guards are green: fires the airlock-OUT membrane (co-equal with airlock-IN, ADR-0.33.0)
  **after** the hard guard-gate passes and **before** the close signature — it is **additive** to
  the hard gate, never a replacement. It books one `airlock_out` L2 event and surfaces any drift
  findings as warnings; it is **diagnostic-only** and never blocks the close (real-entry accounting
  deferred). Then writes one `mx_session_closed` ledger event (the marker stays removed); the
  operator's `--attestor` is the airworthiness signature.

**There is no `--force` flag.** You cannot narrow your way out of a red guard.
**Exit is the ONLY path that clears the marker.** A marker removed without a matching
`mx_session_closed` event is a detected dangling state (ADR-0.0.74 Boundary Invariant #4).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Hangar closed successfully |
| 1 | Validation failure: empty attestor or no active session |
| 2 | System/IO error |
| 3 | Guards reported red — hangar remains open |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Close the hangar after completing maintenance work
gz mx exit --attestor g0
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- [`gz mx enter`](mx-enter.md) — Open the Maintenance Hangar
- ADR-0.0.74: MX Mode — Maintenance Hangar (design and decision record)
