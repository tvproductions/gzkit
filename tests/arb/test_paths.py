"""Tests for gzkit.arb.paths.

@covers REQ-0.25.0-33-03
"""

import os
import tempfile
import unittest
from pathlib import Path


class TestReceiptsRoot(unittest.TestCase):
    """receipts_root() returns the configured directory, creating it on demand."""

    def test_default_path_from_config(self) -> None:
        """Default config maps to artifacts/receipts under the project root."""
        from gzkit.arb.paths import receipts_root
        from gzkit.config import GzkitConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()
            root = receipts_root(config=config, project_root=project_root)
            self.assertEqual(root, project_root / "artifacts" / "receipts")
            self.assertTrue(root.exists())
            self.assertTrue(root.is_dir())

    def test_custom_receipts_root(self) -> None:
        """A custom arb.receipts_root is honored."""
        from gzkit.arb.paths import receipts_root
        from gzkit.config import ArbConfig, GzkitConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(arb=ArbConfig(receipts_root="custom/arb"))
            root = receipts_root(config=config, project_root=project_root)
            self.assertEqual(root, project_root / "custom" / "arb")
            self.assertTrue(root.exists())

    def test_env_override(self) -> None:
        """GZKIT_ARB_RECEIPTS_ROOT env var overrides config (for tests)."""
        from gzkit.arb.paths import receipts_root
        from gzkit.config import GzkitConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            override = Path(tmpdir) / "env-override"
            prior = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
            os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(override)
            try:
                root = receipts_root(config=GzkitConfig(), project_root=Path(tmpdir))
            finally:
                if prior is None:
                    os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
                else:
                    os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = prior
            self.assertEqual(root, override)
            self.assertTrue(root.exists())

    def test_auto_load_config_when_not_provided(self) -> None:
        """Calling receipts_root() without arguments loads config from cwd."""
        from gzkit.arb.paths import receipts_root

        with tempfile.TemporaryDirectory() as tmpdir:
            previous = Path.cwd()
            try:
                os.chdir(tmpdir)
                prior_env = os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
                try:
                    root = receipts_root()
                finally:
                    if prior_env is not None:
                        os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = prior_env
            finally:
                os.chdir(previous)
            self.assertEqual(root.name, "receipts")
            self.assertEqual(root.parent.name, "artifacts")
