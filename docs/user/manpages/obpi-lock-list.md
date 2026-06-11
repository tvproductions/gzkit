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
- Reaping is auditable (OBPI-0.0.41-03): each reaped lock writes an
  `abandoned_by_reaper` register entry to `.gzkit/handoffs/` and emits an
  `obpi_lock_released` ledger event citing that entry's `handoff_path`. A lock
  whose register-entry write fails is preserved (fail-closed), not silently
  deleted.

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
