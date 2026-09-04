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

import contextlib
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

from gzkit.commands.common import get_project_root
from gzkit.content.ownership import (
    OwnershipDeclaration,
    OwnershipLoadError,
    declaration_journal_path,
    declaration_path,
    exclusive_declaration_lock,
    load_declaration,
    measure_section_spans,
    sections_digest,
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
            "(REQ-0.35.0-04-05); nothing written.\n"
            f"  Ensure {path.as_posix()!r} exists, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as exc:
        print(
            f"Error: ownership declaration at {path.as_posix()!r} is "
            f"malformed: {exc}.\n"
            "Why forbidden: the raise-path must load a well-formed declaration before "
            "mutating it; nothing written.\n"
            f"  Repair {path.as_posix()!r} so it validates against "
            "src/gzkit/schemas/section_ownership.json, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)


_EVENT = "section_ownership_unowned"

# Every field a journalled record must carry to be replayable: the
# `_replay_pending_transition` reads (including `parent_event_id`, needed to
# re-mint `event_id` and check it against the on-disk chain pointer) plus the
# `_append_event_once` reads (including `ts`, read at unown.py:176). A record
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


def _landed_sections(root: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Read the section map from the declaration ON DISK for *record*'s surface.

    The witness must describe the state that exists. Deriving it from the
    journal's own `declaration_json` meant a journal could name any map it
    liked and have the ledger agree with it.
    """
    path = declaration_path(root, record["surface"])
    return json.loads(path.read_text(encoding="utf-8"))["sections"]


def _append_event_once(root: Path, record: dict[str, Any], journal_path: Path) -> None:
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
        "surface": record["surface"],
        "section": record["section"],
        "sections_digest": sections_digest(_landed_sections(root, record)),
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
                journal_path,
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


def _refuse_forged_journal(journal_path: Path, defect: str) -> NoReturn:
    """Refuse and exit 2: the journal is CRASH-RECOVERY STATE ONLY.

    Shared by every `_replay_pending_transition` defect that reaches past
    "parses to a dict carrying the right keys": a journal must be able to
    FINISH a transition its own content proves started from the live on-disk
    predecessor, never to INVENT one. A hand-authored journal that parses
    cleanly but disagrees with the on-disk chain, the deterministic event id,
    or the recomputed successor is exactly as forged as one that fails to
    parse at all, and gets the same governed refusal.
    """
    print(
        f"Error: the pending-transition journal {journal_path.as_posix()!r} is "
        f"unreadable or malformed: {defect}.\n"
        "Why forbidden: an un-owning is completed from its journal, so a "
        "journal that cannot be proven to continue the live on-disk "
        "predecessor makes an interrupted raise unrecoverable and no further "
        "un-owning of this surface may proceed on top of it "
        "(REQ-0.35.0-04-02); nothing written.\n"
        f"  Inspect {journal_path.as_posix()!r} against the ledger, reconcile "
        "the declaration by hand, then delete the journal and retry.",
        file=sys.stderr,
    )
    sys.exit(2)


def _apply_unlanded_transition(
    path: Path,
    journal_path: Path,
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
    # The declaration write never landed: the journal must PROVE it
    # continues the declaration actually on disk, never merely claim to.
    if on_disk.get("unowned_byte_floor") != record["prior_unowned_byte_floor"]:
        _refuse_forged_journal(
            journal_path,
            f"prior_unowned_byte_floor {record['prior_unowned_byte_floor']!r} "
            "does not match the floor currently on disk "
            f"({on_disk.get('unowned_byte_floor')!r}) -- the journal does not "
            "start from the declaration on disk",
        )
    if on_disk.get("floor_event_id") != record["parent_event_id"]:
        _refuse_forged_journal(
            journal_path,
            f"parent_event_id {record['parent_event_id']!r} does not match "
            f"the on-disk floor_event_id ({on_disk.get('floor_event_id')!r})",
        )
    try:
        span = measure_section_spans(surface_text)[record["section"]]
    except KeyError:
        _refuse_forged_journal(
            journal_path,
            f"section {record['section']!r} does not exist on the live surface",
        )
    if record["new_unowned_byte_floor"] != record["prior_unowned_byte_floor"] + span:
        _refuse_forged_journal(
            journal_path,
            f"new_unowned_byte_floor {record['new_unowned_byte_floor']!r} does "
            "not equal the on-disk floor plus section "
            f"{record['section']!r}'s real measured byte span "
            f"({record['prior_unowned_byte_floor'] + span!r})",
        )
    try:
        predecessor = OwnershipDeclaration(**on_disk)
    except (TypeError, ValueError) as exc:
        _refuse_forged_journal(journal_path, f"on-disk declaration does not validate: {exc}")
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
            journal_path,
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
            journal_path,
            "declaration_json does not match the successor derived from "
            "the on-disk predecessor and the journalled transition -- a "
            "journal may finish a transition, never invent one",
        )

    # Write the DERIVED successor, never the journal's own claimed bytes
    # verbatim -- the two are proven equal above, but the derived value is
    # the one this code actually stands behind.
    try:
        write_declaration_atomically(path, expected_declaration_json)
    except OSError as exc:
        print(
            f"Error completing the interrupted un-owning of "
            f"{record['section']!r}: cannot write {path.as_posix()!r}: {exc}.\n"
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
    path: Path, journal_path: Path, record: dict[str, Any], surface_text: str
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
    landed = json.loads(path.read_text(encoding="utf-8"))
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
            journal_path,
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
            journal_path,
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
            journal_path,
            f"the declaration on disk carries floor {landed_floor!r} with a live "
            f"unowned span of {live_unowned_span} -- completing this transition "
            f"would leave a declaration the loader rejects (expected floor "
            f"{record['new_unowned_byte_floor']!r}, and the span may never exceed "
            "the floor). The surface changed after the transition was journalled",
        )


def _replay_pending_transition(
    root: Path, path: Path, journal_path: Path, surface_text: str
) -> dict[str, Any] | None:
    """Finish any journalled transition left behind by an interrupted run.

    Runs INSIDE the declaration lock and BEFORE `load_declaration`, because an
    interrupted run may have left a declaration naming a `floor_event_id` the
    ledger does not carry -- which the loader fails closed on, deliberately
    (REQ-0.35.0-04-02). Recovery therefore has to happen on the WRITE side:
    re-apply the journalled declaration if it never landed, complete the append
    under the SAME event id, then clear the journal. Returns the completed
    record, or None when there was nothing pending.

    The journal is CRASH-RECOVERY STATE ONLY, never a second write path: every
    field is proven to CONTINUE the live on-disk predecessor before anything
    is written, so a hand-forged journal cannot mint a floor raise or an
    ownership flip that the real `content_unown_cmd` transition never
    produced (Step-4b adversary finding 2).
    """
    if not journal_path.exists():
        return None
    record: Any = None
    defect: str | None = None
    try:
        record = json.loads(journal_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
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
        _refuse_forged_journal(journal_path, defect)

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
            journal_path,
            f"event_id {record['event_id']!r} does not re-mint from the journal's own content",
        )

    try:
        on_disk = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        on_disk = {}

    if on_disk.get("floor_event_id") != record["event_id"]:
        # The declaration write never landed, so the journal must PROVE it
        # continues the declaration actually on disk rather than merely claim
        # to. When it HAS landed, that proof is unavailable by construction
        # (the predecessor is gone) and the coherence gate below is what
        # guards the completion instead.
        _apply_unlanded_transition(path, journal_path, record, on_disk, surface_text)

    _refuse_incoherent_landed_state(path, journal_path, record, surface_text)

    try:
        _append_event_once(root, record, journal_path)
    except OSError as exc:
        print(
            f"Error completing the interrupted un-owning of {record['section']!r}: "
            f"cannot append the ledger event: {exc}.\n"
            f"Why forbidden: {path.as_posix()!r} already carries the new floor, so "
            "its witness must be written for the declaration to load at all "
            "(REQ-0.35.0-04-02). The journal is retained, so nothing is lost.\n"
            "  Fix the ledger write, then retry the same command to complete it.",
            file=sys.stderr,
        )
        sys.exit(2)

    # ONE finalization path (Step-4b round-8 finding 1). This branch used to
    # append and unlink without ever calling the digest guard
    # (`post_digest_guard_calls=0`), so recovery could report clean success
    # after the journalled surface moved -- the binding covered the fresh
    # commit and left its twin open. The coherence checks above are not a
    # substitute: they ran correctly, against the surface as it was before the
    # append.
    _refuse_clean_success_on_a_moved_surface(root, journal_path, record)

    with contextlib.suppress(OSError):
        journal_path.unlink()
    return record


def _commit_transition(path: Path, journal_path: Path, root: Path, record: dict[str, Any]) -> None:
    """Journal, then write the declaration, then witness it, then clear the journal.

    This command updates TWO stores -- a mutable declaration and an APPEND-ONLY
    ledger -- and NEITHER order is safe on its own. Declaration-first can leave
    a `floor_event_id` naming an event that does not exist; ledger-first can
    leave an event announcing a floor that was never adopted. The order here is
    declaration-then-ledger (a witness must never outlive the state it
    witnesses) made RECOVERABLE by the journal: the pending transition is
    durable before either store is touched, so an interrupted run is completed
    by the next one rather than tolerated -- and `load_declaration` keeps
    failing closed on an unresolvable chain pointer, unweakened.
    """
    try:
        write_declaration_atomically(journal_path, json.dumps(record, indent=2) + "\n")
    except OSError as exc:
        print(
            f"Error journalling the un-owning of {record['section']!r}: "
            f"cannot write {journal_path.as_posix()!r}: {exc}.\n"
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
        write_declaration_atomically(path, record["declaration_json"])
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
            f"Error writing ownership declaration {path.as_posix()!r}: {exc}.\n"
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
        _append_event_once(root, record, journal_path)
    except OSError as exc:
        print(
            f"Error writing ledger event for {record['surface']!r}/"
            f"{record['section']!r}: {exc}. "
            f"THE UN-OWNING ALREADY HAPPENED — {path.as_posix()!r} is on "
            "disk with the new floor, but the ledger witness is incomplete.\n"
            "Why forbidden: the declaration now names a `floor_event_id` the "
            "ledger does not carry, so it fails closed on every subsequent "
            "load until the witness is written -- Layer 1 and Layer 2 must "
            "agree on the floor (REQ-0.35.0-04-05). The recovery is the "
            "retry below, never a hand-edit of the declaration.\n"
            f"  The transition is journalled at {journal_path.as_posix()!r}: fix "
            "the ledger write and retry the SAME command to complete it, then "
            "verify with `gz validate --ledger`.",
            file=sys.stderr,
        )
        sys.exit(2)

    _refuse_clean_success_on_a_moved_surface(root, journal_path, record)

    with contextlib.suppress(OSError):
        journal_path.unlink()


def _refuse_clean_success_on_a_moved_surface(
    root: Path, journal_path: Path, record: dict[str, Any]
) -> None:
    """Re-verify the journalled surface digest before the journal is cleared.

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
    `post_success_load=REJECTED`. The command reported success, destroyed the
    recovery state, and left a declaration its own canonical loader rejects.

    The transition is NOT rolled back -- it cannot be, the witness is in an
    append-only ledger and it is a truthful record of what was committed. What
    is refused is the CLAIM OF CLEAN SUCCESS, and what is retained is the
    journal, so the surface can be reconciled and the state completed rather
    than being silently wrong.
    """
    journalled = record.get("surface_digest")
    if journalled is None:
        return
    surface_path = root / record["surface"]
    try:
        current = _surface_digest(surface_path.read_bytes())
    except (OSError, UnicodeDecodeError) as exc:
        current = None
        detail = f"it can no longer be read ({exc})"
    else:
        if current == journalled:
            return
        detail = "its bytes changed"
    del current
    print(
        f"Error: surface {record['surface']!r} changed DURING the un-owning of "
        f"section {record['section']!r}: {detail}.\n"
        "Why forbidden: the floor just witnessed was measured against the surface "
        "as it was journalled, so the committed declaration may record a byte span "
        "the surface no longer has, and `load_declaration` fails closed when the "
        "live span exceeds the floor (REQ-0.35.0-04-05). THE TRANSITION DID LAND: "
        "the declaration carries the new floor and the ledger carries its witness, "
        "and neither is retracted -- an append-only witness is a truthful record of "
        "what was committed. What is refused here is the claim that this completed "
        "cleanly.\n"
        f"  The journal is RETAINED at {journal_path.as_posix()!r}. Reconcile the "
        "surface against the declaration, then re-run `gz content unown` to raise "
        "the floor over the new span, or restore the surface to the state that was "
        "measured.",
        file=sys.stderr,
    )
    sys.exit(2)


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


def _read_surface_or_exit(surface_path: Path, surface: str) -> tuple[str, str]:
    """Read the surface, or exit 1 in governed prose. Called INSIDE the lock.

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
        return raw.decode("utf-8"), _surface_digest(raw)
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


def _refuse_surface_changed_under_us(
    surface_path: Path, surface: str, section: str, measured_text: str
) -> None:
    """Refuse and exit 1 if the surface changed since it was measured.

    The declaration lock serializes `gz` processes against each other; it does
    NOT stop an editor writing the surface mid-transition. Every value about to
    be committed -- the measured span, the new floor, the sections map digest --
    derives from `measured_text`, so a surface that moved under us would be
    witnessed at a span it no longer has. Re-reading once more immediately
    before the journal is written closes the window to the width of this check
    rather than the width of the whole critical section, and refusing is safe:
    neither store has been touched yet, and the operator simply retries.
    """
    try:
        current = surface_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        current = None
        detail = f"it could not be re-read ({exc})"
    else:
        if current == measured_text:
            return
        detail = "its bytes changed"
    del current
    print(
        f"Error: surface {surface!r} changed while un-owning section {section!r}: "
        f"{detail}.\n"
        "Why forbidden: the floor about to be witnessed was measured against the "
        "surface as it was read; committing it now would record a byte span the "
        "surface no longer has, and `load_declaration` fails closed on a floor "
        "the live surface exceeds (REQ-0.35.0-04-05). Nothing written.\n"
        "  Let the surface settle, then retry the same command.",
        file=sys.stderr,
    )
    sys.exit(1)


def content_unown_cmd(*, surface: str, section: str, attestor: str, reason: str) -> None:
    """Handle ``gz content unown <surface> --section <id> --attestor <n> --reason <t>``.

    Exit 0 on a successful raise; 1 on a blank attestor/reason, an unreadable
    or malformed declaration, an unknown section id, or a section that is
    already ``unowned``; 2 on IO error writing the declaration or the ledger.
    """
    _refuse_blank_attestation(surface, section, attestor, reason)

    root = get_project_root()
    surface_path = root / surface

    path = declaration_path(root, surface)
    journal_path = declaration_journal_path(root, surface)

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
    with exclusive_declaration_lock(path):
        surface_text, surface_digest = _read_surface_or_exit(surface_path, surface)
        recovered = _replay_pending_transition(root, path, journal_path, surface_text)
        if recovered is not None:
            print(
                f"Completed the interrupted un-owning of section "
                f"{recovered['section']!r} of {surface!r}. Unowned-byte floor rose "
                f"from {recovered['prior_unowned_byte_floor']} to "
                f"{recovered['new_unowned_byte_floor']}. "
                f"Attested by {recovered['attestor']}: {recovered['reason']}"
            )
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

        declaration = _load_declaration_or_exit(path, surface_text, root)

        current = declaration.sections.get(section)
        if current is None:
            known = ", ".join(repr(sid) for sid in sorted(declaration.sections))
            print(
                f"Error: no section {section!r} declared for surface {surface!r}.\n"
                "Why forbidden: an id that names no section in the declaration cannot "
                "be un-owned; nothing written.\n"
                f"  Known section ids: {known}. Retry with one of them.",
                file=sys.stderr,
            )
            sys.exit(1)
        if current != "corpus-owned":
            print(
                f"Error: section {section!r} is already {current!r}, not 'corpus-owned'.\n"
                "Why forbidden: the raise-path un-owns a currently corpus-owned section; "
                "there is nothing to raise the floor by here. Nothing written.\n"
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
            "surface": surface,
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

        _refuse_surface_changed_under_us(surface_path, surface, section, surface_text)
        _commit_transition(path, journal_path, root, record)

    print(
        f"Un-owned section {section!r} of {surface!r}. Unowned-byte floor rose from "
        f"{prior_floor} to {new_floor} (+{span} B). Attested by {attestor}: {reason}"
    )
