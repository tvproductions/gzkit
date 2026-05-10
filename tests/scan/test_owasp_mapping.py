"""Schema-validation tests for the OWASP Top 10:2025 analyzer mapping.

Verifies that ``.gzkit/chores/owasp-top10-2025-scan/mapping.json`` validates
against its companion ``mapping.schema.json`` (Draft 2020-12). The schema
encodes ADR-0.47.0 Decision § A01-A10 invariants mechanically: required
key set, allowed source enum, ruff-rule code shape, coverage-baseline
enum.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from gzkit.scan.mapping import load_mapping
from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING_DIR = PROJECT_ROOT / ".gzkit" / "chores" / "owasp-top10-2025-scan"


class TestOwaspMappingSchema(unittest.TestCase):
    """REQ-derived mapping-vs-schema invariant tests."""

    @covers("REQ-0.47.0-01-01")
    def test_mapping_validates_against_schema(self) -> None:
        """REQ-01: mapping.json validates against mapping.schema.json."""
        mapping_path = MAPPING_DIR / "mapping.json"
        schema_path = MAPPING_DIR / "mapping.schema.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(mapping), key=lambda err: list(err.path))
        self.assertEqual(
            errors,
            [],
            msg=(
                "mapping.json must validate against mapping.schema.json; "
                f"errors: {[err.message for err in errors]}"
            ),
        )

    def test_loader_returns_all_ten_categories(self) -> None:
        """Loader sanity: all OWASP 2025 codes A01..A10 present after load."""
        categories = load_mapping(MAPPING_DIR / "mapping.json")
        expected = {f"A{i:02d}" for i in range(1, 11)}
        self.assertEqual(set(categories.keys()), expected)


if __name__ == "__main__":
    unittest.main()
