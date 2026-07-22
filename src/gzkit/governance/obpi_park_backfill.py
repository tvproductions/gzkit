"""One-shot backfill parking the GHI #520 demotion-cohort orphans (GHI #584).

The 2026-05-23 Day-0 pool demotion renamed 28 ADRs, emitting exactly one
``artifact_renamed`` event each and nothing at all for their children. That left
237 ``obpi_created`` records with no terminal event and a parent id that no
longer resolves — Layer-2 asserting artifacts Layer-1 cannot show.

This module replays that cohort forward: for every ``pool_demotion`` rename, it
emits the ``obpi_parked`` event the demotion should have emitted at the time.
The ledger stays append-only (``AGENTS.md`` Never #2) — nothing is rewritten;
the correction is composed from new forward events.

Not a ``gz`` verb: a one-shot migration, invoked as
``uv run python -m gzkit.governance.obpi_park_backfill --dry-run``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gzkit.governance.trust_audits.taxonomy import _live_adr_ids
from gzkit.ledger import Ledger
from gzkit.ledger_events import obpi_parked_event
from gzkit.obpi_lifecycle import (
    orphaned_obpi_ids,
    parkable_children,
    rename_chain_target,
)

_DEMOTION_REASON = "pool_demotion"


def _demotion_cohort(events: list[dict[str, object]]) -> list[tuple[str, str]]:
    """Return ``(old_id, new_id)`` for every pool-demotion rename, in ledger order."""
    cohort: list[tuple[str, str]] = []
    for event in events:
        if event.get("event") != "artifact_renamed":
            continue
        extra = event.get("extra")
        reason = event.get("reason")
        if reason is None and isinstance(extra, dict):
            reason = extra.get("reason")
        if reason != _DEMOTION_REASON:
            continue
        new_id = event.get("new_id")
        if new_id is None and isinstance(extra, dict):
            new_id = extra.get("new_id")
        old_id = str(event.get("id", ""))
        if old_id and new_id:
            cohort.append((old_id, str(new_id)))
    return cohort


def plan_backfill(ledger: Ledger, project_root: Path | None = None) -> list[tuple[str, str, str]]:
    """Return ``(obpi_id, original_parent, parked_to)`` for every orphan to park.

    Two cohorts, one disposition:

    1. **Demotion cohort** — children of a ``pool_demotion`` rename that never
       received an event (the GHI #520 wound).
    2. **Brief-absent cohort** — undisposed OBPIs whose brief is not on disk,
       regardless of how the brief went away. This is the arm the GHI's title
       actually names ("no on-disk briefs"); parent-resolution alone misses it.
    """
    events = [event.model_dump() for event in ledger.read_all()]
    planned: list[tuple[str, str, str]] = []
    already: set[str] = set()
    for old_id, new_id in _demotion_cohort(events):
        for obpi_id in parkable_children(events, old_id):
            if obpi_id in already:
                continue
            already.add(obpi_id)
            planned.append((obpi_id, old_id, new_id))

    root = project_root or Path()
    adr_root = root / "docs" / "design" / "adr"
    brief_ids = {p.stem for p in adr_root.rglob("OBPI-*.md")} if adr_root.is_dir() else set()
    live_adr_ids = _live_adr_ids(root)
    for obpi_id in orphaned_obpi_ids(events, live_adr_ids, brief_ids=brief_ids):
        if obpi_id in already:
            continue
        parent = _created_parent(events, obpi_id)
        already.add(obpi_id)
        planned.append((obpi_id, parent, rename_chain_target(events, parent)))
    return planned


def _created_parent(events: list[dict[str, object]], obpi_id: str) -> str:
    """Return the parent named on an OBPI's ``obpi_created`` record."""
    for event in events:
        if event.get("event") == "obpi_created" and str(event.get("id", "")) == obpi_id:
            return str(event.get("parent", ""))
    return ""


def apply_backfill(ledger: Ledger, planned: list[tuple[str, str, str]], attestor: str) -> int:
    """Append one ``obpi_parked`` event per planned orphan. Returns the count written."""
    for obpi_id, original_parent, parked_to in planned:
        event = obpi_parked_event(
            obpi_id,
            parent=original_parent,
            parked_to=parked_to,
            reason=_DEMOTION_REASON,
        )
        event.extra["backfill"] = "ghi-584"
        event.extra["attestor"] = attestor
        ledger.append(event)
    return len(planned)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the one-shot backfill."""
    parser = argparse.ArgumentParser(
        prog="gzkit.governance.obpi_park_backfill",
        description="Park the GHI #520 demotion-cohort OBPI orphans (GHI #584).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Report the plan; write nothing.")
    mode.add_argument("--apply", action="store_true", help="Append the park events.")
    parser.add_argument(
        "--attestor",
        default="",
        help="Human witness recorded on each backfilled park event (required with --apply).",
    )
    parser.add_argument(
        "--ledger",
        default=".gzkit/ledger.jsonl",
        help="Ledger path (default: .gzkit/ledger.jsonl).",
    )
    args = parser.parse_args(argv)

    ledger = Ledger(Path(args.ledger))
    planned = plan_backfill(ledger)

    if not planned:
        print("No demotion-cohort orphans found — nothing to park.")  # noqa: T201
        return 0

    by_parent: dict[str, int] = {}
    for _obpi_id, original_parent, _parked_to in planned:
        by_parent[original_parent] = by_parent.get(original_parent, 0) + 1
    print(f"Orphans to park: {len(planned)} across {len(by_parent)} parent ADRs")  # noqa: T201
    for parent, count in sorted(by_parent.items()):
        print(f"  {parent}: {count}")  # noqa: T201

    if args.dry_run:
        print("\nDry run — no events written. Re-run with --apply --attestor <name>.")  # noqa: T201
        return 0

    if not args.attestor.strip():
        print(  # noqa: T201
            "\nBackfill refused: --attestor is required with --apply.\n"
            "  Why: this appends 237 governance events asserting a disposition on\n"
            "  historical work; an unattested bulk ledger write is exactly the\n"
            "  unwitnessed-mutation failure AGENTS.md Never #2 guards against.\n"
            "  Next step: uv run python -m gzkit.governance.obpi_park_backfill "
            "--apply --attestor <name>",
            file=sys.stderr,
        )
        return 1

    written = apply_backfill(ledger, planned, args.attestor.strip())
    print(f"\nParked {written} orphaned OBPIs (attestor: {args.attestor.strip()}).")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
