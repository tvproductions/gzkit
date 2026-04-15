"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse

from gzkit import __version__
from gzkit.cli.helpers import add_common_flags
from gzkit.cli.helpers.exit_codes import exit_code_for
from gzkit.cli.parser import StableArgumentParser
from gzkit.cli.parser_arb import register_arb_parsers
from gzkit.cli.parser_artifacts import register_artifact_parsers
from gzkit.cli.parser_governance import register_governance_parsers
from gzkit.cli.parser_maintenance import register_maintenance_parsers
from gzkit.commands.audit_cmd import _write_audit_artifacts  # noqa: F401 -- test-mock compat
from gzkit.commands.common import (
    GzCliError,  # noqa: F401 -- backward-compat re-export
    console,
    ensure_initialized,  # noqa: F401 -- test-mock compat
    get_project_root,  # noqa: F401 -- test-mock compat
    load_manifest,  # noqa: F401 -- test-mock compat
    resolve_adr_file,  # noqa: F401 -- backward-compat re-export
    resolve_target_adr,  # noqa: F401 -- test-mock compat
)
from gzkit.commands.gates import (
    _run_eval_delta,  # noqa: F401 -- test-mock compat
    _run_gate_1,  # noqa: F401 -- test-mock compat
    _run_gate_2,  # noqa: F401 -- test-mock compat
    _run_gate_3,  # noqa: F401 -- test-mock compat
    _run_gate_4,  # noqa: F401 -- test-mock compat
    _run_gate_5,  # noqa: F401 -- test-mock compat
)
from gzkit.core.exceptions import GzkitError
from gzkit.ledger import resolve_adr_lane  # noqa: F401 -- test-mock compat
from gzkit.quality import run_all_checks, run_command  # noqa: F401 -- test-mock compat


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

    register_governance_parsers(commands)
    register_artifact_parsers(commands)
    register_maintenance_parsers(commands)
    register_arb_parsers(commands)

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


def _ensure_utf8_console() -> None:
    """Reconfigure stdout/stderr to UTF-8 on Windows to avoid cp1252 crashes from Rich."""
    import sys  # noqa: PLC0415

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """argparse-based gz entrypoint."""
    _ensure_utf8_console()
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
    except Exception as exc:  # noqa: BLE001 -- CLI main entry point
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
