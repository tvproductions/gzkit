"""OBPI lock management CLI commands.

Thin orchestration layer over ``lock_manager`` I/O functions and ledger
event emission.  Each command validates inputs, calls the data layer,
appends a ledger event, and formats output.
"""

from __future__ import annotations

import json
import sys

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.handoff_validation import (
    ABANDON_CATEGORIES,
    AbandonSpec,
    InvalidAbandonSpec,
    find_handoff_for_release,
    parse_abandon_spec,
    write_degenerate_handoff,
)
from gzkit.ledger import Ledger
from gzkit.ledger_events import obpi_lock_claimed_event, obpi_lock_released_event
from gzkit.lock_manager import (
    LockData,
    current_branch,
    delete_lock,
    list_locks,
    read_lock,
    reap_expired_locks,
    resolve_agent,
    resolve_session_id,
    write_lock,
)


def obpi_lock_claim_cmd(
    obpi_id: str,
    ttl_minutes: int,
    as_json: bool,
    agent: str | None = None,
) -> None:
    """Claim an OBPI work lock with ledger accounting."""
    config = ensure_initialized()
    project_root = get_project_root()

    resolved_agent = resolve_agent(agent)
    existing = read_lock(project_root, obpi_id)

    if existing is not None and not existing.is_expired and existing.agent != resolved_agent:
        if as_json:
            print(json.dumps({"status": "conflict", "holder": existing.model_dump()}))
        else:
            console.print(
                f"[red]CONFLICT:[/red] {obpi_id} locked by {existing.agent} "
                f"at {existing.claimed_at} (TTL {existing.ttl_minutes}m, "
                f"{existing.elapsed_minutes:.0f}m elapsed)"
            )
        sys.exit(1)

    # Same-agent re-claim or expired lock: delete first to make room for the
    # exclusive-creation write below.
    if existing is not None:
        delete_lock(project_root, obpi_id)

    import os  # noqa: PLC0415

    lock_data = LockData(
        obpi_id=obpi_id,
        agent=resolved_agent,
        pid=os.getpid(),
        session_id=resolve_session_id(),
        claimed_at=_now_iso(),
        branch=current_branch(),
        ttl_minutes=ttl_minutes,
    )
    try:
        write_lock(project_root, lock_data)
    except FileExistsError:
        # Race winner already wrote the lock between our read_lock check and
        # write_lock attempt. Re-read so we report the actual holder, not the
        # ghost from our earlier read.
        actual_holder = read_lock(project_root, obpi_id)
        holder_payload = (
            actual_holder.model_dump(exclude={"is_expired", "elapsed_minutes"})
            if actual_holder is not None
            else {"obpi_id": obpi_id}
        )
        if as_json:
            print(json.dumps({"status": "conflict", "holder": holder_payload, "race": True}))
        else:
            agent_name = actual_holder.agent if actual_holder is not None else "another agent"
            console.print(
                f"[red]CONFLICT:[/red] {obpi_id} race-locked by {agent_name} "
                "(exclusive-creation enforced; second writer rejected)"
            )
        sys.exit(1)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(
        obpi_lock_claimed_event(
            obpi_id=obpi_id,
            agent=resolved_agent,
            ttl_minutes=ttl_minutes,
            branch=lock_data.branch,
            session_id=lock_data.session_id,
        )
    )

    if as_json:
        print(
            json.dumps(
                {
                    "status": "claimed",
                    "lock": lock_data.model_dump(exclude={"is_expired", "elapsed_minutes"}),
                }
            )
        )
    else:
        console.print(
            f"[green]Claimed:[/green] {obpi_id} (agent={resolved_agent}, ttl={ttl_minutes}m)"
        )


def obpi_lock_release_cmd(
    obpi_id: str,
    as_json: bool,
    force: bool = False,
    agent: str | None = None,
    abandon: str | None = None,
) -> None:
    """Release an OBPI work lock with ownership validation.

    The ``abandon`` parameter accepts ``<category>:<reason>`` per token-block
    discipline (``.gzkit/rules/token-block-discipline.md`` § Sub-Invariant 1).
    When provided, a degenerate handoff is written under ``.gzkit/handoffs/``
    and the released event carries ``handoff_path``.

    In the OBPI-02 staging window, releasing without ``--abandon`` AND without a
    matching handoff EMITS A WARNING but still succeeds (exit 0). OBPI-03 flips
    this to fail-closed.
    """
    config = ensure_initialized()
    project_root = get_project_root()

    # Validate abandon spec early so we fail before deleting the lock.
    abandon_spec: AbandonSpec | None = None
    if abandon is not None:
        try:
            abandon_spec = parse_abandon_spec(abandon)
        except InvalidAbandonSpec as e:
            allowed = " | ".join(ABANDON_CATEGORIES)
            msg = f"INVALID --abandon: {e}\n  closed category enum: {allowed}"
            if as_json:
                print(json.dumps({"status": "invalid_abandon", "error": str(e)}))
            else:
                console.print(f"[red]{msg}[/red]")
            sys.exit(1)

    existing = read_lock(project_root, obpi_id)
    if existing is None:
        if as_json:
            print(json.dumps({"status": "not_found", "obpi_id": obpi_id}))
        else:
            console.print(f"[yellow]No lock found:[/yellow] {obpi_id}")
        return

    resolved_agent = resolve_agent(agent)
    if not force and existing.agent != resolved_agent:
        if as_json:
            print(
                json.dumps(
                    {
                        "status": "ownership_error",
                        "obpi_id": obpi_id,
                        "holder": existing.agent,
                        "requester": resolved_agent,
                    }
                )
            )
        else:
            console.print(
                f"[red]OWNERSHIP ERROR:[/red] {obpi_id} is held by {existing.agent}, "
                f"not {resolved_agent}. Use --force to override."
            )
        sys.exit(1)

    # Resolve handoff_path: either by writing a degenerate handoff (abandon
    # path) or by searching for an existing register entry that postdates the
    # lock claim (normal-release path). In OBPI-02 the absence is warning-only.
    handoff_path_str: str | None = None
    missing_handoff_warning: str | None = None
    if abandon_spec is not None:
        adr_id = _adr_id_from_obpi(obpi_id)
        handoff_path = write_degenerate_handoff(
            project_root,
            obpi_id=obpi_id,
            adr_id=adr_id,
            agent=resolved_agent,
            spec=abandon_spec,
            last_claim_timestamp=existing.claimed_at,
            commit_sha=_current_commit_sha(),
            branch=existing.branch,
        )
        handoff_path_str = handoff_path.relative_to(project_root).as_posix()
    else:
        handoff_match = find_handoff_for_release(
            project_root,
            obpi_id=obpi_id,
            after_timestamp=existing.claimed_at,
        )
        if handoff_match is None:
            # OBPI-02 staging window: warning-only, exit 0.
            missing_handoff_warning = (
                f"WARNING: releasing {obpi_id} without a register entry and "
                "without --abandon. The token-block doctrine requires a "
                "register entry on every surrender (see `gz-session-handoff` "
                "skill). OBPI-0.0.41-03 will flip this path to fail-closed."
            )
            print(missing_handoff_warning, file=sys.stderr)
        else:
            handoff_path_str = handoff_match.relative_to(project_root).as_posix()

    delete_lock(project_root, obpi_id)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(
        obpi_lock_released_event(
            obpi_id=obpi_id,
            agent=resolved_agent,
            force=force,
            handoff_path=handoff_path_str,
        )
    )

    if as_json:
        payload: dict[str, object] = {"status": "released", "obpi_id": obpi_id}
        if handoff_path_str is not None:
            payload["handoff_path"] = handoff_path_str
        if abandon_spec is not None:
            payload["abandoned"] = True
            payload["category"] = abandon_spec.category
            payload["reason"] = abandon_spec.reason
        print(json.dumps(payload))
    else:
        console.print(f"[green]Released:[/green] {obpi_id}")


def obpi_lock_check_cmd(obpi_id: str, as_json: bool) -> None:
    """Check if an OBPI is locked.  Exit 0 if held, exit 1 if free."""
    ensure_initialized()
    project_root = get_project_root()

    existing = read_lock(project_root, obpi_id)

    if existing is not None and not existing.is_expired:
        if as_json:
            print(
                json.dumps(
                    {
                        "status": "held",
                        "lock": existing.model_dump(exclude={"is_expired", "elapsed_minutes"}),
                        "elapsed_minutes": round(existing.elapsed_minutes, 1),
                        "remaining_minutes": round(
                            max(0, existing.ttl_minutes - existing.elapsed_minutes), 1
                        ),
                    }
                )
            )
        else:
            remaining = max(0, existing.ttl_minutes - existing.elapsed_minutes)
            console.print(
                f"[green]HELD:[/green] {obpi_id}  agent={existing.agent}  "
                f"elapsed={existing.elapsed_minutes:.0f}m  remaining={remaining:.0f}m"
            )
        return  # exit 0

    if as_json:
        print(json.dumps({"status": "free", "obpi_id": obpi_id}))
    else:
        console.print(f"[dim]FREE:[/dim] {obpi_id}")
    sys.exit(1)


def obpi_lock_list_cmd(adr_id: str | None, as_json: bool) -> None:
    """List active OBPI locks after reaping expired ones."""
    ensure_initialized()
    project_root = get_project_root()

    reaped = reap_expired_locks(project_root)
    locks = list_locks(project_root, adr_filter=adr_id)
    # After reaping, only non-expired locks remain in the directory.
    # Filter out any that are still expired (race or TTL boundary).
    active = [lk for lk in locks if not lk.is_expired]

    if as_json:
        print(
            json.dumps(
                {
                    "locks": [
                        lk.model_dump(exclude={"is_expired", "elapsed_minutes"}) for lk in active
                    ],
                    "reaped": [
                        lk.model_dump(exclude={"is_expired", "elapsed_minutes"}) for lk in reaped
                    ],
                    "count": len(active),
                }
            )
        )
    else:
        if reaped:
            for rp in reaped:
                console.print(f"  [dim]Reaped expired:[/dim] {rp.obpi_id} (agent={rp.agent})")
        if not active:
            console.print("[dim]No active locks.[/dim]")
            return
        for lk in active:
            console.print(
                f"  {lk.obpi_id}  [green]ACTIVE[/green]  agent={lk.agent}  "
                f"elapsed={lk.elapsed_minutes:.0f}m  ttl={lk.ttl_minutes}m"
            )


# Keep lock_dir accessible for tests that need to set up lock directories.
__all__ = [
    "obpi_lock_claim_cmd",
    "obpi_lock_release_cmd",
    "obpi_lock_check_cmd",
    "obpi_lock_list_cmd",
]


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    from datetime import UTC, datetime  # noqa: PLC0415

    return datetime.now(UTC).isoformat()


def _adr_id_from_obpi(obpi_id: str) -> str:
    """Derive `ADR-X.Y.Z` from an `OBPI-X.Y.Z-NN[-slug]` identifier.

    Used by the degenerate-handoff writer so the handoff frontmatter carries the
    parent ADR ID without the caller needing to thread it through.
    """
    if not obpi_id.startswith("OBPI-"):
        return "ADR-unknown"
    parts = obpi_id[5:].split("-")
    if len(parts) < 1:
        return "ADR-unknown"
    return f"ADR-{parts[0]}"


def _current_commit_sha() -> str:
    """Return the current HEAD commit SHA, or 'unknown' on failure."""
    import subprocess  # noqa: PLC0415

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"
