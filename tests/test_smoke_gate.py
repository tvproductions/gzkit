"""The smoke tier's budget must be enforced by something (GHI #724).

The 60s ceiling sat in `.gzkit/rules/tests.md` as prose with no consumer, so a
4.5x breach was invisible to everything but a stopwatch. These tests pin the
consumer's three outcomes — and specifically that an EMPTY tier is a breach
rather than a pass, since a subset with no members satisfies any budget.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.smoke_cmd import smoke_cmd, smoke_gate
from gzkit.smoke import SMOKE_BUDGET_SECONDS, smoke, smoke_marked_files

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MarkerIsMetadataOnly(unittest.TestCase):
    """`@smoke` must not change what the test does."""

    def test_decorated_function_still_runs_and_returns(self) -> None:
        @smoke
        def sample() -> str:
            return "ran"

        self.assertEqual(sample(), "ran")

    def test_decorated_function_carries_the_marker(self) -> None:
        @smoke
        def sample() -> None:
            return None

        self.assertTrue(getattr(sample, "__gzkit_smoke__", False))


class EmptyTierIsABreach(unittest.TestCase):
    """Green-by-emptiness is the failure a budget gate invites."""

    def test_empty_tier_exits_policy_breach(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "tests").mkdir()
            self.assertEqual(smoke_gate(Path(tmp)), 3)

    def test_empty_tier_is_not_reported_as_success(self) -> None:
        """A zero-member run would otherwise finish in 0.00s and 'pass'."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "tests").mkdir()
            self.assertNotEqual(smoke_gate(Path(tmp)), 0)


class BudgetIsEnforced(unittest.TestCase):
    """The ceiling must have teeth, and the default must come from the rule."""

    def test_over_budget_run_exits_policy_breach(self) -> None:
        self.assertEqual(smoke_gate(_PROJECT_ROOT, budget=0.0), 3)

    def test_within_budget_run_exits_zero(self) -> None:
        self.assertEqual(smoke_gate(_PROJECT_ROOT), 0)

    def test_default_budget_is_the_rule_declared_ceiling(self) -> None:
        """A drifting default would silently relax the published contract."""
        self.assertEqual(SMOKE_BUDGET_SECONDS, 60.0)


class ExitCodeReachesTheShell(unittest.TestCase):
    """`cli.main` discards handler return values and reads SystemExit.

    A gate that only *returned* 3 reported success at the shell — observed live
    before this test existed.
    """

    def test_breach_raises_system_exit_with_the_code(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            smoke_cmd(_PROJECT_ROOT, budget=0.0)
        self.assertEqual(caught.exception.code, 3)

    def test_success_does_not_raise(self) -> None:
        self.assertIsNone(smoke_cmd(_PROJECT_ROOT))


class TierIsPopulatedHere(unittest.TestCase):
    """This repository must actually carry smoke members."""

    def test_repository_declares_smoke_members(self) -> None:
        self.assertTrue(
            smoke_marked_files(_PROJECT_ROOT),
            msg="no test under tests/ carries @smoke; the tier would pass by emptiness",
        )


class FailingMemberIsDistinctFromABreach(unittest.TestCase):
    """A broken build and a slow tier are different problems with different exits."""

    def test_test_failure_exits_one_not_three(self) -> None:
        failing = unittest.TestResult()
        failing.failures = [(None, "boom")]  # type: ignore[list-item]
        with mock.patch("gzkit.commands.smoke_cmd.run_smoke", return_value=(failing, 0.01)):
            self.assertEqual(smoke_gate(_PROJECT_ROOT), 1)


if __name__ == "__main__":
    unittest.main()
