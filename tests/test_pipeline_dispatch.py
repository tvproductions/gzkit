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
from gzkit.roles import HandoffResult, HandoffStatus

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


if __name__ == "__main__":
    unittest.main()
