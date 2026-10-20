# gz mx renew

Renew the open session's lease. Runs no guard.

## Usage

<!-- gz-validate-skip: command-shape -->
```bash
gz mx renew --attestor ATTESTOR
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--attestor ATTESTOR` | Operator identity renewing the lease (required; never an agent) |

## Runtime Behavior

- Validates that `--attestor` is non-empty; fails closed (exit 1) if empty or whitespace-only —
  no lock is touched, no ledger event is emitted.
- Checks a ledger-bound session is open (`marker.is_valid`). Fails closed (exit 1) if not.
- Claims the `mx-session` lock afresh for the same session, so its TTL starts again, and
  writes one `mx_session_lease_renewed` ledger event carrying `renewed_at`.
- Runs **no guard**. The marker is untouched and the session stays open.
- The lease guard (`gz validate --mx-hardening`) measures the lease from the last renewal,
  and the next lease expiry is booked once more only if the renewed lease also runs out.
- Advisory debt is **not** reset: it keeps aging from the first safe-mode open under the
  session's contract (GHI #1258). `gz mx exit` stays the only full-strength gate.

Lease-only by operator ruling (2026-10-20, verbatim *"Make renewal lease-only, as the 10-18
ruling already implies."*); the 2026-10-18 ruling called a close-and-reopen inside one
drydock *"a lease renewal"* (GHI #1261).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Lease renewed |
| 1 | Validation failure: empty attestor or no open session |
| 2 | System/IO error |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Renew an expired lease when resuming a drydock session
gz mx renew --attestor g0
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- [`gz mx exit`](mx-exit.md) — the full-strength exit gate
