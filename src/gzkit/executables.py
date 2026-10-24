"""Resolve an external tool to an absolute path before gzkit spawns it.

A bare name in an argv (``["git", ...]``) lets the operating system choose the
binary, and on Windows ``CreateProcess`` tries the current directory before
``PATH``: a ``git.exe`` committed to a repository gzkit runs inside would be the
one spawned. ``shutil.which`` keeps the same order on Windows unless
``NoDefaultCurrentDirectoryInExePath`` is set, so it cannot close that alone.

:func:`resolve_executable` walks the absolute ``PATH`` entries only and hands
each to ``shutil.which`` as a directory-qualified name, which searches that
directory alone and still honours ``PATHEXT``. A relative entry, ``.`` included,
names the current directory by another spelling and is skipped. Resolution runs
at spawn time, so a recorded argv keeps the bare, portable name (RO-9 tranche 4,
Ruff S607, ruled 2026-10-24 "Package fixed, tests curated (Rec.)").
"""

import errno
import inspect
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


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


def resolve_argv(argv: Sequence[str]) -> list[str]:
    """Return ``argv`` with its executable resolved by :func:`resolve_executable`.

    An executable named with a directory part (``sys.executable``, ``./tool``) is
    the caller's explicit choice and is kept as given; only a bare name is looked
    up. The caller keeps the bare argv for anything it records.

    Returns:
        A new argv whose first element is an absolute path or the named path.

    """
    head, *rest = argv
    if Path(head).name != head:
        return [head, *rest]
    return [resolve_executable(head), *rest]


def standalone_source() -> str:
    """Return :func:`find_executable` and :func:`resolve_executable` as source text.

    A generated hook runs as ``uv run python <hook>``, where gzkit may not be
    importable, so it carries these functions verbatim rather than a hand copy
    that could drift. The receiving script imports ``errno``, ``os``, ``shutil``
    and ``pathlib.Path``.

    Returns:
        Both functions' source, separated as top-level definitions.

    """
    return "\n\n".join(inspect.getsource(fn) for fn in (find_executable, resolve_executable))
