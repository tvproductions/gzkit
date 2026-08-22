"""gz content remember command handler — ADR-0.0.37 § Re-Alignment, OBPI-19.

Append-only corpus capture: ``gz content remember <surface> --section <id> --text <text>
[--tier invariant|compressible]`` appends one addressed/provenanced ``CorpusEntry`` to the
per-surface corpus store and emits a ``corpus_entry_appended`` ledger event. It NEVER edits
a rendered surface (AGENTS.md, CLAUDE.md, or any mirror) — capture writes the source of
truth; deterministic playback (OBPI-22) remains the sole writer of rendered surfaces.

Fail-closed discipline: an unknown surface (no parseable AgentContract) or a ``--section``
that resolves to no template-defined Pillar of that surface aborts with a non-zero exit and
writes no entry — an unaddressable entry is never persisted.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import Literal

from gzkit.commands.common import get_project_root
from gzkit.commands.content._drift import warn_on_rendition_drift
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import AgentContract, Corpus, CorpusEntry
from gzkit.content.parse import parse
from gzkit.content.parse.markdown_parser import section_id
from gzkit.ledger import Ledger
from gzkit.ledger_events import corpus_entry_appended_event

_Tier = Literal["invariant", "compressible"]
_Classification = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]


def content_remember_cmd(
    *,
    surface: str,
    section: str,
    text: str,
    tier: _Tier,
    classification: _Classification,
    origin: str,
    witness: str = "",
) -> None:
    """Handle ``gz content remember <surface> --section <id> --text <text> [...]``.

    Exit 0 on a successful append; 1 on unknown surface / unaddressable section;
    2 on IO error writing the corpus store.
    """
    root = get_project_root()
    surface_path = root / surface

    try:
        surface_text = surface_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(
            f"Error: unknown surface {surface!r} (no file at {surface_path.as_posix()}). "
            "Capture targets an existing control surface; no entry written.",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading surface {surface_path.as_posix()}: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        parsed = parse(surface_text, "AgentContract", file_path=str(surface_path))
    except ValueError as exc:
        print(
            f"Error: surface {surface!r} does not parse as an AgentContract: {exc}. "
            "No entry written.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not isinstance(parsed, AgentContract):  # parse('AgentContract') returns this type
        print(f"Error: surface {surface!r} did not yield an AgentContract.", file=sys.stderr)
        sys.exit(1)
    contract = parsed

    normalized_section = section_id(section)
    timestamp = datetime.now(UTC).isoformat()
    entry = CorpusEntry(
        id=f"corpus-{normalized_section}-{timestamp}",
        surface=surface,
        section=normalized_section,
        tier=tier,
        classification=classification,
        text=text,
        origin=origin,
        # `origin` is HOW the entry arrived (`cli:content-remember`); `witness` is WHO
        # vouches for it. Distinct questions, so an unsupplied witness stays None rather
        # than defaulting to the origin string — a fabricated witness is worse than an
        # absent one on the artifact the whole system trusts (ADR-0.35.0 § Alternatives B).
        witness=witness.strip() or None,
        ts=timestamp,
    )

    # Validate BEFORE any write — an unaddressable section never reaches the store (REQ-04).
    try:
        Corpus(entries=(entry,)).validate_against(contract)
    except ValueError:
        valid = ", ".join(sorted(pillar.id for pillar in contract.pillars))
        print(
            f"Error: section {section!r} (normalized {normalized_section!r}) resolves to no "
            f"section of {surface!r}. Valid sections: {valid}. No entry written.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Refuse a text already live in the store (GHI #862). `gz content retire`
    # refuses a second retraction of the same id on the same ground -- idempotent
    # by refusal, not by silent re-append. Capture had no such guard, so one
    # 2026-06-19 import doubled seven operator directives and every check stayed
    # green: byte-identical copies are both satisfied by one rendered occurrence,
    # so the invariant floor never noticed. Retired rows do not count, which keeps
    # retire-then-remember -- the amendment path -- open.
    duplicate = load_corpus(root, surface).live_entry_with_text(text)
    if duplicate is not None:
        print(
            f"Error: corpus entry {duplicate.id!r} (section {duplicate.section!r}) already "
            f"carries this text verbatim in {surface!r}. Capture is idempotent by refusal, "
            "not by silent re-append; nothing written. To amend the wording, retire that "
            "entry first (`gz content retire`) and then remember the new text.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        append_entry(root, surface, entry)
    except OSError as exc:
        print(f"Error writing corpus store for {surface!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    Ledger(root / ".gzkit" / "ledger.jsonl").append(
        corpus_entry_appended_event(
            surface=surface,
            section=normalized_section,
            entry_id=entry.id,
            tier=tier,
        )
    )

    if sys.stdout.isatty():
        from gzkit.content.tui.status import render_status_line  # noqa: PLC0415

        render_status_line(
            operation="remembered",
            source=surface,
            result=normalized_section,
            byte_count=len(text.encode("utf-8")),
        )
    else:
        print(f"Appended corpus entry {entry.id} to {surface} [{normalized_section}].")

    warn_on_rendition_drift(root, surface, mutation="append", floor_risk=tier == "invariant")
