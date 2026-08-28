"""Generated control surfaces are written only when their bytes change (GHI #890).

``gz validate --surfaces`` proves sync parity by *performing* a sync, so every
unconditional writer in the sync path made a read-only validator mutate the tree
it was inspecting -- 102 canonical files on every invocation, byte-identical, so
``git status`` stayed clean while mtimes churned.

These are unit-level pins. The end-to-end assertion lives in
``tests.test_validate_sync_parity.SyncParityNonMutatingTest``, but its fixture is
a bare temp project where ``uv run ruff`` does not resolve, so ``_ruff_format_dir``
no-ops there and the fixture cannot reach the ruff arm at all. That arm is pinned
directly here instead.
"""

import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.hooks import core as hooks_core
from gzkit.rules import _cleanup_stale_nested_agents
from gzkit.surface_write import write_if_changed, write_text_if_changed


def _assert_mode_0o755(case: unittest.TestCase, mode: int, *, writable: bool, why: str) -> None:
    """Assert ``mode=0o755`` landed, in the permission bits the platform has.

    POSIX carries the full triplet, so the literal is asserted directly. NTFS
    has no execute bit and ``os.chmod`` toggles only the read-only attribute,
    so every writable file reads back ``0o666`` and ``0o755`` is unreachable by
    construction -- ``AssertionError: 493 != 438`` on ``windows-latest`` while
    ``ubuntu-latest`` passed the same run (GHI #901).

    ``writable`` is asserted on BOTH legs, before the branch: it is the one bit
    of ``0o755`` that NTFS does represent, so it carries the claim on the side
    where the octal literal cannot. The Windows leg then asserts the documented
    no-op rather than returning early, matching
    ``tests.test_hooks.test_execute_bit_is_set_wherever_the_platform_has_one``
    -- a runtime that DOES start carrying the bit fails here and the branch
    gets revisited, instead of drifting into an untrue comment.

    Takes already-observed VALUES rather than a path, so the ``stat``/``access``
    calls stay in the test bodies that also drive production code. A helper that
    read the filesystem itself would be a filesystem op plus an assertion with
    no production call in the same function -- the exact shape
    ``gz check``'s tautological-test audit flags, and it flagged the first
    draft of this helper for precisely that reason.
    """
    case.assertTrue(stat.S_ISREG(mode), f"not a regular file: {oct(mode)}")
    case.assertTrue(writable, why)
    if os.name == "nt":
        case.assertFalse(mode & stat.S_IXUSR, "NTFS is not expected to carry S_IXUSR")
    else:
        case.assertEqual(0o755, mode & 0o777, f"mode not enforced: {oct(mode & 0o777)}")


class WriteIfChangedTest(unittest.TestCase):
    """The primitive every generated-surface writer funnels through."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gzkit-write-")
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_identical_payload_leaves_the_file_untouched(self) -> None:
        target = self.root / "surface.md"
        self.assertTrue(write_if_changed(target, b"body\n"))
        before = target.stat().st_mtime_ns
        os.utime(target, ns=(before - 10**9, before - 10**9))
        stamped = target.stat().st_mtime_ns

        self.assertFalse(write_if_changed(target, b"body\n"))
        self.assertEqual(
            stamped,
            target.stat().st_mtime_ns,
            "an unchanged surface must not be rewritten; mtime is the observable",
        )

    def test_differing_payload_is_written(self) -> None:
        target = self.root / "surface.md"
        write_if_changed(target, b"old\n")
        self.assertTrue(write_if_changed(target, b"new\n"))
        self.assertEqual(b"new\n", target.read_bytes())

    def test_mode_is_enforced_even_when_content_matches(self) -> None:
        """Hooks must stay executable; on POSIX chmod moves ctime, never mtime.

        The drift is planted as read-only rather than ``0o644`` so the
        enforcement is observable on every platform (GHI #901). Windows chmod
        carries only the read-only attribute, so ``0o644`` and ``0o755`` both
        read back ``0o666`` and a Windows leg planted at ``0o644`` asserts
        nothing whatsoever -- the file it checks is byte-identical AND
        mode-identical to the one it started with, whether or not
        ``write_if_changed`` re-applied anything. Read-only -> writable states
        the same claim in the one bit NTFS represents, so the planted drift is
        real drift on both legs.
        """
        target = self.root / "hook.py"
        write_if_changed(target, b"#!/usr/bin/env python\n", mode=0o755)
        target.chmod(0o444)

        self.assertFalse(write_if_changed(target, b"#!/usr/bin/env python\n", mode=0o755))
        _assert_mode_0o755(
            self,
            target.stat().st_mode,
            writable=os.access(target, os.W_OK),
            why="mode was not re-applied on the byte-identical path",
        )

    def test_text_sibling_writes_utf8_without_newline_translation(self) -> None:
        target = self.root / "surface.md"
        write_text_if_changed(target, "line\nline\n")
        self.assertEqual(b"line\nline\n", target.read_bytes())


class RuffFormatConfigTest(unittest.TestCase):
    """Staged hook formatting must carry the project's ruff config."""

    def test_staging_format_passes_project_config(self) -> None:
        """Without --config, ruff discovers nothing and falls back to 88 chars.

        ``pyproject.toml`` pins ``line-length = 100`` and its own
        per-file-ignores comment records that the emitted hooks are
        "ruff-formatted at line-length 100". A staging tree lives outside the
        project, so config discovery would silently use a different width and
        every hook would differ forever instead of once.
        """
        with tempfile.TemporaryDirectory(prefix="gzkit-fmt-") as name:
            staging = Path(name) / "hooks"
            staging.mkdir()
            (staging / "h.py").write_text("x = 1\n", encoding="utf-8")
            config = Path(name) / "pyproject.toml"
            config.write_text("[tool.ruff]\nline-length = 100\n", encoding="utf-8")

            with patch("subprocess.run") as run:
                hooks_core._ruff_format_dir(staging, Path(name))

        run.assert_called_once()
        argv = list(run.call_args.args[0])
        self.assertIn("--config", argv)
        self.assertIn(str(config), argv)
        self.assertLess(
            argv.index("--config"),
            argv.index(str(staging)),
            "--config must precede the target so ruff applies it to that tree",
        )

    def test_absent_config_is_not_passed(self) -> None:
        """A project without pyproject.toml keeps ruff's own discovery."""
        with tempfile.TemporaryDirectory(prefix="gzkit-fmt-") as name:
            staging = Path(name) / "hooks"
            staging.mkdir()
            (staging / "h.py").write_text("x = 1\n", encoding="utf-8")

            with patch("subprocess.run") as run:
                hooks_core._ruff_format_dir(staging, Path(name))

        self.assertNotIn("--config", list(run.call_args.args[0]))


class NestedAgentsCleanupTest(unittest.TestCase):
    """Cleanup owns the canonical tree; mirror copies belong to the mirror pass."""

    _MARKER = "<!-- Generated by gzkit -->\n"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gzkit-cleanup-")
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _pairs(self) -> tuple[tuple[Path, Path], ...]:
        return ((self.root / ".claude/skills", self.root / ".gzkit/skills"),)

    def _seed(self, rel: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._MARKER + "body\n", encoding="utf-8")
        return path

    def test_orphaned_mirror_copy_is_removed(self) -> None:
        """A copy whose canonical source is gone is a genuine orphan.

        Excluding mirror trees outright would stop the churn and also strand
        this file forever: ``sync_skill_mirror`` is documented as
        "intentionally additive/non-destructive", so nothing else removes it.
        Scoping the exclusion by canonical counterpart keeps both properties.
        """
        orphan = self._seed(".claude/skills/retired/AGENTS.md")

        _cleanup_stale_nested_agents(self.root, set(), self._pairs())

        self.assertFalse(orphan.is_file(), "mirror copy with no canonical source must go")

    def test_mirror_survives_regardless_of_walk_order(self) -> None:
        """Deletion is decided for the whole sweep, not as ``rglob`` walks.

        A canonical file and its mirror both carry the marker. Deciding per
        file makes the result depend on which one ``rglob`` yields first --
        canonical-first deletes it and orphans the mirror; mirror-first spares
        both. Seeding the canonical as expected pins the real sync's shape.
        """
        self._seed(".gzkit/skills/AGENTS.md")
        canonical = self.root / ".gzkit/skills/AGENTS.md"
        mirror = self._seed(".claude/skills/AGENTS.md")

        _cleanup_stale_nested_agents(self.root, {canonical}, self._pairs())

        self.assertTrue(canonical.is_file())
        self.assertTrue(mirror.is_file(), "mirror-owned AGENTS.md must not be deleted")

    def test_retired_canonical_takes_its_mirror_with_it(self) -> None:
        """When the canonical is retired in this sweep, its mirror goes too."""
        canonical = self._seed(".gzkit/skills/AGENTS.md")
        mirror = self._seed(".claude/skills/AGENTS.md")

        _cleanup_stale_nested_agents(self.root, set(), self._pairs())

        self.assertFalse(canonical.is_file())
        self.assertFalse(mirror.is_file(), "a mirror of a retired canonical is stale")

    def test_genuinely_stale_canonical_file_is_still_removed(self) -> None:
        """The exclusion must not disarm the cleanup it scopes."""
        stale = self._seed("docs/retired/AGENTS.md")

        _cleanup_stale_nested_agents(self.root, set(), self._pairs())

        self.assertFalse(stale.is_file(), "stale generated AGENTS.md must still be removed")

    def test_unmarked_file_is_never_removed(self) -> None:
        hand_written = self.root / "docs" / "AGENTS.md"
        hand_written.parent.mkdir(parents=True, exist_ok=True)
        hand_written.write_text("operator-authored\n", encoding="utf-8")

        _cleanup_stale_nested_agents(self.root, set(), ())

        self.assertTrue(hand_written.is_file())


class HookStagingOrderTest(unittest.TestCase):
    """Normalization must happen BEFORE the comparison, not after the write.

    Four generated hook templates are not ruff-clean. Writing them straight to
    the hooks directory and formatting afterwards produces the right bytes by
    the end of the call, so no bytes comparison anywhere can see the defect --
    the file is simply written twice, and the second write restores what the
    first displaced. Only the ORDER distinguishes the two implementations,
    which is what these tests pin.

    ``_ruff_format_dir`` is stubbed with a formatter that rewrites its input,
    so "the written bytes are the post-format bytes" becomes observable
    without needing a resolvable ``uv run ruff``.
    """

    _NORMALIZED = b"# normalized by the formatter\n"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gzkit-stage-")
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _formatter(self, directory: Path, config_path: Path | None = None) -> None:
        for path in Path(directory).glob("*.py"):
            path.write_bytes(self._NORMALIZED)

    def test_claude_hooks_write_post_format_bytes(self) -> None:
        from gzkit.hooks.claude import _write_hook_dir

        hooks = self.root / ".claude" / "hooks"
        scripts = (("h.py", lambda: "x=1\n", True),)

        with patch("gzkit.hooks.claude._ruff_format_dir", side_effect=self._formatter):
            _write_hook_dir(self.root, hooks, scripts)

        self.assertEqual(
            self._NORMALIZED,
            (hooks / "h.py").read_bytes(),
            "the raw template reached disk, so formatting ran after the write",
        )

    def test_claude_hooks_second_sync_writes_nothing(self) -> None:
        from gzkit.hooks.claude import _write_hook_dir

        hooks = self.root / ".claude" / "hooks"
        scripts = (("h.py", lambda: "x=1\n", True),)

        with patch("gzkit.hooks.claude._ruff_format_dir", side_effect=self._formatter):
            _write_hook_dir(self.root, hooks, scripts)
            target = hooks / "h.py"
            stamped = target.stat().st_mtime_ns - 10**9
            os.utime(target, ns=(stamped, stamped))

            _write_hook_dir(self.root, hooks, scripts)

        self.assertEqual(
            stamped,
            target.stat().st_mtime_ns,
            "an already-normalized hook must not be rewritten on the next sync",
        )

    def test_copilot_hook_writes_post_format_bytes(self) -> None:
        """``write_hook_script`` carries the same order; it is a separate path."""
        with patch("gzkit.hooks.core._ruff_format_dir", side_effect=self._formatter):
            written = hooks_core.write_hook_script(self.root, "copilot", ".github/copilot/hooks")

        self.assertEqual(self._NORMALIZED, written.read_bytes())
        _assert_mode_0o755(
            self,
            written.stat().st_mode,
            writable=os.access(written, os.W_OK),
            why="staged hook was written read-only",
        )


if __name__ == "__main__":
    unittest.main()
