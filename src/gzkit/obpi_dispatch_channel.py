"""Stage-2 dispatch channel for the OBPI pipeline (GHI #845).

The OBPI pipeline mandates that Stage 2 dispatch an ``implementer`` and then a
two-stage ``spec-reviewer`` + ``quality-reviewer`` review. Until 2026-08-21
nothing recorded whether that happened: a completion receipt produced by a
properly dispatched run and one produced by an orchestrator editing inline were
byte-indistinguishable in every artifact the system emitted.

The machinery to record it was already complete and already correct —
:func:`gzkit.pipeline_runtime.persist_dispatch_state` writes
``marker["dispatch_state"]``, :func:`~gzkit.pipeline_runtime.load_dispatch_state`
reads it back, and three test modules exercise the round trip. Measured
2026-08-21, **no production code path called any of it**; the only production
consumer was ``gz roles``, a display command rendering a list that was always
empty. The absent half was the *call*, not the code.

Two properties are load-bearing here, both inherited from the ``gz-adr-evaluate``
channel that closed the same gap for that ceremony (GHI #770):

**Credit is never inferred.** A role is DISPATCHED only when a record says so.
Inferring it from the presence of code, tests, or a completed stage would
re-create the exact indistinguishability this module exists to end.

**The roster is emitted even when empty.** Silence is the defect. An empty table
would make an undispatched Stage 2 look like a ceremony that has no dispatch
mandate at all.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

#: The Stage-2 roster the pipeline skill mandates. Partial dispatch is still
#: SINGLE-DRIVER: the reviewers exist to catch what the implementer cannot see
#: in its own work, so crediting the implementer alone would launder them.
MANDATED_STAGE2_ROLES: tuple[str, ...] = ("Implementer", "SpecReviewer", "QualityReviewer")

_DECLARATION_KEY = "single_driver_declaration"


class DispatchDisposition(StrEnum):
    """Whether a mandated role produced receipted independent input."""

    DISPATCHED = "DISPATCHED"
    NOT_DISPATCHED = "NOT DISPATCHED"


class RoleDispatch(BaseModel):
    """One row of the dispatch channel."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    role: str = Field(..., description="Mandated Stage-2 role")
    disposition: DispatchDisposition = Field(..., description="Credited only from a record")
    source: str = Field(..., description="What the disposition was derived from")


def _marker_path(plans_dir: Path, obpi_id: str) -> Path:
    """Return the active pipeline marker path for ``obpi_id``."""
    return plans_dir / f".pipeline-active-{obpi_id}.json"


def _read_marker(plans_dir: Path, obpi_id: str) -> dict | None:
    """Return the marker payload, or None when absent/unreadable."""
    try:
        payload = json.loads(_marker_path(plans_dir, obpi_id).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def dispatch_channel(plans_dir: Path, obpi_id: str) -> list[RoleDispatch]:
    """Return the full mandated roster, crediting only recorded dispatches."""
    marker = _read_marker(plans_dir, obpi_id) or {}
    raw = marker.get("dispatch_state")
    recorded = {
        str(r.get("role"))
        for r in (raw if isinstance(raw, list) else [])
        if isinstance(r, dict) and r.get("role")
    }
    return [
        RoleDispatch(
            role=role,
            disposition=(
                DispatchDisposition.DISPATCHED
                if role in recorded
                else DispatchDisposition.NOT_DISPATCHED
            ),
            source=("dispatch record in marker" if role in recorded else "no dispatch recorded"),
        )
        for role in MANDATED_STAGE2_ROLES
    ]


def is_single_driver(channel: list[RoleDispatch]) -> bool:
    """Return True unless EVERY mandated role produced receipted input."""
    return any(e.disposition is DispatchDisposition.NOT_DISPATCHED for e in channel)


def record_dispatch(
    plans_dir: Path,
    obpi_id: str,
    *,
    role: str,
    model: str,
    task_id: int,
) -> None:
    """Append a dispatch record to the active marker.

    This is the call the machinery never had. It reuses
    :func:`gzkit.pipeline_runtime.persist_dispatch_state` rather than writing the
    marker key directly, so the record shape stays owned by one module.
    """
    from gzkit.pipeline_runtime import (
        create_subagent_dispatch_record,
        load_dispatch_state,
        persist_dispatch_state,
    )

    records = list(load_dispatch_state(plans_dir, obpi_id))
    records.append(create_subagent_dispatch_record(task_id, role, model))
    persist_dispatch_state(plans_dir, obpi_id, records)


def declare_single_driver(plans_dir: Path, obpi_id: str, *, reason: str) -> None:
    """Record that this run is knowingly single-driver, and why.

    A gate with no compliant path for a session that genuinely cannot dispatch
    is un-compliable, and an un-compliable gate gets worked around rather than
    obeyed. Declaring is permitted; running single-driver *silently* is not.
    """
    marker_path = _marker_path(plans_dir, obpi_id)
    marker = _read_marker(plans_dir, obpi_id)
    if marker is None:
        msg = f"no active pipeline marker for {obpi_id}; cannot declare single-driver"
        raise FileNotFoundError(msg)
    marker[_DECLARATION_KEY] = {
        "reason": reason,
        "declared_at": datetime.now(UTC).isoformat(),
    }
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def single_driver_declaration(plans_dir: Path, obpi_id: str) -> dict | None:
    """Return the recorded single-driver declaration, or None."""
    marker = _read_marker(plans_dir, obpi_id) or {}
    declaration = marker.get(_DECLARATION_KEY)
    return declaration if isinstance(declaration, dict) else None


def render_dispatch_channel(
    channel: list[RoleDispatch],
    *,
    declaration: dict | None = None,
) -> str:
    """Render the channel as operator-facing markdown, verdict included."""
    rows = "\n".join(f"| {e.role} | {e.disposition.value} | {e.source} |" for e in channel)
    header = (
        "--- Stage-2 Persona Dispatch (mandated by the ceremony; never inferred) ---\n\n"
        "| Role | Independent input | Source |\n"
        "|------|-------------------|--------|\n"
        f"{rows}\n\n"
    )
    if not is_single_driver(channel):
        dispatched = len(channel)
        return header + (
            f"DISPATCH MODE: DISPATCHED — {dispatched} of {dispatched} mandated roles "
            "produced receipted independent input."
        )
    credited = sum(1 for e in channel if e.disposition is DispatchDisposition.DISPATCHED)
    verdict = (
        f"DISPATCH MODE: SINGLE-DRIVER — {credited} of {len(channel)} mandated roles "
        "produced receipted independent input.\nThis OBPI did NOT receive the "
        "two-stage independent review."
    )
    if declaration:
        return header + (
            "DISPATCH MODE: SINGLE-DRIVER DECLARED — knowingly run without the "
            f"mandated dispatch.\nReason: {declaration.get('reason', '(none given)')}\n"
            f"Declared at: {declaration.get('declared_at', '(unknown)')}\n"
            f"{credited} of {len(channel)} mandated roles produced receipted input."
        )
    return header + verdict
