# gz mx

Maintenance Hangar (MX) mode operations.

## Synopsis

<!-- gz-validate-skip: command-shape -->
```bash
gz mx <subcommand> [OPTIONS]
```

## Subcommands

### enter

Open the Maintenance Hangar.

<!-- gz-validate-skip: command-shape -->
```bash
gz mx enter --reason REASON --attestor ATTESTOR [--scope ADR_OR_OBPI ...] [--mode {mx,safe}] [--contract PATH]
```

Sets the marker file, writes one `mx_session_opened` ledger event, and captures the
inspection scope. The marker's presence means MX==TRUE — most governance guards drop to
advisory. gate5_invariants and the PRIME DIRECTIVE still bind.

**Requires an operator-supplied `--attestor`.** Agents cannot open the hangar
autonomously; only an operator may initiate an MX session (ADR-0.0.74 Decision #4).

Empty or whitespace-only `--reason` or `--attestor` fails closed with exit 1 — no
marker is written, no ledger event is emitted.

**Safe mode (GHI #1244).** `--mode safe --contract PATH` opens the
marker in safe mode: OBPI initiation and brief ceremony are suspended under the named
contract, every guard outside `gate5_invariants` runs at advisory (the checkpoint demotes as it does for the hangar; ruled 2026-10-17), and the
awareness banner states the mode and the contract each turn. The contract is the document
that says what the mode suspends and what still binds; `--mode safe` without a readable one
fails closed, and `--mode mx` refuses a contract. `gz mx exit` closes either mode through
the same hard gate.

**The contract is pinned (operator ruling 2026-10-18).** In safe mode the
`mx_session_opened` event records the contract's SHA-256 (`contract_sha256`) and the bodies
of its § What is suspended (`contract_suspended`) and § Exit (`contract_exit`) sections. Each
commit that changes the contract while the session is open books `mx_contract_amended`, with
the new hash, the hash it replaces and the commit, through the post-commit ledger recorder.
An edit that is never committed is not booked.

### exit

Close the Maintenance Hangar — hard gate.

<!-- gz-validate-skip: command-shape -->
```bash
gz mx exit --attestor ATTESTOR
```

Re-runs every guard at full strength — each emitting its `GZ_<LEVEL>` with no in-hangar advisory
demotion — against the inspection scope captured at enter time. Any guard reporting red causes exit
to hard-refuse with exit code 3 (leaving the marker in place, no `mx_session_closed` written).

On all-green, the operator signs, the tool writes one `mx_session_closed` event, and removes the
marker. **There is no `--force` flag.** You cannot narrow your way out of a red guard.

**Exit is the ONLY path that clears the marker.** A marker removed without a matching
`mx_session_closed` event is a detected dangling state (ADR-0.0.74 Boundary Invariant #4).

Empty or whitespace-only `--attestor` fails closed with exit 1 — no marker is cleared,
no ledger event is emitted.

### renew

Renew the open session's lease without leaving the hangar.

<!-- gz-validate-skip: command-shape -->
```bash
gz mx renew --attestor ATTESTOR
```

Claims the `mx-session` lock afresh for the open session and books one
`mx_session_lease_renewed` event. Lease-only (operator ruling 2026-10-20, GHI #1261): no guard
runs, the marker stays, and advisory debt keeps aging. Empty `--attestor`, or no ledger-bound
open session, fails closed with exit 1. See [`gz mx renew`](mx-renew.md).

### repair

Repair an unreadable, missing or unbound marker.

<!-- gz-validate-skip: command-shape -->
```bash
gz mx repair --attestor ATTESTOR
```

Rewrites the marker from the session the ledger keeps open, or removes it when no session backs
it, and books one `mx_marker_repaired` event. A healthy marker is left alone. This is the
recovery the condition's announcement names (operator ruling 2026-10-31, GHI #1273). See
[`gz mx repair`](mx-repair.md).

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--reason REASON` | enter | Reason for entering MX mode (required; must be non-empty) |
| `--attestor ATTESTOR` | enter, exit, renew, repair | Operator identity; never an agent (required) |
| `--scope ADR_OR_OBPI ...` | enter | ADRs/OBPIs under inspection (optional; 0 or more) |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Open the hangar for ADR-0.0.74 repair work
gz mx enter --reason "re-true ledger-proof locks under ADR-0.0.74" --attestor g0

# Open with explicit inspection scope
gz mx enter --reason "repair marker binding" --attestor g0 --scope ADR-0.0.74 OBPI-0.0.74-04

# Renew an expired lease when resuming (no guard runs)
gz mx renew --attestor g0

# Close the hangar (re-run every guard at full strength; operator signs on all-green)
gz mx exit --attestor g0
```

## Behavior

### enter

1. Validates `--reason` and `--attestor` are non-empty. Fails closed (exit 1) if either is empty.
2. Checks the hangar is not already open (`marker.is_active`). Fails closed (exit 1) if it is.
3. Acquires a session lock on the `lock_manager` token rail (`mx-session` key) to serialize
   concurrent entry attempts.
4. Writes the marker file (`.gzkit/mx.json`) with `session_id`, `opened_at`, `reason`,
   `attestor`, and `inspection_scope`.
5. Writes one `mx_session_opened` ledger event (binds the marker anti-contrivance: a
   hand-created marker with no matching ledger event is void).

### exit

1. Validates `--attestor` is non-empty. Fails closed (exit 1) if empty.
2. Checks the hangar is open (`marker.is_active`). Fails closed (exit 1) if not.
3. Holds the marker, marked `exiting: true` — checkpoint demotes nothing, so every guard
   emits at its real `GZ_<LEVEL>` severity (no advisory demotion), and the session stays
   bound to its marker (GHI #1257).
4. Runs every guard at full strength.
5. If any guard is red: puts the marker back as it was, exits 3 — hangar stays open.
6. If all guards are green: writes one `mx_session_closed` ledger event, then removes the
   marker; the operator's `--attestor` is the airworthiness signature.

### Lease

The hangar runs the token block's lifecycle: declare entry, gain a lease, do the work, close.
The lease is the `mx-session` lock's TTL on the token rail (`lock_manager.DEFAULT_LOCK_TTL_MINUTES`),
one definition for both. An open session past its lease is never evicted (operator ruling
2026-10-18): the next session start books one `mx_session_lease_expired` ledger event for it and
the session orientation announces it under `## MX hangar`; the lock reaper leaves the lock of an
open hangar in place. `gz validate --mx-hardening`, a `gz check` step, announces the same finding
and the advisory debt the session carries, and never blocks `gz mx exit` on either. Debt ages
from the first safe-mode open under the session's contract, so closing and reopening under one
contract renews the lease without resetting the debt (GHI #1258). `gz mx renew` renews the lease
in place, with no exit and no guard run; the lease guard then measures from the renewal
(GHI #1261). It grounds
only a dangling session (ledger open, marker missing) and more than one open session (GHI #1257).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Hangar opened (enter), closed (exit) or its lease renewed (renew) successfully |
| 1 | Validation failure: empty input, hangar already active/inactive, or concurrent entry |
| 2 | System/IO error |
| 3 | Policy breach: guards reported red on exit re-run |

## Related

- ADR-0.0.74: MX Mode — Maintenance Hangar (design and decision record)
- `gz validate --documents`: verify governance artifact integrity
