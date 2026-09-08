"""Tool-generated, fail-closed Stage-4 OBPI-acceptance evidence (GHI #643).

The Stage-4 acceptance ceremony was a passive presenter: the agent authored the
evidence packet (Value Narrative, Key Proof, Evidence table, REQ coverage) as prose,
and `gz obpi complete` trusted it. That let an agent assert "this is verified" without
running anything — the fabrication class GHI #643 documents (and ADR-0.0.74 §5 forbids).

This module makes the evidence **non-fabricable** via two independent mechanisms the
agent does not author:

* **generate** (`generate_evidence_packet`) — runs the brief's ``## Demo`` command(s),
  reads the on-disk ARB receipts, and runs ``gz covers``; writes an ``EvidencePacket``
  the operator reads at Stage 4. The agent relays this, it does not type it.
* **validate** (`validate_stage4_evidence`) — at ``gz obpi complete`` time, **re-runs the
  demo live** (does not trust the packet's recorded exit), re-resolves the receipts on
  disk, and re-checks coverage; fail-closed (returns errors) if the packet is absent, the
  live demo exits non-zero, a required receipt is missing/red, or any REQ is uncovered.

Keystone: the brief ``## Demo`` MUST be **assert-shaped** — exit non-zero on a bad state
(``raise SystemExit(0 if <invariant> else 1)``), never a bare ``print``. A print-shaped
demo exits 0 even when the OBPI is broken, which is exactly how the GHI #643 fabrication
survived. ``validate_stage4_evidence`` requires at least one demo command and treats a
non-zero live exit as fail-closed.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.acceptance_store import acceptance_blockers
from gzkit.core.validation_rules import ValidationError

# Canonical ARB steps whose receipts back a Heavy-lane completion.
_REQUIRED_RECEIPT_STEPS: tuple[str, ...] = ("ruff", "typecheck", "unittest")

_EVIDENCE_DIR = (".gzkit", "evidence")
_STDOUT_TAIL_LINES = 40


class DemoResult(BaseModel):
    """Observed result of running one brief ``## Demo`` command."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., description="The demo command line, verbatim")
    ran: bool = Field(..., description="True if the command was executed")
    exit_status: int = Field(..., description="Observed process exit code (-1 if not run)")
    stdout_tail: str = Field(default="", description="Last lines of combined stdout/stderr")


class ReceiptResult(BaseModel):
    """Observed state of one canonical ARB receipt on disk."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step: str = Field(..., description="Canonical ARB step name (ruff/typecheck/unittest)")
    found: bool = Field(..., description="True if a receipt for this step exists on disk")
    receipt_id: str | None = Field(default=None, description="Newest receipt filename for the step")
    exit_status: int | None = Field(default=None, description="Receipt's recorded exit_status")


class EvidencePacket(BaseModel):
    """Tool-generated Stage-4 evidence — derived from observables, not agent prose."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="OBPI slug this packet attests")
    generated_at: str = Field(..., description="ISO-8601 UTC generation timestamp")
    demos: list[DemoResult] = Field(..., description="Per-demo observed run results")
    receipts: list[ReceiptResult] = Field(..., description="Canonical ARB receipt states")
    covers_total: int = Field(..., description="Total REQs in the brief")
    covers_uncovered: int = Field(..., description="REQs with no covering test (uncovered)")
    attestable: bool = Field(..., description="True only if every blocker is clear")
    blockers: list[str] = Field(..., description="Reasons the packet is NOT attestable")
    review_blockers: list[str] = Field(
        default_factory=list, description="Step 4b still required before attestation"
    )


# ---------------------------------------------------------------------------
# Brief Demo extraction
# ---------------------------------------------------------------------------


_HEREDOC_INTRO = re.compile(r"""<<-?[ \t]*(?:'([^']+)'|"([^"]+)"|([A-Za-z_][A-Za-z0-9_]*))""")


def _read_heredoc_delimiter(text: str, index: int) -> tuple[str | None, int]:
    """Return the heredoc delimiter introduced at ``index``, and the index past it."""
    match = _HEREDOC_INTRO.match(text, index)
    if match is None:
        return None, index
    return (match.group(1) or match.group(2) or match.group(3)), match.end()


def _scan_shell(text: str) -> tuple[bool, list[str]]:
    """Return ``(is_open, heredoc_delimiters)`` for an accumulated shell command.

    ``is_open`` is True while the text is mid-construct — an unclosed quote, an
    unbalanced ``$(``, or a trailing backslash — meaning the next physical line
    belongs to this same command. Heredoc delimiters are reported separately
    because their bodies end at a sentinel line, not at a balanced character.
    """
    quote: str | None = None
    depth = 0
    escaped = False
    heredocs: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if escaped:
            escaped = False
        elif quote == "'":
            # Single quotes are literal in POSIX shell: backslash does not escape.
            if char == "'":
                quote = None
        elif char == "\\":
            escaped = True
        elif quote is not None:
            if char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "$" and text.startswith("$(", index):
            depth += 1
            index += 1
        elif char == ")" and depth:
            depth -= 1
        elif text.startswith("<<", index) and not text.startswith("<<<", index):
            delimiter, end = _read_heredoc_delimiter(text, index)
            if delimiter is not None:
                heredocs.append(delimiter)
                index = end
                continue
        index += 1
    return quote is not None or depth > 0 or escaped, heredocs


def _join_demo_commands(fence_lines: list[str]) -> list[str]:
    r"""Join physical lines into whole shell commands (GHI #965).

    Each returned string is executed with ``shell=True``, so the contract is to
    return exactly what a human would have pasted. Splitting at physical line
    boundaries shattered any command spanning lines — a quoted ``python -c``
    program, a ``\\``-continued line, a multi-line ``$(...)`` — and reported
    NOT-ATTESTABLE for a green state.

    A blank or ``#`` line is a fence comment only at the *start* of a command;
    inside a continuation it is program text, and interior lines keep their
    indentation because the languages they carry are whitespace-significant.
    """
    commands: list[str] = []
    pending: list[str] = []
    heredocs: list[str] = []
    for line in fence_lines:
        if heredocs:
            # A heredoc body is opaque: it ends at its sentinel, never at a quote.
            pending.append(line)
            if line.strip() == heredocs[0]:
                heredocs.pop(0)
                if not heredocs:
                    commands.append("\n".join(pending))
                    pending = []
            continue
        if pending:
            pending.append(line)
        else:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            pending.append(stripped)
        is_open, heredocs = _scan_shell("\n".join(pending))
        if is_open or heredocs:
            continue
        commands.append("\n".join(pending))
        pending = []
    if pending:
        # Fail-closed: hand an unterminated command to the shell so it reports a
        # real non-zero exit. Dropping it would turn a malformed Demo into a pass.
        commands.append("\n".join(pending))
    return commands


def extract_demo_commands(brief_path: Path) -> list[str]:
    """Return the executable commands from the brief's ``## Demo`` fenced block.

    Reads the first fenced code block under a ``## Demo`` heading and joins its lines
    into whole commands (see ``_join_demo_commands``); a line starting a command with
    ``#`` marks a comment. Returns ``[]`` when no Demo section or fenced block is present.
    """
    if not brief_path.is_file():
        return []
    lines = brief_path.read_text(encoding="utf-8").splitlines()
    in_demo = False
    in_fence = False
    fence_lines: list[str] = []
    for line in lines:
        if line.startswith("## "):
            # Entering Demo, or leaving it for the next H2.
            in_demo = line.strip().lower() == "## demo"
            continue
        if not in_demo:
            continue
        if line.lstrip().startswith("```"):
            if in_fence:
                break  # end of the Demo fenced block
            in_fence = True
            continue
        if in_fence:
            fence_lines.append(line)
    return _join_demo_commands(fence_lines)


# ---------------------------------------------------------------------------
# Observable collectors
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def replay_shell() -> str | None:
    r"""Return the POSIX shell transcript replay runs under, or None if there is none.

    THE GATE AND ITS VERIFIER MUST AGREE ON WHAT A SHELL IS. `verifier_pipe_gate`
    refuses a verifier in a non-final pipeline stage and sanctions exactly two
    opt-outs -- `set -o pipefail` and `${PIPESTATUS[0]}` -- and BOTH ARE BASH
    FEATURES. Replay ran through `subprocess.run(shell=True)`, whose shell is
    the platform's default, and on neither platform is that a shell the gate's
    own recommendations run under. Measured 2026-09-07:

        $ /bin/dash -c 'set -o pipefail; echo OK | tail -1'
        /bin/dash: 1: set: Illegal option -o pipefail
        dash exit: 2

    `/bin/sh` is bash on macOS and **dash** on Debian/Ubuntu, so a packet using
    the SANCTIONED escape was rejected as a fabricated transcript on every Linux
    runner while verifying on a developer machine (GHI #981). On Windows the
    default is `cmd.exe`, which is not a POSIX shell at all: `;` is not a
    statement separator and `$?` is not a variable, so a transcript reading
    `python3 -c "...; sys.exit(3)"; echo "REAL EXIT: $?"` had its whole suffix
    swallowed as an argument -- the run exited 3 with the pasted status line
    never produced, and the verifier reported a fabricated transcript
    (GHI #982). One defect, two platforms, one seam.

    Resolved ONCE and shared by both replay sites (`_run_demo` here and
    `stage4_packet._run`), because two callers deciding independently which
    shell replays a transcript are two callers that can disagree about whether
    a given packet verifies -- the same single-authority reason `shell_reading`
    is shared between the gates that PARSE these commands.

    **The Windows lookup is explicit rather than a bare `which`.** Git for
    Windows ships bash and is present on the GitHub runner image; so, on some
    images, is `System32\\bash.exe`, which is the WSL LAUNCHER -- a different
    filesystem namespace, where the packet's `cwd` and its relative paths do
    not mean what they mean here. Resolving that would replay transcripts
    against a different tree and report the result as this one's.

    Returns None when no POSIX shell is available. Callers then fall back to the
    platform default, which is the pre-existing behaviour, and the tests that
    depend on POSIX shell semantics declare the limit and skip rather than
    asserting a shell that is not there.
    """
    if os.name == "nt":
        return _windows_posix_shell()
    return shutil.which("bash")


def _windows_posix_shell() -> str | None:
    r"""Return Git for Windows' bash, never the WSL launcher, or None.

    DERIVED FROM THE ``git`` ON PATH rather than from ``%PROGRAMFILES%``: the
    bash that should replay a transcript is the one shipped beside the git this
    process already resolves, so a non-default install is found and no env-var
    read is needed (``tests/policy/test_env_usage.py`` allowlists env access,
    and this lookup has a better answer than widening it). Git for Windows lays
    out ``<root>\cmd\git.exe`` beside ``<root>\bin\bash.exe``.
    """
    git = shutil.which("git")
    if git is not None:
        candidate = Path(git).resolve().parent.parent / "bin" / "bash.exe"
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("bash")
    if found is None:
        return None
    # ``System32\bash.exe`` is the WSL LAUNCHER. It runs in a different
    # filesystem namespace, so a transcript replayed there would be verified
    # against a different tree and the result reported as this one's.
    return None if "system32" in found.replace("/", "\\").lower() else found


def replay_invocation(command: str) -> tuple[list[str] | str, bool]:
    """Return the ``(args, shell)`` pair replaying *command* under `replay_shell`.

    An ARGV, not `shell=True` plus `executable=`. On POSIX the two are the same
    thing -- CPython builds `[executable, "-c", command]` either way -- but on
    Windows `shell=True` appends the command to `COMSPEC /c`, so an `executable`
    override hands `/c` to a shell that does not take it. The argv form is the
    one spelling that means the same thing on both platforms.
    """
    shell = replay_shell()
    if shell is None:
        return command, True
    return [shell, "-c", command], False


def _run_demo(command: str, project_root: Path) -> DemoResult:
    """Execute one demo command, capturing exit status and a stdout/stderr tail."""
    args, use_shell = replay_invocation(command)
    proc = subprocess.run(  # noqa: S602 — demo commands are operator-authored in the brief
        args,
        shell=use_shell,
        cwd=project_root,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(combined.splitlines()[-_STDOUT_TAIL_LINES:])
    return DemoResult(command=command, ran=True, exit_status=proc.returncode, stdout_tail=tail)


def _collect_receipts(project_root: Path) -> list[ReceiptResult]:
    """Read the newest ARB receipt per canonical step from ``artifacts/receipts/``."""
    receipts_dir = project_root / "artifacts" / "receipts"
    results: list[ReceiptResult] = []
    for step in _REQUIRED_RECEIPT_STEPS:
        # ruff uses arb-ruff-*; step-wrapped checks use arb-step-<name>-*.
        patterns = ("arb-ruff-*.json",) if step == "ruff" else (f"arb-step-{step}-*.json",)
        candidates: list[Path] = []
        for pat in patterns:
            candidates.extend(receipts_dir.glob(pat))
        if not candidates:
            results.append(ReceiptResult(step=step, found=False))
            continue
        newest = max(candidates, key=lambda p: p.stat().st_mtime)
        try:
            data = json.loads(newest.read_text(encoding="utf-8"))
            exit_status = int(data.get("exit_status", -1))
        except (json.JSONDecodeError, ValueError, OSError):
            exit_status = -1
        results.append(
            ReceiptResult(step=step, found=True, receipt_id=newest.name, exit_status=exit_status)
        )
    return results


def _counts_from_covers_summary(data: dict) -> tuple[int, int]:
    """Return (total_reqs, behavior_uncovered_count) from a ``gz covers --json`` payload.

    Uses ``behavior_uncovered_reqs``, NOT ``uncovered_reqs`` (GHI #683). SUPPORT and
    STRUCTURAL-FENCE REQs are proven by ledger+validator / parent-ADR invariant, never a
    ``@covers`` test (ADR-0.0.59), so they always appear in ``uncovered_reqs``; counting
    them as an attestability blocker is a category error that reports NOT-ATTESTABLE for
    every SUPPORT-carrying OBPI. Only an uncovered BEHAVIOR REQ is a real Stage-4 blocker.
    """
    summary = data.get("summary", {})
    return int(summary.get("total_reqs", 0)), int(summary.get("behavior_uncovered_reqs", 0))


def _covers_counts(project_root: Path, obpi_id: str) -> tuple[int, int]:
    """Return (total_reqs, uncovered_count) from ``gz covers <obpi> --json``."""
    proc = subprocess.run(  # noqa: S603
        ["uv", "run", "gz", "covers", obpi_id, "--json"],
        cwd=project_root,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )
    try:
        return _counts_from_covers_summary(json.loads(proc.stdout))
    except (json.JSONDecodeError, ValueError):
        return 0, -1  # -1 uncovered signals a covers failure → blocker


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------


def _compute_blockers(
    demos: list[DemoResult],
    receipts: list[ReceiptResult],
    covers_uncovered: int,
) -> list[str]:
    blockers: list[str] = []
    if not demos:
        blockers.append(
            "No ## Demo command in the brief. Stage-4 evidence requires an assert-shaped "
            "demo (exit non-zero on a bad state) so completion can re-run it fail-closed."
        )
    for d in demos:
        if d.exit_status != 0:
            blockers.append(f"Demo exited {d.exit_status} (expected 0): {d.command}")
    for r in receipts:
        if not r.found:
            blockers.append(f"No ARB receipt for canonical step '{r.step}'.")
        elif r.exit_status != 0:
            blockers.append(
                f"ARB receipt for '{r.step}' has exit_status {r.exit_status} (expected 0)."
            )
    if covers_uncovered < 0:
        blockers.append("gz covers did not resolve — REQ coverage could not be verified.")
    elif covers_uncovered > 0:
        blockers.append(f"{covers_uncovered} BEHAVIOR REQ(s) uncovered by a covering test.")
    return blockers


def generate_evidence_packet(project_root: Path, brief_path: Path, obpi_id: str) -> EvidencePacket:
    """Run the brief Demo + read receipts + run covers; build the EvidencePacket."""
    demos = [_run_demo(cmd, project_root) for cmd in extract_demo_commands(brief_path)]
    receipts = _collect_receipts(project_root)
    total, uncovered = _covers_counts(project_root, obpi_id)
    blockers = _compute_blockers(demos, receipts, uncovered)
    blockers.extend(acceptance_blockers(project_root, obpi_id, stage="stage2"))
    review_blockers = acceptance_blockers(project_root, obpi_id)
    return EvidencePacket(
        obpi_id=obpi_id,
        generated_at=datetime.now(UTC).isoformat(),
        demos=demos,
        receipts=receipts,
        covers_total=total,
        covers_uncovered=uncovered,
        attestable=not blockers and not review_blockers,
        blockers=blockers,
        review_blockers=review_blockers,
    )


def packet_path(project_root: Path, obpi_id: str) -> Path:
    """Return the evidence-packet path for an OBPI under the project root."""
    return project_root.joinpath(*_EVIDENCE_DIR) / f"{obpi_id}.evidence.json"


def write_packet(project_root: Path, packet: EvidencePacket) -> Path:
    """Write the evidence packet to disk and return its path."""
    path = packet_path(project_root, packet.obpi_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(packet.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def load_packet(project_root: Path, obpi_id: str) -> EvidencePacket | None:
    """Load and validate an OBPI's evidence packet, or return None if absent/invalid."""
    path = packet_path(project_root, obpi_id)
    if not path.is_file():
        return None
    try:
        return EvidencePacket.model_validate_json(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


# ---------------------------------------------------------------------------
# Validate (independent re-derivation — does NOT trust the packet)
# ---------------------------------------------------------------------------


def _err(message: str) -> ValidationError:
    return ValidationError(type="stage4_evidence", artifact="stage4-evidence", message=message)


def validate_stage4_evidence(
    project_root: Path, brief_path: Path, obpi_id: str
) -> list[ValidationError]:
    """Fail-closed Stage-4 gate: re-derive evidence live; never trust the packet's values.

    Returns one ValidationError per blocker (empty → attestable). The gate:

    1. A tool-generated packet must EXIST (proves ``gz obpi present-evidence`` was run).
    2. The brief Demo is RE-RUN live; every demo must exit 0 (assert-shaped). Absence of
       any demo is fail-closed.
    3. The canonical ARB receipts are re-resolved on disk; each must be present + exit 0.
    4. ``gz covers`` is re-run; uncovered REQs is fail-closed.
    """
    errors: list[ValidationError] = []
    if load_packet(project_root, obpi_id) is None:
        errors.append(
            _err(
                f"No tool-generated evidence packet for {obpi_id}. Run "
                f"`gz obpi present-evidence {obpi_id}` first — Stage-4 evidence may not be "
                "agent-authored (GHI #643)."
            )
        )
    # Re-derive live, independently of the packet's recorded values.
    fresh = generate_evidence_packet(project_root, brief_path, obpi_id)
    errors.extend(_err(b) for b in fresh.blockers)
    errors.extend(_err(b) for b in fresh.review_blockers)
    return errors
