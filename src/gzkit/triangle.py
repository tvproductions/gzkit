"""Spec-test-code triangle data model for governance traceability.

Defines the REQ entity, triangle vertex/edge types, and linkage records
used by the drift detection engine (ADR-0.20.0).
"""

from __future__ import annotations

import enum
import logging
import pathlib
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)

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


# ---------------------------------------------------------------------------
# Brief REQ extraction (OBPI-0.20.0-02)
# ---------------------------------------------------------------------------

_AC_LINE_PATTERN = re.compile(
    r"^-\s+\[(?P<check>[xX ])\]\s+"
    r"(?P<req_id>REQ-\d+\.\d+\.\d+-\d+-\d+)"
    r":\s*(?P<description>.+)$"
)


class DiscoveredReq(BaseModel):
    """A REQ entity paired with the source file path where it was found."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entity: ReqEntity = Field(..., description="The discovered REQ entity")
    source_path: str = Field(..., description="File path where the REQ was found")


def _req_sort_key(req_id: ReqId) -> tuple[tuple[int, ...], int, int]:
    """Generate a sort key for semantic version ordering."""
    semver_parts = tuple(int(p) for p in req_id.semver.split("."))
    return (semver_parts, int(req_id.obpi_item), int(req_id.criterion_index))


def extract_reqs_from_brief(content: str, parent_obpi: str) -> list[ReqEntity]:
    """Extract REQ entities from the Acceptance Criteria section of an OBPI brief.

    Parses checkbox state and description from lines like::

        - [ ] REQ-0.15.0-03-01: Some criterion
        - [x] REQ-0.15.0-03-01: Completed criterion

    Malformed REQ lines are logged as warnings and skipped.
    Results are sorted by REQ identifier (semantic version ordering).
    """
    in_section = False
    reqs: list[ReqEntity] = []

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("## Acceptance Criteria"):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break

        if not in_section or not stripped.startswith("- ["):
            continue

        m = _AC_LINE_PATTERN.match(stripped)
        if m is None:
            if "REQ-" in stripped:
                logger.warning("Malformed REQ line (skipped): %s", stripped)
            continue

        raw_req_id = m.group("req_id")
        try:
            req_id = ReqId.parse(raw_req_id)
        except ValueError:
            logger.warning("Malformed REQ identifier (skipped): %s", raw_req_id)
            continue

        status = ReqStatus.CHECKED if m.group("check").lower() == "x" else ReqStatus.UNCHECKED

        reqs.append(
            ReqEntity(
                id=req_id,
                description=m.group("description").strip(),
                status=status,
                parent_obpi=parent_obpi,
            )
        )

    reqs.sort(key=lambda e: _req_sort_key(e.id))
    return reqs


def _parse_frontmatter_id(content: str) -> str | None:
    """Extract the ``id`` field from YAML frontmatter."""
    in_fm = False
    for line in content.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm:
            m = re.match(r"^id:\s*(.+)$", line)
            if m:
                return m.group(1).strip()
    return None


def _extract_obpi_short_id(frontmatter_id: str) -> str | None:
    """Extract short OBPI ID (e.g. ``OBPI-0.20.0-02``) from a full frontmatter id."""
    m = re.match(r"(OBPI-\d+\.\d+\.\d+-\d+)", frontmatter_id)
    return m.group(1) if m else None


def scan_briefs(directory: pathlib.Path) -> list[DiscoveredReq]:
    """Scan a directory tree for OBPI brief files and extract all REQ entities.

    Returns discovered REQs with their source file paths, sorted by REQ identifier
    (semantic version ordering).
    """

    discovered: list[DiscoveredReq] = []

    for md_file in sorted(pathlib.Path(directory).rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")

        fm_id = _parse_frontmatter_id(content)
        if fm_id is None or not fm_id.startswith("OBPI-"):
            continue

        parent_obpi = _extract_obpi_short_id(fm_id) or fm_id

        for req in extract_reqs_from_brief(content, parent_obpi):
            discovered.append(DiscoveredReq(entity=req, source_path=str(md_file)))

    discovered.sort(key=lambda d: _req_sort_key(d.entity.id))
    return discovered


# ---------------------------------------------------------------------------
# Drift detection engine (OBPI-0.20.0-03)
# ---------------------------------------------------------------------------


def _req_id_sort_key(req_id_str: str) -> tuple[tuple[int, ...], int, int]:
    """Sort key for REQ ID strings using semantic version ordering."""
    try:
        parsed = ReqId.parse(req_id_str)
        return _req_sort_key(parsed)
    except ValueError:
        return ((999, 999, 999), 999, 999)


class DriftSummary(BaseModel):
    """Counts of each drift category."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    unlinked_spec_count: int = Field(..., description="REQs with no test coverage")
    orphan_test_count: int = Field(..., description="Test linkages referencing non-existent REQs")
    unjustified_code_change_count: int = Field(
        ..., description="Code changes without spec justification"
    )
    total_drift_count: int = Field(..., description="Sum of all drift findings")


class DriftReport(BaseModel):
    """Result of drift detection across the spec-test-code triangle."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    unlinked_specs: list[str] = Field(..., description="REQ IDs with no test coverage")
    orphan_tests: list[str] = Field(
        ..., description="Test linkage target REQ IDs not found in briefs"
    )
    unjustified_code_changes: list[str] = Field(
        ..., description="Changed code identifiers without justifies edges"
    )
    summary: DriftSummary = Field(..., description="Counts of each drift category")
    scan_timestamp: str = Field(..., description="ISO-8601 timestamp of the scan")


def detect_drift(
    reqs: list[ReqEntity],
    linkage_records: list[LinkageRecord],
    changed_code_vertices: list[VertexRef],
    scan_timestamp: str,
) -> DriftReport:
    """Compute drift across the spec-test-code triangle.

    Pure computation — no I/O. Deterministic: same inputs always produce same outputs.
    Results sorted by identifier (semantic version order for REQs, alphabetical for code).
    """
    known_req_ids = {str(req.id) for req in reqs}

    covered_req_ids: set[str] = set()
    test_target_req_ids: set[str] = set()
    for record in linkage_records:
        if record.edge_type == EdgeType.COVERS:
            target_id = record.target.identifier
            test_target_req_ids.add(target_id)
            if target_id in known_req_ids:
                covered_req_ids.add(target_id)

    unlinked = sorted(known_req_ids - covered_req_ids, key=_req_id_sort_key)
    orphans = sorted(test_target_req_ids - known_req_ids, key=_req_id_sort_key)

    justified_code_ids: set[str] = set()
    for record in linkage_records:
        if record.edge_type == EdgeType.JUSTIFIES:
            justified_code_ids.add(record.source.identifier)

    unjustified = sorted(
        v.identifier for v in changed_code_vertices if v.identifier not in justified_code_ids
    )

    return DriftReport(
        unlinked_specs=unlinked,
        orphan_tests=orphans,
        unjustified_code_changes=unjustified,
        summary=DriftSummary(
            unlinked_spec_count=len(unlinked),
            orphan_test_count=len(orphans),
            unjustified_code_change_count=len(unjustified),
            total_drift_count=len(unlinked) + len(orphans) + len(unjustified),
        ),
        scan_timestamp=scan_timestamp,
    )
