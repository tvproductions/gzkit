"""ExemplarProject and related models for the exemplar corpus doctrine (ADR-0.0.27).

Exposes the frozen Pydantic model for a pinned project entry in the exemplar
corpus, the vacant-cell representation, the top-level corpus wrapper, and a
loader function that reads ``data/exemplar_corpus.json``.

All models use ``ConfigDict(frozen=True, extra="forbid")`` per
``.gzkit/rules/models.md``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# Canonical SHA40 pattern — 40 lowercase hexadecimal characters.
_SHA40_PATTERN = r"^[0-9a-f]{40}$"
_SHA40_RE = re.compile(_SHA40_PATTERN)


class ExcludedPath(BaseModel):
    """One excluded path glob with its rationale.

    Used inside ``ExemplarProject.excluded_paths_with_rationale`` to make
    the reason for each exclusion explicit and auditable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    glob: str = Field(
        ...,
        min_length=1,
        description="Glob pattern excluded from measurement.",
    )
    exclusion_rationale: str = Field(
        ...,
        min_length=1,
        description=(
            "Why this path is excluded "
            "(e.g. irreducible algorithmic complexity, generated code, test fixtures)."
        ),
    )


class ExemplarProject(BaseModel):
    """A single pinned project entry in the exemplar corpus.

    Every field is required — the corpus doctrine forbids implicit defaults.
    ``commit_sha`` is validated against ``^[0-9a-f]{40}$`` so branch names,
    tags, and short hashes are rejected at construction time.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., min_length=1, description="Canonical project name.")
    canonical_url: HttpUrl = Field(..., description="Canonical repository URL.")
    commit_sha: str = Field(
        ...,
        pattern=_SHA40_PATTERN,
        description="Pinned 40-character lowercase hex commit SHA.",
    )
    archetypal_cell: int = Field(
        ...,
        ge=1,
        le=10,
        description="Archetypal cell index (1–10) from ADR-0.0.27 § Decision.",
    )
    cell_label: str = Field(
        ...,
        min_length=1,
        description="Human-readable label for the archetypal cell.",
    )
    included_paths: tuple[str, ...] = Field(
        ...,
        min_length=1,
        description="Glob patterns for paths included in measurement (at least one required).",
    )
    excluded_paths_with_rationale: tuple[ExcludedPath, ...] = Field(
        ...,
        description="Paths excluded from measurement with per-path rationale.",
    )
    path_filter_rationale: str = Field(
        ...,
        min_length=1,
        description="Overall rationale for the included/excluded path selection.",
    )
    longevity_evidence: str = Field(
        ...,
        min_length=1,
        description="Evidence the project has been active for 5+ years.",
    )
    maintenance_health_evidence: str = Field(
        ...,
        min_length=1,
        description="Evidence of healthy maintenance (e.g. recent release date).",
    )
    practitioner_reputation_citation: str = Field(
        ...,
        min_length=1,
        description="Specific citation (PEP number, book title, talk name) grounding reputation.",
    )
    pure_python_loc_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of included LOC that is pure Python (0.0–1.0).",
    )
    craftsmanship_signal_narrative: str = Field(
        ...,
        min_length=1,
        description="Narrative explaining the craftsmanship signal this project exemplifies.",
    )
    project_doctrine_fitness_narrative: str = Field(
        ...,
        min_length=1,
        description="Narrative explaining why this project fits the corpus doctrine.",
    )


class VacantCell(BaseModel):
    """Explicit representation of a vacant archetypal cell in the corpus.

    A vacant cell is one where no qualifying project was found; it must carry
    a rationale so the gap is intentional and auditable rather than silent.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    archetypal_cell: int = Field(
        ...,
        ge=1,
        le=10,
        description="Archetypal cell index (1–10) that has no qualifying project.",
    )
    vacancy_rationale: str = Field(
        ...,
        min_length=1,
        description="Why no project was found that satisfies the selection criteria for this cell.",
    )


class ExemplarCorpus(BaseModel):
    """Top-level wrapper for the pinned exemplar corpus.

    Mirrors the shape of ``data/exemplar_corpus.json`` exactly.  The JSON
    Schema at ``src/gzkit/schemas/exemplar_corpus.json`` is kept in sync
    with this model; ``gz validate --documents`` enforces the parity.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        ...,
        min_length=1,
        description="Schema version string for the corpus file format.",
    )
    corpus_revision: int = Field(
        ...,
        ge=1,
        description="Monotonically increasing revision number for the corpus content.",
    )
    projects: tuple[ExemplarProject, ...] = Field(
        ...,
        description="Ordered tuple of pinned exemplar projects.",
    )
    vacant_cells: tuple[VacantCell, ...] = Field(
        ...,
        description="Cells with no qualifying project; rationale required for each.",
    )


def load_corpus(path: Path) -> ExemplarCorpus:
    """Load and validate the exemplar corpus from ``path``.

    Reads the file as UTF-8 JSON and passes the result through
    ``ExemplarCorpus.model_validate``.  Any schema drift surfaces as a
    ``pydantic.ValidationError``.

    Args:
        path: Absolute or relative path to the corpus JSON file.

    Returns:
        A frozen ``ExemplarCorpus`` instance.

    Raises:
        pydantic.ValidationError: If the JSON does not conform to the
            ``ExemplarCorpus`` schema.
        json.JSONDecodeError: If the file is not valid JSON.
        OSError: If the file cannot be read.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    return ExemplarCorpus.model_validate(raw)


__all__ = [
    "ExcludedPath",
    "ExemplarProject",
    "VacantCell",
    "ExemplarCorpus",
    "load_corpus",
]
