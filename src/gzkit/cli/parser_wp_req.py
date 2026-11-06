"""``gz wp req`` subparser registrations (RP-12 O2 task 2).

The verb the operator ruled on 2026-11-05 (RP-12 ruling 48, *"a"*). The leaf is
written out literally, ``p_x = req_commands.add_parser(...)`` then
``p_x.set_defaults(func=lambda a: _lazy(...)(...))``, and the group hangs from a
parameter named ``wp_commands``, the name ``register_wp_parsers`` binds to the
``gz wp`` subparsers, because the doc-coverage scanner discovers commands from
that shape.
"""

from typing import TYPE_CHECKING

from gzkit.cli.helpers import add_json_flag, build_epilog
from gzkit.cli.parser_handler_manifest import _lazy

if TYPE_CHECKING:
    import argparse

_EXAMPLE = (
    "gz wp req new WP-01-stamp --statement 'The hook imports a public name.' "
    "--criterion 'the hook is generated|it imports a public name|the import ratchet test' "
    "--kind BEHAVIOR --problem-report 1301"
)


def _register_wp_req(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp req`` and its ``new`` subcommand."""
    p_req = wp_commands.add_parser(
        "req",
        help="Repair requirements, held on their repair package",
        description=(
            "Commands over the repair requirements in data/catalog/reqs.json,\n"
            "each held on its repair package (RP-12 rulings 45 and 48)."
        ),
        epilog=build_epilog([_EXAMPLE]),
    )
    req_commands = p_req.add_subparsers(dest="req_command")
    req_commands.required = True

    p_req_new = req_commands.add_parser(
        "new",
        help="Write a repair REQ with the next id, held on its repair package",
        description=(
            "Write one repair REQ with the next REQ-<n>, held on a repair package\n"
            "that is initiated and not closed, answering an issue it carries."
        ),
        epilog=build_epilog(
            [_EXAMPLE, "gz wp req new WP-01-stamp ... --supersedes REQ-5 --aligns-to REQ-4"]
        ),
    )
    p_req_new.add_argument("work_package", help="The repair package's id, WP-<NN>-<slug>")
    p_req_new.add_argument("--statement", required=True, help="Effect and rationale")
    p_req_new.add_argument(
        "--criterion",
        dest="criteria",
        action="append",
        required=True,
        help="STATE|OUTCOME|EVIDENCE (repeatable, at least one)",
    )
    p_req_new.add_argument(
        "--kind",
        required=True,
        choices=("BEHAVIOR", "SUPPORT", "STRUCTURAL-FENCE"),
        help="Which proof channel binds it",
    )
    p_req_new.add_argument(
        "--problem-report",
        type=int,
        required=True,
        help="The issue it answers, one the package carries",
    )
    p_req_new.add_argument("--aligns-to", default=None, help="A catalog REQ of design it aligns to")
    p_req_new.add_argument("--supersedes", default=None, help="The REQ it supersedes")
    add_json_flag(p_req_new)
    p_req_new.set_defaults(
        func=lambda a: _lazy("wp_req_new_cmd")(
            work_package=a.work_package,
            record={
                "statement": a.statement,
                "kind": a.kind,
                "problem_report": a.problem_report,
                "aligns_to": a.aligns_to,
                "supersedes": a.supersedes,
            },
            criteria=a.criteria,
            as_json=a.as_json,
        )
    )
