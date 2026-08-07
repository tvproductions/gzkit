"""Artifact-focused subparser registrations for gz CLI.

Registers: adr subcommands, obpi subcommands, task subcommands, issue subcommands.

Command handlers are resolved on demand via ``_lazy`` so ``gz --help``
avoids pulling heavy handler dependencies. Each handler's module lives in
``_LAZY_HANDLERS``; ``_lazy`` imports the module on first call and caches
the resolved callable.
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

_ADR_TYPE_NAMES = {"foundation", "feature", "pool"}


def _dispatch_adr_report(a: argparse.Namespace) -> None:
    """Route gz adr report to summary or detail mode."""
    target = a.adr
    if target and target.lower() in _ADR_TYPE_NAMES:
        _lazy("adr_report_cmd")(adr=None, adr_type=target.lower())
    else:
        _lazy("adr_report_cmd")(adr=target, adr_type=a.type)


def register_artifact_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the artifact parser groups.

    Covers adr, obpi, task, justify, knowledge, issue, complexity, governance,
    and context groups.
    """
    _register_adr_parsers(commands)
    _register_obpi_parsers(commands)
    _register_task_parsers(commands)
    _register_justify_parser(commands)
    _register_knowledge_parser(commands)
    _register_issue_parsers(commands)
    _register_complexity_parsers(commands)
    _register_governance_parsers(commands)
    _register_context_parser(commands)


def _register_context_parser(commands: argparse._SubParsersAction) -> None:
    """Register the top-level ``gz context <ADR-ID>`` verb (ADR-0.28.0).

    Renders a focused Markdown context payload combining the target ADR
    body, OBPI briefs under its ``obpis/`` directory, covering-test paths
    discovered via ``@covers`` decorators, and applicable governance
    rules. ``--slim`` (OBPI-0.28.0-02) subtracts the governance section
    for non-governance harnesses.
    """
    p_context = commands.add_parser(
        "context",
        help="Render a focused context payload for one ADR-ID",
        description=(
            "Render a single Markdown document combining the target ADR's body, "
            "every OBPI brief under its obpis/ directory, the test files carrying "
            "@covers(REQ-<ADR-semver>-...) decorators, and a governance-rules "
            "section (lane, lifecycle, current gate, next required action). "
            "Output is suitable for verbatim piping to any agent harness. "
            "Exit codes: 0 success; 1 unresolvable ADR-ID."
        ),
        epilog=build_epilog(
            [
                "gz context ADR-0.0.3-hexagonal-architecture-tune-up",
                "gz context --slim ADR-0.0.3-hexagonal-architecture-tune-up",
            ]
        ),
    )
    p_context.add_argument(
        "adr",
        metavar="ADR-ID",
        help="ADR identifier (e.g., ADR-0.0.3 or ADR-0.0.3-hexagonal-architecture-tune-up)",
    )
    p_context.add_argument(
        "--slim",
        action="store_true",
        default=False,
        help="Omit governance-rules section for non-governance agent harnesses",
    )
    p_context.set_defaults(
        func=lambda a: _lazy("context_cmd")(adr=a.adr, slim=a.slim),
    )


def _register_complexity_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz complexity`` sub-command group (GHI #400).

    Currently exposes the single subverb ``distill`` that wraps the
    OBPI-0.0.27-04 distillation engine for ad-hoc operator invocation by
    the ``gz-complexity-distill`` skill. Future complexity-cluster verbs
    (``advise``, ``guide``) will land alongside under this group.
    """
    p_complexity = commands.add_parser(
        "complexity",
        help="Complexity-doctrine surfaces (distill, advise, guide)",
        description=(
            "Operator surface for the four-ADR complexity-doctrine cluster "
            "(ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30). Currently exposes the "
            "'distill' subverb that runs the measurement pipeline and emits "
            "a dated distilled-characteristics document."
        ),
        epilog=build_epilog(
            [
                "gz complexity distill",
                "gz complexity distill --corpus data/exemplar_corpus.json",
                "gz complexity distill --baseline-json fixtures/baseline.json --no-prior",
            ]
        ),
    )
    complexity_commands = p_complexity.add_subparsers(dest="complexity_command")
    complexity_commands.required = True

    p_distill = complexity_commands.add_parser(
        "distill",
        help="Run a distillation pass and write a distilled-characteristics document",
        description=(
            "Compose the OBPI-0.0.27-03 measurement pipeline with the "
            "OBPI-0.0.27-04 distillation render. Loads the corpus from "
            "--corpus, runs measurement to --baseline-dir, and writes a dated "
            "distilled-characteristics-{YYYY-MM-DD}.md under --output-dir. "
            "Use --baseline-json to inject a pre-built baseline and skip "
            "measurement (test path; agent-runs use --corpus)."
        ),
        epilog=build_epilog(
            [
                "gz complexity distill",
                "gz complexity distill --corpus data/exemplar_corpus.json",
                "gz complexity distill --baseline-json baseline.json --no-prior",
                "gz complexity distill --today 2026-05-05 --allow-dated-sibling",
            ]
        ),
    )
    p_distill.add_argument(
        "--corpus",
        default=None,
        help=f"Corpus JSON path (default: {DEFAULT_CORPUS_PATH_DISPLAY})",
    )
    p_distill.add_argument(
        "--baseline-json",
        dest="baseline_json",
        default=None,
        help="Pre-built baseline JSON (skip measurement; mutually exclusive with --corpus run)",
    )
    p_distill.add_argument(
        "--output-dir",
        dest="output_dir",
        default=None,
        help=f"Distilled-document output directory (default: {DEFAULT_OUTPUT_DIR_DISPLAY})",
    )
    p_distill.add_argument(
        "--baseline-dir",
        dest="baseline_dir",
        default=None,
        help="Baseline output directory (default: <output-dir>/baselines/<today>/)",
    )
    p_distill.add_argument(
        "--prior",
        default=None,
        help="Prior distilled-characteristics document path (default: latest in output-dir)",
    )
    p_distill.add_argument(
        "--no-prior",
        dest="no_prior",
        action="store_true",
        help="Treat as cold start; skip prior auto-detection",
    )
    p_distill.add_argument(
        "--allow-dated-sibling",
        dest="allow_dated_sibling",
        action="store_true",
        help="On same-date collision, write a -1-suffixed sibling instead of failing",
    )
    p_distill.add_argument(
        "--today",
        dest="today_override",
        default=None,
        help="Override today's date (YYYY-MM-DD; for testing)",
    )
    p_distill.set_defaults(
        func=lambda a: _lazy("complexity_distill_cmd")(
            corpus=a.corpus,
            baseline_json=a.baseline_json,
            output_dir=a.output_dir,
            baseline_dir=a.baseline_dir,
            prior=a.prior,
            no_prior=a.no_prior,
            allow_dated_sibling=a.allow_dated_sibling,
            today_override=a.today_override,
        )
    )

    p_advise = complexity_commands.add_parser(
        "advise",
        help="Run the complexity advisor against a file or directory",
        description=(
            "Runs the OBPI-0.0.29-02 diagnosis engine against the file or "
            "directory at PATH. Loads the canonical threshold table from "
            ".gzkit/rules/complexity-thresholds.json (ADR-0.0.28), measures "
            "per-function radon_cc via radon's Python API, and emits an "
            "AdvisorDiagnosis for every band crossing. Default output is "
            "structured prose; --json emits the canonical Pydantic "
            "serialization. Exit codes: 0 success or warn-band crossings, "
            "1 user/config error, 2 system/IO error, 3 block-band crossing."
        ),
        epilog=build_epilog(
            [
                "gz complexity advise src/gzkit/commands/validate.py",
                "gz complexity advise src/gzkit/ --json",
                "gz complexity advise tests/ --quiet",
            ]
        ),
    )
    p_advise.add_argument(
        "path",
        help="File or directory to analyze (recursive on directories)",
    )
    p_advise.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit AdvisorDiagnosis list as a JSON array (machine-readable)",
    )
    p_advise.add_argument(
        "--quiet",
        action="store_true",
        help="Errors only (no progress output)",
    )
    p_advise.add_argument(
        "--verbose",
        action="store_true",
        help="Debug output (per-file analysis trace)",
    )
    add_dry_run_flag(p_advise)
    p_advise.add_argument(
        "--auto-chain",
        dest="auto_chain",
        action="store_true",
        help="Trigger-fired run; selects condensed commit-time presentation",
    )
    p_advise.add_argument(
        "--rule-path",
        dest="rule_path",
        default=None,
        help="Override threshold data path (default: .gzkit/rules/complexity-thresholds.json)",
    )
    p_advise.add_argument(
        "--attest-intrinsic",
        dest="attest_intrinsic",
        action="store_true",
        help="Commit-time intrinsic attestation; requires <file>:<qualname> as path",
    )
    p_advise.add_argument(
        "--reason",
        dest="reason",
        default=None,
        help="Rationale for intrinsic attestation (required with --attest-intrinsic)",
    )
    p_advise.add_argument(
        "--attestor",
        dest="attestor",
        default=None,
        help="Full name of the attesting human (required with --attest-intrinsic)",
    )
    p_advise.set_defaults(
        func=lambda a: _lazy("complexity_advise_cmd")(
            path=a.path,
            json_output=a.json_output,
            quiet=a.quiet,
            verbose=a.verbose,
            dry_run=a.dry_run,
            auto_chain=a.auto_chain,
            rule_path=a.rule_path,
            attest_intrinsic=a.attest_intrinsic,
            reason=a.reason,
            attestor=a.attestor,
        )
    )

    p_guide = complexity_commands.add_parser(
        "guide",
        help="Surface authoring-time complexity hints for a file or directory",
        description=(
            "Reads the advise band from the canonical threshold table "
            "(.gzkit/rules/complexity-thresholds.json, ADR-0.0.28), measures "
            "the target file or directory, and emits AuthoringHint blocks for "
            "functions approaching the warn threshold. Exit 3 is NOT used — "
            "this surface never blocks; that is gz complexity advise's role."
        ),
        epilog=build_epilog(
            [
                "gz complexity guide src/gzkit/commands/validate.py",
                "gz complexity guide src/gzkit/ --json",
            ]
        ),
    )
    p_guide.add_argument("path", nargs="?", default=None, help="File or directory to analyze")
    p_guide.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit canonical AuthoringHint JSON array to stdout",
    )
    p_guide.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output; rely on exit code only",
    )
    p_guide.add_argument(
        "--verbose",
        action="store_true",
        help="Emit debug output to stderr",
    )
    p_guide.add_argument(
        "--server",
        action="store_true",
        default=False,
        help="Start JSON-over-stdio LSP-style protocol server for editor/IDE integration.",
    )
    p_guide.set_defaults(
        func=lambda a: _lazy("complexity_guide_cmd")(
            path=a.path,
            json_output=a.json_output,
            quiet=a.quiet,
            verbose=a.verbose,
            server=a.server,
        )
    )


def _register_governance_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz governance`` sub-command group (ADR-0.0.37, OBPI-0.0.37-02).

    Exposes the ``render`` subverb that projects the constitutional invariant
    registry into a governance surface (initially ``agents-md``).
    """
    p_gov = commands.add_parser(
        "governance",
        help="Constitutional invariant governance commands",
        description="Commands for rendering governance surfaces from the invariant registry.",
        epilog=build_epilog(
            [
                "gz governance render --target agents-md --check",
                "gz governance render --target agents-md --stdout",
                "gz governance render --target agents-md",
            ]
        ),
    )
    gov_commands = p_gov.add_subparsers(dest="governance_command")
    gov_commands.required = True

    p_render = gov_commands.add_parser(
        "render",
        help="Render a governance surface from the constitutional invariant registry",
        description=(
            "Render a governance surface from the invariant registry at "
            "``.gzkit/invariants/``. Output is byte-deterministic. "
            "Supports ``--check`` (drift detection) and ``--stdout`` (inspection)."
        ),
        epilog=build_epilog(
            [
                "gz governance render --target agents-md --check",
                "gz governance render --target agents-md --stdout",
                "gz governance render --target agents-md",
            ]
        ),
    )
    p_render.add_argument(
        "--target",
        required=True,
        help="Render target. Only 'agents-md' is supported at this time.",
    )
    p_render.add_argument(
        "--check",
        action="store_true",
        help="Byte-compare rendered output against the committed file. Exit 3 on drift.",
    )
    p_render.add_argument(
        "--stdout",
        action="store_true",
        help="Emit rendered bytes to stdout. Does not write the file.",
    )
    p_render.set_defaults(
        func=lambda a: _lazy("governance_render_cmd")(
            target=a.target, check=a.check, stdout=a.stdout
        )
    )


# Display strings for help text — live values are re-imported in the handler so
# the parser does not pull the heavy complexity stack at ``gz --help`` time.
DEFAULT_CORPUS_PATH_DISPLAY = "data/exemplar_corpus.json"
DEFAULT_OUTPUT_DIR_DISPLAY = "docs/governance/complexity"


def _register_justify_parser(commands: argparse._SubParsersAction) -> None:
    """Register the top-level ``gz justify`` verb (ADR-0.0.19).

    Supports two invocation shapes (OBPI-03 introduced the subverb form):

    * ``gz justify <anchor> [--save] [--output] [--related] [--draft] [--draft-slug]``
      — scaffold rendering (OBPI-02 default behavior).
    * ``gz justify validate <file> [--json]`` — reverse-parse a filled
      walkthrough and report structural completeness (OBPI-03).

    Argparse cannot natively mix a positional with subparsers, so we keep a
    flat parser and dispatch on the first positional: if it is the literal
    string ``"validate"``, the handler routes to the validate subverb and
    treats the second positional as ``<file>``; otherwise the first
    positional is the anchor identifier and the scaffold path runs. This
    preserves backward-compatibility with ``gz justify GHI-232`` from
    OBPI-02.
    """
    p_justify = commands.add_parser(
        "justify",
        help="Produce a reasoning scaffold, or validate a filled walkthrough",
        description=(
            "Scaffold an 8-section pre-execution reasoning walkthrough for a "
            "GHI, OBPI, or draft anchor, or validate a filled walkthrough "
            "markdown file via the 'validate' subverb. The CLI never invokes "
            "an LLM; the scaffold renders deterministically from gathered "
            "evidence, and validate reverse-parses filled markdown into the "
            "same Pydantic model used for rendering. "
            "Exit codes for 'validate': 0 parseable and complete; 1 "
            "parseable but incomplete (lists unfilled sections); 2 "
            "unparseable markdown."
        ),
        epilog=build_epilog(
            [
                "gz justify GHI-232",
                "gz justify GHI-232 --save",
                "gz justify --draft 'proposal text' --save --draft-slug my-idea",
                "gz justify validate path/to/walkthrough.md",
                "gz justify validate path/to/walkthrough.md --json",
            ]
        ),
    )
    p_justify.add_argument(
        "anchor_or_subverb",
        nargs="?",
        default=None,
        metavar="<anchor>|validate",
        help="Anchor (GHI/OBPI) or literal 'validate'; omit with --draft",
    )
    p_justify.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Filled walkthrough markdown file (validate subverb only)",
    )
    p_justify.add_argument(
        "--save",
        action="store_true",
        help="Write scaffold to artifacts/justify/<slug>-<timestamp>.md",
    )
    p_justify.add_argument(
        "--output",
        default=None,
        help="Write scaffold to explicit path (must not exist)",
    )
    p_justify.add_argument(
        "--related",
        default=None,
        help="Comma-separated list of related anchors for evidence context",
    )
    p_justify.add_argument(
        "--draft",
        default=None,
        help="Literal draft text in place of a resolvable anchor",
    )
    p_justify.add_argument(
        "--draft-slug",
        default=None,
        help="Slug used to name --save output when combined with --draft",
    )
    p_justify.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="(validate subverb) Emit ValidateResult JSON instead of a sentence",
    )
    p_justify.set_defaults(
        func=lambda a: _lazy("justify_cmd")(
            subverb=("validate" if a.anchor_or_subverb == "validate" else None),
            anchor=(None if a.anchor_or_subverb == "validate" else a.anchor_or_subverb),
            file=(a.file if a.anchor_or_subverb == "validate" else None),
            json_output=a.json_output,
            save=a.save,
            output=a.output,
            related=a.related,
            draft=a.draft,
            draft_slug=a.draft_slug,
        )
    )


def _register_knowledge_parser(commands: argparse._SubParsersAction) -> None:
    """Register the top-level ``gz knowledge`` verb (ADR-0.30.0, OBPI-0.30.0-04).

    Supports generating and refreshing the OKF orientation bundle over the
    governance tracer slice (state doctrine, trust doctrine, agent-contract
    rationale, active campaign).
    """
    p_knowledge = commands.add_parser(
        "knowledge",
        help="Generate or refresh OKF knowledge bundle",
        description=(
            "Generate an OKF-conformant markdown bundle over the governance "
            "tracer slice (state doctrine, trust doctrine, agent-contract "
            "rationale, active campaign). The bundle provides typed frontmatter "
            "and markdown links for agents to navigate documentation."
        ),
        epilog=build_epilog(
            [
                "gz knowledge generate",
                "gz knowledge refresh",
            ]
        ),
    )

    knowledge_commands = p_knowledge.add_subparsers(
        dest="knowledge_command",
        help="Subcommand to execute",
    )
    knowledge_commands.required = True

    # Register 'generate' subcommand
    p_generate = knowledge_commands.add_parser(
        "generate",
        help="Emit the OKF knowledge bundle",
        description=(
            "Generate an OKF-conformant knowledge bundle and emit it over "
            "the tracer slice. Creates markdown documents with typed frontmatter "
            "and navigation links for agents to access governance documentation."
        ),
        epilog=build_epilog(
            [
                "gz knowledge generate",
            ]
        ),
    )
    p_generate.set_defaults(func=lambda a: _lazy("knowledge_cmd")(subverb="generate"))

    # Register 'refresh' subcommand
    p_refresh = knowledge_commands.add_parser(
        "refresh",
        help="Re-generate the bundle idempotently from current sources",
        description=(
            "Re-generate the OKF knowledge bundle idempotently from current "
            "sources. Running refresh twice leaves the bundle byte-identical; "
            "idempotency ensures operator-driven bundle updates are deterministic."
        ),
        epilog=build_epilog(
            [
                "gz knowledge refresh",
            ]
        ),
    )
    p_refresh.set_defaults(func=lambda a: _lazy("knowledge_cmd")(subverb="refresh"))


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
        func=lambda a: _lazy("adr_status_cmd")(
            adr=a.adr, as_json=a.as_json, show_gates=a.show_gates
        )
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
        "--kind",
        choices=["pool", "foundation", "feature"],
        default=None,
        help="Target taxonomy: foundation (0.0.x) or feature (0.y.z). pool rejected.",
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
        func=lambda a: _lazy("adr_promote_cmd")(
            pool_adr=a.pool_adr,
            semver=a.semver,
            slug=a.slug,
            title=a.title,
            parent=a.parent,
            lane=a.lane,
            kind=a.kind,
            target_status=a.target_status,
            as_json=a.as_json,
            dry_run=a.dry_run,
            force=a.force,
        )
    )

    p_adr_demote = adr_commands.add_parser(
        "demote",
        help="Demote a feature or foundation ADR back to pool",
        description=(
            "Inverse of ``gz adr promote``: strip kind/semver frontmatter, "
            "move the ADR file from pre-release/ or foundation/ to pool/, "
            "delete the source package directory (briefs + closeout form), "
            "and emit an artifact_renamed ledger event with "
            "reason=pool_demotion."
        ),
        epilog=build_epilog(
            [
                "gz adr demote ADR-0.27.0-arb-receipt-system-absorption --ghi 520",
                "gz adr demote ADR-0.27.0 --ghi 520 --dry-run",
                "gz adr demote ADR-0.27.0 --ghi 520 --note 'queue collapse' --json",
            ]
        ),
    )
    p_adr_demote.add_argument(
        "adr_id",
        help="ADR id to demote (e.g., ADR-0.27.0-arb-receipt-system-absorption or ADR-0.27.0)",
    )
    p_adr_demote.add_argument(
        "--ghi",
        required=True,
        type=int,
        help="GitHub Issue number this demotion is tracked under (required for auditability)",
    )
    p_adr_demote.add_argument(
        "--note",
        default=None,
        help="Free-text operator rationale stored in the ledger event extras",
    )
    p_adr_demote.add_argument(
        "--operator",
        default=None,
        help="Operator identity (name only; never email per Local Agent Rules)",
    )
    add_json_flag(p_adr_demote)
    add_dry_run_flag(p_adr_demote)
    add_force_flag(
        p_adr_demote,
        help_override="Override dependent-children safety check (orphans the children)",
    )
    p_adr_demote.add_argument(
        "--on-collision",
        choices=("fail", "keep-pool"),
        default="fail",
        help="Pool-slug collision policy: fail (default) or keep-pool",
    )
    p_adr_demote.set_defaults(
        func=lambda a: _lazy("adr_demote_cmd")(
            adr_id=a.adr_id,
            ghi=a.ghi,
            note=a.note,
            operator=a.operator,
            as_json=a.as_json,
            dry_run=a.dry_run,
            force=a.force,
            on_collision=a.on_collision,
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
        func=lambda a: _lazy("adr_eval_cmd")(
            adr_id=a.adr_id,
            as_json=a.as_json,
            write_scorecard=a.write_scorecard,
        )
    )

    p_adr_audit_begin = adr_commands.add_parser(
        "audit-begin",
        help="Open an ADR audit ceremony (writes co-presence marker for Gate-5 emit)",
        description=(
            "Open an ADR audit ceremony by writing the per-ADR co-presence "
            "marker that the GHI #292 agent-relayed Gate-5 emit accepts. "
            "Pair with 'gz adr audit-end' after the validated receipt lands."
        ),
        epilog=build_epilog(["gz adr audit-begin ADR-0.1.0"]),
    )
    p_adr_audit_begin.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.4)")
    p_adr_audit_begin.set_defaults(func=lambda a: _lazy("adr_audit_begin_cmd")(adr=a.adr))

    p_adr_audit_end = adr_commands.add_parser(
        "audit-end",
        help="Close an ADR audit ceremony (removes the co-presence marker)",
        description=(
            "Close an ADR audit ceremony by removing the per-ADR marker "
            "written by 'gz adr audit-begin'. Idempotent: missing-marker "
            "is a soft warning, not an error."
        ),
        epilog=build_epilog(["gz adr audit-end ADR-0.1.0"]),
    )
    p_adr_audit_end.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.4)")
    p_adr_audit_end.set_defaults(func=lambda a: _lazy("adr_audit_end_cmd")(adr=a.adr))

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
    p_adr_audit_check.add_argument(
        "--strict",
        action="store_true",
        help="Fail-close on covers-backfill findings (lite ADRs).",
    )
    p_adr_audit_check.set_defaults(
        func=lambda a: _lazy("adr_audit_check")(adr=a.adr, as_json=a.as_json, strict=a.strict)
    )

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
    p_adr_covers_check.set_defaults(
        func=lambda a: _lazy("adr_covers_check")(adr=a.adr, as_json=a.as_json)
    )

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
        choices=["completed", "validated", "closed"],
        help="Receipt event type (completed|validated|closed)",
    )
    p_adr_emit.add_argument("--attestor", required=True, help="Identity of the attestor")
    p_adr_emit.add_argument(
        "--evidence-json",
        help="JSON with value_narrative, key_proof; Heavy adds attestation fields",
    )
    p_adr_emit.add_argument(
        "--attestor-present",
        dest="attestor_present",
        action="store_true",
        help="Agent-relayed operator attestation, gated on active pipeline marker (GHI #292)",
    )
    add_dry_run_flag(p_adr_emit)
    p_adr_emit.set_defaults(
        func=lambda a: _lazy("adr_emit_receipt_cmd")(
            adr=a.adr,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
            attestor_present=a.attestor_present,
            dry_run=a.dry_run,
        )
    )

    p_adr_fidelity = adr_commands.add_parser(
        "fidelity",
        help="Run an ADR's Fidelity Assertions against the running system",
        description=(
            "Parse the '## Fidelity Assertions' block from an ADR Decision, "
            "run each command, and compare observed-vs-expected exit code. "
            "Exits 0 when all assertions pass, 1 when any fail. "
            "Use --check to verify the block is parseable without running commands."
        ),
        epilog=build_epilog(
            [
                "gz adr fidelity ADR-0.0.73-verification-layer-binding-audit",
                "gz adr fidelity ADR-0.0.73-verification-layer-binding-audit --check",
            ]
        ),
    )
    p_adr_fidelity.add_argument("adr", help="ADR identifier (e.g. ADR-0.0.73-...)")
    p_adr_fidelity.add_argument(
        "--check",
        action="store_true",
        help="Parse-only: verify the Fidelity Assertions block is parseable (no commands run)",
    )
    p_adr_fidelity.set_defaults(
        func=lambda a: _lazy("adr_fidelity_cmd")(adr=a.adr, check_only=a.check)
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
        help="Attestor identity for Stage 5 (e.g. jeff or agent:<name>)",
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
        help="Remove pipeline markers older than 4 hours",
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
    p_task_list.set_defaults(func=lambda a: _lazy("task_list_cmd")(obpi=a.obpi, as_json=a.as_json))

    p_task_start = task_commands.add_parser(
        "start",
        help="Start or resume a task",
        description="Transition a task to in_progress (from pending or blocked).",
        epilog=build_epilog(
            [
                "gz task start TASK-0.20.0-01-01-01",
                "gz task start TASK-0.20.0-01-01-01 --json",
                "gz task start --req REQ-0.20.0-01-01 --seq next",
                "gz task start --req REQ-0.20.0-01-01 --seq 2",
            ]
        ),
    )
    p_task_start.add_argument(
        "task_id",
        nargs="?",
        help="TASK identifier (e.g. TASK-0.20.0-01-01-01); omit when using --req/--seq",
    )
    p_task_start.add_argument(
        "--req",
        metavar="REQ_ID",
        help="REQ identifier for subdivision-based start (e.g. REQ-0.0.64-03-01)",
    )
    p_task_start.add_argument(
        "--seq",
        metavar="NEXT_OR_N",
        help="Sequence value: 'next' for auto-increment, or explicit positive integer",
    )
    add_json_flag(p_task_start)

    def _dispatch_task_start(a: argparse.Namespace) -> None:
        """Route gz task start to the positional-TASK-ID or --req/--seq handler."""
        if a.req:
            if a.task_id:
                p_task_start.error("Cannot combine positional task_id with --req/--seq")
            if not a.seq:
                p_task_start.error("--seq is required when --req is provided")
            _lazy("task_start_by_req_cmd")(req_id=a.req, seq_arg=a.seq, as_json=a.as_json)
        elif a.task_id:
            _lazy("task_start_cmd")(task_id_str=a.task_id, as_json=a.as_json)
        else:
            p_task_start.error("Provide a task_id positional OR --req + --seq")

    p_task_start.set_defaults(func=_dispatch_task_start)

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
        func=lambda a: _lazy("task_complete_cmd")(task_id_str=a.task_id, as_json=a.as_json)
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
        func=lambda a: _lazy("task_block_cmd")(
            task_id_str=a.task_id, reason=a.reason, as_json=a.as_json
        )
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
        func=lambda a: _lazy("task_escalate_cmd")(
            task_id_str=a.task_id, reason=a.reason, as_json=a.as_json
        )
    )

    p_task_envelope = task_commands.add_parser(
        "envelope",
        help="TASK envelope utilities",
        description="TASK envelope inspection and diagnosis commands.",
        epilog=build_epilog(["gz task envelope diagnose OBPI-0.0.64-04"]),
    )
    envelope_cmds = p_task_envelope.add_subparsers(dest="envelope_command", metavar="<command>")
    envelope_cmds.required = True
    p_diagnose = envelope_cmds.add_parser(
        "diagnose",
        help="Show per-channel TASK declarations side-by-side for an OBPI",
        description="Render TASK IDs from all four discovery channels for an OBPI.",
        epilog=build_epilog(
            [
                "gz task envelope diagnose OBPI-0.0.64-04",
                "gz task envelope diagnose OBPI-0.0.64-04 --json",
            ]
        ),
    )
    p_diagnose.add_argument("obpi_id", help="OBPI identifier (e.g. OBPI-0.0.64-04)")
    add_json_flag(p_diagnose)
    p_diagnose.set_defaults(
        func=lambda a: _lazy("task_envelope_diagnose_cmd")(a.obpi_id, as_json=a.as_json)
    )

    p_task_fanout = task_commands.add_parser(
        "fanout",
        help="Show TASK fan-out for a REQ-ID",
        description="Display per-task attribution rows for a given REQ-ID.",
        epilog=build_epilog(
            [
                "gz task fanout REQ-0.0.64-05-01",
                "gz task fanout REQ-0.0.64-05-01 --json",
                "gz task fanout REQ-0.0.64-05-01 --detail",
            ]
        ),
    )
    p_task_fanout.add_argument("req_id", help="REQ identifier (e.g. REQ-0.0.64-05-01)")
    p_task_fanout.add_argument(
        "--detail",
        action="store_true",
        default=False,
        help="Render ASCII tree with file:line spans",  # noqa: E501
    )
    add_json_flag(p_task_fanout)
    p_task_fanout.set_defaults(
        func=lambda a: _lazy("task_fanout_cmd")(a.req_id, detail=a.detail, as_json=a.as_json)
    )


def _register_issue_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the top-level ``gz issue`` verb (ADR-0.0.23, OBPI-04).

    ``gz issue file`` files a defect or enhancement at ``tvproductions/gzkit``
    regardless of the consuming repo's git remote, with an auto-stamped
    provenance trailer naming the consumer slug and the gzkit version.
    Hard-rejects bodies that reference no gzkit-owned surface — closes the
    misrouting failure class structurally per
    ``.gzkit/rules/agent-failure-modes.md`` § Safeguard circumvention.
    """
    p_issue = commands.add_parser(
        "issue",
        help="Cross-repo defect/enhancement filing against gzkit's tracker",
        description=(
            "File a defect or enhancement at tvproductions/gzkit from any "
            "consuming repository, with an auto-stamped provenance trailer."
        ),
        epilog=build_epilog(
            [
                'gz issue file --title "T" --body "gz validate fails" --defect',
                'gz issue file --title "T" --body "gzkit.events crashes" --enhancement --dry-run',
            ]
        ),
    )
    issue_commands = p_issue.add_subparsers(dest="issue_command")
    issue_commands.required = True

    p_issue_file = issue_commands.add_parser(
        "file",
        help="File a GHI at tvproductions/gzkit with provenance trailer",
        description=(
            "Compose a GHI body with a 'Filed from <consumer-repo-slug> running "
            "gz vX.Y.Z' trailer, validate that the body references a "
            "gzkit-owned surface (gz <verb>, .gzkit/, src/gzkit/, gzkit.<module>), "
            "and either preview (--dry-run) or invoke gh issue create against "
            "tvproductions/gzkit. Exit codes: 0 success; 1 user/config error "
            "(including hard-reject of bodies without a gzkit-surface "
            "reference); 2 system/IO error (gh subprocess failure); 3 policy "
            "breach (reserved)."
        ),
        epilog=build_epilog(
            [
                'gz issue file --title "T" --body "gz validate fails" --defect',
                'gz issue file --title "T" --body "src/gzkit/x crashes" --enhancement --dry-run',
            ]
        ),
    )
    p_issue_file.add_argument("--title", required=True, help="Issue title")
    p_issue_file.add_argument("--body", required=True, help="Issue body (markdown)")
    label_group = p_issue_file.add_mutually_exclusive_group()
    label_group.add_argument(
        "--defect",
        dest="label",
        action="store_const",
        const="defect",
        help="Apply the 'defect' label (default)",
    )
    label_group.add_argument(
        "--enhancement",
        dest="label",
        action="store_const",
        const="enhancement",
        help="Apply the 'enhancement' label",
    )
    p_issue_file.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the composed body, target, and label without invoking gh",
    )
    p_issue_file.set_defaults(
        label="defect",
        func=lambda a: _lazy("issue_file_cmd")(
            title=a.title,
            body=a.body,
            label=a.label,
            dry_run=a.dry_run,
        ),
    )
