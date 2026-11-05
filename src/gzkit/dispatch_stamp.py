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

import itertools
import json
import os
import re
import shlex
from pathlib import Path
from typing import TYPE_CHECKING, Any

from gzkit.shell_reading import (
    PIPE,
    STATEMENT_SEPARATORS,
    normalize_statement_newlines,
    program_name,
    split_on,
    strip_uv_run,
    tokenize_shell,
)

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


_GZ = frozenset({"gz", "gzkit"})
#: Programs that run the command they are given, its words after their own.
_WRAPPERS = frozenset(
    {"env", "exec", "command", "time", "nohup", "sudo", "xargs", "nice", "timeout", "!"}
)
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
_GROUPING = frozenset({"(", ")", "{", "}", "((", "))", "|&"})
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_GZKIT_IMPORT = re.compile(r"\bgzkit\b")


def _is_gz(word: str) -> bool:
    return program_name(word).lower() in _GZ


def _python_runs_gzkit(words: list[str]) -> bool:
    """Say whether a Python command line runs gzkit.

    Returns:
        True for ``-m gzkit…`` or ``-c`` code naming gzkit.

    """
    for flag, value in itertools.pairwise(words):
        if flag == "-m" and value.lower().split(".")[0] == "gzkit":
            return True
        if flag == "-c" and _GZKIT_IMPORT.search(value):
            return True
    return False


def _command_runs_gz(words: list[str]) -> bool:
    """Say whether one simple command, its words in order, runs ``gz``.

    Returns:
        True when its program, or the program a wrapper runs, is ``gz``.

    """
    while words and _ASSIGNMENT.match(words[0]):
        words = words[1:]
    if not words:
        return False
    head = program_name(words[0]).lower()
    rest = words[1:]
    if head in _GZ:
        return True
    if head in {"uv", "uvx"} or head in _WRAPPERS or head.startswith("-"):
        # A leading option is `uv run`'s, left after `strip_uv_run` (`-m gzkit`,
        # `--project <dir> gz`), read like a wrapper's.
        # Options and their values vary by wrapper, so any word that is gz runs it.
        return any(_is_gz(word) for word in rest) or _python_runs_gzkit(words)
    if head.startswith("python"):
        return _python_runs_gzkit(rest)
    if head in _SHELLS:
        return any(flag == "-c" and names_gz(script) for flag, script in itertools.pairwise(rest))
    return False


def names_gz(command: str) -> bool:
    r"""Say whether a Bash command runs ``gz`` or ``gzkit`` (ruling 34).

    Reads command words, not text: a word in command position whose program is
    ``gz`` or ``gzkit`` in any case (``.venv/bin/gz``, ``\gz`` and ``GZ``
    included, since a case-folding volume runs it), behind assignments or a
    wrapper (``uv run``, ``uvx``, ``env``, ``exec``, ``time``, ``sudo``),
    ``python -m gzkit…`` or ``-c`` code importing gzkit, and a ``sh -c`` script,
    ``$(…)`` or backticks read the same way. A path or word that is only an
    argument, ``git -C …/gzkit log`` or ``ls src/gzkit``, is not one, so ruling
    34's other calls keep their allow rules. A command that does not parse
    counts when it mentions ``gz`` at all, the safe error.

    Returns:
        True when the command runs ``gz`` or ``gzkit``.

    """
    tokens = tokenize_shell(normalize_statement_newlines(command))
    if tokens is None:
        return "gz" in command.lower()
    for word in tokens:
        if (
            ("$(" in word or "`" in word)
            and word != command
            and names_gz(word.replace("$(", " ; ").replace("`", " ; ").replace(")", " ; "))
        ):
            return True
    separators = STATEMENT_SEPARATORS | _GROUPING | {PIPE}
    plain = [token for token in tokens if "`" not in token]
    return any(_command_runs_gz(strip_uv_run(segment)) for segment in split_on(plain, separators))


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


def _subagent_prompt(payload: Mapping[str, Any], agent_id: str) -> str | None:
    """Read the subagent's prompt from its own transcript (ruling 35).

    Returns:
        The prompt its first record carries, or None when the transcript is
        missing or unreadable, or its first record is not this agent's prompt.

    """
    transcript = payload.get("transcript_path")
    if not isinstance(transcript, str) or not transcript.endswith(".jsonl"):
        return None
    session = Path(transcript.removesuffix(".jsonl"))
    record = _first_record(session / "subagents" / f"agent-{agent_id}.jsonl")
    if record is None or record.get("type") != "user" or record.get("agentId") != agent_id:
        return None
    return _prompt_text(record)


def _stamp_for(payload: Mapping[str, Any], agent_id: str, project_root: Path) -> tuple[str, str]:
    """Decide the root and the dispatch id a subagent's call is stamped with.

    A prompt with no dispatch line is the undispatched subagent, held to this
    project's own root (ruling 38). One that mentions a dispatch is held to the
    root the ledger books for it (rulings 1, 35). Anything unread stamps no root.

    Returns:
        The root, possibly empty, and the dispatch id, possibly empty.

    """
    prompt = _subagent_prompt(payload, agent_id)
    if prompt is None:
        return "", ""
    # Deferred, as in `_intended_root`: only a subagent's gz command reads it.
    from gzkit.work_package_run import DISPATCH_LINE_PREFIX, read_dispatch_id  # noqa: PLC0415

    if DISPATCH_LINE_PREFIX.strip() not in prompt:
        return project_root.resolve().as_posix(), ""
    dispatch_id = read_dispatch_id(prompt)
    if dispatch_id is None:
        return "", ""
    return _intended_root(project_root, dispatch_id), dispatch_id


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


#: Why a subagent's PowerShell ``gz`` call is denied, and what to do instead.
POWERSHELL_DENIAL = (
    "A subagent's PowerShell command naming gz is denied: the dispatch stamp is "
    "measured on the Bash tool only, and an unstamped gz call from a subagent is "
    "the wrong-root write the cwd-escape guard exists to stop (RP-12 ruling 39). "
    "Run the same gz command through the Bash tool, where it is stamped with its "
    "dispatch's root."
)


def powershell_denial() -> dict:
    """Compose the PreToolUse deny for a subagent's PowerShell ``gz`` call (ruling 39).

    Returns:
        The hook output: a deny with recovery prose, rewriting nothing.

    """
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": POWERSHELL_DENIAL,
        }
    }


def stamp_hook_output(payload: Mapping[str, Any], project_root: Path) -> dict | None:
    """Decide the PreToolUse output for one Bash call (rulings 34, 35, 38).

    Args:
        payload: The hook's input.
        project_root: The project whose ledger books the dispatches.

    Returns:
        None to let the call run untouched: neither Bash nor PowerShell, the main
        session's (no ``agent_id``), or a command naming no ``gz``. A subagent's
        PowerShell ``gz`` call is denied (ruling 39). Otherwise the output that
        rewrites the command to carry the stamp, with no permission decision: a
        dispatch's root, this project's for an undispatched subagent, or none
        for a dispatch that cannot be read and found.

    """
    agent_id = payload.get("agent_id")
    tool_input = payload.get("tool_input")
    tool_name = payload.get("tool_name")
    if tool_name not in {"Bash", "PowerShell"} or not isinstance(agent_id, str) or not agent_id:
        return None
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    if not isinstance(command, str) or not names_gz(command):
        return None
    if tool_name == "PowerShell":
        return powershell_denial()
    root, dispatch_id = _stamp_for(payload, agent_id, project_root)
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, "command": stamp_prefix(root, dispatch_id) + command},
        }
    }
