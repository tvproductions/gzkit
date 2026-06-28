"""MX awareness hook — shared banner/marker-read + liveness logic (ADR-0.0.74 OBPI-07).

stdlib-only marker read: this module carries NO gzkit-internal imports so
the banner fires even when gz itself is the patient (MX premise). pathlib +
json only — pydantic is deliberately omitted here even though it is present in
``gzkit.mx.marker``, because awareness is the fallback nerve for the hook
script and must remain importable when the wider gzkit package is broken.
"""

from __future__ import annotations

import json
from pathlib import Path

MX_BANNER = (
    "MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind"
)

_MARKER_RELPATH = (".gzkit", "mx.json")
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


def get_banner(project_root: Path | None = None) -> str:
    """Return the MX banner when the marker is present; empty string otherwise.

    stdlib-only: no gzkit imports — fires even when gz itself is the patient.
    """
    root = project_root if project_root is not None else _find_project_root()
    if _is_marker_active(root):
        return MX_BANNER
    return ""


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
    except (OSError, ValueError):
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
