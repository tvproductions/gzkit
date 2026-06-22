"""Unit tests for MX disposition handler and checkpoint.resolve() (OBPI-0.0.74-12).

REQ-0.0.74-12-01 and REQ-0.0.74-12-02 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below. REQ-0.0.74-12-03 is a [structural-fence]
REQ — its proof channel is the parent ADR § Boundary Invariants #2 (one
disposition handler routes the checkpoint-resolved level); no ``@covers`` test
is authored for it per ADR-0.0.59.
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


class TestDispositionMatrix(unittest.TestCase):
    """REQ-0.0.74-12-02: the one handler maps level→route per the ADR matrix."""

    @covers("REQ-0.0.74-12-02")
    def test_each_matrix_row(self) -> None:
        from gzkit.mx import disposition, levels

        expected = [
            (levels.CRITICAL, disposition.Route.AOG_MX_HANGAR),
            (levels.ERROR, disposition.Route.BLOCK_GHI_FIX),
            (levels.WARNING, disposition.Route.REFACTOR_CHORES),
            (levels.NOTICE, disposition.Route.DRIFT_DRAIN),
            (levels.INFO, disposition.Route.TRACK),
            (levels.DEBUG, disposition.Route.STEERING),
        ]
        for level, expected_route in expected:
            with self.subTest(level=level):
                self.assertEqual(disposition.route(level), expected_route)


class TestCheckpointResolveInterface(unittest.TestCase):
    """REQ-0.0.74-12-01: a guard emits a GZ_<LEVEL> sensor reading; the
    checkpoint.resolve() call-site is the one place the disposition is computed."""

    @covers("REQ-0.0.74-12-01")
    def test_resolve_callable_with_level_arg(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # No marker — normal (outside-hangar) call
            result = checkpoint.resolve("gate3-docs", levels.WARNING, root)
            self.assertIsInstance(result, disposition.Route)


class TestUnderMarkerDemotion(unittest.TestCase):
    """REQ-0.0.74-12-02 (under-marker behaviour): non-floor guards demote to
    ADVISORY; gate5_invariants pin to CRITICAL; the CRITICAL floor is never
    demoted even for non-invariant guards."""

    @covers("REQ-0.0.74-12-02")
    def test_non_floor_guard_demotes_to_advisory(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            result = checkpoint.resolve("gate3-docs", levels.WARNING, root)
            self.assertEqual(result, disposition.Route.ADVISORY)

    @covers("REQ-0.0.74-12-02")
    def test_gate5_invariant_pins_critical_route(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            for invariant in checkpoint.GATE5_INVARIANTS:
                with self.subTest(invariant=invariant):
                    result = checkpoint.resolve(invariant, levels.WARNING, root)
                    self.assertEqual(
                        result,
                        disposition.Route.AOG_MX_HANGAR,
                        f"gate5_invariant '{invariant}' must pin to CRITICAL route under marker",
                    )

    @covers("REQ-0.0.74-12-02")
    def test_critical_emitted_stays_aog_under_marker(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            # CRITICAL is the floor — non-invariant guard emitting CRITICAL must
            # still route to AOG_MX_HANGAR (no demotion below floor).
            result = checkpoint.resolve("gate3-docs", levels.CRITICAL, root)
            self.assertEqual(result, disposition.Route.AOG_MX_HANGAR)
