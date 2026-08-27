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

**Credit is Layer-2 evidence, never a marker key (GHI #886).** Until 2026-08-27
both facts this module reports — the dispatch records and the single-driver
declaration — lived only in the pipeline marker under ``.claude/plans/``.
``ADR-0.0.9`` names markers Layer 3 in its own table, and its Rule 5 states the
consequence: *"Layer 3 artifacts cannot block gates. Only L1 (canon) and L2
(events) can be gate evidence."* Measured on ``OBPI-0.35.0-02``: a run that
dispatched 3/3 across two tasks had its credit destroyed by
``gz obpi pipeline --clear-stale`` — the SANCTIONED recovery path — and the gate
then reported 0 of 3, a loss indistinguishable from the dispatch never having
happened. The marker is still written, because ``gz roles`` and the resume
rendering read it; it is a CACHE of what the ledger records, and no verdict here
consults it.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.ledger import Ledger

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


_DISPATCH_EVENT = "stage2_dispatch_recorded"
_DECLARATION_EVENT = "stage2_single_driver_declared"


def _plans_dir(project_root: Path) -> Path:
    """Return the plans directory holding the pipeline marker cache."""
    from gzkit.pipeline_markers import pipeline_plans_dir

    return pipeline_plans_dir(project_root)


def _marker_path(project_root: Path, obpi_id: str) -> Path:
    """Return the active pipeline marker path for ``obpi_id``."""
    return _plans_dir(project_root) / f".pipeline-active-{obpi_id}.json"


def _read_marker(project_root: Path, obpi_id: str) -> dict | None:
    """Return the marker payload, or None when absent/unreadable."""
    try:
        payload = json.loads(_marker_path(project_root, obpi_id).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _ledger(project_root: Path) -> Ledger:
    """Return the project ledger, honouring ``.gzkit.json`` when it is readable.

    Falls back to the canonical relative path rather than raising: a fixture or a
    partially-initialized tree must still be able to READ an empty channel, and a
    config failure is a different defect with its own surface.
    """
    rel = ".gzkit/ledger.jsonl"
    try:
        from gzkit.config import GzkitConfig

        rel = GzkitConfig.load(project_root / ".gzkit.json").paths.ledger
    except (OSError, ValueError):
        pass
    return Ledger(project_root / rel)


def _obpi_events(project_root: Path, obpi_id: str, event_type: str) -> list[dict]:
    """Return this OBPI's payloads for ``event_type``, oldest first.

    The id filter is load-bearing, not defensive: the ledger is project-wide, so
    without it every OBPI would inherit every other OBPI's dispatch records and
    "credit is never inferred" would collapse into "credit is inferred from any
    dispatch anyone ever made". A mutation sweep found this arm untested.

    Scope is the OBPI's WHOLE history, deliberately — not "since the most recent
    ``pipeline_launched``". Narrowing to the current run would reproduce GHI #886
    exactly: the incident's recovery WAS a relaunch, so a launch-scoped window
    would discard the credit recorded before it for the same reason the marker
    did. The disclosed consequence is that an OBPI re-run after a repudiated
    completion inherits its earlier dispatch credit — which is honest, since that
    review did happen, and is the side to err on when the alternative silently
    converts a compliant run into a non-compliant one.
    """
    return [
        event.extra
        for event in _ledger(project_root).read_all()
        if event.event == event_type and event.id == obpi_id
    ]


def _parent_adr(project_root: Path, obpi_id: str) -> str:
    """Return the parent ADR the marker names, or empty when it names none."""
    marker = _read_marker(project_root, obpi_id) or {}
    parent = marker.get("parent_adr")
    return parent if isinstance(parent, str) else ""


def dispatch_channel(project_root: Path, obpi_id: str) -> list[RoleDispatch]:
    """Return the full mandated roster, crediting only ledger-recorded dispatches.

    The marker's ``dispatch_state`` key is deliberately NOT consulted (GHI #886).
    Reading it would put a Layer-3 artifact behind a gate verdict, and it would
    reopen the forgery surface GHI #412 closed for the marker's nonce: any process
    with write access could otherwise buy the verdict by editing a JSON file no
    ceremony produced.
    """
    recorded = {
        str(payload.get("role"))
        for payload in _obpi_events(project_root, obpi_id, _DISPATCH_EVENT)
        if payload.get("role")
    }
    return [
        RoleDispatch(
            role=role,
            disposition=(
                DispatchDisposition.DISPATCHED
                if role in recorded
                else DispatchDisposition.NOT_DISPATCHED
            ),
            source=("dispatch record in ledger" if role in recorded else "no dispatch recorded"),
        )
        for role in MANDATED_STAGE2_ROLES
    ]


def is_single_driver(channel: list[RoleDispatch]) -> bool:
    """Return True unless EVERY mandated role produced receipted input."""
    return any(e.disposition is DispatchDisposition.NOT_DISPATCHED for e in channel)


def record_dispatch(
    project_root: Path,
    obpi_id: str,
    *,
    role: str,
    model: str,
    task_id: int,
) -> None:
    """Record a Stage-2 dispatch on the ledger, and refresh the marker cache.

    The ledger append is the one that matters: it is what
    :func:`dispatch_channel` credits from, and it is what survives the
    ``--clear-stale`` recovery path that destroyed a compliant run's credit on
    ``OBPI-0.35.0-02`` (GHI #886). The marker write is kept because ``gz roles``
    and the resume rendering read it, and it reuses
    :func:`gzkit.pipeline_runtime.persist_dispatch_state` rather than writing the
    key directly, so the record shape stays owned by one module.

    Ledger first, marker second, deliberately: if the marker write fails the
    credit still exists, whereas the reverse order could leave a cache claiming a
    dispatch that no gate would ever credit.
    """
    from gzkit.ledger import stage2_dispatch_recorded_event
    from gzkit.pipeline_runtime import (
        create_subagent_dispatch_record,
        load_dispatch_state,
        persist_dispatch_state,
    )

    _ledger(project_root).append(
        stage2_dispatch_recorded_event(
            obpi_id=obpi_id,
            parent=_parent_adr(project_root, obpi_id),
            role=role,
            model=model,
            task_id=task_id,
        )
    )
    plans_dir = _plans_dir(project_root)
    records = list(load_dispatch_state(plans_dir, obpi_id))
    records.append(create_subagent_dispatch_record(task_id, role, model))
    persist_dispatch_state(plans_dir, obpi_id, records)


def declare_single_driver(project_root: Path, obpi_id: str, *, reason: str) -> None:
    """Record on the ledger that this run is knowingly single-driver, and why.

    A gate with no compliant path for a session that genuinely cannot dispatch
    is un-compliable, and an un-compliable gate gets worked around rather than
    obeyed. Declaring is permitted; running single-driver *silently* is not.

    The declaration is what turns the Stage-5 verdict from BLOCK to PASS, so it
    carries the same durability requirement as the dispatch records themselves
    (GHI #886). Storing it only in the marker would have left the gate
    half-durable: a ``--clear-stale`` would return a knowingly-declared run to
    the silent single-driver state this gate exists to refuse.
    """
    marker_path = _marker_path(project_root, obpi_id)
    marker = _read_marker(project_root, obpi_id)
    if marker is None:
        msg = f"no active pipeline marker for {obpi_id}; cannot declare single-driver"
        raise FileNotFoundError(msg)

    from gzkit.ledger import stage2_single_driver_declared_event

    _ledger(project_root).append(
        stage2_single_driver_declared_event(
            obpi_id=obpi_id,
            parent=_parent_adr(project_root, obpi_id),
            reason=reason,
        )
    )
    marker[_DECLARATION_KEY] = {
        "reason": reason,
        "declared_at": datetime.now(UTC).isoformat(),
    }
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def single_driver_declaration(project_root: Path, obpi_id: str) -> dict | None:
    """Return the ledger-recorded single-driver declaration, or None.

    Last declaration wins. Re-declaring is an ordinary forward correction over an
    append-only store (``AGENTS.md`` Never #2) — a session whose reason changed
    states the new one rather than editing the old.
    """
    declarations = _obpi_events(project_root, obpi_id, _DECLARATION_EVENT)
    return dict(declarations[-1]) if declarations else None


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
