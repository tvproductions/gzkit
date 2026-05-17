"""Content-model schema-migration registry — ADR-0.0.34 § Decision item #7."""

from gzkit.content.migration.registry import MIGRATIONS, MigrationError, apply_migrations

__all__ = ["MIGRATIONS", "MigrationError", "apply_migrations"]
