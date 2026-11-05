"""``gz wp`` subparser registrations (drydock RO-5 tranche 2).

The verbs the operator named on 2026-10-28, selection "gz wp <verb> (Recommended)".
Handlers resolve through ``_lazy`` so ``gz --help`` imports none of them. Each leaf
is written out literally, ``p_x = wp_commands.add_parser(...)`` then
``p_x.set_defaults(func=lambda a: _lazy(...)(...))``, because the doc-coverage
scanner discovers commands from that shape.
"""

from typing import TYPE_CHECKING

from gzkit.cli.helpers import add_dry_run_flag, add_json_flag, build_epilog
from gzkit.cli.parser_acceptance import acceptance_handler, configure_acceptance_parser
from gzkit.cli.parser_handler_manifest import _lazy

if TYPE_CHECKING:
    import argparse

_WITHDRAW_EXAMPLE = (
    "gz wp withdraw-legacy OBPI-0.35.0-11-corpus-shape-witness "
    '--reason "carried to REQ-7" --attestor g0'
)
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
    _register_wp_run(wp_commands)
    _register_wp_acceptance(wp_commands)
    _register_wp_withdraw_legacy(wp_commands)


def _register_wp_withdraw_legacy(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp withdraw-legacy``, the successor to ``gz obpi withdraw``."""
    p_withdraw = wp_commands.add_parser(
        "withdraw-legacy",
        help="Withdraw a legacy unit, permanently, on a human witness",
        description=(
            "Withdraw a legacy OBPI: one-way, and read as withdrawn everywhere. The\n"
            "successor to gz obpi withdraw, accepting legacy ids (RO-14 act 7)."
        ),
        epilog=build_epilog([_WITHDRAW_EXAMPLE]),
    )
    p_withdraw.add_argument("unit", help="The legacy unit's id, OBPI-<X.Y.Z-NN-slug>")
    p_withdraw.add_argument("--reason", required=True, help="Why, and where its REQs went")
    # Human-act verb (GHI #1036): only a human witnesses a withdrawal, so never defaulted.
    p_withdraw.add_argument("--attestor", required=True, help="The human witness, never defaulted")
    add_dry_run_flag(p_withdraw, help_override="Show the event without booking it")
    add_json_flag(p_withdraw)
    p_withdraw.set_defaults(
        func=lambda a: _lazy("wp_withdraw_legacy_cmd")(
            unit=a.unit,
            reason=a.reason,
            attestor=a.attestor,
            dry_run=a.dry_run,
            as_json=a.as_json,
        )
    )


def _dispatch_or_void(parser: argparse.ArgumentParser, a: argparse.Namespace) -> object:
    """Route ``gz wp dispatch`` to its booking or, with ``--void``, to its void.

    Booking needs ``--role`` and ``--model`` and takes no ``--void``; a void
    takes none of booking's flags. A wrong combination is a usage error, exit 2.

    Returns:
        What the handler returns.

    """
    if a.void is not None:
        booking = ("--role", "--model", "--req", "--issue", "--root")
        given = [flag for flag in booking if getattr(a, flag[2:]) is not None]
        if given:
            parser.error(f"--void abandons a dispatch; it takes no {', '.join(given)}")
        return _lazy("wp_dispatch_void_cmd")(
            work_package=a.work_package,
            dispatch_id=a.void,
            reason=a.reason,
            called_by_subagent=bool(getattr(a, "called_by_subagent", False)),
            as_json=a.as_json,
        )
    missing = [flag for flag, value in (("--role", a.role), ("--model", a.model)) if value is None]
    if missing:
        parser.error(f"the following arguments are required: {', '.join(missing)}")
    return _lazy("wp_dispatch_cmd")(
        fields={
            "work_package": a.work_package,
            "role": a.role,
            "model": a.model,
            "req": a.req,
            "issue": a.issue,
            "reason": a.reason,
            "root": a.root,
        },
        as_json=a.as_json,
    )


def _register_wp_run(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp dispatch``, ``block`` and ``unblock`` (RO-14 tranche 1)."""
    p_dispatch = wp_commands.add_parser(
        "dispatch",
        help="Record a dispatch on a commenced package, holding the fix-cycle bound",
        description=(
            "Record one dispatch on a commenced work package. The cycle past the\n"
            "fix-cycle bound is refused whatever was ruled (GHI #1200). The dispatch\n"
            "is bound to a minted id and its intended root; put the printed line in\n"
            "the dispatched agent's prompt (RP-12 rulings 1 and 35). --void abandons\n"
            "a booked dispatch, refused from a subagent's call (ruling 42)."
        ),
        epilog=build_epilog(
            [
                "gz wp dispatch WP-01-x --role Implementer --model sonnet --req REQ-1",
                "gz wp dispatch WP-01-x --role Implementer --model m --issue 1 --root ../tmp",
                "gz wp dispatch WP-01-x --void D-0123456789abcdef --reason 'never spawned'",
            ]
        ),
    )
    p_dispatch.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_dispatch.add_argument(
        "--role",
        default=None,
        help="Implementer, SpecReviewer, QualityReviewer or SingleDriver; required to book",
    )
    p_dispatch.add_argument("--model", default=None, help="The model tier; required to book")
    p_dispatch.add_argument("--req", default=None, help="The frozen REQ dispatched against")
    p_dispatch.add_argument(
        "--issue", type=int, default=None, help="The carried issue dispatched against"
    )
    p_dispatch.add_argument(
        "--reason", default=None, help="Why the run is single-driver, or why a dispatch is voided"
    )
    p_dispatch.add_argument(
        "--void", default=None, metavar="D-ID", help="Abandon this booked dispatch instead"
    )
    p_dispatch.add_argument(
        "--root",
        default=None,
        help="The project root the dispatch is for; defaults to this project's",
    )
    add_json_flag(p_dispatch)
    p_dispatch.set_defaults(func=lambda a: _dispatch_or_void(p_dispatch, a))

    p_block = wp_commands.add_parser(
        "block",
        help="Record that a package awaits the operator",
        description=(
            "Record that a work package awaits the operator. The runtime writes the\n"
            "fix-cycle count and the exits used, so the facts are not the agent's."
        ),
        epilog=build_epilog(['gz wp block WP-01-x --reason R --next-action "rule on REQ-1"']),
    )
    p_block.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_block.add_argument("--reason", required=True, help="Why the package cannot proceed")
    p_block.add_argument("--next-action", required=True, help="The decision the operator owes")
    add_json_flag(p_block)
    p_block.set_defaults(
        func=lambda a: _lazy("wp_block_cmd")(
            work_package=a.work_package,
            reason=a.reason,
            next_action=a.next_action,
            as_json=a.as_json,
        )
    )

    p_unblock = wp_commands.add_parser(
        "unblock",
        help="Record the operator's ruling on a blocked package",
        description=(
            "Record the operator's ruling and clear the block. At the fix-cycle bound\n"
            "the ruling names one exit; no exit opens a further repair cycle."
        ),
        epilog=build_epilog(['gz wp unblock WP-01-x --ruling "hold" --operator g0 --exit hold']),
    )
    p_unblock.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_unblock.add_argument("--ruling", required=True, help="The operator's decision, verbatim")
    # Human-act verb (GHI #1036): the ruling is the operator's own, so never defaulted.
    p_unblock.add_argument("--operator", required=True, help="Who ruled, never defaulted")
    p_unblock.add_argument(
        "--exit",
        dest="exit_taken",
        default=None,
        help="reopen, departure, hold or terminate; required at the bound",
    )
    p_unblock.add_argument("--req", default=None, help="The REQ a reopen or departure names")
    add_json_flag(p_unblock)
    p_unblock.set_defaults(
        func=lambda a: _lazy("wp_unblock_cmd")(
            fields={
                "work_package": a.work_package,
                "ruling": a.ruling,
                "operator": a.operator,
                "exit_taken": a.exit_taken,
                "req": a.req,
            },
            as_json=a.as_json,
        )
    )


def _register_wp_record(wp_commands: argparse._SubParsersAction) -> None:
    """Register ``gz wp new``, ``attach``, ``resolve``, ``evidence`` and ``show``."""
    p_new = wp_commands.add_parser(
        "new",
        help="Write a new work-package record with the next id",
        description="Write a new work-package record with the next id in the one series.",
        epilog=build_epilog(["gz wp new --kind repair --slug astral --issue 1183 --lane lite"]),
    )
    p_new.add_argument(
        "--kind", required=True, choices=("delivery", "repair"), help="delivery or repair"
    )
    p_new.add_argument("--slug", required=True, help="Lowercase words joined by hyphens")
    p_new.add_argument("--outcome", default=None, help="The outcome code (delivery only)")
    p_new.add_argument(
        "--issue", dest="issues", type=int, action="append", default=[], help="Repeatable"
    )
    p_new.add_argument("--lane", choices=("lite", "heavy"), default=None, help="Repair only")
    p_new.add_argument("--alias", dest="aliases", action="append", default=[], help="RO-<n>")
    p_new.add_argument(
        "--module",
        dest="modules",
        action="append",
        default=[],
        help="A path in a repair package's footprint (repeatable)",
    )
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
                "modules": a.modules,
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

    p_evidence = wp_commands.add_parser(
        "evidence",
        help="Append objective quality evidence to a live work package",
        description=(
            "Append objective quality evidence (receipts, commits, paths) to a live\n"
            "work package's record. Entries are never edited, removed or repeated."
        ),
        epilog=build_epilog(['gz wp evidence WP-01-astral --oqe "commit abc1234"']),
    )
    p_evidence.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_evidence.add_argument(
        "--oqe", dest="items", action="append", required=True, help="One entry; repeatable"
    )
    add_json_flag(p_evidence)
    p_evidence.set_defaults(
        func=lambda a: _lazy("wp_evidence_cmd")(
            work_package=a.work_package, items=a.items, as_json=a.as_json
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

    p_runs = wp_commands.add_parser(
        "runs",
        help="Report what the ledger says every run in flight has reached",
        description=(
            "Report every work package commenced and not yet closed, with the last\n"
            "row its run booked. Replayed from the ledger; no marker is read."
        ),
        epilog=build_epilog(["gz wp runs --json"]),
    )
    add_json_flag(p_runs)
    p_runs.set_defaults(func=lambda a: _lazy("wp_runs_cmd")(as_json=a.as_json))


def _register_wp_acceptance(wp_commands: argparse._SubParsersAction) -> None:
    p_acceptance = wp_commands.add_parser(
        "acceptance",
        help="Execute proof, record independent reviews and derive readiness",
        description=(
            "Run the acceptance runtime on a commenced work package: the frozen REQs,\n"
            "or one obligation per carried issue. `gz wp accept` refuses until it reads\n"
            "ready, and three adversarial rounds with a mapped finding stop for the operator."
        ),
        epilog=build_epilog(
            [
                "gz wp acceptance WP-01-x init --author implementing-session",
                "gz wp acceptance WP-01-x prove --spec controls.json",
                "gz wp acceptance WP-01-x status --json",
            ]
        ),
    )
    configure_acceptance_parser(p_acceptance)
    p_acceptance.set_defaults(func=acceptance_handler)


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
                (
                    "gz wp close WP-01-x --decision proceed --attestor g0 "
                    "--residual-risk R --evidence E"
                ),
            ]
        ),
    )
    p_close.add_argument("work_package", help="The work package's id, WP-<NN>-<slug>")
    p_close.add_argument(
        "--decision",
        required=True,
        choices=("proceed", "redirect", "pause", "terminate"),
        help="The Gate 5 decision",
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
    p_change.add_argument(
        "--approver", required=True, choices=("operator", "coordinator"), help="Who approves"
    )
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
    p_change.add_argument(
        "--form", choices=("deviation", "waiver"), default=None, help="A departure's form"
    )
    p_change.add_argument(
        "--duration",
        choices=("temporary", "permanent"),
        default=None,
        help="A departure's duration",
    )
    p_change.add_argument("--clear-by", default=None, help="A temporary departure's condition")
    p_change.add_argument("--req", default=None, help="The REQ a departure departs on")
    p_change.add_argument(
        "--module",
        dest="modules",
        action="append",
        default=[],
        help="A path a change order adds to the footprint (repeatable)",
    )
    p_change.add_argument(
        "--drop-module",
        dest="dropped",
        action="append",
        default=[],
        help="A path a change order drops before the freeze (repeatable)",
    )
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
            modules=a.modules,
            dropped=a.dropped,
            as_json=a.as_json,
        )
    )
