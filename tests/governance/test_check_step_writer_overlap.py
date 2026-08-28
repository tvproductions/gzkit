"""One measured reader may overlap the writer lane; nothing else may (GHI #904).

The writer/reader phase boundary is a conservative approximation of a single
producer->consumer edge — ``Behave`` builds ``dist/*.whl`` and ``Validate default
scopes`` reads it — and it charged every OTHER reader for that one pair. Measured
2026-08-28 at ``d3cf81b0``:

    writer phase (fully serial, no reader may start):
       29.17s  Behave
        3.84s  Docs build
       33.01s  TOTAL
    largest reader, idle for all 33.0s of it: Test at 31.99s

``Test`` was admitted to an overlap lane on a measurement of BOTH sides, taken
with the same marker protocol that produced ``class``: ``Behave`` writes exactly
one path and ``Docs build`` writes only under ``site/``, while ``Test`` is
``read_only`` (writes nothing) and every ``dist/``/``site/`` reference under
``tests/`` is an exclusion naming those trees "not live state".

The tests below guard the two things that could go wrong, and the second matters
more than the first: the edge must survive, and the OPT-IN POLARITY must survive.
An inverted default would make an unmeasured step overlap silently, which is the
flaky gate GHI #835 refused in as many words — *"A parallel runner over steps
with an undeclared dependency is a flaky gate, which is strictly worse than a
slow one."* A speedup that quietly reintroduces that is a regression wearing a
benchmark.
"""

from __future__ import annotations

import json
import threading
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from unittest import mock

from gzkit.commands.common import get_project_root
from gzkit.commands.quality import (
    CheckStepRunner,
    QualityResult,
    _run_check_steps,
    _steps_overlapping_writers,
)

_DECL = get_project_root() / "data" / "check_step_concurrency.json"


class _Progress:
    """Minimal stand-in for the runner's progress object."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def advance(self, name: str) -> None:
        self.seen.append(name)


@dataclass
class _Run:
    """What one fake run observed.

    A typed record rather than a dict, so `writer_order` and `results` stay
    iterable to the type checker — a `dict[str, object]` fixture reads as
    `object` at every access and hides real mistakes behind the same error it
    raises for correct code.
    """

    lane_active: bool = False
    test_saw_lane_active: bool = False
    writer_order: list[str] = field(default_factory=list)
    results: list[tuple[str, QualityResult]] = field(default_factory=list)


def _ok(name: str) -> QualityResult:
    return QualityResult(success=True, command=name, stdout="", stderr="", returncode=0)


class OverlapDeclarationTest(unittest.TestCase):
    """What the declaration admits, and on what terms."""

    def test_only_test_overlaps_today(self) -> None:
        """Each name here cost a two-sided measurement; the set is not a default."""
        self.assertEqual({"Test"}, _steps_overlapping_writers())

    def test_a_writer_can_never_overlap_itself(self) -> None:
        """``overlaps_writers`` on a writer is meaningless and must not be honoured.

        The lane IS the writers. A writer carrying the flag would be claiming to
        overlap itself, so the loader requires ``class == read_only`` as well —
        asserted rather than trusted, because the two fields are independent in
        the JSON and nothing else stops that combination being written.
        """
        decl = json.loads(_DECL.read_text(encoding="utf-8"))
        decl["steps"]["Behave"]["overlaps_writers"] = True
        with mock.patch("gzkit.commands.quality.json.loads", return_value=decl):
            self.assertNotIn("Behave", _steps_overlapping_writers())

    def test_absent_flag_means_wait(self) -> None:
        """Absence is the conservative answer, so silence is never a race.

        This is the polarity GHI #835 requires. If an unmeasured step overlapped
        by default, adding a step would be the dangerous act; as written, adding
        a step is safe and only an explicit measured claim changes anything.
        """
        decl = json.loads(_DECL.read_text(encoding="utf-8"))
        decl["steps"]["Test"].pop("overlaps_writers", None)
        with mock.patch("gzkit.commands.quality.json.loads", return_value=decl):
            self.assertEqual(set(), _steps_overlapping_writers())


class OverlapRunnerTest(unittest.TestCase):
    """What the runner does with the declaration."""

    def _run(self, names: list[str], overlapping: set[str]) -> _Run:
        """Run fake steps, recording whether the writer lane was still running."""
        state = _Run()
        started = threading.Event()

        def writer(name: str) -> CheckStepRunner:
            def run(_root: Path) -> QualityResult:
                state.writer_order.append(name)
                state.lane_active = True
                started.set()
                # Hold the lane open long enough for an overlapping reader to
                # observe it. A reader that never observes it proves nothing.
                threading.Event().wait(0.25)
                state.lane_active = False
                return _ok(name)

            return run

        def reader(name: str) -> CheckStepRunner:
            def run(_root: Path) -> QualityResult:
                if name == "Test":
                    started.wait(2.0)
                    state.test_saw_lane_active = state.lane_active
                return _ok(name)

            return run

        steps = [(n, writer(n) if n in ("Behave", "Docs build") else reader(n)) for n in names]
        classes = {n: ("writes" if n in ("Behave", "Docs build") else "read_only") for n in names}
        with (
            mock.patch("gzkit.commands.quality._step_concurrency_classes", return_value=classes),
            mock.patch(
                "gzkit.commands.quality._steps_overlapping_writers", return_value=overlapping
            ),
            mock.patch("gzkit.commands.quality._seam", side_effect=lambda n, r, _p: r),
        ):
            results = _run_check_steps(steps, get_project_root(), _Progress())
        state.results = results
        return state

    _NAMES = ["Behave", "Docs build", "Test", "Lint"]

    def test_declared_reader_runs_while_the_writer_lane_is_open(self) -> None:
        """The whole point: Test must not wait for the lane to drain."""
        state = self._run(self._NAMES, {"Test"})

        self.assertTrue(
            state.test_saw_lane_active,
            "Test ran only after the writer lane closed — it did not overlap",
        )

    def test_undeclared_reader_waits_for_the_lane(self) -> None:
        """The negative control. Without this, the test above passes vacuously.

        Same steps, same runner, only the declaration differs — so a runner that
        ignored the declaration and always overlapped would pass the positive
        test and fail this one.
        """
        state = self._run(self._NAMES, set())

        self.assertFalse(
            state.test_saw_lane_active,
            "an undeclared reader overlapped the writer lane",
        )

    def test_writers_keep_list_order_inside_the_lane(self) -> None:
        """The Behave -> Validate edge rests on writer order, not on the phase.

        Overlapping readers must not turn the writer lane into a fan-out: the
        writers are submitted as ONE task precisely so their relative order
        survives.
        """
        state = self._run(self._NAMES, {"Test"})

        self.assertEqual(["Behave", "Docs build"], state.writer_order)

    def test_no_writers_means_one_reader_pool(self) -> None:
        """With no lane to overlap, the overlap split must not happen at all.

        Regression: the first cut of this change consulted the declaration
        unconditionally, so a step list of two readers and no writer was split
        into a pool of one and a pool of one — halving the concurrency and
        reordering progress to overlap something that was not there.
        `tests/unit/test_progress_indication.py` caught it, on exactly that
        shape.

        Asserted through the progress object because that is where the split is
        observable from outside: both readers must be ticked from the same pass.
        """
        progress = _Progress()
        steps: list[tuple[str, CheckStepRunner]] = [
            ("Lint", lambda _root: _ok("Lint")),
            ("Test", lambda _root: _ok("Test")),
        ]
        with (
            mock.patch(
                "gzkit.commands.quality._step_concurrency_classes",
                return_value={"Lint": "read_only", "Test": "read_only"},
            ),
            mock.patch("gzkit.commands.quality._seam", side_effect=lambda n, r, _p: r),
        ):
            results = _run_check_steps(steps, get_project_root(), progress)

        self.assertEqual(["Lint", "Test"], sorted(progress.seen))
        self.assertEqual(["Lint", "Test"], [n for n, _ in results])

    def test_every_step_still_reports_once_in_list_order(self) -> None:
        """Splitting the readers must not drop or reorder the returned results."""
        state = self._run(self._NAMES, {"Test"})
        results = state.results

        self.assertEqual(self._NAMES, [n for n, _ in results])
        self.assertTrue(all(r.success for _, r in results))


if __name__ == "__main__":
    unittest.main()
