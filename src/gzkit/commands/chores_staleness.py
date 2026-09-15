"""Chore staleness bands — what `gz chores status` reads and announces (GHI #936).

A chore's currency gate used to be readable only by running the chore it
gates, so an overdue chore told nobody. This module maps a chore's class
declaration and its run record to a band without running anything.

Design authority: ``docs/governance/chore-class-system.md`` § Staleness (four
signals, graded bands, "indicator, not gate") and § Implementation order step 2.

The run witness is the timestamped PASS block ``gz chores run`` appends to
``CHORE-LOG.md``. A FAIL block records that the verb ran, never that the chore
was done, and a hand-written heading records authorship, never a run (GHI #935).
An elapsed-time chore that declares ``staleness.artifacts`` is dated by that
scan record instead, as its gate dates it: the gated run writes the PASS block,
so reading it let an overdue chore never clear and a bare run extend the clock
(GHI #935, reopened). Git is taken as parameters so the band logic runs without
a repository.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.chores_declaration import ChoreDeclaration, StalenessSignal

StalenessBand = Literal["current", "due", "overdue", "paused", "unmeasured"]

# ``gz chores run`` writes "## <ISO timestamp>" followed by "- Status: PASS|FAIL".
_RUN_HEADING = re.compile(
    r"^##[ \t]+(\d{4}-\d{2}-\d{2}T[0-9:.+\-]+)[ \t]*\n- Status: PASS[ \t]*$", re.MULTILINE
)


class ChoreStalenessReading(BaseModel):
    """One chore's staleness band, with the evidence it was read from."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str = Field(..., description="Chore slug")
    signal: StalenessSignal | None = Field(None, description="Declared signal, if declared")
    band: StalenessBand = Field(..., description="current, due, overdue, paused or unmeasured")
    last_run: datetime | None = Field(
        None, description="Newest passing run, or the declared scan record's last change"
    )
    due_since: datetime | None = Field(None, description="When the chore came due, if known")
    reason: str = Field(..., min_length=1, description="Why the chore reads this band")


def newest_pass_stamp(log_text: str) -> datetime | None:
    """Return the newest passing run stamp in *log_text*, or None.

    File order is not trusted: the newest stamp wins wherever it sits. A stamp
    written without an offset is read as UTC rather than skipped, since dropping
    it would silently age the log toward a false breach.
    """
    stamps: list[datetime] = []
    for raw in _RUN_HEADING.findall(log_text):
        try:
            when = datetime.fromisoformat(raw)
        except ValueError:
            continue
        stamps.append(when if when.tzinfo else when.replace(tzinfo=UTC))
    return max(stamps, default=None)


def _by_grace(
    slug: str,
    signal: StalenessSignal,
    last_run: datetime,
    due_at: datetime,
    grace: timedelta,
    now: datetime,
    cause: str,
) -> ChoreStalenessReading:
    band: StalenessBand = "due" if now <= due_at + grace else "overdue"
    return ChoreStalenessReading(
        slug=slug, signal=signal, band=band, last_run=last_run, due_since=due_at, reason=cause
    )


def read_chore_staleness(
    slug: str,
    declaration: ChoreDeclaration | None,
    log_text: str | None,
    *,
    now: datetime,
    newest_commit: Callable[[tuple[str, ...]], datetime | None],
    first_commit_after: Callable[[tuple[str, ...], datetime], datetime | None],
    artifact_changed: Callable[[tuple[str, ...]], datetime | None],
) -> ChoreStalenessReading:
    """Read *slug*'s band from its declaration and its ``CHORE-LOG.md`` text."""
    if declaration is None:
        return ChoreStalenessReading(
            slug=slug, band="unmeasured", reason="no class declaration to read a signal from"
        )
    staleness = declaration.staleness
    signal = staleness.signal
    if staleness.paused:
        return ChoreStalenessReading(
            slug=slug, signal=signal, band="paused", reason="declared paused: intentional dormancy"
        )
    if signal == "accumulated-work":
        return ChoreStalenessReading(
            slug=slug,
            signal=signal,
            band="unmeasured",
            reason="accumulated-work declares no counter to compare against a threshold",
        )

    last_run = newest_pass_stamp(log_text) if log_text else None
    grace = timedelta(days=staleness.grace_days)

    if signal == "elapsed-time":
        period = timedelta(days=staleness.period_days or 0)
        witness = "passing run"
        if staleness.artifacts:
            last_run = artifact_changed(staleness.artifacts)
            witness = "scan record change"
        if last_run is None:
            return ChoreStalenessReading(
                slug=slug, signal=signal, band="overdue", reason=f"no {witness} on record"
            )
        due_at = last_run + period
        if now <= due_at:
            return ChoreStalenessReading(
                slug=slug,
                signal=signal,
                band="current",
                last_run=last_run,
                reason=f"last {witness} within its {period.days}d period",
            )
        cause = f"{period.days}d period elapsed since the last {witness}"
        return _by_grace(slug, signal, last_run, due_at, grace, now, cause)

    surfaces = staleness.surfaces or ()
    if newest_commit(surfaces) is None:
        return ChoreStalenessReading(
            slug=slug,
            signal=signal,
            band="unmeasured",
            last_run=last_run,
            reason="no declared surface has commit history: " + ", ".join(surfaces),
        )
    if last_run is None:
        return ChoreStalenessReading(
            slug=slug, signal=signal, band="overdue", reason="no passing run on record"
        )
    moved_at = first_commit_after(surfaces, last_run)
    if moved_at is None:
        return ChoreStalenessReading(
            slug=slug,
            signal=signal,
            band="current",
            last_run=last_run,
            reason="no declared surface has moved since the last passing run",
        )
    cause = "a declared surface moved after the last passing run"
    return _by_grace(slug, signal, last_run, moved_at, grace, now, cause)


def _git_commit_times(project_root: Path, args: list[str]) -> list[datetime]:
    completed = subprocess.run(
        ["git", "log", "--format=%ct", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [
        datetime.fromtimestamp(int(line), UTC)
        for line in completed.stdout.split()
        if line.isdigit()
    ]


def git_newest_commit(project_root: Path) -> Callable[[tuple[str, ...]], datetime | None]:
    """Return a reader for the newest commit touching any of the given surfaces."""

    def newest(surfaces: tuple[str, ...]) -> datetime | None:
        times = _git_commit_times(project_root, ["-1", "--", *surfaces])
        return times[0] if times else None

    return newest


def git_artifact_changed(
    project_root: Path, now: datetime
) -> Callable[[tuple[str, ...]], datetime | None]:
    """Return a reader for when any of the given scan artifacts last changed.

    An artifact present on disk with uncommitted changes reads as *now*: the
    procedure is writing it, and requiring a commit before ``gz chores run``
    would make the gate's own recovery a two-step dance. Otherwise the newest
    committer date wins. A deleted artifact never reads as now, so removing the
    record cannot pass for writing it; one git has never seen reads None.
    """

    def changed(artifacts: tuple[str, ...]) -> datetime | None:
        # Literal pathspecs, and never a directory: a record is one file, and a
        # pattern or directory would be dated by its neighbours, the run log among
        # them, whose commits move on a FAIL run (GHI #935).
        files = [path for path in artifacts if not (project_root / path).is_dir()]
        if not files:
            return None
        present = [f":(literal){path}" for path in files if (project_root / path).is_file()]
        if present:
            status = subprocess.run(
                ["git", "status", "--porcelain", "--", *present],
                cwd=project_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if status.returncode == 0 and status.stdout.strip():
                return now
        literal = [f":(literal){path}" for path in files]
        times = _git_commit_times(project_root, ["-1", "--", *literal])
        return times[0] if times else None

    return changed


def git_first_commit_after(
    project_root: Path,
) -> Callable[[tuple[str, ...], datetime], datetime | None]:
    """Return a reader for the oldest commit touching the surfaces after a moment.

    Committer dates, never filesystem mtimes: a clone or branch switch rewrites
    every mtime (``scripts/check_proof_freshness.py``). ``--since`` narrows the
    walk; the strict comparison drops a commit landing in the run's own second.
    """

    def first_after(surfaces: tuple[str, ...], since: datetime) -> datetime | None:
        times = _git_commit_times(project_root, [f"--since={since.isoformat()}", "--", *surfaces])
        return min((when for when in times if when > since), default=None)

    return first_after
