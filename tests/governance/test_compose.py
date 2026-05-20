"""Tests for compose.py: composition renderer (ADR-0.0.37, OBPI-0.0.37-02).

REQ-derived assertions for:
  REQ-0.0.37-02-01: byte-deterministic output across calls and processes
  REQ-0.0.37-02-02: iteration order sorted lexicographically by id
  REQ-0.0.37-02-03: template-based rendering (Jinja2 or string.Template)
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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
    """REQ-0.0.37-02-01: byte-deterministic output."""

    @covers("REQ-0.0.37-02-01")
    def test_same_call_produces_identical_bytes(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invariants = {"CIC-test-alpha": _make_alpha()}
        result1 = render_agents_md(invariants, _FIXTURE_ROOT, _FIXTURE_ROOT)
        result2 = render_agents_md(invariants, _FIXTURE_ROOT, _FIXTURE_ROOT)
        self.assertEqual(result1, result2, "must be byte-identical across consecutive calls")

    @covers("REQ-0.0.37-02-01")
    def test_output_is_bytes(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invariants = {"CIC-test-alpha": _make_alpha()}
        result = render_agents_md(invariants, _FIXTURE_ROOT, _FIXTURE_ROOT)
        self.assertIsInstance(result, bytes)

    @covers("REQ-0.0.37-02-01")
    def test_empty_registry_produces_stable_bytes(self) -> None:
        from gzkit.governance.compose import render_agents_md

        result1 = render_agents_md({}, _FIXTURE_ROOT, _FIXTURE_ROOT)
        result2 = render_agents_md({}, _FIXTURE_ROOT, _FIXTURE_ROOT)
        self.assertEqual(result1, result2)

    @covers("REQ-0.0.37-02-01")
    def test_determinism_across_dict_reordering(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invs_ab = {"CIC-test-alpha": _make_alpha(), "CIC-test-beta": _make_beta()}
        invs_ba = {"CIC-test-beta": _make_beta(), "CIC-test-alpha": _make_alpha()}
        self.assertEqual(
            render_agents_md(invs_ab, _FIXTURE_ROOT, _FIXTURE_ROOT),
            render_agents_md(invs_ba, _FIXTURE_ROOT, _FIXTURE_ROOT),
            "Output must be identical regardless of input dict iteration order",
        )


class TestRenderAgentsMdSortOrder(unittest.TestCase):
    """REQ-0.0.37-02-02: iteration order sorted lexicographically by id."""

    @covers("REQ-0.0.37-02-02")
    def test_alpha_appears_before_beta(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invs = {"CIC-test-beta": _make_beta(), "CIC-test-alpha": _make_alpha()}
        rendered = render_agents_md(invs, _FIXTURE_ROOT, _FIXTURE_ROOT).decode("utf-8")
        alpha_pos = rendered.index("CIC-test-alpha")
        beta_pos = rendered.index("CIC-test-beta")
        self.assertLess(alpha_pos, beta_pos, "alpha must appear before beta (lexicographic sort)")

    @covers("REQ-0.0.37-02-02")
    def test_reversed_insertion_order_still_sorts_lexicographically(self) -> None:
        from gzkit.governance.compose import render_agents_md

        invs_reversed = {
            "CIC-test-zz": ConstitutionalInvariant(
                id="CIC-test-zz",
                claim="ZZ claim.",
                structural_witness=["gz validate --zz"],
                composition_targets=[],
            ),
            "CIC-test-aa": ConstitutionalInvariant(
                id="CIC-test-aa",
                claim="AA claim.",
                structural_witness=["gz validate --aa"],
                composition_targets=[],
            ),
        }
        rendered = render_agents_md(invs_reversed, _FIXTURE_ROOT, _FIXTURE_ROOT).decode("utf-8")
        aa_pos = rendered.index("CIC-test-aa")
        zz_pos = rendered.index("CIC-test-zz")
        self.assertLess(aa_pos, zz_pos)


class TestRenderAgentsMdTemplateBased(unittest.TestCase):
    """REQ-0.0.37-02-03: template-based rendering; content derives from template."""

    @covers("REQ-0.0.37-02-03")
    def test_rendered_bytes_contain_invariant_id(self) -> None:
        from gzkit.governance.compose import render_agents_md

        inv = _make_alpha()
        rendered = render_agents_md({"CIC-test-alpha": inv}, _FIXTURE_ROOT, _FIXTURE_ROOT).decode(
            "utf-8"
        )
        self.assertIn("CIC-test-alpha", rendered)

    @covers("REQ-0.0.37-02-03")
    def test_rendered_bytes_contain_claim(self) -> None:
        from gzkit.governance.compose import render_agents_md

        inv = _make_alpha()
        rendered = render_agents_md({"CIC-test-alpha": inv}, _FIXTURE_ROOT, _FIXTURE_ROOT).decode(
            "utf-8"
        )
        self.assertIn("Alpha test invariant claim.", rendered)

    @covers("REQ-0.0.37-02-03")
    def test_missing_template_raises(self) -> None:
        from gzkit.governance.compose import render_agents_md

        with (
            tempfile.TemporaryDirectory() as tmp,
            self.assertRaises((FileNotFoundError, OSError)),
        ):
            render_agents_md({"CIC-test-alpha": _make_alpha()}, Path(tmp), Path(tmp))


class TestRenderAgentsMdProjectSubstitution(unittest.TestCase):
    """Project-context substitution: placeholders resolve to concrete values.

    REQ-0.0.37-02-01: byte-deterministic output — a re-render of the renderer's
    own committed output is byte-identical (idempotent across processes).
    REQ-0.0.37-02-03: template-based rendering yields concrete substituted
    values, never literal ``{placeholder}`` tokens (GHI #504).
    """

    def _scaffold(self, tmp: Path, *, updated: str = "2025-01-01") -> tuple[Path, Path]:
        """Write a minimal gzkit project; return (template_root, project_root)."""
        (tmp / ".gzkit.json").write_text('{"project_name": "demoproj"}\n', encoding="utf-8")
        templates = tmp / ".gzkit" / "templates"
        templates.mkdir(parents=True)
        (templates / "agents.md").write_text(
            "# AGENTS.md\n\n"
            "Universal agent contract for {project_name}.\n\n"
            "## Control Surfaces\n\n"
            "- **Source**: `.gzkit/manifest.json`\n"
            "- **Updated**: {sync_date}\n\n"
            "---\n\n"
            "{local_content}\n",
            encoding="utf-8",
        )
        (tmp / ".gzkit" / "agents.local.md").write_text(
            "# Local Agent Rules\n\n- demo local rule.\n", encoding="utf-8"
        )
        (tmp / "AGENTS.md").write_text(
            "# AGENTS.md\n\n## Control Surfaces\n\n"
            "- **Source**: `.gzkit/manifest.json`\n"
            f"- **Updated**: {updated}\n",
            encoding="utf-8",
        )
        return templates, tmp

    @covers("REQ-0.0.37-02-03")
    def test_project_variables_are_substituted(self) -> None:
        from gzkit.governance.compose import render_agents_md

        with tempfile.TemporaryDirectory() as tmp:
            template_root, project_root = self._scaffold(Path(tmp))
            rendered = render_agents_md({}, template_root, project_root).decode("utf-8")
        self.assertNotIn("{project_name}", rendered)
        self.assertNotIn("{local_content}", rendered)
        self.assertIn("demoproj", rendered)
        self.assertIn("demo local rule.", rendered)

    @covers("REQ-0.0.37-02-01")
    def test_sync_date_sourced_from_committed_agents_md(self) -> None:
        from gzkit.governance.compose import render_agents_md

        with tempfile.TemporaryDirectory() as tmp:
            template_root, project_root = self._scaffold(Path(tmp), updated="2025-01-01")
            rendered = render_agents_md({}, template_root, project_root).decode("utf-8")
        self.assertIn("**Updated**: 2025-01-01", rendered)
        self.assertNotIn("{sync_date}", rendered)

    @covers("REQ-0.0.37-02-01")
    def test_render_is_idempotent_across_two_calls(self) -> None:
        from gzkit.governance.compose import render_agents_md

        with tempfile.TemporaryDirectory() as tmp:
            template_root, project_root = self._scaffold(Path(tmp))
            first = render_agents_md({}, template_root, project_root)
            (project_root / "AGENTS.md").write_bytes(first)
            second = render_agents_md({}, template_root, project_root)
        self.assertEqual(first, second, "re-render of committed output must be byte-identical")


if __name__ == "__main__":
    unittest.main()
