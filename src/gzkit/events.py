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
    field_validator,
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
    commit: str | None = Field(
        default=None, description="Commit SHA the backstop recorder observed (GHI #847)"
    )
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


class FoundationGrandfatheredEvent(_EventBase):
    """foundation_grandfathered event.

    Terminality witness for one closed-manifest `kind: foundation` entry
    (ADR-0.34.0 Foundation Sunset, OBPI-04). Emitted once per
    ``data/foundation_grandfather.json`` entry at populate time
    (backfill-at-populate); ``id`` MUST carry the full slugged ADR id (e.g.
    ``ADR-0.0.9-state-doctrine-source-of-truth``), never a bare semver — the
    reader (``gzkit.governance.trust_audits.taxonomy._grandfathered_event_ids``)
    does exact string set-difference against on-disk frontmatter ids. This
    event is Gate-5-witnessed: for pre-ledger foundations, the human
    attestation of the migration IS the terminality witness, so ``attestor``
    is carried for the audit trail even though the reader itself ignores it.
    """

    event: Literal["foundation_grandfathered"]
    title: str
    semver: str
    frozen_at: str
    # REQUIRED and non-blank. This event IS the Gate-5 terminality witness, and
    # the taxonomy reader admits any event of this type carrying a non-empty id
    # WITHOUT inspecting the witness — so if the model tolerated a missing or
    # empty attestor, a hand-constructed event would satisfy REQ-02's structural
    # proof with no Gate-5 authority behind it. Enforcing it here means such an
    # event fails `gz validate --ledger` (a bound `gz check` step) even though the
    # reader itself is indifferent.
    attestor: str = Field(..., min_length=1, description="Gate-5 human witness")
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")

    @field_validator("attestor")
    @classmethod
    def _attestor_is_not_blank(cls, value: str) -> str:
        """Reject a whitespace-only attestor.

        ``min_length=1`` counts CHARACTERS, so ``"   "`` satisfies it while naming
        no witness at all — a measured bypass of the very guard this field exists
        to be. Stripped-nonempty is the actual invariant.
        """
        if not value.strip():
            msg = "attestor must name a witness — whitespace is not an attestation"
            raise ValueError(msg)
        return value


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


class ObpiLockTtlWarningEvent(_EventBase):
    """obpi_lock_ttl_warning event — held lock past 50% TTL, not yet expired."""

    event: Literal["obpi_lock_ttl_warning"]
    agent: str
    elapsed_minutes: float
    ttl_minutes: int


class ObpiWithdrawnEvent(_EventBase):
    """obpi_withdrawn event — withdrawal record for a non-completing OBPI brief."""

    event: Literal["obpi_withdrawn"]
    reason: str
    attestor: str = ""


class ObpiParkedEvent(_EventBase):
    """obpi_parked event — reversible retirement of an OBPI whose parent left active status.

    Distinct from ``obpi_withdrawn`` (permanent, one-way, not re-completable) and
    from ``obpi_completion_repudiated`` (reverses a Gate-5). A parked OBPI is its
    parent's decomposition, still valid at authoring time, held against a parent
    that moved to pool — it becomes live again when the parent is re-promoted.

    Authored under GHI #584: the GHI #520 Day-0 demotion renamed 28 ADRs without
    transacting over their children, stranding 237 ``obpi_created`` records with
    no terminal event and no resolvable parent.
    """

    event: Literal["obpi_parked"]
    parked_to: str = Field(..., min_length=1, description="Pool id the parent ADR became")
    reason: str = Field(..., min_length=1, description="Transition that caused the park")
    backfill: str | None = Field(default=None, description="GHI tag when parked retroactively")
    attestor: str | None = Field(default=None, description="Human witness for a bulk backfill")


class ObpiUnparkedEvent(_EventBase):
    """obpi_unparked event — a parked OBPI released when its parent is re-promoted (GHI #584)."""

    event: Literal["obpi_unparked"]
    unparked_from: str = Field(..., min_length=1, description="Pool id the parent promoted from")
    reason: str = Field(..., min_length=1, description="Transition that released the park")


class ObpiBlockedOnOperatorEvent(_EventBase):
    """obpi_blocked_on_operator event — the OBPI's next legitimate action is a human's.

    Authored under GHI #887. Measured on ``OBPI-0.35.0-02`` over 2026-08-25/26:
    the brief became structurally uncompletable — every remaining finding needed
    an operator decision, not an implementation — and the pipeline kept launching
    against it. 21 ``red_receipt_emitted``, 10 ``task_started``, ZERO
    ``task_completed``, 4 ``pipeline_launched``, 4 agents, three adversary rounds
    run after the claim could no longer be accepted regardless of their verdict.

    Distinct from ``obpi_parked``, whose required ``parked_to`` names the pool id
    the parent ADR became: here the parent is live and the brief is fine. Distinct
    from ``task_blocked``, which is one TASK inside the brief, not the brief.

    ``next_operator_action`` is required alongside ``reason`` and carries the
    concrete decision awaited. A reason alone records a complaint; naming the
    action is what makes the block dischargeable by someone other than its author.
    """

    event: Literal["obpi_blocked_on_operator"]
    reason: str = Field(..., min_length=1, description="Why the OBPI cannot proceed")
    next_operator_action: str = Field(
        ..., min_length=1, description="The concrete decision the operator owes"
    )


class ObpiUnblockedEvent(_EventBase):
    """obpi_unblocked event — the operator ruled and the OBPI may proceed (GHI #887).

    Composes with ``obpi_blocked_on_operator`` as a forward corrective pair over
    the append-only ledger; ``gzkit.obpi_lifecycle.operator_block_state`` nets the
    sequence. ``ruling`` carries the operator's decision so the block's discharge
    is readable from Layer 2 rather than only from the session that produced it —
    the same durability argument GHI #676 made for the Step-4b verdict.
    """

    event: Literal["obpi_unblocked"]
    ruling: str = Field(..., min_length=1, description="The operator's decision, verbatim")
    operator: str = Field(..., min_length=1, description="Who ruled")


class Stage2DispatchRecordedEvent(_EventBase):
    """stage2_dispatch_recorded event — one mandated Stage-2 role produced input.

    Authored under GHI #886. Dispatch credit previously lived ONLY in the
    pipeline marker under ``.claude/plans/``, which ``ADR-0.0.9``'s own table
    names Layer 3. Rule 5 of that ADR forecloses reading it for a verdict:
    *"Layer 3 artifacts cannot block gates. Only L1 (canon) and L2 (events) can
    be gate evidence."*

    Measured on ``OBPI-0.35.0-02``, 2026-08-26: implementer + spec-reviewer +
    quality-reviewer were dispatched and recorded 3/3 across two tasks, their
    findings drove two fix cycles, and the records were destroyed by
    ``gz obpi pipeline --clear-stale`` — the SANCTIONED recovery path. The gate
    then reported 0 of 3 against a run that had complied, and the loss was
    indistinguishable from the dispatch never having happened.

    The sibling that got this right is ``adversarial_validation``, whose own
    docstring states the principle this event was missing: without a ledger row
    the verdict lives only in an agent transcript or a vendor cache, so a run
    that skipped the gate and one that passed it leave identical records.
    """

    event: Literal["stage2_dispatch_recorded"]
    role: str = Field(..., min_length=1, description="Mandated Stage-2 role dispatched")
    model: str = Field(..., min_length=1, description="Model tier the role was dispatched at")
    task_id: int = Field(..., description="TASK the dispatch was made against")


class Stage2SingleDriverDeclaredEvent(_EventBase):
    """stage2_single_driver_declared event — a knowingly undispatched Stage 2 (GHI #886).

    The declaration is the COMPLIANT path for a session that genuinely cannot
    dispatch, and it is what converts the Stage-5 gate from BLOCK to PASS. It
    therefore has exactly the durability requirement its sibling has: a
    declaration destroyed by ``--clear-stale`` silently returns a declared run to
    the silent single-driver state the gate exists to refuse.

    Fixing only ``stage2_dispatch_recorded`` would have left the gate
    half-durable — the same defect surviving on the other half of the same
    verdict, which is the instance-not-class shape ``AGENTS.md`` § DO IT RIGHT #1
    forbids.
    """

    event: Literal["stage2_single_driver_declared"]
    reason: str = Field(..., min_length=1, description="Why this run could not dispatch")


class ObpiSupersededEvent(_EventBase):
    """obpi_superseded event — one OBPI superseded by another (OBPI-0.31.0-02).

    The ``withdrawn``/``superseded`` transitions in OBPI-01's
    ``CANONICAL_TRANSITIONS`` declare a ``human_attested`` witness; the
    witnessing attestor is carried on the emitted event (enforced non-empty at
    the CLI boundary in ``obpi_supersede_cmd``).
    """

    event: Literal["obpi_superseded"]
    superseded_by: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    attestor: str = Field(..., min_length=1)


class ObpiCompletionRepudiatedEvent(_EventBase):
    """obpi_completion_repudiated event — governed reversal of fabricated Gate-5 (ADR-0.0.71)."""

    event: Literal["obpi_completion_repudiated"]
    repudiated_receipt: str
    cause: Literal["model-induced-fabrication", "operator-error", "verification-invalid"]
    attestor: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)


class SecurityFloorOverriddenEvent(_EventBase):
    """security_floor_overridden — witnessed --accept-security-floor override (ADR-0.0.72-04)."""

    event: Literal["security_floor_overridden"]
    obpi_id: str = Field(..., min_length=1)
    surfaces: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    attestor: str = Field(..., min_length=1)


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


class CorpusEntryRetiredEvent(_EventBase):
    """corpus_entry_retired event — append-only corpus retirement (GHI #635).

    Layer-2 witness that ``gz content retire`` appended a retraction row superseding
    an earlier entry. Distinct from ``corpus_entry_appended`` because it changes what
    canon *currently* requires — the surface's invariant floor shrinks — which is the
    fact an auditor looks for, not merely that a row was added. Nothing is deleted;
    the retired entry keeps its provenance on disk.

    ``floor_direction`` and ``floor_moved_ids`` are what an auditor asking "was a
    0-Kelvin-floor entry un-bound or revived, and by whom?" actually needs -- ``tier``
    is only a PROXY for that question and cannot answer it, because a ``compressible``
    tombstone over an invariant target moves the floor. ``tier`` and ``attestor``
    (OBPI-0.35.0-02) remain recorded: ``tier`` is the RETIRED entry's own tier and is always
    known. ``attestor`` is legitimately empty on a routine compressible-tier
    retirement — the corpus-attestation gate guards only the invariant floor
    (`retire.py`), so this field is never required non-empty here.
    """

    event: Literal["corpus_entry_retired"]
    surface: str
    retired_entry_id: str
    retraction_entry_id: str
    reason: str
    # Both tombstone fields carry a default because this model must parse HISTORY, not
    # only rows this release writes. `tier` was added by OBPI-0.35.0-02; five committed
    # rows predate it (.gzkit/ledger.jsonl:13992,15045,15047,15075,15117) and the ledger
    # is append-only, so they can never grow the key. `schemas/ledger.json` leaves `tier`
    # out of `required` for exactly that reason -- a required field here would make the
    # two readers disagree about the same row: `gz validate --ledger` accepts it while
    # `parse_typed_event` raises. Held by TestTypedModelParsesEveryCommittedLedgerRow.
    tier: str = ""
    attestor: str = ""
    # `floor_direction` / `floor_moved_ids` (round-6 adversary, 2026-08-25): the
    # attestor gate authorizes on the invariant-liveness DELTA (`floor_added |
    # floor_removed`), but this event recorded only the RETIRED ROW'S TIER -- a proxy,
    # not the state. Measured: retiring a compressible tombstone over an invariant
    # entry printed "The invariant floor GREW" while the event carried
    # `tier='compressible'`, and that event with `attestor=''` passed `validate_ledger`
    # with zero errors. Layer 2 therefore could not tell an unaudited floor revival
    # from a routine compressible retirement, so a regression in the tombstone gate
    # would have stayed ledger-valid. Optional with defaults for the same reason `tier`
    # is: the ledger is append-only and committed rows can never grow the keys.
    floor_direction: Literal["unchanged", "shrank", "grew", "changed"] | None = None
    floor_moved_ids: list[str] = Field(default_factory=list)


class CorpusRetirementReconciledEvent(_EventBase):
    """corpus_retirement_reconciled event — after-the-fact tombstone accounting (GHI #885).

    A retraction row reached the corpus without the governed ``gz content retire``
    path: hand-appended (#885's bypass) or orphaned by a crash between the corpus
    write and the ledger appends (#878's partial-write window). This event records
    that a tombstone was FOUND unwitnessed and accounted for — never that the
    governed retirement ran.

    Kept DISTINCT from ``CorpusEntryRetiredEvent`` on purpose. Backfilling that
    type would retroactively witness a procedure nobody performed, which
    ``AGENTS.md`` § Attestation calls a fabricated receipt. Because the types are
    separate, an auditor reading Layer 2 can still tell a governed retirement from
    a reconciled one — collapsing them would destroy exactly the distinction
    ``--corpus-retirement-witness`` was built to preserve.

    No ``attestor`` and no floor delta: the reconciler observed neither. The
    retirement happened at an unknown earlier time under unknown authority, and
    inventing either field would be the same fabrication in a smaller costume.
    ``origin`` carries whatever forensic trace the corpus row itself holds.
    """

    event: Literal["corpus_retirement_reconciled"]
    surface: str
    retired_entry_id: str
    retraction_entry_id: str
    reason: str
    origin: str = ""


class CompositionCandidateEmittedEvent(_EventBase):
    """composition_candidate_emitted event — authoring-time candidate (OBPI-0.0.37-21).

    Layer-2 witness that ``gz content compose`` validated and staged a candidate
    rendition artifact. Carries per-tier byte evidence for the compose audit trail.
    """

    event: Literal["composition_candidate_emitted"]
    surface: str
    consumer: str
    setpoint: str
    invariant_bytes: int
    compressible_bytes_before: int
    compressible_bytes_after: int
    total_bytes: int
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class RenditionCommittedEvent(_EventBase):
    """rendition_committed event — operator-attested candidate→committed promotion (OBPI-22).

    Layer-2 witness that ``gz content commit`` promoted a staged candidate to the
    durable committed rendition under Gate-5 attestation, freezing the corpus
    content-fingerprint the rendition was attested against.
    """

    event: Literal["rendition_committed"]
    surface: str
    consumer: str
    corpus_fingerprint: str
    attestor: str
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class RenditionAdvisorVerdictEvent(_EventBase):
    """rendition_advisor_verdict event — advisor-QC verdict record (ADR-0.0.37, OBPI-24).

    Layer-2 witness that ``gz content advise-rendition`` recorded an
    information-retained-per-byte verdict as an ARB receipt. Advisory, never
    gating: emitted on every successful record regardless of the score value.
    """

    event: Literal["rendition_advisor_verdict"]
    surface: str
    receipt_id: str
    score: float
    consumer: str | None = None
    task_id: str | None = Field(default=None, description="TASK attribution (ADR-0.0.64-01)")


class BriefReconciledEvent(_EventBase):
    """brief_reconciled event — OBPI brief reconciliation run (ADR-0.0.37, OBPI-06).

    Summary record emitted on every ``gz obpi brief-drift`` run. ``applied`` and
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


class EnforcementClaimVerifiedEvent(_EventBase):
    """enforcement_claim_verified event — per-claim NC run receipt (OBPI-0.0.74-16).

    Emitted once per verified claim by ``run_meta_validator()`` on a clean run.
    READ-ONLY on a clean run — no ledger mutation on failures.
    """

    event: Literal["enforcement_claim_verified"]
    claim_id: str = Field(..., description="Enforcement claim identifier slug")
    outcome: Literal["PASS", "FACADE", "TEST_BUG"] = Field(
        ...,
        description="Runner outcome: PASS = caught; FACADE = not caught; TEST_BUG = exception",
    )
    source_fn: str = Field(..., description="Qualified name of the entrypoint")


class MxSessionOpenedEvent(_EventBase):
    """mx_session_opened event — opens the MX maintenance hangar window (ADR-0.0.74, OBPI-06).

    The event ``ts`` is the *enter* anchor that bounds log assembly; ``session_id``
    binds this open to its matching ``mx_session_closed`` and to the marker.
    """

    event: Literal["mx_session_opened"]
    session_id: str = Field(..., description="Binding key to the marker and the close event")
    reason: str = Field(..., description="Operator reason for entering MX mode")
    attestor: str = Field(..., description="Operator who opened the hangar")
    inspection_scope: list[str] = Field(
        default_factory=list, description="ADRs/OBPIs under inspection (the enter-time scope)"
    )


class MxSessionClosedEvent(_EventBase):
    """mx_session_closed event — closes the MX hangar window (ADR-0.0.74, OBPI-06).

    The event ``ts`` is the *exit* anchor; together with the matching
    ``mx_session_opened`` ``ts`` it bounds the enter→exit window the MX log
    is assembled from.
    """

    event: Literal["mx_session_closed"]
    session_id: str = Field(..., description="Binding key to the matching open event")
    attestor: str = Field(..., description="Operator who closed the hangar")


# ---------------------------------------------------------------------------
# Work-domain L2 edge events (ADR-0.32.0, OBPI-06). The four net-new,
# append-only edge event types expressing work coupling: precedence
# (blocks / its inverse blocked_by), provenance (discovered_from), and
# verification (validates). Permanent once emitted — the ADR's one true
# one-way door (§ Consequences Negative #4). Emission is code-gated on a
# recorded WWHTBT edge-vocabulary attestation (gzkit.ontology.work, REQ-07).
# ---------------------------------------------------------------------------


class BlocksEvent(_EventBase):
    """blocks event — ``blocker`` blocks ``blocked`` (precedence edge)."""

    event: Literal["blocks"]
    blocker: str = Field(..., description="The id that must resolve first")
    blocked: str = Field(..., description="The id that cannot proceed until the blocker resolves")


class BlockedByEvent(_EventBase):
    """blocked_by event — ``blocked`` is blocked_by ``blocker`` (inverse precedence edge)."""

    event: Literal["blocked_by"]
    blocked: str = Field(..., description="The id that cannot proceed until the blocker resolves")
    blocker: str = Field(..., description="The id that must resolve first")


class DiscoveredFromEvent(_EventBase):
    """discovered_from event — ``discovered`` was discovered_from ``origin`` (provenance edge)."""

    event: Literal["discovered_from"]
    discovered: str = Field(..., description="The id that was surfaced")
    origin: str = Field(..., description="The id the discovery originated from")


class ValidatesEvent(_EventBase):
    """validates event — ``validator`` validates ``validated`` (verification edge)."""

    event: Literal["validates"]
    validator: str = Field(..., description="The id that provides the validation")
    validated: str = Field(..., description="The id that is validated")


class AdversarialValidationEvent(_EventBase):
    """adversarial_validation event — an adversary's verdict on an OBPI completion claim.

    Recorded before Gate 5 (GHI #676, upstream GHI #643).

    Step 4b of the OBPI pipeline is fail-closed: no OBPI reaches attestation without
    an independent adversary, prompted to REFUTE, re-deriving the completion claim.
    This event is that verdict's durable home. Without it the verdict lives only in an
    agent transcript or a vendor cache — outside the repo, the ledger, and the brief —
    so an agent that skipped 4b and one that was refuted and attested anyway leave
    indistinguishable records.

    ``degraded-human-only`` is the explicit, attested floor when neither a
    different-vendor adversary nor an independent subagent could run. Silence is never
    a substitute for it.
    """

    event: Literal["adversarial_validation"]
    obpi_id: str = Field(..., description="OBPI whose completion claim was attacked")
    verdict: Literal[
        "refuted",
        "not-refuted",
        "refuted-with-caveats",
        "degraded-human-only",
    ] = Field(..., description="The adversary's finding; a closed vocabulary")
    adversary: str = Field(
        ...,
        description="Independent adversary identity — vendor/model, or 'human' in degraded mode",
    )
    job_id: str | None = Field(
        default=None, description="Adversary run id, when the runtime supplies one"
    )
    refuted_claim: str | None = Field(
        default=None, description="The specific claim the adversary broke, verbatim"
    )
    resolution: str | None = Field(
        default=None, description="How a refutation was closed, and how that was re-verified"
    )
    adversary_tier: int | None = Field(
        default=None,
        description="Declared Step-4b tier: 1 cross-vendor, 2 independent same-vendor, 3 degraded",
    )
    adversary_receipt: str | None = Field(
        default=None,
        description=(
            "ARB step receipt run_id proving the tier from the argv that ran (GHI #765). "
            "Unlike job_id, the gate resolves this before admitting the completion"
        ),
    )


class RedReceiptEmittedEvent(_EventBase):
    """red_receipt_emitted event — a BEHAVIOR test observed failing against the base tree.

    The pipeline instructs Red-Green-Refactor but shipped no mechanical witness that a
    BEHAVIOR test ever failed before its implementation existed (GHI #642). A test
    authored after the production code, passing on its first run, was
    byte-indistinguishable from a genuine RED-first test: ``@covers`` parity proves
    coverage, never falsifiability.

    ``failure_class`` is the verdict, not decoration:

    * ``assertion`` — strong RED; the test failed on an assertion.
    * ``error``     — weak RED; it failed for the wrong reason (typically an
      ImportError on a not-yet-existing symbol). Never silently equated with
      ``assertion``.
    * ``none``      — the test PASSED with the production hunks withheld. It cannot
      fail, which is the ``AGENTS.md`` Rule-6 defect, and the gate rejects it.
    * ``not-applicable`` — nothing was withheld, so the experiment never ran. Not a
      verdict on the test; recorded so a void run is distinguishable from a hollow
      one rather than sharing ``none``'s name (GHI #839).

    ``base_provenance`` says WHICH tree produced the class, and it changes what
    ``error`` means (GHI #849). On ``working-tree`` the withheld hunk is the only
    difference, so an import failure can only be the missing implementation — a weak
    RED. On ``reconstructed`` (the parent of the commit that introduced the covering
    test) the tree can be months older than the test, so the same class is as likely
    to be unrelated drift and witnesses nothing. Defaults to ``working-tree`` because
    that is what every event predating the field actually ran against; reading the
    absence as unknown would retroactively void the whole prior corpus.
    """

    event: Literal["red_receipt_emitted"]
    req_id: str = Field(..., min_length=1, description="BEHAVIOR REQ under witness")
    receipt_id: str = Field(..., min_length=1, description="ARB red receipt run_id")
    failure_class: Literal["assertion", "error", "none", "not-applicable"] = Field(
        ..., description="How the test failed against the base tree; a closed vocabulary"
    )
    base_commit: str = Field(..., min_length=7, description="Commit the test ran against")
    base_provenance: Literal["working-tree", "reconstructed"] = Field(
        default="working-tree", description="Which tree the base commit is; a closed vocabulary"
    )
    obpi_id: str | None = Field(default=None, description="Owning OBPI, when run in a pipeline")
    test_names: list[str] = Field(
        default_factory=list, description="unittest-addressable names executed"
    )


class AirlockInEvent(_EventBase):
    """airlock_in event — a transit entered the airlock (declare -> ping -> reconcile -> gate)."""

    event: Literal["airlock_in"]


class AirlockOutEvent(_EventBase):
    """airlock_out event — a transit exited the airlock (drift-diff -> decision -> L2)."""

    event: Literal["airlock_out"]


class SurfaceWeightRecalibratedEvent(_EventBase):
    """surface_weight_recalibrated event — the per-turn surface bands and/or floor moved.

    ADR-0.0.33 § Anti-Patterns item 3 makes this event mandatory: *"Adjusting the
    surface-weight green/yellow/red thresholds without an attested recalibration
    event reproduces the doctrine-drift failure the ADR exists to prevent. Band
    changes are ledger events, not config tweaks."*

    It had no producer for the project's entire life (GHI #791).
    ``OBPI-0.0.33-02`` REQ 4 named ``gz adr emit-receipt`` as the emitter, whose
    ``--event`` is a closed enum of ``{completed, validated, closed}``; no other
    verb could emit it and hand-writing the ledger is forbidden. The ledger
    therefore carried zero of these while the bands moved once anyway, as exactly
    the config tweak the anti-pattern names. ``gz validate --surface-weight
    --recalibrate`` is now the producer.

    The band ceilings ride on the event rather than being left implicit in the
    source constants, so "which thresholds were in force at time T" is answerable
    from Layer 2 instead of from a commit diff — the doctrine being witnessed is
    about the thresholds themselves. ``previous_floor_lines`` keeps the superseded
    floor legible after ``surface_weight_floor.json`` overwrites it, which is the
    only durable record of how much the corpus accreted between calibrations.
    """

    event: Literal["surface_weight_recalibrated"]
    attestor: str = Field(..., min_length=1, description="Who attests the recalibration")
    reason: str = Field(..., min_length=1, description="Operational evidence for the change")
    floor_lines: int = Field(..., description="Newly snapshotted corpus line count")
    previous_floor_lines: int = Field(..., description="The floor this recalibration superseded")
    green_ceiling: int = Field(..., description="Green band ceiling in force at recalibration")
    yellow_ceiling: int = Field(..., description="Yellow band ceiling in force at recalibration")


class SessionExitBookmarkSkippedEvent(_EventBase):
    """session_exit_bookmark_skipped event — the exit beat chose not to book.

    Operator ruling 2026-08-05: the floor bookmark is a safety valve, so when an
    authored handoff already covers the session and provably nothing has happened
    since, there is nothing to relieve — *"if we have a proper fresh handoff and a
    clean tree, skip the bookmark."* Emitting one at every exit is what made the
    artifact carry no information; a bookmark's PRESENCE should mean something was
    unfinished.

    Recorded rather than silent on purpose. GHI #756's whole class was *"a
    governed verb whose trigger was never specified — the surface passes every
    test that asks 'does it work?' and fails the only question that matters,
    'does it fire?'"*. A skip that leaves no trace is indistinguishable from a
    crashed hook, which would reintroduce that ambiguity one layer down. This
    event is the difference between "chose not to" and "could not".

    ``handoff_path`` names the authored handoff the beat deferred to, so the skip
    can be audited against the document that justified it.
    """

    event: Literal["session_exit_bookmark_skipped"]
    session_id: str = Field(..., min_length=1, description="Harness session that exited")
    exit_reason: str = Field(..., min_length=1, description="Harness-reported exit reason")
    handoff_path: str = Field(
        ..., min_length=1, description="Authored handoff that made the bookmark redundant"
    )


class HandoffResumeAuthorizedEvent(_EventBase):
    """handoff_resume_authorized event — the operator ruled on a resumed handoff.

    The Layer-2 record that discharges the Operator Authorization Gate
    (`gz-session-handoff` SKILL.md § RESUME): a resuming agent presents the
    handoff's advised steps and may not mutate anything until the operator rules
    and that ruling is booked here (GHI #574).

    ``operator_text`` is the operator's VERBATIM words, passed through unchanged
    per AGENTS.md § Attestation — the same relay model as Gate 5, where the
    mechanism serves the attestation and never gates it. Session-scoped:
    authorization is per ``session_id``, so it cannot leak across sessions and a
    mechanically-written completion handoff (GHI #619) cannot re-arm the gate
    mid-session.
    """

    event: Literal["handoff_resume_authorized"]
    session_id: str = Field(..., min_length=1, description="Harness session the ruling binds to")
    handoff_path: str = Field(..., min_length=1, description="Resumed handoff the ruling covers")
    operator_text: str = Field(
        ..., min_length=1, description="Operator's verbatim authorization words"
    )


class HandoffResumeDecidedEvent(_EventBase):
    """handoff_resume_decided event — the operator's transit decision on a resumed handoff.

    Successor to :class:`HandoffResumeAuthorizedEvent` (GHI #757). That event was
    a consent BOOLEAN — booking it *was* authorization — so an operator who
    reviewed a handoff and ruled *not yet* left no record at all; the register
    could only ever say yes.

    This is an **acknowledge-and-decide transit, not an attestation**. ADR-0.0.33
    § Alternatives rejects the conflation by name: completion-attestation is
    reserved for claims about completed planned work, and spending that register
    on an every-transit gate cheapens it. The predecessor's docstring claimed
    "the same relay model as Gate 5" — that conflation, written down.

    ``decision`` borrows the airlock's ``Decision`` grammar while the records
    stay the handoff layer's own; only ``proceed`` lifts the gate. ``set_aside``
    names advised steps the ruling declines — the clearance-amendment record.
    ``operator_text`` remains VERBATIM by operator ruling (2026-08-05): the word
    is still recorded, only the drawer it is filed in changed.
    """

    event: Literal["handoff_resume_decided"]
    session_id: str = Field(..., min_length=1, description="Harness session the ruling binds to")
    handoff_path: str = Field(..., min_length=1, description="Resumed handoff the ruling covers")
    operator_text: str = Field(..., min_length=1, description="Operator's verbatim ruling words")
    decision: Literal["proceed", "pause", "hold", "revert"] = Field(
        ..., description="Transit decision recorded for the resumed handoff"
    )
    set_aside: list[str] = Field(
        default_factory=list, description="Advised steps this ruling declines"
    )


class HandoffResumeBlockedEvent(_EventBase):
    """handoff_resume_blocked event — the retired gate refused a tool call.

    **HISTORICAL. Nothing emits this event any more** — the resume gate's last
    enforcement arm was retired 2026-08-15 (operator ruling: a handoff is an
    advisor, not a gate-keeping nanny) and its writer went with it. The model is
    RETAINED because the ledger is append-only and carries one such record
    (2026-08-15T00:08, a `Write`); a reader that could not parse it would fail
    validation on committed history.

    That single record is the whole measured lifetime of the arm. Refusal
    recording landed 2026-08-14 to make the false-refusal rate measurable, after
    the gate had accumulated thirteen admission-breadth corrections in
    twenty-nine days — each discovered by an operator hitting it rather than by
    anyone counting. The measurement it enabled ran for one day and read
    9 lifts to 1 block, which is the evidence the retirement rests on. The event
    outlived the mechanism it was built to measure, and answered the question it
    was built to answer.

    ``tool_name`` is the whole payload beyond identity. The event briefly carried
    command-shape fields for the Bash arm; that arm was removed 2026-08-14 and the
    fields went with it rather than remaining as columns that could only ever be
    empty. No on-disk event ever carried them.
    """

    event: Literal["handoff_resume_blocked"]
    session_id: str = Field(..., min_length=1, description="Harness session that was refused")
    handoff_path: str = Field(..., min_length=1, description="Armed handoff the gate cited")
    tool_name: str = Field(..., min_length=1, description="Tool whose call was refused")


class SectionOwnershipGenesisEvent(_EventBase):
    """section_ownership_genesis event — the day-one unowned-byte ratchet floor.

    Layer-2 witness for a surface's FIRST declared floor (OBPI-0.35.0-04). It
    exists because a genesis declaration used to be witnessed only by
    self-coherence — its stored floor merely agreeing with the summed span of
    its own `unowned` sections — and that is precisely what an attacker
    recomputes after hand-editing the declaration. A Step-4b adversary raised a
    floor 8637 -> 10182 with no ledger file in existence and the loader accepted
    it. `load_declaration` now refuses a null `floor_event_id` outright, so
    genesis is a witnessed STATE rather than a coherent SHAPE, which is what
    AGENTS.md demands of any gate ("name the STATE it must observe").
    """

    event: Literal["section_ownership_genesis"]
    surface: str
    sections_digest: str | None = Field(
        default=None,
        description=(
            "Fingerprint of the section-ownership map this event witnesses. Optional on "
            "the MODEL because the ledger is append-only and carries rows minted before "
            "the field existed; `load_declaration` refuses to trust a witness lacking it, "
            "so the enforcement point is the loader, never the schema (GHI: Step-4b "
            "round-3 finding 2)."
        ),
    )
    new_unowned_byte_floor: int


class UnownedRatchetUpdatedEvent(_EventBase):
    """unowned_ratchet_updated event — the ordinary, decrease-only floor move.

    Emitted when a recorded total is less than or equal to the stored floor
    (REQ-0.35.0-04-03). An increase is unreachable here by construction; raising
    the floor is the attested `gz content unown` path alone, which emits
    `section_ownership_unowned` instead.
    """

    event: Literal["unowned_ratchet_updated"]
    surface: str
    sections_digest: str | None = Field(
        default=None,
        description=(
            "Fingerprint of the section-ownership map this event witnesses. Optional on "
            "the MODEL because the ledger is append-only and carries rows minted before "
            "the field existed; `load_declaration` refuses to trust a witness lacking it, "
            "so the enforcement point is the loader, never the schema (GHI: Step-4b "
            "round-3 finding 2)."
        ),
    )
    prior_unowned_byte_floor: int
    new_unowned_byte_floor: int


class SectionOwnershipUnownedEvent(_EventBase):
    """section_ownership_unowned event — the ATTESTED raise-path.

    The only path by which the ratchet floor may rise (REQ-0.35.0-04-05). It
    carries `attestor` and `reason` because un-owning a section is a change to
    canon and takes the same ceremony as any other, and because those two fields
    are what a later reader has to reconstruct why coverage shrank.
    """

    event: Literal["section_ownership_unowned"]
    surface: str
    sections_digest: str | None = Field(
        default=None,
        description=(
            "Fingerprint of the section-ownership map this event witnesses. Optional on "
            "the MODEL because the ledger is append-only and carries rows minted before "
            "the field existed; `load_declaration` refuses to trust a witness lacking it, "
            "so the enforcement point is the loader, never the schema (GHI: Step-4b "
            "round-3 finding 2)."
        ),
    )
    section: str
    prior_unowned_byte_floor: int
    new_unowned_byte_floor: int
    attestor: str
    reason: str


class SectionOwnershipReanchoredEvent(_EventBase):
    """section_ownership_reanchored event — the CHAINED re-anchor of a floor.

    Exists because `section_ownership_genesis` is restricted to a surface's
    FIRST ownership event (Step-4b round-4 CRITICAL finding: the loader accepted
    a LATE genesis row as a fresh baseline, so minting one reset the ratchet
    floor to whatever the attacker chose). Once genesis is first-only, a
    LEGITIMATE floor migration — the `sections_digest` field arriving mid-flight
    is the motivating case — has nowhere to land. This type is that landing
    place, and it is deliberately not a second day-one.

    The three fields genesis does NOT carry are the whole point.
    ``prior_unowned_byte_floor`` states what the re-anchor moves FROM,
    ``predecessor_event_id`` names the ownership event it re-anchors, and
    ``reason`` records why the migration was legitimate. Together they make the
    event a LINK in the chain a reader can walk back to the one true genesis,
    rather than a new root that severs it.
    """

    event: Literal["section_ownership_reanchored"]
    surface: str
    sections_digest: str | None = Field(
        default=None,
        description=(
            "Fingerprint of the section-ownership map this event witnesses. Optional on "
            "the MODEL because the ledger is append-only and carries rows minted before "
            "the field existed; `load_declaration` refuses to trust a witness lacking it, "
            "so the enforcement point is the loader, never the schema (GHI: Step-4b "
            "round-3 finding 2)."
        ),
    )
    prior_unowned_byte_floor: int
    new_unowned_byte_floor: int
    predecessor_event_id: str
    reason: str


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
    | ObpiLockTtlWarningEvent
    | ObpiWithdrawnEvent
    | ObpiParkedEvent
    | ObpiUnparkedEvent
    | ObpiBlockedOnOperatorEvent
    | ObpiUnblockedEvent
    | Stage2DispatchRecordedEvent
    | Stage2SingleDriverDeclaredEvent
    | ObpiSupersededEvent
    | ObpiCompletionRepudiatedEvent
    | SecurityFloorOverriddenEvent
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
    | CorpusEntryRetiredEvent
    | CorpusRetirementReconciledEvent
    | CompositionCandidateEmittedEvent
    | RenditionCommittedEvent
    | RenditionAdvisorVerdictEvent
    | BriefReconciledEvent
    | BriefReconcileDriftDetectedEvent
    | BriefReconcileDriftOverriddenEvent
    | EnforcementClaimVerifiedEvent
    | MxSessionOpenedEvent
    | MxSessionClosedEvent
    | BlocksEvent
    | BlockedByEvent
    | DiscoveredFromEvent
    | ValidatesEvent
    | AirlockInEvent
    | AirlockOutEvent
    | HandoffResumeAuthorizedEvent
    | HandoffResumeDecidedEvent
    | HandoffResumeBlockedEvent
    | AdversarialValidationEvent
    | RedReceiptEmittedEvent
    | FoundationGrandfatheredEvent
    | SectionOwnershipGenesisEvent
    | UnownedRatchetUpdatedEvent
    | SectionOwnershipUnownedEvent
    | SectionOwnershipReanchoredEvent,
    Field(discriminator="event"),
]

_typed_event_adapter: TypeAdapter[TypedLedgerEvent] = TypeAdapter(TypedLedgerEvent)


def parse_typed_event(data: dict[str, Any]) -> TypedLedgerEvent:
    """Parse a raw dict into a typed event model via discriminated union."""
    return _typed_event_adapter.validate_python(data)
