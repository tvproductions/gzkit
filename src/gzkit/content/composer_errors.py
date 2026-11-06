"""Typed exceptions for :mod:`gzkit.content.composer`.

Held apart from the composer module, which is over the module-size guidance in
``.gzkit/rules/pythonic.md``.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class CompressibleInflationError(ValueError):
    """Byte accounting would report more compressible bytes after compression than before."""

    def __init__(self, bytes_after: int, bytes_before: int) -> None:
        """Name both compressible byte figures."""
        self.bytes_after = bytes_after
        self.bytes_before = bytes_before
        super().__init__(
            f"compressible_bytes_after ({bytes_after}) exceeds "
            f"compressible_bytes_before ({bytes_before}). Compression "
            "cannot add compressible bytes, and an inflated figure is a witness that "
            "cannot fail (ADR-0.35.0 REQ-0.35.0-05-07). Fix the attribution passed to "
            "_byte_evidence -- attributed_compressible for the generated path, or the "
            "candidate text itself for the presence-attribution path -- so it names "
            "only entries that are true members of the corpus's effective compressible "
            "set; never clamp or emit the inflated number."
        )


class CorpusStoreMissingError(FileNotFoundError):
    """No corpus store exists for the surface being composed."""

    def __init__(self, surface: str, store_path: Path) -> None:
        """Name the surface and the store path that does not exist."""
        self.surface = surface
        self.store_path = store_path
        super().__init__(
            f"No corpus store for {surface!r} at {store_path.as_posix()}. "
            "Run 'gz content remember' to seed the corpus first."
        )


class UndeclaredContentTypeError(ValueError):
    """The surface declares no owning content type in the vendor manifest."""

    def __init__(self, surface: str, verb: str) -> None:
        """Name the surface and the caller's verb."""
        self.surface = surface
        super().__init__(
            f"No content type declared for surface {surface!r}; declare it in "
            "surface_content_types in data/vendor-manifest.json. "
            f"{verb} under a guessed owner would grade the candidate against "
            "another type's setpoint and invariant floor (GHI #921)."
        )


class UndeclaredConsumerRouteError(ValueError):
    """The surface's content type declares no route to the requested consumer."""

    def __init__(self, surface: str, owner: str, consumer: str, declared_routes: list[str]) -> None:
        """Name the surface, its owner, the consumer and the routes declared."""
        self.surface = surface
        self.owner = owner
        self.consumer = consumer
        self.declared_routes = declared_routes
        super().__init__(
            f"Surface {surface!r} (content type {owner!r}) declares no route to consumer "
            f"{consumer!r}; declared routes are {declared_routes!r}. Declare the route in "
            "content_type_routes (data/vendor-manifest.json) before generating a "
            f"candidate for {consumer!r}."
        )
