"""Tests for optional task_id field on 8 worklog event models (OBPI-0.0.64-01).

Coverage:
    REQ-0.0.64-01-01 — each of the 8 worklog event models accepts task_id=None
        and a canonical TASK ID string.
    REQ-0.0.64-01-02 — each of the 8 worklog event models rejects unknown fields
        via ValidationError (extra="forbid").
    REQ-0.0.64-01-03 — ledger.json schema admits legacy events (no task_id key)
        and new-shape events (task_id present as string) for each of the 8 event
        types.
    REQ-0.0.64-01-04 — the 4 TASK-boundary event models are not altered by this
        OBPI; their model_fields keysets remain unchanged.
    REQ-0.0.64-01-05 — the 8 worklog event types in ledger.json carry a task_id
        property that is NOT in the event's required array.
    REQ-0.0.64-01-06 — auto_start_obpi_tasks and auto_complete_obpi_tasks
        function names still exist in src/gzkit/commands/task.py (structural-
        fence regression guard).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from gzkit.events import (
    ArtifactEditedEvent,
    ArtifactRenamedEvent,
    AttestedEvent,
    AuditReceiptEmittedEvent,
    CompositionRenderedEvent,
    GateCheckedEvent,
    IntrinsicComplexityAttestationEvent,
    ObpiCompletionUncoveredAcceptEvent,
    TaskBlockedEvent,
    TaskCompletedEvent,
    TaskEscalatedEvent,
    TaskStartedEvent,
)
from gzkit.ledger import LEDGER_SCHEMA
from gzkit.schemas import load_schema
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TASK_ID = "TASK-0.0.64-01-01-01"
_EVT_ID = "test-evt-001"

# The 8 worklog event classes under test
_WORKLOG_EVENT_CLASSES = [
    ArtifactEditedEvent,
    AttestedEvent,
    GateCheckedEvent,
    AuditReceiptEmittedEvent,
    ArtifactRenamedEvent,
    ObpiCompletionUncoveredAcceptEvent,
    IntrinsicComplexityAttestationEvent,
    CompositionRenderedEvent,
]

# Minimal required constructor kwargs for each worklog event class
_WORKLOG_EVENT_KWARGS: dict[type, dict] = {
    ArtifactEditedEvent: {
        "event": "artifact_edited",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "path": "/some/file.py",
    },
    AttestedEvent: {
        "event": "attested",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "status": "completed",
        "by": "Jeffry",
    },
    GateCheckedEvent: {
        "event": "gate_checked",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "gate": 2,
        "status": "pass",
        "command": "uv run -m unittest -q",
        "returncode": 0,
    },
    AuditReceiptEmittedEvent: {
        "event": "audit_receipt_emitted",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "receipt_event": "completed",
        "attestor": "Jeffry",
    },
    ArtifactRenamedEvent: {
        "event": "artifact_renamed",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "new_id": "ADR-0.0.64-renamed",
    },
    ObpiCompletionUncoveredAcceptEvent: {
        "event": "obpi_completion_uncovered_accept",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "obpi_id": "OBPI-0.0.64-01",
        "req_id": "REQ-0.0.64-01-01",
        "operator": "Jeffry",
        "rationale": "field is optional; legacy events grandfather unchanged",
        "acceptance_type": "human",
    },
    IntrinsicComplexityAttestationEvent: {
        "event": "intrinsic-complexity-attestation",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "file_path": "src/gzkit/events.py",
        "qualname": "parse_typed_event",
        "reason": "irreducible dispatch",
        "attestor": "Jeffry",
        "attestation_date": "2026-05-28",
        "metric": "radon_cc",
        "crossing_band": "advise",
        "crossing_value": 12.0,
    },
    CompositionRenderedEvent: {
        "event": "composition_rendered",
        "id": _EVT_ID,
        "schema_": LEDGER_SCHEMA,
        "invariant_count": 10,
        "target": "AGENTS.md",
        "byte_count": 40000,
        "render_ts": "2026-05-28T00:00:00+00:00",
    },
}

# The 8 JSON schema event keys in ledger.json
_SCHEMA_EVENT_KEYS = [
    "artifact_edited",
    "attested",
    "gate_checked",
    "audit_receipt_emitted",
    "artifact_renamed",
    "obpi_completion_uncovered_accept",
    "intrinsic-complexity-attestation",
    "composition_rendered",
]

# The 4 TASK-boundary event classes and their expected pre-OBPI-01 field names
_TASK_BOUNDARY_CLASSES = [
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskBlockedEvent,
    TaskEscalatedEvent,
]


# ---------------------------------------------------------------------------
# REQ-0.0.64-01-01: task_id field accepts None and a valid TASK ID string
# ---------------------------------------------------------------------------


class TestTaskIdFieldAccepted(unittest.TestCase):
    """REQ-0.0.64-01-01: worklog events accept task_id=None and a TASK ID string."""

    @covers("REQ-0.0.64-01-01")
    def test_task_id_none_accepted_on_all_worklog_events(self) -> None:
        """Each worklog event model accepts task_id=None without raising."""
        for cls in _WORKLOG_EVENT_CLASSES:
            kwargs = dict(_WORKLOG_EVENT_KWARGS[cls])
            kwargs["task_id"] = None
            with self.subTest(event_class=cls.__name__):
                instance = cls(**kwargs)
                self.assertIsNone(instance.task_id)

    @covers("REQ-0.0.64-01-01")
    def test_task_id_string_accepted_on_all_worklog_events(self) -> None:
        """Each worklog event model accepts a canonical TASK ID string."""
        for cls in _WORKLOG_EVENT_CLASSES:
            kwargs = dict(_WORKLOG_EVENT_KWARGS[cls])
            kwargs["task_id"] = _TASK_ID
            with self.subTest(event_class=cls.__name__):
                instance = cls(**kwargs)
                self.assertEqual(instance.task_id, _TASK_ID)

    @covers("REQ-0.0.64-01-01")
    def test_task_id_defaults_to_none_when_omitted(self) -> None:
        """Each worklog event model defaults task_id to None when the kwarg is omitted."""
        for cls in _WORKLOG_EVENT_CLASSES:
            kwargs = dict(_WORKLOG_EVENT_KWARGS[cls])
            with self.subTest(event_class=cls.__name__):
                instance = cls(**kwargs)
                self.assertIsNone(instance.task_id)


# ---------------------------------------------------------------------------
# REQ-0.0.64-01-02: extra="forbid" guard rejects unknown fields
# ---------------------------------------------------------------------------


class TestExtraFieldForbidden(unittest.TestCase):
    """REQ-0.0.64-01-02: worklog events reject unknown fields via extra="forbid"."""

    @covers("REQ-0.0.64-01-02")
    def test_garbage_field_raises_validation_error_on_all_worklog_events(self) -> None:
        """Each worklog event raises ValidationError when an unknown field is passed."""
        for cls in _WORKLOG_EVENT_CLASSES:
            kwargs = dict(_WORKLOG_EVENT_KWARGS[cls])
            kwargs["garbage"] = "x"
            with self.subTest(event_class=cls.__name__), self.assertRaises(ValidationError):
                cls(**kwargs)


# ---------------------------------------------------------------------------
# REQ-0.0.64-01-03: ledger.json schema passes legacy and new-shape events
# ---------------------------------------------------------------------------


class TestLedgerSchemaAdmitsTaskId(unittest.TestCase):
    """REQ-0.0.64-01-03: ledger.json schema admits legacy and new-shape events."""

    def setUp(self) -> None:
        self._schema = load_schema("ledger")
        self._event_rules: dict = self._schema.get("events", {})

    @covers("REQ-0.0.64-01-03")
    def test_legacy_event_without_task_id_has_no_missing_required(self) -> None:
        """A legacy event payload (no task_id) has all required fields satisfied.

        For each of the 8 event types, build the minimal required payload and
        assert that task_id is NOT in the event's required list — meaning the
        legacy payload needs no change to pass required-field validation.
        """
        for event_key in _SCHEMA_EVENT_KEYS:
            with self.subTest(event_key=event_key):
                rule = self._event_rules.get(event_key)
                self.assertIsNotNone(rule, f"Event key {event_key!r} missing from ledger.json")
                required = rule.get("required", [])
                self.assertNotIn(
                    "task_id",
                    required,
                    f"task_id must NOT be required for {event_key!r} (legacy compat)",
                )

    @covers("REQ-0.0.64-01-03")
    def test_new_shape_event_with_task_id_matches_schema_property(self) -> None:
        """A new-shape event payload (task_id as string) satisfies the schema property.

        For each of the 8 event types, assert that the schema properties dict
        carries a task_id entry whose type admits strings.
        """
        for event_key in _SCHEMA_EVENT_KEYS:
            with self.subTest(event_key=event_key):
                rule = self._event_rules.get(event_key)
                self.assertIsNotNone(rule, f"Event key {event_key!r} missing from ledger.json")
                properties: dict = rule.get("properties", {})
                self.assertIn(
                    "task_id",
                    properties,
                    f"task_id property missing from ledger.json events.{event_key}.properties",
                )
                task_id_type = properties["task_id"].get("type")
                # Must admit strings — either "string" or ["string", "null"]
                if isinstance(task_id_type, list):
                    self.assertIn("string", task_id_type)
                else:
                    self.assertEqual(task_id_type, "string")


# ---------------------------------------------------------------------------
# REQ-0.0.64-01-04: TASK-boundary event models are NOT changed by this OBPI
# ---------------------------------------------------------------------------


class TestTaskBoundaryEventsUnchanged(unittest.TestCase):
    """REQ-0.0.64-01-04: TASK-boundary event model_fields are not altered by OBPI-01."""

    # Expected model_fields keys for _TaskEventBase subclasses (pre-OBPI-01 baseline).
    # These classes already carry task_id as a required field via _TaskEventBase.
    _EXPECTED_BASE_FIELDS = frozenset(
        {"schema_", "id", "ts", "parent", "task_id", "obpi_id", "adr_id", "agent"}
    )

    @covers("REQ-0.0.64-01-04")
    def test_task_started_fields_unchanged(self) -> None:
        """TaskStartedEvent model_fields contains the expected set of keys."""
        fields = frozenset(TaskStartedEvent.model_fields)
        self.assertIn("task_id", fields, "task_id must be present in TaskStartedEvent")
        # event field is in model_fields too
        expected = self._EXPECTED_BASE_FIELDS | {"event"}
        self.assertEqual(fields, expected)

    @covers("REQ-0.0.64-01-04")
    def test_task_completed_fields_unchanged(self) -> None:
        """TaskCompletedEvent model_fields contains the expected set of keys."""
        fields = frozenset(TaskCompletedEvent.model_fields)
        self.assertIn("task_id", fields, "task_id must be present in TaskCompletedEvent")
        expected = self._EXPECTED_BASE_FIELDS | {"event"}
        self.assertEqual(fields, expected)

    @covers("REQ-0.0.64-01-04")
    def test_task_blocked_fields_unchanged(self) -> None:
        """TaskBlockedEvent model_fields contains the expected set of keys."""
        fields = frozenset(TaskBlockedEvent.model_fields)
        self.assertIn("task_id", fields, "task_id must be present in TaskBlockedEvent")
        expected = self._EXPECTED_BASE_FIELDS | {"event", "reason"}
        self.assertEqual(fields, expected)

    @covers("REQ-0.0.64-01-04")
    def test_task_escalated_fields_unchanged(self) -> None:
        """TaskEscalatedEvent model_fields contains the expected set of keys."""
        fields = frozenset(TaskEscalatedEvent.model_fields)
        self.assertIn("task_id", fields, "task_id must be present in TaskEscalatedEvent")
        expected = self._EXPECTED_BASE_FIELDS | {"event", "reason", "escalated_to"}
        self.assertEqual(fields, expected)


# ---------------------------------------------------------------------------
# REQ-0.0.64-01-05: ledger.json task_id property exists; NOT in required
# ---------------------------------------------------------------------------


class TestLedgerSchemaTaskIdProperty(unittest.TestCase):
    """REQ-0.0.64-01-05: 8 event types carry task_id property; not in required."""

    def setUp(self) -> None:
        self._schema = load_schema("ledger")
        self._event_rules: dict = self._schema.get("events", {})

    @covers("REQ-0.0.64-01-05")
    def test_task_id_in_properties_and_not_in_required_for_all_8_events(self) -> None:
        """task_id property present in all 8 event schemas; absent from required."""
        for event_key in _SCHEMA_EVENT_KEYS:
            with self.subTest(event_key=event_key):
                rule = self._event_rules.get(event_key, {})
                properties = rule.get("properties", {})
                required = rule.get("required", [])
                self.assertIn(
                    "task_id",
                    properties,
                    f"task_id property missing from ledger.json events.{event_key}.properties",
                )
                self.assertNotIn(
                    "task_id",
                    required,
                    f"task_id must not be in required for {event_key!r}",
                )


# ---------------------------------------------------------------------------
# REQ-0.0.64-01-06: structural-fence — auto-coordination call sites unchanged
# ---------------------------------------------------------------------------


class TestAutoCoordinationCallSitesUnchanged(unittest.TestCase):
    """REQ-0.0.64-01-06: auto_start_obpi_tasks / auto_complete_obpi_tasks exist in task.py."""

    @covers("REQ-0.0.64-01-06")
    def test_auto_start_obpi_tasks_defined(self) -> None:
        """auto_start_obpi_tasks is importable from gzkit.commands.task."""
        import gzkit.commands.task as task_mod

        self.assertTrue(
            hasattr(task_mod, "auto_start_obpi_tasks"),
            "auto_start_obpi_tasks not found in gzkit.commands.task",
        )
        self.assertTrue(
            callable(task_mod.auto_start_obpi_tasks),
            "auto_start_obpi_tasks is not callable",
        )

    @covers("REQ-0.0.64-01-06")
    def test_auto_complete_obpi_tasks_defined(self) -> None:
        """auto_complete_obpi_tasks is importable from gzkit.commands.task."""
        import gzkit.commands.task as task_mod

        self.assertTrue(
            hasattr(task_mod, "auto_complete_obpi_tasks"),
            "auto_complete_obpi_tasks not found in gzkit.commands.task",
        )
        self.assertTrue(
            callable(task_mod.auto_complete_obpi_tasks),
            "auto_complete_obpi_tasks is not callable",
        )


if __name__ == "__main__":
    unittest.main()
