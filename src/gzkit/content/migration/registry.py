"""Schema-migration registry for content models — ADR-0.0.34 § Decision item #7.

Each registered migration is a pure callable mapping a valid v_n model
to a valid v_{n+1} model of the same content type. The dispatcher
applies registered migrations in sequence; gaps fail-closed with
MigrationError. We NEVER guess a migration and NEVER silently drop fields.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gzkit.content.models.base import BaseContentModel


class MigrationError(ValueError):
    """Raised when no registered migration covers the requested version path."""


MIGRATIONS: dict[tuple[str, int, int], Callable[[BaseContentModel], BaseContentModel]] = {}


def apply_migrations(
    model: BaseContentModel,
    content_type: str,
    *,
    source_version: int,
    target_version: int,
) -> BaseContentModel:
    """Apply registered migrations from source_version to target_version.

    Args:
        model: A v_{source_version} instance of the named content_type.
        content_type: The content type name (e.g. "Rule").
        source_version: Schema version declared by the source surface.
        target_version: Current model's schema_version default.

    Returns:
        A v_{target_version} instance produced by chaining registered
        migrations (content_type, v, v+1) for v in [source, target).

    Raises:
        MigrationError: if source_version > target_version (unknown future
            version) or if any (content_type, v, v+1) step is unregistered.

    """
    if source_version == target_version:
        return model
    if source_version > target_version:
        raise MigrationError(
            f"Unsupported schema_version {source_version} for {content_type!r}; "
            f"current model is at schema_version {target_version}. "
            f"NEVER guess a migration when none is registered."
        )
    current = model
    for v in range(source_version, target_version):
        key = (content_type, v, v + 1)
        if key not in MIGRATIONS:
            raise MigrationError(
                f"No migration registered for ({content_type!r}, {v}, {v + 1}); "
                f"cannot migrate {content_type!r} from schema_version {v} to {v + 1}."
            )
        current = MIGRATIONS[key](current)
    return current
