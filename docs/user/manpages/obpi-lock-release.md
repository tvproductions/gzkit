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

### Fail-closed release (OBPI-03, landed)

Releasing a held lock without `--abandon` AND without a matching register
entry under `.gzkit/handoffs/` is **fail-closed**: the command prints a
`FAIL-CLOSED` message naming both the `gz-session-handoff` skill and the
`--abandon` flag as remediation, and exits 3 (policy breach). A token cannot
be surrendered without a register entry (token-block discipline
§ Sub-Invariant 5). The lock is left in place. `--force` overrides ownership
validation but does NOT bypass the register-entry requirement.

### Reaping behavior (OBPI-03)

`lock_manager.reap_expired_locks` (invoked by `gz obpi lock list` and the
SessionStart hook) makes forcible surrender as auditable as voluntary
release. For each expired lock the reaper writes an `abandoned_by_reaper`
register entry to `.gzkit/handoffs/` **before** deleting the lock — frontmatter
carries `abandoned: true`, `category: reaping`, `abandoned_by`, `abandoned_at`,
`previous_agent`, plus the Sub-Invariant 2 minimum-information fields — then
emits an `obpi_lock_released` ledger event whose `handoff_path` cites that
entry. If the register-entry write fails, the lock is preserved and no event
is emitted (fail-closed, Sub-Invariant 3 § Reaping-Attestation Requirement).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lock released (via `--abandon` or a matching register entry) or not found |
| 1 | Ownership mismatch (use `--force`) or invalid `--abandon` spec |
| 2 | System error |
| 3 | Fail-closed: release attempted without `--abandon` and without a matching register entry |

## Examples

```bash
gz obpi lock release OBPI-0.1.0-01
gz obpi lock release OBPI-0.1.0-01 --agent my-agent
gz obpi lock release OBPI-0.1.0-01 --force --json
gz obpi lock release OBPI-0.1.0-01 --abandon network_loss:"session interrupted"
gz obpi lock release OBPI-0.1.0-01 --abandon external_blocker:"downstream offline"
```
