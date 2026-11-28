"""The position a resume opens with, computed from the record, never recalled.

`docs/design/briefs/SPEC-session-handoff-picture.md` (accepted 2026-10-31) gives
the operator three levels of picture written by the handoff's author. Built
2026-11-28 on the operator's word, verbatim: *"build it now so every resume shows
the position - this should cut down on vibe coding."*, choosing *"Both
(Recommended)"*: the author's picture sits beside facts it cannot change. This
module supplies the facts. Each names where it was read, so a number the agent
repeats can be checked against its source.

What it reads, and only this:

- the hangar marker, through `gzkit.mx.marker.condition`, for whether the vessel
  is out of service and since when;
- the list of discrepancies in the ledger, through
  `gzkit.mx.record_rows.open_discrepancies`;
- the open contract's own § List of discrepancies, which holds the lines recorded
  before RP-12 O9 carries them into the ledger, counted by their first line's
  grammar: ``- `open` `` opens a line, and ``**blocks return to service**`` right
  after it grades it;
- the contract's § Passage log, for its latest dated row;
- commit subjects the caller passes, so git stays at the caller's boundary.

The states of the repair orders are not computed: today they live only in prose,
so they stay in the author's picture until a record carries them.
"""

import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from gzkit.ledger import Ledger
from gzkit.mx.contract import contract_section
from gzkit.mx.marker import condition
from gzkit.mx.record_rows import DiscrepancyError, open_discrepancies

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

_DISCREPANCIES_HEADING = "## List of discrepancies"
_PASSAGE_LOG_HEADING = "## Passage log"
_OPEN_LINE = re.compile(r"^- `open` ", re.MULTILINE)
_BLOCKING_LINE = re.compile(r"^- `open` \*\*blocks return to service\*\*", re.MULTILINE)
_LOG_ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|", re.MULTILINE)
_ORDER_SUBJECT = re.compile(r"\b(?:RP|RO)-\d+\b|\bdrydock\b", re.IGNORECASE)
_BLOCKING_GRADE = "blocks-return-to-service"


class PositionFact(BaseModel):
    """One computed fact of the position, with where it was read."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str = Field(..., description="What the fact is")
    value: str = Field(..., description="The fact, as read")
    source: str = Field(..., description="Where it was read")


def contract_lines(text: str) -> tuple[int, int]:
    """Count a contract's open discrepancy lines and the open ones that block return.

    Returns:
        (open, blocking) over the contract's § List of discrepancies; (0, 0) without it.

    """
    body = contract_section(text, _DISCREPANCIES_HEADING)
    return len(_OPEN_LINE.findall(body)), len(_BLOCKING_LINE.findall(body))


def last_log_entry(text: str) -> str | None:
    """Return the latest date among a contract's passage-log rows.

    Returns:
        The ISO date of the newest row, or None when the contract has no dated row.

    """
    dates = _LOG_ROW.findall(contract_section(text, _PASSAGE_LOG_HEADING))
    return max(dates) if dates else None


def commit_position(subjects: Sequence[str], *, since: str) -> PositionFact:
    """Count the commits since *since* and those naming a repair order or the drydock.

    Returns:
        The fact, its source naming the window.

    """
    on_orders = sum(1 for subject in subjects if _ORDER_SUBJECT.search(subject))
    return PositionFact(
        label="Commits since this handoff",
        value=f"{on_orders} of {len(subjects)} name a repair order or the drydock",
        source=f"git log --since={since}, subjects matching RP-n, RO-n or drydock",
    )


def _days_since(opened_at: str, now: datetime) -> str:
    try:
        opened = datetime.fromisoformat(opened_at)
    except ValueError:
        return opened_at or "an unrecorded time"
    if opened.tzinfo is None:
        opened = opened.replace(tzinfo=UTC)
    return f"{opened.date().isoformat()} ({(now - opened).days} days)"


def _ledger_lines(project_root: Path) -> PositionFact:
    source = ".gzkit/ledger.jsonl, discrepancy_recorded and discrepancy_cleared"
    try:
        lines = open_discrepancies(Ledger(project_root / ".gzkit" / "ledger.jsonl"))
    except (DiscrepancyError, OSError) as exc:
        return PositionFact(
            label="Ledger discrepancy lines", value=f"unreadable: {exc}", source=source
        )
    blocking = sum(1 for line in lines if line.record.grade == _BLOCKING_GRADE)
    return PositionFact(
        label="Ledger discrepancy lines",
        value=f"{blocking} blocking, {len(lines)} open",
        source=source,
    )


def _contract_facts(project_root: Path, contract: str) -> list[PositionFact]:
    path = project_root / contract
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [
            PositionFact(
                label="Contract", value=f"not found: {contract}", source=".gzkit/mx.json contract"
            )
        ]
    opened, blocking = contract_lines(text)
    facts = [
        PositionFact(
            label="Contract discrepancy lines",
            value=f"{blocking} blocking, {opened} open",
            source=f"{contract} § List of discrepancies, lines recorded before RP-12 O9",
        )
    ]
    last = last_log_entry(text)
    facts.append(
        PositionFact(
            label="Passage log, last entry",
            value=last or "no dated entry",
            source=f"{contract} § Passage log",
        )
    )
    return facts


def drydock_position(project_root: Path, *, now: datetime) -> list[PositionFact]:
    """Return the out-of-service facts: whether, since when, what blocks the return.

    Nothing else is read when the hangar is not open; a missing contract is named,
    never filled in.

    Returns:
        The facts in reading order, each with its source.

    """
    reading = condition(project_root)
    if not reading.on or reading.marker is None:
        return [
            PositionFact(
                label="Out of service",
                value=f"no (the hangar marker reads {reading.cause})",
                source=".gzkit/mx.json, through gzkit.mx.marker.condition",
            )
        ]
    marker = reading.marker
    facts = [
        PositionFact(
            label="Out of service since",
            value=f"{_days_since(marker.opened_at, now)}, at the {marker.level} level",
            source=".gzkit/mx.json opened_at and level",
        ),
        _ledger_lines(project_root),
    ]
    if marker.contract:
        facts.extend(_contract_facts(project_root, marker.contract))
    return facts
