"""Tests for gzkit interview module."""

import unittest

from gzkit.interview import (
    check_interview_complete,
    format_answers_for_template,
    get_interview_questions,
    validate_answer,
)


class TestGetInterviewQuestions(unittest.TestCase):
    """Tests for getting interview questions."""

    def test_prd_questions(self) -> None:
        """Gets PRD interview questions."""
        questions = get_interview_questions("prd")
        self.assertTrue(len(questions) > 0)
        ids = [q.id for q in questions]
        self.assertIn("id", ids)
        self.assertIn("problem_statement", ids)

    def test_adr_questions(self) -> None:
        """Gets ADR interview questions."""
        questions = get_interview_questions("adr")
        self.assertTrue(len(questions) > 0)
        ids = [q.id for q in questions]
        self.assertIn("id", ids)
        self.assertIn("intent", ids)
        self.assertIn("decision", ids)

    def test_brief_questions(self) -> None:
        """Gets brief interview questions."""
        questions = get_interview_questions("brief")
        self.assertTrue(len(questions) > 0)
        ids = [q.id for q in questions]
        self.assertIn("id", ids)
        self.assertIn("objective", ids)

    def test_unknown_type_raises(self) -> None:
        """Unknown document type raises ValueError."""
        with self.assertRaises(ValueError):
            get_interview_questions("unknown")


class TestValidateAnswer(unittest.TestCase):
    """Tests for answer validation."""

    def test_required_empty_fails(self) -> None:
        """Empty answer fails for required question."""
        questions = get_interview_questions("prd")
        id_question = next(q for q in questions if q.id == "id")
        self.assertFalse(validate_answer(id_question, ""))

    def test_required_filled_passes(self) -> None:
        """Filled answer passes for required question."""
        questions = get_interview_questions("prd")
        id_question = next(q for q in questions if q.id == "id")
        self.assertTrue(validate_answer(id_question, "PRD-TEST-1.0.0"))

    def test_custom_validator(self) -> None:
        """Custom validator is applied."""
        questions = get_interview_questions("adr")
        lane_question = next(q for q in questions if q.id == "lane")
        self.assertTrue(validate_answer(lane_question, "lite"))
        self.assertTrue(validate_answer(lane_question, "heavy"))
        self.assertFalse(validate_answer(lane_question, "invalid"))


class TestCheckInterviewComplete(unittest.TestCase):
    """Tests for interview completion checking."""

    def test_incomplete_interview(self) -> None:
        """Incomplete interview returns missing fields."""
        answers = {"id": "PRD-TEST"}  # Missing most fields
        result = check_interview_complete("prd", answers)
        self.assertFalse(result.complete)
        self.assertTrue(len(result.missing) > 0)

    def test_complete_interview(self) -> None:
        """Complete interview has no missing fields."""
        answers = {
            "id": "PRD-TEST-1.0.0",
            "title": "Test PRD",
            "semver": "1.0.0",
            "problem_statement": "Test problem",
            "north_star": "Test goal",
            "invariants": "Test invariants",
            "out_of_scope": "Test out of scope",
        }
        result = check_interview_complete("prd", answers)
        self.assertTrue(result.complete)
        self.assertEqual(result.missing, [])


class TestFormatAnswersForTemplate(unittest.TestCase):
    """Tests for formatting answers."""

    def test_adr_lane_lowercase(self) -> None:
        """ADR lane is lowercased."""
        answers = {"lane": "LITE"}
        formatted = format_answers_for_template("adr", answers)
        self.assertEqual(formatted["lane"], "lite")

    def test_brief_gate_requirements(self) -> None:
        """Brief sets gate requirements based on lane."""
        answers_lite = {"lane": "lite"}
        formatted_lite = format_answers_for_template("brief", answers_lite)
        self.assertEqual(formatted_lite["docs_required"], "No")
        self.assertEqual(formatted_lite["bdd_required"], "No")

        answers_heavy = {"lane": "heavy"}
        formatted_heavy = format_answers_for_template("brief", answers_heavy)
        self.assertEqual(formatted_heavy["docs_required"], "Yes")
        self.assertEqual(formatted_heavy["bdd_required"], "Yes")


if __name__ == "__main__":
    unittest.main()
