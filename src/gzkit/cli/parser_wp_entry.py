"""``gz wp entry`` subparser registrations (RP-12 O4 task 1).

The group the operator ruled on 2026-11-20 (RP-12 ruling 168, *"A: Two groups
(Rec.)"*). Each leaf is written out literally, ``p_x = entry_commands.add_parser(...)``
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

_BOOK_EXAMPLES = [
    (
        "gz wp entry book --dispatch D-717d53816678475f --slug stamp-import"
        " --description 'The stamp generator imports its template again.'"
        " --before 'tests.test_stamp fails: ImportError' --after 'tests.test_stamp passes'"
        " --witness 'uv run -m unittest tests.test_stamp'"
    ),
    (
        "gz wp entry book --dispatch D-9c41f0e2a7b35d18 --slug hexagon-restored"
        " --description 'Restored the hexagon-tests scope.' --before 'scope advisory'"
        " --after 'scope on, 0 findings' --witness 'uv run gz validate --hexagon-tests'"
        " --json"
    ),
]
#: Every refusal of the entry is the writer's or the marker's, and books nothing.
_BOOK_EXIT_CODES = """Exit codes
    0   Booked: the entry_booked event is booked
    1   User/config error: the project is not initialized
    2   Usage or System/IO error
    3   Policy breach: no MX session or a marker present but not on, the call
        not stamped with the named dispatch, a blank field or a malformed slug,
        the dispatch not a live Implementer, SingleDriver or Restoration on an
        order, or the order not commenced, or blocked; nothing is booked
"""


def _register_wp_entry(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp entry`` and its leaf ``book``."""
    p_entry = wp_commands.add_parser(
        "entry",
        help="The maintenance record: one entry per act of maintenance",
        description=(
            "Commands over the maintenance record, ledger events rendered as a\n"
            "view. An entry is ENT-<NN>-<slug> (RP-12 rulings 8, 168, 169)."
        ),
        epilog=build_epilog(_BOOK_EXAMPLES[:1]),
    )
    entry_commands = p_entry.add_subparsers(dest="entry_command")
    entry_commands.required = True

    p_entry_book = entry_commands.add_parser(
        "book",
        help="Book an entry, as the stamped call of the dispatch that did the work",
        description=(
            "Book the performer's entry for one act: what was done and the\n"
            "measurement before and after with its witness, on the order the\n"
            "dispatch is bound to, under the open MX session. Only the call\n"
            "stamped with the dispatch it names may book (RP-12 rulings 8, 167,\n"
            "169, 173, 175)."
        ),
        epilog=build_epilog(_BOOK_EXAMPLES, exit_codes=_BOOK_EXIT_CODES),
    )
    p_entry_book.add_argument(
        "--dispatch",
        required=True,
        metavar="D-ID",
        help="The live dispatch that did the work, the one this call is stamped with",
    )
    p_entry_book.add_argument("--slug", required=True, help="Lowercase words joined by hyphens")
    p_entry_book.add_argument("--description", required=True, help="What was done")
    p_entry_book.add_argument("--before", required=True, help="The measurement before")
    p_entry_book.add_argument("--after", required=True, help="The measurement after")
    p_entry_book.add_argument(
        "--witness", required=True, help="The command or receipt that measured them"
    )
    add_json_flag(p_entry_book)
    p_entry_book.set_defaults(
        func=lambda a: _lazy("wp_entry_book_cmd")(
            request={
                "slug": a.slug,
                "dispatch": a.dispatch,
                "description": a.description,
                "before": a.before,
                "after": a.after,
                "witness": a.witness,
            },
            stamped_dispatch_id=getattr(a, "stamped_dispatch_id", None),
            as_json=a.as_json,
        )
    )
