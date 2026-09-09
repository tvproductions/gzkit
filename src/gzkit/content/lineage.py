"""Rendition provenance-map artifact — generate-time, never commit-time (ADR-0.35.0 Decision 5).

The ADR requires the rendered-section -> contributing-entry-ids provenance map to
be a SEPARATE generate-time artifact from ``RenditionProvenance``
(``gzkit.content.rendition_store``), which is frozen, ``extra="forbid"``, and
written at commit time (§ Alternatives O, Boundary Invariant BI-03). This module
owns that separate artifact: the ``ConsumerLineage``/``SectionLineage`` models,
the staged/committed path helpers, and the staging writer/reader.

This module does NOT populate lineage from a corpus + candidate pair — that is
the corpus candidate generator's job (a later task in this OBPI). It owns only
the shape, the paths, and the staging I/O.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SectionLineage(BaseModel):
    """Per-AGENTS.md-section-id provenance record for one rendered candidate.

    ``byte_span`` is a half-open ``[start, end)`` UTF-8 byte offset range into
    the candidate rendition text.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    owned: bool = Field(
        ..., description="Whether this section is owned by (contains bytes from) the corpus"
    )
    entry_ids: tuple[str, ...] = Field(
        default=(), description="Contributing corpus entry ids; empty for unowned sections"
    )
    byte_span: tuple[int, int] = Field(
        ..., description="Half-open UTF-8 byte offsets [start, end) into the candidate text"
    )

    @field_validator("byte_span")
    @classmethod
    def _validate_span(cls, value: tuple[int, int]) -> tuple[int, int]:
        start, end = value
        if start < 0 or end < 0:
            msg = (
                f"byte_span {value} has a negative offset — half-open UTF-8 byte "
                "offsets must both be >= 0 (ADR-0.35.0 Decision 5). Recompute the "
                "span from the candidate rendition text before staging."
            )
            raise ValueError(msg)
        if start > end:
            msg = (
                f"byte_span {value} is reversed (start > end) — half-open spans "
                "require start <= end (ADR-0.35.0 Decision 5). Recompute the span "
                "from the candidate rendition text before staging."
            )
            raise ValueError(msg)
        return value


class ConsumerLineage(BaseModel):
    """Full lineage map for one (surface, consumer) rendered candidate.

    Serializes (via ``save_candidate_lineage``) as the bare
    ``{section_id: {owned, entry_ids, byte_span}}`` map — ADR-0.35.0 Decision 5's
    literal shape — because ``surface``/``consumer`` are already encoded in the
    file path this model is stored at.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Control surface name (e.g. 'AGENTS.md')")
    consumer: str = Field(..., description="Target vendor (e.g. 'codex')")
    sections: dict[str, SectionLineage] = Field(
        ..., description="Per-AGENTS.md-section-id lineage entries"
    )

    def assert_complete_partition(self, total_bytes: int) -> None:
        """Fail closed unless the section spans disjointly and completely cover [0, total_bytes).

        Raises:
            ValueError: with three-part recovery prose (what failed / why
                forbidden / governed next step) when a gap, an overlap, or
                short coverage is found.

        """
        spans = sorted(section.byte_span for section in self.sections.values())
        cursor = 0
        for start, end in spans:
            if start > cursor:
                msg = (
                    f"lineage section partition has a gap at byte {cursor} "
                    f"(next span starts at {start}) — ADR-0.35.0 Decision 5 requires "
                    "section byte_spans to be disjoint and completely cover "
                    f"[0, {total_bytes}). Regenerate the candidate lineage with the "
                    "corpus candidate generator before staging."
                )
                raise ValueError(msg)
            if start < cursor:
                msg = (
                    f"lineage section partition overlaps at byte {start} "
                    f"(prior span ends at {cursor}) — ADR-0.35.0 Decision 5 requires "
                    "section byte_spans to be disjoint and completely cover "
                    f"[0, {total_bytes}). Regenerate the candidate lineage with the "
                    "corpus candidate generator before staging."
                )
                raise ValueError(msg)
            cursor = end
        if cursor != total_bytes:
            msg = (
                f"lineage section partition covers [0, {cursor}) but the rendition "
                f"is {total_bytes} bytes — ADR-0.35.0 Decision 5 requires the "
                f"partition to completely cover [0, {total_bytes}). Regenerate the "
                "candidate lineage with the corpus candidate generator before staging."
            )
            raise ValueError(msg)


def lineage_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the COMMITTED lineage artifact path for *(surface, consumer)*.

    Layout: ``<root>/.gzkit/renditions/<surface>/<consumer>.lineage.json``

    This task does not write here: publishing the committed lineage at the
    operator-attested commit moment is a later OBPI's scope (mirroring how
    ``rendition_path`` in ``rendition_store.py`` is committed separately from
    ``candidate_path`` in ``rendition.py``).
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.lineage.json"


def candidate_lineage_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the STAGED (candidate) lineage artifact path for *(surface, consumer)*.

    Layout: ``<root>/.gzkit/renditions/<surface>/<consumer>.candidate.lineage.json``

    Kept separate from ``lineage_path`` (the committed location) because
    ADR-0.35.0 Decision 5 requires the provenance map to be a generate-time
    artifact independent from ``RenditionProvenance`` (frozen, commit-time,
    ``extra="forbid"``): staging the candidate lineage here must never
    overwrite the committed lineage of the PRIOR rendition before the new
    candidate lands — the same staged/committed separation that
    ``candidate_path``/``rendition_path`` already enforce for rendition text.
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.candidate.lineage.json"


def save_candidate_lineage(root: Path, lineage: ConsumerLineage) -> Path:
    """Write *lineage* to its staged candidate path and return that path.

    The JSON document is the bare ``{section_id: {owned, entry_ids, byte_span}}``
    map — exactly ADR-0.35.0 Decision 5's shape — because ``surface``/``consumer``
    are already encoded in the file path; wrapping it in an envelope would
    duplicate that addressing inside the file.
    """
    path = candidate_lineage_path(root, lineage.surface, lineage.consumer)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        section_id: section.model_dump(mode="json")
        for section_id, section in lineage.sections.items()
    }
    # write_bytes, never write_text: write_text opens with newline=None and
    # newline-translates (LF -> CRLF on Windows), which would make THIS file's
    # own persisted bytes platform-dependent. REQ-0.35.0-05-08 requires
    # byte-identical lineage, and OBPI-0.35.0-07 publishes this artifact.
    # The hazard here is byte-IDENTITY, not offset corruption: `byte_span`
    # values index the CANDIDATE text, never this file, and the sibling
    # candidate writer (compose.py, Fix 3 of this OBPI's round-1 adversarial
    # review) is what guards those offsets.
    path.write_bytes((json.dumps(document, indent=2) + "\n").encode("utf-8"))
    return path


def load_candidate_lineage(root: Path, surface: str, consumer: str) -> ConsumerLineage | None:
    """Load the staged candidate lineage for *(surface, consumer)*, or ``None`` when absent.

    Absent-is-not-an-error, matching ``rendition_store.load_fingerprint``'s
    convention. ``surface``/``consumer`` are reconstructed from the arguments
    since the on-disk file carries only the bare section map.
    """
    path = candidate_lineage_path(root, surface, consumer)
    if not path.exists():
        return None
    document = json.loads(path.read_text(encoding="utf-8"))
    sections = {
        section_id: SectionLineage.model_validate(section_data)
        for section_id, section_data in document.items()
    }
    return ConsumerLineage(surface=surface, consumer=consumer, sections=sections)
