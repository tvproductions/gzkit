"""Unit tests for OBPI reviewer agent dispatch (ADR-0.23.0 / OBPI-0.23.0-03).

Tests cover: assessment models, prompt composition, result parsing,
artifact storage, and ceremony formatting.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.commands.pipeline import (
    ClosingArgumentQuality,
    DocsQuality,
    PromiseAssessment,
    ReviewerAssessment,
    compose_reviewer_prompt,
    format_reviewer_for_ceremony,
    parse_reviewer_assessment,
    store_reviewer_assessment,
)
from gzkit.roles import ReviewVerdict


class TestPromiseAssessment(unittest.TestCase):
    """PromiseAssessment model validation."""

    def test_create_met(self) -> None:
        pa = PromiseAssessment(requirement="REQ-1", met=True, evidence="Found in code")
        self.assertTrue(pa.met)
        self.assertEqual(pa.requirement, "REQ-1")

    def test_create_unmet(self) -> None:
        pa = PromiseAssessment(requirement="REQ-2", met=False)
        self.assertFalse(pa.met)
        self.assertEqual(pa.evidence, "")

    def test_frozen(self) -> None:
        pa = PromiseAssessment(requirement="REQ-1", met=True)
        with self.assertRaises(ValidationError):
            pa.met = False  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            PromiseAssessment(requirement="R", met=True, extra_field="bad")  # type: ignore[call-arg]


class TestReviewerAssessment(unittest.TestCase):
    """ReviewerAssessment model validation."""

    def _make_assessment(self, **overrides: object) -> ReviewerAssessment:
        defaults: dict[str, object] = {
            "obpi_id": "OBPI-0.23.0-03",
            "promises_met": [
                PromiseAssessment(requirement="REQ-1", met=True, evidence="code exists")
            ],
            "docs_quality": DocsQuality.SUBSTANTIVE,
            "docs_evidence": "Runbook updated",
            "closing_argument_quality": ClosingArgumentQuality.EARNED,
            "closing_argument_evidence": "Cites specific test output",
            "summary": "All promises met",
            "verdict": ReviewVerdict.PASS,
        }
        defaults.update(overrides)
        return ReviewerAssessment(**defaults)  # type: ignore[arg-type]

    def test_pass_verdict(self) -> None:
        a = self._make_assessment()
        self.assertEqual(a.verdict, ReviewVerdict.PASS)
        self.assertEqual(a.docs_quality, DocsQuality.SUBSTANTIVE)

    def test_fail_verdict(self) -> None:
        a = self._make_assessment(verdict=ReviewVerdict.FAIL)
        self.assertEqual(a.verdict, ReviewVerdict.FAIL)

    def test_concerns_verdict(self) -> None:
        a = self._make_assessment(verdict=ReviewVerdict.CONCERNS)
        self.assertEqual(a.verdict, ReviewVerdict.CONCERNS)

    def test_docs_quality_values(self) -> None:
        for quality in DocsQuality:
            a = self._make_assessment(docs_quality=quality)
            self.assertEqual(a.docs_quality, quality)

    def test_closing_argument_quality_values(self) -> None:
        for quality in ClosingArgumentQuality:
            a = self._make_assessment(closing_argument_quality=quality)
            self.assertEqual(a.closing_argument_quality, quality)

    def test_frozen(self) -> None:
        a = self._make_assessment()
        with self.assertRaises(ValidationError):
            a.verdict = ReviewVerdict.FAIL  # type: ignore[misc]

    def test_multiple_promises(self) -> None:
        promises = [
            PromiseAssessment(requirement="REQ-1", met=True, evidence="found"),
            PromiseAssessment(requirement="REQ-2", met=False, evidence="missing"),
            PromiseAssessment(requirement="REQ-3", met=True),
        ]
        a = self._make_assessment(promises_met=promises)
        self.assertEqual(len(a.promises_met), 3)
        self.assertFalse(a.promises_met[1].met)


class TestComposeReviewerPrompt(unittest.TestCase):
    """compose_reviewer_prompt() output validation."""

    def test_contains_obpi_id(self) -> None:
        prompt = compose_reviewer_prompt(
            "OBPI-0.23.0-03", "brief text", "closing text", ["f.py"], []
        )
        self.assertIn("OBPI-0.23.0-03", prompt)

    def test_contains_brief(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "## My Brief Content", "", ["f.py"], [])
        self.assertIn("## My Brief Content", prompt)

    def test_contains_closing_argument(self) -> None:
        prompt = compose_reviewer_prompt(
            "OBPI-1", "brief", "This work earned its closure", ["f.py"], []
        )
        self.assertIn("This work earned its closure", prompt)

    def test_missing_closing_argument(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "brief", "", ["f.py"], [])
        self.assertIn("No closing argument provided", prompt)

    def test_contains_changed_files(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "brief", "arg", ["src/a.py", "src/b.py"], [])
        self.assertIn("`src/a.py`", prompt)
        self.assertIn("`src/b.py`", prompt)

    def test_contains_doc_files(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "brief", "arg", ["f.py"], ["docs/runbook.md"])
        self.assertIn("`docs/runbook.md`", prompt)
        self.assertIn("Documentation Files", prompt)

    def test_no_doc_files_section_when_empty(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "brief", "arg", ["f.py"], [])
        self.assertNotIn("Documentation Files", prompt)

    def test_contains_json_schema(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "brief", "arg", ["f.py"], [])
        self.assertIn("promises_met", prompt)
        self.assertIn("docs_quality", prompt)
        self.assertIn("closing_argument_quality", prompt)

    def test_contains_assessment_criteria(self) -> None:
        prompt = compose_reviewer_prompt("OBPI-1", "brief", "arg", ["f.py"], [])
        self.assertIn("substantive", prompt)
        self.assertIn("boilerplate", prompt)
        self.assertIn("earned", prompt)
        self.assertIn("echoed", prompt)


class TestParseReviewerAssessment(unittest.TestCase):
    """parse_reviewer_assessment() extraction logic."""

    def _wrap_json(self, data: dict[str, object]) -> str:
        return f"Some text before\n```json\n{json.dumps(data)}\n```\nSome text after"

    def test_parse_valid_pass(self) -> None:
        data = {
            "promises_met": [{"requirement": "REQ-1", "met": True, "evidence": "code found"}],
            "docs_quality": "substantive",
            "docs_evidence": "Good docs",
            "closing_argument_quality": "earned",
            "closing_argument_evidence": "Real evidence",
            "summary": "All good",
            "verdict": "PASS",
        }
        result = parse_reviewer_assessment(self._wrap_json(data), "OBPI-0.23.0-03")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.verdict, ReviewVerdict.PASS)
        self.assertEqual(result.obpi_id, "OBPI-0.23.0-03")
        self.assertEqual(len(result.promises_met), 1)
        self.assertTrue(result.promises_met[0].met)

    def test_parse_valid_fail(self) -> None:
        data = {
            "promises_met": [{"requirement": "REQ-1", "met": False}],
            "docs_quality": "missing",
            "closing_argument_quality": "missing",
            "summary": "Nothing delivered",
            "verdict": "FAIL",
        }
        result = parse_reviewer_assessment(self._wrap_json(data), "OBPI-1")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.verdict, ReviewVerdict.FAIL)
        self.assertEqual(result.docs_quality, DocsQuality.MISSING)

    def test_parse_concerns(self) -> None:
        data = {
            "promises_met": [
                {"requirement": "REQ-1", "met": True, "evidence": "ok"},
                {"requirement": "REQ-2", "met": False, "evidence": "partial"},
            ],
            "docs_quality": "boilerplate",
            "closing_argument_quality": "echoed",
            "summary": "Minor gaps",
            "verdict": "CONCERNS",
        }
        result = parse_reviewer_assessment(self._wrap_json(data), "OBPI-1")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.verdict, ReviewVerdict.CONCERNS)
        self.assertEqual(result.closing_argument_quality, ClosingArgumentQuality.ECHOED)

    def test_parse_no_json(self) -> None:
        result = parse_reviewer_assessment("No JSON here", "OBPI-1")
        self.assertIsNone(result)

    def test_parse_invalid_json(self) -> None:
        result = parse_reviewer_assessment("```json\n{invalid}\n```", "OBPI-1")
        self.assertIsNone(result)

    def test_parse_missing_required_field(self) -> None:
        data = {"promises_met": [], "verdict": "PASS"}
        result = parse_reviewer_assessment(self._wrap_json(data), "OBPI-1")
        self.assertIsNone(result)

    def test_obpi_id_injected(self) -> None:
        data = {
            "promises_met": [{"requirement": "R1", "met": True}],
            "docs_quality": "substantive",
            "closing_argument_quality": "earned",
            "summary": "",
            "verdict": "PASS",
        }
        result = parse_reviewer_assessment(self._wrap_json(data), "MY-OBPI")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.obpi_id, "MY-OBPI")


class TestStoreReviewerAssessment(unittest.TestCase):
    """store_reviewer_assessment() artifact output."""

    def _make_assessment(self) -> ReviewerAssessment:
        return ReviewerAssessment(
            obpi_id="OBPI-0.23.0-03",
            promises_met=[
                PromiseAssessment(
                    requirement="Define reviewer role", met=True, evidence="In roles.py"
                ),
                PromiseAssessment(requirement="Store assessment artifact", met=True),
            ],
            docs_quality=DocsQuality.SUBSTANTIVE,
            docs_evidence="Runbook section added",
            closing_argument_quality=ClosingArgumentQuality.EARNED,
            closing_argument_evidence="Cites test results",
            summary="Implementation complete with strong evidence",
            verdict=ReviewVerdict.PASS,
        )

    def test_creates_artifact_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            path = store_reviewer_assessment(self._make_assessment(), adr_dir)
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "REVIEW-OBPI-0.23.0-03.md")

    def test_creates_briefs_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            store_reviewer_assessment(self._make_assessment(), adr_dir)
            self.assertTrue((adr_dir / "briefs").is_dir())

    def test_artifact_contains_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            path = store_reviewer_assessment(self._make_assessment(), adr_dir)
            content = path.read_text(encoding="utf-8")
            self.assertIn("**Verdict:** PASS", content)

    def test_artifact_contains_promises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            path = store_reviewer_assessment(self._make_assessment(), adr_dir)
            content = path.read_text(encoding="utf-8")
            self.assertIn("[YES]", content)
            self.assertIn("Define reviewer role", content)
            self.assertIn("In roles.py", content)

    def test_artifact_contains_docs_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            path = store_reviewer_assessment(self._make_assessment(), adr_dir)
            content = path.read_text(encoding="utf-8")
            self.assertIn("**Assessment:** substantive", content)
            self.assertIn("Runbook section added", content)

    def test_artifact_contains_closing_argument_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            path = store_reviewer_assessment(self._make_assessment(), adr_dir)
            content = path.read_text(encoding="utf-8")
            self.assertIn("**Assessment:** earned", content)

    def test_artifact_contains_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            path = store_reviewer_assessment(self._make_assessment(), adr_dir)
            content = path.read_text(encoding="utf-8")
            self.assertIn("Implementation complete with strong evidence", content)


class TestFormatReviewerForCeremony(unittest.TestCase):
    """format_reviewer_for_ceremony() output formatting."""

    def _make_assessment(self, **overrides: object) -> ReviewerAssessment:
        defaults: dict[str, object] = {
            "obpi_id": "OBPI-0.23.0-03",
            "promises_met": [
                PromiseAssessment(requirement="REQ-1", met=True, evidence="found"),
                PromiseAssessment(requirement="REQ-2", met=False, evidence="missing"),
            ],
            "docs_quality": DocsQuality.SUBSTANTIVE,
            "closing_argument_quality": ClosingArgumentQuality.EARNED,
            "summary": "Mostly good",
            "verdict": ReviewVerdict.CONCERNS,
        }
        defaults.update(overrides)
        return ReviewerAssessment(**defaults)  # type: ignore[arg-type]

    def test_contains_verdict(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment())
        self.assertIn("**CONCERNS**", output)

    def test_contains_table_header(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment())
        self.assertIn("| # | Requirement | Met | Evidence |", output)

    def test_contains_promise_rows(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment())
        self.assertIn("| 1 | REQ-1 | Yes | found |", output)
        self.assertIn("| 2 | REQ-2 | No | missing |", output)

    def test_contains_docs_quality(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment())
        self.assertIn("Documentation: **substantive**", output)

    def test_contains_closing_argument_quality(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment())
        self.assertIn("Closing argument: **earned**", output)

    def test_contains_summary(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment())
        self.assertIn("Summary: Mostly good", output)

    def test_pipe_escaped_in_table(self) -> None:
        a = self._make_assessment(
            promises_met=[
                PromiseAssessment(requirement="req|with|pipes", met=True, evidence="ev|pipe")
            ]
        )
        output = format_reviewer_for_ceremony(a)
        self.assertNotIn("req|with|pipes", output)
        self.assertIn("req\\|with\\|pipes", output)

    def test_pass_verdict_format(self) -> None:
        output = format_reviewer_for_ceremony(self._make_assessment(verdict=ReviewVerdict.PASS))
        self.assertIn("**PASS**", output)


if __name__ == "__main__":
    unittest.main()
