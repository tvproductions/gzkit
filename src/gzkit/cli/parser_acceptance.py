"""Acceptance command registration kept beside its OBPI parent parser."""

import argparse

from gzkit.cli.helpers import add_json_flag
from gzkit.cli.parser_handler_manifest import _lazy


def configure_acceptance_parser(parser: argparse.ArgumentParser) -> None:
    """Configure arguments for the leaf registered in its OBPI parent."""
    parser.add_argument("obpi", help="Canonical OBPI identifier")
    parser.add_argument(
        "action",
        choices=("init", "prove", "review", "human-review", "status"),
        help="Acceptance operation to execute",
    )
    parser.add_argument("--author", help="Implementing session identity (init)")
    parser.add_argument("--spec", help="JSON proof instructions, never execution results (prove)")
    parser.add_argument(
        "--receipt", help="ARB execution run ID containing the review JSON (review)"
    )
    parser.add_argument(
        "--stage",
        choices=("stage2", "stage4"),
        default="stage4",
        help="Readiness boundary to inspect (default: stage4)",
    )
    parser.add_argument(
        "--req", action="append", dest="req_ids", help="Intermediate Stage-2 requirement scope"
    )
    parser.add_argument(
        "--attestor", help="Operator identity for explicitly authorized human-review"
    )
    parser.add_argument(
        "--ruling", help="Operator's verbatim judgment of current proof and findings"
    )
    add_json_flag(parser)


def acceptance_handler(a: argparse.Namespace) -> int:
    """Resolve lazily and propagate refusals through the CLI's SystemExit contract."""
    code = _lazy("obpi_acceptance_cmd")(
        obpi_id=a.obpi,
        action=a.action,
        author=a.author,
        specification=a.spec,
        receipt=a.receipt,
        stage=a.stage,
        as_json=a.as_json,
        req_ids=a.req_ids,
        attestor=a.attestor,
        ruling=a.ruling,
    )
    # cli.main ignores returned values; only SystemExit carries failure to
    # the shell (the same adapter convention as the ARB command family).
    if code:
        raise SystemExit(code)
    return 0
