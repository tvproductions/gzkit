"""Sync parity validation for generated control surfaces (GHI #134)."""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.surface_write import capture_surface_writes
from gzkit.sync_surfaces import sync_all
from gzkit.validate_pkg.sync_parity import (
    SURFACE_ROOTS,
    _collect_files,
    _nested_agents_md,
    check_sync_parity,
    snapshot_surfaces,
)
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


def _write_probe_ns(path: Path) -> int:
    """Timestamp that moves when ``path`` is written, strongest the platform offers.

    POSIX answers ctime: it moves on every write AND every metadata change, and
    it cannot be set from userspace, so no snapshot-restore envelope can forge
    it. That unforgeability is the whole reason the drifted-tree probe exists --
    the validator this suite watches used to write and then put the stamp back
    (GHI #891).

    Windows has no metadata-change time to answer with. ``st_ctime`` there is
    the file CREATION time, so it moves for neither a write nor a chmod; the
    probe read insensitive and the sensitivity check below caught it rather than
    reporting a clean it had not earned (GHI #901). mtime is the strongest
    remaining signal and it is **strictly weaker** in two separate ways, both
    measured on ``windows-latest`` rather than assumed:

    1. It is forgeable. A validator that wrote and then called ``os.utime``
       reads clean on Windows, where on POSIX ctime cannot be put back.
    2. It is coarse. A write issued close enough to the preceding ``stat``
       records a byte-identical stamp -- observed directly, ``1787907512451441900
       == 1787907512451441900`` for a write that certainly happened. This is why
       the sensitivity check below settles the probe against the snapshot it
       must out-resolve, rather than merely asserting that one write moved it.

    The gap is narrower than that sounds, because it is not the only witness:
    ``SyncParityTouchesNoTreeShapeTest`` compares path SETS and is fully
    platform-neutral, so a validator that created or deleted anything is caught
    identically on both legs. What Windows alone cannot see is an in-place
    rewrite of an existing file whose mtime is restored afterwards.

    Python 3.12 deprecated Windows ``st_ctime`` and documents that it will
    become the metadata-change time in a future release, at which point this
    branch collapses and both legs get the strong probe. Written as a branch on
    the platform rather than a skip so that day is a one-line deletion.
    """
    st = path.stat()
    return st.st_mtime_ns if os.name == "nt" else st.st_ctime_ns


def _probe_outresolves(snapshot_ns: int, scratch: Path, timeout_s: float = 5.0) -> bool:
    """Can the probe tell "written after ``snapshot_ns``" from "not written"?

    That is the exact property the drifted-tree measurement rests on, and it is
    strictly narrower than the question the old check asked ("did SOME write
    move the stamp"). A probe can pass that one and still be useless here: the
    write it witnessed happened BEFORE the snapshot, and the writes the test
    hunts happen after it.

    Answers by writing ``scratch`` until its own stamp passes ``snapshot_ns``,
    which settles two failure modes with one loop. A coarse clock resolves
    within a tick or two and returns True. A probe that does not move for a
    write at all -- Windows ``st_ctime``, which is the creation time -- never
    passes and returns False at the deadline, so the guard the loop replaces is
    kept whole rather than relaxed into a sleep.

    ``scratch`` must sit on the same filesystem as the surfaces being measured;
    a probe settled against another volume's clock proves nothing about theirs.
    """
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        scratch.write_bytes(b"probe\n")
        if _write_probe_ns(scratch) > snapshot_ns:
            return True
        time.sleep(0.005)
    return False


class _SyncParityBase(unittest.TestCase):
    """Snapshot any files a test mutates and restore them in tearDown."""

    # Subclasses override with paths (relative to project root) they may mutate.
    _mutable_paths: tuple[str, ...] = ()

    def setUp(self) -> None:
        assert _project_dir is not None
        if Path.cwd() != _project_dir:
            os.chdir(_project_dir)
        self._snapshots: dict[Path, bytes] = {}
        for rel in self._mutable_paths:
            p = Path(rel)
            if p.exists():
                # Preserve exact bytes: a read_text/write_text round-trip
                # translates LF->CRLF on Windows, corrupting the shared module
                # tree's line endings and polluting sibling tests.
                self._snapshots[p] = p.read_bytes()

    def tearDown(self) -> None:
        for p, content in self._snapshots.items():
            p.write_bytes(content)


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


class SyncParityNonMutatingTest(_SyncParityBase):
    """The parity validator observes generated surfaces; it never writes them.

    Architectural Boundary 6 — a derived view must never silently become
    source-of-truth, and a validator that establishes parity by *performing*
    ``sync_all()`` is writing the surface it claims to be inspecting. The
    ledger arm of this property is asserted by
    ``test_default_sync_parity_check_does_not_emit_ledger_event``; this is the
    filesystem arm (GHI #890).

    Asserted on mtime rather than content because the writes are
    byte-identical: ``git status`` stays clean while 102 canonical files --
    ``AGENTS.md``, every ``.claude/rules/`` mirror, all 17 hook scripts --
    move underneath the caller. mtime is what makes the mutation observable,
    and it is what classes the ``gz check`` step as a writer.
    """

    def test_clean_tree_parity_check_writes_nothing(self) -> None:
        root = Path.cwd()
        before = {path: path.stat().st_mtime_ns for path in _collect_files(root) if path.is_file()}
        self.assertGreater(len(before), 50, "surface set should cover the generated tree")

        check_sync_parity(root)

        moved = sorted(
            path.relative_to(root).as_posix()
            for path, mtime in before.items()
            if path.is_file() and path.stat().st_mtime_ns != mtime
        )
        self.assertEqual(
            [],
            moved,
            f"check_sync_parity wrote {len(moved)} surface files: {moved[:10]}",
        )


class SyncParityDriftedTreeIsNonMutatingTest(_SyncParityBase):
    """The validator must not write on a DRIFTED tree either (GHI #891).

    #890 closed the healthy path: on a clean tree ``sync_all`` now writes
    nothing. The unhealthy path is the one that matters for scheduling, because
    a red gate is exactly when a concurrent step would read a torn mirror. A
    validator that can write under ANY input cannot carry a static
    ``read_only`` classification -- rarity is not the property the scheduler
    needs, impossibility is.

    **Asserted on ctime, not mtime.** The old snapshot-restore envelope called
    ``os.utime`` to put the original mtime back, so an mtime probe returns a
    false clean -- the first attempt at this measurement returned ``0`` moved
    files against a tree that had just been rewritten. ctime moves on write and
    cannot be set from userspace, so no restore envelope can forge it.

    Windows has no such stamp and falls back to mtime; :func:`_write_probe_ns`
    carries which leg gets which strength and why (GHI #901).
    """

    _mutable_paths = ("AGENTS.md",)

    def test_drifted_tree_parity_check_writes_nothing(self) -> None:
        root = Path.cwd()
        agents_md = root / "AGENTS.md"

        drifted = agents_md.read_text(encoding="utf-8") + "\n<!-- hand-edited drift -->\n"
        agents_md.write_text(drifted, encoding="utf-8")

        before = {path: _write_probe_ns(path) for path in _collect_files(root) if path.is_file()}
        self.assertGreater(len(before), 50, "surface set should cover the generated tree")

        # The snapshot's own sanity check: unless a write made NOW records a
        # stamp past every stamp in `before`, the comparison after
        # `check_sync_parity` cannot distinguish "wrote nothing" from "wrote
        # too fast to see", and a clean result below proves nothing. Asserted
        # inline rather than as a standalone test so it cannot drift away from
        # the claim it underwrites -- and it has now caught two distinct
        # Windows defects from that position (GHI #901). The scratch file is
        # rooted inside the tree under measurement so it shares its filesystem
        # clock, and is gone before the validator runs.
        with tempfile.TemporaryDirectory(dir=root, prefix=".probe-") as probe_dir:
            self.assertTrue(
                _probe_outresolves(max(before.values()), Path(probe_dir) / "scratch"),
                "write probe cannot out-resolve the snapshot — a clean result "
                "below would be meaningless",
            )

        errors = check_sync_parity(root)

        moved = sorted(
            path.relative_to(root).as_posix()
            for path, stamp in before.items()
            if path.is_file() and _write_probe_ns(path) != stamp
        )
        self.assertEqual(
            [],
            moved,
            f"check_sync_parity wrote {len(moved)} surface files on a drifted tree: {moved[:10]}",
        )
        self.assertTrue(errors, "planted drift must still fail closed")
        self.assertEqual(
            drifted,
            agents_md.read_text(encoding="utf-8"),
            "planted drift must be left in place, not silently repaired",
        )


class SyncParityTouchesNoTreeShapeTest(_SyncParityBase):
    """Beyond file bytes: the check must not add or remove anything (GHI #891).

    The write probe above watches FILES that already exist, so it is blind to a
    validator that creates a directory or deletes a surface. Both are real
    powers of ``sync_all`` -- it creates vendor mirror trees, and it prunes
    stale rules, unshippable chore files and orphaned nested ``AGENTS.md``. A
    sink that suppressed writes but let those through would still be a writer,
    and the per-file write-probe assertion would have reported green. This arm
    compares path SETS, so unlike that probe it is fully platform-neutral --
    which is why it carries proportionally more of the guarantee on Windows
    (:func:`_write_probe_ns`).
    """

    _mutable_paths = ("AGENTS.md",)

    @staticmethod
    def _tree_shape(root: Path) -> set[str]:
        """Every path under a tracked surface root, files and directories alike."""
        shape: set[str] = set()
        for rel in ("AGENTS.md", "CLAUDE.md", ".claude", ".github", ".agents", ".gzkit"):
            base = root / rel
            if base.is_file():
                shape.add(base.relative_to(root).as_posix())
            elif base.is_dir():
                for path in base.rglob("*"):
                    if "__pycache__" in path.parts:
                        continue
                    shape.add(path.relative_to(root).as_posix())
        return shape

    def test_drifted_tree_check_creates_and_removes_nothing(self) -> None:
        root = Path.cwd()
        agents_md = root / "AGENTS.md"
        agents_md.write_text(
            agents_md.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8"
        )
        before = self._tree_shape(root)
        self.assertGreater(len(before), 50, "shape probe must cover the generated tree")

        check_sync_parity(root)

        after = self._tree_shape(root)
        self.assertEqual(sorted(after - before), [], "check_sync_parity created paths")
        self.assertEqual(sorted(before - after), [], "check_sync_parity removed paths")


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
        self._snapshots[hook_file] = hook_file.read_bytes()
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

    def test_clean_parity_preserves_codex_config_mtime(self) -> None:
        config_path = Path(".codex/config.toml")
        fixed_timestamp = 1_000_000_000
        os.utime(config_path, ns=(fixed_timestamp, fixed_timestamp))

        errors = check_sync_parity(Path.cwd())

        self.assertNotIn(".codex/config.toml", [error.artifact for error in errors])
        self.assertEqual(config_path.stat().st_mtime_ns, fixed_timestamp)

    def test_parity_restores_mode_and_removes_created_parent_directories(self) -> None:
        from gzkit.config import GzkitConfig, PathConfig
        from gzkit.sync_surfaces import render_codex_config

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_path = root / ".codex" / "config.toml"
            default_path.parent.mkdir(parents=True)
            default_path.write_text(render_codex_config(), encoding="utf-8", newline="\n")
            default_path.chmod(0o600)
            # Windows cannot represent 0o600 — chmod only toggles the write bit,
            # so stat reports 0o666. Assert the mode is PRESERVED by the
            # write-compare-restore, not equal to a POSIX-only literal.
            mode_before = default_path.stat().st_mode & 0o777
            config = GzkitConfig(
                project_name="demo",
                paths=PathConfig(codex_config="generated/codex.toml"),
            )
            config.save(root / ".gzkit.json")

            check_sync_parity(root, config)

            self.assertEqual(default_path.stat().st_mode & 0o777, mode_before)
            self.assertFalse((root / "generated").exists())

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


class SyncParityPersonaMirrorTest(_SyncParityBase):
    """Vendor persona mirrors are generated surfaces, so parity must cover them.

    ``sync_all`` rewrites ``.agents/personas/``, ``.claude/personas/`` and
    ``.github/personas/`` on every run, and ``AGENTS.md`` § Persona makes them
    governance surfaces -- a hand-edit changes agent behaviour. Nothing
    distinguishes them in kind from ``.claude/rules/``, which parity has always
    covered (GHI #893).
    """

    _mutable_paths = (".claude/personas/main-session.md",)

    def test_hand_edit_to_a_persona_mirror_is_reported_as_drift(self) -> None:
        mirror = Path(".claude/personas/main-session.md")
        self.assertTrue(mirror.is_file(), "sync_all writes this mirror on every run")
        mirror.write_text(mirror.read_text(encoding="utf-8") + "\nhand-edited\n", encoding="utf-8")

        drifted = [e.artifact for e in check_sync_parity(Path.cwd())]

        self.assertIn(
            ".claude/personas/main-session.md",
            drifted,
            "a hand-edit to a generated persona mirror must be reported as drift",
        )


class SyncParityDomainCoversEveryWriteTest(_SyncParityBase):
    """Every path ``sync_all`` writes is in the parity domain, or declared out of it.

    The census GHI #893 asked for, standing in place of a longer literal. A
    hand-maintained ``SURFACE_ROOTS`` cannot announce what it has fallen behind:
    a file outside the tracked roots drops out of BOTH sides of the comparison at
    once and cancels, so the check reports clean on a domain it does not cover.
    Deriving the assertion from the WRITER is what makes that undetectable state
    fail instead.
    """

    #: Package-surface mirrors (``.gzkit/<surface>/`` -> ``src/gzkit/<surface>/``)
    #: are generated by ``sync_pkg_surfaces`` and witnessed by
    #: ``gz validate --distribution``, which byte-compares them against the wheel
    #: (ADR-0.0.31). They are deliberately outside the parity domain, not missing
    #: from it -- this tuple is the declaration that says so.
    _DECLARED_OUT_OF_DOMAIN: tuple[str, ...] = ("src/gzkit/",)

    def test_every_path_sync_all_writes_is_covered_or_declared(self) -> None:
        root = Path.cwd().resolve()
        config = GzkitConfig.load(root / ".gzkit.json")

        with capture_surface_writes() as sink:
            sync_all(root, config, emit_event=False)

        # The DECLARED domain, asked as a prefix question rather than by walking
        # disk. `_collect_files` only admits paths that already exist, so a
        # disk-based comparison answers "what is on disk" and not "what does the
        # domain declare" -- and under a capture sink an unwritten path is
        # neither. The declaration is what falls behind the writer, so the
        # declaration is what this asserts against.
        roots = (*SURFACE_ROOTS, *_nested_agents_md(root), *self._DECLARED_OUT_OF_DOMAIN)

        uncovered = sorted(
            rel
            for rel in (q.resolve().relative_to(root).as_posix() for q in sink.written)
            if not any(rel == r or rel.startswith(r.rstrip("/") + "/") for r in roots)
        )

        self.assertEqual(
            [],
            uncovered,
            "sync_all writes these paths but no SURFACE_ROOTS entry declares them, "
            "so gz validate --surfaces cannot report drift in them; add the root "
            f"or declare it out of domain: {uncovered}",
        )


if __name__ == "__main__":
    unittest.main()
