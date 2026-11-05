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

import json
import os
import re
import shlex
from pathlib import Path
from typing import TYPE_CHECKING, Any

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


# A ``gz`` or ``gzkit`` word, bounded by the shell's own separators and quotes.
# Over-matching is the safe error: a stamped call only waits for approval.
_GZ_WORD = re.compile(r"""(?:^|[\s;&|()`"'])(?:gz|gzkit)(?=$|[\s;&|()`"'])""")


def names_gz(command: str) -> bool:
    """Say whether a Bash command names ``gz`` or ``gzkit`` (ruling 34).

    Returns:
        True when either word stands as a word of the command; a path, a flag or
        a longer word containing it is not one.

    """
    return _GZ_WORD.search(command) is not None


def _first_record(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as handle:
            record = json.loads(handle.readline())
    except OSError, UnicodeDecodeError, json.JSONDecodeError:
        return None
    return record if isinstance(record, dict) else None


def _prompt_text(record: dict[str, Any]) -> str:
    message = record.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        blocks = [b.get("text") for b in content if isinstance(b, dict)]
        return "\n".join(text for text in blocks if isinstance(text, str))
    return ""


def _dispatch_named(payload: Mapping[str, Any], agent_id: str) -> str | None:
    """Read the dispatch id from the subagent's own transcript (ruling 35).

    Returns:
        The id its first record names, or None when the transcript is missing or
        unreadable, its first record is not this agent's prompt, or it names none.

    """
    transcript = payload.get("transcript_path")
    if not isinstance(transcript, str) or not transcript.endswith(".jsonl"):
        return None
    session = Path(transcript.removesuffix(".jsonl"))
    record = _first_record(session / "subagents" / f"agent-{agent_id}.jsonl")
    if record is None or record.get("type") != "user" or record.get("agentId") != agent_id:
        return None
    # Deferred, as in `_intended_root`: only a subagent's gz command reads it.
    from gzkit.work_package_run import read_dispatch_id  # noqa: PLC0415

    return read_dispatch_id(_prompt_text(record))


def _intended_root(project_root: Path, dispatch_id: str) -> str:
    """Read the root the ledger books for a dispatch (rulings 1, 35).

    Returns:
        The root, or an empty string when the ledger cannot be read or holds no
        such dispatch.

    """
    # Deferred: `gz` imports this module on every call, and only a subagent's
    # gz command reaches the ledger.
    from gzkit.config import GzkitConfig  # noqa: PLC0415
    from gzkit.ledger import Ledger  # noqa: PLC0415
    from gzkit.work_package_run import find_dispatch  # noqa: PLC0415

    try:
        config = GzkitConfig.load(project_root / ".gzkit.json")
        record = find_dispatch(Ledger(project_root / config.paths.ledger), dispatch_id)
    except OSError, ValueError:
        return ""
    return record.intended_root if record is not None else ""


def stamp_prefix(root: str, dispatch_id: str) -> str:
    """Compose the prefix that puts the stamp in a command's environment.

    ``export`` rather than bare assignments, so the stamp reaches every command
    of a chain, a ``gz`` after a ``cd`` included (the probe's runs 1 and 2).

    Returns:
        The prefix, ending in a space, to put before the command.

    """
    assignments = f"{STAMP_ROOT_ENV}={shlex.quote(root)} {STAMP_ID_ENV}={shlex.quote(dispatch_id)}"
    return f"export {assignments}; "


def stamp_hook_output(payload: Mapping[str, Any], project_root: Path) -> dict | None:
    """Decide the PreToolUse output for one Bash call (rulings 34, 35).

    Args:
        payload: The hook's input.
        project_root: The project whose ledger books the dispatches.

    Returns:
        None to let the call run untouched: not Bash, the main session's (no
        ``agent_id``), or a command naming no ``gz``. Otherwise the output that
        rewrites the command to carry the stamp, with no permission decision. A
        dispatch that cannot be read and found stamps no root.

    """
    agent_id = payload.get("agent_id")
    tool_input = payload.get("tool_input")
    if payload.get("tool_name") != "Bash" or not isinstance(agent_id, str) or not agent_id:
        return None
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    if not isinstance(command, str) or not names_gz(command):
        return None
    dispatch_id = _dispatch_named(payload, agent_id) or ""
    root = _intended_root(project_root, dispatch_id) if dispatch_id else ""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, "command": stamp_prefix(root, dispatch_id) + command},
        }
    }
