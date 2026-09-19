"""The smoke tier's budget must be enforced by something (GHI #724).

The 60s ceiling sat in `.gzkit/rules/tests.md` as prose with no consumer, so a
4.5x breach was invisible to everything but a stopwatch. These tests pin the
consumer's three outcomes — an EMPTY tier is a breach when the project opts in,
and advisory success otherwise. A required subset cannot pass by having no members.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

from gzkit.commands.smoke_cmd import smoke_cmd, smoke_gate
from gzkit.config import GzkitConfig
from gzkit.smoke import SMOKE_BUDGET_SECONDS, smoke, smoke_marked_files
from tests.commands.common import SilencedConsoleTestCase

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MarkerIsMetadataOnly(SilencedConsoleTestCase):
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


class EmptyTierIsABreachWhenRequired(SilencedConsoleTestCase):
    """Green-by-emptiness is the failure a budget gate invites — once opted in."""

    def _project(self, root: Path, *, required: bool | None) -> None:
        (root / "tests").mkdir()
        if required is not None:
            (root / ".gzkit.json").write_text(
                json.dumps({"smoke": {"required": required}}), encoding="utf-8"
            )

    def test_empty_tier_exits_policy_breach_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._project(Path(tmp), required=True)
            self.assertEqual(smoke_gate(Path(tmp)), 3)

    def test_empty_tier_passes_for_a_project_that_never_opted_in(self) -> None:
        """A freshly scaffolded adopter has no tier yet; `gz check` must not refuse.

        Hard-failing every adopter for lacking a tier gzkit invented is the
        dogfooding leak open at GHI #607, arriving through a different door.
        """
        with tempfile.TemporaryDirectory() as tmp:
            self._project(Path(tmp), required=None)
            self.assertEqual(smoke_gate(Path(tmp)), 0)

    def test_explicit_opt_out_also_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._project(Path(tmp), required=False)
            self.assertEqual(smoke_gate(Path(tmp)), 0)

    def test_this_project_has_opted_in(self) -> None:
        """gzkit's own tier is binding — otherwise its QC control is vacuous."""
        self.assertTrue(GzkitConfig.load(_PROJECT_ROOT / ".gzkit.json").smoke.required)


class BudgetIsEnforced(SilencedConsoleTestCase):
    """The ceiling must have teeth, and the default must come from the rule."""

    def setUp(self) -> None:
        super().setUp()
        result = unittest.TestResult()
        result.testsRun = 1
        self.runner = self.enterContext(
            mock.patch("gzkit.commands.smoke_cmd.run_smoke", return_value=(result, 1.0))
        )

    def test_over_budget_run_exits_policy_breach(self) -> None:
        self.assertEqual(smoke_gate(_PROJECT_ROOT, budget=0.0), 3)

    def test_within_budget_run_exits_zero(self) -> None:
        self.assertEqual(smoke_gate(_PROJECT_ROOT), 0)

    def test_equality_does_not_breach(self) -> None:
        self.assertEqual(smoke_gate(_PROJECT_ROOT, budget=1.0), 0)

    def test_failed_run_precedes_budget_breach(self) -> None:
        result = unittest.TestResult()
        result.testsRun = 1
        result.errors = [(None, "broken")]  # ty: ignore[invalid-assignment]
        self.runner.return_value = result, 2.0
        self.assertEqual(smoke_gate(_PROJECT_ROOT, budget=1.0), 1)

    def test_default_budget_is_the_rule_declared_ceiling(self) -> None:
        """A drifting default would silently relax the published contract."""
        self.assertEqual(SMOKE_BUDGET_SECONDS, 60.0)


class ExitCodeReachesTheShell(SilencedConsoleTestCase):
    """`cli.main` discards handler return values and reads SystemExit.

    A gate that only *returned* 3 reported success at the shell — observed live
    before this test existed.
    """

    def setUp(self) -> None:
        super().setUp()
        result = unittest.TestResult()
        result.testsRun = 1
        self.runner = self.enterContext(
            mock.patch("gzkit.commands.smoke_cmd.run_smoke", return_value=(result, 1.0))
        )

    def test_breach_raises_system_exit_with_the_code(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            smoke_cmd(_PROJECT_ROOT, budget=0.0)
        self.assertEqual(caught.exception.code, 3)

    def test_success_does_not_raise(self) -> None:
        self.assertIsNone(smoke_cmd(_PROJECT_ROOT))


class SourceMarkerInventory(SilencedConsoleTestCase):
    """The advisory source inventory finds this repository's direct decorators."""

    def test_repository_declares_direct_markers(self) -> None:
        self.assertTrue(
            smoke_marked_files(_PROJECT_ROOT),
            msg="source inventory did not find this repository's direct @smoke decorators",
        )


class FailingMemberIsDistinctFromABreach(SilencedConsoleTestCase):
    """A broken build and a slow tier are different problems with different exits."""

    def test_test_failure_exits_one_not_three(self) -> None:
        failing = unittest.TestResult()
        failing.failures = [(None, "boom")]  # ty: ignore[invalid-assignment]
        with mock.patch("gzkit.commands.smoke_cmd.run_smoke", return_value=(failing, 0.01)):
            self.assertEqual(smoke_gate(_PROJECT_ROOT), 1)


class RuntimeMembership(SilencedConsoleTestCase):
    """A source marker cannot certify a discovered smoke member (GHI #1055)."""

    def test_source_only_marker_does_not_satisfy_required_tier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "helper.py").write_text(
                "from gzkit.smoke import smoke\n@smoke\ndef helper(): pass\n",
                encoding="utf-8",
            )
            (root / ".gzkit.json").write_text(
                json.dumps({"smoke": {"required": True}}), encoding="utf-8"
            )
            with mock.patch(
                "gzkit.smoke.unittest.TestLoader.discover", return_value=unittest.TestSuite()
            ):
                self.assertEqual(smoke_gate(root), 3)


class DiscoveryFailures(SilencedConsoleTestCase):
    """Unittest loader failures must reach the gate verdict (GHI #1055)."""

    def test_loader_failure_does_not_pass_as_an_empty_optional_tier(self) -> None:
        loader = unittest.TestLoader()
        failed_suite = loader.loadTestsFromName("gzkit_missing_smoke_fixture")
        self.assertTrue(loader.errors)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            with (
                mock.patch("gzkit.smoke.unittest.TestLoader", return_value=loader),
                mock.patch.object(loader, "discover", return_value=failed_suite),
            ):
                self.assertEqual(smoke_gate(root), 1)

    def test_load_tests_hook_failure_is_not_filtered_away(self) -> None:
        module = ModuleType("smoke_hook_fixture")

        def broken_hook(*args: object) -> None:
            raise RuntimeError("broken load_tests hook")

        module.load_tests = broken_hook
        loader = unittest.TestLoader()
        failed_suite = loader.loadTestsFromModule(module)
        self.assertTrue(loader.errors)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            with (
                mock.patch("gzkit.smoke.unittest.TestLoader", return_value=loader),
                mock.patch.object(loader, "discover", return_value=failed_suite),
            ):
                self.assertEqual(smoke_gate(root), 1)


class DiscoveredMarkerSelection(SilencedConsoleTestCase):
    """Runtime metadata selects members, without executing ordinary tests."""

    def test_aliased_marker_executes_and_unmarked_failure_is_excluded(self) -> None:
        observed = []
        bvt = smoke

        class Members(unittest.TestCase):
            @bvt
            def test_marked(self) -> None:
                observed.append("marked")

            def test_unmarked(self) -> None:
                raise AssertionError("ordinary test must not execute")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            suite = unittest.TestSuite(
                [unittest.TestSuite([Members("test_marked")]), Members("test_unmarked")]
            )
            with mock.patch("gzkit.smoke.unittest.TestLoader.discover", return_value=suite):
                self.assertEqual(smoke_gate(root), 0)
            self.assertEqual(observed, ["marked"])

    def test_discovery_error_cannot_hide_behind_a_passing_marked_member(self) -> None:
        class Members(unittest.TestCase):
            @smoke
            def test_marked(self) -> None:
                pass

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName("gzkit_missing_smoke_fixture")
        suite.addTest(Members("test_marked"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            with (
                mock.patch("gzkit.smoke.unittest.TestLoader", return_value=loader),
                mock.patch.object(loader, "discover", return_value=suite),
                self.assertRaises(SystemExit) as caught,
            ):
                smoke_cmd(root)
            self.assertEqual(caught.exception.code, 1)

    def test_missing_test_directory_preserves_empty_opt_in(self) -> None:
        for required, expected in [(False, 0), (True, 3)]:
            with self.subTest(required=required), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / ".gzkit.json").write_text(
                    json.dumps({"smoke": {"required": required}}), encoding="utf-8"
                )
                self.assertEqual(smoke_gate(root), expected)

    def test_unimportable_discovery_root_fails(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch(
                "gzkit.commands.smoke_cmd.run_smoke", side_effect=ImportError("unimportable")
            ),
        ):
            self.assertEqual(smoke_gate(Path(tmp)), 1)


if __name__ == "__main__":
    unittest.main()
