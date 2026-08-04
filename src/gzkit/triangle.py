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

from gzkit.req_kind import NON_COVERS_KINDS, ReqKind, ReqKindValue

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
        """Return the canonical REQ identifier string."""
        return f"REQ-{self.semver}-{self.obpi_item}-{self.criterion_index}"


# ---------------------------------------------------------------------------
# REQ entity
# ---------------------------------------------------------------------------


class ReqStatus(enum.StrEnum):
    """Whether a REQ acceptance criterion is checked or unchecked in its brief."""

    CHECKED = "checked"
    UNCHECKED = "unchecked"


class ReqTestability(enum.StrEnum):
    """Whether a REQ is testable code or documentation-only.

    The pre-ADR-0.0.59 binary axis, orthogonal to `req_kind.ReqKind`'s three-kind
    taxonomy. Renamed off `ReqKind` under GHI #615: two same-named enums with
    incompatible members made importing the wrong one a silent semantic bug, and
    blocked `ReqEntity.taxonomy_kind` from being typed as the taxonomy it carries.
    """

    CODE = "code"
    DOC = "doc"


class ReqEntity(BaseModel):
    """A single requirement extracted from an OBPI brief acceptance criteria section."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: ReqId = Field(..., description="Parsed REQ identifier")
    description: str = Field(..., description="Human-readable criterion text")
    status: ReqStatus = Field(..., description="Checked or unchecked in the brief")
    parent_obpi: str = Field(..., description="Parent OBPI reference (e.g. 'OBPI-0.15.0-03')")
    kind: ReqTestability = Field(
        ReqTestability.CODE, description="Code (testable) or doc (non-testable)"
    )
    taxonomy_kind: ReqKindValue | None = Field(
        None,
        description="ADR-0.0.59 taxonomy kind (BEHAVIOR/SUPPORT/STRUCTURAL-FENCE) from inline tag",
    )
    brief_status: str | None = Field(
        None,
        description="Owning brief's frontmatter status; None when absent or unreadable",
    )


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

# Derived from `ReqKind`, never re-spelled: a kind added to the taxonomy without
# updating a hand-written alternation here would parse as untagged and silently
# default to BEHAVIOR (GHI #615). Case folding is the field validator's job.
_KIND_ALTERNATION = "|".join(re.escape(kind.value) for kind in ReqKind)

_AC_LINE_PATTERN = re.compile(
    r"^-\s+\[(?P<check>[xX ])\]\s+"
    r"\*{0,2}(?P<req_id>REQ-\d+\.\d+\.\d+-\d+-\d+)"
    # Emphasis is tolerated around the kind tag as it already is around the
    # REQ id: ADR-0.0.59 mandates the tag, not its typographic weight, and an
    # unmatched line is only warned about — so a `**[BEHAVIOR]**` brief would
    # silently under-count its REQ set (GHI #700).
    # `(?i:...)` scopes the case folding to the kind tag alone — the surrounding
    # `REQ-` literal and `[doc]` marker stay case-sensitive as they always were.
    rf"(?:\s+\*{{0,2}}\[(?P<taxonomy_kind>(?i:{_KIND_ALTERNATION}))\]\*{{0,2}})?"
    r":\*{0,2}\s*(?:\[(?P<kind>doc)\]\s+)?(?P<description>.+)$"
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


def extract_reqs_from_brief(
    content: str, parent_obpi: str, brief_status: str | None = None
) -> list[ReqEntity]:
    """Extract REQ entities from the Acceptance Criteria section of an OBPI brief.

    Parses checkbox state and description from lines like::

        - [ ] REQ-0.15.0-03-01: Some criterion
        - [x] REQ-0.15.0-03-01: Completed criterion

    ``brief_status`` stamps each REQ with its owning brief's lifecycle state so
    downstream scoping (see :func:`covers_channel_reqs`) does not need a second
    lookup. Optional: callers parsing a lone brief body may not have it.

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
        kind = ReqTestability.DOC if m.group("kind") == "doc" else ReqTestability.CODE
        # The parse path yields the domain type, not a string the reader must
        # re-normalise (GHI #615). The alternation is derived from `ReqKind`, so
        # a match is a member by construction and this cannot raise.
        raw_taxonomy = m.group("taxonomy_kind")
        taxonomy_kind = ReqKind(raw_taxonomy.upper()) if raw_taxonomy else None

        reqs.append(
            ReqEntity(
                id=req_id,
                description=m.group("description").strip(),
                status=status,
                parent_obpi=parent_obpi,
                kind=kind,
                taxonomy_kind=taxonomy_kind,
                brief_status=brief_status,
            )
        )

    reqs.sort(key=lambda e: _req_sort_key(e.id))
    return reqs


def _parse_frontmatter_field(content: str, field: str) -> str | None:
    """Extract a top-level scalar ``field`` from YAML frontmatter."""
    in_fm = False
    pattern = re.compile(rf"^{re.escape(field)}:\s*(.+)$")
    for line in content.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm:
            m = pattern.match(line)
            if m:
                return m.group(1).strip()
    return None


def _parse_frontmatter_id(content: str) -> str | None:
    """Extract the ``id`` field from YAML frontmatter."""
    return _parse_frontmatter_field(content, "id")


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
        brief_status = _parse_frontmatter_field(content, "status")

        for req in extract_reqs_from_brief(content, parent_obpi, brief_status):
            discovered.append(DiscoveredReq(entity=req, source_path=str(md_file)))

    discovered.sort(key=lambda d: _req_sort_key(d.entity.id))
    return discovered


# Kinds whose proof channel is NOT a `@covers` test (ADR-0.0.59). SUPPORT proves
# via a path-citing ledger event plus its structural validator; STRUCTURAL-FENCE
# proves via the parent ADR's `## Boundary Invariants` entry. Counting either as
# "a REQ with no test" reports the taxonomy working as designed as drift.
# Derived from the proof-channel map, not re-spelled: a kind whose channel is not
# `TEST_COVERS` excludes itself here the moment it is added (GHI #615).
_NON_COVERS_TAXONOMY_KINDS: frozenset[ReqKind] = NON_COVERS_KINDS

# Briefs whose work is RETIRED, which is narrower than sealed. `Completed`,
# `attested_completed`, and `Validated` are terminal but their REQs were
# attested as covered -- a covering test disappearing afterwards is genuine
# regression drift and must still report. Only these four owe nothing further,
# so `is_terminal_brief_status` is deliberately NOT the predicate here.
# Membership is pinned against BRIEF_TERMINAL_STATUSES by
# tests/governance/test_drift_proof_channel_scope.py so an upstream rename
# fails loudly instead of silently un-scoping a status.
_RETIRED_BRIEF_STATUSES: frozenset[str] = frozenset(
    {"Abandoned", "Withdrawn", "Superseded", "archived"}
)

_RETIRED_BRIEF_STATUSES_FOLDED: frozenset[str] = frozenset(
    status.casefold() for status in _RETIRED_BRIEF_STATUSES
)


def _is_retired_brief_status(status: str) -> bool:
    """Return True when a brief's work will never be delivered."""
    return status.strip().strip('"').strip("'").casefold() in _RETIRED_BRIEF_STATUSES_FOLDED


def covers_channel_reqs(reqs: list[ReqEntity]) -> list[ReqEntity]:
    """Return the REQs a `@covers` test is the right proof for (GHI #729).

    Drift's unlinked-spec set answers "which REQ still owes a covering test",
    so a REQ only belongs in it when a test is what would discharge it. Three
    exclusions, each reading a fact already on the record:

    * `taxonomy_kind` in SUPPORT / STRUCTURAL-FENCE — proven through another
      channel entirely (`.claude/rules/tests.md` § Proof-channel matrix).
    * `kind` is `ReqTestability.DOC` — the legacy axis for non-testable REQs.
    * the owning brief is RETIRED — `Abandoned` / `Withdrawn` / `Superseded` /
      `archived`. Note this is narrower than sealed: a `Completed` brief still
      owes its coverage, so losing a test there is regression drift worth
      reporting.

    An UNTAGGED REQ stays in scope. Most of the corpus predates ADR-0.0.59, and
    a missing tag is unknown kind, never an exemption — inferring one would let
    the largest segment silently exempt itself.

    This scopes the UNLINKED arm of drift only. Orphan detection must still see
    every declared REQ, or a test legitimately citing a SUPPORT REQ reads as a
    phantom orphan — which is why :func:`detect_drift` applies this internally
    rather than callers pre-filtering what they hand it.
    """
    in_scope: list[ReqEntity] = []
    for entity in reqs:
        if entity.kind is ReqTestability.DOC:
            continue
        if entity.taxonomy_kind in _NON_COVERS_TAXONOMY_KINDS:
            continue
        if entity.brief_status and _is_retired_brief_status(entity.brief_status):
            continue
        in_scope.append(entity)
    return in_scope


# ---------------------------------------------------------------------------
# Drift detection engine (OBPI-0.20.0-03)
# ---------------------------------------------------------------------------


# The corpus's reserved "this REQ does not exist" sentinel. Tests that prove
# @covers REJECTS an unknown REQ must cite an unknown REQ, so the citation is
# the fixture, not a stale pointer. Used across test_traceability,
# test_advances_decorator, test_ontology_source, and test_req_coverage.
_RESERVED_FIXTURE_SEMVER = "9.9.9"


def _is_reserved_fixture_req(req_id_str: str) -> bool:
    """Return True for the reserved negative-control REQ namespace."""
    try:
        return ReqId.parse(req_id_str).semver == _RESERVED_FIXTURE_SEMVER
    except ValueError:
        return False


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


class SourceSubgraphView(BaseModel):
    """The typed source-subgraph projection ``detect_drift`` reads from (ADR-0.32.0).

    The spec-test-code linkages, viewed as the source subgraph: which REQs are
    known, which are covered, which REQ ids tests target, and which code ids are
    justified. ``detect_drift`` is re-expressed as a VIEW over this projection so
    the drift model and the ontology source subgraph share one shape — behavior
    preserved (OBPI-0.32.0-07 REQ-06; golden-fixture parity pinned).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    known_req_ids: frozenset[str] = Field(..., description="REQ ids declared in briefs")
    covers_channel_req_ids: frozenset[str] = Field(
        frozenset(),
        description="Known REQs a @covers test is the right proof for (GHI #729)",
    )
    covered_req_ids: frozenset[str] = Field(..., description="Known REQs with a COVERS edge")
    test_target_req_ids: frozenset[str] = Field(..., description="All COVERS-edge target REQ ids")
    justified_code_ids: frozenset[str] = Field(..., description="Code ids with a JUSTIFIES edge")


def _project_source_subgraph(
    reqs: list[ReqEntity], linkage_records: list[LinkageRecord]
) -> SourceSubgraphView:
    """Project reqs + linkage records into the typed source-subgraph view."""
    known_req_ids = {str(req.id) for req in reqs}
    covers_channel_ids = {str(req.id) for req in covers_channel_reqs(reqs)}

    covered_req_ids: set[str] = set()
    test_target_req_ids: set[str] = set()
    justified_code_ids: set[str] = set()
    for record in linkage_records:
        if record.edge_type == EdgeType.COVERS:
            target_id = record.target.identifier
            test_target_req_ids.add(target_id)
            if target_id in known_req_ids:
                covered_req_ids.add(target_id)
        elif record.edge_type == EdgeType.JUSTIFIES:
            justified_code_ids.add(record.source.identifier)

    return SourceSubgraphView(
        known_req_ids=frozenset(known_req_ids),
        covers_channel_req_ids=frozenset(covers_channel_ids),
        covered_req_ids=frozenset(covered_req_ids),
        test_target_req_ids=frozenset(test_target_req_ids),
        justified_code_ids=frozenset(justified_code_ids),
    )


def detect_drift(
    reqs: list[ReqEntity],
    linkage_records: list[LinkageRecord],
    changed_code_vertices: list[VertexRef],
    scan_timestamp: str,
) -> DriftReport:
    """Compute drift across the spec-test-code triangle.

    Re-expressed as a VIEW over the typed source subgraph (``SourceSubgraphView``)
    so the drift model and the ontology source subgraph share one shape
    (ADR-0.32.0, OBPI-0.32.0-07 REQ-06). Behavior is preserved exactly: pure
    computation — no I/O, deterministic, results sorted by identifier (semantic
    version order for REQs, alphabetical for code).
    """
    view = _project_source_subgraph(reqs, linkage_records)

    unlinked = sorted(view.covers_channel_req_ids - view.covered_req_ids, key=_req_id_sort_key)
    orphans = sorted(
        (
            req_id
            for req_id in view.test_target_req_ids - view.known_req_ids
            if not _is_reserved_fixture_req(req_id)
        ),
        key=_req_id_sort_key,
    )
    unjustified = sorted(
        v.identifier for v in changed_code_vertices if v.identifier not in view.justified_code_ids
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
