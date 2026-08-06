"""ARB (Agent Self-Reporting) subparser registrations for gz CLI.

Registers the `gz arb` subcommand group with 10 verbs: ruff, step, red, ty,
typecheck, coverage, validate, advise, patterns, archive.

See `AGENTS.md` § Attestation for the binding rule contract
(em-dash pattern, canonical invocations, lane behavior) and
`docs/governance/arb-middleware.md` for the middleware deep-dive.
"""

from __future__ import annotations

import argparse
from typing import Any

from gzkit.cli.helpers import add_json_flag, build_epilog

# Lazy handler manifest used by doc-coverage scanner to resolve docstrings.
# Map each arb_*_cmd handler to its source module.
_LAZY_HANDLERS: dict[str, str] = {
    "arb_red_cmd": "gzkit.commands.arb",
    "arb_ruff_cmd": "gzkit.commands.arb",
    "arb_step_cmd": "gzkit.commands.arb",
    "arb_ty_cmd": "gzkit.commands.arb",
    "arb_typecheck_cmd": "gzkit.commands.arb",
    "arb_coverage_cmd": "gzkit.commands.arb",
    "arb_validate_cmd": "gzkit.commands.arb",
    "arb_advise_cmd": "gzkit.commands.arb",
    "arb_patterns_cmd": "gzkit.commands.arb",
    "arb_archive_cmd": "gzkit.commands.arb",
}


def _arb(name: str) -> Any:
    """Resolve an ``arb_*_cmd`` handler lazily, propagating its exit code.

    ``cli.main`` discards a handler's return value; only ``SystemExit`` reaches the
    shell. Every ``arb_*_cmd`` returns a meaningful status, so without this wrapper
    ``gz arb step --name unittest -- <failing suite>`` exits 0 — and that command is
    AGENTS.md § Attestation's canonical "tests pass" invocation. The ``--soft-fail``
    flag ("emit a receipt but always return exit 0") is only coherent if the default
    propagates, which is the tell that the swallow was a defect (GHI #642).
    """
    from importlib import import_module

    module = import_module("gzkit.commands.arb")
    handler = getattr(module, name)

    def _propagating(**kwargs: Any) -> int:
        code = handler(**kwargs)
        if isinstance(code, int) and code != 0:
            raise SystemExit(code)
        return 0

    return _propagating


def register_arb_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz arb`` sub-command group."""
    p_arb = commands.add_parser(
        "arb",
        help="ARB middleware: wrap QA commands and emit validated receipts",
        description=(
            "Agent Self-Reporting middleware. Wraps QA commands (ruff, ty, "
            "unittest, coverage) and emits schema-validated JSON receipts to "
            "artifacts/receipts/. Receipts are the canonical attestation "
            "evidence for Heavy-lane OBPIs."
        ),
        epilog=build_epilog(
            [
                "gz arb ruff src/gzkit",
                "gz arb step --name unittest -- uv run -m unittest",
                "gz arb validate",
                "gz arb advise --limit 10",
                "gz arb patterns",
            ]
        ),
    )
    arb_commands = p_arb.add_subparsers(dest="arb_command")
    arb_commands.required = True

    _register_ruff(arb_commands)
    _register_step(arb_commands)
    _register_red(arb_commands)
    _register_ty(arb_commands)
    _register_typecheck(arb_commands)
    _register_coverage(arb_commands)
    _register_validate(arb_commands)
    _register_advise(arb_commands)
    _register_patterns(arb_commands)
    _register_archive(arb_commands)


def _register_ruff(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "ruff",
        help="Run ruff via ARB and emit a lint receipt",
        description="Run ruff check on the given paths and emit a validated lint receipt.",
        epilog=build_epilog(["gz arb ruff src/gzkit", "gz arb ruff --fix src"]),
    )
    p.add_argument("paths", nargs="*", help="Paths to check (defaults to '.').")
    p.add_argument("--fix", action="store_true", help="Apply ruff auto-fixes.")
    p.add_argument(
        "--soft-fail",
        action="store_true",
        help="Emit a receipt but always return exit 0 (measurement-only mode).",
    )
    p.set_defaults(
        func=lambda a: _arb("arb_ruff_cmd")(
            paths=a.paths or None,
            fix=a.fix,
            quiet=getattr(a, "quiet", False),
            soft_fail=a.soft_fail,
        )
    )


def _register_red(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "red",
        help="Witness a BEHAVIOR REQ's test failing against the base tree",
        description=(
            "Reconstruct the base tree in a throwaway git worktree, copy in ONLY the "
            "test files, and run the REQ's covering test there. Exit 0 when a RED is "
            "witnessed; exit 1 when the test passes without its implementation and "
            "therefore cannot fail (GHI #642)."
        ),
        epilog=build_epilog(
            [
                "gz arb red --req REQ-0.33.0-01-01",
                "gz arb red --req REQ-0.33.0-01-01 --obpi OBPI-0.33.0-01-airlock",
                "gz arb red --req REQ-0.33.0-01-01 --base HEAD~1",
            ]
        ),
    )
    p.add_argument("--req", required=True, help="BEHAVIOR REQ id to witness.")
    p.add_argument(
        "--base",
        default=None,
        help="Commit to run the test against (default: HEAD, the pre-change tree).",
    )
    p.add_argument("--obpi", default=None, help="Owning OBPI id, recorded on the event.")
    p.set_defaults(
        func=lambda a: _arb("arb_red_cmd")(
            req=a.req,
            base=a.base,
            obpi=a.obpi,
            quiet=getattr(a, "quiet", False),
        )
    )


def _register_step(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "step",
        help="Wrap an arbitrary command and emit a step receipt",
        description=(
            "Run any command with --name <label> and the argv after '--'. "
            "Emits a step receipt capturing stdout/stderr tail and duration."
        ),
        epilog=build_epilog(
            [
                "gz arb step --name unittest -- uv run -m unittest",
                "gz arb step --name mkdocs -- uv run mkdocs build --strict",
            ]
        ),
    )
    p.add_argument("--name", required=True, help="Logical step name for the receipt.")
    p.add_argument(
        "--soft-fail",
        action="store_true",
        help="Emit a receipt but always return exit 0 (measurement-only mode).",
    )
    p.add_argument(
        "argv",
        nargs=argparse.REMAINDER,
        help="Command to run (everything after '--').",
    )
    p.set_defaults(
        func=lambda a: _arb("arb_step_cmd")(
            name=a.name,
            argv=[arg for arg in a.argv if arg != "--"],
            quiet=getattr(a, "quiet", False),
            soft_fail=a.soft_fail,
        )
    )


def _register_ty(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "ty",
        help="Run `uvx ty` via ARB and emit a step receipt",
        description="Run the ty type checker via ARB step wrapper.",
        epilog=build_epilog(["gz arb ty check ."]),
    )
    p.add_argument("argv", nargs=argparse.REMAINDER, help="Arguments to forward to ty.")
    p.set_defaults(
        func=lambda a: _arb("arb_ty_cmd")(
            argv=[arg for arg in a.argv if arg != "--"],
            quiet=getattr(a, "quiet", False),
        )
    )


def _register_typecheck(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "typecheck",
        help="Run the canonical `gz typecheck` command via ARB and emit a step receipt",
        description=(
            "Heavy-lane canonical type-check receipt. Wraps the exact command "
            "`gz typecheck` runs so ARB receipts cannot diverge from the "
            "governance gate's scope. Prefer this over `gz arb ty check ...` "
            "for attestation evidence. See GHI #199."
        ),
        epilog=build_epilog(["gz arb typecheck"]),
    )
    p.set_defaults(
        func=lambda a: _arb("arb_typecheck_cmd")(quiet=getattr(a, "quiet", False)),
    )


def _register_coverage(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "coverage",
        help="Run `coverage` via ARB and emit a step receipt",
        description="Run coverage via ARB step wrapper.",
        epilog=build_epilog(["gz arb coverage run -m unittest discover -s tests -t ."]),
    )
    p.add_argument("argv", nargs=argparse.REMAINDER, help="Arguments to forward to coverage.")
    p.set_defaults(
        func=lambda a: _arb("arb_coverage_cmd")(
            argv=[arg for arg in a.argv if arg != "--"],
            quiet=getattr(a, "quiet", False),
        )
    )


def _register_validate(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "validate",
        help="Validate recent ARB receipts against their JSON schemas",
        description=(
            "Load recent receipts from artifacts/receipts/ and validate each "
            "against its declared schema. Reports valid/invalid/unknown counts."
        ),
        epilog=build_epilog(["gz arb validate", "gz arb validate --limit 100 --json"]),
    )
    p.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of most-recent receipts to validate (default: 50).",
    )
    add_json_flag(p)
    p.set_defaults(func=lambda a: _arb("arb_validate_cmd")(limit=a.limit, as_json=a.as_json))


def _register_advise(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "advise",
        help="Summarize recent ARB receipts into actionable recommendations",
        description=(
            "Aggregate recent lint receipts, count rule frequencies, and emit "
            "guardrail tuning recommendations."
        ),
        epilog=build_epilog(["gz arb advise", "gz arb advise --limit 10"]),
    )
    p.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of most-recent receipts to summarize (default: 50).",
    )
    add_json_flag(p)
    p.set_defaults(func=lambda a: _arb("arb_advise_cmd")(limit=a.limit, as_json=a.as_json))


def _register_patterns(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "patterns",
        help="Extract recurring anti-patterns from ARB receipts",
        description=(
            "Aggregate recurring lint rules across receipts and emit pattern "
            "candidates with guidance text suitable for agent instructions."
        ),
        epilog=build_epilog(
            ["gz arb patterns", "gz arb patterns --compact", "gz arb patterns --json"]
        ),
    )
    p.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Maximum number of most-recent receipts to scan (default: 500).",
    )
    p.add_argument(
        "--compact",
        action="store_true",
        help="Emit a single-line summary instead of the full Markdown report.",
    )
    add_json_flag(p)
    p.set_defaults(
        func=lambda a: _arb("arb_patterns_cmd")(
            limit=a.limit,
            as_json=a.as_json,
            compact=a.compact,
        )
    )


def _register_archive(arb_commands: argparse._SubParsersAction) -> None:
    p = arb_commands.add_parser(
        "archive",
        help="Relocate aged, uncited ARB receipts into artifacts/receipts/archive/",
        description=(
            "Move-not-delete retention for the receipt store, on the same shape as "
            "`gz handoff archive`. A receipt is relocated only when it is ARB-emitted, "
            "older than the threshold, and its id is cited nowhere in the ledger — a "
            "cited receipt is Heavy-lane attestation evidence and always stays put. "
            "Nothing is ever deleted; purge is deliberately not implemented (GHI #594 "
            "reserves retention-window and purge-authorization for an operator ruling)."
        ),
        epilog=build_epilog(
            [
                "gz arb archive --older-than 30 --dry-run",
                "gz arb archive --older-than 30",
                "gz arb archive --older-than 90 --json",
            ]
        ),
    )
    p.add_argument(
        "--older-than",
        default="30d",
        dest="older_than",
        help="Age threshold, e.g. 30d. Receipts older than this are eligible (default: 30d).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify and report without relocating anything.",
    )
    add_json_flag(p)
    p.set_defaults(
        func=lambda a: _arb("arb_archive_cmd")(
            older_than=a.older_than,
            dry_run=a.dry_run,
            as_json=a.as_json,
        )
    )
