"""Tests for ARB receipt JSON schemas.

@covers REQ-0.25.0-33-03
"""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


class TestArbSchemas(unittest.TestCase):
    """ARB schemas exist, are valid JSON Schema, and carry gzkit identifiers."""

    def setUp(self) -> None:
        self.schemas_dir = Path(__file__).resolve().parents[2] / "data" / "schemas"
        self.lint_schema_path = self.schemas_dir / "arb_lint_receipt.schema.json"
        self.step_schema_path = self.schemas_dir / "arb_step_receipt.schema.json"

    def test_lint_schema_exists_and_is_valid(self) -> None:
        self.assertTrue(
            self.lint_schema_path.exists(),
            f"Missing: {self.lint_schema_path}",
        )
        schema = json.loads(self.lint_schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["$id"], "gzkit.arb.lint_receipt.schema.json")
        self.assertEqual(
            schema["properties"]["schema"]["const"],
            "gzkit.arb.lint_receipt.v1",
        )

    def test_step_schema_exists_and_is_valid(self) -> None:
        self.assertTrue(
            self.step_schema_path.exists(),
            f"Missing: {self.step_schema_path}",
        )
        schema = json.loads(self.step_schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["$id"], "gzkit.arb.step_receipt.schema.json")
        self.assertEqual(
            schema["properties"]["schema"]["const"],
            "gzkit.arb.step_receipt.v1",
        )

    def test_lint_receipt_shape_matches_schema(self) -> None:
        """A well-formed lint receipt validates against the schema."""
        schema = json.loads(self.lint_schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        receipt = {
            "schema": "gzkit.arb.lint_receipt.v1",
            "tool": {"name": "ruff", "version": "0.5.0"},
            "run_id": "test-run-0001",
            "timestamp_utc": "2026-04-14T23:59:59Z",
            "git": {"commit": "abc1234", "branch": "main", "dirty": False},
            "findings": [
                {
                    "rule": "E501",
                    "path": "src/example.py",
                    "line": 10,
                    "message": "line too long",
                }
            ],
            "exit_status": 1,
        }
        errors = list(validator.iter_errors(receipt))
        self.assertEqual(errors, [], msg=f"Unexpected schema errors: {errors}")

    def test_step_receipt_shape_matches_schema(self) -> None:
        """A well-formed step receipt validates against the schema."""
        schema = json.loads(self.step_schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        receipt = {
            "schema": "gzkit.arb.step_receipt.v1",
            "step": {"name": "unittest", "command": ["uv", "run", "-m", "unittest"]},
            "run_id": "test-run-0002",
            "timestamp_utc": "2026-04-14T23:59:59Z",
            "git": {"commit": "abc1234"},
            "exit_status": 0,
            "duration_ms": 1500,
            "stdout_tail": "OK",
            "stderr_tail": "",
            "stdout_truncated": False,
            "stderr_truncated": False,
        }
        errors = list(validator.iter_errors(receipt))
        self.assertEqual(errors, [], msg=f"Unexpected schema errors: {errors}")
