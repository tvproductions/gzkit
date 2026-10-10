"""Tests for ARB receipt JSON schemas.

The schemas are exercised through the receipt validator that reads them in
production: a receipt the writers would emit is accepted, a receipt missing a
required field or naming an unknown schema is rejected, and each schema the
validator resolves is a well-formed Draft 2020-12 schema carrying its gzkit
identifier.

@covers REQ-0.25.0-33-03
"""

import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from gzkit.arb.ruff_reporter import SCHEMA_ID as LINT_SCHEMA_ID
from gzkit.arb.step_reporter import SCHEMA_ID as STEP_SCHEMA_ID
from gzkit.arb.validator import _schema_path_for_id, validate_receipts


def _lint_receipt() -> dict[str, object]:
    return {
        "schema": LINT_SCHEMA_ID,
        "tool": {"name": "ruff", "version": "0.5.0"},
        "run_id": "arb-ruff-test-run-0001",
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


def _step_receipt() -> dict[str, object]:
    return {
        "schema": STEP_SCHEMA_ID,
        # A non-canonical step label: a canonical one (unittest, typecheck, ...)
        # is also held to its canonical command, which is provenance, not shape.
        "step": {"name": "example-step", "command": ["uv", "run", "python", "-c", "pass"]},
        "run_id": "arb-step-test-run-0002",
        "timestamp_utc": "2026-04-14T23:59:59Z",
        "git": {"commit": "abc1234"},
        "exit_status": 0,
        "duration_ms": 1500,
        "stdout_tail": "OK",
        "stderr_tail": "",
        "stdout_truncated": False,
        "stderr_truncated": False,
    }


def _write(directory: Path, payload: dict[str, object]) -> Path:
    path = directory / f"{payload['run_id']}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class TestArbSchemas(unittest.TestCase):
    """ARB schemas accept the writers' receipts and reject malformed ones."""

    def test_well_formed_lint_receipt_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), _lint_receipt())
            result = validate_receipts(root=Path(tmp))
        self.assertEqual(result.errors, [])
        self.assertEqual((result.scanned, result.valid, result.invalid), (1, 1, 0))

    def test_well_formed_step_receipt_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), _step_receipt())
            result = validate_receipts(root=Path(tmp))
        self.assertEqual(result.errors, [])
        self.assertEqual((result.scanned, result.valid, result.invalid), (1, 1, 0))

    def test_lint_receipt_without_findings_is_rejected(self) -> None:
        receipt = _lint_receipt()
        del receipt["findings"]
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), receipt)
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.valid, result.invalid), (0, 1))
        self.assertEqual(len(result.errors), 1)
        self.assertIn("findings", result.errors[0])

    def test_step_receipt_without_duration_is_rejected(self) -> None:
        receipt = _step_receipt()
        del receipt["duration_ms"]
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), receipt)
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.valid, result.invalid), (0, 1))
        self.assertIn("duration_ms", result.errors[0])

    def test_unknown_schema_id_is_rejected_not_guessed(self) -> None:
        receipt = _step_receipt()
        receipt["schema"] = "gzkit.arb.step_receipt.v99"
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), receipt)
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.valid, result.unknown_schema), (0, 1))

    def test_resolved_schemas_are_well_formed_and_self_identifying(self) -> None:
        expected = {
            LINT_SCHEMA_ID: "gzkit.arb.lint_receipt.schema.json",
            STEP_SCHEMA_ID: "gzkit.arb.step_receipt.schema.json",
        }
        for schema_id, schema_file_id in expected.items():
            with self.subTest(schema=schema_id):
                path = _schema_path_for_id(schema_id)
                self.assertIsNotNone(path, f"validator resolves no schema for {schema_id}")
                schema = json.loads(path.read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)
                self.assertEqual(schema["$id"], schema_file_id)
                self.assertEqual(schema["properties"]["schema"]["const"], schema_id)
