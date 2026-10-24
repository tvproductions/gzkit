"""MX hardening scope: the hangar's bounds, run where they bind (GHI #1257).

ADR-0.0.74 Decision item 14 bounds the Maintenance Hangar with four guards.
``normal_release_blocked`` was wired at the release funnels; the other three
(``ttl_max_open_status``, ``debt_aging_status``, ``dangling_state_status``) were
proved by unit tests of their predicates and called by nothing, so the bound they
promise never happened. This scope runs them on every ``gz check``, and
:func:`mx_hardening_findings` is the one rendering the session orientation reads
too, so both surfaces say the same thing.

Each guard already resolves its route through the shared checkpoint (BI#2), so a
finding grounds exactly where its guard's route grounds and is announced
everywhere else. Under the operator ruling of 2026-10-18 that leaves two grounding
findings, a dangling session outside the hangar and more than one open session;
a session past its lease, and the advisory debt it carries, announce and never
block, ``gz mx exit`` included. Expiry itself is booked by
:func:`gzkit.mx.lease.book_lease_expiries`, never enforced by eviction.

Registered as ``gz validate --mx-hardening``; runs in ``gz check`` as the
"MX hardening" step.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.advisory import emit_advisory
from gzkit.core.validation_rules import ValidationError
from gzkit.mx import hardening
from gzkit.mx import levels as _levels

_RECOVER = "close the hangar with `gz mx exit` through the gz-mx skill"


class MxHardeningFinding(BaseModel):
    """One guard's finding, rendered once for the scope and the orientation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    guard: str = Field(..., description="Checkpoint name of the guard that fired")
    sessions: list[str] = Field(..., description="Open session ids the finding names")
    level: str = Field(..., description="Emitted GZ_<LEVEL> name")
    grounds: bool = Field(..., description="True when the checkpoint route grounds")
    message: str = Field(..., description="Three-part recovery prose")


def _level_name(level: int) -> str:
    return {value: name for name, value in vars(_levels).items() if name.isupper()}.get(
        level, str(level)
    )


def _ttl_findings(root: Path, now: datetime) -> list[MxHardeningFinding]:
    findings: list[MxHardeningFinding] = []
    occupancy = hardening.ttl_max_open_status(root, now=now)
    if occupancy.over_max:
        sessions = sorted(hardening.open_sessions(root))
        findings.append(
            MxHardeningFinding(
                guard="mx-ttl-max-open",
                sessions=sessions,
                level=_level_name(occupancy.emitted_level),
                grounds=occupancy.grounds,
                message=(
                    f"{len(sessions)} MX sessions are open in the ledger ({', '.join(sessions)}) "
                    f"against a max-open of 1: the hangar is single-occupancy (ADR-0.0.74 "
                    f"item 14, max-open guard). Close every session but the one the marker "
                    f"binds; {_RECOVER}."
                ),
            )
        )
    # The lease arm alone: with the max-open bound lifted, the guard reports only
    # the sessions past their lease, at the level and route it gives that fact.
    lease = hardening.ttl_max_open_status(root, now=now, max_open=sys.maxsize)
    if lease.flagged_sessions:
        findings.append(
            MxHardeningFinding(
                guard="mx-ttl-max-open",
                sessions=lease.flagged_sessions,
                level=_level_name(lease.emitted_level),
                grounds=lease.grounds,
                message=(
                    f"MX session {', '.join(lease.flagged_sessions)} is past its lease "
                    f"({hardening.lease_hours():g}h, the session lock's TTL). Expiry is booked as "
                    f"`mx_session_lease_expired` and announced, never evicted (GHI #1257, "
                    f"operator ruling 2026-10-18). To keep working, renew the lease with "
                    f"`gz mx renew` through the gz-mx skill, which runs no guard (GHI #1261); "
                    f"when the work is done, {_RECOVER}."
                ),
            )
        )
    return findings


def _debt_findings(root: Path, now: datetime) -> list[MxHardeningFinding]:
    result = hardening.debt_aging_status(root, now=now)
    if not result.flagged:
        return []
    sessions = sorted(hardening.open_sessions(root))
    return [
        MxHardeningFinding(
            guard="mx-debt-aging",
            sessions=sessions,
            level=_level_name(result.emitted_level),
            grounds=result.grounds,
            message=(
                f"MX session {', '.join(sessions)} has carried advisory debt for "
                f"{result.age_hours:.1f}h at {_level_name(result.emitted_level)}: every guard "
                f"outside gate5_invariants has been advisory that long (ADR-0.0.74 item 14, "
                f"debt aging). When the work is done, {_RECOVER}, which re-runs them at "
                f"full strength."
            ),
        )
    ]


def _dangling_findings(root: Path) -> list[MxHardeningFinding]:
    result = hardening.dangling_state_status(root)
    if not result.dangling:
        return []
    return [
        MxHardeningFinding(
            guard="mx-dangling-state",
            sessions=result.dangling_sessions,
            level=_level_name(result.emitted_level),
            grounds=result.grounds,
            message=(
                f"MX session {', '.join(result.dangling_sessions)} is open in the ledger but "
                f"`.gzkit/mx.json` is missing: the marker was removed outside `gz mx exit`, "
                f"the only path that clears it (ADR-0.0.74 Boundary Invariant #4). Restore "
                f"the marker its `mx_session_opened` event binds, then {_RECOVER}."
            ),
        )
    ]


def mx_hardening_findings(root: Path, *, now: datetime | None = None) -> list[MxHardeningFinding]:
    """Run the three unwired hardening guards and return what each one found."""
    now = now or datetime.now(UTC)
    return [*_ttl_findings(root, now), *_debt_findings(root, now), *_dangling_findings(root)]


def audit_mx_hardening(root: Path, *, now: datetime | None = None) -> list[ValidationError]:
    """Return a ValidationError for each grounding finding and announce the rest.

    A non-grounding finding prints one advisory line and changes no exit code.
    """
    errors: list[ValidationError] = []
    for finding in mx_hardening_findings(root, now=now):
        if finding.grounds:
            errors.append(
                ValidationError(
                    type="mx_hardening",
                    artifact=f"mx-session:{','.join(finding.sessions)}",
                    message=f"[{finding.guard}] {finding.message}",
                )
            )
        else:
            emit_advisory(f"mx-hardening [{finding.guard}, {finding.level}]: {finding.message}")
    return errors
