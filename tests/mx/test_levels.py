"""Unit tests for the GZ_<LEVEL> severity vocabulary (OBPI-0.0.74-11).

The vocabulary is the single graded severity authority the MX shared checkpoint
resolves each guard's effective level against (parent ADR § Boundary Invariants
#2).

REQ-0.0.74-11-01 and REQ-0.0.74-11-02 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below. REQ-0.0.74-11-03 is a [structural-fence]
REQ — its proof channel is the parent ADR § Boundary Invariants #2 (the
checkpoint is the single LEVELED severity authority) per ADR-0.0.59, not a
``@covers`` test; it is intentionally not decorated here.
"""

import logging
import unittest

from gzkit.mx import levels
from gzkit.traceability import covers


class TestLadderReusesStdlib(unittest.TestCase):
    """REQ-0.0.74-11-01: the ladder reuses Python ``logging``'s constants and
    adds ``NOTICE = 25`` as the agent-fidelity / V.I.B.E.S. drift band."""

    @covers("REQ-0.0.74-11-01")
    def test_ladder_rungs_equal_logging_constants(self) -> None:
        # Rungs ARE the stdlib constants (identity of value), not hand-typed
        # magic numbers — STDLIB-FIRST. If logging's constants ever changed,
        # these would track them, which is the point.
        self.assertEqual(levels.CRITICAL, logging.CRITICAL)
        self.assertEqual(levels.ERROR, logging.ERROR)
        self.assertEqual(levels.WARNING, logging.WARNING)
        self.assertEqual(levels.INFO, logging.INFO)
        self.assertEqual(levels.DEBUG, logging.DEBUG)

    @covers("REQ-0.0.74-11-01")
    def test_notice_is_the_rung_python_omits(self) -> None:
        # NOTICE = 25 is the rung Python omits — it sits strictly between
        # INFO (20) and WARNING (30), the drift band.
        self.assertEqual(levels.NOTICE, 25)
        self.assertLess(levels.INFO, levels.NOTICE)
        self.assertLess(levels.NOTICE, levels.WARNING)
        # Confirm we are ADDING a rung, not shadowing an existing stdlib one.
        self.assertFalse(hasattr(logging, "NOTICE"))


class TestGroundingThreshold(unittest.TestCase):
    """REQ-0.0.74-11-02: ``grounds()`` grounds iff effective severity
    ``>= ERROR``; WARNING / NOTICE / INFO / DEBUG are visible-but-non-grounding."""

    @covers("REQ-0.0.74-11-02")
    def test_at_and_above_error_grounds(self) -> None:
        self.assertTrue(levels.grounds(levels.ERROR))
        self.assertTrue(levels.grounds(levels.CRITICAL))

    @covers("REQ-0.0.74-11-02")
    def test_below_error_is_visible_non_grounding(self) -> None:
        for level in (levels.WARNING, levels.NOTICE, levels.INFO, levels.DEBUG):
            with self.subTest(level=level):
                self.assertFalse(levels.grounds(level))

    @covers("REQ-0.0.74-11-02")
    def test_grounding_threshold_is_error(self) -> None:
        # The threshold is ERROR, not a hand-picked magic number — the boundary
        # is the semantic anchor the substrate routes against.
        self.assertEqual(levels.GROUNDING_THRESHOLD, levels.ERROR)


if __name__ == "__main__":
    unittest.main()
