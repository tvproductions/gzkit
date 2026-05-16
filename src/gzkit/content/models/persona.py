"""Persona content model — target .gzkit/personas/<slug>.md surfaces."""

import re

from pydantic import Field, field_validator

from .base import BaseContentModel

_SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class Persona(BaseContentModel):
    """Per-turn surface content for a single persona definition."""

    slug: str
    role: str
    traits: list[str] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def _validate_slug(cls, v: str) -> str:
        if not _SLUG_RE.match(v):
            raise ValueError(f"slug must be kebab-case; got {v!r}")
        return v
