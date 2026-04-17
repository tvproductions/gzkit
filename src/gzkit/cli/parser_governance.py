"""Governance lifecycle subparser registrations for gz CLI.

Registers: init, prd, constitute, specify, plan, state, status, closeout,
patch, audit, attest, implement, gates, migrate-semver, register-adrs, roles.

Command handlers are resolved on demand via ``_lazy`` so ``gz --help``
avoids pulling heavy handler dependencies. Each handler's module lives in
``_LAZY_HANDLERS``; ``_lazy`` imports the module on first call and caches
the resolved callable.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from importlib import import_module
from typing import Any

from gzkit.cli.helpers import (
    add_adr_option,
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    add_table_flag,
    build_epilog,
)

_LAZY_HANDLERS: dict[str, str] = {
    "attest": "gzkit.commands.attest",
    "audit_cmd": "gzkit.commands.audit_cmd",
    "closeout_cmd": "gzkit.commands.closeout",
    "gates_cmd": "gzkit.commands.gates",
    "implement_cmd": "gzkit.commands.gates",
    "constitute": "gzkit.commands.init_cmd",
    "init": "gzkit.commands.init_cmd",
    "prd": "gzkit.commands.init_cmd",
    "patch_release_cmd": "gzkit.commands.patch_release",
    "persona_drift_cmd": "gzkit.commands.personas",
    "personas_list_cmd": "gzkit.commands.personas",
    "plan_cmd": "gzkit.commands.plan",
    "plan_audit_cmd": "gzkit.commands.plan_audit_cmd",
    "migrate_semver": "gzkit.commands.register",
    "register_adrs": "gzkit.commands.register",
    "roles_cmd": "gzkit.commands.roles",
    "specify": "gzkit.commands.specify_cmd",
    "state": "gzkit.commands.state",
    "status": "gzkit.commands.status",
}

_HANDLER_CACHE: dict[str, Callable[..., Any]] = {}


def _lazy(name: str) -> Callable[..., Any]:
    cached = _HANDLER_CACHE.get(name)
    if cached is not None:
        return cached
    module_path = _LAZY_HANDLERS[name]
    impl = getattr(import_module(module_path), name)
    _HANDLER_CACHE[name] = impl
    return impl


def _state_handler(a: argparse.Namespace) -> None:
    """Route gz state to repair or query mode."""
    if a.repair:
        from gzkit.commands.state import state_repair  # noqa: PLC0415

        state_repair(as_json=a.as_json)
    else:
        _lazy("state")(as_json=a.as_json, blocked=a.blocked, ready=a.ready)


def _closeout_dispatch(a: argparse.Namespace) -> None:
    """Route gz closeout to ceremony or standard closeout."""
    ceremony_flags = (
        a.ceremony
        or a.ceremony_next
        or a.ceremony_status
        or a.ceremony_attest
        or a.ceremony_pause
        or a.ceremony_restart
    )
    if ceremony_flags:
        from gzkit.commands.closeout_ceremony import ceremony_cmd  # noqa: PLC0415

        ceremony_cmd(
            adr=a.adr,
            as_json=a.as_json,
            ceremony_next=a.ceremony_next,
            ceremony_status=a.ceremony_status,
            ceremony_attest=a.ceremony_attest,
            ceremony_pause=a.ceremony_pause,
            ceremony_restart=a.ceremony_restart,
        )
    else:
        _lazy("closeout_cmd")(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run)


def register_governance_parsers(commands: argparse._SubParsersAction) -> None:  # noqa: PLR0915
    """Register governance lifecycle subcommands on *commands*."""
    p_init = commands.add_parser(
        "init",
        help="Initialize gzkit in the current project",
        description=(
            "Initialize gzkit governance scaffolding and Python project skeleton. "
            "Re-running on an initialized project repairs missing artifacts."
        ),
        epilog=build_epilog(
            [
                "gz init",
                "gz init --mode heavy",
                "gz init --no-skeleton",
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
    p_init.add_argument(
        "--no-skeleton",
        action="store_true",
        default=False,
        help="Skip Python project skeleton (pyproject.toml, src/, tests/)",
    )
    add_force_flag(p_init)
    add_dry_run_flag(p_init)
    p_init.set_defaults(
        func=lambda a: _lazy("init")(
            mode=a.mode, force=a.force, dry_run=a.dry_run, no_skeleton=a.no_skeleton
        )
    )

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
    p_prd.set_defaults(func=lambda a: _lazy("prd")(name=a.name, title=a.title, dry_run=a.dry_run))

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
        func=lambda a: _lazy("constitute")(name=a.name, title=a.title, dry_run=a.dry_run)
    )

    p_specify = commands.add_parser(
        "specify",
        help="Create a new OBPI",
        description="Create a new OBPI brief linked to a parent ADR.",
        epilog=build_epilog(
            [
                "gz specify my-feature --parent ADR-0.1.0",
                "gz specify my-feature --parent ADR-0.1.0 --author",
                "gz specify my-feature --parent ADR-0.1.0 --item 3 --lane heavy",
                "gz specify my-feature --parent ADR-0.1.0 --dry-run",
            ]
        ),
    )
    p_specify.add_argument("name", help="OBPI slug name (kebab-case)")
    p_specify.add_argument("--parent", required=True, help="Parent ADR identifier (e.g. ADR-0.0.4)")
    p_specify.add_argument("--item", type=int, default=1, help="OBPI item number within parent ADR")
    p_specify.add_argument(
        "--lane",
        choices=["lite", "heavy"],
        default=None,
        help="Governance lane override (default: read from ADR WBS table)",
    )
    p_specify.add_argument(
        "--author",
        action="store_true",
        help="Run the authored brief pass and fail unless --authored validation succeeds.",
    )
    p_specify.add_argument("--title", help="OBPI title override")
    add_dry_run_flag(p_specify)
    p_specify.set_defaults(
        func=lambda a: _lazy("specify")(
            name=a.name,
            parent=a.parent,
            item=a.item,
            lane=a.lane,
            title=a.title,
            author=a.author,
            dry_run=a.dry_run,
        )
    )

    p_plan = commands.add_parser(
        "plan",
        help="ADR planning commands",
        description="Create ADRs and run plan-audit checks.",
        epilog=build_epilog(
            [
                "gz plan create my-feature --semver 0.1.0 --lane lite",
                "gz plan audit OBPI-0.1.0-01",
            ]
        ),
    )
    plan_commands = p_plan.add_subparsers(dest="plan_command")
    plan_commands.required = True

    p_plan_create = plan_commands.add_parser(
        "create",
        help="Create a new ADR",
        description="Create a new Architecture Decision Record with scoring.",
        epilog=build_epilog(
            [
                "gz plan create my-feature --semver 0.1.0 --lane lite",
                'gz plan create my-feature --semver 0.2.0 --lane heavy --title "My Feature"',
                "gz plan create my-feature --semver 0.1.0 --dry-run",
            ]
        ),
    )
    p_plan_create.add_argument("name", help="ADR slug name (kebab-case)")
    p_plan_create.add_argument(
        "--obpi", dest="parent_obpi", help="Parent OBPI identifier for traceability"
    )
    p_plan_create.add_argument(
        "--semver", default="0.1.0", help="Semantic version for the ADR (X.Y.Z)"
    )
    p_plan_create.add_argument(
        "--lane", choices=["lite", "heavy"], default="lite", help="Governance lane (lite|heavy)"
    )
    p_plan_create.add_argument("--title", help="ADR title override")
    p_plan_create.add_argument(
        "--score-data-state", type=int, choices=[0, 1, 2], help="Data-state dimension score (0-2)"
    )
    p_plan_create.add_argument(
        "--score-logic-engine",
        type=int,
        choices=[0, 1, 2],
        help="Logic-engine dimension score (0-2)",
    )
    p_plan_create.add_argument(
        "--score-interface", type=int, choices=[0, 1, 2], help="Interface dimension score (0-2)"
    )
    p_plan_create.add_argument(
        "--score-observability",
        type=int,
        choices=[0, 1, 2],
        help="Observability dimension score (0-2)",
    )
    p_plan_create.add_argument(
        "--score-lineage", type=int, choices=[0, 1, 2], help="Lineage dimension score (0-2)"
    )
    p_plan_create.add_argument(
        "--split-single-narrative",
        action="store_true",
        help="Apply single-narrative split heuristic",
    )
    p_plan_create.add_argument(
        "--split-surface-boundary",
        action="store_true",
        help="Apply surface-boundary split heuristic",
    )
    p_plan_create.add_argument(
        "--split-state-anchor", action="store_true", help="Apply state-anchor split heuristic"
    )
    p_plan_create.add_argument(
        "--split-testability-ceiling",
        action="store_true",
        help="Apply testability-ceiling split heuristic",
    )
    p_plan_create.add_argument(
        "--baseline-selected", type=int, help="Selected baseline index for scoring"
    )
    add_dry_run_flag(p_plan_create)
    p_plan_create.set_defaults(
        func=lambda a: _lazy("plan_cmd")(
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

    p_plan_audit = plan_commands.add_parser(
        "audit",
        help="Structural prerequisite check for plan-OBPI alignment",
        description="Run deterministic checks that ADR, brief, and plan files exist and align.",
        epilog=build_epilog(
            [
                "gz plan audit OBPI-0.1.0-01",
                "gz plan audit OBPI-0.1.0-01 --json",
            ]
        ),
    )
    p_plan_audit.add_argument("obpi_id", help="OBPI identifier (e.g. OBPI-0.1.0-01)")
    add_json_flag(p_plan_audit)
    p_plan_audit.set_defaults(
        func=lambda a: _lazy("plan_audit_cmd")(obpi_id=a.obpi_id, as_json=a.as_json)
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
                "gz state --repair",
                "gz state --repair --json",
            ]
        ),
    )
    add_json_flag(p_state)
    p_state.add_argument("--blocked", action="store_true", help="Show only blocked artifacts")
    p_state.add_argument(
        "--ready", action="store_true", help="Show only ready-to-proceed artifacts"
    )
    p_state.add_argument(
        "--repair",
        action="store_true",
        help="Force-reconcile all frontmatter status from ledger-derived state",
    )

    p_state.set_defaults(func=lambda a: _state_handler(a))

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
        func=lambda a: _lazy("status")(as_json=a.as_json, show_gates=a.show_gates, as_table=a.table)
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
                "gz closeout ADR-0.1.0 --ceremony",
                "gz closeout ADR-0.1.0 --ceremony --next",
                'gz closeout ADR-0.1.0 --ceremony --attest "Completed"',
            ]
        ),
    )
    p_closeout.add_argument("adr", help="ADR identifier to close out (e.g. ADR-0.0.4)")
    add_json_flag(p_closeout)
    add_dry_run_flag(p_closeout)
    p_closeout.add_argument(
        "--ceremony",
        action="store_true",
        default=False,
        help="Run interactive ceremony with deterministic step sequencing",
    )
    p_closeout.add_argument(
        "--next",
        dest="ceremony_next",
        action="store_true",
        default=False,
        help="Advance ceremony to next step (requires --ceremony)",
    )
    p_closeout.add_argument(
        "--ceremony-status",
        dest="ceremony_status",
        action="store_true",
        default=False,
        help="Show current ceremony step (requires --ceremony)",
    )
    p_closeout.add_argument(
        "--attest",
        dest="ceremony_attest",
        default=None,
        metavar="TEXT",
        help='Record attestation at step 6 (e.g. --attest "Completed")',
    )
    p_closeout.add_argument(
        "--pause",
        dest="ceremony_pause",
        action="store_true",
        default=False,
        help="Pause ceremony for revise-and-resubmit",
    )
    p_closeout.add_argument(
        "--restart",
        dest="ceremony_restart",
        action="store_true",
        default=False,
        help="Restart ceremony (new attempt, fresh from Step 1)",
    )

    p_closeout.set_defaults(func=lambda a: _closeout_dispatch(a))

    p_patch = commands.add_parser(
        "patch",
        help="Patch release ceremony commands",
        description="GHI-driven patch release ceremony.",
        epilog=build_epilog(
            [
                "gz patch release --dry-run",
                "gz patch release --full",
                "gz patch release --json",
            ]
        ),
    )
    patch_commands = p_patch.add_subparsers(dest="patch_command")
    patch_commands.required = True

    p_patch_release = patch_commands.add_parser(
        "release",
        help="Run the patch release ceremony",
        description=(
            "Execute the GHI-driven patch release ceremony. "
            "With --full: bump, author release notes, commit, push "
            "(with lint/test gates), and create the GitHub release "
            "as one transaction."
        ),
        epilog=build_epilog(
            [
                "gz patch release --dry-run",
                "gz patch release --full",
                "gz patch release --json",
            ]
        ),
    )
    add_dry_run_flag(p_patch_release)
    add_json_flag(p_patch_release)
    p_patch_release.add_argument(
        "--full",
        action="store_true",
        help="Execute the full ceremony: bump, release notes, commit, push, gh release",
    )
    p_patch_release.set_defaults(
        func=lambda a: _lazy("patch_release_cmd")(dry_run=a.dry_run, as_json=a.as_json, full=a.full)
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
    p_audit.set_defaults(
        func=lambda a: _lazy("audit_cmd")(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run)
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
    p_implement.set_defaults(func=lambda a: _lazy("implement_cmd")(adr=a.adr))

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
    p_gates.set_defaults(func=lambda a: _lazy("gates_cmd")(gate_number=a.gate_number, adr=a.adr))

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
        func=lambda a: _lazy("attest")(
            adr=a.adr,
            attest_status=a.attest_status,
            reason=a.reason,
            force=a.force,
            dry_run=a.dry_run,
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
    p_migrate.set_defaults(func=lambda a: _lazy("migrate_semver")(dry_run=a.dry_run))

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
        help="Register only pool ADRs",
    )
    p_register_adrs.add_argument(
        "--all",
        dest="pool_only",
        action="store_false",
        default=False,
        help="Register all ADRs — pool + versioned (default)",
    )
    add_dry_run_flag(p_register_adrs)
    p_register_adrs.set_defaults(
        func=lambda a: _lazy("register_adrs")(
            lane=a.lane,
            pool_only=a.pool_only,
            dry_run=a.dry_run,
            targets=a.targets,
        )
    )

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
    p_roles.set_defaults(func=lambda a: _lazy("roles_cmd")(pipeline=a.pipeline, as_json=a.as_json))

    p_personas = commands.add_parser(
        "personas",
        help="Persona identity frame commands",
        description="Inspect agent persona definitions (read-only).",
        epilog=build_epilog(
            [
                "gz personas list",
                "gz personas list --json",
            ]
        ),
    )
    personas_commands = p_personas.add_subparsers(dest="personas_command")
    personas_commands.required = True

    p_personas_list = personas_commands.add_parser(
        "list",
        help="List agent personas",
        description="Enumerate persona files from .gzkit/personas/ (read-only).",
        epilog=build_epilog(
            [
                "gz personas list",
                "gz personas list --json",
            ]
        ),
    )
    add_json_flag(p_personas_list)
    p_personas_list.set_defaults(func=lambda a: _lazy("personas_list_cmd")(as_json=a.as_json))

    p_personas_drift = personas_commands.add_parser(
        "drift",
        help="Report persona trait adherence from behavioral proxies",
        description=(
            "Scan local governance artifacts for evidence of trait-aligned "
            "behavior. Reports per-trait pass/fail for each persona using "
            "behavioral proxies only — no activation-space measurement. "
            "Exit code 0 when no drift detected, exit code 3 on policy breach."
        ),
        epilog=build_epilog(
            [
                "gz personas drift",
                "gz personas drift --json",
                "gz personas drift --persona implementer",
            ]
        ),
    )
    p_personas_drift.add_argument(
        "--persona",
        default=None,
        help="Evaluate only the named persona (default: all)",
    )
    add_json_flag(p_personas_drift)
    p_personas_drift.set_defaults(
        func=lambda a: _lazy("persona_drift_cmd")(persona=a.persona, as_json=a.as_json)
    )
