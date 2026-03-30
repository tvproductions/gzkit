"""Tests for config-paths source path literal scanning.

@covers OBPI-0.0.7-05-lint-rule-and-check-expansion
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.config_paths import (
    _collect_source_path_literal_issues,
    _flatten_manifest_paths,
    _is_path_covered_by_manifest,
)

SAMPLE_MANIFEST = {
    "structure": {
        "source_root": "src",
        "tests_root": "tests",
        "docs_root": "docs",
        "design_root": "docs/design",
    },
    "data": {
        "eval_datasets": "data/eval",
        "schemas": "data/schemas",
    },
    "ops": {
        "chores": "config/chores",
    },
    "artifacts": {
        "adr": {"path": "docs/design/adr"},
    },
    "control_surfaces": {
        "skills": ".gzkit/skills",
    },
}


class TestFlattenManifestPaths(unittest.TestCase):
    """Verify manifest path extraction."""

    def test_extracts_known_paths(self):
        paths = _flatten_manifest_paths(SAMPLE_MANIFEST)
        self.assertIn("data/eval", paths)
        self.assertIn("docs/design", paths)
        self.assertIn("docs/design/adr", paths)
        self.assertIn(".gzkit/skills", paths)

    def test_empty_manifest(self):
        paths = _flatten_manifest_paths({})
        self.assertEqual(paths, set())


class TestIsPathCovered(unittest.TestCase):
    """Verify path coverage matching logic."""

    def test_exact_match(self):
        self.assertTrue(_is_path_covered_by_manifest("data/eval", {"data/eval"}))

    def test_prefix_match(self):
        self.assertTrue(_is_path_covered_by_manifest("data/eval/scores.json", {"data/eval"}))

    def test_parent_match(self):
        self.assertTrue(_is_path_covered_by_manifest("data", {"data/eval"}))

    def test_no_match(self):
        self.assertFalse(_is_path_covered_by_manifest("unknown/dir", {"data/eval"}))

    def test_partial_segment_no_match(self):
        """data/evaluate should NOT match data/eval."""
        self.assertFalse(_is_path_covered_by_manifest("data/evaluate", {"data/eval"}))


class TestSourcePathLiteralScan(unittest.TestCase):
    """Verify source scanning detects unmapped path literals."""

    def test_clean_source_no_issues(self):
        """Source with only manifest-mapped paths produces no issues."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "clean.py").write_text(
                'path = "data/eval"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST)
            self.assertEqual(issues, [])

    def test_unmapped_literal_flagged(self):
        """Source with a path literal not in manifest is flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            # Use a directory root not present in SAMPLE_MANIFEST
            (src / "bad.py").write_text(
                'output_dir = "artifacts/unknown/reports"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST)
            self.assertTrue(len(issues) > 0)
            self.assertIn("unmapped path literal", issues[0]["issue"])

    def test_url_not_flagged(self):
        """HTTP URLs are not treated as path literals."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "url.py").write_text(
                'endpoint = "https://docs/design/api"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST)
            self.assertEqual(issues, [])

    def test_missing_src_dir_no_issues(self):
        """If src/gzkit/ doesn't exist, no issues returned."""
        with tempfile.TemporaryDirectory() as tmp:
            issues = _collect_source_path_literal_issues(Path(tmp), SAMPLE_MANIFEST)
            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
