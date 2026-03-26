"""Preflight scan and cleanup for stale pipeline artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.commands.common import console, get_project_root
from gzkit.pipeline_runtime import (
    find_stale_pipeline_markers,
    load_pipeline_json,
)


def _find_orphan_receipts(plans_dir: Path) -> list[tuple[Path, str]]:
    """Find receipts with no matching pipeline marker or plan file."""
    orphans: list[tuple[Path, str]] = []
    for receipt_path in sorted(plans_dir.glob(".plan-audit-receipt-*.json")):
        receipt = load_pipeline_json(receipt_path)
        if receipt is None:
            orphans.append((receipt_path, "unreadable"))
            continue
        obpi_id = str(receipt.get("obpi_id") or "unknown")
        marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
        has_marker = marker_path.exists()
        plan_files = list(plans_dir.glob("*.md"))
        has_plan = any(obpi_id in p.read_text(encoding="utf-8") for p in plan_files if p.is_file())
        if not has_marker and not has_plan:
            orphans.append((receipt_path, obpi_id))
    # Also check legacy receipt
    legacy = plans_dir / ".plan-audit-receipt.json"
    if legacy.exists():
        receipt = load_pipeline_json(legacy)
        if receipt is not None:
            obpi_id = str(receipt.get("obpi_id") or "unknown")
            marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
            has_marker = marker_path.exists()
            plan_files = list(plans_dir.glob("*.md"))
            has_plan = any(
                obpi_id in p.read_text(encoding="utf-8") for p in plan_files if p.is_file()
            )
            if not has_marker and not has_plan:
                orphans.append((legacy, obpi_id))
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
        ttl_minutes = int(lock.get("ttl_minutes") or 120)
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


def _apply_cleanup(
    stale_markers: list[tuple[Path, dict[str, Any]]],
    orphan_receipts: list[tuple[Path, str]],
    expired_locks: list[tuple[Path, str, float]],
) -> None:
    """Remove stale artifacts."""
    for path, _ in stale_markers:
        path.unlink(missing_ok=True)
    for path, _ in orphan_receipts:
        path.unlink(missing_ok=True)
    for path, _, _ in expired_locks:
        path.unlink(missing_ok=True)


def preflight_cmd(*, apply: bool = False, as_json: bool = False) -> None:
    """Scan for stale pipeline artifacts and optionally clean them up."""
    project_root = get_project_root()
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
            _apply_cleanup(stale_markers, orphan_receipts, expired_locks)
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
        _apply_cleanup(stale_markers, orphan_receipts, expired_locks)
        console.print("Cleanup applied.")
    else:
        console.print(f"\n{total} issue(s) found. Run with --apply to clean up.")
        raise SystemExit(1)
