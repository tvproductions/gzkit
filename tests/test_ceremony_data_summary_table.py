"""GHI-116: Bill-of-Materials summary table must not truncate columns.

Before the fix, the table set ``no_wrap=True`` and ``overflow="ellipsis"`` on
Lane, Status, and Objective columns, so a 100-column terminal rendered:

  Lane: ``Li…``, Status: ``Comple…``, Objective: ``gz patch release com…``

Each OBPI must be fully readable.
"""

from __future__ import annotations

import unittest

from gzkit.commands.ceremony_data import format_summary_table
from gzkit.traceability import covers


class TestFormatSummaryTableNoTruncation(unittest.TestCase):
    """The summary table renders OBPI metadata without lossy truncation."""

    @covers("REQ-0.23.0-04-13")
    def test_long_objective_renders_in_full(self) -> None:
        briefs = [
            {
                "id": "OBPI-0.0.15-04-version-sync-integration",
                "lane": "Heavy",
                "status": "Completed",
                "objective": (
                    "gz patch release computes the next semantic version, writes the "
                    "release manifest, and bumps the version across pyproject."
                ),
            }
        ]

        rendered = format_summary_table(briefs, title="Test BOM")

        # Full Lane and Status text — no ellipsis substitution.
        self.assertIn("Heavy", rendered)
        self.assertIn("Completed", rendered)
        self.assertNotIn("Li…", rendered)
        self.assertNotIn("Comple…", rendered)
        self.assertNotIn("…", rendered, "No truncation ellipsis should appear anywhere")

        # Objective text is present, possibly across multiple wrapped lines.
        # Strip newlines and column-padding before substring check so wrap
        # boundaries don't fail the assertion.
        flat = " ".join(line.strip("│ ") for line in rendered.splitlines())
        for phrase in ("gz patch release", "semantic version", "release manifest"):
            self.assertIn(phrase, flat, f"Objective phrase missing: {phrase!r}")

    @covers("REQ-0.23.0-04-13")
    def test_short_objective_one_line(self) -> None:
        """Short objectives still render cleanly without unnecessary wrapping."""
        briefs = [
            {
                "id": "OBPI-0.1.0-01-demo",
                "lane": "Lite",
                "status": "Pending",
                "objective": "Short text.",
            }
        ]
        rendered = format_summary_table(briefs, title="Test BOM")
        self.assertIn("Short text.", rendered)
        self.assertIn("Lite", rendered)
        self.assertIn("Pending", rendered)


if __name__ == "__main__":
    unittest.main()
