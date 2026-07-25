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

from gzkit.cli.helpers import (
    add_dry_run_flag,
    add_json_flag,
    build_epilog,
)
from gzkit.cli.parser_handler_manifest import _lazy
from gzkit.skills import DEFAULT_MAX_REVIEW_AGE_DAYS


def register_maintenance_parsers(commands: argparse._SubParsersAction) -> None:
    """Register maintenance and utility subcommands on *commands*."""
    _register_quality_parsers(commands)
    _register_tooling_parsers(commands)
    _register_chores_parsers(commands)
    _register_skill_parsers(commands)
    _register_agent_parsers(commands)
    _register_flag_parsers(commands)
    _register_frontmatter_parsers(commands)
    _register_handoff_parsers(commands)


def _register_handoff_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz handoff`` sub-command group (ADR-0.0.65 OBPI-03)."""
    p_handoff = commands.add_parser(
        "handoff",
        help="Author and resume session handoffs through the validation gate",
        description=(
            "Create, list, and resume session handoffs. `create` routes authoring "
            "through the fail-closed validate_handoff_document gate; `list` and "
            "`resume` are read-only projections over .gzkit/handoffs/."
        ),
        epilog=build_epilog(
            [
                "gz handoff list",
                "gz handoff list --adr ADR-0.0.65 --json",
                "gz handoff resume --adr ADR-0.0.65",
                "gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 "
                '--decisions "Chose X over Y"',
            ]
        ),
    )
    handoff_sub = p_handoff.add_subparsers(dest="handoff_command")
    handoff_sub.required = True

    p_list = handoff_sub.add_parser(
        "list",
        help="List handoffs newest-first (optionally scoped by ADR)",
        description="List frontmatter-filtered handoffs newest-first.",
        epilog=build_epilog(["gz handoff list", "gz handoff list --adr ADR-0.0.65 --json"]),
    )
    p_list.add_argument("--adr", default=None, help="Scope the listing to one ADR id")
    add_json_flag(p_list)
    p_list.set_defaults(func=lambda a: _lazy("handoff_list_cmd")(adr=a.adr, as_json=a.as_json))

    p_resume = handoff_sub.add_parser(
        "resume",
        help="Resume the newest handoff for an ADR with staleness classification",
        description="Report the newest handoff for an ADR, its staleness, and first next step.",
        epilog=build_epilog(
            [
                "gz handoff resume --adr ADR-0.0.65",
                "gz handoff resume --adr ADR-0.0.65 --json",
            ]
        ),
    )
    p_resume.add_argument(
        "--adr",
        default=None,
        help="ADR id to resume the newest handoff for (omit for newest overall)",
    )
    add_json_flag(p_resume)
    p_resume.set_defaults(func=lambda a: _lazy("handoff_resume_cmd")(adr=a.adr, as_json=a.as_json))

    p_create = handoff_sub.add_parser(
        "create",
        help="Author a handoff, fail-closed through the validation gate",
        description=(
            "Author a handoff document. The document is validated before it is "
            "written; on any violation nothing is written and the verb exits 1. "
            "All seven required sections must be populated: an unsupplied "
            "section is a refusal, not an empty heading (GHI #692)."
        ),
        epilog=build_epilog(
            [
                "gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 "
                '--summary "Landed X" --context "Y constrains Z" '
                '--decisions "Chose X over Y" --next-steps "1. Review W" '
                '--pending "GHI #123 open" --verification "uv run gz check" '
                '--evidence "`src/gzkit/x.py`"',
            ]
        ),
    )
    p_create.add_argument(
        "--adr",
        default=None,
        help="Parent ADR id (ADR-X.Y.Z); omit for work with no parent ADR",
    )
    p_create.add_argument("--slug", required=True, help="Filename slug for the handoff")
    p_create.add_argument("--agent", required=True, help="Authoring agent identity")
    p_create.add_argument("--decisions", required=True, help="Decisions Made section body")
    p_create.add_argument("--branch", default=None, help="Branch (default: current git branch)")
    p_create.add_argument("--summary", default=None, help="Current State Summary section body")
    p_create.add_argument("--context", default=None, help="Important Context section body")
    p_create.add_argument(
        "--next-steps", dest="next_steps", default=None, help="Immediate Next Steps section body"
    )
    p_create.add_argument("--pending", default=None, help="Pending Work / Open Loops section body")
    p_create.add_argument(
        "--verification", default=None, help="Verification Checklist section body"
    )
    p_create.add_argument("--evidence", default=None, help="Evidence / Artifacts section body")
    p_create.add_argument("--obpi", default=None, help="OBPI id this handoff scopes to")
    p_create.add_argument(
        "--continues-from", dest="continues_from", default=None, help="Prior handoff reference"
    )
    p_create.add_argument("--session-id", dest="session_id", default=None, help="Session id")
    p_create.add_argument(
        "--settled",
        action="append",
        default=None,
        metavar="RULING",
        help="Seat a late settled ruling (repeatable); unions with carried entries",
    )
    add_json_flag(p_create)
    p_create.set_defaults(
        func=lambda a: _lazy("handoff_create_cmd")(
            adr=a.adr,
            slug=a.slug,
            agent=a.agent,
            decisions=a.decisions,
            settled=a.settled,
            branch=a.branch,
            summary=a.summary,
            context=a.context,
            next_steps=a.next_steps,
            pending=a.pending,
            verification=a.verification,
            evidence=a.evidence,
            obpi=a.obpi,
            continues_from=a.continues_from,
            session_id=a.session_id,
            as_json=a.as_json,
        )
    )

    p_authorize = handoff_sub.add_parser(
        "authorize",
        help="Book the operator's ruling on a resumed handoff (lifts the resume gate)",
        description=(
            "Record the operator's authorization to act on a resumed handoff. "
            "Until this is booked, the resume gate refuses every mutating tool "
            "call for this session (gz-session-handoff SKILL.md § RESUME). "
            "--operator-text carries the operator's VERBATIM words — never a "
            "paraphrase, and never words they did not say."
        ),
        epilog=build_epilog(
            [
                "gz handoff authorize --handoff .gzkit/handoffs/20260716T204012Z-work.md "
                '--operator-text "focus on handoff first"',
            ]
        ),
    )
    p_authorize.add_argument("--handoff", required=True, help="Resumed handoff the ruling covers")
    p_authorize.add_argument(
        "--operator-text",
        dest="operator_text",
        required=True,
        help="The operator's verbatim authorization words (never paraphrased)",
    )
    p_authorize.add_argument(
        "--session-id",
        dest="session_id",
        required=True,
        help="Harness session the ruling binds to (the gate's block message interpolates it)",
    )
    add_json_flag(p_authorize)
    p_authorize.set_defaults(
        func=lambda a: _lazy("handoff_authorize_cmd")(
            handoff=a.handoff,
            operator_text=a.operator_text,
            session_id=a.session_id,
            as_json=a.as_json,
        )
    )

    p_archive = handoff_sub.add_parser(
        "archive",
        help="Move handoffs older than a threshold into .gzkit/handoffs/archive/",
        description=(
            "Relocate (move-not-delete) handoffs older than --older-than into "
            ".gzkit/handoffs/archive/, honoring the lock-coupling, chain-integrity, "
            "and migration-floor guards. --dry-run reports the would-move set and "
            "mutates nothing."
        ),
        epilog=build_epilog(
            [
                "gz handoff archive --older-than 30d --dry-run",
                "gz handoff archive --older-than 30d",
            ]
        ),
    )
    p_archive.add_argument(
        "--older-than",
        dest="older_than",
        required=True,
        help="Age threshold, e.g. 30d — handoffs older than this are eligible",
    )
    p_archive.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Report the would-move set without moving anything",
    )
    add_json_flag(p_archive)
    p_archive.set_defaults(
        func=lambda a: _lazy("handoff_archive_cmd")(
            older_than=a.older_than,
            dry_run=a.dry_run,
            as_json=a.as_json,
        )
    )


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

    p_test_shape = commands.add_parser(
        "test-shape",
        help="Advisory inventory of test-shape debt (tautological + output assertions)",
        description=(
            "Report advisory test-shape debt: tautological-shaped operations with their "
            "proposed disposition, and output/render assertions with whether their "
            "output-form carve-out is declared. Always exits 0 -- this is a reporting "
            "surface, never a gate (GHI #571)."
        ),
        epilog=build_epilog(
            [
                "gz test-shape",
                "gz test-shape --kind tautological",
                "gz test-shape --kind output --undeclared-only",
                "gz test-shape --json",
            ]
        ),
    )
    p_test_shape.add_argument(
        "--kind",
        choices=["tautological", "output", "all"],
        default="all",
        help="Which screen to report (default: all).",
    )
    p_test_shape.add_argument(
        "--undeclared-only",
        dest="undeclared_only",
        action="store_true",
        help="Show only output assertions with no declared output-form carve-out.",
    )
    add_json_flag(p_test_shape)
    p_test_shape.set_defaults(
        func=lambda a: _lazy("test_shape_cmd")(
            kind=a.kind, undeclared_only=a.undeclared_only, as_json=a.as_json
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
    p_covers.add_argument(
        "--bypass-req-kind-discipline-once",
        dest="bypass_req_kind_discipline_once",
        action="store_true",
        default=False,
        help="Skip parity gate; emits bypass_used event (requires --bypass-reason)",
    )
    p_covers.add_argument(
        "--bypass-reason",
        dest="bypass_reason",
        default=None,
        help="Reason for bypass (required with --bypass-req-kind-discipline-once)",
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
            bypass_req_kind_discipline_once=a.bypass_req_kind_discipline_once,
            bypass_reason=a.bypass_reason,
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
        help="Validate OBPI briefs with lifecycle-aware authored/completed gates",
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
        help="ADR ID (--frontmatter) or path list (--sensitivity)",
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
    p_validate.add_argument(
        "--utf8-prefix",
        dest="check_utf8_prefix",
        action="store_true",
        help="Forbid `PYTHONUTF8=1 uv run gz` anti-pattern in docs/skills",
    )
    p_validate.add_argument(
        "--line-endings",
        dest="check_line_endings",
        action="store_true",
        help="Fail closed on CRLF text surfaces or a missing .gitattributes LF rule",
    )
    p_validate.add_argument(
        "--test-tiers",
        dest="check_test_tiers",
        action="store_true",
        help="Forbid third test tier under tests/ (integration/e2e/slow/bdd)",
    )
    p_validate.add_argument(
        "--pydantic-models",
        dest="check_pydantic_models",
        action="store_true",
        help="Governance classes use Pydantic BaseModel + ConfigDict, not @dataclass",
    )
    p_validate.add_argument(
        "--class-size",
        dest="check_class_size",
        action="store_true",
        help="Classes under src/gzkit/ <=300 lines unless explicitly waived",
    )
    p_validate.add_argument(
        "--version-release",
        dest="check_version_release",
        action="store_true",
        help="pyproject version has a matching vX.Y.Z git tag",
    )
    p_validate.add_argument(
        "--pool-adr-isolation",
        dest="check_pool_adr_isolation",
        action="store_true",
        help="Pool ADRs never receive runtime-track lifecycle/gate events",
    )
    p_validate.add_argument(
        "--behave-req-tags",
        dest="check_behave_req_tags",
        action="store_true",
        help="Heavy OBPI REQs have @REQ-* scenario tags under features/",
    )
    p_validate.add_argument(
        "--skill-alignment",
        dest="check_skill_alignment",
        action="store_true",
        help="Every CLI verb has a wielding skill (Invariant 1)",
    )
    p_validate.add_argument(
        "--advisory-scorecard",
        dest="check_advisory_scorecard",
        action="store_true",
        help="Every .gzkit/rules file appears in advisory-rules-audit scorecard",
    )
    p_validate.add_argument(
        "--complexity-doctrine-links",
        dest="check_complexity_doctrine_links",
        action="store_true",
        help="Audit ADR-0.0.27 complexity-doctrine citations resolve (link integrity)",
    )
    p_validate.add_argument(
        "--complexity-thresholds",
        dest="check_complexity_thresholds",
        action="store_true",
        help="Audit ADR-0.0.28 complexity-thresholds rule body shape and citation",
    )
    p_validate.add_argument(
        "--reconcile-freshness",
        dest="check_reconcile_freshness",
        action="store_true",
        help="Flag if no reconcile event since HEAD (grace: 24h)",
    )
    p_validate.add_argument(
        "--insights-shape",
        dest="check_insights_shape",
        action="store_true",
        help="Validate `.gzkit/insights/agent-insights.jsonl` records (GHI #358)",
    )
    p_validate.add_argument(
        "--instructions-files-budget",
        dest="check_instructions_files_budget",
        action="store_true",
        help="AGENTS.md/CLAUDE.md/.claude/rules char budget (GHI #373)",
    )
    p_validate.add_argument(
        "--agents-md-map-conformance",
        dest="check_agents_md_map_conformance",
        action="store_true",
        help="AGENTS.md template + rendered shape conformance (ADR-0.0.54 / OBPI-0.0.54-03)",
    )
    p_validate.add_argument(
        "--adr-status-fresh",
        dest="check_adr_status_fresh",
        action="store_true",
        help="adr-status.md must agree with on-disk ADR canon (GHI #322)",
    )
    p_validate.add_argument(
        "--obpi-lifecycle-coherence",
        dest="check_obpi_lifecycle_coherence",
        action="store_true",
        help="every obpi_created must be terminal, parked, or parented (GHI #584)",
    )
    p_validate.add_argument(
        "--adversarial-validation",
        dest="check_adversarial_validation",
        action="store_true",
        help="Step-4b adversary verdict must be in the ledger and the brief (GHI #676)",
    )
    p_validate.add_argument(
        "--red-parity",
        dest="check_red_parity",
        action="store_true",
        help="BEHAVIOR REQs must carry a base-tree RED falsifiability witness (GHI #642)",
    )
    p_validate.add_argument(
        "--session-green-gate",
        dest="check_session_green_gate",
        action="store_true",
        help="pre-push gz check hook must be declared in .pre-commit-config.yaml (ADR-0.0.68)",
    )
    p_validate.add_argument(
        "--orientation-freshness",
        dest="check_orientation_freshness",
        action="store_true",
        help="SessionStart orientation hook + script must remain wired (GHI #341)",
    )
    p_validate.add_argument(
        "--taxonomy",
        dest="check_taxonomy",
        action="store_true",
        help="Enforce ADR kind/semver/id-prefix consistency (ADR-0.0.17)",
    )
    p_validate.add_argument(
        "--brief-headings",
        dest="check_brief_headings",
        action="store_true",
        help="Brief evidence sections must be H3, not H2 (GHI #238)",
    )
    p_validate.add_argument(
        "--brief-cross-references",
        dest="check_brief_cross_references",
        action="store_true",
        help="Brief OBPI/ADR identifier references must resolve on-disk (GHI #436)",
    )
    p_validate.add_argument(
        "--brief-demo-section",
        dest="check_brief_demo_section",
        action="store_true",
        help="Heavy-lane CLI-shipping briefs must carry a ## Demo H2 section (GHI #431)",
    )
    p_validate.add_argument(
        "--chores-layout",
        dest="check_chores_layout",
        action="store_true",
        help="Forbid CHORE.md/acceptance.json outside canonical chores roots (ADR-0.0.21)",
    )
    p_validate.add_argument(
        "--unscoped-rules",
        dest="check_unscoped_rules",
        action="store_true",
        help="Fail on .gzkit/rules/*.md with paths: '**' or missing paths: (ADR-0.0.20)",
    )
    p_validate.add_argument(
        "--rule-version-markers",
        dest="check_rule_version_markers",
        action="store_true",
        help="Fail on .gzkit/rules/*.md missing or drifting the rule-version marker",
    )
    p_validate.add_argument(
        "--sensitivity",
        dest="check_sensitivity",
        action="store_true",
        help="Audit ADR-0.0.22 sensitivity binding (auto-detect floor)",
    )
    p_validate.add_argument(
        "--allowlist-only",
        dest="unscoped_rules_allowlist_only",
        action="store_true",
        help="With --unscoped-rules: list current allowlist entries and exit 0",
    )
    p_validate.add_argument(
        "--doc-surface-parity",
        dest="check_doc_surface_parity",
        action="store_true",
        help="Fail if docs/user/commands/ exists (decommissioned, GHI #418)",
    )
    p_validate.add_argument(
        "--absorption-duplicates",
        dest="check_absorption_duplicates",
        action="store_true",
        help="Same opsdev source path across parent ADRs needs paired_with: (GHI #376)",
    )
    p_validate.add_argument(
        "--orphaned-implementation",
        dest="check_orphaned_implementation",
        action="store_true",
        help="Lock force-released after allowed-path edits without completion (GHI #438)",
    )
    p_validate.add_argument(
        "--evaluation-justify-binding",
        dest="check_evaluation_justify_binding",
        nargs="?",
        const="__all__",
        metavar="ARTIFACT_ID",
        help="Require gz-justify artifact for low eval scores (ADR-0.0.26).",
    )
    p_validate.add_argument(
        "--intrinsic-attestation",
        dest="check_intrinsic_attestation",
        action="store_true",
        help="Validate intrinsic-complexity-attestation ledger event shapes (OBPI-0.0.29-07).",
    )
    p_validate.add_argument(
        "--advisor-proof-binding",
        dest="check_advisor_proof_binding",
        action="store_true",
        help="Audit advisor verdict <-> proof binding (OBPI-0.0.29-08).",
    )
    p_validate.add_argument(
        "--lock-handoff-coupling",
        dest="check_lock_handoff_coupling",
        action="store_true",
        default=False,
        help="Validate obpi_lock_released events carry a valid handoff_path (ADR-0.0.41).",
    )
    p_validate.add_argument(
        "--qc-binding",
        dest="check_qc_binding",
        action="store_true",
        default=False,
        help="Behavioral QC-step binding audit (ADR-0.0.73). Exit 0: clean; 3: theater found.",
    )
    p_validate.add_argument(
        "--fidelity-presence",
        dest="check_fidelity_presence",
        action="store_true",
        default=False,
        help="ADR Fidelity Assertions presence gate (ADR-0.0.73). Exit 0: ok; 3: missing.",
    )
    p_validate.add_argument(
        "--waiver-ratchet",
        dest="check_waiver_ratchet",
        action="store_true",
        default=False,
        help="Waiver-ratchet honesty gate (ADR-0.0.73). Exit 0: ratcheted; 3: unratcheted.",
    )
    p_validate.add_argument(
        "--closeout-proof",
        dest="check_closeout_proof",
        action="store_true",
        default=False,
        help="Derived closeout-proof view (ADR-0.0.69). Exit 0: all proven; 3: unproven.",
    )
    p_validate.add_argument(
        "--deprecated-verb-prescription",
        dest="check_deprecated_verb_prescription",
        action="store_true",
        default=False,
        help="Governed surfaces must not prescribe a deprecated verb. Exit 3 on any (#705).",
    )
    p_validate.add_argument(
        "--okf-conformance",
        dest="check_okf_conformance",
        action="store_true",
        default=False,
        help="OKF generated-bundle conformance (ADR-0.30.0). Exit 0: clean; 3: malformed file.",
    )
    p_validate.add_argument(
        "--invariant-coherence",
        dest="check_invariant_coherence",
        action="store_true",
        default=False,
        help="Validate that AGENTS.md matches the rendered constitutional invariant registry.",
    )
    p_validate.add_argument(
        "--router-tables",
        dest="check_router_tables",
        action="store_true",
        default=False,
        help="Router slugs resolve; concrete skills are router-reachable (ADR-0.27.0).",
    )
    p_validate.add_argument(
        "--brief-reconcile",
        dest="check_brief_reconcile",
        action="store_true",
        help="Validate OBPI brief corpus drift across five dimensions (OBPI-0.0.37-05).",
    )
    p_validate.add_argument(
        "--distribution",
        dest="check_distribution",
        action="store_true",
        help="T0 static distribution audit — three drift classes, exit 3 (ADR-0.0.32-07).",
    )
    p_validate.add_argument(
        "--changelog",
        dest="check_changelog",
        action="store_true",
        help="Hermetic CHANGELOG.md structural audit — shape + citations (GHI #685).",
    )
    p_validate.add_argument(
        "--bullet-retention",
        dest="check_bullet_retention",
        action="store_true",
        help="Bullet-retention audit: scorecard Mechanical/Promotable bullets in surface.",
    )
    p_validate.add_argument(
        "--surface-weight",
        dest="check_surface_weight",
        action="store_true",
        help="Surface-weight audit: direction-binding floor + warning bands (ADR-0.0.33-02).",
    )
    p_validate.add_argument(
        "--pointer-anchors",
        dest="check_pointer_anchors",
        action="store_true",
        help="Pointer-integrity audit: > See [...] anchors (ADR-0.0.33-03).",
    )
    p_validate.add_argument(
        "--scenario-reachability",
        dest="check_scenario_reachability",
        action="store_true",
        help="Scenario-reachability: orphan bullets vs loading scenarios (ADR-0.0.33-04).",
    )
    p_validate.add_argument(
        "--surface-fidelity",
        dest="check_surface_fidelity",
        action="store_true",
        help="Composite: run all four surface-fidelity invariants (ADR-0.0.33-05).",
    )
    p_validate.add_argument(
        "--vendor-manifest",
        dest="check_vendor_manifest",
        action="store_true",
        help="Validate vendor manifest schema and content-type route drift (ADR-0.0.34).",
    )
    p_validate.add_argument(
        "--setpoint-coherence",
        dest="check_setpoint_coherence",
        action="store_true",
        help="Every content_type_routes pair has a legal declared setpoint (OBPI-0.0.37-20).",
    )
    p_validate.add_argument(
        "--rendition-freshness",
        dest="check_rendition_freshness",
        action="store_true",
        default=False,
        help="Fail-closed when corpus drifted from committed rendition (OBPI-0.0.37-22).",
    )
    p_validate.add_argument(
        "--rendition-floor-coherence",
        dest="check_rendition_floor_coherence",
        action="store_true",
        default=False,
        help="Rendition omits a corpus invariant-tier entry; fail-closed (GHI #623).",
    )
    p_validate.add_argument(
        "--kind-invariance",
        dest="check_kind_invariance",
        action="store_true",
        help="Validate foundation ADRs have Why-foundation-tier section",
    )
    p_validate.add_argument(
        "--receipt-shape",
        dest="check_receipt_shape",
        action="store_true",
        help="Refuse deprecated receipt shapes post-ADR-0.0.36 cutoff (exit 3)",
    )
    p_validate.add_argument(
        "--req-kind-discipline",
        dest="check_req_kind_discipline",
        action="store_true",
        default=False,
        help="Fail closed (exit 3) on OBPI briefs with missing [kind] tags (ADR-0.0.59-02).",
    )
    p_validate.add_argument(
        "--ontology-purity",
        dest="check_ontology_purity",
        action="store_true",
        default=False,
        help="Fail closed (exit 3) on a product object in ownership:harness (ADR-0.32.0-01).",
    )
    p_validate.add_argument(
        "--brief-command-shape",
        dest="check_brief_command_shape",
        action="store_true",
        default=False,
        help="Fail closed (exit 3) on non-shell-less Verification commands (OBPI-0.0.63-07).",
    )
    p_validate.add_argument(
        "--tautological-test-audit",
        dest="check_tautological_test_audit",
        action="store_true",
        default=False,
        help="Fail closed (exit 3) when tautological-test count drifts (OBPI-0.0.59-04).",
    )
    p_validate.add_argument(
        "--task-envelope-coherence",
        dest="check_task_envelope_coherence",
        action="store_true",
        default=False,
        help="Fail-close (exit 3) on TASK attribution drift (ADR-0.0.64/OBPI-04).",
    )
    p_validate.add_argument(
        "--regenerate",
        dest="check_distribution_regenerate",
        action="store_true",
        help="Rewrite baseline manifest from on-disk truth. Use with --distribution.",
    )
    p_validate.add_argument(
        "--attestation-receipts",
        dest="attestation_receipts",
        default=None,
        metavar="<text|@file>",
        help="Validate ARB receipt citations in an attestation string (ADR-0.0.24)",
    )
    p_validate.add_argument(
        "--lane",
        dest="attestation_lane",
        default="heavy",
        choices=("heavy", "lite"),
        help="Lane for --attestation-receipts (default: heavy)",
    )
    p_validate.add_argument(
        "--kind",
        dest="attestation_kind",
        default="feature",
        choices=("foundation", "feature"),
        help="Kind for --attestation-receipts (default: feature)",
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
            check_utf8_prefix=a.check_utf8_prefix,
            check_line_endings=a.check_line_endings,
            check_test_tiers=a.check_test_tiers,
            check_pydantic_models=a.check_pydantic_models,
            check_class_size=a.check_class_size,
            check_version_release=a.check_version_release,
            check_pool_adr_isolation=a.check_pool_adr_isolation,
            check_behave_req_tags=a.check_behave_req_tags,
            check_skill_alignment=a.check_skill_alignment,
            check_advisory_scorecard=a.check_advisory_scorecard,
            check_complexity_doctrine_links=a.check_complexity_doctrine_links,
            check_complexity_thresholds=a.check_complexity_thresholds,
            check_reconcile_freshness=a.check_reconcile_freshness,
            check_insights_shape=a.check_insights_shape,
            check_instructions_files_budget=a.check_instructions_files_budget,
            check_agents_md_map_conformance=a.check_agents_md_map_conformance,
            check_adr_status_fresh=a.check_adr_status_fresh,
            check_obpi_lifecycle_coherence=a.check_obpi_lifecycle_coherence,
            check_adversarial_validation=a.check_adversarial_validation,
            check_red_parity=a.check_red_parity,
            check_session_green_gate=a.check_session_green_gate,
            check_orientation_freshness=a.check_orientation_freshness,
            check_taxonomy=a.check_taxonomy,
            check_brief_headings=a.check_brief_headings,
            check_brief_cross_references=a.check_brief_cross_references,
            check_brief_demo_section=a.check_brief_demo_section,
            check_chores_layout=a.check_chores_layout,
            check_unscoped_rules=a.check_unscoped_rules or a.check_audits,
            check_rule_version_markers=a.check_rule_version_markers,
            unscoped_rules_allowlist_only=a.unscoped_rules_allowlist_only,
            check_sensitivity=a.check_sensitivity or a.check_audits,
            sensitivity_explain=(a.frontmatter_explain if a.check_sensitivity else None),
            check_doc_surface_parity=a.check_doc_surface_parity or a.check_audits,
            check_absorption_duplicates=a.check_absorption_duplicates,
            check_orphaned_implementation=(a.check_orphaned_implementation or a.check_audits),
            check_evaluation_justify_binding=(a.check_evaluation_justify_binding),
            check_intrinsic_attestation=a.check_intrinsic_attestation,
            check_advisor_proof_binding=a.check_advisor_proof_binding,
            check_lock_handoff_coupling=a.check_lock_handoff_coupling,
            check_qc_binding=a.check_qc_binding,
            check_fidelity_presence=a.check_fidelity_presence,
            check_waiver_ratchet=a.check_waiver_ratchet,
            check_invariant_coherence=a.check_invariant_coherence,
            check_brief_reconcile=a.check_brief_reconcile,
            check_router_tables=a.check_router_tables,
            check_req_kind_discipline=a.check_req_kind_discipline,
            check_ontology_purity=a.check_ontology_purity,
            check_brief_command_shape=a.check_brief_command_shape,
            check_tautological_test_audit=a.check_tautological_test_audit,
            check_task_envelope_coherence=a.check_task_envelope_coherence,
            check_closeout_proof=a.check_closeout_proof,
            check_okf_conformance=a.check_okf_conformance,
            check_deprecated_verb_prescription=a.check_deprecated_verb_prescription,
            check_distribution=a.check_distribution,
            check_distribution_regenerate=a.check_distribution_regenerate,
            check_changelog=a.check_changelog,
            check_bullet_retention=a.check_bullet_retention,
            check_surface_weight=a.check_surface_weight,
            check_pointer_anchors=a.check_pointer_anchors,
            check_scenario_reachability=a.check_scenario_reachability,
            check_surface_fidelity=a.check_surface_fidelity,
            check_vendor_manifest=a.check_vendor_manifest,
            check_setpoint_coherence=a.check_setpoint_coherence,
            check_rendition_freshness=a.check_rendition_freshness,
            check_rendition_floor_coherence=a.check_rendition_floor_coherence,
            check_kind_invariance=a.check_kind_invariance,
            check_receipt_shape=a.check_receipt_shape,
            attestation_receipts=a.attestation_receipts,
            attestation_lane=a.attestation_lane,
            attestation_kind=a.attestation_kind,
            as_json=a.as_json,
            frontmatter_adr=a.frontmatter_adr,
            frontmatter_explain=(None if a.check_sensitivity else a.frontmatter_explain),
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

    p_chores_list = chores_commands.add_parser(
        "list",
        help="List chores from registry",
        description="Display all registered chores and their status.",
        epilog=build_epilog(["gz chores list", "gz chores list --explain"]),
    )
    p_chores_list.add_argument(
        "--explain",
        action="store_true",
        help="Show which resolution path (project|package) won per chore.",
    )
    p_chores_list.set_defaults(
        func=lambda a: _lazy("chores_list")(explain=a.explain),
    )

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

    p_chores_doctor = chores_commands.add_parser(
        "doctor",
        help="Re-scaffold missing or damaged canonical chores; preserve proofs/",
        description=(
            "Inspect .gzkit/chores/ for missing or damaged canonical slugs and "
            "restore them from the package source. Project-local slugs and "
            "proofs/ content are never modified."
        ),
        epilog=build_epilog(
            ["gz chores doctor", "gz chores doctor --dry-run", "gz chores doctor --json"]
        ),
    )
    p_chores_doctor.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be repaired without making any changes.",
    )
    p_chores_doctor.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit one JSON record per slug to stdout (slug, before_status, after_status).",
    )
    p_chores_doctor.set_defaults(
        func=lambda a: _lazy("chores_doctor")(dry_run=a.dry_run, json_output=a.json_output)
    )

    p_chores_propose_ghi = chores_commands.add_parser(
        "propose-ghi",
        help="File GHI proposals for unfiled cluster proposal records",
        description=(
            "Read proposal-*.json files from a chore's proofs/ directory and file "
            "GitHub issues for unfiled proposals (TTY mode) or mark them advisory-only "
            "(headless mode). Requires a TTY and PROPOSE confirmation to create issues."
        ),
        epilog=build_epilog(["gz chores propose-ghi eval-feedback-cluster"]),
    )
    p_chores_propose_ghi.add_argument("slug", help="Chore slug identifier")
    p_chores_propose_ghi.set_defaults(func=lambda a: _lazy("chores_propose_ghi")(slug=a.slug))


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
                "gz flag explain ops.product_proof --json",
            ]
        ),
    )
    p_explain.add_argument("key", help="Dotted flag key (e.g. ops.product_proof)")
    add_json_flag(p_explain)
    p_explain.set_defaults(func=lambda a: _lazy("flag_explain_cmd")(key=a.key, as_json=a.as_json))
