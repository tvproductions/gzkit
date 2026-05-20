"""Pydantic model for `.gzkit/insights/agent-insights.jsonl` records.

GHI #358 locks the read-side schema for the course-correction insights
surface. The file accumulates four trust-bearing record kinds, named by
the `type` field — `defect` observations, `defect-resolution` outcomes,
`improvement` post-correction lessons (Behavior Rule #11), and
`discovery` survey findings (GHI #502) — and was hand-appended without
enforcement until this lock landed; the existing record drift (date-only
timestamps, nested-object evidence, plural `adr_ids` keys, prose
`resolution` field) is preserved via line-keyed waivers in
`gzkit.governance.trust_audits._INSIGHTS_SHAPE_WAIVERS` rather than
rewriting closed-evidence history (trust-doctrine T2).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_ISO8601_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$"
"""ISO8601 with timezone designator (Z or ±HH:MM); date-only is rejected."""

InsightType = Literal["defect", "defect-resolution", "improvement", "discovery"]


class InsightRecord(BaseModel):
    """One line of `.gzkit/insights/agent-insights.jsonl`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ts: str = Field(
        ...,
        pattern=_ISO8601_PATTERN,
        description="ISO8601 with timezone (Z or +HH:MM); date-only is forbidden",
    )
    type: InsightType = Field(
        ..., description="Record kind: defect | defect-resolution | improvement | discovery"
    )
    scope: str = Field(..., min_length=1, description="Surface or skill the record names")
    summary: str = Field(..., min_length=1, description="One-sentence record body")

    id: str | None = Field(default=None, description="Optional record slug")
    adr_id: str | None = Field(default=None, description="ADR identifier when in scope")
    obpi_id: str | None = Field(default=None, description="OBPI identifier when in scope")
    evidence: list[str] | None = Field(
        default=None,
        description="Commands or paths witnessing the record (list of str only)",
    )
    next_action: str | None = Field(
        default=None, description="What changes structurally to prevent recurrence"
    )
    verification: list[str] | None = Field(
        default=None, description="Commands run to verify a defect-resolution"
    )
    result: str | None = Field(default=None, description="Resolution outcome string")
