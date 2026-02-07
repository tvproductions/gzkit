"""Ledger system for tracking governance events.

The ledger is an append-only JSONL file that records all governance events.
State is derived from the ledger, not stored separately.
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LEDGER_SCHEMA = "gzkit.ledger.v1"


@dataclass
class LedgerEvent:
    """A governance event recorded in the ledger.

    All events have:
    - schema: Always "gzkit.ledger.v1"
    - event: Event type (e.g., "project_init", "adr_created")
    - id: Artifact identifier
    - ts: ISO 8601 UTC timestamp

    Event-specific fields are stored in extra.
    """

    event: str
    id: str
    ts: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema: str = LEDGER_SCHEMA
    parent: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "schema": self.schema,
            "event": self.event,
            "id": self.id,
            "ts": self.ts,
        }
        if self.parent:
            result["parent"] = self.parent
        if self.extra:
            result.update(self.extra)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LedgerEvent":
        """Create event from dictionary."""
        # Extract known fields
        event = data.get("event", "")
        id_ = data.get("id", "")
        ts = data.get("ts", "")
        schema = data.get("schema", LEDGER_SCHEMA)
        parent = data.get("parent")

        # Everything else goes in extra
        extra_keys = set(data.keys()) - {"schema", "event", "id", "ts", "parent"}
        extra = {k: data[k] for k in extra_keys}

        return cls(
            event=event,
            id=id_,
            ts=ts,
            schema=schema,
            parent=parent,
            extra=extra,
        )


# Event factory functions for type safety and documentation
def project_init_event(project_name: str, mode: str) -> LedgerEvent:
    """Create a project initialization event."""
    return LedgerEvent(
        event="project_init",
        id=project_name,
        extra={"mode": mode},
    )


def prd_created_event(prd_id: str) -> LedgerEvent:
    """Create a PRD created event."""
    return LedgerEvent(
        event="prd_created",
        id=prd_id,
    )


def constitution_created_event(constitution_id: str) -> LedgerEvent:
    """Create a constitution created event."""
    return LedgerEvent(
        event="constitution_created",
        id=constitution_id,
    )


def obpi_created_event(obpi_id: str, parent: str) -> LedgerEvent:
    """Create an OBPI created event."""
    return LedgerEvent(
        event="obpi_created",
        id=obpi_id,
        parent=parent,
    )


def adr_created_event(adr_id: str, parent: str, lane: str) -> LedgerEvent:
    """Create an ADR created event."""
    return LedgerEvent(
        event="adr_created",
        id=adr_id,
        parent=parent,
        extra={"lane": lane},
    )


def artifact_edited_event(path: str, session: str | None = None) -> LedgerEvent:
    """Create an artifact edited event (from hooks)."""
    extra: dict[str, Any] = {"path": path}
    if session:
        extra["session"] = session
    return LedgerEvent(
        event="artifact_edited",
        id=path,
        extra=extra,
    )


def attested_event(
    adr_id: str,
    status: str,
    by: str,
    reason: str | None = None,
) -> LedgerEvent:
    """Create an attestation event."""
    extra: dict[str, Any] = {"status": status, "by": by}
    if reason:
        extra["reason"] = reason
    return LedgerEvent(
        event="attested",
        id=adr_id,
        extra=extra,
    )


def gate_checked_event(
    adr_id: str,
    gate: int,
    status: str,
    command: str,
    returncode: int,
    evidence: str | None = None,
) -> LedgerEvent:
    """Create a gate checked event."""
    extra: dict[str, Any] = {
        "gate": gate,
        "status": status,
        "command": command,
        "returncode": returncode,
    }
    if evidence:
        extra["evidence"] = evidence
    return LedgerEvent(
        event="gate_checked",
        id=adr_id,
        extra=extra,
    )


def artifact_renamed_event(old_id: str, new_id: str, reason: str | None = None) -> LedgerEvent:
    """Create an artifact rename event used for ID migrations."""
    extra: dict[str, Any] = {"new_id": new_id}
    if reason:
        extra["reason"] = reason
    return LedgerEvent(
        event="artifact_renamed",
        id=old_id,
        extra=extra,
    )


class Ledger:
    """Append-only ledger for governance events.

    The ledger is stored as JSONL (JSON Lines) format - one JSON object per line.
    This enables append-only writes and streaming reads.
    """

    def __init__(self, path: Path):
        """Initialize ledger at the given path.

        Args:
            path: Path to the ledger.jsonl file.
        """
        self.path = path

    def exists(self) -> bool:
        """Check if the ledger file exists."""
        return self.path.exists()

    def create(self) -> None:
        """Create an empty ledger file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()

    def append(self, event: LedgerEvent) -> None:
        """Append an event to the ledger.

        Args:
            event: The event to append.
        """
        if not self.path.exists():
            self.create()

        with open(self.path, "a") as f:
            json.dump(event.to_dict(), f, separators=(",", ":"))
            f.write("\n")

    def read_all(self) -> list[LedgerEvent]:
        """Read all events from the ledger.

        Returns:
            List of all events in chronological order.
        """
        if not self.path.exists():
            return []

        events = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    events.append(LedgerEvent.from_dict(data))

        return events

    def query(
        self,
        event_type: str | None = None,
        artifact_id: str | None = None,
    ) -> list[LedgerEvent]:
        """Query events by type and/or artifact ID.

        Args:
            event_type: Filter by event type (e.g., "adr_created").
            artifact_id: Filter by artifact ID.

        Returns:
            Filtered list of events.
        """
        events = self.read_all()

        if event_type:
            events = [e for e in events if e.event == event_type]

        if artifact_id:
            events = [e for e in events if e.id == artifact_id]

        return events

    def latest_event(self, artifact_id: str) -> LedgerEvent | None:
        """Get the most recent event for an artifact.

        Args:
            artifact_id: The artifact ID to query.

        Returns:
            Most recent event or None if not found.
        """
        events = self.query(artifact_id=artifact_id)
        return events[-1] if events else None

    @staticmethod
    def _build_rename_map(events: list[LedgerEvent]) -> dict[str, str]:
        """Build old->new artifact ID mapping from rename events."""
        rename_map: dict[str, str] = {}
        for event in events:
            if event.event != "artifact_renamed":
                continue
            new_id = event.extra.get("new_id")
            if isinstance(new_id, str) and new_id and new_id != event.id:
                rename_map[event.id] = new_id
        return rename_map

    @staticmethod
    def _canonicalize_with_map(artifact_id: str, rename_map: dict[str, str]) -> str:
        """Resolve an artifact ID through any rename chain."""
        current = artifact_id
        seen: set[str] = set()
        while current in rename_map and current not in seen:
            seen.add(current)
            current = rename_map[current]
        return current

    def canonicalize_id(self, artifact_id: str) -> str:
        """Resolve an artifact ID to the latest canonical identifier."""
        events = self.read_all()
        rename_map = self._build_rename_map(events)
        return self._canonicalize_with_map(artifact_id, rename_map)

    def get_latest_gate_statuses(self, adr_id: str) -> dict[int, str]:
        """Get the latest recorded gate status for an ADR.

        For each gate number, the most recent `gate_checked` event wins.

        Args:
            adr_id: ADR identifier.

        Returns:
            Mapping of gate number to latest status ("pass"/"fail").
        """
        latest: dict[int, str] = {}
        events = self.read_all()
        rename_map = self._build_rename_map(events)
        target_id = self._canonicalize_with_map(adr_id, rename_map)

        for event in events:
            if event.event != "gate_checked":
                continue
            if self._canonicalize_with_map(event.id, rename_map) != target_id:
                continue

            gate_value = event.extra.get("gate")
            status = event.extra.get("status")

            gate: int | None = None
            if isinstance(gate_value, int):
                gate = gate_value
            elif isinstance(gate_value, str) and gate_value.isdigit():
                gate = int(gate_value)

            if gate is None or not isinstance(status, str):
                continue

            latest[gate] = status

        return latest

    def get_artifact_graph(self) -> dict[str, dict[str, Any]]:
        """Build a graph of artifacts and their relationships.

        Returns:
            Dictionary mapping artifact IDs to their info and relationships.
        """
        graph: dict[str, dict[str, Any]] = {}
        events = self.read_all()
        rename_map = self._build_rename_map(events)
        creation_events = (
            "prd_created",
            "constitution_created",
            "obpi_created",
            "adr_created",
        )

        for event in events:
            canonical_id = self._canonicalize_with_map(event.id, rename_map)
            canonical_parent = (
                self._canonicalize_with_map(event.parent, rename_map) if event.parent else None
            )

            if event.event in creation_events and canonical_id not in graph:
                graph[canonical_id] = {
                    "type": event.event.replace("_created", ""),
                    "created": event.ts,
                    "parent": canonical_parent,
                    "children": [],
                    "attested": False,
                }

            # Track parent-child relationships
            if (
                canonical_parent
                and canonical_parent in graph
                and canonical_id not in graph[canonical_parent]["children"]
            ):
                graph[canonical_parent]["children"].append(canonical_id)

            if event.event == "attested" and canonical_id in graph:
                graph[canonical_id]["attested"] = True
                graph[canonical_id]["attestation_status"] = event.extra.get("status")
                graph[canonical_id]["attestation_by"] = event.extra.get("by")

        return graph

    def get_pending_attestations(self) -> list[str]:
        """Get artifact IDs that need attestation.

        Returns:
            List of artifact IDs without attestation events.
        """
        graph = self.get_artifact_graph()
        return [
            artifact_id
            for artifact_id, info in graph.items()
            if info["type"] == "adr" and not info["attested"]
        ]
