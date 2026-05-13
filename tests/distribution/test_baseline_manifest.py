"""Unit tests for the distribution baseline manifest (OBPI-0.0.32-06).

Validates that data/distribution_baseline_manifest.json (a) parses against
the frozen schema, (b) every entry resolves to a real file under
src/gzkit/<surface>/, and (c) contains no duplicate entries within any
surface.

@covers REQ-0.0.32-06-05
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST_PATH = _PROJECT_ROOT / "data" / "distribution_baseline_manifest.json"
_GZKIT_SRC = _PROJECT_ROOT / "src" / "gzkit"

_REQUIRED_SURFACES = ("skills", "rules", "personas", "templates")


def _load_manifest() -> dict:
    with _MANIFEST_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class TestManifestSchemaValidation(unittest.TestCase):
    """Manifest parses against the frozen schema."""

    def setUp(self) -> None:
        self.manifest = _load_manifest()

    def test_schema_version_is_1_0(self) -> None:
        self.assertEqual(self.manifest["schema_version"], "1.0")

    def test_gzkit_version_present(self) -> None:
        version = self.manifest["gzkit_version"]
        self.assertIsInstance(version, str)
        self.assertTrue(version, "gzkit_version must not be empty")

    def test_surfaces_is_dict(self) -> None:
        self.assertIsInstance(self.manifest["surfaces"], dict)

    def test_required_surfaces_present(self) -> None:
        for surface in _REQUIRED_SURFACES:
            self.assertIn(surface, self.manifest["surfaces"], f"missing surface: {surface}")

    def test_surface_lists_are_lists_of_strings(self) -> None:
        for surface in _REQUIRED_SURFACES:
            entries = self.manifest["surfaces"][surface]
            self.assertIsInstance(entries, list, f"{surface} must be a list")
            for entry in entries:
                self.assertIsInstance(entry, str, f"{surface} entry not str: {entry!r}")


class TestManifestFileResolution(unittest.TestCase):
    """Every manifest entry resolves to a real file under src/gzkit/<surface>/."""

    def setUp(self) -> None:
        self.manifest = _load_manifest()

    def _assert_entries_resolve(self, surface: str) -> None:
        entries = self.manifest["surfaces"][surface]
        for entry in entries:
            path = _GZKIT_SRC / surface / entry
            self.assertTrue(
                path.is_file(),
                f"manifest entry {surface}/{entry} does not resolve to a real file at {path}",
            )

    def test_skills_resolve_to_real_files(self) -> None:
        self._assert_entries_resolve("skills")

    def test_rules_resolve_to_real_files(self) -> None:
        self._assert_entries_resolve("rules")

    def test_personas_resolve_to_real_files(self) -> None:
        self._assert_entries_resolve("personas")

    def test_templates_resolve_to_real_files(self) -> None:
        self._assert_entries_resolve("templates")

    def test_skills_count_floor(self) -> None:
        self.assertGreaterEqual(
            len(self.manifest["surfaces"]["skills"]),
            50,
            "Manifest should track at least 50 active (non-retired) skills",
        )

    def test_rules_count_floor(self) -> None:
        self.assertGreaterEqual(
            len(self.manifest["surfaces"]["rules"]),
            14,
            "REQ-0.0.32-06-09 expects at least 14 rule .md files",
        )


class TestManifestDuplicateDetection(unittest.TestCase):
    """No surface contains duplicate entries."""

    def setUp(self) -> None:
        self.manifest = _load_manifest()

    def _assert_no_duplicates(self, surface: str) -> None:
        entries = self.manifest["surfaces"][surface]
        seen: dict[str, int] = {}
        for entry in entries:
            seen[entry] = seen.get(entry, 0) + 1
        duplicates = {k: v for k, v in seen.items() if v > 1}
        self.assertFalse(duplicates, f"duplicates in {surface}: {duplicates}")

    def test_no_duplicate_skills(self) -> None:
        self._assert_no_duplicates("skills")

    def test_no_duplicate_rules(self) -> None:
        self._assert_no_duplicates("rules")

    def test_no_duplicate_personas(self) -> None:
        self._assert_no_duplicates("personas")

    def test_no_duplicate_templates(self) -> None:
        self._assert_no_duplicates("templates")


if __name__ == "__main__":
    unittest.main()
