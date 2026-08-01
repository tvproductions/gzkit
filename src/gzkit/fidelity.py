"""Fidelity Assertions model, parser, and gate (ADR-0.0.73, OBPI-0.0.73-03).

``FidelityAssertion`` is a frozen Pydantic model that records one runnable
assertion from an ADR's ``## Fidelity Assertions`` block.  The parser reads
that block from an ADR file and the gate runs each command, filling in the
``observed`` exit code and ``result`` (``"pass"`` or ``"fail"``).
"""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class FidelityAssertion(BaseModel):
    """One runnable assertion from an ADR Decision's Fidelity Assertions table.

    Fields
    ------
    adr_id          machine-stable ADR identifier slug
    claim           human-readable description of what this assertion tests
    command         shell command to run (split via shlex before subprocess)
    expected_exit   exit code the command must return for the assertion to pass
    observed        actual exit code recorded after the gate runs (None before)
    result          ``"pass"`` or ``"fail"`` after the gate runs (None before)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str = Field(..., description="ADR identifier slug")
    claim: str = Field(..., description="Human-readable assertion description")
    command: str = Field(..., description="Command to run (shell=False)")
    expected_exit: int = Field(..., description="Expected exit code")
    observed: int | None = Field(None, description="Observed exit code (set by gate)")
    result: str | None = Field(None, description="'pass' or 'fail' (set by gate)")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

_FIDELITY_HEADING_RE = re.compile(r"^##\s+Fidelity\s+Assertions\s*$", re.IGNORECASE)
_NEXT_HEADING_RE = re.compile(r"^##\s+")
_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
_SEPARATOR_RE = re.compile(r"^\s*\|[-| :]+\|\s*$")


_SELF_REF_VERB = ("gz", "adr", "fidelity")


def is_self_referential_command(command: str) -> bool:
    """Return True when the command invokes the fidelity gate itself (``gz adr fidelity``).

    A fidelity assertion whose command runs the gate that evaluates it is
    tautological: the gate must reach the row to run it, so the row can never be
    red while it is being evaluated (GHI #702). Its subject is the parser, not
    the ADR's thesis — it inflates the witness count without exercising the
    delivered surface (#699's ``copy-vs-self`` theater signature).

    Detection is a contiguous ``gz adr fidelity`` token run anywhere in the
    command (a leading ``uv run`` wrapper is transparent), which is the only
    shape that re-enters the gate. A command we cannot tokenize is not
    self-referential — the gate runner already reports it as unrunnable.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    run = _SELF_REF_VERB
    return any(tuple(tokens[i : i + len(run)]) == run for i in range(len(tokens) - len(run) + 1))


def _strip_inline_code(cell: str) -> str:
    """Strip surrounding markdown inline-code backticks from a command cell.

    ADR authors naturally wrap a command in ``backticks`` (it renders as code in
    the table). The gate runs the cell via ``shlex.split(command, shell=False)``,
    so a literal backtick makes the first token ```uv`` — not an executable —
    yielding an opaque ``observed=-1`` (GHI #673). Stripping surrounding backticks
    makes the natural authoring form runnable; a bare command is unaffected.
    """
    return cell.strip().strip("`").strip()


def _extract_fidelity_block(text: str) -> list[str]:
    """Return lines between the ## Fidelity Assertions heading and the next H2."""
    lines = text.splitlines()
    in_block = False
    block: list[str] = []
    for line in lines:
        if _FIDELITY_HEADING_RE.match(line):
            in_block = True
            continue
        if in_block:
            if _NEXT_HEADING_RE.match(line):
                break
            block.append(line)
    return block


def parse_fidelity_assertions(adr_path: Path) -> list[FidelityAssertion]:
    """Parse the ``## Fidelity Assertions`` block from an ADR file.

    Returns one ``FidelityAssertion`` per data row in the table.  The
    ``observed`` and ``result`` fields are ``None`` until the gate runs.

    Raises
    ------
    ValueError
        If the block is absent or no data rows are found.

    """
    text = adr_path.read_text(encoding="utf-8")
    adr_id = adr_path.stem

    block = _extract_fidelity_block(text)
    if not block:
        raise ValueError(
            f"No '## Fidelity Assertions' block found in {adr_path}. "
            "Every ADR Decision must carry a runnable Fidelity Assertions block "
            "(ADR-0.0.73 Boundary Invariant #4)."
        )

    assertions: list[FidelityAssertion] = []
    header_seen = False
    for line in block:
        if not _TABLE_ROW_RE.match(line):
            continue
        if _SEPARATOR_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if not header_seen:
            header_seen = True
            continue
        claim, command, expected_exit_str = cells[0], cells[1], cells[2]
        try:
            expected_exit = int(expected_exit_str.strip())
        except ValueError:
            continue
        assertions.append(
            FidelityAssertion(
                adr_id=adr_id,
                claim=claim.strip(),
                command=_strip_inline_code(command),
                expected_exit=expected_exit,
                observed=None,
                result=None,
            )
        )

    if not assertions:
        raise ValueError(
            f"'## Fidelity Assertions' block in {adr_path} contains no data rows. "
            "The table must have at least one claim/command/expected-exit row."
        )

    # Self-referential rows are a policy breach, NOT a structural (ValueError)
    # defect: they parse cleanly. Raise PolicyBreachError (exit 3) so every
    # consumer hard-blocks — the absence handlers in assert_fidelity_for_ceremony
    # and adr_fidelity_cmd catch ValueError only, and must never downgrade a
    # tautological block to a silent "no block" warning (GHI #702).
    self_referential = [a for a in assertions if is_self_referential_command(a.command)]
    if self_referential:
        from gzkit.core.exceptions import PolicyBreachError  # noqa: PLC0415

        rows = "\n".join(f"  - {a.claim!r} (command={a.command!r})" for a in self_referential)
        raise PolicyBreachError(
            f"Fidelity gate: {len(self_referential)} self-referential assertion(s) "
            f"in {adr_path.name}:\n{rows}\n"
            "A row whose command invokes `gz adr fidelity` asserts the gate that "
            "evaluates it — it cannot fail while being evaluated and exercises no "
            "part of the ADR's thesis (GHI #702). Remove the row; keep only "
            "assertions that run the ADR's delivered surface."
        )
    return assertions


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


def run_fidelity_gate(
    assertions: list[FidelityAssertion],
    adr_id: str,
) -> list[FidelityAssertion]:
    """Run each assertion's command and return updated assertions with results.

    Each assertion's ``observed`` is set to the subprocess return code and
    ``result`` is ``"pass"`` when ``observed == expected_exit`` else ``"fail"``.
    Pydantic frozen models are immutable; new instances are created via
    ``model_copy(update=...)``.
    """
    results: list[FidelityAssertion] = []
    for assertion in assertions:
        try:
            proc = subprocess.run(  # noqa: S603
                shlex.split(assertion.command),
                capture_output=True,
                check=False,
            )
            observed = proc.returncode
        except (OSError, ValueError):
            observed = -1
        result = "pass" if observed == assertion.expected_exit else "fail"
        results.append(assertion.model_copy(update={"observed": observed, "result": result}))
    return results


# ---------------------------------------------------------------------------
# Ceremony gate — the single bound gate both closeout and audit consume
# ---------------------------------------------------------------------------


def assert_fidelity_for_ceremony(adr_path: Path, adr_id: str) -> list[FidelityAssertion]:
    """Run the ADR's Fidelity Assertions as a ceremony gate (ADR-0.0.73, OBPI-04).

    This is the one bound gate that BOTH the closeout ceremony and the audit
    ceremony invoke, replacing the prose 'Demonstrate Value' step. Parses the
    ADR's ``## Fidelity Assertions`` block and runs each assertion against the
    running system.

    Absence policy (graceful migration, operator-ratified 2026-06-17): the ADR
    scopes out back-filling fidelity assertions onto already-VALIDATED ADRs (that
    is the forced follow-up sweep). So when an ADR carries NO block, the gate
    emits a loud warning (the absence is flagged, not silently accepted — the
    prose step is still gone) but does NOT block. Hard presence-enforcement stays
    at ADR closeout (Boundary Invariant #4) and the new-ADR template. When a
    block IS present, the gate hard-runs and a failed assertion blocks.

    Raises
    ------
    PolicyBreachError
        when a present block has any failing assertion (observed != expected).

    Returns the run assertions (all passing) when the gate is green, or an empty
    list when the block is absent (warning emitted).

    """
    from gzkit.core.exceptions import PolicyBreachError  # noqa: PLC0415

    try:
        assertions = parse_fidelity_assertions(adr_path)
    except ValueError:
        # Warning is a log, not a result — route to stderr so `--json` stdout
        # stays valid JSON (CLI output contract; `.claude/rules/cli.md`).
        from rich.console import Console  # noqa: PLC0415

        Console(stderr=True).print(
            f"[yellow]Fidelity gate (warning):[/yellow] {adr_id} has no "
            "'## Fidelity Assertions' block. The prose 'Demonstrate Value' step "
            "is removed (ADR-0.0.73, OBPI-0.0.73-04); presence is enforced at ADR "
            "closeout (Boundary Invariant #4). Author a block before closeout."
        )
        return []

    results = run_fidelity_gate(assertions, adr_id=adr_id)
    failed = [r for r in results if r.result == "fail"]
    if failed:

        def _hint(assertion: FidelityAssertion) -> str:
            # observed == -1 is the runner's "could not execute" sentinel (OSError
            # /ValueError from shlex.split + subprocess), distinct from a real
            # exit-code mismatch. Name the cause so the failure is actionable
            # (guardrail-feedback-prose rule), not an opaque -1 (GHI #673).
            if assertion.observed == -1:
                return (
                    " — command could not be executed (not found or unparseable; "
                    "check for stray markdown backticks or a shell builtin, "
                    "not a real exit-code mismatch)"
                )
            return ""

        lines = "\n".join(
            f"  FAIL  {r.claim} (command={r.command!r}, "
            f"expected={r.expected_exit}, observed={r.observed}){_hint(r)}"
            for r in failed
        )
        raise PolicyBreachError(
            f"Fidelity gate: {len(failed)} assertion(s) failed for {adr_id}:\n"
            f"{lines}\n"
            f"Fix the ADR's thesis against the running system, then re-run "
            f"`gz adr fidelity {adr_id}`."
        )
    return results
