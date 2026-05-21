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
    from gzkit.events import EventAnchor

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


def obpi_withdrawn_event(obpi_id: str, parent: str, reason: str) -> LedgerEvent:
    """Create an OBPI withdrawn event."""
    return LedgerEvent(
        event="obpi_withdrawn",
        id=obpi_id,
        parent=parent,
        extra={"reason": reason},
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
) -> LedgerEvent:
    """Create an OBPI lock released event."""
    return LedgerEvent(
        event="obpi_lock_released",
        id=obpi_id,
        extra={"agent": agent, "force": force},
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
