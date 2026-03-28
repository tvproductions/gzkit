"""Governance lifecycle subparser registrations for gz CLI.

Registers: init, prd, constitute, specify, plan, state, status, closeout,
audit, attest, implement, gates, migrate-semver, register-adrs, roles.
"""

import argparse

from gzkit.cli.helpers import (
    add_adr_option,
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    add_table_flag,
    build_epilog,
)
from gzkit.commands.attest import attest
from gzkit.commands.audit_cmd import audit_cmd
from gzkit.commands.closeout import closeout_cmd
from gzkit.commands.gates import gates_cmd, implement_cmd
from gzkit.commands.init_cmd import constitute, init, prd
from gzkit.commands.plan import plan_cmd
from gzkit.commands.register import migrate_semver, register_adrs
from gzkit.commands.roles import roles_cmd
from gzkit.commands.specify_cmd import specify
from gzkit.commands.state import state
from gzkit.commands.status import status


def register_governance_parsers(commands: argparse._SubParsersAction) -> None:
    """Register governance lifecycle subcommands on *commands*."""
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
