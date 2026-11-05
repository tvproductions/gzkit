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

import base64
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


def is_stamped(environ: Mapping[str, str]) -> bool:
    """Say whether a call carries the stamp, so is a subagent's (rulings 17, 38).

    Returns:
        True when the root variable is present, empty or not.

    """
    return STAMP_ROOT_ENV in environ


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
    if not is_stamped(environ):
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
#: What a lifted substitution reads as: one that names gz, and one that does not.
_SUB_GZ, _SUB = "__gz_substitution__", "__substitution__"
#: Words a shell reads before a command's program: keywords and prefixes.
_LEADERS = frozenset(
    {"if", "then", "else", "elif", "do", "while", "until", "!", "coproc", "builtin"}
)
#: Programs that run the program named after their own options, and the options
#: of theirs known to take a value. Past an option outside its set, the next word
#: may be that option's value, so the word after it is read as the program too.
_WRAPPERS: dict[str, frozenset[str]] = {
    "env": frozenset({"-u", "--unset", "-C", "--chdir"}),
    "exec": frozenset({"-a"}),
    "command": frozenset(),
    "nohup": frozenset(),
    "busybox": frozenset(),
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
#: Environment managers that run a command after ``run`` or ``exec``.
_ENV_RUNNERS = frozenset(
    {"poetry", "pdm", "hatch", "pixi", "conda", "mamba", "mise", "pipx", "pyenv", "rye"}
)
_ENV_VALUED = frozenset(
    {
        "-n",
        "--name",
        "-p",
        "--prefix",
        "--spec",
        "-e",
        "--env",
        "--environment",
        "--cwd",
        "-C",
        "--directory",
        "--project",
        "--python",
    }
)
#: Programs that run a command among their arguments in a shape of their own:
#: a word that is ``gz`` itself, or a quoted command string that runs it, counts.
_RUNNERS = frozenset(
    {
        "flock",
        "script",
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
        "tmux",
        "hyperfine",
        "watchexec",
        "entr",
        "su",
        "start-process",
        "get-command",
        "direnv",
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
#: Options well known to take no value, so skipping one leaves no doubt where
#: the program starts; a program's own valued set is consulted first.
_BARE = frozenset(
    {
        "-0",
        "--null",
        "-r",
        "--no-run-if-empty",
        "-t",
        "--verbose",
        "-v",
        "-x",
        "--exit",
        "--foreground",
        "--preserve-status",
        "-q",
        "--quiet",
        "--frozen",
        "--locked",
        "--no-sync",
        "--no-project",
        "--isolated",
        "--offline",
        "--no-dev",
        "--all-extras",
        "--active",
        "--exact",
        "--no-cache",
        "-E",
        "--preserve-env",
        "-H",
        "-i",
        "--ignore-environment",
        "-S",
        "--stdin",
        "-k",
        "-b",
        "--background",
    }
)
_PARALLEL_VALUED = frozenset({"-j", "--jobs", "-S", "--sshlogin", "--joblog", "-a", "--arg-file"})
_SHELL_VALUED = frozenset({"-o", "+o", "-O", "+O", "--rcfile", "--init-file"})
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "pwsh", "powershell"})
_ENCODED = frozenset({"-encodedcommand", "-enc", "-ec", "-e"})
_EVALUATORS = frozenset({"eval", "invoke-expression", "iex"})
_GROUPING = frozenset({"(", ")", "{", "}", "((", "))", "|&", ";;", ";&", ";;&"})
_REDIRECTS = frozenset({">", ">>", "<", "<<", "<<<", "&>", "&>>", ">&", "<&", ">|", "<>"})
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
#: gzkit named as code names it, never as a dotted file (``.gzkit.json``) or a path part.
_GZKIT_CODE = re.compile(r"(?<![\w./\\-])gzkit\b", re.IGNORECASE)
#: gz or gzkit as a word of raw text, for what cannot be read as commands.
_GZ_TEXT = re.compile(r"(?<![\w./\\$-])gz(?:kit)?(?![\w.-])", re.IGNORECASE)
_HEREDOC = re.compile(r"(?<!<)<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")


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


def _strip_heredoc_bodies(text: str) -> str:
    """Drop each heredoc's body and terminator: it is data, not commands.

    Returns:
        The text with every line from a ``<<`` marker's next line to its
        terminator removed.

    """
    out: list[str] = []
    pending: list[tuple[bool, str]] = []
    for line in text.split("\n"):
        if pending:
            tabs, end = pending[0]
            if (line.lstrip("\t") if tabs else line).strip() == end:
                pending.pop(0)
            continue
        out.append(line)
        pending.extend((bool(dash), end) for dash, _quote, end in _HEREDOC.findall(line))
    return "\n".join(out)


def _next_quote(quote: str | None, char: str) -> str | None:
    """Track the quote a scan is inside after one more character.

    Returns:
        The quote character it is inside, or None.

    """
    if char in "'\"" and quote in {None, char}:
        return None if quote == char else char
    return quote


def _escaped(text: str, index: int, quote: str | None) -> bool:
    """Say whether a backslash escapes the next character (not inside single quotes).

    Returns:
        True when the character at ``index`` is such a backslash.

    """
    return text[index] == "\\" and quote != "'" and index + 1 < len(text)


def _comment_starts(text: str, index: int) -> bool:
    return text[index] == "#" and (index == 0 or text[index - 1] in " \t\n;&|()")


def _strip_comments(text: str) -> str:
    """Drop what the shell reads as a comment: ``#`` at a word's start to the line's end.

    A ``#`` inside a word is kept, as the shell keeps it, and then written as
    ``_``, since the shared lexer would read it as a comment (an insight records
    that defect of ``gzkit.shell_reading``).

    Returns:
        The text without comments, its other ``#`` written as ``_``.

    """
    out: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(text):
        if quote is None and _comment_starts(text, index):
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        if _escaped(text, index, quote):
            out.append(text[index : index + 2])
            index += 2
            continue
        quote = _next_quote(quote, text[index])
        out.append("_" if text[index] == "#" else text[index])
        index += 1
    return "".join(out)


def _closing(text: str, start: int) -> int:
    """Find the ``)`` that closes the parenthesis opened before ``start``.

    Returns:
        Its index, or -1 when it is not closed.

    """
    depth, quote, index = 1, None, start
    while index < len(text):
        if _escaped(text, index, quote):
            index += 2
            continue
        quote = _next_quote(quote, text[index])
        if quote is None:
            depth += {"(": 1, ")": -1}.get(text[index], 0)
            if depth == 0:
                return index
        index += 1
    return -1


def _substitution_at(
    text: str, index: int, quote: str | None, *, backticks: bool
) -> tuple[str, int] | None:
    """Read a substitution opening at ``index``, if one does (none in single quotes).

    Returns:
        Its text and the index of its last character, or None.

    """
    if quote == "'":
        return None
    if text[index : index + 2] in {"$(", "<(", ">("}:
        end = _closing(text, index + 2)
        return (text[index + 2 : end], end) if end >= 0 else None
    if backticks and text[index] == "`":
        end = text.find("`", index + 1)
        return (text[index + 1 : end], end) if end > index else None
    return None


def _lift_substitutions(text: str, *, backticks: bool) -> tuple[str, list[str]]:
    """Lift each ``$(…)``, ``<(…)``, ``>(…)`` and backtick pair out of a command.

    Each is a command of its own, read separately; in its place stands a word
    that reads as ``gz`` when the substitution names it (``$(which gz) status``).

    Returns:
        The text with each substitution replaced, and the substitutions' texts.

    """
    out: list[str] = []
    inners: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(text):
        if _escaped(text, index, quote):
            out.append(text[index : index + 2])
            index += 2
            continue
        lifted = _substitution_at(text, index, quote, backticks=backticks)
        if lifted is not None:
            inner, end = lifted
            inners.append(inner)
            out.append(_SUB_GZ if _GZ_TEXT.search(inner) else _SUB)
            index = end + 1
            continue
        quote = _next_quote(quote, text[index])
        out.append(text[index])
        index += 1
    return "".join(out), inners


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
        bare = words[index] in _BARE or "=" in words[index]
        unsure = unsure or (not known and not bare)
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
    """Read the program a wrapper runs: a quoted command string, or its words.

    Past an option not known to take no value, the word after the first is read
    as the program as well, the one that option may have consumed.

    Returns:
        True when it runs ``gz``.

    """
    if not program:
        return False
    if len(program) == 1 and any(char.isspace() for char in program[0]):
        return names_gz(program[0])
    if _command_runs_gz(command, program):
        return True
    return unsure and len(program) > 1 and _command_runs_gz(command, program[1:])


def _subcommand_runs(
    command: str, rest: list[str], valued: frozenset[str], verbs: tuple[tuple[str, ...], ...]
) -> bool:
    """Read a tool that runs a program after a subcommand: ``uv run``, ``poetry run``.

    Returns:
        True when the program after one of ``verbs`` runs ``gz``.

    """
    rest, unsure = _skip_options(rest, valued)
    for attempt in (rest, rest[1:] if unsure else []):
        for verb in verbs:
            if attempt[: len(verb)] == list(verb):
                program, later = _skip_options(attempt[len(verb) :], valued)
                return _program_runs_gz(command, program, unsure=later)
    return False


def _uv_runs(command: str, rest: list[str]) -> bool:
    return _subcommand_runs(command, rest, _UV_VALUED, (("run",), ("tool", "run")))


def _uvx_runs(command: str, rest: list[str]) -> bool:
    program, unsure = _skip_options(rest, _UV_VALUED)
    return _program_runs_gz(command, program, unsure=unsure)


def _env_runner_runs(command: str, rest: list[str]) -> bool:
    return _subcommand_runs(command, rest, _ENV_VALUED, (("run",), ("exec",), ("x",)))


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
    return any(_gz_word(word) for word in rest) or any(
        names_gz(word) for word in rest if any(char.isspace() for char in word)
    )


def _parallel_runs(command: str, rest: list[str]) -> bool:
    before = rest[: rest.index(":::")] if ":::" in rest else rest
    program, unsure = _skip_options(before, _PARALLEL_VALUED)
    return _program_runs_gz(command, program, unsure=unsure)


def _eval_runs(_command: str, rest: list[str]) -> bool:
    return names_gz(" ".join(rest))


def _source_runs(_command: str, rest: list[str]) -> bool:
    return bool(rest) and _gz_word(rest[0])


def _cmd_runs(_command: str, rest: list[str]) -> bool:
    switch = next((index for index, word in enumerate(rest) if word.lower() in {"/c", "/k"}), None)
    return switch is not None and names_gz(" ".join(rest[switch + 1 :]))


def _exec_flag_runs(flags: frozenset[str]) -> Callable[[str, list[str]], bool]:
    def runs(command: str, rest: list[str]) -> bool:
        return any(
            flag in flags and _program_runs_gz(command, rest[index + 1 :], unsure=False)
            for index, flag in enumerate(rest)
        )

    return runs


def _git_runs(command: str, rest: list[str]) -> bool:
    for flag, value in itertools.pairwise(rest):
        if flag in {"-x", "--exec"} and "rebase" in rest and names_gz(value):
            return True
    for index, word in enumerate(rest[:-1]):
        if word == "bisect" and rest[index + 1] == "run":
            return _program_runs_gz(command, rest[index + 2 :], unsure=False)
    return False


def _python_flag(flag: str, value: str) -> tuple[bool | None, int]:
    """Read one Python option: the verdict it settles, and the words it takes.

    Returns:
        True or False when ``-m`` or ``-c`` (joined, or last in a cluster such as
        ``-Im``) settles it, else None; and how many words the option takes.

    """
    if flag.startswith("--"):
        return None, 2 if flag == "--check-hash-based-pycs" else 1
    for position, letter in enumerate(flag[1:], start=2):
        tail = flag[position:]
        if letter == "m":
            return (tail or value).lower().split(".")[0] == "gzkit", 0
        if letter == "c":
            return _GZKIT_CODE.search(tail or value) is not None, 0
        if letter in "XW":
            return None, 1 if tail else 2
    return None, 1


def _python_runs_gzkit(command: str, rest: list[str]) -> bool:
    """Say whether a Python command line runs gzkit.

    Returns:
        True for ``-m gzkit…``, ``-c`` code naming gzkit, or a script read from
        stdin (``-``) when the command names gzkit as code does.

    """
    index = 0
    while index < len(rest) and rest[index].startswith("-") and rest[index] != "-":
        value = rest[index + 1] if index + 1 < len(rest) else ""
        verdict, step = _python_flag(rest[index], value)
        if verdict is not None:
            return verdict
        index += step
    return index < len(rest) and rest[index] == "-" and _GZKIT_CODE.search(command) is not None


def _encoded_runs_gz(value: str) -> bool:
    """Read ``pwsh -EncodedCommand``'s script; one that cannot be decoded counts.

    Returns:
        True when the script runs ``gz``, or cannot be decoded.

    """
    try:
        return names_gz(base64.b64decode(value).decode("utf-16-le"))
    except ValueError, UnicodeDecodeError:
        return True


def _shell_word(head: str, flag: str, value: str, *, script: bool) -> bool | None:
    """Read one word of a shell's arguments.

    Returns:
        The verdict it settles: ``<<<``'s string, an encoded script, or the first
        operand (``-c``'s script, or a script file, which is not read); else None.

    """
    if flag == "<<<":
        return names_gz(value)
    if flag in _REDIRECTS or flag in _SHELL_VALUED:
        return None
    if head in {"pwsh", "powershell"} and flag.lower() in _ENCODED:
        return _encoded_runs_gz(value)
    if not flag.startswith(("-", "+")):
        return script and names_gz(flag)
    return None


def _takes_script(flag: str) -> bool:
    """Say whether a shell flag (``-c``, ``-lc``, ``-Command``) makes its operand a script.

    Returns:
        True for such a flag.

    """
    if flag in _SHELL_VALUED or flag in _REDIRECTS or flag.startswith("--"):
        return False
    return flag.startswith(("-", "+")) and "c" in flag[1:].lower()


def _shell_runs(head: str) -> Callable[[str, list[str]], bool]:
    def runs(command: str, rest: list[str]) -> bool:
        """Read the script a shell runs: ``-c``'s string, ``<<<``'s, or its stdin.

        Returns:
            True when that script runs ``gz``.

        """
        index, script = 0, False
        while index < len(rest):
            flag = rest[index]
            value = rest[index + 1] if index + 1 < len(rest) else ""
            verdict = _shell_word(head, flag, value, script=script)
            if verdict is not None:
                return verdict
            script = script or _takes_script(flag)
            index += 2 if flag in _REDIRECTS or flag in _SHELL_VALUED else 1
        # No script and no file: the shell reads its stdin, from this command.
        return not script and _GZ_TEXT.search(command) is not None

    return runs


def _reader_for(head: str) -> Callable[[str, list[str]], bool] | None:
    """Pick how to read a command whose program is ``head``.

    Returns:
        The reader of its remaining words, or None for a program that runs no
        other program.

    """
    readers: dict[str, Callable[[str, list[str]], bool]] = {
        "uv": _uv_runs,
        "uvx": _uvx_runs,
        "find": _exec_flag_runs(frozenset({"-exec", "-execdir", "-ok", "-okdir"})),
        "fd": _exec_flag_runs(frozenset({"-x", "--exec", "-X", "--exec-batch"})),
        "git": _git_runs,
        "cmd": _cmd_runs,
        "parallel": _parallel_runs,
        "py": _python_runs_gzkit,
        ".": _source_runs,
        "source": _source_runs,
    }
    readers |= {name: _wrapper_runs(name) for name in _WRAPPERS}
    readers |= {name: _shell_runs(name) for name in _SHELLS}
    readers |= dict.fromkeys(_ENV_RUNNERS, _env_runner_runs)
    readers |= dict.fromkeys(_EVALUATORS, _eval_runs)
    readers |= dict.fromkeys(_RUNNERS, _runner_runs)
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
    if head in _GZ or head == _SUB_GZ:
        return True
    reader = _reader_for(head)
    return reader is not None and reader(command, words[1:])


def _reads_gz(command: str, text: str, *, backticks: bool) -> bool:
    text, inners = _lift_substitutions(_strip_comments(text), backticks=backticks)
    if any(names_gz(inner) for inner in inners):
        return True
    tokens = tokenize_shell(normalize_statement_newlines(text))
    if tokens is None:
        return _GZ_TEXT.search(text) is not None
    separators = STATEMENT_SEPARATORS | _GROUPING | {PIPE}
    return any(_command_runs_gz(command, segment) for segment in split_on(tokens, separators))


def names_gz(command: str) -> bool:
    r"""Say whether a Bash command runs ``gz`` or ``gzkit`` (rulings 34, 41).

    Reads each simple command down to the program it runs, after dropping
    heredoc bodies and comments and lifting each ``$(…)``, ``<(…)`` and
    backtick pair out to be read on its own. The program is ``gz`` or ``gzkit``
    by name in any case (``.venv/bin/gz``, ``\gz``, ``GZ.EXE``), a substitution
    naming it in command position (``$(which gz) status``), or Python running
    gzkit. Wrappers, environment runners, ``uv``, ``eval``, ``find``/``fd``
    exec flags, ``git rebase -x`` and ``bisect run``, ``cmd /c`` and shells
    (``-c``, ``<<<``, stdin) are read for what they run, a quoted command string
    included. Past an option not known to take no value, the word it may have
    consumed is skipped as well. A path or word that is only an argument is not
    one, so ruling 34's other calls keep their allow rules. A command that does
    not parse counts when it names ``gz`` as a word.

    The declared coverage is the form lists in
    ``tests/test_dispatch_stamp_hook.py`` (ruling 41); a form outside them is
    ruling 34's limit until O1's dock trial finds it in real use.

    Returns:
        True when the command runs ``gz`` or ``gzkit``.

    """
    return _reads_gz(command, _strip_heredoc_bodies(command), backticks=True)


def powershell_names_gz(command: str) -> bool:
    r"""Say whether a PowerShell command runs ``gz`` or ``gzkit`` (rulings 39, 41).

    Read by the same program reader once here-strings and block comments are
    dropped, its backslashes made slashes so a Windows path keeps its parts
    (``.venv\Scripts\gz.exe`` is ``gz``, ``git -C C:\code\gzkit`` is not), and
    its backticks left as the escapes they are. ``Invoke-Expression``, ``iex``,
    ``cmd /c``, ``Start-Process``, ``Get-Command``, ``. `` and ``pwsh
    -EncodedCommand`` are read for what they run.

    Returns:
        True when the command runs either.

    """
    text = re.sub(r"@(['\"])\n.*?\n\1@", " ", command, flags=re.DOTALL)
    text = re.sub(r"<#.*?#>", " ", text, flags=re.DOTALL)
    return _reads_gz(command, text.replace("\\", "/").replace("`", ""), backticks=False)


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

    PostToolUse on Agent carries the prompt and the subagent's ``agentId``: at a
    foreground subagent's finish, at a background one's launch (probe run 8 and
    RP-12's dock trial), so a dispatched subagent
    that never runs ``gz`` still claims its dispatch, and an undispatched one is
    not held to no root by it for longer than it runs.

    The hook decides nothing; it only books.
    """
    tool_input = payload.get("tool_input")
    response = payload.get("tool_response")
    if payload.get("tool_name") != "Agent":
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
