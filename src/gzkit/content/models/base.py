"""Base class for content models."""

from pydantic import BaseModel, ConfigDict


class BaseContentModel(BaseModel):
    """Frozen Pydantic base for all per-turn surface content models.

    All subclasses inherit frozen=True (immutable) and extra="forbid"
    (strict schema). See ADR-0.0.34 § Decision item #1.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
