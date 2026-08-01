"""gz handoff archive — governed move-not-delete retention (ADR-0.0.65 OBPI-05).

Selects handoffs older than a threshold that are safe to relocate from
``.gzkit/handoffs/`` into ``.gzkit/handoffs/archive/``, honoring guards so the
audit trail is preserved by relocation, never removal:

* **lock-coupling** — never archive a handoff whose project-relative path is any
  recorded ``obpi_lock_released`` ``handoff_path`` (ADR-0.0.41 / token-block).
* **chain-integrity** — never archive a handoff involved in any ``continues_from:``
  chain, in EITHER direction (a referrer that points, or a target that is pointed
  at). Keeping the whole chain canonical means the production resolver
  (:func:`gzkit.handoff_api.load_handoff_chain`) keeps resolving unchanged — this
  module never edits that resolver (OBPI-03's surface), it stays conservative.
* **move-not-delete** — relocation is an ATOMIC no-clobber (``os.link`` + unlink):
  a same-name file already in ``archive/`` is NEVER overwritten, so the migration
  floor (canonical + archive) is preserved by construction, even under a race.

Target resolution DELEGATES to the production resolver
(:func:`gzkit.handoff_api.resolve_continues_from`), so pointer forms it accepts —
bare, project-relative, ``./``/``..``-bearing, absolute — all normalize to the
same protected target by construction rather than by a hand-mirrored copy that
could drift (GHI #689). This module owns the inode-identity keying only.

Domain core: stdlib + Pydantic only; the ledger and handoff frontmatter are read
through existing read-only helpers. No registered security surface is edited
(Requirement 5).

**Concurrency boundary (operator-attested, Step-4b round-3 ruling).** This verb
assumes *exclusive* access to the handoff store — it is an operator-invoked
maintenance command, not a concurrently-run service. Relocation of the
destination is atomic no-clobber (``os.link``), so a same-name file already in
``archive/`` is never overwritten; but the plan→execute guards are not defended
against a *second* ``gz`` process mutating ``.gzkit/handoffs/`` mid-run (e.g. a
concurrent ``gz handoff create``). Under gzkit's single-operator, lock-serialized
model there is no such concurrent writer; store-wide write serialization is
deliberately out of this verb's scope (it would overlap ``lock_manager``).

@covers ADR-0.0.65 (OBPI-0.0.65-05)
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.handoff_api import resolve_continues_from
from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter

_ARCHIVE_NAME = "archive"


class ArchivePlan(BaseModel):
    """Classified outcome of an archive scan — pure selection, no mutation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    eligible: list[str] = Field(
        default_factory=list,
        description="project-relative posix canonical paths safe to move into archive/",
    )
    skipped_locked: list[str] = Field(
        default_factory=list, description="skipped — referenced by an obpi_lock_released event"
    )
    skipped_chained: list[str] = Field(
        default_factory=list, description="skipped — participates in a continues_from chain"
    )
    skipped_recent: list[str] = Field(
        default_factory=list, description="skipped — newer than the threshold"
    )
    skipped_undatable: list[str] = Field(
        default_factory=list, description="skipped — no parseable frontmatter timestamp"
    )
    skipped_conflict: list[str] = Field(
        default_factory=list,
        description="skipped — a same-name file already exists in archive/ (never overwritten)",
    )


class ArchiveResult(BaseModel):
    """Outcome of executing an :class:`ArchivePlan`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    moved: list[str] = Field(
        default_factory=list,
        description="canonical paths that were relocated into archive/ (source paths)",
    )
    skipped_conflict: list[str] = Field(
        default_factory=list,
        description="skipped at execution — a same-name dest appeared after planning (race)",
    )
    plan: ArchivePlan = Field(..., description="the plan that was executed")


def _canonical_dir(base_path: Path) -> Path:
    return base_path / ".gzkit" / "handoffs"


def _rel(base_path: Path, path: Path) -> str:
    return path.relative_to(base_path).as_posix()


def _key(path: Path) -> str:
    """Identity key for a path: filesystem identity when it exists, else a string.

    An existing path is keyed by ``(st_dev, st_ino)`` so two names for the SAME
    file compare equal even on a case-insensitive filesystem (macOS/Windows) —
    ``TARGET.md`` and ``target.md`` resolve to one inode and must not be treated as
    distinct targets (Step-4b round-3 finding). A non-existent target has no inode,
    so it falls back to a resolved-string key (it protects nothing on disk anyway).
    """
    try:
        stat = path.stat()
        return f"ino:{stat.st_dev}:{stat.st_ino}"
    except OSError:
        try:
            return f"str:{path.resolve().as_posix()}"
        except OSError:
            return f"str:{path.as_posix()}"


def _dest_occupied(dest: Path) -> bool:
    """Return True when a directory entry already exists at ``dest``, including a dangling symlink.

    ``exists()`` follows symlinks and misses dangling ones, but ``os.link`` still fails
    on them, so planning must agree with execution (Step-4b round-3 finding).
    """
    return dest.exists() or dest.is_symlink()


def _markdown_handoffs(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.md") if p.name != "AGENTS.md")


def _canonical_handoffs(base_path: Path) -> list[Path]:
    """Markdown handoffs in the canonical store (non-recursive: archive/ excluded)."""
    return _markdown_handoffs(_canonical_dir(base_path))


def _archived_handoffs(base_path: Path) -> list[Path]:
    """Handoffs already relocated into archive/ — still live chain referrers."""
    return _markdown_handoffs(_canonical_dir(base_path) / _ARCHIVE_NAME)


def _frontmatter(path: Path) -> dict | None:
    try:
        parsed = parse_frontmatter(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, HandoffValidationError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _parse_ts(raw: object) -> datetime | None:
    """Parse an ISO-8601 frontmatter timestamp; return None when undatable."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        parsed = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _locked_paths(base_path: Path) -> set[str]:
    """Project-relative handoff paths recorded on obpi_lock_released events."""
    from gzkit.ledger import Ledger  # local import keeps the domain core ledger-free

    ledger_path = base_path / ".gzkit" / "ledger.jsonl"
    if not ledger_path.is_file():
        return set()
    locked: set[str] = set()
    for event in Ledger(ledger_path).query(event_type="obpi_lock_released"):
        handoff_path = event.extra.get("handoff_path")
        if isinstance(handoff_path, str) and handoff_path:
            locked.add(handoff_path.removeprefix("./"))
    return locked


def _resolve_pointer_key(ref: str, referrer: Path, base_path: Path) -> str:
    """Resolve a continues_from pointer to a comparison key.

    Delegates resolution to the production resolver
    (:func:`gzkit.handoff_api.resolve_continues_from`) and applies this module's
    inode-identity key. This module owns the KEYING; it does not own the pointer
    semantics, and must never re-implement them: the guard is only correct while
    it resolves every pointer form exactly as the CREATE/RESUME path does.

    The branching was previously hand-mirrored here across an OBPI brief boundary
    with the coupling asserted in a docstring and enforced by nothing (GHI #689).
    """
    return _key(resolve_continues_from(ref, referrer, base_path))


def _chain_target_keys(handoffs: list[Path], base_path: Path) -> set[str]:
    """Return resolved keys of every continues_from target across the given handoffs."""
    keys: set[str] = set()
    for path in handoffs:
        frontmatter = _frontmatter(path)
        if frontmatter is None:
            continue
        pointer = str(frontmatter.get("continues_from") or "").strip()
        if pointer:
            keys.add(_resolve_pointer_key(pointer, path, base_path))
    return keys


def _has_pointer(path: Path) -> bool:
    frontmatter = _frontmatter(path)
    return bool(frontmatter and str(frontmatter.get("continues_from") or "").strip())


def plan_archive(
    *,
    base_path: Path,
    older_than_days: int,
    now: datetime,
) -> ArchivePlan:
    """Classify canonical handoffs into eligible / skipped buckets (no mutation).

    A handoff is eligible only when it is older than ``now - older_than_days``,
    not lock-coupled, not part of any continues_from chain (referrer or target),
    and has no pre-existing same-name file in ``archive/``. Undatable handoffs are
    conservatively skipped so an un-ageable audit trail is never lost.
    """
    handoffs = _canonical_handoffs(base_path)
    cutoff = now - timedelta(days=older_than_days)
    locked = _locked_paths(base_path)
    # Chain protection spans canonical + archive and both directions: an archived
    # handoff is still a live referrer, and a referrer must not be archived either.
    target_keys = _chain_target_keys(handoffs + _archived_handoffs(base_path), base_path)
    archive_dir = _canonical_dir(base_path) / _ARCHIVE_NAME

    buckets: dict[str, list[str]] = {
        name: []
        for name in (
            "eligible",
            "skipped_locked",
            "skipped_chained",
            "skipped_recent",
            "skipped_undatable",
            "skipped_conflict",
        )
    }
    for path in handoffs:
        rel = _rel(base_path, path)
        timestamp = _parse_ts((_frontmatter(path) or {}).get("timestamp"))
        chain_involved = _has_pointer(path) or _key(path) in target_keys
        if timestamp is None:
            buckets["skipped_undatable"].append(rel)
        elif timestamp > cutoff:
            buckets["skipped_recent"].append(rel)
        elif rel in locked:
            buckets["skipped_locked"].append(rel)
        elif chain_involved:
            buckets["skipped_chained"].append(rel)
        elif _dest_occupied(archive_dir / path.name):
            buckets["skipped_conflict"].append(rel)
        else:
            buckets["eligible"].append(rel)

    return ArchivePlan(**buckets)


def execute_archive(plan: ArchivePlan, *, base_path: Path) -> ArchiveResult:
    """Relocate each eligible handoff into ``archive/`` atomically (move-not-delete).

    Uses ``os.link`` (which fails with ``FileExistsError`` if the destination
    exists) then unlinks the source — an atomic no-clobber move. A same-name file
    that appears in ``archive/`` between planning and execution is therefore NEVER
    overwritten; it is recorded on ``skipped_conflict`` and its source left in place.
    """
    archive_dir = _canonical_dir(base_path) / _ARCHIVE_NAME
    moved: list[str] = []
    raced: list[str] = []
    for rel in plan.eligible:
        source = base_path / rel
        if not source.is_file():
            continue
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / source.name
        try:
            os.link(source, dest)
        except FileExistsError:
            raced.append(rel)
            continue
        source.unlink()
        moved.append(rel)
    return ArchiveResult(moved=moved, skipped_conflict=raced, plan=plan)
