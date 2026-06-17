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
                command=command.strip(),
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
