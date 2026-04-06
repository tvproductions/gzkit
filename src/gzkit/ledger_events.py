"""Event factory functions for the governance ledger.

Each function constructs a typed ``LedgerEvent`` with the correct event name
and extra payload.  Keeping them in a dedicated module keeps ``ledger.py``
under the 600-line module limit while preserving the same public API via
re-exports.
"""

from typing import Any

from gzkit.ledger import LedgerEvent

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
