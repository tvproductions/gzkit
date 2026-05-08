# gz obpi lock list

List active OBPI work locks.

## Usage

```
gz obpi lock list [--adr ADR-X.Y.Z] [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--adr ADR-X.Y.Z` | Filter locks by parent ADR |
| `--json` | Machine-readable JSON output |

## Runtime Behavior

- Automatically reaps expired locks before listing
- Shows remaining TTL for each active lock
- Emits `obpi_lock_reaped` event for each expired lock removed

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | System error |

## Examples

```bash
gz obpi lock list
gz obpi lock list --adr ADR-0.1.0
gz obpi lock list --json
```

## JSON Output

```json
{
  "active_locks": [
    {
      "obpi_id": "OBPI-0.1.0-01",
      "agent": "agent-1",
      "claimed_at": "2026-04-05T14:30:00Z",
      "remaining_minutes": 95.5
    }
  ],
  "reaped": 2,
  "total_active": 1
}
```

## Deprecated

Use `gz obpi lock list` instead of the legacy `gz obpi lock-status`
form.
