"""Shared compositional primitive — a single bulleted item."""

from typing import Literal

from pydantic import Field

from .base import BaseContentModel

_Classification = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]


class Bullet(BaseContentModel):
    """A single bullet (used inside Rule.body, Handoff.open_items, etc.).

    The 0-Kelvin floor (invariants that render at every temperature) now lives
    in the corpus ``tier: invariant`` designation (OBPI-0.0.37-23), not in a
    per-``Bullet`` density dial. The retired ``density_min`` field and its
    ``_enforce_judgment_floor`` validator were proven inert (OBPI-0.0.37-27):
    ``render(lite) == render(medium) == render(heavy)`` byte-for-byte.
    """

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
