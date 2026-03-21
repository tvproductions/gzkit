"""Unit tests for subagent dispatch orchestration in pipeline_runtime.

Tests cover: complexity classification, model routing, prompt composition,
result parsing, dispatch state management, and edge cases.
"""

from __future__ import annotations

import unittest

from gzkit.pipeline_runtime import (
    DISPATCH_MODEL_MAP,
    MAX_BLOCKED_FIX_ATTEMPTS,
    MAX_NEEDS_CONTEXT_RETRIES,
    DispatchRecord,
    DispatchState,
    DispatchTask,
    TaskComplexity,
    TaskStatus,
    advance_dispatch,
    classify_task_complexity,
    compose_implementer_prompt,
    create_dispatch_state,
    extract_plan_tasks,
    handle_task_result,
    parse_handoff_result,
    select_dispatch_model,
)
from gzkit.roles import (
    HandoffResult,
    HandoffStatus,
)

# ---------------------------------------------------------------------------
# Task complexity classification
# ---------------------------------------------------------------------------


class TestClassifyTaskComplexity(unittest.TestCase):
    """Table-driven tests for classify_task_complexity."""

    CASES = [
        ("no files", [], TaskComplexity.SIMPLE),
        ("1 file", ["src/a.py"], TaskComplexity.SIMPLE),
        ("2 files", ["src/a.py", "src/b.py"], TaskComplexity.SIMPLE),
        ("3 files", ["a.py", "b.py", "c.py"], TaskComplexity.STANDARD),
        ("5 files", [f"f{i}.py" for i in range(5)], TaskComplexity.STANDARD),
        ("6 files", [f"f{i}.py" for i in range(6)], TaskComplexity.COMPLEX),
        ("10 files", [f"f{i}.py" for i in range(10)], TaskComplexity.COMPLEX),
    ]

    def test_complexity_levels(self):
        for label, paths, expected in self.CASES:
            with self.subTest(label):
                result = classify_task_complexity("some task", paths)
                self.assertEqual(result, expected)


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------


class TestSelectDispatchModel(unittest.TestCase):
    """Verify model routing map covers all complexity levels."""

    def test_all_complexities_mapped(self):
        for complexity in TaskComplexity:
            model = select_dispatch_model(complexity)
            self.assertIn(model, {"haiku", "sonnet", "opus"})
            self.assertEqual(model, DISPATCH_MODEL_MAP[complexity])

    def test_simple_routes_to_haiku(self):
        self.assertEqual(select_dispatch_model(TaskComplexity.SIMPLE), "haiku")

    def test_standard_routes_to_sonnet(self):
        self.assertEqual(select_dispatch_model(TaskComplexity.STANDARD), "sonnet")

    def test_complex_routes_to_opus(self):
        self.assertEqual(select_dispatch_model(TaskComplexity.COMPLEX), "opus")


# ---------------------------------------------------------------------------
# Plan task extraction
# ---------------------------------------------------------------------------


class TestExtractPlanTasks(unittest.TestCase):
    """Test plan markdown parsing into task dicts."""

    def test_heading_format(self):
        plan = "## Task 1: Add the model\n## Task 2: Write tests\n"
        tasks = extract_plan_tasks(plan)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "1")
        self.assertEqual(tasks[0]["description"], "Add the model")
        self.assertEqual(tasks[1]["id"], "2")

    def test_numbered_list_format(self):
        plan = "1. Add the model\n2. Write tests\n3. Update docs\n"
        tasks = extract_plan_tasks(plan)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["description"], "Add the model")
        self.assertEqual(tasks[2]["description"], "Update docs")

    def test_empty_plan(self):
        self.assertEqual(extract_plan_tasks(""), [])
        self.assertEqual(extract_plan_tasks("Some intro text\n"), [])

    def test_h3_step_format(self):
        plan = "### Step 1: First thing\n### Step 2: Second thing\n"
        tasks = extract_plan_tasks(plan)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["description"], "First thing")

    def test_mixed_content_extracts_tasks(self):
        plan = "# Plan\nSome preamble.\n## Task 1: Do it\nDetails here.\n## Task 2: Test it\n"
        tasks = extract_plan_tasks(plan)
        self.assertEqual(len(tasks), 2)


# ---------------------------------------------------------------------------
# Prompt composition
# ---------------------------------------------------------------------------


class TestComposeImplementerPrompt(unittest.TestCase):
    """Verify implementer prompt structure."""

    def _make_task(self, **overrides):
        defaults = {
            "task_id": 1,
            "description": "Add feature X",
            "allowed_paths": ["src/gzkit/example.py"],
            "test_expectations": ["test_feature_x passes"],
            "complexity": TaskComplexity.SIMPLE,
            "model": "haiku",
        }
        defaults.update(overrides)
        return DispatchTask(**defaults)

    def test_contains_task_heading(self):
        task = self._make_task()
        prompt = compose_implementer_prompt(task, [])
        self.assertIn("## Task 1: Add feature X", prompt)

    def test_contains_allowed_files(self):
        task = self._make_task(allowed_paths=["src/a.py", "src/b.py"])
        prompt = compose_implementer_prompt(task, [])
        self.assertIn("`src/a.py`", prompt)
        self.assertIn("`src/b.py`", prompt)

    def test_contains_test_expectations(self):
        task = self._make_task(test_expectations=["test_x passes", "test_y passes"])
        prompt = compose_implementer_prompt(task, [])
        self.assertIn("test_x passes", prompt)

    def test_contains_brief_requirements(self):
        task = self._make_task()
        prompt = compose_implementer_prompt(task, ["REQ-01: Must validate input"])
        self.assertIn("REQ-01: Must validate input", prompt)

    def test_contains_rules_section(self):
        task = self._make_task()
        prompt = compose_implementer_prompt(task, [])
        self.assertIn("### Rules", prompt)
        self.assertIn("Return a JSON result block", prompt)

    def test_extra_context_included(self):
        task = self._make_task()
        prompt = compose_implementer_prompt(task, [], extra_context="Prior task changed X")
        self.assertIn("Prior task changed X", prompt)

    def test_no_extra_context_section_when_empty(self):
        task = self._make_task()
        prompt = compose_implementer_prompt(task, [])
        self.assertNotIn("### Additional Context", prompt)


# ---------------------------------------------------------------------------
# Result parsing
# ---------------------------------------------------------------------------


class TestParseHandoffResult(unittest.TestCase):
    """Test extraction of HandoffResult from agent output text."""

    def _json_block(self, obj_str: str) -> str:
        return f"```json\n{obj_str}\n```"

    def _result_json(self, status: str, **kw) -> str:
        import json

        data = {
            "status": status,
            "files_changed": kw.get("files_changed", []),
            "tests_added": kw.get("tests_added", []),
            "concerns": kw.get("concerns", []),
        }
        return self._json_block(json.dumps(data))

    def test_valid_done_result(self):
        output = f"Some text\n{self._result_json('DONE', files_changed=['a.py'])}\nMore"
        result = parse_handoff_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, HandoffStatus.DONE)
        self.assertEqual(result.files_changed, ["a.py"])

    def test_done_with_concerns(self):
        output = self._result_json("DONE_WITH_CONCERNS", concerns=["might break X"])
        result = parse_handoff_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, HandoffStatus.DONE_WITH_CONCERNS)
        self.assertEqual(result.concerns, ["might break X"])

    def test_blocked_result(self):
        output = self._result_json("BLOCKED", concerns=["missing dep"])
        result = parse_handoff_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, HandoffStatus.BLOCKED)

    def test_needs_context_result(self):
        output = self._result_json("NEEDS_CONTEXT", concerns=["need schema"])
        result = parse_handoff_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, HandoffStatus.NEEDS_CONTEXT)

    def test_no_json_block_returns_none(self):
        self.assertIsNone(parse_handoff_result("No result here"))

    def test_invalid_json_returns_none(self):
        self.assertIsNone(parse_handoff_result("```json\n{bad json}\n```"))

    def test_invalid_status_returns_none(self):
        output = self._result_json("INVALID")
        self.assertIsNone(parse_handoff_result(output))


# ---------------------------------------------------------------------------
# Dispatch state management
# ---------------------------------------------------------------------------


class TestCreateDispatchState(unittest.TestCase):
    """Test dispatch state creation from plan tasks."""

    def test_creates_records_for_each_task(self):
        tasks = [{"id": "1", "description": "First"}, {"id": "2", "description": "Second"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["src/a.py"])
        self.assertEqual(len(state.records), 2)
        self.assertEqual(state.records[0].task.task_id, 1)
        self.assertEqual(state.records[1].task.task_id, 2)

    def test_all_records_start_pending(self):
        tasks = [{"id": "1", "description": "First"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        self.assertEqual(state.records[0].status, TaskStatus.PENDING)

    def test_empty_tasks_creates_empty_state(self):
        state = create_dispatch_state("OBPI-X", "ADR-X", [], ["a.py"])
        self.assertEqual(len(state.records), 0)
        self.assertTrue(state.is_finished)

    def test_complexity_and_model_assigned(self):
        tasks = [{"id": "1", "description": "Task"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py", "b.py"])
        self.assertEqual(state.records[0].task.complexity, TaskComplexity.SIMPLE)
        self.assertEqual(state.records[0].task.model, "haiku")

    def test_test_expectations_propagated(self):
        tasks = [{"id": "1", "description": "Task"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"], ["test_x passes"])
        self.assertEqual(state.records[0].task.test_expectations, ["test_x passes"])


class TestDispatchStateProperties(unittest.TestCase):
    """Test DispatchState computed properties."""

    def _make_state(self, statuses):
        records = []
        for i, status in enumerate(statuses, 1):
            task = DispatchTask(
                task_id=i,
                description=f"Task {i}",
                allowed_paths=["a.py"],
                complexity=TaskComplexity.SIMPLE,
                model="haiku",
            )
            records.append(DispatchRecord(task=task, status=status))
        return DispatchState(obpi_id="OBPI-X", parent_adr="ADR-X", records=records)

    def test_current_index_first_pending(self):
        state = self._make_state([TaskStatus.DONE, TaskStatus.PENDING, TaskStatus.PENDING])
        self.assertEqual(state.current_index, 1)

    def test_current_index_all_done(self):
        state = self._make_state([TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS])
        self.assertEqual(state.current_index, 2)

    def test_completed_count(self):
        state = self._make_state(
            [TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS, TaskStatus.BLOCKED]
        )
        self.assertEqual(state.completed_count, 2)

    def test_blocked_count(self):
        state = self._make_state([TaskStatus.DONE, TaskStatus.BLOCKED, TaskStatus.BLOCKED])
        self.assertEqual(state.blocked_count, 2)

    def test_is_finished_all_terminal(self):
        state = self._make_state([TaskStatus.DONE, TaskStatus.BLOCKED])
        self.assertTrue(state.is_finished)

    def test_is_finished_false_with_pending(self):
        state = self._make_state([TaskStatus.DONE, TaskStatus.PENDING])
        self.assertFalse(state.is_finished)


class TestHandleTaskResult(unittest.TestCase):
    """Test result handling for all four HandoffStatus values."""

    def _make_state_with_one_pending(self):
        tasks = [{"id": "1", "description": "Only task"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        advance_dispatch(state, 0)
        return state

    def _make_state_with_two_tasks(self):
        tasks = [{"id": "1", "description": "First"}, {"id": "2", "description": "Second"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        advance_dispatch(state, 0)
        return state

    def test_done_single_task_completes(self):
        state = self._make_state_with_one_pending()
        result = HandoffResult(status=HandoffStatus.DONE, files_changed=["a.py"])
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "complete")
        self.assertEqual(state.records[0].status, TaskStatus.DONE)

    def test_done_multi_task_advances(self):
        state = self._make_state_with_two_tasks()
        result = HandoffResult(status=HandoffStatus.DONE, files_changed=["a.py"])
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "advance")

    def test_done_with_concerns_logs_concerns(self):
        state = self._make_state_with_one_pending()
        result = HandoffResult(
            status=HandoffStatus.DONE_WITH_CONCERNS,
            concerns=["might break Y"],
        )
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "complete")
        self.assertEqual(state.records[0].concerns, ["might break Y"])
        self.assertEqual(state.all_concerns, ["might break Y"])

    def test_needs_context_first_time_redispatches(self):
        state = self._make_state_with_one_pending()
        result = HandoffResult(status=HandoffStatus.NEEDS_CONTEXT, concerns=["need schema"])
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "redispatch")

    def test_needs_context_circuit_breaker(self):
        state = self._make_state_with_one_pending()
        state.records[0].dispatch_count = MAX_NEEDS_CONTEXT_RETRIES
        result = HandoffResult(status=HandoffStatus.NEEDS_CONTEXT)
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "handoff")
        self.assertEqual(state.records[0].status, TaskStatus.BLOCKED)

    def test_blocked_first_attempt_triggers_fix(self):
        state = self._make_state_with_one_pending()
        result = HandoffResult(status=HandoffStatus.BLOCKED, concerns=["missing dep"])
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "fix")

    def test_blocked_exceeded_fix_attempts_handoff(self):
        state = self._make_state_with_one_pending()
        state.records[0].dispatch_count = MAX_BLOCKED_FIX_ATTEMPTS
        result = HandoffResult(status=HandoffStatus.BLOCKED, concerns=["stuck"])
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "handoff")
        self.assertEqual(state.records[0].status, TaskStatus.BLOCKED)

    def test_invalid_task_index_handoff(self):
        state = self._make_state_with_one_pending()
        result = HandoffResult(status=HandoffStatus.DONE)
        self.assertEqual(handle_task_result(state, -1, result), "handoff")
        self.assertEqual(handle_task_result(state, 99, result), "handoff")


class TestAdvanceDispatch(unittest.TestCase):
    """Test dispatch advancement."""

    def test_marks_in_progress_and_increments_count(self):
        tasks = [{"id": "1", "description": "Task"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        idx = advance_dispatch(state, 0)
        self.assertEqual(idx, 0)
        self.assertEqual(state.records[0].status, TaskStatus.IN_PROGRESS)
        self.assertEqual(state.records[0].dispatch_count, 1)

    def test_invalid_index_returns_none(self):
        tasks = [{"id": "1", "description": "Task"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        self.assertIsNone(advance_dispatch(state, -1))
        self.assertIsNone(advance_dispatch(state, 5))

    def test_redispatch_increments_count(self):
        tasks = [{"id": "1", "description": "Task"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        advance_dispatch(state, 0)
        advance_dispatch(state, 0)
        self.assertEqual(state.records[0].dispatch_count, 2)


# ---------------------------------------------------------------------------
# Stage 2 dispatch loop contract
# ---------------------------------------------------------------------------


class TestStage2DispatchLoopContract(unittest.TestCase):
    """Verify that the existing dispatch functions compose into a correct Stage 2 loop."""

    def test_full_loop_creates_state_and_composes_prompts(self):
        """State creation + prompt composition covers the full dispatch prep."""
        tasks = [
            {"id": "1", "description": "Add config parser"},
            {"id": "2", "description": "Add validation logic"},
        ]
        allowed = ["src/config.py", "src/validate.py"]
        reqs = ["REQUIREMENT: Config MUST parse TOML", "REQUIREMENT: Validation MUST reject nulls"]

        state = create_dispatch_state("OBPI-0.18.0-06", "ADR-0.18.0", tasks, allowed)
        self.assertEqual(len(state.records), 2)

        # Each task can produce a scoped prompt with brief requirements
        for rec in state.records:
            prompt = compose_implementer_prompt(rec.task, reqs)
            self.assertIn("Allowed Files", prompt)
            self.assertIn("src/config.py", prompt)
            self.assertIn("Brief Requirements", prompt)
            self.assertIn("REQUIREMENT: Config MUST parse TOML", prompt)
            self.assertIn("Rules", prompt)

    def test_sequential_advance_and_result_handling(self):
        """Tasks advance sequentially; each result is handled before the next dispatch."""
        tasks = [
            {"id": "1", "description": "Task A"},
            {"id": "2", "description": "Task B"},
            {"id": "3", "description": "Task C"},
        ]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])

        for i in range(3):
            idx = advance_dispatch(state, i)
            self.assertEqual(idx, i)
            result = HandoffResult(
                status=HandoffStatus.DONE, files_changed=["a.py"], tests_added=[], concerns=[]
            )
            action = handle_task_result(state, i, result)
            expected = "complete" if i == 2 else "advance"
            self.assertEqual(action, expected)

        self.assertTrue(state.is_finished)
        self.assertEqual(state.completed_count, 3)
        self.assertEqual(state.blocked_count, 0)

    def test_blocked_task_halts_loop(self):
        """A BLOCKED result after exhausting fix attempts halts the dispatch loop."""
        tasks = [
            {"id": "1", "description": "Task A"},
            {"id": "2", "description": "Task B"},
        ]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        blocked_result = HandoffResult(
            status=HandoffStatus.BLOCKED,
            files_changed=[],
            tests_added=[],
            concerns=["Missing dependency"],
        )

        # First dispatch → fix attempt
        advance_dispatch(state, 0)
        action = handle_task_result(state, 0, blocked_result)
        self.assertEqual(action, "fix")

        # Second dispatch → exhausts MAX_BLOCKED_FIX_ATTEMPTS → handoff
        advance_dispatch(state, 0)
        action2 = handle_task_result(state, 0, blocked_result)
        self.assertEqual(action2, "handoff")
        self.assertEqual(state.blocked_count, 1)
        # Task B was never dispatched
        self.assertEqual(state.records[1].status, TaskStatus.PENDING)

    def test_needs_context_redispatches_once_then_blocks(self):
        """NEEDS_CONTEXT allows one redispatch; second triggers block."""
        tasks = [{"id": "1", "description": "Task A"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])

        # First dispatch
        advance_dispatch(state, 0)
        result_nc = HandoffResult(
            status=HandoffStatus.NEEDS_CONTEXT, files_changed=[], tests_added=[], concerns=[]
        )
        action = handle_task_result(state, 0, result_nc)
        self.assertEqual(action, "redispatch")

        # Redispatch
        advance_dispatch(state, 0)
        action2 = handle_task_result(state, 0, result_nc)
        self.assertEqual(action2, "handoff")

    def test_done_with_concerns_logs_and_advances(self):
        """DONE_WITH_CONCERNS logs concerns; returns 'complete' when last task."""
        tasks = [{"id": "1", "description": "Task A"}, {"id": "2", "description": "Task B"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])

        # First task: DONE_WITH_CONCERNS on non-last task → advance
        advance_dispatch(state, 0)
        result = HandoffResult(
            status=HandoffStatus.DONE_WITH_CONCERNS,
            files_changed=["a.py"],
            tests_added=[],
            concerns=["Unclear spec for edge case"],
        )
        action = handle_task_result(state, 0, result)
        self.assertEqual(action, "advance")
        self.assertIn("Unclear spec for edge case", state.all_concerns)

        # Second task: DONE → complete (last task)
        advance_dispatch(state, 1)
        result2 = HandoffResult(
            status=HandoffStatus.DONE, files_changed=["a.py"], tests_added=[], concerns=[]
        )
        action2 = handle_task_result(state, 1, result2)
        self.assertEqual(action2, "complete")

    def test_model_routing_per_task_complexity(self):
        """Each task gets the correct model based on file count."""
        tasks = [
            {"id": "1", "description": "Simple rename"},
            {"id": "2", "description": "Complex refactor"},
        ]
        # 1 file → simple → haiku; 6 files → complex → opus
        state_simple = create_dispatch_state("OBPI-X", "ADR-X", tasks[:1], ["a.py"])
        self.assertEqual(state_simple.records[0].task.model, "haiku")

        many_files = [f"src/mod{i}.py" for i in range(6)]
        state_complex = create_dispatch_state("OBPI-X", "ADR-X", tasks[1:], many_files)
        self.assertEqual(state_complex.records[0].task.model, "opus")

    def test_empty_plan_produces_empty_state(self):
        """An empty plan produces a dispatch state with no records."""
        state = create_dispatch_state("OBPI-X", "ADR-X", [], ["a.py"])
        self.assertEqual(len(state.records), 0)
        self.assertTrue(state.is_finished)


# ---------------------------------------------------------------------------
# Stage 2 review dispatch wiring contract (OBPI-0.18.0-07)
# ---------------------------------------------------------------------------


class TestStage2ReviewDispatchContract(unittest.TestCase):
    """Verify that review protocol functions compose into Stage 2 review wiring."""

    def test_review_dispatched_only_for_done_statuses(self):
        """should_dispatch_review returns True only for DONE/DONE_WITH_CONCERNS."""
        from gzkit.pipeline_runtime import should_dispatch_review

        self.assertTrue(should_dispatch_review(HandoffStatus.DONE))
        self.assertTrue(should_dispatch_review(HandoffStatus.DONE_WITH_CONCERNS))
        self.assertFalse(should_dispatch_review(HandoffStatus.BLOCKED))
        self.assertFalse(should_dispatch_review(HandoffStatus.NEEDS_CONTEXT))

    def test_spec_review_prompt_includes_task_and_requirements(self):
        """compose_spec_review_prompt threads brief requirements and files changed."""
        from gzkit.pipeline_runtime import compose_spec_review_prompt

        task = DispatchTask(
            task_id=1,
            description="Add validation",
            allowed_paths=["src/a.py"],
            complexity=TaskComplexity.SIMPLE,
            model="haiku",
        )
        reqs = ["Config MUST parse TOML", "Validation MUST reject nulls"]
        files_changed = ["src/a.py", "tests/test_a.py"]

        prompt = compose_spec_review_prompt(task, reqs, files_changed)
        self.assertIn("Add validation", prompt)
        self.assertIn("src/a.py", prompt)
        self.assertIn("tests/test_a.py", prompt)
        self.assertIn("Config MUST parse TOML", prompt)
        self.assertIn("Validation MUST reject nulls", prompt)
        self.assertIn("Verify everything independently", prompt)

    def test_quality_review_prompt_includes_files_and_criteria(self):
        """compose_quality_review_prompt includes changed and test files."""
        from gzkit.pipeline_runtime import compose_quality_review_prompt

        files_changed = ["src/config.py"]
        test_files = ["tests/test_config.py"]

        prompt = compose_quality_review_prompt(files_changed, test_files)
        self.assertIn("src/config.py", prompt)
        self.assertIn("tests/test_config.py", prompt)
        self.assertIn("SOLID principles", prompt)
        self.assertIn("Size limits", prompt)

    def test_review_model_never_haiku(self):
        """Reviews always use sonnet or opus, never haiku."""
        from gzkit.pipeline_runtime import select_review_model

        self.assertEqual(select_review_model(TaskComplexity.SIMPLE), "sonnet")
        self.assertEqual(select_review_model(TaskComplexity.STANDARD), "sonnet")
        self.assertEqual(select_review_model(TaskComplexity.COMPLEX), "opus")

    def test_review_cycle_advance_when_both_pass(self):
        """handle_review_cycle returns 'advance' when both reviews pass."""
        from gzkit.pipeline_runtime import handle_review_cycle
        from gzkit.roles import ReviewResult, ReviewVerdict

        tasks = [{"id": "1", "description": "Task A"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        advance_dispatch(state, 0)

        spec_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")
        quality_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")

        action = handle_review_cycle(state, 0, spec_pass, quality_pass)
        self.assertEqual(action, "advance")

    def test_review_cycle_fix_on_critical_spec_finding(self):
        """handle_review_cycle returns 'fix' when spec has critical findings."""
        from gzkit.pipeline_runtime import handle_review_cycle
        from gzkit.roles import (
            ReviewFinding,
            ReviewFindingSeverity,
            ReviewResult,
            ReviewVerdict,
        )

        tasks = [{"id": "1", "description": "Task A"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        advance_dispatch(state, 0)

        spec_fail = ReviewResult(
            verdict=ReviewVerdict.FAIL,
            findings=[
                ReviewFinding(
                    file="a.py",
                    severity=ReviewFindingSeverity.CRITICAL,
                    message="Requirement not met",
                )
            ],
            summary="Fails spec",
        )
        quality_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")

        action = handle_review_cycle(state, 0, spec_fail, quality_pass)
        self.assertEqual(action, "fix")
        self.assertEqual(state.records[0].review_fix_count, 1)

    def test_review_cycle_blocked_after_max_fix_cycles(self):
        """handle_review_cycle returns 'blocked' after MAX_REVIEW_FIX_CYCLES."""
        from gzkit.pipeline_runtime import MAX_REVIEW_FIX_CYCLES, handle_review_cycle
        from gzkit.roles import (
            ReviewFinding,
            ReviewFindingSeverity,
            ReviewResult,
            ReviewVerdict,
        )

        tasks = [{"id": "1", "description": "Task A"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])
        advance_dispatch(state, 0)

        spec_fail = ReviewResult(
            verdict=ReviewVerdict.FAIL,
            findings=[
                ReviewFinding(
                    file="a.py",
                    severity=ReviewFindingSeverity.CRITICAL,
                    message="Still broken",
                )
            ],
            summary="Fails spec",
        )

        # Exhaust fix cycles
        for _ in range(MAX_REVIEW_FIX_CYCLES):
            action = handle_review_cycle(state, 0, spec_fail, None)
            self.assertEqual(action, "fix")

        # One more should block
        action = handle_review_cycle(state, 0, spec_fail, None)
        self.assertEqual(action, "blocked")

    def test_full_loop_with_review_after_each_task(self):
        """End-to-end: dispatch 2 tasks, review after each, both pass, loop completes."""
        from gzkit.pipeline_runtime import (
            compose_quality_review_prompt,
            compose_spec_review_prompt,
            handle_review_cycle,
            should_dispatch_review,
        )
        from gzkit.roles import ReviewResult, ReviewVerdict

        tasks = [
            {"id": "1", "description": "Add model"},
            {"id": "2", "description": "Add tests"},
        ]
        reqs = ["Model MUST validate input"]
        state = create_dispatch_state("OBPI-07", "ADR-0.18.0", tasks, ["src/m.py", "tests/t.py"])

        for i in range(2):
            # Implementer dispatch
            advance_dispatch(state, i)
            impl_result = HandoffResult(
                status=HandoffStatus.DONE,
                files_changed=["src/m.py"],
                tests_added=["tests/t.py"],
                concerns=[],
            )
            handle_task_result(state, i, impl_result)

            # Review dispatch (only if DONE/DONE_WITH_CONCERNS)
            self.assertTrue(should_dispatch_review(impl_result.status))

            # Compose review prompts
            spec_prompt = compose_spec_review_prompt(
                state.records[i].task, reqs, impl_result.files_changed
            )
            quality_prompt = compose_quality_review_prompt(
                impl_result.files_changed, impl_result.tests_added
            )
            self.assertIn("Add model" if i == 0 else "Add tests", spec_prompt)
            self.assertIn("src/m.py", quality_prompt)

            # Both reviews pass
            spec_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")
            quality_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")
            review_action = handle_review_cycle(state, i, spec_pass, quality_pass)
            self.assertEqual(review_action, "advance")

        self.assertTrue(state.is_finished)
        self.assertEqual(state.completed_count, 2)

    def test_fix_cycle_redispatches_implementer_with_findings(self):
        """After review returns 'fix', implementer is redispatched; review runs again."""
        from gzkit.pipeline_runtime import handle_review_cycle, should_dispatch_review
        from gzkit.roles import (
            ReviewFinding,
            ReviewFindingSeverity,
            ReviewResult,
            ReviewVerdict,
        )

        tasks = [{"id": "1", "description": "Task A"}]
        state = create_dispatch_state("OBPI-X", "ADR-X", tasks, ["a.py"])

        # First dispatch → implementer completes
        advance_dispatch(state, 0)
        impl_result = HandoffResult(
            status=HandoffStatus.DONE, files_changed=["a.py"], tests_added=[], concerns=[]
        )
        handle_task_result(state, 0, impl_result)
        self.assertTrue(should_dispatch_review(impl_result.status))

        # Review finds critical issue
        spec_fail = ReviewResult(
            verdict=ReviewVerdict.FAIL,
            findings=[
                ReviewFinding(
                    file="a.py",
                    severity=ReviewFindingSeverity.CRITICAL,
                    message="Missing null check",
                )
            ],
            summary="Fails",
        )
        review_action = handle_review_cycle(state, 0, spec_fail, None)
        self.assertEqual(review_action, "fix")

        # Redispatch implementer with finding context
        advance_dispatch(state, 0)
        impl_result2 = HandoffResult(
            status=HandoffStatus.DONE, files_changed=["a.py"], tests_added=[], concerns=[]
        )
        handle_task_result(state, 0, impl_result2)

        # Re-review passes
        spec_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")
        review_action2 = handle_review_cycle(state, 0, spec_pass, None)
        self.assertEqual(review_action2, "advance")

    def test_no_review_for_blocked_task(self):
        """BLOCKED tasks should not trigger review dispatch."""
        from gzkit.pipeline_runtime import should_dispatch_review

        self.assertFalse(should_dispatch_review(HandoffStatus.BLOCKED))


# ---------------------------------------------------------------------------
# Stage 3 verification dispatch wiring (OBPI-0.18.0-08)
# ---------------------------------------------------------------------------


class TestPrepareStage3Verification(unittest.TestCase):
    """Test Stage 3 verification plan creation from brief content."""

    def test_extracts_requirements_into_plan(self):
        from gzkit.pipeline_runtime import prepare_stage3_verification

        brief = (
            "## Requirements (FAIL-CLOSED)\n"
            "1. REQUIREMENT: SKILL.md Stage 3 MUST analyze brief requirements\n"
            "1. REQUIREMENT: Non-overlapping paths MUST dispatch in parallel\n"
        )
        plan = prepare_stage3_verification(brief, ["tests/test_a.py", "tests/test_b.py"])
        self.assertEqual(len(plan.scopes), 2)
        self.assertIn("analyze brief requirements", plan.scopes[0].requirement_text)

    def test_empty_brief_returns_sequential(self):
        from gzkit.pipeline_runtime import prepare_stage3_verification

        plan = prepare_stage3_verification("No requirements here.")
        self.assertEqual(plan.strategy, "sequential")
        self.assertEqual(len(plan.scopes), 0)

    def test_no_test_paths_returns_sequential(self):
        from gzkit.pipeline_runtime import prepare_stage3_verification

        brief = "1. REQUIREMENT: Something important\n"
        plan = prepare_stage3_verification(brief)
        self.assertEqual(plan.strategy, "sequential")

    def test_distinct_paths_produce_parallel_plan(self):
        from gzkit.pipeline_runtime import (
            VerificationScope,
            build_verification_plan,
        )

        scopes = [
            VerificationScope(
                req_index=1,
                requirement_text="REQ A",
                test_paths=["tests/test_a.py"],
            ),
            VerificationScope(
                req_index=2,
                requirement_text="REQ B",
                test_paths=["tests/test_b.py"],
            ),
        ]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "parallel")
        self.assertEqual(len(plan.independent_groups), 2)


class TestComputeVerificationTiming(unittest.TestCase):
    """Test wall-clock timing metrics computation."""

    def test_basic_timing(self):
        from gzkit.pipeline_runtime import compute_verification_timing

        # 2 seconds elapsed, 3 groups at 30s each = 90s sequential
        start = 0
        end = 2_000_000_000  # 2 seconds in nanoseconds
        metrics = compute_verification_timing(start, end, "parallel", 3)
        self.assertEqual(metrics.strategy, "parallel")
        self.assertEqual(metrics.group_count, 3)
        self.assertEqual(metrics.elapsed_seconds, 2.0)
        self.assertEqual(metrics.estimated_sequential_seconds, 90.0)
        self.assertEqual(metrics.time_saved_seconds, 88.0)

    def test_sequential_no_savings(self):
        from gzkit.pipeline_runtime import compute_verification_timing

        metrics = compute_verification_timing(0, 30_000_000_000, "sequential", 1)
        self.assertEqual(metrics.time_saved_seconds, 0.0)

    def test_custom_per_group_estimate(self):
        from gzkit.pipeline_runtime import compute_verification_timing

        metrics = compute_verification_timing(
            0, 5_000_000_000, "parallel", 2, per_group_estimate_seconds=10.0
        )
        self.assertEqual(metrics.estimated_sequential_seconds, 20.0)
        self.assertEqual(metrics.time_saved_seconds, 15.0)


class TestCreateVerificationDispatchRecords(unittest.TestCase):
    """Test bridging verification results to dispatch records."""

    def test_creates_records_for_each_scope(self):
        from gzkit.pipeline_runtime import (
            VerificationOutcome,
            VerificationPlan,
            VerificationResult,
            VerificationScope,
            create_verification_dispatch_records,
        )

        plan = VerificationPlan(
            scopes=[
                VerificationScope(
                    req_index=1,
                    requirement_text="REQ A",
                    test_paths=["tests/test_a.py"],
                ),
                VerificationScope(
                    req_index=2,
                    requirement_text="REQ B",
                    test_paths=["tests/test_b.py"],
                ),
            ],
            independent_groups=[[1], [2]],
            strategy="parallel",
        )
        results = [
            VerificationResult(
                req_index=1,
                outcome=VerificationOutcome.PASS,
                detail="All tests pass",
                commands_run=["uv run -m unittest tests.test_a -q"],
            ),
            VerificationResult(
                req_index=2,
                outcome=VerificationOutcome.FAIL,
                detail="Test failed",
                commands_run=["uv run -m unittest tests.test_b -q"],
            ),
        ]
        records = create_verification_dispatch_records(plan, results)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["role"], "Verifier")
        self.assertEqual(records[0]["stage"], 3)
        self.assertEqual(records[0]["status"], "PASS")
        self.assertEqual(records[1]["status"], "FAIL")

    def test_missing_result_marked_as_missing(self):
        from gzkit.pipeline_runtime import (
            VerificationPlan,
            VerificationScope,
            create_verification_dispatch_records,
        )

        plan = VerificationPlan(
            scopes=[
                VerificationScope(
                    req_index=1,
                    requirement_text="REQ A",
                    test_paths=["tests/test_a.py"],
                ),
            ],
            independent_groups=[[1]],
            strategy="sequential",
        )
        records = create_verification_dispatch_records(plan, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "MISSING")


class TestStage3VerificationDispatchContract(unittest.TestCase):
    """End-to-end: verification plan → dispatch → aggregate → timing."""

    def test_full_stage3_verification_flow(self):
        from gzkit.pipeline_runtime import (
            VerificationOutcome,
            VerificationResult,
            VerificationScope,
            aggregate_verification_results,
            build_verification_plan,
            compute_verification_timing,
            create_verification_dispatch_records,
            should_fallback_to_sequential,
        )

        # Build scopes with distinct per-REQ test paths (as Stage 3 would)
        scopes = [
            VerificationScope(
                req_index=1,
                requirement_text="Config MUST parse TOML",
                test_paths=["tests/test_config.py"],
            ),
            VerificationScope(
                req_index=2,
                requirement_text="Validation MUST reject nulls",
                test_paths=["tests/test_validate.py"],
            ),
        ]
        plan = build_verification_plan(scopes)
        self.assertFalse(should_fallback_to_sequential(plan))

        # Simulate subagent results
        results = [
            VerificationResult(
                req_index=1,
                outcome=VerificationOutcome.PASS,
                detail="Config parsing works",
            ),
            VerificationResult(
                req_index=2,
                outcome=VerificationOutcome.PASS,
                detail="Null rejection works",
            ),
        ]
        all_passed, failures = aggregate_verification_results(results, [1, 2])
        self.assertTrue(all_passed)
        self.assertEqual(len(failures), 0)

        # Dispatch records
        records = create_verification_dispatch_records(plan, results)
        self.assertEqual(len(records), 2)
        self.assertTrue(all(r["status"] == "PASS" for r in records))

        # Timing
        metrics = compute_verification_timing(
            0, 5_000_000_000, plan.strategy, len(plan.independent_groups)
        )
        self.assertGreater(metrics.elapsed_seconds, 0)

    def test_no_subagents_flag_uses_sequential(self):
        """--no-subagents forces sequential fallback regardless of plan."""
        from gzkit.pipeline_runtime import (
            prepare_stage3_verification,
            should_fallback_to_sequential,
        )

        brief = "1. REQUIREMENT: Something\n"
        plan = prepare_stage3_verification(brief)
        # No test paths → sequential
        self.assertTrue(should_fallback_to_sequential(plan))


if __name__ == "__main__":
    unittest.main()
