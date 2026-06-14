"""Invariant-tier policy — the 0-Kelvin floor of the compression dial (OBPI-0.0.37-23).

``tier: invariant`` entries MUST appear verbatim in every rendition at every setpoint.
This is the single enforcement surface the composer consumes; no duplicated inline checks.
"""

from __future__ import annotations

from gzkit.content.models import Corpus, CorpusEntry


def invariant_entries(corpus: Corpus) -> list[CorpusEntry]:
    """Return corpus entries whose tier == 'invariant'."""
    return [e for e in corpus.entries if e.tier == "invariant"]


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
