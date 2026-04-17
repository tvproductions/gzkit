"""Artifact-focused subparser registrations for gz CLI.

Registers: adr subcommands, obpi subcommands, task subcommands.

Command handlers are resolved lazily via module-level ``__getattr__`` so
``gz --help`` does not import handler modules (and their heavy transitive
dependencies) just to render the help tree.
"""

from __future__ import annotations

import argparse
from typing import Any

from gzkit.cli.helpers import (
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    build_epilog,
)

_LAZY_HANDLERS: dict[str, str] = {
    "adr_audit_check": "gzkit.commands.adr_audit",
    "adr_covers_check": "gzkit.commands.adr_audit",
    "adr_emit_receipt_cmd": "gzkit.commands.adr_audit",
    "adr_eval_cmd": "gzkit.commands.adr_promote",
    "adr_promote_cmd": "gzkit.commands.adr_promote",
    "obpi_audit_cmd": "gzkit.commands.obpi_audit_cmd",
    "obpi_emit_receipt_cmd": "gzkit.commands.obpi_cmd",
    "obpi_pipeline_cmd": "gzkit.commands.obpi_cmd",
    "obpi_validate_cmd": "gzkit.commands.obpi_cmd",
    "obpi_withdraw_cmd": "gzkit.commands.obpi_cmd",
    "obpi_complete_cmd": "gzkit.commands.obpi_complete",
    "obpi_lock_check_cmd": "gzkit.commands.obpi_lock",
    "obpi_lock_claim_cmd": "gzkit.commands.obpi_lock",
    "obpi_lock_list_cmd": "gzkit.commands.obpi_lock",
    "obpi_lock_release_cmd": "gzkit.commands.obpi_lock",
    "adr_report_cmd": "gzkit.commands.status",
    "adr_status_cmd": "gzkit.commands.status",
    "obpi_reconcile_cmd": "gzkit.commands.status",
    "obpi_status_cmd": "gzkit.commands.status",
    "task_block_cmd": "gzkit.commands.task",
    "task_complete_cmd": "gzkit.commands.task",
    "task_escalate_cmd": "gzkit.commands.task",
    "task_list_cmd": "gzkit.commands.task",
    "task_start_cmd": "gzkit.commands.task",
}


def _make_lazy(module_path: str, name: str) -> Any:
    """Return a stub that imports *module_path* on first call and forwards."""

    def stub(*args: Any, **kwargs: Any) -> Any:
        from importlib import import_module

        impl = getattr(import_module(module_path), name)
        globals()[name] = impl
        return impl(*args, **kwargs)

    stub.__name__ = name
    stub.__qualname__ = name
    return stub


for _name, _mod in _LAZY_HANDLERS.items():
    globals()[_name] = _make_lazy(_mod, _name)
del _name, _mod

_ADR_TYPE_NAMES = {"foundation", "feature", "pool"}


def _dispatch_adr_report(a: argparse.Namespace) -> None:
    """Route gz adr report to summary or detail mode."""
    target = a.adr
    if target and target.lower() in _ADR_TYPE_NAMES:
        adr_report_cmd(adr=None, adr_type=target.lower())
    else:
        adr_report_cmd(adr=target, adr_type=a.type)


def register_artifact_parsers(commands: argparse._SubParsersAction) -> None:
    """Register adr, obpi, and task sub-command groups on *commands*."""
    _register_adr_parsers(commands)
    _register_obpi_parsers(commands)
    _register_task_parsers(commands)


def _register_adr_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz adr`` sub-command group."""
    p_adr = commands.add_parser(
        "adr",
        help="ADR-focused governance commands",
        description="ADR lifecycle, evaluation, and evidence commands.",
        epilog=build_epilog(
            [
                "gz adr status ADR-0.1.0",
                "gz adr report",
                "gz adr report ADR-0.1.0",
            ]
        ),
    )
    adr_commands = p_adr.add_subparsers(dest="adr_command")
    adr_commands.required = True

    p_adr_status = adr_commands.add_parser(
        "status",
        help="Show focused OBPI progress for one ADR",
        description="Display detailed OBPI progress for a single ADR.",
        epilog=build_epilog(
            [
                "gz adr status ADR-0.1.0",
                "gz adr status ADR-0.1.0 --json",
                "gz adr status ADR-0.1.0 --show-gates",
            ]
        ),
    )
    p_adr_status.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.4)")
    add_json_flag(p_adr_status)
    p_adr_status.add_argument(
        "--show-gates",
        action="store_true",
        help="Show detailed gate-level QC breakdown (internal diagnostics).",
    )
    p_adr_status.set_defaults(
        func=lambda a: adr_status_cmd(adr=a.adr, as_json=a.as_json, show_gates=a.show_gates)
    )

    p_adr_report = adr_commands.add_parser(
        "report",
        help="Deterministic tabular report (summary or single ADR)",
        description="Produce deterministic tabular report for all or one ADR, "
        "or filter by type (foundation, feature, pool).",
        epilog=build_epilog(
            [
                "gz adr report",
                "gz adr report ADR-0.1.0",
                "gz adr report pool",
                "gz adr report feature",
                "gz adr report --type foundation",
            ]
        ),
    )
    p_adr_report.add_argument(
        "adr",
        nargs="?",
        default=None,
        help="ADR identifier, or type name (foundation, feature, pool)",
    )
    p_adr_report.add_argument(
        "--type",
        choices=["foundation", "feature", "pool"],
        default=None,
        help="Filter summary to one ADR type (foundation, feature, pool)",
    )
    p_adr_report.set_defaults(func=lambda a: _dispatch_adr_report(a))

    p_adr_promote = adr_commands.add_parser(
        "promote",
        help="Promote a pool ADR into canonical ADR package structure",
        description="Move a backlog pool ADR into versioned ADR package.",
        epilog=build_epilog(
            [
                "gz adr promote ADR-pool.my-feature --semver 0.2.0",
                "gz adr promote ADR-pool.my-feature --semver 0.2.0 --lane heavy",
                "gz adr promote ADR-pool.my-feature --semver 0.2.0 --dry-run",
            ]
        ),
    )
    p_adr_promote.add_argument("pool_adr", help="Pool ADR id (e.g., ADR-pool.gz-chores-system)")
    p_adr_promote.add_argument(
        "--semver",
        required=True,
        help="Target ADR semantic version (X.Y.Z)",
    )
    p_adr_promote.add_argument(
        "--slug",
        help="Target ADR slug (kebab-case). Defaults to slug derived from pool ADR id.",
    )
    p_adr_promote.add_argument("--title", help="Target ADR title override")
    p_adr_promote.add_argument(
        "--parent",
        help="Target ADR parent override (defaults to pool ADR parent metadata)",
    )
    p_adr_promote.add_argument(
        "--lane",
        choices=["lite", "heavy"],
        help="Target ADR lane override (defaults to pool ADR lane metadata)",
    )
    p_adr_promote.add_argument(
        "--status",
        dest="target_status",
        choices=["draft", "proposed"],
        default="proposed",
        help="Initial promoted ADR status (default: proposed)",
    )
    add_json_flag(p_adr_promote)
    add_dry_run_flag(p_adr_promote)
    add_force_flag(
        p_adr_promote,
        help_override="Override scaffold quality gate (briefs contain only template defaults)",
    )
    p_adr_promote.set_defaults(
        func=lambda a: adr_promote_cmd(
            pool_adr=a.pool_adr,
            semver=a.semver,
            slug=a.slug,
            title=a.title,
            parent=a.parent,
            lane=a.lane,
            target_status=a.target_status,
            as_json=a.as_json,
            dry_run=a.dry_run,
            force=a.force,
        )
    )

    p_adr_eval = adr_commands.add_parser(
        "evaluate",
        help="Evaluate ADR/OBPI quality (deterministic scoring)",
        description="Score ADR quality across weighted dimensions.",
        epilog=build_epilog(
            [
                "gz adr evaluate ADR-0.1.0",
                "gz adr evaluate ADR-0.1.0 --json",
                "gz adr evaluate ADR-0.1.0 --no-scorecard",
            ]
        ),
    )
    p_adr_eval.add_argument("adr_id", help="ADR identifier (e.g., ADR-0.19.0)")
    add_json_flag(p_adr_eval)
    p_adr_eval.add_argument(
        "--no-scorecard",
        dest="write_scorecard",
        action="store_false",
        default=True,
        help="Skip writing scorecard file to disk",
    )
    p_adr_eval.set_defaults(
        func=lambda a: adr_eval_cmd(
            adr_id=a.adr_id,
            as_json=a.as_json,
            write_scorecard=a.write_scorecard,
        )
    )

    p_adr_audit_check = adr_commands.add_parser(
        "audit-check",
        help="Verify linked OBPIs are complete with evidence",
        description="Check that all linked OBPIs have passing evidence.",
        epilog=build_epilog(
            [
                "gz adr audit-check ADR-0.1.0",
                "gz adr audit-check ADR-0.1.0 --json",
            ]
        ),
    )
    p_adr_audit_check.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.4)")
    add_json_flag(p_adr_audit_check)
    p_adr_audit_check.set_defaults(func=lambda a: adr_audit_check(adr=a.adr, as_json=a.as_json))

    p_adr_covers_check = adr_commands.add_parser(
        "covers-check",
        help="Verify @covers traceability for ADR, OBPIs, and REQ IDs",
        description="Scan tests for @covers decorators and verify linkage.",
        epilog=build_epilog(
            [
                "gz adr covers-check ADR-0.1.0",
                "gz adr covers-check ADR-0.1.0 --json",
            ]
        ),
    )
    p_adr_covers_check.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.4)")
    add_json_flag(p_adr_covers_check)
    p_adr_covers_check.set_defaults(func=lambda a: adr_covers_check(adr=a.adr, as_json=a.as_json))

    p_adr_emit = adr_commands.add_parser(
        "emit-receipt",
        help="Emit completed/validated receipt event for an ADR",
        description=(
            "Record a receipt event in the ledger for an ADR. "
            "Required --evidence-json fields for completed: "
            "value_narrative, key_proof. "
            "Heavy/Foundation also require: "
            "human_attestation (true), attestation_text, "
            "attestation_date (YYYY-MM-DD)."
        ),
        epilog=build_epilog(
            [
                'gz adr emit-receipt ADR-0.1.0 --event completed --attestor "Jane Doe"',
                'gz adr emit-receipt ADR-0.1.0 --event validated --attestor "Jane Doe" --dry-run',
            ]
        ),
    )
    p_adr_emit.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.4)")
    p_adr_emit.add_argument(
        "--event",
        dest="receipt_event",
        required=True,
        choices=["completed", "validated"],
        help="Receipt event type (completed|validated)",
    )
    p_adr_emit.add_argument("--attestor", required=True, help="Identity of the attestor")
    p_adr_emit.add_argument(
        "--evidence-json",
        help="JSON with value_narrative, key_proof; Heavy adds attestation fields",
    )
    add_dry_run_flag(p_adr_emit)
    p_adr_emit.set_defaults(
        func=lambda a: adr_emit_receipt_cmd(
            adr=a.adr,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
            dry_run=a.dry_run,
        )
    )


def _register_obpi_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz obpi`` sub-command group."""
    p_obpi = commands.add_parser(
        "obpi",
        help="OBPI-focused governance commands",
        description="OBPI lifecycle, pipeline, and evidence commands.",
        epilog=build_epilog(
            [
                "gz obpi status OBPI-0.1.0-01",
                "gz obpi pipeline OBPI-0.1.0-01",
                "gz obpi reconcile OBPI-0.1.0-01",
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
    add_dry_run_flag(p_obpi_emit)
    p_obpi_emit.set_defaults(
        func=lambda a: obpi_emit_receipt_cmd(
            obpi=a.obpi,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
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
    p_obpi_status.set_defaults(func=lambda a: obpi_status_cmd(obpi=a.obpi, as_json=a.as_json))

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
        help="Attestor identity for Stage 5 (e.g. jeff or agent:<name>)",
    )
    p_obpi_pipeline.add_argument(
        "--evidence-json",
        dest="evidence_json",
        help="JSON evidence payload for Stage 5 (value_narrative, key_proof, etc.)",
    )
    p_obpi_pipeline.add_argument(
        "--clear-stale",
        dest="clear_stale",
        action="store_true",
        help="Remove pipeline markers older than 4 hours",
    )
    p_obpi_pipeline.add_argument(
        "--no-subagents",
        dest="no_subagents",
        action="store_true",
        help="Disable subagent dispatch (single-session fallback)",
    )
    p_obpi_pipeline.set_defaults(
        func=lambda a: obpi_pipeline_cmd(
            obpi=a.obpi,
            start_from=a.start_from,
            clear_stale=a.clear_stale,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
        )
    )

    p_obpi_reconcile = obpi_commands.add_parser(
        "reconcile",
        help="Fail-closed runtime reconciliation for one OBPI",
        description="Reconcile OBPI receipt and brief for consistency.",
        epilog=build_epilog(
            [
                "gz obpi reconcile OBPI-0.1.0-01",
                "gz obpi reconcile OBPI-0.1.0-01 --json",
            ]
        ),
    )
    p_obpi_reconcile.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.0.4-01)")
    add_json_flag(p_obpi_reconcile)
    p_obpi_reconcile.set_defaults(func=lambda a: obpi_reconcile_cmd(obpi=a.obpi, as_json=a.as_json))

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
        func=lambda a: obpi_validate_cmd(
            obpi_path=a.obpi_path,
            adr_id=a.adr_id,
            authored=a.authored,
        )
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
                'gz obpi withdraw OBPI-0.21.0-01 --reason "phantom entry from promotion"',
                'gz obpi withdraw OBPI-0.21.0-01 --reason "duplicate" --dry-run',
            ]
        ),
    )
    p_obpi_withdraw.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.21.0-01)")
    p_obpi_withdraw.add_argument("--reason", required=True, help="Reason for withdrawal")
    add_dry_run_flag(p_obpi_withdraw)
    p_obpi_withdraw.set_defaults(
        func=lambda a: obpi_withdraw_cmd(obpi=a.obpi, reason=a.reason, dry_run=a.dry_run)
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
        func=lambda a: obpi_audit_cmd(obpi_id=a.obpi, adr_id=a.adr_id, as_json=a.as_json)
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
                'gz obpi complete OBPI-0.1.0-01 --attestor jeff --attestation-text "Verified"',
                (
                    "gz obpi complete OBPI-0.1.0-01 --attestor jeff "
                    '--attestation-text "Verified" --json'
                ),
                (
                    "gz obpi complete OBPI-0.1.0-01 --attestor jeff "
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
        help="Implementation summary text (reads existing from brief if omitted)",
    )
    p_obpi_complete.add_argument(
        "--key-proof",
        dest="key_proof",
        default=None,
        help="Key proof text (reads existing from brief if omitted)",
    )
    add_json_flag(p_obpi_complete)
    add_dry_run_flag(p_obpi_complete)
    p_obpi_complete.set_defaults(
        func=lambda a: obpi_complete_cmd(
            obpi=a.obpi,
            attestor=a.attestor,
            attestation_text=a.attestation_text,
            implementation_summary=a.implementation_summary,
            key_proof=a.key_proof,
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
        default=120,
        help="Lock TTL in minutes (default: 120)",
    )
    p_lock_claim.add_argument(
        "--agent", dest="agent", default=None, help="Override auto-detected agent identity"
    )
    add_json_flag(p_lock_claim)
    p_lock_claim.set_defaults(
        func=lambda a: obpi_lock_claim_cmd(
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
            ]
        ),
    )
    p_lock_release.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.1.0-01)")
    add_force_flag(p_lock_release, help_override="Release lock regardless of ownership")
    p_lock_release.add_argument(
        "--agent", dest="agent", default=None, help="Override auto-detected agent identity"
    )
    add_json_flag(p_lock_release)
    p_lock_release.set_defaults(
        func=lambda a: obpi_lock_release_cmd(
            obpi_id=a.obpi, as_json=a.as_json, force=a.force, agent=a.agent
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
    p_lock_check.set_defaults(func=lambda a: obpi_lock_check_cmd(obpi_id=a.obpi, as_json=a.as_json))

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
    p_lock_list.set_defaults(func=lambda a: obpi_lock_list_cmd(adr_id=a.adr_id, as_json=a.as_json))

    # --- Deprecated flat aliases (OBPI-03 will remove these after skill migration) ---
    p_lock_claim_dep = obpi_commands.add_parser(
        "lock-claim",
        help="[deprecated] Use 'gz obpi lock claim' instead",
        description="Deprecated alias for 'gz obpi lock claim'. Use the nested form instead.",
        epilog=build_epilog(["gz obpi lock claim OBPI-0.1.0-01"]),
    )
    p_lock_claim_dep.add_argument("obpi", help="OBPI identifier")
    p_lock_claim_dep.add_argument(
        "--ttl", dest="ttl_minutes", type=int, default=120, help="Lock TTL in minutes"
    )
    p_lock_claim_dep.add_argument(
        "--agent", dest="agent", default=None, help="Override auto-detected agent identity"
    )
    add_json_flag(p_lock_claim_dep)
    p_lock_claim_dep.set_defaults(
        func=lambda a: obpi_lock_claim_cmd(
            obpi_id=a.obpi, ttl_minutes=a.ttl_minutes, as_json=a.as_json, agent=a.agent
        )
    )

    p_lock_release_dep = obpi_commands.add_parser(
        "lock-release",
        help="[deprecated] Use 'gz obpi lock release' instead",
        description="Deprecated alias for 'gz obpi lock release'. Use the nested form instead.",
        epilog=build_epilog(["gz obpi lock release OBPI-0.1.0-01"]),
    )
    p_lock_release_dep.add_argument("obpi", help="OBPI identifier")
    add_force_flag(p_lock_release_dep)
    p_lock_release_dep.add_argument(
        "--agent", dest="agent", default=None, help="Override auto-detected agent identity"
    )
    add_json_flag(p_lock_release_dep)
    p_lock_release_dep.set_defaults(
        func=lambda a: obpi_lock_release_cmd(
            obpi_id=a.obpi, as_json=a.as_json, force=a.force, agent=a.agent
        )
    )

    p_lock_status_dep = obpi_commands.add_parser(
        "lock-status",
        help="[deprecated] Use 'gz obpi lock list' instead",
        description="Deprecated alias for 'gz obpi lock list'. Use the nested form instead.",
        epilog=build_epilog(["gz obpi lock list"]),
    )
    p_lock_status_dep.add_argument(
        "--adr", dest="adr_id", default=None, help="Filter locks by parent ADR"
    )
    add_json_flag(p_lock_status_dep)
    p_lock_status_dep.set_defaults(
        func=lambda a: obpi_lock_list_cmd(adr_id=a.adr_id, as_json=a.as_json)
    )


def _register_task_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz task`` sub-command group."""
    p_task = commands.add_parser(
        "task",
        help="TASK lifecycle management commands",
        description=(
            "Manage execution-level TASK entities: list, start, complete, block, escalate."
        ),
        epilog=build_epilog(
            [
                "gz task list OBPI-0.20.0-01",
                "gz task start TASK-0.20.0-01-01-01",
                "gz task complete TASK-0.20.0-01-01-01",
                'gz task block TASK-0.20.0-01-01-01 --reason "Missing API"',
                'gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human decision"',
            ]
        ),
    )
    task_commands = p_task.add_subparsers(dest="task_command")
    task_commands.required = True

    p_task_list = task_commands.add_parser(
        "list",
        help="List tasks for an OBPI",
        description="Show all tasks and their lifecycle status for an OBPI.",
        epilog=build_epilog(
            [
                "gz task list OBPI-0.20.0-01",
                "gz task list OBPI-0.20.0-01 --json",
            ]
        ),
    )
    p_task_list.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.20.0-01)")
    add_json_flag(p_task_list)
    p_task_list.set_defaults(func=lambda a: task_list_cmd(obpi=a.obpi, as_json=a.as_json))

    p_task_start = task_commands.add_parser(
        "start",
        help="Start or resume a task",
        description="Transition a task to in_progress (from pending or blocked).",
        epilog=build_epilog(
            [
                "gz task start TASK-0.20.0-01-01-01",
                "gz task start TASK-0.20.0-01-01-01 --json",
            ]
        ),
    )
    p_task_start.add_argument("task_id", help="TASK identifier (e.g. TASK-0.20.0-01-01-01)")
    add_json_flag(p_task_start)
    p_task_start.set_defaults(
        func=lambda a: task_start_cmd(task_id_str=a.task_id, as_json=a.as_json)
    )

    p_task_complete = task_commands.add_parser(
        "complete",
        help="Complete a task",
        description="Transition a task to completed (from in_progress only).",
        epilog=build_epilog(
            [
                "gz task complete TASK-0.20.0-01-01-01",
            ]
        ),
    )
    p_task_complete.add_argument("task_id", help="TASK identifier (e.g. TASK-0.20.0-01-01-01)")
    add_json_flag(p_task_complete)
    p_task_complete.set_defaults(
        func=lambda a: task_complete_cmd(task_id_str=a.task_id, as_json=a.as_json)
    )

    p_task_block = task_commands.add_parser(
        "block",
        help="Block a task with reason",
        description="Transition a task to blocked (from in_progress only).",
        epilog=build_epilog(
            [
                'gz task block TASK-0.20.0-01-01-01 --reason "Missing API"',
            ]
        ),
    )
    p_task_block.add_argument("task_id", help="TASK identifier (e.g. TASK-0.20.0-01-01-01)")
    p_task_block.add_argument("--reason", required=True, help="Reason for blocking the task")
    add_json_flag(p_task_block)
    p_task_block.set_defaults(
        func=lambda a: task_block_cmd(task_id_str=a.task_id, reason=a.reason, as_json=a.as_json)
    )

    p_task_escalate = task_commands.add_parser(
        "escalate",
        help="Escalate a task with reason",
        description="Transition a task to escalated (from in_progress only).",
        epilog=build_epilog(
            [
                'gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human decision"',
            ]
        ),
    )
    p_task_escalate.add_argument("task_id", help="TASK identifier (e.g. TASK-0.20.0-01-01-01)")
    p_task_escalate.add_argument("--reason", required=True, help="Reason for escalation")
    add_json_flag(p_task_escalate)
    p_task_escalate.set_defaults(
        func=lambda a: task_escalate_cmd(task_id_str=a.task_id, reason=a.reason, as_json=a.as_json)
    )
