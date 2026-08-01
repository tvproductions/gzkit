"""Step-4b adversarial-validation trust audit (GHI #676).

Step 4b of the OBPI pipeline is a fail-closed gate: no OBPI reaches attestation
without an independent adversary, prompted to REFUTE, re-deriving the completion
claim. Nothing retained that adversary's verdict. It lived in an agent transcript
or a vendor plugin cache — outside the repo, outside the ledger, outside git — so
a run that skipped Step 4b and a run that was refuted and attested anyway left
indistinguishable durable records.

Two invariants, one scope:

  1. **Ledger coherence** (dated-cutover). Every heavy-lane completion receipt
     emitted on or after ``CUTOVER`` carries a paired ``adversarial_validation``
     event, and a ``refuted`` verdict carries a resolution. Receipts predating the
     cutover are out of scope because the gate did not exist — that is honesty
     about when the gate landed, not a waiver.

  2. **Brief evidence** (shrink-ratchet). Every heavy-lane brief in a terminal
     status carries a ``### Step 4b — Independent Adversarial Validation`` section,
     unless it is named in the pre-cutover grandfather snapshot.

Per ``docs/governance/state-doctrine.md`` the ledger is Layer 2 and the brief is
Layer 1; a gate decision must trace to one of them. A vendor cache is neither.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.validate import ValidationError

if TYPE_CHECKING:
    from collections.abc import Iterator

_LEDGER_REL = ".gzkit/ledger.jsonl"
_GRANDFATHER_REL = "data/adversarial_validation_grandfather.json"
_ADR_ROOT_REL = "docs/design/adr"
_ENTRIES_KEY = "grandfathered_obpis"

# The instant `gz obpi complete` gained the fail-closed Step-4b gate (GHI #676).
# Every heavy completion receipt emitted at or after this moment must carry a
# paired verdict. Earlier receipts are out of scope: the gate did not yet exist,
# and back-dating a verdict onto them would be the fabrication this audit exists
# to prevent. Registered as a `dated-cutover` honesty mechanism.
#
# The precision is load-bearing, not fussiness. OBPI-0.33.0-01 — the very OBPI
# whose lost Codex verdict motivated GHI #676 — emitted its completion receipt at
# 2026-07-09T01:02:00Z, hours before this gate landed the same day. A date-only
# cutover would demand a ledger event that could only be produced by back-dating
# one. Its verdict survives as Layer-1 brief evidence (`### Step 4b`), which is
# what the brief-section half of this audit checks.
CUTOVER = dt.datetime(2026, 7, 9, 9, 0, tzinfo=dt.UTC)

_ERR_TYPE = "adversarial_validation"
_TERMINAL_STATUSES = frozenset({"Completed", "Validated"})

_LANE_RE = re.compile(r"^lane:\s*[\"']?(\w+)", re.MULTILINE)
_STATUS_RE = re.compile(r"^status:\s*[\"']?([\w-]+)", re.MULTILINE)
_STEP_4B_RE = re.compile(r"^###\s+Step 4b\b", re.MULTILINE)


def _iter_ledger(project_root: Path) -> Iterator[dict]:
    """Yield each well-formed ledger event; skip unparseable lines."""
    ledger = project_root / _LEDGER_REL
    try:
        text = ledger.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            yield event


def _receipt_ts(event: dict) -> dt.datetime | None:
    """Return the receipt's UTC-aware timestamp, or None when it is unusable.

    Naive timestamps are read as UTC — the ledger's writers all stamp UTC, and a
    naive value compared against an aware CUTOVER would raise rather than judge.
    """
    raw = event.get("ts")
    if not isinstance(raw, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.UTC)


def _receipt_obpi_id(event: dict) -> str | None:
    """Resolve the OBPI a receipt refers to.

    Completion receipts carry the OBPI slug on ``id`` and leave ``obpi_id`` null
    (observed across all 635 receipts); newer events populate ``obpi_id``. Prefer
    the explicit field and fall back to ``id``.
    """
    for key in ("obpi_id", "id"):
        value = event.get(key)
        if isinstance(value, str) and value.startswith("OBPI-"):
            return value
    return None


def _brief_index(project_root: Path) -> dict[str, tuple[Path, str, str]]:
    """Map OBPI slug -> (brief path, lane, status) from on-disk frontmatter."""
    index: dict[str, tuple[Path, str, str]] = {}
    adr_root = project_root / _ADR_ROOT_REL
    if not adr_root.is_dir():
        return index
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        try:
            head = brief.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        lane_match = _LANE_RE.search(head)
        status_match = _STATUS_RE.search(head)
        lane = lane_match.group(1).lower() if lane_match else ""
        status = status_match.group(1) if status_match else ""
        index[brief.stem] = (brief, lane, status)
    return index


def _load_grandfathered(project_root: Path) -> set[str]:
    """Load the pre-cutover snapshot of briefs exempt from the section check."""
    path = project_root / _GRANDFATHER_REL
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    entries = payload.get(_ENTRIES_KEY) if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return set()
    return {entry for entry in entries if isinstance(entry, str)}


def _collect_verdicts(project_root: Path) -> tuple[dict[str, list[dict]], list[dict]]:
    """Single ledger pass: adversarial verdicts by OBPI, and completion receipts."""
    verdicts: dict[str, list[dict]] = {}
    receipts: list[dict] = []
    for event in _iter_ledger(project_root):
        name = event.get("event")
        if name == "adversarial_validation":
            obpi_id = event.get("obpi_id")
            if isinstance(obpi_id, str):
                verdicts.setdefault(obpi_id, []).append(event)
        elif name == "obpi_receipt_emitted" and event.get("receipt_event") == "completed":
            receipts.append(event)
    return verdicts, receipts


def _unresolved_refutation(events: list[dict]) -> bool:
    """Return True when the latest verdict is ``refuted`` with no recorded resolution."""
    latest = events[-1]
    return latest.get("verdict") == "refuted" and not latest.get("resolution")


def _audit_ledger_coherence(
    project_root: Path,
    index: dict[str, tuple[Path, str, str]],
) -> list[ValidationError]:
    """Post-cutover heavy completion receipts must carry a paired verdict."""
    errors: list[ValidationError] = []
    verdicts, receipts = _collect_verdicts(project_root)
    for receipt in receipts:
        receipt_ts = _receipt_ts(receipt)
        if receipt_ts is None or receipt_ts < CUTOVER:
            continue
        obpi_id = _receipt_obpi_id(receipt)
        if obpi_id is None:
            continue
        entry = index.get(obpi_id)
        if entry is None or entry[1] != "heavy":
            continue
        events = verdicts.get(obpi_id)
        if not events:
            errors.append(
                ValidationError(
                    type=_ERR_TYPE,
                    artifact=obpi_id,
                    message=(
                        f"Heavy-lane completion receipt for '{obpi_id}' "
                        f"({receipt_ts.isoformat()}) carries no paired "
                        "'adversarial_validation' ledger event. Step 4b's verdict is "
                        "gate-bearing evidence and must outlive the session that "
                        "produced it (GHI #643/#676). Recovery: re-run `gz obpi "
                        "complete` with --adversary-verdict and --adversary, or "
                        "`gz obpi repudiate` the completion if Step 4b never ran."
                    ),
                )
            )
        elif _unresolved_refutation(events):
            errors.append(
                ValidationError(
                    type=_ERR_TYPE,
                    artifact=obpi_id,
                    message=(
                        f"The adversary refuted '{obpi_id}' and the completion receipt "
                        "was emitted with no resolution recorded. A known refutation "
                        "must never be handed to the operator dressed as clean. "
                        "Recovery: fix the refuted claim, re-verify against the "
                        "adversary's own check, and re-emit the verdict with "
                        "--adversary-resolution."
                    ),
                )
            )
    return errors


def _audit_brief_sections(
    project_root: Path,
    index: dict[str, tuple[Path, str, str]],
) -> list[ValidationError]:
    """Terminal heavy-lane briefs must carry the Step-4b evidence section."""
    grandfathered = _load_grandfathered(project_root)
    errors: list[ValidationError] = []
    for obpi_id, (path, lane, status) in sorted(index.items()):
        if lane != "heavy" or status not in _TERMINAL_STATUSES:
            continue
        if obpi_id in grandfathered:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _STEP_4B_RE.search(text):
            continue
        errors.append(
            ValidationError(
                type=_ERR_TYPE,
                artifact=path.relative_to(project_root).as_posix(),
                message=(
                    f"Heavy-lane brief '{obpi_id}' is {status} but carries no "
                    "'### Step 4b — Independent Adversarial Validation' evidence "
                    "section. The adversary's verdict, the claim it broke, and how "
                    "that was resolved must be readable from the brief itself. "
                    "Recovery: add the section citing the verdict and the adversary "
                    "identity. The grandfather snapshot is closed to new entries."
                ),
            )
        )
    return errors


def audit_adversarial_validation(project_root: Path) -> list[ValidationError]:
    """Assert Step-4b verdicts are durably captured in the ledger and the brief."""
    index = _brief_index(project_root)
    return _audit_ledger_coherence(project_root, index) + _audit_brief_sections(project_root, index)
