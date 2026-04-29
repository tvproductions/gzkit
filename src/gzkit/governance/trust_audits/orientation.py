"""SessionStart orientation hook freshness trust audit (GHI #341).

GHI #338 wired ``scripts/session_orientation.py`` into both vendor SessionStart
hooks so agents on stale clones see remote-divergence warnings before editing
canonical surfaces. This audit asserts the wiring stays present so a future
``gz agent sync`` or script edit cannot silently regress the backstop.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from gzkit.validate import ValidationError

_ORIENTATION_SCRIPT = "scripts/session_orientation.py"
_ORIENTATION_REMOTE_HEADING = "Git remote state"
_ORIENTATION_COLLECTOR = "collect_remote_state"
_ORIENTATION_AGGREGATOR = "collect_state"


def _settings_session_start_command_strings(settings_path: Path) -> list[str]:
    """Return concatenated ``SessionStart`` command strings from settings.json."""
    try:
        payload = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    hooks = payload.get("hooks") if isinstance(payload, dict) else None
    sessions = hooks.get("SessionStart") if isinstance(hooks, dict) else None
    if not isinstance(sessions, list):
        return []
    out: list[str] = []
    for matcher in sessions:
        if not isinstance(matcher, dict):
            continue
        for entry in matcher.get("hooks", []):
            if not isinstance(entry, dict):
                continue
            cmd = entry.get("command")
            if isinstance(cmd, str):
                out.append(cmd)
            elif isinstance(cmd, list):
                out.append(" ".join(str(part) for part in cmd))
    return out


def _codex_session_start_command_strings(hooks_path: Path) -> list[str]:
    """Return concatenated ``SessionStart`` command strings from .codex/hooks.json."""
    try:
        payload = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    hooks = payload.get("hooks") if isinstance(payload, dict) else None
    sessions = hooks.get("SessionStart") if isinstance(hooks, dict) else None
    if not isinstance(sessions, list):
        return []
    out: list[str] = []
    for entry in sessions:
        if not isinstance(entry, dict):
            continue
        cmd = entry.get("command")
        if isinstance(cmd, str):
            out.append(cmd)
        elif isinstance(cmd, list):
            out.append(" ".join(str(part) for part in cmd))
    return out


def _script_section_headings(script_path: Path) -> list[str] | None:
    """Extract literal strings from the module-level ``SECTION_HEADINGS`` tuple."""
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
            value = node.value
        else:
            continue
        if not any(isinstance(t, ast.Name) and t.id == "SECTION_HEADINGS" for t in targets):
            continue
        if not isinstance(value, ast.Tuple | ast.List):
            return None
        headings: list[str] = []
        for elt in value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                headings.append(elt.value)
        return headings
    return None


def _collect_state_references_collector(script_path: Path) -> bool | None:
    """Return True if ``collect_state`` body references ``collect_remote_state``."""
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != _ORIENTATION_AGGREGATOR:
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id == _ORIENTATION_COLLECTOR:
                return True
            if isinstance(sub, ast.Attribute) and sub.attr == _ORIENTATION_COLLECTOR:
                return True
        return False
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

    claude_settings = project_root / ".claude" / "settings.json"
    if not claude_settings.exists():
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=".claude/settings.json",
                message=(
                    "SessionStart orientation hook is missing — "
                    ".claude/settings.json not found. Recovery: "
                    "`uv run gz agent sync control-surfaces`."
                ),
            )
        )
    else:
        commands = _settings_session_start_command_strings(claude_settings)
        if not any(_ORIENTATION_SCRIPT in cmd for cmd in commands):
            errors.append(
                ValidationError(
                    type="orientation_freshness",
                    artifact=".claude/settings.json",
                    message=(
                        f"SessionStart hook does not invoke `{_ORIENTATION_SCRIPT}`. "
                        "Recovery: `uv run gz agent sync control-surfaces`."
                    ),
                )
            )

    codex_hooks = project_root / ".codex" / "hooks.json"
    if not codex_hooks.exists():
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=".codex/hooks.json",
                message=(
                    "SessionStart orientation hook is missing — "
                    ".codex/hooks.json not found. Recovery: "
                    "`uv run gz agent sync control-surfaces`."
                ),
            )
        )
    else:
        commands = _codex_session_start_command_strings(codex_hooks)
        if not any(_ORIENTATION_SCRIPT in cmd for cmd in commands):
            errors.append(
                ValidationError(
                    type="orientation_freshness",
                    artifact=".codex/hooks.json",
                    message=(
                        f"SessionStart hook does not invoke `{_ORIENTATION_SCRIPT}`. "
                        "Recovery: `uv run gz agent sync control-surfaces`."
                    ),
                )
            )

    script = project_root / _ORIENTATION_SCRIPT
    if not script.exists():
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=_ORIENTATION_SCRIPT,
                message=(
                    f"`{_ORIENTATION_SCRIPT}` is missing. Restore the script "
                    "or revert the deletion that removed it."
                ),
            )
        )
        return errors

    headings = _script_section_headings(script)
    if headings is None:
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=_ORIENTATION_SCRIPT,
                message=(
                    "SECTION_HEADINGS tuple is missing or unparseable. "
                    "Restore the canonical tuple including "
                    f"`{_ORIENTATION_REMOTE_HEADING}`."
                ),
            )
        )
    elif _ORIENTATION_REMOTE_HEADING not in headings:
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=_ORIENTATION_SCRIPT,
                message=(
                    f"SECTION_HEADINGS does not contain "
                    f"`{_ORIENTATION_REMOTE_HEADING}`. The remote-divergence "
                    "warning class (GHI #338) requires the heading to render. "
                    "Restore it in scripts/session_orientation.py."
                ),
            )
        )

    referenced = _collect_state_references_collector(script)
    if referenced is None:
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=_ORIENTATION_SCRIPT,
                message=(
                    f"`{_ORIENTATION_AGGREGATOR}` function not found. The "
                    "aggregator must wire `collect_remote_state` into the "
                    "session-start digest."
                ),
            )
        )
    elif not referenced:
        errors.append(
            ValidationError(
                type="orientation_freshness",
                artifact=_ORIENTATION_SCRIPT,
                message=(
                    f"`{_ORIENTATION_AGGREGATOR}` does not reference "
                    f"`{_ORIENTATION_COLLECTOR}`. The remote-divergence "
                    "collector is not wired into the aggregated state — "
                    "GHI #338 fix has regressed."
                ),
            )
        )

    return errors
