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
#: statement's (GHI #940). ``&&`` and ``||`` are deliberately absent: ``&&``
#: short-circuits, so a failing verifier aborts the sequence and its status IS
#: the aggregate, and ``||`` runs its right side only ON failure, which is the
#: verdict idiom GHI #942 preserved one surface over rather than a concealment.
_MASKING_SEPARATORS: frozenset[str] = frozenset({";", "\n", "&"})

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
_DECLARED_BEYOND_ARB: frozenset[str] = frozenset({"behave", "ruff", "pytest", "unittest"})

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
    "`||` right-hand sides are permitted: `verifier || echo failed` reports 0 on "
    "failure, but the branch runs ONLY on failure and announces it, which is the "
    "verdict idiom preserved one surface over (GHI #942). A `||` branch that "
    "announces nothing is masking this gate does not refuse.",
)


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


def _statement_terminators(tokens: list[str]) -> list[str | None]:
    """Separator ending each statement, aligned 1:1 with :func:`split_on`'s output.

    ``split_on`` emits one segment per separator plus a final one, so the
    terminator list is the separators in order with ``None`` appended. The
    separator matters because ``&&`` propagates a failure and ``;`` discards it —
    a splitter that forgets which one was used cannot tell those apart.
    """
    return [*(token for token in tokens if token in _STATEMENT_SEPARATORS), None]


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


def masked_verifier_reason(command: str) -> tuple[str, str] | None:
    """Return ``(verifier, arm)`` for a masked verifier, or None.

    ``arm`` is ``"pipe"`` or ``"sequence"``. The caller needs it because the two
    have DIFFERENT remedies: ``pipefail`` makes a pipeline report its first
    failing stage and does nothing for a later statement overwriting the status,
    while ``set -e`` aborts the sequence and does nothing about a pipe. Prose that
    named one remedy for both would hand the caller a correction that leaves the
    command exactly as masked as it was (`.claude/rules/guardrail-feedback-prose.md`).
    """
    # Unquoted newlines become `;` first: shlex eats a newline as whitespace, so
    # a multi-line command would otherwise read as ONE statement — and the
    # harness background surface that GHI #940 was observed on sends exactly that.
    tokens = tokenize_shell(normalize_statement_newlines(command))
    if tokens is None:
        # Unbalanced quotes. The shell will reject this too; a gate that guesses
        # at unparseable input refuses commands nobody could have run anyway.
        return None
    statements = split_on(tokens, _STATEMENT_SEPARATORS)
    terminators = _statement_terminators(tokens)
    pipefail_active = False
    errexit_active = False
    for index, statement in enumerate(statements):
        if _sets_pipefail(statement) or _sets_errexit(statement):
            pipefail_active = pipefail_active or _sets_pipefail(statement)
            errexit_active = errexit_active or _sets_errexit(statement)
            continue

        # ARM 1 — the pipe. A verifier upstream of any pipe has its status
        # replaced by the last stage's.
        stages = split_on(statement, frozenset({_PIPE}))
        if (
            not pipefail_active
            and len(stages) >= 2
            and not any(_reads_pipestatus(later) for later in statements[index + 1 :])
        ):
            for upstream in stages[:-1]:
                name = _verifier_name(upstream)
                if name is not None:
                    return name, "pipe"

        # ARM 2 — the sequence (GHI #940). The shell reports the LAST statement's
        # status, so a verifier in an earlier one is discarded just as completely.
        # `pipefail` does not help here: it fixes which status a PIPELINE reports,
        # not whether a later statement then overwrites it.
        if errexit_active or terminators[index] not in _MASKING_SEPARATORS:
            continue
        later = [rest for rest in statements[index + 1 :] if rest]
        if not later:
            # A trailing separator (`gz check;`) leaves an empty tail. Nothing
            # runs after the verifier, so nothing overwrites its status.
            continue
        name = _verifier_name(stages[-1])
        if name is None:
            continue
        # `$?` reads the status of the statement that JUST ran. A read placed
        # after an intervening statement reports that statement's exit instead —
        # it looks like evidence and is not, so only the next statement counts.
        if _reads_exit_status(later[0]):
            continue
        return name, "sequence"
    return None


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
