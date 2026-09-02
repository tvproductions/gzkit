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

import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.content.ownership import (
    OwnershipLoadError,
    declaration_path,
    load_declaration,
    measure_section_spans,
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
    # Mint the event id BEFORE writing the declaration, and reuse this exact
    # id for the ledger append below -- the declaration's `floor_event_id`
    # chain pointer must name the event that actually witnesses this raise
    # (REQ-0.35.0-04-02's attested-chain requirement), never a second,
    # independently-timestamped id.
    event_id = f"section-ownership-unowned-{surface}-{section}-{datetime.now(UTC).isoformat()}"
    new_declaration = declaration.model_copy(
        update={
            "sections": new_sections,
            "unowned_byte_floor": new_floor,
            "floor_event_id": event_id,
        }
    )

    try:
        path.write_text(new_declaration.model_dump_json(indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(
            f"Error writing ownership declaration {path.as_posix()!r}: {exc}. "
            "Nothing written.\n"
            "  Check file/directory permissions and disk space, then retry.",
            file=sys.stderr,
        )
        sys.exit(2)

    timestamp = datetime.now(UTC).isoformat()
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    try:
        ledger.append(
            LedgerEvent(
                event="section_ownership_unowned",
                id=event_id,
                ts=timestamp,
                extra={
                    "surface": surface,
                    "section": section,
                    "prior_unowned_byte_floor": prior_floor,
                    "new_unowned_byte_floor": new_floor,
                    "attestor": attestor,
                    "reason": reason,
                },
            )
        )
    except OSError as exc:
        print(
            f"Error writing ledger event for {surface!r}/{section!r}: {exc}. "
            f"THE UN-OWNING ALREADY HAPPENED — {path.as_posix()!r} is on "
            "disk with the new floor, but the ledger witness is incomplete "
            "(REQ-0.35.0-04-05).\n"
            "  Fix the ledger write, then verify with `gz validate --ledger`.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(
        f"Un-owned section {section!r} of {surface!r}. Unowned-byte floor rose from "
        f"{prior_floor} to {new_floor} (+{span} B). Attested by {attestor}: {reason}"
    )
