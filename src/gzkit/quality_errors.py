"""Typed quality-gate failures (RO-9, TRY003).

Kept beside :mod:`gzkit.quality` because that module is over the
authoring-time module size limit (``.gzkit/rules/pythonic.md``).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import yaml


class MkdocsConfigYamlError(ValueError):
    """A mkdocs config file is not valid YAML."""

    def __init__(self, exc: yaml.YAMLError) -> None:
        """Build the message from ``exc``."""
        super().__init__(f"not valid YAML: {exc}")


# A TypeError too: raised when an isinstance check fails (TRY004); ValueError keeps its handlers.
class MkdocsConfigNotMappingError(ValueError, TypeError):
    """A mkdocs config file's top level is not a mapping."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("top level is not a mapping")


class MkdocsInheritCycleError(ValueError):
    """A mkdocs config's ``INHERIT`` chain returns to a file already read."""

    def __init__(self, parent_path: Path) -> None:
        """Build the message from ``parent_path``."""
        self.parent_path = parent_path
        super().__init__(f"INHERIT cycle at {parent_path}")


# A TypeError too: raised when an isinstance check fails (TRY004); ValueError keeps its handlers.
class MkdocsValidationNotMappingError(ValueError, TypeError):
    """A mkdocs config's ``validation`` key is not a mapping."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("validation is not a mapping")
