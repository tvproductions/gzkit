"""Committed-rendition store — deterministic playback layer (ADR-0.0.37, OBPI-0.0.37-22).

The rendition store owns ``.gzkit/renditions/<surface>/<consumer>.md``: one
durable artifact per *(surface × consumer)* pair. It is the seam between the
authoring-time compression composer (OBPI-21, non-deterministic) and the
deterministic render path: once committed, the rendition is replayed verbatim
to the rendered surface — no LLM, no network, no template substitution.

The sole mutations are commit (``save_rendition``) and load (``load_rendition``).
``load_rendition`` is fail-closed: a missing artifact raises ``FileNotFoundError``
so callers cannot silently proceed on stale or absent state.
"""

from __future__ import annotations

from pathlib import Path


def rendition_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the artifact path for *(surface, consumer)* under ``<root>/.gzkit/renditions/``.

    Layout: ``<root>/.gzkit/renditions/<surface>/<consumer>.md``
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.md"


def rendition_exists(root: Path, surface: str, consumer: str) -> bool:
    """Return ``True`` when a committed rendition artifact exists for *(surface, consumer)*."""
    return rendition_path(root, surface, consumer).exists()


def load_rendition(root: Path, surface: str, consumer: str) -> bytes:
    """Load the committed rendition for *(surface, consumer)* and return its bytes.

    Fail-closed: raises ``FileNotFoundError`` when the artifact is absent.
    The same committed artifact always produces the same bytes (deterministic).
    """
    path = rendition_path(root, surface, consumer)
    if not path.exists():
        raise FileNotFoundError(
            f"No committed rendition for ({surface!r}, {consumer!r}) at {path}. "
            f"Run `gz content compose {surface}` to compose and commit a rendition."
        )
    return path.read_bytes()


def save_rendition(root: Path, surface: str, consumer: str, content: bytes) -> None:
    """Commit *content* as the durable rendition for *(surface, consumer)*.

    Creates ``.gzkit/renditions/<surface>/`` on first use. Overwrites any prior
    committed rendition (recompose flow).
    """
    path = rendition_path(root, surface, consumer)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
