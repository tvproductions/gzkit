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

    invariant_bytes: int = Field(
        ...,
        description=(
            "POPULATION: summed text bytes of every effective invariant-tier corpus "
            "entry. Never a claim of unique rendered-byte coverage -- two entries whose "
            "texts overlap in the rendition are both counted in full here (brief "
            "§ Generation and Accounting Contract)."
        ),
    )
    compressible_bytes_before: int = Field(
        ...,
        description=(
            "POPULATION: summed text bytes of every effective compressible-tier corpus "
            "entry, pre-compression. Same overlap caveat as invariant_bytes."
        ),
    )
    compressible_bytes_after: int = Field(
        ..., description="Compressible bytes in the candidate (post-compression)"
    )
    emitted_entry_bytes: int | None = Field(
        None,
        description=(
            "RENDERED: bytes of corpus entry text the generator actually emitted into "
            "owned sections, measured during assembly. `None` on the explicit-candidate "
            "path, which assembles nothing and therefore claims no rendered partition."
        ),
    )
    generated_structural_bytes: int | None = Field(
        None,
        description=(
            "RENDERED: bytes of the headings and separators the generator itself wrote, "
            "measured during assembly. `None` on the explicit-candidate path."
        ),
    )
    carried_forward_bytes: int | None = Field(
        None,
        description=(
            "RENDERED: bytes copied byte-verbatim out of unowned sections of the prior "
            "rendition, measured during assembly. `None` on the explicit-candidate path."
        ),
    )
    total_bytes: int = Field(..., description="Total bytes in the candidate rendition")
    setpoint: str = Field(..., description="Compression setpoint tier: lite | medium | heavy")

    @property
    def rendered_bytes_total(self) -> int | None:
        """Sum of the three measured rendered contributions; ``None`` when unmeasured.

        On the generated path this equals ``total_bytes`` by construction --
        the three contributions are the lengths of disjoint byte ranges the
        generator wrote. It is deliberately NOT an identity involving
        ``invariant_bytes`` or ``compressible_bytes_before``: those are
        population statistics over corpus entry text and may exceed the
        candidate when entry texts overlap.
        """
        parts = (
            self.emitted_entry_bytes,
            self.generated_structural_bytes,
            self.carried_forward_bytes,
        )
        if any(part is None for part in parts):
            return None
        return sum(part for part in parts if part is not None)


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
