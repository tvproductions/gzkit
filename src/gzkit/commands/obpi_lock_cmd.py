"""OBPI lock management CLI commands."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console


def _lock_dir(project_root: Path) -> Path:
    """Return the OBPI lock directory, creating if needed."""
    d = project_root / ".gzkit" / "locks" / "obpi"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _lock_path(project_root: Path, obpi_id: str) -> Path:
    """Return the lock file path for a given OBPI."""
    return _lock_dir(project_root) / f"{obpi_id}.lock.json"


def _resolve_agent() -> str:
    """Resolve agent identity from environment."""
    if os.environ.get("CLAUDE_CODE"):
        return "claude-code"
    if os.environ.get("CODEX_SANDBOX"):
        return "codex"
    return f"unknown-{os.getpid()}"


def _current_branch() -> str:
    """Return current git branch or 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def obpi_lock_claim_cmd(obpi_id: str, ttl_minutes: int, as_json: bool) -> None:
    """Claim an OBPI work lock."""
    from gzkit.commands.common import ensure_initialized, get_project_root

    ensure_initialized()
    project_root = get_project_root()
    lock_file = _lock_path(project_root, obpi_id)

    if lock_file.is_file():
        existing = json.loads(lock_file.read_text(encoding="utf-8"))
        claimed_at = datetime.fromisoformat(existing["claimed_at"])
        ttl = existing.get("ttl_minutes", 120)
        now = datetime.now(UTC)
        elapsed = (now - claimed_at).total_seconds() / 60

        if elapsed < ttl and existing.get("agent") != _resolve_agent():
            if as_json:
                print(json.dumps({"status": "conflict", "holder": existing}))
            else:
                console.print(
                    f"[red]CONFLICT:[/red] {obpi_id} locked by {existing.get('agent')} "
                    f"at {existing['claimed_at']} (TTL {ttl}m, {elapsed:.0f}m elapsed)"
                )
            sys.exit(1)

    agent = _resolve_agent()
    lock_data = {
        "obpi_id": obpi_id,
        "agent": agent,
        "pid": os.getpid(),
        "session_id": os.environ.get("CLAUDE_SESSION_ID", str(os.getpid())),
        "claimed_at": datetime.now(UTC).isoformat(),
        "branch": _current_branch(),
        "ttl_minutes": ttl_minutes,
    }
    lock_file.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")

    if as_json:
        print(json.dumps({"status": "claimed", "lock": lock_data}))
    else:
        console.print(f"[green]Claimed:[/green] {obpi_id} (agent={agent}, ttl={ttl_minutes}m)")


def obpi_lock_release_cmd(obpi_id: str, as_json: bool) -> None:
    """Release an OBPI work lock."""
    from gzkit.commands.common import ensure_initialized, get_project_root

    ensure_initialized()
    project_root = get_project_root()
    lock_file = _lock_path(project_root, obpi_id)

    if not lock_file.exists():
        if as_json:
            print(json.dumps({"status": "not_found", "obpi_id": obpi_id}))
        else:
            console.print(f"[yellow]No lock found:[/yellow] {obpi_id}")
        return

    lock_file.unlink()
    if as_json:
        print(json.dumps({"status": "released", "obpi_id": obpi_id}))
    else:
        console.print(f"[green]Released:[/green] {obpi_id}")


def obpi_lock_status_cmd(adr_id: str | None, as_json: bool) -> None:
    """List active OBPI locks."""
    from gzkit.commands.common import ensure_initialized, get_project_root

    ensure_initialized()
    project_root = get_project_root()
    lock_d = _lock_dir(project_root)

    locks = []
    now = datetime.now(UTC)
    for lock_file in sorted(lock_d.glob("*.lock.json")):
        try:
            data = json.loads(lock_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        if adr_id:
            lock_obpi = data.get("obpi_id", "")
            # OBPI-X.Y.Z-NN -> ADR-X.Y.Z
            parts = lock_obpi.replace("OBPI-", "ADR-").rsplit("-", 1)
            if parts[0] != adr_id:
                continue

        claimed_at = datetime.fromisoformat(data["claimed_at"])
        ttl = data.get("ttl_minutes", 120)
        elapsed = (now - claimed_at).total_seconds() / 60
        data["elapsed_minutes"] = round(elapsed, 1)
        data["expired"] = elapsed >= ttl
        locks.append(data)

    if as_json:
        print(json.dumps({"locks": locks, "count": len(locks)}))
    else:
        if not locks:
            console.print("[dim]No active locks.[/dim]")
            return
        for lock in locks:
            status = "[red]EXPIRED[/red]" if lock["expired"] else "[green]ACTIVE[/green]"
            console.print(
                f"  {lock['obpi_id']}  {status}  agent={lock['agent']}  "
                f"elapsed={lock['elapsed_minutes']}m  ttl={lock.get('ttl_minutes', 120)}m"
            )
