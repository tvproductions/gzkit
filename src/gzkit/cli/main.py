"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse
from importlib import import_module
from typing import Any

from gzkit import __version__
from gzkit.cli.helpers import add_common_flags
from gzkit.cli.helpers.exit_codes import exit_code_for
from gzkit.cli.parser import StableArgumentParser
from gzkit.cli.parser_arb import register_arb_parsers
from gzkit.cli.parser_artifacts import register_artifact_parsers
from gzkit.cli.parser_governance import register_governance_parsers
from gzkit.cli.parser_maintenance import register_maintenance_parsers
from gzkit.core.exceptions import GzkitError

# Lazy re-exports preserved for ``@patch("gzkit.cli.main.X")`` compatibility in
# tests and for backward-compat callers. Resolving these at module top pulls
# ``gzkit.commands.common`` -> ``gzkit.sync`` -> ``yaml`` into every ``gz --help``
# invocation (GHI #180). PEP 562 ``__getattr__`` defers the import to first use
# while keeping the attribute addressable by name.
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "_write_audit_artifacts": ("gzkit.commands.audit_cmd", "_write_audit_artifacts"),
    "GzCliError": ("gzkit.commands.common", "GzCliError"),
    "console": ("gzkit.commands.common", "console"),
    "ensure_initialized": ("gzkit.commands.common", "ensure_initialized"),
    "get_project_root": ("gzkit.commands.common", "get_project_root"),
    "load_manifest": ("gzkit.commands.common", "load_manifest"),
    "resolve_adr_file": ("gzkit.commands.common", "resolve_adr_file"),
    "resolve_target_adr": ("gzkit.commands.common", "resolve_target_adr"),
    "_run_eval_delta": ("gzkit.commands.gates", "_run_eval_delta"),
    "_run_gate_1": ("gzkit.commands.gates", "_run_gate_1"),
    "_run_gate_2": ("gzkit.commands.gates", "_run_gate_2"),
    "_run_gate_3": ("gzkit.commands.gates", "_run_gate_3"),
    "_run_gate_4": ("gzkit.commands.gates", "_run_gate_4"),
    "_run_gate_5": ("gzkit.commands.gates", "_run_gate_5"),
    "resolve_adr_lane": ("gzkit.ledger", "resolve_adr_lane"),
    "run_all_checks": ("gzkit.quality", "run_all_checks"),
    "run_command": ("gzkit.quality", "run_command"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'gzkit.cli.main' has no attribute {name!r}")
    module_name, attr = target
    value = getattr(import_module(module_name), attr)
    globals()[name] = value
    return value


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
        from gzkit.commands.common import console  # noqa: PLC0415

        if getattr(args, "debug", False):
            import sys  # noqa: PLC0415
            import traceback  # noqa: PLC0415

            traceback.print_exc(file=sys.stderr)
        console.print(f"[red]{exc}[/red]")
        return exit_code_for(exc)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1
    except KeyboardInterrupt:
        from gzkit.commands.common import console  # noqa: PLC0415

        console.print("[yellow]Interrupted.[/yellow]")
        return 130
    except Exception as exc:  # noqa: BLE001 -- CLI main entry point
        from gzkit.commands.common import console  # noqa: PLC0415

        if getattr(args, "debug", False):
            import sys  # noqa: PLC0415
            import traceback  # noqa: PLC0415

            traceback.print_exc(file=sys.stderr)
        console.print(f"[red]Unexpected error: {exc}[/red]")
        return exit_code_for(exc)
    else:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
