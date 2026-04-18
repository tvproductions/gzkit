"""Tests for TASK entity model, ledger events, and CLI (OBPI-0.22.0-01..04).

Covers: identifier parsing, lifecycle states, transitions, plan-derived creation,
TASK ledger event serialization/parsing, and gz task CLI smoke tests.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from gzkit.cli import main as cli_main
from gzkit.events import (
    TaskBlockedEvent,
    TaskCompletedEvent,
    TaskEscalatedEvent,
    TaskStartedEvent,
    parse_typed_event,
)
from gzkit.ledger import Ledger, LedgerEvent, obpi_created_event
from gzkit.tasks import (
    TaskEntity,
    TaskId,
    TaskStatus,
    create_task_from_plan_step,
    format_commit_trailer,
    parse_ceremony_trailers,
    parse_task_trailers,
    resolve_task_chain,
)


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


class TestTaskId(unittest.TestCase):
    """@covers REQ-0.22.0-01-01, REQ-0.22.0-01-06."""

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    def test_parse_valid_id(self) -> None:
        """REQ-0.22.0-01-01: Parse valid TASK string into components."""
        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        self.assertEqual(tid.semver, "0.20.0")
        self.assertEqual(tid.obpi_item, "01")
        self.assertEqual(tid.req_index, "01")
        self.assertEqual(tid.seq, "01")

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    def test_parse_multi_digit_components(self) -> None:
        tid = TaskId.parse("TASK-0.22.0-03-12-05")
        self.assertEqual(tid.semver, "0.22.0")
        self.assertEqual(tid.obpi_item, "03")
        self.assertEqual(tid.req_index, "12")
        self.assertEqual(tid.seq, "05")

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    def test_parse_strips_whitespace(self) -> None:
        tid = TaskId.parse("  TASK-0.20.0-01-01-01  ")
        self.assertEqual(str(tid), "TASK-0.20.0-01-01-01")

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    def test_parse_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            TaskId.parse("INVALID-0.20.0-01-01-01")

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    def test_parse_missing_seq_raises(self) -> None:
        with self.assertRaises(ValueError):
            TaskId.parse("TASK-0.20.0-01-01")

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    def test_str_roundtrip(self) -> None:
        raw = "TASK-0.20.0-01-01-01"
        tid = TaskId.parse(raw)
        self.assertEqual(str(tid), raw)

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_frozen(self) -> None:
        from pydantic import ValidationError

        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        with self.assertRaises(ValidationError):
            tid.semver = "1.0.0"  # type: ignore[misc]

    @covers("REQ-0.22.0-01-01")
    @covers("REQ-0.22.0-01-06")
    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_extra_forbid(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskId(semver="0.1.0", obpi_item="01", req_index="01", seq="01", extra="bad")  # type: ignore[call-arg]


class TestTaskStatus(unittest.TestCase):
    """@covers REQ-0.22.0-01-05."""

    @covers("REQ-0.22.0-01-05")
    def test_exactly_five_states(self) -> None:
        """REQ-0.22.0-01-05: Exactly 5 lifecycle states."""
        expected = {"pending", "in_progress", "completed", "blocked", "escalated"}
        actual = {s.value for s in TaskStatus}
        self.assertEqual(actual, expected)

    @covers("REQ-0.22.0-01-05")
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

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_create_task(self) -> None:
        task = self._make_task()
        self.assertEqual(str(task.id), "TASK-0.20.0-01-01-01")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.parent_req, "REQ-0.20.0-01-01")
        self.assertEqual(task.parent_obpi, "OBPI-0.20.0-01")

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_pending_to_in_progress(self) -> None:
        """REQ-0.22.0-01-02: pending → in_progress succeeds."""
        task = self._make_task(status=TaskStatus.PENDING)
        new = task.transition(TaskStatus.IN_PROGRESS)
        self.assertEqual(new.status, TaskStatus.IN_PROGRESS)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_in_progress_to_completed(self) -> None:
        task = self._make_task(status=TaskStatus.IN_PROGRESS)
        new = task.transition(TaskStatus.COMPLETED)
        self.assertEqual(new.status, TaskStatus.COMPLETED)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_in_progress_to_blocked(self) -> None:
        task = self._make_task(status=TaskStatus.IN_PROGRESS)
        new = task.transition(TaskStatus.BLOCKED)
        self.assertEqual(new.status, TaskStatus.BLOCKED)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_blocked_to_in_progress(self) -> None:
        """REQ-0.22.0-01-06: blocked → in_progress resume is valid."""
        task = self._make_task(status=TaskStatus.BLOCKED)
        new = task.transition(TaskStatus.IN_PROGRESS)
        self.assertEqual(new.status, TaskStatus.IN_PROGRESS)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_in_progress_to_escalated(self) -> None:
        task = self._make_task(status=TaskStatus.IN_PROGRESS)
        new = task.transition(TaskStatus.ESCALATED)
        self.assertEqual(new.status, TaskStatus.ESCALATED)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_pending_to_completed_raises(self) -> None:
        """REQ-0.22.0-01-03: pending → completed is invalid."""
        task = self._make_task(status=TaskStatus.PENDING)
        with self.assertRaises(ValueError, msg="pending -> completed"):
            task.transition(TaskStatus.COMPLETED)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_pending_to_blocked_raises(self) -> None:
        task = self._make_task(status=TaskStatus.PENDING)
        with self.assertRaises(ValueError):
            task.transition(TaskStatus.BLOCKED)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
    def test_transition_completed_to_anything_raises(self) -> None:
        task = self._make_task(status=TaskStatus.COMPLETED)
        for target in TaskStatus:
            if target != TaskStatus.COMPLETED:
                with self.assertRaises(ValueError, msg=f"completed -> {target}"):
                    task.transition(target)

    @covers("REQ-0.22.0-01-02")
    @covers("REQ-0.22.0-01-03")
    @covers("REQ-0.22.0-01-06")
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

    @covers("REQ-0.22.0-01-04")
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

    @covers("REQ-0.22.0-01-04")
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


# ---------------------------------------------------------------------------
# TASK ledger events (OBPI-0.22.0-02)
# ---------------------------------------------------------------------------

_TASK_FIELDS = {
    "id": "TASK-0.22.0-02-01-01",
    "task_id": "TASK-0.22.0-02-01-01",
    "obpi_id": "OBPI-0.22.0-02",
    "adr_id": "ADR-0.22.0",
    "agent": "claude-code",
}


def _started(**extra: str) -> TaskStartedEvent:
    return TaskStartedEvent(event="task_started", **_TASK_FIELDS, **extra)


def _completed(**extra: str) -> TaskCompletedEvent:
    return TaskCompletedEvent(event="task_completed", **_TASK_FIELDS, **extra)


def _blocked(**extra: str) -> TaskBlockedEvent:
    return TaskBlockedEvent(event="task_blocked", **_TASK_FIELDS, **extra)


def _escalated(**extra: str | None) -> TaskEscalatedEvent:
    return TaskEscalatedEvent(event="task_escalated", **_TASK_FIELDS, **extra)


class TestTaskStartedEvent(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-03, REQ-0.22.0-02-04."""

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-04")
    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    def test_serialize_includes_required_fields(self) -> None:
        """REQ-0.22.0-02-01: task_started serializes with required fields."""
        evt = _started()
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_started")
        self.assertIn("ts", data)
        self.assertEqual(data["task_id"], "TASK-0.22.0-02-01-01")
        self.assertEqual(data["obpi_id"], "OBPI-0.22.0-02")
        self.assertEqual(data["adr_id"], "ADR-0.22.0")
        self.assertEqual(data["agent"], "claude-code")

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-04")
    def test_discriminated_union_parses_task_started(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_started correctly."""
        evt = _started()
        data = json.loads(evt.model_dump_json())
        parsed = parse_typed_event(data)
        self.assertIsInstance(parsed, TaskStartedEvent)
        self.assertEqual(parsed.task_id, "TASK-0.22.0-02-01-01")

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-04")
    def test_task_started_reused_for_resume(self) -> None:
        """REQ-0.22.0-02-04: task_started is reused for blocked->in_progress resume."""
        evt = _started()
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_started")
        parsed = parse_typed_event(data)
        self.assertIsInstance(parsed, TaskStartedEvent)

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-04")
    def test_jsonl_serializable(self) -> None:
        """REQ-0.22.0-02-07: Event serializes to single-line JSON for JSONL."""
        evt = _started()
        line = evt.model_dump_json()
        reparsed = json.loads(line)
        self.assertEqual(reparsed["event"], "task_started")


class TestTaskCompletedEvent(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-03."""

    def test_serialize_includes_required_fields(self) -> None:
        """REQ-0.22.0-02-01: task_completed serializes with all required fields."""
        evt = _completed()
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_completed")
        self.assertIn("ts", data)
        self.assertEqual(data["task_id"], "TASK-0.22.0-02-01-01")
        self.assertEqual(data["obpi_id"], "OBPI-0.22.0-02")
        self.assertEqual(data["adr_id"], "ADR-0.22.0")
        self.assertEqual(data["agent"], "claude-code")

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    def test_discriminated_union_parses_task_completed(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_completed."""
        evt = _completed()
        parsed = parse_typed_event(json.loads(evt.model_dump_json()))
        self.assertIsInstance(parsed, TaskCompletedEvent)


class TestTaskBlockedEvent(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-02, REQ-0.22.0-02-03."""

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-02")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-05")
    def test_serialize_includes_reason(self) -> None:
        """REQ-0.22.0-02-02: task_blocked includes reason field."""
        evt = _blocked(reason="Missing dependency")
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_blocked")
        self.assertEqual(data["reason"], "Missing dependency")
        self.assertEqual(data["task_id"], "TASK-0.22.0-02-01-01")
        self.assertEqual(data["obpi_id"], "OBPI-0.22.0-02")
        self.assertEqual(data["adr_id"], "ADR-0.22.0")
        self.assertEqual(data["agent"], "claude-code")

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-02")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-05")
    def test_reason_required(self) -> None:
        """REQ-0.22.0-02-04: task_blocked requires reason field."""
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskBlockedEvent(event="task_blocked", **_TASK_FIELDS)  # type: ignore[arg-type]

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-02")
    @covers("REQ-0.22.0-02-03")
    def test_discriminated_union_parses_task_blocked(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_blocked."""
        evt = _blocked(reason="Waiting on OBPI-01")
        parsed = parse_typed_event(json.loads(evt.model_dump_json()))
        self.assertIsInstance(parsed, TaskBlockedEvent)
        self.assertEqual(parsed.reason, "Waiting on OBPI-01")


class TestTaskEscalatedEvent(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-03, REQ-0.22.0-02-05."""

    def test_serialize_includes_reason(self) -> None:
        """REQ-0.22.0-02-05: task_escalated has reason and escalated_to."""
        evt = _escalated(reason="Needs human decision", escalated_to="jeff")
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_escalated")
        self.assertEqual(data["reason"], "Needs human decision")
        self.assertEqual(data["escalated_to"], "jeff")

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-05")
    def test_escalated_to_optional(self) -> None:
        """REQ-0.22.0-02-05: escalated_to is optional."""
        evt = _escalated(reason="Complex issue")
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_escalated")
        self.assertEqual(data["reason"], "Complex issue")
        self.assertNotIn("escalated_to", data)

    def test_reason_required(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskEscalatedEvent(event="task_escalated", **_TASK_FIELDS)  # type: ignore[arg-type]

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-05")
    def test_discriminated_union_parses_task_escalated(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_escalated."""
        evt = _escalated(reason="Over complexity budget")
        parsed = parse_typed_event(json.loads(evt.model_dump_json()))
        self.assertIsInstance(parsed, TaskEscalatedEvent)
        self.assertEqual(parsed.reason, "Over complexity budget")


class TestAllFourEventTypes(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-03, REQ-0.22.0-02-06."""

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-06")
    def test_four_event_types_defined(self) -> None:
        """REQ-0.22.0-02-01: Exactly four TASK event types exist."""
        event_types = {
            "task_started": TaskStartedEvent,
            "task_completed": TaskCompletedEvent,
            "task_blocked": TaskBlockedEvent,
            "task_escalated": TaskEscalatedEvent,
        }
        self.assertEqual(len(event_types), 4)
        for event_name, cls in event_types.items():
            self.assertTrue(
                hasattr(cls.model_fields["event"], "default"),
                f"{event_name} must have literal event type",
            )

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-06")
    def test_all_four_roundtrip_via_discriminated_union(self) -> None:
        """REQ-0.22.0-02-03: All four roundtrip via discriminated union."""
        events = [
            _started(),
            _completed(),
            _blocked(reason="blocked"),
            _escalated(reason="escalated"),
        ]
        expected_types = [
            TaskStartedEvent,
            TaskCompletedEvent,
            TaskBlockedEvent,
            TaskEscalatedEvent,
        ]
        for evt, expected_cls in zip(events, expected_types, strict=True):
            data = json.loads(evt.model_dump_json())
            parsed = parse_typed_event(data)
            self.assertIsInstance(parsed, expected_cls, f"Failed for {expected_cls.__name__}")

    @covers("REQ-0.22.0-02-01")
    @covers("REQ-0.22.0-02-03")
    @covers("REQ-0.22.0-02-06")
    def test_all_events_have_common_fields(self) -> None:
        """REQ-0.22.0-02-06: All events follow existing event model patterns."""
        events = [
            _started(),
            _completed(),
            _blocked(reason="r"),
            _escalated(reason="r"),
        ]
        required = (
            "event",
            "id",
            "ts",
            "schema",
            "task_id",
            "obpi_id",
            "adr_id",
            "agent",
        )
        for evt in events:
            data = json.loads(evt.model_dump_json())
            for field in required:
                self.assertIn(field, data, f"Missing {field} in {data['event']}")


# ---------------------------------------------------------------------------
# Git commit linkage (OBPI-0.22.0-03)
# ---------------------------------------------------------------------------


class TestFormatCommitTrailer(unittest.TestCase):
    """@covers REQ-0.22.0-03-02."""

    @covers("REQ-0.22.0-03-02")
    def test_format_trailer_from_task_entity(self) -> None:
        """REQ-0.22.0-03-02: Formatter produces valid trailer line."""
        task = TaskEntity(
            id=TaskId.parse("TASK-0.20.0-01-01-01"),
            description="Implement the REQ model",
            status=TaskStatus.PENDING,
            parent_req="REQ-0.20.0-01-01",
            parent_obpi="OBPI-0.20.0-01",
        )
        result = format_commit_trailer(task)
        self.assertEqual(result, "Task: TASK-0.20.0-01-01-01")

    @covers("REQ-0.22.0-03-02")
    def test_format_trailer_from_task_id(self) -> None:
        """Formatter also accepts a TaskId directly."""
        tid = TaskId.parse("TASK-0.22.0-03-12-05")
        result = format_commit_trailer(tid)
        self.assertEqual(result, "Task: TASK-0.22.0-03-12-05")


class TestParseTaskTrailers(unittest.TestCase):
    """@covers REQ-0.22.0-03-01, REQ-0.22.0-03-03."""

    @covers("REQ-0.22.0-03-01")
    @covers("REQ-0.22.0-03-03")
    def test_parse_single_trailer(self) -> None:
        """REQ-0.22.0-03-01: Extract single TASK ID from commit message."""
        msg = "Add REQ model implementation\n\nTask: TASK-0.20.0-01-01-01\n"
        result = parse_task_trailers(msg)
        self.assertEqual(len(result), 1)
        self.assertEqual(str(result[0]), "TASK-0.20.0-01-01-01")

    @covers("REQ-0.22.0-03-01")
    @covers("REQ-0.22.0-03-03")
    def test_parse_multiple_trailers(self) -> None:
        """REQ-0.22.0-03-03: Multiple Task trailers all extracted."""
        msg = (
            "Implement REQ model and factory\n"
            "\n"
            "Task: TASK-0.20.0-01-01-01\n"
            "Task: TASK-0.20.0-01-01-02\n"
        )
        result = parse_task_trailers(msg)
        self.assertEqual(len(result), 2)
        self.assertEqual(str(result[0]), "TASK-0.20.0-01-01-01")
        self.assertEqual(str(result[1]), "TASK-0.20.0-01-01-02")

    @covers("REQ-0.22.0-03-01")
    @covers("REQ-0.22.0-03-03")
    def test_no_trailers_returns_empty(self) -> None:
        msg = "Simple commit message\n\nNo trailers here.\n"
        result = parse_task_trailers(msg)
        self.assertEqual(result, [])

    @covers("REQ-0.22.0-03-01")
    @covers("REQ-0.22.0-03-03")
    def test_ignores_non_task_trailers(self) -> None:
        msg = (
            "Fix bug\n\nCo-Authored-By: Someone\nTask: TASK-0.20.0-01-01-01\nSigned-off-by: Jeff\n"
        )
        result = parse_task_trailers(msg)
        self.assertEqual(len(result), 1)
        self.assertEqual(str(result[0]), "TASK-0.20.0-01-01-01")

    @covers("REQ-0.22.0-03-01")
    @covers("REQ-0.22.0-03-03")
    def test_ignores_task_keyword_in_body(self) -> None:
        """Only trailer-section lines are parsed, not body text."""
        msg = (
            "Work on Task: TASK-0.20.0-01-01-99 in the body\n"
            "\n"
            "This mentions Task: TASK-0.20.0-01-01-98 mid-paragraph.\n"
            "\n"
            "Task: TASK-0.20.0-01-01-01\n"
        )
        result = parse_task_trailers(msg)
        self.assertEqual(len(result), 1)
        self.assertEqual(str(result[0]), "TASK-0.20.0-01-01-01")


class TestParseCeremonyTrailers(unittest.TestCase):
    """Ceremony trailers satisfy governance-intent for chore/sync commits (GHI #201)."""

    def test_extracts_ceremony_trailer(self) -> None:
        msg = "chore: update artifacts (gz git-sync)\n\nCeremony: gz-git-sync\n"
        result = parse_ceremony_trailers(msg)
        self.assertEqual(result, ["gz-git-sync"])

    def test_returns_empty_for_no_ceremony(self) -> None:
        msg = "feat: add module\n\nTask: TASK-0.20.0-01-01-01\n"
        self.assertEqual(parse_ceremony_trailers(msg), [])

    def test_ignores_ceremony_keyword_in_body(self) -> None:
        msg = "Work on Ceremony: gz-git-sync mid-paragraph\n\nTask: TASK-0.20.0-01-01-01\n"
        self.assertEqual(parse_ceremony_trailers(msg), [])

    def test_coexists_with_task_trailer(self) -> None:
        msg = "fix: patch\n\nTask: TASK-0.20.0-01-01-01\nCeremony: obpi-reconcile\n"
        self.assertEqual(parse_ceremony_trailers(msg), ["obpi-reconcile"])


class TestResolveTaskChain(unittest.TestCase):
    """@covers REQ-0.22.0-03-04."""

    @covers("REQ-0.22.0-03-04")
    def test_resolve_chain(self) -> None:
        """REQ-0.22.0-03-04: Resolve TASK → REQ → OBPI → ADR chain."""
        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        chain = resolve_task_chain(tid)
        self.assertEqual(chain["task"], "TASK-0.20.0-01-01-01")
        self.assertEqual(chain["req"], "REQ-0.20.0-01-01")
        self.assertEqual(chain["obpi"], "OBPI-0.20.0-01")
        self.assertEqual(chain["adr"], "ADR-0.20.0")

    @covers("REQ-0.22.0-03-04")
    def test_resolve_chain_different_ids(self) -> None:
        tid = TaskId.parse("TASK-0.22.0-03-12-05")
        chain = resolve_task_chain(tid)
        self.assertEqual(chain["task"], "TASK-0.22.0-03-12-05")
        self.assertEqual(chain["req"], "REQ-0.22.0-03-12")
        self.assertEqual(chain["obpi"], "OBPI-0.22.0-03")
        self.assertEqual(chain["adr"], "ADR-0.22.0")

    @covers("REQ-0.22.0-03-04")
    def test_resolve_chain_keys(self) -> None:
        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        chain = resolve_task_chain(tid)
        self.assertEqual(set(chain.keys()), {"task", "req", "obpi", "adr"})


# ---------------------------------------------------------------------------
# CLI smoke tests (OBPI-0.22.0-04)
# ---------------------------------------------------------------------------


def _invoke(args: list[str]) -> tuple[int, str]:
    """Invoke the gz CLI and capture exit code + output."""
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = cli_main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


class _TaskCliBase(unittest.TestCase):
    """Base class that sets up an isolated workspace with an OBPI in the ledger.

    Expensive operations (``gz init``, ``gz plan create``) run once per class
    in ``setUpClass``.  Each test gets a fresh ledger restored from the base
    snapshot so mutations in one test don't leak into another.
    """

    @classmethod
    def setUpClass(cls) -> None:
        import os

        cls._tmp_ctx = tempfile.TemporaryDirectory(prefix="gzkit-task-test-")
        cls._tmpdir = cls._tmp_ctx.name
        cls._orig_cwd = Path.cwd()
        os.chdir(cls._tmpdir)
        # Initialize workspace (expensive — do once)
        code, out = _invoke(["init"])
        assert code == 0, out
        # Create ADR (expensive — do once)
        code, out = _invoke(["plan", "create", "0.1.0"])
        assert code == 0, out
        # Seed OBPI and snapshot the ledger
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
        cls._base_ledger = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")

    def setUp(self) -> None:
        # Restore ledger to base state so tests are isolated
        Path(".gzkit/ledger.jsonl").write_text(self._base_ledger, encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        import os

        os.chdir(cls._orig_cwd)
        cls._tmp_ctx.cleanup()

    def _seed_task_started(self, task_id: str = "TASK-0.1.0-01-01-01") -> None:
        """Emit a task_started event so the task is in_progress."""
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        evt = LedgerEvent(
            event="task_started",
            id=task_id,
            extra={
                "task_id": task_id,
                "obpi_id": "OBPI-0.1.0-01",
                "adr_id": "ADR-0.1.0",
                "agent": "test",
            },
        )
        ledger.append(evt)


class TestTaskHelp(_TaskCliBase):
    """Verify gz task help output."""

    def test_task_help(self) -> None:
        """gz task -h exits 0 with subcommand list."""
        code, out = _invoke(["task", "--help"])
        self.assertEqual(code, 0, out)
        self.assertIn("list", out)
        self.assertIn("start", out)
        self.assertIn("complete", out)
        self.assertIn("block", out)
        self.assertIn("escalate", out)

    def test_task_list_help(self) -> None:
        code, out = _invoke(["task", "list", "--help"])
        self.assertEqual(code, 0, out)

    def test_task_start_help(self) -> None:
        code, out = _invoke(["task", "start", "--help"])
        self.assertEqual(code, 0, out)

    def test_task_complete_help(self) -> None:
        code, out = _invoke(["task", "complete", "--help"])
        self.assertEqual(code, 0, out)

    def test_task_block_help(self) -> None:
        code, out = _invoke(["task", "block", "--help"])
        self.assertEqual(code, 0, out)

    def test_task_escalate_help(self) -> None:
        code, out = _invoke(["task", "escalate", "--help"])
        self.assertEqual(code, 0, out)


class TestTaskList(_TaskCliBase):
    """@covers REQ-0.22.0-04-01."""

    @covers("REQ-0.22.0-04-01")
    def test_list_empty(self) -> None:
        """REQ-0.22.0-04-01: gz task list shows empty when no tasks exist."""
        code, out = _invoke(["task", "list", "OBPI-0.1.0-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("No tasks found", out)

    @covers("REQ-0.22.0-04-01")
    def test_list_shows_task_after_start(self) -> None:
        """REQ-0.22.0-04-01: gz task list shows tasks with status after start."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["task", "list", "OBPI-0.1.0-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("TASK-0.1.0-01-01-01", out)
        self.assertIn("in_progress", out)

    @covers("REQ-0.22.0-04-01")
    def test_list_json(self) -> None:
        """REQ-0.22.0-04-07: gz task list --json returns valid JSON."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["task", "list", "OBPI-0.1.0-01", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["obpi"], "OBPI-0.1.0-01")
        self.assertIsInstance(data["tasks"], list)
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["task_id"], "TASK-0.1.0-01-01-01")


class TestTaskStart(_TaskCliBase):
    """@covers REQ-0.22.0-04-02, REQ-0.22.0-04-03."""

    @covers("REQ-0.22.0-04-02")
    @covers("REQ-0.22.0-04-03")
    def test_start_pending(self) -> None:
        """REQ-0.22.0-04-02: gz task start transitions pending -> in_progress."""
        code, out = _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("Started", out)

    @covers("REQ-0.22.0-04-02")
    @covers("REQ-0.22.0-04-03")
    def test_start_json(self) -> None:
        """REQ-0.22.0-04-07: gz task start --json returns structured output."""
        code, out = _invoke(["task", "start", "TASK-0.1.0-01-01-01", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["event"], "task_started")
        self.assertEqual(data["to_status"], "in_progress")

    @covers("REQ-0.22.0-04-02")
    @covers("REQ-0.22.0-04-03")
    @covers("REQ-0.22.0-04-07")
    def test_start_resume_blocked(self) -> None:
        """REQ-0.22.0-04-03: gz task start on blocked task resumes to in_progress."""
        self._seed_task_started()
        _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "blocked"])
        code, out = _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("Resumed", out)


class TestTaskComplete(_TaskCliBase):
    """@covers REQ-0.22.0-04-04, REQ-0.22.0-04-08."""

    @covers("REQ-0.22.0-04-04")
    @covers("REQ-0.22.0-04-08")
    def test_complete_in_progress(self) -> None:
        """REQ-0.22.0-04-04: gz task complete transitions in_progress -> completed."""
        self._seed_task_started()
        code, out = _invoke(["task", "complete", "TASK-0.1.0-01-01-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("Completed", out)

    @covers("REQ-0.22.0-04-04")
    @covers("REQ-0.22.0-04-08")
    def test_complete_pending_fails(self) -> None:
        """REQ-0.22.0-04-08: gz task complete on pending task fails with exit 1."""
        code, out = _invoke(["task", "complete", "TASK-0.1.0-01-01-01"])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid TASK transition", out)


class TestTaskBlock(_TaskCliBase):
    """@covers REQ-0.22.0-04-05."""

    @covers("REQ-0.22.0-04-05")
    def test_block_in_progress(self) -> None:
        """REQ-0.22.0-04-05: gz task block records reason in ledger."""
        self._seed_task_started()
        code, out = _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "Missing API"])
        self.assertEqual(code, 0, out)
        self.assertIn("Blocked", out)

    @covers("REQ-0.22.0-04-05")
    def test_block_pending_fails(self) -> None:
        code, out = _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "test"])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid TASK transition", out)

    @covers("REQ-0.22.0-04-05")
    def test_block_json(self) -> None:
        self._seed_task_started()
        code, out = _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "API", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["event"], "task_blocked")
        self.assertEqual(data["reason"], "API")


class TestTaskEscalate(_TaskCliBase):
    """@covers REQ-0.22.0-04-06."""

    @covers("REQ-0.22.0-04-06")
    def test_escalate_in_progress(self) -> None:
        """REQ-0.22.0-04-06: gz task escalate records reason."""
        self._seed_task_started()
        code, out = _invoke(
            ["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "Needs human decision"]
        )
        self.assertEqual(code, 0, out)
        self.assertIn("Escalated", out)

    @covers("REQ-0.22.0-04-06")
    def test_escalate_pending_fails(self) -> None:
        code, out = _invoke(["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "test"])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid TASK transition", out)

    @covers("REQ-0.22.0-04-06")
    def test_escalate_json(self) -> None:
        self._seed_task_started()
        code, out = _invoke(
            ["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "Complex", "--json"]
        )
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["event"], "task_escalated")
        self.assertEqual(data["reason"], "Complex")


# ---------------------------------------------------------------------------
# Status and state integration (OBPI-0.22.0-05)
# ---------------------------------------------------------------------------


class TestStatusTaskSummary(_TaskCliBase):
    """@covers REQ-0.22.0-05-01, REQ-0.22.0-05-02, REQ-0.22.0-05-04, REQ-0.22.0-05-05."""

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_shows_task_summary_when_tasks_exist(self) -> None:
        """REQ-0.22.0-05-01: gz status shows task summary when tasks exist."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["status"])
        self.assertEqual(code, 0, out)
        self.assertIn("Tasks:", out)
        self.assertIn("1 active", out)

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_no_task_section_when_no_tasks(self) -> None:
        """REQ-0.22.0-05-05: gz status shows no task section when no tasks exist."""
        code, out = _invoke(["status"])
        self.assertEqual(code, 0, out)
        self.assertNotIn("Tasks:", out)

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_json_includes_task_summary(self) -> None:
        """REQ-0.22.0-05-01: gz status --json includes task_summary when tasks exist."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["status", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        adr_data = data["adrs"].get("ADR-0.1.0", {})
        self.assertIn("task_summary", adr_data)
        ts = adr_data["task_summary"]
        self.assertEqual(ts["total"], 1)
        self.assertEqual(ts["in_progress"], 1)

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_json_no_task_summary_when_no_tasks(self) -> None:
        """REQ-0.22.0-05-05: gz status --json omits task_summary when no tasks."""
        code, out = _invoke(["status", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        adr_data = data["adrs"].get("ADR-0.1.0", {})
        self.assertNotIn("task_summary", adr_data)

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_shows_escalated_count(self) -> None:
        """REQ-0.22.0-05-04: Escalated count visible in task summary."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        _invoke(["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "Needs review"])
        code, out = _invoke(["status"])
        self.assertEqual(code, 0, out)
        self.assertIn("Tasks:", out)
        self.assertIn("1 escalated", out)

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_shows_tracing_policy(self) -> None:
        """REQ-0.22.0-05-05: Task tracing policy (advisory/required) is shown."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["status"])
        self.assertEqual(code, 0, out)
        self.assertIn("tracing:", out)

    @covers("REQ-0.22.0-05-01")
    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-04")
    @covers("REQ-0.22.0-05-05")
    def test_status_json_includes_tracing_policy(self) -> None:
        """REQ-0.22.0-05-05: JSON output includes tracing_policy field."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["status", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        adr_data = data["adrs"].get("ADR-0.1.0", {})
        ts = adr_data["task_summary"]
        self.assertIn("tracing_policy", ts)
        self.assertIn(ts["tracing_policy"], ("advisory", "required"))


class TestStateTaskIntegration(_TaskCliBase):
    """@covers REQ-0.22.0-05-02, REQ-0.22.0-05-03, REQ-0.22.0-05-05."""

    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-03")
    @covers("REQ-0.22.0-05-05")
    def test_state_json_includes_task_data(self) -> None:
        """REQ-0.22.0-05-02: gz state --json includes task data per OBPI."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["state", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        obpi_data = data.get("OBPI-0.1.0-01", {})
        self.assertIn("task_summary", obpi_data)
        ts = obpi_data["task_summary"]
        self.assertEqual(ts["total"], 1)
        self.assertEqual(ts["in_progress"], 1)

    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-03")
    @covers("REQ-0.22.0-05-05")
    def test_state_json_no_task_data_when_no_tasks(self) -> None:
        """REQ-0.22.0-05-05: gz state --json omits task_summary when no tasks."""
        code, out = _invoke(["state", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        obpi_data = data.get("OBPI-0.1.0-01", {})
        self.assertNotIn("task_summary", obpi_data)

    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-03")
    @covers("REQ-0.22.0-05-05")
    def test_state_json_task_summary_counts(self) -> None:
        """REQ-0.22.0-05-03: Task summary shows correct counts by status."""
        # Start two tasks, complete one, block another
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        _invoke(["task", "complete", "TASK-0.1.0-01-01-01"])
        _invoke(["task", "start", "TASK-0.1.0-01-01-02"])
        _invoke(["task", "block", "TASK-0.1.0-01-01-02", "--reason", "API"])
        code, out = _invoke(["state", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        obpi_data = data.get("OBPI-0.1.0-01", {})
        ts = obpi_data["task_summary"]
        self.assertEqual(ts["total"], 2)
        self.assertEqual(ts["completed"], 1)
        self.assertEqual(ts["blocked"], 1)

    @covers("REQ-0.22.0-05-02")
    @covers("REQ-0.22.0-05-03")
    @covers("REQ-0.22.0-05-05")
    def test_state_json_task_tracing_policy(self) -> None:
        """REQ-0.22.0-05-05: Task tracing policy in state JSON."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["state", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        obpi_data = data.get("OBPI-0.1.0-01", {})
        ts = obpi_data["task_summary"]
        self.assertIn("tracing_policy", ts)
        self.assertIn(ts["tracing_policy"], ("advisory", "required"))


if __name__ == "__main__":
    unittest.main()
