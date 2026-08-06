"""ARB receipt retention — move-not-delete archive semantics (GHI #594).

Assertions derive from the guarantees the verb promises, not from a run of the
code: a cited receipt is evidence and must survive; nothing is ever deleted; a
pre-existing destination is never overwritten.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.arb.archive import execute_receipt_archive, plan_receipt_archive

NOW = datetime(2026, 8, 6, tzinfo=UTC)


def _write_receipt(root: Path, name: str, *, age_days: int | None) -> Path:
    """Write a receipt whose declared age is *age_days* (None → undatable)."""
    payload: dict[str, object] = {"schema": "gzkit.arb.v1", "tool": "ruff"}
    if age_days is not None:
        payload["timestamp_utc"] = (NOW - timedelta(days=age_days)).isoformat()
    path = root / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class ReceiptArchiveTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.root = self.base / "artifacts" / "receipts"
        self.root.mkdir(parents=True)
        (self.base / ".gzkit").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _ledger(self, *cited_ids: str) -> None:
        lines = [
            json.dumps({"event": "adr_receipt_emitted", "evidence": {"receipts": [rid]}})
            for rid in cited_ids
        ]
        (self.base / ".gzkit" / "ledger.jsonl").write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )

    def _plan(self, days: int = 30):
        return plan_receipt_archive(
            root=self.root, base_path=self.base, older_than_days=days, now=NOW
        )


class TestCitationGuard(ReceiptArchiveTestCase):
    """A receipt cited as attestation evidence must never be relocated."""

    def test_cited_receipt_is_never_eligible_however_old(self) -> None:
        _write_receipt(self.root, "arb-ruff-cited.json", age_days=9999)
        self._ledger("arb-ruff-cited")

        plan = self._plan()

        self.assertEqual(plan.eligible, [])
        self.assertEqual(plan.skipped_cited, ["arb-ruff-cited.json"])

    def test_uncited_sibling_of_a_cited_receipt_is_still_eligible(self) -> None:
        # The guard must key on the individual receipt id, not on "some ARB receipt
        # is cited" — otherwise one citation freezes the entire store.
        _write_receipt(self.root, "arb-ruff-cited.json", age_days=90)
        _write_receipt(self.root, "arb-ruff-loose.json", age_days=90)
        self._ledger("arb-ruff-cited")

        plan = self._plan()

        self.assertEqual(plan.eligible, ["arb-ruff-loose.json"])
        self.assertEqual(plan.skipped_cited, ["arb-ruff-cited.json"])

    def test_citation_is_found_regardless_of_which_field_carries_it(self) -> None:
        # Receipt ids reach the ledger through several event shapes; the guard reads
        # the ledger as text precisely so an unenumerated shape still protects.
        _write_receipt(self.root, "arb-step-unittest-deep.json", age_days=90)
        (self.base / ".gzkit" / "ledger.jsonl").write_text(
            json.dumps(
                {
                    "event": "obpi_completed",
                    "attestation_text": "attest completed — arb-step-unittest-deep proves it",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertEqual(self._plan().skipped_cited, ["arb-step-unittest-deep.json"])


class TestAgeAndOwnershipSelection(ReceiptArchiveTestCase):
    def test_receipt_newer_than_threshold_is_retained(self) -> None:
        _write_receipt(self.root, "arb-ruff-fresh.json", age_days=5)
        self._ledger()

        plan = self._plan(days=30)

        self.assertEqual(plan.eligible, [])
        self.assertEqual(plan.skipped_recent, ["arb-ruff-fresh.json"])

    def test_undatable_receipt_is_skipped_rather_than_assumed_old(self) -> None:
        # An unreadable age must not read as "old enough to move" — the conservative
        # direction is the one that keeps evidence in place.
        _write_receipt(self.root, "arb-ruff-nodate.json", age_days=None)
        self._ledger()

        plan = self._plan()

        self.assertEqual(plan.eligible, [])
        self.assertEqual(plan.skipped_undatable, ["arb-ruff-nodate.json"])

    def test_foreign_emitter_receipts_are_left_alone(self) -> None:
        # The receipts root is shared; this verb owns ARB's lifecycle only.
        _write_receipt(self.root, "adr-taxonomy-backfill-2026.json", age_days=9999)
        self._ledger()

        plan = self._plan()

        self.assertEqual(plan.eligible, [])
        self.assertEqual(plan.skipped_foreign, ["adr-taxonomy-backfill-2026.json"])


class TestMoveNotDelete(ReceiptArchiveTestCase):
    def test_relocation_preserves_content_and_removes_no_evidence(self) -> None:
        source = _write_receipt(self.root, "arb-ruff-old.json", age_days=90)
        original = source.read_text(encoding="utf-8")
        self._ledger()

        result = execute_receipt_archive(self._plan(), root=self.root)

        moved_to = self.root / "archive" / "arb-ruff-old.json"
        self.assertEqual(result.moved, ["arb-ruff-old.json"])
        self.assertFalse(source.exists(), "source should be relocated, not copied")
        self.assertTrue(moved_to.is_file(), "evidence must survive relocation")
        self.assertEqual(moved_to.read_text(encoding="utf-8"), original)

    def test_conflict_present_at_plan_time_is_refused_before_execution(self) -> None:
        _write_receipt(self.root, "arb-ruff-dup.json", age_days=90)
        archive_dir = self.root / "archive"
        archive_dir.mkdir()
        (archive_dir / "arb-ruff-dup.json").write_text("PRIOR", encoding="utf-8")
        self._ledger()

        plan = self._plan()

        self.assertEqual(plan.eligible, [])
        self.assertEqual(plan.skipped_conflict, ["arb-ruff-dup.json"])

    def test_conflict_appearing_after_planning_never_clobbers(self) -> None:
        # The race the atomic no-clobber move exists for: the destination is clean
        # when the plan is computed and occupied by the time it executes. Asserting
        # only the plan-time refusal above would leave this path untested.
        _write_receipt(self.root, "arb-ruff-race.json", age_days=90)
        self._ledger()
        plan = self._plan()
        self.assertEqual(plan.eligible, ["arb-ruff-race.json"])

        archive_dir = self.root / "archive"
        archive_dir.mkdir()
        (archive_dir / "arb-ruff-race.json").write_text("PRIOR", encoding="utf-8")

        result = execute_receipt_archive(plan, root=self.root)

        self.assertEqual(result.moved, [], "a raced destination must not be moved onto")
        self.assertEqual(result.skipped_conflict, ["arb-ruff-race.json"])
        self.assertEqual(
            (archive_dir / "arb-ruff-race.json").read_text(encoding="utf-8"),
            "PRIOR",
            "the pre-existing archived receipt must survive the race",
        )

    def test_planning_is_pure_and_repeatable(self) -> None:
        # Purity asserted through the plan itself rather than a filesystem probe: a
        # plan that mutated the store would classify differently the second time.
        _write_receipt(self.root, "arb-ruff-old.json", age_days=90)
        self._ledger()

        self.assertEqual(self._plan(), self._plan())


if __name__ == "__main__":
    unittest.main()
