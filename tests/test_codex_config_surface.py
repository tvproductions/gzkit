"""Codex config control-surface validation."""

from __future__ import annotations

import json
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig, PathConfig
from gzkit.sync import sync_all
from gzkit.sync_surfaces import (
    is_managed_codex_config,
    render_codex_config,
    sync_codex_config,
)
from gzkit.traceability import covers
from gzkit.validate_pkg.surface import _validate_codex_config


def _write_codex_surface(root: Path, config_text: str | None) -> None:
    codex_dir = root / ".codex"
    codex_dir.mkdir()
    (codex_dir / "hooks.json").write_text('{"hooks": {}}\n', encoding="utf-8")
    if config_text is not None:
        (codex_dir / "config.toml").write_text(config_text, encoding="utf-8")


class TestCodexConfigSurface(unittest.TestCase):
    """Codex hooks must be enabled through the current feature flag."""

    @covers("REQ-0.44.0-01-04")
    def test_missing_configured_codex_config_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            errors = _validate_codex_config(root)

            self.assertTrue(
                any(error.artifact == ".codex/config.toml" for error in errors),
                f"expected missing configured Codex config error, got {errors}",
            )

    @covers("REQ-0.44.0-01-04")
    def test_unmarked_operator_config_remains_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text('model = "gpt-5.4"\n', encoding="utf-8")

            errors = _validate_codex_config(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.44.0-01-04")
    def test_crlf_marker_is_recognized_as_managed(self) -> None:
        content = render_codex_config().replace("\n", "\r\n")

        self.assertTrue(is_managed_codex_config(content))
        self.assertTrue(is_managed_codex_config(content.encode()))

    @covers("REQ-0.44.0-01-04")
    def test_validation_resolves_custom_codex_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(codex_config="config/codex.toml"))
            config.save(root / ".gzkit.json")
            custom_path = root / "config" / "codex.toml"
            custom_path.parent.mkdir(parents=True)
            custom_path.write_text("[", encoding="utf-8")
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            default_path.write_text('model = "gpt-5.4"\n', encoding="utf-8")

            errors = _validate_codex_config(root)

            self.assertTrue(
                any(error.artifact == "config/codex.toml" for error in errors),
                f"expected validation at configured Codex path, got {errors}",
            )

    @covers("REQ-0.44.0-01-04")
    def test_validation_reports_preserved_default_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(codex_config="config/codex.toml"))
            config.save(root / ".gzkit.json")
            custom_path = root / "config" / "codex.toml"
            custom_path.parent.mkdir(parents=True)
            custom_path.write_text(render_codex_config(), encoding="utf-8")
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            default_path.write_text(
                render_codex_config() + '\nmodel = "gpt-5.4"\n',
                encoding="utf-8",
            )

            errors = _validate_codex_config(root)

            self.assertIn(".codex/config.toml", [error.artifact for error in errors])

    @covers("REQ-0.44.0-01-03")
    def test_default_path_alias_is_not_a_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(codex_config="x/../.codex/config.toml"))
            config.save(root / ".gzkit.json")
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(render_codex_config(), encoding="utf-8")

            errors = _validate_codex_config(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.44.0-01-04")
    def test_validation_rejects_codex_path_outside_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(codex_config="../config.toml"))
            config.save(root / ".gzkit.json")

            errors = _validate_codex_config(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("within the project root", errors[0].message)

    @covers("REQ-0.44.0-01-04")
    def test_marked_generated_config_drift_reports_stale_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = "# gzkit-managed-codex-config: v1"
            baseline = render_codex_config()
            if not baseline.startswith(marker):
                baseline = f"{marker}\n{baseline}"
            drifted = baseline.replace(
                'sandbox_mode = "workspace-write"',
                'sandbox_mode = "read-only"',
            )
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(drifted, encoding="utf-8")

            errors = _validate_codex_config(root)

            self.assertTrue(
                any("out of sync" in error.message for error in errors),
                f"expected stale managed-config error, got {errors}",
            )

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


class TestCodexConfigGeneration(unittest.TestCase):
    """Codex receives a usable project baseline during control-surface sync."""

    @covers("REQ-0.44.0-01-01")
    def test_sync_creates_codex_config_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)

            config_path = root / ".codex" / "config.toml"
            self.assertTrue(config_path.is_file(), "sync must create .codex/config.toml")
            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["sandbox_mode"], "workspace-write")
            self.assertIs(config["sandbox_workspace_write"]["network_access"], True)
            self.assertIs(config["features"]["hooks"], True)

    @covers("REQ-0.44.0-01-01")
    def test_sync_writes_codex_config_lf_byte_identical_to_render(self) -> None:
        """Synced .codex/config.toml is byte-identical to render_codex_config().

        The parity check in validate_pkg/sync_parity.py compares RAW bytes
        (read_bytes() vs render().encode()), so a text-mode write that
        translates \\n->\\r\\n on Windows produces spurious drift. read_text()
        normalizes newlines and would mask this; the contract is a raw-byte
        match on every platform (LF). GHI #681.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)
            written = (root / ".codex" / "config.toml").read_bytes()
            self.assertEqual(
                written,
                render_codex_config().encode(),
                "written codex config must be byte-identical to the render (LF), "
                "not CRLF-translated by text-mode write on Windows",
            )

    @covers("REQ-0.44.0-01-02")
    def test_sync_preserves_nonempty_operator_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            operator_config = b'model = "gpt-5.4"\napproval_policy = "on-request"\n'
            config_path.write_bytes(operator_config)

            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)

            self.assertEqual(config_path.read_bytes(), operator_config)

    @covers("REQ-0.44.0-01-02")
    def test_sync_preserves_customized_marked_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            operator_config = (
                render_codex_config() + '\nmodel = "gpt-5.4"\napproval_policy = "on-request"\n'
            ).encode()
            config_path.write_bytes(operator_config)

            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)

            self.assertEqual(config_path.read_bytes(), operator_config)

    @covers("REQ-0.44.0-01-02")
    def test_sync_preserves_marker_prefix_lookalike(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            operator_config = b'# gzkit-managed-codex-config: v1-operator\nmodel = "gpt-5.4"\n'
            config_path.write_bytes(operator_config)

            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)

            self.assertEqual(
                config_path.read_bytes(),
                operator_config,
                "a marker-prefix lookalike remains operator-owned",
            )

    @covers("REQ-0.44.0-01-02")
    def test_sync_initializes_zero_byte_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.touch()

            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)

            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["sandbox_mode"], "workspace-write")
            self.assertIs(config["sandbox_workspace_write"]["network_access"], True)
            self.assertIs(config["features"]["hooks"], True)

    @covers("REQ-0.44.0-01-03")
    def test_sync_writes_only_configured_codex_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custom_path = root / "config" / "codex.toml"
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="config/codex.toml"),
            )

            sync_all(root, config, emit_event=False)

            self.assertTrue(custom_path.is_file(), "sync must use PathConfig.codex_config")
            self.assertFalse(
                (root / ".codex" / "config.toml").exists(),
                "sync must not create a default-path duplicate",
            )
            manifest = json.loads((root / ".gzkit" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["control_surfaces"]["codex_config"], "config/codex.toml")

    @covers("REQ-0.44.0-01-03")
    def test_sync_retires_managed_default_when_path_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sync_all(root, GzkitConfig(project_name="demo"), emit_event=False)
            default_path = root / ".codex" / "config.toml"
            self.assertEqual(default_path.read_text(encoding="utf-8"), render_codex_config())
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="config/codex.toml"),
            )

            sync_all(root, config, emit_event=False)

            self.assertFalse(default_path.exists())
            self.assertTrue((root / "config" / "codex.toml").is_file())

    @covers("REQ-0.44.0-01-03")
    def test_sync_retires_zero_byte_default_when_path_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            default_path.touch()
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="config/codex.toml"),
            )

            sync_all(root, config, emit_event=False)

            self.assertFalse(default_path.exists())
            self.assertTrue((root / "config" / "codex.toml").is_file())

    @covers("REQ-0.44.0-01-03")
    def test_sync_treats_default_path_alias_as_the_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(render_codex_config(), encoding="utf-8")
            fixed_timestamp = 1_000_000_000
            os.utime(config_path, ns=(fixed_timestamp, fixed_timestamp))
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="x/../.codex/config.toml"),
            )

            sync_codex_config(root, config)

            self.assertEqual(config_path.stat().st_mtime_ns, fixed_timestamp)

    @covers("REQ-0.44.0-01-03")
    def test_sync_rejects_codex_path_outside_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="../config.toml"),
            )

            with self.assertRaisesRegex(ValueError, "within the project root"):
                sync_codex_config(root, config)

    @covers("REQ-0.44.0-01-04")
    def test_sync_preserves_and_reports_marked_config_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                render_codex_config().replace(
                    'sandbox_mode = "workspace-write"',
                    'sandbox_mode = "read-only"',
                ),
                encoding="utf-8",
            )

            config = GzkitConfig(project_name="demo")
            sync_all(root, config, emit_event=False)
            errors = _validate_codex_config(root)

            self.assertNotEqual(config_path.read_text(encoding="utf-8"), render_codex_config())
            self.assertTrue(any("out of sync" in error.message for error in errors))

    @covers("REQ-0.44.0-01-02")
    def test_sync_does_not_rewrite_current_managed_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(render_codex_config(), encoding="utf-8")
            fixed_timestamp = 1_000_000_000
            os.utime(config_path, ns=(fixed_timestamp, fixed_timestamp))

            sync_codex_config(root, GzkitConfig(project_name="demo"))

            self.assertEqual(config_path.stat().st_mtime_ns, fixed_timestamp)

    @covers("REQ-0.44.0-01-04")
    def test_committed_codex_config_matches_renderer(self) -> None:
        config_path = Path(__file__).parents[1] / ".codex" / "config.toml"

        self.assertEqual(config_path.read_text(encoding="utf-8"), render_codex_config())
