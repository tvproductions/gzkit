"""Chore content model — target .gzkit/chores/<slug> surfaces."""

import re

from pydantic import Field, field_validator

from .base import BaseContentModel
from .bullet import Bullet

_SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class Chore(BaseContentModel):
    """Per-turn surface content for a single chore."""

    slug: str
    title: str
    cadence: str = "on-demand"
    steps: list[Bullet] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def _validate_slug(cls, v: str) -> str:
        if not _SLUG_RE.match(v):
            raise ValueError(f"slug must be kebab-case; got {v!r}")
        return v
