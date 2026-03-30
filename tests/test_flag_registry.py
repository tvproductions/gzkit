"""Tests for feature flag registry loader (OBPI-0.0.8-01)."""

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.flags.models import FlagSpec, InvalidFlagValueError
from gzkit.flags.registry import load_registry
from gzkit.traceability import covers

# Minimal valid schema file content (contract artifact).
_SCHEMA_STUB = json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema"})


def _write_registry(
    tmp: Path, flags: list[dict[str, object]], *, extra_keys: dict[str, object] | None = None
) -> tuple[Path, Path]:
    """Write a flags.json and schema stub into a temp directory. Return paths."""
    registry_path = tmp / "flags.json"
    schema_path = tmp / "flags.schema.json"

    payload: dict[str, object] = {"flags": flags}
    if extra_keys:
        payload.update(extra_keys)

    registry_path.write_text(json.dumps(payload), encoding="utf-8")
    schema_path.write_text(_SCHEMA_STUB, encoding="utf-8")
    return registry_path, schema_path


def _valid_ops_flag(**overrides: object) -> dict[str, object]:
    """Return a valid ops flag entry dict."""
    base: dict[str, object] = {
        "key": "ops.test_flag",
        "category": "ops",
        "default": True,
        "description": "A test flag for unit tests.",
        "owner": "test-team",
        "introduced_on": "2026-03-29",
        "review_by": "2026-06-29",
    }
    base.update(overrides)
    return base


class TestLoadRegistry(unittest.TestCase):
    """Registry loading happy path."""

    @covers("REQ-0.0.8-01-04")
    def test_load_valid_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            flags = [
                _valid_ops_flag(),
                {
                    "key": "migration.old_path",
                    "category": "migration",
                    "default": False,
                    "description": "Migration flag.",
                    "owner": "governance",
                    "introduced_on": "2026-03-29",
                    "remove_by": "2026-05-01",
                },
            ]
            reg_path, schema_path = _write_registry(tmp_path, flags)
            result = load_registry(reg_path, schema_path=schema_path)

            self.assertEqual(len(result), 2)
            self.assertIn("ops.test_flag", result)
            self.assertIn("migration.old_path", result)
            self.assertIsInstance(result["ops.test_flag"], FlagSpec)

    def test_empty_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reg_path, schema_path = _write_registry(Path(tmp), [])
            result = load_registry(reg_path, schema_path=schema_path)
            self.assertEqual(result, {})


class TestDuplicateKeyDetection(unittest.TestCase):
    """Duplicate key detection."""

    @covers("REQ-0.0.8-01-05")
    def test_duplicate_keys_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            flags = [_valid_ops_flag(), _valid_ops_flag()]
            reg_path, schema_path = _write_registry(Path(tmp), flags)

            with self.assertRaises(InvalidFlagValueError) as ctx:
                load_registry(reg_path, schema_path=schema_path)
            self.assertIn("Duplicate", str(ctx.exception))


class TestSchemaValidation(unittest.TestCase):
    """Registry structural and schema validation."""

    @covers("REQ-0.0.8-01-06")
    def test_missing_flags_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "flags.json"
            schema_path = tmp_path / "flags.schema.json"
            reg_path.write_text('{"not_flags": []}', encoding="utf-8")
            schema_path.write_text(_SCHEMA_STUB, encoding="utf-8")

            with self.assertRaises(InvalidFlagValueError) as ctx:
                load_registry(reg_path, schema_path=schema_path)
            self.assertIn("flags", str(ctx.exception))

    def test_extra_top_level_keys_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reg_path, schema_path = _write_registry(Path(tmp), [], extra_keys={"metadata": "bad"})
            with self.assertRaises(InvalidFlagValueError):
                load_registry(reg_path, schema_path=schema_path)

    def test_invalid_json_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "flags.json"
            schema_path = tmp_path / "flags.schema.json"
            reg_path.write_text("{invalid json", encoding="utf-8")
            schema_path.write_text(_SCHEMA_STUB, encoding="utf-8")

            with self.assertRaises(InvalidFlagValueError):
                load_registry(reg_path, schema_path=schema_path)

    def test_missing_registry_file_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(InvalidFlagValueError):
            load_registry(Path(tmp) / "nonexistent.json")

    def test_missing_schema_file_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "flags.json"
            reg_path.write_text('{"flags": []}', encoding="utf-8")

            with self.assertRaises(InvalidFlagValueError):
                load_registry(reg_path, schema_path=tmp_path / "missing.json")

    def test_invalid_entry_type_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "flags.json"
            schema_path = tmp_path / "flags.schema.json"
            reg_path.write_text('{"flags": ["not_an_object"]}', encoding="utf-8")
            schema_path.write_text(_SCHEMA_STUB, encoding="utf-8")

            with self.assertRaises(InvalidFlagValueError):
                load_registry(reg_path, schema_path=schema_path)

    def test_category_rule_failure_propagated(self) -> None:
        """Pydantic validation errors from category rules propagate."""
        with tempfile.TemporaryDirectory() as tmp:
            flags = [
                {
                    "key": "release.no_remove",
                    "category": "release",
                    "default": False,
                    "description": "Missing remove_by.",
                    "owner": "test",
                    "introduced_on": "2026-03-29",
                }
            ]
            reg_path, schema_path = _write_registry(Path(tmp), flags)

            with self.assertRaises(ValidationError):
                load_registry(reg_path, schema_path=schema_path)

    def test_flags_not_array_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "flags.json"
            schema_path = tmp_path / "flags.schema.json"
            reg_path.write_text('{"flags": "not_array"}', encoding="utf-8")
            schema_path.write_text(_SCHEMA_STUB, encoding="utf-8")

            with self.assertRaises(InvalidFlagValueError):
                load_registry(reg_path, schema_path=schema_path)


class TestRealRegistry(unittest.TestCase):
    """Validate the actual data/flags.json in the repository."""

    def test_real_registry_loads(self) -> None:
        """The shipped data/flags.json parses without error."""
        real_path = Path("data") / "flags.json"
        schema_path = Path("data") / "schemas" / "flags.schema.json"
        if not real_path.is_file():
            self.skipTest("data/flags.json not present (CI artifact)")

        result = load_registry(real_path, schema_path=schema_path)
        self.assertGreater(len(result), 0)
        for key, spec in result.items():
            self.assertEqual(key, spec.key)


if __name__ == "__main__":
    unittest.main()
