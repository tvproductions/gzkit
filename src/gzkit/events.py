"""Typed ledger event models with Pydantic discriminated unions.

Typed event models provide discriminated-union parsing for ledger entries.
The nested evidence models referenced by these events (``EventAnchor`` and
the OBPI-receipt evidence payloads) live in :mod:`gzkit.event_evidence`.
"""

from datetime import UTC, datetime
from typing import Annotated, Any, ClassVar, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    model_serializer,
    model_validator,
)

from gzkit.event_evidence import EventAnchor
from gzkit.ledger import LEDGER_SCHEMA

# ---------------------------------------------------------------------------
# Typed event models (discriminated union over event type)
# ---------------------------------------------------------------------------


class _EventBase(BaseModel):
    """Common fields shared by all ledger event types."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema_: str = Field(default=LEDGER_SCHEMA)
    parent: str | None = None

    _BASE_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {"schema_", "event", "id", "ts", "parent"},
    )

    @model_validator(mode="before")
    @classmethod
    def _map_schema_key(cls, data: Any) -> Any:
        """Map 'schema' → 'schema_' for Pydantic field name."""
        if isinstance(data, dict) and "schema" in data and "schema_" not in data:
            data = dict(data)
            data["schema_"] = data.pop("schema")
        return data

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        """Serialize with schema_→schema mapping and typed fields flattened."""
        result: dict[str, Any] = {
            "schema": self.schema_,
            "event": self.event,  # ty: ignore[unresolved-attribute]
            "id": self.id,
            "ts": self.ts,
        }
        if self.parent:
            result["parent"] = self.parent
        # Flatten event-specific fields
        for name in type(self).model_fields:
            if name not in self._BASE_FIELDS:
                value = getattr(self, name)
                if value is not None:
                    result[name] = value
        return result

    @property
    def extra(self) -> dict[str, Any]:
        """Backward-compatible extra dict for code that accesses event.extra."""
        result: dict[str, Any] = {}
        for name in type(self).model_fields:
            if name not in self._BASE_FIELDS:
                value = getattr(self, name)
                if value is not None:
                    result[name] = value
        return result


class ProjectInitEvent(_EventBase):
    """project_init event."""

    event: Literal["project_init"]
    mode: str


class PrdCreatedEvent(_EventBase):
    """prd_created event."""

    event: Literal["prd_created"]


class ConstitutionCreatedEvent(_EventBase):
    """constitution_created event."""

    event: Literal["constitution_created"]


class ObpiCreatedEvent(_EventBase):
    """obpi_created event."""

    event: Literal["obpi_created"]


class AdrCreatedEvent(_EventBase):
    """adr_created event."""

    event: Literal["adr_created"]
    lane: str


class ArtifactEditedEvent(_EventBase):
    """artifact_edited event."""

    event: Literal["artifact_edited"]
    path: str
    session: str | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class AttestedEvent(_EventBase):
    """attested event."""

    event: Literal["attested"]
    status: str
    by: str
    reason: str | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class GateCheckedEvent(_EventBase):
    """gate_checked event."""

    event: Literal["gate_checked"]
    gate: int
    status: str
    command: str
    returncode: int
    evidence: str | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class CloseoutInitiatedEvent(_EventBase):
    """closeout_initiated event."""

    event: Literal["closeout_initiated"]
    by: str
    mode: str
    evidence: dict[str, Any] | None = None


class AuditReceiptEmittedEvent(_EventBase):
    """audit_receipt_emitted event."""

    event: Literal["audit_receipt_emitted"]
    receipt_event: str
    attestor: str
    evidence: dict[str, Any] | None = None
    anchor: EventAnchor | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class ObpiReceiptEmittedEvent(_EventBase):
    """obpi_receipt_emitted event."""

    event: Literal["obpi_receipt_emitted"]
    receipt_event: str
    attestor: str
    evidence: dict[str, Any] | None = None
    obpi_completion: str | None = None
    anchor: EventAnchor | None = None


class ArtifactRenamedEvent(_EventBase):
    """artifact_renamed event."""

    event: Literal["artifact_renamed"]
    new_id: str
    reason: str | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class AdrAnnotatedEvent(_EventBase):
    """adr_annotated event."""

    event: Literal["adr_annotated"]
    annotation: str
    source_framework: str | None = None
    rationale: str | None = None


class LifecycleTransitionEvent(_EventBase):
    """lifecycle_transition event."""

    event: Literal["lifecycle_transition"]
    content_type: str
    from_state: str
    to_state: str


class AgentSyncCompletedEvent(_EventBase):
    """agent_sync_completed event — mechanical witness for control-surface sync (GHI #369)."""

    event: Literal["agent_sync_completed"]
    updated_paths: list[str]
    canonical_rule_count: int


class AdrEvalCompletedEvent(_EventBase):
    """adr_eval_completed event — ADR evaluation scorecard summary."""

    event: Literal["adr_eval_completed"]
    verdict: str
    adr_weighted_total: float
    obpi_count: int
    action_item_count: int


class AdrEvaluationEvent(_EventBase):
    """adr-evaluation event — full per-dimension scores (ADR-0.0.26-01)."""

    event: Literal["adr-evaluation"]
    artifact_id: str
    artifact_type: str
    dimensions: dict[str, float]
    scores: dict[str, float]
    weighted_total: float
    red_team_challenges_fired: list[str]
    evaluator_persona: str
    timestamp: str


class AuditGeneratedEvent(_EventBase):
    """audit_generated event — heavy-lane ADR audit artifact creation."""

    event: Literal["audit_generated"]
    audit_file: str
    audit_plan_file: str
    passed: bool


class ObpiLockClaimedEvent(_EventBase):
    """obpi_lock_claimed event — multi-agent OBPI claim record."""

    event: Literal["obpi_lock_claimed"]
    agent: str
    ttl_minutes: int
    branch: str
    session_id: str


class ObpiLockReleasedEvent(_EventBase):
    """obpi_lock_released event — OBPI lock release record."""

    event: Literal["obpi_lock_released"]
    agent: str
    force: bool = False


class ObpiWithdrawnEvent(_EventBase):
    """obpi_withdrawn event — withdrawal record for a non-completing OBPI brief."""

    event: Literal["obpi_withdrawn"]
    reason: str


class ObpiCompletionUncoveredAcceptEvent(_EventBase):
    """obpi_completion_uncovered_accept event — records one REQ-coverage waiver (ADR-0.0.25-02)."""

    event: Literal["obpi_completion_uncovered_accept"]
    obpi_id: str
    req_id: str
    operator: str
    rationale: str
    acceptance_type: str
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class PatchReleaseEvent(_EventBase):
    """patch-release event — GHI-driven patch release ceremony record."""

    event: Literal["patch-release"]
    version: str
    previous_version: str
    tag: str | None = None
    ghi_summary: list[dict[str, Any]]
    manifest_path: str


class PipelineMarkerPurgedEvent(_EventBase):
    """pipeline_marker_purged event — auto-purge of orphaned pipeline-active marker (GHI #399)."""

    event: Literal["pipeline_marker_purged"]
    reason: str
    marker_path: str


class PipelineLaunchedEvent(_EventBase):
    """pipeline_launched event — emitted at Stage 1 when the active marker is written (GHI #412).

    Carries the nonce embedded in the marker payload so the agent-relayed
    attestation gate can cross-check that the marker was produced by an
    operator-initiated pipeline launch (rather than a forged file).
    """

    event: Literal["pipeline_launched"]
    nonce: str
    marker_path: str
    lane: str
    entry: str | None = None


# ---------------------------------------------------------------------------
# TASK ledger events (ADR-0.22.0 / OBPI-0.22.0-02)
# ---------------------------------------------------------------------------


class _TaskEventBase(_EventBase):
    """Common fields shared by all TASK-level ledger events."""

    task_id: str = Field(..., description="TASK identifier (e.g. TASK-0.22.0-01-01-01)")
    obpi_id: str = Field(..., description="Parent OBPI identifier")
    adr_id: str = Field(..., description="Parent ADR identifier")
    agent: str = Field(..., description="Agent that emitted the event")


class TaskStartedEvent(_TaskEventBase):
    """task_started event — emitted for both initial start and resume from blocked."""

    event: Literal["task_started"]


class TaskCompletedEvent(_TaskEventBase):
    """task_completed event."""

    event: Literal["task_completed"]


class TaskBlockedEvent(_TaskEventBase):
    """task_blocked event — includes a reason for the block."""

    event: Literal["task_blocked"]
    reason: str = Field(..., description="Reason the task is blocked")


class TaskEscalatedEvent(_TaskEventBase):
    """task_escalated event — includes reason and optional escalation target."""

    event: Literal["task_escalated"]
    reason: str = Field(..., description="Reason the task is escalated")
    escalated_to: str | None = Field(None, description="Escalation target (person/team)")


# ---------------------------------------------------------------------------
# Intrinsic complexity attestation (OBPI-0.0.29-07)
# ---------------------------------------------------------------------------


class IntrinsicComplexityAttestationEvent(_EventBase):
    """intrinsic-complexity-attestation event (OBPI-0.0.29-07).

    Records a human-attested declaration that a named function's cyclomatic
    complexity is irreducibly intrinsic. Emitted by ``gz complexity advise
    --attest-intrinsic``.
    """

    event: Literal["intrinsic-complexity-attestation"]
    file_path: str = Field(..., description="Source file containing the function")
    qualname: str = Field(..., description="Qualified name of the function")
    reason: str = Field(..., description="Human-readable rationale for attestation")
    attestor: str = Field(..., description="Full name of the attesting human")
    attestation_date: str = Field(..., description="ISO 8601 date of attestation")
    metric: str = Field(..., description="Complexity metric key (e.g. radon_cc)")
    crossing_band: Literal["block", "warn", "advise"] = Field(
        ..., description="Threshold band crossed at attestation time"
    )
    crossing_value: float = Field(..., description="Observed metric value at attestation time")
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class DistributionBaselineRegeneratedEvent(_EventBase):
    """distribution_baseline_regenerated event — baseline manifest rewrite (OBPI-0.0.32-15).

    Emitted when ``gz validate --distribution --regenerate`` rewrites
    ``data/distribution_baseline_manifest.json`` from on-disk canonical surface
    truth. Layer-2 witness symmetric to ``agent_sync_completed``.
    """

    event: Literal["distribution_baseline_regenerated"]
    surfaces_walked: list[str]
    file_count: int
    manifest_hash_before: str
    manifest_hash_after: str


class CompositionRenderedEvent(_EventBase):
    """composition_rendered event — constitutional invariant composition render (ADR-0.0.37)."""

    event: Literal["composition_rendered"]
    invariant_count: int
    target: str
    byte_count: int
    render_ts: str
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class CompositionDriftDetectedEvent(_EventBase):
    """composition_drift_detected event — registry vs. committed target drift (ADR-0.0.37)."""

    event: Literal["composition_drift_detected"]
    target: str
    diff_first_50_lines: str
    render_ts: str


class ChoreDecommissionProcessedEvent(_EventBase):
    """chore_decommission_processed event — file processed by the tautological-tests chore."""

    event: Literal["chore_decommission_processed"]
    file_path: str
    disposition: str
    obpi_id: str


class CorpusEntryAppendedEvent(_EventBase):
    """corpus_entry_appended event — append-only corpus capture (ADR-0.0.37, OBPI-19).

    Layer-2 witness that a ``CorpusEntry`` was appended to the per-surface corpus
    store by ``gz content remember``. Carries the addressing tuple needed for
    bidirectional audit; never written for a rendered-surface edit.
    """

    event: Literal["corpus_entry_appended"]
    surface: str
    section: str
    entry_id: str
    tier: str


class BriefReconciledEvent(_EventBase):
    """brief_reconciled event — OBPI brief reconciliation run (ADR-0.0.37, OBPI-06).

    Summary record emitted on every ``gz brief reconcile`` run. ``applied`` and
    ``attestor`` are populated only when ``--apply --attestor`` wrote amendments.
    """

    event: Literal["brief_reconciled"]
    brief_id: str
    has_drift: bool
    allowlist_delta_count: int
    discovery_delta_count: int
    verification_delta_count: int
    req_count_delta: int
    citation_delta_count: int
    applied: bool = False
    attestor: str | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class BriefReconcileDriftDetectedEvent(_EventBase):
    """brief_reconcile_drift_detected event — full per-dimension drift payload (OBPI-06)."""

    event: Literal["brief_reconcile_drift_detected"]
    brief_id: str
    allowlist_missing_in_brief: list[str]
    allowlist_missing_on_disk: list[str]
    discovery_unresolved_paths: list[str]
    verification_unresolved_verbs: list[str]
    declared_reqs: int
    acceptance_criteria_count: int
    req_count_delta: int
    citation_stale: list[str]


class BriefReconcileDriftOverriddenEvent(_EventBase):
    """brief_reconcile_drift_overridden event — escape-hatch override receipt (OBPI-0.0.37-08)."""

    event: Literal["brief_reconcile_drift_overridden"]
    brief_id: str
    override_ts: str
    attestor: str
    reason: str
    original_receipt_id: str | None = None
    original_drift_dimensions: list[str] = Field(default_factory=list)


TypedLedgerEvent = Annotated[
    ProjectInitEvent
    | PrdCreatedEvent
    | ConstitutionCreatedEvent
    | ObpiCreatedEvent
    | AdrCreatedEvent
    | ArtifactEditedEvent
    | AttestedEvent
    | GateCheckedEvent
    | CloseoutInitiatedEvent
    | AuditReceiptEmittedEvent
    | ObpiReceiptEmittedEvent
    | ArtifactRenamedEvent
    | AdrAnnotatedEvent
    | LifecycleTransitionEvent
    | AgentSyncCompletedEvent
    | AdrEvalCompletedEvent
    | AdrEvaluationEvent
    | AuditGeneratedEvent
    | ObpiLockClaimedEvent
    | ObpiLockReleasedEvent
    | ObpiWithdrawnEvent
    | ObpiCompletionUncoveredAcceptEvent
    | PatchReleaseEvent
    | PipelineMarkerPurgedEvent
    | PipelineLaunchedEvent
    | TaskStartedEvent
    | TaskCompletedEvent
    | TaskBlockedEvent
    | TaskEscalatedEvent
    | IntrinsicComplexityAttestationEvent
    | DistributionBaselineRegeneratedEvent
    | CompositionRenderedEvent
    | CompositionDriftDetectedEvent
    | ChoreDecommissionProcessedEvent
    | CorpusEntryAppendedEvent
    | BriefReconciledEvent
    | BriefReconcileDriftDetectedEvent
    | BriefReconcileDriftOverriddenEvent,
    Field(discriminator="event"),
]

_typed_event_adapter: TypeAdapter[TypedLedgerEvent] = TypeAdapter(TypedLedgerEvent)


def parse_typed_event(data: dict[str, Any]) -> TypedLedgerEvent:
    """Parse a raw dict into a typed event model via discriminated union."""
    return _typed_event_adapter.validate_python(data)
