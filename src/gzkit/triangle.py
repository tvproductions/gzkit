"""Spec-test-code triangle data model for governance traceability.

Defines the REQ entity, triangle vertex/edge types, and linkage records
used by the drift detection engine (ADR-0.20.0).
"""

from __future__ import annotations

import enum
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# REQ identifier
# ---------------------------------------------------------------------------

_REQ_PATTERN = re.compile(r"^REQ-(?P<semver>\d+\.\d+\.\d+)-(?P<obpi_item>\d+)-(?P<criterion>\d+)$")


class ReqId(BaseModel):
    """Parsed REQ identifier with structured fields.

    Identifier scheme: ``REQ-<semver>-<obpi_item>-<criterion_index>``
    Example: ``REQ-0.15.0-03-02``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    semver: str = Field(..., description="SemVer portion (e.g. '0.15.0')")
    obpi_item: str = Field(..., description="OBPI item number (e.g. '03')")
    criterion_index: str = Field(..., description="Criterion index (e.g. '02')")

    @classmethod
    def parse(cls, raw: str) -> ReqId:
        """Parse a REQ identifier string into a ``ReqId``.

        Raises ``ValueError`` when *raw* does not match the canonical pattern.
        """
        m = _REQ_PATTERN.match(raw.strip())
        if m is None:
            msg = f"Invalid REQ identifier: {raw!r}"
            raise ValueError(msg)
        return cls(
            semver=m.group("semver"),
            obpi_item=m.group("obpi_item"),
            criterion_index=m.group("criterion"),
        )

    def __str__(self) -> str:
        return f"REQ-{self.semver}-{self.obpi_item}-{self.criterion_index}"


# ---------------------------------------------------------------------------
# REQ entity
# ---------------------------------------------------------------------------


class ReqStatus(enum.StrEnum):
    """Whether a REQ acceptance criterion is checked or unchecked in its brief."""

    CHECKED = "checked"
    UNCHECKED = "unchecked"


class ReqEntity(BaseModel):
    """A single requirement extracted from an OBPI brief acceptance criteria section."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: ReqId = Field(..., description="Parsed REQ identifier")
    description: str = Field(..., description="Human-readable criterion text")
    status: ReqStatus = Field(..., description="Checked or unchecked in the brief")
    parent_obpi: str = Field(..., description="Parent OBPI reference (e.g. 'OBPI-0.15.0-03')")


# ---------------------------------------------------------------------------
# Triangle vertex / edge types
# ---------------------------------------------------------------------------


class VertexType(enum.StrEnum):
    """The three vertices of the spec-test-code triangle."""

    SPEC = "spec"
    TEST = "test"
    CODE = "code"


class EdgeType(enum.StrEnum):
    """The three directed edge types linking triangle vertices."""

    COVERS = "covers"  # test → spec
    PROVES = "proves"  # test → code
    JUSTIFIES = "justifies"  # code → spec


# ---------------------------------------------------------------------------
# Vertex references
# ---------------------------------------------------------------------------


class VertexRef(BaseModel):
    """A reference to a specific vertex in the triangle graph."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    vertex_type: VertexType = Field(..., description="Which triangle vertex this refers to")
    identifier: str = Field(
        ..., description="Unique identifier (REQ id, test path, or source path)"
    )
    location: str | None = Field(None, description="Optional file path or qualified name")
    line: int | None = Field(None, description="Optional line number in the source file")

    @field_validator("identifier")
    @classmethod
    def _identifier_not_empty(cls, v: str) -> str:
        if not v.strip():
            msg = "Vertex identifier must not be empty"
            raise ValueError(msg)
        return v


# ---------------------------------------------------------------------------
# Linkage record
# ---------------------------------------------------------------------------


class LinkageRecord(BaseModel):
    """An observed relationship between two vertices in the triangle."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: VertexRef = Field(..., description="Source vertex of the directed edge")
    target: VertexRef = Field(..., description="Target vertex of the directed edge")
    edge_type: EdgeType = Field(..., description="The kind of relationship")
    evidence_path: str | None = Field(None, description="File path where the linkage was observed")
    evidence_line: int | None = Field(
        None, description="Line number where the linkage was observed"
    )
