"""Auto-stamp `Task:` trailers from the active TASK set (GHI #731).

The pipeline mints one TASK per REQ, then relies on an agent to remember every
one of them in a commit trailer. Measured 2026-07-29, that convention is dead:
87 post-epoch OBPIs minted 467 TASKs that appear in NO commit trailer, and the
one compliant OBPI (0.34.0-03) complied only because an unrelated gate defect
forced a manual amend. Its siblings 0.34.0-01 and -02 declare nothing.

A convention with 15% adherence is not a convention, and Signature (c) cannot
see the failure: an empty channel beside a populated one is skipped, so total
under-declaration reads as "nothing to compare" rather than maximum drift.

Fixing the producer is the same move GHI #653 needed twice — stamp the
attribution the runtime already knows instead of asking a human to recall it.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.tasks import active_task_trailers


def _ledger(root: Path, rows: list[dict[str, str]]) -> Path:
    gz = root / ".gzkit"
    gz.mkdir(parents=True, exist_ok=True)
    path = gz / "ledger.jsonl"
    path.write_text(
        "".join(json.dumps({"schema": "gzkit.ledger.v1", **r}) + "\n" for r in rows),
        encoding="utf-8",
    )
    return path


def _started(task_id: str) -> dict[str, str]:
    return {"event": "task_started", "task_id": task_id, "obpi_id": "OBPI-0.34.0-03"}


def _completed(task_id: str) -> dict[str, str]:
    return {"event": "task_completed", "task_id": task_id, "obpi_id": "OBPI-0.34.0-03"}


class TestActiveTaskTrailers(unittest.TestCase):
    """The runtime stamps what it already knows, scoped to where it is required."""

    def test_stamps_every_in_progress_task(self) -> None:
        """All in-progress TASKs are emitted, not just the first.

        The whole defect: an agent declares one TASK and the ledger records six.
        Emitting a single trailer would reproduce exactly the under-declaration
        this replaces.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _ledger(
                root,
                [
                    _started("TASK-0.34.0-03-01-01"),
                    _started("TASK-0.34.0-03-02-01"),
                    _started("TASK-0.34.0-03-03-01"),
                ],
            )

            self.assertEqual(
                active_task_trailers(path, ["src/gzkit/tasks.py"]),
                [
                    "Task: TASK-0.34.0-03-01-01",
                    "Task: TASK-0.34.0-03-02-01",
                    "Task: TASK-0.34.0-03-03-01",
                ],
            )

    def test_completed_tasks_are_not_stamped(self) -> None:
        """A finished TASK is not active labor and must not be attributed.

        The negative control that gives the emission meaning: without it, a
        function returning every TASK it ever saw would satisfy the test above
        while attributing a diff to work that closed weeks earlier.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _ledger(
                root,
                [
                    _started("TASK-0.34.0-03-01-01"),
                    _started("TASK-0.34.0-03-02-01"),
                    _completed("TASK-0.34.0-03-01-01"),
                ],
            )

            self.assertEqual(
                active_task_trailers(path, ["tests/test_x.py"]),
                ["Task: TASK-0.34.0-03-02-01"],
            )

    def test_no_stamp_outside_src_and_tests_scope(self) -> None:
        """`Task:` is mandatory only on src/tests commits — do not invent one.

        `.gzkit/rules/tests.md` § TASK-Driven Workflow scopes the requirement to
        `src/**` and `tests/**`. Stamping a docs-only commit would manufacture
        attribution the rule never asked for and pollute the very channel this
        change exists to make meaningful.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _ledger(root, [_started("TASK-0.34.0-03-01-01")])

            self.assertEqual(active_task_trailers(path, ["docs/user/runbook.md"]), [])

    def test_no_active_tasks_stamps_nothing(self) -> None:
        """With no TASK in flight the runtime has nothing to attribute.

        Direct-fix work outside OBPI scope keeps its authored slug trailer; the
        stamper must never displace it with a fabricated formal id.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _ledger(
                root, [_started("TASK-0.34.0-03-01-01"), _completed("TASK-0.34.0-03-01-01")]
            )

            self.assertEqual(active_task_trailers(path, ["src/gzkit/tasks.py"]), [])

    def test_missing_ledger_is_not_an_error(self) -> None:
        """A repo without a ledger stamps nothing rather than crashing.

        The stamper runs inside a git hook on every commit; a crash there blocks
        all work. Absent state is a no-op, never an exception.
        """
        with TemporaryDirectory() as tmp:
            self.assertEqual(
                active_task_trailers(Path(tmp) / "nope" / "ledger.jsonl", ["src/x.py"]), []
            )

    def test_malformed_ledger_lines_are_skipped(self) -> None:
        """Junk lines must not take the hook down mid-commit."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            gz = root / ".gzkit"
            gz.mkdir(parents=True)
            path = gz / "ledger.jsonl"
            path.write_text(
                "not json\n[]\n" + json.dumps(_started("TASK-0.34.0-03-01-01")) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(
                active_task_trailers(path, ["src/x.py"]), ["Task: TASK-0.34.0-03-01-01"]
            )


if __name__ == "__main__":
    unittest.main()
