# gz obpi lock check

Check if an OBPI is currently locked.

## Usage

```
gz obpi lock check OBPI-X.Y.Z-NN [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to check |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | OBPI is locked (prints holder info) |
| 1 | OBPI is free (not locked or lock expired) |

## Examples

```bash
gz obpi lock check OBPI-0.1.0-01
gz obpi lock check OBPI-0.1.0-01 --json
```

## JSON Output

When held:
```json
{
  "status": "held",
  "lock": { "obpi_id": "...", "agent": "...", ... },
  "elapsed_minutes": 15.2,
  "remaining_minutes": 104.8
}
```

When free:
```json
{
  "status": "free",
  "obpi_id": "OBPI-0.1.0-01"
}
```
