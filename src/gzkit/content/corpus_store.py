"""Append-only per-surface corpus persistence (ADR-0.0.37 § Re-Alignment, OBPI-19).

The corpus store is the on-disk home of the append-only source-of-truth corpus
(``.gzkit/corpus/<surface>.jsonl``). It consumes the OBPI-18 ``Corpus``/``CorpusEntry``
model read-only — the store layer owns *where* entries live and the append-only I/O
discipline, never the entry shape or validation rules (those belong to the model).

The sole mutation is append: load the existing corpus, ``Corpus.append`` a new entry
(which returns a new immutable corpus), and rewrite the JSONL file. No rendered surface
is ever touched here — capture writes the source of truth; deterministic playback
(OBPI-22) remains the sole writer of rendered surfaces.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.content.models.corpus import Corpus, CorpusEntry


def corpus_path(root: Path, surface: str) -> Path:
    """Return the JSONL store path for *surface* (``<root>/.gzkit/corpus/<surface>.jsonl``)."""
    return root / ".gzkit" / "corpus" / f"{surface}.jsonl"


def load_corpus(root: Path, surface: str) -> Corpus:
    """Load the corpus for *surface*, or an empty ``Corpus`` when no store file exists yet."""
    path = corpus_path(root, surface)
    if not path.exists():
        return Corpus()
    return Corpus.loads(path.read_text(encoding="utf-8"))


def append_entry(root: Path, surface: str, entry: CorpusEntry) -> Corpus:
    """Append *entry* to *surface*'s corpus store and return the new corpus.

    Creates the ``.gzkit/corpus/`` directory and the per-surface file on first use.
    Existing entries are preserved (append-only); the file is rewritten as JSONL with
    a trailing newline.
    """
    path = corpus_path(root, surface)
    updated = load_corpus(root, surface).append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated.dumps() + "\n", encoding="utf-8")
    return updated
