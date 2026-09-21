"""`gz check` measures each step's cost in-gate, as a byproduct of the run (GHI #1077).

WHY: the gate's only per-step cost record lived in `data/check_step_concurrency.json`,
produced by running each step ALONE and refreshed by hand. Three things followed.
Nothing read it — `measured_seconds` and `measured_at_commit` have zero consumers
in `src/` or `tests/`. It measured the wrong quantity: the declaration's own
protocol note says "Adding step wall-times treats cores as free, and they are not",
and GHI #906's commit recorded "Behave standalone is 29.33s but 47-49s inside the
gate". And it decayed with no mechanism to notice — GHI #903 closed that exact
class by re-measuring 58 values by hand, and 23 days later `Test` read 31.99s
against a measured 92.10s.

An in-gate measurement cannot go stale relative to the tree that produced it,
because the run produces it. That is the difference this closes, and it is
`AGENTS.md` § Architectural Boundaries #4 — reconciliation must not stay a
maintenance chore.

SCOPE: console output only. A `duration` field on `QualityResult` (which feeds
`gz check --json`) and new fields in the verified receipt are runtime-contract
changes, deliberately out of this arm.
"""

from __future__ import annotations

import time
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.common import get_project_root
from gzkit.commands.quality import (
    CheckStepRunner,
    QualityResult,
    _format_elapsed,
    _run_check_steps,
)


class _Progress:
    """Minimal stand-in for the runner's progress object."""

    def advance(self, name: str) -> None:
        """Record nothing; the runner only needs the call to succeed."""


def _ok(name: str) -> QualityResult:
    """Return a passing result for *name*."""
    return QualityResult(success=True, command=name, stdout="", stderr="", returncode=0)


def _runner(name: str, sleep_s: float = 0.0) -> CheckStepRunner:
    """Return a runner that optionally burns wall-clock before succeeding."""

    def run(_root: Path) -> QualityResult:
        if sleep_s:
            time.sleep(sleep_s)
        return _ok(name)

    return run


def _collect(
    names: list[str], classes: dict[str, str], sleeps: dict[str, float]
) -> dict[str, float]:
    """Run *names* through the real runner and return the durations it recorded."""
    steps = [(n, _runner(n, sleeps.get(n, 0.0))) for n in names]
    durations: dict[str, float] = {}
    with (
        mock.patch("gzkit.commands.quality._step_concurrency_classes", return_value=classes),
        mock.patch("gzkit.commands.quality._steps_overlapping_writers", return_value=set()),
        mock.patch("gzkit.commands.quality._seam", side_effect=lambda _n, r, _p: r),
    ):
        _run_check_steps(steps, get_project_root(), _Progress(), durations=durations)
    return durations


class TestEveryStepIsTimedInGate(unittest.TestCase):
    """No step runs unmeasured, on either the writer lane or the reader pool."""

    _NAMES = ["Behave", "Docs build", "Test", "Lint"]
    _CLASSES = {
        "Behave": "writes",
        "Docs build": "writes",
        "Test": "read_only",
        "Lint": "read_only",
    }

    def test_writers_and_readers_alike_record_a_duration(self) -> None:
        durations = _collect(self._NAMES, self._CLASSES, {})

        self.assertEqual(
            sorted(durations),
            sorted(self._NAMES),
            "a step that ships unmeasured is the gap this arm closes",
        )

    def test_the_duration_reflects_the_work_the_step_actually_did(self) -> None:
        durations = _collect(self._NAMES, self._CLASSES, {"Test": 0.05})

        self.assertGreaterEqual(
            durations["Test"],
            0.05,
            "the figure must be measured around the real call, not estimated",
        )

    def test_a_run_with_no_writers_still_times_every_step(self) -> None:
        names = ["Lint", "Format"]
        durations = _collect(names, dict.fromkeys(names, "read_only"), {})

        self.assertEqual(sorted(durations), sorted(names))

    def test_a_run_with_no_readers_still_times_every_step(self) -> None:
        names = ["Behave", "Docs build"]
        durations = _collect(names, dict.fromkeys(names, "writes"), {})

        self.assertEqual(sorted(durations), sorted(names))

    def test_the_durations_sink_is_optional(self) -> None:
        """Existing callers pass no sink and must keep working unchanged."""
        steps = [("Lint", _runner("Lint"))]
        with (
            mock.patch(
                "gzkit.commands.quality._step_concurrency_classes",
                return_value={"Lint": "read_only"},
            ),
            mock.patch("gzkit.commands.quality._steps_overlapping_writers", return_value=set()),
            mock.patch("gzkit.commands.quality._seam", side_effect=lambda _n, r, _p: r),
        ):
            results = _run_check_steps(steps, get_project_root(), _Progress())

        self.assertEqual([name for name, _ in results], ["Lint"])


class TestElapsedRendering(unittest.TestCase):
    """The figure is rendered so the expensive steps are findable by eye."""

    def test_sub_minute_costs_render_in_seconds(self) -> None:
        self.assertEqual(_format_elapsed(4.05), "4.05s")

    def test_a_long_step_still_renders_in_seconds(self) -> None:
        self.assertEqual(_format_elapsed(92.1), "92.10s")

    def test_an_unmeasured_step_renders_nothing(self) -> None:
        self.assertEqual(
            _format_elapsed(None),
            "",
            "a missing measurement must not render as a zero cost",
        )
