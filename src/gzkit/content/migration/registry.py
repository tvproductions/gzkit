"""Schema-migration registry for content models — ADR-0.0.34 § Decision item #7.

Each registered migration is a pure callable mapping a valid v_n model
to a valid v_{n+1} model of the same content type. The dispatcher
applies registered migrations in sequence; gaps fail-closed with
MigrationError. We NEVER guess a migration and NEVER silently drop fields.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gzkit.content.models.base import BaseContentModel


class MigrationError(ValueError):
    """Raised when no registered migration covers the requested version path."""


class UnsupportedSchemaVersionError(MigrationError):
    """The source schema_version is newer than the current model's."""

    def __init__(self, source_version: int, target_version: int, content_type: str) -> None:
        """Name the content type and both versions."""
        self.source_version = source_version
        self.target_version = target_version
        self.content_type = content_type
        super().__init__(
            f"Unsupported schema_version {source_version} for {content_type!r}; "
            f"current model is at schema_version {target_version}. "
            f"NEVER guess a migration when none is registered."
        )


class MigrationGapError(MigrationError):
    """No migration is registered for one step of the version chain."""

    def __init__(self, content_type: str, version: int) -> None:
        """Name the content type and the missing step's source version."""
        self.content_type = content_type
        self.version = version
        super().__init__(
            f"No migration registered for ({content_type!r}, {version}, {version + 1}); "
            f"cannot migrate {content_type!r} from schema_version {version} to {version + 1}."
        )


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
        UnsupportedSchemaVersionError: A ``MigrationError``, if
            source_version > target_version (unknown future version).
        MigrationGapError: A ``MigrationError``, if any (content_type, v, v+1)
            step is unregistered.

    """
    if source_version == target_version:
        return model
    if source_version > target_version:
        raise UnsupportedSchemaVersionError(source_version, target_version, content_type)
    current = model
    for v in range(source_version, target_version):
        key = (content_type, v, v + 1)
        if key not in MIGRATIONS:
            raise MigrationGapError(content_type, v)
        current = MIGRATIONS[key](current)
    return current
