"""gz arb archive — governed move-not-delete retention for ARB receipts (GHI #594).

ARB exposed a read/harvest half (``advise``, ``patterns``) and no write-lifecycle
half, so ``artifacts/receipts/`` grew without bound — 3,282 files at the time this
landed, against the 1,875 recorded when the defect was filed. This module supplies
the retention half on the same shape ``gz handoff archive`` established under
GHI #585 (:mod:`gzkit.handoff_archive`): classify, then relocate.

Guards, each the ARB analogue of a handoff-archive guard:

* **citation-coupling** — never archive a receipt whose id is cited anywhere in the
  ledger. A receipt id IS its filename stem (``arb-ruff-<hex>.json`` ↔
  ``arb-ruff-<hex>``), and AGENTS.md § Attestation makes those ids the canonical
  Heavy-lane evidence, so a cited receipt must stay where citations resolve. This
  mirrors handoff-archive's ``obpi_lock_released`` coupling.
* **ARB-owned only** — files whose stem does not start with ``arb-`` are left
  untouched. The receipts root is shared with other emitters
  (``adr-taxonomy-backfill-*``, ``foundation-sunset-migration-*``); this verb owns
  ARB's lifecycle and nothing else's.
* **move-not-delete** — relocation is an ATOMIC no-clobber (``os.link`` + unlink):
  a same-name file already in ``archive/`` is NEVER overwritten. Nothing here
  deletes. Purge is deliberately absent — GHI #594 records that the destructive
  half *"needs an operator design conversation on retention window, archive format,
  and purge authorization"*, so it is not this verb's to assume.

Age is read from the receipt's own ``timestamp_utc`` field, never ``mtime``: mtime
is rewritten by clone, checkout, and archive extraction, so ageing on it would
silently re-date the whole store. An undatable receipt is conservatively skipped.

Domain core: stdlib + Pydantic only; the ledger is read through the existing
read-only helper behind a local import.

**Concurrency boundary.** Like ``gz handoff archive``, this is an operator-invoked
maintenance command assuming exclusive access to the receipts root. Destination
relocation is atomic no-clobber, but the plan→execute window is not defended
against a second ``gz`` process emitting receipts mid-run.
"""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_ARCHIVE_NAME = "archive"
_ARB_PREFIX = "arb-"

# A receipt id as it appears in attestation evidence: the filename stem. Bounded to
# the id character class so the match stops at the enclosing JSON string delimiter.
_RECEIPT_ID_RE = re.compile(r"arb-[A-Za-z0-9.\-]+")


class ReceiptArchivePlan(BaseModel):
    """Classified outcome of a receipt archive scan — pure selection, no mutation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    eligible: list[str] = Field(
        default_factory=list,
        description="receipt filenames safe to move into archive/",
    )
    skipped_cited: list[str] = Field(
        default_factory=list,
        description="skipped — the receipt id is cited in the ledger as attestation evidence",
    )
    skipped_recent: list[str] = Field(
        default_factory=list, description="skipped — newer than the threshold"
    )
    skipped_undatable: list[str] = Field(
        default_factory=list, description="skipped — no parseable timestamp_utc"
    )
    skipped_conflict: list[str] = Field(
        default_factory=list,
        description="skipped — a same-name file already exists in archive/ (never overwritten)",
    )
    skipped_foreign: list[str] = Field(
        default_factory=list,
        description="skipped — not an ARB-emitted receipt (stem does not start with 'arb-')",
    )


class ReceiptArchiveResult(BaseModel):
    """Outcome of executing a :class:`ReceiptArchivePlan`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    moved: list[str] = Field(
        default_factory=list, description="receipt filenames relocated into archive/"
    )
    skipped_conflict: list[str] = Field(
        default_factory=list,
        description="skipped at execution — a same-name dest appeared after planning (race)",
    )
    plan: ReceiptArchivePlan = Field(..., description="the plan that was executed")


def _receipts(root: Path) -> list[Path]:
    """Receipt JSON files in the root (non-recursive, so archive/ is excluded)."""
    if not root.is_dir():
        return []
    return sorted(p for p in root.glob("*.json"))


def _parse_ts(raw: object) -> datetime | None:
    """Parse a receipt's ISO-8601 ``timestamp_utc``; return None when undatable."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        parsed = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _receipt_timestamp(path: Path) -> datetime | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return _parse_ts(payload.get("timestamp_utc"))


def _cited_receipt_ids(base_path: Path) -> set[str]:
    """Receipt ids cited anywhere in the ledger.

    Deliberately conservative: any ``arb-*`` token appearing in the ledger protects
    the matching receipt, regardless of which event or field carries it. Receipt ids
    reach the ledger through several shapes (``gz adr emit-receipt --evidence-json``
    payloads, OBPI completion attestation text, ARB's own events), and enumerating
    those shapes is the failure mode this repo keeps re-learning — an enumeration
    only covers the citation sites someone remembered.
    """
    ledger_path = base_path / ".gzkit" / "ledger.jsonl"
    if not ledger_path.is_file():
        return set()
    try:
        text = ledger_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return set(_RECEIPT_ID_RE.findall(text))


def plan_receipt_archive(
    *,
    root: Path,
    base_path: Path,
    older_than_days: int,
    now: datetime,
) -> ReceiptArchivePlan:
    """Classify receipts into eligible / skipped buckets (no mutation).

    A receipt is eligible only when it is ARB-emitted, older than
    ``now - older_than_days``, not cited in the ledger, and has no pre-existing
    same-name file in ``archive/``. Undatable receipts are conservatively skipped so
    an un-ageable receipt is never relocated out from under a citation this scan
    could not read.
    """
    cutoff = now - timedelta(days=older_than_days)
    cited = _cited_receipt_ids(base_path)
    archive_dir = root / _ARCHIVE_NAME

    buckets: dict[str, list[str]] = {
        name: []
        for name in (
            "eligible",
            "skipped_cited",
            "skipped_recent",
            "skipped_undatable",
            "skipped_conflict",
            "skipped_foreign",
        )
    }
    for path in _receipts(root):
        name = path.name
        if not path.stem.startswith(_ARB_PREFIX):
            buckets["skipped_foreign"].append(name)
            continue
        timestamp = _receipt_timestamp(path)
        if timestamp is None:
            buckets["skipped_undatable"].append(name)
        elif timestamp > cutoff:
            buckets["skipped_recent"].append(name)
        elif path.stem in cited:
            buckets["skipped_cited"].append(name)
        elif (archive_dir / name).exists() or (archive_dir / name).is_symlink():
            buckets["skipped_conflict"].append(name)
        else:
            buckets["eligible"].append(name)

    return ReceiptArchivePlan(**buckets)


def execute_receipt_archive(plan: ReceiptArchivePlan, *, root: Path) -> ReceiptArchiveResult:
    """Relocate each eligible receipt into ``archive/`` atomically (move-not-delete).

    Uses ``os.link`` (which raises ``FileExistsError`` when the destination exists)
    then unlinks the source — an atomic no-clobber move. A same-name file appearing
    in ``archive/`` between planning and execution is therefore NEVER overwritten; it
    is recorded on ``skipped_conflict`` and its source left in place.
    """
    archive_dir = root / _ARCHIVE_NAME
    moved: list[str] = []
    raced: list[str] = []
    for name in plan.eligible:
        source = root / name
        if not source.is_file():
            continue
        archive_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, archive_dir / name)
        except FileExistsError:
            raced.append(name)
            continue
        source.unlink()
        moved.append(name)
    return ReceiptArchiveResult(moved=moved, skipped_conflict=raced, plan=plan)


__all__ = [
    "ReceiptArchivePlan",
    "ReceiptArchiveResult",
    "execute_receipt_archive",
    "plan_receipt_archive",
]
