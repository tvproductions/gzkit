"""Governance-layer event emission helpers (ADR-0.0.37, OBPI-0.0.37-03)."""

from __future__ import annotations

from pathlib import Path

from gzkit.governance.brief_reconcile import ReconcileResult
from gzkit.ledger import Ledger
from gzkit.ledger_events import (
    brief_reconcile_drift_detected_event,
    brief_reconciled_event,
    composition_drift_detected_event,
    composition_rendered_event,
    rendition_committed_event,
)


def emit_composition_rendered(
    root: Path,
    invariant_count: int,
    target: str,
    byte_count: int,
) -> None:
    """Append a composition_rendered event to the project ledger."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        composition_rendered_event(
            invariant_count=invariant_count,
            target=target,
            byte_count=byte_count,
        )
    )


def emit_composition_drift_detected(
    root: Path,
    target: str,
    diff_first_50_lines: str,
) -> None:
    """Append a composition_drift_detected event to the project ledger."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        composition_drift_detected_event(
            target=target,
            diff_first_50_lines=diff_first_50_lines,
        )
    )


def emit_rendition_committed(
    root: Path,
    surface: str,
    consumer: str,
    corpus_fingerprint: str,
    attestor: str,
) -> None:
    """Append a rendition_committed event to the project ledger."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        rendition_committed_event(
            surface=surface,
            consumer=consumer,
            corpus_fingerprint=corpus_fingerprint,
            attestor=attestor,
        )
    )


def emit_brief_reconciled(
    root: Path,
    result: ReconcileResult,
    *,
    applied: bool = False,
    attestor: str | None = None,
) -> None:
    """Append a brief_reconciled summary event to the project ledger (OBPI-06)."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        brief_reconciled_event(
            brief_id=result.brief_id,
            has_drift=result.has_drift,
            allowlist_delta_count=(
                len(result.allowlist_delta.missing_in_brief)
                + len(result.allowlist_delta.missing_on_disk)
            ),
            discovery_delta_count=len(result.discovery_delta.unresolved_paths),
            verification_delta_count=len(result.verification_delta.unresolved_verbs),
            req_count_delta=result.req_count_delta.delta,
            citation_delta_count=len(result.citation_delta.stale_citations),
            applied=applied,
            attestor=attestor,
        )
    )


def emit_brief_reconcile_drift_detected(root: Path, result: ReconcileResult) -> None:
    """Append a brief_reconcile_drift_detected event with the full delta payload (OBPI-06)."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        brief_reconcile_drift_detected_event(
            brief_id=result.brief_id,
            allowlist_missing_in_brief=list(result.allowlist_delta.missing_in_brief),
            allowlist_missing_on_disk=list(result.allowlist_delta.missing_on_disk),
            discovery_unresolved_paths=list(result.discovery_delta.unresolved_paths),
            verification_unresolved_verbs=list(result.verification_delta.unresolved_verbs),
            declared_reqs=result.req_count_delta.declared_reqs,
            acceptance_criteria_count=result.req_count_delta.acceptance_criteria_count,
            req_count_delta=result.req_count_delta.delta,
            citation_stale=[
                f"{path} :: {anchor}" for path, anchor in result.citation_delta.stale_citations
            ],
        )
    )
