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

from gzkit.cli.helpers import (
    add_adr_option,
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    add_table_flag,
    build_epilog,
)
from gzkit.cli.parser_handler_manifest import _lazy


def _nonblank_target(value: str) -> str:
    """Argparse type: reject a blank/whitespace ``--target`` at the parse boundary.

    ``required=True`` only requires the option to be present, not non-empty; an empty
    target books an anonymous, unaccountable airlock transit and glob-selects an
    unrelated ADR (Codex Step-4b, GHI #678). The handler re-checks defensively.
    """
    if not value.strip():
        raise argparse.ArgumentTypeError("must name a non-empty file or region")
    return value


class _SingleValueAction(argparse.Action):
    """Reject a repeated option at parse time instead of silently keeping the last.

    argparse's default scalar action collapses repeated occurrences to the final
    value, which lets an earlier value be silently overwritten. For ``permitted-entry
    --repair`` that is a smuggling bypass — ``--repair <BEYOND> --repair ""`` would
    drop the beyond-ceiling intent past classification (GHI #678, Codex Step-4b). This
    action fails fast (``parser.error`` → exit 2) on the second occurrence so exactly
    one intent reaches the handler.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: object,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string or self.dest} may be given at most once")
        setattr(namespace, self.dest, values)


def _state_handler(a: argparse.Namespace) -> None:
    """Route gz state to repair or query mode."""
    if a.repair:
        from gzkit.commands.state import state_repair  # noqa: PLC0415

        state_repair(as_json=a.as_json)
    else:
        _lazy("state")(
            as_json=a.as_json,
            blocked=a.blocked,
            ready=a.ready,
            include_withdrawn=a.include_withdrawn,
            full=a.full,
        )


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
            "Re-running on an initialized project repairs missing artifacts. "
            "Use --update for version-aware refresh of canonical surfaces from "
            "the installed wheel (preserves operator edits via marker detection)."
        ),
        epilog=build_epilog(
            [
                "gz init",
                "gz init --mode heavy",
                "gz init --no-skeleton",
                "gz init --force --dry-run",
                "gz init --update",
                "gz init --update --dry-run",
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
    p_init.add_argument(
        "--yes",
        action="store_true",
        default=False,
        help="Auto-accept registry-merge prompts during repair",
    )
    p_init.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="Refresh canonical surfaces from wheel; preserve operator edits.",
    )
    add_force_flag(p_init)
    add_dry_run_flag(p_init)
    p_init.set_defaults(
        func=lambda a: _lazy("init")(
            mode=a.mode,
            force=a.force,
            dry_run=a.dry_run,
            no_skeleton=a.no_skeleton,
            yes=a.yes,
            update=a.update,
        )
    )

    p_upgrade = commands.add_parser(
        "upgrade",
        help="Surface-only refresh of .gzkit/<surface>/ from the installed wheel.",
        description=(
            "Surface-only refresh of .gzkit/<surface>/ from the installed wheel's "
            "package data. Simpler than gz init --update: no manifest mutation, no "
            "scaffolder hooks, no agent sync. Use --surface to refresh a subset of "
            "surfaces; use --force to overwrite operator-edited files."
        ),
        epilog=build_epilog(
            [
                "gz upgrade",
                "gz upgrade --surface skills,rules",
                "gz upgrade --surface templates --dry-run",
                "gz upgrade --surface personas --force",
            ]
        ),
    )
    p_upgrade.add_argument(
        "--surface",
        default=None,
        metavar="SURFACES",
        help="Surfaces to refresh: skills,rules,templates,personas,hooks. Default: all.",
    )
    add_force_flag(p_upgrade)
    add_dry_run_flag(p_upgrade)
    p_upgrade.set_defaults(func=lambda a: _lazy("upgrade_cmd")(a))

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
    p_plan_create.add_argument(
        "--kind",
        choices=["pool", "foundation", "feature"],
        default=None,
        help="ADR taxonomy (required)",
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
            kind=a.kind,
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
                "gz state --blocked --full",
                "gz state --ready",
                "gz state --include-withdrawn",
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
        "--include-withdrawn",
        action="store_true",
        help="Include withdrawn OBPIs (hidden by default; ledger history preserved)",
    )
    p_state.add_argument(
        "--repair",
        action="store_true",
        help="Force-reconcile all frontmatter status from ledger-derived state",
    )
    p_state.add_argument(
        "--full",
        action="store_true",
        help="Preserve full IDs (no ellipsis); fold long cells.",
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
                "gz status --show-gates --full",
                "gz status --table --full",
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
    p_status.add_argument(
        "--epic",
        metavar="SLUG",
        default=None,
        help=("Filter pool ADRs by epic (filename prefix or frontmatter 'epic:')."),
    )
    p_status.add_argument(
        "--full",
        action="store_true",
        help="Render every OBPI as a Rich-table row; preserve full IDs.",
    )
    p_status.set_defaults(
        func=lambda a: _lazy("status")(
            as_json=a.as_json,
            show_gates=a.show_gates,
            as_table=a.table,
            epic=a.epic,
            full=a.full,
        )
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

    # gz mx  ---------------------------------------------------------------
    def _mx_dispatch(a: argparse.Namespace) -> None:
        """Route gz mx subcommands to their handlers (local import for lazy loading)."""
        if a.mx_command == "enter":
            from gzkit.commands.mx_cmd import mx_enter_cmd  # noqa: PLC0415

            mx_enter_cmd(
                reason=a.reason,
                attestor=a.attestor,
                inspection_scope=a.inspection_scope,
            )
        elif a.mx_command == "exit":
            from gzkit.commands.mx_cmd import mx_exit_cmd  # noqa: PLC0415

            mx_exit_cmd(attestor=a.attestor)

    p_mx = commands.add_parser(
        "mx",
        help="Maintenance Hangar (MX) mode operations",
        description=(
            "Open and close the Maintenance Hangar. "
            "While the hangar is open, most governance guards drop to advisory "
            "so the operator can repair governance itself. "
            "gate5_invariants and the PRIME DIRECTIVE still bind."
        ),
        epilog=build_epilog(
            [
                'gz mx enter --reason "re-true locks under ADR-0.0.74" --attestor g0',
                'gz mx enter --reason "repair ledger" --attestor g0 --scope ADR-0.0.74',
            ]
        ),
    )
    mx_commands = p_mx.add_subparsers(dest="mx_command")
    mx_commands.required = True
    p_mx.set_defaults(func=_mx_dispatch)

    p_mx_enter = mx_commands.add_parser(
        "enter",
        help="Open the MX hangar (operator only)",
        description=(
            "Open the Maintenance Hangar. "
            "Sets the marker file, writes an mx_session_opened ledger event, "
            "and captures the inspection scope. "
            "Requires an operator-supplied --attestor; agents cannot open the hangar."
        ),
        epilog=build_epilog(
            [
                'gz mx enter --reason "re-true locks under ADR-0.0.74" --attestor g0',
                "gz mx enter --reason 'repair ledger' --attestor g0 --scope ADR-0.0.74",
            ]
        ),
    )
    p_mx_enter.add_argument("--reason", required=True, help="Reason for entering MX mode")
    p_mx_enter.add_argument(
        "--attestor",
        required=True,
        help="Operator identity (never an agent; MX cannot be opened autonomously)",
    )
    p_mx_enter.add_argument(
        "--scope",
        dest="inspection_scope",
        nargs="*",
        default=[],
        metavar="ADR_OR_OBPI",
        help="ADRs/OBPIs under inspection (optional; 0 or more)",
    )
    p_mx_enter.set_defaults(func=_mx_dispatch)

    p_mx_exit = mx_commands.add_parser(
        "exit",
        help="Close the MX hangar — hard gate (re-run every guard at full strength)",
        description=(
            "Hard gate: re-runs every guard at full strength against the enter-time "
            "inspection scope, green-or-grounded, no --force. "
            "On all-green, the operator signs and the tool writes mx_session_closed "
            "and removes the marker. "
            "Exit is the ONLY path that clears the marker."
        ),
        epilog=build_epilog(["gz mx exit --attestor g0"]),
    )
    p_mx_exit.add_argument(
        "--attestor",
        required=True,
        help="Operator identity who signs airworthiness (required; never an agent)",
    )
    p_mx_exit.set_defaults(func=_mx_dispatch)

    # gz permitted-entry — the airlock's third door (ADR-0.33.0, OBPI-05) ---------
    def _permitted_entry_dispatch(a: argparse.Namespace) -> None:
        """Route gz permitted-entry to its handler (local import for lazy loading)."""
        from gzkit.commands.permitted_entry import permitted_entry_cmd  # noqa: PLC0415

        permitted_entry_cmd(
            target=a.target,
            recon=a.recon,
            repair=a.repair,
            dry_run=a.dry_run,
        )

    p_permitted_entry = commands.add_parser(
        "permitted-entry",
        help="Airlock permitted-entry door — ad-hoc reconnaissance, light repair at most",
        description=(
            "Cross the airlock for an ad-hoc/spurious entry: reconnaissance for "
            "comprehension with light repair at most. The acknowledge-and-decide gate "
            "fires on EVERY transit (permissive ceremony, never skipped). A discovered "
            "need beyond light repair trips a fresh transit through the pipeline door "
            "(intentional change) or the mx door (defect repair) — never smuggled inline."
        ),
        epilog=build_epilog(
            [
                "gz permitted-entry --target src/gzkit/quality.py --recon",
                'gz permitted-entry --target README.md --repair "fix typo" --dry-run',
            ]
        ),
    )
    p_permitted_entry.add_argument(
        "--target",
        required=True,
        type=_nonblank_target,
        help="The file or region the ad-hoc entry reconnoiters",
    )
    # --recon and --repair are contradictory (recon = no change; repair = a change
    # intent) and MUTUALLY EXCLUSIVE — argparse rejects them together so a repair
    # intent can never be silently dropped by adding --recon (GHI #678).
    _pe_intent = p_permitted_entry.add_mutually_exclusive_group()
    _pe_intent.add_argument(
        "--recon",
        action="store_true",
        help="Reconnaissance-only (the default posture): inspect for comprehension, no change",
    )
    _pe_intent.add_argument(
        "--repair",
        default=None,
        metavar="INTENT",
        action=_SingleValueAction,
        help="A light-repair intent (at most); beyond the ceiling trips a fresh transit",
    )
    p_permitted_entry.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the transit (fire the gate) without booking the L2 encounter events",
    )
    p_permitted_entry.set_defaults(func=_permitted_entry_dispatch)

    # gz ontology — read-only sonar over the corpus projection (ADR-0.32.0, OBPI-03)
    p_ontology = commands.add_parser(
        "ontology",
        help="Image the governance shape (read-only ontology sonar)",
        description=(
            "Read-only sonar over the corpus-domain projection. Never writes "
            "graph state (Boundary Invariant #2); sense/seams/resense exit 0 "
            "(a sonar never gates), trace/reach exit 1 on an unknown node id."
        ),
        epilog=build_epilog(
            [
                "gz ontology sense",
                "gz ontology trace ADR-0.31.0-obpi-state-machine",
                "gz ontology resense",
                "gz ontology reach ADR-0.32.0-gzkit-ontology",
            ]
        ),
    )
    ontology_commands = p_ontology.add_subparsers(dest="ontology_command")
    ontology_commands.required = True

    def _add_dot_flag(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--dot", action="store_true", help="Emit a graphviz DOT rendering to stdout"
        )

    p_ontology_sense = ontology_commands.add_parser(
        "sense",
        help="Sweep the current structural shape and surface STRUCTURAL seams",
        description="Image the whole current shape and label STRUCTURAL seams (read-only).",
        epilog=build_epilog(["gz ontology sense", "gz ontology sense --json"]),
    )
    add_json_flag(p_ontology_sense)
    _add_dot_flag(p_ontology_sense)
    p_ontology_sense.set_defaults(
        func=lambda a: _lazy("ontology_sense_cmd")(as_json=a.as_json, as_dot=a.dot)
    )

    p_ontology_trace = ontology_commands.add_parser(
        "trace",
        help="Walk one node's vertical lineage + lateral proof with edge provenance",
        description="Trace one node's vertical lineage + lateral anchors/proof (read-only).",
        epilog=build_epilog(["gz ontology trace ADR-0.31.0-obpi-state-machine"]),
    )
    p_ontology_trace.add_argument("node_id", metavar="ID", help="Node id to trace")
    add_json_flag(p_ontology_trace)
    _add_dot_flag(p_ontology_trace)
    p_ontology_trace.set_defaults(
        func=lambda a: _lazy("ontology_trace_cmd")(
            node_id=a.node_id, as_json=a.as_json, as_dot=a.dot
        )
    )

    p_ontology_resense = ontology_commands.add_parser(
        "resense",
        help="Diff the current shape versus the last sweep (the airlock re-sense gate)",
        description="Report added/removed nodes and edges versus the last sweep (read-only).",
        epilog=build_epilog(["gz ontology resense", "gz ontology resense --json"]),
    )
    add_json_flag(p_ontology_resense)
    _add_dot_flag(p_ontology_resense)
    p_ontology_resense.set_defaults(
        func=lambda a: _lazy("ontology_resense_cmd")(as_json=a.as_json, as_dot=a.dot)
    )

    p_ontology_seams = ontology_commands.add_parser(
        "seams",
        help="Fast contacts-only STRUCTURAL seam check (no per-node lineage)",
        description="List STRUCTURAL seams without full per-node lineage (read-only).",
        epilog=build_epilog(["gz ontology seams", "gz ontology seams --json"]),
    )
    add_json_flag(p_ontology_seams)
    _add_dot_flag(p_ontology_seams)
    p_ontology_seams.set_defaults(
        func=lambda a: _lazy("ontology_seams_cmd")(as_json=a.as_json, as_dot=a.dot)
    )

    p_ontology_reach = ontology_commands.add_parser(
        "reach",
        help="Return one node's downstream blast-radius (transitive dependents)",
        description="Report the transitive-dependent blast-radius for one node (read-only).",
        epilog=build_epilog(["gz ontology reach ADR-0.32.0-gzkit-ontology"]),
    )
    p_ontology_reach.add_argument("node_id", metavar="ID", help="Node id to expand")
    add_json_flag(p_ontology_reach)
    _add_dot_flag(p_ontology_reach)
    p_ontology_reach.set_defaults(
        func=lambda a: _lazy("ontology_reach_cmd")(
            node_id=a.node_id, as_json=a.as_json, as_dot=a.dot
        )
    )

    # gz airlock — operator surface over the airlock-IN membrane (ADR-0.33.0, OBPI-02)
    p_airlock = commands.add_parser(
        "airlock",
        help="Run the airlock-IN preflight membrane (diagnostic-only for now)",
        description=(
            "Operator surface over the airlock-IN three-beat gate: DECLARE -> PING "
            "-> RECONCILE -> decide. Diagnostic-only FOR NOW: a NO-GO prints a "
            "refusal but still exits 0. That is a staged posture, not the contract "
            "— production reach yields an empty seam-map, so a fail-closed gate "
            "would be vacuous (ADR-0.33.0 § Calibration frontier, operator-attested "
            "2026-07-10; calibration is a named successor increment). The declared "
            "end state BLOCKS: § Boundary Invariant 4, an un-accounted seam makes "
            "GO structurally unreachable."
        ),
        epilog=build_epilog(["gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run"]),
    )
    airlock_commands = p_airlock.add_subparsers(dest="airlock_command")
    airlock_commands.required = True

    p_airlock_in = airlock_commands.add_parser(
        "in",
        help="Run the airlock-IN preflight for a target OBPI (diagnostic-only)",
        description=(
            "Resolve the target OBPI's brief, run the airlock-IN preflight, and "
            "report the decision plus seam-map counts. A NO-GO prints a refusal "
            "but still exits 0; only an unresolvable brief exits 1."
        ),
        epilog=build_epilog(
            [
                "gz airlock in --target OBPI-0.33.0-01 --dry-run",
                "gz airlock in --target OBPI-0.33.0-01 --json",
            ]
        ),
    )
    p_airlock_in.add_argument(
        "--target", required=True, metavar="OBPI", help="Target OBPI id to preflight"
    )
    p_airlock_in.add_argument("--phase", help="Optional pipeline phase label (e.g. build)")
    add_dry_run_flag(
        p_airlock_in, help_override="Run the preflight without booking an airlock_in event"
    )
    add_json_flag(p_airlock_in)
    p_airlock_in.set_defaults(
        func=lambda a: _lazy("airlock_in_cmd")(
            target=a.target, phase=a.phase, dry_run=a.dry_run, as_json=a.as_json
        )
    )

    p_airlock_out = airlock_commands.add_parser(
        "out",
        help="Run the airlock-OUT exit drift-diff for a target OBPI (diagnostic-only)",
        description=(
            "Resolve the target OBPI's brief, run the airlock-OUT exit membrane "
            "(drift-diff push-minus-pull -> findings + recommendations -> closed "
            "decision menu -> fresh-transit routing -> log to L2), and report the "
            "verdict. Surfaced drift prints findings but still exits 0; only an "
            "unresolvable brief exits 1. NEVER writes L1 canon."
        ),
        epilog=build_epilog(
            [
                "gz airlock out --target OBPI-0.33.0-01 --dry-run",
                "gz airlock out --target OBPI-0.33.0-01 --json",
            ]
        ),
    )
    p_airlock_out.add_argument(
        "--target", required=True, metavar="OBPI", help="Target OBPI id to exit-account"
    )
    add_dry_run_flag(
        p_airlock_out, help_override="Run the drift-diff without booking an airlock_out event"
    )
    add_json_flag(p_airlock_out)
    p_airlock_out.set_defaults(
        func=lambda a: _lazy("airlock_out_cmd")(
            target=a.target, dry_run=a.dry_run, as_json=a.as_json
        )
    )
