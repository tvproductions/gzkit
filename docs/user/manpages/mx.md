# gz mx

Maintenance Hangar (MX) mode operations.

## Synopsis

<!-- gz-validate-skip: command-shape -->
```bash
gz mx <subcommand> [OPTIONS]
```

## Subcommands

### enter

Open the Maintenance Hangar.

<!-- gz-validate-skip: command-shape -->
```bash
gz mx enter --reason REASON --attestor ATTESTOR [--scope ADR_OR_OBPI ...]
```

Sets the marker file, writes one `mx_session_opened` ledger event, and captures the
inspection scope. The marker's presence means MX==TRUE — most governance guards drop to
advisory. gate5_invariants and the PRIME DIRECTIVE still bind.

**Requires an operator-supplied `--attestor`.** Agents cannot open the hangar
autonomously; only an operator may initiate an MX session (ADR-0.0.74 Decision #4).

Empty or whitespace-only `--reason` or `--attestor` fails closed with exit 1 — no
marker is written, no ledger event is emitted.

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--reason REASON` | enter | Reason for entering MX mode (required; must be non-empty) |
| `--attestor ATTESTOR` | enter | Operator identity; never an agent (required) |
| `--scope ADR_OR_OBPI ...` | enter | ADRs/OBPIs under inspection (optional; 0 or more) |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Open the hangar for ADR-0.0.74 repair work
gz mx enter --reason "re-true ledger-proof locks under ADR-0.0.74" --attestor g0

# Open with explicit inspection scope
gz mx enter --reason "repair marker binding" --attestor g0 --scope ADR-0.0.74 OBPI-0.0.74-04
```

## Behavior

1. Validates `--reason` and `--attestor` are non-empty. Fails closed (exit 1) if either is empty.
2. Checks the hangar is not already open (`marker.is_active`). Fails closed (exit 1) if it is.
3. Acquires a session lock on the `lock_manager` token rail (`mx-session` key) to serialize
   concurrent entry attempts.
4. Writes the marker file (`.gzkit/mx.json`) with `session_id`, `opened_at`, `reason`,
   `attestor`, and `inspection_scope`.
5. Writes one `mx_session_opened` ledger event (binds the marker anti-contrivance: a
   hand-created marker with no matching ledger event is void).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Hangar opened successfully |
| 1 | Validation failure: empty input, hangar already active, or concurrent entry |
| 2 | System/IO error |
| 3 | Policy breach |

## Related

- ADR-0.0.74: MX Mode — Maintenance Hangar (design and decision record)
- `gz validate --documents`: verify governance artifact integrity
