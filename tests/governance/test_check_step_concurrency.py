"""Every `gz check` step must declare its concurrency class (GHI #835).

The step set is run concurrently, so a step whose write behaviour is unknown is
not merely undocumented — it is a candidate race. GHI #835 states the bar:
"A parallel runner over steps with an undeclared dependency is a flaky gate,
which is strictly worse than a slow one. The dependency declaration is the
deliverable; the speedup is the consequence."

So the declaration fails closed in both directions, on the `_STEP_CLASSIFICATION`
precedent: an undeclared step raises rather than defaulting to read-only, and a
declaration naming a step that no longer exists is stale rather than harmless.
"""

from __future__ import annotations

import json
import unittest

from gzkit.commands.common import get_project_root

_DECLARATION = get_project_root() / "data" / "check_step_concurrency.json"


def _declared() -> dict[str, dict]:
    return json.loads(_DECLARATION.read_text(encoding="utf-8"))["steps"]


def _live_step_names() -> set[str]:
    from gzkit.commands.quality import _build_check_steps

    return {name for name, _ in _build_check_steps()}


class TestEveryStepIsDeclared(unittest.TestCase):
    """No step ships unaccounted — the `_STEP_CLASSIFICATION` posture."""

    def test_every_live_step_has_a_concurrency_declaration(self) -> None:
        missing = sorted(_live_step_names() - set(_declared()))

        self.assertEqual(
            missing,
            [],
            "Every gz check step must declare read_only or writes in "
            f"data/check_step_concurrency.json. Undeclared: {missing}. "
            "Measure it (run the step alone, see what it wrote) — never guess, "
            "and never default to read_only.",
        )

    def test_declaration_carries_no_step_that_no_longer_exists(self) -> None:
        """A stale entry silently widens what the runner believes is safe."""
        fast_only = {"Test (changed)"}
        orphans = sorted(set(_declared()) - _live_step_names() - fast_only)

        self.assertEqual(
            orphans,
            [],
            f"Declaration names steps absent from _build_check_steps(): {orphans}. "
            "Drop them; a declaration that outlives its step describes nothing.",
        )

    def test_every_declaration_names_a_known_class(self) -> None:
        bad = {
            n: e.get("class")
            for n, e in _declared().items()
            if e.get("class") not in {"read_only", "writes"}
        }

        self.assertEqual(bad, {}, f"Unknown concurrency class: {bad}")

    def test_every_writer_declares_its_paths_and_why(self) -> None:
        """A writer without paths cannot be reasoned about by a future reader.

        The paths are what make the Behave -> Validate default scopes edge
        legible; `why` is what stops the next author from "simplifying" a
        writer into the concurrent phase.
        """
        for name, entry in _declared().items():
            if entry.get("class") != "writes":
                continue
            with self.subTest(step=name):
                self.assertTrue(entry.get("paths"), f"{name} declares writes but names no paths")
                self.assertTrue(entry.get("why"), f"{name} declares writes but no reason")


class TestWritersRunBeforeReadOnlySteps(unittest.TestCase):
    """The measured producer->consumer edge must survive the runner's phasing.

    Behave builds `dist/*.whl`; `gz validate --distribution`, inside the
    Validate default scopes step, reads it. Measured 2026-08-22 — this is the
    concrete dependency the GHI asked to be established before parallelizing.
    """

    def test_partition_places_every_writer_ahead_of_every_reader(self) -> None:
        from gzkit.commands.quality import _partition_steps_by_concurrency

        steps = [("Behave", object()), ("Lint", object()), ("Docs build", object())]
        serial, concurrent = _partition_steps_by_concurrency(steps)

        self.assertEqual([n for n, _ in serial], ["Behave", "Docs build"])
        self.assertEqual([n for n, _ in concurrent], ["Lint"])

    def test_writers_keep_their_relative_list_order(self) -> None:
        """Behave must precede Validate default scopes, which consumes its wheel."""
        from gzkit.commands.quality import _build_check_steps, _partition_steps_by_concurrency

        serial, _ = _partition_steps_by_concurrency(_build_check_steps())
        names = [n for n, _ in serial]

        self.assertLess(
            names.index("Behave"),
            names.index("Validate default scopes"),
            "Validate default scopes reads the wheel Behave builds",
        )

    def test_an_undeclared_step_runs_serially_never_concurrently(self) -> None:
        """A step nobody measured must never land in the concurrent phase.

        Serial is the conservative class: always correct, merely slower. So the
        unsafe default is structurally unavailable — the only way to be run
        concurrently is to be declared `read_only`, which requires measuring.
        The "no step ships unaccounted" guarantee lives in
        `test_every_live_step_has_a_concurrency_declaration` above, which fails
        the commit rather than the runtime.
        """
        from gzkit.commands.quality import _partition_steps_by_concurrency

        serial, concurrent = _partition_steps_by_concurrency([("Totally New Step", object())])

        self.assertEqual([n for n, _ in serial], ["Totally New Step"])
        self.assertEqual(concurrent, [], "An unmeasured step must never run concurrently")


if __name__ == "__main__":
    unittest.main()
