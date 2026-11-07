"""``gz wp order`` subparser registrations (RP-12 O2 task 1).

The nested group the operator ruled on 2026-11-05 (RP-12 ruling 47, *"a"*). Each
leaf is written out literally, ``p_x = order_commands.add_parser(...)`` then
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


def _register_wp_order(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp order`` and its ``new`` and ``show`` subcommands."""
    p_order = wp_commands.add_parser(
        "order",
        help="Orders: the unit Gate 5 sits at, inside a work package",
        description=(
            "Commands over the orders in data/catalog/orders.json. An order is\n"
            "ORD-<NN>-<slug>, its kind read from its package (RP-12 ruling 43)."
        ),
        epilog=build_epilog(
            [
                (
                    "gz wp order new WP-01-stamp --slug import --purpose 'Restore it.'"
                    " --operator-text 'open it'"
                ),
                "gz wp order show ORD-01-import",
            ]
        ),
    )
    order_commands = p_order.add_subparsers(dest="order_command")
    order_commands.required = True

    p_order_new = order_commands.add_parser(
        "new",
        help="Write a new order's record with the next id",
        description=(
            "Write a new order's record with the next ORD-<NN>-<slug> in the one\n"
            "series and book its opening on the operator's words (RP-12 ruling 52).\n"
            "It sits in a repair package until RP-14 (RP-12 ruling 44)."
        ),
        epilog=build_epilog(
            [
                (
                    "gz wp order new WP-01-stamp --slug import --purpose 'Restore it.'"
                    " --operator-text 'open it'"
                ),
                (
                    "gz wp order new WP-01-stamp --slug matcher --purpose 'Fix it.'"
                    " --operator-text 'go' --alias O2"
                ),
            ]
        ),
    )
    p_order_new.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_order_new.add_argument("--slug", required=True, help="Lowercase words joined by hyphens")
    p_order_new.add_argument("--purpose", required=True, help="What the order restores")
    p_order_new.add_argument("--procedure", default="NA", help="Its procedure, or NA")
    p_order_new.add_argument("--operator-text", required=True, help="The operator's words")
    p_order_new.add_argument("--evidence", default="operator opening", help="Justification")
    p_order_new.add_argument(
        "--alias", dest="aliases", action="append", default=[], help="O<n> (repeatable)"
    )
    add_json_flag(p_order_new)
    p_order_new.set_defaults(
        func=lambda a: _lazy("wp_order_new_cmd")(
            work_package=a.work_package,
            record={
                "slug": a.slug,
                "purpose": a.purpose,
                "procedure": a.procedure,
                "aliases": a.aliases,
            },
            opening={"operator_text": a.operator_text, "evidence": a.evidence},
            as_json=a.as_json,
        )
    )

    p_order_show = order_commands.add_parser(
        "show",
        help="Show an order's record and its package's kind",
        description="Show an order's record and the kind of the package it sits in.",
        epilog=build_epilog(["gz wp order show ORD-01-import --json"]),
    )
    p_order_show.add_argument("order", help="The order's id, ORD-<NN>-<slug>")
    add_json_flag(p_order_show)
    p_order_show.set_defaults(
        func=lambda a: _lazy("wp_order_show_cmd")(order_id=a.order, as_json=a.as_json)
    )
