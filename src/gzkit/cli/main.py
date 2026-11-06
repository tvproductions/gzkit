"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse
import os
from importlib import import_module
from typing import Any

from gzkit import __version__
from gzkit.cli.helpers import add_common_flags
from gzkit.cli.helpers.attestor_default import apply_configured_attestor
from gzkit.cli.helpers.exit_codes import exit_code_for
from gzkit.cli.parser import StableArgumentParser
from gzkit.cli.parser_arb import register_arb_parsers
from gzkit.cli.parser_artifacts import register_artifact_parsers
from gzkit.cli.parser_governance import register_governance_parsers
from gzkit.cli.parser_maintenance import register_maintenance_parsers
from gzkit.commands.content import register_content_parsers
from gzkit.commands.insights import register_insights_parsers
from gzkit.core.exceptions import GzkitError
from gzkit.dispatch_stamp import consume_stamp, is_stamped, stamp_refusal


class UnknownModuleAttributeError(AttributeError):
    """A lazily exported module attribute was requested that the module does not export."""

    def __init__(self, module: str, name: str) -> None:
        """Build the message from *module*, *name*."""
        self.module = module
        self.attribute = name
        super().__init__(f"module '{module}' has no attribute {name!r}")


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
        raise UnknownModuleAttributeError(__name__, name)
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
    register_content_parsers(commands)
    register_insights_parsers(commands)

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


def configure_logging_from_flags(args: argparse.Namespace) -> None:
    """Apply the CLI logging adapter at the verbosity the common flags select.

    Every log record goes to stderr, never stdout, so ``--json`` output stays
    clean (``.gzkit/rules/cli.md`` § Output Contracts, GHI #1010). Imported here,
    after parsing, so ``gz --help`` never loads the adapter.
    """
    from gzkit.cli.logging import Verbosity, configure_logging  # noqa: PLC0415

    verbosity: Verbosity = "normal"
    if getattr(args, "debug", False):
        verbosity = "debug"
    elif getattr(args, "verbose", False):
        verbosity = "verbose"
    elif getattr(args, "quiet", False):
        verbosity = "quiet"
    configure_logging(verbosity)


def _ensure_utf8_console() -> None:
    """Reconfigure stdout/stderr to UTF-8 on Windows to avoid cp1252 crashes from Rich.

    Text a command prints can come from a file anyone can write, and a JSON string
    can decode to a lone surrogate no UTF-8 stream encodes, so such a character is
    shown escaped and never stops the command (GHI #1205).
    """
    import sys  # noqa: PLC0415

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")


def _exit_code_from(result: object) -> int:
    """Read a handler's return; GHI #1198, a refused dispatch exited 0.

    Returns:
        ``result`` when it is an int, which is the handler's exit code; 0 for anything
        else, a bool included, which is an answer and not a code.

    """
    return result if type(result) is int else 0


def _refused_by_stamp(*, forwards: bool) -> bool:
    """Refuse a stamped subagent call aimed at another root (RP-12 rulings 17, 36).

    Checked before any handler, so no verb writes for it. The imports are deferred
    like the ones in ``main``: ``--help`` exits before this runs, and every handler
    loads ``gzkit.commands.common`` anyway.

    A call that passes consumes the stamp from ``os.environ`` (ruling 37), so what
    the verb runs carries none, and a second ``main`` call in this process is not
    checked. A verb that runs a command its caller supplies (``forwards``, set by
    its parser) keeps it: ruling 37 rests on a nested ``gz`` whose directory the
    verb's code chooses, and a forwarded command is the agent's own.

    Returns:
        True when the call is refused, its message already on stderr.

    """
    from gzkit.commands.common import err_console, get_project_root  # noqa: PLC0415

    refusal = stamp_refusal(os.environ, get_project_root)
    if refusal is None:
        if not forwards:
            consume_stamp(os.environ)
        return False
    from rich.markup import escape  # noqa: PLC0415

    err_console.print(f"[red]{escape(refusal)}[/red]")
    return True


def _report_failure(args: argparse.Namespace, message: str) -> None:
    """Report a handler's failure on stderr, with its traceback under ``--debug``.

    Called from inside an ``except`` block, so the traceback is the one in flight.
    """
    from rich.markup import escape  # noqa: PLC0415

    from gzkit.commands.common import err_console  # noqa: PLC0415

    if getattr(args, "debug", False):
        import sys  # noqa: PLC0415
        import traceback  # noqa: PLC0415

        traceback.print_exc(file=sys.stderr)
    # The message is text: unescaped, Rich consumes bracketed spans as tags.
    err_console.print(f"[red]{escape(message)}[/red]")


def main(argv: list[str] | None = None) -> int:
    """argparse-based gz entrypoint."""
    _ensure_utf8_console()
    parser = _get_parser()
    try:
        args = parser.parse_args(argv)
        apply_configured_attestor(args)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    configure_logging_from_flags(args)

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 2

    # Read before the check consumes it: a verb an operator or the coordinator
    # alone may run refuses a call stamped as a subagent's (RP-12 ruling 42).
    args.called_by_subagent = is_stamped(os.environ)
    if _refused_by_stamp(forwards=bool(getattr(args, "forwards_command", False))):
        return 3

    try:
        result = handler(args)
    # Every branch reports on stderr: errors and diagnostics never reach stdout,
    # where a command's output is read (cli-standards-v3.md § Output Rules).
    except GzkitError as exc:
        _report_failure(args, str(exc))
        return exit_code_for(exc)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1
    except KeyboardInterrupt:
        from gzkit.commands.common import err_console  # noqa: PLC0415

        err_console.print("[yellow]Interrupted.[/yellow]")
        return 130
    except Exception as exc:  # noqa: BLE001 -- CLI main entry point
        _report_failure(args, f"Unexpected error: {exc}")
        return exit_code_for(exc)
    else:
        return _exit_code_from(result)


if __name__ == "__main__":
    raise SystemExit(main())
