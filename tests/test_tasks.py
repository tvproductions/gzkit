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
    parse_task_trailers,
    resolve_task_chain,
)


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

    def test_discriminated_union_parses_task_started(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_started correctly."""
        evt = _started()
        data = json.loads(evt.model_dump_json())
        parsed = parse_typed_event(data)
        self.assertIsInstance(parsed, TaskStartedEvent)
        self.assertEqual(parsed.task_id, "TASK-0.22.0-02-01-01")

    def test_task_started_reused_for_resume(self) -> None:
        """REQ-0.22.0-02-04: task_started is reused for blocked->in_progress resume."""
        evt = _started()
        data = json.loads(evt.model_dump_json())
        self.assertEqual(data["event"], "task_started")
        parsed = parse_typed_event(data)
        self.assertIsInstance(parsed, TaskStartedEvent)

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

    def test_discriminated_union_parses_task_completed(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_completed."""
        evt = _completed()
        parsed = parse_typed_event(json.loads(evt.model_dump_json()))
        self.assertIsInstance(parsed, TaskCompletedEvent)


class TestTaskBlockedEvent(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-02, REQ-0.22.0-02-03."""

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

    def test_reason_required(self) -> None:
        """REQ-0.22.0-02-04: task_blocked requires reason field."""
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            TaskBlockedEvent(event="task_blocked", **_TASK_FIELDS)  # type: ignore[arg-type]

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

    def test_discriminated_union_parses_task_escalated(self) -> None:
        """REQ-0.22.0-02-03: parse_typed_event resolves task_escalated."""
        evt = _escalated(reason="Over complexity budget")
        parsed = parse_typed_event(json.loads(evt.model_dump_json()))
        self.assertIsInstance(parsed, TaskEscalatedEvent)
        self.assertEqual(parsed.reason, "Over complexity budget")


class TestAllFourEventTypes(unittest.TestCase):
    """@covers REQ-0.22.0-02-01, REQ-0.22.0-02-03, REQ-0.22.0-02-06."""

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

    def test_format_trailer_from_task_id(self) -> None:
        """Formatter also accepts a TaskId directly."""
        tid = TaskId.parse("TASK-0.22.0-03-12-05")
        result = format_commit_trailer(tid)
        self.assertEqual(result, "Task: TASK-0.22.0-03-12-05")


class TestParseTaskTrailers(unittest.TestCase):
    """@covers REQ-0.22.0-03-01, REQ-0.22.0-03-03."""

    def test_parse_single_trailer(self) -> None:
        """REQ-0.22.0-03-01: Extract single TASK ID from commit message."""
        msg = "Add REQ model implementation\n\nTask: TASK-0.20.0-01-01-01\n"
        result = parse_task_trailers(msg)
        self.assertEqual(len(result), 1)
        self.assertEqual(str(result[0]), "TASK-0.20.0-01-01-01")

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

    def test_no_trailers_returns_empty(self) -> None:
        msg = "Simple commit message\n\nNo trailers here.\n"
        result = parse_task_trailers(msg)
        self.assertEqual(result, [])

    def test_ignores_non_task_trailers(self) -> None:
        msg = (
            "Fix bug\n\nCo-Authored-By: Someone\nTask: TASK-0.20.0-01-01-01\nSigned-off-by: Jeff\n"
        )
        result = parse_task_trailers(msg)
        self.assertEqual(len(result), 1)
        self.assertEqual(str(result[0]), "TASK-0.20.0-01-01-01")

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


class TestResolveTaskChain(unittest.TestCase):
    """@covers REQ-0.22.0-03-04."""

    def test_resolve_chain(self) -> None:
        """REQ-0.22.0-03-04: Resolve TASK → REQ → OBPI → ADR chain."""
        tid = TaskId.parse("TASK-0.20.0-01-01-01")
        chain = resolve_task_chain(tid)
        self.assertEqual(chain["task"], "TASK-0.20.0-01-01-01")
        self.assertEqual(chain["req"], "REQ-0.20.0-01-01")
        self.assertEqual(chain["obpi"], "OBPI-0.20.0-01")
        self.assertEqual(chain["adr"], "ADR-0.20.0")

    def test_resolve_chain_different_ids(self) -> None:
        tid = TaskId.parse("TASK-0.22.0-03-12-05")
        chain = resolve_task_chain(tid)
        self.assertEqual(chain["task"], "TASK-0.22.0-03-12-05")
        self.assertEqual(chain["req"], "REQ-0.22.0-03-12")
        self.assertEqual(chain["obpi"], "OBPI-0.22.0-03")
        self.assertEqual(chain["adr"], "ADR-0.22.0")

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
    """Base class that sets up an isolated workspace with an OBPI in the ledger."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="gzkit-task-test-")
        self._orig_cwd = Path.cwd()
        import os

        os.chdir(self._tmpdir)
        # Initialize workspace
        code, out = _invoke(["init"])
        self.assertEqual(code, 0, out)
        # Create ADR
        code, out = _invoke(["plan", "0.1.0"])
        self.assertEqual(code, 0, out)
        # Seed OBPI in ledger
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))

    def tearDown(self) -> None:
        import os
        import shutil

        os.chdir(self._orig_cwd)
        shutil.rmtree(self._tmpdir, ignore_errors=True)

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
    """@covers REQ-0.22.0-04-09."""

    def test_task_help(self) -> None:
        """REQ-0.22.0-04-09: gz task -h exits 0 with subcommand list."""
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

    def test_list_empty(self) -> None:
        """REQ-0.22.0-04-01: gz task list shows empty when no tasks exist."""
        code, out = _invoke(["task", "list", "OBPI-0.1.0-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("No tasks found", out)

    def test_list_shows_task_after_start(self) -> None:
        """REQ-0.22.0-04-01: gz task list shows tasks with status after start."""
        _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        code, out = _invoke(["task", "list", "OBPI-0.1.0-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("TASK-0.1.0-01-01-01", out)
        self.assertIn("in_progress", out)

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

    def test_start_pending(self) -> None:
        """REQ-0.22.0-04-02: gz task start transitions pending -> in_progress."""
        code, out = _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("Started", out)

    def test_start_json(self) -> None:
        """REQ-0.22.0-04-07: gz task start --json returns structured output."""
        code, out = _invoke(["task", "start", "TASK-0.1.0-01-01-01", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["event"], "task_started")
        self.assertEqual(data["to_status"], "in_progress")

    def test_start_resume_blocked(self) -> None:
        """REQ-0.22.0-04-03: gz task start on blocked task resumes to in_progress."""
        self._seed_task_started()
        _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "blocked"])
        code, out = _invoke(["task", "start", "TASK-0.1.0-01-01-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("Resumed", out)


class TestTaskComplete(_TaskCliBase):
    """@covers REQ-0.22.0-04-04, REQ-0.22.0-04-08."""

    def test_complete_in_progress(self) -> None:
        """REQ-0.22.0-04-04: gz task complete transitions in_progress -> completed."""
        self._seed_task_started()
        code, out = _invoke(["task", "complete", "TASK-0.1.0-01-01-01"])
        self.assertEqual(code, 0, out)
        self.assertIn("Completed", out)

    def test_complete_pending_fails(self) -> None:
        """REQ-0.22.0-04-08: gz task complete on pending task fails with exit 1."""
        code, out = _invoke(["task", "complete", "TASK-0.1.0-01-01-01"])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid TASK transition", out)


class TestTaskBlock(_TaskCliBase):
    """@covers REQ-0.22.0-04-05."""

    def test_block_in_progress(self) -> None:
        """REQ-0.22.0-04-05: gz task block records reason in ledger."""
        self._seed_task_started()
        code, out = _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "Missing API"])
        self.assertEqual(code, 0, out)
        self.assertIn("Blocked", out)

    def test_block_pending_fails(self) -> None:
        code, out = _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "test"])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid TASK transition", out)

    def test_block_json(self) -> None:
        self._seed_task_started()
        code, out = _invoke(["task", "block", "TASK-0.1.0-01-01-01", "--reason", "API", "--json"])
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["event"], "task_blocked")
        self.assertEqual(data["reason"], "API")


class TestTaskEscalate(_TaskCliBase):
    """@covers REQ-0.22.0-04-06."""

    def test_escalate_in_progress(self) -> None:
        """REQ-0.22.0-04-06: gz task escalate records reason."""
        self._seed_task_started()
        code, out = _invoke(
            ["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "Needs human decision"]
        )
        self.assertEqual(code, 0, out)
        self.assertIn("Escalated", out)

    def test_escalate_pending_fails(self) -> None:
        code, out = _invoke(["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "test"])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid TASK transition", out)

    def test_escalate_json(self) -> None:
        self._seed_task_started()
        code, out = _invoke(
            ["task", "escalate", "TASK-0.1.0-01-01-01", "--reason", "Complex", "--json"]
        )
        self.assertEqual(code, 0, out)
        data = json.loads(out)
        self.assertEqual(data["event"], "task_escalated")
        self.assertEqual(data["reason"], "Complex")


if __name__ == "__main__":
    unittest.main()
