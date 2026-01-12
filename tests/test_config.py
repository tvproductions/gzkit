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
        self.assertEqual(config.canon, "docs/canon")
        self.assertEqual(config.adrs, "docs/adr")
        self.assertEqual(config.specs, "docs/specs")
        self.assertEqual(config.audits, "docs/audit")


class TestGzkitConfig(unittest.TestCase):
    """Tests for GzkitConfig."""

    def test_defaults(self) -> None:
        """GzkitConfig has sensible defaults."""
        config = GzkitConfig()
        self.assertEqual(config.mode, "lite")
        self.assertIsInstance(config.paths, PathConfig)

    def test_load__missing_file__returns_defaults(self) -> None:
        """Loading from missing file returns defaults."""
        config = GzkitConfig.load(Path("/nonexistent/.gzkit.yaml"))
        self.assertEqual(config.mode, "lite")

    def test_load__valid_file__parses_correctly(self) -> None:
        """Loading from valid file parses configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("mode: heavy\n")
            f.write("paths:\n")
            f.write("  canon: custom/canon\n")
            f.write("  adrs: custom/adr\n")
            f.flush()

            config = GzkitConfig.load(Path(f.name))
            self.assertEqual(config.mode, "heavy")
            self.assertEqual(config.paths.canon, "custom/canon")
            self.assertEqual(config.paths.adrs, "custom/adr")

    def test_save__roundtrip(self) -> None:
        """Saved config can be loaded back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.yaml"

            original = GzkitConfig(
                mode="heavy",
                paths=PathConfig(canon="my/canon", adrs="my/adr"),
            )
            original.save(config_path)

            loaded = GzkitConfig.load(config_path)
            self.assertEqual(loaded.mode, "heavy")
            self.assertEqual(loaded.paths.canon, "my/canon")


if __name__ == "__main__":
    unittest.main()
