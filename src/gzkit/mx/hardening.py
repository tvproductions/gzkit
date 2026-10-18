"""MX hardening guards (ADR-0.0.74 Decision item 14).

Four guards bound the Maintenance Hangar so it cannot stay open forever, ship a
release mid-repair, let advisory debt sit silent, or leave a hand-deleted marker
undetected:

1. :func:`ttl_max_open_status` — flags a session open past its lease or beyond
   the max-open count. Past the lease it announces and never grounds: expiry is
   booked and notified, never an eviction (GHI #1257, operator ruling 2026-10-18).
2. :func:`normal_release_blocked` — refuses a normal release while the hangar is
   open (wired at the real release funnels — ``gz patch release`` / ``gz closeout``).
3. :func:`debt_aging_status` — accrued advisory debt grows *louder* the longer an
   open session sits (the open hangar IS the advisory-debt state: every non-floor
   guard is demoted to advisory while the marker is up).
4. :func:`dangling_state_status` — detects "ledger open but marker missing" (the
   backstop for the WWHTBT condition that exit is the only path that clears the
   marker, parent ADR § Consequences/Negative #4).

Each guard EMITS a ``GZ_<LEVEL>`` (:mod:`gzkit.mx.levels`) and resolves its
effective severity through the shared leveled checkpoint
(:func:`gzkit.mx.checkpoint.resolve`) — the single leveled severity authority
(parent ADR Boundary Invariant #2). No guard hand-sets its own disposition with a
module-level bool; the only level that grounds while the marker is up is
``CRITICAL`` (the checkpoint pins it), which the meta-guards emit when they must
bite inside the hangar.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from gzkit import lock_manager
from gzkit.ledger import Ledger
from gzkit.mx import checkpoint, disposition, levels, marker

# Hangar bounds. The lease is the session lock's TTL on the token rail, read from
# lock_manager at call time and never restated here: one definition, as in the
# token block (.gzkit/rules/token-block-discipline.md § Sub-Invariant 4; GHI #1257).
# The hangar is single-occupancy, so more than one open session is a hard breach.
_MAX_OPEN = 1

_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class TtlMaxOpenResult(BaseModel):
    """Outcome of the TTL / max-open guard."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    flagged_sessions: list[str]
    over_max: bool
    emitted_level: int
    route: disposition.Route
    grounds: bool


class ReleaseLockResult(BaseModel):
    """Outcome of the no-normal-release-while-open guard."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    blocked: bool
    emitted_level: int
    route: disposition.Route
    reason: str


class DebtAgingResult(BaseModel):
    """Outcome of the ledger debt-aging guard."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    flagged: bool
    age_hours: float
    emitted_level: int
    route: disposition.Route
    grounds: bool


class DanglingStateResult(BaseModel):
    """Outcome of the dangling-state detector."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dangling: bool
    dangling_sessions: list[str]
    emitted_level: int
    route: disposition.Route
    grounds: bool


# ---------------------------------------------------------------------------
# Shared ledger reader
# ---------------------------------------------------------------------------


def open_sessions(root: Path) -> dict[str, str]:
    """Map ``session_id`` → earliest ``opened_at`` ts for still-open MX sessions.

    A session is open when it has an ``mx_session_opened`` event and no matching
    ``mx_session_closed`` — the same open-set rule the marker's binding check uses.
    Reads through :class:`gzkit.ledger.Ledger` (the guards READ the ledger; they
    never mutate the writer — brief Denied Paths).
    """
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    closed = {e.extra.get("session_id") for e in ledger.query(event_type="mx_session_closed")}
    out: dict[str, str] = {}
    for event in ledger.query(event_type="mx_session_opened"):
        sid = event.extra.get("session_id")
        if not isinstance(sid, str) or not sid or sid in closed:
            continue
        if sid not in out or event.ts < out[sid]:
            out[sid] = event.ts
    return out


def lease_hours() -> float:
    """Return the hangar's lease in hours: the session lock's TTL on the token rail."""
    return lock_manager.DEFAULT_LOCK_TTL_MINUTES / 60


def age_hours(opened_at: str, now: datetime) -> float:
    """Hours between *opened_at* (ISO-8601) and *now*; 0 on an unparseable ts."""
    try:
        opened = datetime.fromisoformat(opened_at)
    except ValueError:
        return 0.0
    if opened.tzinfo is None:
        opened = opened.replace(tzinfo=UTC)
    return (now - opened).total_seconds() / 3600.0


# ---------------------------------------------------------------------------
# Guard 1 — TTL / max-open (REQ-0.0.74-14-01)
# ---------------------------------------------------------------------------


def ttl_max_open_status(
    root: Path | None = None,
    *,
    now: datetime | None = None,
    ttl_hours: float | None = None,
    max_open: int = _MAX_OPEN,
) -> TtlMaxOpenResult:
    """Flag an MX session open past its lease or beyond the max-open count.

    Past the lease emits ``WARNING``: announced, never grounding, in the hangar,
    outside it and in exit's full-strength re-run (GHI #1257). Expiry is booked as a
    ledger status by :func:`gzkit.mx.lease.book_lease_expiries`, not enforced by
    eviction. Exceeding ``max_open`` is a hard single-occupancy breach and emits
    ``CRITICAL``, which the checkpoint pins through an active marker.
    """
    root = root or Path.cwd()
    now = now or datetime.now(UTC)
    ttl = lease_hours() if ttl_hours is None else ttl_hours
    sessions = open_sessions(root)

    flagged = sorted(sid for sid, ts in sessions.items() if age_hours(ts, now) > ttl)
    over_max = len(sessions) > max_open

    if over_max:
        emitted = levels.CRITICAL
    elif flagged:
        emitted = levels.WARNING
    else:
        emitted = levels.INFO

    route = checkpoint.resolve("mx-ttl-max-open", emitted, root)
    return TtlMaxOpenResult(
        flagged_sessions=flagged,
        over_max=over_max,
        emitted_level=emitted,
        route=route,
        grounds=disposition.grounds(route),
    )


# ---------------------------------------------------------------------------
# Guard 2 — no normal release while open (REQ-0.0.74-14-02)
# ---------------------------------------------------------------------------


def normal_release_blocked(root: Path | None = None) -> ReleaseLockResult:
    """Refuse a normal release while an MX hangar is open.

    Emits ``CRITICAL`` when the marker is active so the checkpoint pins it (a
    grounding route) rather than demoting it to advisory; emits ``INFO`` (the
    non-grounding track route) when no hangar is open. The release funnels
    (``gz patch release`` / ``gz closeout``) consult ``.blocked`` and refuse.
    """
    root = root or Path.cwd()
    emitted = levels.CRITICAL if marker.is_active(root) else levels.INFO
    route = checkpoint.resolve("mx-normal-release", emitted, root)
    blocked = disposition.grounds(route)
    reason = (
        "an MX maintenance hangar is open; exit it (gz mx exit) before releasing" if blocked else ""
    )
    return ReleaseLockResult(blocked=blocked, emitted_level=emitted, route=route, reason=reason)


# ---------------------------------------------------------------------------
# Guard 3 — ledger debt-aging (REQ-0.0.74-14-03)
# ---------------------------------------------------------------------------


def _debt_level(age: float) -> int:
    """Map the oldest open session's age to a rising, never-grounding level.

    The rungs are fractions of the lease: a quarter is NOTICE, a half warns. The top
    rung is WARNING, never a grounding level: debt past the lease announces at full
    volume and blocks nothing, exit included (GHI #1257, operator ruling 2026-10-18).
    """
    lease = lease_hours()
    if age >= lease / 2:
        return levels.WARNING
    if age >= lease / 4:
        return levels.NOTICE
    return levels.INFO


def _debt_since(root: Path, sessions: dict[str, str]) -> dict[str, str]:
    """Map each open session to the ts its debt ages from: per contract, else its own open.

    A safe-mode session cycle under one contract renews the lease, never the debt
    (GHI #1258, operator ruling 2026-10-18 'Per contract (Rec.)').
    """
    opened = Ledger(root.joinpath(*_LEDGER_RELPATH)).query(event_type="mx_session_opened")
    first: dict[str, str] = {}
    contract_of: dict[str, str] = {}
    for event in opened:
        contract = event.extra.get("contract")
        if not isinstance(contract, str) or not contract:
            continue
        contract_of[str(event.extra.get("session_id"))] = contract
        if contract not in first or event.ts < first[contract]:
            first[contract] = event.ts
    return {sid: first.get(contract_of.get(sid, ""), ts) for sid, ts in sessions.items()}


def debt_aging_status(
    root: Path | None = None,
    *,
    now: datetime | None = None,
) -> DebtAgingResult:
    """Raise the effective level of accrued advisory debt as an open session ages.

    The open hangar is the advisory-debt state (every non-floor guard demoted to
    advisory while the marker is up); the longer the oldest open session sits, the
    louder the emitted level — debt does not stay silent.
    """
    root = root or Path.cwd()
    now = now or datetime.now(UTC)
    sessions = open_sessions(root)

    since = _debt_since(root, sessions)
    oldest = max((age_hours(ts, now) for ts in since.values()), default=0.0)
    emitted = _debt_level(oldest) if sessions else levels.INFO
    route = checkpoint.resolve("mx-debt-aging", emitted, root)
    return DebtAgingResult(
        flagged=emitted >= levels.NOTICE,
        age_hours=oldest,
        emitted_level=emitted,
        route=route,
        grounds=disposition.grounds(route),
    )


# ---------------------------------------------------------------------------
# Guard 4 — dangling-state detector (REQ-0.0.74-14-04)
# ---------------------------------------------------------------------------


def dangling_state_status(root: Path | None = None) -> DanglingStateResult:
    """Detect an open ledger session whose marker file is missing on disk.

    Exit (writing ``mx_session_closed``) is the only sanctioned path that clears
    the marker; a marker removed without a close event leaves an open session with
    no marker — the dangling state this guard flags. Marker absent ⇒ the checkpoint
    does not demote, so ``ERROR`` grounds.
    """
    root = root or Path.cwd()
    sessions = open_sessions(root)
    dangling = bool(sessions) and not marker.is_active(root)
    dangling_sessions = sorted(sessions) if dangling else []

    emitted = levels.ERROR if dangling else levels.INFO
    route = checkpoint.resolve("mx-dangling-state", emitted, root)
    return DanglingStateResult(
        dangling=dangling,
        dangling_sessions=dangling_sessions,
        emitted_level=emitted,
        route=route,
        grounds=disposition.grounds(route),
    )
