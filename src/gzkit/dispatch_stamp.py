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
    {"if", "then", "else", "elif", "do", "while", "until", "!", "coproc", "builtin"}
)
#: Programs that run the program named after their own options, and the options
#: of theirs known to take a value. An option outside its set may take one, so
#: a command past such an option is also read for any later ``gz`` word.
_WRAPPERS: dict[str, frozenset[str]] = {
    "env": frozenset({"-u", "--unset", "-C", "--chdir"}),
    "exec": frozenset({"-a"}),
    "command": frozenset(),
    "nohup": frozenset(),
    "time": frozenset({"-f", "--format", "-o", "--output"}),
    "sudo": frozenset({"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U"}),
    "doas": frozenset({"-u", "-C"}),
    "nice": frozenset({"-n", "--adjustment"}),
    "ionice": frozenset({"-c", "--class", "-n", "--classdata", "-p", "--pid"}),
    "timeout": frozenset({"-s", "--signal", "-k", "--kill-after"}),
    "xargs": frozenset({"-I", "-i", "-n", "-P", "-L", "-l", "-d", "-a", "-E", "-e", "-s"}),
    "watch": frozenset({"-n", "--interval", "-d"}),
    "stdbuf": frozenset({"-i", "-o", "-e"}),
    "caffeinate": frozenset({"-t", "-w"}),
}
#: Programs that run a command among their arguments in a shape of their own:
#: any later ``gz`` word counts.
_RUNNERS = frozenset(
    {
        "direnv",
        "flock",
        "script",
        "parallel",
        "chronic",
        "unbuffer",
        "systemd-run",
        "taskset",
        "chrt",
        "numactl",
        "firejail",
        "strace",
        "ltrace",
        "valgrind",
        "start-process",
    }
)
#: ``uv``'s options, before or after its subcommand, known to take a value.
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
_PYTHON_VALUED = frozenset({"-X", "-W", "--check-hash-based-pycs"})
_SHELL_VALUED = frozenset({"-o", "+o", "-O", "+O", "--rcfile", "--init-file"})
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "pwsh", "powershell"})
_EVALUATORS = frozenset({"eval", "invoke-expression", "iex"})
_GROUPING = frozenset({"(", ")", "{", "}", "((", "))", "|&", ";;", ";&", ";;&", "<(", ">("})
_REDIRECTS = frozenset({">", ">>", "<", "<<", "<<<", "&>", "&>>", ">&", "<&", ">|", "<>"})
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_GZKIT_WORD = re.compile(r"\bgzkit\b", re.IGNORECASE)


def _program(word: str) -> str:
    return program_name(word.lower())


def _gz_word(word: str) -> bool:
    """Say whether a word is ``gz`` itself: bare, or a ``bin`` or ``Scripts`` path to it.

    Returns:
        True for ``gz``, ``gzkit`` or a path to either in a ``bin`` or ``Scripts``
        directory; a path elsewhere ending in ``gzkit`` is a directory, not one.

    """
    lowered = word.lower().replace("\\", "/")
    if _program(lowered) not in _GZ:
        return False
    return "/" not in lowered or any(part in lowered for part in ("/bin/", "/scripts/"))


def _skip_options(words: list[str], valued: frozenset[str]) -> tuple[list[str], bool]:
    """Drop a program's leading options, and the value of each known to take one.

    Returns:
        The words from the first that is not an option or a known option's value,
        and whether an option outside ``valued`` was skipped, which may have taken
        the next word as its value.

    """
    index, unsure = 0, False
    while index < len(words) and words[index].startswith("-") and words[index] not in {"-", "--"}:
        known = words[index] in valued
        unsure = unsure or (not known and "=" not in words[index])
        index += 2 if known else 1
    if index < len(words) and words[index] == "--":
        index += 1
    return words[index:], unsure


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


def _program_runs_gz(command: str, program: list[str], *, unsure: bool) -> bool:
    """Read a wrapper's program, and past an unknown option any later ``gz`` word.

    Returns:
        True when it runs ``gz``.

    """
    if program and _command_runs_gz(command, program):
        return True
    return unsure and any(_gz_word(word) for word in program)


def _uv_runs(command: str, rest: list[str]) -> bool:
    rest, unsure = _skip_options(rest, _UV_VALUED)
    if rest[:1] == ["run"]:
        program, later = _skip_options(rest[1:], _UV_VALUED)
    elif rest[:2] == ["tool", "run"]:
        program, later = _skip_options(rest[2:], _UV_VALUED)
    else:
        program, later = (rest if unsure else []), False
    return _program_runs_gz(command, program, unsure=unsure or later)


def _uvx_runs(command: str, rest: list[str]) -> bool:
    program, unsure = _skip_options(rest, _UV_VALUED)
    return _program_runs_gz(command, program, unsure=unsure)


def _wrapper_runs(head: str) -> Callable[[str, list[str]], bool]:
    def runs(command: str, rest: list[str]) -> bool:
        if head == "command" and rest[:1] in (["-v"], ["-V"]):
            return False  # a lookup, not a run
        if head == "env":
            for flag, value in itertools.pairwise(rest):
                if flag in {"-S", "--split-string"} and names_gz(value):
                    return True
        program, unsure = _skip_options(rest, _WRAPPERS[head])
        if head == "timeout":
            program = program[1:]  # its duration
        return _program_runs_gz(command, program, unsure=unsure)

    return runs


def _runner_runs(_command: str, rest: list[str]) -> bool:
    return any(_gz_word(word) for word in rest)


def _eval_runs(_command: str, rest: list[str]) -> bool:
    return names_gz(" ".join(rest))


def _cmd_runs(command: str, rest: list[str]) -> bool:
    switch = next((index for index, word in enumerate(rest) if word.lower() in {"/c", "/k"}), None)
    return switch is not None and _command_runs_gz(command, rest[switch + 1 :])


def _find_runs(command: str, rest: list[str]) -> bool:
    return any(
        flag in {"-exec", "-execdir", "-ok", "-okdir"}
        and _command_runs_gz(command, rest[index + 1 :])
        for index, flag in enumerate(rest)
    )


def _python_runs_gzkit(command: str, rest: list[str]) -> bool:
    """Say whether a Python command line runs gzkit.

    Returns:
        True for ``-m gzkit…`` (joined or not), ``-c`` code naming gzkit, or a
        script read from stdin (``-``) when the command names gzkit at all.

    """
    index = 0
    while index < len(rest) and rest[index].startswith("-"):
        flag = rest[index]
        value = rest[index + 1] if index + 1 < len(rest) else ""
        if flag.startswith("-m"):
            module = flag.removeprefix("-m") or value
            return module.lower().split(".")[0] == "gzkit"
        if flag == "-c":
            return _GZKIT_WORD.search(value) is not None
        if flag == "-":
            return _GZKIT_WORD.search(command) is not None
        index += 2 if flag in _PYTHON_VALUED else 1
    return False


def _shell_runs(_command: str, rest: list[str]) -> bool:
    """Read the script a shell runs with ``-c``, its flags combined or not.

    Returns:
        True when that script runs ``gz``.

    """
    index, script = 0, False
    while index < len(rest):
        flag = rest[index]
        if not flag.startswith(("-", "+")):
            return script and names_gz(flag)
        if flag in _SHELL_VALUED:
            index += 2
            continue
        if not flag.startswith("--") and "c" in flag[1:].lower():
            script = True
        index += 1
    return False


def _reader_for(head: str) -> Callable[[str, list[str]], bool] | None:
    """Pick how to read a command whose program is ``head``.

    Returns:
        The reader of its remaining words, or None for a program that runs no
        other program.

    """
    readers: dict[str, Callable[[str, list[str]], bool]] = {
        "uv": _uv_runs,
        "uvx": _uvx_runs,
        "find": _find_runs,
        "cmd": _cmd_runs,
        "py": _python_runs_gzkit,
    }
    readers |= {name: _wrapper_runs(name) for name in _WRAPPERS}
    readers |= dict.fromkeys(_EVALUATORS, _eval_runs)
    readers |= dict.fromkeys(_RUNNERS, _runner_runs)
    readers |= dict.fromkeys(_SHELLS, _shell_runs)
    if head.startswith("python"):
        return _python_runs_gzkit
    return readers.get(head)


def _command_runs_gz(command: str, words: list[str]) -> bool:
    """Say whether one simple command, its words in order, runs ``gz``.

    Returns:
        True when the program it runs, through any wrapper, is ``gz``.

    """
    words = _peel(words)
    if not words:
        return False
    head = _program(words[0])
    if head in _GZ:
        return True
    reader = _reader_for(head)
    return reader is not None and reader(command, words[1:])


def names_gz(command: str) -> bool:
    r"""Say whether a Bash command runs ``gz`` or ``gzkit`` (ruling 34).

    Reads each simple command down to the program it runs: past keywords
    (``if``, ``do``), assignments, redirections, wrappers and their options
    (``env``, ``time``, ``sudo``, ``timeout``, ``xargs``, ``watch``, ``ionice``,
    ``find -exec``, ``eval``, ``direnv exec``, ``flock``), ``uv run``, ``uv tool
    run`` and ``uvx`` past ``uv``'s options, and into ``sh -c`` scripts,
    ``$(…)``, ``<(…)`` and backticks. Past an option not known to take no
    value, any later word that is ``gz`` itself counts too, the safe error. The
    program is ``gz`` or ``gzkit`` by its name in any case (``.venv/bin/gz``,
    ``\gz``, ``GZ.EXE``), or Python running gzkit (``-m``, ``-c``, a stdin
    script). A path or word that is only an argument, ``git -C …/gzkit log``,
    ``uv run --project …/gzkit python``, is not one, so ruling 34's other calls
    keep their allow rules. ``#`` is read as a space, since the shared lexer
    ends a line at a ``#`` inside a word; a command that does not parse counts
    when it mentions ``gz`` at all. Heredoc bodies are read as commands, an
    over-match that costs the allow rule.

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
    r"""Say whether a PowerShell command runs ``gz`` or ``gzkit`` (ruling 39).

    Read as POSIX shell once its backslashes are slashes, so a Windows path keeps
    its parts: ``.venv\Scripts\gz.exe`` is ``gz``, ``git -C C:\code\gzkit``
    is not. ``Invoke-Expression``, ``iex``, ``cmd /c`` and ``Start-Process`` are
    read for the command they run.

    Returns:
        True when the command runs either.

    """
    return names_gz(command.replace("\\", "/"))


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
