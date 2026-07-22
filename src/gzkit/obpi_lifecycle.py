"""OBPI lifecycle derivation over ledger events (GHI #584).

Single definition of what it means for an OBPI to be *live*, *terminal*, or
*parked* under a parent ADR. Demotion, promotion, the orphan backfill, and
``gz validate --obpi-lifecycle-coherence`` all read these functions rather than
each re-deriving the predicate — the four-copies-of-the-instance shape is how
the GHI #520 demotion came to transact over ADR nodes but not their children.

Pure stdlib over already-parsed event dicts: no ledger IO, no adapters, so the
predicate is testable without a project tree (hexagonal-architecture.md § 6).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

#: Events that permanently retire an OBPI. A terminal OBPI is never parked —
#: parking one would double-count it against a disposition it already has.
TERMINAL_EVENTS = frozenset(
    {
        "obpi_withdrawn",
        "obpi_completion_repudiated",
        "obpi_superseded",
        "obpi_abandoned",
    }
)

#: Events proving an OBPI reached genuine completion.
COMPLETION_EVENTS = frozenset({"obpi_receipt_emitted"})

_PARK = "obpi_parked"
_UNPARK = "obpi_unparked"


def _event_type(event: Mapping[str, Any]) -> str:
    return str(event.get("event", ""))


def _field(event: Mapping[str, Any], key: str) -> str:
    """Read an event payload field across both serialization shapes.

    Raw ledger JSONL flattens extras to top level; ``LedgerEvent.model_dump()``
    nests them under ``extra``. Reading only one shape would make this module
    correct for whichever call site was written first and silently wrong for the
    other.
    """
    if key in event:
        return str(event.get(key, ""))
    extra = event.get("extra")
    if isinstance(extra, Mapping):
        return str(extra.get(key, ""))
    return ""


def created_children(events: Iterable[Mapping[str, Any]], parent_id: str) -> list[str]:
    """Return OBPI ids created under ``parent_id``, in ledger order, deduplicated."""
    seen: dict[str, None] = {}
    for event in events:
        if _event_type(event) == "obpi_created" and str(event.get("parent", "")) == parent_id:
            seen.setdefault(str(event.get("id", "")), None)
    seen.pop("", None)
    return list(seen)


def terminal_obpi_ids(events: Iterable[Mapping[str, Any]]) -> set[str]:
    """Return every OBPI id carrying a terminal (permanently retiring) event."""
    return {str(event.get("id", "")) for event in events if _event_type(event) in TERMINAL_EVENTS}


def park_state(events: Iterable[Mapping[str, Any]]) -> dict[str, bool]:
    """Return ``{obpi_id: is_currently_parked}`` by last-park-event-wins.

    Park and unpark compose as forward corrective events — the ledger is
    append-only, so current state is the net of the sequence, never an edit
    (``AGENTS.md`` Never #2).
    """
    state: dict[str, bool] = {}
    for event in events:
        kind = _event_type(event)
        if kind == _PARK:
            state[str(event.get("id", ""))] = True
        elif kind == _UNPARK:
            state[str(event.get("id", ""))] = False
    state.pop("", None)
    return state


def parkable_children(events: Iterable[Mapping[str, Any]], parent_id: str) -> list[str]:
    """Return child OBPIs of ``parent_id`` that a demotion must park.

    Excludes OBPIs already terminal (they hold a disposition) and OBPIs already
    parked (parking twice would inflate the census).
    """
    materialized = list(events)
    terminal = terminal_obpi_ids(materialized)
    parked = park_state(materialized)
    return [
        obpi_id
        for obpi_id in created_children(materialized, parent_id)
        if obpi_id not in terminal and not parked.get(obpi_id, False)
    ]


def parked_children(events: Iterable[Mapping[str, Any]], parent_id: str) -> list[str]:
    """Return child OBPIs of ``parent_id`` currently parked (release set on promotion)."""
    materialized = list(events)
    parked = park_state(materialized)
    return [
        obpi_id
        for obpi_id in created_children(materialized, parent_id)
        if parked.get(obpi_id, False)
    ]


def parked_at(events: Iterable[Mapping[str, Any]], pool_id: str) -> list[tuple[str, str]]:
    """Return ``(obpi_id, original_parent)`` pairs currently parked against ``pool_id``.

    Keyed on the park event's ``parked_to`` rather than on ``parent``: a parked
    OBPI's ``obpi_created`` record names the *pre*-demotion ADR id, so promotion
    cannot find its release set by parent lookup alone. ``parked_to`` is the only
    field that survives the rename.
    """
    materialized = list(events)
    parked = park_state(materialized)
    origins: dict[str, str] = {}
    for event in materialized:
        if _event_type(event) == _PARK and _field(event, "parked_to") == pool_id:
            origins[str(event.get("id", ""))] = str(event.get("parent", ""))
    origins.pop("", None)
    return [(obpi_id, parent) for obpi_id, parent in origins.items() if parked.get(obpi_id, False)]


def orphaned_obpi_ids(events: Iterable[Mapping[str, Any]], live_parent_ids: set[str]) -> list[str]:
    """Return created OBPIs that are neither terminal, parked, completed, nor parented.

    This is the census GHI #584 named: an ``obpi_created`` assertion whose parent
    id no longer resolves to a live ADR and which carries no disposition of any
    kind. Layer-2 asserts the artifact exists; Layer-1 has nothing to show.
    """
    materialized = list(events)
    terminal = terminal_obpi_ids(materialized)
    parked = park_state(materialized)
    completed = {
        str(event.get("id", ""))
        for event in materialized
        if _event_type(event) in COMPLETION_EVENTS
    }
    orphans: dict[str, None] = {}
    for event in materialized:
        if _event_type(event) != "obpi_created":
            continue
        obpi_id = str(event.get("id", ""))
        parent = str(event.get("parent", ""))
        if not obpi_id:
            continue
        if obpi_id in terminal or obpi_id in completed or parked.get(obpi_id, False):
            continue
        if parent in live_parent_ids:
            continue
        orphans.setdefault(obpi_id, None)
    return list(orphans)
