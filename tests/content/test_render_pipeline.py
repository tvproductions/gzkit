"""Tests for the Jinja2 render pipeline (OBPI-0.0.34-02, OBPI-0.0.37-27).

Covers:
  REQ-0.0.34-02-05 — typed TemplateNotFound raised for unknown vendor, fail-closed
  REQ-0.0.37-27-02 — the inert temperature-projection filter is retired; render output
                     is byte-identical across all valid temperatures; unknown temperature
                     still fails closed before template lookup
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


class TestTemperatureProjectionRetired(unittest.TestCase):
    """The temperature-projection filter is retired (OBPI-0.0.37-27).

    REQ-0.0.37-27-02: removing `_bullet_renders` / `_project_for_temperature` leaves
    render output unchanged — the dial was empirically inert. The `temperature`
    parameter survives for per-vendor routing parity but no longer filters the model.
    """

    @covers("REQ-0.0.37-27-02")
    def test_render_byte_identical_across_temperatures(self) -> None:
        """A contract with classification-varied bullets and a non-default-ordered,
        tier-tagged pillar renders byte-identically at lite/medium/heavy — proving the
        projection filter (density + section withholding + order sort) is gone. Before
        retirement these inputs produced three different byte streams."""
        contract = AgentContract(
            name="Projection Retired Agent",
            purpose="Pinning that temperature no longer projects the model",
            rules=[
                Bullet(text="plain rule"),
                Bullet(text="judgment rule", classification="Judgment"),
            ],
            pillars=[
                Pillar(
                    id="second",
                    title="SECOND_SECTION",
                    order=2,
                    tier="heavy",
                    bullets=[Bullet(text="second bullet")],
                ),
                Pillar(
                    id="first",
                    title="FIRST_SECTION",
                    order=1,
                    enabled=False,
                    bullets=[Bullet(text="first bullet")],
                ),
            ],
        )
        lite = render(contract, "claude", temperature="lite")
        medium = render(contract, "claude", temperature="medium")
        heavy = render(contract, "claude", temperature="heavy")
        self.assertEqual(lite, medium, "lite and medium renders must be byte-identical")
        self.assertEqual(medium, heavy, "medium and heavy renders must be byte-identical")
        # The previously-withheld section MUST now appear at every temperature — proof the
        # enabled/tier section-withholding filter is gone, not merely that bytes match.
        self.assertIn(
            "FIRST_SECTION",
            heavy.decode("utf-8"),
            "Formerly enabled=False section must now render (projection filter retired)",
        )
        self.assertIn(
            "SECOND_SECTION",
            lite.decode("utf-8"),
            "Formerly tier='heavy' section must now render at lite (projection filter retired)",
        )

    @covers("REQ-0.0.37-27-02")
    def test_unknown_temperature_raises_before_lookup(self) -> None:
        """render() with an unknown temperature must still raise ValueError before template
        lookup — fail-closed routing parity survives the projection retirement. A nonexistent
        vendor proves ordering: if temperature validation ran after vendor lookup,
        TemplateNotFound would surface first."""
        contract = AgentContract(
            name="Validation Test Agent",
            purpose="Testing temperature validation ordering",
        )
        with self.assertRaises(ValueError):
            render(contract, "__nonexistent_vendor__", temperature="ultra")
