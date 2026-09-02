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
import hashlib
import json
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# `_exclusive_store_lock` is the project's ONE cross-platform advisory-lock
# primitive (`flock` on POSIX, `msvcrt.locking` on Windows). Restating it here
# would mean two implementations of "exclusive access to a content store" that
# can drift apart; promoting it out of `corpus_store` into a neutral module is
# the right home and is out of this task's allowed paths.
from gzkit.content.corpus_store import _exclusive_store_lock
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


def write_declaration_atomically(path: Path, text: str) -> None:
    r"""Replace *path*'s contents with *text* in one atomic step, or not at all.

    `Path.write_text` opens the target with `mode='w'` -- it TRUNCATES before
    it writes, so an interrupted or disk-full write leaves a half-serialized
    declaration on disk. On this surface that is worse than the refused
    operation: a declaration nobody can parse is an unreadable coverage claim
    on the ONE store gating the unowned-byte ratchet, and every reader of it
    fails closed until a human hand-edits a repair -- exactly the silent
    hand-edit ADR-0.35.0 § Consequences Negative #4 exists to close.

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
    recovery path, unrunnable on Windows. `newline="\n"` is pinned for the
    same reason: the declaration is a TRACKED artifact, and the platform
    default would commit `\r\n` on Windows and `\n` everywhere else. This
    mirrors `corpus_store._commit_atomically`, the project's other atomic
    content write, rather than restating a second durability discipline.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        staging = Path(handle.name)
        try:
            handle.write(text)
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
    crash would wedge the raise-path permanently. It reuses
    `corpus_store._exclusive_store_lock` rather than restating the
    platform-conditional `flock`/`msvcrt` pair -- one implementation of
    "exclusive access to a content store", not two that can drift.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with _exclusive_store_lock(path):
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
