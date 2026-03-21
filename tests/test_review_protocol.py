"""Unit tests for the two-stage review protocol in pipeline_runtime.

Tests cover: review dispatch routing, model selection, prompt composition,
result parsing, critical finding detection, advancement blocking logic,
and the handle_review_cycle orchestration.
"""

from __future__ import annotations

import json
import unittest

from gzkit.pipeline_runtime import (
    MAX_REVIEW_FIX_CYCLES,
    REVIEW_MODEL_MAP,
    DispatchRecord,
    DispatchState,
    DispatchTask,
    TaskComplexity,
    TaskStatus,
    compose_quality_review_prompt,
    compose_spec_review_prompt,
    handle_review_cycle,
    parse_review_result,
    review_blocks_advancement,
    review_has_critical_findings,
    select_review_model,
    should_dispatch_review,
)
from gzkit.roles import (
    HandoffStatus,
    ReviewFinding,
    ReviewFindingSeverity,
    ReviewResult,
    ReviewVerdict,
)

# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_task(
    task_id: int = 1,
    description: str = "test task",
    allowed_paths: list[str] | None = None,
    test_expectations: list[str] | None = None,
    complexity: TaskComplexity = TaskComplexity.SIMPLE,
    model: str = "sonnet",
) -> DispatchTask:
    """Return a DispatchTask with sensible defaults."""
    return DispatchTask(
        task_id=task_id,
        description=description,
        allowed_paths=allowed_paths or ["src/gzkit/example.py"],
        test_expectations=test_expectations or [],
        complexity=complexity,
        model=model,
    )


def _make_finding(
    severity: ReviewFindingSeverity,
    file: str = "test.py",
    message: str = "test finding",
    line: int | None = None,
) -> ReviewFinding:
    """Return a ReviewFinding with specified severity."""
    return ReviewFinding(file=file, line=line, severity=severity, message=message)


def _make_review_result(
    verdict: ReviewVerdict,
    findings: list[ReviewFinding] | None = None,
    summary: str = "",
) -> ReviewResult:
    """Return a ReviewResult with specified verdict and optional findings."""
    return ReviewResult(verdict=verdict, findings=findings or [], summary=summary)


def _make_dispatch_state(num_tasks: int = 1) -> DispatchState:
    """Return a DispatchState with num_tasks records, all in DONE status."""
    records = []
    for i in range(1, num_tasks + 1):
        task = _make_task(task_id=i, description=f"Task {i}")
        records.append(DispatchRecord(task=task, status=TaskStatus.DONE))
    return DispatchState(obpi_id="OBPI-0.18.0-03", parent_adr="ADR-0.18.0", records=records)


# ---------------------------------------------------------------------------
# should_dispatch_review
# ---------------------------------------------------------------------------


class TestShouldDispatchReview(unittest.TestCase):
    """Table-driven tests for should_dispatch_review across all HandoffStatus values."""

    CASES = [
        ("DONE triggers review", HandoffStatus.DONE, True),
        ("DONE_WITH_CONCERNS triggers review", HandoffStatus.DONE_WITH_CONCERNS, True),
        ("BLOCKED does not trigger review", HandoffStatus.BLOCKED, False),
        ("NEEDS_CONTEXT does not trigger review", HandoffStatus.NEEDS_CONTEXT, False),
    ]

    def test_dispatch_review_routing(self):
        for label, status, expected in self.CASES:
            with self.subTest(label):
                self.assertEqual(should_dispatch_review(status), expected)

    def test_all_statuses_covered(self):
        """Every HandoffStatus must have an explicit routing decision."""
        for status in HandoffStatus:
            result = should_dispatch_review(status)
            self.assertIsInstance(result, bool)


# ---------------------------------------------------------------------------
# select_review_model
# ---------------------------------------------------------------------------


class TestSelectReviewModel(unittest.TestCase):
    """Verify review model routing — never haiku, COMPLEX uses opus."""

    CASES = [
        ("SIMPLE routes to sonnet", TaskComplexity.SIMPLE, "sonnet"),
        ("STANDARD routes to sonnet", TaskComplexity.STANDARD, "sonnet"),
        ("COMPLEX routes to opus", TaskComplexity.COMPLEX, "opus"),
    ]

    def test_model_routing(self):
        for label, complexity, expected in self.CASES:
            with self.subTest(label):
                self.assertEqual(select_review_model(complexity), expected)

    def test_never_routes_to_haiku(self):
        for complexity in TaskComplexity:
            with self.subTest(complexity):
                model = select_review_model(complexity)
                self.assertNotEqual(
                    model, "haiku", f"{complexity} should never route reviews to haiku"
                )

    def test_review_model_map_covers_all_complexity_levels(self):
        """REVIEW_MODEL_MAP must contain an entry for every TaskComplexity value."""
        for complexity in TaskComplexity:
            self.assertIn(complexity, REVIEW_MODEL_MAP)

    def test_select_review_model_matches_map(self):
        """select_review_model must return the same value as REVIEW_MODEL_MAP lookup."""
        for complexity in TaskComplexity:
            with self.subTest(complexity):
                self.assertEqual(select_review_model(complexity), REVIEW_MODEL_MAP[complexity])


# ---------------------------------------------------------------------------
# compose_spec_review_prompt
# ---------------------------------------------------------------------------


class TestComposeSpecReviewPrompt(unittest.TestCase):
    """Verify spec compliance review prompt content."""

    def _prompt(
        self,
        task: DispatchTask | None = None,
        brief_requirements: list[str] | None = None,
        files_changed: list[str] | None = None,
    ) -> str:
        t = task or _make_task(description="Implement the widget")
        return compose_spec_review_prompt(
            t,
            brief_requirements or [],
            files_changed or [],
        )

    def test_contains_task_description(self):
        task = _make_task(task_id=3, description="Implement the widget")
        prompt = self._prompt(task=task)
        self.assertIn("Implement the widget", prompt)

    def test_contains_task_id(self):
        task = _make_task(task_id=3, description="Implement the widget")
        prompt = self._prompt(task=task)
        self.assertIn("Task 3", prompt)

    def test_contains_skeptic_instruction(self):
        prompt = self._prompt()
        self.assertIn("The implementer may be optimistic. Verify everything independently.", prompt)

    def test_contains_brief_requirements(self):
        prompt = self._prompt(brief_requirements=["REQ-01: Must validate input", "REQ-02: Log it"])
        self.assertIn("REQ-01: Must validate input", prompt)
        self.assertIn("REQ-02: Log it", prompt)

    def test_contains_files_changed(self):
        prompt = self._prompt(files_changed=["src/gzkit/widget.py", "tests/test_widget.py"])
        self.assertIn("`src/gzkit/widget.py`", prompt)
        self.assertIn("`tests/test_widget.py`", prompt)

    def test_contains_json_result_format_instructions(self):
        prompt = self._prompt()
        self.assertIn("verdict", prompt)
        self.assertIn("findings", prompt)
        self.assertIn("summary", prompt)
        self.assertIn("PASS|FAIL|CONCERNS", prompt)

    def test_contains_severity_guide(self):
        prompt = self._prompt()
        self.assertIn("critical", prompt)
        self.assertIn("major", prompt)
        self.assertIn("minor", prompt)
        self.assertIn("info", prompt)

    def test_works_with_empty_brief_requirements(self):
        prompt = self._prompt(brief_requirements=[])
        self.assertIn("Verify everything independently.", prompt)
        self.assertNotIn("### Brief Requirements to Verify", prompt)

    def test_works_with_empty_files_changed(self):
        prompt = self._prompt(files_changed=[])
        # Should still produce a valid prompt without crashing
        self.assertIn("Spec Compliance Review", prompt)

    def test_returns_string(self):
        prompt = self._prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)


# ---------------------------------------------------------------------------
# compose_quality_review_prompt
# ---------------------------------------------------------------------------


class TestComposeQualityReviewPrompt(unittest.TestCase):
    """Verify code quality review prompt content."""

    def _prompt(
        self,
        files_changed: list[str] | None = None,
        test_files: list[str] | None = None,
    ) -> str:
        return compose_quality_review_prompt(
            files_changed if files_changed is not None else ["src/gzkit/widget.py"],
            test_files if test_files is not None else ["tests/test_widget.py"],
        )

    def test_contains_files_changed(self):
        prompt = self._prompt(files_changed=["src/gzkit/widget.py", "src/gzkit/helper.py"])
        self.assertIn("`src/gzkit/widget.py`", prompt)
        self.assertIn("`src/gzkit/helper.py`", prompt)

    def test_contains_test_files(self):
        prompt = self._prompt(test_files=["tests/test_widget.py"])
        self.assertIn("`tests/test_widget.py`", prompt)

    def test_contains_solid_criterion(self):
        prompt = self._prompt()
        self.assertIn("SOLID", prompt)

    def test_contains_size_limits_criterion(self):
        prompt = self._prompt()
        self.assertIn("Size limits", prompt)

    def test_contains_test_coverage_criterion(self):
        prompt = self._prompt()
        self.assertIn("Test coverage", prompt)

    def test_contains_error_handling_criterion(self):
        prompt = self._prompt()
        self.assertIn("Error handling", prompt)

    def test_contains_cross_platform_criterion(self):
        prompt = self._prompt()
        self.assertIn("Cross-platform", prompt)

    def test_contains_pydantic_criterion(self):
        prompt = self._prompt()
        self.assertIn("Pydantic", prompt)

    def test_contains_json_result_format_instructions(self):
        prompt = self._prompt()
        self.assertIn("verdict", prompt)
        self.assertIn("findings", prompt)
        self.assertIn("summary", prompt)
        self.assertIn("PASS|FAIL|CONCERNS", prompt)

    def test_works_with_empty_test_files(self):
        prompt = self._prompt(test_files=[])
        self.assertIn("Code Quality Review", prompt)
        self.assertNotIn("### Test Files to Review", prompt)

    def test_returns_string(self):
        prompt = self._prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)


# ---------------------------------------------------------------------------
# parse_review_result
# ---------------------------------------------------------------------------


def _json_block(obj: dict) -> str:
    """Wrap a dict as a JSON code block for output parsing tests."""
    return f"```json\n{json.dumps(obj)}\n```"


class TestParseReviewResult(unittest.TestCase):
    """Test extraction of ReviewResult from reviewer subagent output text."""

    def _review_json(
        self,
        verdict: str = "PASS",
        findings: list[dict] | None = None,
        summary: str = "All good",
    ) -> str:
        data = {
            "verdict": verdict,
            "findings": findings or [],
            "summary": summary,
        }
        return _json_block(data)

    def test_valid_pass_verdict(self):
        output = self._review_json("PASS", summary="Everything looks good")
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.verdict, ReviewVerdict.PASS)
        self.assertEqual(result.findings, [])
        self.assertEqual(result.summary, "Everything looks good")

    def test_valid_fail_verdict_with_findings(self):
        findings = [
            {"file": "src/a.py", "line": 42, "severity": "critical", "message": "Req not met"}
        ]
        output = self._review_json("FAIL", findings=findings, summary="Requirement gap")
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.verdict, ReviewVerdict.FAIL)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.CRITICAL)
        self.assertEqual(result.findings[0].file, "src/a.py")
        self.assertEqual(result.findings[0].line, 42)

    def test_valid_concerns_verdict(self):
        findings = [
            {"file": "src/b.py", "line": None, "severity": "major", "message": "Some gap"},
            {"file": "src/c.py", "line": 5, "severity": "minor", "message": "Style issue"},
        ]
        output = self._review_json("CONCERNS", findings=findings, summary="A few concerns")
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.verdict, ReviewVerdict.CONCERNS)
        self.assertEqual(len(result.findings), 2)

    def test_all_severity_levels_parsed(self):
        findings = [
            {"file": "f.py", "line": None, "severity": "critical", "message": "c"},
            {"file": "f.py", "line": None, "severity": "major", "message": "m"},
            {"file": "f.py", "line": None, "severity": "minor", "message": "mi"},
            {"file": "f.py", "line": None, "severity": "info", "message": "i"},
        ]
        output = self._review_json("CONCERNS", findings=findings)
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        severities = {f.severity for f in result.findings}
        self.assertEqual(
            severities,
            {
                ReviewFindingSeverity.CRITICAL,
                ReviewFindingSeverity.MAJOR,
                ReviewFindingSeverity.MINOR,
                ReviewFindingSeverity.INFO,
            },
        )

    def test_no_json_block_returns_none(self):
        self.assertIsNone(parse_review_result("No result here at all."))

    def test_invalid_json_returns_none(self):
        self.assertIsNone(parse_review_result("```json\n{bad: json here}\n```"))

    def test_json_with_wrong_fields_returns_none(self):
        # Missing required "verdict" field — should cause Pydantic validation error
        bad_data = _json_block({"result": "ok", "notes": "stuff"})
        self.assertIsNone(parse_review_result(bad_data))

    def test_multiple_json_blocks_uses_first(self):
        first = self._review_json("PASS", summary="first block")
        second = self._review_json("FAIL", summary="second block")
        output = f"Some text.\n{first}\nMore text.\n{second}\n"
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.verdict, ReviewVerdict.PASS)
        self.assertEqual(result.summary, "first block")

    def test_pass_with_no_findings_succeeds(self):
        output = self._review_json("PASS")
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.verdict, ReviewVerdict.PASS)
        self.assertEqual(result.findings, [])

    def test_result_embedded_in_prose(self):
        prose = (
            "I reviewed all the files carefully.\n\n"
            "Here is my verdict:\n\n"
            + self._review_json("PASS", summary="Clean implementation")
            + "\n\nEnd of review."
        )
        result = parse_review_result(prose)
        self.assertIsNotNone(result)
        self.assertEqual(result.verdict, ReviewVerdict.PASS)

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_review_result(""))


# ---------------------------------------------------------------------------
# review_has_critical_findings
# ---------------------------------------------------------------------------


class TestReviewHasCriticalFindings(unittest.TestCase):
    """Verify critical finding detection logic."""

    def test_no_findings_returns_false(self):
        result = _make_review_result(ReviewVerdict.PASS)
        self.assertFalse(review_has_critical_findings(result))

    def test_only_minor_findings_returns_false(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[_make_finding(ReviewFindingSeverity.MINOR)],
        )
        self.assertFalse(review_has_critical_findings(result))

    def test_only_major_findings_returns_false(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[_make_finding(ReviewFindingSeverity.MAJOR)],
        )
        self.assertFalse(review_has_critical_findings(result))

    def test_only_info_findings_returns_false(self):
        result = _make_review_result(
            ReviewVerdict.PASS,
            findings=[_make_finding(ReviewFindingSeverity.INFO)],
        )
        self.assertFalse(review_has_critical_findings(result))

    def test_one_critical_finding_returns_true(self):
        result = _make_review_result(
            ReviewVerdict.FAIL,
            findings=[_make_finding(ReviewFindingSeverity.CRITICAL)],
        )
        self.assertTrue(review_has_critical_findings(result))

    def test_mixed_with_one_critical_returns_true(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[
                _make_finding(ReviewFindingSeverity.MINOR),
                _make_finding(ReviewFindingSeverity.CRITICAL, message="deal breaker"),
                _make_finding(ReviewFindingSeverity.MAJOR),
            ],
        )
        self.assertTrue(review_has_critical_findings(result))

    def test_multiple_critical_findings_returns_true(self):
        result = _make_review_result(
            ReviewVerdict.FAIL,
            findings=[
                _make_finding(ReviewFindingSeverity.CRITICAL, file="a.py"),
                _make_finding(ReviewFindingSeverity.CRITICAL, file="b.py"),
            ],
        )
        self.assertTrue(review_has_critical_findings(result))


# ---------------------------------------------------------------------------
# review_blocks_advancement
# ---------------------------------------------------------------------------


class TestReviewBlocksAdvancement(unittest.TestCase):
    """Verify the advancement-blocking predicate covers all verdict/finding combos."""

    def test_fail_verdict_always_blocks(self):
        # FAIL with no findings
        result = _make_review_result(ReviewVerdict.FAIL)
        self.assertTrue(review_blocks_advancement(result))

    def test_fail_verdict_with_findings_blocks(self):
        result = _make_review_result(
            ReviewVerdict.FAIL,
            findings=[_make_finding(ReviewFindingSeverity.CRITICAL)],
        )
        self.assertTrue(review_blocks_advancement(result))

    def test_pass_verdict_never_blocks(self):
        result = _make_review_result(ReviewVerdict.PASS)
        self.assertFalse(review_blocks_advancement(result))

    def test_pass_verdict_with_findings_does_not_block(self):
        # Even PASS with info findings should not block
        result = _make_review_result(
            ReviewVerdict.PASS,
            findings=[_make_finding(ReviewFindingSeverity.INFO)],
        )
        self.assertFalse(review_blocks_advancement(result))

    def test_concerns_with_critical_finding_blocks(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[_make_finding(ReviewFindingSeverity.CRITICAL)],
        )
        self.assertTrue(review_blocks_advancement(result))

    def test_concerns_with_only_major_findings_does_not_block(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[_make_finding(ReviewFindingSeverity.MAJOR)],
        )
        self.assertFalse(review_blocks_advancement(result))

    def test_concerns_with_only_minor_findings_does_not_block(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[_make_finding(ReviewFindingSeverity.MINOR)],
        )
        self.assertFalse(review_blocks_advancement(result))

    def test_concerns_with_no_findings_does_not_block(self):
        result = _make_review_result(ReviewVerdict.CONCERNS)
        self.assertFalse(review_blocks_advancement(result))

    def test_concerns_mixed_major_minor_does_not_block(self):
        result = _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[
                _make_finding(ReviewFindingSeverity.MAJOR),
                _make_finding(ReviewFindingSeverity.MINOR),
            ],
        )
        self.assertFalse(review_blocks_advancement(result))


# ---------------------------------------------------------------------------
# handle_review_cycle
# ---------------------------------------------------------------------------


class TestHandleReviewCycle(unittest.TestCase):
    """Orchestration tests for handle_review_cycle."""

    def _passing_spec(self) -> ReviewResult:
        return _make_review_result(ReviewVerdict.PASS, summary="Spec satisfied")

    def _passing_quality(self) -> ReviewResult:
        return _make_review_result(ReviewVerdict.PASS, summary="Quality ok")

    def _blocking_spec(self) -> ReviewResult:
        return _make_review_result(
            ReviewVerdict.FAIL,
            findings=[_make_finding(ReviewFindingSeverity.CRITICAL, message="Missing req")],
            summary="Spec failed",
        )

    def _blocking_quality(self) -> ReviewResult:
        return _make_review_result(
            ReviewVerdict.FAIL,
            findings=[_make_finding(ReviewFindingSeverity.CRITICAL, message="Bad code")],
            summary="Quality failed",
        )

    def _concerns_only_spec(self) -> ReviewResult:
        """CONCERNS verdict with only minor findings — does not block."""
        return _make_review_result(
            ReviewVerdict.CONCERNS,
            findings=[_make_finding(ReviewFindingSeverity.MINOR, message="Small style issue")],
            summary="Minor concerns only",
        )

    # -----------------------------------------------------------------------
    # Advancement paths
    # -----------------------------------------------------------------------

    def test_spec_passes_no_quality_result_advances(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 0, self._passing_spec(), None)
        self.assertEqual(action, "advance")

    def test_spec_passes_quality_passes_advances(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 0, self._passing_spec(), self._passing_quality())
        self.assertEqual(action, "advance")

    def test_spec_concerns_only_no_critical_advances_to_quality_check(self):
        """CONCERNS spec (non-critical) should not block — quality review then proceeds."""
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 0, self._concerns_only_spec(), self._passing_quality())
        self.assertEqual(action, "advance")

    def test_spec_concerns_only_no_quality_result_advances(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 0, self._concerns_only_spec(), None)
        self.assertEqual(action, "advance")

    # -----------------------------------------------------------------------
    # Fix paths
    # -----------------------------------------------------------------------

    def test_spec_fails_critical_returns_fix_on_first_cycle(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 0, self._blocking_spec(), None)
        self.assertEqual(action, "fix")

    def test_quality_fails_critical_returns_fix_on_first_cycle(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 0, self._passing_spec(), self._blocking_quality())
        self.assertEqual(action, "fix")

    # -----------------------------------------------------------------------
    # Blocked paths (MAX_REVIEW_FIX_CYCLES exceeded)
    # -----------------------------------------------------------------------

    def test_spec_fails_after_max_cycles_returns_blocked(self):
        state = _make_dispatch_state(num_tasks=1)
        # Pre-fill review_fix_count to the maximum
        state.records[0].review_fix_count = MAX_REVIEW_FIX_CYCLES
        action = handle_review_cycle(state, 0, self._blocking_spec(), None)
        self.assertEqual(action, "blocked")

    def test_quality_fails_after_max_cycles_returns_blocked(self):
        state = _make_dispatch_state(num_tasks=1)
        state.records[0].review_fix_count = MAX_REVIEW_FIX_CYCLES
        action = handle_review_cycle(state, 0, self._passing_spec(), self._blocking_quality())
        self.assertEqual(action, "blocked")

    # -----------------------------------------------------------------------
    # Fix-count increment behaviour
    # -----------------------------------------------------------------------

    def test_spec_fail_increments_review_fix_count(self):
        state = _make_dispatch_state(num_tasks=1)
        self.assertEqual(state.records[0].review_fix_count, 0)
        handle_review_cycle(state, 0, self._blocking_spec(), None)
        self.assertEqual(state.records[0].review_fix_count, 1)

    def test_quality_fail_increments_review_fix_count(self):
        state = _make_dispatch_state(num_tasks=1)
        self.assertEqual(state.records[0].review_fix_count, 0)
        handle_review_cycle(state, 0, self._passing_spec(), self._blocking_quality())
        self.assertEqual(state.records[0].review_fix_count, 1)

    def test_review_fix_count_increments_across_repeated_calls(self):
        state = _make_dispatch_state(num_tasks=1)
        handle_review_cycle(state, 0, self._blocking_spec(), None)  # count → 1, returns "fix"
        handle_review_cycle(state, 0, self._blocking_spec(), None)  # count → 2, returns "fix"
        self.assertEqual(state.records[0].review_fix_count, 2)

    def test_advance_does_not_increment_review_fix_count(self):
        state = _make_dispatch_state(num_tasks=1)
        handle_review_cycle(state, 0, self._passing_spec(), self._passing_quality())
        self.assertEqual(state.records[0].review_fix_count, 0)

    # -----------------------------------------------------------------------
    # Invalid index
    # -----------------------------------------------------------------------

    def test_invalid_task_index_negative_returns_blocked(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, -1, self._passing_spec(), None)
        self.assertEqual(action, "blocked")

    def test_invalid_task_index_out_of_bounds_returns_blocked(self):
        state = _make_dispatch_state(num_tasks=1)
        action = handle_review_cycle(state, 99, self._passing_spec(), None)
        self.assertEqual(action, "blocked")

    # -----------------------------------------------------------------------
    # Multi-task state (only the targeted record is affected)
    # -----------------------------------------------------------------------

    def test_only_targeted_record_review_fix_count_changes(self):
        state = _make_dispatch_state(num_tasks=3)
        handle_review_cycle(state, 1, self._blocking_spec(), None)
        self.assertEqual(state.records[0].review_fix_count, 0)
        self.assertEqual(state.records[1].review_fix_count, 1)
        self.assertEqual(state.records[2].review_fix_count, 0)

    # -----------------------------------------------------------------------
    # MAX_REVIEW_FIX_CYCLES constant sanity check
    # -----------------------------------------------------------------------

    def test_max_review_fix_cycles_is_positive_int(self):
        self.assertIsInstance(MAX_REVIEW_FIX_CYCLES, int)
        self.assertGreater(MAX_REVIEW_FIX_CYCLES, 0)


if __name__ == "__main__":
    unittest.main()
