"""Append-only store for the settled-ruling corpus (GHI #838).

Rulings used to be transported by COPYING PROSE: ``_carried_settled`` read its
entries out of the predecessor's rendered body, so every session re-embedded the
whole corpus as text purely to hand it to the next one. Measured on
`20260822T132232Z`, that was 98,247 of 107,480 bytes — 91.4% of the document —
and seven authored handoffs over two days spent 687,729 bytes shipping a corpus
that is conceptually one list.

This module separates the STORE from the TRANSPORT. Rulings live here, in one
append-only JSONL; a handoff carries a count and a pointer. The retention
question GHI #838 poses — *should a booked ruling ever stop carrying forward* —
is answered NO and left answered: nothing retires, nothing is dropped, and
:func:`ruling_key` is inherited verbatim rather than widened. Widening it is the
fix GHI #838 explicitly rules out, because collapsing two genuinely distinct
rulings drops a booked operator ruling silently, which is the worse of the two
failure directions.

It also deletes a failure class instead of defending against it.
``handoff_api._ruling_source`` exists only because the corpus travels THROUGH
documents, one of which — the machine-written floor bookmark — carries none by
construction and so acted as a sink (453 rulings to 0, repaired in `02ca03ee`).
A store cannot be sunk by an empty document in the chain.

What this does NOT fix is identity. GHI #838's 3x example — one decision
re-derived by three sessions in three phrasings — needs the typed ``ruling``
ledger event the campaign's Movement D names. This store is the surface that
event later replaces, and the place ids attach without touching the handoff
format a second time.

Discipline: stdlib only. NO LLM, NO network.

@covers GHI #838
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

__all__ = [
    "RULINGS_FILENAME",
    "dedup_rulings",
    "read_rulings",
    "record_rulings",
    "ruling_key",
    "rulings_store_path",
]

#: The corpus lives beside the handoffs it serves, so a clone that carries the
#: handoff directory carries the rulings too. One file, never rotated: the
#: retention answer is "nothing retires", and a rotated log would quietly
#: re-introduce the question through the back door.
RULINGS_FILENAME = "rulings.jsonl"

# Quote glyphs an author may pick between without changing what a ruling says.
# Straight and curly, single and double, all fold to one sentinel for comparison.
_QUOTE_GLYPHS = str.maketrans(dict.fromkeys("'‘’“”", '"'))


def rulings_store_path(base_path: Path) -> Path:
    """Return the corpus path for a project root."""
    return base_path / ".gzkit" / "handoffs" / RULINGS_FILENAME


def ruling_key(entry: str) -> str:
    """Return the comparison key for a settled ruling.

    Two entries are the SAME ruling when they differ only in characters that
    carry no meaning: which quote glyph the author reached for, and how the text
    happened to wrap. Observed on `20260725T085656Z`, where the #580 reframe
    ruling landed twice, byte-identical but for ``'...'`` versus ``"..."`` around
    the operator's verbatim words.

    Normalization stays deliberately narrow because the two failure directions
    are not symmetric. A duplicate is visible and harmless; collapsing two
    genuinely distinct rulings DROPS a booked operator ruling silently, which is
    precisely the decay this channel exists to stop. So this folds quoting,
    whitespace, and case — and nothing that could distinguish one ruling from
    another.

    Moved here from ``handoff_api`` unchanged when the corpus moved out of the
    documents (GHI #838). The storage layer owns identity because it is the layer
    that must not write the same ruling twice; widening the key to shrink the
    corpus is the fix GHI #838 rejects on the asymmetry above.
    """
    return " ".join(entry.translate(_QUOTE_GLYPHS).casefold().split())


def dedup_rulings(entries: list[str]) -> list[str]:
    """De-duplicate settled rulings on :func:`ruling_key`, first-seen text kept.

    Shared by composition and storage on purpose: a ruling normalized on one path
    and compared exactly on the other would still multiply, which is the defect
    wearing a different hat.
    """
    seen: set[str] = set()
    composed: list[str] = []
    for entry in entries:
        key = ruling_key(entry)
        if key in seen:
            continue
        seen.add(key)
        composed.append(entry)
    return composed


def read_rulings(base_path: Path) -> list[str]:
    """Return every booked ruling in the order it was booked.

    A missing store reads EMPTY rather than raising: a project that has never
    booked a ruling and a project whose store was not yet created are the same
    state, and an exception here would fail handoff authoring closed over an
    absence that is not an error.

    A malformed line is skipped rather than aborting the read. The corpus is the
    only copy once the documents stop carrying it, so one bad line must never
    make the other several hundred unreadable.
    """
    store = rulings_store_path(base_path)
    try:
        raw = store.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    entries: list[str] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = record.get("text") if isinstance(record, dict) else None
        if isinstance(text, str) and text.strip():
            entries.append(text.strip())
    return dedup_rulings(entries)


def record_rulings(entries: list[str], *, base_path: Path, source: str) -> list[str]:
    """Append rulings not already booked and return the full corpus.

    Idempotent on :func:`ruling_key`: the composer runs on every authoring pass
    and hands over the whole carried set, so a store that appended
    unconditionally would reproduce the exact multiplication it exists to end.

    *source* names the handoff that booked the entry. It is provenance, not
    identity — a ruling re-stated by a later session keeps the source that first
    booked it, which is what makes the log answer "when did this become settled".

    Written before the handoff document, deliberately. If authoring then fails
    validation the store holds rulings no document yet references, which is
    recoverable and harmless; the reverse order would let a document promise a
    corpus the store never received, and that loses a booked ruling. Same
    asymmetry that keeps :func:`ruling_key` narrow.
    """
    known = {ruling_key(entry) for entry in read_rulings(base_path)}
    fresh = [entry for entry in dedup_rulings(entries) if ruling_key(entry) not in known]
    if fresh:
        store = rulings_store_path(base_path)
        store.parent.mkdir(parents=True, exist_ok=True)
        booked = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        lines = "".join(
            json.dumps({"ts": booked, "source": source, "text": entry}, ensure_ascii=False) + "\n"
            for entry in fresh
        )
        with store.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(lines)
    return read_rulings(base_path)
