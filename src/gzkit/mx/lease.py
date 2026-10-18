"""MX hangar lease expiry: book a status, never evict (GHI #1257).

The hangar runs the token block's lifecycle: declare entry, gain a lease, do the
work, close. The lease is the session lock's TTL on the token rail. When an open
session outlives it, the operator ruled (2026-10-18, verbatim): "what are we going
to do? evict? at worst, we book a status at least expiry and notify." So expiry is
one ``mx_session_lease_expired`` ledger event per session, and nothing moves: the
marker, the session and its lock stay where they are. The TTL guard in
:mod:`gzkit.mx.hardening` announces the same fact; this module only records it.

The guards stay read-only (OBPI-0.0.74-14 Denied Paths); the booking is a separate
writer, called by the session orientation at boot, as the token block's TTL warning
is.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from gzkit import lock_manager
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.mx import hardening

_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")
LEASE_EXPIRED_EVENT = "mx_session_lease_expired"


def book_lease_expiries(root: Path, *, now: datetime | None = None) -> list[str]:
    """Book each open session past its lease once; return the session ids booked now.

    A session already booked is skipped, so a session that stays open for days
    carries one expiry status, not one per boot.
    """
    now = now or datetime.now(UTC)
    expired = hardening.ttl_max_open_status(root, now=now).flagged_sessions
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    already = {
        event.extra.get("session_id") for event in ledger.query(event_type=LEASE_EXPIRED_EVENT)
    }
    opened = hardening.open_sessions(root)
    booked: list[str] = []
    for session_id in expired:
        if session_id in already:
            continue
        opened_at = opened[session_id]
        ledger.append(
            LedgerEvent(
                event=LEASE_EXPIRED_EVENT,
                id=session_id,
                extra={
                    "session_id": session_id,
                    "opened_at": opened_at,
                    "lease_minutes": lock_manager.DEFAULT_LOCK_TTL_MINUTES,
                    "age_minutes": round(hardening.age_hours(opened_at, now) * 60, 1),
                },
            )
        )
        booked.append(session_id)
    return booked
