"""Committed-rendition store — deterministic playback layer (ADR-0.0.37, OBPI-0.0.37-22).

The rendition store owns ``.gzkit/renditions/<surface>/<consumer>.md``: one
durable artifact per *(surface × consumer)* pair. It is the seam between the
authoring-time compression composer (OBPI-21, non-deterministic) and the
deterministic render path: once committed, the rendition is replayed verbatim
to the rendered surface — no LLM, no network, no template substitution.

Two artifacts are committed per pair: the rendition bytes (``save_rendition``)
and a provenance sidecar (``save_fingerprint``) at ``<consumer>.corpus.json``
that freezes the corpus content-fingerprint at commit time. The freshness gate
(OBPI-0.0.37-22 REQ-03) compares that frozen fingerprint against the corpus's
current fingerprint — a CONTENT comparison, not the prior mtime tautology.

``load_rendition`` is fail-closed: a missing artifact raises ``FileNotFoundError``
so callers cannot silently proceed on stale or absent state. ``load_fingerprint``
returns ``None`` when the sidecar is absent — the gate treats a missing sidecar as
drift (the rendition's derivation from the corpus is unproven).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.content.models.corpus import Corpus


class RenditionProvenance(BaseModel):
    """Frozen provenance sidecar — the corpus fingerprint a rendition was committed against.

    Written at the operator-attested commit moment (``gz content commit``); read by the
    freshness gate to prove the committed rendition still derives from the current corpus.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    algorithm: str = Field("sha256", description="Fingerprint hash algorithm.")
    corpus_fingerprint: str = Field(..., description="Hex digest of the corpus at commit time.")
    corpus_entry_count: int = Field(..., description="Entry count of the corpus at commit time.")
    committed_ts: str = Field(..., description="ISO-8601 commit timestamp.")
    attestor: str = Field(..., description="Operator who attested the commit (Gate 5).")
    attestation_text: str = Field(..., description="Operator's verbatim attestation token.")


def corpus_fingerprint(corpus: Corpus) -> str:
    """Return the SHA-256 hex digest of *corpus*'s canonical model serialization.

    Hashing ``Corpus.dumps()`` (the canonical ``model_dump_json`` per entry, joined with
    ``\\n``) — never the on-disk file bytes — makes the digest cross-platform stable:
    a CRLF ``.jsonl`` on Windows and an LF ``.jsonl`` on Linux with identical entries
    produce the identical digest, because ``Corpus.loads`` absorbs the line ending on read.
    """
    return hashlib.sha256(corpus.dumps().encode("utf-8")).hexdigest()


def rendition_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the artifact path for *(surface, consumer)* under ``<root>/.gzkit/renditions/``.

    Layout: ``<root>/.gzkit/renditions/<surface>/<consumer>.md``
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.md"


def fingerprint_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the provenance sidecar path for *(surface, consumer)*.

    Layout: ``<root>/.gzkit/renditions/<surface>/<consumer>.corpus.json`` — the
    ``.corpus.json`` suffix is invisible to the ``*.md`` rendition globs.
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.corpus.json"


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


def save_fingerprint(
    root: Path, surface: str, consumer: str, provenance: RenditionProvenance
) -> None:
    """Commit *provenance* as the corpus-fingerprint sidecar for *(surface, consumer)*."""
    path = fingerprint_path(root, surface, consumer)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(provenance.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_fingerprint(root: Path, surface: str, consumer: str) -> RenditionProvenance | None:
    """Load the provenance sidecar for *(surface, consumer)*, or ``None`` when absent.

    A missing sidecar is NOT an error here: the freshness gate interprets ``None`` as
    drift (the rendition's derivation from the corpus is unproven), with a recompose hint.
    """
    path = fingerprint_path(root, surface, consumer)
    if not path.exists():
        return None
    return RenditionProvenance.model_validate_json(path.read_text(encoding="utf-8"))
