"""Per-flag documentation coverage scanner (GHI #350).

Closes the class of failure where an ``add_argument("--flag", ...)`` call lands
in an existing subcommand's parser but no corresponding section is added to
``docs/user/commands/<command>.md``. The pre-existing surfaces (per-command
``manpage``, ``index_entry``, runbook references) are command-grained, not
flag-grained — a new flag never tripped any mechanical check.

The implementation lives in a separate module from ``scanner.py`` to keep the
parent under the 600-line module cap (``.claude/rules/pythonic.md``); the AST
helpers it depends on are imported from ``scanner.py`` rather than duplicated.
"""

import ast
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.doc_coverage.scanner import (
    _find_build_parser_body,
    _find_root_parser_name,
    _handle_assignment,
    _ParserState,
    _read_cli_sources,
)


def _collect_long_flags_from_call(call: ast.Call) -> list[str]:
    """Return long-form flag names (``--xxx``) from an add_argument call's args."""
    long_flags: list[str] = []
    for arg in call.args:
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        if arg.value.startswith("--"):
            long_flags.append(arg.value)
    return long_flags


def discover_command_flags(source: str) -> dict[str, list[str]]:
    """Discover registered argparse long flags per leaf command.

    Walks parser-registration source and returns ``{command_name: [--flag, ...]}``
    by joining ``state.parser_vars`` (parser variable -> command name) with
    ``add_argument`` calls on those parser variables. Only explicit
    ``p_xxx.add_argument("--flag", ...)`` shapes are captured; helper-mediated
    flags (e.g. ``add_json_flag(parser)``) are out of scope and tracked
    separately if a class-of-failure for them surfaces.
    """
    tree = ast.parse(source)
    body = _find_build_parser_body(tree)
    if body is None:
        return {}

    state = _ParserState(_find_root_parser_name(body))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (
            node.name.startswith("register_") or node.name.startswith("_register_")
        ):
            for arg in node.args.args:
                state.subparser_vars[arg.arg] = ""

    for stmt in body:
        if isinstance(stmt, ast.Assign):
            _handle_assignment(stmt, state)

    flags_by_command: dict[str, list[str]] = {}
    for node in ast.walk(tree):
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
_PER_FLAG_DOC_WAIVERS: dict[str, frozenset[str]] = {
    "adr emit-receipt": frozenset({"--attestor-present"}),
    "adr report": frozenset({"--type"}),
    "arb patterns": frozenset({"--fix", "--soft-fail", "--name"}),
    "closeout": frozenset(
        {"--ceremony", "--next", "--ceremony-status", "--attest", "--pause", "--restart"}
    ),
    "covers": frozenset({"--features-dir", "--include-doc"}),
    "interview": frozenset({"--from"}),
    "obpi complete": frozenset({"--attestor-present"}),
    "obpi emit-receipt": frozenset({"--attestor-present"}),
    "obpi pipeline": frozenset(
        {"--attestor", "--evidence-json", "--clear-stale", "--no-subagents"}
    ),
    "patch release": frozenset({"--full"}),
    "skill new": frozenset({"--description"}),
    "state": frozenset({"--full"}),
    "status": frozenset({"--full"}),
    "test": frozenset({"--bdd", "--obpi"}),
    "tidy": frozenset({"--check", "--fix"}),
    "validate": frozenset(
        {
            "--version",
            "--type-ignores",
            "--cli-alignment",
            "--event-handlers",
            "--validator-fields",
            "--utf8-prefix",
            "--test-tiers",
            "--pydantic-models",
            "--class-size",
            "--version-release",
            "--pool-adr-isolation",
            "--behave-req-tags",
            "--skill-alignment",
            "--advisory-scorecard",
            "--reconcile-freshness",
            "--adr-status-fresh",
            "--orientation-freshness",
            "--brief-headings",
        }
    ),
}


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
            rel = f"docs/user/commands/{slug}.md"
            issues.append(
                {
                    "path": rel,
                    "issue": f"missing per-flag doc for `{flag}` (GHI #350)",
                }
            )
    return issues
