"""Typed handoff-document failures (RO-9, TRY003).

``HandoffValidationError`` is the base every handoff failure subclasses; it is
re-exported from :mod:`gzkit.handoff_validation`, its historical home, so
callers keep importing it from there. Each subclass builds its message in
``__init__`` from the failure's variable parts.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import yaml


class HandoffValidationError(Exception):
    """Raised when a handoff document fails validation."""


class FrontmatterOpeningMissingError(HandoffValidationError):
    """The handoff document does not open with a ``---`` frontmatter delimiter."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Missing opening frontmatter delimiter (---)")


class FrontmatterClosingMissingError(HandoffValidationError):
    """The handoff frontmatter has no closing ``---`` delimiter."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Missing closing frontmatter delimiter (---)")


class FrontmatterYamlError(HandoffValidationError):
    """The handoff frontmatter is not valid YAML."""

    def __init__(self, exc: yaml.YAMLError) -> None:
        """Build the message from ``exc``."""
        super().__init__(f"Invalid YAML in frontmatter: {exc}")


class FrontmatterNotMappingError(HandoffValidationError):
    """The handoff frontmatter parses to something other than a mapping."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Frontmatter must be a YAML mapping")


class NoHandoffFoundError(HandoffValidationError):
    """No handoff document exists for the requested scope."""

    def __init__(self, scope: str) -> None:
        """Build the message from ``scope``."""
        self.scope = scope
        super().__init__(f"No handoff found for {scope}")
