"""Flag test fixtures whose verdict depends on when they run (GHI #865, arm 1).

A fixture that pins an absolute timestamp into a field feeding a wall-clock
predicate is true only until the clock crosses the threshold. It passes at
authoring, then fails forever — in someone else's unrelated change, with a
traceback pointing at code they did not write.

Measured instance: a fixture pinned ``claimed_at="2026-08-22T01:00:00+00:00"``
against ``ttl_minutes=1440``. The suite passed at 20:30Z and failed at 01:14Z
the next day, fourteen minutes after that lock expired, in a commit that
modified zero Python.

This is the NET. Arm 2 is the fix: :meth:`gzkit.lock_manager.LockData.is_expired_at`
takes the clock as a parameter, so a deterministic test needs no real timestamp
at all. Nothing forces authors onto that seam, which is why this audit exists.

**The predicate requires BOTH halves, because either alone is inert.** A bomb
needs an absolute timestamp AND a verdict taken against the wall clock. Measured
2026-08-23: two files carry an absolute ``claimed_at`` and take ZERO liveness
verdicts (``test_obpi_complete_lock_release``, ``test_handoff_frontmatter_coherence``)
— their timestamps are coherent fixture dates that never reach a wall-clock
predicate, and flagging them would demand a change that breaks the coupling
between ``claimed_at`` and ``last_lock_event_timestamp`` for no safety gain.
Requiring both conditions is what makes this a detector rather than a proxy.

**Scope is deliberately narrow.** Only ``tests/`` is scanned — production code
legitimately carries absolute timestamps. A far-past timestamp is never flagged:
those fixtures assert EXPIRY, which no TTL can undo, and that is the correct
hardcoded shape (``_ANCIENT_CLAIM``). Flagging it would push authors to break a
fixture that cannot rot.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from gzkit.validate import ValidationError

#: Fields whose value is compared against ``datetime.now()`` by a predicate.
#: Extend as new wall-clock-sensitive fields appear — a detector that reads one
#: field defends one field.
WALL_CLOCK_FIELDS: tuple[str, ...] = ("claimed_at",)

#: A timestamp older than this many days cannot be made live by any plausible
#: TTL, so it asserts expiry and never decays.
INERT_AGE_DAYS = 365

_ASSIGNMENT = re.compile(
    r"(?P<field>" + "|".join(WALL_CLOCK_FIELDS) + r")\s*=\s*[\"'](?P<ts>\d{4}-\d{2}-\d{2}T[^\"']+)"
)

_SEAM_CALL = re.compile(r"\b(is_expired_at|elapsed_minutes_at)\s*\(")

#: Message prefix, and the stable discriminator for these findings. The
#: ``ValidationError.type`` is the SCOPE's type rather than this check's own,
#: because that field is the exit-code routing key: only a member of
#: ``_POLICY_BREACH_ERROR_TYPES`` exits 3, and adding a member costs a line in
#: ``commands/validate_cmd.py``, which sits AT its shrink-only ceiling with zero
#: headroom (measured 1242/1242, 2026-08-23). Callers separating these findings
#: from their sibling's should match this prefix, not the type.
FINDING_PREFIX = "Wall-clock-sensitive fixture:"

#: A verdict taken against the WALL CLOCK. Its presence is the second half of
#: the predicate: without it, an absolute timestamp is inert data.
_WALL_CLOCK_VERDICT = re.compile(r"\.(is_expired|elapsed_minutes)\b")

_RECOVERY = (
    "A fixed date plus a finite TTL is a time bomb: it passes until the wall clock "
    "crosses expiry, then fails forever in an unrelated change. Take the clock as a "
    "parameter instead — `lock.is_expired_at(base + timedelta(minutes=N))` pins either "
    "verdict deterministically with no mock and no real timestamp (GHI #865). If the "
    "fixture asserts EXPIRY, use a far-past date, which cannot decay."
)


def _is_inert(raw: str, *, now: datetime) -> bool:
    """Return True when *raw* is far enough past that no TTL can make it live."""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return (now - parsed).days >= INERT_AGE_DAYS


def audit_wall_clock_fixtures(
    project_root: Path, *, now: datetime | None = None
) -> list[ValidationError]:
    """Return an error per test fixture pinned to a decaying absolute timestamp.

    *now* is injectable for the same reason this audit exists: an audit that
    read the wall clock internally would itself change verdict with the
    calendar, which is the defect it reports.
    """
    when = now or datetime.now(UTC)
    tests_dir = project_root / "tests"
    if not tests_dir.is_dir():
        return []

    errors: list[ValidationError] = []
    for path in sorted(tests_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        # A file that drives the seam is already deterministic; the timestamps
        # beside it are inputs to an explicit clock, not to the wall clock.
        if _SEAM_CALL.search(text):
            continue
        # No wall-clock verdict anywhere in the file means no absolute timestamp
        # in it can decay into a different answer. Both halves or nothing.
        if not _WALL_CLOCK_VERDICT.search(text):
            continue
        relative = path.relative_to(project_root).as_posix()
        for number, line in enumerate(text.splitlines(), start=1):
            match = _ASSIGNMENT.search(line)
            if match is None or _is_inert(match.group("ts"), now=when):
                continue
            errors.append(
                ValidationError(
                    type="tautological_test_audit",
                    artifact=f"{relative}:{number}",
                    message=(
                        f"{FINDING_PREFIX} {match.group('field')}="
                        f"{match.group('ts')!r} is an absolute timestamp. {_RECOVERY}"
                    ),
                )
            )
    return errors
