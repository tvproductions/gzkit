# gz obpi lock-claim

Claim an OBPI work lock for multi-agent coordination.

## Usage

```
gz obpi lock-claim OBPI-X.Y.Z-NN [--ttl MINUTES] [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to lock |
| `--ttl MINUTES` | Lock time-to-live in minutes (default: 120) |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock claimed successfully |
| 1 | Lock conflict (another agent holds it) |
| 2 | System error |

## Examples

```bash
gz obpi lock-claim OBPI-0.1.0-01
gz obpi lock-claim OBPI-0.1.0-01 --ttl 240
gz obpi lock-claim OBPI-0.1.0-01 --json
```
