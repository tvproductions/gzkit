"""Tests for the Jinja2 render pipeline (OBPI-0.0.34-02).

Covers:
  REQ-0.0.34-02-05 — typed TemplateNotFound raised for unknown vendor, fail-closed
"""

import unittest

from gzkit.content.models import Rule
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
