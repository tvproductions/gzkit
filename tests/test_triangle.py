"""Tests for the spec-test-code triangle data model.

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-01-req-entity-and-triangle-data-model
"""

from __future__ import annotations

import json
import unittest

from pydantic import ValidationError

from gzkit.triangle import (
    EdgeType,
    LinkageRecord,
    ReqEntity,
    ReqId,
    ReqStatus,
    VertexRef,
    VertexType,
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


if __name__ == "__main__":
    unittest.main()
