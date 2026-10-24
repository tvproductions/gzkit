"""The insights-shape audit holds each recorded insight to its ledger pointer.

The ``insight_recorded`` event fingerprints the record it names (operator ruling
2026-10-18, "Pointer + 3 fields"), so a record edited by hand after it was recorded,
or removed, is a finding. A record with no pointer predates the ruling and is not
backfilled (the 2026-10-17 structure-not-population ruling).
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_insights_shape
from gzkit.insights.ledger_ref import book_insight_recorded, insight_lines_by_ts

_LINE = json.dumps(
    {"ts": "2026-10-18T17:00:00+00:00", "type": "discovery", "scope": "s", "summary": "a"},
    separators=(",", ":"),
)


def _root(tmp: str, insight_lines: list[str]) -> Path:
    root = Path(tmp)
    store = root / ".gzkit" / "insights" / "agent-insights.jsonl"
    store.parent.mkdir(parents=True)
    store.write_text("".join(line + "\n" for line in insight_lines), encoding="utf-8")
    return root


def _pointer_findings(root: Path) -> list[str]:
    return [e.message for e in audit_insights_shape(root) if "insight_recorded" in e.message]


class TestRecordedInsightMatchesItsPointer(unittest.TestCase):
    def test_an_unedited_recorded_insight_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, [_LINE])
            book_insight_recorded(root / ".gzkit" / "ledger.jsonl", _LINE, source="operator")
            self.assertEqual(_pointer_findings(root), [])

    def test_a_record_edited_after_recording_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edited = _LINE.replace('"summary":"a"', '"summary":"b"')
            root = _root(tmp, [edited])
            book_insight_recorded(root / ".gzkit" / "ledger.jsonl", _LINE, source="operator")
            self.assertEqual(len(_pointer_findings(root)), 1)

    def test_a_pointer_to_a_missing_record_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, [])
            book_insight_recorded(root / ".gzkit" / "ledger.jsonl", _LINE, source="agent")
            self.assertEqual(len(_pointer_findings(root)), 1)

    def test_a_record_with_no_pointer_is_not_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, [_LINE])
            self.assertEqual(_pointer_findings(root), [])


class TestUnreadableInputsAreSkippedNotFatal(unittest.TestCase):
    def test_no_ledger_means_no_pointer_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit_insights_shape(_root(tmp, [_LINE])), [])

    def test_a_malformed_ledger_row_does_not_hide_the_next_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edited = _LINE.replace('"summary":"a"', '"summary":"b"')
            root = _root(tmp, [edited])
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.write_text('{"event": "insight_recorded", broken\n', encoding="utf-8")
            book_insight_recorded(ledger_path, _LINE, source="agent")
            self.assertEqual(len(_pointer_findings(root)), 1)

    def test_a_missing_store_maps_to_no_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(insight_lines_by_ts(Path(tmp) / "absent.jsonl"), {})

    def test_a_malformed_store_line_does_not_hide_the_valid_ones(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "store.jsonl"
            store.write_text("not json\n" + _LINE + "\n", encoding="utf-8")
            self.assertEqual(insight_lines_by_ts(store), {"2026-10-18T17:00:00+00:00": _LINE})


class TestThePointerReplaysInTheCorpus(unittest.TestCase):
    def test_a_ledger_carrying_pointers_still_projects_complete(self) -> None:
        from gzkit.ledger import Ledger
        from gzkit.ontology.corpus import project_corpus

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, [_LINE])
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            book_insight_recorded(ledger_path, _LINE, source="operator")
            fidelity = project_corpus(Ledger(ledger_path)).fidelity

        self.assertTrue(fidelity.complete, fidelity)


if __name__ == "__main__":
    unittest.main()
