"""Section-ownership declaration, byte-span measurement, fail-closed load.

ADR-0.35.0 § Decision item 4: sections declare `corpus-owned` or `unowned`; the
unowned byte total is recorded in a decrease-only ratchet. This module ships the
declaration shape and the two load-bearing primitives Task 1 scopes -- byte-span
measurement and the fail-closed loader. The ratchet, the attested raise-path,
ledger events, and the day-one declaration are later tasks in this OBPI.

gzkit's invariant floor is asserted over ALL of a control surface but verified
over none of it by default -- this module makes "which sections are actually
witnessed" an explicit, fail-closed fact instead of silence. There is no
undeclared third state: every H1/H2 section of the surface must carry exactly
one of the two closed-enum values, or loading fails closed naming the
offending section id (REQ-0.35.0-04-01).

"""

from __future__ import annotations

import contextlib
import errno
import hashlib
import json
import os
import tempfile
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.content.models.corpus import Corpus, effective_corpus
from gzkit.content.parse import section_id
from gzkit.file_lock import exclusive_file_lock
from gzkit.governance.events import (
    emit_unowned_ratchet_updated,
)
from gzkit.ledger import Ledger

_Ownership = Literal["corpus-owned", "unowned"]
_OWNERSHIP_VALUES: frozenset[str] = frozenset({"corpus-owned", "unowned"})
_H1_PREFIX = "# "
_H2_PREFIX = "## "

# The recognized roster of ledger event types that may witness a section-
# ownership floor (REQ-0.35.0-04-02). ANY event type used to pass here as
# long as its id resolved and its recorded floor matched -- the Step-4b
# adversary showed a `task_started` event accepted as proof. Only these three
# event types carry the `extra["surface"]` / `extra["new_unowned_byte_floor"]`
# shape `load_declaration` cross-checks against.
_OWNERSHIP_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "section_ownership_genesis",
        "section_ownership_reanchored",
        "section_ownership_unowned",
        "unowned_ratchet_updated",
    }
)

# The one type that may open a surface's chain. Every other ownership event is a
# LINK and must name the floor it moves from; genesis is the root and names none.
# Step-4b round-4 (CRITICAL) turned that exemption into the attack: genesis was
# not restricted to the FIRST event, so minting a second one re-declared day one
# at any floor the miner chose, with no attestor and no reason.
_GENESIS_EVENT: str = "section_ownership_genesis"


class OwnershipDeclaration(BaseModel):
    """A control surface's per-section ownership declaration and ratchet floor.

    Mirrors `src/gzkit/schemas/section_ownership.json`. `sections` keys on the
    stable kebab-case section id (`gzkit.content.parse.section_id`), never on
    the heading title (REQ-0.35.0-04-06).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Control surface name (e.g. 'AGENTS.md').")
    sections: dict[str, _Ownership] = Field(
        ...,
        description=(
            "Section id -> ownership state. Exactly one of 'corpus-owned' or "
            "'unowned' -- the closed enum REQ-0.35.0-04-01 exists to enforce."
        ),
    )
    unowned_byte_floor: int = Field(
        ...,
        ge=0,
        description="Decrease-only ratchet floor over unowned section byte spans.",
    )
    measured_at: str = Field(
        ..., description="ISO 8601 timestamp the declaration's spans were measured."
    )
    floor_event_id: str | None = Field(
        ...,
        description=(
            "The ledger event id that last set unowned_byte_floor -- a "
            "section_ownership_genesis, unowned_ratchet_updated, or "
            "section_ownership_unowned event whose new_unowned_byte_floor "
            "equals unowned_byte_floor and whose surface equals this "
            "declaration's surface. Never null at the loader: every floor, "
            "day-one included, is witnessed by a real ledger event rather "
            "than by self-coherence (REQ-0.35.0-04-02). Modeled as "
            "`str | None` here only because a raw on-disk value must be "
            "readable long enough for `load_declaration` to refuse a null "
            "one with recovery prose -- `OwnershipDeclaration.model_validate` "
            "is never reached on that path."
        ),
    )


class OwnershipLoadError(ValueError):
    """Raised when a declaration or its surface fails the closed-enum/coverage cross-check."""


def sections_digest(sections: Mapping[str, str]) -> str:
    """Canonical fingerprint of a complete section-ownership map.

    Step-4b round-3 finding 2 (`[high]`). The ratchet's ledger witness bound only
    the scalar floor, and the loader's span check is `<=` because the ratchet is
    decrease-only. Those two facts compose into a hole: whenever the stored floor
    sits ABOVE the true summed span -- the legitimate state after a surface
    shrink, before the next recording -- that slack is room to flip a section from
    `corpus-owned` to `unowned` while the sum stays under the floor. Reproduced:
    a flip accepted with the ledger holding exactly one row before and after, so
    coverage was LOST with no transition record at all.

    A scalar cannot witness a map. This binds the whole map to the event that
    corroborates it, so any ownership change without a matching witness fails
    closed regardless of what the floor arithmetic permits.

    The digest lives ONLY on the ledger event, never on the declaration: a stored
    copy alongside the sections it summarizes is a second source of truth that can
    disagree with itself, and re-deriving it here means the comparison is always
    against what the declaration actually says.
    """
    canonical = json.dumps(dict(sorted(sections.items())), separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


def measure_section_spans(surface_text: str) -> dict[str, int]:
    """Return {section_id: byte_span} for every H1/H2 heading in *surface_text*.

    A section's span runs from its own heading line to the byte before the next
    H1/H2 heading, or EOF for the last section. Keyed by the canonical
    `gzkit.content.parse.section_id` vocabulary so ownership never keys on
    heading TITLE (REQ-0.35.0-04-06) -- a heading whose text changes but whose
    section id does not still resolves. Spans are measured in UTF-8 encoded
    bytes and always sum to `len(surface_text.encode("utf-8"))`. H3+ headings
    do not open a new span; their lines stay inside the enclosing H1/H2.

    A SECOND heading line resolving to a section id already seen is a
    genuine collision and fails closed (`OwnershipLoadError`) rather than
    silently summing its span onto the first -- silently summing hides the
    second heading behind the first's declaration entry, so the
    undeclared-section check `load_declaration` performs never fires for it
    (REQ-0.35.0-04-01). This holds whether the two heading titles match or
    differ: title equality is not the discriminator, id collision is -- two
    physically separate sections sharing an id are ambiguous for ownership
    purposes regardless of how they were spelled. This is distinct from a
    single heading whose TITLE changed but whose id did not (REQ-0.35.0-04-06)
    -- that case is one heading line, not two, and does not trigger this
    guard.
    """
    lines = surface_text.splitlines(keepends=True)
    boundaries: list[tuple[int, str, str]] = []
    offset = 0
    for line in lines:
        stripped = line.rstrip("\r\n")
        title: str | None = None
        if stripped.startswith(_H1_PREFIX):
            title = stripped[len(_H1_PREFIX) :].strip()
        elif stripped.startswith(_H2_PREFIX):
            title = stripped[len(_H2_PREFIX) :].strip()
        if title is not None:
            boundaries.append((offset, section_id(title), title))
        offset += len(line.encode("utf-8"))

    total = offset
    spans: dict[str, int] = {}
    titles_by_id: dict[str, str] = {}
    for index, (start, sid, title) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else total
        if sid in titles_by_id:
            first_title = titles_by_id[sid]
            if first_title != title:
                msg = (
                    f"What failed: headings {first_title!r} and {title!r} "
                    f"both slugify to section id {sid!r}.\n"
                    "Why forbidden: REQ-0.35.0-04-01 -- a colliding section "
                    "id silently sums two distinct sections' byte spans, "
                    "hiding the second heading behind the first's ownership "
                    "declaration so the undeclared-section check never fires "
                    "for it.\n"
                    f"Next step: rename {first_title!r} or {title!r} so "
                    "their slugified section ids no longer collide, then "
                    "retry."
                )
            else:
                msg = (
                    f"What failed: two separate headings both titled "
                    f"{title!r} slugify to section id {sid!r}.\n"
                    "Why forbidden: REQ-0.35.0-04-01 -- a colliding section "
                    "id silently sums two distinct sections' byte spans, "
                    "hiding the second heading behind the first's ownership "
                    "declaration so the undeclared-section check never fires "
                    "for it.\n"
                    f"Next step: rename one of the {title!r} headings so "
                    "their slugified section ids no longer collide, then "
                    "retry."
                )
            raise OwnershipLoadError(msg)
        titles_by_id[sid] = title
        spans[sid] = spans.get(sid, 0) + (end - start)
    return spans


def load_declaration(path: Path, surface_text: str, root: Path) -> OwnershipDeclaration:
    """Load an OwnershipDeclaration at *path*, fail-closed against *surface_text*.

    Fails closed (raises `OwnershipLoadError`) on:
      * a declared section value outside {'corpus-owned', 'unowned'};
      * a section measured in *surface_text* with no declaration;
      * a declared section id absent from *surface_text*;
      * a summed unowned byte span that EXCEEDS the stored `unowned_byte_floor`
        -- always checked, on every load (REQ-0.35.0-04-02). Below or equal
        LOADS CLEANLY: the ratchet is decrease-only, so a legitimate surface
        shrink legitimately leaves the true span below the recorded floor.
      * an `unowned_byte_floor` that cannot be proven by an attested ledger
        transition (REQ-0.35.0-04-02).

    The last check is the fail-closed guard against a direct, unattested
    hand-edit of the floor: `gz content unown` is meant to be the ONLY way
    the floor rises, but nothing stops a hand-edit of this JSON file unless
    the load path itself refuses to trust an unproven number. There is ONE
    uniform path -- a null `floor_event_id` is refused outright, including
    for a day-one declaration: self-coherence (the stored floor merely
    agreeing with the summed span at load time) is exactly what an attacker
    who hand-raises the floor can simply recompute, so it is never accepted
    as a proof. Every declaration's `floor_event_id` must instead resolve to
    a real ledger event, and ALL of the following must hold:

      * the id resolves to an event in `.gzkit/ledger.jsonl` under *root*;
      * the event's TYPE is in the recognized ownership roster
        (`_OWNERSHIP_EVENT_TYPES`) -- ANY event type used to pass here as
        long as its id resolved, and the Step-4b adversary showed a
        `task_started` event accepted as proof;
      * the event's `extra["surface"]` equals this declaration's `surface`
        -- an event for a different surface used to pass whenever the floor
        value happened to agree;
      * the event's recorded `new_unowned_byte_floor` equals the declaration's
        stored `unowned_byte_floor` -- the attested-chain proof.

    Every failure names the offending section id or value and carries
    three-part recovery prose (what failed / why forbidden / governed next
    step) per `.claude/rules/guardrail-feedback-prose.md`.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    declared_sections = raw.get("sections", {})
    if not isinstance(declared_sections, dict):
        msg = (
            f"What failed: ownership declaration at {path.as_posix()!r} has a "
            f"non-object 'sections' field ({declared_sections!r}).\n"
            "Why forbidden: REQ-0.35.0-04-01 requires 'sections' to map each "
            "section id to a closed-enum ownership value; a non-object cannot "
            "be cross-checked against the surface.\n"
            f"Next step: rewrite {path.as_posix()!r} so 'sections' is a JSON "
            "object of {section-id: 'corpus-owned'|'unowned'}, then retry."
        )
        raise OwnershipLoadError(msg)

    for offending_id, value in declared_sections.items():
        if value not in _OWNERSHIP_VALUES:
            msg = (
                f"What failed: section {offending_id!r} in {path.as_posix()!r} "
                f"declares ownership value {value!r}.\n"
                "Why forbidden: REQ-0.35.0-04-01 -- ownership is a closed enum "
                "of exactly 'corpus-owned' or 'unowned'; there is no undeclared "
                "third state.\n"
                f"Next step: edit {path.as_posix()!r} so section {offending_id!r} "
                "is exactly 'corpus-owned' or 'unowned', then retry."
            )
            raise OwnershipLoadError(msg)

    measured = measure_section_spans(surface_text)

    for offending_id in sorted(measured.keys() - declared_sections.keys()):
        msg = (
            f"What failed: section {offending_id!r} is present in the surface "
            f"but has no ownership declaration in {path.as_posix()!r}.\n"
            "Why forbidden: REQ-0.35.0-04-01 -- an undeclared section is the "
            "silent third state this OBPI exists to remove.\n"
            f"Next step: add {offending_id!r}: 'corpus-owned' or 'unowned' to "
            f"the 'sections' map in {path.as_posix()!r}, then retry."
        )
        raise OwnershipLoadError(msg)

    for offending_id in sorted(declared_sections.keys() - measured.keys()):
        msg = (
            f"What failed: section {offending_id!r} is declared in "
            f"{path.as_posix()!r} but is absent from the surface.\n"
            "Why forbidden: a stale declaration for a section id the surface "
            "no longer carries cannot be cross-checked (REQ-0.35.0-04-01 "
            "declared-vs-measured coverage).\n"
            f"Next step: remove {offending_id!r} from {path.as_posix()!r}, or "
            "restore the section under that id, then retry."
        )
        raise OwnershipLoadError(msg)

    stored_floor = raw.get("unowned_byte_floor")
    floor_event_id = raw.get("floor_event_id")
    declared_surface = raw.get("surface")

    # ALWAYS-ON, regardless of how floor_event_id resolves: the true
    # unowned span may LEGITIMATELY sit at or below the stored floor (a
    # surface shrink before the next ratchet recording is a correct tree),
    # but it may never sit ABOVE it. `<=` is the relation, never `==` --
    # an equality check would fail closed on that legitimate shrink. `>`
    # is the reproduced attack: flipping a corpus-owned section to
    # 'unowned' raises the true span past the recorded floor.
    unowned_span_sum = sum(
        span for sid, span in measured.items() if declared_sections.get(sid) == "unowned"
    )
    if unowned_span_sum > stored_floor:
        msg = (
            f"What failed: {path.as_posix()!r} declares unowned_byte_floor "
            f"{stored_floor!r}, but the summed byte span of its declared-"
            f"'unowned' sections is {unowned_span_sum}, which exceeds it.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- the unowned-byte ratchet is "
            "decrease-only. The true unowned span may legitimately sit BELOW "
            "the stored floor (a surface shrink before the next ratchet "
            "recording), but it may never sit ABOVE it -- exceeding the "
            "floor is the reproduced attack, where flipping a "
            "'corpus-owned' section to 'unowned' raises the true span past "
            "the recorded floor.\n"
            "Next step: restore the flipped section(s) to their prior "
            "ownership value, or raise the floor through `gz content "
            "unown` so it gains a fresh, attested floor_event_id covering "
            "the new total, then retry."
        )
        raise OwnershipLoadError(msg)

    # ONE uniform path: a null floor_event_id is refused outright, day-one
    # declarations included. Self-coherence (the stored floor merely
    # agreeing with the summed span above) is exactly what an attacker who
    # hand-raises the floor can simply recompute -- there is no longer a
    # genesis branch that trusts it.
    if floor_event_id is None:
        msg = (
            f"What failed: {path.as_posix()!r} declares floor_event_id "
            "null.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- every ratchet floor, "
            "including a surface's day-one declaration, must be witnessed "
            "by a real ledger event (`section_ownership_genesis` for "
            "day-one, `unowned_ratchet_updated` or "
            "`section_ownership_unowned` for a later raise). A null "
            "floor_event_id was witnessed only by self-coherence -- the "
            "stored floor agreeing with the summed unowned span -- which an "
            "attacker can simply recompute after hand-editing the "
            "declaration.\n"
            f"Next step: mint a `section_ownership_genesis` event for "
            f"{declared_surface!r} (or the appropriate raise event) and set "
            "floor_event_id to its id, then retry."
        )
        raise OwnershipLoadError(msg)

    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    event = ledger.latest_event(floor_event_id)
    if event is None:
        msg = (
            f"What failed: {path.as_posix()!r} declares floor_event_id "
            f"{floor_event_id!r}, which resolves to no event in "
            f"{(root / '.gzkit' / 'ledger.jsonl').as_posix()!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- an increase is only "
            "reachable through the attested raise-path, and a floor "
            "chain pointer naming an event that does not exist proves "
            "nothing.\n"
            "Next step: restore the declaration to a state whose "
            "floor_event_id resolves in the ledger, or raise the floor "
            "again through `gz content unown` so it gains a fresh, "
            "resolvable floor_event_id, then retry."
        )
        raise OwnershipLoadError(msg)

    if event.event not in _OWNERSHIP_EVENT_TYPES:
        msg = (
            f"What failed: {path.as_posix()!r} declares floor_event_id "
            f"{floor_event_id!r}, which resolves to a {event.event!r} "
            "event, not a recognized section-ownership event.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- only "
            f"{sorted(_OWNERSHIP_EVENT_TYPES)} events may witness a "
            "section-ownership floor; any other event type resolving to "
            "the right id proves nothing about this declaration's floor.\n"
            "Next step: repoint floor_event_id at a "
            "section_ownership_genesis, unowned_ratchet_updated, or "
            "section_ownership_unowned event, or raise the floor again "
            "through `gz content unown` so it gains one, then retry."
        )
        raise OwnershipLoadError(msg)

    event_surface = event.extra.get("surface")
    if event_surface != declared_surface:
        msg = (
            f"What failed: {path.as_posix()!r} declares surface "
            f"{declared_surface!r} and floor_event_id {floor_event_id!r}, "
            f"but that event witnesses surface {event_surface!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- an event witnessing a "
            "DIFFERENT surface's floor proves nothing about this "
            "declaration's floor, even when the recorded value happens to "
            "agree.\n"
            f"Next step: repoint floor_event_id at an event that witnesses "
            f"{declared_surface!r}, or raise the floor again through `gz "
            "content unown` so it gains one, then retry."
        )
        raise OwnershipLoadError(msg)

    event_floor = event.extra.get("new_unowned_byte_floor")
    if event_floor != stored_floor:
        msg = (
            f"What failed: {path.as_posix()!r} declares unowned_byte_floor "
            f"{stored_floor!r}, but its floor_event_id {floor_event_id!r} "
            f"resolves to a ledger event recording "
            f"new_unowned_byte_floor {event_floor!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- an increase is only "
            "reachable through the attested raise-path; a stored floor "
            "that disagrees with the event it claims to be proven by is "
            "an unattested direct edit (e.g. a hand-raised floor after "
            "the attested event was written).\n"
            f"Next step: set unowned_byte_floor back to {event_floor!r} "
            "to match the attested event, or raise it again through "
            "`gz content unown` so it gains a fresh floor_event_id, then "
            "retry."
        )
        raise OwnershipLoadError(msg)

    _refuse_wrong_direction_witness(path, event, floor_event_id)
    _refuse_unchained_witness(path, ledger, event, floor_event_id, declared_surface)
    _refuse_unwitnessed_section_map(path, event, floor_event_id, declared_sections)

    return OwnershipDeclaration.model_validate(raw)


def _ownership_chain(ledger: Any, surface: str) -> tuple[list[Any], set[str]]:
    """Return *surface*'s ownership chain in ledger order, later genesis INERT.

    The ledger is append-only, so file order IS chronological order. Only a
    surface's FIRST `section_ownership_genesis` is its root; subsequent genesis
    rows are SKIPPED rather than treated as errors (operator ruling
    2026-09-03). The append-only ledger cannot lose the second genesis this
    repository already carries, so rejecting such a chain would strand the
    surface permanently -- while skipping leaves an attacker's appended genesis
    rows achieving nothing at all.
    """
    chain: list[Any] = []
    inert: set[str] = set()
    seen_root = False
    for event in ledger.read_all():
        if event.event not in _OWNERSHIP_EVENT_TYPES:
            continue
        if event.extra.get("surface") != surface:
            continue
        if event.event == _GENESIS_EVENT:
            if seen_root:
                inert.add(event.id)
                continue
            seen_root = True
        chain.append(event)
    return chain, inert


def _refuse_duplicate_chain_ids(path: Path, chain: list[Any], surface: str) -> None:
    """Fail closed when a surface's chain carries the same id twice.

    Step-4b round-5 `[high]`. `Ledger.latest_event` returns the LAST matching
    payload while a positional lookup finds the FIRST matching row, so the two
    disagree about which row is under test: observed `load=ACCEPTED floor=200`
    with `actual_predecessor_of_latest_dup=mid floor=60` but
    `accepted_claimed_predecessor=g floor=100`. The record passed against a
    predecessor it did not follow. Rather than reconcile the two lookups, refuse
    the ambiguity -- a chain in which an id does not name exactly one row cannot
    be replayed at all.
    """
    seen: set[str] = set()
    for event in chain:
        if event.id in seen:
            msg = (
                f"What failed: {path.as_posix()!r} names surface {surface!r}, whose "
                f"ownership chain carries the id {event.id!r} more than once.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- an event id must name exactly "
                "one row for a chain to be replayable. With a duplicate, the "
                "payload read for validation and the row used to locate the "
                "predecessor can be DIFFERENT rows, so a record is checked "
                "against a predecessor it never followed.\n"
                "Next step: the ledger is append-only, so resolve this by "
                "re-recording the transition under a fresh, unique id and "
                "repointing floor_event_id at it, then retry."
            )
            raise OwnershipLoadError(msg)
        seen.add(event.id)


def _refuse_broken_prefix(
    path: Path, chain: list[Any], upto: int, surface: str, inert_genesis: set[str]
) -> None:
    """Replay EVERY edge from the root through position *upto*.

    Step-4b round-5 CRITICAL. Round 4's repair validated the terminal edge and
    stopped, so everything behind it was trusted: an invalid middle record was
    laundered by appending one locally-consistent tail. Reproduced with wholly
    unique ids -- root 0, a middle claiming `100 -> 50`, a tail claiming
    `50 -> 40` -- giving `load=ACCEPTED floor=40` and a
    `net_unattested_raise=0 -> 40`. The adversary's own summary: the walk
    "validates one edge. Everything behind that edge ... is trusted without
    replay."

    Operator ruled 2026-09-03: replay the complete prefix. Chains are short --
    this repository's AGENTS.md carries three rows -- so the cost is nil and the
    class of defect closes rather than moving one link further back.
    """
    if not chain:
        return
    root = chain[0]
    if root.event != _GENESIS_EVENT:
        msg = (
            f"What failed: {path.as_posix()!r} names surface {surface!r}, whose "
            f"ownership chain OPENS with a {root.event!r} event ({root.id!r}) "
            "rather than a genesis.\n"
            f"Why forbidden: REQ-0.35.0-04-02 -- only {_GENESIS_EVENT!r} may be a "
            "surface's first ownership event. Any other type is a link, and a "
            "link with nothing before it names a predecessor that does not "
            "exist.\n"
            f"Next step: record {surface!r}'s genesis first, then chain its "
            "transitions to it and retry."
        )
        raise OwnershipLoadError(msg)

    for index in range(1, upto + 1):
        event = chain[index]
        predecessor = chain[index - 1]
        _refuse_wrong_direction_witness(path, event, event.id)
        actual_prior = predecessor.extra.get("new_unowned_byte_floor")
        claimed_prior = event.extra.get("prior_unowned_byte_floor")
        if claimed_prior != actual_prior:
            msg = (
                f"What failed: {path.as_posix()!r} rests on chain link {event.id!r}, "
                f"which claims to move FROM floor {claimed_prior!r}, but its real "
                f"predecessor {predecessor.id!r} recorded floor {actual_prior!r}.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- the WHOLE prefix is replayed, "
                "not merely the last edge. Validating only the terminal link let "
                "an invalid middle record be laundered by appending one locally "
                "consistent tail, so a floor could rise with nothing attesting "
                "any step of the path it claims to have taken.\n"
                "Next step: re-record the affected transition through `gz content "
                "unown` so it chains to the real predecessor, then repoint "
                "floor_event_id at it and retry."
            )
            raise OwnershipLoadError(msg)

        named = event.extra.get("predecessor_event_id")
        # A link may name an INERT genesis row: those are skipped by the chain,
        # so a link minted while such a row still counted names the row that sat
        # where the root now sits. This is the completion of the operator's
        # 2026-09-03 INERT ruling, not a softening -- refusing these would strand
        # exactly the surface that ruling exists to rescue. It grants an attacker
        # nothing: the FLOOR edge is still checked against the REAL predecessor,
        # the map binding still holds, and a genesis row carries no prior floor,
        # so naming one asserts the same state the root asserts.
        names_inert_root = named in inert_genesis and predecessor.event == _GENESIS_EVENT
        if named is not None and named != predecessor.id and not names_inert_root:
            msg = (
                f"What failed: {path.as_posix()!r} rests on chain link {event.id!r}, "
                f"which names predecessor {named!r}, but its real predecessor is "
                f"{predecessor.id!r}.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- a row naming a predecessor "
                "other than its real one claims a place in the chain it does not "
                "hold, which is how a transition is made to appear to continue "
                "state it never saw.\n"
                "Next step: re-record the transition against its real predecessor "
                "and retry."
            )
            raise OwnershipLoadError(msg)

        if event.event == "section_ownership_reanchored":
            _refuse_non_migration_reanchor(path, event, predecessor)


def _refuse_non_migration_reanchor(path: Path, event: Any, predecessor: Any) -> None:
    """Hold a re-anchor to MIGRATION-ONLY: floor unchanged, map unchanged.

    Step-4b round-5 CRITICAL, and a hole this OBPI introduced while closing
    round 4's: the new type fell through the direction guard with no constraint
    on its map, so it was an unattested ownership-change path in its own right.
    Reproduced schema-valid: `load=ACCEPTED floor=12 alpha=unowned`,
    `attestor_present=False` -- ownership changed and the floor rose 0 -> 12
    with no `gz content unown`.

    Operator ruled 2026-09-03: a re-anchor may only re-point a declaration at an
    EQUIVALENT state, which is exactly the `sections_digest` migration it was
    created to carry. Any real ownership change goes through the attested path.

    The map arm is deliberately vacuous when the predecessor records NO digest:
    the genesis rows minted before `sections_digest` existed have none, and
    supplying it is the migration itself. There is nothing to compare against,
    and inventing a comparison would forbid the one case the type exists for.
    """
    prior = event.extra.get("prior_unowned_byte_floor")
    new = event.extra.get("new_unowned_byte_floor")
    if prior != new:
        msg = (
            f"What failed: {path.as_posix()!r} rests on re-anchor {event.id!r}, "
            f"which moves the floor {prior!r} -> {new!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- a re-anchor is MIGRATION-ONLY. "
            "It re-points a declaration at an equivalent state so a schema change "
            "can land; it is not a second raise-path. A re-anchor that moves the "
            "floor raises it outside `gz content unown`, with no attestor and no "
            "reason -- the exact bypass the ratchet exists to forbid.\n"
            "Next step: make the floor change through `gz content unown`, which "
            "records its attestor and reason, then retry."
        )
        raise OwnershipLoadError(msg)

    predecessor_digest = predecessor.extra.get("sections_digest")
    event_digest = event.extra.get("sections_digest")
    if predecessor_digest is not None and event_digest != predecessor_digest:
        msg = (
            f"What failed: {path.as_posix()!r} rests on re-anchor {event.id!r}, "
            f"which records section map {event_digest!r} while its predecessor "
            f"{predecessor.id!r} records {predecessor_digest!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- a re-anchor is MIGRATION-ONLY in "
            "the MAP as well as the floor. Changing which sections are owned, "
            "under a type that carries no attestor and no reason, is an ownership "
            "change wearing a migration's name.\n"
            "Next step: make the ownership change through `gz content unown`, "
            "then retry."
        )
        raise OwnershipLoadError(msg)


def _refuse_unchained_witness(
    path: Path, ledger: Any, event: Any, floor_event_id: str, declared_surface: str
) -> None:
    """Fail closed unless the WHOLE prefix behind this witness replays cleanly.

    Round 4 chained a witness to its immediate predecessor; round 5 showed that
    validating one edge trusts everything behind it. This now locates the
    witness in its surface's chain and replays every edge from the root to it.
    """
    chain, inert_genesis = _ownership_chain(ledger, declared_surface)
    _refuse_duplicate_chain_ids(path, chain, declared_surface)

    position = next(
        (index for index, candidate in enumerate(chain) if candidate.id == floor_event_id),
        None,
    )
    if position is None:
        # Either the surface cross-check upstream already refused a mismatch, or
        # the witness is a later genesis row the chain deliberately treats as
        # inert. A row skipped as inert may not witness a declaration: it is not
        # part of the chain, so there is no prefix to replay behind it.
        if event.event == _GENESIS_EVENT:
            msg = (
                f"What failed: {path.as_posix()!r} names floor_event_id "
                f"{floor_event_id!r}, a {_GENESIS_EVENT!r} row that is NOT "
                f"{declared_surface!r}'s first ownership event.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- genesis is the ROOT of a "
                "chain, so only the first one counts and every later one is "
                "INERT. A later genesis re-declares day one at whatever floor it "
                "carries, with no prior floor to move from, no attestor and no "
                "reason.\n"
                "Next step: record the change as a "
                "'section_ownership_reanchored' event naming its predecessor, "
                "then repoint floor_event_id at it and retry."
            )
            raise OwnershipLoadError(msg)
        return

    if position == 0 and event.event != _GENESIS_EVENT:
        msg = (
            f"What failed: {path.as_posix()!r} names floor_event_id "
            f"{floor_event_id!r}, a {event.event!r} event that OPENS "
            f"{declared_surface!r}'s chain with no genesis beneath it.\n"
            f"Why forbidden: REQ-0.35.0-04-02 -- only {_GENESIS_EVENT!r} may be a "
            "surface's first ownership event. Any other type is a link, and a "
            "link with nothing before it names a predecessor that does not "
            "exist.\n"
            f"Next step: record {declared_surface!r}'s genesis first, then chain "
            "this transition to it and retry."
        )
        raise OwnershipLoadError(msg)

    _refuse_broken_prefix(path, chain, position, declared_surface, inert_genesis)


def _refuse_unwitnessed_section_map(
    path: Path, event: Any, floor_event_id: str, declared_sections: dict[str, str]
) -> None:
    """Fail closed when the ownership MAP is not the one its witness recorded.

    Step-4b round-3 finding 2 (`[high]`). Every other check on this path
    corroborates the scalar floor; none of them looks at WHICH sections are
    owned. Because the span check is `<=` (correctly -- the ratchet is
    decrease-only, so a legitimate surface shrink leaves the true sum below the
    stored floor), any slack between sum and floor is room to flip a section from
    `corpus-owned` to `unowned` with the arithmetic still satisfied. Measured on
    a fixture carrying one section's worth of slack: the flip loaded cleanly and
    the ledger held one row before and one row after, so the coverage loss had no
    witness anywhere.

    Comparing the recomputed map digest against the one the event recorded closes
    that, and does so without weakening the `<=` relation the shrink case needs.
    """
    recorded = event.extra.get("sections_digest")
    actual = sections_digest(declared_sections)
    if recorded == actual:
        return

    if recorded is None:
        why = (
            "the event records no sections_digest at all, so it witnesses only a "
            "floor VALUE and cannot corroborate which sections are owned"
        )
    else:
        why = f"the event witnesses the map {recorded!r} while this declaration's map is {actual!r}"
    msg = (
        f"What failed: {path.as_posix()!r} declares a section-ownership map that "
        f"its floor_event_id {floor_event_id!r} does not witness -- {why}.\n"
        "Why forbidden: REQ-0.35.0-04-02 and REQ-0.35.0-04-05 -- an ownership "
        "transition is reachable only through the attested path. The floor is a "
        "SCALAR and cannot witness a MAP: while the stored floor sits above the "
        "true summed span (the legitimate state after a surface shrink), that "
        "slack is enough room to move a section from 'corpus-owned' to 'unowned' "
        "with the arithmetic still satisfied and no transition recorded "
        "anywhere.\n"
        "Next step: make the ownership change through `gz content unown`, which "
        "records the new map alongside its attestor and reason, then repoint "
        "floor_event_id at that event and retry."
    )
    raise OwnershipLoadError(msg)


def _refuse_wrong_direction_witness(path: Path, event: Any, floor_event_id: str) -> None:
    """Fail closed when a witness records a move its own TYPE cannot make.

    Step-4b round-3 finding 1 (`[critical]`). Membership of
    `_OWNERSHIP_EVENT_TYPES` was treated as sufficient, so the roster admitted
    any listed type in EITHER direction. `unowned_ratchet_updated` is the
    ORDINARY, decrease-only path -- `record_unowned_total` refuses to emit it
    for an increase -- yet a row carrying `prior=26, new=83` was accepted as
    proof of a RAISE, observed as `floor_raised=True, load=ACCEPTED,
    ledger_validation_errors=0`. That defeats REQ-0.35.0-04-02's central claim
    directly: the floor rose with no `gz content unown`, no attestor and no
    reason, using a schema-valid row of a type that structurally cannot mean
    what it was read to mean.

    A type is a CLAIM about which transition occurred, so the loader must hold
    each type to the transition it is able to witness -- exactly the distinction
    between "an allowed discriminator appeared" and "the governed procedure
    ran". `section_ownership_genesis` records no prior floor and so asserts no
    direction; it is the day-one baseline and is deliberately exempt.
    """
    prior = event.extra.get("prior_unowned_byte_floor")
    new = event.extra.get("new_unowned_byte_floor")

    if event.event == _GENESIS_EVENT:
        # The root of a chain names no predecessor floor, so it asserts no
        # direction. Genesis's own constraint -- that it be FIRST -- is enforced
        # by `_refuse_unchained_witness`, not here.
        return

    if not isinstance(prior, int):
        # Step-4b round-4: this early return used to fire for EVERY type whose
        # `prior` was absent, so omitting the field bought exemption from the
        # very check the field exists to enable
        # (`missing_prior_non_genesis_load=raise-without-prior`). Only genesis
        # is exempt, and it returned above.
        msg = (
            f"What failed: {path.as_posix()!r} names floor_event_id "
            f"{floor_event_id!r}, a {event.event!r} event recording NO "
            "prior_unowned_byte_floor.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- only "
            f"{_GENESIS_EVENT!r} may open a chain without naming the floor it "
            "moves from. Every other ownership event is a LINK: without a prior "
            "floor there is nothing to check a direction against, so the row "
            "witnesses a transition it declines to describe.\n"
            "Next step: repoint floor_event_id at an event that records its "
            "prior_unowned_byte_floor, or raise the floor through `gz content "
            "unown` so it gains one, then retry."
        )
        raise OwnershipLoadError(msg)

    if not isinstance(new, int) or isinstance(new, bool):
        # Step-4b round-5 `[medium]`: this early return accepted values Pydantic
        # later COERCED. A forged `new=12.0` gave `load=ACCEPTED floor=12
        # type=int` -- the canonical loader admitting a prohibited ordinary-path
        # raise until some other command happened to run the ledger validator.
        # `bool` is excluded explicitly because it is an `int` subclass, so
        # `True` would otherwise read as the floor 1.
        msg = (
            f"What failed: {path.as_posix()!r} names floor_event_id "
            f"{floor_event_id!r}, whose new_unowned_byte_floor is "
            f"{new!r} ({type(new).__name__}), not an integer.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- a floor is a byte count. A "
            "non-integer is compared and coerced rather than refused, so a "
            "forged value slips past the direction check and lands as a floor "
            "the ordinary path could never have set.\n"
            "Next step: re-record the transition through `gz content unown` so "
            "its floors are integers, then retry."
        )
        raise OwnershipLoadError(msg)

    if event.event == "unowned_ratchet_updated" and new > prior:
        direction, permitted = "an INCREASE", "decrease-only"
    elif event.event == "section_ownership_unowned" and new <= prior:
        direction, permitted = "a DECREASE-or-equal", "raise-only"
    else:
        return

    msg = (
        f"What failed: {path.as_posix()!r} names floor_event_id "
        f"{floor_event_id!r}, an {event.event!r} event recording "
        f"{direction} ({prior} -> {new}).\n"
        f"Why forbidden: REQ-0.35.0-04-02 -- {event.event!r} is the "
        f"{permitted} path, so a row of that type recording the opposite "
        "move cannot witness it. Accepting one lets a floor rise outside "
        "the attested raise-path, with no attestor and no reason, purely "
        "because an allowed event type carried a matching floor value. An "
        "event TYPE is a claim about which transition occurred; a row that "
        "contradicts its own type witnesses nothing.\n"
        "Next step: raise the floor through `gz content unown`, which emits "
        "a section_ownership_unowned event carrying the attestor and reason, "
        "then repoint floor_event_id at it and retry."
    )
    raise OwnershipLoadError(msg)


def write_declaration_atomically(path: Path, text: str) -> None:
    r"""Serialize *text* as UTF-8 and write it through `write_bytes_atomically`.

    `Path.write_text` opens the target with `mode='w'` -- it TRUNCATES before
    it writes, so an interrupted or disk-full write leaves a half-serialized
    declaration on disk. On this surface that is worse than the refused
    operation: a declaration nobody can parse is an unreadable coverage claim
    on the ONE store gating the unowned-byte ratchet, and every reader of it
    fails closed until a human hand-edits a repair -- exactly the silent
    hand-edit ADR-0.35.0 § Consequences Negative #4 exists to close.

    THIS FUNCTION IS THE TEXT SPELLING AND NOTHING ELSE. The staging file, the
    per-call unique name, the fsync-before-rename ordering, the parent-directory
    barrier and the Windows reasoning all live in `write_bytes_atomically`; a
    delegator that also narrates the mechanism is a second description of it,
    and two descriptions of one durability discipline drift the way two
    implementations do. Encoding is pinned to UTF-8 here because that is the
    only decision left at this layer: the declaration is a TRACKED artifact, so
    its bytes must not vary by platform. Line endings need no separate pin --
    `str.encode` performs no newline translation, unlike the text-mode handle
    this function used to open.
    """
    write_bytes_atomically(path, text.encode("utf-8"))


def write_bytes_atomically(path: Path, data: bytes) -> None:
    r"""Replace *path*'s contents with *data* in one atomic step, or not at all.

    The byte-level primitive `write_declaration_atomically` delegates to, and
    the one place this project's declaration-side durability discipline is
    stated. It is spelled in BYTES because the un-owning transaction must also
    retain the measured source (§ Recovery Protocol state E), and a source
    snapshot is bytes.

    THE REASON THIS EXISTS IS ONE DISCIPLINE, NOT TWO. It would be overstated
    to claim the extraction was forced by byte-exactness: `_read_surface_or_exit`
    guarantees the surface decodes as UTF-8, and a strict decode/encode round
    trip is byte-exact, so the previous text writer would have written the
    snapshot correctly. What it could not do is keep ONE statement of the
    fsync/rename/barrier ordering -- the alternative was a second atomic writer
    beside this one, which is the drift GHI #945 removed from the file-locking
    primitive for the same reason.

    Staging lives in the TARGET's directory so `os.replace` is a
    same-filesystem rename (atomic on POSIX and on Windows), and the staging
    name is unique per call rather than derived from the pid, because two
    THREADS of one process share a pid. `fsync` before the rename is what
    makes the durability claim real rather than buffered.

    The barrier is applied to the descriptor that WROTE the file, never to a
    freshly-opened read handle: on Windows `os.fsync` is `_commit` ->
    `FlushFileBuffers`, which requires GENERIC_WRITE, so a read handle returns
    ERROR_ACCESS_DENIED and `os.fsync` raises -- which this function's own
    `except OSError` would re-raise, making every declaration write, and its
    recovery path, unrunnable on Windows. THAT MUCH mirrors
    `corpus_store._commit_atomically`, the project's other atomic content
    write, which fsyncs the same write handle for the same reason.

    THE MIRROR STOPS AT THE FILE. `_commit_atomically` fsyncs the handle and
    calls `Path.replace`, and takes NO directory barrier at all -- so the
    `commit_directory_entry` call this function ends with has no counterpart
    there, and reading the two as one discipline would suggest the corpus store
    commits its rename's directory entry, which it does not. The barrier is
    stated once, in `commit_directory_entry`, precisely so the two writers can
    differ here without either restating it.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        staging = Path(handle.name)
        try:
            handle.write(data)
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
    # The fsync above makes the file's BYTES durable; it says nothing about the
    # RENAME. That barrier is `commit_directory_entry`, shared with the removal
    # side rather than restated here.
    commit_directory_entry(path.parent)


BARRIER_UNSUPPORTED_ERRNOS: frozenset[int] = frozenset(
    {errno.EINVAL, errno.ENOSYS, errno.ENOTSUP, errno.EOPNOTSUPP}
)
"""Errnos meaning the filesystem HAS NO directory-fsync operation.

`commit_directory_entry` is already a no-op on Windows, where there is no
directory handle to sync. These errnos are the SAME disposition arriving
through an errno instead of through `os.name`: a POSIX export that answers
`fsync` on a directory with `EINVAL` cannot provide the barrier at all, so a
caller that treats the raise as a transient fault refuses every invocation
forever and offers a remedy no retry can reach. A caller needing the ordering
this barrier establishes MUST classify on this set before refusing; every other
errno (a full disk, a read-only mount, a permissions change) is a real fault a
retry can clear.
"""


def commit_directory_entry(directory: Path) -> None:
    r"""Commit *directory*'s pending entry changes — the barrier, stated ONCE.

    A directory entry created by `os.replace` or destroyed by `Path.unlink` is
    buffered metadata on POSIX: the operation is atomic but NOT durable, so a
    power loss immediately afterwards can leave the directory still naming the
    old inode, or still naming an unlinked one. Syncing the parent directory is
    what commits the entry, and this store is the ONE artifact gating the
    unowned-byte ratchet.

    IT IS EXTRACTED RATHER THAN DUPLICATED BECAUSE THE REMOVAL SIDE NEEDS THE
    SAME BARRIER FOR A DIFFERENT INVARIANT. `write_bytes_atomically` needs it
    so a VISIBLE file is a DURABLE one -- one file's own durability, where a
    crash before the fsync and a crash before the rename are equally harmless.
    `commands/content/unown.py` needs it for CROSS-FILE ORDERING: the
    pending-transition journal gates replay of every dependent recovery file,
    so the journal's absence must be committed before any dependent is deleted
    or its path reused. Without the barrier between them, nothing forbids the
    dependents' entry removals committing while the journal's does not --
    journal back, retained source gone. That the two directories differ (the
    journal beside the declaration, the extract beside the surface) is exactly
    why the barrier is a function taking one: each entry is committed in the
    directory that holds it.

    Windows has no directory handle to sync (`os.open` on a directory raises
    PermissionError), so the barrier is POSIX-only BY CONSTRUCTION rather than
    by omission, and callers on Windows get a no-op that raises nothing. A
    second statement of this discipline beside the first is the drift GHI #945
    removed from the file-locking primitive for the same reason.
    """
    if os.name != "posix":
        return
    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


@contextlib.contextmanager
def exclusive_declaration_lock(path: Path) -> Iterator[None]:
    """Serialize the whole read-modify-write of the declaration at *path*.

    Loading a declaration, deciding a transition from it, and writing the
    result back is a read-modify-write over a whole file. Run unserialized, two
    concurrent writers both read the pre-transition floor and the second
    clobbers the first: both exit 0, both emit a ledger event, and one
    transition is silently discarded while its witness still claims it
    happened (the Step-4b adversary's forced concurrent run). Callers MUST
    re-read the declaration INSIDE this lock -- a value read before acquiring
    is stale by construction.

    The lock is an OS lock on a sidecar file, never a marker file whose
    presence means "held": a marker outlives the process that made it, so one
    crash would wedge the raise-path permanently. It calls
    `gzkit.file_lock.exclusive_file_lock` -- the repository's ONE
    cross-platform advisory-lock primitive, shared with the corpus store and
    owned by neither -- rather than restating the platform-conditional
    `flock`/`msvcrt` pair, because two implementations of an OS lock drift
    apart and the drift only manifests under concurrency (GHI #945).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(path):
        yield


def declaration_journal_path(root: Path, surface: str) -> Path:
    """Path to *surface*'s pending-transition journal, beside its declaration.

    The raise-path must update TWO stores -- a mutable declaration file and an
    APPEND-ONLY ledger -- and neither order is safe alone. Declaration-first
    can leave a `floor_event_id` naming an event that does not exist (which
    `load_declaration` fails closed on, deliberately); ledger-first can leave
    an event announcing a floor that was never adopted. The journal is what
    makes the residue RECOVERABLE instead of merely tolerated: the pending
    transition is recorded here before either store is touched and cleared
    only after both writes succeed, so a retry COMPLETES the interrupted move
    with the same event id rather than starting a new one -- recovery from the
    write side, never by softening the loader (REQ-0.35.0-04-02).
    """
    return declaration_path(root, surface).with_name(f"{surface}.json.journal")


def declaration_journal_source_path(root: Path, surface: str) -> Path:
    """Path to the MEASURED SOURCE BYTES retained beside *surface*'s journal.

    Step-4b round-10 finding 2. The journal records the surface's DIGEST, and a
    digest names the bytes recovery needs without being able to supply them: an
    ordinary editor replacing the uncommitted text left the transition
    permanently uncompletable and blocked every other section of the same
    surface, recoverable only by restoring bytes the governed path had
    discarded. Those bytes are retained here, immutable for the life of the
    journal and cleared with it.

    This is NOT a second copy of canon (operator ruling 2026-09-05): the
    journal already copies the serialized successor declaration, and retained
    recovery material is historical evidence about an interrupted transition,
    never a surface anything reads as authority. Nothing loads from this file;
    it is extracted to a side path for the operator to reconcile against, and
    the source surface is never rewritten from it.
    """
    return declaration_path(root, surface).with_name(f"{surface}.json.journal.source")


def declaration_path(root: Path, surface: str) -> Path:
    """Path to *surface*'s section-ownership declaration under *root*.

    The single source for where an ownership declaration lives on disk --
    `commands/content/unown.py`'s attested raise-path and
    `record_unowned_total`'s ordinary ratchet path both resolve through this
    one function, mirroring the reason `section_id` is the one place a
    heading resolves to a section id: two surfaces independently deciding
    where declarations live are two surfaces that can disagree.
    """
    return root / ".gzkit" / "ownership" / f"{surface}.json"


class RatchetRefusedError(ValueError):
    """Raised when an unattested total would raise the decrease-only unowned-byte ratchet."""


def record_unowned_total(
    root: Path, declaration: OwnershipDeclaration, total: int
) -> OwnershipDeclaration:
    """Record *total* as *declaration*'s new unowned-byte ratchet floor.

    Decrease-only (REQ-0.35.0-04-02, REQ-0.35.0-04-03): a *total* less than or
    equal to the stored floor PERSISTS the updated declaration to
    `declaration_path(root, declaration.surface)` and THEN emits an
    `unowned_ratchet_updated` ledger event carrying the prior and new floor
    values -- durable state is written before the ledger witnesses it, so
    Layer-2 never announces a floor Layer-1 does not also carry. A *total*
    greater than the stored floor is REFUSED -- the floor stays
    byte-unchanged and no declaration is written -- because raising the floor
    is reachable only through the attested `gz content unown` raise-path
    (OBPI-0.35.0-04 Task 3), never through this ordinary path. The stronger
    claim that nothing under *root* is touched at all holds ONLY of the
    pre-lock fast-path refusal: a refusal decided in-lock has necessarily
    already created `<surface>.json.lock` through `exclusive_declaration_lock`,
    and no declaration state is written on either.
    `OwnershipDeclaration` is frozen, so success returns a NEW instance built
    from the committed declaration; *declaration* itself is never mutated. Persistence and
    ledger emission stay in this one adapter-level function: no allowlisted
    command-layer caller exists yet, and splitting them would leave REQ-03's
    durable-state claim unprovable.

    This path writes the SAME file as the attested raise-path, so it takes the
    SAME disciplines rather than a weaker set of its own. A lock serializes
    only when EVERY writer takes it -- a non-participating second writer
    reopens the lost-update race `exclusive_declaration_lock` exists to close
    -- so the refusal decision is made first (it touches nothing under *root*,
    and creating a lock sidecar would break that claim) and the whole
    modify-write then runs inside the lock. The write is atomic for the same
    reason it is on the raise-path: a truncating in-place write leaves a torn
    declaration that every reader fails closed on.

    The event id is DERIVED from the transition's own content and CHAINED on
    the declaration's current `floor_event_id`, never minted from a wall
    clock. Because the declaration is written before its witness, an
    interrupted run leaves a declaration naming an event the ledger lacks, and
    `load_declaration` fails closed on that forever. What reproducibility
    actually buys is narrower than "re-mintable": two callers starting from
    the SAME committed predecessor (same `floor_event_id`) mint the SAME id
    for the same transition, so concurrent readers agree on one witness
    rather than mint duplicates for a single move. It does NOT make an
    interrupted run's own move recoverable -- see the residue paragraph
    below: once THIS write commits, the predecessor has moved, so a retry
    chains onto a different parent and mints a different id; the original
    stays unreachable. Chaining on the predecessor rather than hashing
    content alone keeps two genuinely distinct recordings of the same total
    (lower, restore, lower again) from colliding into one id and silently
    dropping the second witness.

    The lock encloses the READ as well as the WRITE. *declaration* arrives as a
    parameter the caller read at some earlier moment, so it is stale by
    construction; the decrease-only comparison and the chain link are therefore
    decided against the floor and `floor_event_id` RE-READ from disk under the
    lock, and the parameter's floor serves only as a cheap pre-lock fast path.
    Without that re-read, two callers both holding floor 100 that record 40 and
    then 60 leave 60 durable -- an INCREASE over the committed 40, through the
    one path REQ-0.35.0-04-02 forbids raising the floor from, and
    self-consistent enough that `load_declaration` accepts it.

    The re-read governs the WHOLE persisted object, not merely the two scalars
    the comparison needs: the declaration written back is the one read from
    disk INSIDE the lock with `unowned_byte_floor` and `floor_event_id`
    applied to it, never the caller's copy. Patching the caller's copy is the
    identical lost-update one field over -- `gz content unown` flips a section
    to `unowned` and raises the floor to 200, a caller holding the pre-flip
    declaration records a legal 90, and the write REVERTS the attested flip
    while its ledger event still stands, leaving a file self-consistent enough
    that `load_declaration` accepts it forever. That is why this reads the raw
    JSON mapping rather than calling `load_declaration`, which would demand a
    surface text this signature has no use for, and why the return value is
    derived from committed state: a caller who persists or compares what it
    gets back would otherwise reintroduce the staleness this re-read closes.
    An on-disk `surface` naming a different control surface fails closed --
    the path was derived from `declaration.surface`, so a disagreement means
    the caller is about to overwrite a declaration that is not its own.

    Residue, stated rather than hidden: this path has NO journal, so a run
    interrupted between the declaration write and the ledger append still
    leaves a declaration the loader refuses, and the prior floor needed to
    complete the append by hand is no longer on disk. The journalled
    two-store transaction lives in `commands/content/unown.py`; there is no
    production caller of this function yet, and lifting that machinery here
    would duplicate a reviewed transaction rather than share it. The caller
    that makes this reachable (OBPI-0.35.0-05's materialization path) must
    either route through the journalled transaction or lift it into a shared
    primitive before this ships live.
    """
    # Fast path only: refusing here touches nothing under *root* (not even a
    # lock sidecar), which is what makes the "nothing is written" claim
    # literal. It is NOT the authoritative check -- *declaration* was read
    # outside the lock and its floor may already be stale.
    if total > declaration.unowned_byte_floor:
        raise RatchetRefusedError(
            _ratchet_refusal(
                declaration.surface,
                total,
                declaration.unowned_byte_floor,
                floor_is_committed=False,
            )
        )

    path = declaration_path(root, declaration.surface)
    with exclusive_declaration_lock(path):
        # Authoritative: re-read the COMMITTED declaration inside the lock.
        # Two callers holding the same pre-read floor of 100 that record 40
        # then 60 would otherwise leave 60 durable -- an increase over the
        # committed 40 through the one path REQ-0.35.0-04-02 forbids raising
        # the floor from, and self-consistent enough that `load_declaration`
        # accepts it. This reads the raw JSON rather than `load_declaration`,
        # which would demand a surface text this signature does not carry.
        committed, floor, parent_event_id = _committed_state(path, declaration)
        if total > floor:
            raise RatchetRefusedError(
                _ratchet_refusal(declaration.surface, total, floor, floor_is_committed=True)
            )

        event_id = _mint_ratchet_event_id(
            declaration.surface, prior_floor=floor, parent_event_id=parent_event_id, total=total
        )
        # Built from the COMMITTED mapping, never from the caller's copy:
        # patching the parameter would carry its stale `sections` and
        # `measured_at` back to disk, reverting an attested section flip
        # committed in between while that flip's ledger event still stands.
        # Validating the mapping is the same fail-closed posture every reader
        # of this file takes -- a torn or unknown-key declaration is refused
        # here rather than rewritten into a shape the loader will reject.
        updated = OwnershipDeclaration.model_validate(
            {**committed, "unowned_byte_floor": total, "floor_event_id": event_id}
        )
        write_declaration_atomically(path, updated.model_dump_json(indent=2) + "\n")
        emit_unowned_ratchet_updated(
            root,
            event_id=event_id,
            surface=declaration.surface,
            # The COMMITTED map, not the caller's copy -- `updated` is built from
            # the declaration re-read inside the lock, so the witness names the
            # ownership state actually on disk even when the caller's parameter
            # went stale against an attested flip committed in between.
            sections_digest=sections_digest(updated.sections),
            prior_unowned_byte_floor=floor,
            new_unowned_byte_floor=total,
        )
    return updated


def _committed_state(
    path: Path, declaration: OwnershipDeclaration
) -> tuple[dict[str, Any], int, str | None]:
    """Return the on-disk declaration mapping at *path* with its ratchet scalars.

    The MAPPING, not just the two scalars the decrease-only comparison needs:
    the caller writes the committed declaration back with the new floor
    applied to it, so anything read from the parameter instead is a field the
    write can silently revert.

    Falls back to *declaration*'s own dump when no file exists yet: that is
    the genuine first-write case, and there is nothing committed for the
    caller's read to be stale against. `load_declaration`'s full
    surface-coverage validation belongs to readers of the declaration, not to
    the writer deciding a ratchet transition, and requiring it here would
    force a surface text through a signature that has no use for it.

    An on-disk `surface` that disagrees with *declaration*'s fails closed
    rather than being overwritten. *path* is derived from
    `declaration.surface`, so the two can only disagree if the file on disk
    belongs to a different control surface -- writing through that would
    destroy another surface's declaration under a lock taken in its name.
    """
    if not path.exists():
        return (
            declaration.model_dump(),
            declaration.unowned_byte_floor,
            declaration.floor_event_id,
        )
    committed = json.loads(path.read_text(encoding="utf-8"))
    if committed.get("surface") != declaration.surface:
        raise OwnershipLoadError(
            f"What failed: the declaration at {path} names surface "
            f"{committed.get('surface')!r}, but the recording was requested "
            f"for surface {declaration.surface!r}.\n"
            "Why forbidden: this path rewrites the file it read, so proceeding "
            "would overwrite one control surface's ownership declaration with "
            "another's under a lock taken in the wrong surface's name.\n"
            "Next step: check the declaration handed to `record_unowned_total` "
            f"against the file on disk -- one of the two is for the wrong "
            f"surface, or {path.name} was written by hand."
        )
    return committed, int(committed["unowned_byte_floor"]), committed.get("floor_event_id")


def _ratchet_refusal(surface: str, total: int, floor: int, *, floor_is_committed: bool) -> str:
    """Three-part refusal prose for a total that would raise *surface*'s floor.

    *floor_is_committed* distinguishes the two call sites, which do NOT carry
    the same guarantee about *floor*. The in-lock caller passes the floor
    `_committed_state` just re-read from disk under the write lock -- genuinely
    committed at the moment of refusal. The pre-lock fast path passes
    `declaration.unowned_byte_floor`, the caller's own parameter read at some
    earlier moment and, by this module's own comment above that call site,
    possibly stale. Naming a possibly-stale parameter "the current committed
    value" would tell an operator to check the wrong number.
    """
    floor_label = (
        f"the current committed value {floor}"
        if floor_is_committed
        else f"the value {floor} you last read -- this fast path does not "
        "re-read the committed floor, so the true committed value may differ"
    )
    return (
        f"What failed: recording an unowned-byte total of {total} for "
        f"surface {surface!r} would raise its ratchet floor above "
        f"{floor_label}.\n"
        "Why forbidden: REQ-0.35.0-04-02 -- the unowned-byte ratchet is "
        "decrease-only; recording through this ordinary path can only "
        "lower or hold the floor, never raise it. The committed floor is "
        "re-read under the write lock, so it may have moved below the value "
        "you read before calling.\n"
        f"Next step: raise the floor through the attested raise-path "
        f"(`gz content unown {surface} --section <id> "
        "--attestor <name> --reason <reason>`), never by recording a "
        "larger total here."
    )


def _mint_ratchet_event_id(
    surface: str, *, prior_floor: int, parent_event_id: str | None, total: int
) -> str:
    """Mint the deterministic, chained id witnessing *surface*'s move to *total*.

    Mirrors `commands/content/unown.py::_mint_event_id` -- content-derived so a
    retry of the same move reproduces the id, and chained on the predecessor
    `floor_event_id` so a repeated move from a different predecessor earns a
    distinct id instead of colliding with the earlier one.

    Takes the predecessor as explicit scalars rather than reading them off a
    declaration object: the authoritative predecessor is the one COMMITTED at
    write time, which is not necessarily the one the caller read. A chain link
    minted from a stale predecessor points at something that is no longer the
    predecessor, which is a broken chain wearing a valid-looking id.
    """
    payload = json.dumps(
        {
            "surface": surface,
            "prior_unowned_byte_floor": prior_floor,
            "new_unowned_byte_floor": total,
            "parent_event_id": parent_event_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"unowned-ratchet-updated-{surface}-{digest}"


class OwnershipBaseline(BaseModel):
    """A control surface's derived ownership baseline (REQ-0.35.0-04-07/-08).

    Every field is computed fresh from a surface's text and corpus at call
    time -- nothing here is read from a stored constant
    (`.claude/rules/governance-core.md`: a value written in a Markdown doc is
    illustrative, never authoritative). `entry_count_by_section` is
    REQ-0.35.0-04-08's honesty companion to `coverage_pct`: the span-based
    coverage figure counts an owned section's FULL byte span even where a
    single corpus entry backs it, so the bare percentage alone overstates how
    much of the surface is actually witnessed -- the histogram is what makes
    that visible.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    owned_section_count: int
    total_section_count: int
    unowned_byte_span: int
    total_byte_span: int
    coverage_pct: float
    entry_count_by_section: dict[str, int]


def compute_baseline(surface_text: str, corpus: Corpus) -> OwnershipBaseline:
    """Derive the ownership baseline for *surface_text* against *corpus*, at call time.

    A section is 'corpus-owned' for this baseline when *corpus*'s LIVE view
    (`gzkit.content.models.corpus.effective_corpus` -- the tombstone-folded
    projection, not the raw append log) carries at least one entry addressing
    its section id; every other measured section is 'unowned'. Coverage is
    owned byte span over total byte span (REQ-0.35.0-04-07), never rounded or
    averaged (REQ-0.35.0-04-08).
    """
    spans = measure_section_spans(surface_text)
    entry_count_by_section: dict[str, int] = {}
    for entry in effective_corpus(corpus).entries:
        if entry.section in spans:
            entry_count_by_section[entry.section] = entry_count_by_section.get(entry.section, 0) + 1
    owned_ids = set(entry_count_by_section)
    total_byte_span = sum(spans.values())
    unowned_byte_span = sum(span for sid, span in spans.items() if sid not in owned_ids)
    owned_byte_span = total_byte_span - unowned_byte_span
    coverage_pct = (owned_byte_span / total_byte_span * 100) if total_byte_span else 0.0
    return OwnershipBaseline(
        owned_section_count=len(owned_ids),
        total_section_count=len(spans),
        unowned_byte_span=unowned_byte_span,
        total_byte_span=total_byte_span,
        coverage_pct=coverage_pct,
        entry_count_by_section=dict(sorted(entry_count_by_section.items())),
    )
