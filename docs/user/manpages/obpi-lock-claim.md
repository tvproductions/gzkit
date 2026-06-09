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

- Creates a lock file in `.gzkit/locks/obpi/` with timestamp and TTL,
  using exclusive-creation (`open(path, "x")`) to atomically reject
  concurrent claim attempts (ADR-0.0.41 — token-block discipline)
- Emits `obpi_lock_claimed` event to ledger for audit trail
- Returns error if lock already held by another agent OR if a
  concurrent claimer won the race to write the lock file first

## Race-condition interlock

Two concurrent `gz obpi lock claim` invocations on the same `obpi_id`
cannot both succeed. The underlying `lock_manager.write_lock` uses
exclusive-creation; the second writer receives `FileExistsError` which
the claim command surfaces as `status: conflict` (exit 1) with the
actual race-winner's identity in the holder payload.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock claimed successfully |
| 1 | Lock conflict (another agent holds it OR race winner wrote first) |
| 2 | System error |

## Examples

```bash
gz obpi lock claim OBPI-0.1.0-01
gz obpi lock claim OBPI-0.1.0-01 --ttl 240
gz obpi lock claim OBPI-0.1.0-01 --agent my-agent --json
```
