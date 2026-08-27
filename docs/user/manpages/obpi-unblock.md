# gz obpi unblock

Record the operator ruling that releases a blocked OBPI.

## Usage

```bash
gz obpi unblock OBPI-<X.Y.Z-NN> --ruling "..." --operator "..."
gz obpi unblock OBPI-<X.Y.Z-NN> --ruling "..." --operator "..." --dry-run
```

## Description

Records an `obpi_unblocked` event, clearing the block written by
`gz obpi block` and restoring `gz obpi pipeline` launch for the OBPI (GHI #887).

Block and unblock compose as forward corrective events over the append-only
ledger — current state is the net of the sequence, never an edit (AGENTS.md
Never #2). An OBPI may be blocked again after a ruling; that is ordinary, and
the latest event wins.

`--ruling` carries the operator's decision **verbatim**, per AGENTS.md
§ Attestation: the agent seats the operator's words and never rewrites them.
Recording the ruling is what makes the block's discharge readable from Layer 2
rather than only from the session that produced it — the same durability
argument GHI #676 made for the Step-4b adversary verdict.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `obpi` | Yes | OBPI identifier (e.g. OBPI-0.35.0-02) |

## Flags

| Flag | Description |
|------|-------------|
| `--ruling` | The operator's decision, verbatim (non-empty) |
| `--operator` | Who ruled (non-empty) |
| `--dry-run` | Show the event without writing it |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (unknown OBPI, empty ruling or operator) |

## Examples

```bash
# Release the block once the operator has ruled
uv run gz obpi unblock OBPI-0.35.0-02 \
  --ruling "amend REQ-04; append without reserializing is a separate defect" \
  --operator "g0"
```

## See Also

- [`obpi-block`](obpi-block.md) — record that an OBPI awaits a human ruling
- [`obpi-pipeline`](obpi-pipeline.md) — the launch surface the block gates
