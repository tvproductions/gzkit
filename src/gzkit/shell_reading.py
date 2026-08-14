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

import os
import shlex
from collections.abc import Iterable

__all__ = [
    "PIPE",
    "STATEMENT_SEPARATORS",
    "program_name",
    "runs_no_command",
    "split_on",
    "strip_nonwriting_redirections",
    "strip_reserved_words",
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

#: Every operator that WRITES, so every operator whose target decides whether
#: anything persists. All five lex whole (probed: ``&>>`` is one token), and
#: enumerating a subset is the miss :data:`gzkit.handoff_resume_gate._PERMITTED_BASH`
#: records four consecutive times — ``2>`` alone would have left ``&>`` refusing.
_WRITE_OPERATORS: frozenset[str] = frozenset({">", ">>", ">&", "&>", "&>>"})

#: The discard sinks, per platform. ``NUL`` is the null device on Windows and an
#: ORDINARY RELATIVE FILENAME on POSIX, where ``> nul`` creates a file — so this
#: is keyed to the host that will RUN the command rather than to the string.
#: That is a deliberate exception to this module's read-the-command-not-the-
#: filesystem stance (cf. :func:`program_name`, which reduces a Windows path on a
#: POSIX host): name reduction is safe when wrong, and admission is not.
_NULL_DEVICES: frozenset[str] = frozenset({"nul"} if os.name == "nt" else {"/dev/null"})

#: Reserved words that may stand in FRONT of a real command. Stripping one
#: changes nothing about what executes, so whatever follows is re-judged on its
#: own merits — ``do rm -rf x`` still refuses on ``rm``.
#:
#: Membership is not an enumeration of examples, which is the miss
#: :data:`gzkit.handoff_resume_gate._PERMITTED_BASH` records six times. Bash's
#: reserved-word set is CLOSED and specified (``compgen -k``), so this can be
#: complete: every word in that set is either here or in
#: :data:`_WORD_LIST_HEADS`. The split between the two is by what FOLLOWS the
#: word — a command here, data there — because that is what decides whether a
#: verb check still has something to check.
#:
#: ``function`` is here rather than treated as a definition form on purpose:
#: stripping it leaves the function's NAME as the head, which matches no
#: allowlist entry and refuses. That is the right answer — a body nobody has
#: read is not a read.
_COMMAND_PREFIX_KEYWORDS: frozenset[str] = frozenset(
    {
        "!",
        "coproc",
        "do",
        "done",
        "elif",
        "else",
        "fi",
        "function",
        "if",
        "then",
        "time",
        "until",
        "while",
        "{",
        "}",
    }
)

#: Reserved words followed by a WORD LIST rather than a command. ``for x in a b``
#: and ``select x in a b`` name a variable and some data; no program is invoked,
#: so there is no verb for an allowlist to judge and the segment is admitted as
#: the syntax it is. Substitution in the word list is still refused, one layer
#: up: :func:`gzkit.handoff_resume_gate._is_compound` sees ``$(`` before this is
#: ever consulted.
#:
#: ``case`` and ``[[`` are DELIBERATELY ABSENT, not overlooked. Both are lexed
#: with punctuation (``)``, ``;;``, ``]]``) that the separator set does not
#: split on, so admitting the head would leave operator tokens inside a segment
#: and the segment refuses anyway. Supporting them means teaching the splitter
#: two more separators for a shape no verification command in this repo has ever
#: used. Naming the exclusion here is the lesson of the ``2>&1`` grouping: an
#: unstated omission gets re-read later as a policy nobody chose.
_WORD_LIST_HEADS: frozenset[str] = frozenset({"for", "in", "select"})


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
    """Return tokens with the redirections that PERSIST NOTHING removed.

    Three members, decided on two different axes — which is the part worth
    reading, because conflating them is what produced the defects this function
    exists to close:

    * ``2>&1`` — descriptor duplication, admitted by its OPERATOR. Points one
      descriptor at another and names no file. A DIGIT target is what makes it
      a duplication: ``>&`` also carries csh-style ``cmd >& out.txt``, a
      genuine write left standing.
    * ``< path`` — input redirection, admitted by its OPERATOR. Feeds a file to
      stdin; no form of it writes. ``<<`` and ``<<<`` are distinct tokens and
      stay.
    * ``> /dev/null`` and the other four write operators — admitted by their
      TARGET, and only for the sinks in :data:`_NULL_DEVICES`. The operator
      here genuinely writes; the device discards. Any other path is a real
      write and is left standing, so this is a two-element set rather than a
      path model, and nothing generalizes from it.

    The target axis was left unruled through two prior fixes on purpose: it
    widens what the gate admits on a judgment about a path, which is an
    operator's call and not an agent's (ruled 2026-08-14, verbatim "fix it
    now"). The operator axis needed no ruling because an operator with no
    writing form cannot widen anything.

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
        duplication = token == _FD_DUP_OPERATOR and target.isdigit()
        discard = token in _WRITE_OPERATORS and target.lower() in _NULL_DEVICES
        if duplication or discard:
            if kept and kept[-1].isdigit():
                kept.pop()  # the source descriptor: the `2` of `2>&1`, `2>/dev/null`
            index += 2
            continue
        if token == _STDIN_OPERATOR and target:
            index += 2
            continue
        kept.append(token)
        index += 1
    return kept


def strip_reserved_words(tokens: Iterable[str]) -> list[str]:
    """Return tokens with every leading shell reserved word removed.

    Repeated rather than single, because reserved words stack: ``do`` opens a
    body whose first word may itself be ``if``, and ``! time git log`` is legal.

    LEADING only. A reserved word in argument position is ordinary data — the
    ``do`` of ``grep do file`` is a pattern, not syntax — and this stops at the
    first token that is not reserved, so that ``grep`` is never reached.
    """
    parts = list(tokens)
    index = 0
    while index < len(parts) and parts[index] in _COMMAND_PREFIX_KEYWORDS:
        index += 1
    return parts[index:]


def runs_no_command(tokens: Iterable[str]) -> bool:
    """Return True when a token stream invokes no program at all.

    Two shapes qualify, and both are syntax rather than execution: a stream that
    is ENTIRELY reserved words (``done``, ``fi``, ``else``), and one that heads a
    word list (``for n in 803 802``). Neither names a program, so asking an
    allowlist of programs about them is asking a question it cannot hold an
    answer to — it refuses them for the same reason it refuses an unknown binary,
    which reads back to the caller as a claim that ``for`` is a command being
    guarded (operator report 2026-08-14, "this is ridiculous ... FIX IT").

    An EMPTY stream returns False, deliberately and load-bearingly. Callers reach
    this with tokens from a lexer that yields nothing on unbalanced quotes, and
    an unparseable command must fail CLOSED. Answering True for empty would make
    "I could not read this" indistinguishable from "this is pure syntax" — the
    same conflation of a lexer artifact with a policy that the ``2>&1`` refusal
    was. The resume gate's own compound check happens to refuse unparseable input
    first; this does not lean on that ordering.
    """
    parts = list(tokens)
    if not parts:
        return False
    remainder = strip_reserved_words(parts)
    return not remainder or remainder[0] in _WORD_LIST_HEADS


def program_name(token: str) -> str:
    r"""Return the bare program name from a command head.

    Splits on both separators rather than using ``pathlib``: the token is a
    *shell word*, not a path this process resolves, and a Windows-shaped
    ``C:\\tools\\ruff.exe`` must reduce on a POSIX host (and vice versa) because
    the gate reads commands, not the filesystem.
    """
    name = token.replace("\\", "/").rsplit("/", 1)[-1]
    return name.removesuffix(".exe")
