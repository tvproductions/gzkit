"""Append-only corrective actions over any ledger event (GHI #611).

Operator intent, verbatim: *"we need the power to UNDO agent (or human)
error"*, *"not to erase the ledger, but to provide subsequent corrective
actions."*

Corrective work under ADR-0.0.71, whose § Intent already declared repudiation a
**port** — *"an erroneously- or fraudulently-attested completion can be
governed-reversed without retiring the OBPI, leaving an honest audit trail"* —
with ``obpi_completion_repudiated`` named as its **first adapter**. gzkit then
grew a second, a third and a fourth adapter of that same port
(``obpi_parked``/``obpi_unparked``, ``obpi_blocked_on_operator``/
``obpi_unblocked``) without ever laying the port itself, so each new error class
re-discovered the problem and shipped its own verb pair. This module is the
port: one correction event over *every* event type, one netting rule, and two
derived readings that every consumer shares.

**Two readings, and they are not the same question.**

* :func:`evidence_events` answers *what is true* — it drops only ``void`` rows,
  because a void row records something that was never the case.
* :func:`live_events` answers *what condition is currently in force* — it drops
  ``void`` and ``discharged``, because a discharged row was TRUE when written
  and stopped being live afterwards.

Collapsing the two would repeat the mistake GHI #823 names: an erroneous record
and a correctly-recorded-then-superseded one have different premises, and a
primitive that cannot tell them apart forces one to be filed as the other.

Pure stdlib over already-parsed events: no ledger IO and no adapters, so the
semantics are testable without a project tree (``hexagonal-architecture.md``
§ 6) and the raw-JSONL trust audits can consume them without importing the
ledger reader. Both serialization shapes are accepted — raw JSONL flattens
payload fields to top level, while :meth:`gzkit.ledger.LedgerEvent.model_dump`
nests them under ``extra`` — for the reason :mod:`gzkit.obpi_lifecycle` states:
reading only one shape is correct for whichever call site was written first and
silently wrong for the other.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

#: The one corrective event. Deliberately not per-subject-type: a family of
#: typed corrective events would be the point-solution shape this closes.
CORRECTION_EVENT = "ledger_event_corrected"

VOID = "void"
DISCHARGED = "discharged"
REINSTATED = "reinstated"

#: Closed disposition vocabulary. ``reinstated`` is the in-family reversal that
#: makes a correction itself reversible, which the issue's declared design
#: surface asks for ("how a correction is itself attestable/reversible").
DISPOSITIONS: frozenset[str] = frozenset({VOID, DISCHARGED, REINSTATED})

#: Closed cause vocabulary, mirroring ADR-0.0.71 Boundary Invariant 4's ruling
#: that ``cause`` is "extensible only by amendment ADR, never free-form" — a
#: free-text cause can be read but never censused. ``runtime-error`` exists
#: because GHI #842 recorded a ledger the runtime itself wrote wrong, where no
#: actor erred; ``condition-resolved`` is the non-error cause that pairs with
#: ``discharged``.
CAUSES: frozenset[str] = frozenset(
    {"agent-error", "operator-error", "runtime-error", "condition-resolved"}
)

#: Identity of one ledger row: ``(event, id, ts)``. Measured 2026-09-06 over the
#: 15,923 committed rows, this triple is unique for every row but one pair of
#: byte-identical ``session_exit_bookmark_skipped`` rows sharing a timestamp.
#: A reference therefore names a determinate SET of rows — normally one — and
#: every reader computes that set the same way. It is never a heuristic match:
#: the id alone would sweep every event on an artifact, and the timestamp alone
#: would sweep unrelated rows written in the same instant.
SubjectKey = tuple[str, str, str]


def _field(event: Any, key: str) -> str:
    """Read a payload field across both serialization shapes."""
    if isinstance(event, Mapping):
        if key in event:
            return str(event.get(key, ""))
        extra = event.get("extra")
        return str(extra.get(key, "")) if isinstance(extra, Mapping) else ""
    value = getattr(event, key, None)
    if value is not None:
        return str(value)
    extra = getattr(event, "extra", None)
    return str(extra.get(key, "")) if isinstance(extra, Mapping) else ""


def _envelope(event: Any, key: str) -> str:
    """Read an envelope field (``event``, ``id``, ``ts``) from either shape."""
    if isinstance(event, Mapping):
        return str(event.get(key, ""))
    return str(getattr(event, key, ""))


def subject_key(event: Any) -> SubjectKey:
    """Return the identity of ``event`` itself — what a correction would name."""
    return (_envelope(event, "event"), _envelope(event, "id"), _envelope(event, "ts"))


def corrected_subject(correction: Any) -> SubjectKey:
    """Return the row identity a correction event names."""
    return (
        _field(correction, "subject_event"),
        _field(correction, "subject_id"),
        _field(correction, "subject_ts"),
    )


def is_correction(event: Any) -> bool:
    """Report whether ``event`` is a corrective action rather than a subject row."""
    return _envelope(event, "event") == CORRECTION_EVENT


def resolve_subject(events: Iterable[Any], key: SubjectKey) -> list[Any]:
    """Return every row matching ``key``, in ledger order.

    An empty result is the fail-closed signal: a correction whose subject does
    not resolve names nothing, and callers must refuse it rather than let a
    dangling reference silently void an adjacent row.
    """
    return [event for event in events if subject_key(event) == key]


def is_well_formed(correction: Any) -> bool:
    """Report whether a correction satisfies its own declared contract.

    The same requirements :class:`~gzkit.events.LedgerEventCorrectedEvent`
    declares and ``gz ledger correct`` enforces, applied at the READ boundary so
    a correction that never passed the CLI cannot change derived state. An
    unattributed or unexplained correction is refused for the reason the event
    exists at all: a state change nobody signed is the thing being corrected,
    not a correction.

    The subject triple must be complete, and it may not name another correction
    — ``reinstated`` is the in-family reversal, so the netting never resolves
    itself recursively.
    """
    subject = corrected_subject(correction)
    if not all(subject) or subject[0] == CORRECTION_EVENT:
        return False
    if _field(correction, "disposition") not in DISPOSITIONS:
        return False
    if _field(correction, "cause") not in CAUSES:
        return False
    return bool(_field(correction, "attestor").strip() and _field(correction, "reason").strip())


def correction_state(events: Iterable[Any]) -> dict[SubjectKey, str]:
    """Return ``{subject: disposition}`` for every currently-corrected row.

    Last correction wins, the same netting rule
    :func:`gzkit.obpi_lifecycle.park_state` already uses: the ledger is
    append-only, so current state is the net of the sequence and never an edit
    (``AGENTS.md`` Never #2). ``reinstated`` removes the entry, which is what
    makes ``void -> reinstate -> void`` resolve to ``void`` rather than to an
    order-dependent answer.

    **Every correction is validated HERE, not only at the CLI.** A correction
    reaching a reader has not necessarily passed ``gz ledger correct``: the
    exported factory can be called directly, a row can be hand-written, and a
    merge can carry one in. Replay is what every consumer actually uses, so a
    guard that lives only on the write path is decorative — an invalid
    correction would still change derived state everywhere. :func:`is_well_formed`
    applies the event's own declared contract, and a correction failing it is
    INERT rather than partially applied.

    Ignored rather than applied:

    * a malformed correction (empty attestor or reason, unknown disposition or
      cause, incomplete subject triple) — :func:`is_well_formed`;
    * one whose ``subject_event`` is itself :data:`CORRECTION_EVENT` — a
      correction is reversed by ``reinstated``, never by a second correction
      naming it, so the netting can never need to resolve itself recursively.

    A reference that resolves to no row is NOT filtered here: this function is
    pure over the sequence it is handed, and a caller holding only a window of
    the ledger would otherwise drop a correction whose subject sits outside it.
    The dangling case is refused at the write boundary, where the whole ledger
    is in hand, and is inert here because nothing matches the key.
    """
    state: dict[SubjectKey, str] = {}
    for event in events:
        if not is_correction(event) or not is_well_formed(event):
            continue
        subject = corrected_subject(event)
        disposition = _field(event, "disposition")
        if disposition in {VOID, DISCHARGED}:
            state[subject] = disposition
        else:  # REINSTATED — the only remaining member of the closed vocabulary
            state.pop(subject, None)
    return state


def _without[EventT](events: Iterable[EventT], dropped: frozenset[str]) -> list[EventT]:
    """Return ``events`` minus the correction rows and every subject in ``dropped``."""
    materialized = list(events)
    state = correction_state(materialized)
    return [
        event
        for event in materialized
        if not is_correction(event) and state.get(subject_key(event)) not in dropped
    ]


def evidence_events[EventT](events: Iterable[EventT]) -> list[EventT]:
    """Return the stream answering *what is true*: raw minus ``void``.

    For witness selection and evidence audits. A ``discharged`` row survives
    here because discharging asserts its condition ended, never that its finding
    was false.
    """
    return _without(events, frozenset({VOID}))


def live_events[EventT](events: Iterable[EventT]) -> list[EventT]:
    """Return the stream answering *what is in force now*: raw minus ``void`` and ``discharged``.

    For state derivation — the artifact graph, lifecycle status, TASK liveness.
    """
    return _without(events, frozenset({VOID, DISCHARGED}))
