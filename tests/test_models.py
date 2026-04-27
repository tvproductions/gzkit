"""Tests for gzkit Pydantic frontmatter models."""

import unittest

from pydantic import ValidationError as PydanticValidationError

from gzkit.models.frontmatter import (
    AdrFrontmatter,
    ObpiFrontmatter,
    PrdFrontmatter,
    validate_frontmatter_model,
)
from gzkit.traceability import covers


class TestAdrFrontmatter(unittest.TestCase):
    """Tests for AdrFrontmatter model."""

    def test_valid_adr(self) -> None:
        fm = AdrFrontmatter(
            id="ADR-0.1.0-test-feature",
            status="Draft",
            semver="0.1.0",
            lane="lite",
            kind="foundation",
            parent="OBPI-core",
            date="2026-01-01",
        )
        self.assertEqual(fm.id, "ADR-0.1.0-test-feature")
        self.assertEqual(fm.status, "Draft")
        self.assertEqual(fm.lane, "lite")
        self.assertEqual(fm.kind, "foundation")

    def test_extra_fields_allowed(self) -> None:
        fm = AdrFrontmatter(
            id="ADR-0.1.0-test-feature",
            status="Draft",
            semver="0.1.0",
            lane="lite",
            kind="foundation",
            parent="OBPI-core",
            date="2026-01-01",
            custom_field="allowed",  # type: ignore[unknown-argument]
        )
        self.assertEqual(fm.id, "ADR-0.1.0-test-feature")

    def test_frozen(self) -> None:
        fm = AdrFrontmatter(
            id="ADR-0.1.0-test-feature",
            status="Draft",
            semver="0.1.0",
            lane="lite",
            kind="foundation",
            parent="OBPI-core",
            date="2026-01-01",
        )
        with self.assertRaises(PydanticValidationError):
            fm.id = "ADR-0.2.0-other"

    def test_invalid_id_pattern(self) -> None:
        with self.assertRaises(PydanticValidationError) as ctx:
            AdrFrontmatter(
                id="BAD-0.1.0",
                status="Draft",
                semver="0.1.0",
                lane="lite",
                kind="foundation",
                parent="OBPI-core",
                date="2026-01-01",
            )
        self.assertTrue(any(e["type"] == "string_pattern_mismatch" for e in ctx.exception.errors()))

    def test_invalid_status_enum(self) -> None:
        with self.assertRaises(PydanticValidationError) as ctx:
            AdrFrontmatter(
                id="ADR-0.1.0",
                status="Invalid",  # type: ignore[invalid-argument-type]
                semver="0.1.0",
                lane="lite",
                kind="foundation",
                parent="OBPI-core",
                date="2026-01-01",
            )
        self.assertTrue(any(e["type"] == "literal_error" for e in ctx.exception.errors()))

    def test_invalid_lane(self) -> None:
        with self.assertRaises(PydanticValidationError):
            AdrFrontmatter(
                id="ADR-0.1.0",
                status="Draft",
                semver="0.1.0",
                lane="Lite",  # type: ignore[invalid-argument-type]
                kind="foundation",
                parent="OBPI-core",
                date="2026-01-01",
            )

    def test_invalid_date_pattern(self) -> None:
        with self.assertRaises(PydanticValidationError):
            AdrFrontmatter(
                id="ADR-0.1.0",
                status="Draft",
                semver="0.1.0",
                lane="lite",
                kind="foundation",
                parent="OBPI-core",
                date="Jan 1 2026",
            )

    def test_missing_required_field(self) -> None:
        with self.assertRaises(PydanticValidationError) as ctx:
            AdrFrontmatter(  # ty: ignore[missing-argument]
                id="ADR-0.1.0",
                status="Draft",
            )
        missing_fields = {
            str(e["loc"][0]) for e in ctx.exception.errors() if e["type"] == "missing"
        }
        self.assertIn("semver", missing_fields)
        self.assertIn("lane", missing_fields)
        self.assertIn("kind", missing_fields)
        self.assertIn("parent", missing_fields)
        self.assertIn("date", missing_fields)

    def test_all_status_values(self) -> None:
        for status in ("Draft", "Proposed", "Accepted", "Superseded", "Deprecated"):
            fm = AdrFrontmatter(
                id="ADR-0.1.0-test-feature",
                status=status,
                semver="0.1.0",
                lane="heavy",
                kind="feature",
                parent="OBPI-core",
                date="2026-01-01",
            )
            self.assertEqual(fm.status, status)

    @covers("REQ-0.0.17-01-03")
    @covers("REQ-0.0.17-01-05")
    def test_invalid_kind_enum(self) -> None:
        for bad_value in ("pool", "", "Foundation", "unknown"):
            with self.assertRaises(PydanticValidationError) as ctx:
                AdrFrontmatter(
                    id="ADR-0.1.0",
                    status="Draft",
                    semver="0.1.0",
                    lane="lite",
                    kind=bad_value,  # type: ignore[invalid-argument-type]
                    parent="OBPI-core",
                    date="2026-01-01",
                )
            errors = ctx.exception.errors()
            self.assertTrue(
                any(e["type"] == "literal_error" and e["loc"] == ("kind",) for e in errors),
                f"Expected literal_error on kind for value {bad_value!r}, got {errors}",
            )

    @covers("REQ-0.0.17-01-05")
    def test_missing_kind(self) -> None:
        with self.assertRaises(PydanticValidationError) as ctx:
            AdrFrontmatter(  # ty: ignore[missing-argument]
                id="ADR-0.1.0",
                status="Draft",
                semver="0.1.0",
                lane="lite",
                parent="OBPI-core",
                date="2026-01-01",
            )
        missing = {str(e["loc"][0]) for e in ctx.exception.errors() if e["type"] == "missing"}
        self.assertIn("kind", missing)


class TestObpiFrontmatter(unittest.TestCase):
    """Tests for ObpiFrontmatter model."""

    def test_valid_obpi(self) -> None:
        fm = ObpiFrontmatter(
            id="OBPI-0.1.0-01-feature-name",
            parent="ADR-0.1.0-some-adr",
            item="1",
            lane="Lite",
            status="Draft",
        )
        self.assertEqual(fm.id, "OBPI-0.1.0-01-feature-name")
        self.assertEqual(fm.item, "1")

    def test_valid_obpi_numeric_only_id(self) -> None:
        fm = ObpiFrontmatter(
            id="OBPI-0.1.0-01",
            parent="ADR-0.1.0-some-adr",
            item=1,
            lane="lite",
            status="Active",
        )
        self.assertEqual(fm.id, "OBPI-0.1.0-01")
        self.assertEqual(fm.item, 1)

    def test_lane_case_variants(self) -> None:
        for lane in ("lite", "heavy", "Lite", "Heavy"):
            fm = ObpiFrontmatter(
                id="OBPI-0.1.0-01",
                parent="ADR-0.1.0",
                item="1",
                lane=lane,
                status="Draft",
            )
            self.assertEqual(fm.lane, lane)

    def test_invalid_id_pattern(self) -> None:
        with self.assertRaises(PydanticValidationError):
            ObpiFrontmatter(
                id="OBPI-0.1.0-1",
                parent="ADR-0.1.0",
                item="1",
                lane="lite",
                status="Draft",
            )

    def test_invalid_status(self) -> None:
        with self.assertRaises(PydanticValidationError):
            ObpiFrontmatter(
                id="OBPI-0.1.0-01",
                parent="ADR-0.1.0",
                item="1",
                lane="lite",
                status="Closed",  # type: ignore[invalid-argument-type]
            )

    def test_all_status_values(self) -> None:
        for status in ("Draft", "Active", "Completed", "Abandoned"):
            fm = ObpiFrontmatter(
                id="OBPI-0.1.0-01",
                parent="ADR-0.1.0",
                item="1",
                lane="lite",
                status=status,
            )
            self.assertEqual(fm.status, status)


class TestPrdFrontmatter(unittest.TestCase):
    """Tests for PrdFrontmatter model."""

    def test_valid_prd(self) -> None:
        fm = PrdFrontmatter(
            id="PRD-GZKIT-1.0.0",
            status="Draft",
            semver="1.0.0",
            date="2026-01-01",
        )
        self.assertEqual(fm.id, "PRD-GZKIT-1.0.0")

    def test_invalid_id_pattern(self) -> None:
        with self.assertRaises(PydanticValidationError):
            PrdFrontmatter(
                id="PRD-gzkit-1.0.0",
                status="Draft",
                semver="1.0.0",
                date="2026-01-01",
            )

    def test_invalid_status(self) -> None:
        with self.assertRaises(PydanticValidationError):
            PrdFrontmatter(
                id="PRD-GZKIT-1.0.0",
                status="Active",  # type: ignore[invalid-argument-type]
                semver="1.0.0",
                date="2026-01-01",
            )

    def test_missing_required_field(self) -> None:
        with self.assertRaises(PydanticValidationError) as ctx:
            PrdFrontmatter(id="PRD-GZKIT-1.0.0")  # ty: ignore[missing-argument]
        missing_fields = {
            str(e["loc"][0]) for e in ctx.exception.errors() if e["type"] == "missing"
        }
        self.assertIn("status", missing_fields)
        self.assertIn("semver", missing_fields)
        self.assertIn("date", missing_fields)

    def test_all_status_values(self) -> None:
        for status in ("Draft", "Review", "Approved", "Superseded"):
            fm = PrdFrontmatter(
                id="PRD-GZKIT-1.0.0",
                status=status,
                semver="1.0.0",
                date="2026-01-01",
            )
            self.assertEqual(fm.status, status)


class TestValidateFrontmatterModel(unittest.TestCase):
    """Tests for the validate_frontmatter_model translation layer."""

    def test_returns_none_for_unknown_schema(self) -> None:
        result = validate_frontmatter_model({}, {"$id": "unknown.v1"}, "test.md")
        self.assertIsNone(result)

    def test_valid_adr_returns_empty(self) -> None:
        fm = {
            "id": "ADR-0.1.0-test-feature",
            "status": "Draft",
            "semver": "0.1.0",
            "lane": "lite",
            "kind": "foundation",
            "parent": "OBPI-core",
            "date": "2026-01-01",
        }
        result = validate_frontmatter_model(fm, {"$id": "gzkit.adr.v1"}, "test.md")
        self.assertEqual(result, [])

    def test_missing_field_error_message(self) -> None:
        fm = {"id": "ADR-0.1.0", "status": "Draft"}
        result = validate_frontmatter_model(fm, {"$id": "gzkit.adr.v1"}, "test.md")
        self.assertIsNotNone(result)
        assert result is not None
        messages = [e["message"] for e in result]
        self.assertTrue(any("Missing required frontmatter field: semver" in m for m in messages))

    def test_pattern_error_message(self) -> None:
        fm = {
            "id": "BAD-ID",
            "status": "Draft",
            "semver": "0.1.0",
            "lane": "lite",
            "kind": "foundation",
            "parent": "core",
            "date": "2026-01-01",
        }
        result = validate_frontmatter_model(fm, {"$id": "gzkit.adr.v1"}, "test.md")
        self.assertIsNotNone(result)
        assert result is not None
        messages = [e["message"] for e in result]
        self.assertTrue(any("does not match pattern" in m for m in messages))

    def test_enum_error_message(self) -> None:
        fm = {
            "id": "ADR-0.1.0",
            "status": "Invalid",
            "semver": "0.1.0",
            "lane": "lite",
            "kind": "foundation",
            "parent": "core",
            "date": "2026-01-01",
        }
        result = validate_frontmatter_model(fm, {"$id": "gzkit.adr.v1"}, "test.md")
        self.assertIsNotNone(result)
        assert result is not None
        messages = [e["message"] for e in result]
        self.assertTrue(any("must be one of" in m and "got 'Invalid'" in m for m in messages))

    def test_error_dict_shape(self) -> None:
        fm = {"id": "ADR-0.1.0"}
        result = validate_frontmatter_model(fm, {"$id": "gzkit.adr.v1"}, "test.md")
        self.assertIsNotNone(result)
        assert result is not None
        for err in result:
            self.assertIn("type", err)
            self.assertIn("artifact", err)
            self.assertIn("message", err)
            self.assertIn("field", err)
            self.assertEqual(err["type"], "frontmatter")
            self.assertEqual(err["artifact"], "test.md")

    @covers("REQ-0.0.17-01-06")
    def test_translates_kind_literal_error(self) -> None:
        fm = {
            "id": "ADR-0.1.0",
            "status": "Draft",
            "semver": "0.1.0",
            "lane": "lite",
            "kind": "pool",
            "parent": "core",
            "date": "2026-01-01",
        }
        result = validate_frontmatter_model(fm, {"$id": "gzkit.adr.v1"}, "test.md")
        self.assertIsNotNone(result)
        assert result is not None
        kind_errors = [e for e in result if e["field"] == "kind"]
        self.assertEqual(
            len(kind_errors), 1, f"expected one kind error, got {len(kind_errors)}: {result}"
        )
        err = kind_errors[0]
        self.assertEqual(err["type"], "frontmatter")
        self.assertEqual(err["artifact"], "test.md")
        self.assertEqual(err["field"], "kind")
        self.assertIn("foundation", err["message"])
        self.assertIn("feature", err["message"])
        self.assertIn("pool", err["message"])


if __name__ == "__main__":
    unittest.main()
