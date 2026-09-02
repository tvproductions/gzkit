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
from gzkit.config import GzkitConfig


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):
        return obj

    return _identity


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

    @covers("REQ-0.0.7-05-04")
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
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

    @covers("REQ-0.0.7-05-02")
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
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertTrue(len(issues) > 0)
            self.assertIn("unmapped path literal", issues[0]["issue"])

    @covers("REQ-0.0.7-05-02")
    def test_exempt_literal_not_flagged(self):
        """Path-shaped literals that are not config paths are exempt.

        A forbidden-pattern detector string (``ops/chores/``) and a template
        placeholder example (``config/file.json``) are path-shaped but name no
        real config location; mapping them to the manifest would be wrong, so
        the audit exempts them rather than demanding a mapping.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "detector.py").write_text(
                'FORBIDDEN = "ops/chores/"\nPLACEHOLDER = "config/file.json"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

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
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

    def test_missing_src_dir_no_issues(self):
        """If src/gzkit/ doesn't exist, no issues returned."""
        with tempfile.TemporaryDirectory() as tmp:
            issues = _collect_source_path_literal_issues(Path(tmp), SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()


class TestPathConfigDeclaredDefaults(unittest.TestCase):
    """A literal declared as a PathConfig default is governed by config.

    The scanner's question is "is this literal governed by config?", and
    ``GzkitConfig.paths`` is config. Before GHI #938 the scanner consulted the
    manifest alone, so a declared ``PathConfig`` default was reported unmapped
    -- including at the ``config.py`` line that declares it.
    """

    @covers("REQ-0.0.7-05-02")
    def test_declared_default_not_flagged(self):
        """A literal equal to a PathConfig default is not an unmapped literal."""
        config = GzkitConfig()
        # Precondition: the manifest genuinely does not carry this path, so a
        # pass can only come from config coverage, never from manifest overlap.
        self.assertFalse(
            _is_path_covered_by_manifest(
                config.paths.discovery_index, _flatten_manifest_paths(SAMPLE_MANIFEST)
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "declares.py").write_text(
                f'discovery_index: str = "{config.paths.discovery_index}"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, config)
            self.assertEqual(issues, [])

    @covers("REQ-0.0.7-05-02")
    def test_undeclared_sibling_still_flagged(self):
        """Config coverage is exact: a sibling under the same root stays flagged.

        Boundary test. Deriving parent directories from config defaults would
        make ``.github`` itself covered and silently exempt every ``.github/**``
        literal, which is the opposite of what the audit is for.
        """
        config = GzkitConfig()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "sibling.py").write_text(
                'legacy = ".github/skills"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, config)
            self.assertEqual(len(issues), 1)
            self.assertIn(".github/skills", issues[0]["issue"])
