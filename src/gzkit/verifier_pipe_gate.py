"""Verification exit-code integrity gate — the clause's teeth (GHI #589).

`.gzkit/rules/tests.md` § Verification exit-code integrity has been **binding
prose since rule 0.8.0** and enforced by nothing:

    "A verifier's truth is its own exit code, never a downstream filter's. NEVER
    pipe `unittest`/`behave`/`mkdocs --strict` (or any ARB-wrapped verifier)
    through `tail`/`head`/`grep`/`Select-Object`: the shell reports the *last*
    process's exit (the filter's — always 0), masking a failing suite as a green
    run. ... A harness 'exit code 0' notification on a piped command attests the
    filter, not the verifier."

`docs/governance/advisory-rules-audit.md` row 66 scored it **Promotable,
unenforced** and named this promotion path. It is the highest-frequency observed
violation class in agent sessions, and its failure mode is the worst kind: it
does not error, it produces a *confident false green* that then gets relayed to
an operator as attestation evidence.

Design notes that are load-bearing:

* **The masking is the pipe, not the filter.** The clause names ``tail``/``head``/
  ``grep``/``Select-Object``, but those are instances. The shell reports the LAST
  process's exit whatever that process is, so a gate keyed to a filter allowlist
  would wave ``gz check | cat`` straight through — the identical defect wearing a
  different name. Enumerate-the-examples is the failure this codebase has now
  repeated three times on the resume gate's own allowlist (see
  :data:`gzkit.handoff_resume_gate._PERMITTED_BASH`); the predicate is
  *is a verifier upstream of any pipe*, and that is what is implemented here.

* **A verifier is what a segment RUNS, not a name that appears in it.** A
  substring or token-presence check would refuse ``grep -rn "unittest" src/``,
  which mentions a verifier and runs none. Resolution goes through the command
  head and the ``-m <module>`` form instead.

* **The verifier set is READ from the ARB registry, not restated.**
  ``CANONICAL_STEP_COMMANDS`` is the locked authority for what "an ARB-wrapped
  verifier" means (AGENTS.md § Attestation), so a canonical step added there is
  covered here by construction. A hand-copied list would silently stop matching
  the clause it enforces — the drift class GHI #754 found one file over.

* **Two escapes are honored because they genuinely work.** ``pipefail`` makes the
  shell report the first failing stage, and ``PIPESTATUS[0]`` is the clause's own
  named remedy. Both are explicit operator opt-ins; refusing them would make the
  gate un-compliable for the one correct way to pipe a verifier.

* **An escape counts when it is USED, never when it is NAMED** — the bullet above
  applied to the excuse half (GHI #796). The escape predicate was a substring scan
  over every token in the command, so ``grep -rn "pipefail" docs/ ; gz check | tail``
  disarmed the gate: the word had only to appear, not to set anything. That is the
  same token-presence test the bullet below rejects for verifiers, applied to the
  fail-OPEN half — the gate resolved what it REFUSED semantically and what it
  EXCUSED lexically, and only the lexical half leaked. Resolution is now
  head-based for ``set`` and reference-based for ``PIPESTATUS``, and ordered:
  shell state protects what follows it, never what already ran.

Coverage limits are declared, not hidden — see :data:`UNWITNESSABLE`.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS
from gzkit.shell_reading import (
    PIPE,
    STATEMENT_SEPARATORS,
    normalize_statement_newlines,
    program_name,
    split_on,
    strip_uv_run,
    tokenize_shell,
)

__all__ = [
    "GZ_VERIFIER_VERBS",
    "UNWITNESSABLE",
    "VERIFIER_ESCAPE_CLAIM_ID",
    "VERIFIER_PIPE_CLAIM_ID",
    "VERIFIER_PIPE_CLAIM_IDS",
    "VERIFIER_PROGRAMS",
    "Verdict",
    "decide",
    "masked_verifier",
    "masked_verifier_reason",
]

#: Tokens that END a pipeline. A verifier in an earlier statement is not upstream
#: of a later statement's pipe: ``gz check; ls | head`` masks nothing. Read from
#: :mod:`gzkit.shell_reading` rather than restated — the resume gate splits on
#: the same grammar, and a second copy is how the two would come to disagree
#: about what ends a command (GHI #800 residual, 2026-08-14).
_STATEMENT_SEPARATORS = STATEMENT_SEPARATORS
_PIPE = PIPE

#: Interpreters whose ``-m <module>`` form names the real program.
_PYTHON_RUNNERS: frozenset[str] = frozenset({"python", "python3", "python3.13", "py"})

#: The builtin that actually enables ``pipefail``. The HEAD is the
#: discriminator, exactly as it is on the verifier side: ``pipefail`` reaching
#: the shell any other way — a ``grep`` pattern, an ``echo`` argument, a flag
#: value — changes no shell state at all (GHI #796).
_SET_BUILTIN = "set"

#: The operand that names the option, in either spelling the shell accepts:
#: ``set -o pipefail`` and ``set -euo pipefail`` both leave it a bare token.
_PIPEFAIL_OPERAND = "pipefail"

#: A parameter REFERENCE, not a bare word. ``${PIPESTATUS[0]}`` and
#: ``$PIPESTATUS`` read the array the clause names; ``PIPESTATUS.md`` is a
#: filename and reads nothing.
_PIPESTATUS_REFERENCES: tuple[str, ...] = ("${PIPESTATUS", "$PIPESTATUS")

#: Separators after which the aggregate exit status is NO LONGER the preceding
#: statement's (GHI #940, widened GHI #970). ``&&`` is absent because it
#: short-circuits: a failing verifier aborts the list and its status IS the
#: LIST's status — which is not the command's once a later separator in this set
#: ends the list. The arm therefore reads the separator ending the verifier's
#: AND-OR list, never its own terminator (GHI #971): ``verifier && ok; ls`` exits 0.
#:
#: ``||`` WAS absent on the reasoning that its branch "runs only on failure and
#: announces it", which is the verdict idiom GHI #942 preserved one surface over.
#: That reasoning conflated ANNOUNCING with REPORTING. The branch does announce,
#: in output — and then replaces the failing status with its own, so
#: ``verifier || echo failed`` exits 0 *exactly when* the verifier failed. Every
#: consumer that reads the status rather than the transcript therefore sees green
#: at the one moment there is something to hide, and on the Step-4a packet surface
#: — a CURATED excerpt, where omission is the whole attack — the announcement can
#: simply not be pasted. Measured 2026-09-06: such a packet verified with zero
#: blockers.
#:
#: What keeps the verdict idiom alive is not this set but the scope the arm
#: already had — a recognized VERIFIER. ``test -f x && echo DEFECT || echo OK``
#: exits non-zero when the assertion HOLDS, and runs no verifier, so it never
#: reaches here. All 3 top-level ``||`` transcripts in this repository's 1154 are
#: that shape.
_MASKING_SEPARATORS: frozenset[str] = frozenset({";", "\n", "&", "||"})

#: The masking separators ``set -e`` genuinely aborts on — a strict subset, and
#: the distinction is measured, not reasoned (GHI #970). ``sh -c 'set -e; false
#: || echo caught'`` exits 0 because POSIX suppresses errexit for a command on
#: the left of ``||``, and ``sh -c 'set -e; false & wait'`` exits 0 because
#: errexit cannot fire on a background job. Honoring the escape there would hand
#: the caller a disarm that disarms only the gate.
_ERREXIT_PROTECTED_SEPARATORS: frozenset[str] = frozenset({";", "\n"})

#: The separator whose branch REPLACES a failing status rather than discarding a
#: silent one. Named because the arm it selects has its own recovery.
_OR_ELSE = "||"

#: The separator that carries a failure through an AND-OR list to the list's end.
_AND_THEN = "&&"

#: The separator that backgrounds its list. After it, ``$?`` is the LAUNCH's
#: status — 0 — so a status read there reports success over a failing verifier
#: (measured: ``false & echo "REAL EXIT: $?"`` prints 0; GHI #971).
_BACKGROUND = "&"

#: Short-flag bundle or long operand that turns on ``errexit``. ``set -e`` and
#: ``set -euo pipefail`` both abort the sequence on a failing verifier, so the
#: aggregate carries the failure. Read on USE like ``pipefail`` (GHI #796).
_ERREXIT_LONG_OPERAND = "errexit"

#: A parameter REFERENCE to the last exit status. ``$?`` and ``${?}`` retrieve
#: it; a bare word containing a question mark retrieves nothing.
_EXIT_STATUS_REFERENCES: tuple[str, ...] = ("$?", "${?")

#: `gz` sub-verbs that run a verification tier. `gz` alone is far too coarse —
#: `gz state | grep ADR-x` is an ordinary read and must stay permitted.
GZ_VERIFIER_VERBS: frozenset[str] = frozenset(
    {"check", "test", "smoke", "validate", "lint", "typecheck", "arb", "covers", "audit"}
)

#: Verifiers the clause governs that the ARB step registry cannot supply:
#: `behave` has no canonical STEP command (it runs inside `gz test`), `ruff`'s
#: canonical invocation emits a LINT receipt rather than a step receipt, and
#: `pytest` is forbidden outright by `.gzkit/rules/tests.md` § General Rules —
#: if one ever appears, its exit status still must not be masked.
#:
#: `unittest` joined this set when the canonical step moved to the pinned
#: `unittest-parallel` runner (GHI #856). It is NOT redundant with that entry:
#: `_canonical_program_names` derives only what the table names, so the swap
#: silently dropped `unittest` from `VERIFIER_PROGRAMS` — and `uv run -m unittest`
#: is still how a scoped run is spelled at ~3,100 call sites in this repo, every
#: one of which must keep failing closed when piped. Membership here is what
#: `_module_verifier` reads for the `-m <module>` form.
#:
#: `coverage` joined for the same reason when its canonical step followed onto
#: the parallel runner (GHI #1027): the table no longer names the `coverage`
#: program, while `coverage run ...` and `coverage report --fail-under` are still
#: typed by hand and by the `coverage-40pct` chore, and a piped floor check that
#: reads green is the exact masked verifier this gate exists to refuse.
_DECLARED_BEYOND_ARB: frozenset[str] = frozenset(
    {"behave", "ruff", "pytest", "unittest", "coverage"}
)

#: Coverage this gate structurally cannot provide. Stated so a green is never
#: read as total (the `unwitnessable.md` precedent the resume gate follows).
UNWITNESSABLE: tuple[str, ...] = (
    "Verifiers invoked through a shell script or Makefile target: the gate reads "
    "the command string the harness is asked to run, not what that command runs "
    "in turn.",
    "Non-Bash execution surfaces (MCP tool calls, IDE-run tasks) never reach the "
    "Bash matcher, so a verifier piped there is unseen.",
    "`pipefail` / `PIPESTATUS` are honored on USE but not on CORRECT use: a "
    "command that genuinely sets pipefail, or reads PIPESTATUS after some other "
    "pipeline, and then ignores the value is permitted. Scoping the read to the "
    "pipeline it describes needs dataflow the token stream does not carry. "
    "Merely NAMING an escape no longer disarms the gate (GHI #796).",
    "`set -e` and an immediate `$?` read are honored on the same terms (GHI "
    "#940): a command that reads the status and then discards the value is "
    "permitted, because whether a printed status is READ is not a property of "
    "the command string.",
    "THE AGGREGATE STATUS ITSELF (GHI #940). Even a correctly-written `verifier "
    '> log 2>&1; echo "REAL EXIT: $?"` still exits with the LAST statement\'s '
    "code, so a harness that reports only the aggregate still announces success "
    "over a red suite. The gate can require the status be surfaced; it cannot "
    "make a summary line report it. This is why the clause's last word is to "
    "cite the ARB receipt's `exit_status` — the receipt is the only channel that "
    "carries the verifier's own result out of the shell.",
    "A `||` branch whose LEFT SIDE runs no recognized verifier (GHI #970). "
    "`test -f x && echo DEFECT || echo OK` exits non-zero when the assertion "
    "HOLDS, so its status is a verdict rather than a suppressed failure, and this "
    "gate does not widen past its canonical scope to read it. A generic command "
    "silenced by `||` is therefore unseen, exactly as a generic command piped "
    "without `pipefail` is.",
    "A verifier inside command substitution — `$( … )` or backticks — or behind a "
    "reserved word (`time`, `!`, an `if`/`while` condition, a `then`/`do`/`else` "
    "body) is not recognized: resolution is by command head, and the head is the "
    "reserved word, or the substitution sits inside a word. Groups `( … )` and "
    "`{ …; }` ARE read (GHI #1008). Tracked at GHI #1012.",
    "A heredoc body is read as shell statements, though it is data the shell never "
    "runs: body prose can be refused, and an apostrophe in it leaves the command "
    "unparseable, so a masked verifier after it is admitted. Tracked at GHI #1013.",
    "A quoted lone `(` or `)` lexes exactly like an operator, so a command whose "
    "parens do not balance — that, or a `case` pattern — keeps the ungrouped "
    "reading this gate gave before groups were read (GHI #1008).",
)

#: Characters the shared lexer emits as punctuation (``shlex`` ``punctuation_chars``).
_PUNCTUATION: frozenset[str] = frozenset("();<>|&")

#: A grouping opener in command position, mapped to the token that closes it.
_GROUP_CLOSERS: dict[str, str] = {"(": ")", "{": "}"}

_SUBSHELL_OPENER = "("
_SUBSHELL_CLOSER = ")"


class _Group(BaseModel):
    """A ``( … )`` subshell or ``{ …; }`` brace group: ONE command of its list (GHI #1008).

    The shell reports a group's status as its last statement's, exactly as it
    reports a command's, so the group is read as a command whose verifier is
    whichever one its own list carries to that end.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    subshell: bool = Field(..., description="True for `( … )`, whose shell state stays inside")
    body: tuple[str | _Group, ...] = Field(..., description="The group's own list, groups nested")


class _ListReading(BaseModel):
    """What one statement list does to a verifier's status (GHI #1008)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    masked: tuple[str, str] | None = Field(None, description="(verifier, arm) whose status is lost")
    carried: str | None = Field(None, description="Verifier whose failure the list reports")
    backgrounded: str | None = Field(
        None, description="Verifier the list's last command launched in the background"
    )
    pipefail: bool = Field(..., description="pipefail state after the list ran")
    errexit: bool = Field(..., description="errexit state after the list ran")


def _canonical_program_names() -> frozenset[str]:
    """Resolve the verifier program of every runnable canonical ARB step command.

    Reads ``CANONICAL_STEP_COMMANDS`` rather than restating its contents so a step
    added to the ARB registry is covered here without a second edit. Reserved
    slots (declared name, empty command — ``security``, ``meta-receipt-bind``)
    contribute nothing, which is correct: there is no invocation to mask yet.
    """
    names: set[str] = set()
    for argv in CANONICAL_STEP_COMMANDS.values():
        if not argv:
            continue
        tokens = strip_uv_run(argv)
        if not tokens:
            continue
        head = tokens[0]
        if head == "-m":
            if len(tokens) > 1:
                names.add(tokens[1])
            continue
        program = program_name(head)
        if program in _PYTHON_RUNNERS and tokens[1:2] == ["-m"] and len(tokens) > 2:
            names.add(tokens[2])
            continue
        names.add(program)
    return frozenset(names)


#: Every program whose exit status the clause protects.
VERIFIER_PROGRAMS: frozenset[str] = _canonical_program_names() | _DECLARED_BEYOND_ARB


class Verdict(BaseModel):
    """Gate decision for one tool call. ``blocked`` is the whole contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    blocked: bool = Field(..., description="True when the tool call must be refused")
    reason: str = Field(default="", description="Three-part guardrail prose; empty when allowed")


def _strip_env_assignments(tokens: list[str]) -> list[str]:
    """Drop leading ``VAR=value`` prefixes so the real command head is reachable."""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.startswith("-") or "=" not in token:
            break
        index += 1
    return tokens[index:]


def _sets_pipefail(statement: list[str]) -> bool:
    """Return True when this statement is a ``set`` builtin enabling ``pipefail``.

    Head-resolved on purpose (GHI #796). ``grep -rn "pipefail" docs/`` and
    ``set -o pipefail`` are indistinguishable by token presence — posix
    tokenization strips the quotes, so both leave a bare ``pipefail`` operand —
    and only one of them changes how the shell reports a pipeline.
    """
    tokens = _strip_env_assignments(statement)
    return bool(tokens) and tokens[0] == _SET_BUILTIN and _PIPEFAIL_OPERAND in tokens[1:]


def _reads_pipestatus(statement: list[str]) -> bool:
    """Return True when a token READS the ``PIPESTATUS`` array.

    A reference (``${PIPESTATUS[0]}``, ``$PIPESTATUS``) retrieves the upstream
    status; a bare word that merely contains the name — a path, a flag value —
    retrieves nothing.
    """
    return any(ref in token for token in statement for ref in _PIPESTATUS_REFERENCES)


def _sets_errexit(statement: list[str]) -> bool:
    """Return True when this statement is a ``set`` builtin enabling ``errexit``.

    Head-resolved exactly as :func:`_sets_pipefail` is (GHI #796): ``grep -rn
    "set -e" docs/`` names the escape and enables nothing. Accepts both the
    short-flag bundle (``-e``, ``-euo``) and the long form (``-o errexit``).
    """
    tokens = _strip_env_assignments(statement)
    if not tokens or tokens[0] != _SET_BUILTIN:
        return False
    for token in tokens[1:]:
        if token == _ERREXIT_LONG_OPERAND:
            return True
        if token.startswith("-") and not token.startswith("--") and "e" in token[1:]:
            return True
    return False


def _reads_exit_status(statement: list[str]) -> bool:
    """Return True when a token READS ``$?``."""
    return any(ref in token for token in statement for ref in _EXIT_STATUS_REFERENCES)


def _statement_terminators(items: list[str | _Group]) -> list[str | None]:
    """Separator ending each statement, aligned 1:1 with :func:`split_on`'s output.

    ``split_on`` emits one segment per separator plus a final one, so the
    terminator list is the separators in order with ``None`` appended. The
    separator matters because ``&&`` propagates a failure and ``;`` discards it —
    a splitter that forgets which one was used cannot tell those apart.
    """
    return [*(token for token in _plain(items) if token in _STATEMENT_SEPARATORS), None]


def _module_verifier(rest: list[str]) -> str | None:
    """Return the verifier named by a ``-m <module>`` invocation, if any."""
    if not rest:
        return None
    module = rest[0]
    return module if module in VERIFIER_PROGRAMS else None


def _gz_verifier(rest: list[str]) -> str | None:
    """Return ``gz <verb>`` when the first non-flag token runs a verification tier."""
    for token in rest:
        if token.startswith("-"):
            continue
        return f"gz {token}" if token in GZ_VERIFIER_VERBS else None
    return None


def _verifier_name(segment: list[str]) -> str | None:
    """Return the verifier this pipeline segment RUNS, or None.

    Resolution is by command head — never by token presence. That distinction is
    the whole difference between a gate and a substring search: ``grep -rn
    "unittest" src/`` contains the token and runs no verifier.
    """
    tokens = _strip_env_assignments(strip_uv_run(segment))
    if not tokens:
        return None
    head = tokens[0]
    # `uv run -m unittest -q` leaves `-m` as the head once `uv run` is stripped.
    if head == "-m":
        return _module_verifier(tokens[1:])
    program = program_name(head)
    if program in _PYTHON_RUNNERS:
        rest = tokens[1:]
        # `python script.py` is not a named verifier; only the `-m` form is.
        return _module_verifier(rest[1:]) if rest[:1] == ["-m"] else None
    if program == "gz":
        return _gz_verifier(tokens[1:])
    return program if program in VERIFIER_PROGRAMS else None


def masked_verifier(command: str) -> str | None:
    """Return the verifier whose exit status this command discards, or None.

    The name-only facade over :func:`masked_verifier_reason`, kept because most
    callers only need to know THAT a verifier was silenced.

    A verifier is masked when it runs in any pipeline stage other than the last:
    the shell reports only the final process's status, so every upstream exit is
    thrown away. Returns the verifier's display name so the block prose can name
    what was actually silenced rather than echoing the whole command.

    Both escapes are honored only where they are USED, and ORDER is part of
    that (GHI #796). ``pipefail`` is shell state, so it protects the pipelines
    that FOLLOW the ``set``, never one that already ran; ``PIPESTATUS`` is read
    back after the pipeline it describes. The predicate was previously a
    substring scan over every token in the command, which let any mention of
    either name — a ``grep`` pattern, a filename — disarm the gate wholesale.
    """
    reason = masked_verifier_reason(command)
    return reason[0] if reason else None


def _is_paren_run(token: str) -> bool:
    return set(token) <= _PUNCTUATION and ("(" in token or ")" in token)


def _split_paren_runs(tokens: list[str]) -> list[str]:
    """Split a merged punctuation token at its parens (GHI #1008).

    ``shlex`` joins ADJACENT punctuation into one token, so ``(x);ls`` lexes as
    ``);`` and ``ls;(x)`` as ``;(`` — the separator hides inside the token that
    closes or opens the group. Only runs carrying a paren are split, so a
    paren-free command lexes exactly as it did.

    A ``(`` straight after a plain word is not shell syntax this gate reads —
    it is prose in a heredoc body, a quoted lone paren, or a function name — so
    the run that CLOSES it keeps its lexing. Splitting there turned heredoc prose
    like ``clean (receipt); mkdocs --strict clean`` into a refused command.
    """
    split: list[str] = []
    opened_after_word: list[bool] = []
    previous: str | None = None
    for token in tokens:
        if not _is_paren_run(token):
            split.append(token)
            previous = token
            continue
        parts = [part for part in re.split(r"([()])", token) if part]
        closes_prose = False
        for part in parts:
            if part == _SUBSHELL_OPENER:
                # `$(`, `a=(`, `{ (` and an operator-led `(` are shell syntax; a
                # word-led one is not.
                opened_after_word.append(
                    previous is not None
                    and previous not in _GROUP_CLOSERS
                    and not set(previous) <= _PUNCTUATION
                    and not previous.endswith(("$", "="))
                )
            elif part == _SUBSHELL_CLOSER and opened_after_word:
                closes_prose = opened_after_word.pop() or closes_prose
            previous = part
        split.extend([token] if closes_prose and len(parts) > 1 else parts)
        previous = token
    return split


def _read_groups(tokens: list[str]) -> list[str | _Group] | None:
    """Nest every command-position ``( … )`` and ``{ …; }``; None when they do not balance.

    A paren outside command position — ``$(``, ``<(``, ``a=(``, ``f()`` — opens no
    group. It stays a plain token but is still balanced, so its ``)`` closes
    nothing. ``}`` closes a brace group only in command position, which is the
    only place the shell reads it as a closer.
    """
    # (opener, items, is_group). A non-group paren shares its parent's items.
    frames: list[tuple[str | None, list[str | _Group], bool]] = [(None, [], False)]
    at_head = True
    for token in tokens:
        opener, items, is_group = frames[-1]
        if at_head and token in _GROUP_CLOSERS:
            frames.append((token, [], True))
            continue
        if token != _SUBSHELL_CLOSER and token.startswith(_SUBSHELL_CLOSER) and not is_group:
            # An unsplit closing run (see `_split_paren_runs`) still closes its paren.
            if opener is None:
                return None
            frames.pop()
            items.append(token)
            at_head = False
            continue
        if token == _SUBSHELL_CLOSER or (at_head and token in _GROUP_CLOSERS.values()):
            if opener is None or token != _GROUP_CLOSERS[opener]:
                return None
            frames.pop()
            if is_group:
                frames[-1][1].append(_Group(subshell=opener == _SUBSHELL_OPENER, body=tuple(items)))
            else:
                items.append(token)
            at_head = False
            continue
        if token == _SUBSHELL_OPENER:
            frames.append((token, items, False))
        items.append(token)
        at_head = token in _STATEMENT_SEPARATORS or token == _PIPE
    return frames[0][1] if len(frames) == 1 else None


def _plain(items: list[str | _Group]) -> list[str]:
    """Return the items' own tokens; nothing inside a nested group is the caller's."""
    return [item for item in items if isinstance(item, str)]


def _words_run_first(statement: list[str | _Group]) -> list[str]:
    """Tokens of what runs FIRST: a statement headed by a group runs its first statement."""
    while statement and isinstance(statement[0], _Group):
        statement = split_on(list(statement[0].body), _STATEMENT_SEPARATORS)[0]
    return _plain(statement)


def _all_words(items: list[str | _Group]) -> list[str]:
    """Every token, nested groups included."""
    words: list[str] = []
    for item in items:
        words.extend(_all_words(list(item.body)) if isinstance(item, _Group) else [item])
    return words


def _pipe_arm(
    names: list[str | None], rest: list[list[str | _Group]], *, pipefail_active: bool
) -> str | None:
    """ARM 1 — the pipe. A verifier upstream of any pipe loses its status to the last stage.

    ``names`` holds the verifier each stage runs, resolved by the caller so a
    grouped stage names the verifier its group carries (GHI #1008).
    """
    if pipefail_active or len(names) < 2:
        return None
    if any(_reads_pipestatus(_all_words(later)) for later in rest):
        return None
    return next((name for name in names[:-1] if name is not None), None)


def _status_carrier(names: list[str | None], *, pipefail_active: bool) -> str | None:
    """Return the verifier whose status this statement REPORTS, or None.

    Without ``pipefail`` a pipeline reports its last stage. With it, a failing
    verifier in ANY stage becomes the pipeline's status, so a later statement
    that overwrites the pipeline overwrites the verifier (GHI #971).
    """
    candidates = names if pipefail_active else names[-1:]
    return next((name for name in candidates if name is not None), None)


def _replacement_arm(
    names: list[str | None],
    rest: list[list[str | _Group]],
    terminators: list[str | None],
    *,
    pipefail_active: bool,
    errexit_active: bool,
    errexit_reaches: bool,
) -> tuple[str, str] | None:
    """ARMS 2 to 6 — a later statement REPLACES the verifier's status.

    The shell reports the last statement exactly as it reports the last stage
    (GHI #940), and a ``||`` branch reports the branch (GHI #970). ``pipefail``
    reaches neither: it fixes which status a PIPELINE reports, not whether
    something afterwards overwrites it.

    ``terminators`` starts at the verifier's own terminator. The separator that
    decides is the one ENDING the verifier's AND-OR list: ``&&`` carries the
    failure onward, so ``verifier && ok; ls`` is masked by the ``;`` (GHI #971).

    Returns ``(verifier, "carried")`` when the verifier's failure reaches the end
    of this list as the list's own status — what a GROUP around the list then
    reports (GHI #1008). ``errexit_reaches`` is False inside a group that is not
    last in its AND-OR list, where the shell suppresses errexit for every command.
    """
    name = _status_carrier(names, pipefail_active=pipefail_active)
    if name is None:
        return None
    end = 0
    while terminators[end] == _AND_THEN:
        end += 1
    list_end = terminators[end]
    if list_end not in _MASKING_SEPARATORS:
        return name, "carried"
    chained = end > 0
    protected = not chained and list_end in _ERREXIT_PROTECTED_SEPARATORS
    # POSIX suppresses errexit for a command that is not the last in an AND-OR
    # list, so `set -e` cannot abort on a verifier inside a chain.
    if errexit_active and errexit_reaches and protected:
        return name, "carried"
    later = [statement for statement in rest[end:] if statement]
    if not later:
        # A trailing separator (`gz check;`) leaves an empty tail. Nothing runs
        # after the verifier, so nothing overwrites its status — unless it was
        # backgrounded, which reports the launch to whatever follows the list.
        return name, ("backgrounded" if list_end == _BACKGROUND else "carried")
    # `$?` reads the status of the list that JUST ran. A read placed after an
    # intervening statement reports that statement's exit instead — it looks like
    # evidence and is not, so only the next statement counts. After `&` it reads
    # the background launch, never the verifier.
    if list_end != _BACKGROUND and _reads_exit_status(_words_run_first(later[0])):
        return None
    if list_end == _BACKGROUND:
        return name, "background"
    if chained:
        return name, "chain"
    if list_end == _OR_ELSE:
        return name, "or-else"
    return name, ("sequence" if errexit_reaches else "errexit-suppressed")


def _read_stages(
    stages: list[list[str | _Group]],
    *,
    pipefail_active: bool,
    errexit_active: bool,
    errexit_reaches: bool,
) -> list[str | _ListReading | None]:
    """Resolve each stage: the verifier it runs by name, or a grouped stage's reading."""
    resolved: list[str | _ListReading | None] = []
    for stage in stages:
        head = stage[0] if stage else None
        if not isinstance(head, _Group):
            resolved.append(_verifier_name(_plain(stage)))
            continue
        resolved.append(
            _read_list(
                list(head.body),
                pipefail_active=pipefail_active,
                errexit_active=errexit_active,
                errexit_reaches=errexit_reaches,
            )
        )
    return resolved


def _leaves_state_behind(stages: list[list[str | _Group]], terminator: str | None) -> bool:
    """Return True when the statement is a brace group running in THIS shell.

    What a brace group sets outlives it; a subshell, a pipeline stage or a
    background job runs elsewhere and does not (measured: `{ set -e; }; false; ls`
    exits 1, `{ set -e; } | cat; false; ls` exits 0).
    """
    head = stages[0][0] if stages[0] else None
    return (
        isinstance(head, _Group)
        and not head.subshell
        and len(stages) == 1
        and terminator != _BACKGROUND
    )


def _read_statement(
    statement: list[str | _Group],
    rest: list[list[str | _Group]],
    terminators: list[str | None],
    *,
    pipefail_active: bool,
    errexit_active: bool,
    errexit_reaches: bool,
) -> _ListReading:
    """Read one statement that sets no shell option; ``terminators`` starts at its own."""
    stages = split_on(statement, frozenset({_PIPE}))
    # errexit is suppressed for every command inside a group that is not last in
    # its AND-OR list — measured: `set -e; (false; ls) || echo x` exits 0.
    resolved = _read_stages(
        stages,
        pipefail_active=pipefail_active,
        errexit_active=errexit_active,
        errexit_reaches=errexit_reaches and terminators[0] not in (_AND_THEN, _OR_ELSE),
    )
    readings = [stage for stage in resolved if isinstance(stage, _ListReading)]
    masked_inside = next((reading for reading in readings if reading.masked is not None), None)
    if masked_inside is not None:
        return masked_inside
    if _leaves_state_behind(stages, terminators[0]):
        pipefail_active, errexit_active = readings[0].pipefail, readings[0].errexit
    # A group that ended by backgrounding a verifier reports the launch, so ANY
    # later statement replaces a status no read can recover (`(false &); echo "$?"`
    # prints 0).
    launched = next((reading.backgrounded for reading in readings if reading.backgrounded), None)
    if launched is not None and any(rest):
        return _ListReading(
            masked=(launched, "background"), pipefail=pipefail_active, errexit=errexit_active
        )
    names = [stage.carried if isinstance(stage, _ListReading) else stage for stage in resolved]

    name = _pipe_arm(names, rest, pipefail_active=pipefail_active)
    found = (
        (name, "pipe")
        if name is not None
        else _replacement_arm(
            names,
            rest,
            terminators,
            pipefail_active=pipefail_active,
            errexit_active=errexit_active,
            errexit_reaches=errexit_reaches,
        )
    )
    return _statement_reading(
        found, launched, pipefail_active=pipefail_active, errexit_active=errexit_active
    )


def _statement_reading(
    found: tuple[str, str] | None,
    launched: str | None,
    *,
    pipefail_active: bool,
    errexit_active: bool,
) -> _ListReading:
    """Sort an arm's outcome into a masking, a carried status, or a background launch."""
    name, outcome = found if found is not None else (None, None)
    return _ListReading(
        masked=found if outcome not in (None, "carried", "backgrounded") else None,
        carried=name if outcome == "carried" else None,
        backgrounded=name if outcome == "backgrounded" else launched,
        pipefail=pipefail_active,
        errexit=errexit_active,
    )


def _read_list(
    items: list[str | _Group], *, pipefail_active: bool, errexit_active: bool, errexit_reaches: bool
) -> _ListReading:
    """Read one statement list — the whole command, or a group's body (GHI #1008)."""
    statements = split_on(items, _STATEMENT_SEPARATORS)
    terminators = _statement_terminators(items)
    carried: str | None = None
    backgrounded: str | None = None
    for index, statement in enumerate(statements):
        plain = [] if statement and isinstance(statement[0], _Group) else _plain(statement)
        if _sets_pipefail(plain) or _sets_errexit(plain):
            pipefail_active = pipefail_active or _sets_pipefail(plain)
            errexit_active = errexit_active or _sets_errexit(plain)
            continue
        reading = _read_statement(
            statement,
            statements[index + 1 :],
            terminators[index:],
            pipefail_active=pipefail_active,
            errexit_active=errexit_active,
            errexit_reaches=errexit_reaches,
        )
        if reading.masked is not None:
            return reading
        pipefail_active, errexit_active = reading.pipefail, reading.errexit
        carried = carried or reading.carried
        backgrounded = backgrounded or reading.backgrounded
    return _ListReading(
        carried=carried,
        backgrounded=backgrounded,
        pipefail=pipefail_active,
        errexit=errexit_active,
    )


def masked_verifier_reason(command: str) -> tuple[str, str] | None:
    """Return ``(verifier, arm)`` for a masked verifier, or None.

    ``arm`` is ``"pipe"``, ``"sequence"``, ``"or-else"``, ``"chain"``,
    ``"background"`` or ``"errexit-suppressed"``. The caller needs it because they
    have DIFFERENT remedies: ``pipefail`` makes a pipeline report its first failing
    stage and does nothing for a later statement overwriting the status; ``set -e``
    aborts the sequence and does nothing about a pipe; and NEITHER reaches ``||``,
    a non-final ``&&`` member, ``&``, or a sequence inside a group that is not last
    in its AND-OR list, where the shell suppresses or cannot apply errexit. Prose
    that named one remedy for all would hand the caller a correction that leaves
    the command exactly as masked as it was
    (`.claude/rules/guardrail-feedback-prose.md`).
    """
    # Unquoted newlines become `;` first: shlex eats a newline as whitespace, so
    # a multi-line command would otherwise read as ONE statement — and the
    # harness background surface that GHI #940 was observed on sends exactly that.
    tokens = tokenize_shell(normalize_statement_newlines(command))
    if tokens is None:
        # Unbalanced quotes. The shell will reject this too; a gate that guesses
        # at unparseable input refuses commands nobody could have run anyway.
        return None
    # Groups read as one command each (GHI #1008). Parens that do not balance keep
    # the reading of the unsplit tokens, exactly as before groups were read: that
    # fallback is where heredoc prose lands, and re-lexing it changes verdicts on
    # text the shell never runs.
    items: list[str | _Group] = _read_groups(_split_paren_runs(tokens)) or list(tokens)
    return _read_list(
        items, pipefail_active=False, errexit_active=False, errexit_reaches=True
    ).masked


def _block_prose(verifier: str, command: str, arm: str = "pipe") -> str:
    """Three-part guardrail prose: what failed, why forbidden, governed next step.

    Per `.claude/rules/guardrail-feedback-prose.md` — the feedback IS the prompt
    the operator would otherwise have typed, so it hands back the caller's OWN
    command corrected, never a shape to translate.

    **Both permitted routes preserve the status; the ORDER is what gets acted on.**
    This prose used to lead its ``NEXT STEP`` with the two-call file capture and
    demote ``pipefail`` to a clause behind *"if you genuinely need the pipe"* —
    phrasing that reads as a carve-out for an unusual need when wanting a tail of
    the output is the normal case. Observed cost: an agent took the two-call route
    eleven times in one session while the one-call escape sat unread in the same
    message. Nothing is relaxed here — ``masked_verifier`` refuses exactly what it
    refused before, and the file-capture route survives as the alternative it
    always was.

    ``command`` is prepended-to whole rather than rewritten per statement: what the
    caller re-runs is the whole line, and ``pipefail`` is shell state that protects
    every pipeline following the ``set``.
    """
    if arm == "or-else":
        return (
            f"BLOCKED: Bash refused — `{verifier}` is followed by a `||` branch, so "
            "the exit status you would read back is the BRANCH's. The branch runs "
            f"only when `{verifier}` fails, which means this command reports 0 "
            "exactly when there is a failure to report.\n\n"
            "WHY: `.gzkit/rules/tests.md` § Verification exit-code integrity "
            "(binding, GHI #589, extended GHI #970) — a `||` branch ANNOUNCES the "
            "failure in output and REPLACES it in status, and those are different "
            "claims. Anything reading the status rather than the transcript — a "
            "harness notification, a Step-4a packet replay — sees green; and a "
            "packet is a curated excerpt, so the announcement can simply not be "
            "pasted.\n\n"
            "NEXT STEP: keep the `||` and have its branch report the real status. "
            "No prefix corrects this arm, so the fix is a one-token substitution "
            "inside the branch you already wrote:\n"
            '  <your command> || echo "REAL EXIT: $?"\n\n'
            "`set -e` does NOT help here — the shell suppresses errexit for a "
            "command on the left of `||`, so it aborts nothing (`sh -c 'set -e; "
            "false || echo caught'` exits 0). For attestation evidence, cite the "
            "ARB receipt's `exit_status` (`uv run gz arb step ...`), never an "
            "aggregate status."
        )
    if arm == "chain":
        return (
            f"BLOCKED: Bash refused — `{verifier}` sits in an `&&` chain that a "
            "later `;`, newline or `||` catches, so the exit status you would read "
            f"back is a later statement's, not `{verifier}`'s.\n\n"
            "WHY: `.gzkit/rules/tests.md` § Verification exit-code integrity "
            "(binding, GHI #589, extended GHI #971) — `&&` carries a failure to the "
            "END of its chain, and whatever runs after that end replaces it: "
            "`verifier && ok; ls` and `verifier && ok || echo x` both exit 0 over a "
            "failed verifier.\n\n"
            "NEXT STEP: read `$?` in the statement immediately after the chain. When "
            f"`{verifier}` fails the chain stops there, so `$?` is its status:\n"
            '  <your chain>; echo "REAL EXIT: $?"\n'
            '  <your chain> || echo "REAL EXIT: $?"\n\n'
            "`set -e` does NOT help here — the shell suppresses errexit for a "
            "command that is not the last in an `&&` chain (`sh -c 'set -e; false "
            "&& echo ok; ls'` exits 0), and `pipefail` fixes only a pipeline. For "
            "attestation evidence, cite the ARB receipt's `exit_status` "
            "(`uv run gz arb step ...`), never an aggregate status."
        )
    if arm == "background":
        return (
            f"BLOCKED: Bash refused — `{verifier}` runs in the background (`&`), so "
            "the command reports the status of what runs next, and a `$?` read "
            "after `&` reports the background launch — 0 — not the verifier.\n\n"
            "WHY: `.gzkit/rules/tests.md` § Verification exit-code integrity "
            '(binding, GHI #589, extended GHI #971) — `false & echo "REAL EXIT: '
            '$?"` prints `REAL EXIT: 0`, so the status line looks like evidence '
            "and reports success over a failed verifier.\n\n"
            f"NEXT STEP: run `{verifier}` in the foreground and read its status "
            "immediately:\n"
            '  <verifier> > out.log 2>&1; echo "REAL EXIT: $?"\n\n'
            "`set -e` does NOT help here — errexit cannot abort on a background "
            "job (`sh -c 'set -e; false & ls'` exits 0). For attestation evidence, "
            "cite the ARB receipt's `exit_status` (`uv run gz arb step ...`), never "
            "an aggregate status."
        )
    if arm == "errexit-suppressed":
        return (
            f"BLOCKED: Bash refused — `{verifier}` is not the last statement of a "
            "`( … )` or `{ …; }` group that sits in an `&&`/`||` list, so the "
            f"status the group reports is a later statement's, not `{verifier}`'s.\n\n"
            "WHY: `.gzkit/rules/tests.md` § Verification exit-code integrity "
            "(binding, GHI #589, extended GHI #1008) — a group reports its last "
            "statement exactly as a command does, and the shell suppresses errexit "
            "for every command inside a group that is not last in its AND-OR list "
            "(`sh -c 'set -e; (false; ls) || echo x'` exits 0).\n\n"
            "NEXT STEP: read `$?` inside the group, immediately after the verifier:\n"
            '  ( <verifier> > out.log 2>&1; echo "REAL EXIT: $?"; <rest> )\n\n'
            "`set -e` does NOT help here — errexit never fires inside that group, so "
            "prefixing it changes nothing. For attestation evidence, cite the ARB "
            "receipt's `exit_status` (`uv run gz arb step ...`), never an aggregate "
            "status."
        )
    if arm == "sequence":
        return (
            f"BLOCKED: Bash refused — `{verifier}` is not the last statement, so "
            "the exit status you would read back is the final statement's, not "
            f"`{verifier}`'s.\n\n"
            "WHY: `.gzkit/rules/tests.md` § Verification exit-code integrity "
            "(binding, GHI #589, extended GHI #940) — the shell reports the LAST "
            "statement's exit, so `verifier > log; tail log` discards the "
            "verifier's status exactly as a pipe would. On a backgrounded run the "
            "aggregate status is the ONLY signal reported, and that false green is "
            "what then gets relayed as attestation evidence.\n\n"
            "NEXT STEP: re-run with errexit, which aborts the sequence the moment "
            f"`{verifier}` fails so its status survives as the command's. This is "
            "your command, corrected — paste it:\n"
            f"  set -e; {command}\n\n"
            "Or read the status immediately after the verifier, before anything "
            "else runs:\n"
            '  <verifier> > out.log 2>&1; echo "REAL EXIT: $?"\n\n'
            "`pipefail` does NOT help here — it fixes which status a PIPELINE "
            "reports, not a later statement overwriting it. For attestation "
            "evidence, cite the ARB receipt's `exit_status` "
            "(`uv run gz arb step ...`), never an aggregate status."
        )
    return (
        f"BLOCKED: Bash refused — this command pipes `{verifier}` into another "
        "process, so the exit status you would read back is the last stage's, not "
        f"`{verifier}`'s.\n\n"
        "WHY: `.gzkit/rules/tests.md` § Verification exit-code integrity (binding, "
        "GHI #589) — 'A verifier's truth is its own exit code, never a downstream "
        "filter's. ... the shell reports the last process's exit (the filter's — "
        "always 0), masking a failing suite as a green run.' A harness 'exit code 0' "
        "on a piped verifier attests the filter, not the verifier, and that false "
        "green is what then gets relayed as attestation evidence.\n\n"
        "NEXT STEP: re-run with pipefail, which keeps the pipe AND reports "
        f"`{verifier}`'s own status. This is your command, corrected — paste it:\n"
        f"  set -o pipefail; {command}\n\n"
        "Or capture to a file if you would rather inspect the output separately:\n"
        '  <your command> > out.log 2>&1; echo "REAL EXIT: $?"\n\n'
        "Reading `${PIPESTATUS[0]}` after the pipeline is equally permitted. For "
        "attestation evidence, cite the ARB receipt's `exit_status` "
        "(`uv run gz arb step ...`), never a piped run."
    )


def decide(tool_name: str, tool_input: dict | None = None) -> Verdict:
    """Decide whether a tool call masks a verifier's exit status.

    Scoped to Bash: a verifier reaches the harness no other way, and the clause
    governs shell pipelines specifically.
    """
    if tool_name != "Bash":
        return Verdict(blocked=False)
    command = str((tool_input or {}).get("command", ""))
    reason = masked_verifier_reason(command)
    if reason is None:
        return Verdict(blocked=False)
    verifier, arm = reason
    return Verdict(blocked=True, reason=_block_prose(verifier, command, arm))


# ---------------------------------------------------------------------------
# Live negative control — the floor's teeth for this gate (ADR-0.0.74 §5)
#
# ONE claim, because the clause declares one rule. The control asserts the
# DIFFERENTIAL (refuse piped AND permit unpiped) rather than the refusal alone:
# an always-block implementation is not a working gate, and a refusal-only
# control cannot tell the two apart.
# ---------------------------------------------------------------------------

VERIFIER_PIPE_CLAIM_ID = "verifier-exit-status-masked"

#: The gate's OTHER half (GHI #797). ``verifier-exit-status-masked`` proves the
#: rule fires; this proves the ESCAPE admits only a used escape. The distinction
#: is not academic — the rule claim was registered, enrolled, and passing on
#: every ``gz check`` for the entire life of GHI #796's bypass, because it never
#: touched the exemption. A gate with an exemption makes two claims, and only
#: one of them was ever controlled.
VERIFIER_ESCAPE_CLAIM_ID = "verifier-escape-must-be-used"

VERIFIER_PIPE_CLAIM_IDS: frozenset[str] = frozenset(
    {VERIFIER_PIPE_CLAIM_ID, VERIFIER_ESCAPE_CLAIM_ID}
)


def _build_masked_verifier_violation() -> Path:
    """Return a temp root whose NAME seeds a runtime-unique command string.

    The random token is unknowable at mutation-authoring time, so a broken
    :func:`masked_verifier` cannot special-case a fixed sentinel to sneak past
    the control (the Step-4b facade attack — a FIXED string proves only that the
    gate refuses THAT string, never the general rule). The root is allocated
    inside the active runner-owned workspace.
    """
    from gzkit.enforcement import create_fixture_tempdir  # noqa: PLC0415

    return create_fixture_tempdir(prefix="gzkit-verifier-pipe-nc-")


def _ep_verifier_pipe_gate(root: Path) -> int:
    """Assert the DIFFERENTIAL: refuse the piped form, permit the unpiped one.

    Truthy only when BOTH poles hold, which proves the verdict tracks *masking*
    rather than any fixed answer. An always-block mutation fails the permit pole;
    an always-allow mutation fails the refuse pole. The verdict is COMPUTED by
    production :func:`decide` with no forcing kwarg pre-bound
    (§ Boundary Invariants #7).
    """
    piped = {"command": f"uv run -m unittest -q --nc-{root.name} | tail -5"}
    unpiped = {"command": f"uv run -m unittest -q --nc-{root.name} > out-{root.name}.log 2>&1"}
    refused = decide("Bash", piped).blocked
    permitted = not decide("Bash", unpiped).blocked
    return 1 if (refused and permitted) else 0


def _ep_verifier_escape_must_be_used(root: Path) -> int:
    """Assert the EXEMPTION differential: refuse a NAMED escape, permit a USED one.

    The second half of this gate's contract (GHI #797). ``_ep_verifier_pipe_gate``
    proves the rule fires on a piped verifier; nothing proved the escape admits
    only an escape that was actually used, and that is the half that broke.

    Both poles are required, for the same reason the rule control needs both: an
    always-refuse mutation would make the gate un-compliable for the one correct
    way to pipe a verifier, and an always-permit mutation is the bypass itself.
    The mention-only command carries a runtime-unique token so a broken predicate
    cannot special-case a fixed sentinel.
    """
    named = {"command": f'grep -rn "pipefail" docs-{root.name}/ ; uv run gz check | tail -5'}
    used = {"command": f"set -o pipefail; uv run gz check --nc-{root.name} | tail -5"}
    refused = decide("Bash", named).blocked
    permitted = not decide("Bash", used).blocked
    return 1 if (refused and permitted) else 0


def _verifier_pipe_marker() -> None:
    """Inert carrier for the verifier-pipe ``@enforces`` registration."""


def _ensure_verifier_pipe_claims_registered() -> None:
    """(Re)register the verifier-pipe enforcement claim (idempotent, reset-safe).

    MUST stay wired into ``_ensure_production_claims_registered`` — a
    registration authored but un-wired there is an ORPHAN whose floor membership
    is a facade (the §5 failure class these NCs exist to prevent).
    """
    from gzkit.airlock.enter import _AIRLOCK_CLAIM_IDS  # noqa: PLC0415
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        enforces,
        get_enforcement_registry,
        set_known_claims,
    )
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )
    from gzkit.handoff_resume_gate import RESUME_GATE_CLAIM_IDS  # noqa: PLC0415

    set_known_claims(
        _KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS | RESUME_GATE_CLAIM_IDS | VERIFIER_PIPE_CLAIM_IDS
    )
    existing = {r.claim_id for r in get_enforcement_registry()}
    if VERIFIER_PIPE_CLAIM_ID not in existing:
        enforces(
            VERIFIER_PIPE_CLAIM_ID,
            _build_masked_verifier_violation,
            _ep_verifier_pipe_gate,
            exempts=VERIFIER_ESCAPE_CLAIM_ID,
        )(_verifier_pipe_marker)
    if VERIFIER_ESCAPE_CLAIM_ID not in existing:
        enforces(
            VERIFIER_ESCAPE_CLAIM_ID,
            _build_masked_verifier_violation,
            _ep_verifier_escape_must_be_used,
            exempts=EXEMPTS_NONE,
        )(_verifier_pipe_marker)
