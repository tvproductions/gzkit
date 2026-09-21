"""A row appearing twice in the ledger is detected, not silent (GHI #1075).

WHY: `ledger_merge` deliberately does NOT deduplicate. GHI #1075's close comment
measured what that means, on both the pre-fix and current module:

    Identical addition at the TAIL   (anc=[A], both sides [A,B])   -> [A,B,B]
    Identical addition MID-FILE      (anc=[A,C], both sides [A,B,C]) -> [A,B,B,C]

Duplication is therefore not new for tail additions; what the repair widened is
the mid-file variant, which used to be refused as rewritten history and now
merges. The rule is KEPT -- collapsing rows would let a merge destroy a genuine
event, and nothing can tell a real repeat from a merge artifact automatically.

What was wrong is that the result was SILENT: a ledger carrying one row twice
validated at ZERO errors, against a no-duplicate control also at zero. The
surface whose job is to detect ledger defects could not see this one.

Detection, not deduplication, is the repair. Operator ruling 2026-09-21 ("do").

The historical instance is waived by CONTENT hash rather than removed: the
ledger is append-only with no delete path, and trust-doctrine T2 forbids
rewriting closed-evidence history. Measured 2026-09-21: exactly ONE duplicate in
17027 rows.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.validate_pkg.ledger_check import (
    _DUPLICATE_ROW_GRANDFATHER,
    _row_fingerprint,
    validate_ledger,
)

_LIVE_LEDGER = get_project_root() / ".gzkit" / "ledger.jsonl"

_ROW = {
    "schema": "gzkit.ledger.v1",
    "event": "obpi_created",
    "id": "OBPI-0.1.0-01-example",
    "ts": "2026-01-01T00:00:00+00:00",
    "parent": "ADR-0.1.0-example",
}
_LATER = {**_ROW, "id": "OBPI-0.1.0-02-example", "ts": "2026-01-02T00:00:00+00:00"}


def _errors_for(rows: list[dict[str, object]]) -> list[str]:
    """Write *rows* to a throwaway ledger and return the validator's messages."""
    path = Path(tempfile.mkdtemp()) / "ledger.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
    return [error.message for error in validate_ledger(path)]


def _live_errors() -> list[str]:
    """Return the validator's messages for this repository's own ledger."""
    return [error.message for error in validate_ledger(_LIVE_LEDGER)]


def _live_fingerprints() -> set[str]:
    """Return the content fingerprint of every row in the live ledger."""
    fingerprints = set()
    for line in _LIVE_LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            fingerprints.add(_row_fingerprint(json.loads(line)))
    return fingerprints


class TestDuplicateRowsAreDetected(unittest.TestCase):
    """The condition GHI #1075 measured as silent now reports."""

    def test_a_repeated_row_is_reported(self) -> None:
        messages = _errors_for([_ROW, _ROW])

        self.assertTrue(
            any("Duplicate row" in message for message in messages),
            "a ledger carrying one row twice validated at zero errors before this",
        )

    def test_the_report_names_the_line_the_row_first_appeared_on(self) -> None:
        messages = _errors_for([_ROW, _LATER, dict(_ROW)])

        self.assertTrue(any("byte-identical to line 1" in message for message in messages))

    def test_distinct_rows_are_green(self) -> None:
        self.assertEqual(_errors_for([_ROW, _LATER]), [])

    def test_key_order_does_not_hide_a_duplicate(self) -> None:
        reordered = dict(reversed(list(_ROW.items())))
        messages = _errors_for([_ROW, reordered])

        self.assertTrue(
            any("Duplicate row" in message for message in messages),
            "the fingerprint is canonical, so re-serialising a row cannot evade it",
        )


class TestTheGrandfatherStaysHonest(unittest.TestCase):
    """The waiver discloses history; it must not become a standing permission."""

    def test_the_live_ledger_is_green(self) -> None:
        self.assertEqual(
            _live_errors(),
            [],
            "the single pre-existing duplicate is waived by content hash; any "
            "other finding here is a real defect",
        )

    def test_every_waived_fingerprint_is_still_present(self) -> None:
        stale = sorted(set(_DUPLICATE_ROW_GRANDFATHER) - _live_fingerprints())

        self.assertEqual(
            stale,
            [],
            "a waived fingerprint no longer in the ledger is a standing permission "
            "nothing uses; remove the entry",
        )

    def test_every_waiver_carries_a_reason(self) -> None:
        self.assertTrue(all(reason.strip() for reason in _DUPLICATE_ROW_GRANDFATHER.values()))

    def test_the_waiver_table_is_closed_to_new_content(self) -> None:
        """A NEW duplicate fails even though an older one is waived."""
        messages = _errors_for([_ROW, _ROW])

        self.assertTrue(any("Duplicate row" in message for message in messages))
