"""The ledger's pointer to an insights-store record (operator ruling 2026-10-18).

An operator ruling recorded with ``gz insights remember`` lived only in the insights
store, outside the ledger. The operator asked "what is the harm that the ledger notes
that an insight was recorded and references it?" and selected "Pointer + 3 fields": one
``insight_recorded`` event per record, naming its ``ts``, a SHA-256 of its line (so a
later hand edit shows as a mismatch), whose words it carries, and an optional
``supersedes`` reference to an earlier record. The store stays the store.
"""

import hashlib
import json
from pathlib import Path
from typing import Literal

from gzkit.ledger import Ledger, LedgerEvent

INSIGHT_RECORDED_EVENT = "insight_recorded"
Source = Literal["operator", "agent"]


def insight_sha256(line: str) -> str:
    """Return the SHA-256 hex digest of one serialized insights-store line."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def insight_lines_by_ts(insights_path: Path) -> dict[str, str]:
    """Map each record's ``ts`` to its serialized line; unreadable lines are skipped."""
    try:
        text = insights_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    lines: dict[str, str] = {}
    for raw in text.splitlines():
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("ts"), str):
            lines[payload["ts"]] = raw
    return lines


def book_insight_recorded(
    ledger_path: Path, line: str, *, source: Source, supersedes: str | None = None
) -> None:
    """Append the ``insight_recorded`` pointer for the record serialized as ``line``."""
    ts = json.loads(line)["ts"]
    extra: dict[str, str] = {
        "insight_ts": ts,
        "insight_sha256": insight_sha256(line),
        "source": source,
    }
    if supersedes is not None:
        extra["supersedes"] = supersedes
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    Ledger(ledger_path).append(LedgerEvent(event=INSIGHT_RECORDED_EVENT, id=ts, extra=extra))
