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
- Books a lease that ran out before this renewal as `mx_session_lease_expired` first,
  once, as the session orientation books it at boot, and says so; a live lease books none
  (GHI #1257). Expiry is never an eviction.
- Claims the `mx-session` lock afresh for the same session, so its TTL starts again, and
  writes one `mx_session_lease_renewed` ledger event carrying `renewed_at`. The lock is
  held by the MX session id, never the harness session that renews it, which a `/clear`
  replaces (RP-12 rulings 3 and 149).
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

Observed in a scratch project whose hangar was opened and whose lease then ran out:

```console
$ uv run gz mx renew --attestor g0
Lease expiry booked. The lease of session 5c7bf21b-3c12-4092-866b-1eef7444e87f
ran out before this renewal; its expiry is booked once, never an eviction.
Lease renewed. session_id=5c7bf21b-3c12-4092-866b-1eef7444e87f, lease=24h,
attestor=g0. No guards were run; `gz mx exit` remains the full-strength gate.
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- [`gz mx exit`](mx-exit.md) — the full-strength exit gate
