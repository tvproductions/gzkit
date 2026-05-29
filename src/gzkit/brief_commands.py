"""Shared brief-command discipline (BI-1, ADR-0.0.63).

OBPI briefs author commands in ``## Verification``, ``## Demo``, and
``## Examples`` fenced blocks. Those commands are executed under the gzkit
shell-less runtime (``shlex.split`` + ``subprocess.run(shell=False)``,
GHI #415) — *not* a shell. This module is the single shared place that:

1. Extracts fenced commands as cohesive *logical* commands, joining multi-line
   constructs (``python -c "…"`` spanning lines) instead of shredding them per
   physical line (GHI #539).
2. Classifies a command as shell-less-executable or not, so compound shell
   forms (``&&``, ``||``, ``|``, ``;``, ``$(…)``, redirects) can be rejected at
   authoring time rather than failing confusingly at the verify gate
   (GHI #550 — consumed by OBPI-0.0.63-07's verify-stage gate).
3. Re-executes a demo command and binds a receipt to the *observed* exit code +
   a SHA-256 of observed stdout, flagging an exit-shape mismatch (GHI #540).

Boundary Invariant **BI-1** in the parent ADR names this as the one shared
classifier; the verify-stage gate (OBPI-07) imports from here, never a fork.
"""

from __future__ import annotations

import hashlib
import shlex
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.quality import run_command

# Bare tokens that are shell *syntax* (not program arguments) when they survive
# ``shlex.split`` as standalone tokens. An operator inside a quoted argument
# (e.g. ``python -c "a | b"``) is collapsed into one token by shlex and is data,
# not syntax — so it does not appear here.
_BARE_SHELL_OPERATORS = frozenset({"&&", "||", "|", ";", "&"})


def _command_complete(text: str) -> bool:
    """Return ``True`` when ``text`` is a complete logical command.

    Uses ``shlex`` itself to decide quote balance: an unterminated quote makes
    ``shlex.split`` raise ``ValueError``, which means the command continues on
    the next physical line. A trailing backslash is an explicit continuation.
    """
    if text.rstrip().endswith("\\"):
        return False
    try:
        shlex.split(text)
    except ValueError:
        return False
    return True


def extract_fenced_commands(section_text: str) -> list[str]:
    """Extract logical commands from the fenced code blocks in ``section_text``.

    Each fenced block (```` ``` ````-delimited) is parsed line by line. A logical
    command may span several physical lines when it carries an unterminated quote
    or a trailing backslash — a multi-line ``python -c "…"`` heredoc is returned
    as exactly one command, not one per line (GHI #539). Blank lines and comment
    lines are skipped only at a command boundary; inside an open quote every
    physical line (including ``#`` lines and indentation) is preserved verbatim.
    """
    commands: list[str] = []
    in_fence = False
    buffer: list[str] = []
    for raw in section_text.splitlines():
        if raw.strip().startswith("```"):
            if buffer:  # defensive: never let a fence boundary split a command
                commands.append("\n".join(buffer))
                buffer = []
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        if not buffer:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            buffer.append(stripped)
        else:
            buffer.append(raw.rstrip())  # preserve leading indentation mid-command
        if _command_complete("\n".join(buffer)):
            commands.append("\n".join(buffer))
            buffer = []
    if buffer:
        commands.append("\n".join(buffer))
    return commands


def command_argv(command: str) -> list[str]:
    """Tokenize ``command`` into argv exactly as the shell-less runtime will.

    A multi-line command's quoted body remains a single argv element — newlines
    are preserved inside it, never split into separate tokens (ADR Decision #3).
    """
    return shlex.split(command)


def is_shell_less_executable(command: str) -> bool:
    """Return ``True`` when ``command`` runs under ``subprocess.run(shell=False)``.

    A command fails this contract when it relies on shell syntax the runtime
    does not interpret: command chaining (``&&``/``||``/``;``/``&``), pipes
    (``|``), command substitution (``$(…)`` / backticks), or redirects
    (``>``/``<``). Operators *inside a quoted argument* are program data and are
    permitted. Unbalanced quotes are not executable.
    """
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    if not argv:
        return False
    for tok in argv:
        if tok in _BARE_SHELL_OPERATORS:
            return False
        if tok.startswith((">", "<")) or tok.endswith((">", "<")):
            return False
        if "$(" in tok or "`" in tok:
            return False
    return True


class DemoReceipt(BaseModel):
    """Observed-evidence receipt for a re-executed demo command (GHI #540)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., description="The demo command as authored in the brief")
    shell_less: bool = Field(..., description="Whether the command is shell-less-executable")
    executed: bool = Field(..., description="Whether the command was actually run")
    returncode: int = Field(..., description="Observed exit code (-1 when not executed)")
    stdout_sha256: str = Field(..., description="SHA-256 of observed stdout ('' when not executed)")
    mismatch: bool = Field(..., description="Observed exit code disagrees with the claimed shape")


def reexecute_demo(
    command: str,
    *,
    cwd: Path | None = None,
    expected_returncode: int = 0,
) -> DemoReceipt:
    """Re-execute a demo command and bind a receipt to observed behavior.

    A command that is not shell-less-executable is never run (it would error
    confusingly under the shell-less runtime); it returns a receipt with
    ``executed=False`` and ``mismatch=True`` so authoring-vs-runtime drift fails
    closed. An executed command binds the *observed* exit code and a SHA-256 of
    observed stdout — never a prose claim of what the command would do.
    """
    if not is_shell_less_executable(command):
        return DemoReceipt(
            command=command,
            shell_less=False,
            executed=False,
            returncode=-1,
            stdout_sha256="",
            mismatch=True,
        )
    result = run_command(command, cwd=cwd)
    stdout_sha256 = hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()
    return DemoReceipt(
        command=command,
        shell_less=True,
        executed=True,
        returncode=result.returncode,
        stdout_sha256=stdout_sha256,
        mismatch=result.returncode != expected_returncode,
    )
