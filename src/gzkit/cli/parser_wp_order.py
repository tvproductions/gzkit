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
    """Register ``gz wp order`` and its leaves, ``new`` through ``close`` and ``show``."""
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

    p_order_freeze = order_commands.add_parser(
        "freeze",
        help="Freeze an opened order's REQ baseline and seal its package's footprint",
        description=(
            "Freeze an opened order: its REQ baseline of the package's own repair REQs,\n"
            "the risk note, the reviewer's receipt and every planned alteration no\n"
            "earlier order's freeze approved. The freeze seals the repair package's\n"
            "footprint (RP-12 rulings 53, 56 and 63)."
        ),
        epilog=build_epilog(
            [
                (
                    "gz wp order freeze ORD-01-import --baseline REQ-1@1 --risk-note R"
                    " --review-receipt V --evidence E"
                ),
            ]
        ),
    )
    p_order_freeze.add_argument("order", help="The order's id, ORD-<NN>-<slug>")
    p_order_freeze.add_argument(
        "--baseline", action="append", default=[], help="REQ-<n>@<rev> (repeatable)"
    )
    p_order_freeze.add_argument("--risk-note", required=True, help="The short risk note")
    p_order_freeze.add_argument("--review-receipt", required=True, help="The reviewer's receipt")
    p_order_freeze.add_argument(
        "--approve-alteration",
        dest="approved",
        action="append",
        default=[],
        help="An alteration this freeze approves (repeatable)",
    )
    p_order_freeze.add_argument("--evidence", required=True, help="What justifies the freeze")
    add_json_flag(p_order_freeze)
    p_order_freeze.set_defaults(
        func=lambda a: _lazy("wp_order_transition_cmd")(
            fields={
                "order": a.order,
                "to_state": "frozen",
                "evidence": a.evidence,
                "risk_note": a.risk_note,
                "review_receipt": a.review_receipt,
                "approved_alterations": a.approved,
            },
            baseline=a.baseline,
            as_json=a.as_json,
        )
    )

    p_order_commence = order_commands.add_parser(
        "commence",
        help="Record that work has commenced on a frozen order",
        description="Record that work has commenced on a frozen order (RP-12 O2 task 3).",
        epilog=build_epilog(["gz wp order commence ORD-01-import --evidence tags-hung"]),
    )
    p_order_commence.add_argument("order", help="The order's id, ORD-<NN>-<slug>")
    p_order_commence.add_argument("--evidence", required=True, help="What justifies the move")
    add_json_flag(p_order_commence)
    p_order_commence.set_defaults(
        func=lambda a: _lazy("wp_order_transition_cmd")(
            fields={"order": a.order, "to_state": "commenced", "evidence": a.evidence},
            baseline=None,
            as_json=a.as_json,
        )
    )

    p_order_accept = order_commands.add_parser(
        "accept",
        help="Accept a commenced order once its acceptance reads ready",
        description=(
            "Accept a commenced order. Refused until `gz wp acceptance <ORD-id>` reads\n"
            "the order ready and every changed file lies in its package's sealed\n"
            "footprint; an order stopped by an exit is excused (RP-12 ruling 60)."
        ),
        epilog=build_epilog(["gz wp order accept ORD-01-import --evidence final-inspection"]),
    )
    p_order_accept.add_argument("order", help="The order's id, ORD-<NN>-<slug>")
    p_order_accept.add_argument("--evidence", required=True, help="The final inspection")
    add_json_flag(p_order_accept)
    p_order_accept.set_defaults(
        func=lambda a: _lazy("wp_order_accept_cmd")(
            order_id=a.order, evidence=a.evidence, as_json=a.as_json
        )
    )

    p_order_close = order_commands.add_parser(
        "close",
        help="Close an order through Gate 5 with the operator's words",
        description=(
            "Close an order through Gate 5 at the order: the decision, the attestor\n"
            "and the operator's verbatim words, from accepted, or from opened as a\n"
            "terminate. Proceed carries --residual-risk, redirect --superseded-by, an\n"
            "opened order of the same package, and pause --revisit-condition. A\n"
            "subagent's call is refused (RP-12 rulings 30 and 73 to 77)."
        ),
        epilog=build_epilog(
            [
                (
                    "gz wp order close ORD-01-import --decision proceed --attestor g0"
                    " --attestation-text 'the import holds' --residual-risk none"
                    " --evidence gate-5"
                ),
                (
                    "gz wp order close ORD-02-matcher --decision redirect --attestor g0"
                    " --attestation-text 'rework it' --superseded-by ORD-03-matcher"
                    " --evidence gate-5"
                ),
            ]
        ),
    )
    p_order_close.add_argument("order", help="The order's id, ORD-<NN>-<slug>")
    p_order_close.add_argument(
        "--decision",
        required=True,
        choices=("proceed", "redirect", "pause", "terminate"),
        help="The Gate 5 decision",
    )
    p_order_close.add_argument("--attestor", required=True, help="Who attests, g0")
    p_order_close.add_argument(
        "--attestation-text", required=True, help="The operator's verbatim words"
    )
    p_order_close.add_argument("--evidence", required=True, help="What justifies the close")
    p_order_close.add_argument("--residual-risk", help="The residual risk, for proceed")
    p_order_close.add_argument("--superseded-by", help="The opened ORD-id, for redirect")
    p_order_close.add_argument("--revisit-condition", help="When to revisit, for pause")
    add_json_flag(p_order_close)
    p_order_close.set_defaults(
        func=lambda a: _lazy("wp_order_close_cmd")(
            fields={
                key: value
                for key, value in {
                    "order": a.order,
                    "evidence": a.evidence,
                    "decision": a.decision,
                    "attestor": a.attestor,
                    "attestation_text": a.attestation_text,
                    "residual_risk": a.residual_risk,
                    "superseded_by": a.superseded_by,
                    "revisit_condition": a.revisit_condition,
                }.items()
                if value is not None
            },
            called_by_subagent=bool(getattr(a, "called_by_subagent", False)),
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
