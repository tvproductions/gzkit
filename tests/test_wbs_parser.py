"""Tests for WBS table parsing and ADR content extraction in gz specify.

@covers ADR-pool.per-command-persona-context
"""

import unittest

from gzkit.commands.specify_cmd import (
    _extract_decision_as_requirements,
    _extract_denied_paths,
    _extract_integration_points,
    _resolve_lane_from_wbs,
    _resolve_objective_from_wbs,
)
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

SAMPLE_ADR_WITH_CONTEXT = """\
# ADR-0.0.11 — Test ADR

## Agent Context Frame — MANDATORY

**Role:** Governance architect

**Purpose:** Establish persona control surface

**Critical Constraint:** Implementations MUST use virtue-ethics framing, NEVER expertise claims.

**Integration Points:**

- `src/gzkit/config.py` — GzkitConfig, PathConfig models
- `src/gzkit/commands/common.py` — load_manifest(), ensure_initialized()
- `.gzkit/manifest.json` — the resolved config artifact

## Decision

- Persona is a **control surface**, stored in `.gzkit/personas/`
- Persona frames use **virtue-ethics-based behavioral identity**
- Traits **compose orthogonally** per the PERSONA/ICLR 2026 framework
- The **operating system view** (PSM) is the adopted model

## Non-Goals

- **Runtime persona switching** — defines static frames, not dynamic changes
- **Activation-space manipulation** — operates at prompt level, not model internals
- **Persona effectiveness measurement** — deferred to ADR-0.0.13

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.11-01 | Research synthesis | Lite | Pending |

## Intent

Some text.
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


class TestExtractIntegrationPoints(unittest.TestCase):
    """Verify Integration Points extraction from ADR content."""

    def test_extracts_paths(self):
        result = _extract_integration_points(SAMPLE_ADR_WITH_CONTEXT)
        self.assertIn("src/gzkit/config.py", result)
        self.assertIn("src/gzkit/commands/common.py", result)
        self.assertIn(".gzkit/manifest.json", result)

    def test_preserves_descriptions(self):
        result = _extract_integration_points(SAMPLE_ADR_WITH_CONTEXT)
        self.assertIn("GzkitConfig", result)

    def test_fallback_when_no_integration_points(self):
        result = _extract_integration_points("# No integration points here")
        self.assertIn("src/module/", result)

    def test_returns_structured_lines(self):
        result = _extract_integration_points(SAMPLE_ADR_WITH_CONTEXT)
        lines = result.strip().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(all(line.startswith("- `") for line in lines))


class TestExtractDecisionAsRequirements(unittest.TestCase):
    """Verify Decision bullets become OBPI requirements."""

    def test_extracts_decision_bullets(self):
        result = _extract_decision_as_requirements(SAMPLE_ADR_WITH_CONTEXT)
        self.assertIn("REQUIREMENT:", result)
        self.assertIn("control surface", result)
        self.assertIn("virtue-ethics", result)

    def test_includes_critical_constraint(self):
        result = _extract_decision_as_requirements(SAMPLE_ADR_WITH_CONTEXT)
        self.assertIn("ALWAYS:", result)
        self.assertIn("virtue-ethics", result)

    def test_fallback_when_no_decision(self):
        result = _extract_decision_as_requirements("# No decision here")
        self.assertIn("Work MUST stay inside the Allowed Paths", result)

    def test_skips_template_placeholders(self):
        adr = "## Decision\n\n- {Testable bullet 1}\n- Real requirement\n"
        result = _extract_decision_as_requirements(adr)
        self.assertNotIn("{Testable", result)
        self.assertIn("Real requirement", result)


class TestExtractDeniedPaths(unittest.TestCase):
    """Verify Non-Goals extraction as denied paths."""

    def test_extracts_non_goals(self):
        result = _extract_denied_paths(SAMPLE_ADR_WITH_CONTEXT)
        self.assertIn("Runtime persona switching", result)
        self.assertIn("Activation-space manipulation", result)

    def test_fallback_when_no_non_goals(self):
        result = _extract_denied_paths("# No non-goals here")
        self.assertIn("Paths not listed in Allowed Paths", result)

    def test_always_includes_catch_all(self):
        result = _extract_denied_paths(SAMPLE_ADR_WITH_CONTEXT)
        self.assertIn("Paths not listed in Allowed Paths", result)


if __name__ == "__main__":
    unittest.main()
