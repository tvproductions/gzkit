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

    Summary record for one ``gz brief reconcile`` run. ``applied`` / ``attestor``
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
    obpi_id: str | None = None,
    test_names: list[str] | None = None,
) -> LedgerEvent:
    """Create a RED-witness event for a BEHAVIOR REQ (GHI #642).

    ``failure_class`` is the verdict: ``assertion`` (strong RED), ``error`` (weak
    RED — failed for the wrong reason), or ``none`` (the test passed without its
    implementation and therefore cannot fail).
    """
    extra: dict[str, object] = {
        "req_id": req_id,
        "receipt_id": receipt_id,
        "failure_class": failure_class,
        "base_commit": base_commit,
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

    The Layer-2 record that discharges the Operator Authorization Gate. Booking
    it is what lifts ``gzkit.handoff_resume_gate``'s block for this session.

    ``operator_text`` carries the operator's VERBATIM words, unmodified — the
    same relay model as Gate 5 attestation (AGENTS.md § Attestation): the agent
    seats the operator's words, it never rewrites or summarizes them.
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
