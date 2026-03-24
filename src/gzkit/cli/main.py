"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse

from gzkit import __version__
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
    GzCliError,
    console,
    ensure_initialized,  # noqa: F401 — test-mock compat
    get_project_root,  # noqa: F401 — test-mock compat
    load_manifest,  # noqa: F401 — test-mock compat
    resolve_adr_file,  # noqa: F401 — backward-compat re-export
    resolve_target_adr,  # noqa: F401 — test-mock compat
)
from gzkit.commands.config_paths import check_config_paths_cmd
from gzkit.commands.gates import (
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
from gzkit.commands.obpi_cmd import obpi_emit_receipt_cmd, obpi_pipeline_cmd, obpi_validate_cmd
from gzkit.commands.parity import parity_check_cmd
from gzkit.commands.plan import plan_cmd
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
from gzkit.commands.tidy import sync_control_surfaces, tidy
from gzkit.commands.validate_cmd import validate
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
    parser.add_argument("--lint", dest="run_lint_gate", action="store_true", default=True)
    parser.add_argument("--no-lint", dest="run_lint_gate", action="store_false")
    parser.add_argument("--test", dest="run_test_gate", action="store_true", default=True)
    parser.add_argument("--no-test", dest="run_test_gate", action="store_false")
    parser.add_argument("--auto-add", dest="auto_add", action="store_true", default=True)
    parser.add_argument("--no-auto-add", dest="auto_add", action="store_false")
    parser.add_argument("--push", dest="allow_push", action="store_true", default=True)
    parser.add_argument("--no-push", dest="allow_push", action="store_false")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")


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

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    p_init = commands.add_parser("init", help="Initialize gzkit in the current project")
    p_init.add_argument("--mode", choices=["lite", "heavy"], default="lite")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--dry-run", action="store_true")
    p_init.set_defaults(func=lambda a: init(mode=a.mode, force=a.force, dry_run=a.dry_run))

    p_prd = commands.add_parser("prd", help="Create a new PRD")
    p_prd.add_argument("name")
    p_prd.add_argument("--title")
    p_prd.add_argument("--dry-run", action="store_true")
    p_prd.set_defaults(func=lambda a: prd(name=a.name, title=a.title, dry_run=a.dry_run))

    p_constitute = commands.add_parser("constitute", help="Create a new constitution")
    p_constitute.add_argument("name")
    p_constitute.add_argument("--title")
    p_constitute.add_argument("--dry-run", action="store_true")
    p_constitute.set_defaults(
        func=lambda a: constitute(name=a.name, title=a.title, dry_run=a.dry_run)
    )

    p_specify = commands.add_parser("specify", help="Create a new OBPI")
    p_specify.add_argument("name")
    p_specify.add_argument("--parent", required=True)
    p_specify.add_argument("--item", type=int, default=1)
    p_specify.add_argument("--lane", choices=["lite", "heavy"], default="lite")
    p_specify.add_argument("--title")
    p_specify.add_argument("--dry-run", action="store_true")
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

    p_plan = commands.add_parser("plan", help="Create a new ADR")
    p_plan.add_argument("name")
    p_plan.add_argument("--obpi", dest="parent_obpi")
    p_plan.add_argument("--semver", default="0.1.0")
    p_plan.add_argument("--lane", choices=["lite", "heavy"], default="lite")
    p_plan.add_argument("--title")
    p_plan.add_argument("--score-data-state", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-logic-engine", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-interface", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-observability", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-lineage", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--split-single-narrative", action="store_true")
    p_plan.add_argument("--split-surface-boundary", action="store_true")
    p_plan.add_argument("--split-state-anchor", action="store_true")
    p_plan.add_argument("--split-testability-ceiling", action="store_true")
    p_plan.add_argument("--baseline-selected", type=int)
    p_plan.add_argument("--dry-run", action="store_true")
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

    p_state = commands.add_parser("state", help="Query ledger state and relationships")
    p_state.add_argument("--json", dest="as_json", action="store_true")
    p_state.add_argument("--blocked", action="store_true")
    p_state.add_argument("--ready", action="store_true")
    p_state.set_defaults(func=lambda a: state(as_json=a.as_json, blocked=a.blocked, ready=a.ready))

    p_status = commands.add_parser("status", help="Show OBPI progress and ADR lifecycle status")
    p_status.add_argument("--json", dest="as_json", action="store_true")
    p_status.add_argument(
        "--table",
        action="store_true",
        help="Show a tabular ADR summary (ADR, lifecycle, lane, OBPI, QC).",
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
        "closeout", help="Initiate closeout mode and record closeout event"
    )
    p_closeout.add_argument("adr")
    p_closeout.add_argument("--json", dest="as_json", action="store_true")
    p_closeout.add_argument("--dry-run", action="store_true")
    p_closeout.set_defaults(
        func=lambda a: closeout_cmd(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run)
    )

    p_audit = commands.add_parser("audit", help="Run ADR audit routine and persist proof artifacts")
    p_audit.add_argument("adr")
    p_audit.add_argument("--json", dest="as_json", action="store_true")
    p_audit.add_argument("--dry-run", action="store_true")
    p_audit.set_defaults(func=lambda a: audit_cmd(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run))

    p_adr = commands.add_parser("adr", help="ADR-focused governance commands")
    adr_commands = p_adr.add_subparsers(dest="adr_command")
    adr_commands.required = True

    p_adr_status = adr_commands.add_parser("status", help="Show focused OBPI progress for one ADR")
    p_adr_status.add_argument("adr")
    p_adr_status.add_argument("--json", dest="as_json", action="store_true")
    p_adr_status.add_argument(
        "--show-gates",
        action="store_true",
        help="Show detailed gate-level QC breakdown (internal diagnostics).",
    )
    p_adr_status.set_defaults(
        func=lambda a: adr_status_cmd(adr=a.adr, as_json=a.as_json, show_gates=a.show_gates)
    )

    p_adr_report = adr_commands.add_parser(
        "report", help="Deterministic tabular report (summary or single ADR)"
    )
    p_adr_report.add_argument("adr", nargs="?", default=None)
    p_adr_report.set_defaults(func=lambda a: adr_report_cmd(adr=a.adr))

    p_adr_promote = adr_commands.add_parser(
        "promote", help="Promote a pool ADR into canonical ADR package structure"
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
    p_adr_promote.add_argument("--json", dest="as_json", action="store_true")
    p_adr_promote.add_argument("--dry-run", action="store_true")
    p_adr_promote.add_argument(
        "--force",
        action="store_true",
        help="Override scaffold quality gate (briefs contain only template defaults)",
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
        "evaluate", help="Evaluate ADR/OBPI quality (deterministic scoring)"
    )
    p_adr_eval.add_argument("adr_id", help="ADR identifier (e.g., ADR-0.19.0)")
    p_adr_eval.add_argument("--json", dest="as_json", action="store_true")
    p_adr_eval.add_argument(
        "--no-scorecard", dest="write_scorecard", action="store_false", default=True
    )
    p_adr_eval.set_defaults(
        func=lambda a: adr_eval_cmd(
            adr_id=a.adr_id,
            as_json=a.as_json,
            write_scorecard=a.write_scorecard,
        )
    )

    p_adr_audit_check = adr_commands.add_parser(
        "audit-check", help="Verify linked OBPIs are complete with evidence"
    )
    p_adr_audit_check.add_argument("adr")
    p_adr_audit_check.add_argument("--json", dest="as_json", action="store_true")
    p_adr_audit_check.set_defaults(func=lambda a: adr_audit_check(adr=a.adr, as_json=a.as_json))

    p_adr_covers_check = adr_commands.add_parser(
        "covers-check", help="Verify @covers traceability for ADR, OBPIs, and REQ acceptance IDs"
    )
    p_adr_covers_check.add_argument("adr")
    p_adr_covers_check.add_argument("--json", dest="as_json", action="store_true")
    p_adr_covers_check.set_defaults(func=lambda a: adr_covers_check(adr=a.adr, as_json=a.as_json))

    p_adr_emit = adr_commands.add_parser(
        "emit-receipt", help="Emit completed/validated receipt event for an ADR"
    )
    p_adr_emit.add_argument("adr")
    p_adr_emit.add_argument(
        "--event", dest="receipt_event", required=True, choices=["completed", "validated"]
    )
    p_adr_emit.add_argument("--attestor", required=True)
    p_adr_emit.add_argument("--evidence-json")
    p_adr_emit.add_argument("--dry-run", action="store_true")
    p_adr_emit.set_defaults(
        func=lambda a: adr_emit_receipt_cmd(
            adr=a.adr,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
            dry_run=a.dry_run,
        )
    )

    p_obpi = commands.add_parser("obpi", help="OBPI-focused governance commands")
    obpi_commands = p_obpi.add_subparsers(dest="obpi_command")
    obpi_commands.required = True

    p_obpi_emit = obpi_commands.add_parser(
        "emit-receipt", help="Emit completed/validated receipt event for an OBPI"
    )
    p_obpi_emit.add_argument("obpi")
    p_obpi_emit.add_argument(
        "--event", dest="receipt_event", required=True, choices=["completed", "validated"]
    )
    p_obpi_emit.add_argument("--attestor", required=True)
    p_obpi_emit.add_argument("--evidence-json")
    p_obpi_emit.add_argument("--dry-run", action="store_true")
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
        "status", help="Show focused runtime status for one OBPI"
    )
    p_obpi_status.add_argument("obpi")
    p_obpi_status.add_argument("--json", dest="as_json", action="store_true")
    p_obpi_status.set_defaults(func=lambda a: obpi_status_cmd(obpi=a.obpi, as_json=a.as_json))

    p_obpi_pipeline = obpi_commands.add_parser(
        "pipeline", help="Launch the OBPI pipeline runtime surface"
    )
    p_obpi_pipeline.add_argument("obpi", nargs="?", default="")
    p_obpi_pipeline.add_argument(
        "--from", dest="start_from", choices=["verify", "ceremony", "sync"]
    )
    p_obpi_pipeline.add_argument(
        "--attestor",
        help="Attestor identity for Stage 5 (e.g. human:<name> or agent:<name>)",
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
        "reconcile", help="Fail-closed runtime reconciliation for one OBPI"
    )
    p_obpi_reconcile.add_argument("obpi")
    p_obpi_reconcile.add_argument("--json", dest="as_json", action="store_true")
    p_obpi_reconcile.set_defaults(func=lambda a: obpi_reconcile_cmd(obpi=a.obpi, as_json=a.as_json))

    p_obpi_validate = obpi_commands.add_parser(
        "validate", help="Validate OBPI brief(s) for completion readiness"
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

    p_check_paths = commands.add_parser(
        "check-config-paths", help="Validate config/manifest paths are coherent"
    )
    p_check_paths.add_argument("--json", dest="as_json", action="store_true")
    p_check_paths.set_defaults(func=lambda a: check_config_paths_cmd(as_json=a.as_json))

    p_cli = commands.add_parser("cli", help="CLI governance commands")
    cli_commands = p_cli.add_subparsers(dest="cli_command")
    cli_commands.required = True
    p_cli_audit = cli_commands.add_parser("audit", help="Audit CLI docs/manpage coverage")
    p_cli_audit.add_argument("--json", dest="as_json", action="store_true")
    p_cli_audit.set_defaults(func=lambda a: cli_audit_cmd(as_json=a.as_json))

    p_parity = commands.add_parser("parity", help="Parity governance commands")
    parity_commands = p_parity.add_subparsers(dest="parity_command")
    parity_commands.required = True
    p_parity_check = parity_commands.add_parser(
        "check", help="Run deterministic parity regression checks"
    )
    p_parity_check.add_argument("--json", dest="as_json", action="store_true")
    p_parity_check.set_defaults(func=lambda a: parity_check_cmd(as_json=a.as_json))

    p_readiness = commands.add_parser("readiness", help="Agent readiness governance commands")
    readiness_commands = p_readiness.add_subparsers(dest="readiness_command")
    readiness_commands.required = True
    p_readiness_audit = readiness_commands.add_parser(
        "audit", help="Audit readiness across disciplines and primitives"
    )
    p_readiness_audit.add_argument("--json", dest="as_json", action="store_true")
    p_readiness_audit.set_defaults(func=lambda a: readiness_audit_cmd(as_json=a.as_json))
    p_readiness_eval = readiness_commands.add_parser(
        "evaluate", help="Run instruction eval suite with positive/negative controls"
    )
    p_readiness_eval.add_argument("--json", dest="as_json", action="store_true")
    p_readiness_eval.set_defaults(func=lambda a: readiness_eval_cmd(as_json=a.as_json))

    p_git_sync = commands.add_parser("git-sync", help="Sync branch with guarded ritual")
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

    p_migrate = commands.add_parser("migrate-semver", help="Record SemVer ID rename events")
    p_migrate.add_argument("--dry-run", action="store_true")
    p_migrate.set_defaults(func=lambda a: migrate_semver(dry_run=a.dry_run))

    p_register_adrs = commands.add_parser(
        "register-adrs",
        help="Register ADR packages that exist in canon but are missing from ledger state",
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
    p_register_adrs.add_argument("--dry-run", action="store_true")
    p_register_adrs.set_defaults(
        func=lambda a: register_adrs(
            lane=a.lane,
            pool_only=a.pool_only,
            dry_run=a.dry_run,
            targets=a.targets,
        )
    )

    p_chores = commands.add_parser("chores", help="Chore registry and execution commands")
    chores_commands = p_chores.add_subparsers(dest="chores_command")
    chores_commands.required = True

    chores_commands.add_parser("list", help="List chores from registry").set_defaults(
        func=lambda a: chores_list()
    )

    p_chores_show = chores_commands.add_parser("show", help="Display CHORE.md for one chore")
    p_chores_show.add_argument("slug")
    p_chores_show.set_defaults(func=lambda a: chores_show(slug=a.slug))

    p_chores_plan = chores_commands.add_parser("plan", help="Show plan details for one chore")
    p_chores_plan.add_argument("slug")
    p_chores_plan.set_defaults(func=lambda a: chores_plan(slug=a.slug))

    p_chores_advise = chores_commands.add_parser(
        "advise",
        help="Dry-run criteria and report status",
    )
    p_chores_advise.add_argument("slug")
    p_chores_advise.set_defaults(func=lambda a: chores_advise(slug=a.slug))

    p_chores_run = chores_commands.add_parser("run", help="Execute one chore by slug")
    p_chores_run.add_argument("slug")
    p_chores_run.set_defaults(func=lambda a: chores_run(slug=a.slug))

    p_chores_audit = chores_commands.add_parser("audit", help="Audit chore log presence")
    chores_audit_target = p_chores_audit.add_mutually_exclusive_group(required=True)
    chores_audit_target.add_argument("--all", dest="all_chores", action="store_true")
    chores_audit_target.add_argument("--slug")
    p_chores_audit.set_defaults(func=lambda a: chores_audit(all_chores=a.all_chores, slug=a.slug))

    p_roles = commands.add_parser("roles", help="List pipeline agent roles and handoff contracts")
    p_roles.add_argument("--pipeline", help="Show dispatch history for an OBPI pipeline run")
    p_roles.add_argument("--json", dest="as_json", action="store_true")
    p_roles.set_defaults(func=lambda a: roles_cmd(pipeline=a.pipeline, as_json=a.as_json))

    p_implement = commands.add_parser("implement", help="Run Gate 2 and record result")
    p_implement.add_argument("--adr")
    p_implement.set_defaults(func=lambda a: implement_cmd(adr=a.adr))

    p_gates = commands.add_parser("gates", help="Run lane-required gates")
    p_gates.add_argument("--gate", dest="gate_number", type=int)
    p_gates.add_argument("--adr")
    p_gates.set_defaults(func=lambda a: gates_cmd(gate_number=a.gate_number, adr=a.adr))

    p_attest = commands.add_parser("attest", help="Record human attestation")
    p_attest.add_argument("adr")
    p_attest.add_argument(
        "--status",
        dest="attest_status",
        required=True,
        choices=["completed", "partial", "dropped"],
    )
    p_attest.add_argument("--reason")
    p_attest.add_argument("--force", action="store_true")
    p_attest.add_argument("--dry-run", action="store_true")
    p_attest.set_defaults(
        func=lambda a: attest(
            adr=a.adr,
            attest_status=a.attest_status,
            reason=a.reason,
            force=a.force,
            dry_run=a.dry_run,
        )
    )

    p_validate = commands.add_parser("validate", help="Validate governance artifacts")
    p_validate.add_argument("--manifest", dest="check_manifest", action="store_true")
    p_validate.add_argument("--documents", dest="check_documents", action="store_true")
    p_validate.add_argument("--surfaces", dest="check_surfaces", action="store_true")
    p_validate.add_argument("--ledger", dest="check_ledger", action="store_true")
    p_validate.add_argument("--instructions", dest="check_instructions", action="store_true")
    p_validate.add_argument(
        "--briefs",
        dest="check_briefs",
        action="store_true",
        help="Validate all OBPI briefs against the canonical OBPI schema",
    )
    p_validate.add_argument("--json", dest="as_json", action="store_true")
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

    p_tidy = commands.add_parser("tidy", help="Run maintenance checks and cleanup")
    p_tidy.add_argument("--check", dest="check_only", action="store_true")
    p_tidy.add_argument("--fix", action="store_true")
    p_tidy.add_argument("--dry-run", action="store_true")
    p_tidy.set_defaults(func=lambda a: tidy(check_only=a.check_only, fix=a.fix, dry_run=a.dry_run))

    commands.add_parser("lint", help="Run lint checks").set_defaults(func=lambda a: lint())
    commands.add_parser("format", help="Run formatter").set_defaults(func=lambda a: format_cmd())
    commands.add_parser("test", help="Run tests").set_defaults(func=lambda a: test())
    commands.add_parser("typecheck", help="Run type checks").set_defaults(
        func=lambda a: typecheck()
    )
    commands.add_parser("check", help="Run all quality checks").set_defaults(func=lambda a: check())

    p_skill = commands.add_parser("skill", help="Skill management commands")
    skill_commands = p_skill.add_subparsers(dest="skill_command")
    skill_commands.required = True

    p_skill_new = skill_commands.add_parser("new", help="Create a new skill")
    p_skill_new.add_argument("name")
    p_skill_new.add_argument("--description")
    p_skill_new.set_defaults(func=lambda a: skill_new(name=a.name, description=a.description))

    skill_commands.add_parser("list", help="List all skills").set_defaults(
        func=lambda a: skill_list()
    )
    p_skill_audit = skill_commands.add_parser(
        "audit",
        help="Audit skill lifecycle and mirror parity",
    )
    p_skill_audit.add_argument("--json", action="store_true", dest="as_json")
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

    p_interview = commands.add_parser("interview", help="Interactive document interview")
    p_interview.add_argument("document_type", choices=["prd", "adr", "obpi"])
    p_interview.set_defaults(func=lambda a: interview(document_type=a.document_type))

    p_agent = commands.add_parser("agent", help="Agent-specific operations")
    agent_commands = p_agent.add_subparsers(dest="agent_command")
    agent_commands.required = True

    p_agent_sync = agent_commands.add_parser("sync", help="Agent synchronization commands")
    agent_sync_commands = p_agent_sync.add_subparsers(dest="agent_sync_command")
    agent_sync_commands.required = True

    p_control_surfaces = agent_sync_commands.add_parser(
        "control-surfaces",
        help="Regenerate agent control surfaces from governance canon",
    )
    p_control_surfaces.add_argument("--dry-run", action="store_true")
    p_control_surfaces.set_defaults(func=lambda a: sync_control_surfaces(dry_run=a.dry_run))

    return parser


_cached_parser: argparse.ArgumentParser | None = None


def _get_parser() -> argparse.ArgumentParser:
    """Return a cached argument parser (built once, reused)."""
    global _cached_parser  # noqa: PLW0603
    if _cached_parser is None:
        _cached_parser = _build_parser()
    return _cached_parser


def main(argv: list[str] | None = None) -> int:
    """argparse-based gz entrypoint."""
    parser = _get_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 2

    try:
        handler(args)
        return 0
    except GzCliError as exc:
        console.print(f"[red]{exc}[/red]")
        return 2
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted.[/yellow]")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
