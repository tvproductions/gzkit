"""gz handoff archive — operator surface over the retention runtime.

Thin adapter over :mod:`gzkit.handoff_archive` (ADR-0.0.65 § Decision #3,
OBPI-0.0.65-05). NO domain logic lives here: the command parses ``--older-than``,
calls the runtime plan/execute functions, and renders human or ``--json`` output.
``--dry-run`` computes the plan and mutates nothing.

@covers ADR-0.0.65 (OBPI-0.0.65-05)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from gzkit.cli.helpers.durations import parse_older_than_days
from gzkit.commands.common import console, get_project_root
from gzkit.handoff_archive import ArchivePlan, ArchiveResult, execute_archive, plan_archive

_SKIP_LABELS: tuple[str, ...] = (
    "skipped_locked",
    "skipped_chained",
    "skipped_recent",
    "skipped_undatable",
    "skipped_conflict",
)


def _parse_older_than(raw: str) -> int:
    """Parse an ``--older-than`` duration like ``30d`` or ``30`` into a day count.

    Delegates to the shared grammar in :mod:`gzkit.cli.helpers.durations` so this
    verb and ``gz arb archive`` cannot drift into accepting different values under
    the same flag name (GHI #594). Retained as a named local so this module's call
    sites and tests keep their existing shape.
    """
    return parse_older_than_days(raw)


def _payload(plan: ArchivePlan, result: ArchiveResult | None, *, dry_run: bool) -> dict:
    payload: dict = {"dry_run": dry_run}
    payload.update({label: getattr(plan, label) for label in _SKIP_LABELS})
    if dry_run:
        payload["would_move"] = plan.eligible
    else:
        payload["moved"] = result.moved if result is not None else []
        # merge any race-time conflict (dest appeared after planning) into the
        # plan-time conflict bucket so the outcome is never silent.
        if result is not None and result.skipped_conflict:
            payload["skipped_conflict"] = [*plan.skipped_conflict, *result.skipped_conflict]
    return payload


def _render(payload: dict, *, dry_run: bool) -> None:
    key, verb = ("would_move", "would move") if dry_run else ("moved", "moved")
    entries = payload[key]
    console.print(f"{verb}: {len(entries)}")
    for rel in entries:
        console.print(f"  {rel}")
    for label in _SKIP_LABELS:
        skipped = payload.get(label, [])
        if skipped:
            console.print(f"SKIPPED ({label.removeprefix('skipped_')}): {len(skipped)}")
            for rel in skipped:
                console.print(f"  {rel}")


def handoff_archive_cmd(
    *,
    older_than: str,
    dry_run: bool = False,
    as_json: bool = False,
    base_path: Path = Path("."),
    now: datetime | None = None,
) -> None:
    """Archive handoffs older than ``--older-than`` (move-not-delete, REQ-01..05).

    ``--dry-run`` reports the would-move set and mutates nothing. ``now`` is
    injectable so age classification can be asserted deterministically; the CLI
    path leaves it ``None`` and uses the wall clock.
    """
    root = get_project_root() if base_path == Path(".") else base_path
    days = _parse_older_than(older_than)
    resolved_now = now if now is not None else datetime.now(UTC)
    plan = plan_archive(base_path=root, older_than_days=days, now=resolved_now)
    result = None if dry_run else execute_archive(plan, base_path=root)
    payload = _payload(plan, result, dry_run=dry_run)
    if as_json:
        print(json.dumps(payload, indent=2))  # noqa: T201
        return
    _render(payload, dry_run=dry_run)
