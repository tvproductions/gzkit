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
    "program_name",
    "split_on",
    "strip_nonwriting_redirections",
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

#: The descriptor-duplication operator, which ``punctuation_chars`` emits whole
#: and DISTINCT from the plain ``>`` of a file redirect. Probed, not assumed:
#: ``2>&1`` lexes as ``['2', '>&', '1']`` while ``> out.txt`` lexes as
#: ``['>', 'out.txt']``, so the operator token alone separates the two.
_FD_DUP_OPERATOR = ">&"

#: Input redirection, which feeds a file to stdin and cannot create, truncate,
#: or modify anything. Exact-match: ``<<`` and ``<<<`` are their own tokens and
#: are deliberately NOT admitted here — a heredoc's body is not in this string.
_STDIN_OPERATOR = "<"


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


def strip_nonwriting_redirections(tokens: Iterable[str]) -> list[str]:
    """Return tokens with the redirections that CANNOT write removed.

    Two members, and membership is a property of the operator rather than a
    judgment about the target:

    * ``2>&1`` — descriptor duplication. Points one descriptor at another and
      names no file, so it can create nothing and truncate nothing. A DIGIT
      target is what makes it a duplication, not the operator alone: ``>&``
      also carries csh-style ``cmd >& out.txt``, a genuine write left standing.
    * ``< path`` — input redirection. Feeds a file to stdin; there is no form
      of it that writes. ``<<`` and ``<<<`` are distinct tokens and stay.

    Deliberately absent: ``> /dev/null``. Whether a write TARGET is inert is a
    question about the path, not the operator, and no caller here models paths.

    Removal rather than classification, because these tokens actively mislead a
    reader downstream: split a command on operator-shaped tokens and ``2>&1``
    yields a phantom command named ``1`` that nobody wrote (observed refusing
    ``gz adr status <ADR> 2>&1 | head``, 2026-08-14). Deleting the group leaves
    the command structure the caller actually expressed.

    Dropping a redirection's operand cannot widen anyone's admission: prefix
    matching reads *leading* tokens, so removing tail tokens can only narrow
    what a head match sees. The leading source descriptor is consumed only when
    bare, and a bare integer is neither an allowlisted head nor a mutating flag.
    """
    parts = list(tokens)
    kept: list[str] = []
    index = 0
    while index < len(parts):
        token = parts[index]
        target = parts[index + 1] if index + 1 < len(parts) else ""
        if token == _FD_DUP_OPERATOR and target.isdigit():
            if kept and kept[-1].isdigit():
                kept.pop()  # the source descriptor: the `2` of `2>&1`
            index += 2
            continue
        if token == _STDIN_OPERATOR and target:
            index += 2
            continue
        kept.append(token)
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
