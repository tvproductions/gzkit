"""Base class for content models."""

from pydantic import BaseModel, ConfigDict


class BaseContentModel(BaseModel):
    """Frozen Pydantic base for all per-turn surface content models.

    All subclasses inherit frozen=True (immutable) and extra="forbid"
    (strict schema). See ADR-0.0.34 § Decision item #1.

    schema_version (ADR-0.0.34 § Decision item #7 / OBPI-0.0.34-07):
        Integer schema version stamped on every content model. Bumped only
        when the rendered shape or field semantics change. Auto-migrated on
        parse via gzkit.content.migration.registry.apply_migrations when the
        source surface declares an older version than the current model.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = 1
