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


class TestRouteGrounds(unittest.TestCase):
    """REQ-0.0.74-12-02 (consumer surface, GHI #637): the disposition handler
    exposes a Route-grounding predicate so a guard holding a resolved Route can
    ask 'does this block?' without re-deriving the level→route matrix. Grounding
    band (>= ERROR) routes block; the V.I.B.E.S.-management band does not."""

    @covers("REQ-0.0.74-12-02")
    def test_grounding_band_routes_block(self) -> None:
        from gzkit.mx import disposition

        for route in (disposition.Route.AOG_MX_HANGAR, disposition.Route.BLOCK_GHI_FIX):
            with self.subTest(route=route):
                self.assertTrue(disposition.grounds(route))

    @covers("REQ-0.0.74-12-02")
    def test_vibes_band_and_advisory_do_not_ground(self) -> None:
        from gzkit.mx import disposition

        non_grounding = (
            disposition.Route.REFACTOR_CHORES,
            disposition.Route.DRIFT_DRAIN,
            disposition.Route.TRACK,
            disposition.Route.STEERING,
            disposition.Route.ADVISORY,
        )
        for route in non_grounding:
            with self.subTest(route=route):
                self.assertFalse(disposition.grounds(route))

    @covers("REQ-0.0.74-12-02")
    def test_grounds_agrees_with_levels_grounding_threshold(self) -> None:
        # Semantic anchor: a route grounds iff the level that produces it grounds
        # (levels.grounds). The two grounding authorities must not diverge.
        from gzkit.mx import disposition, levels

        for level in (
            levels.CRITICAL,
            levels.ERROR,
            levels.WARNING,
            levels.NOTICE,
            levels.INFO,
            levels.DEBUG,
        ):
            with self.subTest(level=level):
                self.assertEqual(
                    disposition.grounds(disposition.route(level)), levels.grounds(level)
                )


class TestLeveledConsumptionEquivalence(unittest.TestCase):
    """GHI #637: a guard consuming the leveled pipeline via
    disposition.grounds(checkpoint.resolve(name, ERROR, root)) must be
    behaviorally identical to the legacy boolean (not is_advisory(name, root))
    across every context — outside the hangar, under the hangar for a non-floor
    guard, and for a gate5_invariant. This is the contract that lets the
    migration preserve observable fail-closed/warn behavior (parent ADR BI#2:
    a single leveled severity authority)."""

    @covers("REQ-0.0.74-12-01")
    def test_leveled_grounding_matches_not_is_advisory(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels

        guards = (
            "rendition-freshness",
            "rendition-floor-coherence",
            "gate3-docs",
            "ledger",
        )
        for marker_active in (False, True):
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                if marker_active:
                    _write_marker(root)
                for guard in guards:
                    with self.subTest(guard=guard, marker=marker_active):
                        route = checkpoint.resolve(guard, levels.ERROR, root)
                        leveled = disposition.grounds(route)
                        legacy = not checkpoint.is_advisory(guard, root)
                        self.assertEqual(leveled, legacy)
