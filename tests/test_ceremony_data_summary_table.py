"""GHI-116: Bill-of-Materials summary table must not truncate columns.

Before the fix, the table set ``no_wrap=True`` and ``overflow="ellipsis"`` on
Lane, Status, and Objective columns, so a 100-column terminal rendered:

  Lane: ``Li…``, Status: ``Comple…``, Objective: ``gz patch release com…``

Each OBPI must be fully readable.
"""

from __future__ import annotations

import unittest
from io import StringIO

from rich.console import Console

from gzkit.commands.ceremony_data import _SUMMARY_COLUMNS, format_summary_table
from gzkit.reporter.presets import status_table
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


class TestSummaryTableColumnAllocation(unittest.TestCase):
    """GHI #362: At constrained widths, the OBPI column must yield to Objective.

    The renderer's allocation contract: when terminal width is constrained,
    OBPI is allowed to wrap (its slug is recoverable from the brief filename),
    so that Objective — which carries the operator's scope-review signal —
    keeps enough horizontal room for sentence-friendly wrap.
    """

    @covers("REQ-0.23.0-04-13")
    def test_obpi_column_wraps_under_squeeze_so_objective_gets_room(self) -> None:
        # Post-_short_obpi_id form: long slug that would dominate the row at
        # narrow widths if OBPI refused to wrap.
        long_slug = "05-gate5-walkthrough-arb-slot"  # 29 chars
        briefs = [
            {
                "id": long_slug,
                "lane": "Heavy",
                "status": "Completed",
                "objective": (
                    "Gate 5 walkthrough extension + ARB canonical command "
                    "slot — Walkthrough prompt at the OBPI command surface; "
                    "CANONICAL_STEP_COMMANDS extends with reserved "
                    "security-scan slot."
                ),
            },
        ]
        # Render at a fixed narrow width — the live terminal size shutil
        # reports is irrelevant here; we drive Console.width directly.
        table = status_table(title="BOM", columns=_SUMMARY_COLUMNS, rows=briefs)
        buf = StringIO()
        Console(file=buf, force_terminal=False, width=60).print(table)
        rendered = buf.getvalue()

        # Behavior pin: at width=60 the long slug must be wrapped (split
        # across multiple lines). If OBPI refused to wrap, the slug would
        # appear on one line and Objective would be squeezed mid-token.
        slug_appears_intact_on_one_line = any(long_slug in line for line in rendered.splitlines())
        self.assertFalse(
            slug_appears_intact_on_one_line,
            (
                "At width=60 the OBPI slug must wrap (yielding width to "
                "Objective), not appear intact on one line. Rendered:\n" + rendered
            ),
        )

        # Operator-facing recoverability: every hyphen-delimited segment of
        # the slug must still appear in the rendered output even though the
        # slug itself is wrapped across multiple lines.
        for segment in long_slug.split("-"):
            self.assertIn(
                segment,
                rendered,
                f"OBPI slug segment {segment!r} missing from wrapped render.",
            )


if __name__ == "__main__":
    unittest.main()
