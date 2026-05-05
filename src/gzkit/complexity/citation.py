"""Citation contract for the gzkit complexity-doctrine cluster (ADR-0.0.27).

Downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) cite the
distilled-characteristics document via a canonical tuple
``(distilled_characteristics_path, section_anchor, corpus_revision)`` so that
boundaries remain portable across corpus refresh.  This module exposes the
parser surface OBPI-0.0.27-07's link-integrity validator consumes.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_SUPPORTED_WINDOW: int = 2
"""Default refresh-portability window: revision N is portable when the current
corpus revision is N or N+1.  Revision N becomes non-portable at N+2 or later."""

_CANONICAL_PATTERN = re.compile(
    r"^(?P<path>docs/governance/complexity/[^\s]+\.md)\s+"
    r"§\s+(?P<anchor>[a-z0-9][a-z0-9-]*)\s+"
    r"\(corpus revision\s+(?P<revision>\d+)\)$"
)


class Citation(BaseModel):
    """Canonical citation tuple for distilled-characteristics references."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    distilled_characteristics_path: str = Field(
        pattern=r"^docs/governance/complexity/.+\.md$",
        description="Relative path to the cited distilled-characteristics document.",
    )
    section_anchor: str = Field(
        pattern=r"^[a-z0-9][a-z0-9-]*$",
        description="Slugified anchor identifying the metric section within the document.",
    )
    corpus_revision: int = Field(
        gt=0,
        description="Corpus revision the citation was authored against.",
    )


def parse_citation(text: str) -> Citation:
    """Parse the canonical string form into a ``Citation`` instance.

    Canonical form is::

        docs/governance/complexity/distilled-characteristics-{date}.md
            § {anchor} (corpus revision {N})

    Raises :class:`pydantic.ValidationError` when any of the three fields is
    missing or fails its constraint.
    """

    match = _CANONICAL_PATTERN.match(text.strip())
    if match is None:
        return Citation(
            distilled_characteristics_path="",
            section_anchor="",
            corpus_revision=0,
        )
    return Citation(
        distilled_characteristics_path=match.group("path"),
        section_anchor=match.group("anchor"),
        corpus_revision=int(match.group("revision")),
    )


def is_portable(
    citation: Citation,
    current_revision: int,
    supported_window: int = DEFAULT_SUPPORTED_WINDOW,
) -> bool:
    """Return ``True`` when ``citation`` is portable against ``current_revision``.

    A citation written against revision ``N`` is portable when ``current_revision``
    is in ``[N, N + supported_window - 1]``.  At ``current_revision >= N + supported_window``
    the citation is out of date and the link-integrity validator (OBPI-07) flags
    it for amendment.
    """

    delta = current_revision - citation.corpus_revision
    return 0 <= delta < supported_window
