# gz mx enter

Open the Maintenance Hangar (MX mode).

## Usage

<!-- gz-validate-skip: command-shape -->
```bash
gz mx enter --reason REASON --attestor ATTESTOR [--scope ADR_OR_OBPI ...]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--reason REASON` | Reason for entering MX mode (required; must be non-empty) |
| `--attestor ATTESTOR` | Operator identity (required; never an agent — only operators may open the hangar) |
| `--scope ADR_OR_OBPI ...` | ADRs/OBPIs under inspection (optional; 0 or more) |

## Runtime Behavior

- Validates that `--reason` and `--attestor` are non-empty; fails closed (exit 1) if either is empty
  or whitespace-only — no marker is written, no ledger event is emitted.
- Checks the hangar is not already open (`marker.is_active`). Fails closed (exit 1) if it is.
- Acquires a session lock on the `lock_manager` token rail (`mx-session` key) to serialize
  concurrent entry attempts (ADR-0.0.74 Decision #4 — token-rail/lock_manager).
- Writes the marker file (`.gzkit/mx.json`) with `session_id`, `opened_at`, `reason`,
  `attestor`, and `inspection_scope`.
- Writes one `mx_session_opened` ledger event, binding the marker to the ledger
  (anti-contrivance: a hand-created marker with no matching ledger event is void).
- Emits a success message with `session_id` and `attestor`.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Hangar opened successfully |
| 1 | Validation failure: empty input, hangar already active, or concurrent entry |
| 2 | System/IO error |
| 3 | Policy breach |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Open the hangar for ADR-0.0.74 repair work
gz mx enter --reason "re-true ledger-proof locks under ADR-0.0.74" --attestor g0

# Open with explicit inspection scope
gz mx enter --reason "repair marker binding" --attestor g0 --scope ADR-0.0.74 OBPI-0.0.74-04

# Multiple scope items
gz mx enter --reason "broad repair" --attestor g0 --scope ADR-0.0.74 ADR-0.0.73 OBPI-0.0.74-02
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- ADR-0.0.74: MX Mode — Maintenance Hangar (design and decision record)
