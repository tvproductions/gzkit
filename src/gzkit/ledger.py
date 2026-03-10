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


ATTESTATION_CANONICAL_TERMS: dict[str, str] = {
    "completed": "Completed",
    "partial": "Completed - Partial",
    "dropped": "Dropped",
}

OBPI_RUNTIME_STATES = {
    "pending",
    "in_progress",
    "completed",
    "attested_completed",
    "validated",
    "drift",
}
OBPI_COMPLETED_RUNTIME_STATES = {"completed", "attested_completed", "validated"}
OBPI_PROOF_STATES = {"missing", "partial", "recorded", "validated"}
OBPI_ATTESTATION_REQUIREMENTS = {"required", "optional"}
OBPI_ATTESTATION_STATES = {"not_required", "missing", "recorded"}
REQ_PROOF_INPUT_KINDS = {
    "command",
    "artifact",
    "brief_section",
    "attestation",
    "legacy_key_proof",
}
REQ_PROOF_INPUT_STATUSES = {"present", "missing"}


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


def closeout_initiated_event(
    adr_id: str,
    by: str,
    mode: str,
    evidence: dict[str, Any] | None = None,
) -> LedgerEvent:
    """Create a closeout initiation event."""
    extra: dict[str, Any] = {"by": by, "mode": mode}
    if evidence is not None:
        extra["evidence"] = evidence
    return LedgerEvent(
        event="closeout_initiated",
        id=adr_id,
        extra=extra,
    )


def audit_receipt_emitted_event(
    adr_id: str,
    receipt_event: str,
    attestor: str,
    evidence: dict[str, Any] | None = None,
    anchor: dict[str, str] | None = None,
) -> LedgerEvent:
    """Create an audit receipt event."""
    extra: dict[str, Any] = {"receipt_event": receipt_event, "attestor": attestor}
    if evidence is not None:
        extra["evidence"] = evidence
    if anchor is not None:
        extra["anchor"] = anchor
    return LedgerEvent(
        event="audit_receipt_emitted",
        id=adr_id,
        extra=extra,
    )


def obpi_receipt_emitted_event(
    obpi_id: str,
    receipt_event: str,
    attestor: str,
    evidence: dict[str, Any] | None = None,
    parent_adr: str | None = None,
    obpi_completion: str | None = None,
    anchor: dict[str, str] | None = None,
) -> LedgerEvent:
    """Create an OBPI receipt event."""
    extra: dict[str, Any] = {"receipt_event": receipt_event, "attestor": attestor}
    if evidence is not None:
        extra["evidence"] = evidence
    if obpi_completion is not None:
        extra["obpi_completion"] = obpi_completion
    if anchor is not None:
        extra["anchor"] = anchor
    return LedgerEvent(
        event="obpi_receipt_emitted",
        id=obpi_id,
        parent=parent_adr,
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


def parse_frontmatter_value(content: str, key: str) -> str | None:
    """Extract a single value from YAML frontmatter."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        raw_key, _, raw_value = line.partition(":")
        if raw_key.strip() != key:
            continue
        return raw_value.strip().strip("\"'")
    return None


def resolve_adr_lane(info: dict[str, Any], default_mode: str) -> str:
    """Resolve lane from ADR metadata with mode fallback."""
    lane = str(info.get("lane") or default_mode).lower()
    return lane if lane in {"lite", "heavy"} else default_mode


def _normalize_req_proof_input_item(item: Any) -> dict[str, str] | None:
    """Validate and normalize one REQ-proof input row."""
    if not isinstance(item, dict):
        return None

    name = item.get("name")
    kind = item.get("kind")
    source = item.get("source")
    status = item.get("status", "present")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(kind, str) or kind not in REQ_PROOF_INPUT_KINDS:
        return None
    if not isinstance(source, str) or not source.strip():
        return None
    if not isinstance(status, str) or status not in REQ_PROOF_INPUT_STATUSES:
        return None

    entry = {
        "name": name.strip(),
        "kind": kind,
        "source": source.strip(),
        "status": status,
    }
    for optional_field in ("scope", "gap_reason"):
        optional_value = item.get(optional_field)
        if isinstance(optional_value, str) and optional_value.strip():
            entry[optional_field] = optional_value.strip()
    return entry


def _fallback_req_proof_inputs(
    fallback_key_proof: str | None,
    human_attestation: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Build compatibility proof inputs when structured evidence is absent."""
    normalized: list[dict[str, str]] = []
    if isinstance(fallback_key_proof, str) and fallback_key_proof.strip():
        normalized.append(
            {
                "name": "key_proof",
                "kind": "legacy_key_proof",
                "source": fallback_key_proof.strip(),
                "status": "present",
            }
        )
    if human_attestation and human_attestation.get("valid"):
        attestor = human_attestation.get("attestor", "human")
        attestation_date = human_attestation.get("date", "unknown-date")
        normalized.append(
            {
                "name": "human_attestation",
                "kind": "attestation",
                "source": f"{attestor} @ {attestation_date}",
                "status": "present",
            }
        )
    return normalized


def normalize_req_proof_inputs(
    raw_inputs: Any,
    *,
    fallback_key_proof: str | None = None,
    human_attestation: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Normalize REQ-proof inputs into a stable machine-readable list."""
    if isinstance(raw_inputs, list):
        normalized = [
            entry
            for item in raw_inputs
            if (entry := _normalize_req_proof_input_item(item)) is not None
        ]
        if normalized:
            return normalized

    return _fallback_req_proof_inputs(fallback_key_proof, human_attestation)


def summarize_req_proof_inputs(inputs: list[dict[str, str]]) -> dict[str, int | str]:
    """Summarize normalized REQ-proof input state."""
    total = len(inputs)
    present = sum(1 for item in inputs if item.get("status") == "present")
    missing = total - present

    if total == 0:
        state = "missing"
    elif missing == 0:
        state = "recorded"
    elif present == 0:
        state = "missing"
    else:
        state = "partial"

    return {
        "total": total,
        "present": present,
        "missing": missing,
        "state": state,
    }


def _resolve_attestation_requirement(evidence: dict[str, Any], obpi_completion: Any) -> str:
    """Resolve whether explicit human attestation evidence is required."""
    requirement = evidence.get("attestation_requirement")
    if isinstance(requirement, str):
        return requirement
    return "required" if obpi_completion == "attested_completed" else "optional"


def _human_attestation_is_valid(
    human_attestation: dict[str, Any] | None,
    evidence: dict[str, Any],
) -> bool:
    """Return True when human attestation evidence is present and usable."""
    human_attestation_ok = bool(human_attestation and human_attestation.get("valid"))
    if evidence.get("human_attestation") is not True:
        return human_attestation_ok
    attestation_text = evidence.get("attestation_text")
    attestation_date = evidence.get("attestation_date")
    return human_attestation_ok or (
        isinstance(attestation_text, str)
        and bool(attestation_text.strip())
        and isinstance(attestation_date, str)
        and bool(attestation_date.strip())
    )


def _derive_obpi_issues(
    *,
    ledger_completed: bool,
    file_completed: bool,
    found_file: bool,
    latest_receipt_event: Any,
    implementation_evidence_ok: bool,
    key_proof_ok: bool,
    attestation_requirement: str,
    human_attestation_ok: bool,
) -> list[str]:
    """Collect fail-closed OBPI runtime issues."""
    issues: list[str] = []
    if not ledger_completed:
        issues.append("ledger proof of completion is missing")
    if not file_completed and not ledger_completed:
        issues.append("brief file status is not Completed")
    if not found_file and latest_receipt_event:
        issues.append("ledger proof exists but the OBPI brief file is missing")
    if ledger_completed and not file_completed:
        issues.append("ledger says completed but brief file status is not Completed")
    if file_completed and not ledger_completed:
        issues.append("brief file says Completed but ledger proof of completion is missing")
    if latest_receipt_event == "validated" and not ledger_completed:
        issues.append("validated receipt exists without completed proof state")
    if file_completed and not implementation_evidence_ok:
        issues.append("implementation summary is missing or placeholder")
    if file_completed and not key_proof_ok:
        issues.append("key proof is missing or placeholder")
    if attestation_requirement == "required" and file_completed and not human_attestation_ok:
        issues.append("required human attestation evidence is missing")
    return issues


def derive_obpi_semantics(
    info: dict[str, Any],
    *,
    found_file: bool,
    file_completed: bool,
    implementation_evidence_ok: bool,
    key_proof_ok: bool,
    fallback_key_proof: str | None = None,
    human_attestation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive shared OBPI runtime semantics from ledger and brief evidence."""
    latest_receipt_event = info.get("latest_receipt_event")
    obpi_completion = info.get("obpi_completion")
    ledger_completed = bool(info.get("ledger_completed"))
    validated = bool(info.get("validated"))

    evidence = info.get("latest_evidence")
    if not isinstance(evidence, dict):
        evidence = {}

    attestation_requirement = _resolve_attestation_requirement(evidence, obpi_completion)

    req_proof_inputs = normalize_req_proof_inputs(
        evidence.get("req_proof_inputs"),
        fallback_key_proof=fallback_key_proof,
        human_attestation=human_attestation,
    )
    req_proof_summary = summarize_req_proof_inputs(req_proof_inputs)
    req_proof_state = str(req_proof_summary["state"])

    human_attestation_ok = _human_attestation_is_valid(human_attestation, evidence)

    if attestation_requirement == "required":
        attestation_state = "recorded" if human_attestation_ok else "missing"
    else:
        attestation_state = "not_required"

    evidence_ok = implementation_evidence_ok and key_proof_ok

    issues = _derive_obpi_issues(
        ledger_completed=ledger_completed,
        file_completed=file_completed,
        found_file=found_file,
        latest_receipt_event=latest_receipt_event,
        implementation_evidence_ok=implementation_evidence_ok,
        key_proof_ok=key_proof_ok,
        attestation_requirement=attestation_requirement,
        human_attestation_ok=human_attestation_ok,
    )

    runtime_state = "pending"
    if issues and ledger_completed:
        runtime_state = "drift"
    elif validated and ledger_completed and evidence_ok and attestation_state != "missing":
        runtime_state = "validated"
    elif (
        obpi_completion == "attested_completed" and evidence_ok and attestation_state == "recorded"
    ):
        runtime_state = "attested_completed"
    elif obpi_completion == "completed" and evidence_ok:
        runtime_state = "completed"
    elif any(
        [
            latest_receipt_event,
            file_completed,
            implementation_evidence_ok,
            key_proof_ok,
            req_proof_summary["present"],
        ]
    ):
        runtime_state = "in_progress"

    proof_state = "validated" if runtime_state == "validated" else req_proof_state

    completed = runtime_state in OBPI_COMPLETED_RUNTIME_STATES
    return {
        "runtime_state": runtime_state,
        "proof_state": proof_state,
        "attestation_requirement": attestation_requirement,
        "attestation_state": attestation_state,
        "req_proof_state": req_proof_state,
        "req_proof_inputs": req_proof_inputs,
        "req_proof_summary": req_proof_summary,
        "completed": completed,
        "ledger_completed": ledger_completed,
        "evidence_ok": evidence_ok,
        "issues": issues,
    }


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

    @staticmethod
    def _artifact_creation_entry(
        event: LedgerEvent,
        canonical_parent: str | None,
    ) -> dict[str, Any]:
        """Create the initial graph entry for an artifact creation event."""
        entry: dict[str, Any] = {
            "type": event.event.replace("_created", ""),
            "created": event.ts,
            "parent": canonical_parent,
            "children": [],
            "attested": False,
        }
        if event.event == "obpi_created":
            entry["latest_receipt_event"] = None
            entry["latest_evidence"] = None
            entry["validated"] = False
            entry["ledger_completed"] = False
        if event.event == "adr_created":
            entry["lane"] = event.extra.get("lane")
            entry["closeout_initiated"] = False
            entry["closeout_by"] = None
            entry["closeout_mode"] = None
            entry["closeout_evidence"] = None
            entry["latest_receipt_event"] = None
            entry["validated"] = False
        return entry

    @classmethod
    def _ensure_artifact_entry(
        cls,
        graph: dict[str, dict[str, Any]],
        event: LedgerEvent,
        canonical_id: str,
        canonical_parent: str | None,
    ) -> None:
        """Create graph node on first creation event for an artifact."""
        creation_events = {
            "prd_created",
            "constitution_created",
            "obpi_created",
            "adr_created",
        }
        if event.event not in creation_events or canonical_id in graph:
            return
        graph[canonical_id] = cls._artifact_creation_entry(event, canonical_parent)

    @staticmethod
    def _record_parent_child_relationship(
        graph: dict[str, dict[str, Any]],
        canonical_parent: str | None,
        canonical_id: str,
    ) -> None:
        """Attach child to parent node if both are represented in the graph."""
        if not canonical_parent or canonical_parent not in graph:
            return
        children = graph[canonical_parent]["children"]
        if canonical_id not in children:
            children.append(canonical_id)

    @staticmethod
    def _apply_adr_created_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "adr_created" or canonical_id not in graph:
            return
        graph[canonical_id]["lane"] = event.extra.get("lane", graph[canonical_id].get("lane"))

    @staticmethod
    def _apply_attestation_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "attested" or canonical_id not in graph:
            return
        graph[canonical_id]["attested"] = True
        graph[canonical_id]["attestation_status"] = event.extra.get("status")
        graph[canonical_id]["attestation_by"] = event.extra.get("by")

    @staticmethod
    def _apply_closeout_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "closeout_initiated" or canonical_id not in graph:
            return
        graph[canonical_id]["closeout_initiated"] = True
        graph[canonical_id]["closeout_by"] = event.extra.get("by")
        graph[canonical_id]["closeout_mode"] = event.extra.get("mode")
        graph[canonical_id]["closeout_evidence"] = event.extra.get("evidence")

    @staticmethod
    def _apply_audit_receipt_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "audit_receipt_emitted" or canonical_id not in graph:
            return
        receipt_event = event.extra.get("receipt_event")
        graph[canonical_id]["latest_receipt_event"] = receipt_event
        evidence = event.extra.get("evidence")
        adr_completion = evidence.get("adr_completion") if isinstance(evidence, dict) else None
        if receipt_event == "validated" and adr_completion != "not_completed":
            graph[canonical_id]["validated"] = True

    @staticmethod
    def _apply_obpi_receipt_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "obpi_receipt_emitted" or canonical_id not in graph:
            return
        if graph[canonical_id].get("type") != "obpi":
            return
        receipt_event = event.extra.get("receipt_event")
        graph[canonical_id]["latest_receipt_event"] = receipt_event
        evidence = event.extra.get("evidence")
        if isinstance(evidence, dict):
            graph[canonical_id]["latest_evidence"] = dict(evidence)

        obpi_completion = event.extra.get("obpi_completion")
        if obpi_completion:
            graph[canonical_id]["obpi_completion"] = obpi_completion
            if obpi_completion in {"completed", "attested_completed"}:
                graph[canonical_id]["ledger_completed"] = True

        if receipt_event == "validated":
            graph[canonical_id]["validated"] = True

    @classmethod
    def _apply_graph_event_metadata(
        cls,
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        """Apply non-creation metadata for a ledger event."""
        cls._apply_adr_created_metadata(graph, canonical_id, event)
        cls._apply_attestation_metadata(graph, canonical_id, event)
        cls._apply_closeout_metadata(graph, canonical_id, event)
        cls._apply_audit_receipt_metadata(graph, canonical_id, event)
        cls._apply_obpi_receipt_metadata(graph, canonical_id, event)

    def get_artifact_graph(self) -> dict[str, dict[str, Any]]:
        """Build a graph of artifacts and their relationships.

        Returns:
            Dictionary mapping artifact IDs to their info and relationships.
        """
        graph: dict[str, dict[str, Any]] = {}
        events = self.read_all()
        rename_map = self._build_rename_map(events)

        for event in events:
            canonical_id = self._canonicalize_with_map(event.id, rename_map)
            canonical_parent = (
                self._canonicalize_with_map(event.parent, rename_map) if event.parent else None
            )

            self._ensure_artifact_entry(graph, event, canonical_id, canonical_parent)
            self._record_parent_child_relationship(graph, canonical_parent, canonical_id)
            self._apply_graph_event_metadata(graph, canonical_id, event)

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

    @staticmethod
    def canonical_attestation_term(status: str | None) -> str | None:
        """Map internal attestation token to canonical display term."""
        if status is None:
            return None
        return ATTESTATION_CANONICAL_TERMS.get(status, status)

    @classmethod
    def derive_adr_semantics(cls, info: dict[str, Any]) -> dict[str, Any]:
        """Derive canonical lifecycle and closeout-phase semantics for ADR status surfaces."""
        attestation_status = info.get("attestation_status")
        validated = bool(info.get("validated"))
        closeout_initiated = bool(info.get("closeout_initiated"))

        if validated:
            lifecycle_status = "Validated"
            closeout_phase = "validated"
        elif attestation_status == "dropped":
            lifecycle_status = "Abandoned"
            closeout_phase = "attested"
        elif attestation_status in {"completed", "partial"}:
            lifecycle_status = "Completed"
            closeout_phase = "attested"
        elif closeout_initiated:
            lifecycle_status = "Pending"
            closeout_phase = "closeout_initiated"
        else:
            lifecycle_status = "Pending"
            closeout_phase = "pre_closeout"

        return {
            "lifecycle_status": lifecycle_status,
            "closeout_phase": closeout_phase,
            "attestation_term": cls.canonical_attestation_term(
                attestation_status if isinstance(attestation_status, str) else None
            ),
        }
