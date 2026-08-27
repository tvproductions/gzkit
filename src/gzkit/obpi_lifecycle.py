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

_BLOCK = "obpi_blocked_on_operator"
_UNBLOCK = "obpi_unblocked"


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


def operator_block_state(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, str]]:
    """Return ``{obpi_id: {reason, next_operator_action}}`` for OBPIs awaiting a human.

    Block and unblock compose as forward corrective events by
    last-event-wins, the same way :func:`park_state` composes — the ledger is
    append-only, so current state is the net of the sequence, never an edit
    (``AGENTS.md`` Never #2). An unblock for an OBPI that was never blocked is
    inert rather than synthesizing a record.

    **Why this lives in Layer 2 rather than the pipeline marker (GHI #887).**
    The marker already carries ``required_human_action`` and ``next_command``
    keys, and the cheaper repair would have been to populate them and gate stage
    advance on them. ``ADR-0.0.9`` Rule 5 forbids it in as many words: *"Layer 3
    artifacts cannot block gates. Only L1 (canon) and L2 (events) can be gate
    evidence. L3 can surface warnings but never fail-close a gate."* Markers are
    named Layer 3 in that ADR's own table, so a guard reading one would be a gate
    decision tracing to Layer 3 — the defect GHI #886 files against Stage-2
    dispatch credit, reproduced on a second fact.

    ``obpi_parked`` could not carry this. Its ``parked_to`` field is required
    non-empty and names the pool id the parent ADR became, so the vocabulary
    already spends that term on a different subject: a parked OBPI is fine and
    its parent left, whereas a blocked one is fine, its parent is live, and a
    human owes it a decision.
    """
    state: dict[str, dict[str, str]] = {}
    for event in events:
        kind = _event_type(event)
        obpi_id = str(event.get("id", ""))
        if not obpi_id:
            continue
        if kind == _BLOCK:
            state[obpi_id] = {
                "reason": _field(event, "reason"),
                "next_operator_action": _field(event, "next_operator_action"),
            }
        elif kind == _UNBLOCK:
            state.pop(obpi_id, None)
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


def fold_renames(pairs: Iterable[tuple[str, str]]) -> dict[str, str]:
    """Fold ``(old_id, new_id)`` renames temporally into ``id -> current id``.

    The single definition of *where is this artifact now*. Callers supply their
    own event-shape extraction and get identical semantics, so the two readers
    of this question cannot drift apart again.

    For each rename ``A -> B`` in temporal order: repoint every key already
    resolving to A's current target onto B, then map A itself to B. Propagating
    is what makes a **cycle** resolve correctly — on ``A -> B -> A`` the second
    hop repoints B *and* A to A, so both land where the artifact actually sits.

    A flat last-write-wins dict cannot do this: it stores ``{A: B, B: A}`` and
    leaves the reader to walk it, which either loops or must stop early, and
    stopping early is stopping one hop short of the answer. That was the shape
    GHI #557 removed from :class:`~gzkit.ledger.Ledger` — and the shape that
    survived here, unnoticed, because nothing compared the two.

    Unrenamed ids are **absent** rather than self-mapped: the result is a pure
    delta, and the caller supplies the identity default.
    """
    canonical: dict[str, str] = {}
    for old_id, new_id in pairs:
        if not old_id or not new_id or old_id == new_id:
            continue
        previous = canonical.get(old_id, old_id)
        if previous != new_id:
            for key, target in canonical.items():
                if target == previous:
                    canonical[key] = new_id
        canonical[old_id] = new_id
    return canonical


def rename_events(events: Iterable[Mapping[str, Any]]) -> list[tuple[str, str]]:
    """Extract ``(old_id, new_id)`` pairs from mapping-shaped ledger events."""
    return [
        (str(event.get("id", "")), _field(event, "new_id"))
        for event in events
        if _event_type(event) == "artifact_renamed"
    ]


def rename_chain_target(events: Iterable[Mapping[str, Any]], artifact_id: str) -> str:
    """Resolve ``artifact_id`` to the id it currently carries.

    An ``obpi_created`` record names whatever its parent was called that day.
    Promotion, demotion, and slug corrections all rename ADRs, so a parent id
    that looks absent is usually just historical. Resolving the chain is what
    separates *renamed* from *missing* — conflating the two is what made 20 of
    this census's findings false.

    A shape adapter over :func:`fold_renames`; the semantics live there, shared
    with :meth:`gzkit.ledger.Ledger._build_rename_map`.
    """
    return fold_renames(rename_events(events)).get(artifact_id, artifact_id)


def park_coherence_violations(
    events: Iterable[Mapping[str, Any]],
    brief_owners: Mapping[str, str],
) -> list[tuple[str, str]]:
    """Return ``(obpi_id, owning_adr)`` for OBPIs parked while living outside pool.

    ``brief_owners`` maps an OBPI id to the **non-pool** ADR whose package
    currently holds its brief on disk. Parked means "this OBPI's parent went back
    to pool", so a parked OBPI whose brief sits in a live ADR's package is
    asserting two contradictory things at once (GHI #774).

    **Why it went unwitnessed for so long.** Park is one of the dispositions
    :func:`orphaned_obpi_ids` excludes from its census, so parking an orphan
    *silences* it — and nothing then re-checked that the disposition was still
    true. The GHI #584 backfill wrote 356 park events to quiet 233 orphans
    without consulting where each parent actually lived. With ``obpi_unparked``
    never once emitted in the repository's history, nothing could clear them.

    The consequence is destructive rather than cosmetic: :func:`parkable_children`
    skips already-parked OBPIs, so ``gz adr demote`` on such a parent emits *no*
    park events while still deleting every brief — and this census's exclusion of
    parked OBPIs means the deletion raises no finding. A hollow exit 0.

    **Grounded in Layer-1 placement, not the rename chain.** The obvious
    implementation — resolve the ``obpi_created`` parent through
    :func:`rename_chain_target` and test it against the non-pool ADR ids — is
    wrong for exactly the ADRs that matter. A demote-then-promote round trip is a
    rename *cycle* (``A -> B -> A``), and that function seeds ``seen = {current}``
    and halts when the next hop is already seen, so it resolves such an ADR to its
    **pool** id while the file sits in ``pre-release/``. Round-tripped ADRs are
    precisely the population this check exists to find, so the chain would have
    hidden them. Where the brief *is* needs no inference, and it is also exactly
    the set ``gz adr demote`` would delete.

    Completion does not exempt a violation: completion is a disposition, not a
    location, and the most consequential instance (a Gate-5-attested brief in a
    package ``demote`` would delete) is precisely a completed one.
    """
    parked = park_state(list(events))
    return sorted(
        (obpi_id, owner) for obpi_id, owner in brief_owners.items() if parked.get(obpi_id, False)
    )


def orphaned_obpi_ids(
    events: Iterable[Mapping[str, Any]],
    live_parent_ids: set[str],
    brief_ids: set[str] | None = None,
) -> list[str]:
    """Return created OBPIs that carry no disposition and nothing in Layer-1.

    This is the census GHI #584 named. An OBPI is flagged when it has no
    disposition (terminal / completed / parked) **and** either arm fails:

    * its parent id does not resolve to a live ADR, or
    * no brief for it exists on disk (``brief_ids``).

    Both arms matter. Parent-resolution alone is a proxy — an OBPI under a
    perfectly live ADR whose brief was deleted is still Layer-2 asserting an
    artifact Layer-1 cannot show, which is the incoherence the GHI's title
    names. Passing ``brief_ids=None`` checks the parent arm only.

    **Both ids resolve through their ``artifact_renamed`` chain** — an artifact
    that was renamed is not an artifact that vanished. The parent arm has always
    done this; the subject arm was a raw stem-membership test until 2026-08-16,
    so the sentence was true of the OBPI's parent and false of the OBPI itself.
    It stayed latent because the disposition short-circuit above catches every
    renamed OBPI in this repository's history — all of them terminal or
    completed by the time they were renamed — leaving the arm reachable only by
    an undisposed brief, which is exactly the case a live slug correction makes.
    Each arm tests the id *and* its chain terminal rather than the terminal
    alone, because :func:`rename_chain_target` halts on a cycle: an ``A -> B ->
    A`` round trip resolves to ``B`` while the artifact sits on disk as ``A``.
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
        parent_resolves = parent in live_parent_ids or (
            rename_chain_target(materialized, parent) in live_parent_ids
        )
        brief_exists = (
            brief_ids is None
            or obpi_id in brief_ids
            or rename_chain_target(materialized, obpi_id) in brief_ids
        )
        if parent_resolves and brief_exists:
            continue
        orphans.setdefault(obpi_id, None)
    return list(orphans)
