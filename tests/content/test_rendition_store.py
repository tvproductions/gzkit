"""Committed-rendition store tests — OBPI-0.0.37-22 (REQ-0.0.37-22-01).

Covers the store contract: per-(surface×consumer) artifact at
``.gzkit/renditions/<surface>/<consumer>.md``, deterministic load
(same file → same bytes), and fail-closed absent behavior.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.rendition_store import (
    load_rendition,
    rendition_exists,
    rendition_path,
    save_rendition,
)
from gzkit.traceability import covers


class TestRenditionStorePath(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-22-01")
    def test_rendition_path_is_per_surface_consumer_md_under_gzkit_renditions(self) -> None:
        """The store artifact is .gzkit/renditions/<surface>/<consumer>.md."""
        path = rendition_path(self._root, "AGENTS.md", "claude")
        self.assertEqual(
            path, self._root / ".gzkit" / "renditions" / "AGENTS.md" / "claude.md"
        )

    @covers("REQ-0.0.37-22-01")
    def test_rendition_path_uses_consumer_as_filename(self) -> None:
        """Different consumers under the same surface get distinct artifact paths."""
        claude_path = rendition_path(self._root, "AGENTS.md", "claude")
        codex_path = rendition_path(self._root, "AGENTS.md", "codex")
        self.assertNotEqual(claude_path, codex_path)
        self.assertEqual(claude_path.parent, codex_path.parent)


class TestRenditionStoreExists(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-22-01")
    def test_rendition_exists_returns_false_when_artifact_absent(self) -> None:
        """rendition_exists returns False when no artifact has been committed."""
        self.assertFalse(rendition_exists(self._root, "AGENTS.md", "claude"))

    @covers("REQ-0.0.37-22-01")
    def test_rendition_exists_returns_true_after_save(self) -> None:
        """rendition_exists returns True after save_rendition commits the artifact."""
        save_rendition(self._root, "AGENTS.md", "claude", b"content")
        self.assertTrue(rendition_exists(self._root, "AGENTS.md", "claude"))


class TestRenditionStoreLoadSave(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-22-01")
    def test_load_raises_when_artifact_absent(self) -> None:
        """load_rendition fails closed with FileNotFoundError when artifact is absent."""
        with self.assertRaises(FileNotFoundError):
            load_rendition(self._root, "AGENTS.md", "claude")

    @covers("REQ-0.0.37-22-01")
    def test_save_creates_parent_dirs_on_first_use(self) -> None:
        """save_rendition creates .gzkit/renditions/<surface>/ on first use."""
        path = rendition_path(self._root, "AGENTS.md", "claude")
        self.assertFalse(path.parent.exists())
        save_rendition(self._root, "AGENTS.md", "claude", b"hello")
        self.assertTrue(path.exists())

    @covers("REQ-0.0.37-22-01")
    def test_load_returns_byte_identical_content_to_saved(self) -> None:
        """load_rendition returns the exact bytes that were committed via save_rendition."""
        content = b"deterministic rendition content\nline two\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        loaded = load_rendition(self._root, "AGENTS.md", "claude")
        self.assertEqual(loaded, content)

    @covers("REQ-0.0.37-22-01")
    def test_load_is_deterministic_same_file_same_bytes(self) -> None:
        """Same committed artifact yields byte-identical bytes across multiple loads."""
        content = b"# AGENTS.md\n\nsome content\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        first = load_rendition(self._root, "AGENTS.md", "claude")
        second = load_rendition(self._root, "AGENTS.md", "claude")
        self.assertEqual(first, second)
        self.assertIs(type(first), bytes)

    @covers("REQ-0.0.37-22-01")
    def test_each_surface_consumer_pair_has_isolated_store(self) -> None:
        """A save to one (surface, consumer) does not affect another pair."""
        save_rendition(self._root, "AGENTS.md", "claude", b"claude content")
        self.assertFalse(rendition_exists(self._root, "AGENTS.md", "codex"))
        with self.assertRaises(FileNotFoundError):
            load_rendition(self._root, "AGENTS.md", "codex")

    @covers("REQ-0.0.37-22-01")
    def test_save_overwrites_existing_artifact(self) -> None:
        """save_rendition replaces a prior committed rendition (recompose flow)."""
        save_rendition(self._root, "AGENTS.md", "claude", b"v1 content")
        save_rendition(self._root, "AGENTS.md", "claude", b"v2 content")
        loaded = load_rendition(self._root, "AGENTS.md", "claude")
        self.assertEqual(loaded, b"v2 content")


if __name__ == "__main__":
    unittest.main()
