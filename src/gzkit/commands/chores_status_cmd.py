"""`gz chores status` — read every chore's staleness band without running it (GHI #936).

A chore's currency gate was readable only by running the chore it gates, so
nothing outside a run reported that a chore was overdue. This verb reads each
registered chore's declaration and run record and renders its band. It
announces and never gates: every band exits 0 (operator ruling 2026-09-12,
``docs/governance/chore-class-system.md`` § Staleness — Indicator, not gate).
"""

from __future__ import annotations

from datetime import UTC, datetime

from rich.markup import escape
from rich.table import Table

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.chores import _filter_registry, _load_chores_registry
from gzkit.commands.chores_exec import _log_path
from gzkit.commands.chores_staleness import (
    ChoreStalenessReading,
    StalenessBand,
    git_artifact_changed,
    git_first_commit_after,
    git_newest_commit,
    read_chore_staleness,
)
from gzkit.commands.common import get_project_root

# Loudest first: the order an operator should read the board in.
BAND_ORDER: tuple[StalenessBand, ...] = ("overdue", "due", "unmeasured", "paused", "current")

_BAND_STYLE = {
    "overdue": "bold red",
    "due": "yellow",
    "unmeasured": "magenta",
    "paused": "dim",
    "current": "green",
}


def collect_chore_staleness(now: datetime | None = None) -> list[ChoreStalenessReading]:
    """Return every registered chore's staleness reading, loudest band first."""
    project_root = get_project_root()
    _registry_path, registry = _load_chores_registry()
    newest = git_newest_commit(project_root)
    first_after = git_first_commit_after(project_root)
    moment = now or datetime.now(UTC)
    artifact_changed = git_artifact_changed(project_root, moment)
    readings: list[ChoreStalenessReading] = []
    for chore in _filter_registry(registry).values():
        log = _log_path(project_root, chore)
        readings.append(
            read_chore_staleness(
                chore.slug,
                chore.declaration,
                log.read_text(encoding="utf-8") if log.is_file() else None,
                now=moment,
                newest_commit=newest,
                first_commit_after=first_after,
                artifact_changed=artifact_changed,
            )
        )
    return sorted(readings, key=lambda r: (BAND_ORDER.index(r.band), r.slug))


def _day(moment: datetime | None) -> str:
    return moment.date().isoformat() if moment else "-"


def chores_status(*, as_json: bool = False) -> None:
    """Report each registered chore's staleness band; announces, never gates."""
    readings = collect_chore_staleness()
    counts = {band: sum(1 for r in readings if r.band == band) for band in BAND_ORDER}
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.data(
            {
                "chores": [reading.model_dump(mode="json") for reading in readings],
                "counts": counts,
            }
        )
        return

    table = Table(title="Chore Staleness")
    table.add_column("Slug", style="cyan", no_wrap=True, overflow="fold")
    table.add_column("Signal")
    table.add_column("Band", no_wrap=True)
    table.add_column("Last run")
    table.add_column("Due since")
    table.add_column("Reason")
    for reading in readings:
        style = _BAND_STYLE[reading.band]
        table.add_row(
            reading.slug,
            reading.signal or "-",
            f"[{style}]{reading.band}[/{style}]",
            _day(reading.last_run),
            _day(reading.due_since),
            escape(reading.reason),
        )
    fmt.table(table)
    fmt.print(", ".join(f"{counts[band]} {band}" for band in BAND_ORDER))
