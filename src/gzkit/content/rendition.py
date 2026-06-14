"""Candidate rendition model and staging path helper (OBPI-0.0.37-21).

The *candidate* rendition is the authoring artifact produced by the
``gz content compose`` tool: the agent supplies the compressed text; the
tool validates invariant-floor compliance, computes byte evidence, writes
the candidate, and emits a ledger event. The *committed* rendition (the
durable store) and deterministic playback are OBPI-22 scope.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ByteEvidence(BaseModel):
    """Per-tier byte evidence emitted alongside every compose run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    invariant_bytes: int = Field(..., description="Bytes of all invariant-tier corpus entries")
    compressible_bytes_before: int = Field(
        ..., description="Bytes of all compressible-tier corpus entries (pre-compression)"
    )
    compressible_bytes_after: int = Field(
        ..., description="Compressible bytes in the candidate (post-compression)"
    )
    total_bytes: int = Field(..., description="Total bytes in the candidate rendition")
    setpoint: str = Field(..., description="Compression setpoint tier: lite | medium | heavy")


class CandidateRendition(BaseModel):
    """Authoring-time candidate rendition — agent-supplied, tool-validated."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Control surface name (e.g. 'AGENTS.md')")
    consumer: str = Field(..., description="Target vendor (e.g. 'codex')")
    setpoint: str = Field(..., description="Compression setpoint tier: lite | medium | heavy")
    candidate_text: str = Field(..., description="The full candidate rendition text")
    byte_evidence: ByteEvidence = Field(..., description="Per-tier byte accounting")


def candidate_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the staging path for a candidate rendition.

    Written by ``gz content compose``; never by the playback path (OBPI-22).
    Path: ``<root>/.gzkit/renditions/<surface>/<consumer>.candidate.md``
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.candidate.md"
