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
    "PIPE",
    "STATEMENT_SEPARATORS",
    "normalize_statement_newlines",
    "program_name",
    "split_on",
    "strip_uv_run",
    "tokenize_shell",
]

#: Token that opens a new pipeline stage. Exact-match only — ``punctuation_chars``
#: emits ``||`` as a single token, so a logical-or is never read as a pipe.
PIPE = "|"

#: The tokens that END one command and begin another. **Declared, never derived.**
#: A reader that instead asks "does this token look like an operator" also splits
#: on redirection operators, which separate a command from its OPERAND rather
#: than from another command — so the operand becomes a phantom command that no
#: allowlist can match (GHI #800 residual, 2026-08-14). ``|`` is held out because
#: :mod:`gzkit.verifier_pipe_gate` needs pipeline stages *within* a statement;
#: readers wanting every command boundary use ``STATEMENT_SEPARATORS | {PIPE}``.
STATEMENT_SEPARATORS: frozenset[str] = frozenset({";", "&&", "||", "&", "\n"})


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


def normalize_statement_newlines(command: str) -> str:
    r"""Rewrite unquoted newlines as ``;`` so a multi-line command reads as a sequence.

    ``shlex`` treats ``\n`` as whitespace, so a newline never survives
    :func:`tokenize_shell` as a token and the ``"\n"`` entry in
    :data:`STATEMENT_SEPARATORS` is unreachable by that route. A multi-line
    command therefore collapses into ONE statement, which is precisely the shape
    the harness's background surface sends (GHI #940) — three statements on three
    lines read as a single run, and any per-statement reasoning silently sees one.

    A newline and a ``;`` end a statement identically, so rewriting loses nothing
    a statement-level reader needs. The scan is quote- and escape-aware because a
    newline INSIDE a quoted argument is data, not a separator.

    Offered as a separate function rather than folded into :func:`tokenize_shell`:
    other readers of this grammar are entitled to the tokens the shell would
    actually produce, and only a caller reasoning about statement sequence needs
    this normalization.
    """
    out: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(command):
        char = command[index]
        if quote is not None:
            if char == "\\" and quote == '"' and index + 1 < len(command):
                out.append(command[index : index + 2])
                index += 2
                continue
            if char == quote:
                quote = None
            out.append(char)
        elif char == "\\" and index + 1 < len(command):
            out.append(command[index : index + 2])
            index += 2
            continue
        elif char in "'\"":
            quote = char
            out.append(char)
        elif char == "\n":
            out.append(";")
        else:
            out.append(char)
        index += 1
    return "".join(out)


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


def program_name(token: str) -> str:
    r"""Return the bare program name from a command head.

    Splits on both separators rather than using ``pathlib``: the token is a
    *shell word*, not a path this process resolves, and a Windows-shaped
    ``C:\\tools\\ruff.exe`` must reduce on a POSIX host (and vice versa) because
    the gate reads commands, not the filesystem.
    """
    name = token.replace("\\", "/").rsplit("/", 1)[-1]
    return name.removesuffix(".exe")
