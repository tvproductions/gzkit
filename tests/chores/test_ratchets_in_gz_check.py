"""The reachability and ledger-inertness ratchets run as `gz check` steps (GHI #1063).

Both chores were fail-closed ratchets whose only automatic caller was a
pre-commit hook, so `gz check` and CI never ran them: a tree could pass the
per-change gate while one of them was red. Operator ruling 2026-09-29 (verbatim):
"Add both ratchets to gz check".

These tests pin what the aggregator receives from each step — a breach reaches
`gz check` as a failing exit, a toothless ratchet (failed self-test) is refused
before it runs, a clean tree passes, and a project that does not carry the
(projectLocal) chore is not failed for a surface it never had.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.common import GzCliError
from gzkit.quality import QualityResult


def _step_runners() -> dict[str, object]:
    from gzkit.commands.quality import _build_check_steps

    return dict(_build_check_steps())


class TestStepsAreWired(unittest.TestCase):
    """Each ratchet is a step of the aggregator, bound to its own runner."""

    def test_reachability_ratchet_is_a_gz_check_step(self) -> None:
        from gzkit.quality import run_validator_reachability_audit

        self.assertIs(
            _step_runners().get("Validator reachability"), run_validator_reachability_audit
        )

    def test_ledger_inertness_ratchet_is_a_gz_check_step(self) -> None:
        from gzkit.quality import run_ledger_inertness_audit

        self.assertIs(
            _step_runners().get("Ledger vocabulary inertness"), run_ledger_inertness_audit
        )

    def test_every_live_step_carries_guard_meta(self) -> None:
        """`_build_check_steps` item 7: every step belongs in `_STEP_GUARD_META` (GHI #787)."""
        from gzkit.commands.quality import _STEP_GUARD_META

        missing = sorted(set(_step_runners()) - set(_STEP_GUARD_META))
        self.assertEqual(missing, [], f"steps absent from _STEP_GUARD_META: {missing}")


def _result(returncode: int, command: str) -> QualityResult:
    return QualityResult(
        success=returncode == 0, command=command, stdout="", stderr="", returncode=returncode
    )


class TestRunnerVerdict(unittest.TestCase):
    """The step reports the ratchet's own exit, and refuses to trust a toothless one.

    The ratchets' verdicts over real trees are witnessed by their chore tests and
    by the `validator-reachability` / `ledger-inertness` negative controls; these
    tests pin what the step does with that verdict.
    """

    def _run(self, runner, exits: dict[bool, int]) -> tuple[QualityResult, list[list[str]]]:
        calls: list[list[str]] = []

        def fake(argv: list[str], cwd: Path) -> QualityResult:
            calls.append(argv)
            return _result(exits["--self-test" in argv], " ".join(argv))

        with patch("gzkit.quality.run_command", side_effect=fake):
            return runner(Path(".")), calls

    def test_policy_breach_fails_the_step_with_exit_3(self) -> None:
        from gzkit.quality import run_ledger_inertness_audit, run_validator_reachability_audit

        for runner in (run_validator_reachability_audit, run_ledger_inertness_audit):
            with self.subTest(runner=runner.__name__):
                result, calls = self._run(runner, {True: 0, False: 3})
                self.assertFalse(result.success)
                self.assertEqual(result.returncode, 3)
                self.assertEqual(len(calls), 2)

    def test_failed_self_test_fails_the_step_before_the_ratchet_runs(self) -> None:
        from gzkit.quality import run_ledger_inertness_audit, run_validator_reachability_audit

        for runner in (run_validator_reachability_audit, run_ledger_inertness_audit):
            with self.subTest(runner=runner.__name__):
                result, calls = self._run(runner, {True: 1, False: 0})
                self.assertFalse(result.success)
                self.assertEqual(len(calls), 1)

    def test_clean_ratchet_passes_the_step(self) -> None:
        from gzkit.quality import run_ledger_inertness_audit, run_validator_reachability_audit

        for runner in (run_validator_reachability_audit, run_ledger_inertness_audit):
            with self.subTest(runner=runner.__name__):
                result, _ = self._run(runner, {True: 0, False: 0})
                self.assertTrue(result.success)


class TestInstallWithoutTheRatchets(unittest.TestCase):
    """A wheel install withholds both scripts: it lists neither step nor claims either.

    QC binding refuses a bound step with no registered control (green-by-emptiness),
    and the enforcement floor runs in every project, so steps and claims must key
    off the same install predicate.
    """

    def test_steps_are_absent_when_the_install_lacks_the_scripts(self) -> None:
        with patch("gzkit.quality.project_local_ratchets_installed", return_value=False):
            names = set(_step_runners())
        self.assertNotIn("Validator reachability", names)
        self.assertNotIn("Ledger vocabulary inertness", names)

    def test_no_controls_are_offered_when_the_install_lacks_the_scripts(self) -> None:
        from gzkit.governance.trust_audits import _qc_negative_controls as nc

        with patch("gzkit.quality.project_local_ratchets_installed", return_value=False):
            self.assertEqual(nc._optional_project_local_controls(), ())
        with patch("gzkit.quality.project_local_ratchets_installed", return_value=True):
            claims = {entry[0] for entry in nc._optional_project_local_controls()}
        self.assertEqual(
            claims,
            {
                "validator-reachability",
                "validator-reachability-disclosed",
                "ledger-vocabulary-inertness",
                "ledger-vocabulary-inertness-disclosed",
            },
        )


class TestProjectWithoutTheChore(unittest.TestCase):
    """Both chores are projectLocal: a project that does not carry one is not failed."""

    def test_absent_chore_passes_both_steps(self) -> None:
        from gzkit.quality import run_ledger_inertness_audit, run_validator_reachability_audit

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch(
                "gzkit.commands.chores._resolve_chore_dir",
                side_effect=GzCliError("chore not found"),
            ),
        ):
            for runner in (run_validator_reachability_audit, run_ledger_inertness_audit):
                with self.subTest(runner=runner.__name__):
                    result = runner(Path(tmp))
                    self.assertTrue(result.success)
                    self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
