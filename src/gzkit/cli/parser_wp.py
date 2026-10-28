"""``gz wp`` subparser registrations (drydock RO-5 tranche 2).

The verbs the operator named on 2026-10-28, selection "gz wp <verb> (Recommended)".
Handlers resolve through ``_lazy`` so ``gz --help`` imports none of them. Each leaf
is written out literally, ``p_x = wp_commands.add_parser(...)`` then
``p_x.set_defaults(func=lambda a: _lazy(...)(...))``, because the doc-coverage
scanner discovers commands from that shape.
"""

from typing import TYPE_CHECKING

from gzkit.cli.helpers import add_json_flag, build_epilog
from gzkit.cli.parser_handler_manifest import _lazy

if TYPE_CHECKING:
    import argparse

_RUNGS = ("pen_and_ink", "change_order", "attachment", "supplement", "alteration", "departure")


def register_wp_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp`` and its subcommands."""
    p_wp = commands.add_parser(
        "wp",
        help="Work packages: the record, its lifecycle and its change ladder",
        description=(
            "Commands over the work packages in data/catalog/work_packages.json\n"
            "and their ledger events. Lifecycle, one step at a time: initiated,\n"
            "frozen, commenced, accepted, closed."
        ),
        epilog=build_epilog(["gz wp show WP-01-astral"]),
    )
    wp_commands = p_wp.add_subparsers(dest="wp_command")
    wp_commands.required = True
    _register_wp_record(wp_commands)
    _register_wp_lifecycle(wp_commands)
    _register_wp_close_change(wp_commands)


def _register_wp_record(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp new``, ``attach``, ``resolve`` and ``show``."""
    p_new = wp_commands.add_parser(
        "new",
        help="Write a new work-package record with the next id",
        description="Write a new work-package record with the next id in the one series.",
        epilog=build_epilog(["gz wp new --kind repair --slug astral --issue 1183 --lane lite"]),
    )
    p_new.add_argument("--kind", required=True, choices=("delivery", "repair"))
    p_new.add_argument("--slug", required=True, help="Lowercase words joined by hyphens")
    p_new.add_argument("--outcome", default=None, help="The outcome code (delivery only)")
    p_new.add_argument("--issue", dest="issues", type=int, action="append", default=[])
    p_new.add_argument("--lane", choices=("lite", "heavy"), default=None, help="Repair only")
    p_new.add_argument("--alias", dest="aliases", action="append", default=[], help="RO-<n>")
    p_new.add_argument("--initial-conditions", default="NA", help="Section text, or NA")
    p_new.add_argument("--procedure", default="NA", help="Section text, or NA")
    p_new.add_argument("--test-and-inspection", default="NA", help="Section text, or NA")
    p_new.add_argument("--system-restoration", default="NA", help="Section text, or NA")
    p_new.add_argument(
        "--alteration",
        dest="alterations",
        action="append",
        default=[],
        help="ID:reconnected|replaced|retired:description (repeatable)",
    )
    add_json_flag(p_new)
    p_new.set_defaults(
        func=lambda a: _lazy("wp_new_cmd")(
            record={
                "kind": a.kind,
                "slug": a.slug,
                "outcome": a.outcome,
                "issues": a.issues,
                "lane": a.lane,
                "aliases": a.aliases,
                "initial_conditions": a.initial_conditions,
                "procedure": a.procedure,
                "test_and_inspection": a.test_and_inspection,
                "system_restoration": a.system_restoration,
            },
            alterations=a.alterations,
            as_json=a.as_json,
        )
    )

    p_attach = wp_commands.add_parser(
        "attach",
        help="Attach GitHub issues to a repair package",
        description="Attach GitHub issues to a repair package.",
        epilog=build_epilog(["gz wp attach WP-01-astral --issue 1184"]),
    )
    p_attach.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_attach.add_argument(
        "--issue", dest="issues", type=int, action="append", required=True, help="Repeatable"
    )
    add_json_flag(p_attach)
    p_attach.set_defaults(
        func=lambda a: _lazy("wp_attach_cmd")(
            work_package=a.work_package, issues=a.issues, as_json=a.as_json
        )
    )

    p_resolve = wp_commands.add_parser(
        "resolve",
        help="Record an issue's close against its repair package",
        description=(
            "Record a GitHub issue's close against its repair package (ruling 10).\n"
            "The package itself closes only through Gate 5 (gz wp close)."
        ),
        epilog=build_epilog(
            ["gz wp resolve WP-01-astral 1183 --commit abc1234 --reviewer spec-reviewer"]
        ),
    )
    p_resolve.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_resolve.add_argument("issue", type=int, help="The GitHub issue number")
    p_resolve.add_argument("--commit", required=True, help="The fix's commit SHA")
    p_resolve.add_argument("--reviewer", required=True, help="Who confirmed the fix")
    add_json_flag(p_resolve)
    p_resolve.set_defaults(
        func=lambda a: _lazy("wp_resolve_cmd")(
            work_package=a.work_package,
            issue=a.issue,
            commit=a.commit,
            reviewer=a.reviewer,
            as_json=a.as_json,
        )
    )

    p_show = wp_commands.add_parser(
        "show",
        help="Show a work package's record, state and ledger history",
        description="Show a work package's record, its lifecycle state and its ledger history.",
        epilog=build_epilog(["gz wp show WP-01-astral --json"]),
    )
    p_show.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    add_json_flag(p_show)
    p_show.set_defaults(
        func=lambda a: _lazy("wp_show_cmd")(work_package=a.work_package, as_json=a.as_json)
    )


def _register_wp_lifecycle(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp initiate``, ``freeze``, ``commence`` and ``accept``."""
    p_initiate = wp_commands.add_parser(
        "initiate",
        help="Initiate a work package on the operator's words",
        description="Initiate a work package on the operator's words.",
        epilog=build_epilog(['gz wp initiate WP-01-astral --operator-text "start it"']),
    )
    p_initiate.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_initiate.add_argument("--operator-text", required=True, help="The operator's words")
    p_initiate.add_argument("--evidence", default="operator initiation", help="Justification")
    add_json_flag(p_initiate)
    p_initiate.set_defaults(
        func=lambda a: _lazy("wp_transition_cmd")(
            fields={
                "work_package": a.work_package,
                "to_state": "initiated",
                "evidence": a.evidence,
                "operator_text": a.operator_text,
            },
            as_json=a.as_json,
        )
    )

    p_freeze = wp_commands.add_parser(
        "freeze",
        help="Freeze the baseline after the nine-criteria review",
        description="Freeze the baseline after the reviewer's nine-criteria check.",
        epilog=build_epilog(["gz wp freeze WP-01-x --risk-note R --review-receipt V --evidence E"]),
    )
    p_freeze.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_freeze.add_argument("--baseline", action="append", default=[], help="REQ-<n>@<rev>")
    p_freeze.add_argument("--risk-note", required=True, help="The short risk note")
    p_freeze.add_argument("--review-receipt", required=True, help="The reviewer's receipt")
    p_freeze.add_argument(
        "--approve-alteration", dest="approved", action="append", default=[], help="Alteration"
    )
    p_freeze.add_argument("--evidence", required=True, help="What justifies the freeze")
    add_json_flag(p_freeze)
    p_freeze.set_defaults(
        func=lambda a: _lazy("wp_transition_cmd")(
            fields={
                "work_package": a.work_package,
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

    p_commence = wp_commands.add_parser(
        "commence",
        help="Record that work has commenced on a frozen package",
        description="Record that work has commenced on a frozen work package.",
        epilog=build_epilog(["gz wp commence WP-01-astral --evidence tags-hung"]),
    )
    p_commence.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_commence.add_argument("--evidence", required=True, help="What justifies the move")
    add_json_flag(p_commence)
    p_commence.set_defaults(
        func=lambda a: _lazy("wp_transition_cmd")(
            fields={
                "work_package": a.work_package,
                "to_state": "commenced",
                "evidence": a.evidence,
            },
            as_json=a.as_json,
        )
    )

    p_accept = wp_commands.add_parser(
        "accept",
        help="Record final inspection of a commenced package",
        description="Record final inspection of a commenced work package.",
        epilog=build_epilog(["gz wp accept WP-01-astral --evidence final-inspection"]),
    )
    p_accept.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_accept.add_argument("--evidence", required=True, help="What justifies the move")
    add_json_flag(p_accept)
    p_accept.set_defaults(
        func=lambda a: _lazy("wp_transition_cmd")(
            fields={"work_package": a.work_package, "to_state": "accepted", "evidence": a.evidence},
            as_json=a.as_json,
        )
    )


def _register_wp_close_change(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp close`` and ``change``."""
    p_close = wp_commands.add_parser(
        "close",
        help="Close an accepted package through Gate 5",
        description="Close an accepted work package through Gate 5.",
        epilog=build_epilog(
            [
                "gz wp close WP-01-x --decision proceed --attestor g0 \\",
                "    --residual-risk R --evidence E",
            ]
        ),
    )
    p_close.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_close.add_argument(
        "--decision", required=True, choices=("proceed", "redirect", "pause", "terminate")
    )
    # Human-act verb (GHI #1036): Gate 5 is the operator's own act, so never defaulted.
    p_close.add_argument("--attestor", required=True, help="Gate 5 attestor, never defaulted")
    p_close.add_argument("--residual-risk", required=True, help="The residual risk")
    p_close.add_argument(
        "--account", dest="accounted", action="append", default=[], help="Alteration accounted"
    )
    p_close.add_argument(
        "--open-departure", dest="open_departures", action="append", default=[], help="DFS id"
    )
    p_close.add_argument("--evidence", required=True, help="What justifies the close")
    add_json_flag(p_close)
    p_close.set_defaults(
        func=lambda a: _lazy("wp_transition_cmd")(
            fields={
                "work_package": a.work_package,
                "to_state": "closed",
                "evidence": a.evidence,
                "attestor": a.attestor,
                "decision": a.decision,
                "residual_risk": a.residual_risk,
                "configuration_changes": a.accounted,
                "open_departures": a.open_departures,
            },
            as_json=a.as_json,
        )
    )

    p_change = wp_commands.add_parser(
        "change",
        help="Record one change on the ladder, or an alteration or departure",
        description="Record one change on the change ladder, or an alteration or departure.",
        epilog=build_epilog(
            ["gz wp change WP-01-x --rung pen_and_ink --approver coordinator --change C"]
        ),
    )
    p_change.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_change.add_argument(
        "--rung", required=True, choices=_RUNGS, metavar="RUNG", help=", ".join(_RUNGS)
    )
    p_change.add_argument("--approver", required=True, choices=("operator", "coordinator"))
    p_change.add_argument("--change", required=True, help="The change made")
    p_change.add_argument("--superseded", default=None, help="The superseded content, kept")
    p_change.add_argument("--work-stopped", action="store_true", help="Change order: work stops")
    p_change.add_argument("--supplement", default=None, help="The supplement's package id")
    p_change.add_argument("--item", default=None, help="Alteration or departure id")
    p_change.add_argument(
        "--configuration-change",
        choices=("reconnected", "replaced", "retired"),
        default=None,
        help="A new alteration's configuration change",
    )
    p_change.add_argument("--form", choices=("deviation", "waiver"), default=None)
    p_change.add_argument("--duration", choices=("temporary", "permanent"), default=None)
    p_change.add_argument("--clear-by", default=None, help="A temporary departure's condition")
    p_change.add_argument("--req", default=None, help="The REQ a departure departs on")
    add_json_flag(p_change)
    p_change.set_defaults(
        func=lambda a: _lazy("wp_change_cmd")(
            fields={
                "work_package": a.work_package,
                "rung": a.rung,
                "approver": a.approver,
                "change": a.change,
                "superseded": a.superseded,
                "work_stopped": a.work_stopped,
                "supplement": a.supplement,
                "item": a.item,
            },
            item_fields={
                "configuration_change": a.configuration_change,
                "form": a.form,
                "duration": a.duration,
                "clear_by": a.clear_by,
                "req": a.req,
            },
            as_json=a.as_json,
        )
    )
