"""Tests for compose.py: deterministic rendition playback (ADR-0.0.37, OBPI-0.0.37-22).

``render_agents_md`` is a playback function:
- Returns committed rendition bytes when .gzkit/renditions/AGENTS.md/claude.md exists
- Returns b"" when no rendition exists (bootstrap-safe)

REQ-derived assertions for:
  REQ-0.0.37-02-01: byte-deterministic output across calls
  REQ-0.0.37-02-03: content derives from the committed rendition (playback)

REQ-0.0.37-02-02 ("invariants parameter accepted for backward compat") is retired
with the parameter it existed to preserve (GHI #623): the registry→AGENTS.md renderer
was obsoleted by the 2026-06-03 corpus Re-Alignment and permanently withdrawn
2026-07-17, so a requirement to keep accepting its discarded argument no longer
describes anything the code owes. The dict-reordering and substitution assertions
went with it — the former exercised the removed parameter, the latter saved content
free of ``{project_name}``/``{sync_date}`` and asserted those markers were absent,
which cannot fail whatever the production code does (.gzkit/rules/tests.md
§ The discriminator).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.rendition_store import save_rendition
from gzkit.governance.compose import render_agents_md
from gzkit.traceability import covers


class TestRenderAgentsMdDeterminism(unittest.TestCase):
    """REQ-0.0.37-02-01: byte-deterministic output (rendition-playback semantics)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)
        (self._root / ".gzkit").mkdir()
        self._rendition = b"# AGENTS.md\n\nDeterministic rendition content.\n"
        save_rendition(self._root, "AGENTS.md", "claude", self._rendition)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.37-02-01")
    def test_same_call_produces_identical_bytes(self) -> None:
        self.assertEqual(
            render_agents_md(self._root),
            render_agents_md(self._root),
            "must be byte-identical across consecutive calls",
        )

    @covers("REQ-0.0.37-02-01")
    def test_output_is_bytes(self) -> None:
        self.assertIsInstance(render_agents_md(self._root), bytes)

    @covers("REQ-0.0.37-02-01")
    def test_committed_rendition_bytes_returned(self) -> None:
        self.assertEqual(render_agents_md(self._root), self._rendition)

    @covers("REQ-0.0.37-02-01")
    def test_playback_tracks_a_recommitted_rendition(self) -> None:
        """Playback reflects the rendition on disk, not a value cached from an earlier call.

        Distinguishes real playback from a first-call-wins cache: the second read must
        return the *new* bytes. Fails if render_agents_md ever memoizes per root.
        """
        first = render_agents_md(self._root)
        replacement = b"# AGENTS.md\n\nRecommitted rendition content.\n"
        save_rendition(self._root, "AGENTS.md", "claude", replacement)
        self.assertEqual(render_agents_md(self._root), replacement)
        self.assertNotEqual(first, replacement, "fixture must actually differ")


class TestRenderAgentsMdPlaybackSource(unittest.TestCase):
    """REQ-0.0.37-02-03: content derives from the committed rendition."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.37-02-03")
    def test_rendered_bytes_are_the_committed_rendition_verbatim(self) -> None:
        content = b"# Test\n\nminimal test agent contract\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        self.assertEqual(render_agents_md(self._root), content)

    @covers("REQ-0.0.37-02-03")
    def test_missing_rendition_returns_empty_bytes(self) -> None:
        """Missing committed rendition returns empty bytes (bootstrap-safe — OBPI-0.0.37-22)."""
        self.assertEqual(render_agents_md(self._root), b"")


if __name__ == "__main__":
    unittest.main()
