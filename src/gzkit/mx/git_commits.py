"""Git's commits as the maintenance record's views read them (RP-12 rulings 170, 192 and 193).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the commit that lands an
entry's work names it in its subject (ruling 170), and both views of the record, the
MX log at `gz mx exit` and `gz wp entry show`, join each entry to those commits
through `gzkit.mx.entries.landings`, which takes the commits as a parameter (ruling
192). This module is the one git reader both views call, so both read the subject as
git does, ``%s``: the first paragraph of the message, its lines joined.

A git that cannot be read is never an empty history (ruling 193): the reader raises
`CommitsUnreadableError` naming the cause, the exit refuses on it, and
`gz wp entry show` names it in place of each Landed line.
"""

import subprocess
from typing import TYPE_CHECKING

from gzkit.executables import resolve_argv
from gzkit.mx.entries import LandingCommit

if TYPE_CHECKING:
    from pathlib import Path

#: git log field and record separators: the ASCII unit and record separators, which
#: do not appear in normal commit text; a message carrying one splits its record, and
#: the reader refuses that record as unreadable rather than misread it.
FIELD_SEP = "\x1f"
RECORD_SEP = "\x1e"


class CommitsUnreadableError(RuntimeError):
    """Git could not be read, so no view may read the commits as none (ruling 193)."""


def git_log(root: Path, selection: list[str], fields: tuple[str, ...]) -> list[list[str]]:
    """Read ``git log`` over *selection*: each commit's SHA, then each of *fields* (``%s``, ``%B``).

    Returns:
        One list per commit, newest first: its SHA, then exactly one value per field.

    Raises:
        CommitsUnreadableError: git could not run, or exited non-zero (not a
            repository, or one with no commit yet), or a record did not split into
            its SHA and fields (a message carrying a separator); the message names
            the cause.

    """
    pretty = "%H" + "".join(FIELD_SEP + field for field in fields) + RECORD_SEP
    cmd = ["git", "log", *selection, f"--pretty=format:{pretty}"]
    try:
        result = subprocess.run(  # noqa: S603 — the git log argv this module builds
            resolve_argv(cmd),
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        msg = f"git could not run ({exc})"
        raise CommitsUnreadableError(msg) from exc
    if result.returncode != 0:
        cause = result.stderr.strip().splitlines()[0] if result.stderr.strip() else "no message"
        msg = f"`git log` exited {result.returncode}: {cause}"
        raise CommitsUnreadableError(msg)
    records: list[list[str]] = []
    # git puts a newline between records; strip only that, never str.strip(), which
    # reads the separators themselves as whitespace and would drop an empty field.
    for raw in result.stdout.split(RECORD_SEP):
        if not (record := raw.lstrip("\n")):
            continue
        parts = record.split(FIELD_SEP, len(fields))
        if len(parts) != len(fields) + 1:
            msg = f"a `git log` record did not parse: {record[:60]!r}"
            raise CommitsUnreadableError(msg)
        records.append(parts)
    return records


def commits_citing_entries(root: Path) -> list[LandingCommit]:
    """Read every commit in HEAD's ancestry whose message carries ``ENT-`` (ruling 192).

    `gz wp entry show` joins the record to these through `gzkit.mx.entries.landings`,
    which reads each whole id from the subject alone; git's ``--grep`` only narrows
    the read.

    Returns:
        Each such commit, newest first, its subject as git reads it (``%s``).

    """
    return [
        LandingCommit(commit_sha=sha, subject=subject.strip())
        for sha, subject in git_log(root, ["--fixed-strings", "--grep", "ENT-"], ("%s",))
    ]
