"""Tests for the load_config() parameter-injection entry point.

`load_config(path=...)` is gzkit's canonical config seam (the hexagonal
injection point per the 2026-07-06 ruling that blessed parameter injection as
the canonical hexagon). The former `FileConfigStore` adapter — a ConfigStore
Protocol impl that duplicated this function and was wired into zero production
code — was retired with REQ-0.0.3-05-03 superseded. See
docs/governance/hexagonal-architecture.md.
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig, load_config
from gzkit.traceability import covers


class TestLoadConfigDefaults(unittest.TestCase):
    """load_config() returns frozen GzkitConfig with defaults."""

    @covers("REQ-0.0.3-05-01")
    def test_missing_file_returns_defaults(self) -> None:
        """load_config() with missing file returns Pydantic defaults."""
        config = load_config(path=Path("/nonexistent/.gzkit.json"))
        self.assertIsInstance(config, GzkitConfig)
        self.assertEqual(config.mode, "lite")
        self.assertEqual(config.project_name, "")

    @covers("REQ-0.0.3-05-02")
    def test_returns_frozen_config(self) -> None:
        """Returned config is frozen (immutable)."""
        from pydantic import ValidationError

        config = load_config(path=Path("/nonexistent/.gzkit.json"))
        with self.assertRaises(ValidationError):
            config.mode = "heavy"  # type: ignore[misc]


class TestLoadConfigPrecedence(unittest.TestCase):
    """load_config() respects the 3-layer precedence chain."""

    def test_file_layer_overrides_defaults(self) -> None:
        """Config file values override Pydantic defaults (layer 2 > layer 1)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"
            config_path.write_text(
                json.dumps({"mode": "heavy", "project_name": "myproject"}),
                encoding="utf-8",
            )
            config = load_config(path=config_path)
            self.assertEqual(config.mode, "heavy")
            self.assertEqual(config.project_name, "myproject")

    @covers("REQ-0.0.3-05-07")
    def test_cli_overrides_override_file(self) -> None:
        """CLI overrides beat config file values (layer 3 > layer 2)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"
            config_path.write_text(
                json.dumps({"mode": "heavy", "project_name": "from-file"}),
                encoding="utf-8",
            )
            cli = {"mode": "lite", "project_name": "from-cli"}
            config = load_config(path=config_path, cli_overrides=cli)
            self.assertEqual(config.mode, "lite")
            self.assertEqual(config.project_name, "from-cli")

    def test_cli_partial_override(self) -> None:
        """Only CLI keys present are applied; others retain file values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"
            config_path.write_text(
                json.dumps({"mode": "heavy", "project_name": "original"}),
                encoding="utf-8",
            )
            config = load_config(path=config_path, cli_overrides={"project_name": "override"})
            self.assertEqual(config.mode, "heavy")
            self.assertEqual(config.project_name, "override")

    def test_no_cli_overrides_returns_file_config(self) -> None:
        """load_config() with no CLI overrides returns file config directly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"
            config_path.write_text(json.dumps({"mode": "heavy"}), encoding="utf-8")
            config = load_config(path=config_path)
            self.assertEqual(config.mode, "heavy")

    def test_none_cli_overrides_is_safe(self) -> None:
        """load_config() with cli_overrides=None does not crash."""
        config = load_config(
            path=Path("/nonexistent/.gzkit.json"),
            cli_overrides=None,
        )
        self.assertEqual(config.mode, "lite")

    def test_empty_cli_overrides_returns_file_config(self) -> None:
        """Empty CLI overrides dict returns file config unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"
            config_path.write_text(json.dumps({"mode": "heavy"}), encoding="utf-8")
            config = load_config(path=config_path, cli_overrides={})
            self.assertEqual(config.mode, "heavy")

    @covers("REQ-0.0.3-05-04")
    def test_no_env_parameter_exists(self) -> None:
        """load_config() does not accept an env parameter."""
        import inspect

        sig = inspect.signature(load_config)
        self.assertNotIn("env", sig.parameters)


if __name__ == "__main__":
    unittest.main()
