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
from typing import Any

from gzkit.commands.common import get_project_root
from gzkit.content.ownership import (
    OwnershipLoadError,
    declaration_journal_path,
    declaration_path,
    exclusive_declaration_lock,
    load_declaration,
    measure_section_spans,
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

# Every field a journalled record must carry to be replayable: the three
# `_replay_pending_transition` reads plus the five `_append_event_once` reads.
# A record missing any of them cannot complete the interrupted transition, so
# it is refused in prose rather than half-applied.
_JOURNAL_FIELDS: tuple[str, ...] = (
    "event_id",
    "surface",
    "section",
    "prior_unowned_byte_floor",
    "new_unowned_byte_floor",
    "attestor",
    "reason",
    "declaration_json",
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


def _append_event_once(root: Path, record: dict[str, Any]) -> None:
    """Append *record*'s ledger event unless the ledger already carries that id.

    The append is the step a retry resumes at, so it MUST be idempotent: a run
    interrupted after the ledger write but before the journal was cleared would
    otherwise emit a second witness for one transition.
    """
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    if ledger.latest_event(record["event_id"]) is not None:
        return
    ledger.append(
        LedgerEvent(
            event=_EVENT,
            id=record["event_id"],
            ts=record["ts"],
            extra={
                "surface": record["surface"],
                "section": record["section"],
                "prior_unowned_byte_floor": record["prior_unowned_byte_floor"],
                "new_unowned_byte_floor": record["new_unowned_byte_floor"],
                "attestor": record["attestor"],
                "reason": record["reason"],
            },
        )
    )


def _replay_pending_transition(root: Path, path: Path, journal_path: Path) -> dict[str, Any] | None:
    """Finish any journalled transition left behind by an interrupted run.

    Runs INSIDE the declaration lock and BEFORE `load_declaration`, because an
    interrupted run may have left a declaration naming a `floor_event_id` the
    ledger does not carry -- which the loader fails closed on, deliberately
    (REQ-0.35.0-04-02). Recovery therefore has to happen on the WRITE side:
    re-apply the journalled declaration if it never landed, complete the append
    under the SAME event id, then clear the journal. Returns the completed
    record, or None when there was nothing pending.
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
        print(
            f"Error: the pending-transition journal {journal_path.as_posix()!r} is "
            f"unreadable or malformed: {defect}.\n"
            "Why forbidden: an un-owning is completed from its journal, so an "
            "unreadable journal makes an interrupted raise unrecoverable and no "
            "further un-owning of this surface may proceed on top of it "
            "(REQ-0.35.0-04-02); nothing written.\n"
            f"  Inspect {journal_path.as_posix()!r} against the ledger, reconcile "
            "the declaration by hand, then delete the journal and retry.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        on_disk = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        on_disk = {}
    if on_disk.get("floor_event_id") != record["event_id"]:
        # The declaration write never landed: re-apply it from the journal.
        try:
            write_declaration_atomically(path, record["declaration_json"])
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

    try:
        _append_event_once(root, record)
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
            f"cannot write {journal_path.as_posix()!r}: {exc}. Nothing written.\n"
            "Why forbidden: the pending transition is recorded before either "
            "store is touched so an interrupted raise can be completed rather "
            "than left unrecoverable (REQ-0.35.0-04-02).\n"
            "  Check file/directory permissions and disk space, then retry.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        write_declaration_atomically(path, record["declaration_json"])
    except OSError as exc:
        with contextlib.suppress(OSError):
            journal_path.unlink()
        print(
            f"Error writing ownership declaration {path.as_posix()!r}: {exc}. "
            "Nothing written.\n"
            "Why forbidden: the declaration must carry the new floor durably "
            "BEFORE its ledger witness is written -- Layer 2 may never announce "
            "a floor Layer 1 does not carry (REQ-0.35.0-04-05). The write is "
            "atomic, so the declaration is byte-unchanged, and the journal has "
            "been cleared, so no transition is left pending.\n"
            "  Check file/directory permissions and disk space, then retry.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        _append_event_once(root, record)
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

    with contextlib.suppress(OSError):
        journal_path.unlink()


def content_unown_cmd(*, surface: str, section: str, attestor: str, reason: str) -> None:
    """Handle ``gz content unown <surface> --section <id> --attestor <n> --reason <t>``.

    Exit 0 on a successful raise; 1 on a blank attestor/reason, an unreadable
    or malformed declaration, an unknown section id, or a section that is
    already ``unowned``; 2 on IO error writing the declaration or the ledger.
    """
    _refuse_blank_attestation(surface, section, attestor, reason)

    root = get_project_root()
    surface_path = root / surface
    try:
        surface_text = surface_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"Error: cannot read surface {surface_path.as_posix()!r}: {exc}.\n"
            "Why forbidden: un-owning a section requires re-measuring its byte span "
            "against the live surface (REQ-0.35.0-04-05); nothing written.\n"
            f"  Verify {surface!r} exists at the project root, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    path = declaration_path(root, surface)
    journal_path = declaration_journal_path(root, surface)

    # Everything from here to the cleared journal is ONE critical section. The
    # read and the write were previously unserialized, so two concurrent runs
    # both read the pre-transition floor, both exited 0, both emitted a ledger
    # event, and only ONE transition survived on disk -- a witness asserting a
    # floor raise that was silently discarded, on the one governed path that
    # may raise the ratchet at all. The declaration is re-read INSIDE the lock:
    # any value read before acquiring is stale by construction.
    with exclusive_declaration_lock(path):
        recovered = _replay_pending_transition(root, path, journal_path)
        if recovered is not None and recovered["section"] == section:
            print(
                f"Completed the interrupted un-owning of section {section!r} of "
                f"{surface!r}. Unowned-byte floor rose from "
                f"{recovered['prior_unowned_byte_floor']} to "
                f"{recovered['new_unowned_byte_floor']}. "
                f"Attested by {recovered['attestor']}: {recovered['reason']}"
            )
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
        # Mint the event id BEFORE writing anything, and reuse this exact id for
        # the ledger append below -- the declaration's `floor_event_id` chain
        # pointer must name the event that actually witnesses this raise
        # (REQ-0.35.0-04-02's attested-chain requirement), never a second,
        # independently-derived id.
        record["event_id"] = _mint_event_id(record, declaration.floor_event_id)
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

        _commit_transition(path, journal_path, root, record)

    print(
        f"Un-owned section {section!r} of {surface!r}. Unowned-byte floor rose from "
        f"{prior_floor} to {new_floor} (+{span} B). Attested by {attestor}: {reason}"
    )
