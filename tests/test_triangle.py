"""Tests for the spec-test-code triangle data model.

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-01-req-entity-and-triangle-data-model
@covers OBPI-0.20.0-02-brief-req-extraction
@covers OBPI-0.20.0-03-drift-detection-engine
@covers OBPI-0.20.0-05-advisory-gate-integration
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.traceability import covers
from gzkit.triangle import (
    DiscoveredReq,
    DriftReport,
    DriftSummary,
    EdgeType,
    LinkageRecord,
    ReqEntity,
    ReqId,
    ReqStatus,
    VertexRef,
    VertexType,
    detect_drift,
    extract_reqs_from_brief,
    scan_briefs,
)


class TestReqIdParsing(unittest.TestCase):
    """@covers REQ-0.20.0-01-01
    @covers REQ-0.20.0-01-02
    """

    @covers("REQ-0.20.0-01-01")
    def test_parse_valid_req_id(self) -> None:
        """REQ-0.20.0-01-01: Parse a valid REQ string into structured fields."""
        req = ReqId.parse("REQ-0.15.0-03-02")
        self.assertEqual(req.semver, "0.15.0")
        self.assertEqual(req.obpi_item, "03")
        self.assertEqual(req.criterion_index, "02")

    def test_parse_single_digit_components(self) -> None:
        req = ReqId.parse("REQ-1.0.0-1-1")
        self.assertEqual(req.semver, "1.0.0")
        self.assertEqual(req.obpi_item, "1")
        self.assertEqual(req.criterion_index, "1")

    def test_parse_strips_whitespace(self) -> None:
        req = ReqId.parse("  REQ-0.20.0-01-04  ")
        self.assertEqual(req.semver, "0.20.0")

    def test_str_roundtrip(self) -> None:
        raw = "REQ-0.15.0-03-02"
        req = ReqId.parse(raw)
        self.assertEqual(str(req), raw)

    def test_frozen_immutability(self) -> None:
        req = ReqId.parse("REQ-0.15.0-03-02")
        with self.assertRaises(ValidationError):
            req.semver = "1.0.0"  # type: ignore[misc]

    def test_extra_fields_forbidden(self) -> None:
        with self.assertRaises(ValidationError):
            ReqId(semver="0.1.0", obpi_item="01", criterion_index="01", extra="bad")  # type: ignore[call-arg]


class TestReqIdParsingInvalid(unittest.TestCase):
    """@covers REQ-0.20.0-01-02"""

    @covers("REQ-0.20.0-01-02")
    def test_parse_invalid_prefix(self) -> None:
        """REQ-0.20.0-01-02: Invalid REQ string raises ValueError."""
        with self.assertRaises(ValueError, msg="Invalid REQ identifier"):
            ReqId.parse("REQ-invalid")

    def test_parse_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            ReqId.parse("")

    def test_parse_missing_criterion(self) -> None:
        with self.assertRaises(ValueError):
            ReqId.parse("REQ-0.15.0-03")

    def test_parse_wrong_prefix(self) -> None:
        with self.assertRaises(ValueError):
            ReqId.parse("OBPI-0.15.0-03-02")

    def test_parse_non_numeric_semver(self) -> None:
        with self.assertRaises(ValueError):
            ReqId.parse("REQ-abc-03-02")


class TestReqEntity(unittest.TestCase):
    """@covers REQ-0.20.0-01-01
    @covers REQ-0.20.0-01-02
    """

    def test_create_checked_req(self) -> None:
        req_id = ReqId.parse("REQ-0.15.0-03-02")
        entity = ReqEntity(
            id=req_id,
            description="Given a valid input, returns correct output",
            status=ReqStatus.CHECKED,
            parent_obpi="OBPI-0.15.0-03",
        )
        self.assertEqual(entity.status, ReqStatus.CHECKED)
        self.assertEqual(entity.parent_obpi, "OBPI-0.15.0-03")

    def test_create_unchecked_req(self) -> None:
        req_id = ReqId.parse("REQ-0.20.0-01-01")
        entity = ReqEntity(
            id=req_id,
            description="Pending criterion",
            status=ReqStatus.UNCHECKED,
            parent_obpi="OBPI-0.20.0-01",
        )
        self.assertEqual(entity.status, ReqStatus.UNCHECKED)

    def test_frozen_immutability(self) -> None:
        req_id = ReqId.parse("REQ-0.15.0-03-02")
        entity = ReqEntity(
            id=req_id,
            description="Test",
            status=ReqStatus.CHECKED,
            parent_obpi="OBPI-0.15.0-03",
        )
        with self.assertRaises(ValidationError):
            entity.status = ReqStatus.UNCHECKED  # type: ignore[misc]


class TestVertexTypes(unittest.TestCase):
    """@covers REQ-0.20.0-01-03"""

    def test_three_vertex_types_exist(self) -> None:
        """Exactly Spec, Test, Code vertices."""
        members = {m.value for m in VertexType}
        self.assertEqual(members, {"spec", "test", "code"})

    def test_vertex_type_count(self) -> None:
        self.assertEqual(len(VertexType), 3)


class TestEdgeTypes(unittest.TestCase):
    """@covers REQ-0.20.0-01-04"""

    @covers("REQ-0.20.0-01-04")
    def test_three_edge_types_exist(self) -> None:
        """REQ-0.20.0-01-04: Exactly covers, proves, justifies edges."""
        members = {m.value for m in EdgeType}
        self.assertEqual(members, {"covers", "proves", "justifies"})

    def test_edge_type_count(self) -> None:
        self.assertEqual(len(EdgeType), 3)


class TestVertexRef(unittest.TestCase):
    """@covers REQ-0.20.0-01-03"""

    def test_create_spec_vertex(self) -> None:
        ref = VertexRef(
            vertex_type=VertexType.SPEC,
            identifier="REQ-0.15.0-03-02",
        )
        self.assertEqual(ref.vertex_type, VertexType.SPEC)
        self.assertIsNone(ref.location)
        self.assertIsNone(ref.line)

    def test_create_test_vertex_with_location(self) -> None:
        ref = VertexRef(
            vertex_type=VertexType.TEST,
            identifier="tests.test_triangle.TestReqIdParsing.test_parse_valid_req_id",
            location="tests/test_triangle.py",
            line=30,
        )
        self.assertEqual(ref.vertex_type, VertexType.TEST)
        self.assertEqual(ref.line, 30)

    def test_create_code_vertex(self) -> None:
        ref = VertexRef(
            vertex_type=VertexType.CODE,
            identifier="gzkit.triangle.ReqId.parse",
            location="src/gzkit/triangle.py",
        )
        self.assertEqual(ref.vertex_type, VertexType.CODE)

    def test_empty_identifier_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            VertexRef(vertex_type=VertexType.SPEC, identifier="")

    def test_whitespace_only_identifier_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            VertexRef(vertex_type=VertexType.SPEC, identifier="   ")


class TestLinkageRecord(unittest.TestCase):
    """@covers REQ-0.20.0-01-03
    @covers REQ-0.20.0-01-04
    """

    def _make_linkage(self) -> LinkageRecord:
        return LinkageRecord(
            source=VertexRef(
                vertex_type=VertexType.TEST,
                identifier="tests.test_triangle.TestReqIdParsing.test_parse_valid_req_id",
                location="tests/test_triangle.py",
                line=30,
            ),
            target=VertexRef(
                vertex_type=VertexType.SPEC,
                identifier="REQ-0.15.0-03-02",
            ),
            edge_type=EdgeType.COVERS,
            evidence_path="tests/test_triangle.py",
            evidence_line=30,
        )

    def test_create_covers_linkage(self) -> None:
        record = self._make_linkage()
        self.assertEqual(record.edge_type, EdgeType.COVERS)
        self.assertEqual(record.source.vertex_type, VertexType.TEST)
        self.assertEqual(record.target.vertex_type, VertexType.SPEC)

    @covers("REQ-0.20.0-01-03")
    def test_json_serialization_roundtrip(self) -> None:
        """REQ-0.20.0-01-03: Serialize to JSON and back, preserving all fields."""
        original = self._make_linkage()
        json_str = original.model_dump_json()
        restored = LinkageRecord.model_validate_json(json_str)
        self.assertEqual(original, restored)

    def test_dict_serialization_roundtrip(self) -> None:
        original = self._make_linkage()
        data = original.model_dump()
        restored = LinkageRecord.model_validate(data)
        self.assertEqual(original, restored)

    def test_json_output_is_valid_json(self) -> None:
        record = self._make_linkage()
        parsed = json.loads(record.model_dump_json())
        self.assertIn("source", parsed)
        self.assertIn("target", parsed)
        self.assertIn("edge_type", parsed)

    def test_frozen_immutability(self) -> None:
        record = self._make_linkage()
        with self.assertRaises(ValidationError):
            record.edge_type = EdgeType.PROVES  # type: ignore[misc]

    def test_linkage_without_evidence(self) -> None:
        record = LinkageRecord(
            source=VertexRef(vertex_type=VertexType.CODE, identifier="gzkit.triangle"),
            target=VertexRef(vertex_type=VertexType.SPEC, identifier="REQ-0.20.0-01-01"),
            edge_type=EdgeType.JUSTIFIES,
        )
        self.assertIsNone(record.evidence_path)
        self.assertIsNone(record.evidence_line)


class TestReqStatusEnum(unittest.TestCase):
    """@covers REQ-0.20.0-01-02"""

    def test_checked_value(self) -> None:
        self.assertEqual(ReqStatus.CHECKED.value, "checked")

    def test_unchecked_value(self) -> None:
        self.assertEqual(ReqStatus.UNCHECKED.value, "unchecked")

    def test_exactly_two_members(self) -> None:
        self.assertEqual(len(ReqStatus), 2)


# ---------------------------------------------------------------------------
# OBPI-0.20.0-02: Brief REQ extraction tests
# ---------------------------------------------------------------------------

SAMPLE_BRIEF = """\
---
id: OBPI-0.15.0-03-some-feature
parent: ADR-0.15.0
item: 3
lane: Lite
status: Accepted
---

# OBPI-0.15.0-03: Some Feature

## Acceptance Criteria

- [ ] REQ-0.15.0-03-01: Given a valid input, returns correct output.
- [x] REQ-0.15.0-03-02: Given an invalid input, raises a clear error.
- [ ] REQ-0.15.0-03-03: Given edge case, handles gracefully.

## Evidence

```text
# Paste test output here
```
"""


class TestExtractReqsFromBrief(unittest.TestCase):
    """@covers REQ-0.20.0-02-01
    @covers REQ-0.20.0-02-02
    @covers REQ-0.20.0-02-03
    """

    @covers("REQ-0.20.0-02-01")
    def test_extract_unchecked_req(self) -> None:
        """REQ-0.20.0-02-01: Unchecked checkbox produces status=unchecked."""
        reqs = extract_reqs_from_brief(SAMPLE_BRIEF, "OBPI-0.15.0-03")
        unchecked = [r for r in reqs if str(r.id) == "REQ-0.15.0-03-01"]
        self.assertEqual(len(unchecked), 1)
        self.assertEqual(unchecked[0].status, ReqStatus.UNCHECKED)
        self.assertEqual(
            unchecked[0].description,
            "Given a valid input, returns correct output.",
        )

    @covers("REQ-0.20.0-02-02")
    def test_extract_checked_req(self) -> None:
        """REQ-0.20.0-02-02: Checked checkbox produces status=checked."""
        reqs = extract_reqs_from_brief(SAMPLE_BRIEF, "OBPI-0.15.0-03")
        checked = [r for r in reqs if str(r.id) == "REQ-0.15.0-03-02"]
        self.assertEqual(len(checked), 1)
        self.assertEqual(checked[0].status, ReqStatus.CHECKED)

    def test_extract_description(self) -> None:
        reqs = extract_reqs_from_brief(SAMPLE_BRIEF, "OBPI-0.15.0-03")
        self.assertEqual(len(reqs), 3)
        self.assertEqual(
            reqs[1].description,
            "Given an invalid input, raises a clear error.",
        )

    def test_extract_parent_obpi(self) -> None:
        reqs = extract_reqs_from_brief(SAMPLE_BRIEF, "OBPI-0.15.0-03")
        for req in reqs:
            self.assertEqual(req.parent_obpi, "OBPI-0.15.0-03")

    def test_extract_sorted_by_req_id(self) -> None:
        reqs = extract_reqs_from_brief(SAMPLE_BRIEF, "OBPI-0.15.0-03")
        ids = [str(r.id) for r in reqs]
        self.assertEqual(
            ids,
            [
                "REQ-0.15.0-03-01",
                "REQ-0.15.0-03-02",
                "REQ-0.15.0-03-03",
            ],
        )

    def test_empty_content_returns_empty(self) -> None:
        reqs = extract_reqs_from_brief("", "OBPI-0.1.0-01")
        self.assertEqual(reqs, [])

    def test_no_acceptance_criteria_section(self) -> None:
        content = "# Some Doc\n\nNo criteria here.\n"
        reqs = extract_reqs_from_brief(content, "OBPI-0.1.0-01")
        self.assertEqual(reqs, [])

    def test_stops_at_next_section(self) -> None:
        content = """\
## Acceptance Criteria

- [ ] REQ-0.1.0-01-01: First criterion.

## Evidence

- [ ] REQ-0.1.0-01-02: Should not be extracted.
"""
        reqs = extract_reqs_from_brief(content, "OBPI-0.1.0-01")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(str(reqs[0].id), "REQ-0.1.0-01-01")

    def test_uppercase_x_checkbox(self) -> None:
        content = """\
## Acceptance Criteria

- [X] REQ-0.1.0-01-01: Uppercase X checkbox.
"""
        reqs = extract_reqs_from_brief(content, "OBPI-0.1.0-01")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].status, ReqStatus.CHECKED)


class TestExtractMalformedLines(unittest.TestCase):
    """@covers REQ-0.20.0-02-04"""

    @covers("REQ-0.20.0-02-04")
    def test_malformed_req_id_logged_and_skipped(self) -> None:
        """REQ-0.20.0-02-04: Malformed REQ line logs warning, skips."""
        content = """\
## Acceptance Criteria

- [ ] REQ-bad: This should be skipped.
- [ ] REQ-0.15.0-03-01: Valid line.
"""
        with self.assertLogs("gzkit.triangle", level="WARNING") as cm:
            reqs = extract_reqs_from_brief(content, "OBPI-0.15.0-03")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(str(reqs[0].id), "REQ-0.15.0-03-01")
        self.assertTrue(any("Malformed REQ line" in msg for msg in cm.output))

    def test_non_req_checkbox_silently_skipped(self) -> None:
        content = """\
## Acceptance Criteria

- [ ] Gate 1 (ADR): Intent recorded
- [ ] REQ-0.1.0-01-01: Valid line.
"""
        reqs = extract_reqs_from_brief(content, "OBPI-0.1.0-01")
        self.assertEqual(len(reqs), 1)


def _make_brief(obpi_id: str, reqs: list[tuple[str, bool, str]]) -> str:
    """Create a brief markdown string with given REQs."""
    lines = [
        "---",
        f"id: {obpi_id}",
        "parent: ADR-test",
        "item: 1",
        "lane: Lite",
        "status: Accepted",
        "---",
        "",
        f"# {obpi_id}",
        "",
        "## Acceptance Criteria",
        "",
    ]
    for req_id, checked, desc in reqs:
        check = "x" if checked else " "
        lines.append(f"- [{check}] {req_id}: {desc}")
    return "\n".join(lines) + "\n"


class TestScanBriefs(unittest.TestCase):
    """@covers REQ-0.20.0-02-03
    @covers REQ-0.20.0-02-01
    """

    @covers("REQ-0.20.0-02-03")
    def test_scan_three_briefs_twelve_reqs(self) -> None:
        """REQ-0.20.0-02-03: Scan 3 briefs with 12 total REQs."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            obpis_dir = tmp_dir / "obpis"
            obpis_dir.mkdir()

            (obpis_dir / "OBPI-0.15.0-01-feature-a.md").write_text(
                _make_brief(
                    "OBPI-0.15.0-01-feature-a",
                    [
                        ("REQ-0.15.0-01-01", False, "Criterion A1"),
                        ("REQ-0.15.0-01-02", True, "Criterion A2"),
                        ("REQ-0.15.0-01-03", False, "Criterion A3"),
                        ("REQ-0.15.0-01-04", True, "Criterion A4"),
                    ],
                ),
                encoding="utf-8",
            )

            (obpis_dir / "OBPI-0.15.0-02-feature-b.md").write_text(
                _make_brief(
                    "OBPI-0.15.0-02-feature-b",
                    [
                        ("REQ-0.15.0-02-01", True, "Criterion B1"),
                        ("REQ-0.15.0-02-02", False, "Criterion B2"),
                        ("REQ-0.15.0-02-03", True, "Criterion B3"),
                        ("REQ-0.15.0-02-04", False, "Criterion B4"),
                    ],
                ),
                encoding="utf-8",
            )

            (obpis_dir / "OBPI-0.15.0-03-feature-c.md").write_text(
                _make_brief(
                    "OBPI-0.15.0-03-feature-c",
                    [
                        ("REQ-0.15.0-03-01", False, "Criterion C1"),
                        ("REQ-0.15.0-03-02", True, "Criterion C2"),
                        ("REQ-0.15.0-03-03", False, "Criterion C3"),
                        ("REQ-0.15.0-03-04", True, "Criterion C4"),
                    ],
                ),
                encoding="utf-8",
            )

            results = scan_briefs(tmp_dir)

        self.assertEqual(len(results), 12)
        source_paths = {r.source_path for r in results}
        self.assertEqual(len(source_paths), 3)
        req_ids = [str(r.entity.id) for r in results]
        self.assertEqual(len(set(req_ids)), 12)

    def test_scan_returns_correct_source_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            brief_file = tmp_dir / "OBPI-0.1.0-01-test.md"
            brief_file.write_text(
                _make_brief(
                    "OBPI-0.1.0-01-test",
                    [
                        ("REQ-0.1.0-01-01", False, "Test criterion"),
                    ],
                ),
                encoding="utf-8",
            )

            results = scan_briefs(tmp_dir)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source_path, str(brief_file))

    def test_scan_sorted_across_briefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)

            (tmp_dir / "OBPI-0.2.0-01-z.md").write_text(
                _make_brief(
                    "OBPI-0.2.0-01-z",
                    [
                        ("REQ-0.2.0-01-01", False, "Later version"),
                    ],
                ),
                encoding="utf-8",
            )
            (tmp_dir / "OBPI-0.1.0-01-a.md").write_text(
                _make_brief(
                    "OBPI-0.1.0-01-a",
                    [
                        ("REQ-0.1.0-01-01", False, "Earlier version"),
                    ],
                ),
                encoding="utf-8",
            )

            results = scan_briefs(tmp_dir)

        self.assertEqual(len(results), 2)
        self.assertEqual(str(results[0].entity.id), "REQ-0.1.0-01-01")
        self.assertEqual(str(results[1].entity.id), "REQ-0.2.0-01-01")

    def test_scan_skips_non_obpi_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            (tmp_dir / "README.md").write_text("# Not an OBPI\n", encoding="utf-8")
            (tmp_dir / "ADR-0.1.0-test.md").write_text(
                "---\nid: ADR-0.1.0-test\n---\n# ADR\n",
                encoding="utf-8",
            )

            results = scan_briefs(tmp_dir)

        self.assertEqual(results, [])

    def test_scan_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            results = scan_briefs(Path(tmp))
        self.assertEqual(results, [])


class TestDiscoveredReqModel(unittest.TestCase):
    """@covers REQ-0.20.0-02-01"""

    def test_discovered_req_immutable(self) -> None:
        req = DiscoveredReq(
            entity=ReqEntity(
                id=ReqId.parse("REQ-0.1.0-01-01"),
                description="Test",
                status=ReqStatus.UNCHECKED,
                parent_obpi="OBPI-0.1.0-01",
            ),
            source_path="test.md",
        )
        with self.assertRaises(ValidationError):
            req.source_path = "other.md"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# OBPI-0.20.0-03: Drift detection engine tests
# ---------------------------------------------------------------------------

FIXED_TIMESTAMP = "2026-03-27T00:00:00Z"


def _make_req(semver: str, obpi: str, criterion: str) -> ReqEntity:
    """Helper to create a ReqEntity for drift tests."""
    return ReqEntity(
        id=ReqId(semver=semver, obpi_item=obpi, criterion_index=criterion),
        description=f"Criterion {criterion}",
        status=ReqStatus.UNCHECKED,
        parent_obpi=f"OBPI-{semver}-{obpi}",
    )


def _make_covers_linkage(req_id_str: str) -> LinkageRecord:
    """Helper to create a COVERS linkage record."""
    return LinkageRecord(
        source=VertexRef(vertex_type=VertexType.TEST, identifier=f"test_for_{req_id_str}"),
        target=VertexRef(vertex_type=VertexType.SPEC, identifier=req_id_str),
        edge_type=EdgeType.COVERS,
    )


def _make_justifies_linkage(code_id: str, req_id_str: str) -> LinkageRecord:
    """Helper to create a JUSTIFIES linkage record."""
    return LinkageRecord(
        source=VertexRef(vertex_type=VertexType.CODE, identifier=code_id),
        target=VertexRef(vertex_type=VertexType.SPEC, identifier=req_id_str),
        edge_type=EdgeType.JUSTIFIES,
    )


def _make_code_vertex(identifier: str) -> VertexRef:
    """Helper to create a changed code vertex."""
    return VertexRef(vertex_type=VertexType.CODE, identifier=identifier)


class TestDriftDetectionNoDrift(unittest.TestCase):
    """@covers REQ-0.20.0-03-01"""

    @covers("REQ-0.20.0-03-01")
    def test_all_reqs_covered_no_drift(self) -> None:
        """REQ-0.20.0-03-01: 5 REQs, 5 matching linkages, no drift."""
        reqs = [_make_req("0.15.0", "01", f"0{i}") for i in range(1, 6)]
        linkages = [_make_covers_linkage(str(r.id)) for r in reqs]

        report = detect_drift(reqs, linkages, [], FIXED_TIMESTAMP)

        self.assertEqual(report.unlinked_specs, [])
        self.assertEqual(report.orphan_tests, [])
        self.assertEqual(report.unjustified_code_changes, [])
        self.assertEqual(report.summary.total_drift_count, 0)


class TestDriftDetectionUnlinkedSpecs(unittest.TestCase):
    """@covers REQ-0.20.0-03-01
    @covers REQ-0.20.0-03-02
    """

    @covers("REQ-0.20.0-03-02")
    def test_all_reqs_unlinked(self) -> None:
        """REQ-0.20.0-03-02: 5 REQs, 0 linkages, all 5 unlinked."""
        reqs = [_make_req("0.15.0", "01", f"0{i}") for i in range(1, 6)]

        report = detect_drift(reqs, [], [], FIXED_TIMESTAMP)

        self.assertEqual(len(report.unlinked_specs), 5)
        self.assertEqual(report.summary.unlinked_spec_count, 5)
        for req in reqs:
            self.assertIn(str(req.id), report.unlinked_specs)

    def test_partial_coverage(self) -> None:
        """Some REQs covered, others not."""
        reqs = [_make_req("0.15.0", "01", f"0{i}") for i in range(1, 4)]
        linkages = [_make_covers_linkage(str(reqs[0].id))]

        report = detect_drift(reqs, linkages, [], FIXED_TIMESTAMP)

        self.assertEqual(len(report.unlinked_specs), 2)
        self.assertNotIn(str(reqs[0].id), report.unlinked_specs)
        self.assertIn(str(reqs[1].id), report.unlinked_specs)
        self.assertIn(str(reqs[2].id), report.unlinked_specs)


class TestDriftDetectionOrphanTests(unittest.TestCase):
    """@covers REQ-0.20.0-03-03"""

    @covers("REQ-0.20.0-03-03")
    def test_orphan_tests_detected(self) -> None:
        """REQ-0.20.0-03-03: 3 REQs, 5 linkages (2 non-existent), 2 orphaned."""
        reqs = [_make_req("0.15.0", "01", f"0{i}") for i in range(1, 4)]
        linkages = [
            _make_covers_linkage(str(reqs[0].id)),
            _make_covers_linkage(str(reqs[1].id)),
            _make_covers_linkage(str(reqs[2].id)),
            _make_covers_linkage("REQ-0.15.0-01-99"),
            _make_covers_linkage("REQ-0.15.0-02-88"),
        ]

        report = detect_drift(reqs, linkages, [], FIXED_TIMESTAMP)

        self.assertEqual(len(report.orphan_tests), 2)
        self.assertIn("REQ-0.15.0-01-99", report.orphan_tests)
        self.assertIn("REQ-0.15.0-02-88", report.orphan_tests)
        self.assertEqual(report.summary.orphan_test_count, 2)


class TestDriftDetectionUnjustifiedCode(unittest.TestCase):
    """@covers REQ-0.20.0-03-04"""

    @covers("REQ-0.20.0-03-04")
    def test_unjustified_code_changes(self) -> None:
        """REQ-0.20.0-03-04: 2 changed vertices, 1 justifies, 1 unjustified."""
        reqs = [_make_req("0.15.0", "01", "01")]
        changed = [
            _make_code_vertex("gzkit.triangle.detect_drift"),
            _make_code_vertex("gzkit.triangle.unrelated_func"),
        ]
        linkages = [
            _make_justifies_linkage("gzkit.triangle.detect_drift", str(reqs[0].id)),
        ]

        report = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)

        self.assertEqual(len(report.unjustified_code_changes), 1)
        self.assertIn("gzkit.triangle.unrelated_func", report.unjustified_code_changes)
        self.assertEqual(report.summary.unjustified_code_change_count, 1)

    def test_all_code_justified(self) -> None:
        """All changed code has justifies edges."""
        reqs = [_make_req("0.15.0", "01", "01")]
        changed = [_make_code_vertex("gzkit.module.func")]
        linkages = [_make_justifies_linkage("gzkit.module.func", str(reqs[0].id))]

        report = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)

        self.assertEqual(report.unjustified_code_changes, [])

    def test_no_changed_code(self) -> None:
        """No changed code vertices, no unjustified."""
        report = detect_drift([], [], [], FIXED_TIMESTAMP)
        self.assertEqual(report.unjustified_code_changes, [])


class TestDriftDetectionDeterminism(unittest.TestCase):
    """@covers REQ-0.20.0-03-05"""

    @covers("REQ-0.20.0-03-05")
    def test_identical_inputs_identical_outputs(self) -> None:
        """REQ-0.20.0-03-05: Same inputs produce equal DriftReports."""
        reqs = [_make_req("0.15.0", "01", f"0{i}") for i in range(1, 4)]
        linkages = [
            _make_covers_linkage(str(reqs[0].id)),
            _make_covers_linkage("REQ-0.15.0-01-99"),
        ]
        changed = [_make_code_vertex("gzkit.module.func")]

        report1 = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)
        report2 = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)

        self.assertEqual(report1, report2)
        self.assertEqual(report1.model_dump_json(), report2.model_dump_json())


class TestDriftReportModel(unittest.TestCase):
    """@covers REQ-0.20.0-03-04
    @covers REQ-0.20.0-03-05
    """

    def test_json_serialization_roundtrip(self) -> None:
        """DriftReport serializable to JSON and back."""
        reqs = [_make_req("0.15.0", "01", "01")]
        report = detect_drift(reqs, [], [], FIXED_TIMESTAMP)

        json_str = report.model_dump_json()
        restored = DriftReport.model_validate_json(json_str)
        self.assertEqual(report, restored)

    def test_report_is_valid_json(self) -> None:
        report = detect_drift([], [], [], FIXED_TIMESTAMP)
        parsed = json.loads(report.model_dump_json())
        self.assertIn("unlinked_specs", parsed)
        self.assertIn("orphan_tests", parsed)
        self.assertIn("unjustified_code_changes", parsed)
        self.assertIn("summary", parsed)
        self.assertIn("scan_timestamp", parsed)

    def test_frozen_immutability(self) -> None:
        report = detect_drift([], [], [], FIXED_TIMESTAMP)
        with self.assertRaises(ValidationError):
            report.scan_timestamp = "changed"  # type: ignore[misc]

    def test_summary_counts_correct(self) -> None:
        """Summary counts match list lengths."""
        reqs = [_make_req("0.15.0", "01", f"0{i}") for i in range(1, 4)]
        changed = [_make_code_vertex("func.a"), _make_code_vertex("func.b")]
        linkages = [_make_covers_linkage("REQ-0.15.0-01-99")]

        report = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)

        self.assertEqual(report.summary.unlinked_spec_count, len(report.unlinked_specs))
        self.assertEqual(report.summary.orphan_test_count, len(report.orphan_tests))
        self.assertEqual(
            report.summary.unjustified_code_change_count,
            len(report.unjustified_code_changes),
        )
        self.assertEqual(
            report.summary.total_drift_count,
            report.summary.unlinked_spec_count
            + report.summary.orphan_test_count
            + report.summary.unjustified_code_change_count,
        )

    def test_results_sorted_semantically(self) -> None:
        """Results sorted by identifier using semantic version order."""
        reqs = [
            _make_req("0.15.0", "03", "01"),
            _make_req("0.15.0", "01", "01"),
            _make_req("0.15.0", "02", "01"),
        ]

        report = detect_drift(reqs, [], [], FIXED_TIMESTAMP)

        self.assertEqual(
            report.unlinked_specs,
            [
                "REQ-0.15.0-01-01",
                "REQ-0.15.0-02-01",
                "REQ-0.15.0-03-01",
            ],
        )


class TestDriftDetectionMixed(unittest.TestCase):
    """@covers REQ-0.20.0-03-01
    @covers REQ-0.20.0-03-02
    @covers REQ-0.20.0-03-03
    @covers REQ-0.20.0-03-04
    """

    def test_all_drift_categories(self) -> None:
        """Mixed scenario: unlinked, orphan, and unjustified all present."""
        reqs = [
            _make_req("0.15.0", "01", "01"),
            _make_req("0.15.0", "01", "02"),
        ]
        linkages = [
            _make_covers_linkage("REQ-0.15.0-01-01"),
            _make_covers_linkage("REQ-0.15.0-99-01"),
            _make_justifies_linkage("gzkit.justified_func", "REQ-0.15.0-01-01"),
        ]
        changed = [
            _make_code_vertex("gzkit.justified_func"),
            _make_code_vertex("gzkit.unjustified_func"),
        ]

        report = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)

        self.assertEqual(report.unlinked_specs, ["REQ-0.15.0-01-02"])
        self.assertEqual(report.orphan_tests, ["REQ-0.15.0-99-01"])
        self.assertEqual(report.unjustified_code_changes, ["gzkit.unjustified_func"])
        self.assertEqual(report.summary.total_drift_count, 3)

    def test_empty_inputs(self) -> None:
        """No REQs, no linkages, no changes, zero drift."""
        report = detect_drift([], [], [], FIXED_TIMESTAMP)

        self.assertEqual(report.unlinked_specs, [])
        self.assertEqual(report.orphan_tests, [])
        self.assertEqual(report.unjustified_code_changes, [])
        self.assertEqual(report.summary.total_drift_count, 0)


class TestDriftSummaryModel(unittest.TestCase):
    """@covers REQ-0.20.0-03-04"""

    def test_summary_frozen(self) -> None:
        summary = DriftSummary(
            unlinked_spec_count=1,
            orphan_test_count=2,
            unjustified_code_change_count=3,
            total_drift_count=6,
        )
        with self.assertRaises(ValidationError):
            summary.total_drift_count = 0  # type: ignore[misc]

    def test_summary_extra_forbidden(self) -> None:
        with self.assertRaises(ValidationError):
            DriftSummary(
                unlinked_spec_count=0,
                orphan_test_count=0,
                unjustified_code_change_count=0,
                total_drift_count=0,
                extra=1,  # type: ignore[call-arg]
            )


# ---------------------------------------------------------------------------
# OBPI-0.20.0-04: Drift CLI surface tests
# ---------------------------------------------------------------------------


class TestScanCoversReferences(unittest.TestCase):
    """@covers REQ-0.20.0-04-02
    @covers OBPI-0.20.0-04-gz-drift-cli-surface
    """

    def test_scan_finds_covers_in_docstring(self) -> None:
        """REQ-0.20.0-04-02: Extract @covers REQ references from test files."""
        from gzkit.commands.drift import scan_covers_references

        # Build fixture content via f-string so the @covers pattern does not
        # appear literally in this source file (avoids false-positive orphans
        # when gz drift scans the tests/ directory).
        tag = "@" + "covers"
        fixture = f'"""{tag} REQ-0.1.0-01-01\n{tag} REQ-0.1.0-01-02\n"""\nimport unittest\n'

        with tempfile.TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "test_example.py"
            test_file.write_text(fixture, encoding="utf-8")

            linkages = scan_covers_references(Path(tmp))

        self.assertEqual(len(linkages), 2)
        targets = {r.target.identifier for r in linkages}
        self.assertEqual(targets, {"REQ-0.1.0-01-01", "REQ-0.1.0-01-02"})
        for linkage in linkages:
            self.assertEqual(linkage.edge_type, EdgeType.COVERS)
            self.assertEqual(linkage.source.vertex_type, VertexType.TEST)
            self.assertEqual(linkage.target.vertex_type, VertexType.SPEC)

    def test_scan_empty_directory(self) -> None:
        from gzkit.commands.drift import scan_covers_references

        with tempfile.TemporaryDirectory() as tmp:
            linkages = scan_covers_references(Path(tmp))
        self.assertEqual(linkages, [])

    def test_scan_skips_non_python_files(self) -> None:
        from gzkit.commands.drift import scan_covers_references

        tag = "@" + "covers"
        with tempfile.TemporaryDirectory() as tmp:
            md_file = Path(tmp) / "notes.md"
            md_file.write_text(f"{tag} REQ-0.1.0-01-01\n", encoding="utf-8")

            linkages = scan_covers_references(Path(tmp))

        self.assertEqual(linkages, [])

    def test_scan_ignores_non_req_covers(self) -> None:
        from gzkit.commands.drift import scan_covers_references

        with tempfile.TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "test_example.py"
            test_file.write_text(
                '"""@covers ADR-0.1.0-some-feature\n@covers OBPI-0.1.0-01-feature\n"""\n',
                encoding="utf-8",
            )

            linkages = scan_covers_references(Path(tmp))

        self.assertEqual(linkages, [])


class TestFormatHuman(unittest.TestCase):
    """@covers REQ-0.20.0-04-04
    @covers OBPI-0.20.0-04-gz-drift-cli-surface
    """

    def test_no_drift_message(self) -> None:
        """REQ-0.20.0-04-04: Human output says no drift when clean."""
        from gzkit.commands.drift import _format_human

        report = detect_drift([], [], [], FIXED_TIMESTAMP)
        output = _format_human(report)
        self.assertIn("No drift detected", output)

    @covers("REQ-0.20.0-04-01")
    def test_drift_shows_categories(self) -> None:
        from gzkit.commands.drift import _format_human

        reqs = [_make_req("0.15.0", "01", "01")]
        report = detect_drift(reqs, [], [], FIXED_TIMESTAMP)
        output = _format_human(report)
        self.assertIn("Unlinked Specs", output)
        self.assertIn("REQ-0.15.0-01-01", output)
        self.assertIn("Summary:", output)

    def test_orphan_tests_shown(self) -> None:
        from gzkit.commands.drift import _format_human

        linkages = [_make_covers_linkage("REQ-0.1.0-99-01")]
        report = detect_drift([], linkages, [], FIXED_TIMESTAMP)
        output = _format_human(report)
        self.assertIn("Orphan Tests", output)
        self.assertIn("REQ-0.1.0-99-01", output)

    @covers("REQ-0.20.0-04-05")
    def test_unjustified_shown(self) -> None:
        from gzkit.commands.drift import _format_human

        changed = [_make_code_vertex("src/gzkit/module.py")]
        report = detect_drift([], [], changed, FIXED_TIMESTAMP)
        output = _format_human(report)
        self.assertIn("Unjustified Code Changes", output)
        self.assertIn("src/gzkit/module.py", output)


class TestFormatPlain(unittest.TestCase):
    """@covers REQ-0.20.0-04-06
    @covers OBPI-0.20.0-04-gz-drift-cli-surface
    """

    def test_plain_no_drift(self) -> None:
        """REQ-0.20.0-04-06: Plain output is empty when no drift."""
        from gzkit.commands.drift import _format_plain

        report = detect_drift([], [], [], FIXED_TIMESTAMP)
        output = _format_plain(report)
        self.assertEqual(output, "")

    def test_plain_one_per_line(self) -> None:
        from gzkit.commands.drift import _format_plain

        reqs = [_make_req("0.15.0", "01", "01")]
        linkages = [_make_covers_linkage("REQ-0.1.0-99-01")]
        changed = [_make_code_vertex("src/gzkit/module.py")]
        report = detect_drift(reqs, linkages, changed, FIXED_TIMESTAMP)
        output = _format_plain(report)
        lines = output.strip().split("\n")
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("unlinked\t"))
        self.assertTrue(lines[1].startswith("orphan\t"))
        self.assertTrue(lines[2].startswith("unjustified\t"))


class TestFormatJson(unittest.TestCase):
    """@covers REQ-0.20.0-04-05
    @covers OBPI-0.20.0-04-gz-drift-cli-surface
    """

    @covers("REQ-0.20.0-04-02")
    def test_json_output_valid(self) -> None:
        """REQ-0.20.0-04-05: JSON output is valid DriftReport JSON."""
        reqs = [_make_req("0.15.0", "01", "01")]
        report = detect_drift(reqs, [], [], FIXED_TIMESTAMP)
        json_str = report.model_dump_json(indent=2)
        parsed = json.loads(json_str)
        self.assertIn("unlinked_specs", parsed)
        self.assertIn("orphan_tests", parsed)
        self.assertIn("unjustified_code_changes", parsed)
        self.assertIn("summary", parsed)
        self.assertIn("scan_timestamp", parsed)

    def test_json_roundtrip(self) -> None:
        reqs = [_make_req("0.15.0", "01", "01")]
        report = detect_drift(reqs, [], [], FIXED_TIMESTAMP)
        restored = DriftReport.model_validate_json(report.model_dump_json())
        self.assertEqual(report, restored)


class TestDriftCmdExitCodes(unittest.TestCase):
    """@covers REQ-0.20.0-04-03
    @covers REQ-0.20.0-04-04
    @covers OBPI-0.20.0-04-gz-drift-cli-surface
    """

    @covers("REQ-0.20.0-04-03")
    def test_exit_0_no_drift(self) -> None:
        """REQ-0.20.0-04-03: Exit 0 when no drift detected."""
        from unittest.mock import patch as _patch

        from gzkit.commands.drift import drift_cmd

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adr_dir = tmp_path / "adrs"
            adr_dir.mkdir()
            test_dir = tmp_path / "tests"
            test_dir.mkdir()

            with (
                _patch("gzkit.commands.drift.get_changed_files", return_value=[]),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                drift_cmd(
                    as_json=True,
                    adr_dir=str(adr_dir),
                    test_dir=str(test_dir),
                )

    @covers("REQ-0.20.0-04-04")
    def test_exit_1_with_drift(self) -> None:
        """REQ-0.20.0-04-04: Exit 1 when drift detected."""
        from unittest.mock import patch as _patch

        from gzkit.commands.drift import drift_cmd

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adr_dir = tmp_path / "adrs"
            adr_dir.mkdir()
            test_dir = tmp_path / "tests"
            test_dir.mkdir()

            brief = adr_dir / "OBPI-0.1.0-01-test.md"
            brief.write_text(
                _make_brief(
                    "OBPI-0.1.0-01-test",
                    [("REQ-0.1.0-01-01", False, "Criterion")],
                ),
                encoding="utf-8",
            )

            with (
                _patch("gzkit.commands.drift.get_changed_files", return_value=[]),
                contextlib.redirect_stdout(io.StringIO()),
                self.assertRaises(SystemExit) as cm,
            ):
                drift_cmd(
                    as_json=True,
                    adr_dir=str(adr_dir),
                    test_dir=str(test_dir),
                )
            self.assertEqual(cm.exception.code, 1)


class TestDriftHelpText(unittest.TestCase):
    """@covers REQ-0.20.0-04-06
    @covers OBPI-0.20.0-04-gz-drift-cli-surface
    """

    @covers("REQ-0.20.0-04-06")
    def test_help_includes_description(self) -> None:
        """REQ-0.20.0-04-06: Help includes description, options, example."""
        import subprocess as sp

        result = sp.run(
            ["uv", "run", "gz", "drift", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("drift", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--plain", result.stdout)
        self.assertIn("Examples", result.stdout)

    def test_help_lines_under_80_chars(self) -> None:
        """REQ-0.20.0-04-06: Help text lines <= 80 chars."""
        import subprocess as sp

        result = sp.run(
            ["uv", "run", "gz", "drift", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        for line in result.stdout.splitlines():
            self.assertLessEqual(
                len(line),
                80,
                f"Help line too long ({len(line)} chars): {line!r}",
            )


class TestDriftAdvisoryResult(unittest.TestCase):
    """@covers REQ-0.20.0-05-01
    @covers REQ-0.20.0-05-02
    @covers REQ-0.20.0-05-03
    @covers REQ-0.20.0-05-04
    @covers REQ-0.20.0-05-05
    """

    @covers("REQ-0.20.0-05-01")
    def test_advisory_result_with_drift(self) -> None:
        """REQ-0.20.0-05-01: Advisory result captures drift findings."""
        from gzkit.quality import DriftAdvisoryResult

        result = DriftAdvisoryResult(
            has_drift=True,
            unlinked_specs=["REQ-0.1.0-01-01"],
            orphan_tests=[],
            unjustified_code_changes=[],
            total_drift_count=1,
            scan_timestamp="2026-03-27T00:00:00Z",
        )
        self.assertTrue(result.advisory)
        self.assertTrue(result.has_drift)
        self.assertEqual(result.total_drift_count, 1)

    @covers("REQ-0.20.0-05-02")
    def test_advisory_result_no_drift(self) -> None:
        """REQ-0.20.0-05-03: No drift section when no findings."""
        from gzkit.quality import DriftAdvisoryResult

        result = DriftAdvisoryResult(
            has_drift=False,
            unlinked_specs=[],
            orphan_tests=[],
            unjustified_code_changes=[],
            total_drift_count=0,
            scan_timestamp="2026-03-27T00:00:00Z",
        )
        self.assertFalse(result.has_drift)
        self.assertEqual(result.total_drift_count, 0)

    def test_advisory_flag_always_true(self) -> None:
        """REQ-0.20.0-05-02: Advisory flag is always true (drift never blocks)."""
        from gzkit.quality import DriftAdvisoryResult

        result = DriftAdvisoryResult(
            has_drift=True,
            unlinked_specs=["REQ-0.1.0-01-01"],
            orphan_tests=["REQ-99.0.0-01-01"],
            unjustified_code_changes=["src/gzkit/foo.py"],
            total_drift_count=3,
            scan_timestamp="2026-03-27T00:00:00Z",
        )
        self.assertTrue(result.advisory)

    @covers("REQ-0.20.0-05-04")
    def test_to_dict_includes_advisory_flag(self) -> None:
        """REQ-0.20.0-05-04: JSON output includes advisory: true."""
        from gzkit.quality import DriftAdvisoryResult

        result = DriftAdvisoryResult(
            has_drift=True,
            unlinked_specs=["REQ-0.1.0-01-01"],
            orphan_tests=[],
            unjustified_code_changes=[],
            total_drift_count=1,
            scan_timestamp="2026-03-27T00:00:00Z",
        )
        d = result.to_dict()
        self.assertTrue(d["advisory"])
        self.assertTrue(d["has_drift"])
        self.assertEqual(d["total_drift_count"], 1)
        self.assertIn("unlinked_specs", d)

    def test_check_result_includes_drift(self) -> None:
        """REQ-0.20.0-05-04: CheckResult includes drift in to_dict."""
        from gzkit.quality import CheckResult, DriftAdvisoryResult, QualityResult

        qr = QualityResult(success=True, command="test", stdout="", stderr="", returncode=0)
        drift = DriftAdvisoryResult(
            has_drift=False,
            unlinked_specs=[],
            orphan_tests=[],
            unjustified_code_changes=[],
            total_drift_count=0,
            scan_timestamp="2026-03-27T00:00:00Z",
        )
        cr = CheckResult(
            success=True,
            lint=qr,
            format=qr,
            typecheck=qr,
            test=qr,
            skill_audit=qr,
            parity_check=qr,
            readiness_audit=qr,
            drift=drift,
        )
        d = cr.to_dict()
        self.assertIn("drift", d)
        self.assertTrue(d["drift"]["advisory"])

    @covers("REQ-0.20.0-05-03")
    def test_check_result_without_drift(self) -> None:
        """CheckResult to_dict works when drift is None (backward compat)."""
        from gzkit.quality import CheckResult, QualityResult

        qr = QualityResult(success=True, command="test", stdout="", stderr="", returncode=0)
        cr = CheckResult(
            success=True,
            lint=qr,
            format=qr,
            typecheck=qr,
            test=qr,
            skill_audit=qr,
            parity_check=qr,
            readiness_audit=qr,
        )
        d = cr.to_dict()
        self.assertNotIn("drift", d)

    @covers("REQ-0.20.0-05-05")
    def test_advisory_labels_unjustified_as_advisory(self) -> None:
        """REQ-0.20.0-05-05: Unjustified code changes are labeled advisory."""
        from gzkit.quality import DriftAdvisoryResult

        result = DriftAdvisoryResult(
            has_drift=True,
            unlinked_specs=[],
            orphan_tests=[],
            unjustified_code_changes=["src/gzkit/foo.py"],
            total_drift_count=1,
            scan_timestamp="2026-03-27T00:00:00Z",
        )
        d = result.to_dict()
        self.assertTrue(d["advisory"])
        self.assertEqual(d["unjustified_code_changes"], ["src/gzkit/foo.py"])


if __name__ == "__main__":
    unittest.main()
