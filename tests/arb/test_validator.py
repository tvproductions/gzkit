"""Tests for gzkit.arb.validator.

@covers REQ-0.25.0-33-03
"""

import json
import tempfile
import unittest
from pathlib import Path

_VALID_LINT_RECEIPT = {
    "schema": "gzkit.arb.lint_receipt.v1",
    "tool": {"name": "ruff", "version": "0.5.0"},
    "run_id": "test-0001",
    "timestamp_utc": "2026-04-14T23:59:59Z",
    "git": {"commit": "abc1234"},
    "findings": [],
    "exit_status": 0,
}

_VALID_STEP_RECEIPT = {
    "schema": "gzkit.arb.step_receipt.v1",
    "step": {"name": "unittest", "command": ["uv", "run"]},
    "run_id": "test-0002",
    "timestamp_utc": "2026-04-14T23:59:59Z",
    "git": {"commit": "abc1234"},
    "exit_status": 0,
    "duration_ms": 1000,
    "stdout_tail": "ok",
    "stderr_tail": "",
    "stdout_truncated": False,
    "stderr_truncated": False,
}


def _write_receipt(directory: Path, name: str, payload: dict | str) -> Path:
    path = directory / f"{name}.json"
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class TestValidateReceipts(unittest.TestCase):
    """validate_receipts counts valid/invalid/unknown receipts."""

    def test_all_valid(self) -> None:
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_receipt(directory, "a", _VALID_LINT_RECEIPT)
            _write_receipt(directory, "b", _VALID_STEP_RECEIPT)
            result = validate_receipts(root=directory)

        self.assertEqual(result.scanned, 2)
        self.assertEqual(result.valid, 2)
        self.assertEqual(result.invalid, 0)
        self.assertEqual(result.unknown_schema, 0)
        self.assertEqual(result.errors, [])

    def test_malformed_counts_invalid(self) -> None:
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_receipt(directory, "valid", _VALID_LINT_RECEIPT)
            bad = {**_VALID_LINT_RECEIPT, "exit_status": "not-int"}
            _write_receipt(directory, "bad", bad)
            result = validate_receipts(root=directory)

        self.assertEqual(result.scanned, 2)
        self.assertEqual(result.valid, 1)
        self.assertEqual(result.invalid, 1)

    def test_unknown_schema(self) -> None:
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            unknown = {"schema": "other.schema.v99", "foo": "bar"}
            _write_receipt(directory, "unknown", unknown)
            result = validate_receipts(root=directory)

        self.assertEqual(result.scanned, 1)
        self.assertEqual(result.valid, 0)
        self.assertEqual(result.invalid, 1)
        self.assertEqual(result.unknown_schema, 1)

    def test_missing_schema_field(self) -> None:
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_receipt(directory, "broken", {"no": "schema"})
            result = validate_receipts(root=directory)

        self.assertEqual(result.invalid, 1)
        self.assertEqual(result.unknown_schema, 0)
        self.assertEqual(len(result.errors), 1)

    def test_empty_directory(self) -> None:
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_receipts(root=Path(tmpdir))

        self.assertEqual(result.scanned, 0)
        self.assertEqual(result.valid, 0)

    def test_limit_honored(self) -> None:
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            for i in range(5):
                _write_receipt(directory, f"r{i}", _VALID_LINT_RECEIPT)
            result = validate_receipts(root=directory, limit=3)

        self.assertEqual(result.scanned, 3)

    def test_result_is_frozen_pydantic(self) -> None:
        from pydantic import ValidationError

        from gzkit.arb.validator import ArbReceiptValidationResult

        result = ArbReceiptValidationResult(
            scanned=0, valid=0, invalid=0, unknown_schema=0, errors=[]
        )
        with self.assertRaises(ValidationError):
            result.scanned = 99
