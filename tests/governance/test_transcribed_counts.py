"""Live ADR OBPI counts are refused; dated records are not (GHI #768).

The issue's binding constraint is that a remedy must not falsify the archive:
of the 135 files under `docs/` carrying an `N/M` figure, most are dated
amendment records, audit forms, and sealed briefs where the count is CORRECT AS
HISTORY. So roughly half these tests assert what the audit must NOT flag. An
audit for this class that only proved it catches violations would pass just as
well while rewriting the record, which is the failure the GHI names outright.

Every case runs against a synthetic tree. A suite that only asserted the live
repo is clean would pass equally well if the audit had no teeth.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.transcribed_counts import audit_transcribed_counts


class _Tree(unittest.TestCase):
    """Builds a synthetic repo with one declared live surface."""

    def _build(self, body: str, *, historical: list[str] | None = None) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / "data").mkdir()
        (root / "docs").mkdir()
        (root / "data" / "transcribed_count_surfaces.json").write_text(
            json.dumps(
                {
                    "surfaces": [
                        {
                            "path": "docs/live.md",
                            "historical_sections": historical or [],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (root / "docs" / "live.md").write_text(body, encoding="utf-8")
        return root


class LiveCountsAreRefused(_Tree):
    """The claim the issue was filed about."""

    def test_a_landed_count_beside_an_adr_id_is_flagged(self) -> None:
        root = self._build("# Q\n\n- `ADR-0.35.0` is `Draft`, 0/10 landed.\n")
        self.assertEqual(len(audit_transcribed_counts(root)), 1)

    def test_an_in_progress_count_is_flagged(self) -> None:
        root = self._build("# Q\n\n- `ADR-0.44.0` is `IN_PROGRESS` at **1/6**.\n")
        self.assertEqual(len(audit_transcribed_counts(root)), 1)

    def test_the_finding_names_the_line_number(self) -> None:
        """An audit that cannot say WHERE is not actionable on a 500-line file."""
        root = self._build("# Q\n\nfiller\n\n- `ADR-0.35.0` `Draft` 0/10 landed.\n")
        errors = audit_transcribed_counts(root)
        self.assertEqual(errors[0].artifact, "docs/live.md:5")

    def test_the_finding_states_the_recovery(self) -> None:
        root = self._build("# Q\n\n- `ADR-0.35.0` `Draft` 0/10 landed.\n")
        message = audit_transcribed_counts(root)[0].message
        self.assertIn("gz adr status", message)
        self.assertIn("never", message.lower())


class DatedRecordsAreLeftAlone(_Tree):
    """The half that keeps the remedy from falsifying the archive."""

    def test_a_count_under_a_declared_historical_section_is_not_flagged(self) -> None:
        root = self._build(
            "# C\n\n## Amendments\n\n- 2026-07-29: `ADR-0.35.0` read 0/9 landed.\n",
            historical=["Amendments"],
        )
        self.assertEqual(audit_transcribed_counts(root), [])

    def test_a_historical_heading_matches_with_ordinals_and_parentheticals(self) -> None:
        """Real headings are numbered and annotated; equality matching missed them.

        `## 9. Rulings Register (carried forward — the anti-orphaning mechanism)`
        is the live example that exposed this: an exact-match rule scanned an
        archival section as live and would have demanded the archive be edited.
        """
        root = self._build(
            "# C\n\n## 9. Rulings Register (carried forward)\n\n"
            "- corrects the stale `ADR-0.0.65` 1/5 landed reading.\n",
            historical=["Rulings Register"],
        )
        self.assertEqual(audit_transcribed_counts(root), [])

    def test_a_subsection_inherits_its_historical_parent(self) -> None:
        """Depth tracking, not heading equality — else H3 children read as live."""
        root = self._build(
            "# C\n\n## Amendments\n\n### 2026-07-29 correction\n\n"
            "- `ADR-0.35.0` read 0/9 landed.\n",
            historical=["Amendments"],
        )
        self.assertEqual(audit_transcribed_counts(root), [])

    def test_the_historical_section_closes_at_a_same_depth_heading(self) -> None:
        """Inheritance must END, or one archival section exempts the whole file."""
        root = self._build(
            "# C\n\n## Amendments\n\n- `ADR-0.35.0` read 0/9 landed.\n\n"
            "## Queue\n\n- `ADR-0.35.0` is `Draft` 0/10 landed.\n",
            historical=["Amendments"],
        )
        errors = audit_transcribed_counts(root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].artifact, "docs/live.md:9")

    def test_an_inline_marker_exempts_a_single_line(self) -> None:
        root = self._build("# Q\n\n- `ADR-0.35.0` read 0/9 landed. <!-- historical-count -->\n")
        self.assertEqual(audit_transcribed_counts(root), [])


class NonCountsAreNotMistakenForClaims(_Tree):
    """False positives here would force ADRs to stop naming their own parts."""

    def test_an_obpi_identifier_range_is_not_a_count(self) -> None:
        """`OBPI-02/03` names two briefs; flagging it is a category error."""
        root = self._build("# Q\n\n- `ADR-0.0.37` withdrew OBPI-02/03 as obsolete.\n")
        self.assertEqual(audit_transcribed_counts(root), [])

    def test_a_ratio_with_no_progress_cue_nearby_is_not_a_count(self) -> None:
        """A closeout record's QC dimension score shares the ADR's line."""
        root = self._build("# Q\n\n- `ADR-0.34.0` capstone: Interface scored 2/2.\n")
        self.assertEqual(audit_transcribed_counts(root), [])

    def test_a_count_with_no_adr_on_the_line_is_not_a_count(self) -> None:
        root = self._build("# Q\n\n- Coverage sits at 40/100 of the floor.\n")
        self.assertEqual(audit_transcribed_counts(root), [])


class RegistryFailures(_Tree):
    """A registry that scans nothing must not report clean."""

    def test_a_declared_surface_that_does_not_exist_is_an_error(self) -> None:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / "data").mkdir()
        (root / "data" / "transcribed_count_surfaces.json").write_text(
            json.dumps({"surfaces": [{"path": "docs/gone.md"}]}), encoding="utf-8"
        )
        errors = audit_transcribed_counts(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0].message)

    def test_an_absent_registry_scans_nothing_without_raising(self) -> None:
        """gz check must not crash on a tree that predates the registry."""
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.assertEqual(audit_transcribed_counts(root), [])


if __name__ == "__main__":
    unittest.main()
