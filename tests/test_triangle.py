"""Tests for the spec-test-code triangle data model.

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-01-req-entity-and-triangle-data-model
@covers OBPI-0.20.0-02-brief-req-extraction
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.triangle import (
    DiscoveredReq,
    EdgeType,
    LinkageRecord,
    ReqEntity,
    ReqId,
    ReqStatus,
    VertexRef,
    VertexType,
    extract_reqs_from_brief,
    scan_briefs,
)


class TestReqIdParsing(unittest.TestCase):
    """@covers REQ-0.20.0-01-01
    @covers REQ-0.20.0-01-07
    """

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

    def test_three_edge_types_exist(self) -> None:
        """REQ-0.20.0-01-04: Exactly covers, proves, justifies edges."""
        members = {m.value for m in EdgeType}
        self.assertEqual(members, {"covers", "proves", "justifies"})

    def test_edge_type_count(self) -> None:
        self.assertEqual(len(EdgeType), 3)


class TestVertexRef(unittest.TestCase):
    """@covers REQ-0.20.0-01-05"""

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
    @covers REQ-0.20.0-01-05
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


if __name__ == "__main__":
    unittest.main()
