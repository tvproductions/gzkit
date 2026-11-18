"""``gz wp tag`` subparser registrations (RP-12 O3 tasks 2 to 4).

The nested group the operator ruled on 2026-11-16 (RP-12 ruling 110, *"A: gz wp
tag (Rec.)"*). Each leaf is written out literally, ``p_x = tag_commands.add_parser(...)``
then ``p_x.set_defaults(func=lambda a: _lazy(...)(...))``, and the group hangs from
a parameter named ``wp_commands``, the name ``register_wp_parsers`` binds to the
``gz wp`` subparsers, because the doc-coverage scanner discovers commands from that
shape. The closed sets are written here, not imported from ``gzkit.events``, so
building the parser tree imports no handler-only module (GHI #180).
"""

from typing import TYPE_CHECKING

from gzkit.cli.helpers import add_json_flag, build_epilog
from gzkit.cli.parser_handler_manifest import _lazy

if TYPE_CHECKING:
    import argparse

_ISSUE_EXAMPLES = [
    (
        "gz wp tag issue ORD-01-import --slug stamp-hook --class Danger"
        " --surface hook:dispatch-stamp --position off --hazard 'Stamps no root.'"
        " --removal-procedure 'Re-register the hook.' --source order-work --check-level C"
    ),
    (
        "gz wp tag issue ORD-01-import --slug hexagon --class Caution"
        " --surface validator:hexagon-tests --position advisory --hazard 'Map half built.'"
        " --removal-procedure 'Run the scope.' --source standard-disconnect --check-level D"
    ),
]
_SHOW_EXAMPLES = ["gz wp tag show", "gz wp tag show --all --json"]
_HANG_EXAMPLES = [
    "gz wp tag hang TAG-01-stamp-hook --dispatch D-717d53816678475f",
    "gz wp tag hang TAG-02-hexagon --dispatch D-717d53816678475f --json",
]
#: Every refusal of the hang is the writer's, a policy breach that books nothing.
_HANG_EXIT_CODES = """Exit codes
    0   Hung: the tag_hung event is booked
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: no MX session, the call not stamped with the named dispatch,
        the tag not open or already hung, the dispatch not a live Repair on its
        order, or the order not frozen, or blocked; nothing is booked
"""
_AUTHORIZE_EXAMPLES = [
    "gz wp tag authorize TAG-01-stamp-hook",
    "gz wp tag authorize TAG-02-hexagon --json",
]
#: Every refusal of the clearance is the writer's or the stamp's, and books nothing.
_AUTHORIZE_EXIT_CODES = """Exit codes
    0   Authorized: the tag_clearance_authorized event is booked
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: a subagent's call, no MX session, the tag not issued, not
        hung or already authorized, the order not commenced, or blocked, or the
        hanging dispatch still live; nothing is booked
"""
_CLEAR_EXAMPLES = [
    "gz wp tag clear TAG-01-stamp-hook --dispatch D-9c41f0e2a7b35d18 --position-found off",
    "gz wp tag clear TAG-02-hexagon --dispatch D-9c41f0e2a7b35d18 --position-found on --json",
]
#: A refusal books nothing; an out-of-position find books the order's block (ruling 137).
_CLEAR_EXIT_CODES = """Exit codes
    0   Cleared: the tag_cleared event is booked and the tag reads closed
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: found out of position, the order's block booked and the
        tag still hung; or refused, nothing booked: no MX session, the call not
        stamped with the named dispatch, the tag not hung, not authorized or
        already cleared, the dispatch not a live Restoration on its order, the
        subagent that hung it, or the order not commenced, or blocked
"""
#: `show` writes nothing; it exits 3 only on a ledger row it cannot read.
_SHOW_EXIT_CODES = """Exit codes
    0   Shown, an empty log included
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: a tag_issued row does not parse; void it
"""


def _register_wp_tag(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp tag`` and its five leaves, ``issue`` to ``clear``."""
    p_tag = wp_commands.add_parser(
        "tag",
        help="The tag-out log: tags isolating surfaces for a repair",
        description=(
            "Commands over the tag-out log, ledger events whose open tags are a\n"
            "derived view. A tag is TAG-<NN>-<slug> (RP-12 rulings 4, 110, 111)."
        ),
        epilog=build_epilog([*_ISSUE_EXAMPLES[:1], _SHOW_EXAMPLES[0]]),
    )
    tag_commands = p_tag.add_subparsers(dest="tag_command")
    tag_commands.required = True

    p_tag_issue = tag_commands.add_parser(
        "issue",
        help="Issue a tag on an opened or frozen order, as the coordinator",
        description=(
            "Book the coordinator's issue of one tag, its whole line item, with the\n"
            "next TAG-<NN>-<slug>, held by the open MX session. A subagent's call is\n"
            "refused (RP-12 rulings 6, 113, 114, 120 to 124)."
        ),
        epilog=build_epilog(_ISSUE_EXAMPLES),
    )
    p_tag_issue.add_argument("order", help="The order's id, ORD-<NN>-<slug>")
    p_tag_issue.add_argument("--slug", required=True, help="Lowercase words joined by hyphens")
    p_tag_issue.add_argument(
        "--class",
        dest="tag_class",
        required=True,
        choices=("Danger", "Caution"),
        help="Danger or Caution",
    )
    p_tag_issue.add_argument(
        "--surface", required=True, help="<kind>:<name>, kind validator|check|hook|path"
    )
    p_tag_issue.add_argument(
        "--position",
        required=True,
        choices=("off", "advisory", "recording"),
        help="The position it is to be hung in",
    )
    p_tag_issue.add_argument("--hazard", required=True, help="The hazard it guards against")
    p_tag_issue.add_argument(
        "--removal-procedure", required=True, help="How it is removed, legible to anyone"
    )
    p_tag_issue.add_argument(
        "--source",
        required=True,
        choices=("order-work", "standard-disconnect", "mel-bypass", "surveillant-stop"),
        metavar="SOURCE",
        help="order-work, standard-disconnect, mel-bypass or surveillant-stop",
    )
    p_tag_issue.add_argument("--check-level", required=True, help="The check level, C or D")
    add_json_flag(p_tag_issue)
    p_tag_issue.set_defaults(
        func=lambda a: _lazy("wp_tag_issue_cmd")(
            line_item={
                "slug": a.slug,
                "order": a.order,
                "tag_class": a.tag_class,
                "surface": a.surface,
                "position": a.position,
                "hazard": a.hazard,
                "removal_procedure": a.removal_procedure,
                "source": a.source,
                "check_level": a.check_level,
            },
            called_by_subagent=bool(getattr(a, "called_by_subagent", False)),
            as_json=a.as_json,
        )
    )

    p_tag_show = tag_commands.add_parser(
        "show",
        help="Show the tag-out log: the open tags, or every tag with --all",
        description=(
            "Render the tag-out log from the ledger's tag events, a read-only Layer 3\n"
            "view: the open tags by default, every tag with --all (RP-12 rulings 4, 110)."
        ),
        epilog=build_epilog(_SHOW_EXAMPLES, exit_codes=_SHOW_EXIT_CODES),
    )
    p_tag_show.add_argument(
        "--all",
        dest="every",
        action="store_true",
        help="Every tag issued, open and closed, each marked which",
    )
    add_json_flag(p_tag_show)
    p_tag_show.set_defaults(
        func=lambda a: _lazy("wp_tag_show_cmd")(every=a.every, as_json=a.as_json)
    )

    p_tag_hang = tag_commands.add_parser(
        "hang",
        help="Hang an issued tag, as the Repair dispatch's stamped call",
        description=(
            "Book the Repair dispatch's hang of one issued tag, its line item copied\n"
            "from the issue, held by the open MX session. Only the call stamped with\n"
            "the dispatch it names may hang (RP-12 rulings 6, 120, 129 to 133)."
        ),
        epilog=build_epilog(_HANG_EXAMPLES, exit_codes=_HANG_EXIT_CODES),
    )
    p_tag_hang.add_argument("tag", help="The tag's id, TAG-<NN>-<slug>")
    p_tag_hang.add_argument(
        "--dispatch",
        required=True,
        metavar="D-ID",
        help="The live Repair dispatch hanging it, the one this call is stamped with",
    )
    add_json_flag(p_tag_hang)
    p_tag_hang.set_defaults(
        func=lambda a: _lazy("wp_tag_hang_cmd")(
            tag_id=a.tag,
            dispatch_id=a.dispatch,
            stamped_dispatch_id=getattr(a, "stamped_dispatch_id", None),
            as_json=a.as_json,
        )
    )

    p_tag_authorize = tag_commands.add_parser(
        "authorize",
        help="Authorize a hung tag's clearance, as the coordinator",
        description=(
            "Book the coordinator's clearance authorized for one hung tag on a\n"
            "commenced order, the repair activity marked not available from the\n"
            "hanging dispatch's end or void. A subagent's call is refused (RP-12\n"
            "rulings 6, 7, 114, 115, 118, 138)."
        ),
        epilog=build_epilog(_AUTHORIZE_EXAMPLES, exit_codes=_AUTHORIZE_EXIT_CODES),
    )
    p_tag_authorize.add_argument("tag", help="The hung tag's id, TAG-<NN>-<slug>")
    add_json_flag(p_tag_authorize)
    p_tag_authorize.set_defaults(
        func=lambda a: _lazy("wp_tag_authorize_cmd")(
            tag_id=a.tag,
            called_by_subagent=bool(getattr(a, "called_by_subagent", False)),
            as_json=a.as_json,
        )
    )

    p_tag_clear = tag_commands.add_parser(
        "clear",
        help="Clear an authorized tag, as the Restoration dispatch's stamped call",
        description=(
            "Book the Restoration dispatch's clear of one hung tag whose clearance\n"
            "is authorized, recording the position found. Found out of position, it\n"
            "blocks the order and leaves the tag hung. Only the call stamped with\n"
            "the dispatch it names may clear (RP-12 rulings 6, 129, 137 to 140)."
        ),
        epilog=build_epilog(_CLEAR_EXAMPLES, exit_codes=_CLEAR_EXIT_CODES),
    )
    p_tag_clear.add_argument("tag", help="The hung tag's id, TAG-<NN>-<slug>")
    p_tag_clear.add_argument(
        "--dispatch",
        required=True,
        metavar="D-ID",
        help="The live Restoration dispatch clearing it, the one this call is stamped with",
    )
    p_tag_clear.add_argument(
        "--position-found",
        required=True,
        choices=("off", "advisory", "recording", "on"),
        help="The position the surface was found in; any but the hung one is out of position",
    )
    add_json_flag(p_tag_clear)
    p_tag_clear.set_defaults(
        func=lambda a: _lazy("wp_tag_clear_cmd")(
            tag_id=a.tag,
            dispatch_id=a.dispatch,
            position_found=a.position_found,
            stamped_dispatch_id=getattr(a, "stamped_dispatch_id", None),
            as_json=a.as_json,
        )
    )
