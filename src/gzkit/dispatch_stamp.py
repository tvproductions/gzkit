"""The verb refusal of RP-12 ruling 17: a stamped call aimed at a root its dispatch did not intend.

The stamp hook (rulings 34 and 35) puts two variables in the environment of a
dispatched subagent's ``gz`` command: the root its dispatch intends and the
dispatch id. The main session's calls carry neither, so they are never refused
(#1296's case 3). The real root is the directory the verb runs in, which is what
``gzkit.commands.common.get_project_root`` answers, so the check needs only that
directory and the environment, both taken as parameters.

``gz`` runs it before any handler, for every verb (ruling 36): one check, nothing
to enumerate, so a writer added later is covered without a change here. It is on
at every level (ruling 28) and reads no mode. A call that passes consumes the
stamp from its own process environment (ruling 37), so in one process only the
first ``main`` call is checked; nothing in the package calls ``main`` twice.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, MutableMapping

#: The root the subagent's dispatch intends; present, possibly empty, on every stamped call.
STAMP_ROOT_ENV = "GZKIT_DISPATCH_ROOT"
#: The dispatch id the stamp was read from, named in a refusal.
STAMP_ID_ENV = "GZKIT_DISPATCH_ID"


def _same_directory(intended: Path, real: Path) -> bool:
    """Compare two roots as directories, not spellings.

    The volume's own identity decides: device and inode, so a case-folding
    volume's respelling, a link and a Windows short name all count as the root
    they name. A volume that reports inode 0 (some network shares and FUSE
    mounts) gives every directory one identity, so there the resolved paths are
    compared instead, case folded on Windows only, so elsewhere a respelling
    there is refused.

    Returns:
        True when both name one directory; False otherwise, a root that does not
        exist or cannot be read included, being no directory a verb runs in.

    """
    try:
        mine, theirs = intended.stat(), real.stat()
        if mine.st_ino and theirs.st_ino:
            return (mine.st_dev, mine.st_ino) == (theirs.st_dev, theirs.st_ino)
        return os.path.normcase(intended.resolve()) == os.path.normcase(real.resolve())
    except OSError:
        return False


def stamp_refusal(environ: Mapping[str, str], real_root: Callable[[], Path]) -> str | None:
    """Say why a stamped call is refused, or nothing when it may run.

    Args:
        environ: The process environment.
        real_root: Reads the directory the verb runs in, its real project root;
            called only for a stamped call, so an unstamped one is unaffected even
            where that read fails.

    Returns:
        None for an unstamped call, or one whose stamped root is the real root's
        directory; otherwise the refusal's message. A stamp naming no root, a
        subagent with no dispatch record, is refused, and so is a root that is not
        absolute on this host, which no dispatch here books.

    """
    if STAMP_ROOT_ENV not in environ:
        return None
    stamped = environ[STAMP_ROOT_ENV].strip()
    dispatch = environ.get(STAMP_ID_ENV, "").strip() or "no dispatch id"
    lead = f"Refused before any write: this call is stamped as a dispatched subagent's ({dispatch})"
    if not stamped:
        return f"{lead}, which names no intended root (RP-12 ruling 17)."
    intended = Path(stamped)
    if not intended.is_absolute():
        return (
            f"{lead}, whose root {stamped!r} is not an absolute path on this host "
            "(RP-12 ruling 17)."
        )
    try:
        real = real_root()
    except OSError as exc:
        return (
            f"{lead}, and the directory this verb runs in cannot be read: {exc} (RP-12 ruling 17)."
        )
    if not _same_directory(intended, real):
        return (
            f"{lead}, for {intended.as_posix()}, and this verb runs in {real.as_posix()}. "
            "Run it from the root the dispatch intends (RP-12 ruling 17)."
        )
    return None


def consume_stamp(environ: MutableMapping[str, str]) -> None:
    """Take the stamp out of an environment, once its call has passed (ruling 37).

    A stamp is checked once, at the call it was put on. What that verb then runs,
    a test whose fixtures sit in a temporary directory or a nested ``gz`` the
    verb aims elsewhere, runs as the main session's would; the test harness
    drops it the same way for a test run started some other way. The limit is
    ruling 37's: a nested ``gz`` a passing verb starts is unguarded, its
    directory chosen by the verb's code, not by the agent.
    """
    for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
        environ.pop(name, None)
