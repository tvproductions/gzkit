#!/usr/bin/env python3
"""Control Surface Sync Hook.

PostToolUse hook that runs `gz agent sync control-surfaces` after edits
to canonical governance files in .gzkit/.

.gzkit/ holds master versions of all control surfaces:
  - skills/ — universal, mirrored identically across vendors
  - hooks/ — master source, rendered to platform-specific forms
  - rules/ — master source, rendered to platform-specific forms

Exit codes:
  0 - Always (non-blocking; sync failures do not prevent edits)
"""

import errno
import json
import os
import shutil
import subprocess
import sys
from contextlib import suppress
from pathlib import Path

TIMEOUT_SECONDS = 30

CONTROL_SURFACE_PATTERNS = (".gzkit/",)


def find_executable(name: str) -> str | None:
    """Return the absolute path of ``name`` from the absolute ``PATH`` entries.

    The ``shutil.which`` replacement for a presence probe: same answer on POSIX,
    and on Windows never the current directory.

    Returns:
        The executable's absolute path, or None when no absolute entry holds it.

    """
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        directory = Path(entry)
        if not entry or not directory.is_absolute():
            continue
        found = shutil.which(str(directory / name))
        if found is not None:
            return found
    return None


def resolve_executable(name: str) -> str:
    """Return the absolute path of ``name``, as :func:`find_executable` finds it.

    Returns:
        The executable's absolute path.

    Raises:
        FileNotFoundError: no absolute ``PATH`` entry holds ``name``; the same
            exception ``subprocess`` raises for a missing executable, so a
            caller's existing handling still applies.

    """
    found = find_executable(name)
    if found is None:
        raise FileNotFoundError(
            errno.ENOENT,
            f"{name} is not on an absolute PATH entry; install it or add its directory to PATH",
            name,
        )
    return found


def main():
    """Run control-surface sync if the edited file is a canonical source."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    cwd = input_data.get("cwd", "")
    try:
        target = Path(file_path)
        if not target.is_absolute() and cwd:
            target = Path(cwd) / target
        target = target.resolve()
        # Find project root
        project_root = Path(cwd).resolve() if cwd else Path.cwd()
        current = project_root
        while current != current.parent:
            if (current / ".gzkit").is_dir():
                project_root = current
                break
            current = current.parent
        rel_path = target.relative_to(project_root).as_posix()
    except ValueError, TypeError, OSError:
        sys.exit(0)

    matches = any(
        rel_path.startswith(p) or rel_path == p.rstrip("/") for p in CONTROL_SURFACE_PATTERNS
    )
    if not matches:
        sys.exit(0)

    print(f"Control surface edited: {rel_path}", file=sys.stderr)
    print("Running gz agent sync control-surfaces...", file=sys.stderr)

    with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
        result = subprocess.run(  # noqa: S603 — gz agent sync, a fixed argv; executable resolved
            [resolve_executable("uv"), "run", "gz", "agent", "sync", "control-surfaces"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            cwd=str(project_root),
        )
        if result.returncode == 0:
            print("Sync complete.", file=sys.stderr)
        else:
            print(f"Sync failed (exit {result.returncode}).", file=sys.stderr)
            if result.stderr:
                print(result.stderr[:500], file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
