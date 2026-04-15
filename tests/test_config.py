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
        self.assertEqual(config.obpis, "design/adr")
        self.assertEqual(config.adrs, "design/adr")
        self.assertEqual(config.source_root, "src")
        self.assertEqual(config.tests_root, "tests")

    def test_gzkit_paths(self) -> None:
        """PathConfig has gzkit internal paths."""
        config = PathConfig()
        self.assertEqual(config.gzkit_dir, ".gzkit")
        self.assertEqual(config.ledger, ".gzkit/ledger.jsonl")
        self.assertEqual(config.manifest, ".gzkit/manifest.json")
        self.assertEqual(config.skills, ".gzkit/skills")
        self.assertEqual(config.canonical_rules, ".gzkit/rules")
        self.assertEqual(config.canonical_schemas, ".gzkit/schemas")
        self.assertEqual(config.claude_skills, ".claude/skills")
        self.assertEqual(config.codex_skills, ".agents/skills")
        self.assertEqual(config.copilot_skills, ".github/skills")


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
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text(
                '{"mode":"heavy","paths":{"prd":"custom/prd","adrs":"custom/adr"}}',
                encoding="utf-8",
            )

            config = GzkitConfig.load(config_file)
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
        self.assertEqual(path.as_posix(), "design/prd")


class TestVendorConfig(unittest.TestCase):
    """Tests for VendorConfig model."""

    def test_defaults(self) -> None:
        """VendorConfig defaults to disabled with empty surface_root."""
        from gzkit.config import VendorConfig

        config = VendorConfig()
        self.assertFalse(config.enabled)
        self.assertEqual(config.surface_root, "")
        self.assertEqual(config.instruction_format, "generic")

    def test_frozen(self) -> None:
        """VendorConfig is immutable."""
        from pydantic import ValidationError

        from gzkit.config import VendorConfig

        config = VendorConfig(enabled=True, surface_root=".claude")
        with self.assertRaises(ValidationError):
            config.enabled = False


class TestArbConfig(unittest.TestCase):
    """Tests for ArbConfig — ARB receipt middleware configuration.

    @covers REQ-0.25.0-33-03
    """

    def test_defaults(self) -> None:
        """ArbConfig defaults to artifacts/receipts and limit 20."""
        from gzkit.config import ArbConfig

        config = ArbConfig()
        self.assertEqual(config.receipts_root, "artifacts/receipts")
        self.assertEqual(config.default_limit, 20)

    def test_frozen(self) -> None:
        """ArbConfig is immutable."""
        from pydantic import ValidationError

        from gzkit.config import ArbConfig

        config = ArbConfig()
        with self.assertRaises(ValidationError):
            config.receipts_root = "other/path"

    def test_gzkit_config_exposes_arb(self) -> None:
        """GzkitConfig has an arb section with defaults."""
        from gzkit.config import ArbConfig

        config = GzkitConfig()
        self.assertIsInstance(config.arb, ArbConfig)
        self.assertEqual(config.arb.receipts_root, "artifacts/receipts")

    def test_arb_roundtrip_through_gzkit_config(self) -> None:
        """GzkitConfig round-trips an explicit arb section via save/load."""
        from gzkit.config import ArbConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".gzkit.json"

            original = GzkitConfig(
                arb=ArbConfig(receipts_root="custom/receipts", default_limit=50),
            )
            original.save(config_path)

            loaded = GzkitConfig.load(config_path)
            self.assertEqual(loaded.arb.receipts_root, "custom/receipts")
            self.assertEqual(loaded.arb.default_limit, 50)

    def test_extra_forbid(self) -> None:
        """VendorConfig rejects unknown fields."""
        from pydantic import ValidationError

        from gzkit.config import VendorConfig

        with self.assertRaises(ValidationError):
            VendorConfig(enabled=True, unknown_field="x")  # type: ignore[call-arg]


class TestVendorsConfig(unittest.TestCase):
    """Tests for VendorsConfig model."""

    def test_defaults__claude_enabled(self) -> None:
        """Claude is enabled by default."""
        from gzkit.config import VendorsConfig

        config = VendorsConfig()
        self.assertTrue(config.claude.enabled)
        self.assertEqual(config.claude.surface_root, ".claude")
        self.assertEqual(config.claude.instruction_format, "claude-rules")

    def test_defaults__others_disabled(self) -> None:
        """Non-Claude vendors are disabled by default."""
        from gzkit.config import VendorsConfig

        config = VendorsConfig()
        self.assertFalse(config.copilot.enabled)
        self.assertFalse(config.codex.enabled)
        self.assertFalse(config.gemini.enabled)
        self.assertFalse(config.opencode.enabled)

    def test_vendor_surface_roots(self) -> None:
        """Each vendor has the correct surface_root."""
        from gzkit.config import VendorsConfig

        config = VendorsConfig()
        self.assertEqual(config.copilot.surface_root, ".github")
        self.assertEqual(config.codex.surface_root, ".agents")
        self.assertEqual(config.gemini.surface_root, ".gemini")
        self.assertEqual(config.opencode.surface_root, ".opencode")


class TestGzkitConfigVendors(unittest.TestCase):
    """Tests for vendor integration in GzkitConfig."""

    def test_config_has_vendors(self) -> None:
        """GzkitConfig includes vendors field with defaults."""
        config = GzkitConfig()
        self.assertTrue(config.vendors.claude.enabled)
        self.assertFalse(config.vendors.copilot.enabled)

    def test_load__no_vendors__uses_defaults(self) -> None:
        """Loading config without vendors key uses defaults (backward compat)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text('{"mode":"lite","paths":{}}', encoding="utf-8")

            config = GzkitConfig.load(config_file)
            self.assertTrue(config.vendors.claude.enabled)
            self.assertFalse(config.vendors.copilot.enabled)

    def test_load__with_vendors__parses(self) -> None:
        """Loading config with vendors key parses vendor enablement."""
        import json

        data = {
            "mode": "lite",
            "paths": {},
            "vendors": {
                "claude": {
                    "enabled": True,
                    "surface_root": ".claude",
                    "instruction_format": "claude-rules",
                },
                "copilot": {
                    "enabled": True,
                    "surface_root": ".github",
                    "instruction_format": "github-instructions",
                },
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()

            config = GzkitConfig.load(Path(f.name))
            self.assertTrue(config.vendors.claude.enabled)
            self.assertTrue(config.vendors.copilot.enabled)
            self.assertFalse(config.codex.enabled) if hasattr(config, "codex") else None  # type: ignore[unresolved-attribute]
            # Unspecified vendors get defaults
            self.assertFalse(config.vendors.codex.enabled)

    def test_canonical_check__config_vendors_claude_enabled(self) -> None:
        """config.vendors.claude.enabled is the canonical vendor check."""
        config = GzkitConfig()
        self.assertIs(config.vendors.claude.enabled, True)


class TestGatesRemoved(unittest.TestCase):
    """Tests confirming config.gates prototype has been removed (OBPI-0.0.8-07)."""

    def test_no_gates_field(self) -> None:
        """GzkitConfig no longer has a gates field."""
        config = GzkitConfig()
        self.assertFalse(hasattr(config, "gates"))

    def test_no_gate_method(self) -> None:
        """GzkitConfig no longer has a gate() method."""
        config = GzkitConfig()
        self.assertFalse(hasattr(config, "gate"))

    def test_gates_in_config_rejected(self) -> None:
        """Constructing GzkitConfig with gates= raises ValidationError."""
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            GzkitConfig(gates={"product_proof": "advisory"})

    def test_load__without_gates__clean(self) -> None:
        """Config without gates key loads cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text('{"mode":"lite","paths":{}}', encoding="utf-8")

            config = GzkitConfig.load(config_file)
            self.assertEqual(config.mode, "lite")
            self.assertFalse(hasattr(config, "gates"))

    def test_load__with_stale_gates__warns(self) -> None:
        """Config with stale gates key emits DeprecationWarning and loads."""
        import json
        import warnings

        data = {"mode": "lite", "paths": {}, "gates": {"product_proof": "advisory"}}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text(json.dumps(data), encoding="utf-8")

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                config = GzkitConfig.load(config_file)

            self.assertEqual(config.mode, "lite")
            deprecation_warnings = [w for w in caught if issubclass(w.category, DeprecationWarning)]
            self.assertEqual(len(deprecation_warnings), 1)
            self.assertIn("gates", str(deprecation_warnings[0].message))
            self.assertIn("flags", str(deprecation_warnings[0].message))


if __name__ == "__main__":
    unittest.main()
