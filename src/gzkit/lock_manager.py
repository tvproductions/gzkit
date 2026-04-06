"""Lock file I/O and TTL logic for OBPI work locks.

Provides the data layer for gz obpi lock commands. All functions take
``project_root: Path`` as input — no config or initialization required.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field


class LockData(BaseModel):
    """Immutable representation of a single OBPI work lock."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="OBPI identifier, e.g. OBPI-0.0.14-01")
    agent: str = Field(..., description="Agent identity string")
    pid: int = Field(..., description="Process ID of the locking process")
    session_id: str = Field(..., description="Session or process identifier")
    claimed_at: str = Field(..., description="ISO 8601 timestamp when lock was claimed")
    branch: str = Field(..., description="Git branch active at claim time")
    ttl_minutes: int = Field(..., description="Time-to-live in minutes")

    @computed_field
    @property
    def is_expired(self) -> bool:
        """Return True if the lock TTL has elapsed."""
        claimed = datetime.fromisoformat(self.claimed_at)
        elapsed = (datetime.now(UTC) - claimed).total_seconds() / 60
        return elapsed >= self.ttl_minutes

    @computed_field
    @property
    def elapsed_minutes(self) -> float:
        """Return minutes elapsed since claimed_at."""
        claimed = datetime.fromisoformat(self.claimed_at)
        return (datetime.now(UTC) - claimed).total_seconds() / 60


def resolve_agent(agent_override: str | None = None) -> str:
    """Resolve agent identity.

    If *agent_override* is provided it is returned as-is. Otherwise the
    running environment is inspected: ``CLAUDE_CODE`` env var → ``"claude-code"``,
    ``CODEX_SANDBOX`` env var → ``"codex"``, fallback → ``"unknown-<pid>"``.
    """
    if agent_override is not None:
        return agent_override
    if os.environ.get("CLAUDE_CODE"):
        return "claude-code"
    if os.environ.get("CODEX_SANDBOX"):
        return "codex"
    return f"unknown-{os.getpid()}"


def resolve_session_id() -> str:
    """Return session identifier from environment, or fall back to PID."""
    return os.environ.get("CLAUDE_SESSION_ID", str(os.getpid()))


def current_branch() -> str:
    """Return the current git branch name, or ``"unknown"`` on error."""
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


def lock_dir(project_root: Path) -> Path:
    """Return the OBPI lock directory, creating it if it does not exist."""
    d = project_root / ".gzkit" / "locks" / "obpi"
    d.mkdir(parents=True, exist_ok=True)
    return d


def lock_path(project_root: Path, obpi_id: str) -> Path:
    """Return the lock file path for *obpi_id*."""
    return lock_dir(project_root) / f"{obpi_id}.lock.json"


def read_lock(project_root: Path, obpi_id: str) -> LockData | None:
    """Read and parse a lock file.

    Returns ``None`` if the file does not exist or contains invalid JSON.
    """
    path = lock_path(project_root, obpi_id)
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return LockData(**data)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return None


def write_lock(project_root: Path, lock: LockData) -> Path:
    """Serialize *lock* to disk and return the written path.

    Uses ``model_dump()`` to produce a plain dict before JSON serialisation so
    that computed fields (``is_expired``, ``elapsed_minutes``) are excluded from
    the stored payload.
    """
    path = lock_path(project_root, lock.obpi_id)
    # Exclude computed fields — only persist the raw declared fields.
    payload = lock.model_dump(exclude={"is_expired", "elapsed_minutes"})
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def delete_lock(project_root: Path, obpi_id: str) -> bool:
    """Delete the lock file for *obpi_id*.

    Returns ``True`` if the file existed and was removed, ``False`` if it was
    not found.
    """
    path = lock_path(project_root, obpi_id)
    if not path.is_file():
        return False
    path.unlink()
    return True


def list_locks(project_root: Path, adr_filter: str | None = None) -> list[LockData]:
    """Return all parseable locks, optionally filtered by ADR prefix.

    *adr_filter* should be an ADR identifier such as ``"ADR-0.0.14"``.
    Matching converts OBPI-X.Y.Z-NN → ADR-X.Y.Z and compares the prefix.
    """
    d = lock_dir(project_root)
    locks: list[LockData] = []
    for lock_file in sorted(d.glob("*.lock.json")):
        try:
            raw = lock_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            lock = LockData(**data)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            continue

        if adr_filter is not None:
            # OBPI-X.Y.Z-NN → ADR-X.Y.Z
            parts = lock.obpi_id.replace("OBPI-", "ADR-").rsplit("-", 1)
            if parts[0] != adr_filter:
                continue

        locks.append(lock)
    return locks


def reap_expired_locks(project_root: Path) -> list[LockData]:
    """Delete all expired locks and return the reaped ``LockData`` objects."""
    reaped: list[LockData] = []
    for lock in list_locks(project_root):
        if lock.is_expired:
            path = lock_path(project_root, lock.obpi_id)
            try:
                path.unlink()
                reaped.append(lock)
            except OSError:
                pass
    return reaped
