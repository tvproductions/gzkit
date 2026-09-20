"""Awareness of the settings-local backup vault (GHI #1072).

``scripts/settings_local_backup.py`` writes timestamped snapshots of
``.claude/settings.local.json`` outside the repository, so the vault survives
whatever happens to the working tree. This module is the reading half: it lets
gzkit report whether a vault exists, whether its newest snapshot still matches
the live file, and where to find it.

Why gzkit does NOT import the hook, and the hook does not import gzkit: the
hook is deliberately standalone and stdlib-only, because "a backup failure must
not cost the operator a session". Sharing code would make the backup depend on
gzkit importing cleanly, which is precisely the condition under which a backup
matters most and is least likely to hold. The two implementations are instead
held in agreement by ``tests/governance/test_settings_vault_awareness.py``,
the same shape ``test_active_campaign_registry.py`` uses for the campaign
pointer.

Until this module existed the hook's guarantee had no witness. It was false on
Windows for an unknown period (GHI #1071) with the external vault empty, and
nothing reported it.
"""

from __future__ import annotations

import hashlib
import re
from enum import Enum
from pathlib import Path, PurePath

from pydantic import BaseModel, ConfigDict, Field

#: Location of the live file, relative to the project root.
LIVE_RELATIVE = Path(".claude") / "settings.local.json"

#: Snapshots are named ``settings.local.<stamp>.json`` by the hook.
_SNAPSHOT_GLOB = "settings.local.*.json"


class VaultState(Enum):
    """What the vault can be, from gzkit's point of view."""

    CURRENT = "current"
    DRIFTED = "drifted"
    ABSENT = "absent"
    RECOVERABLE = "recoverable"
    NOT_APPLICABLE = "not_applicable"


class VaultStatus(BaseModel):
    """A reportable answer about one project's vault."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    state: VaultState = Field(..., description="What the vault currently is")
    directory: Path = Field(..., description="Where the vault lives, outside the project")
    snapshot_count: int = Field(..., description="How many snapshots the vault holds")
    message: str = Field(..., description="Operator-facing explanation of the state")

    @property
    def is_actionable(self) -> bool:
        """True when a maintenance pass should say something to the operator."""
        return self.state in (VaultState.DRIFTED, VaultState.ABSENT, VaultState.RECOVERABLE)


def vault_slug(root: PurePath) -> str:
    """Flatten a project root into one filesystem-safe path segment.

    Must agree with ``_slug`` in ``scripts/settings_local_backup.py``.
    ``str(Path)`` emits the platform separator, so a Windows root keeps its
    backslashes and its drive letter; a segment carrying a drive is absolute
    and ``pathlib`` discards everything to its left, which is how the vault
    ended up inside the repository it protects (GHI #1071).
    """
    flattened = re.sub(r"[^A-Za-z0-9._-]+", "-", root.as_posix()).strip("-")
    return flattened or "root"


def vault_dir(root: PurePath, vault_root: Path | None = None) -> Path:
    """Return the vault directory for *root*.

    ``vault_root`` overrides the computed location for tests; production
    callers omit it and get ``~/.claude/backups/<slug>/settings.local``.
    """
    if vault_root is not None:
        return vault_root
    return Path.home() / ".claude" / "backups" / vault_slug(root) / "settings.local"


def _digest(path: Path) -> str:
    """Return the SHA-256 of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshots(directory: Path) -> list[Path]:
    """Return the vault's snapshots, oldest first."""
    if not directory.is_dir():
        return []
    return sorted(directory.glob(_SNAPSHOT_GLOB))


def _status_without_live_file(directory: Path, snapshots: list[Path]) -> VaultStatus:
    """Report the two states that apply when the live file is gone.

    Surviving snapshots make this the recovery case, which is the scenario the
    backup hook was written for; no snapshots means there was never anything
    to protect here.
    """
    if snapshots:
        newest = snapshots[-1]
        return VaultStatus(
            state=VaultState.RECOVERABLE,
            directory=directory,
            snapshot_count=len(snapshots),
            message=(
                f"{LIVE_RELATIVE.as_posix()} is missing but {len(snapshots)} snapshot(s) "
                f"survive. Restore the newest with: copy {newest.name} from {directory}"
            ),
        )
    return VaultStatus(
        state=VaultState.NOT_APPLICABLE,
        directory=directory,
        snapshot_count=0,
        message=(
            f"No {LIVE_RELATIVE.as_posix()} in this project and no snapshots; nothing to back up."
        ),
    )


def vault_status(root: Path, vault_root: Path | None = None) -> VaultStatus:
    """Report the vault's state for the project at *root*.

    Absence is reported rather than passed over, because an empty vault and an
    unchecked vault look identical from the outside. That indistinguishability
    is what let GHI #1071 run undetected.
    """
    directory = vault_dir(root, vault_root)
    snapshots = _snapshots(directory)
    live = root / LIVE_RELATIVE

    if not live.is_file():
        return _status_without_live_file(directory, snapshots)

    if not snapshots:
        return VaultStatus(
            state=VaultState.ABSENT,
            directory=directory,
            snapshot_count=0,
            message=(
                f"No snapshots of {LIVE_RELATIVE.as_posix()} exist at {directory}. The file is "
                "gitignored, so a wipe or a fresh clone loses it with no recovery from origin."
            ),
        )

    if _digest(snapshots[-1]) == _digest(live):
        return VaultStatus(
            state=VaultState.CURRENT,
            directory=directory,
            snapshot_count=len(snapshots),
            message=(
                f"{len(snapshots)} snapshot(s) at {directory}; the newest matches the live file."
            ),
        )

    return VaultStatus(
        state=VaultState.DRIFTED,
        directory=directory,
        snapshot_count=len(snapshots),
        message=(
            f"The live {LIVE_RELATIVE.as_posix()} differs from the newest of "
            f"{len(snapshots)} snapshot(s) at {directory}. The backup hook records the "
            "change at the next session boundary; this is a notice, not a repair step."
        ),
    )
