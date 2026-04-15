"""Tests for closeout ceremony enforcement (ADR-0.23.0 / OBPI-0.23.0-04).

Tests the Defense Brief rendering, closing argument extraction,
reviewer assessment gathering, and ceremony readiness logic.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.closeout_form import _render_adr_closeout_form
from gzkit.commands.common import (
    _extract_review_verdict,
    compute_defense_brief,
    extract_closing_argument,
    gather_reviewer_assessments,
    render_defense_brief_section,
)
from gzkit.quality import ObpiProofStatus, ProductProofResult
from gzkit.traceability import covers


class TestExtractClosingArgument(unittest.TestCase):
    """Tests for extract_closing_argument()."""

    @covers("REQ-0.23.0-04-01")
    def test_extracts_closing_argument(self):
        brief = (
            "# OBPI-0.1.0-01\n\n"
            "## OBJECTIVE\n\nDo something.\n\n"
            "## Closing Argument\n\n"
            "1. **What was built** -- the thing.\n\n"
            "2. **What it enables** -- capability.\n\n"
            "### Implementation Summary\n\n- done\n"
        )
        result = extract_closing_argument(brief)
        self.assertIsNotNone(result)
        self.assertIn("What was built", result)
        self.assertIn("What it enables", result)
        self.assertNotIn("Implementation Summary", result)

    @covers("REQ-0.23.0-04-04")
    def test_returns_none_when_missing(self):
        brief = "# OBPI-0.1.0-01\n\n## OBJECTIVE\n\nDo something.\n"
        result = extract_closing_argument(brief)
        self.assertIsNone(result)

    @covers("REQ-0.23.0-04-04")
    def test_returns_none_for_placeholder(self):
        brief = "## Closing Argument\n\n*To be authored at completion from delivered evidence.*\n"
        result = extract_closing_argument(brief)
        self.assertIsNone(result)

    @covers("REQ-0.23.0-04-01")
    def test_stops_at_next_h2(self):
        brief = (
            "## Closing Argument\n\nArgument text here.\n\n## Quality Gates\n\nSomething else.\n"
        )
        result = extract_closing_argument(brief)
        self.assertEqual(result, "Argument text here.")

    @covers("REQ-0.23.0-04-01")
    def test_stops_at_key_proof(self):
        brief = "## Closing Argument\n\nArgument text.\n\n### Key Proof\n\nSome proof.\n"
        result = extract_closing_argument(brief)
        self.assertEqual(result, "Argument text.")

    @covers("REQ-0.23.0-04-04")
    def test_returns_none_for_empty_section(self):
        brief = "## Closing Argument\n\n## Next Section\n"
        result = extract_closing_argument(brief)
        self.assertIsNone(result)


class TestGatherReviewerAssessments(unittest.TestCase):
    """Tests for gather_reviewer_assessments()."""

    @covers("REQ-0.23.0-03-09")
    def test_finds_reviews_in_briefs_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            briefs_dir = adr_dir / "briefs"
            briefs_dir.mkdir()
            review = briefs_dir / "REVIEW-OBPI-0.1.0-01-feature.md"
            review.write_text("**Verdict:** PASS\n", encoding="utf-8")

            result = gather_reviewer_assessments(adr_dir)
            self.assertIn("OBPI-0.1.0-01-feature", result)
            self.assertEqual(result["OBPI-0.1.0-01-feature"], review)

    @covers("REQ-0.23.0-03-09")
    def test_finds_reviews_in_obpis_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir()
            review = obpis_dir / "REVIEW-OBPI-0.1.0-02-other.md"
            review.write_text("**Verdict:** CONCERNS\n", encoding="utf-8")

            result = gather_reviewer_assessments(adr_dir)
            self.assertIn("OBPI-0.1.0-02-other", result)

    @covers("REQ-0.23.0-03-09")
    def test_returns_empty_when_no_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = gather_reviewer_assessments(Path(tmp))
            self.assertEqual(result, {})

    @covers("REQ-0.23.0-03-09")
    def test_returns_empty_when_dir_missing(self):
        result = gather_reviewer_assessments(Path("/nonexistent/path"))
        self.assertEqual(result, {})


class TestExtractReviewVerdict(unittest.TestCase):
    """Tests for _extract_review_verdict()."""

    @covers("REQ-0.23.0-04-03")
    def test_extracts_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REVIEW.md"
            path.write_text("# Review\n\n**Verdict:** PASS\n", encoding="utf-8")
            self.assertEqual(_extract_review_verdict(path), "PASS")

    @covers("REQ-0.23.0-04-03")
    def test_extracts_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REVIEW.md"
            path.write_text("**Verdict:** FAIL\n", encoding="utf-8")
            self.assertEqual(_extract_review_verdict(path), "FAIL")

    @covers("REQ-0.23.0-04-03")
    def test_returns_unknown_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REVIEW.md"
            path.write_text("# No verdict here\n", encoding="utf-8")
            self.assertEqual(_extract_review_verdict(path), "unknown")


class TestExtractReviewFields(unittest.TestCase):
    """Tests for _extract_review_fields() structured extraction."""

    def _write_review(self, tmp: str) -> Path:
        path = Path(tmp) / "REVIEW.md"
        path.write_text(
            "\n".join(
                [
                    "# Reviewer Assessment: OBPI-0.1.0-01",
                    "",
                    "**Verdict:** PASS",
                    "",
                    "## Promises Met",
                    "",
                    "1. **[YES]** Feature works",
                    "2. **[YES]** Tests pass",
                    "3. **[NO]** Missing edge case",
                    "",
                    "## Documentation Quality",
                    "",
                    "**Assessment:** substantive",
                    "",
                    "## Closing Argument Quality",
                    "",
                    "**Assessment:** earned",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    @covers("REQ-0.23.0-04-03")
    def test_extracts_all_fields(self):
        from gzkit.commands.common import _extract_review_fields

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_review(tmp)
            fields = _extract_review_fields(path)
            self.assertEqual(fields["verdict"], "PASS")
            self.assertEqual(fields["docs_quality"], "substantive")
            self.assertEqual(fields["closing_argument_quality"], "earned")
            self.assertEqual(fields["promises_met"], "2/3")

    @covers("REQ-0.23.0-04-03")
    def test_handles_no_promises(self):
        from gzkit.commands.common import _extract_review_fields

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REVIEW.md"
            path.write_text("**Verdict:** CONCERNS\n", encoding="utf-8")
            fields = _extract_review_fields(path)
            self.assertEqual(fields["verdict"], "CONCERNS")
            self.assertEqual(fields["promises_met"], "n/a")


class TestRenderDefenseBriefSection(unittest.TestCase):
    """Tests for render_defense_brief_section()."""

    @covers("REQ-0.23.0-04-01")
    def test_renders_closing_arguments(self):
        args = {"OBPI-0.1.0-01": "Built the thing.", "OBPI-0.1.0-02": "Built another."}
        result = render_defense_brief_section(args, None, {})
        self.assertIn("## Defense Brief", result)
        self.assertIn("### Closing Arguments", result)
        self.assertIn("#### OBPI-0.1.0-01", result)
        self.assertIn("Built the thing.", result)

    @covers("REQ-0.23.0-04-04")
    def test_renders_no_closing_arguments(self):
        result = render_defense_brief_section({}, None, {})
        self.assertIn("*No closing arguments found.*", result)

    @covers("REQ-0.23.0-04-02")
    def test_renders_product_proof_table(self):
        proof = ProductProofResult(
            adr_id="ADR-0.1.0",
            success=True,
            obpi_proofs=[
                ObpiProofStatus(
                    obpi_id="OBPI-0.1.0-01",
                    docstring_found=True,
                ),
            ],
            missing_count=0,
        )
        result = render_defense_brief_section({}, proof, {})
        self.assertIn("### Product Proof", result)
        self.assertIn("OBPI-0.1.0-01", result)
        self.assertIn("FOUND", result)

    @covers("REQ-0.23.0-04-05")
    def test_renders_missing_product_proof(self):
        proof = ProductProofResult(
            adr_id="ADR-0.1.0",
            success=False,
            obpi_proofs=[
                ObpiProofStatus(obpi_id="OBPI-0.1.0-01"),
            ],
            missing_count=1,
        )
        result = render_defense_brief_section({}, proof, {})
        self.assertIn("MISSING", result)

    @covers("REQ-0.23.0-04-03")
    def test_renders_reviewer_table_with_structured_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            review_path = Path(tmp) / "REVIEW-OBPI-0.1.0-01.md"
            review_path.write_text(
                "**Verdict:** PASS\n\n"
                "## Promises Met\n\n1. **[YES]** Works\n\n"
                "## Documentation Quality\n\n**Assessment:** substantive\n\n"
                "## Closing Argument Quality\n\n**Assessment:** earned\n",
                encoding="utf-8",
            )
            reviews = {"OBPI-0.1.0-01": review_path}
            result = render_defense_brief_section({}, None, reviews)
            self.assertIn("### Reviewer Assessment", result)
            self.assertIn("PASS", result)
            self.assertIn("Promises Met", result)
            self.assertIn("Docs Quality", result)
            self.assertIn("substantive", result)
            self.assertIn("earned", result)

    @covers("REQ-0.23.0-04-06")
    def test_renders_no_reviewer(self):
        result = render_defense_brief_section({}, None, {})
        self.assertIn("*No reviewer assessments found.*", result)


class TestComputeDefenseBrief(unittest.TestCase):
    """Tests for compute_defense_brief()."""

    @covers("REQ-0.23.0-04-01")
    @covers("REQ-0.23.0-04-03")
    def test_computes_from_briefs_and_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp) / "adr-pkg"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)

            brief = obpis_dir / "OBPI-0.1.0-01-feat.md"
            brief.write_text(
                "# OBPI\n\n## Closing Argument\n\nWe built it.\n\n"
                "### Implementation Summary\n\n- done\n",
                encoding="utf-8",
            )

            review = obpis_dir / "REVIEW-OBPI-0.1.0-01-feat.md"
            review.write_text("**Verdict:** PASS\n", encoding="utf-8")

            obpi_files = {"OBPI-0.1.0-01-feat": brief}
            result = compute_defense_brief(obpi_files, adr_dir, None)
            self.assertIn("We built it.", result)
            self.assertIn("PASS", result)


class TestCloseoutFormDefenseBrief(unittest.TestCase):
    """Tests for Defense Brief integration in ADR-CLOSEOUT-FORM.md."""

    @covers("REQ-0.23.0-04-07")
    def test_form_includes_defense_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            adr_file = project_root / "docs" / "adr" / "ADR-0.1.0.md"
            adr_file.parent.mkdir(parents=True)
            adr_file.write_text("# ADR\n", encoding="utf-8")

            defense = "## Defense Brief\n\n### Closing Arguments\n\nGreat work.\n"
            form = _render_adr_closeout_form(
                project_root,
                "ADR-0.1.0",
                adr_file,
                [],
                [],
                {},
                attestation_command="uv run gz closeout ADR-0.1.0",
                defense_brief=defense,
            )
            self.assertIn("## Defense Brief", form)
            self.assertIn("Great work.", form)
            # Defense Brief should appear before Human Attestation
            brief_idx = form.index("## Defense Brief")
            attest_idx = form.index("## Human Attestation")
            self.assertLess(brief_idx, attest_idx)

    @covers("REQ-0.23.0-04-07")
    def test_form_without_defense_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            adr_file = project_root / "docs" / "adr" / "ADR-0.1.0.md"
            adr_file.parent.mkdir(parents=True)
            adr_file.write_text("# ADR\n", encoding="utf-8")

            form = _render_adr_closeout_form(
                project_root,
                "ADR-0.1.0",
                adr_file,
                [],
                [],
                {},
                attestation_command="uv run gz closeout ADR-0.1.0",
            )
            self.assertNotIn("## Defense Brief", form)
            self.assertIn("## Human Attestation", form)


if __name__ == "__main__":
    unittest.main()
