"""Typed exceptions for :mod:`gzkit.content.ownership`.

Held apart from the ownership module, which is over the module-size guidance in
``.gzkit/rules/pythonic.md``; ``gzkit.content.ownership`` re-exports each name.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class OwnershipLoadError(ValueError):
    """Raised when a declaration or its surface fails the closed-enum/coverage cross-check."""


class DeclarationSurfaceMismatchError(OwnershipLoadError):
    """The declaration on disk names a different surface than the one being recorded."""

    def __init__(self, path: Path, committed_surface: object, requested_surface: str) -> None:
        """Name the file, the surface it carries and the surface requested."""
        self.path = path
        self.committed_surface = committed_surface
        self.requested_surface = requested_surface
        super().__init__(
            f"What failed: the declaration at {path} names surface "
            f"{committed_surface!r}, but the recording was requested "
            f"for surface {requested_surface!r}.\n"
            "Why forbidden: this path rewrites the file it read, so proceeding "
            "would overwrite one control surface's ownership declaration with "
            "another's under a lock taken in the wrong surface's name.\n"
            "Next step: check the declaration handed to `record_unowned_total` "
            f"against the file on disk -- one of the two is for the wrong "
            f"surface, or {path.name} was written by hand."
        )
