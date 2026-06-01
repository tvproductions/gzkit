"""Tests for the Jinja2 render pipeline (OBPI-0.0.34-02, OBPI-0.0.37-12).

Covers:
  REQ-0.0.34-02-05 — typed TemplateNotFound raised for unknown vendor, fail-closed
  REQ-0.0.37-12-01 — lite temperature omits heavy-density bullets, never Judgment bullets
  REQ-0.0.37-12-02 — unknown temperature raises ValueError before template lookup
  REQ-0.0.37-12-03 — disabled/above-tier sections absent; section order follows order
  REQ-0.0.37-12-05 — heavy renders a strict superset of lite content (monotonic density)
"""

import unittest

from gzkit.content.models import AgentContract, Bullet, Rule
from gzkit.content.models.agent_contract import Pillar
from gzkit.content.render import TemplateNotFound, render
from gzkit.traceability import covers


class TestRenderPipeline(unittest.TestCase):
    """Render pipeline dispatcher tests."""

    @covers("REQ-0.0.34-02-05")
    def test_template_not_found_raises_for_unknown_vendor(self) -> None:
        """render() must raise TemplateNotFound for an unregistered vendor — fail-closed."""
        rule = Rule(title="Test Rule", version="1.0.0", paths=[], body=[])
        with self.assertRaises(TemplateNotFound) as ctx:
            render(rule, vendor="__nonexistent_vendor__")
        exc = ctx.exception
        self.assertEqual(exc.content_type, "Rule")
        self.assertEqual(exc.vendor, "__nonexistent_vendor__")

    def test_template_not_found_is_exception(self) -> None:
        """TemplateNotFound must be a proper Exception subclass."""
        self.assertTrue(issubclass(TemplateNotFound, Exception))

    def test_template_not_found_attributes(self) -> None:
        """TemplateNotFound carries content_type and vendor attributes."""
        exc = TemplateNotFound(content_type="Skill", vendor="unknown")
        self.assertEqual(exc.content_type, "Skill")
        self.assertEqual(exc.vendor, "unknown")

    @covers("REQ-0.0.34-02-03")
    def test_sync_surfaces_exposes_render_content_surface(self) -> None:
        """sync_surfaces must expose render_content_surface() that uses the render pipeline."""
        import gzkit.sync_surfaces as ss  # noqa: PLC0415

        self.assertTrue(
            callable(getattr(ss, "render_content_surface", None)),
            "sync_surfaces.render_content_surface must be a callable",
        )
        # Verify it actually calls render() by checking a real model writes rendered bytes.
        import tempfile  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        from gzkit.content.models import Rule  # noqa: PLC0415

        rule = Rule(title="Sync Test", version="1.0.0", paths=[], body=[])
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out" / "rule.md"
            project_root = Path(tmp)
            updated: list[str] = []
            ss.render_content_surface(rule, dest, "claude", project_root, updated)
            self.assertTrue(dest.exists())
            content = dest.read_bytes()
            self.assertGreater(len(content), 0)
            self.assertIn(b"Sync Test", content)
            self.assertEqual(updated, ["out/rule.md"])


class TestTemperatureRenderer(unittest.TestCase):
    """Temperature-aware render pipeline tests (OBPI-0.0.37-12)."""

    @covers("REQ-0.0.37-12-01")
    def test_lite_temperature_omits_heavy_bullets(self) -> None:
        """render() at temperature='lite' must omit heavy-density bullets but keep Judgment
        and density_min=None bullets — they always render (0-Kelvin floor)."""
        contract = AgentContract(
            name="Density Test Agent",
            purpose="Testing density-aware rendering",
            rules=[
                Bullet(text="HEAVY_BULLET_MARKER", density_min="heavy"),
                Bullet(text="NONE_DENSITY_BULLET_MARKER"),
                Bullet(text="JUDGMENT_BULLET_MARKER", classification="Judgment"),
            ],
        )
        output = render(contract, "claude", temperature="lite").decode("utf-8")
        self.assertNotIn(
            "HEAVY_BULLET_MARKER",
            output,
            "Heavy-density bullet must be omitted at lite temperature",
        )
        self.assertIn(
            "NONE_DENSITY_BULLET_MARKER",
            output,
            "Bullet with density_min=None must render at every temperature",
        )
        self.assertIn(
            "JUDGMENT_BULLET_MARKER",
            output,
            "Judgment-classified bullet must render at every temperature (0-Kelvin floor)",
        )

    @covers("REQ-0.0.37-12-01")
    def test_medium_temperature_includes_medium_bullets(self) -> None:
        """render() at temperature='medium' must include medium-density bullets but omit
        heavy-density bullets — exercising the medium tier boundary."""
        contract = AgentContract(
            name="Medium Density Test Agent",
            purpose="Testing medium tier boundary",
            rules=[
                Bullet(text="HEAVY_DENSITY_BULLET", density_min="heavy"),
                Bullet(text="MEDIUM_DENSITY_BULLET", density_min="medium"),
                Bullet(text="ALWAYS_PRESENT_BULLET"),
            ],
        )
        output = render(contract, "claude", temperature="medium").decode("utf-8")
        self.assertIn(
            "MEDIUM_DENSITY_BULLET",
            output,
            "Medium-density bullet must render at medium temperature",
        )
        self.assertNotIn(
            "HEAVY_DENSITY_BULLET",
            output,
            "Heavy-density bullet must be omitted at medium temperature",
        )
        self.assertIn(
            "ALWAYS_PRESENT_BULLET",
            output,
            "Bullet with density_min=None must render at every temperature",
        )

    @covers("REQ-0.0.37-12-02")
    def test_unknown_temperature_raises_before_lookup(self) -> None:
        """render() with an unknown temperature must raise ValueError before template
        lookup — fail-closed. Using a nonexistent vendor proves ordering: if temperature
        validation ran after vendor lookup, TemplateNotFound would appear first."""
        contract = AgentContract(
            name="Validation Test Agent",
            purpose="Testing temperature validation ordering",
        )
        with self.assertRaises(ValueError):
            render(contract, "__nonexistent_vendor__", temperature="ultra")

    @covers("REQ-0.0.37-12-03")
    def test_disabled_section_absent_from_output(self) -> None:
        """A Pillar with enabled=False must be absent from output regardless of temperature."""
        contract = AgentContract(
            name="Section Test Agent",
            purpose="Testing section withholding",
            pillars=[
                Pillar(id="enabled-section", title="ENABLED_SECTION_TITLE", order=1),
                Pillar(
                    id="disabled-section",
                    title="DISABLED_SECTION_TITLE",
                    order=2,
                    enabled=False,
                ),
            ],
        )
        output = render(contract, "claude", temperature="heavy").decode("utf-8")
        self.assertIn(
            "ENABLED_SECTION_TITLE",
            output,
            "Enabled section must appear in output",
        )
        self.assertNotIn(
            "DISABLED_SECTION_TITLE",
            output,
            "Disabled section must be absent from output regardless of temperature",
        )

    @covers("REQ-0.0.37-12-03")
    def test_high_tier_section_withheld_at_lite(self) -> None:
        """A Pillar with tier='heavy' must be absent at lite; a tier='lite' pillar must remain.

        Positive control: lite-tier section IS present at lite temperature.
        Negative control: heavy-tier section is NOT present at lite temperature.
        This distinguishes a correct implementation from one that over-withholds all sections.
        """
        contract = AgentContract(
            name="Tier Test Agent",
            purpose="Testing tier-based section withholding",
            pillars=[
                Pillar(id="heavy-section", title="HEAVY_TIER_SECTION_TITLE", order=1, tier="heavy"),
                Pillar(id="lite-section", title="LITE_TIER_SECTION_TITLE", order=2, tier="lite"),
            ],
        )
        output = render(contract, "claude", temperature="lite").decode("utf-8")
        self.assertNotIn(
            "HEAVY_TIER_SECTION_TITLE",
            output,
            "Section with tier='heavy' must be withheld at lite temperature",
        )
        self.assertIn(
            "LITE_TIER_SECTION_TITLE",
            output,
            "Section with tier='lite' must be present at lite temperature (positive control)",
        )

    @covers("REQ-0.0.37-12-03")
    def test_section_order_in_output(self) -> None:
        """Sections must appear in ascending order regardless of construction order."""
        contract = AgentContract(
            name="Order Test Agent",
            purpose="Testing section ordering",
            pillars=[
                Pillar(id="second-section", title="SECOND_SECTION_MARKER", order=2),
                Pillar(id="first-section", title="FIRST_SECTION_MARKER", order=1),
            ],
        )
        output = render(contract, "claude", temperature="heavy").decode("utf-8")
        first_pos = output.find("FIRST_SECTION_MARKER")
        second_pos = output.find("SECOND_SECTION_MARKER")
        self.assertGreater(first_pos, -1, "First section (order=1) must appear in output")
        self.assertGreater(second_pos, -1, "Second section (order=2) must appear in output")
        self.assertLess(
            first_pos,
            second_pos,
            "Section order=1 must precede order=2 in rendered output",
        )

    @covers("REQ-0.0.37-12-03")
    def test_judgment_bullet_in_withheld_section_is_dropped(self) -> None:
        """Section-withholding wins over the 0-Kelvin Judgment floor: a Judgment bullet
        inside a disabled or above-tier pillar is dropped with the whole section.

        REQ-03 ("a section MUST be withheld when enabled=False or tier above temperature")
        is unconditional — it is the coarse axis above the per-bullet Judgment floor (REQ-01).
        """
        contract = AgentContract(
            name="Withheld Judgment Agent",
            purpose="Pinning the section-withholding-wins resolution",
            pillars=[
                Pillar(
                    id="disabled-with-judgment",
                    title="DISABLED_PILLAR_TITLE",
                    order=1,
                    enabled=False,
                    bullets=[Bullet(text="JUDGMENT_IN_DISABLED_MARKER", classification="Judgment")],
                ),
                Pillar(
                    id="high-tier-with-judgment",
                    title="HIGH_TIER_PILLAR_TITLE",
                    order=2,
                    tier="heavy",
                    bullets=[
                        Bullet(text="JUDGMENT_IN_HIGH_TIER_MARKER", classification="Judgment")
                    ],
                ),
            ],
        )
        output = render(contract, "claude", temperature="lite").decode("utf-8")
        self.assertNotIn(
            "JUDGMENT_IN_DISABLED_MARKER",
            output,
            "Judgment bullet in a disabled section must be dropped (section-withholding wins)",
        )
        self.assertNotIn(
            "JUDGMENT_IN_HIGH_TIER_MARKER",
            output,
            "Judgment bullet in an above-tier section must be dropped at lite "
            "(section-withholding wins)",
        )

    @covers("REQ-0.0.37-12-05")
    def test_heavy_is_strict_superset_of_lite(self) -> None:
        """render() at temperature='heavy' must produce output >= lite in length
        (monotonic density): every line in lite output is also present in heavy output,
        AND heavy contains content that lite does not (strictly larger, not equal)."""
        contract = AgentContract(
            name="Superset Test Agent",
            purpose="Testing monotonic density across temperatures",
            rules=[
                Bullet(text="HEAVY_ONLY_BULLET", density_min="heavy"),
                Bullet(text="MEDIUM_ONLY_BULLET", density_min="medium"),
                Bullet(text="LITE_BULLET"),
                Bullet(text="JUDGMENT_BULLET", classification="Judgment"),
            ],
        )
        lite_out = render(contract, "claude", temperature="lite")
        heavy_out = render(contract, "claude", temperature="heavy")
        self.assertGreaterEqual(
            len(heavy_out),
            len(lite_out),
            "Heavy temperature output must be >= lite in byte length (monotonic density)",
        )
        lite_lines = set(lite_out.decode("utf-8").splitlines())
        heavy_lines = set(heavy_out.decode("utf-8").splitlines())
        missing = lite_lines - heavy_lines
        self.assertEqual(
            missing,
            set(),
            f"These lines in lite output are missing from heavy output: {missing!r}",
        )
        # Strictness check: heavy must contain content that lite does not.
        # An implementation that always renders all bullets (ignoring temperature)
        # would have lite_out == heavy_out — this assertion proves it does not.
        self.assertIn(
            "HEAVY_ONLY_BULLET",
            heavy_out.decode("utf-8"),
            "Heavy-density bullet must appear in heavy temperature output",
        )
        self.assertNotIn(
            "HEAVY_ONLY_BULLET",
            lite_out.decode("utf-8"),
            "Heavy-density bullet must NOT appear in lite output (strict superset proof)",
        )
