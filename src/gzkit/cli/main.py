"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse

from gzkit import __version__
from gzkit.cli.helpers import (
    add_adr_option,
    add_common_flags,
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    add_table_flag,
    build_epilog,
)
from gzkit.cli.helpers.exit_codes import exit_code_for
from gzkit.cli.parser import StableArgumentParser
from gzkit.commands.adr_audit import (
    adr_audit_check,
    adr_covers_check,
    adr_emit_receipt_cmd,
)
from gzkit.commands.adr_promote import adr_eval_cmd, adr_promote_cmd
from gzkit.commands.attest import attest
from gzkit.commands.audit_cmd import (
    _write_audit_artifacts,  # noqa: F401 — test-mock compat
    audit_cmd,
)
from gzkit.commands.chores import (
    chores_advise,
    chores_audit,
    chores_list,
    chores_plan,
    chores_run,
    chores_show,
)
from gzkit.commands.cli_audit import cli_audit_cmd
from gzkit.commands.closeout import closeout_cmd
from gzkit.commands.common import (
    COMMAND_DOCS,  # noqa: F401 — backward-compat re-export
    GzCliError,  # noqa: F401 — backward-compat re-export
    console,
    ensure_initialized,  # noqa: F401 — test-mock compat
    get_project_root,  # noqa: F401 — test-mock compat
    load_manifest,  # noqa: F401 — test-mock compat
    resolve_adr_file,  # noqa: F401 — backward-compat re-export
    resolve_target_adr,  # noqa: F401 — test-mock compat
)
from gzkit.commands.config_paths import check_config_paths_cmd
from gzkit.commands.covers import covers_cmd  # noqa: F401 — used in _build_parser
from gzkit.commands.drift import drift_cmd  # noqa: F401 — used in _build_parser
from gzkit.commands.gates import (
    _run_eval_delta,  # noqa: F401 — test-mock compat
    _run_gate_1,  # noqa: F401 — test-mock compat
    _run_gate_2,  # noqa: F401 — test-mock compat
    _run_gate_3,  # noqa: F401 — test-mock compat
    _run_gate_4,  # noqa: F401 — test-mock compat
    _run_gate_5,  # noqa: F401 — test-mock compat
    gates_cmd,
    implement_cmd,
)
from gzkit.commands.init_cmd import constitute, init, prd
from gzkit.commands.interview_cmd import interview
from gzkit.commands.obpi_cmd import (
    obpi_emit_receipt_cmd,
    obpi_pipeline_cmd,
    obpi_validate_cmd,
    obpi_withdraw_cmd,
)
from gzkit.commands.parity import parity_check_cmd
from gzkit.commands.plan import plan_cmd
from gzkit.commands.preflight import preflight_cmd
from gzkit.commands.quality import check, format_cmd, lint, test, typecheck
from gzkit.commands.readiness import readiness_audit_cmd, readiness_eval_cmd
from gzkit.commands.register import migrate_semver, register_adrs
from gzkit.commands.roles import roles_cmd
from gzkit.commands.skills_cmd import skill_audit_cmd, skill_list, skill_new
from gzkit.commands.specify_cmd import specify
from gzkit.commands.state import state
from gzkit.commands.status import (
    adr_report_cmd,
    adr_status_cmd,
    obpi_reconcile_cmd,
    obpi_status_cmd,
    status,
)
from gzkit.commands.sync import git_sync
from gzkit.commands.task import (
    task_block_cmd,
    task_complete_cmd,
    task_escalate_cmd,
    task_list_cmd,
    task_start_cmd,
)
from gzkit.commands.tidy import sync_control_surfaces, tidy
from gzkit.commands.validate_cmd import validate
from gzkit.core.exceptions import GzkitError
from gzkit.ledger import resolve_adr_lane  # noqa: F401 — test-mock compat
from gzkit.quality import run_all_checks, run_command  # noqa: F401 — test-mock compat
from gzkit.skills import DEFAULT_MAX_REVIEW_AGE_DAYS


def _add_git_sync_options(parser: argparse.ArgumentParser) -> None:
    """Register common git-sync CLI flags."""
    parser.add_argument(
        "--skill",
        action="store_true",
        help="Print path to paired skill file and exit",
    )
    parser.add_argument("--branch", help="Branch to sync (default: current branch)")
    parser.add_argument("--remote", default="origin", help="Remote name")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute sync actions (dry-run by default)",
    )
    parser.add_argument(
        "--lint",
        dest="run_lint_gate",
        action="store_true",
        default=True,
        help="Run lint gate before sync (default)",
    )
    parser.add_argument(
        "--no-lint", dest="run_lint_gate", action="store_false", help="Skip lint gate"
    )
    parser.add_argument(
        "--test",
        dest="run_test_gate",
        action="store_true",
        default=True,
        help="Run test gate before sync (default)",
    )
    parser.add_argument(
        "--no-test", dest="run_test_gate", action="store_false", help="Skip test gate"
    )
    parser.add_argument(
        "--auto-add",
        dest="auto_add",
        action="store_true",
        default=True,
        help="Auto-add tracked files before commit (default)",
    )
    parser.add_argument(
        "--no-auto-add",
        dest="auto_add",
        action="store_false",
        help="Skip auto-add of tracked files",
    )
    parser.add_argument(
        "--push",
        dest="allow_push",
        action="store_true",
        default=True,
        help="Push after commit (default)",
    )
    parser.add_argument(
        "--no-push", dest="allow_push", action="store_false", help="Commit without pushing"
    )
    add_json_flag(parser, help_override="Output as JSON")


def _build_parser() -> argparse.ArgumentParser:
    """Build argparse parser tree for gz CLI."""
    parser = StableArgumentParser(
        prog="gz",
        description="gzkit: A Development Covenant for Human-AI Collaboration.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"gzkit {__version__}",
    )
    add_common_flags(parser)

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    p_init = commands.add_parser(
        "init",
        help="Initialize gzkit in the current project",
        description="Initialize gzkit governance scaffolding in the current directory.",
        epilog=build_epilog(
            [
                "gz init",
                "gz init --mode heavy",
                "gz init --force --dry-run",
            ]
        ),
    )
    p_init.add_argument(
        "--mode",
        choices=["lite", "heavy"],
        default="lite",
        help="Governance lane mode (lite|heavy)",
    )
    add_force_flag(p_init)
    add_dry_run_flag(p_init)
    p_init.set_defaults(func=lambda a: init(mode=a.mode, force=a.force, dry_run=a.dry_run))

    p_prd = commands.add_parser(
        "prd",
        help="Create a new PRD",
        description="Create a new product requirements document.",
        epilog=build_epilog(
            [
                "gz prd my-product",
                'gz prd my-product --title "My Product Requirements"',
                "gz prd my-product --dry-run",
            ]
        ),
    )
    p_prd.add_argument("name", help="PRD slug name (kebab-case)")
    p_prd.add_argument("--title", help="PRD title override")
    add_dry_run_flag(p_prd)
    p_prd.set_defaults(func=lambda a: prd(name=a.name, title=a.title, dry_run=a.dry_run))

    p_constitute = commands.add_parser(
        "constitute",
        help="Create a new constitution",
        description="Create a new governance constitution document.",
        epilog=build_epilog(
            [
                "gz constitute my-constitution",
                'gz constitute my-constitution --title "Project Constitution"',
                "gz constitute my-constitution --dry-run",
            ]
        ),
    )
    p_constitute.add_argument("name", help="Constitution slug name (kebab-case)")
    p_constitute.add_argument("--title", help="Constitution title override")
    add_dry_run_flag(p_constitute)
    p_constitute.set_defaults(
        func=lambda a: constitute(name=a.name, title=a.title, dry_run=a.dry_run)
    )

    p_specify = commands.add_parser(
        "specify",
        help="Create a new OBPI",
        description="Create a new OBPI brief linked to a parent ADR.",
        epilog=build_epilog(
            [
                "gz specify my-feature --parent ADR-0.1.0",
                "gz specify my-feature --parent ADR-0.1.0 --item 3 --lane heavy",
                "gz specify my-feature --parent ADR-0.1.0 --dry-run",
            ]
        ),
    )
    p_specify.add_argument("name", help="OBPI slug name (kebab-case)")
    p_specify.add_argument("--parent", required=True, help="Parent ADR identifier (e.g. ADR-0.0.4)")
    p_specify.add_argument("--item", type=int, default=1, help="OBPI item number within parent ADR")
    p_specify.add_argument(
        "--lane", choices=["lite", "heavy"], default="lite", help="Governance lane (lite|heavy)"
    )
    p_specify.add_argument("--title", help="OBPI title override")
    add_dry_run_flag(p_specify)
    p_specify.set_defaults(
        func=lambda a: specify(
            name=a.name,
            parent=a.parent,
            item=a.item,
            lane=a.lane,
            title=a.title,
            dry_run=a.dry_run,
        )
    )

    p_plan = commands.add_parser(
        "plan",
        help="Create a new ADR",
        description="Create a new Architecture Decision Record with scoring.",
        epilog=build_epilog(
            [
                "gz plan my-feature --semver 0.1.0 --lane lite",
                'gz plan my-feature --semver 0.2.0 --lane heavy --title "My Feature"',
                "gz plan my-feature --semver 0.1.0 --dry-run",
            ]
        ),
    )
    p_plan.add_argument("name", help="ADR slug name (kebab-case)")
    p_plan.add_argument(
        "--obpi", dest="parent_obpi", help="Parent OBPI identifier for traceability"
    )
    p_plan.add_argument("--semver", default="0.1.0", help="Semantic version for the ADR (X.Y.Z)")
    p_plan.add_argument(
        "--lane", choices=["lite", "heavy"], default="lite", help="Governance lane (lite|heavy)"
    )
    p_plan.add_argument("--title", help="ADR title override")
    p_plan.add_argument(
        "--score-data-state", type=int, choices=[0, 1, 2], help="Data-state dimension score (0-2)"
    )
    p_plan.add_argument(
        "--score-logic-engine",
        type=int,
        choices=[0, 1, 2],
        help="Logic-engine dimension score (0-2)",
    )
    p_plan.add_argument(
        "--score-interface", type=int, choices=[0, 1, 2], help="Interface dimension score (0-2)"
    )
    p_plan.add_argument(
        "--score-observability",
        type=int,
        choices=[0, 1, 2],
        help="Observability dimension score (0-2)",
    )
    p_plan.add_argument(
        "--score-lineage", type=int, choices=[0, 1, 2], help="Lineage dimension score (0-2)"
    )
    p_plan.add_argument(
        "--split-single-narrative",
        action="store_true",
        help="Apply single-narrative split heuristic",
    )
    p_plan.add_argument(
        "--split-surface-boundary",
        action="store_true",
        help="Apply surface-boundary split heuristic",
    )
    p_plan.add_argument(
        "--split-state-anchor", action="store_true", help="Apply state-anchor split heuristic"
    )
    p_plan.add_argument(
        "--split-testability-ceiling",
        action="store_true",
        help="Apply testability-ceiling split heuristic",
    )
    p_plan.add_argument("--baseline-selected", type=int, help="Selected baseline index for scoring")
    add_dry_run_flag(p_plan)
    p_plan.set_defaults(
        func=lambda a: plan_cmd(
            name=a.name,
            parent_obpi=a.parent_obpi,
            semver=a.semver,
            lane=a.lane,
            title=a.title,
            score_data_state=a.score_data_state,
            score_logic_engine=a.score_logic_engine,
            score_interface=a.score_interface,
            score_observability=a.score_observability,
            score_lineage=a.score_lineage,
            split_single_narrative=a.split_single_narrative,
            split_surface_boundary=a.split_surface_boundary,
            split_state_anchor=a.split_state_anchor,
            split_testability_ceiling=a.split_testability_ceiling,
            baseline_selected=a.baseline_selected,
            dry_run=a.dry_run,
        )
    )

    p_state = commands.add_parser(
        "state",
        help="Query ledger state and relationships",
        description="Query artifact graph, blockers, and readiness from ledger.",
        epilog=build_epilog(
            [
                "gz state --json",
                "gz state --blocked",
                "gz state --ready",
            ]
        ),
    )
    add_json_flag(p_state)
    p_state.add_argument("--blocked", action="store_true", help="Show only blocked artifacts")
    p_state.add_argument(
        "--ready", action="store_true", help="Show only ready-to-proceed artifacts"
    )
    p_state.set_defaults(func=lambda a: state(as_json=a.as_json, blocked=a.blocked, ready=a.ready))

    p_status = commands.add_parser(
        "status",
        help="Show OBPI progress and ADR lifecycle status",
        description="Display OBPI completion progress and ADR lifecycle state.",
        epilog=build_epilog(
            [
                "gz status --table",
                "gz status --json",
                "gz status --show-gates",
            ]
        ),
    )
    add_json_flag(p_status)
    add_table_flag(
        p_status, help_override="Show a tabular ADR summary (ADR, lifecycle, lane, OBPI, QC)."
    )
    p_status.add_argument(
        "--show-gates",
        action="store_true",
        help="Show detailed gate-level QC breakdown (internal diagnostics).",
    )
    p_status.set_defaults(
        func=lambda a: status(as_json=a.as_json, show_gates=a.show_gates, as_table=a.table)
    )

    p_closeout = commands.add_parser(
        "closeout",
        help="Initiate closeout mode and record closeout event",
        description="Begin ADR closeout and generate closeout form.",
        epilog=build_epilog(
            [
                "gz closeout ADR-0.1.0",
                "gz closeout ADR-0.1.0 --dry-run",
                "gz closeout ADR-0.1.0 --json",
            ]
        ),
    )
    p_closeout.add_argument("adr", help="ADR identifier to close out (e.g. ADR-0.0.4)")
    add_json_flag(p_closeout)
    add_dry_run_flag(p_closeout)
    p_closeout.set_defaults(
        func=lambda a: closeout_cmd(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run)
    )

    p_audit = commands.add_parser(
        "audit",
        help="Run ADR audit routine and persist proof artifacts",
        description="Run post-attestation audit and persist proof artifacts.",
        epilog=build_epilog(
            [
                "gz audit ADR-0.1.0",
                "gz audit ADR-0.1.0 --dry-run",
                "gz audit ADR-0.1.0 --json",
            ]
        ),
    )
    p_audit.add_argument("adr", help="ADR identifier to audit (e.g. ADR-0.0.4)")
    add_json_flag(p_audit)
    add_dry_run_flag(p_audit)
    p_audit.set_defaults(func=lambda a: audit_cmd(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run))

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
        description="Produce deterministic tabular report for all or one ADR.",
        epilog=build_epilog(
            [
                "gz adr report",
                "gz adr report ADR-0.1.0",
            ]
        ),
    )
    p_adr_report.add_argument(
        "adr", nargs="?", default=None, help="ADR identifier (omit for summary)"
    )
    p_adr_report.set_defaults(func=lambda a: adr_report_cmd(adr=a.adr))

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
        description="Record a receipt event in the ledger for an ADR.",
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
    p_adr_emit.add_argument("--evidence-json", help="JSON evidence payload string")
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
        description="Record a receipt event in the ledger for an OBPI.",
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
    p_obpi_emit.add_argument("--evidence-json", help="JSON evidence payload string")
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
        help="Validate OBPI brief(s) for completion readiness",
        description="Check OBPI briefs against the canonical completion schema.",
        epilog=build_epilog(
            [
                "gz obpi validate docs/design/adr/my-adr/obpis/OBPI-0.1.0-01-my-feature.md",
                "gz obpi validate --adr ADR-0.1.0",
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
    p_obpi_validate.set_defaults(
        func=lambda a: obpi_validate_cmd(obpi_path=a.obpi_path, adr_id=a.adr_id)
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

    p_check_paths = commands.add_parser(
        "check-config-paths",
        help="Validate config/manifest paths are coherent",
        description="Verify configured and manifest path coherence.",
        epilog=build_epilog(
            [
                "gz check-config-paths",
                "gz check-config-paths --json",
            ]
        ),
    )
    add_json_flag(p_check_paths)
    p_check_paths.set_defaults(func=lambda a: check_config_paths_cmd(as_json=a.as_json))

    p_preflight = commands.add_parser(
        "preflight",
        help="Scan for stale pipeline artifacts",
        description="Detect and clean stale markers, orphan receipts, and expired locks.",
        epilog=build_epilog(
            [
                "gz preflight",
                "gz preflight --apply",
                "gz preflight --json",
            ]
        ),
    )
    p_preflight.add_argument(
        "--apply",
        action="store_true",
        help="Remove stale artifacts (default: dry-run report only)",
    )
    add_json_flag(p_preflight)
    p_preflight.set_defaults(func=lambda a: preflight_cmd(apply=a.apply, as_json=a.as_json))

    p_cli = commands.add_parser(
        "cli",
        help="CLI governance commands",
        description="CLI documentation and coverage audit commands.",
        epilog=build_epilog(
            [
                "gz cli audit",
                "gz cli audit --json",
            ]
        ),
    )
    cli_commands = p_cli.add_subparsers(dest="cli_command")
    cli_commands.required = True
    p_cli_audit = cli_commands.add_parser(
        "audit",
        help="Audit CLI docs/manpage coverage",
        description="Check CLI command documentation and manpage parity.",
        epilog=build_epilog(
            [
                "gz cli audit",
                "gz cli audit --json",
            ]
        ),
    )
    add_json_flag(p_cli_audit)
    p_cli_audit.set_defaults(func=lambda a: cli_audit_cmd(as_json=a.as_json))

    p_parity = commands.add_parser(
        "parity",
        help="Parity governance commands",
        description="Cross-repository parity regression commands.",
        epilog=build_epilog(
            [
                "gz parity check",
                "gz parity check --json",
            ]
        ),
    )
    parity_commands = p_parity.add_subparsers(dest="parity_command")
    parity_commands.required = True
    p_parity_check = parity_commands.add_parser(
        "check",
        help="Run deterministic parity regression checks",
        description="Execute deterministic parity regression checks.",
        epilog=build_epilog(
            [
                "gz parity check",
                "gz parity check --json",
            ]
        ),
    )
    add_json_flag(p_parity_check)
    p_parity_check.set_defaults(func=lambda a: parity_check_cmd(as_json=a.as_json))

    p_readiness = commands.add_parser(
        "readiness",
        help="Agent readiness governance commands",
        description="Agent readiness audit and evaluation commands.",
        epilog=build_epilog(
            [
                "gz readiness audit",
                "gz readiness evaluate",
            ]
        ),
    )
    readiness_commands = p_readiness.add_subparsers(dest="readiness_command")
    readiness_commands.required = True
    p_readiness_audit = readiness_commands.add_parser(
        "audit",
        help="Audit readiness across disciplines and primitives",
        description="Audit agent readiness across all disciplines.",
        epilog=build_epilog(
            [
                "gz readiness audit",
                "gz readiness audit --json",
            ]
        ),
    )
    add_json_flag(p_readiness_audit)
    p_readiness_audit.set_defaults(func=lambda a: readiness_audit_cmd(as_json=a.as_json))
    p_readiness_eval = readiness_commands.add_parser(
        "evaluate",
        help="Run instruction eval suite with positive/negative controls",
        description="Execute instruction evaluation with control cases.",
        epilog=build_epilog(
            [
                "gz readiness evaluate",
                "gz readiness evaluate --json",
            ]
        ),
    )
    add_json_flag(p_readiness_eval)
    p_readiness_eval.set_defaults(func=lambda a: readiness_eval_cmd(as_json=a.as_json))

    p_git_sync = commands.add_parser(
        "git-sync",
        help="Sync branch with guarded ritual",
        description="Commit, lint-gate, test-gate, and push in one ritual.",
        epilog=build_epilog(
            [
                "gz git-sync --apply --lint --test",
                "gz git-sync --apply --no-push",
                "gz git-sync --json",
            ]
        ),
    )
    _add_git_sync_options(p_git_sync)
    p_git_sync.set_defaults(
        func=lambda a: git_sync(
            branch=a.branch,
            remote=a.remote,
            apply=a.apply,
            run_lint_gate=a.run_lint_gate,
            run_test_gate=a.run_test_gate,
            auto_add=a.auto_add,
            allow_push=a.allow_push,
            as_json=a.as_json,
            show_skill=a.skill,
        )
    )

    p_migrate = commands.add_parser(
        "migrate-semver",
        help="Record SemVer ID rename events",
        description="Record semver identifier migration events in ledger.",
        epilog=build_epilog(
            [
                "gz migrate-semver",
                "gz migrate-semver --dry-run",
            ]
        ),
    )
    add_dry_run_flag(p_migrate)
    p_migrate.set_defaults(func=lambda a: migrate_semver(dry_run=a.dry_run))

    p_register_adrs = commands.add_parser(
        "register-adrs",
        help="Register ADR packages missing from ledger state",
        description="Reconcile on-disk ADR packages with governance ledger.",
        epilog=build_epilog(
            [
                "gz register-adrs",
                "gz register-adrs ADR-0.1.0 ADR-0.2.0",
                "gz register-adrs --all --dry-run",
            ]
        ),
    )
    p_register_adrs.add_argument(
        "targets",
        nargs="*",
        help="Optional ADR ids to reconcile; when omitted, scan all eligible ADR packages",
    )
    p_register_adrs.add_argument(
        "--lane",
        choices=["lite", "heavy"],
        help="Default lane to use when ADR metadata has no lane",
    )
    p_register_adrs.add_argument(
        "--pool-only",
        dest="pool_only",
        action="store_true",
        default=True,
        help="Register only pool ADRs (default)",
    )
    p_register_adrs.add_argument(
        "--all",
        dest="pool_only",
        action="store_false",
        help="Register all ADRs (pool + non-pool)",
    )
    add_dry_run_flag(p_register_adrs)
    p_register_adrs.set_defaults(
        func=lambda a: register_adrs(
            lane=a.lane,
            pool_only=a.pool_only,
            dry_run=a.dry_run,
            targets=a.targets,
        )
    )

    p_chores = commands.add_parser(
        "chores",
        help="Chore registry and execution commands",
        description="Discover, plan, execute, and audit repository chores.",
        epilog=build_epilog(
            [
                "gz chores list",
                "gz chores show my-chore",
                "gz chores run my-chore",
            ]
        ),
    )
    chores_commands = p_chores.add_subparsers(dest="chores_command")
    chores_commands.required = True

    chores_commands.add_parser(
        "list",
        help="List chores from registry",
        description="Display all registered chores and their status.",
        epilog=build_epilog(
            [
                "gz chores list",
            ]
        ),
    ).set_defaults(func=lambda a: chores_list())

    p_chores_show = chores_commands.add_parser(
        "show",
        help="Display CHORE.md for one chore",
        description="Show the full chore definition for a given slug.",
        epilog=build_epilog(
            [
                "gz chores show my-chore",
            ]
        ),
    )
    p_chores_show.add_argument("slug", help="Chore slug identifier")
    p_chores_show.set_defaults(func=lambda a: chores_show(slug=a.slug))

    p_chores_plan = chores_commands.add_parser(
        "plan",
        help="Show plan details for one chore",
        description="Display the execution plan for a given chore.",
        epilog=build_epilog(
            [
                "gz chores plan my-chore",
            ]
        ),
    )
    p_chores_plan.add_argument("slug", help="Chore slug identifier")
    p_chores_plan.set_defaults(func=lambda a: chores_plan(slug=a.slug))

    p_chores_advise = chores_commands.add_parser(
        "advise",
        help="Dry-run criteria and report status",
        description="Evaluate chore criteria and advise on readiness.",
        epilog=build_epilog(
            [
                "gz chores advise my-chore",
            ]
        ),
    )
    p_chores_advise.add_argument("slug", help="Chore slug identifier")
    p_chores_advise.set_defaults(func=lambda a: chores_advise(slug=a.slug))

    p_chores_run = chores_commands.add_parser(
        "run",
        help="Execute one chore by slug",
        description="Execute a single chore and record results.",
        epilog=build_epilog(
            [
                "gz chores run my-chore",
            ]
        ),
    )
    p_chores_run.add_argument("slug", help="Chore slug identifier")
    p_chores_run.set_defaults(func=lambda a: chores_run(slug=a.slug))

    p_chores_audit = chores_commands.add_parser(
        "audit",
        help="Audit chore log presence",
        description="Verify chore execution logs are present.",
        epilog=build_epilog(
            [
                "gz chores audit --all",
                "gz chores audit --slug my-chore",
            ]
        ),
    )
    chores_audit_target = p_chores_audit.add_mutually_exclusive_group(required=True)
    chores_audit_target.add_argument(
        "--all", dest="all_chores", action="store_true", help="Audit all registered chores"
    )
    chores_audit_target.add_argument("--slug", help="Audit a single chore by slug")
    p_chores_audit.set_defaults(func=lambda a: chores_audit(all_chores=a.all_chores, slug=a.slug))

    p_roles = commands.add_parser(
        "roles",
        help="List pipeline agent roles and handoff contracts",
        description="Display agent roles and pipeline dispatch history.",
        epilog=build_epilog(
            [
                "gz roles",
                "gz roles --pipeline OBPI-0.1.0-01",
                "gz roles --json",
            ]
        ),
    )
    p_roles.add_argument("--pipeline", help="Show dispatch history for an OBPI pipeline run")
    add_json_flag(p_roles)
    p_roles.set_defaults(func=lambda a: roles_cmd(pipeline=a.pipeline, as_json=a.as_json))

    # --- gz task ---
    p_task = commands.add_parser(
        "task",
        help="TASK lifecycle management commands",
        description="Manage execution-level TASK entities: list, start, complete, block, escalate.",
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

    p_implement = commands.add_parser(
        "implement",
        help="Run Gate 2 and record result",
        description="Execute Gate 2 verification and record result event.",
        epilog=build_epilog(
            [
                "gz implement --adr ADR-0.1.0",
            ]
        ),
    )
    add_adr_option(p_implement)
    p_implement.set_defaults(func=lambda a: implement_cmd(adr=a.adr))

    p_gates = commands.add_parser(
        "gates",
        help="Run lane-required gates",
        description="Execute lane-required governance gates for an ADR.",
        epilog=build_epilog(
            [
                "gz gates --adr ADR-0.1.0",
                "gz gates --adr ADR-0.1.0 --gate 2",
            ]
        ),
    )
    p_gates.add_argument(
        "--gate", dest="gate_number", type=int, help="Run a specific gate number only"
    )
    add_adr_option(p_gates)
    p_gates.set_defaults(func=lambda a: gates_cmd(gate_number=a.gate_number, adr=a.adr))

    p_attest = commands.add_parser(
        "attest",
        help="Record human attestation",
        description="Record explicit human attestation for an ADR.",
        epilog=build_epilog(
            [
                "gz attest ADR-0.1.0 --status completed",
                'gz attest ADR-0.1.0 --status partial --reason "OBPIs 3-5 deferred"',
                "gz attest ADR-0.1.0 --status completed --dry-run",
            ]
        ),
    )
    p_attest.add_argument("adr", help="ADR identifier to attest (e.g. ADR-0.0.4)")
    p_attest.add_argument(
        "--status",
        dest="attest_status",
        required=True,
        choices=["completed", "partial", "dropped"],
        help="Attestation status (completed|partial|dropped)",
    )
    p_attest.add_argument("--reason", help="Reason for partial or dropped attestation")
    add_force_flag(p_attest)
    add_dry_run_flag(p_attest)
    p_attest.set_defaults(
        func=lambda a: attest(
            adr=a.adr,
            attest_status=a.attest_status,
            reason=a.reason,
            force=a.force,
            dry_run=a.dry_run,
        )
    )

    p_validate = commands.add_parser(
        "validate",
        help="Validate governance artifacts",
        description="Check governance artifacts against schema rules.",
        epilog=build_epilog(
            [
                "gz validate --manifest --ledger",
                "gz validate --documents --surfaces",
                "gz validate --briefs --json",
            ]
        ),
    )
    p_validate.add_argument(
        "--manifest",
        dest="check_manifest",
        action="store_true",
        help="Validate .gzkit/manifest.json",
    )
    p_validate.add_argument(
        "--documents",
        dest="check_documents",
        action="store_true",
        help="Validate governance documents",
    )
    p_validate.add_argument(
        "--surfaces", dest="check_surfaces", action="store_true", help="Validate control surfaces"
    )
    p_validate.add_argument(
        "--ledger", dest="check_ledger", action="store_true", help="Validate ledger integrity"
    )
    p_validate.add_argument(
        "--instructions",
        dest="check_instructions",
        action="store_true",
        help="Validate agent instructions",
    )
    p_validate.add_argument(
        "--briefs",
        dest="check_briefs",
        action="store_true",
        help="Validate all OBPI briefs against the canonical OBPI schema",
    )
    add_json_flag(p_validate)
    p_validate.set_defaults(
        func=lambda a: validate(
            check_manifest=a.check_manifest,
            check_documents=a.check_documents,
            check_surfaces=a.check_surfaces,
            check_ledger=a.check_ledger,
            check_instructions=a.check_instructions,
            check_briefs=a.check_briefs,
            as_json=a.as_json,
        )
    )

    p_tidy = commands.add_parser(
        "tidy",
        help="Run maintenance checks and cleanup",
        description="Run maintenance checks and apply cleanup routines.",
        epilog=build_epilog(
            [
                "gz tidy --check",
                "gz tidy --fix",
                "gz tidy --fix --dry-run",
            ]
        ),
    )
    p_tidy.add_argument(
        "--check", dest="check_only", action="store_true", help="Report issues without fixing"
    )
    p_tidy.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    add_dry_run_flag(p_tidy)
    p_tidy.set_defaults(func=lambda a: tidy(check_only=a.check_only, fix=a.fix, dry_run=a.dry_run))

    commands.add_parser(
        "lint",
        help="Run lint checks",
        description="Run Ruff linter on the codebase.",
        epilog=build_epilog(
            [
                "gz lint",
            ]
        ),
    ).set_defaults(func=lambda a: lint())
    commands.add_parser(
        "format",
        help="Run formatter",
        description="Run Ruff formatter on the codebase.",
        epilog=build_epilog(
            [
                "gz format",
            ]
        ),
    ).set_defaults(func=lambda a: format_cmd())
    commands.add_parser(
        "test",
        help="Run tests",
        description="Run the unittest test suite.",
        epilog=build_epilog(
            [
                "gz test",
            ]
        ),
    ).set_defaults(func=lambda a: test())
    commands.add_parser(
        "typecheck",
        help="Run type checks",
        description="Run static type analysis with ty.",
        epilog=build_epilog(
            [
                "gz typecheck",
            ]
        ),
    ).set_defaults(func=lambda a: typecheck())
    p_check = commands.add_parser(
        "check",
        help="Run all quality checks",
        description="Run lint, format, typecheck, test, and advisory drift in sequence.",
        epilog=build_epilog(
            [
                "gz check",
                "gz check --json",
            ]
        ),
    )
    add_json_flag(p_check)
    p_check.set_defaults(func=lambda a: check(as_json=a.as_json))

    p_drift = commands.add_parser(
        "drift",
        help="Detect spec-test-code drift",
        description="Detect spec-test-code governance drift.",
        epilog=build_epilog(
            [
                "gz drift",
                "gz drift --json",
                "gz drift --plain",
                "gz drift --adr-dir path/to/adrs",
            ]
        ),
    )
    add_json_flag(p_drift)
    p_drift.add_argument(
        "--plain",
        action="store_true",
        default=False,
        help="One record per line (grep-friendly)",
    )
    p_drift.add_argument(
        "--adr-dir",
        default=None,
        help="Override ADR directory to scan (default: docs/design/adr)",
    )
    p_drift.add_argument(
        "--test-dir",
        default=None,
        help="Override test directory to scan (default: tests)",
    )
    p_drift.set_defaults(
        func=lambda a: drift_cmd(
            as_json=a.as_json,
            plain=a.plain,
            adr_dir=a.adr_dir,
            test_dir=a.test_dir,
        )
    )

    # --- gz covers ---
    p_covers = commands.add_parser(
        "covers",
        help="Report requirement coverage from @covers annotations",
        description="Report requirement coverage at ADR, OBPI, or REQ granularity.",
        epilog=build_epilog(
            [
                "gz covers",
                "gz covers ADR-0.20.0",
                "gz covers OBPI-0.20.0-01",
                "gz covers --json",
                "gz covers ADR-0.20.0 --plain",
            ]
        ),
    )
    p_covers.add_argument(
        "target",
        nargs="?",
        default=None,
        help="ADR-X.Y.Z or OBPI-X.Y.Z-NN to filter (default: all)",
    )
    add_json_flag(p_covers)
    p_covers.add_argument(
        "--plain",
        action="store_true",
        default=False,
        help="One record per line (grep-friendly)",
    )
    p_covers.add_argument(
        "--adr-dir",
        default=None,
        help="Override ADR directory to scan (default: docs/design/adr)",
    )
    p_covers.add_argument(
        "--test-dir",
        default=None,
        help="Override test directory to scan (default: tests)",
    )
    p_covers.set_defaults(
        func=lambda a: covers_cmd(
            target=a.target,
            as_json=a.as_json,
            plain=a.plain,
            adr_dir=a.adr_dir,
            test_dir=a.test_dir,
        )
    )

    p_skill = commands.add_parser(
        "skill",
        help="Skill management commands",
        description="Create, list, and audit gzkit skills.",
        epilog=build_epilog(
            [
                "gz skill list",
                "gz skill new my-skill",
                "gz skill audit",
            ]
        ),
    )
    skill_commands = p_skill.add_subparsers(dest="skill_command")
    skill_commands.required = True

    p_skill_new = skill_commands.add_parser(
        "new",
        help="Create a new skill",
        description="Scaffold a new skill directory and SKILL.md.",
        epilog=build_epilog(
            [
                "gz skill new my-skill",
                'gz skill new my-skill --description "Does something useful"',
            ]
        ),
    )
    p_skill_new.add_argument("name", help="Skill name (kebab-case)")
    p_skill_new.add_argument("--description", help="Short description of the skill")
    p_skill_new.set_defaults(func=lambda a: skill_new(name=a.name, description=a.description))

    skill_commands.add_parser(
        "list",
        help="List all skills",
        description="Display all registered skills and their status.",
        epilog=build_epilog(
            [
                "gz skill list",
            ]
        ),
    ).set_defaults(func=lambda a: skill_list())
    p_skill_audit = skill_commands.add_parser(
        "audit",
        help="Audit skill lifecycle and mirror parity",
        description="Check skill files, mirrors, and review freshness.",
        epilog=build_epilog(
            [
                "gz skill audit",
                "gz skill audit --strict",
                "gz skill audit --json",
            ]
        ),
    )
    add_json_flag(p_skill_audit)
    p_skill_audit.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as blocking failures.",
    )
    p_skill_audit.add_argument(
        "--max-review-age-days",
        type=int,
        default=DEFAULT_MAX_REVIEW_AGE_DAYS,
        help="Maximum age of last_reviewed before audit fails (default: 90).",
    )
    p_skill_audit.set_defaults(
        func=lambda a: skill_audit_cmd(
            as_json=a.as_json,
            strict=a.strict,
            max_review_age_days=a.max_review_age_days,
        )
    )

    p_interview = commands.add_parser(
        "interview",
        help="Interactive document interview",
        description="Run an interactive interview to generate a document.",
        epilog=build_epilog(
            [
                "gz interview prd",
                "gz interview adr",
                "gz interview obpi",
            ]
        ),
    )
    p_interview.add_argument(
        "document_type",
        choices=["prd", "adr", "obpi"],
        help="Document type to generate (prd|adr|obpi)",
    )
    p_interview.set_defaults(func=lambda a: interview(document_type=a.document_type))

    p_agent = commands.add_parser(
        "agent",
        help="Agent-specific operations",
        description="Agent synchronization and management commands.",
        epilog=build_epilog(
            [
                "gz agent sync control-surfaces",
            ]
        ),
    )
    agent_commands = p_agent.add_subparsers(dest="agent_command")
    agent_commands.required = True

    p_agent_sync = agent_commands.add_parser(
        "sync",
        help="Agent synchronization commands",
        description="Synchronize agent control surfaces and mirrors.",
        epilog=build_epilog(
            [
                "gz agent sync control-surfaces",
                "gz agent sync control-surfaces --dry-run",
            ]
        ),
    )
    agent_sync_commands = p_agent_sync.add_subparsers(dest="agent_sync_command")
    agent_sync_commands.required = True

    p_control_surfaces = agent_sync_commands.add_parser(
        "control-surfaces",
        help="Regenerate agent control surfaces from governance canon",
        description="Rebuild CLAUDE.md and mirrors from governance source.",
        epilog=build_epilog(
            [
                "gz agent sync control-surfaces",
                "gz agent sync control-surfaces --dry-run",
            ]
        ),
    )
    add_dry_run_flag(p_control_surfaces)
    p_control_surfaces.set_defaults(func=lambda a: sync_control_surfaces(dry_run=a.dry_run))

    # Register common flags on every subcommand so users can write
    # ``gz status --verbose`` (not only ``gz --verbose status``).
    _propagate_common_flags(parser)

    return parser


def _propagate_common_flags(parser: argparse.ArgumentParser) -> None:
    """Recursively apply ``add_common_flags`` to all nested subparsers."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for subparser in action.choices.values():
                if isinstance(subparser, argparse.ArgumentParser):
                    add_common_flags(subparser)
                    _propagate_common_flags(subparser)


_cached_parser: argparse.ArgumentParser | None = None


def _get_parser() -> argparse.ArgumentParser:
    """Return a cached argument parser (built once, reused)."""
    global _cached_parser  # noqa: PLW0603
    if _cached_parser is None:
        _cached_parser = _build_parser()
    return _cached_parser


def _apply_debug_mode() -> None:
    """Enable DEBUG-level logging and full tracebacks."""
    import logging

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(name)s: %(message)s")


def main(argv: list[str] | None = None) -> int:
    """argparse-based gz entrypoint."""
    parser = _get_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    if getattr(args, "debug", False):
        _apply_debug_mode()

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 2

    try:
        handler(args)
    except GzkitError as exc:
        if getattr(args, "debug", False):
            import sys
            import traceback

            traceback.print_exc(file=sys.stderr)
        console.print(f"[red]{exc}[/red]")
        return exit_code_for(exc)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted.[/yellow]")
        return 130
    except Exception as exc:  # noqa: BLE001 — CLI main entry point
        if getattr(args, "debug", False):
            import sys
            import traceback

            traceback.print_exc(file=sys.stderr)
        console.print(f"[red]Unexpected error: {exc}[/red]")
        return exit_code_for(exc)
    else:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
