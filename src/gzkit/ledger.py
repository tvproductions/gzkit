"""Ledger system for tracking governance events.

The ledger is an append-only JSONL file that records all governance events.
State is derived from the ledger, not stored separately.
"""

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

_ADR_SEMVER_RE = re.compile(r"^ADR-(\d+\.\d+\.\d+)(?:-.*)?$")
_OBPI_BARE_RE = re.compile(r"^OBPI-(\d+\.\d+\.\d+-\d+)(?:-.*)?$")


def _extract_bare_adr_semver(adr_id: str) -> str | None:
    """Return the bare ``ADR-X.Y.Z`` form for any ADR id that carries a semver.

    Returns ``None`` for non-ADR ids, pool ADRs (``ADR-pool.<slug>``), and
    anything else that does not match the foundation/feature semver shape.
    The bridge in :meth:`Ledger.has_adr_created` uses this to collapse
    ``ADR-0.0.22`` and ``ADR-0.0.22-security-sensitivity-doctrine`` into the
    same identity for idempotency without requiring an explicit
    ``artifact_renamed`` event between them (GHI #279).
    """
    match = _ADR_SEMVER_RE.match(adr_id)
    if match is None:
        return None
    return f"ADR-{match.group(1)}"


def _extract_bare_obpi_id(obpi_id: str) -> str | None:
    """Return the bare ``OBPI-X.Y.Z-NN`` form for any indexed OBPI id.

    Symmetric with :func:`_extract_bare_adr_semver` — used by the on-disk
    drift detector in ``migrate_semver`` (GHI #345) to collapse bare-form
    ``OBPI-0.1.0-01`` and slug-form ``OBPI-0.1.0-01-gz-init`` to the same
    identity when reconciling ledger touched ids against on-disk canon.
    Returns ``None`` for pool OBPIs and any id that does not match the
    indexed semver shape.
    """
    match = _OBPI_BARE_RE.match(obpi_id)
    if match is None:
        return None
    return f"OBPI-{match.group(1)}"


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
    "withdrawn",
}
OBPI_COMPLETED_RUNTIME_STATES = {"completed", "attested_completed", "validated"}
# ADR-level audit receipt events that represent human Gate 5 attestation —
# mirrors ``_HUMAN_ATTESTATION_RECEIPT_EVENTS`` in
# ``src/gzkit/commands/adr_audit.py`` (the emit-side authority). Defined
# locally to keep ``ledger.py`` free of command-module imports (GHI #391).
_AUDIT_HUMAN_ATTESTATION_EVENTS = frozenset({"validated", "attested", "accepted"})
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


class LedgerEvent(BaseModel):
    """A governance event recorded in the ledger.

    All events have:
    - schema: Always "gzkit.ledger.v1"
    - event: Event type (e.g., "project_init", "adr_created")
    - id: Artifact identifier
    - ts: ISO 8601 UTC timestamp

    Event-specific fields are stored in extra and flattened during serialization.

    Use ``model_validate(data)`` to parse from a dict (replaces ``from_dict``).
    Use ``model_dump()`` to serialize (replaces ``to_dict``).
    """

    model_config = ConfigDict(extra="forbid")

    event: str
    id: str
    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema_: str = Field(default=LEDGER_SCHEMA)
    parent: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

    _KNOWN_FIELDS: ClassVar[frozenset[str]] = frozenset({"schema", "event", "id", "ts", "parent"})

    @model_validator(mode="before")
    @classmethod
    def _collect_extra_fields(cls, data: Any) -> Any:
        """Map 'schema' key to 'schema_' and collect unknown keys into extra."""
        if not isinstance(data, dict):
            return data
        result = dict(data)
        # Map "schema" → "schema_" for Pydantic field name
        if "schema" in result and "schema_" not in result:
            result["schema_"] = result.pop("schema")
        # Collect unknown keys into extra
        extra_keys = set(result.keys()) - cls._KNOWN_FIELDS - {"schema_", "extra"}
        if extra_keys:
            existing_extra = result.get("extra", {})
            if not isinstance(existing_extra, dict):
                existing_extra = {}
            for key in extra_keys:
                existing_extra[key] = result.pop(key)
            result["extra"] = existing_extra
        return result

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        """Serialize with schema_→schema mapping and extra flattened into top level."""
        result: dict[str, Any] = {
            "schema": self.schema_,
            "event": self.event,
            "id": self.id,
            "ts": self.ts,
        }
        if self.parent:
            result["parent"] = self.parent
        if self.extra:
            result.update(self.extra)
        return result


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
        self._cached_events: list[LedgerEvent] | None = None
        self._cached_graph: dict[str, dict[str, Any]] | None = None

    def exists(self) -> bool:
        """Check if the ledger file exists."""
        return self.path.exists()

    def create(self) -> None:
        """Create an empty ledger file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()

    def _invalidate_cache(self) -> None:
        """Invalidate all in-memory caches after a mutation."""
        self._cached_events = None
        self._cached_graph = None

    def append(self, event: LedgerEvent) -> None:
        """Append an event to the ledger.

        Args:
            event: The event to append.

        """
        if not self.path.exists():
            self.create()

        with self.path.open("a") as f:
            json.dump(event.model_dump(), f, separators=(",", ":"))
            f.write("\n")
            f.flush()

        self._invalidate_cache()

    def has_adr_created(self, adr_id: str) -> bool:
        """Return True if an ``adr_created`` event resolves to ``adr_id``.

        Three matching paths, in order of strictness:

        1. ``canonicalize_id`` equality on both sides — handles historical
           bare-semver emissions (``ADR-0.0.20``) renamed to a slugged
           canonical via ``artifact_renamed`` events.
        2. Bare-semver bridge — when one side is ``ADR-X.Y.Z`` and the other
           is ``ADR-X.Y.Z-<slug>``, treat them as the same ADR even without
           an explicit ``artifact_renamed`` event. This closes the GHI #279
           regression on ADR-0.0.22 where a bare-ID ``adr_created`` event
           was emitted at authoring time and the second slugged emission
           slipped through because no rename event existed to bridge the
           two forms.

        The bridge is per-semver: ``ADR-0.0.22`` matches ``ADR-0.0.22-foo``
        but does not match ``ADR-0.0.23`` or ``ADR-0.0.23-bar``.

        Used by emission paths to enforce idempotency and prevent the
        duplicate ``adr_created`` class surfaced in GHI #279.
        """
        target = self.canonicalize_id(adr_id)
        target_bare = _extract_bare_adr_semver(target)
        for event in self.read_all():
            if event.event != "adr_created":
                continue
            event_canonical = self.canonicalize_id(event.id)
            if event_canonical == target:
                return True
            event_bare = _extract_bare_adr_semver(event_canonical)
            if target_bare is not None and event_bare is not None and target_bare == event_bare:
                return True
        return False

    def read_all(self) -> list[LedgerEvent]:
        """Read all events from the ledger.

        Returns:
            List of all events in chronological order.
            Results are cached for the lifetime of this Ledger instance.

        """
        if self._cached_events is not None:
            return self._cached_events

        if not self.path.exists():
            return []

        events = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    events.append(LedgerEvent.model_validate(data))

        self._cached_events = events
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

    def resolve_artifact_id(self, artifact_id: str) -> str:
        """Resolve an artifact ID through rename-map then short-form→long-form (GHI #222).

        After rename-map collapse, if the result is a short-form ADR id
        (``ADR-X.Y.Z``) and exactly one graph key starts with ``ADR-X.Y.Z-``,
        return the long form. Ambiguous prefixes return unchanged. Non-ADR
        ids and already-canonical ids pass through.
        """
        canonical = self.canonicalize_id(artifact_id)
        if not canonical.startswith("ADR-"):
            return canonical
        graph = self.get_artifact_graph()
        if canonical in graph:
            return canonical
        prefix = f"{canonical}-"
        matches = [k for k in graph if k.startswith(prefix)]
        if len(matches) == 1:
            return matches[0]
        return canonical

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

    def get_effective_gate_statuses(self, adr_id: str) -> dict[int, str]:
        """Return gate statuses honoring lifecycle authority for display.

        Identical to `get_latest_gate_statuses` except that within a
        Validated/Completed lifecycle epoch, `gate_checked: fail` events are
        treated as observational noise — lifecycle is the authoritative source
        for validation status (state-doctrine; GHI #392).

        Rules:
        - If the latest `lifecycle_transition` event for the canonical ADR
          places it in `{Completed, Validated}` and no subsequent rollback
          transition fires, any `gate_checked: fail` event after that
          lifecycle event yields `pass` for that gate.
        - A subsequent `lifecycle_transition` away from the validated states
          opens a new epoch — observations within the new epoch apply normally.
        - Pre-validation observations (and ADRs with no lifecycle transition)
          fall through to raw `get_latest_gate_statuses` semantics.

        Use this for display surfaces (`gz adr report`, `gz adr status`).
        Use raw `get_latest_gate_statuses` for prerequisite checks
        (`_attestation_gate_snapshot`) where lifecycle isn't yet validated.
        """
        events = self.read_all()
        rename_map = self._build_rename_map(events)
        target_id = self._canonicalize_with_map(adr_id, rename_map)

        validated_states = {"Completed", "Validated"}
        validated_since: str | None = None
        for event in events:
            if event.event != "lifecycle_transition":
                continue
            if self._canonicalize_with_map(event.id, rename_map) != target_id:
                continue
            to_state = event.extra.get("to_state")
            if isinstance(to_state, str) and to_state in validated_states:
                validated_since = event.ts
            else:
                validated_since = None

        latest: dict[int, str] = {}
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

            if status == "fail" and validated_since is not None and event.ts > validated_since:
                latest[gate] = "pass"
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
            entry["withdrawn"] = False
            entry["withdrawn_reason"] = None
            entry["latest_receipt_event"] = None
            entry["latest_evidence"] = None
            entry["latest_completion_evidence"] = None
            entry["latest_completion_anchor"] = None
            entry["latest_completion_ts"] = None
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
        if canonical_id not in graph:
            return
        if event.event == "attested":
            graph[canonical_id]["attested"] = True
            graph[canonical_id]["attestation_status"] = event.extra.get("status")
            graph[canonical_id]["attestation_by"] = event.extra.get("by")
            return
        if event.event == "obpi_receipt_emitted":
            evidence = event.extra.get("evidence") or {}
            if isinstance(evidence, dict) and evidence.get("human_attestation"):
                graph[canonical_id]["attested"] = True
                graph[canonical_id]["attestation_status"] = evidence.get(
                    "obpi_completion"
                ) or event.extra.get("obpi_completion")
                graph[canonical_id]["attestation_by"] = event.extra.get("attestor")

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
        if isinstance(receipt_event, str) and receipt_event in _AUDIT_HUMAN_ATTESTATION_EVENTS:
            graph[canonical_id]["attested"] = True
            evidence_dict = evidence if isinstance(evidence, dict) else {}
            graph[canonical_id]["attestation_status"] = (
                evidence_dict.get("attestation_text") or receipt_event
            )
            graph[canonical_id]["attestation_by"] = event.extra.get("attestor")

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
        if receipt_event == "completed":
            graph[canonical_id]["latest_completion_evidence"] = dict(evidence or {})
            graph[canonical_id]["latest_completion_anchor"] = _normalize_anchor(
                event.extra.get("anchor")
            )
            graph[canonical_id]["latest_completion_ts"] = event.ts

        obpi_completion = event.extra.get("obpi_completion")
        if obpi_completion:
            graph[canonical_id]["obpi_completion"] = obpi_completion
            if obpi_completion in {"completed", "attested_completed"}:
                graph[canonical_id]["ledger_completed"] = True

        if receipt_event == "validated":
            graph[canonical_id]["validated"] = True

    @staticmethod
    def _apply_obpi_withdrawn_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "obpi_withdrawn" or canonical_id not in graph:
            return
        if graph[canonical_id].get("type") != "obpi":
            return
        graph[canonical_id]["withdrawn"] = True
        graph[canonical_id]["withdrawn_reason"] = event.extra.get("reason")

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
        cls._apply_obpi_withdrawn_metadata(graph, canonical_id, event)

    @staticmethod
    def _resolve_short_form_parents(graph: dict[str, dict[str, Any]]) -> None:
        """Rewrite short-form ADR parents to canonical long-form (GHI #222).

        When a node's ``parent`` is set to a short-form id like ``ADR-0.0.17``
        but the actual parent is registered in the graph as
        ``ADR-0.0.17-adr-taxonomy-mechanical``, rewrite the parent reference
        to the long form and reattach the parent→child relationship. Only
        applied when the short form has exactly one long-form candidate —
        ambiguous prefixes are left unchanged.
        """
        graph_keys = set(graph.keys())
        for canonical_id, info in graph.items():
            parent = info.get("parent")
            if not parent or not parent.startswith("ADR-") or parent in graph_keys:
                continue
            prefix = f"{parent}-"
            matches = [k for k in graph_keys if k.startswith(prefix)]
            if len(matches) != 1:
                continue
            resolved = matches[0]
            info["parent"] = resolved
            children = graph[resolved]["children"]
            if canonical_id not in children:
                children.append(canonical_id)

    def get_artifact_graph(self) -> dict[str, dict[str, Any]]:
        """Build a graph of artifacts and their relationships.

        Returns:
            Dictionary mapping artifact IDs to their info and relationships.
            Results are cached for the lifetime of this Ledger instance.

        """
        if self._cached_graph is not None:
            return self._cached_graph

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

        self._resolve_short_form_parents(graph)

        self._cached_graph = graph
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


# ---------------------------------------------------------------------------
# Re-exports: keep ``from gzkit.ledger import X`` working for all consumers.
# These imports run AFTER LedgerEvent, Ledger, and constants are defined,
# which breaks the circular-import chain (the sub-modules only need names
# that are already bound above).
# ---------------------------------------------------------------------------
from gzkit.ledger_events import (  # noqa: E402, F401
    adr_created_event,
    adr_eval_completed_event,
    adr_evaluation_event,
    artifact_edited_event,
    artifact_renamed_event,
    attested_event,
    audit_generated_event,
    audit_receipt_emitted_event,
    closeout_initiated_event,
    constitution_created_event,
    gate_checked_event,
    lifecycle_transition_event,
    obpi_completion_uncovered_accept_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
    obpi_withdrawn_event,
    pipeline_marker_purged_event,
    prd_created_event,
    project_init_event,
)
from gzkit.ledger_proof import (  # noqa: E402, F401
    normalize_req_proof_inputs,
    summarize_req_proof_inputs,
)
from gzkit.ledger_semantics import (  # noqa: E402, F401
    _normalize_anchor,
    derive_obpi_semantics,
)
