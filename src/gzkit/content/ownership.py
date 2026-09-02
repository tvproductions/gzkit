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

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.content.models.corpus import Corpus, effective_corpus
from gzkit.content.parse import section_id
from gzkit.governance.events import emit_unowned_ratchet_updated
from gzkit.ledger import Ledger

_Ownership = Literal["corpus-owned", "unowned"]
_OWNERSHIP_VALUES: frozenset[str] = frozenset({"corpus-owned", "unowned"})
_H1_PREFIX = "# "
_H2_PREFIX = "## "


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
            "The ledger event id that last set unowned_byte_floor -- an "
            "unowned_ratchet_updated or section_ownership_unowned event whose "
            "new_unowned_byte_floor must equal unowned_byte_floor. Null ONLY "
            "for a genesis declaration, permitted solely when unowned_byte_floor "
            "equals the summed byte span of the sections declared 'unowned' "
            "(REQ-0.35.0-04-02)."
        ),
    )


class OwnershipLoadError(ValueError):
    """Raised when a declaration or its surface fails the closed-enum/coverage cross-check."""


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
      * an `unowned_byte_floor` that cannot be proven by an attested ledger
        transition (REQ-0.35.0-04-02).

    The last check is the fail-closed guard against a direct, unattested
    hand-edit of the floor: `gz content unown` is meant to be the ONLY way
    the floor rises, but nothing stops a hand-edit of this JSON file unless
    the load path itself refuses to trust an unproven number. Two shapes are
    accepted:

      * `floor_event_id` names a ledger event in `.gzkit/ledger.jsonl` under
        *root* whose `new_unowned_byte_floor` equals the stored
        `unowned_byte_floor` -- the attested-chain proof.
      * `floor_event_id` is `null` AND `unowned_byte_floor` equals the summed
        byte span of the sections declared 'unowned' -- the genesis proof.
        This is the load-bearing half: without it, hand-raising the floor
        AND nulling `floor_event_id` together would walk straight past the
        chain check above.

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

    if floor_event_id is None:
        genesis_floor = sum(
            span for sid, span in measured.items() if declared_sections.get(sid) == "unowned"
        )
        if stored_floor != genesis_floor:
            msg = (
                f"What failed: {path.as_posix()!r} declares unowned_byte_floor "
                f"{stored_floor!r} with floor_event_id null, but the summed byte "
                f"span of its declared-'unowned' sections is {genesis_floor}.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- the ratchet floor is only "
                "reachable through the attested raise-path (`gz content unown`). "
                "A null floor_event_id is permitted ONLY for a genesis "
                "declaration whose floor is provably the coherent sum of its "
                "own unowned spans; a floor that disagrees with that sum is an "
                "unattested direct edit with no chain to prove it.\n"
                f"Next step: either set unowned_byte_floor to {genesis_floor} "
                "in a genuine genesis declaration, or raise it through "
                "`gz content unown` so it gains a valid floor_event_id, then "
                "retry."
            )
            raise OwnershipLoadError(msg)
    else:
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

    return OwnershipDeclaration.model_validate(raw)


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
    greater than the stored floor is REFUSED -- the floor stays byte-unchanged,
    nothing is written, and nothing under *root* is touched -- because raising
    the floor is reachable only through the attested `gz content unown`
    raise-path (OBPI-0.35.0-04 Task 3), never through this ordinary path.
    `OwnershipDeclaration` is frozen, so success returns a NEW copy via
    `model_copy`; *declaration* itself is never mutated. Persistence and
    ledger emission stay in this one adapter-level function: no allowlisted
    command-layer caller exists yet, and splitting them would leave REQ-03's
    durable-state claim unprovable.
    """
    floor = declaration.unowned_byte_floor
    if total > floor:
        msg = (
            f"What failed: recording an unowned-byte total of {total} for "
            f"surface {declaration.surface!r} would raise its ratchet floor "
            f"above the stored value {floor}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- the unowned-byte ratchet is "
            "decrease-only; recording through this ordinary path can only "
            "lower or hold the floor, never raise it.\n"
            f"Next step: raise the floor through the attested raise-path "
            f"(`gz content unown {declaration.surface} --section <id> "
            "--attestor <name> --reason <reason>`), never by recording a "
            "larger total here."
        )
        raise RatchetRefusedError(msg)

    event_id = f"unowned-ratchet-updated-{declaration.surface}-{datetime.now(UTC).isoformat()}"
    updated = declaration.model_copy(
        update={"unowned_byte_floor": total, "floor_event_id": event_id}
    )
    path = declaration_path(root, declaration.surface)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated.model_dump_json(indent=2) + "\n", encoding="utf-8")
    emit_unowned_ratchet_updated(
        root,
        event_id=event_id,
        surface=declaration.surface,
        prior_unowned_byte_floor=floor,
        new_unowned_byte_floor=total,
    )
    return updated


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
