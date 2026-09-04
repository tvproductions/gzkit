"""Cross-platform exclusive advisory file lock (GHI #945).

This module exists so the repository holds exactly ONE implementation of
"block until this process has exclusive access to a store". Two stores need
it today — the append-only corpus (``gzkit.content.corpus_store``) and the
section-ownership declaration (``gzkit.content.ownership``) — and both run a
whole-file read-modify-write, where an unserialized second writer computes
its result from a snapshot the first is already replacing and silently
discards the first writer's committed change.

It lives at package level rather than under ``gzkit.content`` because nothing
about ``flock`` / ``msvcrt.locking`` on a ``<name>.lock`` sidecar is
content-specific: the home belongs to neither caller. Reaching a shared
primitive through a private name in one caller's module (the shape this
module replaces) made the coupling invisible to ruff and to every test, so a
rename or inline in the owning module would have broken the other caller with
no mechanical signal.

The rejected alternative is restating the platform-conditional pair in each
caller. Two implementations of an OS lock drift apart, and the drift only
manifests under concurrency — the one condition ordinary use does not
exercise and ordinary tests do not reach.

Not to be confused with ``gzkit.lock_manager``, which owns OBPI *work* locks:
TTL-bearing coordination records for agents, not kernel locks on a file.
"""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import IO

if sys.platform == "win32":  # pragma: no cover - selected by platform, not by test

    def _take_exclusive(handle: IO[bytes]) -> None:
        """Block until this process holds the lock byte (Windows)."""
        import msvcrt  # noqa: PLC0415 - platform-conditional, unimportable elsewhere

        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)

    def _release_exclusive(handle: IO[bytes]) -> None:
        """Release the lock byte (Windows)."""
        import msvcrt  # noqa: PLC0415 - platform-conditional, unimportable elsewhere

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

else:

    def _take_exclusive(handle: IO[bytes]) -> None:
        """Block until this process holds the lock (POSIX)."""
        import fcntl  # noqa: PLC0415 - platform-conditional, unimportable elsewhere

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)

    def _release_exclusive(handle: IO[bytes]) -> None:
        """Release the lock (POSIX)."""
        import fcntl  # noqa: PLC0415 - platform-conditional, unimportable elsewhere

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def exclusive_file_lock(path: Path) -> Iterator[None]:
    """Serialize a read-modify-write sequence for *path* across writers.

    The lock is an OS lock on a sidecar file, never a marker file whose
    presence means "held": a marker survives the process that created it, so
    one crash would wedge an append-only canon store permanently. Both
    ``flock`` and ``msvcrt.locking`` are released by the kernel when the
    handle closes — including on abnormal exit.

    The sidecar is NOT *path*. Callers commit by replacing *path*, which on
    POSIX gives the new file a different inode; a lock taken on the old inode
    would protect a file no later writer opens.

    The caller owns *path*'s parent directory: the sidecar is opened beside
    *path*, so a caller whose store directory may not exist yet must create it
    before entering. *path* itself is neither created nor read here.
    """
    lock_path = path.with_name(f"{path.name}.lock")
    with lock_path.open("ab+") as handle:
        _take_exclusive(handle)
        try:
            yield
        finally:
            _release_exclusive(handle)
