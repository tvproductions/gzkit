"""Lock file I/O and TTL logic for OBPI work locks.

Provides the data layer for gz obpi lock commands. All functions take
``project_root: Path`` as input — no config or initialization required.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import yaml
from pydantic import BaseModel, ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from gzkit.ledger import LedgerEvent


class _LedgerSink(Protocol):
    """Structural type for the reap event sink — anything with ``append``.

    The reaper only needs to append release events; it does not need the full
    ``gzkit.ledger.Ledger`` surface. Typing the parameter structurally keeps the
    data layer free of a *runtime* layering import on ``gzkit.ledger`` (the
    ``LedgerEvent`` annotation is resolved under ``TYPE_CHECKING`` only, which
    sidesteps the ledger/ledger_events load-order cycle) and lets tests pass a
    lightweight capturing double (dependency inversion). The real
    ``gzkit.ledger.Ledger`` satisfies this Protocol structurally.
    """

    def append(self, event: LedgerEvent) -> None: ...


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
    running environment is inspected: ``CLAUDECODE`` env var (Claude Code
    exports this, not ``CLAUDE_CODE``) → ``"claude-code[-<sid8>]"``,
    ``CODEX_SANDBOX`` env var → ``"codex"``, fallback → ``"unknown-<pid>"``.
    """
    if agent_override is not None:
        return agent_override
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE"):
        sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
        return f"claude-code-{sid[:8]}" if sid else "claude-code"
    if os.environ.get("CODEX_SANDBOX"):
        return "codex"
    return f"unknown-{os.getpid()}"


def resolve_session_id() -> str:
    """Return session identifier from environment, or fall back to PID."""
    return (
        os.environ.get("CLAUDE_CODE_SESSION_ID")
        or os.environ.get("CLAUDE_SESSION_ID")
        or str(os.getpid())
    )


def current_branch() -> str:
    """Return the current git branch name, or ``"unknown"`` on error."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
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
    """Serialize *lock* to disk via exclusive-creation and return the written path.

    Uses ``open(path, "x")`` so that the second concurrent attempt raises
    ``FileExistsError`` instead of silently overwriting an existing lock. This
    closes the check-then-write race the token-block doctrine
    (``.gzkit/rules/token-block-discipline.md``) names as the load-bearing
    exclusion property of the lock primitive.

    Computed fields (``is_expired``, ``elapsed_minutes``) are excluded from the
    stored payload.
    """
    path = lock_path(project_root, lock.obpi_id)
    payload = lock.model_dump(exclude={"is_expired", "elapsed_minutes"})
    with open(path, "x", encoding="utf-8") as f:
        f.write(json.dumps(payload, indent=2))
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


def _head_commit_sha() -> str:
    """Return the current HEAD commit SHA, or ``"unknown"`` on failure."""
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


def _write_reaping_handoff(project_root: Path, lock: LockData, reaper_agent: str) -> Path:
    """Write an ``abandoned_by_reaper`` register entry under ``.gzkit/handoffs/``.

    The register entry pairs a reaped lock surrender with a durable audit
    artifact (token-block discipline § Sub-Invariant 3). Frontmatter carries the
    reaping-specific fields (``abandoned: true``, ``category: reaping``,
    ``abandoned_by``, ``abandoned_at``, ``previous_agent``) plus the
    Sub-Invariant 2 minimum-information fields (``last_lock_event_timestamp``,
    ``last_commit_sha``). Returns the on-disk path written.
    """
    handoff_dir = project_root / ".gzkit" / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    timestamp_token = now.replace(":", "").replace("-", "")
    filename = f"{timestamp_token}-{lock.obpi_id}-reaped.md"
    path = handoff_dir / filename

    # Derive the parent ADR id from the OBPI semver triplet
    # (OBPI-X.Y.Z-NN[-slug] -> ADR-X.Y.Z). rsplit("-", 1) is wrong for
    # slug-bearing obpi_ids — it strips only the last slug segment, yielding an
    # invalid ADR id like ADR-0.0.72-02-handoff-frontmatter (OBPI-0.0.72-02 fix).
    _semver_match = re.match(r"OBPI-(\d+\.\d+\.\d+)-", lock.obpi_id)
    adr_id = f"ADR-{_semver_match.group(1)}" if _semver_match else lock.obpi_id
    frontmatter = {
        "mode": "CREATE",
        "adr_id": adr_id,
        "obpi_id": lock.obpi_id,
        "branch": lock.branch,
        "timestamp": now,
        "agent": reaper_agent,
        "abandoned": True,
        "category": "reaping",
        "abandoned_by": reaper_agent,
        "abandoned_at": now,
        "previous_agent": lock.agent,
        "last_lock_event_timestamp": lock.claimed_at,
        "last_commit_sha": _head_commit_sha(),
    }

    body = (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n\n"
        + f"<!-- abandoned_by_reaper register entry for {lock.obpi_id} -->\n\n"
        + "## Current State Summary\n\n"
        + f"Lock for {lock.obpi_id} (held by `{lock.agent}`) reaped by "
        + f"`{reaper_agent}` after TTL ({lock.ttl_minutes}m) expired.\n\n"
        + "## Decisions Made\n\n"
        + f"- Forcible surrender: TTL exceeded; last claim at {lock.claimed_at}.\n"
    )

    path.write_text(body, encoding="utf-8")
    return path


def reap_expired_locks(
    project_root: Path,
    *,
    ledger: _LedgerSink | None = None,
    reaper_agent: str | None = None,
) -> list[LockData]:
    """Reap expired locks, pairing each surrender with a register entry.

    For every expired lock the reaper writes an ``abandoned_by_reaper`` register
    entry BEFORE deleting the lock (token-block discipline § Sub-Invariant 3),
    then deletes the lock, then — only after a successful delete — emits the
    ``obpi_lock_released`` event. The ordering is the load-bearing invariant:

    - handoff write fails → lock NOT deleted, NO event, lock excluded from the
      returned list (fail-closed; the register entry is the precondition);
    - lock already gone / unlink fails → NO event for a release that did not
      happen, lock excluded from the returned list (no duplicate-event-on-retry,
      no crash on a concurrently-reaped lock).

    When *ledger* is provided, the event cites the written register entry's
    ``handoff_path``. When *ledger* is ``None`` the register entry is still
    written and the lock still reaped, but no event is emitted (no sink).
    """
    # Lazy import: gzkit.ledger_events ↔ gzkit.ledger form a load-order cycle
    # (ledger_events imports LedgerEvent from ledger; ledger re-imports the event
    # constructors from ledger_events). Doing it at call time keeps lock_manager —
    # the config-free data layer — free of the ledger stack at module load. Load
    # gzkit.ledger FIRST: it defines LedgerEvent before its own ledger_events
    # import, so loading it fully resolves the pair and the constructor import
    # then succeeds even when reap is the first caller to touch the ledger stack
    # (e.g. an isolated unit test, which is how the REQ-coverage gate runs).
    import gzkit.ledger  # noqa: F401, PLC0415 — force-load to settle the cycle
    from gzkit.ledger_events import obpi_lock_released_event  # noqa: PLC0415

    agent = reaper_agent or resolve_agent(None)
    reaped: list[LockData] = []
    for lock in list_locks(project_root):
        if not lock.is_expired:
            continue
        try:
            handoff_path = _write_reaping_handoff(project_root, lock, agent)
        except OSError:
            # Fail-closed: no register entry → lock survives, no event emitted.
            continue
        try:
            lock_path(project_root, lock.obpi_id).unlink()
        except OSError:
            # Lock vanished (concurrent reaper) or could not be removed: emit no
            # release event for a surrender that did not complete here, and leave
            # any still-present lock for the next pass. The register entry we just
            # wrote is harmless if orphaned.
            continue
        if ledger is not None:
            ledger.append(
                obpi_lock_released_event(
                    obpi_id=lock.obpi_id,
                    agent=agent,
                    force=True,
                    handoff_path=handoff_path.relative_to(project_root).as_posix(),
                )
            )
        reaped.append(lock)
    return reaped
