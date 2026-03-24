"""Tests for core scoring domain logic (extracted from decomposition.py)."""

import unittest

from pydantic import ValidationError

from gzkit.core.scoring import (
    DecompositionScorecard,
    baseline_range_for_total,
    build_checklist_seed,
    compute_scorecard,
    extract_markdown_section,
    parse_checklist_items,
)


class TestCoreDecompositionScorecard(unittest.TestCase):
    """Verify DecompositionScorecard is importable from core."""

    def test_scorecard_frozen(self) -> None:
        card = compute_scorecard(
            data_state=1,
            logic_engine=1,
            interface=1,
            observability=1,
            lineage=1,
            split_single_narrative=0,
            split_surface_boundary=0,
            split_state_anchor=0,
            split_testability_ceiling=0,
        )
        self.assertIsInstance(card, DecompositionScorecard)
        with self.assertRaises(ValidationError):
            card.data_state = 2


class TestCoreBaselineRange(unittest.TestCase):
    """Verify baseline range computation from core."""

    def test_low_total(self) -> None:
        self.assertEqual(baseline_range_for_total(2), (1, 2))

    def test_mid_total(self) -> None:
        self.assertEqual(baseline_range_for_total(5), (3, 3))

    def test_high_total(self) -> None:
        result = baseline_range_for_total(9)
        self.assertEqual(result, (5, None))


class TestCoreMarkdownParsing(unittest.TestCase):
    """Verify markdown helpers from core."""

    def test_extract_section(self) -> None:
        content = "## Foo\nbar\n## Baz\nqux\n"
        result = extract_markdown_section(content, "Foo")
        self.assertEqual(result, "bar")

    def test_parse_checklist_items(self) -> None:
        content = "## Checklist\n- [ ] Item one\n- [x] Item two\n"
        items = parse_checklist_items(content)
        self.assertEqual(len(items), 2)


class TestCoreBuildChecklist(unittest.TestCase):
    """Verify checklist seed generation from core."""

    def test_build_checklist(self) -> None:
        result = build_checklist_seed("0.1.0", 3)
        self.assertIn("OBPI-0.1.0-01", result)
        self.assertIn("OBPI-0.1.0-03", result)


class TestCoreReExports(unittest.TestCase):
    """Verify original module re-exports work (backward compat)."""

    def test_decomposition_reexports_scorecard(self) -> None:
        from gzkit.decomposition import DecompositionScorecard as orig

        self.assertIs(orig, DecompositionScorecard)

    def test_decomposition_reexports_functions(self) -> None:
        from gzkit.decomposition import compute_scorecard as orig

        self.assertIs(orig, compute_scorecard)


if __name__ == "__main__":
    unittest.main()
