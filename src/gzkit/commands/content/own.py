"""gz content own command handler — the governed `unowned -> corpus-owned` transition (GHI #974).

ADR-0.35.0 § Decision 3 declares a two-directional ownership seam over a
decrease-only ratchet. OBPI-0.35.0-04 shipped the raise direction
(`gz content unown`); this verb is the lowering move that CHANGES THE MAP: a
section becomes ``corpus-owned`` once the corpus actually carries it, and the
unowned-byte floor falls to what the surface then measures. Without it an
unowned section that grew past the recorded floor had exactly one exit -- a
hand-edited declaration -- which is the move the ratchet exists to forbid.

Three facts the transition establishes, none of them a presence check:

1. **Coverage.** Every content line of the section's body is carried verbatim
   by a LIVE corpus entry addressed to that section (`section_coverage`). One
   entry that merely addresses the section -- the measure `compute_baseline`
   reports and REQ-0.35.0-04-08 names as inflated -- owns nothing here.
2. **The floor is measured, never subtracted.** The new floor is the summed
   span of the sections that REMAIN unowned on the live surface
   (`unowned_span_total`). `prior - span` assumes the other unowned sections
   still have the spans they had when the prior floor was recorded, and the
   state this verb exists for is the one where that assumption fails. A
   remainder ABOVE the stored floor is refused by the loader itself, reading
   the floor relation over the successor map (`load_declaration`'s
   `sections_becoming_owned`): this is the ordinary, decrease-or-equal path
   and may never raise the ratchet (REQ-0.35.0-04-02).
3. **Attestation.** Owning a section makes the corpus the authority for its
   content -- a canon change every time, with the same corpus-attestation
   shape as `gz content unown` and `gz content retire`: blank ``--attestor``
   or ``--reason`` exits 1 and writes nothing (REQ-0.35.0-04-04).

The witness is an ``unowned_ratchet_updated`` row -- it IS the
decrease-or-equal move that type witnesses -- carrying the section, the new
map's digest, the predecessor link, the attestor, the reason and the coverage
evidence; the loader holds any ratchet row that changes the map to that
attestation (`ownership._refuse_unattested_map_change`).

EVERY MECHANISM IS SHARED with `commands/content/unown.py`, never copied: the
resolved target, the declaration lock, the entry-time recovery boundary, the
retained source, the journal, the two-store commit, § Recovery Protocol states
A-E and the cleanup. A surface has ONE pending journal, and whichever verb runs
next completes it; the journal's ``transition`` field selects the direction.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import Any, NoReturn

from gzkit.commands.common import get_project_root
from gzkit.commands.content.unown import (
    _ENTRY_SWEEP_CAVEAT,
    _OWN_TRANSITION,
    _commit_transition,
    _coverage_or_refuse,
    _establish_recovery_boundary,
    _load_declaration_or_exit,
    _mint_event_id,
    _read_transaction_surface_or_exit,
    _recovery_summary,
    _refuse_blank_attestation,
    _refuse_foreign_declaration_snapshot,
    _refuse_surface_changed_under_us,
    _replay_pending_transition,
    _resolve_target_or_exit,
    _transition_kind,
)
from gzkit.content.ownership import (
    SectionCoverage,
    exclusive_declaration_lock,
    measure_section_spans,
    unowned_span_total,
)


def _refuse_incomplete_coverage(surface: str, section: str, coverage: SectionCoverage) -> NoReturn:
    """Refuse and exit 1: the live corpus does not carry the whole section.

    Names every uncovered line verbatim, because the recovery is to capture
    exactly those lines; a count alone would send the operator back to diff
    the section by hand. Nothing was written -- this runs before the journal.
    """
    if coverage.body_lines == 0:
        what = (
            f"section {section!r} of {surface!r} has no content lines to cover, so there "
            "is nothing for the corpus to be the authority for"
        )
        next_step = (
            f"  A section with no content cannot be corpus-owned; leave {section!r} "
            "unowned, or give it content and capture that content first."
        )
    else:
        named = "\n".join(f"    - {line!r}" for line in coverage.uncovered_lines)
        what = (
            f"the live corpus carries {coverage.covered_lines} of the {coverage.body_lines} "
            f"content line(s) of section {section!r} of {surface!r}; uncovered:\n{named}"
        )
        next_step = (
            f"  Capture each uncovered line with `gz content remember {surface} --section "
            f'{section} --text "<line>" --tier invariant --classification <Mechanical|'
            'Promotable|Judgment|Ambiguous> --origin "<why>"`, then retry the same command.'
        )
    print(
        f"Error: {what}.\n"
        "Why forbidden: a section becomes corpus-owned only when the corpus carries EVERY "
        "content line of it verbatim -- one entry that merely addresses the section is a "
        "presence check, and AGENTS.md § DO IT RIGHT forbids a gate whose only witness is "
        "that something exists (ADR-0.35.0 § Decision 3; GHI #974). Sub-headings inside the "
        f"section ({coverage.structural_lines} here) are structure and are exempt. "
        f"{_ENTRY_SWEEP_CAVEAT}\n"
        f"{next_step}",
        file=sys.stderr,
    )
    sys.exit(1)


def _refuse_section_not_owning(
    surface: str, section: str, current: str | None, known: list[str]
) -> NoReturn:
    """Refuse and exit 1: *section* is unknown, or is already corpus-owned."""
    if current is None:
        listed = ", ".join(repr(sid) for sid in known)
        print(
            f"Error: no section {section!r} declared for surface {surface!r}.\n"
            "Why forbidden: an id that names no section in the declaration cannot "
            f"be owned. {_ENTRY_SWEEP_CAVEAT}\n"
            f"  Known section ids: {listed}. Retry with one of them.",
            file=sys.stderr,
        )
    else:
        print(
            f"Error: section {section!r} is already {current!r}, not 'unowned'.\n"
            "Why forbidden: owning moves a currently unowned section into the corpus's "
            f"authority; there is nothing to move here. {_ENTRY_SWEEP_CAVEAT}\n"
            f"  Section {section!r} needs no action.",
            file=sys.stderr,
        )
    sys.exit(1)


def _refuse_recovered_other_transition(section: str, recovered: dict[str, Any]) -> NoReturn:
    """Refuse and exit 1: this run completed a pending transition, not the requested owning."""
    pending = "owning" if _transition_kind(recovered) == _OWN_TRANSITION else "un-owning"
    print(
        f"Error: section {section!r} was NOT owned by this invocation — it completed "
        f"the pending {pending} of {recovered['section']!r} instead.\n"
        "Why forbidden: a recovery is a durable state change, and reporting it alongside "
        "a second, unrelated transition would make either account ambiguous "
        f"(REQ-0.35.0-04-02). The recovery above DID land; nothing was written for "
        f"{section!r}.\n"
        f"  Re-run the same command to own {section!r} now that the pending transition "
        "is complete.",
        file=sys.stderr,
    )
    sys.exit(1)


def content_own_cmd(*, surface: str, section: str, attestor: str, reason: str) -> None:
    """Handle ``gz content own <surface> --section <id> --attestor <n> --reason <t>``.

    Exit 0 when the section becomes ``corpus-owned`` and the floor is recorded
    at the live remaining unowned span; 1 on a blank attestor/reason, a
    *surface* that is not the identity its declaration declares, an unreadable
    or malformed declaration, an unknown or already-owned section, incomplete
    corpus coverage, a remainder that would raise the floor, or a surface that
    moved between measurement and commit; 2 on IO error writing either store,
    on a journal that cannot be proven to continue the declaration on disk,
    and on a pending transition whose source or coverage is unreconciled.
    """
    _refuse_blank_attestation(surface, section, attestor, reason, verb="own")

    root = get_project_root()
    target = _resolve_target_or_exit(root, surface, section, verb="own")
    surface = target.surface

    with exclusive_declaration_lock(target.declaration_path):
        surface_text, surface_digest, surface_bytes = _read_transaction_surface_or_exit(target)
        warned_orphans = _establish_recovery_boundary(target)
        replayed = _replay_pending_transition(root, target, surface_text, surface_digest)
        if replayed is not None:
            recovered, committed_now = replayed
            print(_recovery_summary(surface, recovered, committed_now=committed_now))
            if recovered["section"] != section or _transition_kind(recovered) != _OWN_TRANSITION:
                _refuse_recovered_other_transition(section, recovered)
            return

        # The floor relation is read over the map this transition PRODUCES;
        # every other loader check binds the declaration as it is on disk.
        declaration = _load_declaration_or_exit(
            target.declaration_path,
            surface_text,
            root,
            sections_becoming_owned=frozenset({section}),
        )
        if declaration.surface != target.surface:
            _refuse_foreign_declaration_snapshot(
                target, declaration.surface, "loaded declaration", journal_retained=False
            )

        current = declaration.sections.get(section)
        if current != "unowned":
            _refuse_section_not_owning(surface, section, current, sorted(declaration.sections))

        coverage = _coverage_or_refuse(root, target, section, surface_text, journal_retained=False)
        if not coverage.complete:
            _refuse_incomplete_coverage(surface, section, coverage)

        # The floor is what the surface MEASURES under the successor map -- the
        # same `unowned_span_total` the loader just evaluated over this very
        # map, which is why a remainder above the stored floor was refused
        # there, in the loader's own prose, before this line could be reached.
        spans = measure_section_spans(surface_text)
        new_sections = dict(declaration.sections)
        new_sections[section] = "corpus-owned"
        prior_floor = declaration.unowned_byte_floor
        new_floor = unowned_span_total(spans, new_sections)

        record: dict[str, Any] = {
            "transition": _OWN_TRANSITION,
            "surface": target.surface,
            "section": section,
            "prior_unowned_byte_floor": prior_floor,
            "new_unowned_byte_floor": new_floor,
            "attestor": attestor,
            "reason": reason,
            "ts": datetime.now(UTC).isoformat(),
            "covering_entry_ids": list(coverage.covering_entry_ids),
            "covered_lines": coverage.covered_lines,
            "body_lines": coverage.body_lines,
        }
        record["parent_event_id"] = declaration.floor_event_id
        record["event_id"] = _mint_event_id(record, record["parent_event_id"])
        new_declaration = declaration.model_copy(
            update={
                "sections": new_sections,
                "unowned_byte_floor": new_floor,
                "floor_event_id": record["event_id"],
            }
        )
        record["declaration_json"] = new_declaration.model_dump_json(indent=2) + "\n"
        record["surface_digest"] = surface_digest

        _refuse_surface_changed_under_us(
            target.surface_path, surface, section, record["surface_digest"], gerund="owning"
        )
        _commit_transition(root, target, record, surface_bytes, warned_orphans)

    exempt = (
        f" ({coverage.structural_lines} sub-heading line(s) exempt as structure)"
        if coverage.structural_lines
        else ""
    )
    print(
        f"Owned section {section!r} of {surface!r}. Unowned-byte floor fell from "
        f"{prior_floor} to {new_floor} (-{prior_floor - new_floor} B). "
        f"Coverage: {len(coverage.covering_entry_ids)} live entries carry "
        f"{coverage.covered_lines}/{coverage.body_lines} content lines{exempt}. "
        f"Attested by {attestor}: {reason}"
    )
