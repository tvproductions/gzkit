"""Shared compositional primitive — a single bulleted item."""

from typing import Literal

from pydantic import Field, model_validator

from .base import BaseContentModel

_Temperature = Literal["lite", "medium", "heavy"]
_Classification = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]


class Bullet(BaseContentModel):
    """A single bullet (used inside Rule.body, Handoff.open_items, etc.)."""

    text: str
    indent: int = 0
    classification: _Classification | None = Field(
        None, description="Bullet classification for density-aware rendering."
    )
    witness: str | None = Field(
        None, description="Gate command that mechanically enforces this bullet."
    )
    rationale_ref: str | None = Field(
        None, description="Doc pointer to rationale (never rendered inline)."
    )
    density_min: _Temperature | None = Field(
        None, description="Lowest temperature at which this bullet renders."
    )

    @model_validator(mode="after")
    def _enforce_judgment_floor(self) -> "Bullet":
        """Judgment bullets pin to 'lite' — the 0-Kelvin floor (ADR-0.0.37 Decision Extension)."""
        if self.classification == "Judgment":
            if self.density_min is None:
                object.__setattr__(self, "density_min", "lite")
            elif self.density_min != "lite":
                raise ValueError(
                    "Judgment bullets must have density_min='lite' (0-Kelvin floor invariant)"
                )
        return self
