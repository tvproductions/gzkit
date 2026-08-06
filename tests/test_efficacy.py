"""Efficacy channel — a capability must report its reach, not just its numerator.

`OBPI-0.25.0-33` shipped ARB `attested_completed` on criteria that asserted files
were present and six scenarios existed, with `Receipts scanned: 0` cited as a
passing Key Proof. Every criterion still holds while the harvest reads 4% of its
store. These tests pin the properties that make that state impossible to report
as success.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from gzkit.arb.advisor import collect_arb_advice
from gzkit.arb.coverage import measure_receipt_coverage
from gzkit.arb.patterns import collect_patterns
from gzkit.arb.ruff_reporter import SCHEMA_ID as LINT_SCHEMA_ID
from gzkit.efficacy import StoreCoverage


class TestReachIsMeasuredAgainstTheWholeStore(unittest.TestCase):
    """The denominator is the store, never the consumer's own eligible subset."""

    def test_a_consumer_that_narrows_its_input_does_not_thereby_reach_100_percent(self) -> None:
        # ARB's shape: 130 readable of 3286 present, all readable ones read.
        # Measured against `eligible` this is 100% and looks finished.
        coverage = StoreCoverage(
            store="artifacts/receipts", present=3286, eligible=130, covered=130
        )
        self.assertAlmostEqual(coverage.reach, 130 / 3286, places=6)
        self.assertLess(coverage.reach, 0.05)

    def test_empty_store_reports_zero_rather_than_dividing_by_zero(self) -> None:
        coverage = StoreCoverage(store="s", present=0, eligible=0, covered=0)
        self.assertEqual(coverage.reach, 0.0)

    def test_exhaustive_requires_both_untruncated_and_complete(self) -> None:
        # A retention or promotion decision keys on this, so each half must bind:
        # a truncated run says nothing about what it never looked at.
        complete = StoreCoverage(store="s", present=10, eligible=4, covered=4)
        truncated = StoreCoverage(store="s", present=10, eligible=4, covered=4, truncated=True)
        partial = StoreCoverage(store="s", present=10, eligible=4, covered=2)
        self.assertTrue(complete.exhaustive)
        self.assertFalse(truncated.exhaustive)
        self.assertFalse(partial.exhaustive)


class TestRenderKeepsTheDenominatorAttached(unittest.TestCase):
    """`Receipts scanned: 130` read as success for three months. `130 of 3286` cannot."""

    def test_summary_states_both_terms_and_names_what_has_no_harvester(self) -> None:
        coverage = StoreCoverage(
            store="artifacts/receipts",
            present=3286,
            eligible=130,
            covered=130,
            unreadable=[("gzkit.arb.step_receipt.v1", 2265)],
        )
        rendered = coverage.render()
        self.assertIn("130 of 3286", rendered)
        self.assertIn("gzkit.arb.step_receipt.v1 x2265", rendered)

    def test_truncation_is_stated_rather_than_implied_by_a_low_number(self) -> None:
        coverage = StoreCoverage(store="s", present=100, eligible=100, covered=5, truncated=True)
        self.assertIn("TRUNCATED", coverage.render())


class ReceiptStoreTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _write(self, name: str, schema: str) -> None:
        (self.root / name).write_text(
            json.dumps(
                {
                    "schema": schema,
                    "exit_status": 0,
                    "findings": [],
                    "findings_total": 0,
                    "timestamp_utc": datetime.now(UTC).isoformat(),
                }
            ),
            encoding="utf-8",
        )


class TestCensusCountsWhatNoHarvesterReads(ReceiptStoreTestCase):
    def test_kinds_the_consumer_cannot_read_stay_in_the_denominator(self) -> None:
        # The defect this exists to surface: excluding them would report the
        # harvest as complete while 69% of the store had no reader at all.
        self._write("arb-ruff-a.json", LINT_SCHEMA_ID)
        for i in range(9):
            self._write(f"arb-step-{i}.json", "gzkit.arb.step_receipt.v1")

        coverage = measure_receipt_coverage(
            self.root, readable_schema=LINT_SCHEMA_ID, covered=1, truncated=False
        )

        self.assertEqual(coverage.present, 10)
        self.assertEqual(coverage.eligible, 1)
        self.assertEqual(coverage.unreadable, [("gzkit.arb.step_receipt.v1", 9)])

    def test_an_unparseable_receipt_is_counted_not_skipped(self) -> None:
        # A file the census cannot read is still occupying the store; dropping it
        # would shrink the denominator exactly where the store is least healthy.
        self._write("arb-ruff-a.json", LINT_SCHEMA_ID)
        (self.root / "broken.json").write_text("{not json", encoding="utf-8")

        coverage = measure_receipt_coverage(
            self.root, readable_schema=LINT_SCHEMA_ID, covered=1, truncated=False
        )

        self.assertEqual(coverage.present, 2)
        self.assertIn(("<unparseable>", 1), coverage.unreadable)


class TestHarvestVerbsReportCoverage(ReceiptStoreTestCase):
    def test_advise_reports_reach_over_the_whole_store(self) -> None:
        self._write("arb-ruff-a.json", LINT_SCHEMA_ID)
        for i in range(3):
            self._write(f"arb-step-{i}.json", "gzkit.arb.step_receipt.v1")

        advice = collect_arb_advice(limit=-1, root=self.root)

        self.assertIsNotNone(advice.coverage)
        assert advice.coverage is not None
        self.assertEqual(advice.coverage.present, 4)
        self.assertEqual(advice.coverage.covered, advice.scanned_receipts)

    def test_patterns_reports_reach_over_the_whole_store(self) -> None:
        self._write("arb-ruff-a.json", LINT_SCHEMA_ID)
        self._write("arb-step-0.json", "gzkit.arb.step_receipt.v1")

        report = collect_patterns(limit=-1, root=self.root)

        self.assertIsNotNone(report.coverage)
        assert report.coverage is not None
        self.assertEqual(report.coverage.present, 2)
        self.assertEqual(report.coverage.eligible, 1)

    def test_a_limited_run_declares_itself_truncated(self) -> None:
        # Silent truncation is what made `--limit 50` look like a full harvest.
        for i in range(6):
            self._write(f"arb-ruff-{i}.json", LINT_SCHEMA_ID)

        limited = collect_arb_advice(limit=2, root=self.root)
        full = collect_arb_advice(limit=-1, root=self.root)

        assert limited.coverage is not None and full.coverage is not None
        self.assertTrue(limited.coverage.truncated)
        self.assertFalse(limited.coverage.exhaustive)
        self.assertTrue(full.coverage.exhaustive)


if __name__ == "__main__":
    unittest.main()
