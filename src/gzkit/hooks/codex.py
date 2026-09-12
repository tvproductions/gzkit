"""Native Codex hook delivery for the retained interim integration.

Canonical producer for project orientation. The pool vendor-alignment ADR
owns broader lifecycle parity; this restores the already prescribed sync path.
Codex still requires review/trust of each generated hook before execution.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.surface_write import write_text_if_changed

_ORIENTATION = "scripts/session_orientation.py"
_ROOT = "$(git rev-parse --show-toplevel)"
_COMMAND = f'uv run --cache-dir "{_ROOT}/.gzkit/cache/uv" python "{_ROOT}/{_ORIENTATION}"'
_ADAPTER = (
    f'uv run --project "{_ROOT}" --cache-dir "{_ROOT}/.gzkit/cache/uv" python -m gzkit.hooks.codex'
)
_LABELS = {
    "orientation": "Loading gzkit project orientation",
    "SessionStart": "Loading gzkit handoff advisement",
    "PreToolUse": "Checking verification exit-code integrity",
}


def _operator_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove owned handlers, retaining other handlers even in the same group.

    The generated status labels are stable ownership markers. The old command
    array has no marker, so only its exact shipped command is migrated.
    """
    retained = []
    for group in groups:
        if group.get("command") == ["sh", "-c", _COMMAND]:
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            retained.append(group)
            continue
        remaining = [
            h
            for h in handlers
            if not (isinstance(h, dict) and h.get("statusMessage") in _LABELS.values())
        ]
        if remaining:
            retained.append({**group, "hooks": remaining})
    return retained


def _adapter_group(event: str) -> dict[str, Any]:
    return {
        "matcher": "Bash" if event == "PreToolUse" else "startup|resume|clear|compact",
        "hooks": [
            {
                "type": "command",
                "command": _ADAPTER,
                "timeout": 10,
                "statusMessage": _LABELS[event],
            }
        ],
    }


def _orientation_group() -> dict[str, Any]:
    return {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
            {
                "type": "command",
                "command": _COMMAND,
                "timeout": 30,
                "statusMessage": _LABELS["orientation"],
                "additionalContextLimit": 6000,
            }
        ],
    }


def sync_codex_hooks(project_root: Path) -> list[str]:
    """Recover orientation where its script exists, preserving unrelated hooks.

    Adopter projects without the repository's orientation script get no dangling
    command. Malformed operator JSON is surfaced, never overwritten as empty.
    All writes participate in the sync preview's capture sink.
    """
    if not (project_root / _ORIENTATION).is_file():
        return []
    path = project_root / ".codex" / "hooks.json"
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if not isinstance(payload, dict) or not isinstance(payload.get("hooks", {}), dict):
        raise ValueError(f"Invalid Codex hook configuration: {path}; repair JSON before syncing.")
    hooks = payload.setdefault("hooks", {})
    for event in ("SessionStart", "UserPromptSubmit", "PreToolUse"):
        groups = hooks.get(event, [])
        if not isinstance(groups, list) or any(not isinstance(g, dict) for g in groups):
            raise ValueError(f"Invalid {event} hook groups in {path}; repair JSON before syncing.")
        retained = _operator_groups(groups)
        if retained:
            hooks[event] = retained
        else:
            hooks.pop(event, None)
    hooks.setdefault("SessionStart", []).append(_orientation_group())
    for event in ("SessionStart", "PreToolUse"):
        hooks.setdefault(event, []).append(_adapter_group(event))
    write_text_if_changed(path, json.dumps(payload, indent=2) + "\n")
    return [path.relative_to(project_root).as_posix()]


def hook_output(payload: dict[str, Any]) -> dict[str, Any]:
    """Adapt native events to shared decisions without authorizing any work."""
    event = payload.get("hook_event_name")
    if event == "PreToolUse":
        from gzkit.verifier_pipe_gate import decide  # noqa: PLC0415

        tool_name = payload.get("tool_name")
        if tool_name not in {"Bash", "exec_command", "shell", "shell_command"}:
            return {}
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            return {}
        if "command" not in tool_input and tool_name in {"exec_command", "shell_command"}:
            tool_input = {**tool_input, "command": tool_input.get("cmd", "")}
        verdict = decide("Bash", tool_input)
        if verdict.blocked:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": verdict.reason,
                }
            }
    elif event == "SessionStart" and isinstance(payload.get("cwd"), str):
        from gzkit.session_start import build_advisement  # noqa: PLC0415

        cwd = Path(payload["cwd"]).resolve()
        root = next((p for p in (cwd, *cwd.parents) if (p / ".gzkit").is_dir()), None)
        if root is None:
            return {}
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        advisement = build_advisement(root, now=now)
        if advisement.present:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": advisement.text,
                }
            }
    return {}


def main() -> None:
    """Read one native hook payload and emit supported JSON only."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    if isinstance(payload, dict):
        output = hook_output(payload)
        if output:
            print(json.dumps(output))  # noqa: T201 — hook protocol stdout


if __name__ == "__main__":
    main()
