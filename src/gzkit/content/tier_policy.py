"""Invariant-tier policy — the 0-Kelvin floor of the compression dial (OBPI-0.0.37-23).

``tier: invariant`` entries MUST appear verbatim in every rendition at every setpoint.
This is the single enforcement surface the composer consumes; no duplicated inline checks.
"""

from __future__ import annotations

from gzkit.content.models import Corpus, CorpusEntry
from gzkit.content.models.corpus import effective_corpus


def invariant_entries(corpus: Corpus) -> list[CorpusEntry]:
    """Return corpus entries whose tier == 'invariant' in the effective (folded) view.

    Routed through :func:`effective_corpus` (OBPI-0.35.0-01 D3), not a flat
    `retired_ids()` scan: `effective_corpus` already drops every row that is
    either not live or is a pure `retires` tombstone (Algebra 8), so no
    additional retirement filter belongs here. Retirement only ever shrinks
    this set relative to the raw log, so a rendition that satisfied the floor
    before a retirement still satisfies it after -- but un-retirement
    (Algebra 6, a later tombstone retiring an earlier one) can GROW it back,
    which the old flat form could never express. Scope that to the FLOOR:
    retiring OR un-retiring an entry still moves the corpus fingerprint, so
    the freshness gate's derivation proof breaks and a recompose IS required
    before the next push. This sentence was lifted into the `gz content
    retire` help, where it read as a claim about the whole operation and told
    operators no recomposition was due (GHI #863).
    """
    return [e for e in effective_corpus(corpus).entries if e.tier == "invariant"]


def assert_invariant_verbatim(corpus: Corpus, rendered_text: str) -> None:
    """Raise ValueError when any invariant entry's text is absent or altered in rendered_text.

    Returns cleanly when all invariant-tier entries are present verbatim.
    This is the single enforcement surface; the composer calls this function —
    no duplicated inline check.
    """
    for entry in invariant_entries(corpus):
        if entry.text not in rendered_text:
            raise ValueError(
                f"Invariant-floor violation: entry {entry.id!r} text not found verbatim "
                "in rendered text. Invariant-tier entries MUST appear unchanged at every "
                f"setpoint. Entry text (first 80 chars): {entry.text[:80]!r}"
            )
