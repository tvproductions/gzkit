#!/usr/bin/env python3
"""MX Awareness Hook (ADR-0.0.74, OBPI-0.0.74-07).

UserPromptSubmit hook — injects the MX banner to stdout on every agent turn
while the MX marker is present. Stdout content is injected as agent context
by the Claude Code harness on each turn.

Per-turn guarantee (not agent memory): an agent drifting across edit/read
turns still receives the hangar reminder every turn. The hook reads the
marker via a stdlib-only fallback so the banner fires even when gz itself
is broken (the MX premise).

Fail-open contract: hook failure must NOT block agent turns — always exits 0.

Exit codes:
  0 - Always (fail-open; turn must always begin)
"""

import json
import os
import sys
from pathlib import Path

_RECOVER = (
    "nothing is lowered, every guard is at full strength; if a session "
    "should be open, recover with gz mx repair through the gz-mx skill"
)


def _session_bound(root: Path, session: str) -> bool:
    """Read the ledger for *session*.

    Returns:
        True when the ledger opened *session* and has not closed it.

    """
    bound = False
    try:
        lines = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    except OSError:
        return False
    for line in lines.splitlines():
        if session not in line or "mx_session_" not in line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get("session_id") != session:
            continue
        if event.get("event") == "mx_session_closed":
            bound = False
        elif event.get("event") == "mx_session_opened":
            bound = True
    return bound


def _project_root(cwd: str | None) -> Path | None:
    """Walk up from *cwd*.

    Returns:
        The nearest directory holding ``.gzkit``, or None.

    """
    start = Path(cwd).resolve() if cwd else Path.cwd()
    for candidate in (start, *start.parents):
        if (candidate / ".gzkit").is_dir():
            return candidate
    return None


def _safe_banner(contract: str) -> str:
    """Say what safe mode suspends.

    Returns:
        The banner, the stdlib twin of ``safe_mode_banner``.

    """
    return (
        "SAFE MODE ACTIVE — OBPI initiation and brief "
        f"ceremony are suspended under {contract}; most guards "
        "advisory; slow alarms off, lint and fast static checks on; "
        "gate5_invariants, the ledger through gz verbs and operator PII "
        "still bind; every act is one commit with its trailer; what it "
        "breaks goes on the punch list"
    )


def _known_marker(raw: object) -> bool:
    """Check what a marker must name.

    Returns:
        True when *raw* names a session and a known level or mode.

    """
    if not isinstance(raw, dict) or not isinstance(raw.get("session_id"), str):
        return False
    level, mode = raw.get("level", "hangar"), raw.get("mode", "mx")
    if not isinstance(level, str) or not isinstance(mode, str):
        return False
    return bool(raw["session_id"]) and level in {"hangar", "drydock"} and mode in {"mx", "safe"}


def _banner_stdlib(cwd: str | None) -> str:
    """Stdlib-only reading of the condition — the gzkit-import-free fallback."""
    _BANNER = (
        "MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind"
    )
    _MARKER = (".gzkit", "mx.json")

    root = _project_root(cwd)
    if root is None or not root.joinpath(*_MARKER).is_file():
        return ""
    try:
        raw = json.loads(root.joinpath(*_MARKER).read_text(encoding="utf-8"))
    except OSError, ValueError:
        raw = {}
    if not _known_marker(raw):
        return f"MX MARKER UNREADABLE — {_RECOVER}"
    if not _session_bound(root, str(raw["session_id"])):
        return f"MX MARKER UNBOUND — {_RECOVER}"
    if raw.get("exiting"):
        return (
            "MX EXIT RUNNING — every guard at full strength; if no exit is "
            "running, recover with gz mx repair through the gz-mx skill"
        )
    if raw.get("level") == "drydock" or raw.get("mode") == "safe":
        return _safe_banner(str(raw.get("contract") or "<no contract recorded>"))
    return _BANNER


def main() -> int:
    """Run the awareness hook; always exits 0 (fail-open)."""
    cwd: str | None = None
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
    except Exception:
        pass

    banner = ""
    try:
        from gzkit.mx.awareness import _find_project_root, get_banner

        root = _find_project_root(Path(cwd).resolve() if cwd else None)
        banner = get_banner(root)
    except Exception:
        banner = _banner_stdlib(cwd)

    if banner:
        sys.stdout.write(banner + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
