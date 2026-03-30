"""Tests for WBS table parsing and lane resolution in gz specify.

@covers ADR-pool.per-command-persona-context
"""

import unittest

from gzkit.commands.specify_cmd import _resolve_lane_from_wbs, _resolve_objective_from_wbs
from gzkit.core.scoring import WbsRow, parse_wbs_table

SAMPLE_ADR = """\
# ADR-0.0.11 — Test ADR

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.11-01 | Research synthesis and design principles | Lite | Pending |
| 2 | OBPI-0.0.11-02 | Persona control surface definition | Heavy | Pending |
| 3 | OBPI-0.0.11-03 | Trait composition model | Lite | Pending |
| 4 | OBPI-0.0.11-04 | AGENTS.md template update | Heavy | Pending |

## Intent

Some intent text.
"""


class TestParseWbsTable(unittest.TestCase):
    """Verify WBS table parsing extracts rows correctly."""

    def test_extracts_all_rows(self):
        rows = parse_wbs_table(SAMPLE_ADR)
        self.assertEqual(len(rows), 4)

    def test_row_fields(self):
        rows = parse_wbs_table(SAMPLE_ADR)
        row1 = rows[0]
        self.assertEqual(row1.item, 1)
        self.assertEqual(row1.obpi_id, "OBPI-0.0.11-01")
        self.assertEqual(row1.spec_summary, "Research synthesis and design principles")
        self.assertEqual(row1.lane, "lite")
        self.assertEqual(row1.status, "Pending")

    def test_heavy_lane_parsed(self):
        rows = parse_wbs_table(SAMPLE_ADR)
        row2 = rows[1]
        self.assertEqual(row2.lane, "heavy")
        self.assertEqual(row2.item, 2)

    def test_empty_content_returns_empty(self):
        rows = parse_wbs_table("# No WBS here\n\n## Intent\n\nSome text.")
        self.assertEqual(rows, [])

    def test_missing_section_returns_empty(self):
        rows = parse_wbs_table("")
        self.assertEqual(rows, [])


class TestResolveLaneFromWbs(unittest.TestCase):
    """Verify lane resolution priority: CLI > WBS > fallback."""

    def setUp(self):
        self.wbs_rows = parse_wbs_table(SAMPLE_ADR)

    def test_cli_override_wins(self):
        lane = _resolve_lane_from_wbs(self.wbs_rows, 1, "heavy")
        self.assertEqual(lane, "heavy")

    def test_wbs_used_when_no_cli(self):
        lane = _resolve_lane_from_wbs(self.wbs_rows, 2, None)
        self.assertEqual(lane, "heavy")

    def test_wbs_lite_used_when_no_cli(self):
        lane = _resolve_lane_from_wbs(self.wbs_rows, 1, None)
        self.assertEqual(lane, "lite")

    def test_fallback_lite_when_item_not_in_wbs(self):
        lane = _resolve_lane_from_wbs(self.wbs_rows, 99, None)
        self.assertEqual(lane, "lite")

    def test_fallback_lite_when_no_wbs(self):
        lane = _resolve_lane_from_wbs([], 1, None)
        self.assertEqual(lane, "lite")


class TestResolveObjectiveFromWbs(unittest.TestCase):
    """Verify objective extraction from WBS spec summary."""

    def setUp(self):
        self.wbs_rows = parse_wbs_table(SAMPLE_ADR)

    def test_extracts_spec_summary(self):
        obj = _resolve_objective_from_wbs(self.wbs_rows, 1, "fallback")
        self.assertEqual(obj, "Research synthesis and design principles.")

    def test_fallback_when_item_missing(self):
        obj = _resolve_objective_from_wbs(self.wbs_rows, 99, "fallback text")
        self.assertEqual(obj, "fallback text")

    def test_fallback_when_no_wbs(self):
        obj = _resolve_objective_from_wbs([], 1, "fallback text")
        self.assertEqual(obj, "fallback text")

    def test_preserves_existing_period(self):
        rows = [WbsRow(item=1, obpi_id="X", spec_summary="Already ends.", lane="lite", status="P")]
        obj = _resolve_objective_from_wbs(rows, 1, "fallback")
        self.assertEqual(obj, "Already ends.")


if __name__ == "__main__":
    unittest.main()
