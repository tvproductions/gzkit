"""gz content land command handler -- OBPI-0.35.0-07 (ADR-0.35.0 Decision 6).

The governed multi-consumer promotion seam. ``gz content land <surface>``
generates every routed consumer's candidate from the corpus, verifies it,
passes it through the retention gate, and lands the whole set under ONE corpus
attestation on the corpus delta. Preparation is pure
(:func:`gzkit.content.landing.prepare_landing`): any refusal refuses the WHOLE
landing and writes nothing for any consumer.

Resume: when the surface's landing journal records an interrupted landing,
``gz content land <surface>`` resumes it with the recorded attestation and
landing_id -- no new attestation is taken, explicit values are ignored and said
so, and files already at their new hash are never rewritten. ``--status
<landing_id>`` classifies each consumer by content hashes, never mtimes, and
writes nothing.

Rollback: committed renditions are single files with NO prior-version
retention, so "put it back" is ``git checkout`` of the rendition, provenance
and lineage artifacts together from one known-good revision.

Exit 0: landed or resumed (or, with ``--dry-run``, planned; with ``--status``,
    classified -- including indeterminate consumers).
Exit 1: user/config error (empty attestation on a new delta, unreusable
    evidence, unrouted surface, duplicate or malformed --retention-map, inputs
    changed after preparation, a malformed journal, a resume refused over drift
    or a foreign edit, an unknown --status landing id).
Exit 2: system/IO error or incomplete publication (the journal is retained).
Exit 3: retention gate refusal -- a removed block is unaccounted for, including a
    --retention-map bound to no routed consumer of the surface.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from gzkit.attestor import configured_attestor_handle
from gzkit.commands.common import get_project_root
from gzkit.content.landing import (
    LandingJournal,
    LandingPlan,
    LandingRefusal,
    LandingStatus,
    landing_status,
    load_journal,
    prepare_landing,
    publish_landing,
    resume_landing,
)


def _short(digest: str | None) -> str:
    return digest[:12] if digest is not None else "absent"


def _action(old: str | None, new: str | None) -> str:
    if old == new:
        return "unchanged"
    return "remove" if new is None else "write"


def _attestation_source(journal: LandingJournal) -> str:
    return (
        "reused from verified committed sidecars (corpus unchanged)"
        if journal.attestation_reused
        else "supplied on this invocation"
    )


def render_landed(journal: LandingJournal, notes: tuple[str, ...], *, resumed: bool = False) -> str:
    """Render a completed landing: id, published artifacts, attestation source, next step."""
    lines = [
        f"Landed {journal.surface}: {journal.landing_id}",
        f"Corpus fingerprint: {_short(journal.new_corpus_fingerprint)}... "
        f"(entries={journal.corpus_entry_count})",
        f"Attestation: {journal.attestor} -- "
        + (
            "recorded in the landing journal (reused on resume)"
            if resumed
            else _attestation_source(journal)
        ),
    ]
    for consumer in journal.consumers:
        lines.append(f"  {consumer.consumer}:")
        lines.extend(
            f"    {'removed' if a.new_sha256 is None else 'published'} {a.kind:<10} {a.path}"
            for a in consumer.artifacts
        )
    lines.extend(notes)
    lines.append(
        "Every sidecar carries this landing_id; rollback is `git checkout` of the rendition, "
        "provenance and lineage artifacts together from one known-good revision."
    )
    lines.append(
        "Next: run `uv run gz agent sync control-surfaces` to deliver the landed renditions."
    )
    return "\n".join(lines)


def render_status(status: LandingStatus) -> str:
    """Render ``--status``: phase, one ``<consumer>: <verdict>`` line each, recovery prose."""
    source = (
        "the active landing journal"
        if status.source == "journal"
        else "its rendition_landed ledger event"
    )
    lines = [
        f"Landing {status.landing_id} of {status.surface}: phase {status.phase}",
        f"Manifest: {source}; corpus fingerprint {_short(status.new_corpus_fingerprint)}...",
        "Classified by the SHA-256 of every artifact's current bytes (never mtimes):",
    ]
    for consumer in status.consumers:
        lines.append(f"  {consumer.consumer}: {consumer.verdict}")
        lines.extend(f"    - {finding}" for finding in consumer.findings)
    lines.extend(c.recovery for c in status.consumers if c.recovery is not None)
    return "\n".join(lines)


def render_plan(plan: LandingPlan) -> str:
    """Render *plan* for ``--dry-run``: targets, hash prefixes, actions, attestation source."""
    journal = plan.journal
    source = _attestation_source(journal)
    lines = [
        f"Landing plan (dry run -- nothing written): {journal.landing_id}",
        "  (the id is minted per invocation; a real landing records its own)",
        f"Surface: {journal.surface}",
        f"Corpus fingerprint: {_short(journal.new_corpus_fingerprint)}... "
        f"(entries={journal.corpus_entry_count})",
        f"Attestation: {journal.attestor} -- {source}",
        f"Consumers: {', '.join(c.consumer for c in journal.consumers)}",
    ]
    for consumer in journal.consumers:
        lines.append(
            f"  {consumer.consumer} (old corpus fingerprint "
            f"{_short(consumer.old_corpus_fingerprint)}):"
        )
        lines.extend(
            f"    {_action(a.old_sha256, a.new_sha256):<9} {a.kind:<10} {a.path}  "
            f"old={_short(a.old_sha256)} new={_short(a.new_sha256)}"
            for a in consumer.artifacts
        )
    lines.extend(plan.notes)
    lines.append(
        f"Next: re-run without --dry-run to land {journal.surface} across every consumer above."
    )
    return "\n".join(lines)


def render_resume_plan(journal: LandingJournal) -> str:
    """Render ``--dry-run`` over an in-flight landing: what resume would still publish."""
    lines = [
        f"Resume plan (dry run -- nothing written): {journal.landing_id} (phase {journal.phase})",
        f"Attestation: {journal.attestor} -- recorded in the landing journal",
    ]
    for consumer in journal.consumers:
        state = "published" if consumer.published else "pending"
        lines.append(f"  {consumer.consumer} ({state}):")
        lines.extend(
            f"    {a.kind:<10} {a.path}  new={_short(a.new_sha256)}" for a in consumer.artifacts
        )
    lines.append(
        f"Next: re-run without --dry-run to resume; `gz content land {journal.surface} --status "
        f"{journal.landing_id}` classifies each consumer first."
    )
    return "\n".join(lines)


def _attestor_was_supplied(root: Path, attestor: str) -> bool:
    """Return whether *attestor* differs from what an omitted ``--attestor`` resolves to.

    ``--attestor`` defaults from `.gzkit.json`'s configured handle
    (``default_attestor_from_config``), so a value equal to that configured
    default was read the same way an omission is -- never as an operator
    override on THIS invocation -- or every resume on a configured machine
    would report a flag nobody typed as ignored.
    """
    return bool(attestor) and attestor != (configured_attestor_handle(root) or "")


def _resume_ignored_note(
    root: Path,
    active: LandingJournal,
    attestor: str,
    attestation_text: str,
    retention_maps: Sequence[str],
) -> str | None:
    """Name only the values THIS invocation supplied that resume ignores, or ``None``."""
    flags = [
        flag
        for flag, given in (
            ("--attestor", _attestor_was_supplied(root, attestor)),
            ("--attestation-text", bool(attestation_text.strip())),
        )
        if given
    ]
    sentences: list[str] = []
    if flags:
        sentences.append(
            f"{'/'.join(flags)} were ignored: landing {active.landing_id} keeps the "
            "attestation recorded when it was prepared -- the attestation is on the corpus "
            "delta, not on the write."
        )
    if retention_maps:
        named = ", ".join(repr(m) for m in retention_maps)
        verb = "was" if len(retention_maps) == 1 else "were"
        sentences.append(
            f"--retention-map {named} {verb} dropped: resume of landing {active.landing_id} "
            "never re-runs the retention gate (Requirement 12)."
        )
    if not sentences:
        return None
    return "Note: " + " ".join(sentences)


def _resume(
    root: Path,
    active: LandingJournal,
    *,
    dry_run: bool,
    attestor: str,
    attestation_text: str,
    retention_maps: Sequence[str],
) -> None:
    """Resume the surface's in-flight landing with its recorded attestation (REQ-07/08)."""
    if dry_run:
        print(render_resume_plan(active))
        return
    notes: list[str] = []
    note = _resume_ignored_note(root, active, attestor, attestation_text, retention_maps)
    if note is not None:
        notes.append(note)
    try:
        landed = resume_landing(root, active.surface)
    except LandingRefusal as refusal:
        print(refusal.message, file=sys.stderr)
        sys.exit(refusal.exit_code)
    notes.append(f"Resumed landing {landed.landing_id}; already-landed files were not rewritten.")
    print(render_landed(landed, tuple(notes), resumed=True))


def content_land_cmd(
    *,
    surface: str,
    attestor: str = "",
    attestation_text: str = "",
    retention_maps: list[str] | None = None,
    dry_run: bool = False,
    status: str | None = None,
) -> None:
    """Handle ``gz content land <surface>``.

    Exit 0 on success; 1 on config/validation error; 2 on IO error; 3 on a
    retention-gate refusal.
    """
    root = get_project_root()
    if status is not None:
        try:
            verdict = landing_status(root, surface, status)
        except LandingRefusal as refusal:
            print(refusal.message, file=sys.stderr)
            sys.exit(refusal.exit_code)
        print(render_status(verdict))
        return

    try:
        active = load_journal(root, surface)
    except LandingRefusal as refusal:
        print(refusal.message, file=sys.stderr)
        sys.exit(refusal.exit_code)
    if active is not None:
        _resume(
            root,
            active,
            dry_run=dry_run,
            attestor=attestor,
            attestation_text=attestation_text,
            retention_maps=retention_maps or [],
        )
        return

    try:
        plan = prepare_landing(
            root,
            surface,
            attestor=attestor,
            attestation_text=attestation_text,
            retention_maps=retention_maps or [],
        )
    except LandingRefusal as refusal:
        print(refusal.message, file=sys.stderr)
        sys.exit(refusal.exit_code)

    if dry_run:
        print(render_plan(plan))
        return

    try:
        landed = publish_landing(root, plan)
    except LandingRefusal as refusal:
        print(refusal.message, file=sys.stderr)
        sys.exit(refusal.exit_code)
    print(render_landed(landed, plan.notes))
