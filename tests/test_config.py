"""Tests for gzkit configuration."""

import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig, PathConfig


class TestPathConfig(unittest.TestCase):
    """Tests for PathConfig dataclass."""

    def test_defaults(self) -> None:
        """PathConfig has sensible defaults."""
        config = PathConfig()
        self.assertEqual(config.prd, "design/prd")
        self.assertEqual(config.constitutions, "design/constitutions")
        self.assertEqual(config.obpis, "design/obpis")
        self.assertEqual(config.adrs, "design/adr")
        self.assertEqual(config.source_root, "src")
        self.assertEqual(config.tests_root, "tests")

    def test_gzkit_paths(self) -> None:
        """PathConfig has gzkit internal paths."""
        config = PathConfig()
        self.assertEqual(config.gzkit_dir, ".gzkit")
        self.assertEqual(config.ledger, ".gzkit/ledger.jsonl")
        self.assertEqual(config.manifest, ".gzkit/manifest.json")
        self.assertEqual(config.claude_skills, ".claude/skills")


class TestGzkitConfig(unittest.TestCase):
    """Tests for GzkitConfig."""

    def test_defaults(self) -> None:
        """GzkitConfig has sensible defaults."""
        config = GzkitConfig()
        self.assertEqual(config.mode, "lite")
        self.assertIsInstance(config.paths, PathConfig)

    def test_load__missing_file__returns_defaults(self) -> None:
        """Loading from missing file returns defaults."""
        config = GzkitConfig.load(Path("/nonexistent/.gzkit.json"))
        self.assertEqual(config.mode, "lite")

    def test_load__valid_file__parses_correctly(self) -> None:
        """Loading from valid file parses configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"mode":"heavy","paths":{"prd":"custom/prd","adrs":"custom/adr"}}')
            f.flush()

            config = GzkitConfig.load(Path(f.name))
            self.assertEqual(config.mode, "heavy")
            self.assertEqual(config.paths.prd, "custom/prd")
            self.assertEqual(config.paths.adrs, "custom/adr")

    def test_save__roundtrip(self) -> None:
        """Saved config can be loaded back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"

            original = GzkitConfig(
                mode="heavy",
                paths=PathConfig(prd="my/prd", adrs="my/adr"),
            )
            original.save(config_path)

            loaded = GzkitConfig.load(config_path)
            self.assertEqual(loaded.mode, "heavy")
            self.assertEqual(loaded.paths.prd, "my/prd")

    def test_get_path(self) -> None:
        """get_path returns Path object."""
        config = GzkitConfig()
        path = config.get_path("prd")
        self.assertIsInstance(path, Path)
        self.assertEqual(str(path), "design/prd")


if __name__ == "__main__":
    unittest.main()
