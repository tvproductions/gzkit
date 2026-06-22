"""Unit tests for GATE5_INVARIANTS — the never-relax floor (OBPI-0.0.74-03).

REQ-0.0.74-03-01 [behavior]: GATE5_INVARIANTS is a code constant naming exactly
the five never-relax guards including grader-gaming.

REQ-0.0.74-03-02 [behavior]: the leveled checkpoint cannot resolve a gate5_invariant
member below CRITICAL — even under an active marker.

REQ-0.0.74-03-03 [structural-fence]: proof channel is parent ADR § Boundary
Invariants #3 — no @covers test required or appropriate.
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


_EXPECTED_MEMBERS = frozenset(
    {
        "gate5-attestation",
        "secrets",
        "operator-pii",
        "ledger",
        "grader-gaming",
    }
)


class TestGate5InvariantsConstant(unittest.TestCase):
    """REQ-0.0.74-03-01: GATE5_INVARIANTS names exactly the five never-relax guards."""

    @covers("REQ-0.0.74-03-01")
    def test_exactly_five_members(self) -> None:
        from gzkit.mx.invariants import GATE5_INVARIANTS

        self.assertEqual(
            len(GATE5_INVARIANTS),
            5,
            f"Expected exactly 5 members; got {len(GATE5_INVARIANTS)}: {sorted(GATE5_INVARIANTS)}",
        )

    @covers("REQ-0.0.74-03-01")
    def test_all_five_guards_present(self) -> None:
        from gzkit.mx.invariants import GATE5_INVARIANTS

        self.assertEqual(
            GATE5_INVARIANTS,
            _EXPECTED_MEMBERS,
            f"Constant does not match expected set; diff: {GATE5_INVARIANTS ^ _EXPECTED_MEMBERS}",
        )

    @covers("REQ-0.0.74-03-01")
    def test_is_frozenset_code_constant(self) -> None:
        from gzkit.mx.invariants import GATE5_INVARIANTS

        self.assertIsInstance(
            GATE5_INVARIANTS,
            frozenset,
            "GATE5_INVARIANTS must be a frozenset (immutable code constant, not config)",
        )

    @covers("REQ-0.0.74-03-01")
    def test_grader_gaming_is_member(self) -> None:
        from gzkit.mx.invariants import GATE5_INVARIANTS

        self.assertIn(
            "grader-gaming",
            GATE5_INVARIANTS,
            "grader-gaming must be a member — the 5th never-relax guard (ADR-0.0.74 item 3)",
        )


class TestCheckpointCannotDowngradeInvariant(unittest.TestCase):
    """REQ-0.0.74-03-02: checkpoint structurally cannot resolve a gate5_invariant below CRITICAL."""

    @covers("REQ-0.0.74-03-02")
    def test_invariants_resolve_fail_closed_outside_hangar(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            for member in GATE5_INVARIANTS:
                with self.subTest(member=member):
                    result = checkpoint.resolve(member, levels.WARNING, root)
                    # CRITICAL level routes to AOG_MX_HANGAR — the grounding route
                    self.assertEqual(
                        result,
                        disposition.Route.AOG_MX_HANGAR,
                        f"'{member}' must resolve CRITICAL outside the hangar",
                    )

    @covers("REQ-0.0.74-03-02")
    def test_invariants_resolve_fail_closed_inside_hangar(self) -> None:
        from gzkit.mx import checkpoint, disposition, levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            for member in GATE5_INVARIANTS:
                with self.subTest(member=member):
                    result = checkpoint.resolve(member, levels.WARNING, root)
                    # gate5_invariants pin to CRITICAL (AOG_MX_HANGAR) even inside the hangar
                    self.assertEqual(
                        result,
                        disposition.Route.AOG_MX_HANGAR,
                        f"'{member}' must stay CRITICAL inside the hangar",
                    )

    @covers("REQ-0.0.74-03-02")
    def test_grader_gaming_cannot_be_downgraded_in_hangar(self) -> None:
        """grader-gaming specifically cannot go advisory inside the hangar."""
        from gzkit.mx import checkpoint, disposition, levels

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            result = checkpoint.resolve("grader-gaming", levels.WARNING, root)
            self.assertEqual(
                result,
                disposition.Route.AOG_MX_HANGAR,
                "grader-gaming must stay CRITICAL — cannot make MX the safe vibing place",
            )

    @covers("REQ-0.0.74-03-02")
    def test_checkpoint_is_not_advisory_for_any_invariant_in_hangar(self) -> None:
        from gzkit.mx import checkpoint
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_marker(root)
            for member in GATE5_INVARIANTS:
                with self.subTest(member=member):
                    self.assertFalse(
                        checkpoint.is_advisory(member, root),
                        f"gate5_invariant '{member}' must not be advisory in the hangar",
                    )
