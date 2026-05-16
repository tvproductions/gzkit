"""Handoff content model — target .gzkit/handoffs/*.md surfaces."""

import re

from pydantic import Field, field_validator

from .base import BaseContentModel
from .bullet import Bullet

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class Handoff(BaseContentModel):
    """Per-turn surface content for a single session handoff."""

    session_id: str
    state_summary: str
    open_items: list[Bullet] = Field(default_factory=list)
    resume_point: str = ""

    @field_validator("session_id")
    @classmethod
    def _validate_session_id(cls, v: str) -> str:
        if not _SESSION_ID_RE.match(v):
            raise ValueError(f"session_id must be a non-empty identifier (alnum + -_); got {v!r}")
        return v
