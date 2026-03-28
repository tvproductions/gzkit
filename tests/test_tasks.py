"""Tests for TASK entity model (OBPI-0.22.0-01).

Covers: identifier parsing, lifecycle states, transitions, and plan-derived creation.
"""

from __future__ import annotations

import unittest

from gzkit.tasks import TaskEntity, TaskId, TaskStatus, create_task_from_plan_step


class TestTaskId(unittest.TestCase):
    """@covers REQ-0.22.0-01-01, REQ-0.22.0-01-06."""

    def test_parse_valid_id(self) -> None:
        """REQ-0.22.0-01-01: Parse valid TASK string into components."""
        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        self.assertEqual(tid.semver, "0.20.0")
        self.assertEqual(tid.obpi_item, "01")
        self.assertEqual(tid.req_index, "01")
        self.assertEqual(tid.seq, "01")

    def test_parse_multi_digit_components(self) -> None:
        tid = TaskId.parse("TASK-0.22.0-03-12-05")
        self.assertEqual(tid.semver, "0.22.0")
        self.assertEqual(tid.obpi_item, "03")
        self.assertEqual(tid.req_index, "12")
        self.assertEqual(tid.seq, "05")

    def test_parse_strips_whitespace(self) -> None:
        tid = TaskId.parse("  TASK-0.20.0-01-01-01  ")
        self.assertEqual(str(tid), "TASK-0.20.0-01-01-01")

    def test_parse_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            TaskId.parse("INVALID-0.20.0-01-01-01")

    def test_parse_missing_seq_raises(self) -> None:
        with self.assertRaises(ValueError):
            TaskId.parse("TASK-0.20.0-01-01")

    def test_str_roundtrip(self) -> None:
        raw = "TASK-0.20.0-01-01-01"
        tid = TaskId.parse(raw)
        self.assertEqual(str(tid), raw)

    def test_frozen(self) -> None:
        from pydantic import ValidationError

        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        with self.assertRaises(ValidationError):
            tid.semver = "1.0.0"  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskId(semver="0.1.0", obpi_item="01", req_index="01", seq="01", extra="bad")  # type: ignore[call-arg]


class TestTaskStatus(unittest.TestCase):
    """@covers REQ-0.22.0-01-05."""

    def test_exactly_five_states(self) -> None:
        """REQ-0.22.0-01-05: Exactly 5 lifecycle states."""
        expected = {"pending", "in_progress", "completed", "blocked", "escalated"}
        actual = {s.value for s in TaskStatus}
        self.assertEqual(actual, expected)

    def test_states_are_strings(self) -> None:
        for s in TaskStatus:
            self.assertIsInstance(s.value, str)


class TestTaskEntity(unittest.TestCase):
    """@covers REQ-0.22.0-01-02, REQ-0.22.0-01-03, REQ-0.22.0-01-06."""

    def _make_task(self, *, status: TaskStatus = TaskStatus.PENDING) -> TaskEntity:
        return TaskEntity(
            id=TaskId.parse("TASK-0.20.0-01-01-01"),
            description="Implement the REQ model",
            status=status,
            parent_req="REQ-0.20.0-01-01",
            parent_obpi="OBPI-0.20.0-01",
        )

    def test_create_task(self) -> None:
        task = self._make_task()
        self.assertEqual(str(task.id), "TASK-0.20.0-01-01-01")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.parent_req, "REQ-0.20.0-01-01")
        self.assertEqual(task.parent_obpi, "OBPI-0.20.0-01")

    def test_transition_pending_to_in_progress(self) -> None:
        """REQ-0.22.0-01-02: pending → in_progress succeeds."""
        task = self._make_task(status=TaskStatus.PENDING)
        new = task.transition(TaskStatus.IN_PROGRESS)
        self.assertEqual(new.status, TaskStatus.IN_PROGRESS)

    def test_transition_in_progress_to_completed(self) -> None:
        task = self._make_task(status=TaskStatus.IN_PROGRESS)
        new = task.transition(TaskStatus.COMPLETED)
        self.assertEqual(new.status, TaskStatus.COMPLETED)

    def test_transition_in_progress_to_blocked(self) -> None:
        task = self._make_task(status=TaskStatus.IN_PROGRESS)
        new = task.transition(TaskStatus.BLOCKED)
        self.assertEqual(new.status, TaskStatus.BLOCKED)

    def test_transition_blocked_to_in_progress(self) -> None:
        """REQ-0.22.0-01-06: blocked → in_progress resume is valid."""
        task = self._make_task(status=TaskStatus.BLOCKED)
        new = task.transition(TaskStatus.IN_PROGRESS)
        self.assertEqual(new.status, TaskStatus.IN_PROGRESS)

    def test_transition_in_progress_to_escalated(self) -> None:
        task = self._make_task(status=TaskStatus.IN_PROGRESS)
        new = task.transition(TaskStatus.ESCALATED)
        self.assertEqual(new.status, TaskStatus.ESCALATED)

    def test_transition_pending_to_completed_raises(self) -> None:
        """REQ-0.22.0-01-03: pending → completed is invalid."""
        task = self._make_task(status=TaskStatus.PENDING)
        with self.assertRaises(ValueError, msg="pending -> completed"):
            task.transition(TaskStatus.COMPLETED)

    def test_transition_pending_to_blocked_raises(self) -> None:
        task = self._make_task(status=TaskStatus.PENDING)
        with self.assertRaises(ValueError):
            task.transition(TaskStatus.BLOCKED)

    def test_transition_completed_to_anything_raises(self) -> None:
        task = self._make_task(status=TaskStatus.COMPLETED)
        for target in TaskStatus:
            if target != TaskStatus.COMPLETED:
                with self.assertRaises(ValueError, msg=f"completed -> {target}"):
                    task.transition(target)

    def test_transition_escalated_to_anything_raises(self) -> None:
        task = self._make_task(status=TaskStatus.ESCALATED)
        for target in TaskStatus:
            if target != TaskStatus.ESCALATED:
                with self.assertRaises(ValueError, msg=f"escalated -> {target}"):
                    task.transition(target)

    def test_frozen(self) -> None:
        from pydantic import ValidationError

        task = self._make_task()
        with self.assertRaises(ValidationError):
            task.status = TaskStatus.IN_PROGRESS  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskEntity(
                id=TaskId.parse("TASK-0.20.0-01-01-01"),
                description="test",
                status=TaskStatus.PENDING,
                parent_req="REQ-0.20.0-01-01",
                parent_obpi="OBPI-0.20.0-01",
                extra_field="bad",  # type: ignore[call-arg]
            )


class TestCreateTaskFromPlanStep(unittest.TestCase):
    """@covers REQ-0.22.0-01-04."""

    def test_create_from_plan_step(self) -> None:
        """REQ-0.22.0-01-04: Factory creates TASK from plan text + parent context."""
        task = create_task_from_plan_step(
            plan_text="Implement the REQ model",
            parent_obpi="OBPI-0.20.0-01",
            parent_req="REQ-0.20.0-01-01",
            semver="0.20.0",
            obpi_item="01",
            req_index="01",
            seq=1,
        )
        self.assertEqual(str(task.id), "TASK-0.20.0-01-01-01")
        self.assertEqual(task.description, "Implement the REQ model")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.parent_req, "REQ-0.20.0-01-01")
        self.assertEqual(task.parent_obpi, "OBPI-0.20.0-01")

    def test_create_auto_pads_seq(self) -> None:
        task = create_task_from_plan_step(
            plan_text="Second step",
            parent_obpi="OBPI-0.20.0-01",
            parent_req="REQ-0.20.0-01-01",
            semver="0.20.0",
            obpi_item="01",
            req_index="01",
            seq=3,
        )
        self.assertEqual(str(task.id), "TASK-0.20.0-01-01-03")


if __name__ == "__main__":
    unittest.main()
