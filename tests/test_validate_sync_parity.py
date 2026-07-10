"""Sync parity validation for generated control surfaces (GHI #134)."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.traceability import covers
from gzkit.validate_pkg.sync_parity import check_sync_parity, snapshot_surfaces
from tests.commands.common import CliRunner

_uv_sync_patcher = patch("gzkit.commands.init_cmd._run_uv_sync", return_value=None)

# Module-level state: a single ``gz init`` run and a single ``sync_all`` pass to
# capture the expected surface bytes. Every test then compares its tree against
# the cached expected state via ``check_sync_parity(expected=...)`` — the
# expensive ``sync_all`` pass no longer runs per test (GHI #253).
_tmpctx: tempfile.TemporaryDirectory | None = None
_project_dir: Path | None = None
_orig_cwd: Path | None = None
_expected_surfaces: dict[Path, bytes] = {}


def setUpModule() -> None:
    """Stub ``uv sync``, run ``gz init`` once, and cache expected surface bytes."""
    global _tmpctx, _project_dir, _orig_cwd, _expected_surfaces
    _uv_sync_patcher.start()
    _orig_cwd = Path.cwd()
    _tmpctx = tempfile.TemporaryDirectory(prefix="gzkit-parity-")
    _project_dir = Path(_tmpctx.name) / "project"
    _project_dir.mkdir()
    os.chdir(_project_dir)
    CliRunner().invoke(main, ["init"])
    # ``gz init`` just produced a fully-synced tree, so snapshotting it is
    # equivalent to (and far cheaper than) running ``sync_all`` again via
    # ``compute_expected_surfaces``.
    _expected_surfaces = snapshot_surfaces(_project_dir)


def tearDownModule() -> None:
    global _tmpctx, _project_dir, _orig_cwd, _expected_surfaces
    try:
        if _orig_cwd is not None:
            os.chdir(_orig_cwd)
    finally:
        if _tmpctx is not None:
            _tmpctx.cleanup()
        _tmpctx = None
        _project_dir = None
        _orig_cwd = None
        _expected_surfaces = {}
        _uv_sync_patcher.stop()


class _SyncParityBase(unittest.TestCase):
    """Snapshot any files a test mutates and restore them in tearDown."""

    # Subclasses override with paths (relative to project root) they may mutate.
    _mutable_paths: tuple[str, ...] = ()

    def setUp(self) -> None:
        assert _project_dir is not None
        if Path.cwd() != _project_dir:
            os.chdir(_project_dir)
        self._snapshots: dict[Path, str] = {}
        for rel in self._mutable_paths:
            p = Path(rel)
            if p.exists():
                self._snapshots[p] = p.read_text(encoding="utf-8")

    def tearDown(self) -> None:
        for p, content in self._snapshots.items():
            p.write_text(content, encoding="utf-8")


class SyncParityCleanTreeTest(_SyncParityBase):
    """A freshly initialized project has no sync parity drift."""

    def test_clean_init_reports_no_drift(self) -> None:
        errors = check_sync_parity(Path.cwd(), expected=_expected_surfaces)
        self.assertEqual(
            [],
            [(e.artifact, e.message) for e in errors],
            f"expected clean parity; got {[(e.artifact, e.message) for e in errors]}",
        )

    def test_default_sync_parity_check_does_not_emit_ledger_event(self) -> None:
        """Validation parity checks are read-only and must not attest sync."""
        ledger = Path(".gzkit/ledger.jsonl")
        before = ledger.read_text(encoding="utf-8")

        check_sync_parity(Path.cwd())

        after = ledger.read_text(encoding="utf-8")
        self.assertEqual(
            before,
            after,
            "check_sync_parity must call sync_all with emit_event=False",
        )


class SyncParityContentDriftTest(_SyncParityBase):
    """A hand-edited generated surface must surface as drift."""

    _mutable_paths = ("AGENTS.md",)

    def test_hand_edited_agents_md_reports_drift(self) -> None:
        agents_md = Path("AGENTS.md")
        original = agents_md.read_text(encoding="utf-8")
        agents_md.write_text(
            original + "\n\n<!-- hand-edited drift marker -->\n",
            encoding="utf-8",
        )

        errors = check_sync_parity(Path.cwd(), expected=_expected_surfaces)
        drift_artifacts = [e.artifact for e in errors]
        self.assertIn("AGENTS.md", drift_artifacts)

    def test_hand_edited_claude_hook_reports_drift(self) -> None:
        hook_file = next(Path(".claude/hooks").glob("*.py"), None)
        self.assertIsNotNone(hook_file, ".claude/hooks must be populated after init")
        assert hook_file is not None
        # Snapshot this specific hook so tearDown restores it even though the
        # class-level _mutable_paths doesn't know which hook file we picked.
        self._snapshots[hook_file] = hook_file.read_text(encoding="utf-8")
        hook_file.write_text(
            hook_file.read_text(encoding="utf-8") + "\n# rogue hand-edit\n",
            encoding="utf-8",
        )

        errors = check_sync_parity(Path.cwd(), expected=_expected_surfaces)
        drift_artifacts = [e.artifact for e in errors]
        self.assertTrue(
            any(".claude/hooks" in a for a in drift_artifacts),
            f"expected .claude/hooks drift; got {drift_artifacts}",
        )


class SyncParityRestoresSnapshotTest(_SyncParityBase):
    """The parity check must not mutate the tree after it finishes."""

    _mutable_paths = ("AGENTS.md",)

    def test_hand_edited_surface_is_restored_after_check(self) -> None:
        agents_md = Path("AGENTS.md")
        drifted = agents_md.read_text(encoding="utf-8") + "\nextra\n"
        agents_md.write_text(drifted, encoding="utf-8")

        errors = check_sync_parity(Path.cwd(), expected=_expected_surfaces)
        self.assertTrue(errors, "expected drift to be reported")

        self.assertEqual(
            drifted,
            agents_md.read_text(encoding="utf-8"),
            "check_sync_parity must restore the pre-check file state",
        )


class CodexConfigSyncParityTest(_SyncParityBase):
    """Managed Codex config participates in non-mutating parity validation."""

    _mutable_paths = (".codex/config.toml",)

    @covers("REQ-0.44.0-01-04")
    def test_missing_managed_config_is_reported_and_remains_missing(self) -> None:
        config_path = Path(".codex/config.toml")
        config_path.unlink()

        errors = check_sync_parity(Path.cwd())

        messages = [error.message for error in errors if error.artifact == ".codex/config.toml"]
        self.assertTrue(
            any("missing" in message.lower() for message in messages),
            f"expected missing Codex config parity error, got {messages}",
        )
        self.assertFalse(config_path.exists(), "parity validation must restore missing state")

    @covers("REQ-0.44.0-01-04")
    def test_marked_config_drift_is_reported_and_restored(self) -> None:
        config_path = Path(".codex/config.toml")
        drifted = config_path.read_text(encoding="utf-8").replace(
            'sandbox_mode = "workspace-write"',
            'sandbox_mode = "read-only"',
        )
        config_path.write_text(drifted, encoding="utf-8")

        errors = check_sync_parity(Path.cwd())

        self.assertIn(".codex/config.toml", [error.artifact for error in errors])
        self.assertEqual(
            config_path.read_text(encoding="utf-8"),
            drifted,
            "parity validation must restore the caller's drifted bytes",
        )

    @covers("REQ-0.44.0-01-04")
    def test_custom_managed_config_path_is_reported_and_restored(self) -> None:
        from gzkit.config import GzkitConfig, PathConfig
        from gzkit.sync_surfaces import render_codex_config, sync_all

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="config/codex.toml"),
            )
            config.save(root / ".gzkit.json")
            sync_all(root, config, emit_event=False)
            config_path = root / "config" / "codex.toml"
            drifted = render_codex_config().replace(
                'sandbox_mode = "workspace-write"',
                'sandbox_mode = "read-only"',
            )
            config_path.write_text(drifted, encoding="utf-8")

            errors = check_sync_parity(root, config)

            self.assertIn("config/codex.toml", [error.artifact for error in errors])
            self.assertEqual(config_path.read_text(encoding="utf-8"), drifted)

    @covers("REQ-0.44.0-01-04")
    def test_unmarked_operator_config_is_not_managed_drift(self) -> None:
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_all

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(project_name="demo")
            config.save(root / ".gzkit.json")
            sync_all(root, config, emit_event=False)
            config_path = root / ".codex" / "config.toml"
            operator_bytes = b'model = "gpt-5.4"\n'
            config_path.write_bytes(operator_bytes)

            errors = check_sync_parity(root, config)

            self.assertNotIn(".codex/config.toml", [error.artifact for error in errors])
            self.assertEqual(config_path.read_bytes(), operator_bytes)

    @covers("REQ-0.44.0-01-04")
    def test_custom_path_reports_preserved_default_duplicate(self) -> None:
        from gzkit.config import GzkitConfig, PathConfig
        from gzkit.sync_surfaces import render_codex_config, sync_all

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            customized = (render_codex_config() + '\nmodel = "gpt-5.4"\n').encode()
            default_path.write_bytes(customized)
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="config/codex.toml"),
            )
            config.save(root / ".gzkit.json")
            sync_all(root, config, emit_event=False)

            errors = check_sync_parity(root, config)

            self.assertIn(".codex/config.toml", [error.artifact for error in errors])
            self.assertEqual(default_path.read_bytes(), customized)

    @covers("REQ-0.44.0-01-04")
    def test_clean_parity_preserves_codex_config_mtime(self) -> None:
        config_path = Path(".codex/config.toml")
        fixed_timestamp = 1_000_000_000
        os.utime(config_path, ns=(fixed_timestamp, fixed_timestamp))

        errors = check_sync_parity(Path.cwd())

        self.assertNotIn(".codex/config.toml", [error.artifact for error in errors])
        self.assertEqual(config_path.stat().st_mtime_ns, fixed_timestamp)

    @covers("REQ-0.44.0-01-04")
    def test_parity_restores_mode_and_removes_created_parent_directories(self) -> None:
        from gzkit.config import GzkitConfig, PathConfig
        from gzkit.sync_surfaces import render_codex_config

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            default_path.write_text(render_codex_config(), encoding="utf-8")
            default_path.chmod(0o600)
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="generated/codex.toml"),
            )
            config.save(root / ".gzkit.json")

            check_sync_parity(root, config)

            self.assertEqual(default_path.stat().st_mode & 0o777, 0o600)
            self.assertFalse((root / "generated").exists())

    @covers("REQ-0.44.0-01-04")
    def test_exact_obsolete_default_reports_one_parity_error(self) -> None:
        from gzkit.config import GzkitConfig, PathConfig
        from gzkit.sync_surfaces import render_codex_config

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            default_path.write_text(render_codex_config(), encoding="utf-8")
            custom_path = root / "config" / "codex.toml"
            custom_path.parent.mkdir(parents=True)
            custom_path.write_text(render_codex_config(), encoding="utf-8")
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="config/codex.toml"),
            )
            config.save(root / ".gzkit.json")

            errors = check_sync_parity(root, config)

            default_errors = [e for e in errors if e.artifact == ".codex/config.toml"]
            self.assertEqual(len(default_errors), 1, default_errors)

    @covers("REQ-0.44.0-01-04")
    def test_directory_config_path_returns_validation_error(self) -> None:
        from gzkit.config import GzkitConfig

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / ".codex" / "config.toml"
            config_path.mkdir(parents=True)
            config = GzkitConfig(project_name="demo")
            config.save(root / ".gzkit.json")

            errors = check_sync_parity(root, config)

            self.assertEqual([error.artifact for error in errors], [".codex/config.toml"])


class SyncParityDateNormalizationTest(_SyncParityBase):
    """Stale AGENTS.md sync_date must not be reported as drift."""

    _mutable_paths = ("AGENTS.md",)

    def test_outdated_sync_date_does_not_trigger_drift(self) -> None:
        agents_md = Path("AGENTS.md")
        content = agents_md.read_text(encoding="utf-8")
        stale = content.replace("- **Updated**: 20", "- **Updated**: 19", 1)
        if stale == content:
            import re

            stale = re.sub(
                r"- \*\*Updated\*\*: \d{4}-\d{2}-\d{2}",
                "- **Updated**: 1999-01-01",
                content,
                count=1,
            )
        self.assertNotEqual(stale, content, "test fixture must actually change the date")
        # Preserve LF line endings: on Windows (a co-equal target platform)
        # write_text with the default newline translates every \n to \r\n,
        # surfacing as whole-file line-ending drift that would mask the
        # date-only change this test asserts is normalized away.
        agents_md.write_text(stale, encoding="utf-8", newline="\n")

        errors = check_sync_parity(Path.cwd(), expected=_expected_surfaces)
        agents_errors = [e for e in errors if e.artifact == "AGENTS.md"]
        self.assertEqual(
            [],
            agents_errors,
            f"stale sync_date must not trigger drift; got {[e.message for e in agents_errors]}",
        )


if __name__ == "__main__":
    unittest.main()
