"""Subparser registrations for the ``gz obpi`` sub-command group.

Registers: obpi status, lock, complete, park, pipeline, and the rest of the
OBPI lifecycle surface.

Extracted from ``parser_artifacts.py``, which breached its shrink-only
module-size ceiling. This family is what grew: every commit in the overage
window added Step-4b flags to this group (GHI #678, #765, #774/#775).

The module name is load-bearing. ``gzkit.doc_coverage.scanner`` discovers CLI
verbs by globbing ``parser_*.py`` under ``src/gzkit/cli/`` and reading the
literal string argument of each ``add_parser`` call via AST, so a module
outside that glob is invisible to manpage coverage.

Command handlers are resolved on demand via ``_lazy`` so ``gz --help`` avoids
pulling heavy handler dependencies.
"""

from __future__ import annotations

import argparse

from gzkit.cli.helpers import (
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    build_epilog,
)
from gzkit.cli.parser_handler_manifest import _lazy
from gzkit.lock_manager import DEFAULT_LOCK_TTL_MINUTES


def register_obpi_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz obpi`` sub-command group."""
    p_obpi = commands.add_parser(
        "obpi",
        help="OBPI-focused governance commands",
        description="OBPI lifecycle, pipeline, and evidence commands.",
        epilog=build_epilog(
            [
                "gz obpi status OBPI-0.1.0-01",
                "gz obpi pipeline OBPI-0.1.0-01",
                "gz obpi sync OBPI-0.1.0-01",
                "gz obpi brief-drift OBPI-0.1.0-01",
            ]
        ),
    )
    obpi_commands = p_obpi.add_subparsers(dest="obpi_command")
    obpi_commands.required = True

    p_obpi_emit = obpi_commands.add_parser(
        "emit-receipt",
        help="Emit completed/validated receipt event for an OBPI",
        description=(
            "Record a receipt event in the ledger for an OBPI. "
            "Required --evidence-json fields for completed: "
            "value_narrative, key_proof. "
            "Heavy/Foundation also require: "
            "human_attestation (true), attestation_text, "
            "attestation_date (YYYY-MM-DD)."
        ),
        epilog=build_epilog(
            [
                'gz obpi emit-receipt OBPI-0.1.0-01 --event completed --attestor "Jane Doe"',
                'gz obpi emit-receipt OBPI-0.1.0-01 --event validated --attestor "Jane Doe"',
            ]
        ),
    )
    p_obpi_emit.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.4-01)")
    p_obpi_emit.add_argument(
        "--event",
        dest="receipt_event",
        required=True,
        choices=["completed", "validated"],
        help="Receipt event type (completed|validated)",
    )
    p_obpi_emit.add_argument("--attestor", required=True, help="Identity of the attestor")
    p_obpi_emit.add_argument(
        "--evidence-json",
        help="JSON with value_narrative, key_proof; Heavy adds attestation fields",
    )
    p_obpi_emit.add_argument(
        "--attestor-present",
        dest="attestor_present",
        action="store_true",
        help="Agent-relayed operator attestation, gated on active pipeline marker (GHI #292)",
    )
    add_dry_run_flag(p_obpi_emit)
    p_obpi_emit.set_defaults(
        func=lambda a: _lazy("obpi_emit_receipt_cmd")(
            obpi=a.obpi,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
            attestor_present=a.attestor_present,
            dry_run=a.dry_run,
        )
    )

    p_obpi_status = obpi_commands.add_parser(
        "status",
        help="Show focused runtime status for one OBPI",
        description="Display runtime status and evidence for a single OBPI.",
        epilog=build_epilog(
            [
                "gz obpi status OBPI-0.1.0-01",
                "gz obpi status OBPI-0.1.0-01 --json",
            ]
        ),
    )
    p_obpi_status.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.4-01)")
    add_json_flag(p_obpi_status)
    p_obpi_status.set_defaults(
        func=lambda a: _lazy("obpi_status_cmd")(obpi=a.obpi, as_json=a.as_json)
    )

    p_obpi_pipeline = obpi_commands.add_parser(
        "pipeline",
        help="Launch the OBPI pipeline runtime surface",
        description="Run or query the OBPI pipeline lifecycle runtime.",
        epilog=build_epilog(
            [
                "gz obpi pipeline OBPI-0.1.0-01",
                "gz obpi pipeline OBPI-0.1.0-01 --from verify",
                "gz obpi pipeline --clear-stale",
            ]
        ),
    )
    p_obpi_pipeline.add_argument(
        "obpi", nargs="?", default="", help="OBPI identifier (e.g. OBPI-0.0.4-01)"
    )
    p_obpi_pipeline.add_argument(
        "--from",
        dest="start_from",
        choices=["verify", "ceremony", "sync"],
        help="Resume pipeline from a specific stage",
    )
    p_obpi_pipeline.add_argument(
        "--attestor",
        help="Attestor identity for Stage 5 (e.g. g0 or agent:<name>)",
    )
    p_obpi_pipeline.add_argument(
        "--evidence-json",
        dest="evidence_json",
        help="Stage 5 JSON; must include attestation_text (see manpage)",
    )
    p_obpi_pipeline.add_argument(
        "--clear-stale",
        dest="clear_stale",
        action="store_true",
        help="Remove pipeline markers older than 24 hours",
    )
    p_obpi_pipeline.add_argument(
        "--no-subagents",
        dest="no_subagents",
        action="store_true",
        help="Disable subagent dispatch (single-session fallback)",
    )
    p_obpi_pipeline.set_defaults(
        func=lambda a: _lazy("obpi_pipeline_cmd")(
            obpi=a.obpi,
            start_from=a.start_from,
            clear_stale=a.clear_stale,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
        )
    )

    # Renamed from `gz obpi sync` (GHI #641). `sync` names what this verb
    # actually absorbed — gz-obpi-audit + gz-obpi-sync — and ends the collision
    # with the brief-content check now called `brief-drift`.
    p_obpi_sync = obpi_commands.add_parser(
        "sync",
        help="Fail-closed runtime reconciliation for one OBPI (receipt + ADR table)",
        description="Reconcile OBPI receipt and brief for consistency.",
        epilog=build_epilog(
            [
                "gz obpi sync OBPI-0.1.0-01",
                "gz obpi sync OBPI-0.1.0-01 --json",
            ]
        ),
    )
    p_obpi_sync.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.4-01)")
    add_json_flag(p_obpi_sync)
    p_obpi_sync.set_defaults(
        func=lambda a: _lazy("obpi_reconcile_cmd")(obpi=a.obpi, as_json=a.as_json)
    )

    # Was `gz brief reconcile` in a single-verb `brief` namespace, colliding with
    # `gz obpi reconcile` on the same artifact (GHI #641). A brief IS an OBPI's
    # brief, so the namespace was never a disambiguator an operator could draw,
    # and mis-selection was silent — each exits 0/3 on a different axis. The verb
    # now names the axis it checks: brief content against the project tree.
    # Registered inline rather than via a helper because the doc-coverage scanner
    # binds every `_register_*` parameter to an empty prefix, so a helper taking a
    # NESTED subparsers action gets discovered as a top-level command.
    p_brief_drift = obpi_commands.add_parser(
        "brief-drift",
        help="Check an OBPI brief against project state (five drift dimensions)",
        description=(
            "Run the brief reconciliation engine across allowlist, discovery "
            "checklist, verification verbs, REQ count, and citation tuples. "
            "Emits a brief_reconciled ledger event on every run (and "
            "brief_reconcile_drift_detected on drift); exits 0 when clean, 3 on "
            "drift. Use --apply --attestor to write operator-attested amendments."
        ),
        epilog=build_epilog(
            [
                "gz obpi brief-drift OBPI-0.1.0-01",
                "gz obpi brief-drift OBPI-0.1.0-01 --apply --dry-run",
                'gz obpi brief-drift OBPI-0.1.0-01 --apply --attestor "Jane Doe"',
            ]
        ),
    )
    p_brief_drift.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.1.0-01)")
    p_brief_drift.add_argument(
        "--apply",
        action="store_true",
        help="Write operator-attested amendments back into the brief (requires --attestor)",
    )
    p_brief_drift.add_argument(
        "--attestor",
        default=None,
        help="Full name of the attesting human (required with --apply)",
    )
    add_dry_run_flag(p_brief_drift)
    add_json_flag(p_brief_drift)
    p_brief_drift.set_defaults(
        func=lambda a: _lazy("brief_reconcile_cmd")(
            obpi_id=a.obpi,
            dry_run=a.dry_run,
            apply=a.apply,
            attestor=a.attestor,
            as_json=a.as_json,
        )
    )

    p_obpi_validate = obpi_commands.add_parser(
        "validate",
        help="Validate OBPI brief(s) for authored or completion readiness",
        description="Check OBPI briefs against the canonical authored/completion schema.",
        epilog=build_epilog(
            [
                "gz obpi validate docs/design/adr/my-adr/obpis/OBPI-0.1.0-01-my-feature.md",
                (
                    "gz obpi validate "
                    "docs/design/adr/my-adr/obpis/OBPI-0.1.0-01-my-feature.md --authored"
                ),
                "gz obpi validate --adr ADR-0.1.0",
                "gz obpi validate --adr ADR-0.1.0 --authored",
            ]
        ),
    )
    p_obpi_validate.add_argument(
        "obpi_path", nargs="?", default=None, help="Path to a single OBPI brief file"
    )
    p_obpi_validate.add_argument(
        "--adr",
        dest="adr_id",
        default=None,
        help="Validate all OBPI briefs under an ADR (e.g., --adr ADR-0.0.3)",
    )
    p_obpi_validate.add_argument(
        "--authored",
        action="store_true",
        help="Require authored-ready brief content before pipeline execution.",
    )
    p_obpi_validate.set_defaults(
        func=lambda a: _lazy("obpi_validate_cmd")(
            obpi_path=a.obpi_path,
            adr_id=a.adr_id,
            authored=a.authored,
        )
    )

    p_obpi_precomplete = obpi_commands.add_parser(
        "precomplete",
        help="Verify Stage 5 preconditions before invoking 'gz obpi complete'",
        description=(
            "Mechanical pre-flight checklist: brief readiness, frontmatter "
            "idempotence, lock ownership, ARB receipts, plan-audit receipt. "
            "Each check exits with a named remediation when it fails. Closes "
            "the reactive-triage class of failure (GHI #196)."
        ),
        epilog=build_epilog(
            [
                "gz obpi precomplete OBPI-0.1.0-01",
                "gz obpi precomplete OBPI-0.0.16-04 --json",
            ]
        ),
    )
    p_obpi_precomplete.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.16-04)")
    add_json_flag(p_obpi_precomplete)
    p_obpi_precomplete.set_defaults(
        func=lambda a: _lazy("obpi_precomplete_cmd")(obpi_id=a.obpi, as_json=a.as_json)
    )

    p_obpi_dispatch = obpi_commands.add_parser(
        "dispatch",
        help="Record a Stage-2 subagent dispatch, or declare a single-driver run",
        description=(
            "Record that Stage 2 dispatched a mandated persona, so "
            "'gz obpi precomplete' can attest it. Credit is never inferred - "
            "this verb is the only way the dispatch channel reports DISPATCHED. "
            "Use --single-driver --reason when the session genuinely cannot "
            "dispatch: declared single-driver is permitted, silent is refused "
            "(GHI #845)."
        ),
        epilog=build_epilog(
            [
                "gz obpi dispatch OBPI-0.1.0-01 --role Implementer --model sonnet --task 1",
                "gz obpi dispatch OBPI-0.1.0-01 --role SpecReviewer --model opus --task 2",
                'gz obpi dispatch OBPI-0.1.0-01 --single-driver --reason "cron run, no Agent tool"',
            ]
        ),
    )
    p_obpi_dispatch.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.16-04)")
    p_obpi_dispatch.add_argument("--role", help="Mandated Stage-2 role that was dispatched")
    p_obpi_dispatch.add_argument("--model", help="Model tier used for the dispatch")
    p_obpi_dispatch.add_argument("--task", type=int, default=1, help="1-based task index")
    p_obpi_dispatch.add_argument(
        "--single-driver",
        action="store_true",
        help="Declare this run knowingly single-driver (requires --reason)",
    )
    p_obpi_dispatch.add_argument("--reason", help="Why the mandated dispatch could not run")
    p_obpi_dispatch.set_defaults(
        func=lambda a: _lazy("obpi_dispatch_cmd")(
            obpi_id=a.obpi,
            role=a.role,
            model=a.model,
            task_id=a.task,
            single_driver=a.single_driver,
            reason=a.reason,
        )
    )

    p_obpi_present_evidence = obpi_commands.add_parser(
        "present-evidence",
        help="Generate tool-derived Stage-4 acceptance evidence (GHI #643)",
        description=(
            "Generate the Stage-4 evidence packet from observables the agent cannot "
            "author: run the brief's ## Demo (assert-shaped), read on-disk ARB receipts, "
            "and run gz covers. Writes .gzkit/evidence/<OBPI>.evidence.json and prints it "
            "for operator attestation. Exits 3 (NOT-ATTESTABLE) on any blocker."
        ),
        epilog=build_epilog(
            [
                "gz obpi present-evidence OBPI-0.1.0-01",
                "gz obpi present-evidence OBPI-0.0.74-16 --json",
            ]
        ),
    )
    p_obpi_present_evidence.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.74-16)")
    add_json_flag(p_obpi_present_evidence)
    p_obpi_present_evidence.set_defaults(
        func=lambda a: _lazy("obpi_present_evidence_cmd")(obpi_id=a.obpi, as_json=a.as_json)
    )

    p_obpi_verify_packet = obpi_commands.add_parser(
        "verify-packet",
        help="Re-run a Step-4a packet's pasted transcripts (GHI #942)",
        description=(
            "Re-execute every $-prompted transcript in a composed Step-4a evidence "
            "packet and report which pasted output lines the command did not produce. "
            "Fenced shell blocks with no $ prompt claim no output and are reported as "
            "citations, never re-run. Exits 3 (NOT-VERIFIED) on any blocker."
        ),
        epilog=build_epilog(
            [
                "gz obpi verify-packet .gzkit/evidence/OBPI-0.1.0-01.stage4a.md",
                "gz obpi verify-packet packet.md --json",
            ]
        ),
    )
    p_obpi_verify_packet.add_argument("packet", help="Path to the composed Step-4a packet")
    add_json_flag(p_obpi_verify_packet)
    p_obpi_verify_packet.set_defaults(
        func=lambda a: _lazy("obpi_verify_packet_cmd")(packet=a.packet, as_json=a.as_json)
    )

    p_obpi_withdraw = obpi_commands.add_parser(
        "withdraw",
        help="Withdraw a phantom or erroneous OBPI from the ledger",
        description=(
            "Record an obpi_withdrawn event. The OBPI remains in the"
            " ledger but is excluded from counts."
        ),
        epilog=build_epilog(
            [
                'gz obpi withdraw OBPI-0.21.0-01 --reason "phantom entry from promotion"'
                ' --attestor "Jane Doe"',
                'gz obpi withdraw OBPI-0.21.0-01 --reason "duplicate" --attestor "Jane Doe"'
                " --dry-run",
            ]
        ),
    )
    p_obpi_withdraw.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.21.0-01)")
    p_obpi_withdraw.add_argument("--reason", required=True, help="Reason for withdrawal")
    p_obpi_withdraw.add_argument(
        "--attestor",
        required=True,
        help="Human attestor witnessing the withdrawal (non-empty; only humans witness)",
    )
    add_dry_run_flag(p_obpi_withdraw)
    p_obpi_withdraw.set_defaults(
        func=lambda a: _lazy("obpi_withdraw_cmd")(
            obpi=a.obpi, reason=a.reason, attestor=a.attestor, dry_run=a.dry_run
        )
    )

    p_obpi_block = obpi_commands.add_parser(
        "block",
        help="Record that an OBPI is waiting on an operator ruling",
        description=(
            "Record an obpi_blocked_on_operator event. The pipeline refuses to "
            "launch against a blocked OBPI until `gz obpi unblock` records the "
            "ruling (GHI #887). Reversible and unattested: the block states that "
            "the next legitimate action belongs to a human, not that work ended."
        ),
        epilog=build_epilog(
            [
                'gz obpi block OBPI-0.35.0-02 --reason "REQ-04 contradicts its own'
                ' counterexample test" --next-action "amend REQ-04 under attestation,'
                ' or change persistence to append without reserializing"',
            ]
        ),
    )
    p_obpi_block.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.21.0-01)")
    p_obpi_block.add_argument(
        "--reason", required=True, help="Why the OBPI cannot proceed without a human"
    )
    p_obpi_block.add_argument(
        "--next-action",
        dest="next_action",
        required=True,
        help="The concrete decision the operator owes (non-empty)",
    )
    add_dry_run_flag(p_obpi_block)
    p_obpi_block.set_defaults(
        func=lambda a: _lazy("obpi_block_cmd")(
            obpi=a.obpi, reason=a.reason, next_action=a.next_action, dry_run=a.dry_run
        )
    )

    p_obpi_unblock = obpi_commands.add_parser(
        "unblock",
        help="Record the operator ruling that releases a blocked OBPI",
        description=(
            "Record an obpi_unblocked event, releasing the block recorded by "
            "`gz obpi block` and restoring pipeline launch (GHI #887). --ruling "
            "carries the operator's decision verbatim."
        ),
        epilog=build_epilog(
            [
                'gz obpi unblock OBPI-0.35.0-02 --ruling "amend REQ-04" --operator "g0"',
            ]
        ),
    )
    p_obpi_unblock.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.21.0-01)")
    p_obpi_unblock.add_argument(
        "--ruling", required=True, help="The operator's decision, verbatim (non-empty)"
    )
    p_obpi_unblock.add_argument("--operator", required=True, help="Who ruled (non-empty)")
    add_dry_run_flag(p_obpi_unblock)
    p_obpi_unblock.set_defaults(
        func=lambda a: _lazy("obpi_unblock_cmd")(
            obpi=a.obpi, ruling=a.ruling, operator=a.operator, dry_run=a.dry_run
        )
    )

    p_obpi_supersede = obpi_commands.add_parser(
        "supersede",
        help="Supersede one OBPI by another",
        description=(
            "Record an obpi_superseded event. The superseded OBPI's graph node "
            "is marked superseded; the OBPI remains in the ledger but is "
            "replaced by the superseding OBPI named via --by."
        ),
        epilog=build_epilog(
            [
                "gz obpi supersede OBPI-0.21.0-01 --by OBPI-0.21.0-04"
                ' --rationale "replaced by redesigned brief" --attestor "Jane Doe"',
                "gz obpi supersede OBPI-0.21.0-01 --by OBPI-0.21.0-04"
                ' --rationale "replaced by redesigned brief" --attestor "Jane Doe"'
                " --dry-run",
            ]
        ),
    )
    p_obpi_supersede.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.21.0-01)")
    p_obpi_supersede.add_argument("--by", required=True, help="Superseding OBPI identifier")
    p_obpi_supersede.add_argument(
        "--rationale", required=True, help="Why the OBPI is superseded (non-empty)"
    )
    p_obpi_supersede.add_argument(
        "--attestor",
        required=True,
        help="Human attestor witnessing the supersession (non-empty)",
    )
    add_dry_run_flag(p_obpi_supersede)
    p_obpi_supersede.set_defaults(
        func=lambda a: _lazy("obpi_supersede_cmd")(
            obpi=a.obpi,
            by=a.by,
            rationale=a.rationale,
            attestor=a.attestor,
            dry_run=a.dry_run,
        )
    )

    _REPUDIATE_CAUSE_CHOICES = [
        "model-induced-fabrication",
        "operator-error",
        "verification-invalid",
    ]
    p_obpi_repudiate = obpi_commands.add_parser(
        "repudiate",
        help="Repudiate a fraudulent or erroneous OBPI completion without retiring the OBPI",
        description=(
            "Record an obpi_completion_repudiated event. Reverses a completion "
            "without the permanent retirement semantics of withdraw — the OBPI "
            "stays live for re-completion. Operator-gated: requires non-empty "
            "--attestor and --reason. Only a human may repudiate a Gate-5."
        ),
        epilog=build_epilog(
            [
                "gz obpi repudiate OBPI-0.0.70-02 --cause model-induced-fabrication"
                ' --reason "agent fabricated attestation" --attestor "g0"',
                "gz obpi repudiate OBPI-0.0.70-02 --cause operator-error"
                ' --reason "..." --attestor "g0" --dry-run',
            ]
        ),
    )
    p_obpi_repudiate.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.70-02)")
    p_obpi_repudiate.add_argument(
        "--cause",
        required=True,
        choices=_REPUDIATE_CAUSE_CHOICES,
        help="Cause enum (model-induced-fabrication | operator-error | verification-invalid)",
    )
    p_obpi_repudiate.add_argument(
        "--reason", required=True, help="Required repudiation reason text (non-empty)"
    )
    p_obpi_repudiate.add_argument(
        "--attestor", required=True, help="Human attestor name (non-empty; only humans repudiate)"
    )
    add_dry_run_flag(p_obpi_repudiate)
    p_obpi_repudiate.set_defaults(
        func=lambda a: _lazy("obpi_repudiate_cmd")(
            obpi=a.obpi, cause=a.cause, reason=a.reason, attestor=a.attestor, dry_run=a.dry_run
        )
    )

    p_obpi_audit = obpi_commands.add_parser(
        "audit",
        help="Gather evidence for OBPI brief and record in audit ledger",
        description="Run deterministic evidence checks (tests, coverage, @covers) for an OBPI.",
        epilog=build_epilog(
            [
                "gz obpi audit OBPI-0.1.0-01",
                "gz obpi audit OBPI-0.1.0-01 --json",
                "gz obpi audit --adr ADR-0.1.0",
            ]
        ),
    )
    p_obpi_audit.add_argument(
        "obpi", nargs="?", default=None, help="OBPI identifier (e.g. OBPI-0.1.0-01)"
    )
    p_obpi_audit.add_argument(
        "--adr", dest="adr_id", default=None, help="Audit all OBPIs under this ADR"
    )
    add_json_flag(p_obpi_audit)
    p_obpi_audit.set_defaults(
        func=lambda a: _lazy("obpi_audit_cmd")(obpi_id=a.obpi, adr_id=a.adr_id, as_json=a.as_json)
    )

    # --- gz obpi complete (atomic OBPI completion transaction) ---
    p_obpi_complete = obpi_commands.add_parser(
        "complete",
        help="Atomically complete an OBPI (validate, write evidence, flip status, emit receipt)",
        description=(
            "All-or-nothing OBPI completion: validates the brief, writes evidence "
            "sections, flips status to Completed, records attestation in the audit "
            "ledger, and emits a completion receipt. If any step fails, no files "
            "or ledger entries are modified."
        ),
        epilog=build_epilog(
            [
                'gz obpi complete OBPI-0.1.0-01 --attestor g0 --attestation-text "Verified"',
                (
                    "gz obpi complete OBPI-0.1.0-01 --attestor g0 "
                    '--attestation-text "Verified" --json'
                ),
                (
                    "gz obpi complete OBPI-0.1.0-01 --attestor g0 "
                    '--attestation-text "Verified" --dry-run'
                ),
            ]
        ),
    )
    p_obpi_complete.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.14-01)")
    p_obpi_complete.add_argument(
        "--attestor", required=True, help="Identity of the attestor (required)"
    )
    p_obpi_complete.add_argument(
        "--attestation-text",
        dest="attestation_text",
        required=True,
        help="Substantive attestation text (required)",
    )
    p_obpi_complete.add_argument(
        "--implementation-summary",
        dest="implementation_summary",
        default=None,
        help=("Implementation summary text (falls back to brief; fails closed if empty)"),
    )
    p_obpi_complete.add_argument(
        "--key-proof",
        dest="key_proof",
        default=None,
        help="Key proof text (falls back to brief; fails closed if empty)",
    )
    p_obpi_complete.add_argument(
        "--attestor-present",
        dest="attestor_present",
        action="store_true",
        help="Agent-relayed operator attestation, gated on active pipeline marker (GHI #292)",
    )
    p_obpi_complete.add_argument(
        "--accept-uncovered",
        action="append",
        dest="accept_uncovered",
        metavar="REQ_ID",
        default=None,
        help="Waive an uncovered REQ (repeatable). Requires --accept-uncovered-reason.",
    )
    p_obpi_complete.add_argument(
        "--accept-uncovered-reason",
        action="append",
        dest="accept_uncovered_reason",
        metavar="REASON",
        default=None,
        help="Rationale for --accept-uncovered (repeatable, 1:1 positional pairing).",
    )
    p_obpi_complete.add_argument(
        "--accept-security-floor",
        dest="accept_security_floor",
        metavar="REASON",
        default=None,
        help="Override unfilled security-scan canonical slot with rationale (GHI #462).",
    )
    p_obpi_complete.add_argument(
        "--accept-stale-reconciliation",
        dest="accept_stale_reconciliation",
        action="store_true",
        default=False,
        help="Override stale/drifted reconcile receipt. Requires --reason (min 10 chars).",
    )
    p_obpi_complete.add_argument(
        "--reason",
        dest="accept_stale_reconciliation_reason",
        metavar="TEXT",
        default=None,
        help="Rationale for --accept-stale-reconciliation (min 10 chars).",
    )
    # GHI #676 — Step-4b independent adversarial validation. Required on the heavy
    # lane; the verdict lands in the ledger as an `adversarial_validation` event so
    # it outlives the session that produced it.
    p_obpi_complete.add_argument(
        "--adversary-verdict",
        dest="adversary_verdict",
        choices=["refuted", "not-refuted", "refuted-with-caveats", "degraded-human-only"],
        default=None,
        help="Step-4b adversary verdict (required on heavy lane).",
    )
    p_obpi_complete.add_argument(
        "--adversary",
        dest="adversary",
        metavar="IDENTITY",
        default=None,
        help="Adversary identity, e.g. codex/gpt-5.4, or 'human' in degraded mode.",
    )
    p_obpi_complete.add_argument(
        "--adversary-job-id",
        dest="adversary_job_id",
        metavar="ID",
        default=None,
        help="Adversary run id, when the runtime supplies one.",
    )
    p_obpi_complete.add_argument(
        "--adversary-receipt",
        dest="adversary_receipt",
        metavar="RUN_ID",
        default=None,
        help="ARB step receipt run_id proving the tier from the argv that ran.",
    )
    p_obpi_complete.add_argument(
        "--refuted-claim",
        dest="refuted_claim",
        metavar="TEXT",
        default=None,
        help="The specific claim the adversary broke, verbatim.",
    )
    p_obpi_complete.add_argument(
        "--adversary-resolution",
        dest="adversary_resolution",
        metavar="TEXT",
        default=None,
        help="How a refutation was closed and re-verified. Required when verdict is 'refuted'.",
    )
    p_obpi_complete.add_argument(
        "--adversary-fallback-reason",
        dest="adversary_fallback_reason",
        metavar="TEXT",
        default=None,
        help="Why Codex was unavailable, if a Claude-family adversary ran (GHI #678).",
    )
    p_obpi_complete.add_argument(
        "--adversary-tier",
        dest="adversary_tier",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help="Declared Step-4b tier: 1 cross-vendor, 2 independent same-vendor, 3 degraded.",
    )
    add_json_flag(p_obpi_complete)
    add_dry_run_flag(p_obpi_complete)
    p_obpi_complete.set_defaults(
        func=lambda a: _lazy("obpi_complete_cmd")(
            obpi=a.obpi,
            attestor=a.attestor,
            attestation_text=a.attestation_text,
            implementation_summary=a.implementation_summary,
            key_proof=a.key_proof,
            attestor_present=a.attestor_present,
            accept_uncovered=a.accept_uncovered,
            accept_uncovered_reason=a.accept_uncovered_reason,
            accept_security_floor=a.accept_security_floor,
            accept_stale_reconciliation=a.accept_stale_reconciliation,
            accept_stale_reconciliation_reason=a.accept_stale_reconciliation_reason,
            adversary_verdict=a.adversary_verdict,
            adversary=a.adversary,
            adversary_job_id=a.adversary_job_id,
            adversary_receipt=a.adversary_receipt,
            refuted_claim=a.refuted_claim,
            adversary_resolution=a.adversary_resolution,
            adversary_fallback_reason=a.adversary_fallback_reason,
            adversary_tier=a.adversary_tier,
            as_json=a.as_json,
            dry_run=a.dry_run,
        )
    )

    # --- Nested lock subcommand group: gz obpi lock {claim|release|check|list} ---
    p_lock = obpi_commands.add_parser(
        "lock",
        help="OBPI work lock management for multi-agent coordination",
        description="Claim, release, check, and list OBPI work locks.",
        epilog=build_epilog(
            [
                "gz obpi lock claim OBPI-0.1.0-01",
                "gz obpi lock release OBPI-0.1.0-01",
                "gz obpi lock check OBPI-0.1.0-01",
                "gz obpi lock list",
            ]
        ),
    )
    lock_commands = p_lock.add_subparsers(dest="lock_command")
    lock_commands.required = True

    p_lock_claim = lock_commands.add_parser(
        "claim",
        help="Claim an OBPI work lock",
        description="Create a lock file and emit a ledger event.",
        epilog=build_epilog(
            [
                "gz obpi lock claim OBPI-0.1.0-01",
                "gz obpi lock claim OBPI-0.1.0-01 --ttl 240",
                "gz obpi lock claim OBPI-0.1.0-01 --agent my-agent --json",
            ]
        ),
    )
    p_lock_claim.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.1.0-01)")
    p_lock_claim.add_argument(
        "--ttl",
        dest="ttl_minutes",
        type=int,
        default=DEFAULT_LOCK_TTL_MINUTES,
        help="Lock TTL in minutes (default: 1440)",
    )
    p_lock_claim.add_argument(
        "--agent", dest="agent", default=None, help="Override auto-detected agent identity"
    )
    add_json_flag(p_lock_claim)
    p_lock_claim.set_defaults(
        func=lambda a: _lazy("obpi_lock_claim_cmd")(
            obpi_id=a.obpi, ttl_minutes=a.ttl_minutes, as_json=a.as_json, agent=a.agent
        )
    )

    p_lock_release = lock_commands.add_parser(
        "release",
        help="Release an OBPI work lock",
        description="Remove a lock file with ownership validation and emit a ledger event.",
        epilog=build_epilog(
            [
                "gz obpi lock release OBPI-0.1.0-01",
                "gz obpi lock release OBPI-0.1.0-01 --force",
                "gz obpi lock release OBPI-0.1.0-01 --json",
                "gz obpi lock release OBPI-0.1.0-01 --abandon network_loss:reason",
            ]
        ),
    )
    p_lock_release.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.1.0-01)")
    add_force_flag(p_lock_release, help_override="Release lock regardless of ownership")
    p_lock_release.add_argument(
        "--agent", dest="agent", default=None, help="Override auto-detected agent identity"
    )
    p_lock_release.add_argument(
        "--abandon",
        dest="abandon",
        default=None,
        metavar="CATEGORY:REASON",
        help=("Record abandonment; writes a degenerate handoff. See manpage for category enum."),
    )
    add_json_flag(p_lock_release)
    p_lock_release.set_defaults(
        func=lambda a: _lazy("obpi_lock_release_cmd")(
            obpi_id=a.obpi,
            as_json=a.as_json,
            force=a.force,
            agent=a.agent,
            abandon=a.abandon,
        )
    )

    p_lock_check = lock_commands.add_parser(
        "check",
        help="Check if an OBPI is locked (exit 0 = held, exit 1 = free)",
        description="Query lock status for a single OBPI.",
        epilog=build_epilog(
            [
                "gz obpi lock check OBPI-0.1.0-01",
                "gz obpi lock check OBPI-0.1.0-01 --json",
            ]
        ),
    )
    p_lock_check.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.1.0-01)")
    add_json_flag(p_lock_check)
    p_lock_check.set_defaults(
        func=lambda a: _lazy("obpi_lock_check_cmd")(obpi_id=a.obpi, as_json=a.as_json)
    )

    p_lock_list = lock_commands.add_parser(
        "list",
        help="List active OBPI work locks (auto-reaps expired)",
        description="Reap expired locks, then list remaining active locks.",
        epilog=build_epilog(
            [
                "gz obpi lock list",
                "gz obpi lock list --adr ADR-0.1.0",
                "gz obpi lock list --json",
            ]
        ),
    )
    p_lock_list.add_argument(
        "--adr", dest="adr_id", default=None, help="Filter locks by parent ADR"
    )
    add_json_flag(p_lock_list)
    p_lock_list.set_defaults(
        func=lambda a: _lazy("obpi_lock_list_cmd")(adr_id=a.adr_id, as_json=a.as_json)
    )
