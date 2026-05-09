"""Per-flag documentation coverage scanner (GHI #350).

Closes the class of failure where an ``add_argument("--flag", ...)`` call lands
in an existing subcommand's parser but no corresponding section is added to
``docs/user/manpages/<command>.md``. The pre-existing surfaces (per-command
``manpage``, ``index_entry``, runbook references) are command-grained, not
flag-grained — a new flag never tripped any mechanical check.

The implementation lives in a separate module from ``scanner.py`` to keep the
parent under the 600-line module cap (``.claude/rules/pythonic.md``); the AST
helpers it depends on are imported from ``scanner.py`` rather than duplicated.
"""

import ast
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.doc_coverage.scanner import (
    _find_root_parser_name,
    _handle_assignment,
    _ParserState,
    _read_cli_sources,
)

_MANPAGE_DIR_POSIX = MANPAGE_DIR.as_posix()


def _collect_long_flags_from_call(call: ast.Call) -> list[str]:
    """Return long-form flag names (``--xxx``) from an add_argument call's args."""
    long_flags: list[str] = []
    for arg in call.args:
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        if arg.value.startswith("--"):
            long_flags.append(arg.value)
    return long_flags


def _parser_func_depth(name: str) -> int:
    """Return processing depth for a parser-registration function.

    ``_build_parser`` (root) is depth 0; ``register_X_parsers`` (subparser
    group authors) is depth 1; ``_register_X`` (leaf flag registrations) is
    depth 2. Lower depths must process before higher depths so that a
    caller's ``X = parent.add_subparsers(...)`` lands in shared
    ``subparser_vars`` before the callee's leaf-parser assignments resolve
    against it.
    """
    if name == "_build_parser":
        return 0
    if name.startswith("_register_"):
        return 2
    return 1


def discover_command_flags(source: str) -> dict[str, list[str]]:
    """Discover registered argparse long flags per leaf command.

    Walks parser-registration source and returns ``{command_name: [--flag, ...]}``
    by joining parser-variable bindings to ``add_argument`` calls. Each
    parser-registration function is processed in its OWN ``parser_vars``
    scope: local variables like ``p`` in ``_register_ruff`` and
    ``_register_step`` are isolated rather than colliding on the last write
    (GHI #355). Subparser-group bindings remain shared across functions so
    a caller's ``arb_commands = p_arb.add_subparsers(...)`` is visible in
    the callee's ``arb_commands`` parameter.
    """
    tree = ast.parse(source)

    parser_funcs = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and (
            node.name == "_build_parser"
            or node.name.startswith("register_")
            or node.name.startswith("_register_")
        )
    ]
    if not parser_funcs:
        return {}

    body_all: list[ast.stmt] = []
    for fn in parser_funcs:
        body_all.extend(fn.body)

    state = _ParserState(_find_root_parser_name(body_all))
    for fn in parser_funcs:
        for arg in fn.args.args:
            state.subparser_vars.setdefault(arg.arg, "")

    flags_by_command: dict[str, list[str]] = {}
    for fn in sorted(parser_funcs, key=lambda f: (_parser_func_depth(f.name), f.name)):
        saved_parser_vars = state.parser_vars
        state.parser_vars = dict(saved_parser_vars)

        for stmt in fn.body:
            if isinstance(stmt, ast.Assign):
                _handle_assignment(stmt, state)

        for node in ast.walk(fn):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            if node.func.attr != "add_argument":
                continue
            if not isinstance(node.func.value, ast.Name):
                continue
            parser_var = node.func.value.id
            command_name = state.parser_vars.get(parser_var)
            if command_name is None:
                continue
            for flag in _collect_long_flags_from_call(node):
                flags_by_command.setdefault(command_name, []).append(flag)

        state.parser_vars = saved_parser_vars

    return flags_by_command


def scan_command_flags(project_root: Path | None = None) -> dict[str, list[str]]:
    """Discover per-command flags by AST-scanning cli/main.py and parser modules.

    Returns an empty mapping when the CLI source layout is absent — matches the
    fallback in ``check_surfaces_report`` so an isolated test fixture without
    ``src/gzkit/cli/main.py`` does not crash the audit.
    """
    if project_root is None:
        project_root = get_project_root()
    try:
        source = _read_cli_sources(project_root)
    except (FileNotFoundError, OSError):
        return {}
    return discover_command_flags(source)


# Pre-existing per-flag doc gaps surfaced when this audit landed (GHI #350).
# Drained by the doc backlog tracked under GHI #353. Removing a flag from this
# waiver requires the corresponding section to land in the cited doc; adding
# a new flag without doc coverage fails the audit immediately. The waiver is
# the snapshot of "known historical drift" — Trust Doctrine T2 (unrepairable
# evidence captured in a stable surface), mirroring the precedent at
# ``_UTF8_PIPE_WAIVERS`` in ``src/gzkit/governance/trust_audits.py``.
_PER_FLAG_DOC_WAIVERS: dict[str, frozenset[str]] = {}


def check_flag_doc_coverage(
    commands_dir: Path,
    flags_by_command: dict[str, list[str]],
    waivers: dict[str, frozenset[str]] | None = None,
) -> list[dict[str, str]]:
    """Assert every long flag has at least one mention in its command doc.

    Returns issue dicts shaped like ``cli_audit_cmd``'s existing list:
    ``{"path": "<doc-rel-path>", "issue": "<message>"}``. A flag is considered
    documented when the string ``--flag`` appears anywhere in the file (Usage
    line, examples, prose). The string-presence fallback closes the common
    drift class — a flag declared in argparse but never named in the doc —
    without forcing a rigid heading shape on every command doc.

    ``waivers`` defaults to ``_PER_FLAG_DOC_WAIVERS`` and lists the
    pre-existing gaps when this audit landed; new gaps fail the check.
    """
    waiver_map = waivers if waivers is not None else _PER_FLAG_DOC_WAIVERS
    issues: list[dict[str, str]] = []
    for command_name in sorted(flags_by_command):
        slug = command_name.replace(" ", "-")
        doc_path = commands_dir / f"{slug}.md"
        if not doc_path.is_file():
            continue
        content = doc_path.read_text(encoding="utf-8")
        waived = waiver_map.get(command_name, frozenset())
        for flag in flags_by_command[command_name]:
            if flag in content:
                continue
            if flag in waived:
                continue
            rel = f"{_MANPAGE_DIR_POSIX}/{slug}.md"
            issues.append(
                {
                    "path": rel,
                    "issue": f"missing per-flag doc for `{flag}` (GHI #350)",
                }
            )
    return issues
