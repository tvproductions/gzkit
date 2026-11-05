"""The verb refusal of RP-12 ruling 17: a stamped call aimed at a root its dispatch did not intend.

The stamp hook (rulings 34 and 35) puts two variables in the environment of a
dispatched subagent's ``gz`` command: the root its dispatch intends and the
dispatch id. The main session's calls carry neither, so they are never refused
(#1296's case 3). The real root is the directory the verb runs in, which is what
``gzkit.commands.common.get_project_root`` answers, so the check needs only that
directory and the environment, both taken as parameters.

``gz`` runs it before any handler, for every verb (ruling 36): one check, nothing
to enumerate, so a writer added later is covered without a change here. It is on
at every level (ruling 28) and reads no mode.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

#: The root the subagent's dispatch intends; present, possibly empty, on every stamped call.
STAMP_ROOT_ENV = "GZKIT_DISPATCH_ROOT"
#: The dispatch id the stamp was read from, named in a refusal.
STAMP_ID_ENV = "GZKIT_DISPATCH_ID"


def stamp_refusal(environ: Mapping[str, str], cwd: Path) -> str | None:
    """Say why a stamped call is refused, or nothing when it may run.

    Args:
        environ: The process environment.
        cwd: The directory the verb runs in, its real project root.

    Returns:
        None for an unstamped call, or one whose stamped root is ``cwd`` once both
        are resolved; otherwise the refusal's message. A stamp naming no root, a
        subagent with no dispatch record, is refused, and so is a relative one,
        which no dispatch books.

    """
    if STAMP_ROOT_ENV not in environ:
        return None
    stamped = environ[STAMP_ROOT_ENV].strip()
    dispatch = environ.get(STAMP_ID_ENV, "").strip() or "no dispatch id"
    lead = f"Refused before any write: this call is stamped as a dispatched subagent's ({dispatch})"
    if not stamped:
        return f"{lead}, which names no intended root (RP-12 ruling 17)."
    intended = Path(stamped)
    real = cwd.resolve()
    if not intended.is_absolute():
        return f"{lead}, whose root {stamped!r} is not absolute (RP-12 ruling 17)."
    if intended.resolve() != real:
        return (
            f"{lead}, for {intended.as_posix()}, and this verb runs in {real.as_posix()}. "
            "Run it from the root the dispatch intends (RP-12 ruling 17)."
        )
    return None
