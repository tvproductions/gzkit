"""Codex config control-surface validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.validate_pkg.surface import _validate_codex_config


def _write_codex_surface(root: Path, config_text: str | None) -> None:
    codex_dir = root / ".codex"
    codex_dir.mkdir()
    (codex_dir / "hooks.json").write_text('{"hooks": {}}\n', encoding="utf-8")
    if config_text is not None:
        (codex_dir / "config.toml").write_text(config_text, encoding="utf-8")


class TestCodexConfigSurface(unittest.TestCase):
    """Codex hooks must be enabled through the current feature flag."""

    def test_deprecated_codex_hooks_feature_fails_close(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_codex_surface(
                root,
                'sandbox_mode = "workspace-write"\n[features]\ncodex_hooks = true\n',
            )

            errors = _validate_codex_config(root)

            self.assertTrue(
                any(error.field == "features.codex_hooks" for error in errors),
                f"expected deprecated codex_hooks error, got {errors}",
            )

    def test_hooks_json_requires_current_hooks_feature_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_codex_surface(root, 'sandbox_mode = "workspace-write"\n')

            errors = _validate_codex_config(root)

            self.assertTrue(
                any(error.field == "features.hooks" for error in errors),
                f"expected missing features.hooks error, got {errors}",
            )

    def test_missing_config_with_hooks_json_fails_close(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_codex_surface(root, None)

            errors = _validate_codex_config(root)

            self.assertTrue(
                any(error.field == "features.hooks" for error in errors),
                f"expected missing config error, got {errors}",
            )

    def test_current_hooks_feature_flag_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_codex_surface(
                root,
                'sandbox_mode = "workspace-write"\n[features]\nhooks = true\n',
            )

            errors = _validate_codex_config(root)

            self.assertEqual(errors, [])
