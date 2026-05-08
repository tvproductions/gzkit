# gz obpi lock claim

Claim an OBPI work lock for multi-agent coordination.

## Usage

```
gz obpi lock claim OBPI-X.Y.Z-NN [--ttl MINUTES] [--agent NAME]
[--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to lock |
| `--ttl MINUTES` | Lock time-to-live in minutes (default: 120) |
| `--agent NAME` | Agent identity (default: from environment) |
| `--json` | Machine-readable JSON output |

## Runtime Behavior

- Creates a lock file in `.gzkit/locks/obpi/` with timestamp and TTL
- Emits `obpi_lock_claimed` event to ledger for audit trail
- Returns error if lock already held by another agent

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock claimed successfully |
| 1 | Lock conflict (another agent holds it) |
| 2 | System error |

## Examples

```bash
gz obpi lock claim OBPI-0.1.0-01
gz obpi lock claim OBPI-0.1.0-01 --ttl 240
gz obpi lock claim OBPI-0.1.0-01 --agent my-agent --json
```

## Deprecated

Use `gz obpi lock claim` instead of the legacy `gz obpi lock-claim`
form.
