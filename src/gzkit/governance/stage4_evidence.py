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
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

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


# ---------------------------------------------------------------------------
# Brief Demo extraction
# ---------------------------------------------------------------------------


def extract_demo_commands(brief_path: Path) -> list[str]:
    """Return the executable command lines from the brief's ``## Demo`` fenced block.

    Reads the first fenced code block under a ``## Demo`` heading; returns its non-empty,
    non-comment lines (a leading ``#`` marks a comment). Returns ``[]`` when no Demo
    section or fenced block is present.
    """
    if not brief_path.is_file():
        return []
    lines = brief_path.read_text(encoding="utf-8").splitlines()
    in_demo = False
    in_fence = False
    commands: list[str] = []
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
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
    return commands


# ---------------------------------------------------------------------------
# Observable collectors
# ---------------------------------------------------------------------------


def _run_demo(command: str, project_root: Path) -> DemoResult:
    """Execute one demo command, capturing exit status and a stdout/stderr tail."""
    proc = subprocess.run(  # noqa: S602 — demo commands are operator-authored in the brief
        command,
        shell=True,
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
    return EvidencePacket(
        obpi_id=obpi_id,
        generated_at=datetime.now(UTC).isoformat(),
        demos=demos,
        receipts=receipts,
        covers_total=total,
        covers_uncovered=uncovered,
        attestable=not blockers,
        blockers=blockers,
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
    return errors
