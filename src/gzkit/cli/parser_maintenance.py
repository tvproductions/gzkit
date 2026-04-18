"""Maintenance and utility subparser registrations for gz CLI.

Registers: check, drift, covers, lint, format, test, typecheck, validate,
skill subcommands, parity, readiness, check-config-paths, preflight, cli,
agent, git-sync, tidy, chores, interview.

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
    add_dry_run_flag,
    add_json_flag,
    build_epilog,
)
from gzkit.skills import DEFAULT_MAX_REVIEW_AGE_DAYS

_LAZY_HANDLERS: dict[str, str] = {
    "chores_advise": "gzkit.commands.chores",
    "chores_audit": "gzkit.commands.chores",
    "chores_list": "gzkit.commands.chores",
    "chores_plan": "gzkit.commands.chores",
    "chores_run": "gzkit.commands.chores",
    "chores_show": "gzkit.commands.chores",
    "cli_audit_cmd": "gzkit.commands.cli_audit",
    "check_config_paths_cmd": "gzkit.commands.config_paths",
    "covers_cmd": "gzkit.commands.covers",
    "drift_cmd": "gzkit.commands.drift",
    "frontmatter_reconcile_cmd": "gzkit.commands.frontmatter_reconcile",
    "flag_explain_cmd": "gzkit.commands.flags",
    "flags_list_cmd": "gzkit.commands.flags",
    "interview": "gzkit.commands.interview_cmd",
    "parity_check_cmd": "gzkit.commands.parity",
    "preflight_cmd": "gzkit.commands.preflight",
    "check": "gzkit.commands.quality",
    "format_cmd": "gzkit.commands.quality",
    "lint": "gzkit.commands.quality",
    "test": "gzkit.commands.quality",
    "typecheck": "gzkit.commands.quality",
    "readiness_audit_cmd": "gzkit.commands.readiness",
    "readiness_eval_cmd": "gzkit.commands.readiness",
    "skill_audit_cmd": "gzkit.commands.skills_cmd",
    "skill_list": "gzkit.commands.skills_cmd",
    "skill_new": "gzkit.commands.skills_cmd",
    "git_sync": "gzkit.commands.sync",
    "sync_control_surfaces": "gzkit.commands.tidy",
    "tidy": "gzkit.commands.tidy",
    "validate": "gzkit.commands.validate_cmd",
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


def register_maintenance_parsers(commands: argparse._SubParsersAction) -> None:
    """Register maintenance and utility subcommands on *commands*."""
    _register_quality_parsers(commands)
    _register_tooling_parsers(commands)
    _register_chores_parsers(commands)
    _register_skill_parsers(commands)
    _register_agent_parsers(commands)
    _register_flag_parsers(commands)
    _register_frontmatter_parsers(commands)


def _register_frontmatter_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz frontmatter`` sub-command group (ADR-0.0.16 OBPI-03)."""
    p_fm = commands.add_parser(
        "frontmatter",
        help="Frontmatter-ledger coherence commands",
        description="Reconcile ADR/OBPI frontmatter with the ledger (ledger-wins).",
        epilog=build_epilog(
            ["gz frontmatter reconcile --dry-run", "gz frontmatter reconcile --json"]
        ),
    )
    fm_sub = p_fm.add_subparsers(dest="frontmatter_cmd")
    p_reconcile = fm_sub.add_parser(
        "reconcile",
        help="Rewrite drifted frontmatter to match ledger (ledger-wins)",
        description=(
            "Detect frontmatter drift via the OBPI-01 validator and rewrite the "
            "drifted id/parent/lane/status fields to match the ledger. Emits a "
            "schema-validated receipt under artifacts/receipts/frontmatter-coherence/."
        ),
        epilog=build_epilog(
            [
                "gz frontmatter reconcile",
                "gz frontmatter reconcile --dry-run",
                "gz frontmatter reconcile --json",
            ]
        ),
    )
    add_dry_run_flag(p_reconcile)
    add_json_flag(p_reconcile)
    p_reconcile.set_defaults(
        func=lambda a: _lazy("frontmatter_reconcile_cmd")(dry_run=a.dry_run, as_json=a.as_json)
    )


def _register_quality_parsers(commands: argparse._SubParsersAction) -> None:
    """Register quality and validation subcommands."""
    commands.add_parser(
        "lint",
        help="Run lint checks",
        description="Run Ruff linter on the codebase.",
        epilog=build_epilog(["gz lint"]),
    ).set_defaults(func=lambda a: _lazy("lint")())
    commands.add_parser(
        "format",
        help="Run formatter",
        description="Run Ruff formatter on the codebase.",
        epilog=build_epilog(["gz format"]),
    ).set_defaults(func=lambda a: _lazy("format_cmd")())
    p_test = commands.add_parser(
        "test",
        help="Run unit tests (--obpi scopes to one OBPI; --bdd adds behave)",
        description=(
            "Run tests with scope selection. Default = full unittest suite. "
            "--obpi OBPI-X.Y.Z-NN runs only tests whose @covers decorator "
            "targets a REQ in that OBPI (fastest; pipeline Stage 3 default). "
            "--bdd adds behave scenarios (ADR closeout / Heavy-lane). "
            "--obpi and --bdd are mutually exclusive. See .gzkit/rules/tests.md."
        ),
        epilog=build_epilog(
            [
                "gz test --obpi OBPI-0.0.16-01",
                "gz test",
                "gz test --bdd",
            ]
        ),
    )
    p_test.add_argument(
        "--bdd",
        action="store_true",
        default=False,
        help="Also run behave scenarios (Heavy-lane / closeout ceremony)",
    )
    p_test.add_argument(
        "--obpi",
        default=None,
        help="Scope run to tests @covers-covering one OBPI's REQs",
    )
    p_test.set_defaults(func=lambda a: _lazy("test")(bdd=a.bdd, obpi=a.obpi))
    commands.add_parser(
        "typecheck",
        help="Run type checks",
        description="Run static type analysis with ty.",
        epilog=build_epilog(["gz typecheck"]),
    ).set_defaults(func=lambda a: _lazy("typecheck")())

    p_check = commands.add_parser(
        "check",
        help="Run all quality checks",
        description="Run lint, format, typecheck, test, and advisory drift in sequence.",
        epilog=build_epilog(["gz check", "gz check --json"]),
    )
    add_json_flag(p_check)
    p_check.set_defaults(func=lambda a: _lazy("check")(as_json=a.as_json))

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
        "--plain", action="store_true", default=False, help="One record per line (grep-friendly)"
    )
    p_drift.add_argument(
        "--adr-dir", default=None, help="Override ADR directory to scan (default: docs/design/adr)"
    )
    p_drift.add_argument(
        "--test-dir", default=None, help="Override test directory to scan (default: tests)"
    )
    p_drift.set_defaults(
        func=lambda a: _lazy("drift_cmd")(
            as_json=a.as_json, plain=a.plain, adr_dir=a.adr_dir, test_dir=a.test_dir
        )
    )

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
                "gz covers ADR-0.9.0 --include-doc",
            ]
        ),
    )
    p_covers.add_argument(
        "target", nargs="?", default=None, help="ADR-X.Y.Z or OBPI-X.Y.Z-NN to filter (all)"
    )
    add_json_flag(p_covers)
    p_covers.add_argument(
        "--plain", action="store_true", default=False, help="One record per line (grep-friendly)"
    )
    p_covers.add_argument(
        "--adr-dir", default=None, help="Override ADR directory to scan (default: docs/design/adr)"
    )
    p_covers.add_argument(
        "--test-dir", default=None, help="Override test directory to scan (default: tests)"
    )
    p_covers.add_argument(
        "--features-dir",
        dest="features_dir",
        default=None,
        help="Override behave features directory to scan (default: features)",
    )
    p_covers.add_argument(
        "--include-doc",
        action="store_true",
        default=False,
        help="Include doc-kind REQs (default: excluded — tests are for code)",
    )
    p_covers.set_defaults(
        func=lambda a: _lazy("covers_cmd")(
            target=a.target,
            as_json=a.as_json,
            plain=a.plain,
            adr_dir=a.adr_dir,
            test_dir=a.test_dir,
            features_dir=a.features_dir,
            include_doc=a.include_doc,
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
        "--documents", dest="check_documents", action="store_true", help="Validate governance docs"
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
    p_validate.add_argument(
        "--personas",
        dest="check_personas",
        action="store_true",
        help="Validate persona files in .gzkit/personas/",
    )
    p_validate.add_argument(
        "--interviews",
        dest="check_interviews",
        action="store_true",
        help="Verify ADRs with OBPIs have interview transcript artifacts",
    )
    p_validate.add_argument(
        "--decomposition",
        dest="check_decomposition",
        action="store_true",
        help="Validate ADR decomposition scorecards and checklist-to-brief alignment",
    )
    p_validate.add_argument(
        "--requirements",
        dest="check_requirements",
        action="store_true",
        help="Flag OBPI briefs whose REQUIREMENTS sections lack REQ-ID identifiers",
    )
    p_validate.add_argument(
        "--commit-trailers",
        dest="check_commit_trailers",
        action="store_true",
        help="Flag HEAD commits touching src/ or tests/ without a Task: trailer",
    )
    p_validate.add_argument(
        "--frontmatter",
        dest="check_frontmatter",
        action="store_true",
        help="Validate frontmatter against ledger truth (exit 3 on drift)",
    )
    p_validate.add_argument(
        "--adr",
        dest="frontmatter_adr",
        default=None,
        help="Scope --frontmatter validation to one ADR (and its OBPIs)",
    )
    p_validate.add_argument(
        "--explain",
        dest="frontmatter_explain",
        default=None,
        help="Print step-by-step remediation commands per drifted field for one ADR",
    )
    p_validate.add_argument(
        "--version",
        dest="check_version",
        action="store_true",
        help="Validate version consistency across all locations",
    )
    p_validate.add_argument(
        "--type-ignores",
        dest="check_type_ignores",
        action="store_true",
        help="Fail on `# type: ignore[<code>]` under src/ (ty-unhonored)",
    )
    p_validate.add_argument(
        "--cli-alignment",
        dest="check_cli_alignment",
        action="store_true",
        help="Every `gz <verb>` in features/operator-docs must resolve",
    )
    p_validate.add_argument(
        "--event-handlers",
        dest="check_event_handlers",
        action="store_true",
        help="Every ledger event type must be claimed by a graph handler",
    )
    p_validate.add_argument(
        "--validator-fields",
        dest="check_validator_fields",
        action="store_true",
        help="Every validator info.get(field) must have a graph writer",
    )
    p_validate.add_argument(
        "--audits",
        dest="check_audits",
        action="store_true",
        help="Run all four trust-doctrine pattern audits",
    )
    add_json_flag(p_validate)
    p_validate.set_defaults(
        func=lambda a: _lazy("validate")(
            check_manifest=a.check_manifest,
            check_documents=a.check_documents,
            check_surfaces=a.check_surfaces,
            check_ledger=a.check_ledger,
            check_instructions=a.check_instructions,
            check_briefs=a.check_briefs,
            check_personas=a.check_personas,
            check_interviews=a.check_interviews,
            check_decomposition=a.check_decomposition,
            check_requirements=a.check_requirements,
            check_commit_trailers=a.check_commit_trailers,
            check_frontmatter=a.check_frontmatter,
            check_version=a.check_version,
            check_type_ignores=a.check_type_ignores or a.check_audits,
            check_cli_alignment=a.check_cli_alignment or a.check_audits,
            check_event_handlers=a.check_event_handlers or a.check_audits,
            check_validator_fields=a.check_validator_fields or a.check_audits,
            as_json=a.as_json,
            frontmatter_adr=a.frontmatter_adr,
            frontmatter_explain=a.frontmatter_explain,
        )
    )

    p_check_paths = commands.add_parser(
        "check-config-paths",
        help="Validate config/manifest paths are coherent",
        description="Verify configured and manifest path coherence.",
        epilog=build_epilog(["gz check-config-paths", "gz check-config-paths --json"]),
    )
    add_json_flag(p_check_paths)
    p_check_paths.set_defaults(func=lambda a: _lazy("check_config_paths_cmd")(as_json=a.as_json))


def _register_tooling_parsers(commands: argparse._SubParsersAction) -> None:
    """Register tooling, sync, and audit subcommands."""
    p_tidy = commands.add_parser(
        "tidy",
        help="Run maintenance checks and cleanup",
        description="Run maintenance checks and apply cleanup routines.",
        epilog=build_epilog(["gz tidy --check", "gz tidy --fix", "gz tidy --fix --dry-run"]),
    )
    p_tidy.add_argument(
        "--check", dest="check_only", action="store_true", help="Report issues without fixing"
    )
    p_tidy.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    add_dry_run_flag(p_tidy)
    p_tidy.set_defaults(
        func=lambda a: _lazy("tidy")(check_only=a.check_only, fix=a.fix, dry_run=a.dry_run)
    )

    p_preflight = commands.add_parser(
        "preflight",
        help="Scan for stale pipeline artifacts",
        description="Detect and clean stale markers, orphan receipts, and expired locks.",
        epilog=build_epilog(["gz preflight", "gz preflight --apply", "gz preflight --json"]),
    )
    p_preflight.add_argument(
        "--apply", action="store_true", help="Remove stale artifacts (default: dry-run report only)"
    )
    add_json_flag(p_preflight)
    p_preflight.set_defaults(
        func=lambda a: _lazy("preflight_cmd")(apply=a.apply, as_json=a.as_json)
    )

    p_cli = commands.add_parser(
        "cli",
        help="CLI governance commands",
        description="CLI documentation and coverage audit commands.",
        epilog=build_epilog(["gz cli audit", "gz cli audit --json"]),
    )
    cli_commands = p_cli.add_subparsers(dest="cli_command")
    cli_commands.required = True
    p_cli_audit = cli_commands.add_parser(
        "audit",
        help="Audit CLI docs/manpage coverage",
        description="Check CLI command documentation and manpage parity.",
        epilog=build_epilog(["gz cli audit", "gz cli audit --json"]),
    )
    add_json_flag(p_cli_audit)
    p_cli_audit.set_defaults(func=lambda a: _lazy("cli_audit_cmd")(as_json=a.as_json))

    p_parity = commands.add_parser(
        "parity",
        help="Parity governance commands",
        description="Cross-repository parity regression commands.",
        epilog=build_epilog(["gz parity check", "gz parity check --json"]),
    )
    parity_commands = p_parity.add_subparsers(dest="parity_command")
    parity_commands.required = True
    p_parity_check = parity_commands.add_parser(
        "check",
        help="Run deterministic parity regression checks",
        description="Execute deterministic parity regression checks.",
        epilog=build_epilog(["gz parity check", "gz parity check --json"]),
    )
    add_json_flag(p_parity_check)
    p_parity_check.set_defaults(func=lambda a: _lazy("parity_check_cmd")(as_json=a.as_json))

    p_readiness = commands.add_parser(
        "readiness",
        help="Agent readiness governance commands",
        description="Agent readiness audit and evaluation commands.",
        epilog=build_epilog(["gz readiness audit", "gz readiness evaluate"]),
    )
    readiness_commands = p_readiness.add_subparsers(dest="readiness_command")
    readiness_commands.required = True
    p_readiness_audit = readiness_commands.add_parser(
        "audit",
        help="Audit readiness across disciplines and primitives",
        description="Audit agent readiness across all disciplines.",
        epilog=build_epilog(["gz readiness audit", "gz readiness audit --json"]),
    )
    add_json_flag(p_readiness_audit)
    p_readiness_audit.set_defaults(func=lambda a: _lazy("readiness_audit_cmd")(as_json=a.as_json))
    p_readiness_eval = readiness_commands.add_parser(
        "evaluate",
        help="Run instruction eval suite with positive/negative controls",
        description="Execute instruction evaluation with control cases.",
        epilog=build_epilog(["gz readiness evaluate", "gz readiness evaluate --json"]),
    )
    add_json_flag(p_readiness_eval)
    p_readiness_eval.set_defaults(func=lambda a: _lazy("readiness_eval_cmd")(as_json=a.as_json))

    p_git_sync = commands.add_parser(
        "git-sync",
        help="Sync branch with guarded ritual",
        description=(
            "Commit, fetch, rebase, push — pre-commit hooks enforce lint/test "
            "automatically. Use --lint/--test only for explicit edge-case gates."
        ),
        epilog=build_epilog(
            [
                "gz git-sync --apply",
                "gz git-sync --apply --lint --test",
                "gz git-sync --apply --no-push",
                "gz git-sync --json",
            ]
        ),
    )
    _add_git_sync_options(p_git_sync)
    p_git_sync.set_defaults(
        func=lambda a: _lazy("git_sync")(
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

    p_interview = commands.add_parser(
        "interview",
        help="Interactive document interview",
        description="Run an interactive interview to generate a document.",
        epilog=build_epilog(["gz interview prd", "gz interview adr", "gz interview obpi"]),
    )
    p_interview.add_argument(
        "document_type",
        choices=["prd", "adr", "obpi"],
        help="Document type to generate (prd|adr|obpi)",
    )
    p_interview.add_argument(
        "--from",
        dest="from_file",
        metavar="FILE",
        help="Load answers from a JSON file instead of interactive prompts",
    )
    p_interview.set_defaults(
        func=lambda a: _lazy("interview")(document_type=a.document_type, from_file=a.from_file),
    )


def _register_chores_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz chores`` sub-command group."""
    p_chores = commands.add_parser(
        "chores",
        help="Chore registry and execution commands",
        description="Discover, plan, execute, and audit repository chores.",
        epilog=build_epilog(
            ["gz chores list", "gz chores show my-chore", "gz chores run my-chore"]
        ),
    )
    chores_commands = p_chores.add_subparsers(dest="chores_command")
    chores_commands.required = True

    chores_commands.add_parser(
        "list",
        help="List chores from registry",
        description="Display all registered chores and their status.",
        epilog=build_epilog(["gz chores list"]),
    ).set_defaults(func=lambda a: _lazy("chores_list")())

    p_chores_show = chores_commands.add_parser(
        "show",
        help="Display CHORE.md for one chore",
        description="Show the full chore definition for a given slug.",
        epilog=build_epilog(["gz chores show my-chore"]),
    )
    p_chores_show.add_argument("slug", help="Chore slug identifier")
    p_chores_show.set_defaults(func=lambda a: _lazy("chores_show")(slug=a.slug))

    p_chores_plan = chores_commands.add_parser(
        "plan",
        help="Show plan details for one chore",
        description="Display the execution plan for a given chore.",
        epilog=build_epilog(["gz chores plan my-chore"]),
    )
    p_chores_plan.add_argument("slug", help="Chore slug identifier")
    p_chores_plan.set_defaults(func=lambda a: _lazy("chores_plan")(slug=a.slug))

    p_chores_advise = chores_commands.add_parser(
        "advise",
        help="Dry-run criteria and report status",
        description="Evaluate chore criteria and advise on readiness.",
        epilog=build_epilog(["gz chores advise my-chore"]),
    )
    p_chores_advise.add_argument("slug", help="Chore slug identifier")
    p_chores_advise.set_defaults(func=lambda a: _lazy("chores_advise")(slug=a.slug))

    p_chores_run = chores_commands.add_parser(
        "run",
        help="Execute one chore by slug",
        description="Execute a single chore and record results.",
        epilog=build_epilog(["gz chores run my-chore"]),
    )
    p_chores_run.add_argument("slug", help="Chore slug identifier")
    p_chores_run.set_defaults(func=lambda a: _lazy("chores_run")(slug=a.slug))

    p_chores_audit = chores_commands.add_parser(
        "audit",
        help="Audit chore log presence",
        description="Verify chore execution logs are present.",
        epilog=build_epilog(["gz chores audit --all", "gz chores audit --slug my-chore"]),
    )
    chores_audit_target = p_chores_audit.add_mutually_exclusive_group(required=True)
    chores_audit_target.add_argument(
        "--all", dest="all_chores", action="store_true", help="Audit all registered chores"
    )
    chores_audit_target.add_argument("--slug", help="Audit a single chore by slug")
    p_chores_audit.set_defaults(
        func=lambda a: _lazy("chores_audit")(all_chores=a.all_chores, slug=a.slug)
    )


def _register_skill_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz skill`` sub-command group."""
    p_skill = commands.add_parser(
        "skill",
        help="Skill management commands",
        description="Create, list, and audit gzkit skills.",
        epilog=build_epilog(["gz skill list", "gz skill new my-skill", "gz skill audit"]),
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
    p_skill_new.set_defaults(
        func=lambda a: _lazy("skill_new")(name=a.name, description=a.description)
    )

    p_skill_list = skill_commands.add_parser(
        "list",
        help="List skills (active by default)",
        description=(
            "Display skills. Retired/archived skills are hidden by default so the "
            "CLI matches the generated AGENTS.md catalog filter. Use --all to "
            "surface retired skills with their lifecycle label."
        ),
        epilog=build_epilog(
            [
                "gz skill list",
                "gz skill list --all",
                "gz skill list --json",
            ]
        ),
    )
    add_json_flag(p_skill_list)
    p_skill_list.add_argument(
        "--all",
        dest="show_all",
        action="store_true",
        help="Include retired/archived skills in the listing.",
    )
    p_skill_list.set_defaults(
        func=lambda a: _lazy("skill_list")(include_retired=a.show_all, as_json=a.as_json)
    )

    p_skill_audit = skill_commands.add_parser(
        "audit",
        help="Audit skill lifecycle and mirror parity",
        description="Check skill files, mirrors, and review freshness.",
        epilog=build_epilog(["gz skill audit", "gz skill audit --strict", "gz skill audit --json"]),
    )
    add_json_flag(p_skill_audit)
    p_skill_audit.add_argument(
        "--strict", action="store_true", help="Treat warnings as blocking failures."
    )
    p_skill_audit.add_argument(
        "--max-review-age-days",
        type=int,
        default=DEFAULT_MAX_REVIEW_AGE_DAYS,
        help="Maximum age of last_reviewed before audit fails (default: 90).",
    )
    p_skill_audit.set_defaults(
        func=lambda a: _lazy("skill_audit_cmd")(
            as_json=a.as_json, strict=a.strict, max_review_age_days=a.max_review_age_days
        )
    )


def _register_agent_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz agent`` sub-command group."""
    p_agent = commands.add_parser(
        "agent",
        help="Agent-specific operations",
        description="Agent synchronization and management commands.",
        epilog=build_epilog(["gz agent sync control-surfaces"]),
    )
    agent_commands = p_agent.add_subparsers(dest="agent_command")
    agent_commands.required = True

    p_agent_sync = agent_commands.add_parser(
        "sync",
        help="Agent synchronization commands",
        description="Synchronize agent control surfaces and mirrors.",
        epilog=build_epilog(
            ["gz agent sync control-surfaces", "gz agent sync control-surfaces --dry-run"]
        ),
    )
    agent_sync_commands = p_agent_sync.add_subparsers(dest="agent_sync_command")
    agent_sync_commands.required = True

    p_control_surfaces = agent_sync_commands.add_parser(
        "control-surfaces",
        help="Regenerate agent control surfaces from governance canon",
        description="Rebuild CLAUDE.md and mirrors from governance source.",
        epilog=build_epilog(
            ["gz agent sync control-surfaces", "gz agent sync control-surfaces --dry-run"]
        ),
    )
    add_dry_run_flag(p_control_surfaces)
    p_control_surfaces.set_defaults(
        func=lambda a: _lazy("sync_control_surfaces")(dry_run=a.dry_run)
    )


def _add_git_sync_options(parser: argparse.ArgumentParser) -> None:
    """Register common git-sync CLI flags."""
    parser.add_argument(
        "--skill", action="store_true", help="Print path to paired skill file and exit"
    )
    parser.add_argument("--branch", help="Branch to sync (default: current branch)")
    parser.add_argument("--remote", default="origin", help="Remote name")
    parser.add_argument(
        "--apply", action="store_true", help="Execute sync actions (dry-run by default)"
    )
    parser.add_argument(
        "--lint",
        dest="run_lint_gate",
        action="store_true",
        default=False,
        help="Run lint gate before sync (redundant with pre-commit hook; opt-in)",
    )
    parser.add_argument(
        "--no-lint",
        dest="run_lint_gate",
        action="store_false",
        help="Skip lint gate (default; pre-commit hook handles lint)",
    )
    parser.add_argument(
        "--test",
        dest="run_test_gate",
        action="store_true",
        default=False,
        help="Run test gate before sync (redundant with pre-commit hook; opt-in)",
    )
    parser.add_argument(
        "--no-test",
        dest="run_test_gate",
        action="store_false",
        help="Skip test gate (default; pre-commit hook handles tests)",
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


def _register_flag_parsers(commands: argparse._SubParsersAction) -> None:
    """Register ``gz flags`` and ``gz flag`` subcommands."""
    # --- gz flags (list) ---------------------------------------------------
    p_flags = commands.add_parser(
        "flags",
        help="List all feature flags with resolved values",
        description="Display all registered feature flags with current values and sources.",
        epilog=build_epilog(
            [
                "gz flags",
                "gz flags --stale",
                "gz flags --json",
            ]
        ),
    )
    p_flags.add_argument(
        "--stale",
        action="store_true",
        help="Show only stale flags (past review_by or remove_by dates)",
    )
    add_json_flag(p_flags)
    p_flags.set_defaults(func=lambda a: _lazy("flags_list_cmd")(stale=a.stale, as_json=a.as_json))

    # --- gz flag (single-flag inspection) -----------------------------------
    p_flag = commands.add_parser(
        "flag",
        help="Inspect a single feature flag",
        description="Single-flag inspection commands (explain).",
        epilog=build_epilog(
            [
                "gz flag explain ops.product_proof",
                "gz flag explain ops.product_proof --json",
            ]
        ),
    )
    flag_commands = p_flag.add_subparsers(dest="flag_command")
    flag_commands.required = True

    p_explain = flag_commands.add_parser(
        "explain",
        help="Show full metadata and resolved state for one flag",
        description="Display flag metadata, resolved value with source, staleness, and linked ADR.",
        epilog=build_epilog(
            [
                "gz flag explain ops.product_proof",
                "gz flag explain migration.config_gates_to_flags --json",
            ]
        ),
    )
    p_explain.add_argument("key", help="Dotted flag key (e.g. ops.product_proof)")
    add_json_flag(p_explain)
    p_explain.set_defaults(func=lambda a: _lazy("flag_explain_cmd")(key=a.key, as_json=a.as_json))
