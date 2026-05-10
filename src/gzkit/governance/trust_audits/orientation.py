"""SessionStart orientation hook freshness trust audit (GHI #341).

GHI #338 wired ``scripts/session_orientation.py`` into both vendor SessionStart
hooks so agents on stale clones see remote-divergence warnings before editing
canonical surfaces. This audit asserts the wiring stays present so a future
``gz agent sync`` or script edit cannot silently regress the backstop.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from gzkit.validate import ValidationError

_ORIENTATION_SCRIPT = "scripts/session_orientation.py"
_ORIENTATION_REMOTE_HEADING = "Git remote state"
_ORIENTATION_COLLECTOR = "collect_remote_state"
_ORIENTATION_AGGREGATOR = "collect_state"


def _read_session_start_blocks(path: Path) -> list[Any]:
    """Load the ``hooks.SessionStart`` list from a JSON config, or return ``[]``."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    hooks = payload.get("hooks") if isinstance(payload, dict) else None
    sessions = hooks.get("SessionStart") if isinstance(hooks, dict) else None
    return sessions if isinstance(sessions, list) else []


def _format_command(cmd: Any) -> str | None:
    if isinstance(cmd, str):
        return cmd
    if isinstance(cmd, list):
        return " ".join(str(part) for part in cmd)
    return None


def _settings_session_start_command_strings(settings_path: Path) -> list[str]:
    """Return concatenated ``SessionStart`` command strings from settings.json."""
    out: list[str] = []
    for matcher in _read_session_start_blocks(settings_path):
        if not isinstance(matcher, dict):
            continue
        for entry in matcher.get("hooks", []):
            if not isinstance(entry, dict):
                continue
            formatted = _format_command(entry.get("command"))
            if formatted is not None:
                out.append(formatted)
    return out


def _codex_session_start_command_strings(hooks_path: Path) -> list[str]:
    """Return concatenated ``SessionStart`` command strings from .codex/hooks.json."""
    out: list[str] = []
    for entry in _read_session_start_blocks(hooks_path):
        if not isinstance(entry, dict):
            continue
        formatted = _format_command(entry.get("command"))
        if formatted is not None:
            out.append(formatted)
    return out


def _section_headings_assignment(
    node: ast.AST,
) -> tuple[list[ast.expr], ast.expr] | None:
    """Return ``(targets, value)`` for module-level ``SECTION_HEADINGS = …``."""
    if isinstance(node, ast.Assign):
        return node.targets, node.value
    if isinstance(node, ast.AnnAssign) and node.value is not None:
        return [node.target], node.value
    return None


def _targets_section_headings(targets: list[ast.expr]) -> bool:
    return any(isinstance(t, ast.Name) and t.id == "SECTION_HEADINGS" for t in targets)


def _string_literals(value: ast.expr) -> list[str] | None:
    if not isinstance(value, ast.Tuple | ast.List):
        return None
    return [
        elt.value
        for elt in value.elts
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
    ]


def _script_section_headings(script_path: Path) -> list[str] | None:
    """Extract literal strings from the module-level ``SECTION_HEADINGS`` tuple."""
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        assignment = _section_headings_assignment(node)
        if assignment is None:
            continue
        targets, value = assignment
        if not _targets_section_headings(targets):
            continue
        return _string_literals(value)
    return None


def _node_references_collector(node: ast.AST) -> bool:
    """Return True for ``Name``/``Attribute`` nodes referring to ``_ORIENTATION_COLLECTOR``."""
    if isinstance(node, ast.Name) and node.id == _ORIENTATION_COLLECTOR:
        return True
    return isinstance(node, ast.Attribute) and node.attr == _ORIENTATION_COLLECTOR


def _collect_state_references_collector(script_path: Path) -> bool | None:
    """Return True if ``collect_state`` body references ``collect_remote_state``."""
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != _ORIENTATION_AGGREGATOR:
            continue
        return any(_node_references_collector(sub) for sub in ast.walk(node))
    return None


def _orientation_error(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="orientation_freshness", artifact=artifact, message=message)


def _check_hook_wired(
    config_path: Path,
    artifact: str,
    extract: Callable[[Path], list[str]],
) -> ValidationError | None:
    """Return a finding if the hook config is missing or no longer invokes the script."""
    if not config_path.exists():
        return _orientation_error(
            artifact,
            "SessionStart orientation hook is missing — "
            f"{artifact} not found. Recovery: "
            "`uv run gz agent sync control-surfaces`.",
        )
    commands = extract(config_path)
    if any(_ORIENTATION_SCRIPT in cmd for cmd in commands):
        return None
    return _orientation_error(
        artifact,
        f"SessionStart hook does not invoke `{_ORIENTATION_SCRIPT}`. "
        "Recovery: `uv run gz agent sync control-surfaces`.",
    )


def _check_orientation_headings(script: Path) -> ValidationError | None:
    headings = _script_section_headings(script)
    if headings is None:
        return _orientation_error(
            _ORIENTATION_SCRIPT,
            "SECTION_HEADINGS tuple is missing or unparseable. "
            "Restore the canonical tuple including "
            f"`{_ORIENTATION_REMOTE_HEADING}`.",
        )
    if _ORIENTATION_REMOTE_HEADING not in headings:
        return _orientation_error(
            _ORIENTATION_SCRIPT,
            f"SECTION_HEADINGS does not contain "
            f"`{_ORIENTATION_REMOTE_HEADING}`. The remote-divergence "
            "warning class (GHI #338) requires the heading to render. "
            "Restore it in scripts/session_orientation.py.",
        )
    return None


def _check_orientation_collector_wiring(script: Path) -> ValidationError | None:
    referenced = _collect_state_references_collector(script)
    if referenced is None:
        return _orientation_error(
            _ORIENTATION_SCRIPT,
            f"`{_ORIENTATION_AGGREGATOR}` function not found. The "
            "aggregator must wire `collect_remote_state` into the "
            "session-start digest.",
        )
    if not referenced:
        return _orientation_error(
            _ORIENTATION_SCRIPT,
            f"`{_ORIENTATION_AGGREGATOR}` does not reference "
            f"`{_ORIENTATION_COLLECTOR}`. The remote-divergence "
            "collector is not wired into the aggregated state — "
            "GHI #338 fix has regressed.",
        )
    return None


def audit_orientation_freshness(project_root: Path) -> list[ValidationError]:
    """Fail-close on regression of the SessionStart orientation backstop (GHI #341).

    Asserts ``scripts/session_orientation.py`` remains wired into both
    ``.claude/settings.json`` and ``.codex/hooks.json`` SessionStart blocks,
    and that the script retains the ``Git remote state`` heading and the
    ``collect_state`` -> ``collect_remote_state`` reference. Recovery: re-run
    ``uv run gz agent sync control-surfaces`` if the hook drifted.
    """
    errors: list[ValidationError] = []

    claude_err = _check_hook_wired(
        project_root / ".claude" / "settings.json",
        ".claude/settings.json",
        _settings_session_start_command_strings,
    )
    if claude_err is not None:
        errors.append(claude_err)

    codex_err = _check_hook_wired(
        project_root / ".codex" / "hooks.json",
        ".codex/hooks.json",
        _codex_session_start_command_strings,
    )
    if codex_err is not None:
        errors.append(codex_err)

    script = project_root / _ORIENTATION_SCRIPT
    if not script.exists():
        errors.append(
            _orientation_error(
                _ORIENTATION_SCRIPT,
                f"`{_ORIENTATION_SCRIPT}` is missing. Restore the script "
                "or revert the deletion that removed it.",
            )
        )
        return errors

    for finding in (
        _check_orientation_headings(script),
        _check_orientation_collector_wiring(script),
    ):
        if finding is not None:
            errors.append(finding)

    return errors
