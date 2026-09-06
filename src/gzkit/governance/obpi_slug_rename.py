"""Record a slug correction to an OBPI id as a forward ``artifact_renamed`` event.

An OBPI's slug can stop describing its brief — a design is revised, the work is
repurposed rather than withdrawn, and the id keeps the name of the thing that was
withdrawn. Correcting the name on disk moves Layer-1 without moving Layer-2, and
``obpi_created`` then asserts a brief at an id nothing on disk carries. The
ledger is append-only (``AGENTS.md`` Never #2), so the correction is composed
from a new forward event, never an edit.

**Why this is not ``gz migrate-semver``.** That verb's disk-drift detector is
scoped to the bare→slug class by construction (GHI #345): it derives the OLD id
by extracting the bare form from an on-disk stem, so it can propose
``OBPI-0.1.0-01 -> OBPI-0.1.0-01-gz-init`` and nothing else. A slug→slug
correction has no bare form to derive from, and a detector that scanned for one
would have to guess which retired id a new stem replaces — over a corpus where
briefs are also legitimately withdrawn, parked, and re-authored at the same item
number. That guess, written in bulk to an append-only ledger, is the shape of
both GHI #584 (237 bad records) and its 356-event backfill. So this names both
ids explicitly and repairs one at a time.

Not a ``gz`` verb: a narrow governed repair, invoked as
``uv run python -m gzkit.governance.obpi_slug_rename --old <id> --new <id>
--reason <text> --attestor <name> --dry-run``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gzkit.ledger import Ledger, extract_bare_obpi_id
from gzkit.ledger_events import artifact_renamed_event
from gzkit.obpi_lifecycle import (
    COMPLETION_EVENTS,
    TERMINAL_EVENTS,
    park_state,
    rename_chain_target,
)

_ADR_ROOT = Path("docs") / "design" / "adr"


def _brief_stems(project_root: Path) -> set[str]:
    """Every OBPI brief id currently on disk, by filename stem (Layer-1)."""
    return {path.stem for path in (project_root / _ADR_ROOT).rglob("OBPI-*.md")}


def _disposition_of(events: list[dict[str, object]], obpi_id: str) -> str | None:
    """Return the disposition retiring *obpi_id*, or ``None`` if it is live.

    A disposed OBPI must not be renamed: the census already excludes it, so the
    rename would be a Layer-2 write with no witness behind it, and the id it
    retires under is part of the sealed record.
    """
    for event in events:
        if str(event.get("id", "")) != obpi_id:
            continue
        kind = str(event.get("event", ""))
        if kind in TERMINAL_EVENTS or kind in COMPLETION_EVENTS:
            return kind
    if park_state(events).get(obpi_id, False):
        return "obpi_parked"
    return None


def _refusals(
    events: list[dict[str, object]], stems: set[str], old_id: str, new_id: str
) -> list[str]:
    """Return every precondition *old_id* → *new_id* fails, or an empty list.

    Fail-closed and complete: all refusals are reported at once rather than one
    per run, so an operator fixing an invocation sees the whole set.
    """
    problems: list[str] = []
    known = {str(event.get("id", "")) for event in events}

    if old_id not in known:
        problems.append(f"{old_id} carries no ledger events — nothing to rename")
    if old_id in stems:
        problems.append(f"{old_id} is still on disk — rename the brief first, then record it")
    if new_id not in stems:
        problems.append(f"{new_id} is not on disk — the new id must name a real brief")
    if extract_bare_obpi_id(old_id) != extract_bare_obpi_id(new_id):
        problems.append(
            f"{old_id} and {new_id} are different OBPIs, not one renamed — a slug "
            "correction preserves the ADR semver and item number"
        )
    if (disposition := _disposition_of(events, old_id)) is not None:
        problems.append(
            f"{old_id} is already retired by `{disposition}` — a disposed id is "
            "sealed record, not a live name to correct"
        )
    if (current := rename_chain_target(events, old_id)) != old_id:
        problems.append(f"{old_id} was already renamed to {current}")
    return problems


def main(argv: list[str] | None = None) -> int:
    """Record one OBPI slug correction. Dry-run unless ``--apply`` is passed."""
    parser = argparse.ArgumentParser(
        prog="python -m gzkit.governance.obpi_slug_rename",
        description="Record an OBPI slug correction as a forward artifact_renamed event.",
    )
    parser.add_argument("--old", required=True, help="Current ledger id (the stale slug)")
    parser.add_argument("--new", required=True, help="Corrected id, already on disk")
    parser.add_argument("--reason", required=True, help="Why the slug no longer describes it")
    parser.add_argument("--attestor", required=True, help="Who authorized the correction")
    parser.add_argument("--apply", action="store_true", help="Write the event (default: dry run)")
    args = parser.parse_args(argv)

    project_root = Path.cwd()
    ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
    events = [event.model_dump() for event in ledger.read_all()]

    problems = _refusals(events, _brief_stems(project_root), args.old, args.new)
    if problems:
        print(f"Refused: {args.old} -> {args.new}", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    if not args.apply:
        print(f"Dry run: would record artifact_renamed {args.old} -> {args.new}")
        print(f"  reason:   {args.reason}")
        print(f"  attestor: {args.attestor}")
        return 0

    ledger.append(
        artifact_renamed_event(
            old_id=args.old,
            new_id=args.new,
            reason=f"obpi_slug_correction ({args.reason}; attestor: {args.attestor})",
        )
    )
    print(f"Recorded artifact_renamed: {args.old} -> {args.new}")
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
