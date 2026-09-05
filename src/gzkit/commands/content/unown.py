"""gz content unown command handler — attested ratchet-raise path (OBPI-0.35.0-04 Task 3).

Un-owning a section is the ONE move that RAISES the decrease-only unowned-byte
ratchet: ``record_unowned_total`` (`src/gzkit/content/ownership.py`) refuses
every other attempt to raise the stored floor, and this command is the
governed exception. ADR-0.35.0 § Decision item 3: *"an undefined reversal path
is the one agents invent."* Without this attested path, the cheapest recovery
from an owned section that cannot round-trip a legitimate operator edit is a
silent hand-edit of the declaration file — this command is what stands between
that and silent coverage collapse (ADR § Consequences Negative #4).

Same corpus-attestation shape as ``gz content retire``
(`src/gzkit/commands/content/retire.py`), with one deliberate difference: un-
owning a section is a canon change EVERY time, so it never reaches the
unchanged-canon exemption ``gz content commit`` carries forward a standing
attestation through. Empty or whitespace-only ``--attestor`` or ``--reason``
exits non-zero and writes nothing (REQ-0.35.0-04-04). Given a non-empty
attestor and reason against a ``corpus-owned`` section, the section becomes
``unowned``, the floor RISES by that section's measured byte span, and a
``section_ownership_unowned`` ledger event records the section id, both floor
values, the attestor, and the reason (REQ-0.35.0-04-05).

The event is emitted from THIS command layer, not from
``gzkit.content.ownership`` — the correct layer per this OBPI's Tracked
Defects: the content layer stays pure and the command layer owns the ledger
write, mirroring ``commands/content/commit.py``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import get_project_root
from gzkit.content.ownership import (
    BARRIER_UNSUPPORTED_ERRNOS,
    OwnershipDeclaration,
    OwnershipLoadError,
    commit_directory_entry,
    declaration_journal_path,
    declaration_journal_source_path,
    declaration_path,
    exclusive_declaration_lock,
    load_declaration,
    measure_section_spans,
    sections_digest,
    write_bytes_atomically,
    write_declaration_atomically,
)
from gzkit.ledger import Ledger, LedgerEvent


def _refuse_blank_attestation(surface: str, section: str, attestor: str, reason: str) -> None:
    """Refuse and exit 1 when either --attestor or --reason is blank after strip().

    Runs BEFORE any filesystem read of the declaration, so a refusal here
    structurally guarantees the declaration stays byte-unchanged and no
    ledger event is written (REQ-0.35.0-04-04).
    """
    if attestor.strip() and reason.strip():
        return
    missing = [
        name
        for name, value in (("--attestor", attestor), ("--reason", reason))
        if not value.strip()
    ]
    verb = "is" if len(missing) == 1 else "are"
    print(
        f"Error: {' and '.join(missing)} {verb} empty or whitespace-only.\n"
        "Why forbidden: un-owning a section is a canon change with the same "
        "corpus-attestation shape as `gz content retire` -- it always requires a "
        "named attestor and a reason, fail-closed, with no unchanged-canon exemption "
        "(REQ-0.35.0-04-04; AGENTS.md § Operator Doctrine). Nothing written.\n"
        f"  Retry with `gz content unown {surface} --section {section} "
        '--attestor "<your name>" --reason "<why>"`.',
        file=sys.stderr,
    )
    sys.exit(1)


class _TransactionTarget(BaseModel):
    """The ONE identity-and-paths a single un-owning transaction operates on.

    Resolved once, before the lock, and carried through every phase: fresh
    commit, both recovery branches, witness construction and finalization.
    Its purpose is to make ONE value the sole selector of what this
    transaction reads and writes.

    Why the paths are fields rather than re-derived from `surface` at each
    site: `declaration_path`, `declaration_journal_path` and the lock path are
    built by separate helpers from the NAME, so two surface spellings that
    alias one inode can still produce different sidecar names. `samefile` on
    the surface therefore proves nothing about the sidecars, and alias
    resolution has to happen BEFORE locking, fixing all three.

    A frozen target is necessary and NOT sufficient. Paths are immutable
    values; their CONTENTS stay mutable, so freezing alone would merely
    relocate a check-then-act. The declaration snapshot consumed under the lock
    is therefore validated against this target and is then the very object the
    transition is built from. Payload identities -- `record["surface"]`, a
    journal's `surface`, a declaration's `surface` -- are values CHECKED
    against the target, NEVER inputs that route a read or a write.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="The canonical surface identity, resolved once.")
    surface_path: Path = Field(..., description="The measured surface's fixed path.")
    declaration_path: Path = Field(..., description="The ownership declaration's fixed path.")
    journal_path: Path = Field(..., description="The pending-transition journal's fixed path.")
    journal_source_path: Path = Field(
        ...,
        description=(
            "Where the MEASURED SOURCE BYTES are retained for the life of the "
            "journal -- § Recovery Protocol state E's immutable recovery material."
        ),
    )
    recovery_extract_path: Path = Field(
        ...,
        description=(
            "Where a state-E refusal EXTRACTS those bytes for the operator to "
            "diff and restore from, beside the surface. Never the surface itself: "
            "the source is never rewritten and newer edits are always preserved."
        ),
    )


def _target_for(root: Path, surface: str) -> _TransactionTarget:
    """Fix all three paths from one resolved identity."""
    surface_path = root / surface
    return _TransactionTarget(
        surface=surface,
        surface_path=surface_path,
        declaration_path=declaration_path(root, surface),
        journal_path=declaration_journal_path(root, surface),
        journal_source_path=declaration_journal_source_path(root, surface),
        recovery_extract_path=surface_path.with_name(f"{surface_path.name}.unowning-recovery"),
    )


def _declared_surface(path: Path) -> str | None:
    """Return the surface identity the declaration at *path* declares, or None.

    A raw read of one field, deliberately not `load_declaration`: the canonical
    loader fails closed on a declaration whose `floor_event_id` names an event
    the ledger does not carry, which is exactly the state an interrupted run
    leaves behind and exactly the state `_replay_pending_transition` exists to
    recover from. Identity has to be resolvable BEFORE that recovery runs, so
    it is read from the field that carries it and nothing else.

    FAIL-CLOSED POSTURE, matching `_is_same_file`. None is returned only for a
    state the canonical loader will refuse DETERMINISTICALLY on its own read --
    an absent declaration, or content that is not a JSON object carrying a
    string `surface` -- because the caller then falls through to a governed
    path that names the defect better than an identity guard can. An `OSError`
    on a declaration that EXISTS is not such a state: it is transient (a
    permission flip, an interrupted external write), so the loader's later read
    may SUCCEED where this one failed, and returning None there would hand the
    caller's raw spelling straight through to the witness -- the exact value
    this whole path exists to keep out of durable state. That case re-raises
    and the caller refuses.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        if path.exists():
            raise
        return None
    except ValueError:
        return None
    declared = raw.get("surface") if isinstance(raw, dict) else None
    return declared if isinstance(declared, str) else None


def _is_same_file(left: Path, right: Path) -> bool:
    """Report whether *left* and *right* name one file.

    A path that cannot be stat-ed is never the same file as anything, which is
    the fail-closed reading: an unresolvable spelling is refused rather than
    canonicalized.
    """
    try:
        return left.samefile(right)
    except OSError:
        return False


def _resolve_target_or_exit(root: Path, surface: str, section: str) -> _TransactionTarget:
    """Resolve the ONE transaction target this invocation operates on, or exit 1.

    Step-4b round-9 finding 1, `[high]`. On a case-insensitive filesystem
    `AGENTS.md` and `agents.md` are the same file, so the loader accepted a
    request spelled either way -- but the caller's spelling was then copied
    into `record["surface"]`, the journal and the ledger witness while the
    declaration kept its own. `load_declaration` cross-checks
    `event.extra["surface"] == declared_surface`, so the command reported
    success, deleted the journal, and left a declaration its own loader
    rejects. Nothing was forged; only the CLI argument differed.

    `OwnershipDeclaration.surface` is the authoritative identity, so it is
    resolved HERE -- once, at transaction entry, before the declaration path,
    the journal path, the surface path or the lock are derived. That placement
    is the point: every later site, the replay path and the fresh path alike,
    reads the resolved value because the caller's raw spelling no longer
    exists under any name. A guard installed further in would have to be
    installed twice, which is the round-8 finding-1 asymmetry.

    Two arms, per the operator's ruled design. A spelling that differs from the
    declared identity but names the SAME FILE canonicalizes to the declared
    one; a spelling naming a DIFFERENT file is refused in three-part prose
    before anything is journalled.
    """
    try:
        declared = _declared_surface(declaration_path(root, surface))
        if declared is None or declared == surface:
            return _target_for(root, surface)
        # Read eagerly so BOTH raw reads share one fail-closed handler: the
        # second one can raise for the same transient reason as the first.
        settles = _declared_surface(declaration_path(root, declared)) == declared
    except OSError as exc:
        _refuse_surface_identity(
            surface,
            section,
            None,
            f"its ownership declaration exists but could not be read ({exc})",
        )
    requested_path = root / surface
    declared_path = root / declared
    if not requested_path.exists():
        # Distinguished from "different files" deliberately. `_is_same_file`
        # fails closed on an unstat-able path, so a request naming a surface
        # that simply is not there used to be reported as two files that
        # differ -- which is false, and sends the operator looking for a
        # collision instead of a missing file. This refusal fires before the
        # surface is ever read, so it is the first thing they see.
        detail = (
            f"the declaration declares {declared!r}, and "
            f"{requested_path.as_posix()!r} does not exist"
        )
    elif not _is_same_file(requested_path, declared_path):
        detail = (
            f"the declaration declares {declared!r}, and "
            f"{requested_path.as_posix()!r} and {declared_path.as_posix()!r} "
            "are different files"
        )
    elif not settles:
        # The two spellings name one surface file, but the declaration reached
        # under the canonical spelling does not itself declare that identity --
        # so canonicalizing would carry a name no declaration stands behind.
        detail = (
            f"the ownership declaration for {declared!r} does not itself "
            f"declare {declared!r}, so the identity does not settle"
        )
    else:
        return _target_for(root, declared)
    _refuse_surface_identity(surface, section, declared, detail)


def _refuse_surface_identity(
    surface: str, section: str, declared: str | None, detail: str
) -> NoReturn:
    """Refuse and exit 1: the request does not resolve to ONE surface identity.

    Runs before the declaration lock is acquired, so a refusal here
    structurally leaves both stores untouched.

    The next step names the canonical retry and NOTHING ELSE. An earlier draft
    also offered "or repair the declaration so it declares <requested>", which
    is unactionable and actively harmful: the floor's witness sits in an
    APPEND-ONLY ledger naming the old identity, so a declaration hand-edited to
    declare the requested spelling is one `load_declaration` immediately fails
    closed on (`event_surface != declared_surface`). It is also precisely the
    silent hand-edit of the declaration this command exists to stand between
    the operator and (module docstring; `_refuse_forged_journal`).
    """
    if declared is not None:
        retry = (
            f"  Retry with `gz content unown {declared} --section {section} "
            '--attestor "<your name>" --reason "<why>"`.'
        )
    else:
        retry = (
            f"  Restore read access to the ownership declaration for {surface!r}, "
            "then retry the same command."
        )
    print(
        f"Error: surface {surface!r} does not resolve to the identity its "
        f"ownership declaration declares: {detail}.\n"
        "Why forbidden: `OwnershipDeclaration.surface` is the ONE identity a "
        "transaction speaks in -- the journal, the declaration and the ledger "
        "witness must all name it, and `load_declaration` fails closed when a "
        "floor's witness names a different surface than the declaration it "
        f"proves (REQ-0.35.0-04-02). Nothing written.\n{retry}",
        file=sys.stderr,
    )
    sys.exit(1)


_ENTRY_SWEEP_CAVEAT = (
    "Nothing was un-owned: no declaration byte changed and no witness was "
    "appended. That is NOT a claim that this run touched no file -- the entry "
    "boundary runs before every check below it, and on an entry that finds no "
    "journal it removes the recovery material that outlived one, reporting "
    "separately any removal it could not make."
)
"""What a refusal BELOW `_establish_recovery_boundary` may honestly say.

Every one of these refusals used to print a bare "nothing written". They are
all reachable only on an entry that found NO journal -- an entry that found one
completes or refuses the replay instead -- so by the time any of them runs, the
boundary has been established and `_sweep_recovery_residue` has UNLINKED every
dependent that outlived the missing journal. The claim was therefore not merely
unproven but FALSE whenever the sweep found anything, and the operator was told
the run was inert by the same message that follows a real deletion.

This is the class `_refuse_forged_journal` already corrected on this module's
other side, in its own words: *"a premise it cannot know is the defect,
whichever direction it points."* What these refusals DO establish is the part
kept here -- no declaration byte changed and no witness was appended.
"""


def _refuse_foreign_declaration_snapshot(
    target: _TransactionTarget, declared: Any, phase: str, *, journal_retained: bool
) -> NoReturn:
    """Refuse: the declaration snapshot CONSUMED is not the target's.

    The transaction never adopts a second identity while holding the first
    one's lock -- that move is what turns a declaration edit into a durable
    witness naming a surface the declaration on disk does not carry. This
    invocation is refused; restarting at entry, where alias resolution happens,
    is left to a later retry.

    Applied at every phase that consumes a snapshot -- the fresh load, the
    not-yet-landed predecessor, the landed state and the witness -- because a
    check on one is a check on one.

    The three RECOVERY-SIDE phases read the declaration RAW and must not route
    through `load_declaration`: a legitimate pending declaration names the very
    event recovery still has to append, so the canonical loader fails closed on
    exactly the state recovery exists to finish. The FRESH load is not one of
    them -- it goes through `_load_declaration_or_exit`, and should, because
    nothing is pending there and the full ledger-backed validation is exactly
    what a fresh transition wants. Stating the exemption as universal would
    read as a licence to unbind the fresh path, which is the dangerous
    direction to be wrong in.
    """
    exit_code = 2 if journal_retained else 1
    residue = (
        f"The journal is RETAINED at {target.journal_path.as_posix()!r}, so the "
        "transition stays completable."
        if journal_retained
        else _ENTRY_SWEEP_CAVEAT
    )
    print(
        f"Error: the {phase} declares identity {declared!r}, but this "
        f"transaction's target is {target.surface!r} "
        f"({target.declaration_path.as_posix()!r}).\n"
        "Why forbidden: the target fixes ONE identity and its surface, "
        "declaration and journal paths for the whole transaction, and every "
        "snapshot consumed under its lock must agree with it. Adopting a second "
        "identity here would write and witness through paths chosen from "
        "different values, and `load_declaration` fails closed when a floor's "
        f"witness names a surface its declaration does not (REQ-0.35.0-04-02). {residue}\n"
        "  Re-run the same command. The identity is resolved at entry, so a "
        "retry either proceeds against the declaration as it now stands or "
        "refuses naming the conflict.",
        file=sys.stderr,
    )
    sys.exit(exit_code)


def _load_declaration_or_exit(path: Path, surface_text: str, root: Path):
    """Load the ownership declaration, or exit 1 with three-part recovery prose."""
    try:
        return load_declaration(path, surface_text, root)
    except OwnershipLoadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(
            f"Error: cannot read ownership declaration at "
            f"{path.as_posix()!r}: {exc}.\n"
            "Why forbidden: the raise-path requires an existing declaration to mutate "
            f"(REQ-0.35.0-04-05). {_ENTRY_SWEEP_CAVEAT}\n"
            f"  Ensure {path.as_posix()!r} exists, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as exc:
        print(
            f"Error: ownership declaration at {path.as_posix()!r} is "
            f"malformed: {exc}.\n"
            "Why forbidden: the raise-path must load a well-formed declaration before "
            f"mutating it. {_ENTRY_SWEEP_CAVEAT}\n"
            f"  Repair {path.as_posix()!r} so it validates against "
            "src/gzkit/schemas/section_ownership.json, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)


_EVENT = "section_ownership_unowned"

# Every field a journalled record must carry to be replayable: the
# `_replay_pending_transition` reads (including `parent_event_id`, needed to
# re-mint `event_id` and check it against the on-disk chain pointer) plus the
# `_append_event_once` reads (including `ts`, which it copies onto the
# `LedgerEvent`). A line number is not a citation -- it rots on the next edit
# and cites a stranger; the function is the stable name.  A record
# missing any of them cannot complete the interrupted transition, so it is
# refused in prose rather than half-applied or left to crash with a raw
# KeyError.
_JOURNAL_FIELDS: tuple[str, ...] = (
    "event_id",
    "surface",
    "section",
    "prior_unowned_byte_floor",
    "new_unowned_byte_floor",
    "attestor",
    "reason",
    "declaration_json",
    "parent_event_id",
    "ts",
)


def _mint_event_id(record: dict[str, Any], parent_event_id: str | None) -> str:
    """Mint the DETERMINISTIC event id witnessing *record*'s pending transition.

    The previous id embedded `datetime.now()`, so an interrupted run could
    never reproduce it -- which is precisely why the residue of a failed
    ledger append was unrecoverable rather than merely untidy. Deriving the id
    from the transition's own content makes a retry mint the SAME id, so
    completing the interrupted append is idempotent by construction instead of
    by bookkeeping.

    *parent_event_id* -- the floor_event_id the transition starts FROM -- is in
    the digest to make this a chain link rather than a content fingerprint: two
    genuinely distinct un-ownings of the same section with the same attestor
    and reason (un-own, re-own, un-own again) start from different predecessors
    and so earn different ids, where a pure content hash would collide and
    silently drop the second witness.
    """
    payload = json.dumps(
        {
            "surface": record["surface"],
            "section": record["section"],
            "prior_unowned_byte_floor": record["prior_unowned_byte_floor"],
            "new_unowned_byte_floor": record["new_unowned_byte_floor"],
            "attestor": record["attestor"],
            "reason": record["reason"],
            "parent_event_id": parent_event_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"section-ownership-unowned-{record['surface']}-{record['section']}-{digest}"


def _checked_landed_snapshot(target: _TransactionTarget, record: dict[str, Any]) -> dict[str, Any]:
    """Read and VALIDATE the declaration at the target's FIXED destination.

    The witness must describe the state that exists. Deriving it from the
    journal's own `declaration_json` meant a journal could name any map it
    liked and have the ledger agree with it -- so it is read from disk. But
    the destination was RE-DERIVED from `record["surface"]`, which made a
    payload field route a filesystem read: the write destination and the later
    read destination were then chosen through different values, which is the
    defect the target exists to remove. It reads `target.declaration_path`.

    Reading is not enough either. The snapshot is checked to BE the transition
    this witness is about to describe -- the target's identity, the event
    pointer this run minted, the floor it computed, and the COMPLETE section
    map the journalled successor commits to. A digest taken from an unchecked
    read describes whatever happens to be there.
    """
    landed = json.loads(target.declaration_path.read_text(encoding="utf-8"))
    if landed.get("surface") != target.surface:
        _refuse_foreign_declaration_snapshot(
            target, landed.get("surface"), "witness source declaration", journal_retained=True
        )
    expected_map = json.loads(record["declaration_json"])["sections"]
    divergent = [
        f"{field} {landed.get(field)!r} != {value!r}"
        for field, value in (
            ("floor_event_id", record["event_id"]),
            ("unowned_byte_floor", record["new_unowned_byte_floor"]),
            ("sections", expected_map),
        )
        if landed.get(field) != value
    ]
    if divergent:
        _refuse_forged_journal(
            target,
            "the declaration at "
            f"{target.declaration_path.as_posix()!r} is not the transition this "
            f"witness would describe ({'; '.join(divergent)}) -- a witness is "
            "derived from the state that landed, never from one that was hoped for",
        )
    return landed["sections"]


def _append_event_once(root: Path, target: _TransactionTarget, record: dict[str, Any]) -> None:
    """Append *record*'s ledger event unless the ledger already carries that id.

    The append is the step a retry resumes at, so it MUST be idempotent: a run
    interrupted after the ledger write but before the journal was cleared would
    otherwise emit a second witness for one transition.
    """
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    # The map the transition COMMITS TO, read from the declaration ACTUALLY ON
    # DISK -- so the witness names the ownership state that exists, never the
    # one a journal claims. Reading it from `record["declaration_json"]` let a
    # forged journal author the digest for a map that never landed (round-4
    # finding 2). Derived BEFORE the existence check, because the expected
    # witness is what an existing row must be compared against.
    expected = {
        "surface": target.surface,
        "section": record["section"],
        "sections_digest": sections_digest(_checked_landed_snapshot(target, record)),
        "prior_unowned_byte_floor": record["prior_unowned_byte_floor"],
        "new_unowned_byte_floor": record["new_unowned_byte_floor"],
        "attestor": record["attestor"],
        "reason": record["reason"],
    }

    existing = ledger.latest_event(record["event_id"])
    if existing is not None:
        # Step-4b round-5 `[high]`: this returned on the mere EXISTENCE of the
        # id, before the landed map was derived or compared -- so the round-4
        # map binding guarded the append path and left this one open. Observed
        # `existing_digest_matches_landed=False`, `ledger_append_count=0`,
        # `journal_unlinked=True`, then `post_replay_load=REJECTED`. Idempotence
        # means "this exact witness is already recorded", never "something wears
        # this id".
        divergent = [
            field for field, value in expected.items() if existing.extra.get(field) != value
        ]
        if existing.event != _EVENT:
            divergent.insert(0, "event")
        if divergent:
            _refuse_forged_journal(
                target,
                f"the ledger already carries {record['event_id']!r}, but it "
                f"disagrees with the witness this transition would record on "
                f"{', '.join(divergent)} -- completing would consume the journal "
                "while leaving a declaration whose witness describes a different "
                "transition. An id already being present is not proof that the "
                "SAME transition was already witnessed",
            )
        return

    ledger.append(
        LedgerEvent(
            event=_EVENT,
            id=record["event_id"],
            ts=record["ts"],
            extra=expected,
        )
    )


def _refuse_forged_journal(target: _TransactionTarget, defect: str) -> NoReturn:
    """Refuse and exit 2: the journal is CRASH-RECOVERY STATE ONLY.

    Shared by every `_replay_pending_transition` defect that reaches past
    "parses to a dict carrying the right keys": a journal must be able to
    FINISH a transition its own content proves started from the live on-disk
    predecessor, never to INVENT one. A hand-authored journal that parses
    cleanly but disagrees with the on-disk chain, the deterministic event id,
    or the recomputed successor is exactly as forged as one that fails to
    parse at all, and gets the same governed refusal.

    THE NEXT STEP IS DERIVED FROM THE ENUMERATED INTERRUPTION STATE, never
    from one signal (§ Recovery Protocol binding constraints 3 and 4). It used
    to read: if the ledger carries no `section_ownership_unowned` event, "the
    raise never completed: delete the journal and re-run." That is false, and
    destructively so. States B and C BOTH have an absent witness with the
    declaration ALREADY replaced -- they are the states round-10 finding 1 is
    about -- so an operator following it deletes the only record able to
    complete the transition and leaves a declaration `load_declaration` refuses
    forever. Absence of a witness establishes nothing on its own; the state is
    settled by the declaration's `floor_event_id` AND the ledger together, and
    each branch below names the state it came from.

    The same correction applies to the middle clause: this refusal is reached
    from branches where the declaration is untouched AND from branches where it
    already carries the transition, so it does not claim "nothing written" --
    a premise it cannot know is the defect, whichever direction it points.
    """
    print(
        f"Error: the pending-transition journal {target.journal_path.as_posix()!r} is "
        f"unreadable or malformed: {defect}.\n"
        "Why forbidden: an un-owning is completed from its journal, so a "
        "journal that cannot be proven to continue the live on-disk "
        "predecessor makes an interrupted raise unrecoverable and no further "
        "un-owning of this surface may proceed on top of it "
        "(REQ-0.35.0-04-02). No ledger witness was written by this run, and "
        "the journal is RETAINED.\n"
        "  Do NOT delete the journal and do NOT hand-edit the ownership "
        "declaration. Identify the interruption state from BOTH signals "
        f"together -- the `floor_event_id` in {target.declaration_path.as_posix()!r} "
        "and whether `.gzkit/ledger.jsonl` carries the journal's `event_id` "
        "(`gz validate --ledger`):\n"
        "    - state A, floor_event_id equals the journal's `parent_event_id` "
        "and the ledger has no such row: nothing landed. Move the journal "
        "aside for the record, then re-run to start a fresh transition from "
        "the declaration on disk.\n"
        "    - state B or state C -- INDISTINGUISHABLE from disk, and the "
        "retry handles both the same way -- floor_event_id equals the "
        "journal's `event_id` and the ledger has no such row: the declaration "
        "ALREADY carries this transition, and what is outstanding is its "
        "durability barrier, its witness, or both. Re-run the same command; it "
        "re-establishes the barrier and appends the missing witness. This is "
        "the pair the retired advice treated as proof that nothing landed.\n"
        "    - state D, the ledger carries the journal's `event_id`: the "
        "transition completed and is witnessed. Re-run the same command. If "
        "the surface still carries the bytes the floor was measured against it "
        "clears the recovery material; if an editor has since changed them, it "
        "refuses naming state D AND state E and hands you the measured bytes -- "
        "the SOURCE axis is orthogonal to states A-D, so a witness settles the "
        "transition and says nothing about the source.\n"
        "  If the journal cannot be parsed at all its `event_id` is "
        "unreadable, so `floor_event_id` alone cannot separate state A from "
        "state B or state C: capture both files and ask the operator to rule.",
        file=sys.stderr,
    )
    sys.exit(2)


def _apply_unlanded_transition(
    target: _TransactionTarget,
    record: dict[str, Any],
    on_disk: dict[str, Any],
    surface_text: str,
) -> None:
    """Prove a not-yet-landed journal continues the declaration on disk, then apply it.

    Extracted from `_replay_pending_transition`, which had grown to rank D on the
    xenon ceiling by conflating two responsibilities the reader has to separate
    anyway: proving the journal is not forged, and applying the transition it
    describes. An auditor asking "can a hand-authored journal move the floor"
    should not have to read the write/rollback machinery to answer it.

    Every check here is a REFUSAL that exits; reaching the end means the journal
    is corroborated by the live declaration and surface, and the DERIVED successor
    has been written.
    """
    # The predecessor CONSUMED here is the snapshot the derived successor is
    # built from, so its identity is checked before anything is derived. Read
    # raw, never through `load_declaration`: a pending declaration names the
    # event this recovery still has to append, and the canonical loader fails
    # closed on exactly that state.
    if on_disk.get("surface") != target.surface:
        _refuse_foreign_declaration_snapshot(
            target, on_disk.get("surface"), "on-disk predecessor", journal_retained=True
        )
    # The declaration write never landed: the journal must PROVE it
    # continues the declaration actually on disk, never merely claim to.
    if on_disk.get("unowned_byte_floor") != record["prior_unowned_byte_floor"]:
        _refuse_forged_journal(
            target,
            f"prior_unowned_byte_floor {record['prior_unowned_byte_floor']!r} "
            "does not match the floor currently on disk "
            f"({on_disk.get('unowned_byte_floor')!r}) -- the journal does not "
            "start from the declaration on disk",
        )
    if on_disk.get("floor_event_id") != record["parent_event_id"]:
        _refuse_forged_journal(
            target,
            f"parent_event_id {record['parent_event_id']!r} does not match "
            f"the on-disk floor_event_id ({on_disk.get('floor_event_id')!r})",
        )
    try:
        span = measure_section_spans(surface_text)[record["section"]]
    except KeyError:
        _refuse_forged_journal(
            target,
            f"section {record['section']!r} does not exist on the live surface",
        )
    if record["new_unowned_byte_floor"] != record["prior_unowned_byte_floor"] + span:
        _refuse_forged_journal(
            target,
            f"new_unowned_byte_floor {record['new_unowned_byte_floor']!r} does "
            "not equal the on-disk floor plus section "
            f"{record['section']!r}'s real measured byte span "
            f"({record['prior_unowned_byte_floor'] + span!r})",
        )
    try:
        predecessor = OwnershipDeclaration(**on_disk)
    except (TypeError, ValueError) as exc:
        _refuse_forged_journal(target, f"on-disk declaration does not validate: {exc}")
    # The section must actually BE 'corpus-owned' on the on-disk predecessor
    # -- the same eligibility the live command path enforces at unown.py
    # (`current != "corpus-owned"` refusal). Without this check, a journal
    # naming an ALREADY-unowned section with a self-consistent event id, a
    # real prior floor/parent, and a real measured span still passes every
    # check above: flipping an already-'unowned' section to 'unowned' is a
    # no-op on `sections`, so the derived successor JSON matches too, and
    # the floor is durably inflated a second time for one section with a
    # genuine ledger event witnessing a flip that never happened.
    predecessor_status = predecessor.sections.get(record["section"])
    if predecessor_status != "corpus-owned":
        _refuse_forged_journal(
            target,
            f"section {record['section']!r} is {predecessor_status!r} on the "
            "on-disk predecessor, not 'corpus-owned' -- only a corpus-owned "
            "section may be un-owned",
        )
    new_sections = dict(predecessor.sections)
    new_sections[record["section"]] = "unowned"
    expected_declaration = predecessor.model_copy(
        update={
            "sections": new_sections,
            "unowned_byte_floor": record["new_unowned_byte_floor"],
            "floor_event_id": record["event_id"],
        }
    )
    expected_declaration_json = expected_declaration.model_dump_json(indent=2) + "\n"
    if expected_declaration_json != record["declaration_json"]:
        _refuse_forged_journal(
            target,
            "declaration_json does not match the successor derived from "
            "the on-disk predecessor and the journalled transition -- a "
            "journal may finish a transition, never invent one",
        )

    # Write the DERIVED successor, never the journal's own claimed bytes
    # verbatim -- the two are proven equal above, but the derived value is
    # the one this code actually stands behind.
    try:
        write_declaration_atomically(target.declaration_path, expected_declaration_json)
    except OSError as exc:
        print(
            f"Error completing the interrupted un-owning of "
            f"{record['section']!r}: cannot write "
            f"{target.declaration_path.as_posix()!r}: {exc}.\n"
            "Why forbidden: the journalled transition must be re-applied to "
            "the declaration before its ledger witness is written -- Layer 2 "
            "may never announce a floor Layer 1 does not carry "
            "(REQ-0.35.0-04-05). The journal is retained.\n"
            "  Check file permissions and disk space, then retry the same "
            "command to complete it.",
            file=sys.stderr,
        )
        sys.exit(2)


def _refuse_incoherent_landed_state(
    target: _TransactionTarget, record: dict[str, Any], surface_text: str
) -> None:
    """Fail closed unless the landed declaration is a state the loader accepts.

    Extracted from `_replay_pending_transition`, which crossed the xenon C
    ceiling again once the map arm landed. The seam is the same one the round-3
    extraction found: proving a journal may be completed is a separate
    responsibility from completing it, and an auditor checking the first should
    not have to read the second.

    Applied on BOTH branches. The already-landed branch -- where the declaration
    write survived but the ledger append did not -- reached the append and the
    journal unlink having validated NOTHING: every predecessor, span,
    eligibility and derived-successor check lives in the not-yet-landed branch.
    Failing closed here RETAINS the journal, so the transition stays completable
    once the surface is reconciled.
    """
    # Coherence gate, applied on BOTH branches (Step-4b round-3 finding 4).
    # The already-landed branch -- where the declaration write survived but the
    # ledger append did not -- reached the append and the journal unlink having
    # validated NOTHING: every predecessor, span, eligibility and derived-
    # successor check lives inside the not-yet-landed branch above. A run
    # interrupted at the append, whose surface then GREW before the retry, was
    # therefore completed and its journal consumed while leaving a declaration
    # the canonical loader rejects (measured: unowned 131 against floor 83,
    # `retry_exit=0`, `post_retry_load=REJECTED`) -- recovery reporting success
    # while destroying the only record that could have recovered it.
    #
    # Re-assert the loader's own invariant against the LIVE surface before
    # witnessing anything: an interrupted transition may only be completed into
    # a state the loader would accept. Failing closed here RETAINS the journal,
    # so the transition stays completable once the surface is reconciled.
    landed = json.loads(target.declaration_path.read_text(encoding="utf-8"))
    # The snapshot CONSUMED by this branch, checked before it is reasoned
    # about. Raw again, never `load_declaration` (see the unlanded sibling).
    if landed.get("surface") != target.surface:
        _refuse_foreign_declaration_snapshot(
            target, landed.get("surface"), "landed declaration", journal_retained=True
        )
    landed_floor = landed.get("unowned_byte_floor")
    live_unowned_span = sum(
        span
        for sid, span in measure_section_spans(surface_text).items()
        if landed.get("sections", {}).get(sid) == "unowned"
    )
    # Step-4b round-4 finding 2: the gate read `landed_floor` and
    # `live_unowned_span` and never the section MAP, while the witness's digest
    # was derived from the JOURNAL's claimed declaration. A journal carrying a
    # different map at the same floor therefore passed, was witnessed with a
    # digest describing a state that does not exist, and had its journal
    # consumed -- observed `journal_unlinked=True` with disk and ledger digests
    # disagreeing, then `post_replay_loader=REJECTED`. A scalar cannot witness a
    # map here for the same reason it could not witness one in the loader.
    try:
        journalled_sections = json.loads(record["declaration_json"])["sections"]
    except (ValueError, KeyError, TypeError):
        journalled_sections = None
    landed_sections = landed.get("sections")
    if journalled_sections is not None and journalled_sections != landed_sections:
        _refuse_forged_journal(
            target,
            f"the declaration on disk declares the section map "
            f"{sections_digest(landed_sections or {})!r} while the journal's "
            f"successor declares {sections_digest(journalled_sections)!r} -- "
            "completing this transition would witness a map that never landed, "
            "leaving a declaration the loader rejects. The floor agrees, which is "
            "exactly why the floor alone cannot witness the map",
        )

    # Step-4b round-7 finding 2: `live_unowned_span` sums only ids PRESENT in the
    # landed map, so a section RENAMED by an ordinary editor contributes nothing
    # and the scalar check passes while the declaration no longer covers the
    # surface at all. Measured: an injected append failure, then a rename, then a
    # retry gave `retry_exit=0`, "Completed the interrupted un-owning", one
    # witness and `journal_unlinked=True` -- and the canonical reload then
    # rejected the undeclared section. Coverage is a SET property; a sum cannot
    # witness it, for the same reason a scalar could not witness the map at round
    # 4 or the direction at round 5.
    live_ids = set(measure_section_spans(surface_text))
    landed_ids = set(landed_sections or {})
    if live_ids != landed_ids:
        missing = sorted(live_ids - landed_ids)
        stale = sorted(landed_ids - live_ids)
        _refuse_forged_journal(
            target,
            f"the declaration on disk declares sections {sorted(landed_ids)!r} "
            f"while the live surface carries {sorted(live_ids)!r} "
            f"(undeclared: {missing!r}; declared but absent: {stale!r}) -- "
            "completing this transition would witness a declaration that does not "
            "cover the surface, which the loader rejects. The surface was "
            "restructured after the transition was journalled, and the summed span "
            "cannot see it because a renamed section contributes nothing to a sum "
            "keyed on the landed map",
        )

    if landed_floor != record["new_unowned_byte_floor"] or live_unowned_span > landed_floor:
        _refuse_forged_journal(
            target,
            f"the declaration on disk carries floor {landed_floor!r} with a live "
            f"unowned span of {live_unowned_span} -- completing this transition "
            f"would leave a declaration the loader rejects (expected floor "
            f"{record['new_unowned_byte_floor']!r}, and the span may never exceed "
            "the floor). The surface changed after the transition was journalled",
        )


def _refuse_source_changed_since_measurement(
    target: _TransactionTarget, record: dict[str, Any], surface_digest: str
) -> None:
    """Refuse a replay whose surface no longer carries the measured bytes — state E.

    Step-4b round-10 finding 2, `[high]`. The journalled floor was measured
    against a specific sequence of bytes. When an ordinary editor replaces them
    the transition cannot be completed as journalled, and -- because the journal
    gates every un-owning of this surface -- no OTHER section can proceed
    either: `UNBACKED requested alpha-section exit 2 / doc-title exit 2 /
    alpha-section exit 2`. The state was reachable through ordinary CLI use and
    was escapable ONLY by restoring bytes the governed path had discarded.

    Two things make it escapable now. The bytes are RETAINED beside the journal,
    and this refusal EXTRACTS them to a side path next to the surface so the
    operator can diff, merge and restore without hunting for them. The source
    surface is NEVER rewritten: the operator's newer edit is theirs, and a
    command that silently reverted it would be trading one silent loss for
    another.

    THE RECONCILE SCRIPT IS NOT WRITTEN HERE. It is single-sourced through
    `_reconciliation_sequence`, and this site supplies only what step 4's
    re-run has left to do. It is printed CONDITIONALLY -- `if extracted:` below
    -- because the sequence requires a verified extraction, and
    `_extract_retained_source`'s failure branches cannot establish one; each
    carries its own next step instead. Printing it unconditionally is the
    retired behaviour, and `_reconciliation_sequence`'s own docstring states the
    live rule. It used to
    carry its own copy, and that copy is where the retired step 5 survived the
    correction to its twin -- an inline script drifted from the shared one
    inside a single change (Step-4b round-11 finding 1, operator ruling point
    2). Observed before the rewire: the pure-E console still printed *"5.
    re-apply your saved edit and ... record it through `gz content unown`
    again"*, whose verbatim execution leaves `load_declaration` rejecting the
    surface (floor 83, summed unowned span 443) and the advertised remedy
    exiting 1 at its own initial load.

    Placed at the TOP of the replay, before any store is read for a decision,
    so the operator meets ONE refusal naming the real condition rather than
    whichever downstream coherence guard happened to notice a consequence of
    it. Those guards are unchanged and still fire on their own conditions -- a
    surface that moves DURING the replay never reaches this check, which is why
    `_refuse_clean_success_on_a_moved_surface` remains the finalization binding.

    A journal carrying no `surface_digest` predates the round-7 binding and is
    passed through untouched: this check cannot speak about a surface the
    journal never versioned, and the coverage and span guards downstream still
    can.
    """
    journalled = record.get("surface_digest")
    if journalled is None or journalled == surface_digest:
        return

    located, extracted = _extract_retained_source(target, journalled)
    # The reconcile script names the extract, so it is appended ONLY where the
    # extract exists; each failure branch above carries its own next step.
    if extracted:
        located = f"{located} " + _reconciliation_sequence(
            target,
            "re-run the same command, which completes the pending transition "
            "and clears the journal and the retained material",
        )
    print(
        f"Error: surface {target.surface!r} no longer carries the bytes the "
        f"pending un-owning of section {record['section']!r} was measured "
        "against.\n"
        "Why forbidden: this is § Recovery Protocol state E -- the journalled "
        "floor counts PHYSICAL BYTES of the surface as it was read, so "
        "completing the transition now would witness a span the surface no "
        "longer has and `load_declaration` fails closed on a floor the live "
        "span exceeds (REQ-0.35.0-04-05). The journal gates every un-owning of "
        "this surface, so no other section may proceed on top of it either. "
        f"The journal is RETAINED at {target.journal_path.as_posix()!r} with "
        "the measured source beside it; your edit to the surface is untouched "
        "and was NOT reverted.\n"
        f"  {located}",
        file=sys.stderr,
    )
    sys.exit(2)


def _extract_retained_source(
    target: _TransactionTarget, journalled_digest: str
) -> tuple[str, bool]:
    """Extract the retained measured bytes to a side path; report WHERE they are.

    Returns guidance and whether extraction completed with verified measured
    bytes. A write error can leave an older file or a visible replacement whose
    durability is unconfirmed; neither permits the numbered recovery sequence.

    Extraction and disclosure are ONE act deliberately: naming a path the
    operator is told to restore from, without first proving that path holds the
    journalled bytes, is another instruction the command cannot keep. The
    retained material is read, VERIFIED against the digest the journal carries,
    and only then written to the side path the returned sentence names.

    EACH FAILURE BRANCH CARRIES ITS OWN EXECUTABLE NEXT STEP, because the three
    differ in what would repair them: an unreadable retention is a storage
    fault the operator can clear, a digest mismatch is a divergence only the
    operator can rule on, and a failed extraction write is a storage fault
    whose retry is this same command. None of the three may borrow the
    reconcile script -- none established a completed, verified extraction.

    The successful branch returns LOCATION, never an instruction: its two
    callers reach state E from different sides -- a pending transition versus
    one already witnessed -- and each supplies its own `step_four`.
    """
    try:
        retained = target.journal_source_path.read_bytes()
    except OSError as exc:
        return (
            "The retained measured source at "
            f"{target.journal_source_path.as_posix()!r} could not be read "
            f"({exc}), so this command cannot hand you the bytes it measured "
            "and cannot offer a verified copy to diff or restore. Restore read "
            "access to that file -- check its permissions and the health of "
            f"the mount under {target.journal_source_path.parent.as_posix()!r} "
            "-- then re-run the same command, which extracts it and prints the "
            "reconcile-and-restore sequence. If the file is GONE, capture "
            f"{target.journal_path.as_posix()!r} and "
            f"{target.declaration_path.as_posix()!r} for the record and ask the "
            "operator to rule -- do NOT delete the journal and do NOT hand-edit "
            "the ownership declaration, whose floor must stay witnessed by a "
            "real ledger event.",
            False,
        )
    if _surface_digest(retained) != journalled_digest:
        return (
            "The retained measured source at "
            f"{target.journal_source_path.as_posix()!r} does not reproduce the "
            f"journalled digest {journalled_digest}, so it is not the state "
            "this transition was measured against and nothing was extracted -- "
            "there is no file this command can prove holds the measured bytes. "
            f"Capture {target.journal_source_path.as_posix()!r}, "
            f"{target.journal_path.as_posix()!r} and "
            f"{target.declaration_path.as_posix()!r} for the record and ask the "
            "operator to rule -- do NOT delete the journal and do NOT hand-edit "
            "the ownership declaration.",
            False,
        )
    try:
        write_bytes_atomically(target.recovery_extract_path, retained)
    except OSError as exc:
        return (
            "The verified measured source is retained at "
            f"{target.journal_source_path.as_posix()!r} but could not be "
            f"fully extracted to {target.recovery_extract_path.as_posix()!r} ({exc}). "
            "That path may hold an older copy or the new replacement; its final "
            "state and durability are unconfirmed. Fix the storage fault under "
            f"{target.recovery_extract_path.parent.as_posix()!r} -- disk space, "
            "directory permissions, a read-only mount -- then re-run the same "
            "command, which retries the extraction and prints the "
            "reconcile-and-restore sequence. If you cannot, copy "
            f"{target.journal_source_path.as_posix()!r} to a path OUTSIDE this "
            "repository yourself and diff it against "
            f"{target.surface_path.as_posix()!r}. Do NOT delete the journal and "
            "do NOT hand-edit the ownership declaration.",
            False,
        )
    return (
        "The bytes this transition measured are extracted to "
        f"{target.recovery_extract_path.as_posix()!r}, and the immutable "
        f"original is retained at {target.journal_source_path.as_posix()!r}.",
        True,
    )


def _ledger_witness_present(root: Path, event_id: str) -> bool:
    """Report whether the ledger already carries *event_id* — the state-D probe.

    § Recovery Protocol distinguishes state D (the witness landed) from states
    B and C (the declaration carries the transition, no witness exists) by
    exactly this signal, and by nothing else. D is NOT "only the journal is
    left to clear": a witnessed transition still owes source reconciliation and
    cleanup, which are separate obligations a witness discharges neither of
    (operator ruling 2026-09-05).
    It is read HERE rather than inferred from the declaration because a landed
    `floor_event_id` is common to all three -- that inference is round-10
    finding 1.

    A ledger that cannot be read proves NOTHING about the witness, so the
    fail-closed reading is "not witnessed": recovery then re-establishes the
    declaration's durability, an idempotent write, instead of skipping it, and
    takes the completion path rather than the clear-only one.

    WHAT HAPPENS TO THE SWALLOWED ERROR DIFFERS BY ARM, and only one of them is
    governed. An `OSError` here recurs inside `_append_event_once` and exits
    through its three-part prose, so it is reported once and properly. A
    `ValueError` -- a `JSONDecodeError` from a crash-truncated final ledger row
    -- does NOT: the catch around `_append_event_once` is `OSError` only, so it
    escapes as a raw traceback. That is GHI #953's disclosed residual, it
    predates this function, and this function neither widens nor repairs it;
    the docstring says so rather than asserting a governed path one arm does
    not have.
    """
    try:
        return Ledger(root / ".gzkit" / "ledger.jsonl").latest_event(event_id) is not None
    except (OSError, ValueError):
        return False


def _reestablish_landed_declaration_durability(target: _TransactionTarget) -> None:
    """Re-assert the durability barrier on a landed declaration — states B and C.

    Step-4b round-10 finding 1, `[high]`. `write_declaration_atomically`
    performs `os.replace` and THEN syncs the parent directory, so EVERY write
    in `_commit_transition` has a window where the swap landed and its
    durability barrier did not. Landed recovery read ONE signal -- the
    declaration already carries the journalled `floor_event_id` -- and inferred
    a state that signal does not establish: it skipped the atomic writer
    entirely, appended the witness, cleared the journal and reported success.
    Measured: `REAL_WRITER first_exit 2 directory_fsync_attempts 2` then
    `REAL_WRITER retry_exit 0 fsync_calls 0 witnesses 1 journal False`.

    State B (durability unconfirmed) and state C (durable, witness absent) are
    INDISTINGUISHABLE by inspection -- that is the defect, not a limitation of
    the probe. So recovery does not decide which one it is in; it re-establishes
    the barrier unconditionally on the landed branch, which is a no-op in C and
    the repair in B. The bytes rewritten are the ones READ BACK from the
    destination, already validated by `_refuse_incoherent_landed_state`, so the
    re-write cannot introduce content the coherence gate did not admit.

    A persistent barrier failure must keep REFUSING with the journal retained:
    the whole point is that the witness may not be written and the recovery
    record may not be cleared while Layer 1's durability is unconfirmed.
    """
    try:
        landed_bytes = target.declaration_path.read_bytes()
        write_bytes_atomically(target.declaration_path, landed_bytes)
    except OSError as exc:
        print(
            f"Error completing the interrupted un-owning: the ownership "
            f"declaration {target.declaration_path.as_posix()!r} could not be "
            f"made durable: {exc}.\n"
            "Why forbidden: this run entered § Recovery Protocol state B or "
            "state C, which are INDISTINGUISHABLE from disk, so it did not "
            "guess between them -- it re-attempted the durability barrier that "
            "settles both, and the attempt FAILED. What is established: the "
            "declaration on disk carries the new floor and its "
            "`floor_event_id`, no ledger witness exists, and its durability is "
            "UNCONFIRMED. A visible declaration is not a durable one, so "
            "witnessing it now would let Layer 2 announce a floor a crash can "
            "still take back, and clearing the journal would destroy the only "
            "record able to re-apply it (REQ-0.35.0-04-05). The journal is "
            f"RETAINED at {target.journal_path.as_posix()!r} and no ledger "
            "witness was written.\n"
            f"{_barrier_next_step(target.declaration_path.parent, exc)}"
            "Each retry re-attempts the barrier "
            "and completes the SAME transition; nothing is witnessed or "
            "cleared until it succeeds. Do NOT delete the journal and do NOT "
            "hand-edit the declaration.",
            file=sys.stderr,
        )
        sys.exit(2)


def _refuse_unreadable_journal(target: _TransactionTarget, exc: OSError) -> NoReturn:
    """Refuse and exit 2: the journal could not be READ — a storage fault.

    Distinguished from `_refuse_forged_journal` because the two are different
    claims with different remedies, exactly as `_on_disk_declaration_or_refuse`
    distinguishes them on the declaration. A forged journal is one whose
    CONTENT cannot be proven to continue the live predecessor; a journal that
    could not be read has had no content examined at all, so the forgery
    refusal's enumeration of interruption states asks the operator to compare
    signals this run never obtained -- while the sentence that would actually
    recover them, restore read access and re-run, was printed nowhere.
    """
    print(
        f"Error: cannot read the pending-transition journal "
        f"{target.journal_path.as_posix()!r}: {exc}.\n"
        "Why forbidden: an interrupted un-owning is completed FROM its journal, "
        "and a journal that cannot be READ proves nothing about the transition "
        "either way -- this is a STORAGE FAULT, not evidence that the journal "
        "is malformed or forged, and reporting it as the latter sends you to "
        "compare `floor_event_id` against the ledger when the file was never "
        "examined (REQ-0.35.0-04-02). No ledger witness was written by this run "
        f"and the journal is RETAINED at {target.journal_path.as_posix()!r}, so "
        "the transition stays completable.\n"
        "  Restore read access to the journal -- check its permissions and the "
        "health of the mount under "
        f"{target.journal_path.parent.as_posix()!r} -- then re-run the same "
        "command to complete the pending transition. Do NOT delete the journal "
        "and do NOT hand-edit the ownership declaration.",
        file=sys.stderr,
    )
    sys.exit(2)


def _journal_record_or_refuse(target: _TransactionTarget) -> dict[str, Any]:
    """Read the pending-transition journal and prove it is REPLAYABLE, or refuse.

    Extracted from `_replay_pending_transition`, which crossed the xenon C
    ceiling again once the D+E arm landed (Step-4b round-11 finding 1). The
    seam is the one the round-3 and round-7 extractions already used: proving a
    journal MAY be replayed is a separate responsibility from deciding WHICH
    interruption state it is in, and an auditor asking "can a hand-authored
    journal reach the write path" should not have to read the state machine to
    answer it.

    Every check here is a refusal that exits. Reaching the return means the
    journal parses, carries every replayable field, names THIS target, carries
    a non-blank attestation, and re-mints its own `event_id` from its own
    content -- and nothing about the on-disk stores has been consulted yet.
    """
    record: Any = None
    defect: str | None = None
    try:
        record = json.loads(target.journal_path.read_text(encoding="utf-8"))
    except OSError as exc:
        # Same line its sibling `_on_disk_declaration_or_refuse` draws, and for
        # the same reason: an `OSError` is a statement about the STORE, never
        # about the journal's contents. Routing it to `_refuse_forged_journal`
        # printed forgery-class prose -- "cannot be proven to continue the live
        # on-disk predecessor" -- for a permission flip on a journal nobody
        # touched, and the remedy that actually applies appeared nowhere.
        _refuse_unreadable_journal(target, exc)
    except ValueError as exc:
        # Content that does not parse IS a claim about the contents, so it
        # keeps the refusal that enumerates the interruption states.
        defect = str(exc)
    if defect is None:
        # A journal that PARSES is not yet a journal that can be REPLAYED. An
        # interrupted write can leave valid JSON that is `null`, a list, or an
        # object missing fields; every one of those reaches a key lookup below
        # and escapes as a TypeError/KeyError traceback, past the three-part
        # prose this same branch supplies for the unparseable case. Shape is
        # checked here so both defects exit through one governed message.
        if not isinstance(record, dict):
            defect = f"expected a JSON object, found {type(record).__name__}"
        else:
            missing = [field for field in _JOURNAL_FIELDS if field not in record]
            if missing:
                defect = f"missing required field(s) {', '.join(missing)}"
    if defect is not None:
        _refuse_forged_journal(target, defect)

    # The journal's OWN `surface` is a value that reaches durable state: it is
    # what `_checked_landed_snapshot` resolves a declaration path from and what
    # `_append_event_once` writes into the witness. Resolving the identity at
    # transaction entry stops the CALLER's spelling reaching the ledger and
    # leaves this twin open -- on a case-insensitive filesystem a journal
    # naming `doc.md` passes the prior-floor, parent, span, eligibility and
    # derived-successor checks unchanged, then lands a witness the
    # declaration's own loader rejects. Same finding, second site; binding one
    # and not the other is the round-8 finding-1 asymmetry (round-9 finding 1).
    if record["surface"] != target.surface:
        _refuse_forged_journal(
            target,
            f"surface {record['surface']!r} is not this transaction's target "
            f"({target.surface!r}) -- a journal completes a transition for THIS "
            "target or none. The journal is a PAYLOAD: its identity is CHECKED "
            "against the target, never used to choose a path",
        )

    # The replay path takes the SAME fail-closed shape as the command path
    # for a blank attestor/reason (REQ-0.35.0-04-04) -- reuse the one
    # governed check rather than a second copy that could drift from it.
    _refuse_blank_attestation(
        record["surface"], record["section"], record["attestor"], record["reason"]
    )

    # `event_id` must re-mint from the record's OWN claimed content -- a
    # journal whose id does not match what `_mint_event_id` derives from its
    # own fields did not come from a real `_commit_transition` run.
    if _mint_event_id(record, record["parent_event_id"]) != record["event_id"]:
        _refuse_forged_journal(
            target,
            f"event_id {record['event_id']!r} does not re-mint from the journal's own content",
        )

    return record


def _on_disk_declaration_or_refuse(target: _TransactionTarget) -> dict[str, Any]:
    """Read the declaration the journal must be proven against, or refuse.

    Read RAW, never through `load_declaration`: a legitimate pending
    declaration names the very event recovery still has to append, so the
    canonical loader fails closed on exactly the state recovery exists to
    finish.

    An ABSENT declaration returns `{}` -- a real state the journal must be
    proven against, and the unlanded branch does prove it. An UNREADABLE one
    that exists is refused instead, because the two are different claims.
    """
    on_disk: dict[str, Any]
    try:
        on_disk = json.loads(target.declaration_path.read_text(encoding="utf-8"))
    except OSError as exc:
        # Same posture as `_declared_surface`: an OSError on a declaration that
        # EXISTS is transient, not a statement about its contents. Collapsing it
        # to `{}` made the identity check below report "the on-disk predecessor
        # declares identity None" -- an identity mismatch the operator cannot
        # act on, whose "re-run the same command" next step does not address a
        # permission flip or a failing disk. An absent declaration keeps falling
        # through as `{}`, which is a real state the journal must be proven
        # against.
        if not target.declaration_path.exists():
            on_disk = {}
        else:
            print(
                f"Error: cannot read the ownership declaration at "
                f"{target.declaration_path.as_posix()!r}: {exc}.\n"
                "Why forbidden: a journalled transition is completed by proving it "
                "continues the declaration ACTUALLY on disk, and a declaration that "
                "cannot be read proves nothing either way (REQ-0.35.0-04-02). The "
                f"journal is RETAINED at {target.journal_path.as_posix()!r}, so the "
                "transition stays completable.\n"
                "  Restore read access to the declaration, then re-run the same "
                "command to complete the pending transition.",
                file=sys.stderr,
            )
            sys.exit(2)
    except ValueError:
        on_disk = {}

    return on_disk


def _append_witness_or_exit(root: Path, target: _TransactionTarget, record: dict[str, Any]) -> None:
    """Append the transition's witness, or exit 2 in three-part prose.

    Idempotent by construction: `_append_event_once` returns without writing
    when the ledger already carries a row that MATCHES this witness
    semantically, and refuses when one merely wears its id (round-5 finding).
    That is why state D reaches this too -- the existing-row arm is what proves
    the present witness describes THIS transition, and it is the reason D
    preserves the witness without duplicating it.
    """
    try:
        _append_event_once(root, target, record)
    except OSError as exc:
        print(
            f"Error completing the interrupted un-owning of {record['section']!r}: "
            f"cannot append the ledger event: {exc}.\n"
            f"Why forbidden: {target.declaration_path.as_posix()!r} already carries "
            "the new floor, so "
            "its witness must be written for the declaration to load at all "
            "(REQ-0.35.0-04-02). The journal is retained, so nothing is lost.\n"
            "  Fix the ledger write, then retry the same command to complete it.",
            file=sys.stderr,
        )
        sys.exit(2)


def _replay_pending_transition(
    root: Path, target: _TransactionTarget, surface_text: str, surface_digest: str
) -> tuple[dict[str, Any], bool] | None:
    """Finish any journalled transition left behind by an interrupted run.

    Runs INSIDE the declaration lock and BEFORE `load_declaration`, because an
    interrupted run may have left a declaration naming a `floor_event_id` the
    ledger does not carry -- which the loader fails closed on, deliberately
    (REQ-0.35.0-04-02). Recovery therefore has to happen on the WRITE side:
    re-apply the journalled declaration if it never landed, complete the append
    under the SAME event id, then clear the journal. Returns the completed
    record PAIRED WITH whether THIS run committed it, or None when there was
    nothing pending. The pair is what lets the caller's success sentence stay
    true: in state D the transition was already durable and already witnessed,
    so this run writes no declaration and appends no event -- it only clears --
    and a report of "Completed the interrupted un-owning ... floor rose from A
    to B" would describe a DIFFERENT run. It is the same distinction
    `_refuse_clean_success_on_a_moved_surface` carries as `committed_now`, and
    it is derived from the same value.

    The journal is CRASH-RECOVERY STATE ONLY, never a second write path: every
    field is proven to CONTINUE the live on-disk predecessor before anything
    is written, so a hand-forged journal cannot mint a floor raise or an
    ownership flip that the real `content_unown_cmd` transition never
    produced (Step-4b adversary finding 2).
    """
    if not target.journal_path.exists():
        # The durability boundary and the orphan sweep this state owes were
        # already discharged by `_establish_recovery_boundary`, which the
        # caller runs before this replay. They live there because their RESULT
        # -- the identities of orphans that could not be removed -- has to
        # reach finalization, and this function's return type speaks only about
        # a pending transition.
        return None
    record = _journal_record_or_refuse(target)
    on_disk = _on_disk_declaration_or_refuse(target)

    # THE STATE IS SETTLED FROM BOTH SIGNALS BEFORE ANY ACTION IS CHOSEN.
    # § Recovery Protocol enumerates five states, but E is ORTHOGONAL to A-D
    # rather than a fifth alternative: a transition can be in state D *and*
    # have a changed source. Reading the digest first therefore made an
    # ordinary crash between the ledger append and the journal unlink, followed
    # by an ordinary editor save, refuse in state E's terms and demand a full
    # reconcile-and-restore -- when the transition was already complete and the
    # only outstanding action was clearing the journal. The E prose was false
    # there too: it says completing "would witness a span the surface no longer
    # has", and in D `_append_event_once` appends nothing at all.
    #
    # `settled` is D: the declaration points at this transition AND the ledger
    # carries its witness. Both are required -- a witness whose declaration
    # does not name it is not a completed transition, and the unlanded branch
    # still has to derive a successor from measured bytes.
    already_landed = on_disk.get("floor_event_id") == record["event_id"]
    settled = already_landed and _ledger_witness_present(root, record["event_id"])

    if not settled:
        # State E, and only where it can still bear on an outcome: every
        # remaining branch writes or witnesses something derived from the
        # measured bytes, so a surface that moved before this run started is
        # met by name rather than through whichever downstream guard first
        # notices a consequence of it.
        _refuse_source_changed_since_measurement(target, record, surface_digest)

    if not already_landed:
        # § Recovery Protocol state A -- the declaration write never landed, so
        # the journal must PROVE it continues the declaration actually on disk
        # rather than merely claim to. When it HAS landed, that proof is
        # unavailable by construction (the predecessor is gone) and the
        # coherence gate below is what guards the completion instead.
        _apply_unlanded_transition(target, record, on_disk, surface_text)

    # The coherence gate asks whether an interrupted transition may be
    # COMPLETED into a state the loader accepts. In D nothing is being
    # completed -- the declaration and its witness are both already durable --
    # so running it there would refuse on a surface condition this run neither
    # created nor can fix.
    #
    # THE SURVIVING DISCRIMINATOR IS WHICH PROSE THE OPERATOR MEETS, not what
    # residue is left. A second ground used to be stated here -- that refusing
    # in D "would leave journal residue that blocks every future un-owning" --
    # and it no longer separates the branches: the D+E path RETAINS the journal
    # by design (`_refuse_clean_success_on_a_moved_surface` applies in D since
    # the 2026-09-05 ruling), so a refusal in D leaves exactly that residue on
    # purpose. What the skip buys is that the operator meets the refusal naming
    # the state they are actually in, rather than a coherence complaint about a
    # transition nothing is completing.
    #
    # WHAT LICENSES THAT SKIP IS THE DIGEST BINDING, NOT THE SETTLED STATE. In
    # D the live surface is still observed -- by
    # `_refuse_source_changed_since_measurement` above and by
    # `_refuse_clean_success_on_a_moved_surface` below -- and BOTH return early
    # on a journal carrying no `surface_digest`, because neither can speak
    # about a surface the journal never versioned. On such a journal the skip
    # left NOTHING observing the live surface: the section-id coverage check
    # and the span-versus-floor check inside the gate are the only remaining
    # readers of it, and a legacy journal in D reached the witness and the
    # cleanup with every one of them unrun. Their own docstrings promise the
    # downstream guards compensate; on this path they did not.
    if not settled or record.get("surface_digest") is None:
        _refuse_incoherent_landed_state(target, record, surface_text)

    if already_landed and not settled:
        # States B and C. Validated FIRST, re-established SECOND: durability is
        # re-asserted only for a declaration the coherence gate above has just
        # proven is the transition this journal describes. Skipped in D, where
        # a witness could not exist unless the barrier had already succeeded.
        _reestablish_landed_declaration_durability(target)

    _append_witness_or_exit(root, target, record)

    # ONE finalization path (Step-4b round-8 finding 1). This branch used to
    # append and unlink without ever calling the digest guard
    # (`post_digest_guard_calls=0`), so recovery could report clean success
    # after the journalled surface moved -- the binding covered the fresh
    # commit and left its twin open. The coherence checks above are not a
    # substitute: they ran correctly, against the surface as it was before the
    # append.
    #
    # APPLIED IN D TOO (operator ruling 2026-09-05; Step-4b round-11 finding 1).
    # It was skipped there on the reasoning that this run commits nothing in D,
    # which is true and beside the point: the guard's subject is the SOURCE, not
    # this run's authorship. Skipping it let a retry clear the journal, the
    # retained source and the extract and exit 0 over a surface whose live span
    # exceeded the floor -- `D+E retry_exit 0 floor 83 span 102 journal False
    # snapshot False extract False`, then `advertised_raise alpha-section exit
    # 1`. `committed_now` carries the only real difference into the prose.
    # `_append_event_once` above still ran, and in D its existing-row arm is
    # what proves the witness already present describes THIS transition rather
    # than merely wearing its id (round-5 finding) -- so the witness is
    # preserved, never duplicated.
    _refuse_clean_success_on_a_moved_surface(target, record, committed_now=not settled)

    _clear_recovery_state(target)
    return record, not settled


def _commit_transition(
    root: Path,
    target: _TransactionTarget,
    record: dict[str, Any],
    surface_bytes: bytes,
    already_warned: frozenset[str],
) -> None:
    """Retain the source, journal, write the declaration, witness it, then clear.

    This command updates TWO stores -- a mutable declaration and an APPEND-ONLY
    ledger -- and NEITHER order is safe on its own. Declaration-first can leave
    a `floor_event_id` naming an event that does not exist; ledger-first can
    leave an event announcing a floor that was never adopted. The order here is
    declaration-then-ledger (a witness must never outlive the state it
    witnesses) made RECOVERABLE by the journal: the pending transition is
    durable before either store is touched, so an interrupted run is completed
    by the next one rather than tolerated -- and `load_declaration` keeps
    failing closed on an unresolvable chain pointer, unweakened.

    The MEASURED SOURCE BYTES are retained FIRST, before the journal that names
    their digest exists, so a journal is never on disk without the material
    § Recovery Protocol state E needs to reconcile against (round-10 finding 2).
    They are cleared with the journal by `_clear_recovery_state`.
    """
    try:
        write_bytes_atomically(target.journal_source_path, surface_bytes)
    except OSError as exc:
        print(
            f"Error retaining the measured source of {target.surface!r}: cannot "
            f"write {target.journal_source_path.as_posix()!r}: {exc}.\n"
            "Why forbidden: a pending transition is completed by proving the "
            "surface still carries the bytes its floor was measured against, and "
            "§ Recovery Protocol state E is reconciled from those bytes -- a "
            "journal written without them can be blocked by an ordinary editor "
            "save with no route back (REQ-0.35.0-04-05). The ownership "
            "declaration, the ledger and the journal are ALL untouched -- this "
            "is the first write of the transaction. This write itself is not "
            "provably all-or-nothing: the durability barrier runs after the "
            "atomic swap, so the retained-source file may or may not have "
            "landed. Nothing reads it while no journal exists, and the next "
            "attempt overwrites it.\n"
            "  Check file/directory permissions and disk space under "
            f"{target.journal_source_path.parent.as_posix()!r}, then retry the "
            "same command.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        write_declaration_atomically(target.journal_path, json.dumps(record, indent=2) + "\n")
    except OSError as exc:
        print(
            f"Error journalling the un-owning of {record['section']!r}: "
            f"cannot write {target.journal_path.as_posix()!r}: {exc}.\n"
            "Why forbidden: the pending transition is recorded before either "
            "store is touched so an interrupted raise can be completed rather "
            "than left unrecoverable (REQ-0.35.0-04-02). The ownership "
            "declaration and the ledger are BOTH unchanged -- but this write is "
            "not provably all-or-nothing: the durability barrier runs after the "
            "atomic swap, so the journal file itself may or may not have "
            "landed.\n"
            "  Check file/directory permissions and disk space, then retry the "
            "same command; a journal that did land is re-validated against the "
            "declaration on disk before it is replayed.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        write_declaration_atomically(target.declaration_path, record["declaration_json"])
    except OSError as exc:
        # The journal is RETAINED here (Step-4b round-3 finding 3). This branch
        # used to delete it and report "Nothing written" on the premise that the
        # write was all-or-nothing, so an error proved the declaration
        # byte-unchanged. That premise DIED when the parent-directory fsync
        # barrier was added: it runs AFTER `os.replace` has already swapped the
        # file, so an OSError here may mean the declaration carries the new floor
        # while no ledger witness exists. Deleting the journal on that path
        # destroyed the only record able to complete the transition and left a
        # declaration the loader rejects forever -- while telling the operator
        # nothing had happened. Measured: `floor_changed=True`,
        # `ownership_event_count=0`, `journal_exists=False`,
        # `post_failure_load=REJECTED`.
        #
        # Retaining is safe in BOTH directions: if the replace genuinely never
        # landed, the next run replays the journal and every check above
        # re-validates it against the declaration actually on disk.
        print(
            f"Error writing ownership declaration "
            f"{target.declaration_path.as_posix()!r}: {exc}.\n"
            "Why forbidden: the declaration must carry the new floor durably "
            "BEFORE its ledger witness is written -- Layer 2 may never announce "
            "a floor Layer 1 does not carry (REQ-0.35.0-04-05). This write is "
            "NOT provably all-or-nothing: the durability barrier runs after the "
            "atomic swap, so the declaration may or may not already carry the "
            "new floor. The journal is RETAINED so the transition stays "
            "completable either way.\n"
            "  Check file/directory permissions and disk space, then retry the "
            "same command to complete it.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        _append_event_once(root, target, record)
    except OSError as exc:
        print(
            f"Error writing ledger event for {target.surface!r}/"
            f"{record['section']!r}: {exc}. "
            f"THE UN-OWNING ALREADY HAPPENED — {target.declaration_path.as_posix()!r} is on "
            "disk with the new floor, but the ledger witness is incomplete.\n"
            "Why forbidden: the declaration now names a `floor_event_id` the "
            "ledger does not carry, so it fails closed on every subsequent "
            "load until the witness is written -- Layer 1 and Layer 2 must "
            "agree on the floor (REQ-0.35.0-04-05). The recovery is the "
            "retry below, never a hand-edit of the declaration.\n"
            f"  The transition is journalled at {target.journal_path.as_posix()!r}: fix "
            "the ledger write and retry the SAME command to complete it, then "
            "verify with `gz validate --ledger`.",
            file=sys.stderr,
        )
        sys.exit(2)

    _refuse_clean_success_on_a_moved_surface(target, record, committed_now=True)

    _clear_recovery_state(target, already_warned=already_warned)


def _remove_if_present(path: Path) -> OSError | None:
    """Remove *path*, tolerating only its EXPECTED ABSENCE. Report anything else.

    ABSENCE IS A CLASS, NOT ONE ERRNO. `FileNotFoundError` is its ordinary
    spelling; `NotADirectoryError` is the same fact reported one component
    further up -- a parent path element has been replaced by a FILE, so nothing
    can exist under that path at all. Both mean the obligation this cleanup
    exists to discharge is already discharged. Escalating the second sends the
    operator to check disk space and mount health for a target the filesystem
    is telling them is not there.

    Every OTHER `OSError` is a STORAGE FAULT -- a read-only mount, a failing
    disk, a directory whose permissions changed, or (on Windows, co-equal per
    `.claude/rules/cross-platform.md`) a `PermissionError` because another
    process holds the file open. Those are reported, because the file IS there
    and was NOT removed; what they need is a remedy list that names the
    condition, which is why `_refuse_cleanup_pending` names the held-open file
    alongside permissions and disk space. The two classes have different
    remedies, exactly as `_on_disk_declaration_or_refuse` distinguishes them on
    the read side.

    Suppressing the whole class made a removal that did NOT happen
    byte-indistinguishable from one that did (Step-4b round-11 finding 2):
    `journal_unlink_failed exit 0 journal True snapshot False
    diagnostic_mentions_IO_fault False`.
    """
    try:
        path.unlink()
    except (FileNotFoundError, NotADirectoryError):
        return None
    except OSError as exc:
        return exc
    return None


def _staging_residue(path: Path) -> list[Path]:
    """Every `write_bytes_atomically` staging file left beside *path*.

    The writer stages `.<name>.<random>.tmp` in the TARGET's directory and then
    renames, so an interruption between the two leaves a COMPLETE COPY of the
    bytes under a name the final target never mentions. For the extract that is
    a copy of the measured source sitting beside a tracked Layer-1 surface,
    which is the same hazard the final extract's own cleanup exists to close
    (operator ruling 2026-09-05 point 4: *"Handle the complete extraction-file
    family. Cover final and temporary filenames in ignore rules and recovery
    cleanup."*). Measured at round 11: `EXTRACT_CRASH residue
    ['.doc.md.unowning-recovery.3.tmp'] RESIDUE_IS_MEASURED_SOURCE True`,
    retained across a successful recovery.

    Enumeration errors propagate: an unreadable directory is not an empty
    sweep. `Path.glob` suppresses those errors, so use `iterdir` instead.

    THE NAME IS DATA, NEVER A PATTERN. A surface filename carrying `[`, `]`,
    `*` or `?` -- all legal on every supported platform -- is a glob expression
    once interpolated, and the failure is not merely a miss: `a[1].md` reads as
    a character class, so the sweep looks for `a1.md`'s residue instead. It
    would then leave its own complete copy of the measured source bytes in
    place and remove a stranger's, which is the opposite of both obligations.
    Literal prefix/suffix matching keeps metacharacters inert.
    """
    prefix = f".{path.name}."
    return sorted(
        candidate
        for candidate in path.parent.iterdir()
        if candidate.name.startswith(prefix) and candidate.name.endswith(".tmp")
    )


_TWO_OF_THREE_DISCHARGED = (
    "Why forbidden: THREE OBLIGATIONS ARE SEPARATE HERE and exactly two are "
    "discharged -- transition witnessed; source reconciled; RECOVERY CLEANUP "
    "PENDING."
)
_NO_HAND_EDIT = (
    "Do NOT hand-edit the ownership declaration: its floor is witnessed by a real ledger event"
)
"""The two sentences `_refuse_cleanup_pending` and its BARRIER sibling share.

Both fire with the transition complete and the third obligation outstanding, so
both state the same accounting and give the same hand-edit warning -- and they
carried it as byte-identical prose in two places, in a module that extracted
`commit_directory_entry` and `exclusive_file_lock` to stop exactly that (GHI
#945). Two copies of one sentence drift the way two implementations do.

This shares nothing with the ORPHAN twin, and that separation is deliberate:
`_warn_orphan_residue_pending` fires where no transition completed, so neither
sentence is available to it. What is single-sourced here is what the two
COMPLETED-transition reports genuinely have in common, never a flag selecting
prose across paths that establish different facts.
"""

_CLEANUP_REMEDIES = (
    "file and directory permissions, disk space, a read-only mount, or another "
    "process holding the file open (the extract is the file the reconcile "
    "sequence tells you to open in a diff tool, and Windows refuses to unlink a "
    "file that is still open)"
)


def _refuse_cleanup_pending(
    target: _TransactionTarget, path: Path, exc: OSError, *, dependents_retained: bool
) -> NoReturn:
    """Refuse and exit 2: THIS run's transition completed, its cleanup did NOT.

    Reached ONLY from `_clear_recovery_state` and from the post-completion
    sweep it performs, so every claim below is something this run established:
    the declaration is durable, the ledger carries the witness, and
    `_refuse_clean_success_on_a_moved_surface` let the run through, which is
    what discharges the source obligation.

    ITS ORPHAN TWIN IS A SEPARATE FUNCTION ON PURPOSE, sharing not one sentence
    with this one. `_warn_orphan_residue_pending` -- which WARNS rather than
    refusing, per the operator ruling below -- serves the journal-absent sweep,
    where no transition was completed and none of these claims are
    available. Selecting between the two inside one body with a flag is how
    this refusal came to assert a completed un-owning, a discharged source
    reconciliation and § Recovery Protocol state D on a path reachable by a
    crash during the transaction's FIRST write -- which leaves staging residue
    and nothing else. The split is also what lets the two carry different
    OUTCOMES without one's prose leaking into the other.

    THE THIRD OBLIGATION, REPORTED ON ITS OWN TERMS (operator ruling
    2026-09-05: *"Keep three obligations separate: the transition is durably
    witnessed; the source is reconciled; recovery cleanup is complete.
    Establishing one does not discharge the others."*). Two are discharged when
    this fires -- that is why the prose says so rather than implying a failed
    transition -- and reporting success anyway would hide a storage fault that
    never heals on its own, while every later run replays the same completed
    transition from a journal nothing can remove.
    """
    if dependents_retained:
        residue = (
            "Its dependent recovery material is RETAINED -- the journal is what "
            "`gz content unown` gates replay on, so material that outlives a failed "
            "journal removal stays usable, where material deleted under one does "
            f"not. That journal keeps gating every un-owning of {target.surface!r} "
            "until it can be removed."
        )
    else:
        # The journal was removed by THIS run, one statement earlier in
        # `_clear_recovery_state`, so its absence is observed rather than
        # assumed -- and nothing gates replay any more. What is NOT said here is
        # that a later run sweeps it: while the condition persists, the next run
        # attempts the same removal and reports the same fault.
        residue = (
            "This run removed the journal itself, so what remains gates nothing and "
            "no later run replays it. It is still a complete copy of measured source "
            "bytes beside a tracked surface, which is why it is reported rather than "
            "passed over."
        )
    print(
        f"Error: the un-owning of {target.surface!r} is complete, but its recovery "
        f"material could not be cleared: cannot remove {path.as_posix()!r}: {exc}.\n"
        f"{_TWO_OF_THREE_DISCHARGED} "
        "This is § Recovery Protocol state D with cleanup outstanding. "
        "An attempted unlink does not establish that anything was removed, and a "
        "suppressed failure is reported as success while the material is still "
        f"there (REQ-0.35.0-04-02). {residue}\n"
        f"  Fix the underlying condition -- {_CLEANUP_REMEDIES} -- under "
        f"{path.parent.as_posix()!r}, then re-run the same command. Each retry "
        "re-attempts every removal still outstanding; while the condition "
        f"persists a retry finds the same material and reports it again. "
        f"{_NO_HAND_EDIT} and the transition itself is sound.",
        file=sys.stderr,
    )
    sys.exit(2)


_BARRIER_REMEDIES = (
    "a full or failing disk, a read-only mount, or a directory whose permissions changed"
)
"""Conditions a RETRY can clear -- the only ones a re-run remedy may name.

This list used to end with *"an export (NFS, a network share) that cannot fsync
a directory"*, on refusals whose entire next step is "re-run the same command".
A filesystem without the operation is not a condition the operator clears by
retrying, and naming it here told them to re-run against a fault no re-run
reaches. `_barrier_next_step` gives unsupported operations a different remedy;
both kinds of failure preserve recovery material and refuse.
"""


def _establish_durable_journal_absence(
    target: _TransactionTarget, *, removed_by_this_run: bool
) -> None:
    """Commit the journal's ABSENCE before any dependent is deleted or reused.

    THE INVARIANT HERE IS CROSS-FILE ORDERING, NEVER ONE REMOVAL'S OWN
    DURABILITY. This module used to argue no barrier was needed because *"a
    crash can land before the fsync exactly as easily as before the unlink"* --
    true of a single file, and beside the point. What every later run relies on
    is that a journal that SURVIVES keeps all of its material: the journal
    gates replay, so its dependents may never predecease it. Nothing without a
    barrier between the journal's unlink and the dependents' unlinks forbids
    the dependents' directory-entry removals being committed while the
    journal's is not -- journal back, retained source gone, which is Step-4b
    round-11 finding 2 restated by the filesystem instead of by the code. The
    artifacts also span TWO directories (journal and retained source under
    `.gzkit/ownership/`, the extract beside the surface), so the ordering the
    barrier establishes is not one directory's internal affair either.

    RUN ON BOTH ENTRIES, because both move dependents. `_clear_recovery_state`
    reaches here having just removed the journal. The journal-absent entry
    reaches here having removed nothing at all -- and it still needs the
    boundary, because it both DELETES the orphan dependents and REUSES one of
    their paths: `_commit_transition` writes the retained source at the start
    of every fresh transaction. An absence nobody committed is an absence a
    crash can take back.

    The barrier itself is `gzkit.content.ownership.commit_directory_entry` --
    the SAME statement of the discipline `write_bytes_atomically` ends with,
    extracted rather than restated. Two descriptions of one durability
    discipline drift the way two implementations do (GHI #945).

    An unsupported directory sync also leaves this boundary unestablished.
    It changes the remedy, never the preservation and non-success requirements.

    *removed_by_this_run* selects between two refusals that share no sentence,
    for the reason `_refuse_cleanup_pending` and `_warn_orphan_residue_pending`
    are separate functions: the two entries establish different facts, and
    choosing prose inside one body with a flag is how a refusal came to assert
    a completed un-owning on a path where nothing was un-owned.
    """
    try:
        commit_directory_entry(target.journal_path.parent)
    except OSError as exc:
        if removed_by_this_run:
            _refuse_unbarriered_journal_removal(target, exc)
        _refuse_unbarriered_orphan_boundary(target, exc)


def _barrier_next_step(directory: Path, exc: OSError) -> str:
    """Distinguish an unavailable required operation from a transient storage fault."""
    if exc.errno in BARRIER_UNSUPPORTED_ERRNOS:
        return (
            f"  The required directory sync is unsupported or invalid at {directory.as_posix()!r}. "
            "Repeating under unchanged conditions cannot establish durability. Preserve the "
            "recovery material and use an environment where the required directory sync "
            "succeeds before retrying. "
        )
    return (
        f"  Fix the underlying condition -- {_BARRIER_REMEDIES} -- under "
        f"{directory.as_posix()!r}, then re-run the same command. "
    )


def _refuse_unbarriered_journal_removal(target: _TransactionTarget, exc: OSError) -> NoReturn:
    """Refuse and exit 2: THIS run removed the journal, and the removal is not durable.

    Reached only from `_clear_recovery_state`, so the transition is complete:
    the declaration is durable, the ledger carries the witness, and the source
    obligation was discharged before cleanup began. What is outstanding is the
    THIRD obligation, and specifically its ordering half.

    The dependents are RETAINED, which is the whole point of refusing here. The
    unlink made the journal invisible; the barrier is what makes it gone, and
    until it succeeds a crash may leave the journal's directory entry intact.
    Removing the retained source under that uncertainty is the one outcome
    recovery cannot survive -- a surviving journal whose reconciliation
    material no longer exists.
    """
    print(
        f"Error: the un-owning of {target.surface!r} is complete, but the removal of "
        f"its pending-transition journal {target.journal_path.as_posix()!r} could not "
        f"be made durable: {exc}.\n"
        f"{_TWO_OF_THREE_DISCHARGED} "
        "A directory entry removed by `unlink` is buffered metadata until "
        "the parent directory is synced, so the journal is INVISIBLE but not yet "
        "GONE. Its dependent recovery material is RETAINED and NOT removed: the "
        "journal gates replay, so deleting the retained source while the journal's "
        "absence can still be taken back is the one ordering recovery cannot "
        "survive -- a journal that comes back with its measured source destroyed "
        "(REQ-0.35.0-04-02). The un-owning itself is sound and no later run "
        "repeats it.\n"
        f"{_barrier_next_step(target.journal_path.parent, exc)}"
        "The unlink SUCCEEDED -- only its barrier did not -- so the next run finds "
        "no journal and re-attempts the BARRIER ALONE, through the journal-absent "
        "boundary, which names this same directory. Nothing dependent is cleared "
        f"until that barrier succeeds. {_NO_HAND_EDIT}.",
        file=sys.stderr,
    )
    sys.exit(2)


def _refuse_unbarriered_orphan_boundary(target: _TransactionTarget, exc: OSError) -> NoReturn:
    """Refuse and exit 2: no journal on entry, and that absence is not durable.

    AN ORPHAN SWEEP REPORTS ONLY WHAT IT OBSERVED (operator ruling
    2026-09-05), so this claims no transition, no witness and no § Recovery
    Protocol state -- the same discipline `_warn_orphan_residue_pending`
    carries, and for the same reason: a run that found no journal completed
    nothing and cannot say which transition left the material behind.

    IT REFUSES WHERE ITS SIBLING WARNS, and that is the ruling's own split. A
    failed REMOVAL of unrelated orphan residue warns and permits fresh work; a
    failed BOUNDARY does not, because everything after it -- the sweep's
    deletions and `_commit_transition`'s reuse of the retained-source path --
    rests on the absence this barrier commits. Nothing is deleted, nothing is
    written, and the ordinary transaction is not started.
    """
    print(
        f"Error: no pending-transition journal exists at "
        f"{target.journal_path.as_posix()!r}, but that absence could not be made "
        f"durable: {exc}.\n"
        "Why forbidden: a directory entry is buffered metadata until the parent "
        "directory is synced, so an absence nobody committed is one a crash can "
        "take back. This run would next DELETE the recovery material that outlived "
        "that journal and REUSE one of its paths for a fresh transaction's retained "
        "source -- and both moves rest on the journal being gone for good. If it "
        "returns while its material has been removed or overwritten, every later "
        "run replays a transition it can no longer reconcile (REQ-0.35.0-04-02). "
        "This run completed nothing, witnessed nothing and wrote nothing: the "
        "recovery material is PRESERVED exactly as it was found and the ownership "
        "declaration is byte-unchanged.\n"
        f"{_barrier_next_step(target.journal_path.parent, exc)}"
        "The retry re-attempts the boundary before touching anything. Do NOT hand-edit "
        "the ownership declaration: this run read nothing from it and establishes "
        "nothing about it.",
        file=sys.stderr,
    )
    sys.exit(2)


def _warn_orphan_residue_pending(
    target: _TransactionTarget, failures: list[tuple[Path, OSError]]
) -> None:
    """Warn on stderr: ORPHAN recovery material could not be removed. Then continue.

    AN ORPHAN SWEEP REPORTS ONLY WHAT IT OBSERVED (operator ruling 2026-09-05).
    This fires on the journal-absent path, where the run has completed nothing,
    witnessed nothing and written nothing -- so it states the journal's ABSENCE,
    which is the whole of what it knows, and claims no transition at all.

    IT WARNS RATHER THAN REFUSING, and the ruling draws that line by CAUSE, not
    by severity: *"failed removal of unrelated orphan residue may warn and
    permit fresh work"*, while *"cleanup failure belonging to the current
    transaction remains non-success"*. This material belongs to some earlier
    run the journal that would name it no longer exists to name. Refusing here
    made an old leftover under a persistent storage condition block every
    subsequent un-owning of the surface -- a run answering for a fault it did
    not cause. What is NOT relaxed: the durability boundary above it, which
    still refuses (`_refuse_unbarriered_orphan_boundary`), and the ordinary
    transaction below it, which still validates its declaration and still
    retains its own measured source. A warning buys no shortcut past either.

    Its twin `_refuse_cleanup_pending` said otherwise on this exact path, and
    every sentence of it was unsupported: *"the un-owning of <surface> is
    complete"*, *"exactly two are discharged -- transition witnessed; source
    reconciled"* and *"§ Recovery Protocol state D with cleanup outstanding"*.
    A crash during `_commit_transition`'s FIRST `write_bytes_atomically` -- the
    retention of the measured source, before the journal naming its digest
    exists -- reaches here with no journal, no declaration change and no
    witness anywhere, so nothing was un-owned and no § Recovery Protocol state
    applies. The message also contradicted itself, saying the journal *"keeps
    gating every un-owning"* one sentence after saying it was *"already gone"*.
    This is the class `_refuse_forged_journal`'s docstring already names:
    *"a premise it cannot know is the defect, whichever direction it points."*

    WHAT THIS SWEEP CANNOT SAY, and therefore does not: which transition left
    the material, or whether that transition completed. The journal that would
    settle both is gone, and the sweep does not guess between them.

    NOR DOES IT SPEAK FOR THE REST OF THE RUN. Its refusing predecessor could
    say *"this run completed nothing, witnessed nothing and wrote nothing"*
    because it terminated the invocation on the spot. A WARNING does not: the
    ordinary transaction proceeds underneath it, so that sentence would be
    contradicted a few lines later by *"Un-owned section ... floor rose from A
    to B"* in the same console. An orphan sweep reports only what it observed
    (operator ruling 2026-09-05), and what it observed is the MATERIAL and the
    journal's absence -- never the outcome of work that has not happened yet.

    EVERY un-removed path is named, not merely the first: the operator cannot
    act on material the report does not mention, and this run is not going to
    stop on any of them.
    """
    named = "\n".join(f"    - {path.as_posix()!r}: {exc}" for path, exc in failures)
    print(
        f"Warning: recovery material for {target.surface!r} outlived its "
        "pending-transition journal and could not be removed:\n"
        f"{named}\n"
        "Why it is only a warning: this sweep found no journal at "
        f"{target.journal_path.as_posix()!r}, so it cannot say which transition "
        "left this material behind, or whether that transition finished -- the "
        "journal that would settle either question is gone. What it CAN see is a "
        "file that gates no replay and that nothing reads, holding a complete "
        "copy of measured source bytes beside a tracked surface. That is an "
        "EARLIER run's residue, so it does not make THIS run fail, and it is not "
        "reported again at finalization as this transaction's cleanup: the "
        "journal's absence has been made durable, so fresh work may proceed over "
        "it (REQ-0.35.0-04-02). Whatever this run does next is reported on its "
        "own terms below.\n"
        f"  Fix the underlying condition -- {_CLEANUP_REMEDIES} -- under "
        f"{target.declaration_path.parent.as_posix()!r} and "
        f"{target.surface_path.parent.as_posix()!r}, then re-run the same "
        "command, which re-attempts the removal; while the condition persists "
        "every run finds the same material and reports it again. Do NOT "
        "hand-edit the ownership declaration: this sweep read nothing from it "
        "and establishes nothing about it.",
        file=sys.stderr,
    )


def _journal_dependents(
    target: _TransactionTarget,
) -> tuple[list[Path], list[tuple[Path, OSError]]]:
    """Every artifact whose only purpose was to serve the journal.

    The two NAMED dependents -- the retained measured source and the extract
    beside the surface -- plus the staging residue of all three recovery paths,
    the journal's own included: `write_bytes_atomically` stages a COMPLETE COPY
    of the bytes under a name the final target never mentions, so a sweep that
    listed only final names would leave the very material it exists to remove.
    """
    dependents = [target.journal_source_path, target.recovery_extract_path]
    inspection_failures = []
    for named in (target.journal_path, target.journal_source_path, target.recovery_extract_path):
        try:
            dependents.extend(_staging_residue(named))
        except OSError as exc:
            inspection_failures.append((named, exc))
    return dependents, inspection_failures


def _report_recovery_inspection_failure(
    target: _TransactionTarget, failures: list[tuple[Path, OSError]], *, after_completion: bool
) -> None:
    """Report unknown file families without claiming observed orphan identities."""
    details = "; ".join(
        f"cannot inspect {path.parent.as_posix()!r} for staging files with literal prefix "
        f"{f'.{path.name}.'!r} and suffix '.tmp': {exc}"
        for path, exc in failures
    )
    if after_completion:
        disposition = f"Error: recovery cleanup for {target.surface!r} is incomplete"
    else:
        disposition = "Warning: no pending-transition journal was found, but residue is unverified"
    print(
        f"{disposition}: {details}.\n"
        "The directory contents are unknown; no successful sweep or set of old files was "
        "established. Recovery material is retained. A new transaction must still persist "
        "its own measured source and complete its own cleanup.\n"
        f"  Restore directory read access and storage health, then retry. {_NO_HAND_EDIT}.",
        file=sys.stderr,
    )
    if after_completion:
        sys.exit(2)


def _failed_removals(paths: list[Path]) -> list[tuple[Path, OSError]]:
    """Attempt EVERY removal, then report the ones that failed, in order.

    Every removal is attempted before any failure is reported, so one faulty
    file cannot shelter the rest behind it -- the caller decides what to do
    with the set, and it can only decide over a set that was actually gathered.
    """
    return [
        (path, failure)
        for path, failure in ((path, _remove_if_present(path)) for path in paths)
        if failure is not None
    ]


def _sweep_recovery_residue(
    target: _TransactionTarget,
    *,
    after_completion: bool,
    already_warned: frozenset[str] = frozenset(),
) -> frozenset[str]:
    """Remove every artifact whose only purpose was to serve the journal.

    Called on BOTH sides of the journal's life, and *after_completion* is which
    side: True from `_clear_recovery_state`, where THIS run has just completed
    and witnessed the transition and removed its journal; False from the
    journal-absent entry, where the run knows only that residue exists. A sweep
    may only assert what its own caller established, and the orphan side
    established nothing -- so the two sides differ in OUTCOME as well as prose:
    the completion side refuses, the orphan side warns and returns.

    A RETRY IS NOT PROMISED LESS WORK: under a
    read-only mount or a directory permission flip NO removal lands, so the
    next run finds exactly the same set -- and those are the very conditions
    the reports' own remedy lists name.

    THE RETURN VALUE IS WHAT KEEPS AN OLD LEFTOVER OLD (operator ruling
    2026-09-05: *"Keep orphan warnings distinct through finalization; do not
    reclassify the same old leftover as a failure of the new transaction's
    cleanup."*). The orphan side returns the paths it warned about; the
    completion side is handed them back as *already_warned* and reports only
    what is NOT among them. Without that, the post-completion sweep meets the
    same persistent storage condition, and a completed and witnessed un-owning
    exits non-zero blaming a file an earlier run left -- the mirror of the
    false-premise defect `_warn_orphan_residue_pending` exists to correct.

    THE RETAINED SOURCE IS DELIBERATELY EXCLUDED from the carried set.
    `_commit_transition` REUSES that path for every fresh transaction, so by
    finalization the file living there is THIS run's measured source and a
    removal failure on it is this run's own cleanup failure. Carrying it would
    be a blanket suppression wearing the ruling's name.
    """
    dependents, inspection_failures = _journal_dependents(target)
    if inspection_failures:
        _report_recovery_inspection_failure(
            target, inspection_failures, after_completion=after_completion
        )
        return frozenset()
    failures = _failed_removals(dependents)
    if not failures:
        return frozenset()
    if not after_completion:
        _warn_orphan_residue_pending(target, failures)
        return frozenset(
            path.as_posix() for path, _ in failures if path != target.journal_source_path
        )
    unreported = [(path, exc) for path, exc in failures if path.as_posix() not in already_warned]
    if unreported:
        path, failure = unreported[0]
        _refuse_cleanup_pending(target, path, failure, dependents_retained=False)
    return frozenset()


def _establish_recovery_boundary(target: _TransactionTarget) -> frozenset[str]:
    """Make an ALREADY-ABSENT journal durably absent, then sweep what outlived it.

    RETRIES MUST HANDLE RESIDUAL ARTIFACTS EVEN WHEN THE JOURNAL IS ALREADY
    ABSENT (operator ruling 2026-09-05). The deletions in
    `_clear_recovery_state` are not one atomic act, so a crash or a removal
    that failed on a dependent leaves recovery material with nothing left to
    gate it: `_replay_pending_transition` read that as "nothing pending" and no
    other path looked, so a copy of the measured source accumulated beside a
    tracked Layer-1 surface indefinitely.

    THE BOUNDARY COMES FIRST, on an entry that removed no journal. The sweep
    DELETES those dependents and `_commit_transition` REUSES one of their paths
    for the fresh transaction's retained source, and both moves rest on this
    journal being gone for good rather than merely unseen.

    It runs from `content_unown_cmd` rather than from inside the replay because
    its RESULT outlives the replay: the warned orphan identities travel to
    finalization, and a function that returns None to a caller that discards it
    cannot carry them.
    """
    if target.journal_path.exists():
        return frozenset()
    _establish_durable_journal_absence(target, removed_by_this_run=False)
    return _sweep_recovery_residue(target, after_completion=False)


def _clear_recovery_state(
    target: _TransactionTarget, *, already_warned: frozenset[str] = frozenset()
) -> None:
    """Clear the journal, then every piece of material that depends on it.

    ONE clearing path, called only where the transition is complete: the
    declaration is durable, its witness is in the ledger, and the surface still
    carries the bytes the floor was measured against.

    THE JOURNAL GOES FIRST AND ITS FAILURE STOPS THE REST. It is what
    `_replay_pending_transition` gates on, so the dependent material must
    outlive a failed journal removal -- a journal that survives while its
    retained source is deleted leaves every later run recovering a transition
    whose reconciliation material is gone, which is round-11 finding 2 exactly.

    INTERRUPTION BETWEEN THE DELETIONS IS ACCOUNTED FOR BY ORDER, BY THE SWEEP,
    AND BY A DURABILITY BARRIER BETWEEN THEM. The ordering buys that either
    outcome is recoverable: a journal that survives keeps all of its material
    and is replayed and cleared normally, and a journal that is gone leaves
    inert residue the journal-absent sweep removes on the next run. The barrier
    is what makes the second half of that sentence TRUE OF THE FILESYSTEM and
    not merely of this function's statement order -- see
    `_establish_durable_journal_absence`.

    Directory-sync errors preserve dependents and refuse, including unsupported
    operations. The shared helper syncs a directory descriptor on POSIX and
    completes a native directory flush on Windows. Both require the filesystem
    and storage to honor the requested synchronization boundary.

    THE RETIRED ARGUMENT, NAMED SO IT IS NOT RE-DERIVED. This docstring used to
    claim no barrier was needed because *"a crash can land before the fsync
    exactly as easily as before the unlink, so the barrier would narrow no
    window here"*. That is true of ONE removal's own durability and says
    nothing about the invariant actually relied upon, which is CROSS-FILE
    ORDERING: without a barrier between the journal's unlink and the
    dependents', nothing forbids the dependents' entry removals being committed
    while the journal's is not. Operator-ruled mandatory 2026-09-05.
    """
    failure = _remove_if_present(target.journal_path)
    if failure is not None:
        # The dependents are NOT touched. The journal gates replay, so its
        # dependents may never predecease it.
        _refuse_cleanup_pending(target, target.journal_path, failure, dependents_retained=True)
    _establish_durable_journal_absence(target, removed_by_this_run=True)
    # *already_warned* is what this run reported on ENTRY, before its own
    # transaction began. Those paths are an earlier run's residue, so meeting
    # them again here is not a failure of this transaction's cleanup.
    _sweep_recovery_residue(target, after_completion=True, already_warned=already_warned)


def _reconciliation_sequence(target: _TransactionTarget, step_four: str) -> str:
    """Build the ONE reconcile-and-restore script every source-changed refusal prints.

    Single-sourced across the three CALL PATHS that reach § Recovery Protocol
    state E -- `_refuse_source_changed_since_measurement`, the finalization
    binding, and the replay's D+E arm, the last two of which share one print
    site -- because they differ ONLY in what step 4's re-run has left to do.
    The first is NOT "the pre-flight refusal": this module assigns that name to
    `_refuse_surface_changed_under_us`, which runs before the journal write and
    never prints this sequence. Copies of a
    multi-step script drift, and this one already drifted into an instruction
    the command could not keep.

    Printed ONLY where the extract it names exists: `_extract_retained_source`
    reports whether a verified extraction completed, and its failure branches carry
    their own next step instead of this one.

    STEP 5 WAS A LIE AND IS GONE (operator ruling 2026-09-05, Step-4b round-11
    finding 1). It read *"re-apply your saved edit and, if it changed a
    section's span, record it through `gz content unown` again"* -- and an
    operator executing it verbatim ends with a surface whose unowned span
    exceeds the recorded floor, which `load_declaration` fails closed on, so
    the very command named as the remedy refuses at its own initial load.
    Operator verbatim: *"Do not instruct users to reapply an oversized edit and
    then invoke a command whose initial loader rejects it."* The sequence now
    ENDS at step 4 with a declaration the loader accepts, and re-application is
    named for what it is -- a separate decision subject to the ratchet.

    Step 1 sends the operator's copy OUTSIDE the repository deliberately. A
    surface is a tracked Layer-1 file, `AGENTS.md` § Execution Rules mandates
    `git add -A` before `gz check`, and a full copy of canon saved beside it
    under an unignored name is STAGED rather than merely noticed -- the same
    hazard the `.gitignore` rules for the retained material exist to close.
    """
    return (
        "Reconcile in this order, which preserves your edit and ends with a "
        "declaration `load_declaration` accepts: 1. save your current work -- "
        f"copy {target.surface_path.as_posix()!r} to a path OUTSIDE this "
        "repository; those bytes stay yours and nothing below reads them; "
        f"2. diff that copy against {target.recovery_extract_path.as_posix()!r} "
        "to see what moved; 3. restore the measured bytes over "
        f"{target.surface_path.as_posix()!r}; 4. {step_four}. Your saved copy is "
        "untouched by every step above. RE-APPLYING IT IS A SEPARATE DECISION "
        "about the coverage claim and is never part of this recovery: an edit "
        "that grows an unowned section past the recorded floor is still refused. "
        "Un-owning another section increases the floor and live unowned span "
        "equally, so it does not create headroom for that edit. Keep the saved "
        "copy outside the repository while deciding how to revise it within "
        "the ratchet. Do NOT delete the journal and do "
        "NOT hand-edit the ownership declaration -- its floor must stay "
        "witnessed by a real ledger event, and an edited one is refused on the "
        "next load."
    )


def _refuse_clean_success_on_a_moved_surface(
    target: _TransactionTarget, record: dict[str, Any], *, committed_now: bool
) -> None:
    """Refuse to call a witnessed transition complete while its source is unreconciled.

    This is the transaction's binding on the surface, and it runs at the ONLY
    point where the check is meaningful: after the declaration and the ledger
    witness are both durable, and before the journal -- the sole recovery
    record -- is destroyed.

    A pre-flight check cannot cover this. `_refuse_surface_changed_under_us`
    runs before the journal write and is worth keeping, because a refusal there
    writes nothing at all; but it is a check-then-act guard, so an edit landing
    between it and the commit slips through by construction. Step-4b round 7
    reproduced exactly that: `exit=0`, success prose claiming `26 to 83 (+57 B)`,
    `stored_floor=83`, `live_unowned_span=653`, `journal_exists=False`, then
    `post_success_load=REJECTED`.

    THREE OBLIGATIONS, KEPT SEPARATE (operator ruling 2026-09-05, verbatim:
    *"Reject 'D beats E.' Keep three obligations separate: the transition is
    durably witnessed; the source is reconciled; recovery cleanup is complete.
    Establishing one does not discharge the others."*). Step-4b round-11
    finding 1 came from collapsing them: an earlier correction resolved "E
    shadows D" by letting a present ledger witness SKIP this binding on the
    replay path, so the retry cleared the journal, the retained source and the
    extract and exited 0 while the declaration's floor was exceeded by the live
    span -- `D+E retry_exit 0 floor 83 span 102 journal False snapshot False
    extract False`, then `advertised_raise alpha-section exit 1`. A durable
    witness establishes that the transition was witnessed. It establishes
    nothing about the source, and nothing about cleanup.

    The transition is NOT rolled back -- it cannot be, the witness is in an
    append-only ledger and it is a truthful record of what was committed. What
    is refused is the CLAIM OF CLEAN SUCCESS, and what is RETAINED is every
    piece of recovery material, so the surface can be reconciled and the state
    completed rather than being silently wrong.

    *committed_now* separates the two callers by the only thing that differs
    between them -- whether THIS run committed the transition or found it
    already witnessed by an earlier one. Everything downstream of that sentence
    is identical, and is single-sourced through `_reconciliation_sequence`,
    because the state is identical: stores in § Recovery Protocol state D,
    source in state E, the two orthogonal axes met as a pair.
    """
    journalled = record.get("surface_digest")
    if journalled is None:
        return
    # The FIXED target surface path, never one re-derived from the record: the
    # final observation must be of the same file the transaction measured.
    try:
        current = _surface_digest(target.surface_path.read_bytes())
    except OSError as exc:
        detail = f"it can no longer be read ({exc})"
    else:
        if current == journalled:
            return
        detail = "its bytes changed"

    if committed_now:
        opening = (
            f"surface {target.surface!r} changed DURING the un-owning of "
            f"section {record['section']!r}: {detail}"
        )
        step_four = (
            "re-run the same command, which has nothing left to complete -- the "
            "transition is already witnessed -- and clears the journal and the "
            "retained material"
        )
    else:
        opening = (
            f"the un-owning of section {record['section']!r} of "
            f"{target.surface!r} was witnessed by an earlier run, but the "
            f"surface no longer carries the bytes its floor was measured "
            f"against: {detail}"
        )
        step_four = (
            "re-run the same command, which clears the journal and the retained "
            "material once the surface matches what was measured"
        )
    located, extracted = _extract_retained_source(target, journalled)
    if extracted:
        located = f"{located} {_reconciliation_sequence(target, step_four)}"
    print(
        f"Error: {opening}.\n"
        "Why forbidden: THREE OBLIGATIONS ARE SEPARATE HERE and exactly one is "
        "discharged -- transition witnessed; source reconciliation pending; "
        "recovery cleanup pending. THE STORES ARE IN § Recovery Protocol state "
        "D and the SOURCE IS IN state E -- the two are orthogonal axes, and "
        "this exit is the pair. THE TRANSITION DID LAND: the declaration "
        "carries the new floor and the ledger carries its witness, and neither "
        "is retracted -- an append-only witness is a truthful record of what "
        "was committed. But the floor was measured against the surface as it "
        "was journalled, so the committed declaration may record a byte span "
        "the surface no longer has, and `load_declaration` fails closed while "
        "the live span exceeds the floor (REQ-0.35.0-04-05). A durable witness "
        "does NOT establish that the source was reconciled, so what is refused "
        "here is the claim that this completed cleanly. The journal is RETAINED "
        f"at {target.journal_path.as_posix()!r}. Your edit to the surface is "
        "untouched and was NOT reverted.\n"
        f"  {located}",
        file=sys.stderr,
    )
    sys.exit(2)


def _recovery_summary(surface: str, record: dict[str, Any], *, committed_now: bool) -> str:
    """Report what THIS run did to the pending transition, never what some run did.

    *committed_now* is the only thing that differs between the two arms, and it
    is the same discriminator `_refuse_clean_success_on_a_moved_surface` carries
    for the same reason. In § Recovery Protocol states A, B and C this run
    re-applies the declaration and/or appends the witness, so it genuinely
    completed the interrupted un-owning. In state D both stores were already
    durable before it started: `_append_event_once` finds the existing row and
    appends nothing, the durability re-establishment is skipped because a
    witness could not exist unless the barrier had succeeded, and the coherence
    gate is skipped too -- the run CLEARS and does nothing else.

    Reporting that as "Completed the interrupted un-owning ... Unowned-byte
    floor rose from A to B" attributes an earlier run's durable state change to
    this one, which is the same unsupported premise the refusal paths were
    corrected for. The floor values stay in the sentence because they are true
    of the transition; what changes is whose run made the move.
    """
    if committed_now:
        opening = (
            f"Completed the interrupted un-owning of section {record['section']!r} "
            f"of {surface!r}. Unowned-byte floor rose from "
            f"{record['prior_unowned_byte_floor']} to {record['new_unowned_byte_floor']}."
        )
    else:
        opening = (
            f"Cleared the recovery material for the un-owning of section "
            f"{record['section']!r} of {surface!r}. This run wrote no declaration "
            "and appended no ledger event: an EARLIER run committed and witnessed "
            f"the transition, which raised the unowned-byte floor from "
            f"{record['prior_unowned_byte_floor']} to {record['new_unowned_byte_floor']}."
        )
    return f"{opening} Attested by {record['attestor']}: {record['reason']}"


def _surface_digest(raw: bytes) -> str:
    """Digest the surface's RAW BYTES — never newline-normalized text.

    Step-4b round-8 finding 2. `Path.read_text` applies universal-newline
    translation, so a CRLF file decodes to the same string as its LF twin and
    hashed identically: `raw_lengths=25,29 decoded_equal=True
    digests_equal=True`. The floor this digest protects is a count of PHYSICAL
    BYTES, so a line-ending conversion changed the governed quantity without
    firing the binding and the recorded floor silently undercounted the file.

    Not an exotic input: `.claude/rules/cross-platform.md` makes Windows
    co-equal, and an editor there produces CRLF by saving. The digest must be
    taken over exactly the bytes whose spans are measured, which is why the
    read path below decodes with `bytes.decode` (no translation) rather than
    `read_text` (translation).
    """
    return hashlib.sha256(raw).hexdigest()


def _read_surface_or_exit(surface_path: Path, surface: str) -> tuple[str, str, bytes]:
    """Read the surface, or exit 1 in governed prose. Called INSIDE the lock.

    Returns the decoded text, its digest, and the RAW BYTES -- the third
    because those bytes are retained as § Recovery Protocol state E's recovery
    material, and re-encoding the text to obtain them would reintroduce exactly
    the text/bytes asymmetry round-8 finding 2 removed from this same read.

    `UnicodeDecodeError` is caught alongside `OSError` because it is a
    `ValueError`, not an `OSError`: an ordinary non-UTF-8 byte -- a bad paste,
    a mis-set editor encoding, a truncated multi-byte sequence -- otherwise
    escaped every governed failure path and surfaced as a bare
    `Unexpected error: 'utf-8' codec can't decode byte 0xff...` with no
    what/why/next-step (Step-4b round-6 finding 6). Nothing is written on
    either branch: this runs before the declaration is even loaded.
    """
    try:
        raw = surface_path.read_bytes()
        # `bytes.decode` performs NO newline translation, unlike `read_text`, so
        # the text measured here is byte-faithful to the bytes hashed beside it.
        return raw.decode("utf-8"), _surface_digest(raw), raw
    except (OSError, UnicodeDecodeError) as exc:
        print(
            f"Error: cannot read surface {surface_path.as_posix()!r}: {exc}.\n"
            "Why forbidden: un-owning a section requires re-measuring its byte span "
            "against the live surface (REQ-0.35.0-04-05); nothing written.\n"
            f"  Verify {surface!r} exists at the project root and is UTF-8 encoded, "
            "then retry.",
            file=sys.stderr,
        )
        sys.exit(1)


def _read_transaction_surface_or_exit(target: _TransactionTarget) -> tuple[str, str, bytes]:
    """Keep early read failures informative when a transaction already retained bytes."""
    try:
        return _read_surface_or_exit(target.surface_path, target.surface)
    except SystemExit:
        if target.journal_path.exists():
            print(
                f"Pending recovery journal: {target.journal_path.as_posix()!r}. "
                f"Retained snapshot path: {target.journal_source_path.as_posix()!r}. "
                "This run has not read or verified the snapshot. Preserve both files.\n"
                "  Before changing the source, save its raw bytes to a path OUTSIDE this "
                "repository; restore read access first if necessary. Verify the retained "
                "snapshot's SHA-256 against the journal's surface_digest before deliberately "
                "restoring those bytes over the source, then retry the same command. If the "
                "snapshot cannot be read or verified, preserve the files for recovery and "
                "do not overwrite the source. Do NOT delete the journal or hand-edit the "
                "ownership declaration.",
                file=sys.stderr,
            )
        raise


def _refuse_surface_changed_under_us(
    surface_path: Path, surface: str, section: str, measured_digest: str
) -> None:
    """Refuse and exit 1 if the surface changed since it was measured.

    The declaration lock serializes `gz` processes against each other; it does
    NOT stop an editor writing the surface mid-transition. Every value about to
    be committed -- the measured span, the new floor, the sections map digest --
    derives from the surface as it was read, so a surface that moved under us
    would be witnessed at a span it no longer has. Re-reading once more
    immediately before the journal is written closes the window to the width of
    this check rather than the width of the whole critical section, and
    refusing is safe: neither store has been touched yet, and the operator
    simply retries.

    Step-4b round-9 finding 2. This compared the re-read against the MEASURED
    TEXT, and the two reads were not the same quantity: the measuring read
    decodes `read_bytes()` (no translation, deliberately -- round-8 finding 2),
    while this one used `read_text` (universal-newline translation). For any
    CRLF surface those can never be equal, so an unchanged valid surface ALWAYS
    appeared changed and the command was unusable on a platform
    `.claude/rules/cross-platform.md` makes co-equal: observed `CRLF raw_bytes
    129 measured_bytes 129 roundtrips True initial_load ACCEPTED` then `exit 1
    writes [] appended 0 journal False`.

    Comparing `_surface_digest` over RAW BYTES against the digest this
    transaction journals makes the recheck govern the same quantity the
    transaction does -- one read, one digest, compared here and again after the
    witness lands. It also STRENGTHENS the guard: a CRLF -> LF conversion that
    leaves the visible text identical changes every physical span the floor
    counts, and the text comparison could not see it structurally.
    """
    try:
        current = _surface_digest(surface_path.read_bytes())
    except OSError as exc:
        current = None
        detail = f"it could not be re-read ({exc})"
    else:
        if current == measured_digest:
            return
        detail = "its bytes changed"
    del current
    print(
        f"Error: surface {surface!r} changed while un-owning section {section!r}: "
        f"{detail}.\n"
        "Why forbidden: the floor about to be witnessed was measured against the "
        "surface as it was read; committing it now would record a byte span the "
        "surface no longer has, and `load_declaration` fails closed on a floor "
        f"the live surface exceeds (REQ-0.35.0-04-05). {_ENTRY_SWEEP_CAVEAT}\n"
        "  Let the surface settle, then retry the same command.",
        file=sys.stderr,
    )
    sys.exit(1)


def content_unown_cmd(*, surface: str, section: str, attestor: str, reason: str) -> None:
    """Handle ``gz content unown <surface> --section <id> --attestor <n> --reason <t>``.

    Exit 0 on a successful raise; 1 on a blank attestor/reason, a *surface*
    that is not the identity its ownership declaration declares, an unreadable
    or malformed declaration, an unknown section id, a section that is already
    ``unowned``, or a surface that moved between measurement and commit; 2 on
    IO error writing the declaration or the ledger, on a journal that cannot be
    proven to continue the declaration on disk, and on a transition whose
    source is unreconciled -- including one already witnessed, because a
    durable witness discharges the witness obligation and neither of the other
    two (operator ruling 2026-09-05; Step-4b round-11 finding 1).
    """
    _refuse_blank_attestation(surface, section, attestor, reason)

    root = get_project_root()
    # ONE canonical transaction target, resolved ONCE, before the lock. Alias
    # resolution has to precede locking because the lock is taken on the
    # declaration SIDECAR, whose name is derived from the identity -- and two
    # surface spellings that alias one inode can still produce different
    # sidecar names, so `samefile` on the surface proves nothing about them.
    # The parameter is REBOUND to the target: the caller's raw spelling stops
    # existing under any name, so no later site can select a path from it.
    target = _resolve_target_or_exit(root, surface, section)
    surface = target.surface

    # Everything from here to the cleared journal is ONE critical section. The
    # read and the write were previously unserialized, so two concurrent runs
    # both read the pre-transition floor, both exited 0, both emitted a ledger
    # event, and only ONE transition survived on disk -- a witness asserting a
    # floor raise that was silently discarded, on the one governed path that
    # may raise the ratchet at all. The declaration is re-read INSIDE the lock:
    # any value read before acquiring is stale by construction.
    #
    # The SURFACE is read here too, for the same reason and by the same rule.
    # It used to be read at the top of the handler, and that snapshot then fed
    # span arithmetic, replay validation and the committed declaration -- so an
    # ordinary editor save between the read and the lock made the command
    # witness a span the surface no longer had, exit 0, and leave a declaration
    # `load_declaration` rejects (Step-4b round-6 finding 3). The lock excludes
    # other `gz` processes; it excludes no editor, so acquiring it is necessary
    # but not sufficient -- `_refuse_surface_changed_under_us` below re-reads
    # once more before either store is touched.
    with exclusive_declaration_lock(target.declaration_path):
        surface_text, surface_digest, surface_bytes = _read_transaction_surface_or_exit(target)
        # BEFORE the replay, because it is the state where no journal exists
        # that owes a durability boundary, and because the orphan identities it
        # returns must reach finalization.
        warned_orphans = _establish_recovery_boundary(target)
        replayed = _replay_pending_transition(root, target, surface_text, surface_digest)
        if replayed is not None:
            recovered, committed_now = replayed
            print(_recovery_summary(surface, recovered, committed_now=committed_now))
            if recovered["section"] != section:
                # Step-4b round-8 finding 3: this used to fall THROUGH to the
                # ordinary refusal paths, whose prose says "nothing written" --
                # after a witness had landed and its journal had been deleted.
                # Observed `exit=1 event_appended=True journal_exists=False`
                # alongside a claim that the stores were untouched, which no
                # `.gzkit/` access was needed to produce. A recovery is a
                # durable state change and always terminates the invocation
                # that performed it; the requested section is a separate run.
                print(
                    f"Error: section {section!r} was NOT un-owned by this "
                    f"invocation — it completed the pending transition for "
                    f"{recovered['section']!r} instead.\n"
                    "Why forbidden: a recovery is a durable state change, and "
                    "reporting it alongside a second, unrelated transition would "
                    "make either account ambiguous (REQ-0.35.0-04-02). The "
                    "recovery above DID land; nothing was written for "
                    f"{section!r}.\n"
                    f"  Re-run the same command to un-own {section!r} now that "
                    "the pending transition is complete.",
                    file=sys.stderr,
                )
                sys.exit(1)
            return

        declaration = _load_declaration_or_exit(target.declaration_path, surface_text, root)
        # The snapshot ACTUALLY CONSUMED, checked against the target before a
        # single value is taken from it -- and it is then the very object the
        # record and the successor below are built from. An earlier identity
        # peek at its own disk read binds nothing this path consumes; that is
        # why the lock-entry peek was removed rather than kept alongside.
        if declaration.surface != target.surface:
            _refuse_foreign_declaration_snapshot(
                target, declaration.surface, "loaded declaration", journal_retained=False
            )

        current = declaration.sections.get(section)
        if current is None:
            known = ", ".join(repr(sid) for sid in sorted(declaration.sections))
            print(
                f"Error: no section {section!r} declared for surface {surface!r}.\n"
                "Why forbidden: an id that names no section in the declaration cannot "
                f"be un-owned. {_ENTRY_SWEEP_CAVEAT}\n"
                f"  Known section ids: {known}. Retry with one of them.",
                file=sys.stderr,
            )
            sys.exit(1)
        if current != "corpus-owned":
            print(
                f"Error: section {section!r} is already {current!r}, not 'corpus-owned'.\n"
                "Why forbidden: the raise-path un-owns a currently corpus-owned section; "
                f"there is nothing to raise the floor by here. {_ENTRY_SWEEP_CAVEAT}\n"
                f"  Section {section!r} needs no action.",
                file=sys.stderr,
            )
            sys.exit(1)

        span = measure_section_spans(surface_text)[section]
        prior_floor = declaration.unowned_byte_floor
        new_floor = prior_floor + span
        new_sections = dict(declaration.sections)
        new_sections[section] = "unowned"
        record: dict[str, Any] = {
            # The TARGET's identity -- checked one statement after the load
            # against the very snapshot this record is built from, so the two
            # cannot disagree. It is a payload field, never a path selector:
            # every read and write below goes through `target`.
            "surface": target.surface,
            "section": section,
            "prior_unowned_byte_floor": prior_floor,
            "new_unowned_byte_floor": new_floor,
            "attestor": attestor,
            "reason": reason,
            "ts": datetime.now(UTC).isoformat(),
        }
        # `parent_event_id` is PERSISTED on the record (not merely passed as an
        # argument) so a replay of an interrupted transition can re-mint
        # `event_id` from the journal's own content and check it, rather than
        # trusting a claimed id it has no way to reproduce.
        record["parent_event_id"] = declaration.floor_event_id
        # Mint the event id BEFORE writing anything, and reuse this exact id for
        # the ledger append below -- the declaration's `floor_event_id` chain
        # pointer must name the event that actually witnesses this raise
        # (REQ-0.35.0-04-02's attested-chain requirement), never a second,
        # independently-derived id.
        record["event_id"] = _mint_event_id(record, record["parent_event_id"])
        new_declaration = declaration.model_copy(
            update={
                "sections": new_sections,
                "unowned_byte_floor": new_floor,
                "floor_event_id": record["event_id"],
            }
        )
        # Journal the SERIALIZED declaration, not a re-derivable description of
        # it: a recovering run must re-apply the exact bytes the interrupted one
        # intended, never re-decide the transition from a surface that may since
        # have changed.
        record["declaration_json"] = new_declaration.model_dump_json(indent=2) + "\n"
        # BIND THE SURFACE INTO THE TRANSACTION (Step-4b round 7, operator-ruled
        # 2026-09-04: "bind the surface into the transaction"). Every value about
        # to be committed -- the measured span, the new floor, the sections map
        # digest -- derives from `surface_text`. Journalling its digest makes the
        # surface a VERSIONED PARTICIPANT in the transition rather than an
        # unversioned input read twice and hoped about: `_commit_transition`
        # re-verifies this digest after the declaration and the witness are
        # durable, so a surface that moved mid-transaction is detected on the one
        # path that can still act on it. Rounds 6 and 7 both named the absence of
        # this binding as the weakest point; round 6's scalar re-read was a
        # substitute for it, and round 7 reproduced the residue the substitute
        # left.
        record["surface_digest"] = surface_digest

        # Compared against the JOURNALLED digest, not a second local copy: the
        # pre-commit recheck and the post-witness binding must govern one
        # quantity, read once (round-9 finding 2).
        _refuse_surface_changed_under_us(
            target.surface_path, surface, section, record["surface_digest"]
        )
        _commit_transition(root, target, record, surface_bytes, warned_orphans)

    print(
        f"Un-owned section {section!r} of {surface!r}. Unowned-byte floor rose from "
        f"{prior_floor} to {new_floor} (+{span} B). Attested by {attestor}: {reason}"
    )
