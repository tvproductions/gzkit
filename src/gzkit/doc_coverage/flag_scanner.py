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
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import get_project_root
from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.doc_coverage.scanner import (
    _find_root_parser_name,
    _handle_assignment,
    _ParserState,
    _read_cli_sources,
)

_MANPAGE_DIR_POSIX = MANPAGE_DIR.as_posix()

#: argparse actions that consume no argument. Everything else binds a value, so
#: a manpage showing ``--flag PLACEHOLDER`` for one of these is making a false
#: claim about the command's contract.
_VALUELESS_ACTIONS: frozenset[str] = frozenset(
    {"store_true", "store_false", "store_const", "count", "help", "version"}
)


class FlagSpec(BaseModel):
    """A flag's argparse contract — the facts a manpage restates and can contradict.

    Carries only what is mechanically comparable against a doc. ``help=`` text is
    deliberately absent: comparing prose to prose is a grader, not a check, and
    the false positives are what routed GHI #690 away from a fail-closed home.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    flag: str = Field(..., description="Long-form flag name, e.g. `--session-id`")
    required: bool = Field(False, description="argparse `required=True`")
    takes_value: bool = Field(True, description="False for store_true and friends")


def _collect_long_flags_from_call(call: ast.Call) -> list[str]:
    """Return long-form flag names (``--xxx``) from an add_argument call's args."""
    long_flags: list[str] = []
    for arg in call.args:
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        if arg.value.startswith("--"):
            long_flags.append(arg.value)
    return long_flags


def _keyword_constant(call: ast.Call, name: str) -> object | None:
    """Return a literal keyword's value from an add_argument call, else None."""
    for keyword in call.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return None


def _spec_from_call(call: ast.Call, flag: str) -> FlagSpec:
    """Build a FlagSpec from one ``add_argument`` call.

    Non-literal keywords (``required=some_var``) read as absent rather than
    guessed: the audit fails OPEN on what it cannot introspect, because a
    fabricated contract is worse than an unchecked one.
    """
    action = _keyword_constant(call, "action")
    return FlagSpec(
        flag=flag,
        required=_keyword_constant(call, "required") is True,
        takes_value=not (isinstance(action, str) and action in _VALUELESS_ACTIONS),
    )


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

    Name-only projection of :func:`discover_command_flag_specs` — one AST walk,
    two consumers. A second traversal here would drift from the spec walker the
    first time argparse's registration shape changed (the duplicated-resolver
    class closed at GHI #689).
    """
    return {
        command: [spec.flag for spec in specs]
        for command, specs in discover_command_flag_specs(source).items()
    }


def discover_command_flag_specs(source: str) -> dict[str, list[FlagSpec]]:
    """Discover each leaf command's flags WITH their argparse contract.

    Walks parser-registration source and returns ``{command_name: [FlagSpec, ...]}``
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

    specs_by_command: dict[str, list[FlagSpec]] = {}
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
                specs_by_command.setdefault(command_name, []).append(_spec_from_call(node, flag))

        state.parser_vars = saved_parser_vars

    return specs_by_command


def scan_command_flags(project_root: Path | None = None) -> dict[str, list[str]]:
    """Discover per-command flags by AST-scanning cli/main.py and parser modules.

    Returns an empty mapping when the CLI source layout is absent — matches the
    fallback in ``check_surfaces_report`` so an isolated test fixture without
    ``src/gzkit/cli/main.py`` does not crash the audit.
    """
    return {
        command: [spec.flag for spec in specs]
        for command, specs in scan_command_flag_specs(project_root).items()
    }


def scan_command_flag_specs(project_root: Path | None = None) -> dict[str, list[FlagSpec]]:
    """Discover per-command flag specs by AST-scanning cli/main.py and parser modules.

    Same absent-source fallback as :func:`scan_command_flags`.
    """
    if project_root is None:
        project_root = get_project_root()
    try:
        source = _read_cli_sources(project_root)
    except (FileNotFoundError, OSError):
        return {}
    return discover_command_flag_specs(source)


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


#: Matches the fenced block under a ``## Usage`` / ``## Synopsis`` heading — the
#: only region of a manpage that DECLARES the command's invocation contract.
#: Prose elsewhere may legitimately discuss, quote, or historicize a bracket form
#: without claiming it (see the "claims outside the usage block" test).
_USAGE_BLOCK_RE = re.compile(
    r"^##\s+(?:usage|synopsis)\s*$\n+```[a-z]*\n(.*?)\n```",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

#: Pre-existing usage-line drift surfaced when this audit landed (GHI #693).
#: Shrink-only: removing an entry requires the doc to be corrected; a NEW
#: contradiction fails the audit immediately. Same Trust-Doctrine-T2 shape as
#: ``_PER_FLAG_DOC_WAIVERS`` above.
_FLAG_TRUTH_WAIVERS: dict[str, frozenset[str]] = {}


def _usage_blocks(content: str) -> list[str]:
    """Return the fenced usage/synopsis blocks declaring a command's contract."""
    return _USAGE_BLOCK_RE.findall(content)


#: Asserts a flag name ends where it appears to. ``--attestor`` is a PREFIX of
#: ``--attestor-present``, so a bare substring test reads the sibling's bracket
#: as the parent's and invents a contradiction — both findings of this check's
#: first-run census were this collision, and nothing in the doc was wrong.
_FLAG_END = r"(?![\w-])"


def _mentions(usage: str, flag: str) -> bool:
    """True when the usage block names ``flag`` itself (not a longer sibling)."""
    return bool(re.search(rf"{re.escape(flag)}{_FLAG_END}", usage))


def _claims_optional(usage: str, flag: str) -> bool:
    """True when the usage block brackets ``flag`` itself as optional."""
    return bool(re.search(rf"\[{re.escape(flag)}{_FLAG_END}", usage))


def _claims_takes_value(usage: str, flag: str) -> bool:
    """True when the usage block shows ``flag`` binding a placeholder.

    Placeholders are uppercase by manpage convention (``PATH``, ``TEXT``, ``ID``).
    Matched on the SAME LINE only: ``\\s+`` would span the newline between a
    valueless flag and the next line's ``GZ COMMAND``, inventing a claim the doc
    never made.
    """
    return bool(re.search(rf"{re.escape(flag)}{_FLAG_END}[ \t]+[A-Z][A-Z_]*", usage))


def check_flag_doc_truth(
    commands_dir: Path,
    specs_by_command: dict[str, list[FlagSpec]],
    waivers: dict[str, frozenset[str]] | None = None,
) -> list[dict[str, str]]:
    """Assert a manpage's usage line AGREES with the parser (GHI #693).

    ``check_flag_doc_coverage`` proves a flag is *mentioned*; this proves what the
    doc *says* about it is true. A wrong row is worse than a missing one — a
    missing row fails the audit loudly, while a wrong row passes green and is
    believed (the ``gz handoff authorize --session-id`` instance, 2026-07-16,
    shipped with three falsehoods in two lines under a fully green ``gz check``).

    Scope is deliberately the two claims argparse can adjudicate without
    inference: required-ness and value-taking. Stated defaults and env fallbacks
    are prose (``"Defaults to the current branch"`` is true with an argparse
    default of ``None``), so checking them means grading prose — the
    false-positive failure that routed GHI #690 away from a fail-closed home. A
    missing doc is the presence check's finding, not this one's; reporting it
    here would double-count the same drift under two classes.
    """
    waiver_map = waivers if waivers is not None else _FLAG_TRUTH_WAIVERS
    issues: list[dict[str, str]] = []
    for command_name in sorted(specs_by_command):
        slug = command_name.replace(" ", "-")
        doc_path = commands_dir / f"{slug}.md"
        if not doc_path.is_file():
            continue
        usage_blocks = _usage_blocks(doc_path.read_text(encoding="utf-8"))
        if not usage_blocks:
            continue
        usage = "\n".join(usage_blocks)
        waived = waiver_map.get(command_name, frozenset())
        rel = f"{_MANPAGE_DIR_POSIX}/{slug}.md"
        for spec in specs_by_command[command_name]:
            if spec.flag in waived or not _mentions(usage, spec.flag):
                continue
            if spec.required and _claims_optional(usage, spec.flag):
                issues.append(
                    {
                        "path": rel,
                        "issue": (
                            f"usage brackets `{spec.flag}` as optional, but the parser "
                            f"declares it required (GHI #693)"
                        ),
                    }
                )
            if not spec.takes_value and _claims_takes_value(usage, spec.flag):
                issues.append(
                    {
                        "path": rel,
                        "issue": (
                            f"usage shows `{spec.flag}` taking a value, but the parser "
                            f"declares it valueless (GHI #693)"
                        ),
                    }
                )
    return issues
