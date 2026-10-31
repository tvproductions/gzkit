"""MX awareness hook — shared banner/marker-read + liveness logic (ADR-0.0.74 OBPI-07).

stdlib-only marker read: this module carries NO gzkit-internal imports so
the banner fires even when gz itself is the patient (MX premise). pathlib +
json only — pydantic is deliberately omitted here even though it is present in
``gzkit.mx.marker``, because awareness is the fallback nerve for the hook
script and must remain importable when the wider gzkit package is broken.
"""

import json
from pathlib import Path

MX_BANNER = (
    "MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind"
)


MX_EXITING_BANNER = "MX EXIT RUNNING — every guard at full strength until gz mx exit finishes"


def void_marker_banner(cause: str) -> str:
    """Return the banner for a marker that lowers nothing, naming *cause* and its recovery."""
    return (
        f"MX MARKER {cause.upper()} — nothing is lowered, every guard is at full strength; "
        "if a session should be open, recover with gz mx repair through the gz-mx skill"
    )


def safe_mode_banner(contract: str) -> str:
    """Return the per-turn banner for safe mode (GHI #1244)."""
    return (
        f"SAFE MODE ACTIVE — OBPI initiation and brief ceremony are suspended "
        f"under {contract or '<no contract recorded>'}; most guards advisory; "
        "slow alarms off, lint and fast static checks on; gate5_invariants, the ledger "
        "through gz verbs and operator PII still "
        "bind; every act is one commit with its trailer; what it breaks goes on the punch list"
    )


_MARKER_RELPATH = (".gzkit", "mx.json")
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")
_HOOK_RELPATH = (".claude", "hooks", "mx-awareness.py")
_SETTINGS_RELPATH = (".claude", "settings.json")
_HOOK_SCRIPT_NAME = "mx-awareness.py"


def _find_project_root(start: Path | None = None) -> Path:
    """Walk up from *start* to the nearest directory holding ``.gzkit``.

    Mirrors ``gzkit.mx.marker._find_project_root`` — duplicated deliberately
    so this module stays free of gzkit-internal imports.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".gzkit").is_dir():
            return candidate
    return current


def _is_marker_active(project_root: Path) -> bool:
    return project_root.joinpath(*_MARKER_RELPATH).is_file()


def _read_marker(project_root: Path) -> dict | None:
    """Parse the marker with stdlib ``json``.

    Returns:
        Its object, or None when it cannot name a session and a mode.

    """
    try:
        raw = json.loads(project_root.joinpath(*_MARKER_RELPATH).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None
    if not isinstance(raw, dict) or not raw.get("session_id"):
        return None
    return raw if raw.get("mode", "mx") in {"mx", "safe"} else None


def _session_is_open(project_root: Path, session_id: str) -> bool:
    """Return True when the ledger opened *session_id* and has not closed it.

    The stdlib twin of ``gzkit.mx.marker._open_session_ids``: this module imports
    no gzkit code, so the banner fires when gz is the patient.

    Returns:
        True when an open event stands with no close after it.

    """
    state = False
    try:
        text = project_root.joinpath(*_LEDGER_RELPATH).read_text(encoding="utf-8")
    except OSError:
        return False
    for line in text.splitlines():
        if session_id not in line or "mx_session_" not in line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get("session_id") != session_id:
            continue
        if event.get("event") == "mx_session_closed":
            return False
        state = state or event.get("event") == "mx_session_opened"
    return state


def get_banner(project_root: Path | None = None) -> str:
    """Return the banner for the condition; empty string when there is no marker.

    It says what ``gzkit.mx.marker.condition`` reads: a marker that is unreadable or
    unbound lowers nothing and is announced (GHI #1273). stdlib-only: no gzkit
    imports — fires even when gz itself is the patient.
    """
    root = project_root if project_root is not None else _find_project_root()
    if not _is_marker_active(root):
        return ""
    held = _read_marker(root)
    if held is None:
        return void_marker_banner("unreadable")
    if not _session_is_open(root, str(held["session_id"])):
        return void_marker_banner("unbound")
    if held.get("exiting"):
        return MX_EXITING_BANNER
    if held.get("mode") == "safe":
        return safe_mode_banner(str(held.get("contract") or ""))
    return MX_BANNER


class LivenessResult:
    """Result carrier for the hook liveness check."""

    def __init__(self, ok: bool, defect: str | None = None) -> None:
        """Initialize with the liveness ``ok`` flag and optional ``defect`` detail."""
        self.ok = ok
        self.defect = defect

    def __repr__(self) -> str:
        """Return the debug representation of the liveness result."""
        if self.ok:
            return "LivenessResult(ok=True)"
        return f"LivenessResult(ok=False, defect={self.defect!r})"


def check_hook_liveness(project_root: Path | None = None) -> LivenessResult:
    """Check whether the Claude hook adapter is wired and alive.

    Returns ``LivenessResult(ok=True)`` when the hook file exists and is
    registered in ``.claude/settings.json`` as a ``UserPromptSubmit`` hook.
    Returns ``LivenessResult(ok=False, defect=<reason>)`` for any defect.
    A non-ok result means the per-turn awareness guarantee is broken.
    """
    root = project_root if project_root is not None else _find_project_root()

    hook_path = root.joinpath(*_HOOK_RELPATH)
    if not hook_path.is_file():
        return LivenessResult(
            ok=False,
            defect=f"hook file missing: {hook_path.relative_to(root).as_posix()}",
        )

    settings_path = root.joinpath(*_SETTINGS_RELPATH)
    if not settings_path.is_file():
        return LivenessResult(
            ok=False,
            defect=f"settings.json missing: {settings_path.relative_to(root).as_posix()}",
        )

    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return LivenessResult(ok=False, defect="cannot read .claude/settings.json")

    hooks = data.get("hooks", {})
    for group in hooks.get("UserPromptSubmit", []):
        for hook in group.get("hooks", []):
            if _HOOK_SCRIPT_NAME in hook.get("command", ""):
                return LivenessResult(ok=True)

    return LivenessResult(
        ok=False,
        defect="mx-awareness.py not registered in settings.json UserPromptSubmit hooks",
    )
