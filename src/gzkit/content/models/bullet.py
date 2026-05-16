"""Shared compositional primitive — a single bulleted item."""

from .base import BaseContentModel


class Bullet(BaseContentModel):
    """A single bullet (used inside Rule.body, Handoff.open_items, etc.)."""

    text: str
    indent: int = 0
