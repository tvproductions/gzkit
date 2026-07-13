"""Mechanical writer for `.gzkit/insights/agent-insights.jsonl` (GHI #575).

The insight-append path was hand-authored: agents wrote lines into the
append-only insights store by hand and drifted from the `InsightRecord`
schema that gates it. This helper closes that gap by *constructing* an
`InsightRecord` first, then serializing it — a missing or malformed
required field (`ts`, `type`, `scope`, `summary`) fails closed at
construction with a `pydantic.ValidationError` rather than reaching disk.

Hexagonal: the target path is a parameter (the external resource), so the
core write logic is exercised against a tempfile with no monkeypatching.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from gzkit.insights.model import InsightRecord, InsightType

DEFAULT_INSIGHTS_PATH = Path(".gzkit") / "insights" / "agent-insights.jsonl"
"""Default append target, relative to the project root."""


def append_insight_record(
    *,
    type: InsightType,
    scope: str,
    summary: str,
    evidence: list[str] | None = None,
    next_action: str | None = None,
    id: str | None = None,
    adr_id: str | None = None,
    obpi_id: str | None = None,
    verification: list[str] | None = None,
    result: str | None = None,
    ts: str | None = None,
    path: Path = DEFAULT_INSIGHTS_PATH,
) -> str:
    """Append one `InsightRecord` line to ``path`` and return the serialized line.

    Construction happens FIRST: a missing or malformed required field raises
    ``pydantic.ValidationError`` before ``path`` is opened, so an invalid record
    never reaches disk. ``ts`` defaults to the current UTC instant in ISO8601
    with a timezone designator (the schema forbids date-only stamps).
    """
    record = InsightRecord(
        ts=ts if ts is not None else datetime.now(UTC).isoformat(),
        type=type,
        scope=scope,
        summary=summary,
        evidence=evidence,
        next_action=next_action,
        id=id,
        adr_id=adr_id,
        obpi_id=obpi_id,
        verification=verification,
        result=result,
    )
    line = record.model_dump_json(exclude_none=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return line
