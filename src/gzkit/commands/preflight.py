"""Preflight scan and cleanup for stale pipeline artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from rich.markup import escape

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.ledger import Ledger
from gzkit.lock_manager import (
    DEFAULT_LOCK_TTL_MINUTES,
    reap_expired_locks,
    resolve_agent,
)
from gzkit.pipeline_markers import plan_declares_obpi
from gzkit.pipeline_runtime import (
    find_stale_pipeline_markers,
    load_pipeline_json,
)


def _find_orphan_receipts(plans_dir: Path) -> list[tuple[Path, str]]:
    """Find receipts with no matching pipeline marker or plan file."""
    receipt_paths = sorted(plans_dir.glob(".plan-audit-receipt-*.json"))
    legacy = plans_dir / ".plan-audit-receipt.json"
    if legacy.exists():
        receipt_paths.append(legacy)
    plan_files = [p for p in plans_dir.glob("*.md") if p.is_file()]
    orphans: list[tuple[Path, str]] = []
    for receipt_path in receipt_paths:
        receipt = load_pipeline_json(receipt_path)
        if receipt is None:
            orphans.append((receipt_path, "unreadable"))
            continue
        obpi_id = str(receipt.get("obpi_id") or "unknown")
        has_marker = (plans_dir / f".pipeline-active-{obpi_id}.json").exists()
        has_plan = any(plan_declares_obpi(p, obpi_id) for p in plan_files)
        if not has_marker and not has_plan:
            orphans.append((receipt_path, obpi_id))
    return orphans


def _find_expired_locks(locks_dir: Path) -> list[tuple[Path, str, float]]:
    """Find lock files whose claimed_at + ttl_minutes has passed."""
    expired: list[tuple[Path, str, float]] = []
    if not locks_dir.is_dir():
        return expired
    now = datetime.now(UTC)
    for lock_path in sorted(locks_dir.glob("*.lock.json")):
        lock = load_pipeline_json(lock_path)
        if lock is None:
            expired.append((lock_path, "unreadable", 0))
            continue
        obpi_id = str(lock.get("obpi_id") or "unknown")
        claimed_at = str(lock.get("claimed_at") or "")
        ttl_minutes = int(lock.get("ttl_minutes") or DEFAULT_LOCK_TTL_MINUTES)
        if not claimed_at:
            expired.append((lock_path, obpi_id, 0))
            continue
        try:
            claim_time = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
        except ValueError:
            expired.append((lock_path, obpi_id, 0))
            continue
        age_minutes = (now - claim_time).total_seconds() / 60
        if age_minutes > ttl_minutes:
            expired.append((lock_path, obpi_id, age_minutes))
    return expired


ARCHIVE_DIR_NAME = "archive"


class ReceiptArchiveResult(BaseModel):
    """Outcome of preserving one plan-audit receipt."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    archived: bool = Field(..., description="True only if the copy verified and origin removed")
    archive_path: str = Field(default="", description="Where the preserved receipt now lives")
    provenance_path: str = Field(default="", description="Sidecar recording origin and verdict")
    error: str = Field(default="", description="Why preservation failed; empty on success")


def archive_plan_audit_receipt(receipt_path: Path) -> ReceiptArchiveResult:
    """Preserve an orphaned plan-audit receipt instead of unlinking it (GHI #967).

    A raw ``unlink`` here destroyed audit content — a verdict, a gap count, scope
    collision rows — three lines under a docstring that refuses to do the same to
    an expired lock because it would be "a silent bypass of that audit coupling".

    Operator ruling 2026-09-06: cleanup MAY archive automatically, provided it
    preserves the complete contents and provenance, verifies the archive before
    removing the operational copy, leaves the finding and FAIL verdict
    unresolved, and — if preservation fails — retains the original and fails
    closed. **Moving evidence is not resolving its finding**, which is why the
    provenance record carries ``finding_resolved: false`` and the receipt's bytes
    are copied unchanged: the verdict still stands, it simply no longer sits in
    the operational scan path.

    Order is the safety property. The copy is written and its digest compared to
    the source BEFORE the source is removed, so any failure leaves the only copy
    where it was.
    """
    try:
        source_bytes = receipt_path.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()
        archive_dir = receipt_path.parent / ARCHIVE_DIR_NAME
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / receipt_path.name
        shutil.copyfile(receipt_path, archive_path)
        if hashlib.sha256(archive_path.read_bytes()).hexdigest() != digest:
            return ReceiptArchiveResult(
                archived=False, error=f"archive digest mismatch for {receipt_path.name}"
            )
        provenance_path = archive_dir / f"{receipt_path.name}.provenance.json"
        provenance_path.write_text(
            json.dumps(
                {
                    "original_path": str(receipt_path),
                    "archived_at": datetime.now(UTC).isoformat(),
                    "sha256": digest,
                    "obpi_id": _receipt_field(source_bytes, "obpi_id"),
                    "verdict": _receipt_field(source_bytes, "verdict"),
                    "finding_resolved": False,
                    "note": (
                        "Preserved by gz preflight --apply. Moving evidence does not "
                        "resolve its finding: the verdict above still stands."
                    ),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        # Fail closed: the original is still the only copy and must survive.
        return ReceiptArchiveResult(archived=False, error=f"{type(exc).__name__}: {exc}")

    receipt_path.unlink(missing_ok=True)
    return ReceiptArchiveResult(
        archived=True,
        archive_path=str(archive_path),
        provenance_path=str(provenance_path),
    )


def _receipt_field(source_bytes: bytes, key: str) -> str:
    """Read one field from the receipt for provenance; never fail the archive on it."""
    try:
        return str(json.loads(source_bytes.decode("utf-8")).get(key, "unknown"))
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return "unreadable"


def _apply_cleanup(
    project_root: Path,
    ledger: Ledger,
    stale_markers: list[tuple[Path, dict[str, Any]]],
    orphan_receipts: list[tuple[Path, str]],
) -> None:
    """Remove stale markers, PRESERVE orphan receipts, and reap expired locks.

    Markers are plain artifacts — a raw unlink is correct. Expired locks are
    tokens: their surrender is routed through the canonical ``reap_expired_locks``
    so every release writes an ``abandoned_by_reaper`` register entry and emits
    ``obpi_lock_released`` BEFORE the lock file is removed
    (token-block-discipline.md § Sub-Invariant 3).

    Receipts are neither (GHI #967). A plan-audit receipt carries a verdict, so it
    is audit content and is ARCHIVED rather than unlinked — see
    ``archive_plan_audit_receipt`` for the four constraints that governs. A
    receipt whose preservation fails is left exactly where it is and reported, so
    the cleanup pass can never be the reason a finding disappeared.
    """
    for path, _ in stale_markers:
        path.unlink(missing_ok=True)
    for path, _ in orphan_receipts:
        result = archive_plan_audit_receipt(path)
        if result.archived:
            console.print(f"  preserved: {escape(result.archive_path)} (finding unresolved)")
        else:
            console.print(
                f"  [red]not archived, original retained:[/red] "
                f"{path.name} — {escape(result.error)}"
            )
    reap_expired_locks(project_root, ledger=ledger, reaper_agent=resolve_agent(None))


def preflight_cmd(*, apply: bool = False, as_json: bool = False) -> None:
    """Scan for stale pipeline artifacts and optionally clean them up."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    plans_dir = project_root / ".claude" / "plans"
    locks_dir = project_root / ".gzkit" / "locks" / "obpi"

    stale_markers = find_stale_pipeline_markers(plans_dir) if plans_dir.is_dir() else []
    orphan_receipts = _find_orphan_receipts(plans_dir) if plans_dir.is_dir() else []
    expired_locks = _find_expired_locks(locks_dir)

    if as_json:
        data = {
            "stale_markers": [
                {"path": str(p.name), "obpi_id": str(m.get("obpi_id", "unknown"))}
                for p, m in stale_markers
            ],
            "orphan_receipts": [
                {"path": str(p.name), "obpi_id": oid} for p, oid in orphan_receipts
            ],
            "expired_locks": [
                {"path": str(p.name), "obpi_id": oid, "age_minutes": round(age, 1)}
                for p, oid, age in expired_locks
            ],
        }
        console.print(json.dumps(data, indent=2))
        if apply:
            _apply_cleanup(project_root, ledger, stale_markers, orphan_receipts)
        return

    total = len(stale_markers) + len(orphan_receipts) + len(expired_locks)

    if total == 0:
        console.print("Preflight scan: clean")
        return

    console.print("Preflight scan:")
    for path, marker in stale_markers:
        obpi_id = str(marker.get("obpi_id", "unknown"))
        console.print(f"  Stale marker:   {path.name} ({obpi_id})")
    for path, obpi_id in orphan_receipts:
        console.print(f"  Orphan receipt:  {path.name} ({obpi_id})")
    for path, obpi_id, age in expired_locks:
        console.print(f"  Expired lock:    {path.name} ({obpi_id}, {age:.0f}m)")

    if apply:
        _apply_cleanup(project_root, ledger, stale_markers, orphan_receipts)
        console.print("Cleanup applied.")
    else:
        console.print(f"\n{total} issue(s) found. Run with --apply to clean up.")
        raise SystemExit(1)
