"""Sync parity validation for generated control surfaces (GHI #134)."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
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
