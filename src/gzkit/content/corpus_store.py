"""Append-only per-surface corpus persistence (ADR-0.0.37 § Re-Alignment, OBPI-19).

The corpus store is the on-disk home of the append-only source-of-truth corpus
(``.gzkit/corpus/<surface>.jsonl``). It consumes the OBPI-18 ``Corpus``/``CorpusEntry``
model read-only — the store layer owns *where* entries live and the append-only I/O
discipline, never the entry shape or validation rules (those belong to the model).

The sole mutation is append: load the existing corpus, ``Corpus.append`` a new entry
(which returns a new immutable corpus), and rewrite the JSONL file. No rendered surface
is ever touched here — capture writes the source of truth; deterministic playback
(OBPI-22) remains the sole writer of rendered surfaces.

That rewrite-the-whole-file shape is why this module owns three disciplines rather than
none — a store with no delete path cannot recover from a bad write, so every failure
mode of read-modify-write had to be closed at once (GHI #875, #880, #881):

* **Exclusion.** The load-append-commit sequence runs under ``exclusive_file_lock``
  (``gzkit.file_lock``, the repository's one advisory-lock primitive), so two writers
  cannot both compute their new corpus from the same pre-write snapshot and have the
  later one silently erase the earlier one's row. The primitive is shared with the
  section-ownership declaration store and belongs to neither (GHI #945).
* **Validation before persistence.** ``Corpus.loads`` validates the tombstone algebra
  and ``Corpus.append`` does not, so the write boundary asserts it explicitly. Without
  that, the store could be left holding bytes its own reader refuses.
* **Atomic commit.** The new content is staged beside the target, fsynced, and moved
  into place with a single ``Path.replace``. A failed append leaves the prior corpus
  byte-identical rather than truncated.

Validating INSIDE the lock is load-bearing beyond GHI #875's own scope: it is what
closes the double-retire race in ``content retire``, whose two guards read a snapshot
taken before ``append_entry`` re-reads the file. Two processes retiring the same live
entry both pass those caller-side guards, and Algebra 7 (at most one LIVE tombstone per
target) is what then refuses the second one.
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

from gzkit.content.models.corpus import Corpus, CorpusEntry, validate_tombstone_algebra
from gzkit.file_lock import exclusive_file_lock


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

    The three lines inside the ``with`` are the module docstring's three disciplines,
    and their ORDER is the contract: load and validate under the same lock the commit
    holds, so no writer can validate against a corpus another writer is replacing.
    Raises ``ValueError`` if the resulting corpus would break the tombstone algebra and
    ``OSError`` if the commit fails; in both cases the store is left byte-identical.
    """
    path = corpus_path(root, surface)
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(path):
        updated = load_corpus(root, surface).append(entry)
        validate_tombstone_algebra(updated.entries)
        _commit_atomically(path, updated.dumps() + "\n")
    return updated


def _commit_atomically(path: Path, text: str) -> None:
    """Replace *path*'s contents with *text* in one atomic step, or not at all.

    ``Path.write_text`` opens with ``mode='w'`` — it truncates before it writes, so an
    interrupted or disk-full write leaves the target destroyed. On an append-only store
    with no delete path that is worse than the refused operation: canon is lost and the
    caller is told nothing was written (GHI #881).

    Staging lives in the TARGET's directory so the replace is same-filesystem, and the
    name is unique by construction rather than derived from the pid: a pid-named staging
    file is shared by every THREAD of one process, and two threads racing on it made one
    writer replace the file the other was still holding open. ``fsync`` before the
    replace is what makes the durability claim real rather than buffered.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        staging = Path(handle.name)
        try:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        except OSError:
            with contextlib.suppress(OSError):
                staging.unlink()
            raise
    try:
        staging.replace(path)
    except OSError:
        with contextlib.suppress(OSError):
            staging.unlink()
        raise
