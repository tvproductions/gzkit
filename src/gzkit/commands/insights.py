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
import sys
from typing import get_args

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
    p.set_defaults(
        func=lambda a: remember(
            insight_type=a.insight_type,
            scope=a.scope,
            summary=a.summary,
            evidence=a.evidence,
            next_action=a.next_action,
        )
    )


def remember(
    *,
    insight_type: InsightType,
    scope: str,
    summary: str,
    evidence: list[str] | None,
    next_action: str | None,
) -> None:
    """Handle ``gz insights remember --type ... --scope ... --summary ...``.

    Delegates to the mechanical writer, which constructs the record before it
    serializes. An empty required field raises ``ValidationError`` at
    construction — caught here and turned into exit 1 with no line written
    (out-of-enum ``--type`` is already rejected by argparse ``choices``).
    """
    from pydantic import ValidationError  # noqa: PLC0415

    from gzkit.commands.common import get_project_root  # noqa: PLC0415
    from gzkit.insights.append import (  # noqa: PLC0415
        DEFAULT_INSIGHTS_PATH,
        append_insight_record,
    )

    path = get_project_root() / DEFAULT_INSIGHTS_PATH
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

    print(f"Appended insight record to {path.as_posix()}: {line}")
