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
    "step": {"name": "unittest", "command": ["uv", "run", "-m", "unittest", "-q"]},
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
    """Write a receipt under the real ``arb-`` filename contract.

    ARB receipts are always written as ``arb-ruff-*`` / ``arb-step-*`` /
    ``arb-red-*`` (AGENTS.md § Attestation pins the prefixes), and the validator
    scopes its scan to them because the receipts directory is shared with other
    artifact kinds. Fixtures named ``a`` / ``bad`` did not exercise that contract.
    """
    path = directory / f"arb-{name}.json"
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

    def test_co_located_non_arb_artifact_is_not_reported(self) -> None:
        """A different artifact kind in the receipts directory is not an ARB defect.

        ``artifacts/receipts/`` is shared: ``foundation-sunset-migration-*.json``
        lives beside the ARB receipts and carries no ``schema`` field at all. A
        bare ``*.json`` scan reported three of them as invalid ARB receipts — a
        false positive about files that never claimed to be ARB receipts, and one
        that made `gz arb validate` unusable as a chore criterion.
        """
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_receipt(directory, "step-real", _VALID_STEP_RECEIPT)
            (directory / "foundation-sunset-migration-2026-07-30T03-38-01Z.json").write_text(
                json.dumps({"attestor": "g0", "demote_count": 3, "dry_run": False}),
                encoding="utf-8",
            )
            result = validate_receipts(root=directory)

        self.assertEqual(result.scanned, 1, "only the arb-* receipt is in scope")
        self.assertEqual(result.valid, 1)
        self.assertEqual(result.invalid, 0, "a non-ARB artifact is not an invalid ARB receipt")

    def test_malformed_arb_receipt_is_still_caught(self) -> None:
        """Scoping by filename must not become a way to skip a real defect.

        The scan is filename-scoped rather than filtered on the ``schema`` field
        precisely so an ``arb-*`` receipt with a missing or wrong schema still
        fails — that is the defect the validator exists to catch.
        """
        from gzkit.arb.validator import validate_receipts

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_receipt(directory, "ruff-deadbeef", {"no": "schema"})
            result = validate_receipts(root=directory)

        self.assertEqual(result.scanned, 1)
        self.assertEqual(result.invalid, 1)

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
