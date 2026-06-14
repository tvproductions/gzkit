"""Tests for compose.py: composition renderer (ADR-0.0.37, OBPI-0.0.37-02/22).

After OBPI-0.0.37-22, render_agents_md is a rendition-playback function:
- Returns committed rendition bytes when .gzkit/renditions/AGENTS.md/claude.md exists
- Returns b"" when no rendition exists (bootstrap-safe)
- invariants/template_root params accepted for backward compat, not used in playback

REQ-derived assertions for:
  REQ-0.0.37-02-01: byte-deterministic output across calls and processes
  REQ-0.0.37-02-02: invariants parameter accepted (backward compat)
  REQ-0.0.37-02-03: content derives from committed rendition (rendition-playback)
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.rendition_store import save_rendition
from gzkit.governance.invariants import ConstitutionalInvariant
from gzkit.traceability import covers

_FIXTURE_ROOT = Path(__file__).parent.parent / "fixtures" / "compose"


def _make_alpha() -> ConstitutionalInvariant:
    return ConstitutionalInvariant(
        id="CIC-test-alpha",
        claim="Alpha test invariant claim.",
        structural_witness=["gz validate --alpha"],
        composition_targets=["AGENTS.md"],
    )


def _make_beta() -> ConstitutionalInvariant:
    return ConstitutionalInvariant(
        id="CIC-test-beta",
        claim="Beta test invariant claim.",
        structural_witness=["gz validate --beta"],
        composition_targets=[],
    )


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
        from gzkit.governance.compose import render_agents_md

        invariants = {"CIC-test-alpha": _make_alpha()}
        result1 = render_agents_md(invariants, _FIXTURE_ROOT, self._root)
        result2 = render_agents_md(invariants, _FIXTURE_ROOT, self._root)
        self.assertEqual(result1, result2, "must be byte-identical across consecutive calls")

    @covers("REQ-0.0.37-02-01")
    def test_output_is_bytes(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invariants = {"CIC-test-alpha": _make_alpha()}
        result = render_agents_md(invariants, _FIXTURE_ROOT, self._root)
        self.assertIsInstance(result, bytes)

    @covers("REQ-0.0.37-02-01")
    def test_committed_rendition_bytes_returned(self) -> None:
        from gzkit.governance.compose import render_agents_md

        result = render_agents_md({}, _FIXTURE_ROOT, self._root)
        self.assertEqual(result, self._rendition)

    @covers("REQ-0.0.37-02-01")
    def test_determinism_across_dict_reordering(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invs_ab = {"CIC-test-alpha": _make_alpha(), "CIC-test-beta": _make_beta()}
        invs_ba = {"CIC-test-beta": _make_beta(), "CIC-test-alpha": _make_alpha()}
        self.assertEqual(
            render_agents_md(invs_ab, _FIXTURE_ROOT, self._root),
            render_agents_md(invs_ba, _FIXTURE_ROOT, self._root),
            "Output must be identical regardless of input dict iteration order",
        )


class TestRenderAgentsMdSortOrder(unittest.TestCase):
    """REQ-0.0.37-02-02: invariants parameter accepted without affecting output
    (after OBPI-0.0.37-22: invariants are not used in rendition-playback path;
    they are accepted for backward-compat)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)
        (self._root / ".gzkit").mkdir()
        save_rendition(self._root, "AGENTS.md", "claude", b"# Playback content\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.37-02-02")
    def test_different_invariants_produce_identical_bytes(self) -> None:
        """Invariants parameter is accepted but not used in rendition playback."""
        from gzkit.governance.compose import render_agents_md

        invs_ab = {"CIC-test-beta": _make_beta(), "CIC-test-alpha": _make_alpha()}
        invs_ba = {"CIC-test-beta": _make_beta()}
        self.assertEqual(
            render_agents_md(invs_ab, _FIXTURE_ROOT, self._root),
            render_agents_md(invs_ba, _FIXTURE_ROOT, self._root),
            "invariants parameter must not affect output — rendition is authoritative",
        )

    @covers("REQ-0.0.37-02-02")
    def test_empty_and_nonempty_invariants_produce_identical_bytes(self) -> None:
        """Invariants dict content must not change rendered bytes (backward-compat accept)."""
        from gzkit.governance.compose import render_agents_md

        with_invs = render_agents_md(
            {"CIC-test-alpha": _make_alpha()}, _FIXTURE_ROOT, self._root
        )
        without_invs = render_agents_md({}, _FIXTURE_ROOT, self._root)
        self.assertEqual(with_invs, without_invs)


class TestRenderAgentsMdTemplateBased(unittest.TestCase):
    """REQ-0.0.37-02-03: content derives from committed rendition (rendition-playback)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.37-02-03")
    def test_rendered_bytes_contain_committed_rendition_content(self) -> None:
        """Rendered output contains the committed rendition bytes verbatim."""
        from gzkit.governance.compose import render_agents_md

        content = b"# Test\n\nminimal test agent contract\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        rendered = render_agents_md({}, _FIXTURE_ROOT, self._root)
        self.assertIn(b"minimal test agent contract", rendered)

    @covers("REQ-0.0.37-02-03")
    def test_rendered_bytes_are_nonempty_for_committed_rendition(self) -> None:
        """A committed rendition yields non-empty bytes."""
        from gzkit.governance.compose import render_agents_md

        save_rendition(self._root, "AGENTS.md", "claude", b"# Non-empty rendition\n")
        rendered = render_agents_md({}, _FIXTURE_ROOT, self._root)
        self.assertGreater(len(rendered), 0)

    @covers("REQ-0.0.37-02-03")
    def test_missing_rendition_returns_empty_bytes(self) -> None:
        """Missing committed rendition returns empty bytes (bootstrap-safe — OBPI-0.0.37-22)."""
        from gzkit.governance.compose import render_agents_md

        result = render_agents_md({}, _FIXTURE_ROOT, self._root)
        self.assertEqual(result, b"")


class TestRenderAgentsMdProjectSubstitution(unittest.TestCase):
    """Rendition playback: render_agents_md returns committed rendition verbatim.

    REQ-0.0.37-02-01: byte-deterministic output — same committed rendition → same bytes.
    REQ-0.0.37-02-03: content derives from committed rendition (rendition-playback).
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._root = Path(self._tmp.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.37-02-03")
    def test_project_variables_are_substituted(self) -> None:
        """Committed rendition with substituted vars is returned byte-identically."""
        from gzkit.governance.compose import render_agents_md

        content = b"# AGENTS.md\n\nUniversal agent contract for demoproj.\n\n- demo local rule.\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        rendered = render_agents_md({}, _FIXTURE_ROOT, self._root).decode("utf-8")
        self.assertNotIn("{project_name}", rendered)
        self.assertIn("demoproj", rendered)
        self.assertIn("demo local rule.", rendered)

    @covers("REQ-0.0.37-02-01")
    def test_sync_date_sourced_from_committed_agents_md(self) -> None:
        """Committed rendition with a specific date is returned byte-identically."""
        from gzkit.governance.compose import render_agents_md

        content = b"# AGENTS.md\n\n- **Updated**: 2025-01-01\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        rendered = render_agents_md({}, _FIXTURE_ROOT, self._root).decode("utf-8")
        self.assertIn("**Updated**: 2025-01-01", rendered)
        self.assertNotIn("{sync_date}", rendered)

    @covers("REQ-0.0.37-02-01")
    def test_render_is_idempotent_across_two_calls(self) -> None:
        """Same committed rendition → byte-identical output on every call."""
        from gzkit.governance.compose import render_agents_md

        content = b"# AGENTS.md\n\nIdempotent rendition.\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        first = render_agents_md({}, _FIXTURE_ROOT, self._root)
        second = render_agents_md({}, _FIXTURE_ROOT, self._root)
        self.assertEqual(
            first, second, "re-render of same committed rendition must be byte-identical"
        )


if __name__ == "__main__":
    unittest.main()
