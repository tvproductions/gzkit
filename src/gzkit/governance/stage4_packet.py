"""Re-execution of the agent-composed Step-4a packet's transcripts (GHI #942).

``stage4_evidence`` makes the *tool-generated* packet non-fabricable. This module
covers the other Stage-4 artifact: the markdown packet the ``narrator`` composes and
the operator actually reads when deciding to attest. Its pasted command output was
believed on the composing agent's word.

Observed 2026-09-02 on OBPI-0.35.0-04: a ``$``-prefixed block rendered ``gz covers
--json`` output with an invented object shape — keys ``obpi_id`` and ``coverage_pct``
that the command does not emit, three real fields dropped — around figures that were
themselves correct. A second block cited a proof command that returns nothing when
run. GHI #643's remedy does not reach either: Step 4b re-derives the *claim* from the
repository, and is never handed the *packet*, so a fabricated transcript passes an
adversary that never looks at it.

**The contract this module enforces.** A ``$`` prompt is a claim — *"I ran this and
this came back."* Every such transcript is re-run and the packet is held to it:

* a pasted line the command did not produce is a blocker (the fabrication direction);
* a transcript where neither the packet nor the command produced any output is a
  blocker (it witnesses nothing);
* a packet carrying no transcript at all is a blocker (Stage 4a owes the reader
  "one concrete command + output the reviewer can run").

Abridging is honest and re-indentation is presentation, so the comparison is
containment, not equality: the packet may show *less* than the command produced,
never something it did not. Output that cannot reproduce — a timestamp, a freshly
minted receipt id — is elided with ``...`` rather than pasted.

**What is deliberately NOT re-run.** A fenced shell block with no ``$`` prompt claims
no output; it cites an incantation whose result is carried elsewhere (the ARB receipt
rows). Re-running those would spend a full unittest sweep to witness a claim nobody
made. They are reported as citations so the operator sees what this check did not
witness.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.governance.stage4_evidence import _join_demo_commands

# A fenced block cites shell commands only when it says so. A ``json``/``text``
# block is data: reading its lines as commands fills the operator's surface with
# noise, and an empty info string is too weak a signal to spend that noise on.
_SHELL_INFO_STRINGS: frozenset[str] = frozenset({"bash", "sh", "shell", "console"})

_FENCE_RE = re.compile(r"^\s*```+\s*([A-Za-z0-9_+.-]*)\s*$")
_PROMPT_RE = re.compile(r"^\s*\$[ \t]?(.*)$")
_ELISION_RE = re.compile(r"^(?:#\s*)?(?:\.{2,}|…)$")

_COMMAND_TIMEOUT_SECONDS = 120
_OUTPUT_TAIL_LINES = 40


class Transcript(BaseModel):
    """One ``$``-prompted claim parsed out of the packet."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., description="The command as pasted, joined across lines")
    claimed: list[str] = Field(..., description="Output lines the packet says came back")


class TranscriptResult(BaseModel):
    """Observed result of re-running one transcript, against what it claimed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., description="The transcript's command, verbatim")
    exit_status: int = Field(..., description="Observed exit code (-1 if it did not run)")
    timed_out: bool = Field(default=False, description="True if the command exceeded the limit")
    produced_output: bool = Field(..., description="True if the re-run wrote anything")
    missing_lines: list[str] = Field(..., description="Claimed lines the command did not produce")
    output_tail: str = Field(default="", description="Last lines of the observed output")


class PacketVerification(BaseModel):
    """Verdict for one Step-4a packet."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    packet: str = Field(..., description="Path of the packet that was verified")
    transcripts: list[TranscriptResult] = Field(..., description="Per-transcript re-run results")
    citations: list[str] = Field(..., description="Cited commands, reported but not re-run")
    verified: bool = Field(..., description="True only if every blocker is clear")
    blockers: list[str] = Field(..., description="Reasons the packet is NOT verified")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _fenced_blocks(text: str) -> list[tuple[str, list[str]]]:
    """Return ``(info_string, lines)`` for each fenced block in the packet."""
    blocks: list[tuple[str, list[str]]] = []
    info: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        match = _FENCE_RE.match(line)
        if match is None:
            if info is not None:
                body.append(line)
            continue
        if info is None:
            info, body = match.group(1).lower(), []
        else:
            blocks.append((info, body))
            info = None
    if info is not None:
        blocks.append((info, body))  # unterminated fence: read what is there
    return blocks


def _block_transcripts(lines: list[str]) -> list[Transcript]:
    """Parse one fenced block into transcripts.

    A prompt line opens a command; the command may span physical lines exactly as a
    shell command does, so the joiner from ``stage4_evidence`` decides where it ends
    (GHI #965 — splitting at newlines would read a quoted program's own body as
    claimed output and report every interior line as fabricated). Everything from
    there to the next prompt is what the packet says came back.
    """
    transcripts: list[Transcript] = []
    index = 0
    while index < len(lines):
        match = _PROMPT_RE.match(lines[index])
        if match is None:
            index += 1
            continue
        joined = _join_demo_commands([match.group(1).strip(), *lines[index + 1 :]])
        if not joined:
            index += 1
            continue
        command = joined[0]
        index += len(command.split("\n"))
        claimed: list[str] = []
        while index < len(lines) and _PROMPT_RE.match(lines[index]) is None:
            claimed.append(lines[index])
            index += 1
        transcripts.append(Transcript(command=command, claimed=claimed))
    return transcripts


def extract_transcripts(text: str) -> list[Transcript]:
    """Return every ``$``-prompted transcript in the packet, in document order."""
    transcripts: list[Transcript] = []
    for _info, lines in _fenced_blocks(text):
        transcripts.extend(_block_transcripts(lines))
    return transcripts


def extract_citation_commands(text: str) -> list[str]:
    """Return shell commands cited without a prompt — reported, never re-run."""
    citations: list[str] = []
    for info, lines in _fenced_blocks(text):
        if info not in _SHELL_INFO_STRINGS:
            continue
        if any(_PROMPT_RE.match(line) for line in lines):
            continue  # a transcript block: its lines are a claim, not citations
        citations.extend(_join_demo_commands(lines))
    return citations


# ---------------------------------------------------------------------------
# Re-execution
# ---------------------------------------------------------------------------


def _claimed_content(claimed: list[str]) -> list[str]:
    """Return the claim's load-bearing lines — blanks and elisions carry none."""
    return [
        stripped
        for stripped in (line.strip() for line in claimed)
        if stripped and not _ELISION_RE.match(stripped)
    ]


def _run(command: str, project_root: Path) -> tuple[int, str, bool]:
    """Re-run one transcript command; return ``(exit_status, output, timed_out)``.

    The command comes from a packet an agent composed, which is the point: the
    fabrication being witnessed is precisely a claim about what running it does. A
    command that never returns must fail the gate rather than hold it, so the run is
    bounded — this check stands between the agent and the operator's attestation.
    """
    try:
        proc = subprocess.run(  # noqa: S602 — re-running the packet's own claim is the check
            command,
            shell=True,
            cwd=project_root,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return -1, "", True
    return proc.returncode, (proc.stdout or "") + (proc.stderr or ""), False


def _verify_transcript(transcript: Transcript, project_root: Path) -> TranscriptResult:
    """Re-run one transcript and record which of its claimed lines did not reproduce."""
    exit_status, output, timed_out = _run(transcript.command, project_root)
    claimed = _claimed_content(transcript.claimed)
    # Containment, not equality: a packet may show less than the command produced
    # (abridging) and may re-indent what it shows (presentation). It may not show
    # what the command never wrote — that is the one direction fabrication takes.
    missing = [] if timed_out else [line for line in claimed if line not in output]
    tail = "\n".join(output.splitlines()[-_OUTPUT_TAIL_LINES:])
    return TranscriptResult(
        command=transcript.command,
        exit_status=exit_status,
        timed_out=timed_out,
        produced_output=bool(output.strip()),
        missing_lines=missing,
        output_tail=tail,
    )


def _blockers(results: list[TranscriptResult], transcripts: list[Transcript]) -> list[str]:
    blockers: list[str] = []
    if not results:
        blockers.append(
            "Packet contains no `$` transcript. Stage 4a owes the reader one concrete "
            "command and the output it produced; nothing here can be reproduced."
        )
    for result, transcript in zip(results, transcripts, strict=True):
        if result.timed_out:
            blockers.append(
                f"Command timed out after {_COMMAND_TIMEOUT_SECONDS}s: {result.command}"
            )
            continue
        if result.missing_lines:
            shown = "; ".join(result.missing_lines[:3])
            blockers.append(
                f"Command did not produce {len(result.missing_lines)} pasted line(s) "
                f"[{shown}]: {result.command}"
            )
        if not result.produced_output and not _claimed_content(transcript.claimed):
            blockers.append(
                f"Transcript witnesses nothing — no output pasted and none produced: "
                f"{result.command}"
            )
    return blockers


def verify_packet(project_root: Path, packet_path: Path) -> PacketVerification:
    """Re-run every transcript in a Step-4a packet and hold the packet to its claims."""
    text = packet_path.read_text(encoding="utf-8")
    transcripts = extract_transcripts(text)
    results = [_verify_transcript(t, project_root) for t in transcripts]
    blockers = _blockers(results, transcripts)
    return PacketVerification(
        packet=str(packet_path),
        transcripts=results,
        citations=extract_citation_commands(text),
        verified=not blockers,
        blockers=blockers,
    )
