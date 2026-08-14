r"""Quote-aware shell-command reading — the single source of gzkit's lexer facts.

Two PreToolUse gates read a Bash command string before the harness runs it, and
they ask different questions of it:

* :mod:`gzkit.handoff_resume_gate` asks *is this a mutation* (Operator
  Authorization Gate, GHI #574).
* :mod:`gzkit.verifier_pipe_gate` asks *does this mask a verifier's exit status*
  (`.gzkit/rules/tests.md` § Verification exit-code integrity, GHI #589).

Different predicates, one lexer. The lexer *configuration* below is the part that
was established by probing the real ``shlex`` rather than by reasoning about it,
and it is load-bearing in three ways:

* ``posix=True`` is REQUIRED. In non-posix mode a quote that opens mid-token
  raises ``No closing quotation`` — which would fail closed on
  ``git log --since='60 days ago' --grep='^fix('``, the precedent-check command
  AGENTS.md § Defect-fix routing *mandates*, leaving an agent stuck between two
  binding rules.
* ``punctuation_chars=True`` emits real control operators as standalone tokens,
  so a metacharacter *inside a quoted argument* is never mistaken for one. A
  regex over the raw string cannot tell ``a | b`` from ``grep "a\\|b"``, and the
  first resume-gate implementation refused ``jq`` filters and alternation
  patterns — the most ordinary instruments those gates have.
* Tokenization ALONE is not sufficient. Backticks are not punctuation to
  ``shlex``, so ``gz state `rm -rf x``` yields no operator token at all. A caller
  that cares about command substitution must check for it separately; this module
  deliberately does not decide that for anyone.

Restating this configuration in a second reader is exactly how two gates drift
apart on the same input, so both import from here — the single-reader discipline
``rule_version_of()`` and ``TaskId.parse`` already follow.
"""

from __future__ import annotations

import shlex
from collections.abc import Iterable

__all__ = [
    "program_name",
    "split_on",
    "strip_fd_duplications",
    "strip_uv_run",
    "tokenize_shell",
]

#: The duplication operator, which ``punctuation_chars`` emits whole and
#: DISTINCT from the plain ``>`` of a file redirect. Probed, not assumed:
#: ``2>&1`` lexes as ``['2', '>&', '1']`` while ``> out.txt`` lexes as
#: ``['>', 'out.txt']``, so the operator token alone separates the two.
_FD_DUP_OPERATOR = ">&"


def tokenize_shell(command: str) -> list[str] | None:
    """Return quote-aware tokens with control operators split out, or None.

    ``None`` means the command is unparseable (unbalanced quotes). Callers decide
    what that means for them — the resume gate fails CLOSED on it (an
    unparseable command is not a recognized read), while the verifier-pipe gate
    declines to guess (the shell will reject it anyway).
    """
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return None


def strip_uv_run(tokens: Iterable[str]) -> list[str]:
    """Return tokens with every leading ``uv run`` prefix removed.

    Repeated rather than single because ``uv run uv run gz check`` is legal and
    would otherwise smuggle a command past a prefix match.
    """
    parts = list(tokens)
    while parts[:2] == ["uv", "run"]:
        parts = parts[2:]
    return parts


def split_on(tokens: Iterable[str], separators: frozenset[str]) -> list[list[str]]:
    """Split a token stream into segments on exact separator tokens.

    Exact-match, never substring: ``punctuation_chars`` emits ``||`` as one token,
    so splitting on ``{"|"}`` correctly leaves a logical-or intact rather than
    reading it as two empty pipelines.
    """
    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in separators:
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    return segments


def strip_fd_duplications(tokens: Iterable[str]) -> list[str]:
    """Return tokens with file-descriptor duplications (``2>&1``) removed.

    A duplication points one descriptor at another. It names no file, so it can
    create nothing and truncate nothing — unlike ``> out.txt``, whose operand is
    a path. Both wear a ``>``, and that shared character is the whole reason a
    reader classifying by character shape confuses them.

    A DIGIT target is what makes it a duplication, not the operator alone:
    ``>&`` also carries the csh-style ``cmd >& out.txt`` that redirects both
    streams to a FILE, which is a genuine write and is left standing here.

    Removal rather than classification, because the tokens mislead every
    downstream reader: a caller splitting on operator-shaped tokens reads the
    target as a command named ``1`` that nobody wrote (observed refusing
    ``gz adr status <ADR> 2>&1 | head``, 2026-08-14). Deleting the group leaves
    the pipeline structure the caller actually expressed.

    The leading source descriptor is consumed only when bare, and dropping it
    cannot widen anyone's admission: prefix matching reads *leading* tokens, and
    a bare integer is neither an allowlisted head nor a mutating flag.
    """
    parts = list(tokens)
    kept: list[str] = []
    index = 0
    while index < len(parts):
        target = parts[index + 1] if index + 1 < len(parts) else ""
        if parts[index] == _FD_DUP_OPERATOR and target.isdigit():
            if kept and kept[-1].isdigit():
                kept.pop()  # the source descriptor: the `2` of `2>&1`
            index += 2
            continue
        kept.append(parts[index])
        index += 1
    return kept


def program_name(token: str) -> str:
    r"""Return the bare program name from a command head.

    Splits on both separators rather than using ``pathlib``: the token is a
    *shell word*, not a path this process resolves, and a Windows-shaped
    ``C:\\tools\\ruff.exe`` must reduce on a POSIX host (and vice versa) because
    the gate reads commands, not the filesystem.
    """
    name = token.replace("\\", "/").rsplit("/", 1)[-1]
    return name.removesuffix(".exe")
