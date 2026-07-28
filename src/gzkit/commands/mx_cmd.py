"""gz mx command group — Maintenance Hangar (MX) mode operations.

ADR-0.0.74 Decision item #4: gz mx enter. The operator opens the door
(reason + attestor); the tool sets the marker, writes mx_session_opened,
and captures the inspection scope. The agent never opens the hangar on its own.

ADR-0.0.74 Decision item #5: gz mx exit. The hard gate: re-run every guard
at full strength (re-emit levels) against the full inspection scope captured
at enter — green-or-grounded, hard refuse on any red (no --force; you cannot
narrow your way out).
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from gzkit import lock_manager

# The mx door CONSUMES the SHARED airlock primitive extracted by OBPI-02/03 — it
# imports the functions DIRECTLY from the enter/exit submodules and CALLS them,
# never forking a private variant (ADR-0.33.0 § Decision; BI-3; Negative #3).
from gzkit.airlock.enter import airlock_enter, build_refusal
from gzkit.airlock.exit import airlock_exit
from gzkit.airlock.model import Decision
from gzkit.commands.common import console, get_project_root
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.lock_manager import LockData
from gzkit.mx import log, marker
from gzkit.mx.marker import Marker

# Lock identity on the token rail — singleton key for the MX session.
_MX_LOCK_KEY = "mx-session"

# Session-lock TTL tracks the canonical OBPI lock TTL via the shared constant (the
# marker is the real session truth, not the lock; the lock serializes concurrent
# entry only). Sharing the constant keeps the two from drifting apart (GHI #604).
_DEFAULT_TTL_MINUTES = lock_manager.DEFAULT_LOCK_TTL_MINUTES

# Ledger path relative to project root (parallel to marker.py's _LEDGER_RELPATH).
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")

# ADR/OBPI artifact tree, relative to project root — the mx airlock reads a
# DECLARED artifact for its seam-map bodies (§ Allowed Paths). Brief-less DECLARE
# (no resolvable scope) is the attested deferred calibration frontier (ADR-0.33.0).
_ADR_RELPATH = ("docs", "design", "adr")


def _resolve_mx_airlock_brief(
    inspection_scope: list[str], project_root: Path
) -> tuple[str, Path] | None:
    """Resolve the first inspection-scope id naming an on-disk ADR/OBPI artifact.

    The mx session has no OBPI brief of its own; the airlock reads its seam-map
    bodies from a DECLARED artifact. When a ``--scope`` id names a brief-bearing
    artifact on disk, that artifact is the airlock's DECLARE input (mirroring the
    pipeline door, which hands the primitive the real OBPI brief). When no scope
    resolves — the brief-less DECLARE case — this returns ``None`` and the mx
    airlock diagnostic is skipped: brief-less DECLARE is the attested deferred
    calibration frontier (parent ADR § Consequences), not this increment.
    """
    adr_root = project_root.joinpath(*_ADR_RELPATH)
    if not adr_root.is_dir():
        return None
    for scope in inspection_scope:
        token = scope.strip()
        if not token:
            continue
        matches = sorted(adr_root.glob(f"**/{token}*.md"))
        if matches:
            return token, matches[0]
    return None


def _run_mx_airlock_in_diagnostic(
    inspection_scope: list[str],
    project_root: Path,
    *,
    reach_fn: Callable[[str], list[str] | None] | None = None,
) -> None:
    """Reach airlock-IN at the mx-enter seam (ADR-0.33.0, DIAGNOSTIC-ONLY).

    Mirrors the pipeline door's Stage-1 diagnostic but CALLS the SHARED primitive
    (``gzkit.airlock.enter.airlock_enter``) directly — ``pipeline_runtime`` is out
    of scope for the mx door. Books the ``airlock_in`` L2 encounter; a NO-GO is
    surfaced as a diagnostic refusal rather than a block — a STAGED posture per
    parent ADR § Calibration frontier, not the declared end state (§ BI-4 blocks
    on an un-accounted seam). § Negative #5 governs refusal legibility, not
    whether a refusal blocks.
    Real-entry reach is the deferred calibration frontier, so production passes an
    empty reach (the wiring is proven, the meaningful seam-map deferred); tests
    inject a reach to exercise the NO-GO path.
    """
    resolved = _resolve_mx_airlock_brief(inspection_scope, project_root)
    if resolved is None:
        console.print(
            "[yellow]airlock-IN (diagnostic):[/yellow] deferred — no brief-bearing "
            "scope to account (brief-less DECLARE frontier)."
        )
        return
    target, brief_path = resolved
    reach = reach_fn if reach_fn is not None else (lambda _node: [])
    ledger = Ledger(project_root.joinpath(*_LEDGER_RELPATH))
    preflight = airlock_enter(target, brief_path, reach_fn=reach, ledger=ledger)
    if preflight.decision is not Decision.PROCEED:
        console.print(
            f"[yellow]airlock-IN (diagnostic):[/yellow] {build_refusal(preflight.seam_map, target)}"
        )


def _run_mx_airlock_out_diagnostic(
    inspection_scope: list[str],
    project_root: Path,
    *,
    reach_fn: Callable[[str], list[str] | None] | None = None,
) -> None:
    """Reach airlock-OUT at the mx-exit seam (ADR-0.33.0, DIAGNOSTIC-ONLY, co-equal).

    ADDITIVE to ``mx exit``'s hard guard-gate (never a replacement): the caller
    fires this only after the guards pass, before ``mx_session_closed``. Books the
    ``airlock_out`` L2 encounter and surfaces drift findings as warnings; never
    blocks the close. Real-entry reach is the deferred frontier (empty in production).
    """
    resolved = _resolve_mx_airlock_brief(inspection_scope, project_root)
    if resolved is None:
        console.print(
            "[yellow]airlock-OUT (diagnostic):[/yellow] deferred — no brief-bearing "
            "scope to account (brief-less DECLARE frontier)."
        )
        return
    target, brief_path = resolved
    reach = reach_fn if reach_fn is not None else (lambda _node: [])
    ledger = Ledger(project_root.joinpath(*_LEDGER_RELPATH))
    report = airlock_exit(target, brief_path, reach_fn=reach, ledger=ledger)
    for finding in report.findings:
        console.print(
            f"[yellow]airlock-OUT (diagnostic):[/yellow] {finding.kind.value}: "
            f"{finding.edge.target} -> {finding.recommendation}"
        )


def _mx_session_opened_event(
    session_id: str,
    reason: str,
    attestor: str,
    inspection_scope: list[str],
) -> LedgerEvent:
    """Build the mx_session_opened ledger event (the enter anchor).

    Typed by :class:`gzkit.events.MxSessionOpenedEvent` at parse time.
    """
    return LedgerEvent(
        event="mx_session_opened",
        id=session_id,
        extra={
            "session_id": session_id,
            "reason": reason,
            "attestor": attestor,
            "inspection_scope": list(inspection_scope),
        },
    )


def mx_enter_cmd(
    reason: str,
    attestor: str,
    inspection_scope: list[str],
    project_root: Path | None = None,
    *,
    _airlock_reach: Callable[[str], list[str] | None] | None = None,
) -> None:
    """Open the MX maintenance hangar.

    Sets the marker file, writes one ``mx_session_opened`` ledger event, and
    captures the inspection scope.  The operator (``attestor``) is required;
    an agent cannot open the hangar autonomously.  Empty or whitespace-only
    ``reason`` or ``attestor`` fails closed with exit 1.
    """
    if not reason.strip():
        console.print("[red]ERROR:[/red] --reason cannot be empty.")
        sys.exit(1)
    if not attestor.strip():
        console.print(
            "[red]ERROR:[/red] --attestor cannot be empty. "
            "MX cannot be opened autonomously — an operator attestor is required."
        )
        sys.exit(1)

    root = project_root if project_root is not None else get_project_root()

    if marker.is_active(root):
        console.print("[red]ERROR:[/red] MX mode is already active.")
        sys.exit(1)

    # Acquire the session on the lock_manager token rail to serialize concurrent entry.
    session_id = lock_manager.resolve_session_id()
    lock = LockData(
        obpi_id=_MX_LOCK_KEY,
        agent=lock_manager.resolve_agent(),
        pid=os.getpid(),
        session_id=session_id,
        claimed_at=datetime.now(UTC).isoformat(),
        branch=lock_manager.current_branch(),
        ttl_minutes=_DEFAULT_TTL_MINUTES,
    )
    try:
        lock_manager.write_lock(root, lock)
    except FileExistsError:
        console.print(
            "[red]ERROR:[/red] Concurrent MX entry detected — another session is opening."
        )
        sys.exit(1)

    # airlock-IN fires BEFORE the hangar marker write (ADR-0.33.0; BI-2): the gate
    # crosses on EVERY entry regardless of --reason. DIAGNOSTIC-ONLY — a NO-GO logs
    # a refusal, it never blocks the marker (real-entry accounting is deferred).
    _run_mx_airlock_in_diagnostic(inspection_scope, root, reach_fn=_airlock_reach)

    # Write the marker (sets MX==TRUE).
    now = datetime.now(UTC).isoformat()
    m = Marker(
        session_id=session_id,
        opened_at=now,
        reason=reason.strip(),
        attestor=attestor.strip(),
        inspection_scope=list(inspection_scope),
    )
    marker.write(m, root)

    # Write the mx_session_opened ledger event (binds the marker anti-contrivance).
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    ledger.append(
        _mx_session_opened_event(session_id, reason.strip(), attestor.strip(), inspection_scope)
    )

    console.print(
        f"[green]MX session opened.[/green] session_id={session_id}, attestor={attestor.strip()}"
    )


def _mx_session_closed_event(session_id: str, attestor: str) -> LedgerEvent:
    """Build the mx_session_closed ledger event (the exit anchor).

    Typed by :class:`gzkit.events.MxSessionClosedEvent` at parse time.
    """
    return LedgerEvent(
        event="mx_session_closed",
        id=session_id,
        extra={
            "session_id": session_id,
            "attestor": attestor,
        },
    )


def _default_run_guards(project_root: Path) -> int:
    """Run gz check at full strength (marker is absent — advisory demotion bypassed)."""
    result = subprocess.run(["uv", "run", "gz", "check"], cwd=project_root)
    return result.returncode


def mx_exit_cmd(
    attestor: str,
    project_root: Path | None = None,
    _run_guards: Callable[[Path], int] | None = None,
    *,
    _airlock_reach: Callable[[str], list[str] | None] | None = None,
) -> None:
    """Hard gate: re-run every guard at full strength; write mx_session_closed on all-green.

    Temporarily removes the marker before running guards so checkpoint.resolve()
    sees no active session and emits at real severity — no advisory demotion.
    Restores the marker and exits 3 if any guard is red.  On all-green, writes
    the mx_session_closed ledger event (marker stays removed).
    """
    if not attestor.strip():
        console.print("[red]ERROR:[/red] --attestor cannot be empty.")
        sys.exit(1)

    root = project_root if project_root is not None else get_project_root()

    if not marker.is_active(root):
        console.print("[red]ERROR:[/red] No active MX session. Use 'gz mx enter' first.")
        sys.exit(1)

    m = marker.read(root)
    if m is None:
        console.print("[red]ERROR:[/red] Marker file unreadable.")
        sys.exit(1)

    runner = _run_guards if _run_guards is not None else _default_run_guards

    # Temporarily remove the marker so checkpoint.resolve() sees no active session
    # (guards emit at their real severity — no advisory demotion).
    marker_file = marker.marker_path(root)
    saved = marker_file.read_text(encoding="utf-8")
    marker_file.unlink()

    try:
        exit_code = runner(root)
    except OSError:
        marker_file.write_text(saved, encoding="utf-8")
        raise

    if exit_code != 0:
        # Guards red — restore marker, hard refuse.
        marker_file.write_text(saved, encoding="utf-8")
        console.print("[red]Guards reported failures. MX session remains open.[/red]")
        sys.exit(3)

    # All-green — assemble the complete-by-construction MX log and render it for
    # operator review BEFORE the close signature is taken (REQ-06-03). The log is
    # derived from the ledger events + commits in the enter→exit window, so it
    # cannot be hand-narrated or forgotten.
    console.print(log.assemble_and_render(root, m.session_id))

    # airlock-OUT fires (co-equal exit membrane, ADR-0.33.0) — ADDITIVE to the hard
    # guard-gate above, never a replacement: it runs only after the guards pass,
    # before the close signature. DIAGNOSTIC-ONLY (real-entry accounting deferred).
    _run_mx_airlock_out_diagnostic(m.inspection_scope, root, reach_fn=_airlock_reach)

    # Signature: write mx_session_closed, marker stays removed.
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    ledger.append(_mx_session_closed_event(m.session_id, attestor.strip()))

    console.print(
        f"[green]MX session closed.[/green] session_id={m.session_id}, attestor={attestor.strip()}"
    )
