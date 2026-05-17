"""Tests for gz check pipeline composition (OBPI-0.0.35-04 wiring)."""

from __future__ import annotations

import unittest

from gzkit.commands.quality import _build_check_steps
from gzkit.traceability import covers


class TestCheckPipelineComposition(unittest.TestCase):
    """Verify gz check pipeline includes the kind-invariance scope."""

    @covers("REQ-0.0.35-04-06")
    def test_kind_invariance_in_check_pipeline(self):
        """Default gz check pipeline includes Kind invariance scope."""
        steps = _build_check_steps()
        step_names = [name for name, _ in steps]
        self.assertIn("Kind invariance", step_names)


if __name__ == "__main__":
    unittest.main()
