# gz obpi lock-release

Release an OBPI work lock.

## Usage

```
gz obpi lock-release OBPI-X.Y.Z-NN [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to release |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock released or not found |
| 2 | System error |

## Examples

```bash
gz obpi lock-release OBPI-0.1.0-01
gz obpi lock-release OBPI-0.1.0-01 --json
```
