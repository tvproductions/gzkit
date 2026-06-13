"""Tests for obpi_completion_repudiated event model and state-resolution semantics.

REQ-0.0.71-01-01 through REQ-0.0.71-01-07 (ADR-0.0.71 OBPI-01).
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

from pydantic import ValidationError

from gzkit.events import ObpiCompletionRepudiatedEvent
from gzkit.ledger import Ledger
from gzkit.ledger_events import (
    obpi_completion_repudiated_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)
from gzkit.traceability import covers  # noqa: F401

_SCHEMA_PATH = Path(__file__).parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"


def _ledger_schema() -> dict:
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


class TestObpiCompletionRepudiatedEventModel(TestCase):
    """REQ-0.0.71-01-01, REQ-0.0.71-01-02: model validation."""

    def _valid_kwargs(self) -> dict:
        return {
            "id": "OBPI-0.0.71-01",
            "event": "obpi_completion_repudiated",
            "repudiated_receipt": "2026-06-13T00:00:00+00:00",
            "cause": "model-induced-fabrication",
            "attestor": "g0",
            "reason": "Agent fabricated Gate-5 attestation.",
        }

    @covers("REQ-0.0.71-01-01")
    def test_empty_attestor_fails_closed(self) -> None:
        """REQ-0.0.71-01-01: empty attestor raises ValidationError (fails closed)."""
        kwargs = self._valid_kwargs()
        kwargs["attestor"] = ""
        with self.assertRaises(ValidationError):
            ObpiCompletionRepudiatedEvent(**kwargs)

    @covers("REQ-0.0.71-01-01")
    def test_empty_reason_fails_closed(self) -> None:
        """REQ-0.0.71-01-01: empty reason raises ValidationError (fails closed)."""
        kwargs = self._valid_kwargs()
        kwargs["reason"] = ""
        with self.assertRaises(ValidationError):
            ObpiCompletionRepudiatedEvent(**kwargs)

    @covers("REQ-0.0.71-01-02")
    def test_invalid_cause_rejected(self) -> None:
        """REQ-0.0.71-01-02: unknown cause value raises ValidationError."""
        kwargs = self._valid_kwargs()
        kwargs["cause"] = "unknown-cause"
        with self.assertRaises(ValidationError):
            ObpiCompletionRepudiatedEvent(**kwargs)

    @covers("REQ-0.0.71-01-01")
    def test_valid_construction_round_trips(self) -> None:
        """REQ-0.0.71-01-01, REQ-0.0.71-01-02: valid event serializes and deserializes."""
        event = ObpiCompletionRepudiatedEvent(**self._valid_kwargs())
        data = event.model_dump()
        self.assertEqual(data["cause"], "model-induced-fabrication")
        self.assertEqual(data["attestor"], "g0")
        self.assertEqual(data["reason"], "Agent fabricated Gate-5 attestation.")

    @covers("REQ-0.0.71-01-02")
    def test_cause_enum_all_valid_values(self) -> None:
        """REQ-0.0.71-01-02: all three valid cause values construct without error."""
        for cause in ("model-induced-fabrication", "operator-error", "verification-invalid"):
            kwargs = self._valid_kwargs()
            kwargs["cause"] = cause
            event = ObpiCompletionRepudiatedEvent(**kwargs)
            self.assertEqual(event.cause, cause)


class TestObpiCompletionRepudiatedStateResolution(TestCase):
    """REQ-0.0.71-01-03, REQ-0.0.71-01-04, REQ-0.0.71-01-05: state-resolution semantics."""

    def _repudiation_event(self, obpi_id: str, parent: str):
        return obpi_completion_repudiated_event(
            obpi_id=obpi_id,
            parent=parent,
            repudiated_receipt="2026-06-13T00:00:00+00:00",
            cause="model-induced-fabrication",
            attestor="g0",
            reason="Agent fabricated Gate-5.",
        )

    def _completion_event(self, obpi_id: str):
        return obpi_receipt_emitted_event(
            obpi_id=obpi_id,
            receipt_event="completed",
            attestor="g0",
            obpi_completion="attested_completed",
        )

    @covers("REQ-0.0.71-01-03")
    def test_repudiation_flips_ledger_completed_false(self) -> None:
        """REQ-0.0.71-01-03: applying repudiation event sets ledger_completed=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(Path(tmpdir) / "ledger.jsonl")
            obpi_id, parent = "OBPI-0.0.71-01", "ADR-0.0.71"
            ledger.append(obpi_created_event(obpi_id, parent))
            ledger.append(self._completion_event(obpi_id))
            graph = ledger.get_artifact_graph()
            self.assertTrue(graph[obpi_id]["ledger_completed"])

            ledger.append(self._repudiation_event(obpi_id, parent))
            graph = ledger.get_artifact_graph()
            self.assertFalse(graph[obpi_id]["ledger_completed"])

    @covers("REQ-0.0.71-01-03")
    def test_repudiation_sets_repudiated_true(self) -> None:
        """REQ-0.0.71-01-03: repudiation sets repudiated=True on the OBPI node."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(Path(tmpdir) / "ledger.jsonl")
            obpi_id, parent = "OBPI-0.0.71-01", "ADR-0.0.71"
            ledger.append(obpi_created_event(obpi_id, parent))
            ledger.append(self._completion_event(obpi_id))
            ledger.append(self._repudiation_event(obpi_id, parent))
            graph = ledger.get_artifact_graph()
            self.assertTrue(graph[obpi_id].get("repudiated"))
            self.assertEqual(graph[obpi_id].get("repudiated_reason"), "Agent fabricated Gate-5.")

    @covers("REQ-0.0.71-01-03")
    def test_repudiation_does_not_set_withdrawn(self) -> None:
        """REQ-0.0.71-01-03: repudiation NEVER sets withdrawn (reverses, does not retire)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(Path(tmpdir) / "ledger.jsonl")
            obpi_id, parent = "OBPI-0.0.71-01", "ADR-0.0.71"
            ledger.append(obpi_created_event(obpi_id, parent))
            ledger.append(self._completion_event(obpi_id))
            ledger.append(self._repudiation_event(obpi_id, parent))
            graph = ledger.get_artifact_graph()
            self.assertFalse(graph[obpi_id].get("withdrawn", False))

    @covers("REQ-0.0.71-01-04")
    def test_genuine_recompletion_clears_repudiated(self) -> None:
        """REQ-0.0.71-01-04: subsequent genuine obpi_receipt_emitted clears repudiated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(Path(tmpdir) / "ledger.jsonl")
            obpi_id, parent = "OBPI-0.0.71-01", "ADR-0.0.71"
            ledger.append(obpi_created_event(obpi_id, parent))
            ledger.append(self._completion_event(obpi_id))
            ledger.append(self._repudiation_event(obpi_id, parent))
            graph = ledger.get_artifact_graph()
            self.assertTrue(graph[obpi_id].get("repudiated"))

            # Genuine re-completion clears repudiated
            ledger.append(self._completion_event(obpi_id))
            graph = ledger.get_artifact_graph()
            self.assertFalse(graph[obpi_id].get("repudiated", False))
            self.assertTrue(graph[obpi_id]["ledger_completed"])

    @covers("REQ-0.0.71-01-05")
    def test_repudiated_obpi_visible_in_default_graph(self) -> None:
        """REQ-0.0.71-01-05: repudiated OBPI remains visible in default artifact graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(Path(tmpdir) / "ledger.jsonl")
            obpi_id, parent = "OBPI-0.0.71-01", "ADR-0.0.71"
            ledger.append(obpi_created_event(obpi_id, parent))
            ledger.append(self._completion_event(obpi_id))
            ledger.append(self._repudiation_event(obpi_id, parent))
            # Raw ledger graph does not filter repudiated OBPIs (only withdrawn)
            graph = ledger.get_artifact_graph()
            self.assertIn(obpi_id, graph)
            self.assertTrue(graph[obpi_id].get("repudiated"))
            self.assertFalse(graph[obpi_id].get("withdrawn", False))


class TestObpiCompletionRepudiatedSchemaRoundTrip(TestCase):
    """REQ-0.0.71-01-06: schema entry present and model round-trips."""

    def test_schema_entry_exists(self) -> None:
        """REQ-0.0.71-01-06: obpi_completion_repudiated key present in ledger.json schema."""
        schema = _ledger_schema()
        self.assertIn("obpi_completion_repudiated", schema["events"])

    def test_model_serializes_to_correct_event_key(self) -> None:
        """REQ-0.0.71-01-06: serialized event carries obpi_completion_repudiated key."""
        event = ObpiCompletionRepudiatedEvent(
            id="OBPI-0.0.71-01",
            event="obpi_completion_repudiated",
            repudiated_receipt="2026-06-13T00:00:00+00:00",
            cause="operator-error",
            attestor="g0",
            reason="Test reason.",
        )
        data = event.model_dump()
        self.assertEqual(data["event"], "obpi_completion_repudiated")

    def test_factory_returns_ledger_event_with_correct_event_type(self) -> None:
        """REQ-0.0.71-01-06: factory creates a LedgerEvent with correct event type."""
        ev = obpi_completion_repudiated_event(
            obpi_id="OBPI-0.0.71-01",
            parent="ADR-0.0.71",
            repudiated_receipt="2026-06-13T00:00:00+00:00",
            cause="verification-invalid",
            attestor="g0",
            reason="Verification evidence was fabricated.",
        )
        self.assertEqual(ev.event, "obpi_completion_repudiated")
        self.assertEqual(ev.extra["cause"], "verification-invalid")
        self.assertEqual(ev.extra["attestor"], "g0")


if __name__ == "__main__":
    unittest.main()
