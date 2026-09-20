"""The single read seam for `data/` config registries (GHI #1067).

Thirty-plus modules each resolved their own registry path and ran their own
`json.loads`, which is the parallel-systems shape `../airlineops/config` principle
3 forbids. These assert the seam's contract: what it returns, what it refuses,
and — the part that matters most — that it never defaults past a broken file.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.registries import (
    RegistryError,
    load_registry,
    load_registry_field,
    registry_path,
)


class SeamReads(unittest.TestCase):
    """`load_registry` parses a registry or raises one typed error."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "data").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, name: str, text: str) -> None:
        (self.root / "data" / name).write_text(text, encoding="utf-8")

    def test_object_payload_round_trips(self) -> None:
        self._write("t.json", json.dumps({"a": 1}))
        self.assertEqual(load_registry(self.root, "t.json"), {"a": 1})

    def test_bare_array_payload_is_returned_as_is(self) -> None:
        """Registries are objects, arrays or rosters; coercing would invent a schema."""
        self._write("t.json", json.dumps(["a", "b"]))
        self.assertEqual(load_registry(self.root, "t.json"), ["a", "b"])

    def test_missing_registry_raises(self) -> None:
        with self.assertRaises(RegistryError):
            load_registry(self.root, "absent.json")

    def test_malformed_json_raises(self) -> None:
        self._write("t.json", "{not json")
        with self.assertRaises(RegistryError):
            load_registry(self.root, "t.json")

    def test_a_path_instead_of_a_name_is_refused(self) -> None:
        """Passing a path reaches around the seam the seam exists to be."""
        with self.assertRaises(RegistryError):
            load_registry(self.root, "../data/t.json")

    def test_registry_path_resolves_under_data(self) -> None:
        self.assertEqual(registry_path(self.root, "t.json"), self.root / "data" / "t.json")


class SeamFieldReads(unittest.TestCase):
    """`load_registry_field` defaults for an absent field, never for a broken file."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "data").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, payload: object) -> None:
        (self.root / "data" / "t.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_present_field_is_returned(self) -> None:
        self._write({"limit": 7})
        self.assertEqual(load_registry_field(self.root, "t.json", "limit"), 7)

    def test_absent_field_returns_the_default(self) -> None:
        self._write({"other": 1})
        self.assertEqual(load_registry_field(self.root, "t.json", "limit", 3), 3)

    def test_missing_registry_raises_rather_than_defaulting(self) -> None:
        """Defaulting past a broken file is how a disarmed check reports green."""
        with self.assertRaises(RegistryError):
            load_registry_field(self.root, "absent.json", "limit", 3)

    def test_malformed_registry_raises_rather_than_defaulting(self) -> None:
        (self.root / "data" / "t.json").write_text("{nope", encoding="utf-8")
        with self.assertRaises(RegistryError):
            load_registry_field(self.root, "t.json", "limit", 3)

    def test_non_object_registry_raises(self) -> None:
        self._write(["a"])
        with self.assertRaises(RegistryError):
            load_registry_field(self.root, "t.json", "limit")


if __name__ == "__main__":
    unittest.main()
