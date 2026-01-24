"""Tests for gzkit ledger system."""

import tempfile
import unittest
from pathlib import Path

from gzkit.ledger import (
    Ledger,
    LedgerEvent,
    adr_created_event,
    attested_event,
    constitution_created_event,
    obpi_created_event,
    prd_created_event,
    project_init_event,
)


class TestLedgerEvent(unittest.TestCase):
    """Tests for LedgerEvent dataclass."""

    def test_to_dict(self) -> None:
        """Event converts to dictionary correctly."""
        event = LedgerEvent(
            event="test_event",
            id="test-id",
            ts="2026-01-01T00:00:00+00:00",
        )
        d = event.to_dict()
        self.assertEqual(d["event"], "test_event")
        self.assertEqual(d["id"], "test-id")
        self.assertEqual(d["schema"], "gzkit.ledger.v1")

    def test_from_dict(self) -> None:
        """Event parses from dictionary correctly."""
        data = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.1.0",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "OBPI-core",
            "lane": "lite",
        }
        event = LedgerEvent.from_dict(data)
        self.assertEqual(event.event, "adr_created")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.parent, "OBPI-core")
        self.assertEqual(event.extra["lane"], "lite")


class TestEventFactories(unittest.TestCase):
    """Tests for event factory functions."""

    def test_project_init_event(self) -> None:
        """project_init_event creates correct event."""
        event = project_init_event("myproject", "lite")
        self.assertEqual(event.event, "project_init")
        self.assertEqual(event.id, "myproject")
        self.assertEqual(event.extra["mode"], "lite")

    def test_prd_created_event(self) -> None:
        """prd_created_event creates correct event."""
        event = prd_created_event("PRD-TEST-1.0.0")
        self.assertEqual(event.event, "prd_created")
        self.assertEqual(event.id, "PRD-TEST-1.0.0")

    def test_constitution_created_event(self) -> None:
        """constitution_created_event creates correct event."""
        event = constitution_created_event("charter")
        self.assertEqual(event.event, "constitution_created")
        self.assertEqual(event.id, "charter")

    def test_obpi_created_event(self) -> None:
        """obpi_created_event creates correct event with parent."""
        event = obpi_created_event("OBPI-core", "ADR-0.1.0")
        self.assertEqual(event.event, "obpi_created")
        self.assertEqual(event.id, "OBPI-core")
        self.assertEqual(event.parent, "ADR-0.1.0")

    def test_adr_created_event(self) -> None:
        """adr_created_event creates correct event with parent and lane."""
        event = adr_created_event("ADR-0.1.0", "OBPI-core", "lite")
        self.assertEqual(event.event, "adr_created")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.parent, "OBPI-core")
        self.assertEqual(event.extra["lane"], "lite")

    def test_attested_event(self) -> None:
        """attested_event creates correct event."""
        event = attested_event("ADR-0.1.0", "completed", "testuser", "All done")
        self.assertEqual(event.event, "attested")
        self.assertEqual(event.id, "ADR-0.1.0")
        self.assertEqual(event.extra["status"], "completed")
        self.assertEqual(event.extra["by"], "testuser")
        self.assertEqual(event.extra["reason"], "All done")


class TestLedger(unittest.TestCase):
    """Tests for Ledger class."""

    def test_create(self) -> None:
        """Ledger creates empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / ".gzkit" / "ledger.jsonl"
            ledger = Ledger(ledger_path)
            ledger.create()
            self.assertTrue(ledger_path.exists())

    def test_append_and_read(self) -> None:
        """Ledger appends and reads events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            event1 = prd_created_event("PRD-1")
            event2 = obpi_created_event("OBPI-1", "ADR-0.1.0")

            ledger.append(event1)
            ledger.append(event2)

            events = ledger.read_all()
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].id, "PRD-1")
            self.assertEqual(events[1].id, "OBPI-1")

    def test_query_by_type(self) -> None:
        """Ledger queries events by type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(prd_created_event("PRD-1"))
            ledger.append(obpi_created_event("OBPI-1", "ADR-0.1.0"))
            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))

            prds = ledger.query(event_type="prd_created")
            self.assertEqual(len(prds), 1)
            self.assertEqual(prds[0].id, "PRD-1")

    def test_query_by_artifact_id(self) -> None:
        """Ledger queries events by artifact ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "user"))

            events = ledger.query(artifact_id="ADR-0.1.0")
            self.assertEqual(len(events), 2)

    def test_get_artifact_graph(self) -> None:
        """Ledger builds artifact graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(prd_created_event("PRD-1"))
            ledger.append(obpi_created_event("OBPI-1", "ADR-0.1.0"))
            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "user"))

            graph = ledger.get_artifact_graph()
            self.assertIn("PRD-1", graph)
            self.assertIn("OBPI-1", graph)
            self.assertIn("ADR-0.1.0", graph)
            self.assertTrue(graph["ADR-0.1.0"]["attested"])

    def test_get_pending_attestations(self) -> None:
        """Ledger finds ADRs without attestation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            ledger.append(adr_created_event("ADR-0.1.0", "OBPI-1", "lite"))
            ledger.append(adr_created_event("ADR-0.2.0", "OBPI-1", "lite"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "user"))

            pending = ledger.get_pending_attestations()
            self.assertEqual(pending, ["ADR-0.2.0"])


if __name__ == "__main__":
    unittest.main()
