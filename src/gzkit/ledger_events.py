"""Event factory functions for the governance ledger.

Each function constructs a typed ``LedgerEvent`` with the correct event name
and extra payload.  Keeping them in a dedicated module keeps ``ledger.py``
under the 600-line module limit while preserving the same public API via
re-exports.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from gzkit.ledger import LedgerEvent

if TYPE_CHECKING:
    from gzkit.event_evidence import EventAnchor

# ---------------------------------------------------------------------------
# Event factory functions for type safety and documentation
# ---------------------------------------------------------------------------


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


def obpi_withdrawn_event(obpi_id: str, parent: str, reason: str, attestor: str = "") -> LedgerEvent:
    """Create an OBPI withdrawn event.

    ``attestor`` records the human witness of the withdrawal transition
    (OBPI-0.31.0-02): the ``withdrawn`` transition in OBPI-01's
    ``CANONICAL_TRANSITIONS`` declares a ``human_attested`` witness requirement,
    so the witnessing attestor is carried on the emitted event. The witness is
    enforced non-empty at the CLI boundary (``obpi_withdraw_cmd``); the default
    keeps this lower-level factory usable by fixtures and status/reconciliation
    call sites that construct withdrawal events without a witness context.
    """
    return LedgerEvent(
        event="obpi_withdrawn",
        id=obpi_id,
        parent=parent,
        extra={"reason": reason, "attestor": attestor},
    )


def obpi_parked_event(
    obpi_id: str,
    parent: str,
    parked_to: str,
    reason: str = "pool_demotion",
) -> LedgerEvent:
    """Create an OBPI parked event (GHI #584).

    Park is the reversible counterpart to withdraw. ``parked_to`` names the pool
    id the parent ADR became, so a parked OBPI's lineage still resolves after the
    rename — the property the GHI #520 demotion destroyed by emitting no child
    event at all.
    """
    return LedgerEvent(
        event="obpi_parked",
        id=obpi_id,
        parent=parent,
        extra={"parked_to": parked_to, "reason": reason},
    )


def obpi_unparked_event(
    obpi_id: str,
    parent: str,
    unparked_from: str,
    reason: str = "pool_promotion",
) -> LedgerEvent:
    """Create an OBPI unparked event — release on parent re-promotion (GHI #584)."""
    return LedgerEvent(
        event="obpi_unparked",
        id=obpi_id,
        parent=parent,
        extra={"unparked_from": unparked_from, "reason": reason},
    )


def obpi_completion_repudiated_event(
    obpi_id: str,
    parent: str,
    repudiated_receipt: str,
    cause: str,
    attestor: str,
    reason: str,
) -> LedgerEvent:
    """Create an obpi_completion_repudiated event (ADR-0.0.71)."""
    return LedgerEvent(
        event="obpi_completion_repudiated",
        id=obpi_id,
        parent=parent,
        extra={
            "repudiated_receipt": repudiated_receipt,
            "cause": cause,
            "attestor": attestor,
            "reason": reason,
        },
    )


def ledger_event_corrected_event(
    *,
    subject_event: str,
    subject_id: str,
    subject_ts: str,
    disposition: str,
    cause: str,
    attestor: str,
    reason: str,
    parent: str | None = None,
) -> LedgerEvent:
    """Create a ``ledger_event_corrected`` event (GHI #611).

    The append-only corrective action: the subject row is never touched, and
    this forward event is what every reader nets against it
    (:mod:`gzkit.ledger_corrections`). The event's ``id`` is the SUBJECT's id so
    the correction attaches to the artifact it corrects.

    Minted THROUGH :class:`~gzkit.events.LedgerEventCorrectedEvent` rather than
    straight into an untyped ``extra`` bag, so the factory cannot produce what
    both validators reject. ``LedgerEvent.extra`` is ``dict[str, Any]`` and
    validates nothing about its contents; building the row directly let an empty
    attestor and reason through the one constructor callers actually reach.
    Raises ``pydantic.ValidationError`` on an invalid correction.
    """
    from gzkit.events import LedgerEventCorrectedEvent

    typed = LedgerEventCorrectedEvent(
        event="ledger_event_corrected",
        id=subject_id,
        parent=parent,
        subject_event=subject_event,
        subject_id=subject_id,
        subject_ts=subject_ts,
        disposition=disposition,  # ty: ignore[invalid-argument-type]
        cause=cause,  # ty: ignore[invalid-argument-type]
        attestor=attestor,
        reason=reason,
    )
    return LedgerEvent.model_validate(typed.model_dump())


def security_floor_overridden_event(
    *,
    obpi_id: str,
    surfaces: str,
    reason: str,
    attestor: str,
) -> LedgerEvent:
    """Create a security_floor_overridden event (ADR-0.0.72-04).

    Witnesses an operator override of the completion security floor
    (``gz obpi complete --accept-security-floor``) so the override is
    auditable via ledger census rather than a console-only line.
    """
    return LedgerEvent(
        event="security_floor_overridden",
        id=obpi_id,
        parent=obpi_id,
        extra={
            "obpi_id": obpi_id,
            "surfaces": surfaces,
            "reason": reason,
            "attestor": attestor,
        },
    )


def obpi_blocked_on_operator_event(
    obpi_id: str,
    parent: str,
    reason: str,
    next_operator_action: str,
) -> LedgerEvent:
    """Create an obpi_blocked_on_operator event (GHI #887).

    Both payload fields are required with no default. The block exists so a
    reader other than its author can discharge it, and a block naming no awaited
    action is a complaint rather than a state — the shape that let the incident
    run: four agents each re-derived that a human was needed and none could say so.
    """
    return LedgerEvent(
        event="obpi_blocked_on_operator",
        id=obpi_id,
        parent=parent,
        extra={"reason": reason, "next_operator_action": next_operator_action},
    )


def obpi_unblocked_event(
    obpi_id: str,
    parent: str,
    ruling: str,
    operator: str,
) -> LedgerEvent:
    """Create an obpi_unblocked event (GHI #887).

    The inverse of :func:`obpi_blocked_on_operator_event`. ``ruling`` carries the
    operator's decision verbatim per ``AGENTS.md`` § Attestation — the agent seats
    the operator's words, never rewrites them.
    """
    return LedgerEvent(
        event="obpi_unblocked",
        id=obpi_id,
        parent=parent,
        extra={"ruling": ruling, "operator": operator},
    )


def stage2_dispatch_recorded_event(
    obpi_id: str,
    parent: str,
    role: str,
    model: str,
    task_id: int,
) -> LedgerEvent:
    """Create a stage2_dispatch_recorded event (GHI #886).

    One row per dispatched role. The channel credits a role from these rows and
    from nothing else, so the append-only ledger — not the disposable pipeline
    marker — is what a Stage-5 verdict traces to.
    """
    return LedgerEvent(
        event="stage2_dispatch_recorded",
        id=obpi_id,
        parent=parent,
        extra={"role": role, "model": model, "task_id": task_id},
    )


def stage2_single_driver_declared_event(
    obpi_id: str,
    parent: str,
    reason: str,
) -> LedgerEvent:
    """Create a stage2_single_driver_declared event (GHI #886).

    ``reason`` is required and non-empty for the same argument that makes the
    declaration permissible at all: declaring is compliant precisely because it
    is VISIBLE, and a declaration naming no reason discloses nothing.
    """
    return LedgerEvent(
        event="stage2_single_driver_declared",
        id=obpi_id,
        parent=parent,
        extra={"reason": reason},
    )


def obpi_superseded_event(
    obpi_id: str,
    parent: str,
    superseded_by: str,
    rationale: str,
    attestor: str,
) -> LedgerEvent:
    """Create an obpi_superseded event (OBPI-0.31.0-02).

    ``superseded_by`` records the successor OBPI; ``attestor`` records the
    human witness of the ``superseded`` transition (OBPI-01's
    ``CANONICAL_TRANSITIONS`` declares a ``human_attested`` witness
    requirement). No default: this is a brand-new event with no legacy
    positional callers to protect.
    """
    return LedgerEvent(
        event="obpi_superseded",
        id=obpi_id,
        parent=parent,
        extra={
            "superseded_by": superseded_by,
            "rationale": rationale,
            "attestor": attestor,
        },
    )


def adr_created_event(adr_id: str, parent: str, lane: str) -> LedgerEvent:
    """Create an ADR created event."""
    return LedgerEvent(
        event="adr_created",
        id=adr_id,
        parent=parent,
        extra={"lane": lane},
    )


def artifact_edited_event(
    path: str, session: str | None = None, commit: str | None = None
) -> LedgerEvent:
    """Create an artifact edited event (from hooks).

    ``commit`` is set only by the commit-locus backstop
    (:mod:`gzkit.hooks.commit_ledger`, GHI #847) and names the SHA whose diff
    the row was derived from. Its absence marks a tool-locus row, so the two
    recorders stay distinguishable in the record they share.
    """
    extra: dict[str, Any] = {"path": path}
    if session:
        extra["session"] = session
    if commit:
        extra["commit"] = commit
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


def audit_generated_event(
    adr_id: str,
    audit_file: str,
    audit_plan_file: str,
    passed: bool,
) -> LedgerEvent:
    """Create an audit-generated event recording that audit artifacts were created."""
    return LedgerEvent(
        event="audit_generated",
        id=adr_id,
        extra={
            "audit_file": audit_file,
            "audit_plan_file": audit_plan_file,
            "passed": passed,
        },
    )


def audit_receipt_emitted_event(
    adr_id: str,
    receipt_event: str,
    attestor: str,
    evidence: dict[str, Any] | None = None,
    anchor: "EventAnchor | None" = None,
) -> LedgerEvent:
    """Create an audit receipt event."""
    extra: dict[str, Any] = {"receipt_event": receipt_event, "attestor": attestor}
    if evidence is not None:
        extra["evidence"] = evidence
    if anchor is not None:
        extra["anchor"] = anchor.model_dump(exclude_none=True)
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
    anchor: "EventAnchor | None" = None,
) -> LedgerEvent:
    """Create an OBPI receipt event."""
    extra: dict[str, Any] = {"receipt_event": receipt_event, "attestor": attestor}
    if evidence is not None:
        extra["evidence"] = evidence
    if obpi_completion is not None:
        extra["obpi_completion"] = obpi_completion
    if anchor is not None:
        extra["anchor"] = anchor.model_dump(exclude_none=True)
    return LedgerEvent(
        event="obpi_receipt_emitted",
        id=obpi_id,
        parent=parent_adr,
        extra=extra,
    )


def artifact_renamed_event(
    old_id: str, new_id: str, reason: str | None = None, task_id: str | None = None
) -> LedgerEvent:
    """Create an artifact rename event used for ID migrations.

    ``artifact_renamed`` is a TASK worklog type (``_TASK_WORKLOG_TYPES``), so a
    rename emitted while a TASK is active MUST carry ``task_id`` or Signature (a)
    of ``gz validate --task-envelope-coherence`` fails closed. This producer went
    unattributed until ADR-0.34.0 OBPI-04: the only prior bulk demotion (GHI #520,
    2026-05-23) predates ``_TASK_ENVELOPE_ENFORCEMENT_EPOCH``, so the gap never
    surfaced. Optional because renames also occur outside any TASK envelope.
    """
    extra: dict[str, Any] = {"new_id": new_id}
    if reason:
        extra["reason"] = reason
    if task_id:
        extra["task_id"] = task_id
    return LedgerEvent(
        event="artifact_renamed",
        id=old_id,
        extra=extra,
    )


def foundation_grandfathered_event(
    adr_id: str,
    title: str,
    semver: str,
    frozen_at: str,
    attestor: str,
) -> LedgerEvent:
    """Create a foundation_grandfathered terminality witness (ADR-0.34.0, OBPI-04).

    ``adr_id`` MUST be the full slugged ADR id form (e.g.
    ``ADR-0.0.9-state-doctrine-source-of-truth``), never a bare semver
    (``ADR-0.0.9``) — the reader
    (``gzkit.governance.trust_audits.taxonomy._grandfathered_event_ids``) does
    exact string set-difference against on-disk frontmatter ids, so a
    bare-semver id would silently fail the terminal-partition gate.

    ``attestor`` is REQUIRED and fail-closed non-empty: this event IS the
    terminality witness the taxonomy gate consumes, and that reader accepts any
    event of this type carrying a non-empty id without inspecting the witness.
    A defaulted-empty attestor would therefore make the factory itself a
    fabrication path — a witnessless event that satisfies the SUPPORT gate. No
    default: this is a new event with no legacy positional callers to protect
    (same posture as ``obpi_superseded_event``).
    """
    if not attestor.strip():
        msg = (
            "foundation_grandfathered requires a non-empty attestor — the event IS the "
            "Gate-5 terminality witness, and the taxonomy reader does not inspect it, "
            "so an empty attestor would fabricate the witness it claims to record."
        )
        raise ValueError(msg)
    return LedgerEvent(
        event="foundation_grandfathered",
        id=adr_id,
        extra={
            "title": title,
            "semver": semver,
            "frozen_at": frozen_at,
            "attestor": attestor,
        },
    )


def adr_eval_completed_event(
    adr_id: str,
    verdict: str,
    adr_weighted_total: float,
    obpi_count: int,
    action_item_count: int,
) -> LedgerEvent:
    """Create an ADR evaluation completed event."""
    return LedgerEvent(
        event="adr_eval_completed",
        id=adr_id,
        extra={
            "verdict": verdict,
            "adr_weighted_total": adr_weighted_total,
            "obpi_count": obpi_count,
            "action_item_count": action_item_count,
        },
    )


def adr_evaluation_event(
    *,
    artifact_id: str,
    artifact_type: str,
    dimensions: dict[str, float],
    scores: dict[str, float],
    weighted_total: float,
    red_team_challenges_fired: list[str],
    evaluator_persona: str,
    timestamp: str,
) -> LedgerEvent:
    """Create a full per-dimension adr-evaluation event (ADR-0.0.26 Decision item 1)."""
    return LedgerEvent(
        event="adr-evaluation",
        id=artifact_id,
        extra={
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "dimensions": dimensions,
            "scores": scores,
            "weighted_total": weighted_total,
            "red_team_challenges_fired": red_team_challenges_fired,
            "evaluator_persona": evaluator_persona,
            "timestamp": timestamp,
        },
    )


def obpi_completion_uncovered_accept_event(
    *,
    obpi_id: str,
    req_id: str,
    operator: str,
    rationale: str,
    acceptance_type: str,
) -> LedgerEvent:
    """Create an event recording one accepted-uncovered REQ waiver (ADR-0.0.25-02)."""
    return LedgerEvent(
        event="obpi_completion_uncovered_accept",
        id=obpi_id,
        parent=obpi_id,
        extra={
            "obpi_id": obpi_id,
            "req_id": req_id,
            "operator": operator,
            "rationale": rationale,
            "acceptance_type": acceptance_type,
        },
    )


def brief_reconcile_drift_overridden_event(
    *,
    brief_id: str,
    attestor: str,
    reason: str,
    original_receipt_id: str | None = None,
    original_drift_dimensions: list[str] | None = None,
) -> "LedgerEvent":
    """Create an event recording an accepted stale/drifted reconciliation (OBPI-0.0.37-08)."""
    return LedgerEvent(
        event="brief_reconcile_drift_overridden",
        id=brief_id,
        parent=brief_id,
        extra={
            "brief_id": brief_id,
            "override_ts": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "attestor": attestor,
            "reason": reason,
            "original_receipt_id": original_receipt_id,
            "original_drift_dimensions": original_drift_dimensions or [],
        },
    )


def lifecycle_transition_event(
    artifact_id: str,
    content_type: str,
    from_state: str,
    to_state: str,
) -> LedgerEvent:
    """Create a lifecycle state transition event."""
    return LedgerEvent(
        event="lifecycle_transition",
        id=artifact_id,
        extra={
            "content_type": content_type,
            "from_state": from_state,
            "to_state": to_state,
        },
    )


def obpi_lock_claimed_event(
    obpi_id: str,
    agent: str,
    ttl_minutes: int,
    branch: str,
    session_id: str,
) -> LedgerEvent:
    """Create an OBPI lock claimed event."""
    return LedgerEvent(
        event="obpi_lock_claimed",
        id=obpi_id,
        extra={
            "agent": agent,
            "ttl_minutes": ttl_minutes,
            "branch": branch,
            "session_id": session_id,
        },
    )


def obpi_lock_released_event(
    obpi_id: str,
    agent: str,
    force: bool = False,
    handoff_path: str | None = None,
) -> LedgerEvent:
    """Create an OBPI lock released event.

    The ``handoff_path`` field carries the project-relative path of the register
    entry that authorized the surrender (token-block discipline, ADR-0.0.41).
    Optional in OBPI-02 (additive, backward-compatible); OBPI-03 will require
    it at every emission site.
    """
    extra: dict[str, object] = {"agent": agent, "force": force}
    if handoff_path is not None:
        extra["handoff_path"] = handoff_path
    return LedgerEvent(
        event="obpi_lock_released",
        id=obpi_id,
        extra=extra,
    )


def obpi_lock_ttl_warning_event(
    obpi_id: str,
    agent: str,
    elapsed_minutes: float,
    ttl_minutes: int,
) -> LedgerEvent:
    """Create an OBPI lock TTL-warning event (token-block-discipline.md § Sub-Invariant 4).

    Emitted by the SessionStart hook when a held lock has crossed 50% of its
    TTL but has not yet expired (expired locks are reaped, not warned).
    """
    return LedgerEvent(
        event="obpi_lock_ttl_warning",
        id=obpi_id,
        extra={
            "agent": agent,
            "elapsed_minutes": elapsed_minutes,
            "ttl_minutes": ttl_minutes,
        },
    )


def pipeline_launched_event(
    obpi_id: str,
    parent_adr: str,
    lane: str,
    nonce: str,
    marker_path: str,
    entry: str | None = None,
) -> LedgerEvent:
    """Record a pipeline launch with marker nonce (GHI #412).

    Emitted by ``gz obpi pipeline`` at Stage 1 immediately after writing the
    active marker. The nonce in this event is the same one persisted in the
    marker payload; the agent-relayed attestation gate cross-references the
    pair to refuse forged markers whose nonce does not appear in the ledger.
    """
    extra: dict[str, Any] = {
        "nonce": nonce,
        "marker_path": marker_path,
        "lane": lane,
    }
    if entry is not None:
        extra["entry"] = entry
    return LedgerEvent(
        event="pipeline_launched",
        id=obpi_id,
        parent=parent_adr,
        extra=extra,
    )


def pipeline_marker_purged_event(
    obpi_id: str,
    parent_adr: str,
    reason: str,
    marker_path: str,
) -> LedgerEvent:
    """Record auto-purge of a stale pipeline-active marker (GHI #399).

    Emitted by the pipeline launcher when it discovers a ``.pipeline-active-*``
    marker whose OBPI is already ``attested_completed`` in the ledger — the
    marker is provably orphaned (Stage 5 cleanup never fired) and is removed
    so the next pipeline invocation isn't fail-closed by it. Recording the
    cleanup as a ledger event keeps the runtime's marker mutations auditable.
    """
    return LedgerEvent(
        event="pipeline_marker_purged",
        id=obpi_id,
        parent=parent_adr,
        extra={"reason": reason, "marker_path": marker_path},
    )


def distribution_baseline_regenerated_event(
    surfaces_walked: list[str],
    file_count: int,
    manifest_hash_before: str,
    manifest_hash_after: str,
) -> LedgerEvent:
    """Create an event recording a distribution baseline manifest regeneration (OBPI-0.0.32-15).

    Symmetric to ``gz register-adrs`` for the ADR status index; records manifest
    hash before/after so Layer-2 truth captures every regeneration.
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="distribution_baseline_regenerated",
        id=f"distribution-baseline-regen-{timestamp}",
        ts=timestamp,
        extra={
            "surfaces_walked": list(surfaces_walked),
            "file_count": file_count,
            "manifest_hash_before": manifest_hash_before,
            "manifest_hash_after": manifest_hash_after,
        },
    )


def agent_sync_completed_event(
    updated_paths: list[str],
    canonical_rule_count: int,
) -> LedgerEvent:
    """Create an event recording a successful agent control-surface sync (GHI #369).

    Mechanical witness for ``gz agent sync control-surfaces`` runs so brief-level
    requirements (e.g. OBPI-0.0.23-03 REQ-04) can satisfy "sync ran" without
    requiring an ARB receipt wrapper. The event is emitted on every real sync —
    operator-initiated, hook-driven, or ``gz tidy --fix`` — and is suppressed in
    snapshot-replay paths (``plan_sync_all`` in ``validate_pkg/sync_parity.py``).
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="agent_sync_completed",
        id=f"agent-sync-{timestamp}",
        ts=timestamp,
        extra={
            "updated_paths": list(updated_paths),
            "canonical_rule_count": canonical_rule_count,
        },
    )


def patch_release_event(
    version: str,
    previous_version: str,
    tag: str | None,
    ghi_summary: list[dict[str, Any]],
    manifest_path: str,
    foundation_summary: list[dict[str, Any]] | None = None,
) -> LedgerEvent:
    """Create a patch-release event for the governance ledger.

    *foundation_summary* records foundation-ADR closeouts that qualified the
    release as a code surface equal to behavior-level GHIs (GHI #490).
    """
    return LedgerEvent(
        event="patch-release",
        id=f"v{version}",
        extra={
            "version": version,
            "previous_version": previous_version,
            "tag": tag,
            "ghi_summary": ghi_summary,
            "foundation_summary": foundation_summary or [],
            "manifest_path": manifest_path,
        },
    )


def composition_rendered_event(
    invariant_count: int,
    target: str,
    byte_count: int,
) -> LedgerEvent:
    """Create an event recording a successful constitutional invariant composition render."""
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="composition_rendered",
        id=f"composition-rendered-{timestamp}",
        ts=timestamp,
        extra={
            "invariant_count": invariant_count,
            "target": target,
            "byte_count": byte_count,
            "render_ts": timestamp,
        },
    )


def composition_drift_detected_event(
    target: str,
    diff_first_50_lines: str,
) -> LedgerEvent:
    """Create an event recording drift between rendered registry and committed target."""
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="composition_drift_detected",
        id=f"composition-drift-{timestamp}",
        ts=timestamp,
        extra={
            "target": target,
            "diff_first_50_lines": diff_first_50_lines,
            "render_ts": timestamp,
        },
    )


def composition_candidate_emitted_event(
    surface: str,
    consumer: str,
    setpoint: str,
    invariant_bytes: int,
    compressible_bytes_before: int,
    compressible_bytes_after: int,
    total_bytes: int,
) -> LedgerEvent:
    """Create a composition_candidate_emitted event (ADR-0.0.37, OBPI-0.0.37-21).

    Layer-2 witness that ``gz content compose`` validated and staged a candidate
    rendition. Carries per-tier byte evidence for the compose audit trail.
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="composition_candidate_emitted",
        id=f"composition-candidate-emitted-{timestamp}",
        ts=timestamp,
        extra={
            "surface": surface,
            "consumer": consumer,
            "setpoint": setpoint,
            "invariant_bytes": invariant_bytes,
            "compressible_bytes_before": compressible_bytes_before,
            "compressible_bytes_after": compressible_bytes_after,
            "total_bytes": total_bytes,
        },
    )


def rendition_committed_event(
    surface: str,
    consumer: str,
    corpus_fingerprint: str,
    attestor: str,
) -> LedgerEvent:
    """Create a rendition_committed event (ADR-0.0.37, OBPI-0.0.37-22).

    Layer-2 witness that ``gz content commit`` promoted a staged candidate to the
    durable committed rendition under operator attestation (Gate 5), freezing the
    corpus content-fingerprint the rendition was attested against.
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="rendition_committed",
        id=f"rendition-committed-{timestamp}",
        ts=timestamp,
        extra={
            "surface": surface,
            "consumer": consumer,
            "corpus_fingerprint": corpus_fingerprint,
            "attestor": attestor,
        },
    )


def rendition_advisor_verdict_event(
    surface: str,
    consumer: str | None,
    receipt_id: str,
    score: float,
) -> LedgerEvent:
    """Create a rendition_advisor_verdict event (ADR-0.0.37, OBPI-0.0.37-24).

    Layer-2 witness that ``gz content advise-rendition`` recorded an
    information-retained-per-byte verdict as an ARB receipt. Advisory, never
    gating — emitted on every successful record regardless of the score value.
    """
    timestamp = datetime.now(UTC).isoformat()
    extra: dict[str, Any] = {
        "surface": surface,
        "receipt_id": receipt_id,
        "score": score,
    }
    if consumer is not None:
        extra["consumer"] = consumer
    return LedgerEvent(
        event="rendition_advisor_verdict",
        id=f"rendition-advisor-verdict-{timestamp}",
        ts=timestamp,
        extra=extra,
    )


def corpus_entry_appended_event(
    surface: str,
    section: str,
    entry_id: str,
    tier: str,
) -> LedgerEvent:
    """Create a corpus_entry_appended event (ADR-0.0.37 § Re-Alignment, OBPI-19).

    Layer-2 witness for a ``gz content remember`` append to the per-surface corpus
    store. Mirrors ``composition_rendered_event``'s shape.
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="corpus_entry_appended",
        id=f"corpus-entry-appended-{timestamp}",
        ts=timestamp,
        extra={
            "surface": surface,
            "section": section,
            "entry_id": entry_id,
            "tier": tier,
        },
    )


def floor_direction_for(added: set[str], removed: set[str]) -> str:
    """Return the ledger discriminator for an invariant-liveness delta.

    Lives HERE, beside the factory, so the witness is DERIVED from the gate's own
    two sets rather than asserted by the caller. A round-8 adversary probe showed
    the caller-supplied form was constructible into a lie: `floor_direction='grew'`
    with `floor_moved_ids=[]` validated clean under both readers, so a producer
    could claim the floor grew while naming nothing that moved. Deriving both
    fields from one input makes that state unrepresentable.
    """
    if added and removed:
        return "changed"
    if added:
        return "grew"
    if removed:
        return "shrank"
    return "unchanged"


def corpus_entry_retired_event(
    surface: str,
    retired_entry_id: str,
    retraction_entry_id: str,
    reason: str,
    tier: str,
    floor_added: set[str],
    floor_removed: set[str],
    attestor: str = "",
) -> LedgerEvent:
    """Create a corpus_entry_retired event (GHI #635, OBPI-0.35.0-02).

    Layer-2 witness for a ``gz content retire`` append. Distinct from
    ``corpus_entry_appended`` because retirement mutates what canon *currently*
    requires — the invariant floor moves — and that is the fact an auditor needs to
    find, not merely that a row was added. Which WAY it moved is ``floor_direction``;
    retirement is not shrink-only.

    ``tier`` is the RETIRED entry's own tier, always known. ``attestor`` is
    legitimately empty on a compressible-tier retirement — only the invariant
    floor requires a named attestor (`retire.py`'s corpus-attestation gate).

    ``floor_direction`` and ``floor_moved_ids`` record the invariant-liveness DELTA
    the attestor gate actually reads, so Layer 2 can witness the condition that
    required attestation rather than the retired row's tier, which is only a proxy
    for it (round-6 adversary, 2026-08-25). Both default empty because the ledger is
    append-only and committed rows predating them can never grow the keys.
    """
    overlap = floor_added & floor_removed
    if overlap:
        # A real before/after delta over one fold is DISJOINT by construction: an
        # invariant id cannot be both revived and un-bound by a single retirement.
        # A round-9 adversary probe passed the same id in both sets and got a
        # ledger-valid `changed` witness naming one id -- an impossible state that
        # both readers accepted. Refuse it at the boundary rather than emit it.
        raise ValueError(
            f"floor_added and floor_removed overlap on {sorted(overlap)}: a retirement "
            "cannot both revive and un-bind the same invariant entry. The two sets come "
            "from one before/after fold and are disjoint by construction."
        )

    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="corpus_entry_retired",
        id=f"corpus-entry-retired-{timestamp}",
        ts=timestamp,
        extra={
            "surface": surface,
            "retired_entry_id": retired_entry_id,
            "retraction_entry_id": retraction_entry_id,
            "reason": reason,
            "tier": tier,
            "attestor": attestor,
            "floor_direction": floor_direction_for(floor_added, floor_removed),
            "floor_moved_ids": sorted(floor_added | floor_removed),
        },
    )


def corpus_retirement_reconciled_event(
    surface: str,
    retired_entry_id: str,
    retraction_entry_id: str,
    reason: str,
    origin: str = "",
) -> LedgerEvent:
    """Create a corpus_retirement_reconciled event (GHI #885 arm 2, GHI #878).

    Layer-2 accounting for a retraction row that reached the corpus WITHOUT the
    governed ``gz content retire`` path — either hand-appended (the #885 bypass)
    or left behind when the verb died between its corpus write and its ledger
    appends (the #878 partial-write window).

    DELIBERATELY NOT ``corpus_entry_retired``. Emitting that type here would
    stamp today's timestamp and an attestor onto a procedure that never ran — a
    fabricated receipt under ``AGENTS.md`` § Attestation, and the exact
    presence-for-proof substitution GHI #885 exists to remove. This event
    asserts only what is true: a tombstone was FOUND without a witness and
    accounted for on ``ts``. It carries no attestor and no floor delta, because
    the reconciler observed neither — the retirement it describes happened at an
    unknown earlier time under unknown authority, and ``origin`` preserves
    whatever forensic trace the corpus row itself carries.

    ``gz validate --corpus-retirement-witness`` accepts it as a witness. That is
    the point: the gate asks whether Layer 2 accounts for the canon change, not
    whether the change was governed. Whether it WAS governed is readable from
    which event type answers — and that distinction survives only because the
    two types are separate.
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="corpus_retirement_reconciled",
        id=f"corpus-retirement-reconciled-{timestamp}",
        ts=timestamp,
        extra={
            "surface": surface,
            "retired_entry_id": retired_entry_id,
            "retraction_entry_id": retraction_entry_id,
            "reason": reason,
            "origin": origin,
        },
    )


def brief_reconciled_event(
    brief_id: str,
    has_drift: bool,
    allowlist_delta_count: int,
    discovery_delta_count: int,
    verification_delta_count: int,
    req_count_delta: int,
    citation_delta_count: int,
    *,
    applied: bool = False,
    attestor: str | None = None,
) -> LedgerEvent:
    """Create a brief_reconciled event (ADR-0.0.37, OBPI-06).

    Summary record for one ``gz obpi brief-drift`` run. ``applied`` / ``attestor``
    are set only when ``--apply --attestor`` wrote amendments back to the brief.
    """
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="brief_reconciled",
        id=f"brief-reconciled-{timestamp}",
        ts=timestamp,
        extra={
            "brief_id": brief_id,
            "has_drift": has_drift,
            "allowlist_delta_count": allowlist_delta_count,
            "discovery_delta_count": discovery_delta_count,
            "verification_delta_count": verification_delta_count,
            "req_count_delta": req_count_delta,
            "citation_delta_count": citation_delta_count,
            "applied": applied,
            "attestor": attestor,
        },
    )


def brief_reconcile_drift_detected_event(
    brief_id: str,
    allowlist_missing_in_brief: list[str],
    allowlist_missing_on_disk: list[str],
    discovery_unresolved_paths: list[str],
    verification_unresolved_verbs: list[str],
    declared_reqs: int,
    acceptance_criteria_count: int,
    req_count_delta: int,
    citation_stale: list[str],
) -> LedgerEvent:
    """Create a brief_reconcile_drift_detected event with the full delta payload (OBPI-06)."""
    timestamp = datetime.now(UTC).isoformat()
    return LedgerEvent(
        event="brief_reconcile_drift_detected",
        id=f"brief-reconcile-drift-{timestamp}",
        ts=timestamp,
        extra={
            "brief_id": brief_id,
            "allowlist_missing_in_brief": allowlist_missing_in_brief,
            "allowlist_missing_on_disk": allowlist_missing_on_disk,
            "discovery_unresolved_paths": discovery_unresolved_paths,
            "verification_unresolved_verbs": verification_unresolved_verbs,
            "declared_reqs": declared_reqs,
            "acceptance_criteria_count": acceptance_criteria_count,
            "req_count_delta": req_count_delta,
            "citation_stale": citation_stale,
        },
    )


def chore_decommission_processed_event(
    file_path: str,
    disposition: str,
    obpi_id: str,
) -> LedgerEvent:
    """Create a chore_decommission_processed event (OBPI-0.0.59-04)."""
    return LedgerEvent(
        event="chore_decommission_processed",
        id=file_path,
        extra={
            "file_path": file_path,
            "disposition": disposition,
            "obpi_id": obpi_id,
        },
    )


def intrinsic_complexity_attestation_event(
    *,
    file_path: str,
    qualname: str,
    reason: str,
    attestor: str,
    attestation_date: str,
    metric: str,
    crossing_band: str,
    crossing_value: float,
) -> LedgerEvent:
    """Create an intrinsic-complexity-attestation event (OBPI-0.0.29-07)."""
    return LedgerEvent(
        event="intrinsic-complexity-attestation",
        id=f"{file_path}::{qualname}",
        extra={
            "file_path": file_path,
            "qualname": qualname,
            "reason": reason,
            "attestor": attestor,
            "attestation_date": attestation_date,
            "metric": metric,
            "crossing_band": crossing_band,
            "crossing_value": crossing_value,
        },
    )


def red_receipt_emitted_event(
    *,
    req_id: str,
    receipt_id: str,
    failure_class: str,
    base_commit: str,
    base_provenance: str = "working-tree",
    obpi_id: str | None = None,
    test_names: list[str] | None = None,
) -> LedgerEvent:
    """Create a RED-witness event for a BEHAVIOR REQ (GHI #642).

    ``failure_class`` is the verdict: ``assertion`` (strong RED), ``error`` (weak
    RED — failed for the wrong reason), or ``none`` (the test passed without its
    implementation and therefore cannot fail).

    ``base_provenance`` says WHICH tree produced it, because that changes what
    ``error`` means (GHI #849). It defaults to ``working-tree``, which is also how a
    reader must treat an event that predates the field: every witness emitted before
    the reconstructed base existed ran against HEAD.
    """
    extra: dict[str, object] = {
        "req_id": req_id,
        "receipt_id": receipt_id,
        "failure_class": failure_class,
        "base_commit": base_commit,
        "base_provenance": base_provenance,
    }
    if obpi_id:
        extra["obpi_id"] = obpi_id
    if test_names:
        extra["test_names"] = list(test_names)
    return LedgerEvent(
        event="red_receipt_emitted",
        id=receipt_id,
        parent=obpi_id,
        extra=extra,
    )


def handoff_resume_authorized_event(
    *,
    session_id: str,
    handoff_path: str,
    operator_text: str,
) -> LedgerEvent:
    """Create a handoff resume authorization event (GHI #574).

    Superseded by :func:`handoff_resume_decided_event` (GHI #757), which records
    a transit DECISION rather than a bare consent boolean. Retained because the
    gate still reads this shape: every authorization booked before that change
    is one of these, and dropping it would retroactively un-authorize the whole
    committed ledger.

    ``operator_text`` carries the operator's VERBATIM words, unmodified: the
    agent seats the operator's words, it never rewrites or summarizes them.
    """
    return LedgerEvent(
        event="handoff_resume_authorized",
        id=handoff_path,
        extra={
            "session_id": session_id,
            "handoff_path": handoff_path,
            "operator_text": operator_text,
        },
    )


def session_exit_bookmark_skipped_event(
    *,
    session_id: str,
    exit_reason: str,
    handoff_path: str,
) -> LedgerEvent:
    """Record that the exit beat fired and deliberately booked nothing.

    Operator ruling 2026-08-05: the bookmark is a safety valve, so when an
    authored handoff already covers the session and provably nothing has happened
    since, a bookmark is noise — *"if we have a proper fresh handoff and a clean
    tree, skip the bookmark."*

    The skip is RECORDED rather than silent because GHI #756's whole class was
    *"a governed verb whose trigger was never specified — the surface passes every
    test that asks 'does it work?' and fails the only question that matters,
    'does it fire?'"*. A silent skip is indistinguishable from a crashed hook, and
    would reintroduce exactly that ambiguity one layer down. This event is the
    difference between "chose not to" and "could not".

    ``handoff_path`` names the authored handoff that made the bookmark redundant,
    so the skip can be audited against the document it deferred to.
    """
    return LedgerEvent(
        event="session_exit_bookmark_skipped",
        id=session_id,
        extra={
            "session_id": session_id,
            "exit_reason": exit_reason,
            "handoff_path": handoff_path,
        },
    )


def surface_weight_recalibrated_event(
    *,
    attestor: str,
    reason: str,
    floor_lines: int,
    previous_floor_lines: int,
    green_ceiling: int,
    yellow_ceiling: int,
) -> LedgerEvent:
    """Witness a surface-weight band/floor recalibration (GHI #791).

    ADR-0.0.33 § Anti-patterns item 3 declares this event mandatory — *"Band
    changes are ledger events, not config tweaks"* — and OBPI-0.0.33-02 REQ 4
    named ``gz adr emit-receipt`` as its producer. That verb's ``--event`` is a
    closed enum of ``{completed, validated, closed}``, so the event had no
    producer at all and the ledger carried zero of them; the 2026-06-30 band
    change (green 1800->2600, yellow 2200->3000) therefore landed as exactly the
    config tweak the anti-pattern forbids, not through negligence but because
    the ceremony was unperformable.

    The band values are carried on the event rather than left implicit in the
    source constants. An event that recorded only *that* a recalibration
    happened would leave "which bands were in force at time T" answerable only
    by reading a commit diff — and the doctrine this witnesses is about the
    thresholds themselves, so the thresholds are the payload.

    ``previous_floor_lines`` makes the accretion delta legible at Layer 2: the
    superseded floor is otherwise overwritten in ``surface_weight_floor.json``
    and recoverable only from git history.
    """
    return LedgerEvent(
        event="surface_weight_recalibrated",
        id=f"surface-weight-{datetime.now(UTC).isoformat()}",
        extra={
            "attestor": attestor,
            "reason": reason,
            "floor_lines": floor_lines,
            "previous_floor_lines": previous_floor_lines,
            "green_ceiling": green_ceiling,
            "yellow_ceiling": yellow_ceiling,
        },
    )


def handoff_resume_decided_event(
    *,
    session_id: str,
    handoff_path: str,
    operator_text: str,
    decision: str,
    set_aside: list[str] | None = None,
) -> LedgerEvent:
    """Create a handoff resume DECISION event (GHI #757).

    The Layer-2 record of an acknowledge-and-decide transit. This is deliberately
    *not* an attestation: ADR-0.0.33 § Alternatives rejects that conflation by
    name — *"completion-attestation is sacrosanct and reserved for claims about
    completed planned work; the airlock's every-transit gate is
    acknowledge-and-decide, a different sort -- conflating them would spend and
    cheapen the sacred word."* The predecessor event's own docstring claimed
    "the same relay model as Gate 5 attestation", which is that conflation
    written down.

    ``decision`` borrows the airlock's ``Decision`` grammar (PROCEED / PAUSE /
    HOLD / REVERT) while keeping the handoff layer's own records — the two
    systems sit on different axes. No value gates anything — the resume gate was
    retired 2026-08-15, so every decision is an advisory record.

    ``operator_text`` remains VERBATIM by operator ruling (2026-08-05): the word
    is still recorded, what changes is that it is filed as a transit decision
    rather than a completion claim.

    ``set_aside`` names advised steps the ruling declines — the clearance
    AMENDMENT record. Previously nothing captured which counsel was set aside or
    why, so a session could depart from the handoff's advice invisibly. The
    operator's frame: *"ATC keeps a record of all clearances issued and all
    amendments."*
    """
    return LedgerEvent(
        event="handoff_resume_decided",
        id=handoff_path,
        extra={
            "session_id": session_id,
            "handoff_path": handoff_path,
            "operator_text": operator_text,
            "decision": decision,
            "set_aside": list(set_aside or []),
        },
    )
