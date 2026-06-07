# gz obpi lock release

Release an OBPI work lock.

## Usage

```
gz obpi lock release OBPI-X.Y.Z-NN [--force] [--agent NAME]
[--abandon CATEGORY:REASON] [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to release |
| `--force` | Release lock even if held by another agent |
| `--agent NAME` | Agent identity (default: from environment) |
| `--abandon CATEGORY:REASON` | Record abandonment with degenerate handoff (see below) |
| `--json` | Machine-readable JSON output |

## Runtime Behavior

- Removes lock file from `.gzkit/locks/obpi/`
- Validates ownership (release only allowed by lock holder unless
  `--force`)
- Emits `obpi_lock_released` event to ledger for audit trail

## `--abandon` flag (token-block discipline, ADR-0.0.41)

`--abandon <category>:<reason>` records the lock release as an
abandonment and writes a degenerate handoff under `.gzkit/handoffs/`.
The ledger event then carries `handoff_path` pointing at the written
register entry, closing the audit-coupling gap the token-block
doctrine names. The colon delimits category and reason; whitespace
around the category is rejected at parse time.

### Closed category enum

The category is a CLOSED enum (source of truth:
`.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1). Free-text
categories are rejected at parse time (exit 1).

| Category | When to use |
|----------|-------------|
| `network_loss` | Session network interruption; agent unable to gracefully suspend and create register entry |
| `external_blocker` | External service/dependency failure blocking normal completion |
| `wrong_obpi_claimed` | Agent claimed a lock intended for a different OBPI; discovered in release window |
| `tool_failure` | Toolchain crash, corruption, or unrecoverable state requiring operator intervention |
| `reaping` | Forced surrender of an expired token by a different agent (used by `lock_manager.reap_expired_locks`) |

### Staging window (OBPI-02 → OBPI-03)

In OBPI-02 (this release) the no-handoff-and-no-`--abandon` path emits a
WARNING to stderr but still succeeds (exit 0). OBPI-03 flips this to
fail-closed (exit 3).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock released or not found |
| 1 | Ownership mismatch (use `--force`) or invalid `--abandon` spec |
| 2 | System error |

## Examples

```bash
gz obpi lock release OBPI-0.1.0-01
gz obpi lock release OBPI-0.1.0-01 --agent my-agent
gz obpi lock release OBPI-0.1.0-01 --force --json
gz obpi lock release OBPI-0.1.0-01 --abandon network_loss:"session interrupted"
gz obpi lock release OBPI-0.1.0-01 --abandon external_blocker:"downstream offline"
```

## Deprecated

Use `gz obpi lock release` instead of the legacy `gz obpi
lock-release` form.
