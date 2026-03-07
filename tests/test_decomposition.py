"""Tests for deterministic ADR decomposition helpers."""

import unittest

from gzkit.decomposition import (
    baseline_range_for_total,
    build_checklist_seed,
    compute_scorecard,
    parse_checklist_items,
    parse_scorecard,
)


class TestDecompositionScoring(unittest.TestCase):
    """Scoring and cutoff behavior tests."""

    def test_baseline_cutoffs(self) -> None:
        """Dimension totals map to expected baseline ranges."""
        self.assertEqual(baseline_range_for_total(0), (1, 2))
        self.assertEqual(baseline_range_for_total(4), (3, 3))
        self.assertEqual(baseline_range_for_total(8), (4, 4))
        self.assertEqual(baseline_range_for_total(10), (5, None))

    def test_scorecard_final_target_adds_split_rules(self) -> None:
        """Final target equals selected baseline + split total."""
        card = compute_scorecard(
            data_state=1,
            logic_engine=1,
            interface=1,
            observability=1,
            lineage=1,
            split_single_narrative=1,
            split_surface_boundary=1,
            split_state_anchor=0,
            split_testability_ceiling=0,
            baseline_selected=3,
        )
        self.assertEqual(card.dimension_total, 5)
        self.assertEqual(card.split_total, 2)
        self.assertEqual(card.final_target_obpi_count, 5)

    def test_build_checklist_seed_matches_target_count(self) -> None:
        """Checklist seed helper emits one line per target OBPI."""
        checklist = build_checklist_seed("0.9.0", 3)
        self.assertEqual(checklist.count("- [ ]"), 3)
        self.assertIn("OBPI-0.9.0-03", checklist)


class TestDecompositionParsing(unittest.TestCase):
    """Parser behavior tests for ADR scorecard/checklist surfaces."""

    def test_parse_checklist_multiline_items(self) -> None:
        """Checklist parser folds wrapped lines into single item text."""
        content = """## Checklist

- [ ] OBPI-0.1.0-01: First line
      wrapped continuation
- [ ] OBPI-0.1.0-02: Second item
"""
        items = parse_checklist_items(content)
        self.assertEqual(len(items), 2)
        self.assertIn("wrapped continuation", items[0])

    def test_parse_scorecard_valid(self) -> None:
        """Valid scorecard parses into a structured card."""
        content = """## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 4
"""
        card, errors = parse_scorecard(content)
        self.assertEqual(errors, [])
        self.assertIsNotNone(card)
        assert card is not None
        self.assertEqual(card.final_target_obpi_count, 4)

    def test_parse_scorecard_missing_section(self) -> None:
        """Missing scorecard section reports an explicit error."""
        card, errors = parse_scorecard("## Checklist\n\n- [ ] Item")
        self.assertIsNone(card)
        self.assertTrue(any("Missing required section" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
