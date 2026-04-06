# gz obpi lock release

Release an OBPI work lock.

## Usage

```
gz obpi lock release OBPI-X.Y.Z-NN [--force] [--agent NAME]
[--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to release |
| `--force` | Release lock even if held by another agent |
| `--agent NAME` | Agent identity (default: from environment) |
| `--json` | Machine-readable JSON output |

## Runtime Behavior

- Removes lock file from `.gzkit/locks/obpi/`
- Validates ownership (release only allowed by lock holder unless
  `--force`)
- Emits `obpi_lock_released` event to ledger for audit trail

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock released or not found |
| 1 | Ownership mismatch (use `--force` to override) |
| 2 | System error |

## Examples

```bash
gz obpi lock release OBPI-0.1.0-01
gz obpi lock release OBPI-0.1.0-01 --agent my-agent
gz obpi lock release OBPI-0.1.0-01 --force --json
```

## Deprecated

Use `gz obpi lock release` instead of the legacy `gz obpi
lock-release` form.
