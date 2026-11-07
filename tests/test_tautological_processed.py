"""A processed tautological op is booked on the ledger (GHI #1305 item 2).

The decommission chore promised a ``chore_decommission_processed`` event per
processed item and no verb wrote one. These tests hold the producer to its
refusals: exactly one work order, a schema disposition, a baselined file, and
nothing written when any check fails.
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.events import parse_typed_event
from gzkit.tautological_processed import (
    FileNotInBaselineError,
    UnknownDispositionError,
    WorkOrderAmbiguousError,
    WorkOrderMalformedError,
    record_processed,
)

_FILE = "tests/test_example.py"


class RecordProcessed(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "data").mkdir()
        op = {
            "file_path": _FILE,
            "line_number": 3,
            "function_name": "test_x",
            "operation_kind": "is_dir",
            "assertion_kind": "assertTrue",
        }
        baseline = {"operations": [op], "generated_at": "2026-11-07T00:00:00+00:00"}
        (self.root / "data/tautological_test_baseline.json").write_text(
            json.dumps(baseline), encoding="utf-8"
        )
        self.ledger = self.root / "ledger.jsonl"

    def _record(self, **kwargs: str | None) -> dict[str, str]:
        fields: dict = {"file_path": _FILE, "disposition": "convert", "task_id": "TASK-x"}
        fields.update(kwargs)
        return record_processed(self.root, ledger_path=self.ledger, **fields)

    def _events(self) -> list[dict]:
        if not self.ledger.is_file():
            return []
        return [json.loads(line) for line in self.ledger.read_text(encoding="utf-8").splitlines()]

    def test_a_batch_under_a_task_books_one_parseable_event(self) -> None:
        self._record()
        (event,) = self._events()
        parsed = parse_typed_event(event)
        self.assertEqual(parsed.event, "chore_decommission_processed")
        self.assertEqual(event["file_path"], _FILE)
        self.assertEqual(event["task_id"], "TASK-x")
        self.assertNotIn("obpi_id", event)

    def test_a_batch_under_an_obpi_books_the_obpi(self) -> None:
        self._record(task_id=None, obpi_id="OBPI-0.0.59-05-first-sweep-wave-top-5-offenders")
        (event,) = self._events()
        self.assertEqual(event["obpi_id"], "OBPI-0.0.59-05-first-sweep-wave-top-5-offenders")
        self.assertNotIn("task_id", event)

    def test_each_refusal_writes_nothing(self) -> None:
        cases = {
            "no work order": ({"task_id": None}, WorkOrderAmbiguousError),
            "both work orders": ({"obpi_id": "OBPI-1"}, WorkOrderAmbiguousError),
            "a task without its prefix": ({"task_id": "chore-x"}, WorkOrderMalformedError),
            "an obpi without its prefix": (
                {"task_id": None, "obpi_id": "0.0.59-05"},
                WorkOrderMalformedError,
            ),
            "an unknown disposition": ({"disposition": "delete"}, UnknownDispositionError),
            "a file never baselined": ({"file_path": "tests/other.py"}, FileNotInBaselineError),
        }
        for name, (kwargs, error) in cases.items():
            with self.subTest(name), self.assertRaises(error):
                self._record(**kwargs)
        self.assertEqual(self._events(), [])

    def test_a_pre_existing_obpi_row_still_parses(self) -> None:
        """Rows written before the TASK work order existed carry obpi_id alone."""
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "chore_decommission_processed",
            "id": _FILE,
            "ts": "2026-05-27T06:28:31.705004+00:00",
            "file_path": _FILE,
            "disposition": "fold-to-validator",
            "obpi_id": "OBPI-0.0.59-05-first-sweep-wave-top-5-offenders",
        }
        self.assertEqual(parse_typed_event(row).event, "chore_decommission_processed")


if __name__ == "__main__":
    unittest.main()
