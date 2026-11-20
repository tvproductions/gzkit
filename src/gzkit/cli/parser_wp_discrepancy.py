"""``gz wp discrepancy`` subparser registrations (RP-12 O4 task 2).

The group the operator ruled on 2026-11-20 (RP-12 ruling 168, *"A: Two groups
(Rec.)"*). Each leaf is written out literally, ``p_x = discrepancy_commands.add_parser(...)``
then ``p_x.set_defaults(func=lambda a: _lazy(...)(...))``, and the group hangs from
a parameter named ``wp_commands``, the name ``register_wp_parsers`` binds to the
``gz wp`` subparsers, because the doc-coverage scanner discovers commands from that
shape. Building the parser tree imports no handler-only module (GHI #180).
"""

from typing import TYPE_CHECKING

from gzkit.cli.helpers import add_json_flag, build_epilog
from gzkit.cli.parser_handler_manifest import _lazy

if TYPE_CHECKING:
    import argparse

#: The members of ``gzkit.events.DiscrepancyGrade`` and ``DiscrepancySource``, spelled
#: out as the sibling parsers spell theirs: a driving adapter imports no module outside
#: its region's row (`docs/governance/hexagonal-architecture.md` § The dependency
#: rules). ``DiscrepancyChoicesTests`` holds them equal to the closed sets.
_GRADES = ("blocks-return-to-service", "due-by-event")
_SOURCES = ("left-broken", "inspector-rejection", "found-in-work")

_RECORD_EXAMPLES = [
    (
        "gz wp discrepancy record --order ORD-01-import --slug hook-left-off"
        " --grade blocks-return-to-service --source left-broken"
        " --description 'The stamp hook is left off.'"
    ),
    (
        "gz wp discrepancy record --order ORD-01-import --slug size-gate"
        ' --grade due-by-event --due-by "O9\'s carry" --source left-broken'
        " --description 'The size gate stays advisory.' --tag TAG-01-size"
    ),
    (
        "gz wp discrepancy record --dispatch D-717d53816678475f --slug stale-cache"
        " --grade due-by-event --due-by 'the next order' --source found-in-work"
        " --description 'The cache is never invalidated.'"
    ),
]
_SHOW_EXAMPLES = ["gz wp discrepancy show", "gz wp discrepancy show --all --json"]
#: `show` writes nothing; it exits 3 only on a ledger row it cannot read.
_SHOW_EXIT_CODES = """Exit codes
    0   Shown, an empty list included
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: a discrepancy row does not parse; void it
"""
_CLEAR_EXAMPLES = [
    "gz wp discrepancy clear DSC-02-size-gate --entry ENT-03-size-restored",
    (
        "gz wp discrepancy clear DSC-01-hook-left-off --tag TAG-02-hook"
        " --root-cause 'The hook was disabled for the repair.'"
        " --corrective-action 'The order restores it before close.'"
    ),
    "gz wp discrepancy clear DSC-03-stale-cache --ghi 1412 --json",
]
#: Every refusal of a record is the writer's, the marker's or the stamp's, and books nothing.
_RECORD_EXIT_CODES = """Exit codes
    0   Recorded: the discrepancy_recorded event is booked
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: no MX session or a marker present but not on, a
        malformed slug, a blank description, a grade and --due-by that
        disagree, an inspector's rejection (O6), the coordinator's line with
        no --order or with --dispatch, a performer's call not stamped as its
        dispatch, not a find in the work, typing --order or --tag, or its
        dispatch not a live Implementer, SingleDriver or Restoration, an order
        not held, not opened or closed, or of a package not initiated, or a
        tag not on the order; nothing is booked
"""
#: A clear exits 2 when `gh` cannot read the issue it cites; every other refusal is 3.
_CLEAR_EXIT_CODES = """Exit codes
    0   Cleared: the discrepancy_cleared event is booked
    1   User/config error: the project is not initialized
    2   Usage or System/IO error, or the issue --ghi cites could not be read
        through gh; nothing is booked
    3   Policy breach: a subagent's call, no MX session or a marker present
        but not on, a line not recorded or already cleared, no evidence, an
        entry or tag not of the line's package or a tag not cleared, an issue
        closed, a blank field, root cause and corrective action missing where
        the line blocks return to service or recurs, or --recurs on a blocking
        line or short of the recurrence threshold; nothing is booked
"""


def _register_wp_discrepancy(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp discrepancy`` and its leaves, ``record``, ``clear`` and ``show``."""
    p_discrepancy = wp_commands.add_parser(
        "discrepancy",
        help="The list of discrepancies: one line per discrepancy, cleared with evidence",
        description=(
            "Commands over the list of discrepancies, ledger events rendered as a\n"
            "view. A line is DSC-<NN>-<slug> (RP-12 rulings 9, 168, 169)."
        ),
        epilog=build_epilog([_RECORD_EXAMPLES[0], _CLEAR_EXAMPLES[0], _SHOW_EXAMPLES[0]]),
    )
    discrepancy_commands = p_discrepancy.add_subparsers(dest="discrepancy_command")
    discrepancy_commands.required = True

    p_discrepancy_record = discrepancy_commands.add_parser(
        "record",
        help="Record a line: the coordinator's on an order, or a performer's find",
        description=(
            "Record one discrepancy on an order, graded blocks-return-to-service\n"
            "or due-by-event with the event in text, under the open MX session. The\n"
            "coordinator's unstamped call names --order; a performer's stamped call\n"
            "names its --dispatch and records a find in the work (RP-12 rulings 9,\n"
            "172, 178, 179)."
        ),
        epilog=build_epilog(_RECORD_EXAMPLES, exit_codes=_RECORD_EXIT_CODES),
    )
    p_discrepancy_record.add_argument(
        "--slug", required=True, help="Lowercase words joined by hyphens"
    )
    p_discrepancy_record.add_argument(
        "--grade", required=True, choices=_GRADES, help="The line's grade"
    )
    p_discrepancy_record.add_argument(
        "--source", required=True, choices=_SOURCES, help="Where it comes from"
    )
    p_discrepancy_record.add_argument("--description", required=True, help="What is wrong")
    p_discrepancy_record.add_argument(
        "--due-by", help="The event a due-by-event line is due by, in text"
    )
    p_discrepancy_record.add_argument(
        "--order", metavar="ORD-ID", help="The line's order, the coordinator's call"
    )
    p_discrepancy_record.add_argument(
        "--dispatch",
        metavar="D-ID",
        help="The live performer that found it, the one this call is stamped with",
    )
    p_discrepancy_record.add_argument(
        "--tag", metavar="TAG-ID", help="A tag issued on the order the line carries"
    )
    add_json_flag(p_discrepancy_record)
    p_discrepancy_record.set_defaults(
        func=lambda a: _lazy("wp_discrepancy_record_cmd")(
            request={
                "slug": a.slug,
                "grade": a.grade,
                "source": a.source,
                "description": a.description,
                "due_by": a.due_by,
                "order": a.order,
                "dispatch": a.dispatch,
                "tag": a.tag,
            },
            called_by_subagent=bool(getattr(a, "called_by_subagent", False)),
            stamped_dispatch_id=getattr(a, "stamped_dispatch_id", None),
            as_json=a.as_json,
        )
    )

    p_discrepancy_clear = discrepancy_commands.add_parser(
        "clear",
        help="Clear a line on its evidence, the coordinator's call",
        description=(
            "Clear one discrepancy on an entry, a cleared tag or the open issue it\n"
            "was filed as, which gh confirms, with root cause and corrective action\n"
            "on a line that blocks return to service or recurs (RP-12 rulings 172,\n"
            "180, 181)."
        ),
        epilog=build_epilog(_CLEAR_EXAMPLES, exit_codes=_CLEAR_EXIT_CODES),
    )
    p_discrepancy_clear.add_argument("discrepancy", help="The line's id, DSC-<NN>-<slug>")
    p_discrepancy_clear.add_argument(
        "--entry", metavar="ENT-ID", help="An entry of the line's package"
    )
    p_discrepancy_clear.add_argument(
        "--tag", metavar="TAG-ID", help="A cleared tag of the line's package"
    )
    p_discrepancy_clear.add_argument(
        "--ghi", type=int, metavar="N", help="The open issue the line was filed as"
    )
    p_discrepancy_clear.add_argument("--root-cause", help="The line's root cause")
    p_discrepancy_clear.add_argument("--corrective-action", help="The line's corrective action")
    p_discrepancy_clear.add_argument(
        "--recurs",
        action="append",
        default=[],
        metavar="CITE",
        help="An insight ts or #GHI of the same failure; repeatable",
    )
    add_json_flag(p_discrepancy_clear)
    p_discrepancy_clear.set_defaults(
        func=lambda a: _lazy("wp_discrepancy_clear_cmd")(
            request={
                "discrepancy": a.discrepancy,
                "entry": a.entry,
                "tag": a.tag,
                "ghi": a.ghi,
                "root_cause": a.root_cause,
                "corrective_action": a.corrective_action,
                "recurs": tuple(a.recurs),
            },
            called_by_subagent=bool(getattr(a, "called_by_subagent", False)),
            as_json=a.as_json,
        )
    )

    p_discrepancy_show = discrepancy_commands.add_parser(
        "show",
        help="Show the list of discrepancies: the open lines, or every line with --all",
        description=(
            "Render the list of discrepancies from the ledger's discrepancy events,\n"
            "a read-only Layer 3 view, oldest first: the open lines by default,\n"
            "every line with --all, each with its clear (RP-12 rulings 9, 168)."
        ),
        epilog=build_epilog(_SHOW_EXAMPLES, exit_codes=_SHOW_EXIT_CODES),
    )
    p_discrepancy_show.add_argument(
        "--all",
        dest="every",
        action="store_true",
        help="Every line recorded, open and cleared, each marked which",
    )
    add_json_flag(p_discrepancy_show)
    p_discrepancy_show.set_defaults(
        func=lambda a: _lazy("wp_discrepancy_show_cmd")(every=a.every, as_json=a.as_json)
    )
