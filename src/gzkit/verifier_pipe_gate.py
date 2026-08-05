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

Coverage limits are declared, not hidden — see :data:`UNWITNESSABLE`.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS
from gzkit.shell_reading import program_name, split_on, strip_uv_run, tokenize_shell

__all__ = [
    "GZ_VERIFIER_VERBS",
    "UNWITNESSABLE",
    "VERIFIER_PIPE_CLAIM_ID",
    "VERIFIER_PROGRAMS",
    "Verdict",
    "decide",
    "masked_verifier",
]

#: Token that opens a new pipeline stage. Exact-match only — ``punctuation_chars``
#: emits ``||`` as a single token, so a logical-or is never read as a pipe.
_PIPE = "|"

#: Tokens that END a pipeline. A verifier in an earlier statement is not upstream
#: of a later statement's pipe: ``gz check; ls | head`` masks nothing.
_STATEMENT_SEPARATORS: frozenset[str] = frozenset({";", "&&", "||", "&", "\n"})

#: Interpreters whose ``-m <module>`` form names the real program.
_PYTHON_RUNNERS: frozenset[str] = frozenset({"python", "python3", "python3.13", "py"})

#: Shell constructs that genuinely preserve an upstream exit status through a
#: pipe. ``pipefail`` reports the first failing stage; ``PIPESTATUS[0]`` is the
#: remedy `.gzkit/rules/tests.md` names in the clause itself.
_EXIT_PRESERVING_MARKERS: tuple[str, ...] = ("pipefail", "PIPESTATUS")

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
_DECLARED_BEYOND_ARB: frozenset[str] = frozenset({"behave", "ruff", "pytest"})

#: Coverage this gate structurally cannot provide. Stated so a green is never
#: read as total (the `unwitnessable.md` precedent the resume gate follows).
UNWITNESSABLE: tuple[str, ...] = (
    "Verifiers invoked through a shell script or Makefile target: the gate reads "
    "the command string the harness is asked to run, not what that command runs "
    "in turn.",
    "Non-Bash execution surfaces (MCP tool calls, IDE-run tasks) never reach the "
    "Bash matcher, so a verifier piped there is unseen.",
    "`pipefail` / `PIPESTATUS` are honored as escapes on presence, not on correct "
    "use — a command that sets pipefail and then ignores the status is permitted.",
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

    A verifier is masked when it runs in any pipeline stage other than the last:
    the shell reports only the final process's status, so every upstream exit is
    thrown away. Returns the verifier's display name so the block prose can name
    what was actually silenced rather than echoing the whole command.
    """
    tokens = tokenize_shell(command)
    if tokens is None:
        # Unbalanced quotes. The shell will reject this too; a gate that guesses
        # at unparseable input refuses commands nobody could have run anyway.
        return None
    if any(marker in token for token in tokens for marker in _EXIT_PRESERVING_MARKERS):
        return None
    for statement in split_on(tokens, _STATEMENT_SEPARATORS):
        stages = split_on(statement, frozenset({_PIPE}))
        if len(stages) < 2:
            continue
        for upstream in stages[:-1]:
            name = _verifier_name(upstream)
            if name is not None:
                return name
    return None


def _block_prose(verifier: str) -> str:
    """Three-part guardrail prose: what failed, why forbidden, governed next step.

    Per `.claude/rules/guardrail-feedback-prose.md` — the feedback IS the prompt
    the operator would otherwise have typed, so it hands back the corrected
    command shape rather than pointing at documentation.
    """
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
        "NEXT STEP: capture to a file and read the real status:\n"
        '  <your command> > out.log 2>&1; echo "REAL EXIT: $?"\n'
        "then inspect `out.log` separately. If you genuinely need the pipe, opt in "
        "explicitly with `set -o pipefail` or read `${PIPESTATUS[0]}` — both preserve "
        "the verifier's status and are permitted. For attestation evidence, cite the "
        "ARB receipt's `exit_status` (`uv run gz arb step ...`), never a piped run."
    )


def decide(tool_name: str, tool_input: dict | None = None) -> Verdict:
    """Decide whether a tool call masks a verifier's exit status.

    Scoped to Bash: a verifier reaches the harness no other way, and the clause
    governs shell pipelines specifically.
    """
    if tool_name != "Bash":
        return Verdict(blocked=False)
    command = str((tool_input or {}).get("command", ""))
    verifier = masked_verifier(command)
    if verifier is None:
        return Verdict(blocked=False)
    return Verdict(blocked=True, reason=_block_prose(verifier))


# ---------------------------------------------------------------------------
# Live negative control — the floor's teeth for this gate (ADR-0.0.74 §5)
#
# ONE claim, because the clause declares one rule. The control asserts the
# DIFFERENTIAL (refuse piped AND permit unpiped) rather than the refusal alone:
# an always-block implementation is not a working gate, and a refusal-only
# control cannot tell the two apart.
# ---------------------------------------------------------------------------

VERIFIER_PIPE_CLAIM_ID = "verifier-exit-status-masked"


def _build_masked_verifier_violation() -> Path:
    """Return a temp root whose NAME seeds a runtime-unique command string.

    The random token is unknowable at mutation-authoring time, so a broken
    :func:`masked_verifier` cannot special-case a fixed sentinel to sneak past
    the control (the Step-4b facade attack — a FIXED string proves only that the
    gate refuses THAT string, never the general rule). The root itself is the
    fixture so the runner's ``shutil.rmtree`` cleans it.
    """
    return Path(tempfile.mkdtemp(prefix="gzkit-verifier-pipe-nc-"))


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
        enforces,
        get_enforcement_registry,
        set_known_claims,
    )
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )
    from gzkit.handoff_resume_gate import RESUME_GATE_CLAIM_IDS  # noqa: PLC0415

    set_known_claims(
        _KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS | RESUME_GATE_CLAIM_IDS | {VERIFIER_PIPE_CLAIM_ID}
    )
    existing = {r.claim_id for r in get_enforcement_registry()}
    if VERIFIER_PIPE_CLAIM_ID not in existing:
        enforces(
            VERIFIER_PIPE_CLAIM_ID,
            _build_masked_verifier_violation,
            _ep_verifier_pipe_gate,
        )(_verifier_pipe_marker)
