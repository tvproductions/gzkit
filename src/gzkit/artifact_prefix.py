"""One rule for what a short-form artifact id names in the ledger graph (GHI #1162).

An OBPI id embeds its parent ADR's semver. Pool demotion parks the old OBPIs and
releases the semver, and a rescope withdraws a phantom OBPI; the ledger is
append-only, so both keep their graph keys forever. A reused semver then leaves a
short id such as ``OBPI-0.35.0-09`` prefixing a parked or withdrawn sibling as
well as the live OBPI.

Two resolvers read short ids: ``gz obpi status`` through
``gzkit.commands.common._prefix_match_candidates``, and handoff citations through
``gzkit.commands.reference_checker._unique_prefix_entry``. They disagreed: the
first dropped phantoms by brief presence on disk (GHI #666), the second dropped
nothing, so the same id resolved in one and was ``unknown`` in the other. Both
now take their candidates from :func:`active_prefix_matches`.

The signal is Layer 2 — the graph's ``parked`` and ``withdrawn`` fields — because
the citation resolver reads only the ledger. Measured 2026-10-02 over the 90
short OBPI ids with more than one graph key, this rule and the brief-on-disk rule
select the same candidates for all 90.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

__all__ = ["active_prefix_matches"]


def _inactive(info: Mapping[str, Any]) -> bool:
    return bool(info.get("parked") or info.get("withdrawn"))


def active_prefix_matches(
    graph: Mapping[str, Mapping[str, Any]],
    identifier: str,
    *,
    artifact_type: str | None = None,
) -> list[str]:
    """Return the graph keys *identifier* prefixes, inactive siblings dropped.

    The match is against ``<identifier>-``, so ``OBPI-0.1.0-1`` never names
    ``OBPI-0.1.0-10-…``. Parked and withdrawn keys are dropped only when at least
    one active key remains: an id whose every candidate is inactive returns them
    all, so a caller still sees the ambiguity instead of a silent empty answer.
    Callers decide what more than one survivor means; GHI #826 rules that it names
    none of them.
    """
    prefix = f"{identifier}-"
    hits = [
        key
        for key, info in graph.items()
        if key.startswith(prefix) and (artifact_type is None or info.get("type") == artifact_type)
    ]
    active = [key for key in hits if not _inactive(graph[key])]
    return active or hits
