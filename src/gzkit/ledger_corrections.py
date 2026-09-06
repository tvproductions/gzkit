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
from datetime import UTC, datetime
from typing import Any

#: The ledger format tag every row carries. Defined HERE, in the module both the
#: reader and the validator already import, rather than in :mod:`gzkit.ledger`
#: which re-exports it. One definition, so the envelope check below cannot drift
#: from the value producers stamp.
LEDGER_SCHEMA = "gzkit.ledger.v1"

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


def _field(event: Any, key: str) -> Any:
    """Read a payload field across both serialization shapes, VALUE UNCHANGED.

    This deliberately does not stringify. It used to return ``str(value)``, and
    that single coercion decided three separate questions wrongly:

    * ``attestor: None`` became ``"None"`` — non-empty, so an unattributed
      correction passed :func:`is_well_formed` and voided its subject, while
      both declared validators refuse a null attestor;
    * ``7`` became ``"7"``, so a numeric ``subject_id`` matched the artifact
      whose id is the *string* ``"7"`` and voided a row nothing had named;
    * ``False`` and ``{}`` became ``"False"`` and ``"{}"``, non-empty by the
      same accident.

    The callers below therefore type-check what they read, which is what the
    event's own declaration says: every one of these fields is ``str``.
    """
    if isinstance(event, Mapping):
        if key in event:
            return event.get(key)
        extra = event.get("extra")
        return extra.get(key) if isinstance(extra, Mapping) else None
    value = getattr(event, key, None)
    if value is not None:
        return value
    extra = getattr(event, "extra", None)
    return extra.get(key) if isinstance(extra, Mapping) else None


def _text(event: Any, key: str) -> str:
    """Read a payload field that must be a string, or ``""`` when it is not.

    A non-string value reads as ABSENT rather than as its repr: the declared
    contract for every field this is used on is ``str``, so anything else is
    malformed input, never content.
    """
    value = _field(event, key)
    return value if isinstance(value, str) else ""


def _envelope(event: Any, key: str) -> Any:
    """Read an envelope field (``event``, ``id``, ``ts``) from either shape."""
    if isinstance(event, Mapping):
        return event.get(key, "")
    return getattr(event, key, "")


def _schema_value(event: Any) -> Any:
    """Read the ledger-format tag across both serialization shapes.

    Raw JSONL spells it ``schema``; the typed model spells it ``schema_``,
    because ``schema`` collides with a ``BaseModel`` method. Reading it through
    :func:`_envelope` would therefore return that bound METHOD on a
    :class:`~gzkit.ledger.LedgerEvent` — truthy, unequal to the tag, and so a
    typed correction would fail the envelope check that a raw one passes.
    """
    if isinstance(event, Mapping):
        return event.get("schema", event.get("schema_"))
    return getattr(event, "schema_", None)


def parse_ledger_ts(ts_value: Any) -> datetime | None:
    """Parse a ledger ``ts`` into an aware datetime, or ``None`` when unusable.

    Returns ``None`` rather than raising for malformed input: a bad timestamp is
    a finding to report, never an exception that aborts the reader holding it.

    A naive timestamp is read as UTC. Every live row is tz-aware, but comparing
    a naive datetime against an aware one raises ``TypeError``, which would turn
    a malformed row into a crash instead of a finding.

    Defined here rather than in the validator so the ONE timestamp contract is
    shared by everything that judges a ledger row — ``gz validate --ledger``
    re-exports it, and the envelope check below is the replay-side consumer that
    made sharing necessary: a correction whose ``ts`` the validator refuses was
    still voiding its subject at replay.
    """
    if not isinstance(ts_value, str) or not ts_value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(ts_value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed


def subject_key(event: Any) -> SubjectKey:
    """Return the identity of ``event`` itself — what a correction would name.

    Values are returned as they are, never stringified, so identity comparison
    is type-strict: an integer ``7`` and the string ``"7"`` are different rows.
    """
    return (_envelope(event, "event"), _envelope(event, "id"), _envelope(event, "ts"))


def identity_key(event: Any) -> SubjectKey | None:
    """Return the HASHABLE identity of ``event``, or ``None`` when it has none.

    :func:`subject_key` reads the triple as it is, so a row carrying ``id: []``
    yields a tuple no ``set`` or ``dict`` will take. Every reader that indexes
    rows by identity therefore has to ask whether the row HAS an identity before
    hashing it, and three of them did not: :func:`_without`, the subject index in
    ``gz validate --ledger``, and through them
    :func:`~gzkit.ledger.read_corrected_rows` — whose entire contract is that it
    must not raise — all died with ``TypeError: unhashable type`` on an ordinary
    malformed row, corrections absent entirely.

    ``None`` rather than a coerced key: the ledger's identity rule declares all
    three components ``str``, so a row failing that has no identity to compute,
    and no well-formed correction can name it. Skipping it from an index is
    therefore complete as well as safe — never a dropped match.
    """
    key = subject_key(event)
    return key if all(isinstance(part, str) for part in key) else None


def corrected_subject(correction: Any) -> SubjectKey:
    """Return the row identity a correction event names, values unchanged.

    Compared against :func:`subject_key` by equality, so a subject reference of
    the wrong TYPE names nothing — which is the correct reading: the event
    declares all three components ``str``, and :func:`is_well_formed` refuses a
    correction whose reference is not.
    """
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


def _has_valid_envelope(event: Any) -> bool:
    """Report whether ``event`` is a well-formed ledger row at the envelope level.

    The three envelope facts ``gz validate --ledger`` checks on every row before
    it looks at any payload: the format tag is THIS ledger's, ``id`` is a
    non-empty string, and ``ts`` parses as ISO8601. ``event`` itself is not
    re-checked here — :func:`is_correction` has already matched it.
    """
    if _schema_value(event) != LEDGER_SCHEMA:
        return False
    row_id = _envelope(event, "id")
    if not isinstance(row_id, str) or not row_id.strip():
        return False
    return parse_ledger_ts(_envelope(event, "ts")) is not None


def is_well_formed(correction: Any) -> bool:
    """Report whether a correction satisfies its own declared contract.

    The same requirements :class:`~gzkit.events.LedgerEventCorrectedEvent`
    declares and ``gz ledger correct`` enforces, applied at the READ boundary so
    a correction that never passed the CLI cannot change derived state. An
    unattributed or unexplained correction is refused for the reason the event
    exists at all: a state change nobody signed is the thing being corrected,
    not a correction.

    The subject triple must be complete and must be STRINGS — the event declares
    all three ``str``, and a reference of another type names a row that does not
    exist under this ledger's identity rule. It may not name another correction:
    ``reinstated`` is the in-family reversal, so the netting never resolves
    itself recursively.

    Type is checked, not just emptiness. Reading these fields through ``str()``
    made ``None``, ``7``, ``False`` and ``{}`` all read as non-empty content, so
    a correction both declared validators refuse still changed derived state.

    The vocabulary reads go through :func:`_text` for a second reason beyond
    content: ``DISPOSITIONS`` and ``CAUSES`` are frozensets, and testing an
    unhashable value against one RAISES rather than returning ``False``. A
    correction carrying ``cause: []`` therefore did not read as malformed — it
    took down every reader that touched it.

    The ENVELOPE is checked too, not only the payload. A correction is first a
    ledger row: it carries this ledger's ``schema`` tag, a non-empty ``id``, and
    a parseable ``ts``. Omitting that check is what let a row ``gz validate
    --ledger`` rejects go on voiding its subject at replay, which is the split
    this contract exists to close — the two paths now refuse the same rows.
    """
    if not _has_valid_envelope(correction):
        return False
    subject = corrected_subject(correction)
    if not all(isinstance(part, str) and part.strip() for part in subject):
        return False
    if subject[0] == CORRECTION_EVENT:
        return False
    if _text(correction, "disposition") not in DISPOSITIONS:
        return False
    if _text(correction, "cause") not in CAUSES:
        return False
    return bool(_text(correction, "attestor").strip() and _text(correction, "reason").strip())


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

    * one whose subject has not been seen YET at the point the correction
      appears. A corrective action is appended after the fact it corrects, so a
      correction standing ahead of its subject in the sequence cannot have been
      written by ``gz ledger correct``, and applying it lets a row be voided
      before it exists.

    **Append order is POSITION, never the timestamp.** Two rows may legitimately
    share a ``ts`` — the ledger holds a byte-identical pair already — so an
    ordering rule reading timestamps alone accepts a correction that precedes its
    subject whenever the two are stamped the same instant. It also cannot see the
    ordering at all when either ``ts`` fails to parse. The sequence handed to
    this function IS the append order; comparing positions in it needs neither.

    Requiring the subject to have been seen also subsumes the dangling case in
    the direction that matters, WITHOUT the global knowledge a resolution check
    would need. A correction whose subject sits outside the window this caller
    holds nets nothing — which was already true, because nothing in the window
    matches its key — so a windowed reader is no worse off than before, while a
    correction inverted against a subject the window DOES contain is now refused.
    Dangling references are reported by ``gz validate --ledger``, which holds the
    whole file and can tell "outside my window" from "nowhere at all."
    """
    state: dict[SubjectKey, str] = {}
    seen: set[SubjectKey] = set()
    for event in events:
        if not is_correction(event):
            if (key := identity_key(event)) is not None:
                seen.add(key)
            continue
        if not is_well_formed(event):
            continue
        subject = corrected_subject(event)
        if subject not in seen:
            continue
        disposition = _text(event, "disposition")
        if disposition in {VOID, DISCHARGED}:
            state[subject] = disposition
        else:  # REINSTATED — the only remaining member of the closed vocabulary
            state.pop(subject, None)
    return state


def _disposition(event: Any, state: dict[SubjectKey, str]) -> str | None:
    """Return the disposition currently in force over ``event``, if any.

    A row with no computable identity (:func:`identity_key` returns ``None``) is
    uncorrectable rather than corrected: no well-formed correction can name it,
    so it is never dropped — and, critically, never HASHED, which is what made
    a single malformed row abort the whole read.
    """
    key = identity_key(event)
    return None if key is None else state.get(key)


def _without[EventT](events: Iterable[EventT], dropped: frozenset[str]) -> list[EventT]:
    """Return ``events`` minus the correction rows and every subject in ``dropped``."""
    materialized = list(events)
    state = correction_state(materialized)
    return [
        event
        for event in materialized
        if not is_correction(event) and _disposition(event, state) not in dropped
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
