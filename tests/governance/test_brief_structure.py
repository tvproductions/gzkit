"""Tests for BriefStructure model and parse_brief loader (OBPI-0.0.37-04).

REQ-derived assertions for:
  REQ-0.0.37-04-01: frozen Pydantic BriefStructure model with all named fields
  REQ-0.0.37-04-02: JSON Schema mirror with additionalProperties: false
  REQ-0.0.37-04-03: parse_brief permissive mode returns BriefStructure or LegacyBriefShape+warning
  REQ-0.0.37-04-04: parse_brief strict=True raises ValueError on legacy brief
  REQ-0.0.37-04-05: round-trip parse of OBPI-0.0.37-04 brief itself returns BriefStructure
"""

from __future__ import annotations

import json
import unittest
import warnings
from pathlib import Path

import jsonschema
from pydantic import ValidationError

from gzkit.governance.brief_structure import BriefStructure, LegacyBriefShape, parse_brief
from gzkit.traceability import covers

FIXTURES = Path(__file__).parent.parent / "fixtures" / "brief_structure"
SCHEMA_PATH = (
    Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "obpi_brief_structure.json"
)
THIS_BRIEF = (
    Path(__file__).parent.parent.parent
    / "docs"
    / "design"
    / "adr"
    / "foundation"
    / "ADR-0.0.37-constitutional-invariant-composition"
    / "obpis"
    / "OBPI-0.0.37-04-brief-structural-schema.md"
)

_VALID_FIELDS = {
    "id": "OBPI-0.0.37-04-brief-structural-schema",
    "parent": "ADR-0.0.37-constitutional-invariant-composition",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/x.py"],
    "reqs": ["REQ-0.0.37-04-01"],
    "verification": ["uv run gz lint"],
    "citations": [],
}


class TestBriefStructureModel(unittest.TestCase):
    """REQ-0.0.37-04-01: frozen model with all named fields."""

    @covers("REQ-0.0.37-04-01")
    def test_model_is_frozen(self) -> None:
        b = BriefStructure(**_VALID_FIELDS)
        with self.assertRaises((ValueError, TypeError)):
            b.id = "MUTATED"  # type: ignore

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_allowlist(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "allowlist": []})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_reqs(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "reqs": []})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_verification(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "verification": []})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_extra_fields(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**_VALID_FIELDS, unexpected_field="bad")  # type: ignore

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_invalid_id(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "id": "not-a-valid-obpi-id"})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_invalid_req_format(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "reqs": ["bad-format"]})

    @covers("REQ-0.0.37-04-01")
    def test_model_accepts_citations_list(self) -> None:
        b = BriefStructure(**{**_VALID_FIELDS, "citations": [("src/x.py", "#anchor")]})
        self.assertEqual(b.citations, [("src/x.py", "#anchor")])

    def test_model_accepts_active_in_flight_status(self) -> None:
        """An in-flight brief carries status Active (status_vocab canon:
        in_progress -> Active). The structured schema MUST accept it so a brief
        the pipeline has flipped to Active still parses as BriefStructure rather
        than degrading to LegacyBriefShape (which silently disables reconcile
        drift-escalation during implementation). GHI #646."""
        b = BriefStructure(**{**_VALID_FIELDS, "status": "Active"})
        self.assertEqual(b.status, "Active")

    def test_tasks_optional_defaults_empty(self) -> None:
        """tasks field is optional and defaults to empty list (OBPI-0.0.64-04)."""
        b = BriefStructure(**_VALID_FIELDS)
        self.assertEqual(b.tasks, [])

    def test_tasks_accepts_list_of_strings(self) -> None:
        """tasks field accepts a list of TASK ID strings (OBPI-0.0.64-04)."""
        b = BriefStructure(**{**_VALID_FIELDS, "tasks": ["TASK-0.0.64-04-01-01"]})
        self.assertEqual(b.tasks, ["TASK-0.0.64-04-01-01"])

    @covers("REQ-0.0.64-04-04")
    def test_req_atomic_optional_defaults_empty(self) -> None:
        """req_atomic field is optional and defaults to empty list (OBPI-0.0.64-04)."""
        b = BriefStructure(**_VALID_FIELDS)
        self.assertEqual(b.req_atomic, [])

    @covers("REQ-0.0.64-04-04")
    def test_req_atomic_accepts_list_of_strings(self) -> None:
        """req_atomic accepts a list of REQ ID strings (OBPI-0.0.64-04)."""
        b = BriefStructure(**{**_VALID_FIELDS, "req_atomic": ["REQ-0.0.64-04-01"]})
        self.assertEqual(b.req_atomic, ["REQ-0.0.64-04-01"])


class TestBriefStructureJsonSchema(unittest.TestCase):
    """REQ-0.0.37-04-02: JSON Schema mirror."""

    def _schema(self) -> dict:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    @covers("REQ-0.0.37-04-02")
    def test_schema_has_additional_properties_false(self) -> None:
        schema = self._schema()
        self.assertIs(schema.get("additionalProperties"), False)

    @covers("REQ-0.0.37-04-02")
    def test_schema_validates_compliant_instance(self) -> None:
        schema = self._schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Draft",
            "allowlist": ["src/x.py"],
            "reqs": ["REQ-0.0.1-01-01"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        jsonschema.validate(instance, schema)  # must not raise

    @covers("REQ-0.0.37-04-02")
    def test_schema_rejects_missing_reqs(self) -> None:
        schema = self._schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Draft",
            "allowlist": ["src/x.py"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


class TestParseBriefPermissive(unittest.TestCase):
    """REQ-0.0.37-04-03: permissive mode behavior."""

    @covers("REQ-0.0.37-04-03")
    def test_compliant_brief_returns_brief_structure(self) -> None:
        result = parse_brief(FIXTURES / "compliant.md")
        self.assertIsInstance(result, BriefStructure)

    @covers("REQ-0.0.37-04-03")
    def test_compliant_brief_no_deprecation_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(FIXTURES / "compliant.md")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecations, [])

    @covers("REQ-0.0.37-04-03")
    def test_legacy_brief_returns_legacy_shape(self) -> None:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = parse_brief(FIXTURES / "legacy.md")
        self.assertIsInstance(result, LegacyBriefShape)

    @covers("REQ-0.0.37-04-03")
    def test_legacy_brief_emits_deprecation_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(FIXTURES / "legacy.md")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertGreater(len(deprecations), 0)


class TestParseBriefStrict(unittest.TestCase):
    """REQ-0.0.37-04-04: strict=True raises ValueError on legacy brief."""

    @covers("REQ-0.0.37-04-04")
    def test_strict_raises_on_legacy_brief(self) -> None:
        with self.assertRaises(ValueError):
            parse_brief(FIXTURES / "legacy.md", strict=True)

    @covers("REQ-0.0.37-04-04")
    def test_strict_succeeds_on_compliant_brief(self) -> None:
        result = parse_brief(FIXTURES / "compliant.md", strict=True)
        self.assertIsInstance(result, BriefStructure)


class TestParseBriefRoundTrip(unittest.TestCase):
    """REQ-0.0.37-04-05: round-trip on OBPI-0.0.37-04 brief itself."""

    @covers("REQ-0.0.37-04-05")
    def test_this_brief_parses_as_brief_structure(self) -> None:
        result = parse_brief(THIS_BRIEF)
        self.assertIsInstance(result, BriefStructure)

    @covers("REQ-0.0.37-04-05")
    def test_this_brief_no_deprecation_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(THIS_BRIEF)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecations, [])


if __name__ == "__main__":
    unittest.main()
