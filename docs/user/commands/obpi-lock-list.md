# gz obpi lock list

List active OBPI work locks after reaping expired ones.

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
- Shows elapsed time and TTL for each active lock
- Reports reaped locks in JSON output

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
  "locks": [
    {
      "obpi_id": "OBPI-0.1.0-01",
      "agent": "claude-code",
      "claimed_at": "2026-04-05T14:30:00Z",
      "ttl_minutes": 120
    }
  ],
  "reaped": [],
  "count": 1
}
```

## Deprecated

The legacy `gz obpi lock-status` command is a deprecated alias for
this command. Use `gz obpi lock list` instead.
