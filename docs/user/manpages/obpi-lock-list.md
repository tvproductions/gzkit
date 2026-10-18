# gz obpi lock list

List held OBPI work locks, marking any whose lease has expired.

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

- An expired work lock stays held: its expiry is booked once as
  `obpi_lock_lease_expired` and it is listed as `LEASE EXPIRED` (`"expired": true`
  in JSON), never evicted (operator ruling 2026-10-18). It is freed by its holder's
  completion or by `gz obpi lock release <obpi> --force --abandon <category>:<reason>`
  on the operator's word.
- Shows elapsed time and TTL for each held lock
- The one lock still reaped is the orphan `mx-session` lock, whose hangar is no
  longer open; it is reported under `reaped`. Reaping stays auditable
  (OBPI-0.0.41-03): it writes an `abandoned_by_reaper` register entry to
  `.gzkit/locks/exchange/` and emits an `obpi_lock_released` ledger event citing that
  entry's `handoff_path`; if the register-entry write fails the lock is preserved.

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
      "obpi_id": "mx-session",
      "agent": "claude-code-e6800367",
      "pid": 69162,
      "session_id": "e6800367-eb28-4b68-9624-65d94f7cdf17",
      "claimed_at": "2026-10-18T16:50:05.726480+00:00",
      "branch": "main",
      "ttl_minutes": 1440,
      "expired": false
    }
  ],
  "reaped": [],
  "count": 1
}
```
