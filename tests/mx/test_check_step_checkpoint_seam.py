"""Unit tests for the gz check step-layer checkpoint seam (OBPI-0.0.74-20).

The seam lives in ``_apply_mx_seam`` (``src/gzkit/commands/quality.py``):
a single function called once per step in the ``check()`` loop that routes
each step's ``returncode=3`` result through ``checkpoint.resolve`` — demoting
to advisory under an active marker, preserving full strength outside.

REQ-0.0.74-20-01 and -02 are BEHAVIOR REQs proven by ``@covers``-decorated
methods.  REQ-0.0.74-20-03 is proven by ``TestFloorPin``.
REQ-0.0.74-20-04 is proven by ``TestExcludedPaths``.
REQ-0.0.74-20-05 is a [FENCE] REQ — proof channel is parent ADR
§ Boundary Invariants #2 (OBPI-02, OBPI-09, OBPI-11, OBPI-12, OBPI-20);
not proven by a ``@covers`` test.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mx import marker
from gzkit.mx.marker import Marker
from gzkit.traceability import covers


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _write_marker(root: Path) -> None:
    marker.write(Marker(session_id="test-session"), root)


def _failing_result():
    """Return a QualityResult representing a policy-breach (returncode=3)."""
    from gzkit.quality import QualityResult

    return QualityResult(
        success=False,
        command="test-step",
        stdout="violation found",
        stderr="",
        returncode=3,
    )


class TestDemoteUnderMarker(unittest.TestCase):
    """REQ-0.0.74-20-01/-02: non-floor step demotes under marker, full-strength outside."""

    @covers("REQ-0.0.74-20-01")
    def test_non_floor_step_demotes_to_advisory_under_marker(self) -> None:
        """Under an active marker a non-floor step's returncode=3 demotes to success."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)

            result = _apply_mx_seam(_failing_result(), "test-guard", levels.ERROR, root)

            self.assertTrue(
                result.success,
                "Non-floor step must demote to advisory (success=True) under marker",
            )
            self.assertEqual(result.returncode, 0, "Demoted result must have returncode=0")

    @covers("REQ-0.0.74-20-02")
    def test_non_floor_step_stays_fatal_without_marker(self) -> None:
        """Without a marker a non-floor step's returncode=3 stays fatal (full strength)."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # No marker written — outside the hangar

            result = _apply_mx_seam(_failing_result(), "test-guard", levels.ERROR, root)

            self.assertFalse(
                result.success,
                "Non-floor step must stay fatal (success=False) without marker",
            )
            self.assertEqual(result.returncode, 3, "Fatal result must retain returncode=3")

    @covers("REQ-0.0.74-20-02")
    def test_success_result_passes_through_unchanged(self) -> None:
        """A passing result (returncode=0) is not modified by the seam."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.quality import QualityResult

        passing = QualityResult(success=True, command="test", stdout="ok", stderr="", returncode=0)
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)  # marker active — should make no difference

            result = _apply_mx_seam(passing, "test-guard", levels.ERROR, root)

            self.assertTrue(result.success)
            self.assertEqual(result.returncode, 0)


class TestFloorPin(unittest.TestCase):
    """REQ-0.0.74-20-03: gate5_invariants guard_names pin CRITICAL and never demote."""

    @covers("REQ-0.0.74-20-03")
    def test_gate5_invariant_step_stays_fatal_under_marker(self) -> None:
        """Every gate5_invariants member stays fatal (returncode=3) even under marker."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)

            for invariant in GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    result = _apply_mx_seam(_failing_result(), invariant, levels.ERROR, root)
                    self.assertFalse(
                        result.success,
                        f"Floor member '{invariant}' must stay fatal under marker",
                    )
                    self.assertEqual(
                        result.returncode,
                        3,
                        f"Floor member '{invariant}' must retain returncode=3 under marker",
                    )

    @covers("REQ-0.0.74-20-03")
    def test_gate5_invariant_step_stays_fatal_outside_marker(self) -> None:
        """gate5_invariants members are fatal outside the marker too (no regression)."""
        from gzkit.commands.quality import _apply_mx_seam
        from gzkit.mx import levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # No marker

            for invariant in GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    result = _apply_mx_seam(_failing_result(), invariant, levels.ERROR, root)
                    self.assertFalse(result.success)
                    self.assertEqual(result.returncode, 3)


class TestExcludedPaths(unittest.TestCase):
    """REQ-0.0.74-20-04: excluded policy paths are not routed through the seam."""

    @covers("REQ-0.0.74-20-04")
    def test_excluded_guard_names_absent_from_step_guard_meta(self) -> None:
        """_STEP_GUARD_META contains no guard_name matching the excluded policy paths."""
        from gzkit.commands.quality import _STEP_GUARD_META

        guard_names = set(_STEP_GUARD_META.values())
        # Each value is (guard_name, emitted_level); extract guard_names
        step_guard_names = {gn for gn, _ in guard_names}

        # The sensitivity security-floor handler and attestation lane/kind handler
        # must NOT appear in the step guard metadata — they self-decide and bypass
        # the seam entirely.
        for excluded in ("sensitivity", "attestation-lane-kind"):
            self.assertNotIn(
                excluded,
                step_guard_names,
                f"Excluded policy path '{excluded}' must not be in _STEP_GUARD_META",
            )

    @covers("REQ-0.0.74-20-04")
    def test_sensitivity_guard_name_not_in_build_check_steps(self) -> None:
        """_build_check_steps() step names do not include a sensitivity-mapped step."""
        from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps

        steps = _build_check_steps()
        step_display_names = {name for name, _ in steps}

        # Resolve guard_names for all current steps
        step_guard_names = {
            _STEP_GUARD_META.get(name, (name.lower().replace(" ", "-"), None))[0]
            for name in step_display_names
        }

        # The sensitivity handler must not appear as a guard routed through the seam.
        self.assertNotIn(
            "sensitivity",
            step_guard_names,
            "The --sensitivity handler must not be wired through the checkpoint seam",
        )
