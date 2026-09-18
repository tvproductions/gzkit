"""The full-suite coverage run uses the parallel runner, spelled once (GHI #1027).

`CANONICAL_STEP_COMMANDS["unittest"]` moved to `unittest-parallel` on 2026-08-27
(GHI #856); `"coverage"` was left on the serial stdlib runner. Operator ruling
2026-09-18: "We want parallel everywhere unless you can give me a good reason why
we can't." The reason offered then -- a multi-process runner needs `parallel =
true` plus `coverage combine` -- was measured and did not hold: on the same tree,
10,467 tests, both exit 0,

    coverage run -m unittest discover -s tests -t .      493 s   53840 / 6359 / 88%
    unittest-parallel ... --coverage --coverage-source   307 s   53840 / 6359 / 88%

Identical statement and miss counts, and the parallel runner leaves a combined
data file that `coverage report --fail-under` reads unchanged.

Same shape as `test_unittest_runner_lockstep.py`: consumers that can derive are
mutation-tested; the one that cannot (a chore's JSON criterion, read by the chore
runner) is pinned by equality.
"""

from __future__ import annotations

import json
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.arb.validator import (
    CANONICAL_STEP_COMMANDS,
    RETIRED_STEP_COMMANDS,
    validate_receipts,
)
from gzkit.cli.main import _build_parser
from gzkit.commands.arb import arb_coverage_cmd

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SENTINEL_COMMAND = ["uv", "run", "sentinel-runner", "--coverage"]
_SERIAL = ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-t", "."]


def _write_coverage_receipt(root: Path, name: str, command: list[str], timestamp: str) -> None:
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": f"arb-step-coverage-{name}",
        "timestamp_utc": timestamp,
        "duration_ms": 10,
        "exit_status": 0,
        "stdout_tail": "",
        "stdout_truncated": False,
        "stderr_tail": "",
        "stderr_truncated": False,
        "git": {"commit": "abcdef0", "branch": "main", "dirty": False},
        "step": {"name": "coverage", "command": command},
    }
    (root / f"arb-step-coverage-{name}.json").write_text(json.dumps(payload), encoding="utf-8")


class TestCanonicalCoverageIsTheParallelRunner(unittest.TestCase):
    def test_canonical_coverage_runs_unittest_parallel_with_coverage(self) -> None:
        argv = CANONICAL_STEP_COMMANDS["coverage"]
        self.assertIn("unittest-parallel", argv)
        self.assertIn("--coverage", argv)

    def test_it_measures_the_same_suite_as_the_unittest_step(self) -> None:
        """Coverage of a different test population is a different number."""
        unit = CANONICAL_STEP_COMMANDS["unittest"]
        self.assertEqual(CANONICAL_STEP_COMMANDS["coverage"][: len(unit)], unit)


class TestCoverageSupersessionKeepsHistoryValid(unittest.TestCase):
    def test_a_serial_receipt_predating_the_swap_stays_canonical(self) -> None:
        """Newest serial coverage receipt on disk at the swap: 2026-09-11T01:17:34Z."""
        with tempfile.TemporaryDirectory() as tmp:
            _write_coverage_receipt(Path(tmp), "historic", _SERIAL, "2026-09-11T01:17:34Z")
            result = validate_receipts(limit=10, root=Path(tmp))
        self.assertEqual((result.valid, result.non_canonical_provenance), (1, 0))

    def test_the_serial_command_run_after_the_swap_is_rejected(self) -> None:
        retired_at, command = RETIRED_STEP_COMMANDS["coverage"][-1]
        self.assertEqual(command, _SERIAL)
        with tempfile.TemporaryDirectory() as tmp:
            _write_coverage_receipt(Path(tmp), "stale", _SERIAL, "2026-10-01T00:00:00Z")
            result = validate_receipts(limit=10, root=Path(tmp))
        self.assertEqual(result.non_canonical_provenance, 1, msg=f"retired_at={retired_at}")


class TestArbCoverageVerbFollowsCanon(unittest.TestCase):
    """`gz arb coverage` with no arguments is the canonical run, as `gz arb typecheck` is.

    With arguments it stays the pass-through to coverage.py it always was
    (`gz arb coverage report --fail-under=40`).
    """

    def test_no_arguments_runs_whatever_canon_declares(self) -> None:
        with (
            mock.patch.dict(CANONICAL_STEP_COMMANDS, {"coverage": _SENTINEL_COMMAND}),
            mock.patch("gzkit.commands.arb.arb_step_cmd", return_value=0) as step,
        ):
            arb_coverage_cmd(argv=[])
        self.assertEqual(list(step.call_args.kwargs["argv"]), _SENTINEL_COMMAND)

    def test_arguments_are_still_forwarded_to_coverage(self) -> None:
        with mock.patch("gzkit.commands.arb.arb_step_cmd", return_value=0) as step:
            arb_coverage_cmd(argv=["report", "--fail-under=40"])
        self.assertEqual(
            list(step.call_args.kwargs["argv"]), ["coverage", "report", "--fail-under=40"]
        )

    def test_help_does_not_teach_the_retired_invocation(self) -> None:
        parser = _build_parser()
        arb = parser._subparsers._group_actions[0].choices["arb"]  # noqa: SLF001
        coverage = arb._subparsers._group_actions[0].choices["coverage"]  # noqa: SLF001
        self.assertNotIn("-m unittest discover", coverage.epilog or "")


class TestCoverageChoreMatchesCanon(unittest.TestCase):
    """The one copy that cannot derive is pinned by equality."""

    def test_the_coverage_run_criterion_equals_the_canonical_command(self) -> None:
        path = _REPO_ROOT / ".gzkit" / "chores" / "coverage-40pct" / "acceptance.json"
        criteria = json.loads(path.read_text(encoding="utf-8"))["criteria"]
        runs = [c["command"] for c in criteria if "--coverage" in c["command"]]
        self.assertEqual(
            [shlex.split(command) for command in runs],
            [CANONICAL_STEP_COMMANDS["coverage"]],
            msg="coverage-40pct measures the floor with a different run than the attested one",
        )


if __name__ == "__main__":
    unittest.main()
