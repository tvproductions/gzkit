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

import contextlib
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
    tokenize_shell,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, MutableMapping

    from gzkit.ledger import Ledger

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
#: Words a shell reads before a command's program: keywords and prefixes.
_LEADERS = frozenset(
    {"if", "then", "else", "elif", "do", "while", "until", "!", "time", "coproc", "builtin"}
)
#: Programs that run the program named after their own options, and the options
#: of theirs that take a value. ``timeout`` also takes a leading duration.
_WRAPPERS: dict[str, frozenset[str]] = {
    "env": frozenset({"-u", "--unset", "-C", "--chdir", "-S", "--split-string"}),
    "exec": frozenset({"-a"}),
    "command": frozenset(),
    "nohup": frozenset(),
    "sudo": frozenset({"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U"}),
    "nice": frozenset({"-n", "--adjustment"}),
    "timeout": frozenset({"-s", "--signal", "-k", "--kill-after"}),
    "xargs": frozenset({"-I", "-i", "-n", "-P", "-L", "-l", "-d", "-a", "-E", "-e", "-s"}),
    "watch": frozenset({"-n", "--interval", "-d"}),
    "stdbuf": frozenset({"-i", "-o", "-e"}),
    "nohup.exe": frozenset(),
}
#: ``uv``'s options, before or after its subcommand, that take a value.
_UV_VALUED = frozenset(
    {
        "--project",
        "--directory",
        "--with",
        "--from",
        "--python",
        "-p",
        "--package",
        "--env-file",
        "--extra",
        "--group",
        "--index",
        "--default-index",
        "--index-url",
        "--extra-index-url",
        "--with-requirements",
        "--with-editable",
        "--config-file",
        "--cache-dir",
        "-w",
    }
)
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
_GROUPING = frozenset({"(", ")", "{", "}", "((", "))", "|&", ";;", ";&", ";;&"})
_REDIRECTS = frozenset({">", ">>", "<", "<<", "<<<", "&>", "&>>", ">&", "<&", ">|", "<>"})
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_GZKIT_WORD = re.compile(r"\bgzkit\b", re.IGNORECASE)
#: PowerShell is never lexed as POSIX shell: any gz or gzkit word counts (ruling 39).
_POWERSHELL_GZ = re.compile(r"(?<![a-z0-9_-])gz(?:kit)?(?![a-z0-9_-])", re.IGNORECASE)


def _skip_options(words: list[str], valued: frozenset[str]) -> list[str]:
    """Drop a program's leading options, and the value of each that takes one.

    Returns:
        The words from the first that is not an option or an option's value.

    """
    index = 0
    while index < len(words) and words[index].startswith("-") and words[index] != "-":
        index += 2 if words[index] in valued else 1
    return words[index:]


def _peel(words: list[str]) -> list[str]:
    """Strip what a shell reads before a command's program.

    Keywords, assignments and redirections with their targets, so the first word
    left is the program, or nothing.

    Returns:
        The words from the program on.

    """
    while words:
        word = words[0]
        if word in _LEADERS or _ASSIGNMENT.match(word):
            words = words[1:]
        elif word in _REDIRECTS or (word.isdigit() and len(words) > 1 and words[1] in _REDIRECTS):
            words = words[2:] if word in _REDIRECTS else words[3:]
        else:
            return words
    return words


def _uv_program(rest: list[str]) -> list[str]:
    """Find what a ``uv`` or ``uvx`` command runs.

    Returns:
        The words from the program ``uv run``, ``uv tool run`` or ``uvx`` runs,
        or nothing for a ``uv`` subcommand that runs none (``uv pip``).

    """
    rest = _skip_options(rest, _UV_VALUED)
    if rest[:1] == ["run"]:
        return _skip_options(rest[1:], _UV_VALUED)
    if rest[:2] == ["tool", "run"]:
        return _skip_options(rest[2:], _UV_VALUED)
    return []


def _python_runs_gzkit(command: str, rest: list[str]) -> bool:
    """Say whether a Python command line runs gzkit.

    Returns:
        True for ``-m gzkit…`` (joined or not), ``-c`` code naming gzkit, or a
        script read from stdin (``-``) when the command names gzkit at all.

    """
    for index, flag in enumerate(rest):
        value = rest[index + 1] if index + 1 < len(rest) else ""
        module = flag.removeprefix("-m") if flag != "-m" else value
        if flag.startswith("-m") and module.lower().split(".")[0] == "gzkit":
            return True
        if flag == "-c" and _GZKIT_WORD.search(value):
            return True
        if flag == "-":
            return _GZKIT_WORD.search(command) is not None
        if not flag.startswith("-"):
            return False
    return False


def _shell_script(rest: list[str]) -> str | None:
    """Read the script a shell runs with ``-c``, its flags combined or not.

    Returns:
        The script, or None when the shell is not given one.

    """
    for index, flag in enumerate(rest):
        if not flag.startswith("-") or flag.startswith("--"):
            return None
        if "c" in flag[1:]:
            return rest[index + 1] if index + 1 < len(rest) else None
    return None


def _uv_runs(command: str, rest: list[str]) -> bool:
    program = _uv_program(rest)
    return bool(program) and _command_runs_gz(command, program)


def _uvx_runs(command: str, rest: list[str]) -> bool:
    program = _skip_options(rest, _UV_VALUED)
    return bool(program) and _command_runs_gz(command, program)


def _wrapper_runs(head: str) -> Callable[[str, list[str]], bool]:
    def runs(command: str, rest: list[str]) -> bool:
        if head == "command" and rest[:1] in (["-v"], ["-V"]):
            return False  # a lookup, not a run
        program = _skip_options(rest, _WRAPPERS[head])
        if head == "timeout":
            program = program[1:]  # its duration
        return _command_runs_gz(command, program)

    return runs


def _eval_runs(_command: str, rest: list[str]) -> bool:
    return names_gz(" ".join(rest))


def _find_runs(command: str, rest: list[str]) -> bool:
    return any(
        flag in {"-exec", "-execdir", "-ok", "-okdir"}
        and _command_runs_gz(command, rest[index + 1 :])
        for index, flag in enumerate(rest)
    )


def _shell_runs(_command: str, rest: list[str]) -> bool:
    script = _shell_script(rest)
    return script is not None and names_gz(script)


def _reader_for(head: str) -> Callable[[str, list[str]], bool] | None:
    """Pick how to read a command whose program is ``head``.

    Returns:
        The reader of its remaining words, or None for a program that runs no
        other program.

    """
    readers: dict[str, Callable[[str, list[str]], bool]] = {
        "uv": _uv_runs,
        "uvx": _uvx_runs,
        "eval": _eval_runs,
        "find": _find_runs,
    }
    if head in readers:
        return readers[head]
    if head in _WRAPPERS:
        return _wrapper_runs(head)
    if head.startswith("python") or head == "py":
        return _python_runs_gzkit
    if head in _SHELLS:
        return _shell_runs
    return None


def _command_runs_gz(command: str, words: list[str]) -> bool:
    """Say whether one simple command, its words in order, runs ``gz``.

    Returns:
        True when the program it runs, through any wrapper, is ``gz``.

    """
    words = _peel(words)
    if not words:
        return False
    head = program_name(words[0]).lower()
    if head in _GZ:
        return True
    reader = _reader_for(head)
    return reader is not None and reader(command, words[1:])


def names_gz(command: str) -> bool:
    r"""Say whether a Bash command runs ``gz`` or ``gzkit`` (ruling 34).

    Reads each simple command down to the program it runs: past keywords
    (``if``, ``do``, ``time``), assignments, redirections, wrappers and their
    options (``env``, ``sudo``, ``timeout``, ``xargs``, ``watch``, ``find
    -exec``, ``eval``), ``uv run``, ``uv tool run`` and ``uvx`` with ``uv``'s
    options, and into ``sh -c`` scripts, ``$(…)`` and backticks. The program is
    ``gz`` or ``gzkit`` by its name in any case (``.venv/bin/gz``, ``\gz``,
    ``GZ``), or Python running gzkit. A path or word that is only an argument,
    ``git -C …/gzkit log``, ``uv run --project …/gzkit python``, is not one, so
    ruling 34's other calls keep their allow rules. ``#`` is read as a space,
    since the shared lexer would end a line at a ``#`` inside a word; a command
    that does not parse counts when it mentions ``gz`` at all, the safe error.
    Heredoc bodies are read as commands, an over-match that costs the allow rule.

    Returns:
        True when the command runs ``gz`` or ``gzkit``.

    """
    text = normalize_statement_newlines(command).replace("#", " ")
    tokens = tokenize_shell(text)
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
    return any(_command_runs_gz(command, segment) for segment in split_on(plain, separators))


def powershell_names_gz(command: str) -> bool:
    """Say whether a PowerShell command mentions ``gz`` or ``gzkit`` (ruling 39).

    Read as text, never as POSIX shell, whose lexer deletes a Windows path's
    backslashes: a deny that over-matches costs only that call.

    Returns:
        True when either word appears in the command.

    """
    return _POWERSHELL_GZ.search(command) is not None


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
    project's own root (ruling 38) unless an unclaimed dispatch for another root
    is open (ruling 40). One that mentions a dispatch is held to the root the
    ledger books for it, and its claim is booked (rulings 1, 35, 40). Anything
    unread stamps no root.

    Returns:
        The root, possibly empty, and the dispatch id, possibly empty.

    """
    prompt = _subagent_prompt(payload, agent_id)
    if prompt is None:
        return "", ""
    # Deferred, as in `_ledger`: only a subagent's gz command reads it.
    from gzkit.work_package_run import DISPATCH_LINE_PREFIX, read_dispatch_id  # noqa: PLC0415

    if DISPATCH_LINE_PREFIX.strip() not in prompt:
        return _undispatched_root(project_root), ""
    dispatch_id = read_dispatch_id(prompt)
    if dispatch_id is None:
        return "", ""
    return _bind(project_root, dispatch_id, agent_id, "stamp"), dispatch_id


def _ledger(project_root: Path) -> Ledger:
    """Open the project's ledger, where the coordinator books its dispatches.

    Returns:
        The ledger, at the path the project's config names.

    """
    # Deferred: `gz` imports this module on every call, and only a subagent's
    # gz command, or the Agent tool's return, reaches the ledger.
    from gzkit.config import GzkitConfig  # noqa: PLC0415
    from gzkit.ledger import Ledger  # noqa: PLC0415

    config = GzkitConfig.load(project_root / ".gzkit.json")
    return Ledger(project_root / config.paths.ledger)


def _bind(project_root: Path, dispatch_id: str, agent_id: str, source: str) -> str:
    """Read the root a dispatch intends, booking the subagent's claim of it.

    Returns:
        The root, or an empty string when the ledger cannot be read or holds no
        such dispatch. A claim that cannot be booked leaves the dispatch open,
        which errs toward refusal (ruling 40).

    """
    from gzkit.work_package_run import find_dispatch, record_dispatch_claim  # noqa: PLC0415

    try:
        ledger = _ledger(project_root)
        record = find_dispatch(ledger, dispatch_id)
    except OSError, ValueError:
        return ""
    if record is None:
        return ""
    with contextlib.suppress(OSError, ValueError):
        record_dispatch_claim(ledger, dispatch_id, agent_id, source)
    return record.intended_root


def _undispatched_root(project_root: Path) -> str:
    """Read the root an undispatched subagent is held to (rulings 38, 40).

    Returns:
        The project's own root, or an empty string while an unclaimed dispatch
        for another root is open, or when the ledger cannot be read.

    """
    from gzkit.work_package_run import open_unclaimed_dispatches  # noqa: PLC0415

    root = project_root.resolve().as_posix()
    try:
        return "" if open_unclaimed_dispatches(_ledger(project_root), root) else root
    except OSError, ValueError:
        return ""


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
    if not isinstance(command, str):
        return None
    if tool_name == "PowerShell":
        return powershell_denial() if powershell_names_gz(command) else None
    if not names_gz(command):
        return None
    root, dispatch_id = _stamp_for(payload, agent_id, project_root)
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, "command": stamp_prefix(root, dispatch_id) + command},
        }
    }


def claim_hook_output(payload: Mapping[str, Any], project_root: Path) -> None:
    """Book a dispatch's claim when the Agent tool returns (ruling 40).

    PostToolUse on Agent carries the prompt and the subagent's ``agentId``
    (probe run 8, at a foreground subagent's finish), so a dispatched subagent
    that never runs ``gz`` still claims its dispatch, and an undispatched one is
    not held to no root by it for longer than it runs.

    The hook decides nothing; it only books.
    """
    tool_input = payload.get("tool_input")
    response = payload.get("tool_response")
    if payload.get("tool_name") not in {"Agent", "Task"}:
        return
    if not isinstance(tool_input, dict) or not isinstance(response, dict):
        return
    prompt, agent_id = tool_input.get("prompt"), response.get("agentId")
    if not isinstance(prompt, str) or not isinstance(agent_id, str) or not agent_id:
        return
    from gzkit.work_package_run import read_dispatch_id  # noqa: PLC0415

    dispatch_id = read_dispatch_id(prompt)
    if dispatch_id is not None:
        _bind(project_root, dispatch_id, agent_id, "agent_returned")
