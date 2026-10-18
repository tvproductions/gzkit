"""gz insights subparser registrations and the ``remember`` handler (GHI #575).

``gz insights remember`` is the governed author verb for the append-only
insights store at ``.gzkit/insights/agent-insights.jsonl``. It wraps the
mechanical writer in ``gzkit.insights.append``: the payload is *constructed*
into an ``InsightRecord`` and then serialized, so a missing or malformed
required field fails closed (non-zero exit, no line written) instead of
drifting past the schema the way hand-authored appends did.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, get_args

from gzkit.insights.model import InsightType

# ``get_project_root``, the append writer, and pydantic's ``ValidationError`` are
# needed only by ``remember`` and are imported there instead. ``main.py`` imports
# this module eagerly to build the parser tree, so a module-scope
# ``gzkit.commands.common`` import puts it — and transitively ``gzkit.sync`` and
# ``yaml`` — on the ``gz --help`` path, which is the cost GHI #180 exists to keep
# off it. ``InsightType`` stays at module scope: ``_register_remember`` needs it
# at registration time for ``choices``. Guard: tests/cli/test_help_path_imports.py.


def _build_epilog(examples: list[str]) -> str:
    from gzkit.cli.helpers import build_epilog  # noqa: PLC0415

    return build_epilog(examples)


def register_insights_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz insights`` sub-command group."""
    p_insights = commands.add_parser(
        "insights",
        help="Governed authoring for the append-only insights store",
        description=(
            "Commands for appending schema-valid records to the append-only insights "
            "store at .gzkit/insights/agent-insights.jsonl. The store gates on the "
            "InsightRecord schema; hand-authored lines drift from it, so `remember` "
            "constructs-then-serializes to make a missing required field impossible."
        ),
        epilog=_build_epilog(
            [
                "gz insights remember --type improvement --scope obpi-pipeline "
                '--summary "governed author verb replaces hand-authored appends"',
                "gz insights remember --type defect --scope gzkit.cli "
                '--summary "verb drifted from schema" '
                '--evidence "uv run -m unittest tests.commands.test_insights_cmd"',
            ]
        ),
    )
    insights_commands = p_insights.add_subparsers(dest="insights_command")
    insights_commands.required = True

    _register_remember(insights_commands)
    _register_recurrence(insights_commands)


def _register_recurrence(insights_commands: argparse._SubParsersAction) -> None:
    p = insights_commands.add_parser(
        "recurrence",
        help="Check whether cited records qualify a failure to become a rule",
        description=(
            "Resolve each cited insight (by its ts) or GHI (#N) to its full timestamp and "
            "report whether the citations reach the recurrence threshold in "
            "data/recurrence_threshold.json with every pair at least one session lease "
            "apart (maxim 13; operator rulings 2026-10-18). Exits 3 when not met."
        ),
        epilog=_build_epilog(
            [
                "gz insights recurrence 2026-10-01T09:00:00+00:00 '#1257' '#1258'",
                "gz insights recurrence 2026-10-01T09:00:00+00:00 '#1257' --json",
            ]
        ),
    )
    p.add_argument(
        "cites",
        nargs="+",
        metavar="CITE",
        help="An insight record's ts, or a GHI number as #N or N.",
    )
    p.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON to stdout.")
    p.set_defaults(func=lambda a: recurrence(cites=a.cites, as_json=a.as_json))


def _register_remember(insights_commands: argparse._SubParsersAction) -> None:
    p = insights_commands.add_parser(
        "remember",
        help="Append one schema-valid record to the insights store",
        description=(
            "Construct an InsightRecord from the supplied payload and append exactly one "
            "serialized line to .gzkit/insights/agent-insights.jsonl. Fails closed "
            "(non-zero exit, no line written) when --type/--scope/--summary is empty or "
            "--type is out of the InsightType enum — construction is what enforces the schema."
        ),
        epilog=_build_epilog(
            [
                "gz insights remember --type discovery --scope survey "
                '--summary "found N drifted insight lines"',
                "gz insights remember --type defect-resolution --scope gzkit.insights "
                '--summary "verb now constructs-then-serializes" '
                '--next-action "delete the hand-authored append path"',
            ]
        ),
    )
    p.add_argument(
        "--type",
        dest="insight_type",
        required=True,
        choices=list(get_args(InsightType)),
        help="Record kind: defect | defect-resolution | improvement | discovery.",
    )
    p.add_argument("--scope", required=True, help="Surface or skill the record names.")
    p.add_argument("--summary", required=True, help="One-sentence record body.")
    p.add_argument(
        "--evidence",
        action="append",
        default=None,
        help="Command or path witnessing the record (repeatable).",
    )
    p.add_argument(
        "--next-action",
        dest="next_action",
        default=None,
        help="What changes structurally to prevent recurrence.",
    )
    p.add_argument(
        "--source",
        choices=["operator", "agent"],
        default="agent",
        help="Whose words the record carries; booked on the ledger pointer (default: agent).",
    )
    p.add_argument(
        "--supersedes",
        default=None,
        help="ts of an earlier record this one supersedes; refused when no record has it.",
    )
    p.set_defaults(
        func=lambda a: remember(
            insight_type=a.insight_type,
            scope=a.scope,
            summary=a.summary,
            evidence=a.evidence,
            next_action=a.next_action,
            source=a.source,
            supersedes=a.supersedes,
        )
    )


def remember(
    *,
    insight_type: InsightType,
    scope: str,
    summary: str,
    evidence: list[str] | None,
    next_action: str | None,
    source: Literal["operator", "agent"] = "agent",
    supersedes: str | None = None,
) -> None:
    """Handle ``gz insights remember --type ... --scope ... --summary ...``.

    Delegates to the mechanical writer, which constructs the record before it
    serializes. An empty required field raises ``ValidationError`` at
    construction — caught here and turned into exit 1 with no line written
    (out-of-enum ``--type`` is already rejected by argparse ``choices``).

    The record is then named in the ledger by one ``insight_recorded`` event
    (operator ruling 2026-10-18). A ``supersedes`` that names no existing record is
    refused before anything is written.
    """
    from pydantic import ValidationError  # noqa: PLC0415

    from gzkit.commands.common import get_project_root  # noqa: PLC0415
    from gzkit.insights.append import (  # noqa: PLC0415
        DEFAULT_INSIGHTS_PATH,
        append_insight_record,
    )
    from gzkit.insights.ledger_ref import (  # noqa: PLC0415
        book_insight_recorded,
        insight_lines_by_ts,
    )

    root = get_project_root()
    path = root / DEFAULT_INSIGHTS_PATH
    if supersedes is not None and supersedes not in insight_lines_by_ts(path):
        print(
            f"Error: --supersedes {supersedes} names no record in {path.as_posix()}; "
            "no line written.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        line = append_insight_record(
            type=insight_type,
            scope=scope,
            summary=summary,
            evidence=evidence,
            next_action=next_action,
            path=path,
        )
    except ValidationError as exc:
        print(
            f"Error: invalid insight record; no line written.\n{exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    book_insight_recorded(
        root / ".gzkit" / "ledger.jsonl", line, source=source, supersedes=supersedes
    )
    print(f"Appended insight record to {path.as_posix()}: {line}")


def gh_issue_created_at(number: str, project_root: Path) -> datetime | None:
    """Return a GHI's creation time via the ``gh`` read verb, or None when unresolved."""
    from gzkit.utils import run_exec  # noqa: PLC0415

    rc, out, _ = run_exec(
        ["gh", "issue", "view", number, "--json", "createdAt"], project_root, timeout=10
    )
    if rc != 0:
        return None
    try:
        created = json.loads(out).get("createdAt")
        return datetime.fromisoformat(created) if isinstance(created, str) else None
    except (json.JSONDecodeError, AttributeError, ValueError):
        return None


def _resolve_cite(cite: str, store: dict[str, str], root: Path) -> tuple[str, datetime] | None:
    """Map one citation to its label and full timestamp, or None when it names nothing."""
    number = cite.removeprefix("#")
    if number.isdigit():
        created = gh_issue_created_at(number, root)
        return (f"#{number}", created) if created is not None else None
    if cite not in store:
        return None
    stamp = datetime.fromisoformat(cite)
    return cite, stamp if stamp.tzinfo else stamp.replace(tzinfo=UTC)


def recurrence(*, cites: list[str], as_json: bool) -> None:
    """Handle ``gz insights recurrence CITE...``: the maxim-13 recurrence check.

    Exit 0 when the citations reach the threshold with every pair a session lease
    apart, 3 when they do not, 1 when a citation names no insight record or GHI.
    """
    from gzkit import lock_manager  # noqa: PLC0415
    from gzkit.cli.formatters import OutputFormatter  # noqa: PLC0415
    from gzkit.commands.common import get_project_root  # noqa: PLC0415
    from gzkit.insights.append import DEFAULT_INSIGHTS_PATH  # noqa: PLC0415
    from gzkit.insights.ledger_ref import insight_lines_by_ts  # noqa: PLC0415
    from gzkit.insights.recurrence import (  # noqa: PLC0415
        check_recurrence,
        load_min_occurrences,
    )

    root = get_project_root()
    store = insight_lines_by_ts(root / DEFAULT_INSIGHTS_PATH)
    resolved: dict[str, datetime] = {}
    for cite in cites:
        found = _resolve_cite(cite, store, root)
        if found is None:
            print(f"Error: {cite} names no insight record or resolvable GHI.", file=sys.stderr)
            sys.exit(1)
        resolved[found[0]] = found[1]

    verdict = check_recurrence(
        resolved,
        min_occurrences=load_min_occurrences(root),
        separation_hours=lock_manager.DEFAULT_LOCK_TTL_MINUTES / 60,
    )
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.data(verdict.model_dump(mode="json"))
    else:
        state = "met" if verdict.met else "not met"
        fmt.emit(
            f"Recurrence {state}: {verdict.cited} cited of {verdict.required} required, "
            f"each pair at least {verdict.separation_hours:g} h apart."
        )
        for a, b in verdict.too_close:
            fmt.emit(f"  one occurrence: {a} and {b} are inside one lease")
    sys.exit(0 if verdict.met else 3)
