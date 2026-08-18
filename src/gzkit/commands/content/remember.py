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
from pathlib import Path
from typing import Literal

from gzkit.commands.common import get_project_root
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import AgentContract, Corpus, CorpusEntry
from gzkit.content.parse import parse
from gzkit.content.parse.markdown_parser import section_id
from gzkit.content.rendition_store import corpus_fingerprint, load_fingerprint
from gzkit.ledger import Ledger
from gzkit.ledger_events import corpus_entry_appended_event

_Tier = Literal["invariant", "compressible"]
_Classification = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]


def _drifted_consumers(root: Path, surface: str) -> list[str]:
    """Return the committed consumers of *surface* whose provenance no longer matches.

    Reads the same two facts the freshness gate compares — the sidecar's
    ``corpus_fingerprint`` and the current corpus digest — but deliberately does NOT
    call ``validate_rendition_freshness``: that validator emits ``composition_drift_
    detected`` ledger events on its fail-closed path, and a capture command must not
    write drift events for a condition it is merely reporting.

    A consumer with no sidecar is skipped. Its rendition was already unprovable before
    this append, so naming it here would misattribute pre-existing drift to the capture.
    """
    rendition_dir = root / ".gzkit" / "renditions" / surface
    if not rendition_dir.is_dir():
        return []
    current = corpus_fingerprint(load_corpus(root, surface))
    drifted = []
    for path in sorted(rendition_dir.glob("*.md")):
        if path.name.endswith(".candidate.md"):
            continue
        provenance = load_fingerprint(root, surface, path.stem)
        if provenance is not None and provenance.corpus_fingerprint != current:
            drifted.append(path.stem)
    return drifted


def _warn_on_rendition_drift(root: Path, surface: str, tier: _Tier) -> None:
    """Announce, on stderr, the rendition drift this append just caused.

    Advisory only — never changes the exit code. The append succeeded and IS the
    intended effect; what the operator lacked was any signal that ``gz check`` would
    now fail on gates the capture command never mentioned (GHI #654).
    """
    # The append is already durable. Drift detection is best-effort reporting ON TOP of
    # it, so no fault here may cost the operator their words or their exit code: a
    # malformed sidecar makes `RenditionProvenance.model_validate_json` raise, and an
    # unreadable corpus makes `load_corpus` raise. Capture must stay unblockable.
    try:
        drifted = _drifted_consumers(root, surface)
    except (OSError, ValueError):
        return
    if not drifted:
        return

    # Flush first: stdout is buffered and stderr is not, so without this the warning
    # lands ABOVE the success line it is annotating (observed 2026-07-22).
    sys.stdout.flush()

    lines = [
        "",
        f"Warning: this append drifted {len(drifted)} committed rendition(s) of {surface!r}",
        f"  ({', '.join(drifted)}). They no longer derive from the current corpus,",
        "  so `gz check` will now fail on:",
        "    - Rendition freshness",
    ]
    if tier == "invariant":
        lines.append("    - Rendition floor coherence (invariant-tier entry)")
    lines.append("")
    lines.append("  Recover by recomposing and re-attesting each consumer:")
    for consumer in drifted:
        lines.append(f"    uv run gz content compose {surface} --consumer {consumer} \\")
        lines.append("        --candidate <file>")
        lines.append(f"    uv run gz content commit {surface} --consumer {consumer} \\")
        lines.append("        --attestor <you> --attestation-text <words>")
    if tier == "invariant":
        lines.append("")
        lines.append("  The invariant-tier text must appear VERBATIM in every rendition;")
        lines.append("  omitting it fails the floor gate even after a recompose.")

    print("\n".join(lines), file=sys.stderr)


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

    _warn_on_rendition_drift(root, surface, tier)
